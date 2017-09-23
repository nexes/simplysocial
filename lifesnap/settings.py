"""
Django settings for lifesnap project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import json


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

try:
    with open('supertopsecretprivatesettings.json') as f:
        try:
            SETTINGS = json.load(f)
        except json.JSONDecodeError as err:
            print('JSONDecoder error: {}'.format(err))
        else:
            SECRET_KEY = SETTINGS['SECRET_KEY']
            DEBUG = SETTINGS['DEBUG']
            DEPLOY = SETTINGS['DEPLOY']
            ALLOWED_HOSTS = SETTINGS['ALLOWED_HOSTS']
            EMAIL_HOST = SETTINGS['EMAIL_HOST']
            EMAIL_HOST_USER = SETTINGS['EMAIL_USER']
            EMAIL_HOST_PASSWORD = SETTINGS['EMAIL_PASSWORD']
            EMAIL_PORT = SETTINGS['EMAIL_PORT']
            EMAIL_USE_TLS = SETTINGS['EMAIL_TLS']
except FileNotFoundError:
    # our file is not found, we may be deployed and env variables may be set
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    DEBUG = os.getenv('DEBUG', '')
    DEPLOY = os.getcwd('DEPLOY', False)
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '')
    EMAIL_HOST = os.getenv('EMAIL_HOST', '')
    EMAIL_HOST_USER = os.getenv('EMAIL_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_PORT = os.getenv('EMAIL_PORT', '')
    EMAIL_USE_TLS = os.getenv('EMAIL_TLS', '')


# Application definition

INSTALLED_APPS = [
    'userauth.apps.AuthConfig',
    'user.apps.UserConfig',
    'post.apps.PostConfig',
    'comment.apps.CommentConfig',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'lifesnap-frontend.herokuapp.com'
]
CSRF_TRUSTED_ORIGINS = [
    'lifesnap-frontend.herokuapp.com'
]

ROOT_URLCONF = 'lifesnap.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'lifesnap.wsgi.application'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': '5432'
    }
}

# if we are deployed, we set our database vars this way

if SETTINGS['DEPLOY']:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config()

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Boise'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'