import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# .env Datei laden
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Umgebung setzen (Standard: Produktion)
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Sicherheitseinstellungen
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
DEBUG = False

# Hosts, die erlaubt sind
ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    '34.65.209.156', 
    'videoflix.shamarisafa.ch',  
    'www.videoflix.shamarisafa.ch',
    'app.videoflix.shamarisafa.ch' 
]


CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:4200",
    "http://localhost:4200",
    "http://34.65.209.156",
    "https://videoflix.shamarisafa.ch",
    "https://www.videoflix.shamarisafa.ch",
    "https://app.videoflix.shamarisafa.ch",
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://localhost",
    "http://34.65.209.156",
    "https://videoflix.shamarisafa.ch",
    "https://www.videoflix.shamarisafa.ch",
    "https://app.videoflix.shamarisafa.ch",  
]


CORS_ALLOW_CREDENTIALS = True  
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_HEADERS = ['content-type', 'authorization', 'x-requested-with']
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']

# Cache mit Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",  # Docker-Service-Name
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "videoflix",
    }
}

RQ_QUEUES = {
    'low': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 1200,
    },
    'high': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 300,
    },
    'thumbnail': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 300,
    },
    'teaser': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 300,
    },
    'hls': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 7200,
    }
}


# Datenbank auf PostgreSQL setzen
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'videoflix'),
        'USER': os.getenv('POSTGRES_USER', 'admin'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'secret'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),  
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

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
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

# Statische Dateien & Medien
# Korrekte Staticfiles-Konfiguration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Media-Konfiguration
MEDIA_URL = '/media/' 
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


WSGI_APPLICATION = 'videoflix.wsgi.application'

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

# E-Mail-Konfiguration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "dein-email@example.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "dein-passwort")  # Nutze .env!

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Falls im DEBUG-Modus, Mails in der Konsole ausgeben
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
