from django.urls import path
from .api import (
    ScraperPostAPI, TikTokVideoListAPI,TikTokVideoBListAPI,
    TikTokVideoBRetrieveAPI, TikTokVideoBUpdateAPI
)

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
        TikTokVideoBRetrieveAPI.as_view(),
        name='video_b_detail_api'
    ),
    path(
        'api/video/<str:video_id>/update/',
        TikTokVideoBUpdateAPI.as_view(),
        name='video_b_update_api'
    ),
    path(
        'api/list/videos/',
        TikTokVideoBListAPI.as_view(),
        name='video_b_list_api'
    ),
]
