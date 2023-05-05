from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.managers import CityManager

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    webhook_url = models.CharField(blank=True, max_length=255)
    receive_emails = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.id}, {self.username}'


class City(models.Model):
    name = models.CharField(blank=True, max_length=255)
    country_name = models.CharField(blank=True, max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    objects = CityManager()

    class Meta:
        # Ensure that there are no duplicates of the same cities
        unique_together = ('name', 'country_name')

    def __str__(self):
        return f'{self.name}, {self.country_name}'


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', editable=False)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, related_name='subscriptions', editable=False)
    times_per_day = models.IntegerField(default=1, validators=[MaxValueValidator(12), MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # Ensure that there are no duplicates of the same user and country+city
        unique_together = ('user', 'city')

    def __str__(self):
        return f'{self.user}, {self.city}'


class Weather(models.Model):
    city = models.ForeignKey('City', on_delete=models.CASCADE, related_name='weather_data')
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    feels_like = models.DecimalField(max_digits=4, decimal_places=2)
    min_temperature = models.DecimalField(max_digits=4, decimal_places=2)
    max_temperature = models.DecimalField(max_digits=4, decimal_places=2)
    wind_speed = models.DecimalField(max_digits=4, decimal_places=2)
    rain_1h = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    snow_1h = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    pressure = models.IntegerField()
    humidity = models.IntegerField()
    visibility = models.IntegerField()
    cloudiness = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
