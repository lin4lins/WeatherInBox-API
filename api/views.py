from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User
from api.permissions import IsSelfOrAdminUser
from api.serializers import UserSerializer


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that the view requires.
        """
        action_permissions = {
            'create': [AllowAny],
            'retrieve': [IsSelfOrAdminUser],
            'update': [IsSelfOrAdminUser],
            'partial_update': [IsSelfOrAdminUser],
            'list': [IsAdminUser],
            'destroy': [IsAdminUser],
        }

        permission_classes = action_permissions.get(self.action, [IsAdminUser])
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Create a new user and return an access token.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({'access_token': access_token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
