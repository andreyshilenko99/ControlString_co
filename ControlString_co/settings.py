"""
Django settings for ControlString_co project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g*kuum+*d!@-s(h8&0*#ald#4rsf-6r3z=d@fwai2a29xlhbx('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# SECRET_KEY = os.environ.get("SECRET_KEY")
#
# DEBUG = int(os.environ.get("DEBUG", default=0))
#
# # 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# # For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
# ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'leaflet',
    'map',
    'django.contrib.gis',
    'geo',
    'djgeojson'

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

ROOT_URLCONF = 'ControlString_co.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ControlString_co.wsgi.application'

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_TIMEZONE = 'Europe/Moscow'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'stuff',
        'USER': 'dron',
        'PASSWORD': '555',
        'HOST': '192.168.1.66',
        'PORT': '5432', }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': '555',
#         'HOST': '127.0.0.1',
#         'PORT': '5432', }
# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR
STATICFILES_DIRS = [
    'ControlString_co/static'
]
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LEAFLET_CONFIG = {
    'SPATIAL_EXTENT': (30.415, 59.999, 30.477, 60.022),
    'DEFAULT_CENTER': (60.013674, 30.452474),
    'RESET_VIEW': False,
    'DEFAULT_ZOOM': 16,
    'MIN_ZOOM': 10,
    'MAX_ZOOM': 18,
    'TILES': [('lol', 'http://localhost:8000/static/Tiles/{z}/{x}/{y}.png', {'attribution': '&copy; IGN'})],
    'PLUGINS': {
        'draw': {
            'css': ['/static/node_modules/leaflet-draw/dist/leaflet.draw.css',
                    '/static/node_modules/leaflet-draw/dist/leaflet.draw-src.css',
                    '/static/src/L.Icon.Pulse.css',
                    '/static/styles.css',
                    ],
            'js': ['/static/node_modules/leaflet-draw/dist/leaflet.draw.js',
                   '/static/node_modules/leaflet-draw/dist/leaflet.draw-src.js',
                   '/static/src/leaflet.sector.js',
                   '/static/src/leaflet.arc.js',
                   '/static/src/L.Realtime.js',
                   '/static/src/leaflet-realtime.js',
                   '/static/src/L.Icon.Pulse.js',
                   ],
            'auto-include': True
        },
        'ajax': {'js': ['/static/src/leaflet.ajax.js'], 'auto-include': True},
        'jquery': {'js': ['/static/src/jquery.js'], 'auto-include': True},

    }
}

SERIALIZATION_MODULES = {
    "geojson": "django.contrib.gis.serializers.geojson",
 }
