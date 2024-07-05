from rest_framework import permissions


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """Права доступа к объекту, для автора, админа или модератора."""
    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True
        if (
            request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_moderator
                or request.user.is_superuser
            )
        ):
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа для просмотра - всем, для изменения только администратору.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )


class IsAdminUser(permissions.BasePermission):
    """Права доступа только для администратора."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )
