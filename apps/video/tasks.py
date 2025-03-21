import datetime
import requests
import itertools
import structlog
from celery import shared_task
from django.utils.timezone import now
from django.core.cache import cache
from django.db import IntegrityError
from .models import SearchQuery, VideoDetails
from django.conf import settings
logger = structlog.get_logger()

# List of API keys for rotation
YOUTUBE_API_KEYS = settings.YOUTUBE_API_KEYS
api_key_iterator = itertools.cycle(YOUTUBE_API_KEYS)
CURRENT_API_KEY = next(api_key_iterator)

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
FETCH_INTERVAL = 300  # Fetch interval in seconds
LOCK_EXPIRY = 305  # Redis lock expiry in seconds


def get_next_api_key():
    """Rotate to the next API key when quota limit is hit."""
    global CURRENT_API_KEY
    CURRENT_API_KEY = next(api_key_iterator)
    logger.info("Switching to next API key", api_key=CURRENT_API_KEY)
    return CURRENT_API_KEY


@shared_task
def fetch_latest_videos():
    """Main Celery task to fetch videos for all search queries."""
    logger.info("Fetching latest videos for all queries")
    queries = SearchQuery.objects.all()
    for query in queries:
        fetch_videos_for_query.apply_async((query.id, None))


@shared_task
def fetch_videos_for_query(query_id, next_page_token=None):
    """Fetches latest videos for a given search query with API key rotation and distributed locking."""
    global CURRENT_API_KEY

    try:
        search_query = SearchQuery.objects.get(id=query_id)
    except SearchQuery.DoesNotExist:
        logger.warning("Search query not found", query_id=query_id)
        return

    lock_key = f"lock:fetch_videos:{query_id}"
    last_fetch_key = f"last_fetch_time:{query_id}"

    # Attempt to acquire lock
    if not cache.add(lock_key, "locked", timeout=LOCK_EXPIRY):
        logger.info("Task already in progress, skipping", query=search_query.query)
        return

    try:
        last_fetch = cache.get(last_fetch_key) or now() - datetime.timedelta(seconds=FETCH_INTERVAL)
        published_after = last_fetch.strftime("%Y-%m-%dT%H:%M:%S.000Z")


        params = {
            "part": "snippet",
            "q": search_query.query,
            "type": "video",
            "order": "date",
            "publishedAfter": published_after,
            "maxResults": 50,
            "key": CURRENT_API_KEY,
        }
        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(YOUTUBE_API_URL, params=params, timeout=8)
        if response.status_code == 403 and "quotaExceeded" in response.text:
            logger.warning("Quota exceeded, rotating API key")
            params["key"] = get_next_api_key()
            return fetch_videos_for_query(query_id, next_page_token)

        response.raise_for_status()
        data = response.json()
        videos = data.get("items", [])

        for video in videos:
            video_id = video["id"]["videoId"]
            snippet = video["snippet"]
            if not VideoDetails.objects.filter(video_id=video_id).exists():
                try:
                    VideoDetails.objects.create(
                        search_query=search_query,
                        video_id=video_id,
                        title=snippet["title"],
                        description=snippet.get("description", ""),
                        published_at=snippet["publishedAt"],
                        thumbnail_url=snippet["thumbnails"]["high"]["url"],
                    )
                except IntegrityError:
                    pass

        # Update last fetch time
        cache.set(last_fetch_key, now(), timeout=None)
        
        # Recursively fetch next page if token exists
        next_page_token = data.get("nextPageToken")
        if next_page_token:
            fetch_videos_for_query.apply_async((query_id, next_page_token))
    
    except Exception as e:
        logger.error("Error fetching videos for query", query=search_query.query, error=str(e), exc_info=True)

    finally:
        cache.delete(lock_key)  # Release lock
