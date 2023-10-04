from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.filters import SearchFilter, OrderingFilter

from courses.models import Lesson, Course, Payments
from courses.serializers import LessonSerializer, CourseListSerializer, \
    CourseDetailSerializer, PaymentsSerializer, CourseDefaultSerializer, \
    LessonDetailSerializer
from users.permissions import IsModeratorOrOwner


class CourseViewSet(viewsets.ModelViewSet):
    default_serializer = CourseDefaultSerializer
    queryset = Course.objects.annotate(lesson_quantity=Count("lesson"))
    permission_classes = [IsModeratorOrOwner]
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


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]

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
