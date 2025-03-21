from django.db import models,connection

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
        indexes = [
            models.Index(fields=["title"], name="video_title_idx"),
            models.Index(fields=["description"], name="video_desc_idx"),
        ]

    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name="videos")
    video_id = models.CharField(max_length=50, unique=True)
    title = models.TextField(db_index=True)
    description = models.TextField(db_index=True)
    published_at = models.DateTimeField(db_index=True)
    thumbnail_url = models.URLField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  
        
        # Now update the FTS5 table
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO video_details_fts (rowid, title, description)
                VALUES (%s, %s, %s)
                """,
                [self.pk, self.title, self.description], 
            )

    def delete(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM video_details_fts WHERE rowid = ?", [self.id])
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title
