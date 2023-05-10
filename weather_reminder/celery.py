"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
import json
import math
import os
import time
from datetime import datetime

import django

django.setup()


from celery import Celery, signals
from celery.utils.log import get_task_logger
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from api.models import Subscription

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_reminder.settings')

app = Celery('api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

logger = get_task_logger(__name__)


@signals.worker_ready.connect
def schedule_active_subscriptions(sender, **kwargs):
    for sub in Subscription.objects.filter(is_active=True):
        task_interval_seconds = calculate_task_interval_seconds(sub.times_per_day)
        task_params = {'sub_id': sub.id}

        interval, is_interval_created = IntervalSchedule.objects.get_or_create(
            every=task_interval_seconds,
            period=IntervalSchedule.SECONDS)

        periodic_task, is_task_created = PeriodicTask.objects.get_or_create(
            name=f'Sub №{sub.id} on-startup send email',
            task='api.tasks.send_weather_via_email',
            interval=interval,
            kwargs=json.dumps(task_params),
        )

        if is_task_created:
            periodic_task.start_time = calculate_schedule_datetime(sub.times_per_day)
            periodic_task.save()


def calculate_task_interval_seconds(task_frequency: int) -> float:
    seconds_in_day = 24 * 60 * 60
    task_interval_seconds = seconds_in_day / task_frequency
    return task_interval_seconds


def calculate_schedule_datetime(task_frequency: int) -> datetime:
    """
    Calculates the next scheduled datetime for a task given its frequency in a day.

    Args:
        task_frequency: Number of times the task is scheduled to run per day.

    Returns:
        datetime: Next scheduled datetime for the task.
    """
    current_timestamp = time.time()
    today_midnight = datetime.combine(datetime.today(), datetime.min.time())
    today_midnight_timestamp = today_midnight.timestamp()

    task_interval_seconds = calculate_task_interval_seconds(task_frequency)
    elapsed_seconds_since_midnight = current_timestamp - today_midnight_timestamp
    next_task_index = math.ceil(elapsed_seconds_since_midnight / task_interval_seconds)
    next_task_time_seconds = task_interval_seconds * next_task_index
    next_schedule_timestamp = next_task_time_seconds + today_midnight_timestamp
    return datetime.fromtimestamp(next_schedule_timestamp)
