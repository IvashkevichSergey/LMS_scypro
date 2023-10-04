from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsModeratorOrOwner(BasePermission):
    """
    Класс разрешений определяет возможность пользователя из группы Модераторов
    производить любые действия с объектом, кроме его удаления и создания нового объекта.
    Пользователь, не относящийся к группе Модераторов, получает права доступа
    на создание новых объектов и редактирование только тех объектов,
    авторами которых он является
    """

    MODERATOR_ROLE = 'Moderator'

    def has_permission(self, request, view):
        if request.user.groups.filter(name=self.MODERATOR_ROLE).exists():
            permitted_methods = permissions.SAFE_METHODS + ('PUT', 'PATCH')
            return request.method in permitted_methods
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.groups.filter(name=self.MODERATOR_ROLE).exists() \
                and request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            return request.user == obj.author
        return True


class IsCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return request.user == obj
        return True





