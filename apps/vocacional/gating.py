# apps/vocacional/gating.py
from __future__ import annotations

from django.conf import settings
from django.urls import reverse

from apps.core.permissions import (
    PROD_VOCACIONAL,
    user_has_produto,
)

# Flags (pode ligar/desligar via settings.py se quiser)
VOCACIONAL_REQUIRE_BONUS = getattr(settings, "VOCACIONAL_REQUIRE_BONUS", True)
VOCACIONAL_REQUIRE_TERMOS = getattr(settings, "VOCACIONAL_REQUIRE_TERMOS", True)
VOCACIONAL_REQUIRE_CONSENT = getattr(settings, "VOCACIONAL_REQUIRE_CONSENT", True)
VOCACIONAL_REQUIRE_GUIA = getattr(settings, "VOCACIONAL_REQUIRE_GUIA", True)


def bonus_acquired(user) -> bool:
    return user_has_produto(user, PROD_VOCACIONAL)


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


def next_step(user):
    """Retorna a próxima etapa do funil.

    Regra atual (2026-02):
    - Termos + Privacidade/Consentimento ficam em UMA página (core:legal_aceite).
    - A Avaliação do Guia é requisito apenas para liberar o bônus.

    Ordem: bonus -> legal -> guia -> ok
    Retorna None quando está tudo ok.
    """

    if VOCACIONAL_REQUIRE_BONUS and not bonus_acquired(user):
        return "bonus_acquire"

    require_legal = VOCACIONAL_REQUIRE_TERMOS or VOCACIONAL_REQUIRE_CONSENT
    if require_legal and not (termos_ok(user) and consent_ok(user)):
        return "legal"

    if VOCACIONAL_REQUIRE_GUIA and not guia_done(user):
        return "guia"

    return None


def next_url(user) -> str:
    step = next_step(user)
    routes = {
        "bonus_acquire": reverse("portal"),  # aqui você pode apontar para uma página de compra
        "legal": reverse("core:legal_aceite"),
        "guia": reverse("vocacional:guia_avaliacao"),
        "ok": reverse("vocacional:index"),
    }
    if step is None:
        return routes["ok"]
    return routes.get(step, routes["ok"])
