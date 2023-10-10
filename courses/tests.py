from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.serializers import ValidationError

from courses.models import Lesson, Course, Subscription
from users.models import User


class LessonCRUDTestCase(APITestCase):
    """Класс для тестирования CRUD методов модели Lesson и
    функционала создания/удаления подписки (модель Subscription)"""

    def setUp(self):
        """Функция создаёт набор объектов перед каждым тестированием"""
        self.client = APIClient()
        self.user = User.objects.create(email='user@test.com', password='test')
        self.client.force_authenticate(user=self.user)

        self.lesson = Lesson.objects.create(
            title='test',
            author=self.user
        )

        self.course = Course.objects.create(
            title='test',
            author=self.user
        )

    def test_get_lesson(self):
        """Тест GET запроса"""
        response = self.client.get(
            reverse('courses:lessons_list')
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json()['results'][0],
            {'id': 2, 'link': None, 'title': 'test', 'description': None, 'course': None, 'author': 2}
        )

    def test_post_lesson(self):
        """Тест POST запроса"""
        new_obj = {
            'title': 'test',
            'description': 'test_desc'
        }

        response = self.client.post(
            reverse('courses:lessons_create'),
            new_obj
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Lesson.objects.all().count(),
            2
        )

    def test_update_lesson(self):
        """Тест PUT запроса"""
        new_obj = {
            'title': 'new_title',
        }

        response = self.client.put(
            reverse('courses:lessons_update', args=[self.lesson.pk]),
            new_obj
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.lesson.refresh_from_db()

        self.assertEqual(
            self.lesson.title,
            'new_title'
        )

    def test_validation_url_lesson(self):
        """Тест PATCH запроса с проверкой работы валидатора на поле link"""
        invalid_url = 'https://anyurl.com/123'

        response = self.client.patch(
            reverse('courses:lessons_update', args=[self.lesson.pk]),
            {'link': invalid_url}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {'link': ['нельзя размещать ссылки на ресурсы кроме youtube.com']}
        )

    def test_delete_lesson(self):
        """Тест DELETE запроса"""
        response = self.client.delete(
            reverse('courses:lessons_delete', args=[self.lesson.pk])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_subscription(self):
        """Тест создания/удаления подписки - модели Subscription"""
        response = self.client.post(
            reverse('courses:course_subscribe', args=[self.course.pk]),
            {'subscribe': True}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            Subscription.objects.first().course.title,
            self.course.title
        )

        response = self.client.post(
            reverse('courses:course_subscribe', args=[self.course.pk]),
            {'subscribe': False}
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            Subscription.objects.all().count(),
            0
        )
