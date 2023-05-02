from django.db import models

from api.utils import get_lat_lon_values


class CityManager(models.Manager):
    def create(self, **kwargs):
        city = self.model(**kwargs)
        city.latitude, city.longitude = get_lat_lon_values(city.name, city.country_name)
        city.save()
        return city
