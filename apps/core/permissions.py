# apps/core/permissions.py
from __future__ import annotations

from functools import wraps
from urllib.parse import urlencode
from typing import Iterable

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from apps.contas.acessos import tem_acesso
from django.urls import reverse


# --------------------------------------------------------------------
# "Slugs de referência" (internos)
# Use SEMPRE estes em @require_produto(...) e em checagens no Portal.
# --------------------------------------------------------------------
PROD_GUIA = "guia"  # produto principal (Hotmart) que libera os bônus
PROD_VOCACIONAL = "vocacional"
PROD_SONHEMAISALTO = "sonhemaisalto"

# --------------------------------------------------------------------
# Equivalências: permite aceitar slugs antigos durante a fase de transição
# (testes / implantação). Pode “enxugar” depois, quando tudo estiver padronizado.
# --------------------------------------------------------------------
EQUIVALENCIAS: dict[str, set[str]] = {
    # produto “mestre” (pode padronizar depois para apenas 1 slug)
    PROD_GUIA: {
        "guia",
        "guia_descoberta",
        "guia_sonhe_alto",
        "guia-sonhe-alto",
        "guia_hotmart",
    },
    PROD_VOCACIONAL: {
        "vocacional",
        "vocacional_bonus",
        "vocacional_guia",
    },
    PROD_SONHEMAISALTO: {
        "sonhemaisalto",
        "sonhemaisalto_bonus",
        "sonhemaisalto_guia",
        "projeto21_sonhe_alto",
        "projeto21",
    },
}

# O Guia libera os dois bônus (Vocacional e Sonhe + Alto)
EQUIVALENCIAS[PROD_VOCACIONAL].update(EQUIVALENCIAS[PROD_GUIA])
EQUIVALENCIAS[PROD_SONHEMAISALTO].update(EQUIVALENCIAS[PROD_GUIA])


def slugs_equivalentes(slug_ref: str) -> list[str]:
    """Retorna a lista de slugs aceitos para um slug de referência."""
    slugs = set(EQUIVALENCIAS.get(slug_ref, {slug_ref}))
    # ordem determinística: o ref primeiro
    out = [slug_ref]
    for s in sorted(slugs):
        if s != slug_ref:
            out.append(s)
    # dedup (caso o ref esteja no set)
    seen = set()
    final = []
    for s in out:
        if s not in seen:
            final.append(s)
            seen.add(s)
    return final


def user_has_produto(user, slug_ref: str) -> bool:
    """Checagem centralizada de acesso (aceita equivalências)."""
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True
    for s in slugs_equivalentes(slug_ref):
        if tem_acesso(user, s):
            return True
    return False


# --------------------------------------------------------------------
# Perfis
# --------------------------------------------------------------------
def require_perfis(*perfis: str):
    perfis_set = set(perfis)

    def decorator(view):
        @wraps(view)
        def _wrapped(request, *a, **kw):
            u = request.user
            if not u.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if getattr(u, "perfil", None) in perfis_set:
                return view(request, *a, **kw)
            return HttpResponseForbidden("Acesso não permitido para seu perfil.")

        return _wrapped

    return decorator


# --------------------------------------------------------------------
# Produto (bônus)
# --------------------------------------------------------------------
def require_produto(slug_ref: str, redirect_name: str = "portal"):
    """Exige login + produto (slug de referência). Sem produto: volta ao Portal."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user

            if not getattr(user, "is_authenticated", False):
                return redirect_to_login(request.get_full_path())

            if user_has_produto(user, slug_ref):
                return view_func(request, *args, **kwargs)

            messages.error(request, "Acesso não liberado para este conteúdo.")
            return redirect(redirect_name)

        return _wrapped

    return decorator


# --------------------------------------------------------------------
# Onboarding: termos / consentimento / avaliação do Guia
# (mantido aqui para centralizar o gate e reduzir redundâncias).
# --------------------------------------------------------------------
def _staff_bypass(request) -> bool:
    u = request.user
    if not (getattr(u, "is_staff", False) or getattr(u, "is_superuser", False)):
        return False
    # se estiver em modo usuário, NÃO bypass
    # (considera também ?portal_mode=user para facilitar testes)
    mode = request.GET.get("portal_mode")
    if mode in {"user", "gov"}:
        effective = mode
    else:
        effective = request.session.get("portal_mode")
    return effective != "user"

def _has_termos(user) -> bool:
    try:
        from apps.vocacional.models import AvaliacaoGuia
    except Exception:
        return True  # se o app não existe, não bloqueia
    return AvaliacaoGuia.objects.filter(user=user, aceite_termos=True).exists()


def _has_consent(user) -> bool:
    try:
        from apps.vocacional.models_consent import Consentimento
    except Exception:
        return True
    return Consentimento.objects.filter(user=user, aceito=True, revogado_em__isnull=True).exists()



def _has_guia_feedback(user) -> bool:
    try:
        from apps.vocacional.models import AvaliacaoGuia
    except Exception:
        return True
    return AvaliacaoGuia.objects.filter(user=user, status="concluida").exists()

def _has_legal(user) -> bool:
    """Termos + consentimento (LGPD) — ambos no mesmo nível."""
    return _has_termos(user) and _has_consent(user)


def require_legal(view_func=None, redirect_name: str = "core:legal_aceite"):
    """Exige login + Termos + Consentimento LGPD. Sem isso: redireciona para a tela única."""

    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kwargs):
            if _staff_bypass(request):
                return fn(request, *args, **kwargs)

            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if _has_legal(request.user):
                return fn(request, *args, **kwargs)

            messages.info(request, "Antes, aceite Termos e Privacidade.")

            # preserva o destino (volta para a página que o usuário tentou abrir)
            try:
                url = reverse(redirect_name)
                url = f"{url}?{urlencode({'next': request.get_full_path()})}"
                return redirect(url)
            except Exception:
                return redirect(redirect_name)

        return _wrapped

    return decorator(view_func) if callable(view_func) else decorator


# Compat: chamadas antigas continuam funcionando, mas agora apontam para a tela única.
def require_consent(view_func=None, redirect_name: str = "core:legal_aceite"):
    return require_legal(view_func=view_func, redirect_name=redirect_name)


def require_termos(view_func=None, redirect_name: str = "core:legal_aceite"):
    return require_legal(view_func=view_func, redirect_name=redirect_name)


def require_guia_feedback(view_func=None, redirect_name: str = "vocacional:guia_avaliacao"):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kwargs):
            if _staff_bypass(request):
                return fn(request, *args, **kwargs)

            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if _has_guia_feedback(request.user):
                return fn(request, *args, **kwargs)

            messages.info(request, "Para liberar o bônus, responda a Avaliação do Guia.")
            return redirect(redirect_name)
        return _wrapped

    return decorator(view_func) if callable(view_func) else decorator

