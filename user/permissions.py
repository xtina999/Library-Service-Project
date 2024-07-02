from rest_framework.permissions import BasePermission


class AllowAllPermission(BasePermission):
    def has_permission(self, request, view):
        return True
