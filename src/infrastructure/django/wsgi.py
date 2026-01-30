import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(src_path))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infrastructure.django.settings.production")

application = get_wsgi_application()
