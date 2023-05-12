"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
import json
import math
import os
import time
from datetime import datetime

import django
from django.utils import timezone

django.setup()

from celery import Celery
from celery.utils.log import get_task_logger
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from api.models import Subscription

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_reminder.settings')

app = Celery('api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

logger = get_task_logger(__name__)


def schedule_new_subscription(sub_id):
    sub = Subscription.objects.get(id=sub_id)
    task_interval_seconds = calculate_task_interval_seconds(sub.times_per_day)
    interval, is_interval_created = IntervalSchedule.objects.get_or_create(every=task_interval_seconds,
                                                                           period=IntervalSchedule.SECONDS)
    PeriodicTask.objects.create(
        name=f'{sub.id}',
        task='api.tasks.send_weather_via_email',
        interval=interval,
        args=json.dumps([sub.id]),
        start_time=calculate_schedule_datetime(sub.times_per_day)
    )

    logger.info(f'Periodic task for {sub.id=} have been scheduled successfully')


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
    naive_datetime = datetime.fromtimestamp(next_schedule_timestamp)
    aware_datetime = timezone.make_aware(naive_datetime, timezone.get_default_timezone())
    return aware_datetime
