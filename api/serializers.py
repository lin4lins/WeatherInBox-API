from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api.models import City, Subscription, User


class UserSerializer(serializers.ModelSerializer):
    """
        A serializer class for User objects.

        Fields:
        - username (required): The user's username.
        - password (write-only): The user's password, in plain text.
                                 This field is write-only, and is hashed before being stored in the database.
        - first_name (optional): The user's first name.
        - last_name (optional): The user's last name.
        - email (optional): The user's email address.
        - webhook_url (optional): A webhook URL associated with the user.
        - receive_emails (optional): A boolean which means whether the user wants to receive weather updates wia email.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'webhook_url', 'receive_emails']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class CitySerializer(serializers.ModelSerializer):
    """
    A serializer class for City objects.

    Fields:
    - name (required): The name of the city.
    - country_name (required): The name of the country the city is located in.
    - latitude (read-only): The latitude of the city's location.
                            This field is read-only, and is filled before being stored in the database.
    - longitude (read-only): The longitude of the city's location.
                             This field is read-only, and is filled before being stored in the database.
    """
    class Meta:
        model = City
        fields = '__all__'
        read_only_fields = ['latitude', 'longitude']


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    A serializer class for Subscription objects.

    Fields:
    - user(read-only): A nested object representing the user which owns this subscription.
                       This field is read-only, and is taken from the context of the query.
    - city (read-only): A nested object representing the city the user is subscribed to.
    - times_per_day: The number of times per day the user wishes to receive notifications for this subscription.
    - is_active: A boolean, which says whether the subscription is active.

    For creation:
    - city_id (required): An integer representing the id of the city the user is subscribed to.
                        This field should be sent during subscription creation and update.
    """
    user = UserSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=City.objects.all(), source='city')

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'city', 'times_per_day', 'is_active', 'created_at', 'city_id']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        subscription = Subscription.objects.create(user=user, **validated_data)
        return subscription

    def update(self, instance, validated_data):
        instance.times_per_day = validated_data.get('times_per_day', instance.times_per_day)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance
