from rest_framework import permissions

    
class IsAdminOrOwner(permissions.BasePermission):
    """Allow acces to admin and user"""
    def has_object_permission(self, request, view, obj):
        # Admin can see all
        if request.user and request.user.is_staff:
            return True
        # The owner can see only his/hers
        return request.user.is_authenticated and obj == request.user
        #return obj == request.user