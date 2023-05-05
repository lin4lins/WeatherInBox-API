import json

from celery import shared_task
from django.core.mail import send_mail

from api.models import Subscription
from api.serializers import WeatherSerializer
from api.utils import create_weather_record


@shared_task()
def send_weather_via_email(task_params):
    subscription = Subscription.objects.get(id=task_params.get('sub_id'))
    weather_obj = create_weather_record(subscription.city.id)
    weather_serializer = WeatherSerializer(weather_obj)
    weather_data_json = json.dumps(weather_serializer.data, indent=2)
    recipient_email_address = subscription.user.email
    send_mail(
        subject="Weather Update",
        message=weather_data_json,
        from_email='weatherinbox.noreply@gmail.com',
        recipient_list=[recipient_email_address]
    )
    return 'Success'
