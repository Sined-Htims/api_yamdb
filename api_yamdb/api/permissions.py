from rest_framework import permissions


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True
        if (
            request.user.is_admin or request.user.is_moderator
            or request.user.is_superuser
        ):
            return True
        return False


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Кринж? В модели AnonymousUser нет атрибута is_admin
        try:
            return bool(request.user.is_superuser or request.user.is_admin)
        except AttributeError:
            return False
