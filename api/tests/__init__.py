from django.urls import reverse
from rest_framework.test import APIClient

from api.models import User

USER_DATA = {'username': 'test',
             'password': '12TestPassword12',
             'first_name': 'Test',
             'last_name': 'Tester',
             'email': 'test@gmail.com'}
USER_DATA_2 = {'username': 'test2',
               'password': '12TestPassword12',
               'first_name': 'Test2',
               'last_name': 'Tester2',
               'email': 'test2@gmail.com'}
INVALID_PASSWORD = 'abc'
UPDATED_USERNAME = 'updated_username'
UPDATED_TIMES_PER_DAY = 8
ADMIN_DATA = {'username': 'admin',
              'password': '12AdminPassword12',
              'first_name': 'Admin',
              'last_name': 'Adminer',
              'email': 'admin@gmail.com',
              'is_staff': True}
CITY_DATA = {'name': 'Kyiv',
             'country_name': 'Ukraine'}
CITY_DATA_2 = {'name': 'Kharkiv',
               'country_name': 'Ukraine'}
INVALID_CITY_DATA = {'name': 'Kyiv',
                     'country_name': 'Test'}
SUBSCRIPTION_DATA_NEW_CITY = {'city':
                                  {'name': 'Kharkiv',
                                   'country_name': 'Ukraine'},
                              'times_per_day': '6'}
SUBSCRIPTION_DATA_EXISTING_CITY = {'city': CITY_DATA,
                                   'times_per_day': '6'}
KYIV_COORDINATES = {'latitude': '50.4500336', 'longitude': '30.5241361'}
KHARKIV_COORDINATES = {'latitude': '49.9923181', 'longitude': '36.2310146'}


def create_user(data: dict) -> User:
    user = User.objects.create(**data)
    user.set_password(data.get('password'))
    user.save()
    return user


def login_user(data: dict) -> str:
    client = APIClient()
    url = reverse('token_obtain_pair')
    response = client.post(url, data={'username': data.get('username'), 'password': data.get('password')},
                           format='json')
    return response.json().get('access')
