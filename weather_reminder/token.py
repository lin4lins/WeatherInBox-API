from rest_framework_simplejwt.views import TokenObtainPairView as TokenView

from api.models import User


class TokenObtainPairView(TokenView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        current_user = User.objects.get(username=request.data.get('username'))
        response.data['user_id'] = current_user.id
        return response
