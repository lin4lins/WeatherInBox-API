from rest_framework.routers import SimpleRouter

from api.views import CityViewSet, SubscriptionViewSet, UserViewSet

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'cities', CityViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
urlpatterns = router.urls
