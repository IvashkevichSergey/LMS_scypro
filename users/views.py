from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from users.models import User
from users.permissions import IsCurrentUser
from users.serializers import UserSerializer, UserAlienSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsCurrentUser]
    lookup_fields = ['pk']

    # def get_serializer_class(self):
    #     if self.request.user == self.get_object():
    #         return UserSerializer
    #     else:
    #         return UserAlienSerializer

