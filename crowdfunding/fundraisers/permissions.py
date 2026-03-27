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
   #"""Allow access to admin and fundraiser owner"""
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin can access everything
        if request.user.is_staff:
            return True

        # Owner can access only their own object
        return obj.owner == request.user
    
class IsAdminFundraiserOwnerOrSupporter(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        if obj.fundraiser.owner == request.user:
            return True

        if obj.supporter == request.user:
            return True

        return False