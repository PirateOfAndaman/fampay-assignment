import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fampay.settings')
celery_app = Celery('youtube-worker')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


celery_app.conf.beat_schedule = {
    "fetch_youtube_videos_every_10_sec": {
        "task": "apps.video.tasks.fetch_latest_videos",
        "schedule": 5.0, 
    },
}
