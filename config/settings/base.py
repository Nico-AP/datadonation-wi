import os

from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

# APPLICATION DEFINITIONS
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET')

INSTALLED_APPS = [
    'dd_wi_main.apps.DDWIMainConfig',
    'reports.apps.DDWIReportsConfig',
    'scraper.apps.DDWIScraperConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'ddm',
    'ddm.apis',
    'ddm.auth',
    'ddm.logging',
    'ddm.questionnaire',
    'ddm.datadonation',
    'ddm.participation',
    'ddm.projects',
    'ddm.core',
    'django_ckeditor_5',
    'webpack_loader',
    'rest_framework',
    'rest_framework.authtoken',
    'cookie_consent',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware'
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'ddm.core.context_processors.add_ddm_version',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# USER AUTHORIZATION AND PASSWORD VALIDATION
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = 'dd_wi_main.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# INTERNATIONALIZATION
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Zurich'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# STATIC FILES
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# DEFAULT PRIMARY KEY FIELD TYPE
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

X_FRAME_OPTIONS = 'SAMEORIGIN'


# Authentication
# ------------------------------------------------------------------------------
LOGIN_REDIRECT_URL = '/ddm/projects/'
LOGOUT_REDIRECT_URL = '/ddm/login/'


# DJANGO-DDM
# ------------------------------------------------------------------------------
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/vue/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm_core/vue/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    },
}
DDM_SETTINGS = {
    'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)uzh\.ch$',
}

DDM_DEFAULT_HEADER_IMG_LEFT = '/static/dd_wi_main/img/logos/some-logo.svg'
DDM_DEFAULT_HEADER_IMG_RIGHT = '/static/dd_wi_main/img/logos/some-other-logo.svg'

# CKEditor
# ------------------------------------------------------------------------------
CKEDITOR_5_FILE_UPLOAD_PERMISSION = 'authenticated'
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'png', 'mp4']

# Django Rest Framework
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# Django CSP
# ------------------------------------------------------------------------------
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'"]
CSP_SCRIPT_SRC_ELEM = ["'self'", "'unsafe-inline'"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_STYLE_SRC_ATTR = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", "data:"]

# Report Configuration
# ------------------------------------------------------------------------------
# Instagram Report
REPORT_PROJECT_PK = os.getenv('REPORT_PROJECT_PK', None)
REPORT_API_KEY = os.getenv('REPORT_API_KEY', None)
