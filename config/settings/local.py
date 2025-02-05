from .base import *


ALLOWED_HOSTS = []

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
}
