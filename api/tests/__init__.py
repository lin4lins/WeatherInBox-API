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
UPDATED_TIMES_PER_DAY = 12
ADMIN_DATA = {'username': 'admin',
              'password': '12AdminPassword12',
              'first_name': 'Admin',
              'last_name': 'Adminer',
              'email': 'admin@gmail.com',
              'is_staff': True}
CITY_DATA = {'name': 'Kyiv',
             'country_name': 'Ukraine'}


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
