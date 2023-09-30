from rest_framework import serializers
from rest_framework import fields, relations

from courses.models import Lesson, Course, Payments


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        exclude = ('preview',)


class LessonDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('title', 'description', 'link')


class CourseDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ('preview',)


class CourseListSerializer(serializers.ModelSerializer):
    lesson_quantity = fields.IntegerField()

    class Meta:
        model = Course
        exclude = ('preview',)


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons_list = LessonDetailSerializer(source='lesson_set', many=True)

    class Meta:
        model = Course
        exclude = ('preview',)


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'


class PaymentsForUserSerializer(serializers.ModelSerializer):
    payment_way = serializers.SerializerMethodField()
    paid_for = serializers.SerializerMethodField()

    def get_payment_way(self, obj):
        return obj.get_payment_way_display()

    def get_paid_for(self, obj):
        return obj.course.title if obj.course else obj.lesson.title

    class Meta:
        model = Payments
        fields = ['payment_date', 'amount', 'payment_way', 'paid_for']
