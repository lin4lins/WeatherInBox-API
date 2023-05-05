import requests
from rest_framework.exceptions import NotFound
from retry import retry

from weather_reminder.settings import API_KEY, LIMIT


@retry(tries=3, delay=3)
def get_lat_lon_values(city_name: str, country_name: str) -> list:
    """
    Returns latitude and longitude of a city by the given city and country names

    Args:
        city_name: name of a city in English
        country_name: name of a country in English

    Returns: list with latitude and longitude

    """
    base_url = 'http://api.openweathermap.org/geo/1.0/direct'
    params = {'q': f'{city_name},{country_name}',
              'appid': API_KEY,
              'limit': LIMIT}
    response = requests.get(base_url, params=params)
    if response.content.decode() == '[]':
        raise NotFound({'city_name': ['Not found.']})

    return [response.json()[0].get('lat'), response.json()[0].get('lon')]


def create_weather_record(city_id: int):
    from api.models import Weather, City

    city = City.objects.get(id=city_id)
    weather_data = get_weather_data_from_api(city.latitude, city.longitude)
    main_data = weather_data.get('main')
    wind_data = weather_data.get('wind')
    clouds_data = weather_data.get('clouds')
    rain_data = weather_data.get('rain', {})
    snow_data = weather_data.get('snow', {})
    weather = Weather.objects.create(city=city,
                                     temperature=main_data.get('temp'),
                                     feels_like=main_data.get('feels_like'),
                                     min_temperature=main_data.get('temp_min'),
                                     max_temperature=main_data.get('temp_max'),
                                     wind_speed=wind_data.get('speed'),
                                     rain_1h=rain_data.get('rain_1h'),
                                     snow_1h=snow_data.get('snow_1h'),
                                     pressure=main_data.get('pressure'),
                                     humidity=main_data.get('humidity'),
                                     visibility=weather_data.get('visibility'),
                                     cloudiness=clouds_data.get('all')
                                     )
    return weather


def get_weather_data_from_api(latitude: str, longitude: str) -> dict:
    base_url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'lat': latitude,
              'lon': longitude,
              'appid': API_KEY,
              'units': 'metric'}
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise NotFound({'location': ['Not found.']})

    return response.json()
