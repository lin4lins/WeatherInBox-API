from datetime import timedelta

from django.db import models
from django.utils import timezone

from api.utils import get_lat_lon_values, get_weather_data_from_api


class CityManager(models.Manager):
    def create(self, **kwargs):
        city = self.model(**kwargs)
        city.latitude, city.longitude = get_lat_lon_values(city.name, city.country_name)
        city.save()
        return city


class WeatherManager(models.Manager):
    def create(self, **kwargs):
        weather = self.model(**kwargs)
        weather_data = get_weather_data_from_api(weather.city.latitude, weather.city.longitude)
        main_data = weather_data.get('main')
        wind_data = weather_data.get('wind')
        clouds_data = weather_data.get('clouds')
        rain_data = weather_data.get('rain', {})
        snow_data = weather_data.get('snow', {})

        weather.temperature = main_data.get('temp')
        weather.feels_like = main_data.get('feels_like')
        weather.min_temperature = main_data.get('temp_min')
        weather.max_temperature = main_data.get('temp_max')
        weather.wind_speed = wind_data.get('speed')
        weather.rain_1h = rain_data.get('rain_1h')
        weather.snow_1h = snow_data.get('snow_1h')
        weather.pressure = main_data.get('pressure')
        weather.humidity = main_data.get('humidity')
        weather.visibility = weather_data.get('visibility')
        weather.cloudiness = clouds_data.get('all')
        weather.save()
        return weather

    def get_or_create(self, **kwargs):
        weather = self.model(**kwargs)
        current_time_utc = timezone.now()
        one_hour_ago = current_time_utc - timedelta(hours=1)
        weather = self.model.objects.filter(city=weather.city, created_at__gte=one_hour_ago).order_by('-created_at').first()
        if not weather:
            print('new')
            return self.create(**kwargs), True

        print('old')
        return weather, False
