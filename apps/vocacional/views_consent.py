from __future__ import annotations

"""Compat para rotas antigas do Vocacional.

Agora, Termos + Privacidade/Consentimento são tratados pelo Core em uma única tela:
    core:legal_aceite

Mantemos estas views apenas para não quebrar URLs/templates antigos.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse


def privacidade(request):
    return redirect("core:privacidade")


def termos(request):
    return redirect("core:termos")


@login_required
def consentimento_check(request):
    # preserva ?next se veio de decorator
    nxt = request.GET.get("next")
    if nxt:
        return redirect(f"{reverse('core:legal_aceite')}?next={nxt}")
    return redirect("core:legal_aceite")


@login_required
def consentimento_aceitar(request):
    # tela única no Core
    return redirect("core:legal_aceite")


@login_required
def consentimento_revogar(request):
    # a revogação continua no Vocacional, pois altera o Consentimento do usuário
    from django.contrib import messages
    from django.utils import timezone

    from .models_consent import Consentimento

    if request.method != "POST":
        return redirect("core:legal_aceite")

    Consentimento.objects.filter(user=request.user, aceito=True).update(
        aceito=False,
        revogado_em=timezone.now(),
    )
    messages.info(request, "Seu consentimento foi revogado. Algumas áreas ficarão indisponíveis.")
    return redirect("portal")
