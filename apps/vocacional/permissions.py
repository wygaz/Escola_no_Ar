# apps/vocacional/permissions.py
from __future__ import annotations

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.views import redirect_to_login
from functools import wraps

from apps.core.permissions import (
    PROD_VOCACIONAL,
    require_produto,
    require_consent,
    require_guia_feedback,
    require_termos,
)

# --------------------------------------------------------------------
# Este módulo ficou só com compatibilidade/uso específico do Vocacional.
# O gate principal (produto + consent + guia) está centralizado em
# apps/core/permissions.py
# --------------------------------------------------------------------

# (LEGADO) Mantido para não quebrar imports antigos.
# Agora é simplesmente "produto vocacional (slug de referência)".
def require_vocacional_bonus(view_func):
    return require_produto(PROD_VOCACIONAL)(view_func)


def require_mentor(view_func):
    """Exige usuário logado com perfil MENTOR/PROF/ADMIN (ajuste conforme seu projeto)."""
    ALLOWED = {"MENTOR", "PROF", "ADMIN"}

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if not getattr(u, "is_authenticated", False):
            return redirect_to_login(request.get_full_path())
        if getattr(u, "perfil", None) in ALLOWED or getattr(u, "is_superuser", False):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Acesso restrito.")

    return _wrapped
