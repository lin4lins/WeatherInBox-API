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
