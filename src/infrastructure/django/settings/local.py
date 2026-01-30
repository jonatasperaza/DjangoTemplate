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

# More verbose logging in development
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["application"]["level"] = "DEBUG"  # noqa: F405

# Celery - use Redis or in-memory broker for local
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")  # noqa: F405
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")  # noqa: F405

# For easier debugging - eager execution (tasks run synchronously)
# Uncomment if you don't have Redis running locally
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True
