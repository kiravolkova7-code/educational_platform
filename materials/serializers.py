from rest_framework import serializers
from materials.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        depth = 1
        read_only_fields = ('owner', 'created_at', 'updated_at')


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer (many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'update_at')

    def get_lessons_count(self, obj):
        return obj.lessons.count()
