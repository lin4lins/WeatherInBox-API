from datetime import datetime

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from retry import retry

from api.models import Subscription, Weather


@retry(tries=2, delay=3)
@shared_task
def send_weather_via_email(sub_id: int):
    subscription = Subscription.objects.get(id=sub_id)
    weather_obj, created = Weather.objects.get_or_create(city=subscription.city)
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

    return f"{subscription.city} data sent at {datetime.now()}"
