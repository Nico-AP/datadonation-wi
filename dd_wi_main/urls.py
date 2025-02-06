from django.urls import path
from .views import LandingView, WipView

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('wip', WipView.as_view(), name='wip'),
]
