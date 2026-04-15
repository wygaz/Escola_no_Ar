# apps/core/permissions.py
from __future__ import annotations

from functools import wraps
from urllib.parse import urlencode
from typing import Iterable

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

from apps.contas.acessos import tem_acesso

# --------------------------------------------------------------------
# "Slugs de referência" (internos)
# Use SEMPRE estes em @require_produto(...) e em checagens no Portal.
# --------------------------------------------------------------------
PROD_GUIA = "guia"  # produto principal (Hotmart) que libera os bônus

# Bônus atual (75 perguntas) — pode evoluir depois para outros pacotes/níveis
PROD_VOCACIONAL_75 = "vocacional75"

# Nome legado / futuro (mantido para compatibilidade)
PROD_VOCACIONAL = "vocacional"

PROD_SONHEMAISALTO = "sonhemaisalto"

# Refinamento Top 3 (Passes 1/2/3) — serviço adicional (vendido separadamente)
PROD_VOCACIONAL_REFINAMENTO1 = "vocacional_refinamento1"
PROD_VOCACIONAL_REFINAMENTO2 = "vocacional_refinamento2"
PROD_VOCACIONAL_REFINAMENTO3 = "vocacional_refinamento3"
PROD_VOCACIONAL75PLUS = "vocacional75plus"


# --------------------------------------------------------------------
# Equivalências: aceita slugs antigos durante a fase de transição.
# Depois dá para “enxugar” quando tudo estiver padronizado.
# --------------------------------------------------------------------
EQUIVALENCIAS: dict[str, set[str]] = {
    PROD_GUIA: {
        "guia",
        "guia_descoberta",
        "guia_sonhe_alto",
        "guia-sonhe-alto",
        "guia_hotmart",
        "vocacional_guia",
        "sonhemaisalto_guia",
    },
    PROD_VOCACIONAL_75: {
        "vocacional75",
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

# O Guia libera os dois bônus
EQUIVALENCIAS[PROD_VOCACIONAL_75].update(EQUIVALENCIAS[PROD_GUIA])
EQUIVALENCIAS[PROD_SONHEMAISALTO].update(EQUIVALENCIAS[PROD_GUIA])

# Compat: manter PROD_VOCACIONAL apontando para o mesmo conjunto do bônus 75
EQUIVALENCIAS[PROD_VOCACIONAL] = set(EQUIVALENCIAS[PROD_VOCACIONAL_75])

# Refinamento (Passes 1/2/3): aceitar slugs curtos cadastrados no Admin (ex.: passe1/passe2/passe3)
EQUIVALENCIAS.setdefault(PROD_VOCACIONAL_REFINAMENTO1, {PROD_VOCACIONAL_REFINAMENTO1}).update({"passe1", "pass1"})
EQUIVALENCIAS.setdefault(PROD_VOCACIONAL_REFINAMENTO2, {PROD_VOCACIONAL_REFINAMENTO2}).update({"passe2", "pass2"})
EQUIVALENCIAS.setdefault(PROD_VOCACIONAL_REFINAMENTO3, {PROD_VOCACIONAL_REFINAMENTO3}).update({"passe3", "pass3"})
EQUIVALENCIAS.setdefault(PROD_VOCACIONAL75PLUS, {PROD_VOCACIONAL75PLUS}).update({"vocacional75Plus", "vocacional75_plus"})


def slugs_equivalentes(slug_ref: str) -> list[str]:
    """Retorna a lista de slugs aceitos para um slug de referência."""
    slugs = set(EQUIVALENCIAS.get(slug_ref, {slug_ref}))
    out = [slug_ref]
    for s in sorted(slugs):
        if s != slug_ref:
            out.append(s)
    # dedup
    seen = set()
    final: list[str] = []
    for s in out:
        if s not in seen:
            final.append(s)
            seen.add(s)
    return final


def _staff_bypass(user, request=None, bypass_staff: bool = True) -> bool:
    """Retorna True quando o usuário staff/superuser pode bypassar gates.

    - bypass_staff=False -> nunca bypassa
    - Se request tiver portal_mode=user (GET ou session), NÃO bypassa
    """
    if not bypass_staff:
        return False
    if not (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
        return False
    if request is None:
        return True
    mode = request.GET.get("portal_mode") or request.session.get("portal_mode")
    return mode != "user"


def user_has_produto(user, slug_ref: str, *, request=None, bypass_staff: bool = True) -> bool:
    """Checagem centralizada de acesso (aceita equivalências)."""
    if not getattr(user, "is_authenticated", False):
        return False
    if _staff_bypass(user, request=request, bypass_staff=bypass_staff):
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

            if user_has_produto(user, slug_ref, request=request, bypass_staff=True):
                return view_func(request, *args, **kwargs)

            messages.error(request, "Acesso não liberado para este conteúdo.")
            return redirect(redirect_name)

        return _wrapped

    return decorator


# --------------------------------------------------------------------
# Onboarding: termos / consentimento / avaliação do Guia
# --------------------------------------------------------------------
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
    return _has_termos(user) and _has_consent(user)


def _has_valid_guia(user, *, request=None, bypass_staff: bool = True) -> bool:
    return user_has_produto(user, PROD_GUIA, request=request, bypass_staff=bypass_staff)


def onboarding_status(user, *, request=None, bypass_staff: bool = True) -> dict:
    """Retorna o status de onboarding do usuário, usado pelo Portal."""
    if not getattr(user, "is_authenticated", False):
        return {
            "has_legal": False,
            "has_valid_guia": False,
            "has_guia_feedback": False,
            "has_onboarding": False,
        }

    if _staff_bypass(user, request=request, bypass_staff=bypass_staff):
        return {
            "has_legal": True,
            "has_valid_guia": True,
            "has_guia_feedback": True,
            "has_onboarding": True,
        }

    has_legal = _has_legal(user)
    has_valid_guia = _has_valid_guia(user, request=request, bypass_staff=bypass_staff)
    has_guia = _has_guia_feedback(user)
    return {
        "has_legal": has_legal,
        "has_valid_guia": has_valid_guia,
        "has_guia_feedback": has_guia,
        "has_onboarding": (has_legal and has_valid_guia and has_guia),
    }


def require_legal(view_func=None, redirect_name: str = "core:legal_aceite"):
    """Exige login + Termos + Consentimento LGPD. Sem isso: redireciona para a tela única."""

    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kwargs):
            if _staff_bypass(request.user, request=request, bypass_staff=True):
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


def require_consent(view_func=None, redirect_name: str = "core:legal_aceite"):
    return require_legal(view_func=view_func, redirect_name=redirect_name)


def require_termos(view_func=None, redirect_name: str = "core:legal_aceite"):
    return require_legal(view_func=view_func, redirect_name=redirect_name)


def require_guia_feedback(view_func=None, redirect_name: str = "vocacional:guia_avaliacao"):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kwargs):
            if _staff_bypass(request.user, request=request, bypass_staff=True):
                return fn(request, *args, **kwargs)

            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if _has_guia_feedback(request.user):
                return fn(request, *args, **kwargs)

            messages.info(request, "Para liberar o bônus, responda a Avaliação do Guia.")
            return redirect(redirect_name)

        return _wrapped

    return decorator(view_func) if callable(view_func) else decorator


def user_has_onboarding(user, *, request=None, bypass_staff: bool = True) -> bool:
    """Helper público: onboarding completo (Termos + Consentimento + Avaliação do Guia)."""
    st = onboarding_status(user, request=request, bypass_staff=bypass_staff)
    return bool(st.get("has_onboarding"))
