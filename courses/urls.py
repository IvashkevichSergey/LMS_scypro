from django.urls import path
from rest_framework.routers import SimpleRouter

from courses.apps import CoursesConfig
from courses.views import CourseViewSet, LessonListAPIView, LessonCreateAPIView, \
    LessonDeleteAPIView, LessonUpdateAPIView, LessonDetailAPIView

app_name = CoursesConfig.name

router = SimpleRouter()
router.register('', CourseViewSet, 'courses')

urlpatterns = [
    path('lessons/', LessonListAPIView.as_view(), name='lessons_list'),
    path('lessons/<int:pk>/', LessonDetailAPIView.as_view(), name='lessons_detail'),
    path('lessons_create/', LessonCreateAPIView.as_view(), name='lessons_create'),
    path('lessons_update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lessons_update'),
    path('lessons_delete/<int:pk>/', LessonDeleteAPIView.as_view(), name='lessons_delete'),
] + router.urls
