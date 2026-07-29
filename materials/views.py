from django.db.models import Prefetch, Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from users.models import User
from .tasks import send_course_update_email
from materials.models import Course, Lesson
from materials.paginators import StandardResultsSetPagination
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwnerOrModerator


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для Уроков с динамической настройкой прав доступа.
    """
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user

        if IsModerator().has_permission(self.request, self) or user.is_superuser:
            return Lesson.objects.all()

        subscribed_courses_ids = list(user.subscriptions.values_list('course_id', flat=True))
        return Lesson.objects.filter(
            Q(owner=user) |
            Q(course__id__in=subscribed_courses_ids)
        )

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
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Course.objects.prefetch_related(
            Prefetch('lessons', queryset=Lesson.objects.order_by('order'))
        )

        if self.request.user.groups.filter(name='moderators').exists():
            return qs

        user = self.request.user
        subscribed_ids = user.subscriptions.values_list('course_id', flat=True)
        return qs.filter(Q(owner=user) | Q(id__in=subscribed_ids)).distinct()

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def perform_update(self, serializer):
        """
        Вызывается после валидации, но до сохранения при update/partial_update.
        """
        instance = serializer.save()

        materials_updated = any(
            field in self.request.data
            for field in ['modules', 'lessons', 'description']
        )

        if materials_updated:
            emails = User.objects.filter(
                subscriptions__course=instance,
                payments__paid_course=instance,
                is_active=True
            ).values_list('email', flat=True).distinct()

            for email in emails:
                send_course_update_email.delay(
                    user_email=email,
                    course_id=instance.id,
                    course_title=instance.title
                )
