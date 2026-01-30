import os
import sys
from pathlib import Path

from celery import Celery

# Add src to path
src_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(src_path))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infrastructure.django.settings.local")

# Create Celery app
app = Celery("django_hexagonal")

# Load config from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in infrastructure.messaging.tasks
app.autodiscover_tasks(
    [
        "infrastructure.messaging.tasks",
    ]
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery is working."""
    print(f"Request: {self.request!r}")
