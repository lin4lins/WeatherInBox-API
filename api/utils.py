import pycountry as pycountry
import requests
from rest_framework.exceptions import NotFound

from weather_reminder.settings import API_KEY, LIMIT


def get_country_code(country_name: str) -> str:
    """
    Returns the ISO 3166-1 alpha-2 country code for the given country name.

    Args:
        country_name: name of a country in English

    Returns: the ISO 3166-1 alpha-2 country code

    """
    country = pycountry.countries.get(name=country_name)
    if not country:
        raise NotFound()

    return country.alpha_2


def get_lat_lon_values(city_name: str, country_name: str) -> list:
    """
    Returns latitude and longitude of a city by the given city and country names

    Args:
        city_name: name of a city in English
        country_name: name of a country in English

    Returns: list with latitude and longitude

    """
    base_url = 'http://api.openweathermap.org/geo/1.0/direct'
    country_code = get_country_code(country_name)
    params = {'q': f'{city_name},{country_code}',
              'appid': API_KEY,
              'limit': LIMIT}
    response = requests.get(base_url, params=params)
    if len(response.content) == 0:
        raise NotFound()

    return [response.json()[0].get('lat'), response.json()[0].get('lon')]
