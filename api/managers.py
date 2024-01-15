from django.db import models

from api.utils import get_lat_lon_values, get_weather_data_from_api


class CityManager(models.Manager):
    def create(self, **kwargs):
        city = self.model(**kwargs)
        city.latitude, city.longitude = get_lat_lon_values(city.name, city.country_name)
        city.save()
        return city


class WeatherManager(models.Manager):
    def create_and_populate_from_api(self, **kwargs):
        weather_entry = self.model(**kwargs)
        weather_api_response = get_weather_data_from_api(weather_entry.city.latitude, weather_entry.city.longitude)

        weather_conditions = weather_api_response.get('weather')[0]
        atmospheric_conditions = weather_api_response.get('main')
        wind_conditions = weather_api_response.get('wind')
        cloud_conditions = weather_api_response.get('clouds')
        rain_conditions = weather_api_response.get('rain', {})
        snow_conditions = weather_api_response.get('snow', {})

        weather_entry.status = weather_conditions.get('main')
        weather_entry.status_description = weather_conditions.get('description')
        weather_entry.temperature = atmospheric_conditions.get('temp')
        weather_entry.feels_like = atmospheric_conditions.get('feels_like')
        weather_entry.wind_speed = wind_conditions.get('speed')
        weather_entry.rain_1h = rain_conditions.get('1h')
        weather_entry.snow_1h = snow_conditions.get('1h')
        weather_entry.pressure = atmospheric_conditions.get('pressure')
        weather_entry.humidity = atmospheric_conditions.get('humidity')
        weather_entry.visibility = weather_api_response.get('visibility')
        weather_entry.cloudiness = cloud_conditions.get('all')
        weather_entry.save()
        return weather_entry
