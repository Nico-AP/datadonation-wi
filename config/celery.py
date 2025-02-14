import os
from celery import Celery
from dotenv import load_dotenv


load_dotenv()

# Set default settings for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app_name = os.environ.get('CELERY_APP_NAME', 'config')
app = Celery(app_name)

# Load task modules from all registered Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()
