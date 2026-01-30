from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database
# Use SQLite for local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Override JWT cookie settings for local development
JWT_COOKIE_SECURE = False  # Allow HTTP in development

# CORS for local frontend development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Logging in development - INFO avoids noisy DEBUG output
LOGGING["loggers"]["django"]["level"] = "INFO"  # noqa: F405
LOGGING["loggers"]["application"]["level"] = "DEBUG"  # noqa: F405

# Disable SQL query logging (set to WARNING to hide DEBUG queries)
LOGGING["loggers"]["django.db.backends"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "WARNING",
    "propagate": False,
}

# Celery - run tasks synchronously in development (no Redis needed)
# Set CELERY_BROKER_URL env var to use Redis if you have it running
if os.getenv("CELERY_BROKER_URL"):  # noqa: F405
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")  # noqa: F405
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)  # noqa: F405
else:
    # No Redis? Run tasks synchronously (eager mode)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"

# Silence Celery/Kombu connection warnings
LOGGING["loggers"]["celery"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "WARNING",
    "propagate": False,
}
LOGGING["loggers"]["kombu"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "ERROR",
    "propagate": False,
}
