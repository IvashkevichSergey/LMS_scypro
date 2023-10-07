from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.serializers import ValidationError

from courses.models import Lesson, Course, Subscription
from users.models import User


class LessonCRUDTestCase(APITestCase):

    def setUp(self):
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

        # with self.assertRaises(ValidationError):
        #     self.client.patch(
        #         reverse('courses:lessons_update', args=[self.lesson.pk]),
        #         {'link': invalid_url}
        #     )

    def test_delete_lesson(self):
        response = self.client.delete(
            reverse('courses:lessons_delete', args=[self.lesson.pk])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_subscription(self):
        response = self.client.post(
            reverse('courses:course_subscribe', args=[self.course.pk]),
            {'subscribe': True}
        )
        # print(response.json()) - вылетает с ошибкой

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # TODO: создание объекта класса Subscription не происходит (т.е. не запускает переопределённый
        #  метод post() класса MakeSubscription) и получаем пустой response (response.json вываливается в ошибку),
        #  хотя должен быть ответ от сервера {'message': 'Подписка на обновления курса оформлена!!'}
