from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'customer'


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['staff', 'admin']