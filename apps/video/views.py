import structlog
from django.db import connection
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import VideoDetailsSerializer

logger = structlog.get_logger()

class VideoSearchView(APIView):
    """
    Search videos using SQLite FTS5 for efficient full-text search.
    """
    def get(self, request):
        query = request.GET.get("q", "").strip()
        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 10)

        logger.info("Received search request", query=query, page=page_number, page_size=page_size)

        if not query:
            logger.warning("Missing query parameter 'q'")
            return Response({"error": "Query parameter 'q' is required."}, status=400)

        sql_query = """
            SELECT video_details.*
            FROM video_details
            JOIN video_details_fts ON video_details.id = video_details_fts.rowid
            WHERE video_details_fts MATCH %s
            ORDER BY rank
            """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, [query])
                results = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            videos = [dict(zip(columns, row)) for row in results]

            # Paginate results
            paginator = Paginator(videos, page_size)
            page = paginator.get_page(page_number)

            serialized_videos = VideoDetailsSerializer(page.object_list, many=True).data  

            logger.info(
                "Search results retrieved",
                query=query,
                total_results=paginator.count,
                total_pages=paginator.num_pages,
                current_page=page.number
            )

            return Response({
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page.number,
                "results": serialized_videos,  
            })
        except Exception as e:
            logger.error("Error executing search query", error=str(e))
            return Response({"error": "Internal server error"}, status=500)
