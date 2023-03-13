from django.contrib.auth.models import AbstractUser
from django.forms import CharField


# Create your models here.


class User(AbstractUser):
    webhook_url = CharField(blank=True, max_length=255)
