# apps/vocacional/gating.py
from typing import Literal, Optional, Dict, Any
import logging
from functools import wraps
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from apps.contas.models_acessos import tem_acesso
from .models import AvaliacaoGuia
from .models_consent import Consentimento

logger = logging.getLogger("vocacional")

Step = Literal["login", "bonus_acquire", "bonus_validate", "consent", "guia", None]

# ----- checagens atômicas -----
def bonus_acquired(user) -> bool:
    # segue como está hoje (entitlement)
    from apps.contas.models_acessos import tem_acesso
    return tem_acesso(user, "vocacional_bonus")

def consent_ok(user) -> bool:
    return Consentimento.objects.filter(user=user, aceito=True).exists()

def guia_done(user) -> bool:
    return AvaliacaoGuia.objects.filter(user=user, status="concluida").exists()

# ----- flags -----
def require_bonus() -> bool:
    return bool(getattr(settings, "VOCACIONAL_REQUIRE_BONUS", False))

def require_consent() -> bool:
    return bool(getattr(settings, "VOCACIONAL_REQUIRE_CONSENT", True))

def require_guia() -> bool:
    return bool(getattr(settings, "VOCACIONAL_REQUIRE_GUIA", True))

def bonus_validated(user) -> bool:
    return bonus_acquired(user) and consent_ok(user) and guia_done(user)

def gating_state(user) -> Dict[str, Any]:
    is_auth = getattr(user, "is_authenticated", False)
    return {
        "is_auth": is_auth,
        "flags": {
            "require_bonus": require_bonus(),
            "require_consent": require_consent(),
            "require_guia": require_guia(),
        },
        "checks": {
            "bonus_acquired": bonus_acquired(user) if is_auth else False,
            "consent_ok":     consent_ok(user)     if is_auth else False,
            "guia_done":      guia_done(user)      if is_auth else False,
        },
    }


def tem_disponiveis(user) -> int:
    from .models import Avaliacao
    c = Avaliacao.objects.filter(usuario=user, status="concluida").count()
    return max(0, 2 - c)

def next_step(user):
    if not getattr(user, "is_authenticated", False):
        return "login"
    # Se bônus estiver pausado, pule para consent/guia/limite
    if tem_disponiveis(user) == 0:
        return "limit"
    if require_bonus():
        if not bonus_acquired(user):   return "bonus_acquire"
        if not (consent_ok(user) and guia_done(user)): return "bonus_validate"
        return None
    if require_consent() and not consent_ok(user):
        return "consent"
    if require_guia() and not guia_done(user):
        return "guia"
    return None

def next_url(user):
    step = next_step(user)
    if step is None:
        return reverse("vocacional:avaliacao_form")
    mapping = {
        "limit": "vocacional:index",
        "bonus_acquire": "vocacional:bonus",
        "bonus_validate": "vocacional:bonus_validar",
        "consent": "vocacional:consentimento_check",
        "guia": "vocacional:guia_avaliacao",
    }
    return reverse(mapping[step])





'''
# ---- Decorator legado (se houver) ----
def require_produto(produto_slug: str, redirect_name: str = "vocacional:bonus"):
    def _decorator(viewfunc):
        @login_required
        @wraps(viewfunc)
        def _wrapped(request, *args, **kwargs):
            if produto_slug == "vocacional_bonus" and not require_bonus():
                logger.debug("require_produto: bonus pausado -> liberado")
                return viewfunc(request, *args, **kwargs)
            if tem_acesso(request.user, produto_slug):
                logger.debug("require_produto: acesso OK -> view")
                return viewfunc(request, *args, **kwargs)
            logger.debug(f"require_produto: sem acesso -> redirect {redirect_name}")
            return redirect(redirect_name)
        return _wrapped
    return _decorator
'''