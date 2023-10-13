from datetime import datetime, timezone

from celery import shared_task

from users.models import User


@shared_task
def check_active_user():
    """Периодическая задача на проверку активности пользователей.
    Если пользователь не заходил в систему более 30 дней, его статус
    is_active устанавливается в False и блокируется доступ в систему"""
    for user in User.objects.filter(last_login__isnull=False):
        last_login_delta = datetime.now(timezone.utc) - user.last_login
        if last_login_delta.days > 30:
            user.is_active = False
            user.save()
            print(f'Пользователь {user} заблокирован')
