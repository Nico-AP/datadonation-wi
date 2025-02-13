from django.urls import path
from .views import (
    HashtagsView, TikTokReportLoading, TikTokReportResults,
    check_task_status
)

app_name = 'reports'

urlpatterns = [
    path(
        'hashtags/',
        HashtagsView.as_view(),
        name='hashtags'
    ),
    path(
        'tiktok/report/request/<slug:participant_id>',
        TikTokReportLoading.as_view(),
        name='tiktok_report_loading'
    ),
    path(
        'tiktok/report/<str:task_id>/',
        TikTokReportResults.as_view(),
        name='tiktok_report_result'
    ),
    path(
        'api/task-status/<str:task_id>/',
        check_task_status,
        name='check_task_status'
    ),
]
