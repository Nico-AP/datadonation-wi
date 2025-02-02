from django.urls import path
from .views import TikTokReport


urlpatterns = [
    path(
        'tiktok/dein-report/<slug:participant_id>',
        TikTokReport.as_view(),
        name='tiktok-report'
    ),
]
