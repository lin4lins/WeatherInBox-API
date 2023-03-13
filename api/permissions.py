from rest_framework.permissions import BasePermission


class IsSelfOrAdminUser(BasePermission):
    """
    Custom permission to only allow users to view or modify their own profile,
    or for admins to view or modify any user's profile.
    """
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_staff


class IsOwnerOrAdminUser(BasePermission):
    """
    Custom permission to only allow owners of an object or admins to view and modify it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user.id or request.user.is_staff
