from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable some complex features if they depend on Postgres specifics (none should for simple preview)
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1']

