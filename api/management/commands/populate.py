import random

import pycountry
from faker import Faker
from faker.providers import person, profile, internet, geo
from django.core.management.base import BaseCommand, CommandError

from api.models import User, City, Subscription

USERS_COUNT = 10
SUBSCRIPTIONS_PER_USER_MIN = 0
SUBSCRIPTIONS_PER_USER_MAX = 10
CITIES_MAX = 10
TIMES_PER_DAY_MIN = 1
TIMES_PER_DAY_MAX = 12


class Command(BaseCommand):
    help = 'Populates database with fake data'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.subscriptions_max = None
        self.users_count = None
        self.cities_max = None
        self.faker = Faker('en')
        self.faker.add_provider(person)
        self.faker.add_provider(profile)
        self.faker.add_provider(internet)
        self.faker.add_provider(geo)

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, required=False, default=USERS_COUNT,
                            help=f'Number of users. Default is {USERS_COUNT}.')
        parser.add_argument('--cities', type=int, required=False, default=CITIES_MAX,
                            help=f'Max number of cities. Default is {CITIES_MAX}. Max is 60.')
        parser.add_argument('--subscriptions', type=int, required=False, default=SUBSCRIPTIONS_PER_USER_MAX,
                            help=f'Max number of subscriptions per user. Default is {SUBSCRIPTIONS_PER_USER_MAX}.')

    def handle(self, *args, **options):
        self.users_count = options['users']
        self.cities_max = options['cities']
        self.subscriptions_max = options['subscriptions']
        if self.cities_max:
            raise CommandError(f'Max cities count is 60. Got {self.cities_max}.')

        self.__create_users()
        self.__create_cities()
        self.__create_subscriptions()

    def __create_users(self):
        for _ in range(self.users_count):
            user = User(first_name=self.faker.first_name(),
                        last_name=self.faker.last_name(),
                        username=self.faker.user_name(),
                        email=self.faker.free_email())
            has_webhook_url = self.faker.pybool()
            if has_webhook_url:
                user.webhook_url = self.faker.url()

            user.set_password(self.faker.password())
            user.save()

        self.stdout.write(self.style.SUCCESS('Successfully created users'))

    def __create_cities(self):
        for _ in range(CITIES_MAX):
            city_data = self.__get_city_country()
            City.objects.create(name=city_data[0], country_name=city_data[1])

        self.stdout.write(self.style.SUCCESS('Successfully created cities'))

    def __create_subscriptions(self):
        users = User.objects.all()
        cities = City.objects.all()
        for user in users:
            subscriptions_to_create_count = random.randrange(SUBSCRIPTIONS_PER_USER_MIN, SUBSCRIPTIONS_PER_USER_MAX)
            cities_to_subscribe = random.sample(list(cities), subscriptions_to_create_count)
            for city in cities_to_subscribe:
                Subscription.objects.create(user=user, city=city,
                                            times_per_day=random.randrange(TIMES_PER_DAY_MIN, TIMES_PER_DAY_MAX))

        self.stdout.write(self.style.SUCCESS('Successfully created subscriptions'))

    def __get_city_country(self):
        location = self.faker.location_on_land()
        city_name, country_code = location[2], location[3]
        country_name = pycountry.countries.get(alpha_2=country_code).name
        return city_name, country_name
