from .base import *  # noqa


DEBUG = True

HOST = 'http://localhost:8000'

SECRET_KEY = 'secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tweet_monitor',
        'USER': 'vintwitta',
        'PASSWORD': 'v1ntw1tt4',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}


STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

MEDIA_ROOT = 'mediafiles'
MEDIA_URL = '/media/'

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

AUTH_PASSWORD_VALIDATORS = []  # allow easy passwords only on local

# Celery
CELERY_TASK_ALWAYS_EAGER = True

# Email
INSTALLED_APPS += ('naomi',)
EMAIL_BACKEND = 'naomi.mail.backends.naomi.NaomiBackend'
EMAIL_FILE_PATH = base_dir_join('tmp_email')

# Fix My Django
INSTALLED_APPS += ('fixmydjango',)
FIX_MY_DJANGO_ADMIN_MODE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)-8s [%(asctime)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
}
