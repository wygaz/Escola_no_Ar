# apps/vocacional/views_consent.py
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import ConsentimentoForm          # defina no forms.py (nome, email disabled)
from .models_consent import Consentimento     # seu model real
from .gating import next_url

@login_required
def consentimento_check(request):
    # se já aceitou, segue o fluxo
    if Consentimento.objects.filter(user=request.user, aceito=True).exists():
        return redirect(next_url(request.user))
    form = ConsentimentoForm(initial={"nome": request.user.first_name, "email": request.user.email})
    return render(request, "vocacional/consentimento.html", {"form": form})

@login_required
@require_http_methods(["POST"])
def consentimento_aceitar(request):
    form = ConsentimentoForm(request.POST, initial={"email": request.user.email})
    if not form.is_valid():
        messages.error(request, "Confira os dados.")
        return render(request, "vocacional/consentimento.html", {"form": form})

    # opcional: atualizar nome exibido
    nome = (form.cleaned_data.get("nome") or "").strip()
    if nome and nome != (request.user.first_name or ""):
        request.user.first_name = nome
        request.user.save(update_fields=["first_name"])

    # registra consentimento (não confie no e-mail do POST)
    Consentimento.objects.update_or_create(
        user=request.user,
        defaults={"aceito": True, "aceito_em": timezone.now(), "email": request.user.email, "nome": nome},
    )
    messages.success(request, "Consentimento registrado.")
    return redirect(next_url(request.user))

@login_required
def consentimento_revogar(request):
    if request.method == "POST":
        c = Consentimento.objects.filter(user=request.user, ativo=True).first()
        if c:
            c.revogar()
            messages.info(request, "Consentimento revogado. Seus serviços foram interrompidos.")
        return redirect("vocacional:privacidade")
    return redirect("vocacional:privacidade")

@login_required
def privacidade(request):
    c = Consentimento.objects.filter(user=request.user).order_by("-aceito_em").first()
    return render(request, "vocacional/privacidade.html", {"consentimento": c})
