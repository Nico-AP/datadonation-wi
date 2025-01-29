from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include


urlpatterns = [
    path('wi-admin/', admin.site.urls),
    path('ddm/', include('ddm.core.urls')),
    path('ddm/login/', auth_views.LoginView.as_view(template_name='ddm_auth/login.html'), name='ddm_login'),
    path('ddm/logout/', auth_views.LogoutView.as_view(), name='ddm_logout'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]
