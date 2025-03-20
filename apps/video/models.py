from django.db import models

from common.helpers import BaseModelMixin

class SearchQuery(BaseModelMixin):
    class Meta:
        db_table = 'search_query'
        
    query = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.query

class VideoDetails(BaseModelMixin):
    class Meta:
        db_table = "video_details"
        
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name="videos")
    title = models.TextField(db_index=True)
    description = models.TextField(db_index=True)
    published_at = models.DateTimeField(db_index=True)
    thumbnail_url = models.URLField()

    def __str__(self):
        return self.title
