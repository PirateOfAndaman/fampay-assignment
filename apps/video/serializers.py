from rest_framework import serializers
from .models import VideoDetails

class VideoDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoDetails
        fields = [
            "video_id",
            "title",
            "description",
            "published_at",
            "thumbnail_url",
            "search_query_id",
        ] 