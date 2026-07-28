from rest_framework import viewsets, permissions
from django.db.models import Prefetch
from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwnerOrModerator


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для Уроков с динамической настройкой прав доступа.
    """
    serializer_class = LessonSerializer

    def get_queryset(self):
        qs = Lesson.objects.all()
        if self.request.user.groups.filter(name='moderators').exists():
            return qs
        return qs.filter(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        else:  # destroy
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для Курсов с предзагрузкой уроков и динамическими правами.
    """
    serializer_class = CourseSerializer

    def get_queryset(self):
        qs = Course.objects.prefetch_related(
            Prefetch('lessons', queryset=Lesson.objects.order_by('order'))
        )
        if self.request.user.groups.filter(name='moderators').exists():
            return qs
        return qs.filter(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        else:
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
