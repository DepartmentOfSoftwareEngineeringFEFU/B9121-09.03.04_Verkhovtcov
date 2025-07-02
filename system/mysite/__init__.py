from os import environ
from .celery import app as celery_app
from django import setup

environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

__all__ = ('celery_app',)

setup()
