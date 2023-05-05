from rest_framework import serializers

from api.models import City, Subscription, User, Weather


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


class WeatherSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Weather model.

    Serializes and deserializes Weather instances to and from JSON.

    Fields:
    - city (read-only): A foreign key to a City instance that the Weather data is associated with.
    - temperature: The current temperature in degrees Celsius.
    - feels_like: The current "feels like" temperature in degrees Celsius.
    - min_temperature: The minimum temperature in degrees Celsius for the day.
    - max_temperature: The maximum temperature in degrees Celsius for the day.
    - wind_speed: The current wind speed in meters per second.
    - rain_1h: The rain volume for the last 1 hour, in millimeters (optional).
    - snow_1h: The snow volume for the last 1 hour, in millimeters (optional).
    - pressure: The current atmospheric pressure in hPa.
    - humidity: The current relative humidity as a percentage.
    - visibility: The current visibility in meters.
    - cloudiness: The current cloudiness as a percentage.
    - sunrise: The time of sunrise for the current day.
    - sunset: The time of sunset for the current day.
    - created_at (read-only): The date and time when the Weather instance was created.

    """

    city = CitySerializer(read_only=True)

    class Meta:
        model = Weather
        fields = '__all__'
