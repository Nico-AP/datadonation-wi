import socket

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponseForbidden
from django.urls import path, include


def restrict_to_localhost(get_response):
    def middleware(request):
        client_ip = request.META.get('REMOTE_ADDR', "")
        allowed_ips = ['127.0.0.1', '::1']

        # Also allow the server's local IP.
        allowed_ips.append(socket.gethostbyname(socket.gethostname()))

        if client_ip not in allowed_ips:
            return HttpResponseForbidden("Access Denied")

        return get_response(request)

    return middleware


urlpatterns = [
    path('', include('dd_wi_main.urls')),
    path('', include('reports.urls')),
    path('wi-admin/', admin.site.urls),
    path('ddm/', include('ddm.core.urls')),
    path('ddm/login/', auth_views.LoginView.as_view(
        template_name='ddm_auth/login.html'), name='ddm_login'),
    path('ddm/logout/', auth_views.LogoutView.as_view(), name='ddm_logout'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('cookies/', include('cookie_consent.urls')),
    path('scraper/', include('scraper.urls')),
    path('', restrict_to_localhost(include('django_prometheus.urls'))),
]

if settings.DEBUG:
    urlpatterns += \
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'dd_wi_main.views.custom_404_view'
handler500 = 'dd_wi_main.views.custom_500_view'
