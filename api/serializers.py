from rest_framework import serializers

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
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'webhook_url']
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
    - city (required): A nested object representing the city the user is subscribed to.
    - times_per_day (required): The number of times per day the user wishes to receive notifications for this subscription.
    """
    user = UserSerializer(read_only=True)
    city = CitySerializer(validators=[])  # City validators are ignored because having a requested city in db is OK

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'is_active']

    def create(self, validated_data):
        user = self.context['request'].user
        city_data = validated_data.pop('city')
        city, created = City.objects.get_or_create(**city_data)
        subscription = Subscription.objects.create(user=user, city=city, **validated_data)
        return subscription

    def update(self, instance, validated_data):
        instance.times_per_day = validated_data.pop('times_per_day')
        instance.save()
        return instance
