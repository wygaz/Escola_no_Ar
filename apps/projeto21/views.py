# apps/projeto21/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.core.permissions import (
    PROD_SONHEMAISALTO,
    require_guia_feedback,
    require_legal,
    require_produto,
)
@login_required
@require_legal()
@require_guia_feedback
@require_produto(PROD_SONHEMAISALTO)
def projeto21_home(request: HttpRequest) -> HttpResponse:
    """
    Home interna do Projeto 21 / Sonhe + Alto.

    - Requer login.
    - Faz triagem por acesso (entitlement).
    - Esconde o cabeçalho global.
    """
    base_ctx = {"hide_global_header": True}

    return render(request, "projeto21/landing.html", base_ctx)


# Alias para não quebrar links antigos
@login_required
def landing_projeto21(request: HttpRequest) -> HttpResponse:
    return projeto21_home(request)
