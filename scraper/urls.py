from django.urls import path
from .api import ScraperPostAPI, TikTokVideoListAPI

urlpatterns = [
    path(
        'api/post',
        ScraperPostAPI.as_view(),
        name='scraper_post_api'
    ),
    path(
        'api/videos',
        TikTokVideoListAPI.as_view(),
        name='video_list_api'
    ),
]
