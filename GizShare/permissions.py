from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allows access only to admin for create or update."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """ Object-level permission to only allow owners of an object to edit it.
        Assumes the model instance has an `owner` attribute. """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj.user == request.user

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)