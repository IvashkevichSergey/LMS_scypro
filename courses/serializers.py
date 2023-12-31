from rest_framework import serializers
from rest_framework import fields

from courses.models import Lesson, Course, Payments, Subscription
from courses.validators import ValidateURL


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        exclude = ('preview',)


class LessonDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    course = serializers.SerializerMethodField(read_only=True)

    def get_author(self, obj):
        return obj.author.email if obj.author else None

    def get_course(self, obj):
        return obj.course.title if obj.course else None

    class Meta:
        model = Lesson
        fields = ('title', 'description', 'author', 'link', 'course')


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
    author = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_author(self, obj):
        return obj.author.email if obj.author else None

    def get_is_subscribed(self, obj):
        subs = Subscription.objects.filter(
            user=self.context['request'].user,
            course=obj.pk
        )
        return subs.exists()

    class Meta:
        model = Course
        exclude = ('preview',)


class PaymentsSerializer(serializers.ModelSerializer):
    paid_by = serializers.CharField(max_length=50, source='paid_by.username')

    class Meta:
        model = Payments
        fields = '__all__'


class PaymentsForUserSerializer(serializers.ModelSerializer):
    payment_way = serializers.SerializerMethodField()
    paid_for = serializers.SerializerMethodField()

    def get_payment_way(self, obj):
        return obj.get_payment_way_display()

    def get_paid_for(self, obj):
        if obj.course:
            return obj.course.title
        elif obj.lesson:
            return obj.lesson.title

    class Meta:
        model = Payments
        fields = ['payment_date', 'amount', 'payment_way', 'paid_for']


class CourseSubscribeSerializer(serializers.ModelSerializer):
    subscribe = serializers.BooleanField(required=True)

    class Meta:
        model = Subscription
        fields = ('subscribe',)
