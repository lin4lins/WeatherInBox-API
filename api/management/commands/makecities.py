import requests
from django.core.management import BaseCommand
from rest_framework.exceptions import NotFound

from api.models import City


class Command(BaseCommand):
    help = 'Populates database with capitals of all countries'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        url = "https://restcountries.com/v3.1/all"
        response = requests.get(url)
        countries = response.json()
        for country in countries:
            if 'capital' in country and country['capital']:
                capital = country['capital'][0] if isinstance(country['capital'], list) else country['capital']
                try:
                    City.objects.create(name=capital, country_name=country['name']['common'])
                    print(f'{round(countries.index(country) / len(countries) * 100, 2)}%')
                except NotFound:
                    self.stdout.write(self.style.WARNING(f'{capital} not found.'))
                    continue

        self.stdout.write(self.style.SUCCESS('Successfully created cities'))
