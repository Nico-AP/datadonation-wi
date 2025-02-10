from django.urls import path
from .views import TikTokReport, HashtagsView

app_name = 'reports'

urlpatterns = [
    path(
        'tiktok/dein-report/<slug:participant_id>',
        TikTokReport.as_view(),
        name='tiktok-report'
    ),
    path('report/<str:participant_id>/', TikTokReport.as_view(), name='report'),
    path('hashtags/', HashtagsView.as_view(), name='hashtags'),
]
