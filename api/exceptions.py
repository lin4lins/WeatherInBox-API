from rest_framework.exceptions import APIException


class CityChangingUnavailable(APIException):
    status_code = 400
    default_detail = 'Changing the subscription city is not available.'
    default_code = 'city_changing_unavailable'


class SubscriptionAlreadyExists(APIException):
    status_code = 400
    default_detail = 'The subscription with this fields already exists.'
    default_code = 'subscription_already_exists'
