from rest_framework.permissions import BasePermission
from .models import Mentoria


class IsOwner(BasePermission):
    """
    Permite acesso a objetos do próprio usuário (ex.: RegistroDiario).
    """
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "usuario_id", None) == request.user.id


class IsMentorOfUser(BasePermission):
    """
    Verifica se o request.user é mentor do dono do objeto (quando aplicável).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj pode ser RegistroDiario ou um Usuario
        usuario_id = getattr(obj, "usuario_id", None)

        if usuario_id is None and hasattr(obj, "usuario"):
            usuario_id = obj.usuario.id

        if usuario_id is None:
            return False

        return Mentoria.objects.filter(
            mentor=request.user.mentor_profile,  # mentor é MentorProfile
            aluno_id=usuario_id,
            status="ativa",
        ).exists()
