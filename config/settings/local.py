from .base import *


ALLOWED_HOSTS = ['127.0.0.1']

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = True

SITE_ID = 1

# DATABASE
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dd_wi.sqlite',
    }
}

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
    'CUSTOM': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_custom/vue/',
        'STATS_FILE': os.path.join(
            BASE_DIR,
            'ddm_custom/static/ddm_custom/vue/webpack-stats.json'
        ),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}

CSP_SCRIPT_SRC += ["'unsafe-eval'"]
CSP_CONNECT_SRC += ["ws://192.168.1.10:8080/ws"]
