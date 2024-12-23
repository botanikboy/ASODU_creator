import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', default=get_random_secret_key())

DEBUG = os.getenv('DEBUG_MODE', default=True) in (True, 'True', 'true', '1')


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '*',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'panels.apps.PanelsConfig',
    'core.apps.CoreConfig',
    'django_bootstrap5',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'ASODU.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.year.year',
            ],
        },
    },
]

WSGI_APPLICATION = 'ASODU.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', default='mydatabase'),
        'USER': os.getenv('POSTGRES_USER', default='postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
        'HOST': os.getenv('DB_HOST', default='localhost'),
        'PORT': os.getenv('DB_PORT', default='5432')
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = os.getenv('TIME_ZONE', default='UTC')

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_dev')]

CSRF_TRUSTED_ORIGINS = ['https://159.89.213.155/*', "http://localhost/*",]

LOGIN_URL = 'users:login'

LOGIN_REDIRECT_URL = 'panels:index'

if not DEBUG:
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = os.getenv('EMAIL_PORT')
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', default=True) in (True, 'True', 'true', '1')
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

OBJECTS_COUNT_ON_PAGE = 10

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', default='NOT_FOUND')

CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', default='NOT_FOUND')

CELERY_IMPORTS = ('panels.tasks', )

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_CACHE', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_TIMEZONE = TIME_ZONE

CELERY_ENABLE_UTC = False
