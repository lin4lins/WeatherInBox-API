from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.models import City, Subscription
from api.tests import (CITY_DATA, CITY_DATA_2, KHARKIV_COORDINATES,
                       SUBSCRIPTION_DATA_EXISTING_CITY,
                       SUBSCRIPTION_DATA_NEW_CITY, UPDATED_TIMES_PER_DAY,
                       USER_DATA, create_user, login_user)


class SubscriptionViewSetTestCase(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.subscription_list_url = reverse('subscription-list')
        self.user = create_user(USER_DATA)
        self.user_token = login_user(USER_DATA)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        self.city = City.objects.create(**CITY_DATA)

    def tearDown(self):
        self.user.delete()
        self.city.delete()

    @staticmethod
    def get_subscription_detail_url(subscription_id: int):
        return reverse('subscription-detail', args=[subscription_id])

    def test_create_city_not_exists(self):
        response = self.client.post(self.subscription_list_url, data=SUBSCRIPTION_DATA_NEW_CITY, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('city').get('latitude'), KHARKIV_COORDINATES.get('latitude'))
        self.assertEqual(response.json().get('city').get('longitude'), KHARKIV_COORDINATES.get('longitude'))
        Subscription.objects.get(times_per_day=SUBSCRIPTION_DATA_NEW_CITY.get('times_per_day')).delete()
        City.objects.get(name=SUBSCRIPTION_DATA_NEW_CITY.get('city').get('name')).delete()

    def test_create_city_exists(self):
        response = self.client.post(self.subscription_list_url, data=SUBSCRIPTION_DATA_EXISTING_CITY, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('city').get('latitude'), str(self.city.latitude))
        self.assertEqual(response.json().get('city').get('longitude'), str(self.city.longitude))
        self.assertEqual(City.objects.count(), 1)
        Subscription.objects.get(times_per_day=SUBSCRIPTION_DATA_NEW_CITY.get('times_per_day')).delete()

    def test_create_subscription_exists(self):
        subscription = Subscription.objects.create(user=self.user, city=self.city, times_per_day=6)
        response = self.client.post(self.subscription_list_url, data=SUBSCRIPTION_DATA_EXISTING_CITY, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail'), 'The subscription with this fields already exists.')
        subscription.delete()

    def test_update(self):
        subscription_data = SUBSCRIPTION_DATA_EXISTING_CITY.copy()
        subscription_data['times_per_day'] = UPDATED_TIMES_PER_DAY
        subscription = Subscription.objects.create(user=self.user, city=self.city, times_per_day=6)
        response = self.client.put(self.get_subscription_detail_url(subscription.id), data=subscription_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('times_per_day'), UPDATED_TIMES_PER_DAY)
        subscription.delete()

    def test_update_with_changed_city(self):
        subscription_data = SUBSCRIPTION_DATA_EXISTING_CITY.copy()
        subscription_data['times_per_day'] = UPDATED_TIMES_PER_DAY
        subscription_data['city'] = CITY_DATA_2
        subscription = Subscription.objects.create(user=self.user, city=self.city, times_per_day=6)
        response = self.client.put(self.get_subscription_detail_url(subscription.id), data=subscription_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail'), 'Changing the subscription city is not available.')
        subscription.delete()

    def test_partial_update(self):
        subscription = Subscription.objects.create(user=self.user, city=self.city, times_per_day=6)
        response = self.client.patch(self.get_subscription_detail_url(subscription.id),
                                     data={'times_per_day': UPDATED_TIMES_PER_DAY}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('times_per_day'), UPDATED_TIMES_PER_DAY)
        subscription.delete()

    def test_partial_update_with_city(self):
        subscription_data = SUBSCRIPTION_DATA_EXISTING_CITY.copy()
        subscription_data['times_per_day'] = UPDATED_TIMES_PER_DAY
        subscription = Subscription.objects.create(user=self.user, city=self.city, times_per_day=6)
        response = self.client.patch(self.get_subscription_detail_url(subscription.id),
                                     data=subscription_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('detail'), 'Changing the subscription city is not available.')
        subscription.delete()
