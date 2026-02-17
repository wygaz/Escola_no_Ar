# apps/contas/acessos.py
from django.db.models import Q
from django.utils import timezone

from apps.contas.models_acessos import Acesso


def tem_acesso(user, produto_slug: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False

    qs = Acesso.objects.filter(user=user, produto__slug=produto_slug)
    # considera expirados (se expires_at estiver preenchido)
    qs = qs.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
    return qs.exists()


# compatibilidade com código antigo
user_has_produto = tem_acesso



def user_has_produto(user, slug: str) -> bool:
    """
    API única para checar produto por slug.
    - requer login
    - staff/superuser passam
    - demais: delega para tem_acesso()
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False

    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True

    return tem_acesso(user, slug)