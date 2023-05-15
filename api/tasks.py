import json
from datetime import datetime

import requests
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from api.models import City, Subscription, Weather
from api.serializers import WeatherSerializer


@shared_task
def send_weather_for_actual_subscriptions():
    current_hour = datetime.now().hour
    active_subs_at_current_hour = [subscription for subscription in Subscription.objects.filter(is_active=True)
                                   if current_hour % (24 // subscription.times_per_day) == 0]
    create_actual_weather_records(active_subs_at_current_hour)
    send_weather_notifications(active_subs_at_current_hour)

    return 'Weather data have been send successfully.'


def create_actual_weather_records(subs: list):
    cities_with_active_subs = City.objects.filter(subscriptions__in=subs).distinct()
    for city in cities_with_active_subs:
        Weather.objects.create_and_populate_from_api(city=city)


def send_weather_notifications(subs: list):
    for sub in subs:
        if sub.user.receive_emails:
            send_weather_via_email.delay(sub.id)

        if sub.user.webhook_url:
            send_weather_to_webhook_url.delay(sub.id)


@shared_task
def send_weather_via_email(sub_id: int):
    sub = Subscription.objects.get(id=sub_id)
    weather = Weather.objects.filter(city=sub.city).order_by('-created_at').first()
    recipient_email_address = sub.user.email
    html_message = render_to_string(
        'weather_email.html',
        {'weather': weather},
    )

    send_mail(
        subject=f'Weather Update',
        message='',
        from_email='weatherinbox.noreply@gmail.com',
        recipient_list=[recipient_email_address],
        html_message=html_message,
    )

    return f'Email for {sub.city.name} to {sub.user.email} sent at {datetime.now()}'


@shared_task
def send_weather_to_webhook_url(sub_id: int):
    sub = Subscription.objects.get(id=sub_id)
    weather = Weather.objects.filter(city=sub.city).order_by('-created_at').first()
    weather_serializer = WeatherSerializer(weather)
    weather_data_json = json.dumps(weather_serializer.data)
    url = sub.user.webhook_url
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data=weather_data_json, headers=headers)
    if response.status_code != 200:
        return response.content

    return f'Request for {sub.city.name} to {sub.user.webhook_url} sent at {datetime.now()}'
