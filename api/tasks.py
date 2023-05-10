import json
from datetime import datetime

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from api.models import Subscription
from api.utils import create_weather_record


@shared_task
def send_weather_via_email(sub_id: int):
    subscription = Subscription.objects.get(id=sub_id)
    weather_obj = create_weather_record(subscription.city.id)
    recipient_email_address = subscription.user.email
    html_message = render_to_string(
        "weather_email.html",
        {"weather": weather_obj},
    )

    send_mail(
        subject=f"Weather Update",
        message='',
        from_email='weatherinbox.noreply@gmail.com',
        recipient_list=[recipient_email_address],
        html_message=html_message,
    )

    return f"Sent at {datetime.now()}"
