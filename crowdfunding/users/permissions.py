from rest_framework import permissions

    
class IsAdminOrOwner(permissions.BasePermission):
    """Allow acces to admin and user"""
    
    def has_permission(self, request, view):
        # For detail-view user have to be authorised 
        return request.user and request.user.is_authenticated

    
    def has_object_permission(self, request, view, obj):
        # Admin can see all
        if request.user.is_staff:
            return True
        # The owner can see only his/hers
        return obj == request.user
