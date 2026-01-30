import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
# BASE_DIR points to the project root (where manage.py is)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-production")

# Application definition
INSTALLED_APPS = [
    # Django built-in apps (minimal set for API-only)
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # Our infrastructure app
    "infrastructure.django.apps.InfrastructureConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    # Note: We use our own auth middleware, not Django's session-based auth
    "infrastructure.web.middleware.auth_middleware.JWTAuthMiddleware",
]

ROOT_URLCONF = "interface.api.urls"

# Templates (minimal for admin-only use if needed)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

# WSGI application
WSGI_APPLICATION = "infrastructure.django.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Custom User Model
# This is the Django model that adapts our domain User entity
AUTH_USER_MODEL = "django_infra.UserModel"

# We disable Django's session-based authentication backends
# because we're using JWT cookies
AUTHENTICATION_BACKENDS = []

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# JWT Configuration
# =============================================================================
JWT_ACCESS_TOKEN_LIFETIME = int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME", "900"))  # 15 minutes
JWT_REFRESH_TOKEN_LIFETIME = int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME", "604800"))  # 7 days
JWT_ALGORITHM = "HS256"

# =============================================================================
# Celery Configuration
# =============================================================================
CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0")
)
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0")
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# =============================================================================
# Cookie Settings for JWT
# =============================================================================
JWT_COOKIE_SECURE = True  # Override to False in local.py
JWT_COOKIE_HTTPONLY = True
JWT_COOKIE_SAMESITE = "Lax"
JWT_ACCESS_COOKIE_NAME = "access_token"
JWT_REFRESH_COOKIE_NAME = "refresh_token"

# =============================================================================
# CORS Settings (for SPA frontends)
# =============================================================================
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOW_CREDENTIALS = True  # Required for cookies

# =============================================================================
# Logging
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "application": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
