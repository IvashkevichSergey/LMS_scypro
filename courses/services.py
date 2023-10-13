from rest_framework import status
from rest_framework.response import Response

from courses.models import Course, Subscription, Payments
from courses.tasks import send_mail_about_update

import stripe
from config.settings import STRIPE_API_KEY


def check_subscription(course: Course) -> None:
    """Функция проверяет наличие подписок для заданного курса.
    Для каждой найденной подписки запускается фоновая задача"""

    subscriptions = Subscription.objects.filter(course=course)
    if subscriptions:
        for subscription in subscriptions:
            send_mail_about_update.delay(subscription.user.email, course.title)


def make_payment(course_pk: int, request_data):
    """Функция включает весь функционал по выполнению оплаты пользователем
    за выбранный курс"""
    # Ключ для работы с API сервиса STRIPE.COM
    stripe.api_key = STRIPE_API_KEY
    # Оплачиваемый курс
    course = Course.objects.get(pk=course_pk)
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
        paid_by=request_data.user,
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

