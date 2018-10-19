import os

SECRET_KEY = 'dummy-key'

ROOT_URLCONF = 'wagtail_checklist.urls'

INSTALLED_APPS = [
    'wagtail.core',
    'wagtail.admin',
    'rest_framework',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}
