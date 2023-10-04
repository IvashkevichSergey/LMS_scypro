from rest_framework import serializers

from courses.serializers import PaymentsForUserSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    payments_story = PaymentsForUserSerializer(source='payments_set', many=True)

    class Meta:
        model = User
        fields = '__all__'


class UserAlienSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'email', 'avatar', 'city')
