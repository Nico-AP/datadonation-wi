from .base import *
import os


ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split()

SITE_ID = 1

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = False


# SECURITY SETTINGS
# ------------------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# DATABASE
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DJANGO_DB_ENGINE'),
        'HOST': os.environ.get('DJANGO_DB_HOST'),
        'PORT': os.environ.get('DJANGO_DB_PORT'),
        'NAME': os.environ.get('DJANGO_DB_NAME'),
        'USER': os.environ.get('DJANGO_DB_USER'),
        'PASSWORD': os.environ.get('DJANGO_DB_PW'),
    }
}
