from rest_framework import serializers


class ValidateURL:
    """Валидатор для проверки задаваемого значений URL адреса для модели Lesson"""
    def __call__(self, value):
        if 'youtube.com' not in value:
            raise serializers.ValidationError('нельзя размещать ссылки на ресурсы кроме youtube.com')
