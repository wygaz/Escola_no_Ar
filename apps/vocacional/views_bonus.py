# apps/vocacional/views_bonus.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from .gating import next_step, next_url, bonus_acquired, consent_ok, guia_done, require_bonus

@login_required
def bonus(request):
    # Se bônus está pausado, não deveria cair aqui — mas por segurança:
    if not require_bonus():
        return redirect(next_url(request.user))

    # Se já tem bônus, vá para 'validar' (mostrar pendências)
    if bonus_acquired(request.user):
        return redirect("vocacional:bonus_validar")

    # Ainda não tem bônus: só mostra CTA de compra/resgate (SEM link para form)
    return render(request, "vocacional/bonus.html")

@login_required
def bonus_validar(request):
    if not bonus_acquired(request.user):
        return redirect("vocacional:bonus")

    pendencias = []
    if not consent_ok(request.user):
        pendencias.append(("Aceitar Termos de Uso e Privacidade", "vocacional:consentimento_check"))
    if not guia_done(request.user):
        pendencias.append(("Concluir Avaliação do Guia", "vocacional:guia_avaliacao"))

    if not pendencias:
        # todas pendências resolvidas → gating mandará ao form
        return redirect(next_url(request.user))

    return render(request, "vocacional/bonus_validar.html", {"pendencias": pendencias})
