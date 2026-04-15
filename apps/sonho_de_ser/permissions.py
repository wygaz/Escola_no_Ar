from rest_framework.permissions import BasePermission

from .models import Mentoria


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "usuario_id", None) == request.user.id


class IsMentorOfUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        usuario_id = getattr(obj, "usuario_id", None)
        if usuario_id is None and hasattr(obj, "usuario"):
            usuario_id = obj.usuario.id
        if usuario_id is None:
            return False

        return Mentoria.objects.filter(
            mentor=request.user,
            mentorado_id=usuario_id,
            ativo=True,
            status="ATIVA",
        ).exists()
