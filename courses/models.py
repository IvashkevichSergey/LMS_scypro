from django.db import models

from config import settings
from users.models import NULLABLE


class Course(models.Model):
    """Модель учебных курсов"""

    title = models.CharField(max_length=25, verbose_name='название')
    preview = models.ImageField(upload_to='courses/', verbose_name='превью', **NULLABLE)
    description = models.TextField(verbose_name='описание', **NULLABLE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               **NULLABLE, verbose_name='автор')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'


class Lesson(models.Model):
    """Модель уроков, входящих в состав курсов"""

    title = models.CharField(max_length=25, verbose_name='название')
    preview = models.ImageField(upload_to='lessons/', verbose_name='превью', **NULLABLE)
    description = models.TextField(verbose_name='описание', **NULLABLE)
    link = models.CharField(max_length=100, verbose_name='ссылка на видео', **NULLABLE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, **NULLABLE, verbose_name='курс')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               **NULLABLE, verbose_name='автор')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'


class Payments(models.Model):
    """Модель платежей за отдельные курсы/уроки"""

    PAYMENT_WAY_CHOICES = [
        ('cash', 'paid_by_cash'),
        ('transaction', 'paid_by_transaction'),
    ]

    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='плательщик')
    payment_date = models.DateField(auto_now_add=True, verbose_name='дата оплаты')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='курс', **NULLABLE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='урок', **NULLABLE)
    amount = models.PositiveIntegerField(verbose_name='сумма')
    payment_way = models.CharField(max_length=12, choices=PAYMENT_WAY_CHOICES, verbose_name='способ оплаты')

    def __str__(self):
        return f'Оплата {self.paid_by} ' \
               f'за {self.course.title if self.course else self.lesson.title}'

    class Meta:
        verbose_name = 'платеж'
        verbose_name_plural = 'платежи'
        ordering = ['-payment_date']


class Subscription(models.Model):
    """Модель подписки пользователей на курсы"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='курс')

    def __str__(self):
        return f'{self.user.email} подписан на {self.course.title}'

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
