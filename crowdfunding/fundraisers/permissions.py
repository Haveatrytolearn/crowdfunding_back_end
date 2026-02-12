from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsSupporterOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.supporter == request.user
    
class IsAdminOrOwner(permissions.BasePermission):
    """Allow acces to admin and fundraiser owner"""
    def has_object_permission(self, request, view, obj):
        # Admin can see all
        if request.user and request.user.is_staff:
            return True
        # The owner can see only his/hers
        return request.user.is_staff or obj.owner == request.user