from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.managers import CityManager

# Create your models here.


class User(AbstractUser):
    webhook_url = models.CharField(blank=True, max_length=255)

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
        # Ensure that there are no duplicates of the same user and country city
        unique_together = ('user', 'city')

    def __str__(self):
        return f'{self.user}, {self.city}'
