import os

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hosts/domain names that are valid for this site
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Database
# Use PostgreSQL in production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "django_hexagonal"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# Alternative: Use DATABASE_URL if provided (common in cloud platforms)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(DATABASE_URL, conn_max_age=60)

# =============================================================================
# Security Settings
# =============================================================================

# HTTPS settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Other security
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# JWT Cookies must be secure in production
JWT_COOKIE_SECURE = True
JWT_COOKIE_SAMESITE = "Strict"

# =============================================================================
# CORS
# =============================================================================
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# Caching (use Redis)
# =============================================================================
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# =============================================================================
# Celery (use Redis)
# =============================================================================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# =============================================================================
# Logging
# =============================================================================
LOGGING["handlers"]["file"] = {  # noqa: F405
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.getenv("LOG_FILE", "/var/log/app/django.log"),
    "maxBytes": 10 * 1024 * 1024,  # 10 MB
    "backupCount": 5,
    "formatter": "verbose",
}
LOGGING["root"]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["loggers"]["django"]["level"] = "WARNING"  # noqa: F405
