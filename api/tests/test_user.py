from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.models import User
from api.tests import (UPDATED_USERNAME, USER_DATA, USER_DATA_2, create_user,
                       login_user)


class UserViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_list_url = reverse('user-list')

    @staticmethod
    def get_user_detail_url(user_id: int):
        return reverse('user-detail', args=[user_id])

    def test_create(self):
        response = self.client.post(self.user_list_url, data=USER_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('password', None), None)

        User.objects.get(username=USER_DATA.get('username')).delete()

    def test_create_invalid_email(self):
        user_data = USER_DATA.copy()
        user_data['email'] = 'test_email'
        response = self.client.post(self.user_list_url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('email')[0], 'Enter a valid email address.')

    def test_create_not_unique_credentials(self):
        user = create_user(USER_DATA)
        response = self.client.post(self.user_list_url, data=USER_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('username')[0], 'A user with that username already exists.')
        user.delete()

    def test_retrieve(self):
        user = create_user(USER_DATA)
        token = login_user(USER_DATA)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.get_user_detail_url(user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.delete()

    def test_retrieve_not_authenticated(self):
        user = create_user(USER_DATA)
        response = self.client.get(self.get_user_detail_url(user.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        user.delete()

    def test_retrieve_other_user(self):
        user = create_user(USER_DATA)
        user_2 = create_user(USER_DATA_2)
        token = login_user(USER_DATA)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.get_user_detail_url(user_2.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        user_2.delete()
        user.delete()

    def test_update(self):
        user = create_user(USER_DATA)
        token = login_user(USER_DATA)
        user_data = USER_DATA.copy()
        user_data['username'] = UPDATED_USERNAME
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.put(self.get_user_detail_url(user.id), data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('username'), UPDATED_USERNAME)
        user.delete()

    def test_partial_update(self):
        user = create_user(USER_DATA)
        token = login_user(USER_DATA)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.patch(self.get_user_detail_url(user.id), data={'username': UPDATED_USERNAME},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('username'), UPDATED_USERNAME)
        user.delete()

    def test_list(self):
        user = create_user(USER_DATA)
        user_2 = create_user(USER_DATA_2)
        token = login_user(USER_DATA)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.user_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        user_2.delete()
        user.delete()

    def test_delete(self):
        user = create_user(USER_DATA)
        token = login_user(USER_DATA)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.delete(self.get_user_detail_url(user.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_user(self):
        user = create_user(USER_DATA)
        user_2 = create_user(USER_DATA_2)
        token = login_user(USER_DATA)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.delete(self.get_user_detail_url(user_2.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        user_2.delete()
        user.delete()
