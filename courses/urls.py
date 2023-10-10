from django.urls import path
from rest_framework.routers import DefaultRouter

from courses.apps import CoursesConfig
from courses.views import CourseViewSet, LessonListAPIView, LessonCreateAPIView, \
    LessonDeleteAPIView, LessonUpdateAPIView, LessonDetailAPIView, PaymentsViewSet, MakeSubscription, CoursePurchase

app_name = CoursesConfig.name

router = DefaultRouter()
router.register(r'courses', CourseViewSet, 'courses')
router.register(r'payments', PaymentsViewSet, 'payments')

urlpatterns = [
    path('lessons/', LessonListAPIView.as_view(), name='lessons_list'),
    path('lessons/<int:pk>/', LessonDetailAPIView.as_view(), name='lessons_detail'),
    path('lessons_create/', LessonCreateAPIView.as_view(), name='lessons_create'),
    path('lessons_update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lessons_update'),
    path('lessons_delete/<int:pk>/', LessonDeleteAPIView.as_view(), name='lessons_delete'),

    path('courses/<int:pk>/subscribe/', MakeSubscription.as_view(), name='course_subscribe'),
    path('courses/<int:pk>/buy/', CoursePurchase.as_view(), name='course_purchase'),
] + router.urls
