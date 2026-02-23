from .base import *  # noqa: F401,F403
from .base import INSTALLED_APPS, MIDDLEWARE, BASE_DIR

DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [  # noqa: F405
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405

INTERNAL_IPS = ['127.0.0.1', '0.0.0.0']

# Email — catch all emails in Mailpit
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

# Simplified static files for development
STORAGES = {
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
