from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Разрешает доступ только пользователям из группы 'moderators'.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="moderators").exists()
        )


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Разрешает доступ владельцу объекта ИЛИ модератору.
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_moderator = request.user.groups.filter(name="moderators").exists()
        return is_owner or is_moderator
