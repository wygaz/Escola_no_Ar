# vocacional_sprint1_addons\apps\vocacional\views_consent.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .models_consent import Consentimento
from .forms import forms as _forms  # fallback if forms not imported; we will define simple form inline if missing

try:
    from .forms import forms, Form
except Exception:
    from django import forms as django_forms
    class ConsentimentoForm(django_forms.Form):
        nome = django_forms.CharField(label="Nome", max_length=120)
        email = django_forms.EmailField(label="E-mail")
else:
    from django import forms as django_forms
    class ConsentimentoForm(django_forms.Form):
        nome = django_forms.CharField(label="Nome", max_length=120)
        email = django_forms.EmailField(label="E-mail")

@login_required
def consentimento_check(request):
    c = Consentimento.objects.filter(user=request.user, ativo=True).first()
    if c:
        messages.info(request, "Seu consentimento já está ativo.")
        return redirect("vocacional:index")
    form = ConsentimentoForm()
    return render(request, "vocacional/consentimento_form.html", {"form": form})

@login_required
def consentimento_aceitar(request):
    if request.method == "POST":
        form = ConsentimentoForm(request.POST)
        if form.is_valid():
            Consentimento.objects.update_or_create(
                user=request.user, ativo=True,
                defaults={
                    "nome": form.cleaned_data["nome"].strip(),
                    "email": form.cleaned_data["email"].strip(),
                },
            )
            messages.success(request, "Consentimento registrado. Obrigado!")
            return redirect("vocacional:index")
        return render(request, "vocacional/consentimento_form.html", {"form": form})
    return redirect("vocacional:consentimento_check")

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
    c = Consentimento.objects.filter(user=request.user, ativo=True).first()
    return render(request, "vocacional/privacidade.html", {"consentimento": c})
