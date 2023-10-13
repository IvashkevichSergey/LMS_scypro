from celery import shared_task
from django.core.mail import send_mail

from config import settings


@shared_task
def send_mail_about_update(user_email, course_title):
    """Функция для рассылки уведомлений об обновлении курса
    подписанным на него пользователям"""
    print(f'Материалы курса {course_title}, на который Вы подписаны, обновились!')
    # send_mail(
    #     subject=f'Обновление курса {course.title}',
    #     message=f'Материалы курса {course.title}, на который Вы подписаны, обновились!',
    #     recipient_list=[user_email],
    #     from_email=settings.EMAIL_HOST_USER,
    # )
