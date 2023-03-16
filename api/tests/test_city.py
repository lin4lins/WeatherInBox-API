from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.models import City
from api.tests import (ADMIN_DATA, CITY_DATA, INVALID_CITY_DATA,
                       KYIV_COORDINATES, create_user, login_user)


class CityViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.city_list_url = reverse('city-list')
        self.admin = create_user(ADMIN_DATA)
        self.admin_token = login_user(ADMIN_DATA)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)

    def tearDown(self):
        self.admin.delete()

    def test_create(self):
        response = self.client.post(self.city_list_url, data=CITY_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('latitude'), KYIV_COORDINATES.get('latitude'))
        self.assertEqual(response.json().get('longitude'), KYIV_COORDINATES.get('longitude'))
        City.objects.get(name=CITY_DATA.get('name')).delete()

    def test_create_not_unique_city_country_set(self):
        city = City.objects.create(**CITY_DATA)
        response = self.client.post(self.city_list_url, data=CITY_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('non_field_errors')[0],
                         'The fields name, country_name must make a unique set.')
        city.delete()

    def test_create_invalid_city(self):
        response = self.client.post(self.city_list_url, data=INVALID_CITY_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
