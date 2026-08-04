from rest_framework import serializers
from materials.models import Course, Lesson
from materials.validators import validate_youtube_only


class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["video_url"].validators.append(validate_youtube_only)

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("owner", "created_at", "updated_at")


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(read_only=True)
    last_updated_lesson = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_last_updated_lesson(self, obj):
        lesson = obj.lessons.order_by("-updated_at").first()
        if lesson:
            return {"title": lesson.title, "last_updated": lesson.updated_at}
        return None

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.subscriptions.filter(user=request.user).exists()
