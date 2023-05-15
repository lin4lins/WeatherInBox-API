"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_reminder.settings')

app = Celery('api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-weather-notification': {
        'task': 'api.tasks.send_weather_for_actual_subscriptions',
        'schedule': crontab(hour='*'),
    },
}
