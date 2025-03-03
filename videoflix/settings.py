import os
from pathlib import Path
# from dotenv import load_dotenv
from datetime import timedelta

# load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Umgebung setzen (Standard: Entwicklung)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Sicherheitseinstellungen
SECRET_KEY = 'django-insecure-2h6wblj2-bi4$06xf2%g_atpn+!wo#(qw%dj8vl!hc519b7qf^'
DEBUG = ENVIRONMENT != "production"

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:4200",
    "http://localhost:4200",
]

CACHE_TTL = 60 * 15

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'django_rq',
    'corsheaders',

    'userAuth',
    'videos.apps.VideosConfig',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1',
    'http://localhost',
]

CORS_ALLOW_CREDENTIALS = True  

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:4200",
    "http://localhost:4200",
]

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]


# Caching mit Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "videoflix",
    }
}

# RQ-Queue für Hintergrundjobs
RQ_QUEUES = {
    'low': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 1200,
    },
    'high': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 300,
    }
}

ROOT_URLCONF = 'videoflix.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Media-Dateien für Uploads
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

WSGI_APPLICATION = 'videoflix.wsgi.application'

# Lokale Entwicklung mit SQLite, später Wechsel auf PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Später in Produktion auf PostgreSQL umstellen:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB', 'postgres'),
#         'USER': os.getenv('POSTGRES_USER', 'postgres'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
#         'HOST': os.getenv('POSTGRES_HOST', 'postgres'),
#         'PORT': os.getenv('POSTGRES_PORT', '5432'),
#     }
# }

# Passwort-Validierung
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

# REST API Authentifizierung mit JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# E-Mail-Einstellungen für das Versenden von Mails
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Ändere dies entsprechend deines Mailservers
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "dein-email@example.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "dein-passwort")  # Nutze Umgebungsvariablen!

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Entwicklungsmodus: E-Mails nur in der Konsole anzeigen
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
