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
        import stripe
        from config.settings import STRIPE_API_KEY

        # Ключ для работы с API сервиса STRIPE.COM
        stripe.api_key = STRIPE_API_KEY
        # Оплачиваемый курс
        course = Course.objects.get(pk=kwargs.get('pk'))
        # Условная цена за курс
        price = 2000

        # Создаём объект класса PaymentMethod - способ оплаты
        pay_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2034,
                "cvc": "314",
            },
        )
        id_pay_method = pay_method['id']

        # Проводим платёж за курс с автоматическим подтверждением
        # платежа (confirm=True)
        new_pay = stripe.PaymentIntent.create(
            amount=price,
            currency="usd",
            payment_method=id_pay_method,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            confirm=True,
            description=f'Payment for learning course "{course}"'
        )

        # Сохраняем информацию о платеже в БЛ
        payment = Payments.objects.create(
            paid_by=request.user,
            course=course,
            amount=price,
            payment_way='transaction'
        )
        payment.save()

        # Выводим ответ в зависимости от успешности проведённого платежа
        if new_pay['status'] == 'succeeded':
            return Response({'message': f'Оплата за курс {course.title} выполнена успешно'},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Оплата не прошла, сожалеем!'},
                            status=status.HTTP_204_NO_CONTENT)

