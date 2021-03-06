from rest_framework.permissions import BasePermission

class IsUser(BasePermission):
    """
    For use with a user queryset.
    The object must be the request user.
    """
    message = "You can only do this to yourself."

    def has_object_permission(self, request, view, obj):
        return request.user == obj

class IsUserOrGroupAdmin(BasePermission):
    """
    For use with a user queryset.
    The request user must be a group admin or the object itself.
    """
    message = "You must be the user or the group admin to perform this operation."

    def has_object_permission(self, request, view, obj):
        return request.user.is_group_admin or request.user == obj
