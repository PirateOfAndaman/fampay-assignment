from django.urls import path
from .views import VideoSearchView

urlpatterns = [
    path('search/', VideoSearchView.as_view(), name='video-search'),
]
