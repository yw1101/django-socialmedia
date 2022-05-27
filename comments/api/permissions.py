from rest_framework.permissions import BasePermission

class IsObjectOwner(BasePermission):
    message = "You do not have permission to access this object."

    #url not having user id
    def has_permission(self, request, view):
        return True

    #url having id
    def has_object_permission(self, request, view, obj):
        #obj obtained from queryset.get_object
        return request.user == obj.user
