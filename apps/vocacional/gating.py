# apps/vocacional/gating.py
from __future__ import annotations

from django.conf import settings
from django.urls import reverse

from apps.core.permissions import (
    PROD_GUIA,
    PROD_VOCACIONAL_75,
    onboarding_status,
    user_has_produto,
)

# Flags (pode ligar/desligar via settings.py se quiser)
VOCACIONAL_REQUIRE_BONUS = getattr(settings, "VOCACIONAL_REQUIRE_BONUS", False)
VOCACIONAL_REQUIRE_TERMOS = getattr(settings, "VOCACIONAL_REQUIRE_TERMOS", True)
VOCACIONAL_REQUIRE_CONSENT = getattr(settings, "VOCACIONAL_REQUIRE_CONSENT", True)
VOCACIONAL_REQUIRE_GUIA = getattr(settings, "VOCACIONAL_REQUIRE_GUIA", True)


def bonus_acquired(user, *, request=None) -> bool:
    return user_has_produto(user, PROD_VOCACIONAL_75, request=request, allow_demo=True)


def guia_valid(user, *, request=None) -> bool:
    return user_has_produto(user, PROD_GUIA, request=request, allow_demo=True)


def termos_ok(user) -> bool:
    try:
        from apps.vocacional.models import AvaliacaoGuia
    except Exception:
        return True
    return AvaliacaoGuia.objects.filter(user=user, aceite_termos=True).exists()


def consent_ok(user) -> bool:
    try:
        from apps.vocacional.models_consent import Consentimento
    except Exception:
        return True
    return Consentimento.objects.filter(user=user, aceito=True, revogado_em__isnull=True).exists()



def guia_done(user) -> bool:
    try:
        from apps.vocacional.models import AvaliacaoGuia
    except Exception:
        return True
    return AvaliacaoGuia.objects.filter(user=user, status="concluida").exists()


def next_step(user, *, request=None):
    """Retorna a próxima etapa do funil.

    Regra atual:
    - Termos + Privacidade/Consentimento ficam em UMA página (core:legal_aceite).
    - O Guia é pré-requisito válido do programa.
    - A Avaliação do Guia só entra depois do Guia válido.

    Ordem: legal -> guia válido -> guia -> bônus -> ok
    Retorna None quando está tudo ok.
    """

    st = onboarding_status(user, request=request, allow_demo=True)

    require_legal = VOCACIONAL_REQUIRE_TERMOS or VOCACIONAL_REQUIRE_CONSENT
    if require_legal and not st.get("has_legal"):
        return "legal"

    if VOCACIONAL_REQUIRE_BONUS and not st.get("has_valid_guia"):
        return "bonus_acquire"

    if VOCACIONAL_REQUIRE_GUIA and not st.get("has_guia_feedback"):
        return "guia"

    if VOCACIONAL_REQUIRE_BONUS and not bonus_acquired(user, request=request):
        return "bonus_acquire"

    return None


def next_url(user, *, request=None) -> str:
    step = next_step(user, request=request)
    routes = {
        "bonus_acquire": reverse("portal"),  # aqui você pode apontar para uma página de compra
        "legal": reverse("core:legal_aceite"),
        "guia": reverse("vocacional:guia_avaliacao"),
        "ok": reverse("vocacional:index"),
    }
    if step is None:
        return routes["ok"]
    return routes.get(step, routes["ok"])
