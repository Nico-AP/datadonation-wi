from django.urls import path
from .api import ScraperPostAPI, TikTokVideoListAPI, TikTokVideoBRetrieveUpdateAPI, TikTokVideoBListAPI

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
    path(
        'api/video/<str:video_id>/',
        TikTokVideoBRetrieveUpdateAPI.as_view(),
        name='video_b_detail_api'
    ),
    path(
        'api/list/videos/',
        TikTokVideoBListAPI.as_view(),
        name='video_b_list_api'
    ),
]
