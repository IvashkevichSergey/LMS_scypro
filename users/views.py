from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from users.models import User
from users.permissions import IsCurrentUser
from users.serializers import UserSerializer, UserAlienSerializer, UserManageSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsCurrentUser]
    lookup_fields = ['pk']

    def get_serializer_class(self):
        if self.action not in ('list', 'create') and self.request.user == self.get_object():
            return UserSerializer
        else:
            return UserAlienSerializer

    # def create(self, request, *args, **kwargs):
    #     email = request.data.get('email')
    #     password = request.data.get('password')
    #     user = User.objects.create(email=email)
    #     user.set_password(password)
    #     user.save()
    #     return Response('Successful created user', status=status.HTTP_201_CREATED)
