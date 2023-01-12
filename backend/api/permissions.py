from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS

User = get_user_model()


# class ReadOnly(BasePermission):

#     # Права на уровне запроса и пользователя
#     def has_object_permission(self, request, view, obj):
#         return (request.method in SAFE_METHODS
#                 or request.user.is_user
#                 or obj.author == request.user)

#     # Права на уровне объекта
#     def has_permission(self, request, view):
#         return (request.method in SAFE_METHODS
#                 or request.user.is_authenticated)
