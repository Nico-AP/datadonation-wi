from django.urls import path
from dd_wi_main import views


urlpatterns = [
    path('', views.LandingView.as_view(), name='landing'),
    path('en/', views.LandingViewEn.as_view(), name='landing_en'),
    # path('wip', WipView.as_view(), name='wip'),
    path('kontakt', views.ContactView.as_view(), name='contact'),
    path('impressum', views.ImprintView.as_view(), name='imprint'),
    path('datenschutz', views.DataProtectionView.as_view(),
         name='data_protection'),
]
