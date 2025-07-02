import os
from celery import Celery

# Установите дефолтные настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system.settings')

app = Celery('system')

# Используем строку для автоимпорта, чтобы Celery сам находил задачи
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
