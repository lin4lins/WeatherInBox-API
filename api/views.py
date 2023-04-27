from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from api.exceptions import CityChangingUnavailable, SubscriptionAlreadyExists
from api.models import City, Subscription, User
from api.serializers import (CitySerializer, SubscriptionSerializer,
                             UserSerializer)

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        This view allows the user to access his own data only.
        """
        user = self.request.user
        return User.objects.filter(id=user.id)


class CityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = CitySerializer
    queryset = City.objects.all()


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing subscriptions.

    Note: The 'city' field cannot be updated once a subscription is created:

    - update:
    Updates an existing subscription. 'City' field is required in request.
    Whether there are some changes in 'city' detected, raises CityChangingUnavailable.

    - partial_update:
    Updates one or more fields of an existing subscription.
    Whether there is 'city' field in a request, raises CityChangingUnavailable.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        """
        This view returns a list of all the subscriptions for the currently authenticated user.
        """
        user = self.request.user
        return Subscription.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)

        except IntegrityError:
            raise SubscriptionAlreadyExists()

    def partial_update(self, request, *args, **kwargs):
        is_city_data_in_request = request.data.get('city', False)
        if is_city_data_in_request:
            raise CityChangingUnavailable()

        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        city_data = request.data.get('city')
        try:
            city = City.objects.get(**city_data)
        except City.DoesNotExist:
            raise CityChangingUnavailable()

        if city.name != city_data.get('name') or city.country_name != city_data.get('country_name'):
            raise CityChangingUnavailable()

        return super().update(request, *args, **kwargs)
