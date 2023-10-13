from datetime import datetime, timezone

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from courses.models import Lesson, Course, Payments, Subscription
from courses.paginators import SimplePaginator
from courses.serializers import LessonSerializer, CourseListSerializer, \
    CourseDetailSerializer, PaymentsSerializer, CourseDefaultSerializer, \
    LessonDetailSerializer, CourseSubscribeSerializer
from courses.services import check_subscription, make_payment
from users.permissions import IsModeratorOrOwner


class CourseViewSet(viewsets.ModelViewSet):
    default_serializer = CourseDefaultSerializer
    queryset = Course.objects.annotate(lesson_quantity=Count("lesson"))
    permission_classes = [IsModeratorOrOwner]
    pagination_class = SimplePaginator

    serializers = {
        'list': CourseListSerializer,
        'retrieve': CourseDetailSerializer
    }

    def get_serializer_class(self):
        """Метод для определения используемого сериализатора в зависимости
        от вызванного метода"""
        return self.serializers.get(self.action, self.default_serializer)

    def perform_create(self, serializer):
        """Добавляем в поле author текущего пользователя при создании нового курса"""
        serializer.save(author=self.request.user)

    def list(self, request, *args, **kwargs):
        """Для пользователей, не входящих в группу Модераторов отфильтрованный
        queryset объектов, созданных текущим пользователем"""
        if not self.request.user.groups.filter(name='Moderator').exists():
            self.queryset = self.queryset.filter(author=self.request.user)
        return super().list(request, *args, **kwargs)

    def perform_update(self, serializer):
        """При обновлении данных курса запускаем функцию поиска подписок
        на обновления этого курса в том случае, если с момента последнего
        обновления прошло более 4 часов"""
        time_delta = datetime.now(timezone.utc) - self.get_object().updated_at
        course = serializer.save()
        if time_delta.seconds // 3600 > 4:
            return check_subscription(course)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]
    pagination_class = SimplePaginator

    def get_queryset(self):
        """Для пользователей, не входящих в группу Модераторов отфильтрованный
        queryset объектов, созданных текущим пользователем"""
        queryset = super().get_queryset()
        if not self.request.user.groups.filter(name='Moderator').exists():
            queryset = queryset.filter(author=self.request.user)
        return queryset


class LessonDetailAPIView(generics.RetrieveAPIView):
    serializer_class = LessonDetailSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]

    def perform_create(self, serializer):
        """Добавляем в поле author текущего пользователя при создании нового урока"""
        serializer.save(author=self.request.user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]

    def perform_update(self, serializer):
        """При обновлении данных урока -> получаем курс, в состав которого входит
        этот урок -> проверяем, прошло ли более 4 часов с момента крайнего обновления
        курса -> запускаем функцию поиска подписок на обновления курса"""
        course = self.get_object().course
        # Урок может не иметь связи ни с одним курсом, выполняем проверку
        if course:
            time_delta = datetime.now(timezone.utc) - course.updated_at
            # При обновлении урока обновляем поле updated_at
            # связанного с уроком курса
            course.updated_at = datetime.now(timezone.utc)
            course.save()
            if time_delta.seconds // 3600 > 4:
                serializer.save()
                return check_subscription(course)
        serializer.save()


class LessonDeleteAPIView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]


class PaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()
    permission_classes = [IsModeratorOrOwner]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    ordering_fields = ['payment_date']
    filterset_fields = ['lesson', 'course', 'payment_way']


class MakeSubscription(generics.CreateAPIView):
    """Класс используется для добавления/удаления подписки текущего
    пользователя на выбранный курс"""
    serializer_class = CourseSubscribeSerializer

    def post(self, request, *args, **kwargs):
        """Переопределяем метод для вывода кастомного Response и создания
        объекта Subscription"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = {
            'user': request.user,
            'course': Course.objects.get(pk=kwargs.get('pk'))
        }

        if request.data.get('subscribe') in (True, 'true', 'True'):
            subs = Subscription.objects.filter(**data)
            if subs:
                return Response({'message': 'Вы уже подписаны на обновления этого курса!!'},
                                status=status.HTTP_204_NO_CONTENT)
            subs = Subscription.objects.create(**data)
            subs.save()
            return Response({'message': 'Подписка на обновления курса оформлена!!'},
                            status=status.HTTP_201_CREATED)
        else:
            subs = Subscription.objects.filter(**data)
            if subs:
                subs.delete()
                return Response({'message': 'Подписка на обновления курса отменена!!'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'message': 'Вы ещё не подписаны на обновления данного курса!!'},
                            status=status.HTTP_204_NO_CONTENT)


class CoursePurchase(generics.CreateAPIView):
    """Класс используется для оформления покупки на выбранный курс"""

    def post(self, request, *args, **kwargs):
        """При отправке POST запроса выполняется запуск функции, отвечающей
        за проведение оплаты за выбранный курс"""
        make_payment(kwargs.get('pk'), request)
