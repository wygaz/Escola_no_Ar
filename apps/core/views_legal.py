# apps/core/views_legal.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, render
from django.utils import timezone
from django.urls import reverse


def termos(request):
    """Termos de uso (público para leitura)."""
    return render(request, "core/legal/termos.html")


def privacidade(request):
    """Política de privacidade (público para leitura)."""
    return render(request, "core/legal/privacidade.html")


def legal_aceite(request):
    """
    Tela ÚNICA de aceite (Termos + Privacidade/Consentimento LGPD).
    - exige login
    - registra:
        * apps.vocacional.models.AvaliacaoGuia.aceite_termos
        * apps.vocacional.models_consent.Consentimento (aceito/revogado_em)
    """
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    # imports locais (evita acoplamento forte no import do módulo)
    from apps.vocacional.forms import ConsentimentoForm
    from apps.vocacional.models import AvaliacaoGuia
    from apps.vocacional.models_consent import Consentimento

    next_param = request.GET.get("next") or request.POST.get("next")
    if not next_param:
        next_param = reverse("portal")

    if request.method == "POST":
        form = ConsentimentoForm(request.POST, initial={"email": request.user.email})

        aceite_termos = request.POST.get("aceite_termos") == "1"
        aceite_priv = request.POST.get("aceite_privacidade") == "1"

        if not aceite_termos or not aceite_priv:
            messages.error(request, "Você precisa marcar os dois aceites para continuar.")
        elif form.is_valid():
            nome = (form.cleaned_data.get("nome") or "").strip() or (
                request.user.get_full_name()
                or getattr(request.user, "nome", "")
                or request.user.email
            )

            # 1) Termos (flag simples, sem criar novo modelo)
            ag, _ = AvaliacaoGuia.objects.get_or_create(user=request.user)
            if not ag.aceite_termos:
                ag.aceite_termos = True
                ag.save(update_fields=["aceite_termos"])

            # 2) Consentimento LGPD
            Consentimento.objects.update_or_create(
                user=request.user,
                defaults={
                    "nome": nome,
                    "email": request.user.email,
                    "aceito": True,
                    "revogado_em": None,
                    "aceito_em": timezone.now(),
                },
            )

            messages.success(request, "Obrigado! Termos e Privacidade aceitos.")
            return redirect(next_param)
        else:
            messages.error(request, "Confira os dados informados.")

    else:
        form = ConsentimentoForm(
            initial={
                "nome": (
                    request.user.get_full_name()
                    or getattr(request.user, "nome", "")
                    or request.user.email
                ),
                "email": request.user.email,
            }
        )

    return render(
        request,
        "core/legal/aceite.html",
        {
            "form": form,
            "next": next_param,
        },
    )
