# apps/core/capabilities.py
from __future__ import annotations
from dataclasses import dataclass


# níveis: none < starter < full
@dataclass(frozen=True)
class Cap:
    p21: str = "none" # "starter" para plano gratuito, "full" para completo
    vocacional: str = "none" # idem


# Mapa por perfil
CAPS_BY_PERFIL = {
    "ADMIN": Cap(p21="full", vocacional="full"),
    "PROF": Cap(p21="full", vocacional="full"),
    "MENTOR": Cap(p21="full", vocacional="full"),
    "ALUNO": Cap(p21="full", vocacional="full"),
    # Usuário (gratuito): apenas primeiro nível das apps
    "USER": Cap(p21="starter", vocacional="starter"),
}


ORDER = {"none": 0, "starter": 1, "full": 2}


def get_caps(user) -> Cap:
    perfil = getattr(user, "perfil", None) or "USER"
    return CAPS_BY_PERFIL.get(perfil, CAPS_BY_PERFIL["USER"]) # default USER


def has_cap(user, feature: str, level: str = "starter") -> bool:
    caps = get_caps(user)
    current = getattr(caps, feature, "none")
    return ORDER.get(current, 0) >= ORDER.get(level, 1)