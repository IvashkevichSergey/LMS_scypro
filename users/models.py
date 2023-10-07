from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    """Модель пользователя сервисом"""
    username = None
    email = models.EmailField(unique=True, verbose_name='email')

    phone_number = models.PositiveBigIntegerField(verbose_name='телефон', **NULLABLE)
    city = models.CharField(max_length=15, verbose_name='город', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='аватар', **NULLABLE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
