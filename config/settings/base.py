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
    'django_celery_results',
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
    'csp.middleware.CSPMiddleware',
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
        'STATS_FILE': os.path.join(
            STATIC_ROOT,
            'ddm_core/vue/webpack-stats.json'
        ),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    },
}
DDM_SETTINGS = {
    'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)weizenbaum-institut\.de$',
}

DDM_DEFAULT_HEADER_IMG_LEFT = '/static/dd_wi_main/img/logos/wzb_logo.svg'
DDM_DEFAULT_HEADER_IMG_RIGHT = '/static/dd_wi_main/img/logos/ddlab_logo_black.svg'


ATTRIBUTES_TO_ALLOW = {
    'href': True,
    'target': True,
    'rel': True,
    'class': True,
    'aria-label': True,
    'data-*': True,
    'id': True,
    'type': True,
    'data-bs-toggle': True,
    'data-bs-target': True,
    'data-bs-parent': True,
    'aria-expanded': True,
    'aria-controls': True,
    'aria-labelledby': True,
}

CKEDITOR_5_CONFIGS = {
    'ddm_ckeditor':  {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': [
            'heading', '|',
            'alignment', 'outdent', 'indent', '|',
            'bold', 'italic', 'underline', 'link', 'highlight', '|',
            {
                'label': 'Fonts',
                'icon': 'text',
                'items': ['fontSize', 'fontFamily', 'fontColor']
            }, '|',
            'bulletedList', 'numberedList', 'insertTable', 'blockQuote', 'code', 'removeFormat', '|',
            'insertImage', 'fileUpload', 'mediaEmbed', '|',
            'sourceEditing'
        ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
        },
        'heading': {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        },
        'htmlSupport': {
            'allow': [
                {
                    'name': 'video',
                    'attributes': {
                        'height': True,
                        'width': True,
                        'controls': True,
                    },
                    'styles': True
                },
                {
                    'name': 'p',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'span',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'div',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'a',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'table',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'td',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'th',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'button',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'h1',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'h2',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'style',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
            ],
            'disallow': []
        },
        'wordCount': {
            'displayCharacters': False,
            'displayWords': False,
        }
    }
}


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


# CACHE
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': os.getenv(
            'CACHE_BACKEND',
            'django.core.cache.backends.filebased.FileBasedCache'
        ),
        'LOCATION': os.getenv('CACHE_LOCATION', 'django_cache'),
        'TIMEOUT': 86400,  # 24 hours
        'OPTIONS': {}
    }
}


# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'datadlab.log'),
            'maxBytes': 1024*1024*15,
            'formatter': 'verbose'
        },
        'api_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'scraper/api.log'),
            'formatter': 'verbose'
        },
        'scraper_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'scraper/scraper.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'api_logger': {
            'handlers': ['api_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'scraper_logger': {
            'handlers': ['scraper_file'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


# CELERY
# -----------------------------------------------------------------------------
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_DEFAULT_QUEUE = os.environ.get('CELERY_TASK_DEFAULT_QUEUE')


# django-cookie-consent
# -----------------------------------------------------------------------------
COOKIE_CONSENT = {
    "DECLARATIONS": {
        "analytics": {
            "name": "Analytics",
            "description": "Cookies used for tracking analytics (e.g., Matomo)",
            "cookies": ["matomo"],
            "is_required": False,
        }
    }
}
