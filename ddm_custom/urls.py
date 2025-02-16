from django.urls import path
from .views import BriefingViewCustom, DataDonationViewCustom

urlpatterns = [
    path('tiktok-studie/<slug:slug>/briefing/', BriefingViewCustom.as_view(), name='briefing-custom'),
    path('tiktok-studie/<slug:slug>/data-donation/', DataDonationViewCustom.as_view(), name='data-donation-custom'),
]
