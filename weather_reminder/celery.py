"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
import os

import django
from celery import Celery
from celery.schedules import schedule

django.setup()

from api.models import Subscription
from api.tasks import send_weather_via_email

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_reminder.settings')

app = Celery('api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    for sub in Subscription.objects.filter(is_active=True):
        task_params = {'sub_id': sub.id}
        interval_in_seconds = calculate_seconds_interval(sub.times_per_day)
        sender.add_periodic_task(
            schedule(interval_in_seconds),
            send_weather_via_email.s(task_params),
            name=f'{sub.id} sub task'
        )


def calculate_seconds_interval(frequency: int) -> int:
    total_seconds = 24 * 60 * 60
    interval_seconds = total_seconds // frequency
    return interval_seconds

