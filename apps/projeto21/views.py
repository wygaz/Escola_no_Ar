# apps/projeto21/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from apps.contas.models_acessos import Acesso


def tem_acesso_projeto21(user) -> bool:
    if user.is_superuser or user.is_staff:
        return True
    return Acesso.objects.filter(
        user=user,
        produto__slug="projeto21_sonhe_alto",
        # ativo=True,  # se existir no modelo
    ).exists()


@login_required
def projeto21_home(request: HttpRequest) -> HttpResponse:
    """
    Home interna do Projeto 21 / Sonhe + Alto.

    - Requer login.
    - Faz triagem por Acesso (Hotmart/entitlement).
    - Esconde o cabeçalho global.
    """
    base_ctx = {"hide_global_header": True}

    if not tem_acesso_projeto21(request.user):
        return render(
            request,
            "projeto21/acesso_bloqueado.html",
            {**base_ctx, "motivo": "projeto21_sonhe_alto"},
        )

    return render(request, "projeto21/landing.html", base_ctx)


# Se você já tem rota /projeto21/landing/ apontando pra landing_projeto21,
# mantenha como “alias” para não quebrar links:
@login_required
def landing_projeto21(request: HttpRequest) -> HttpResponse:
    return projeto21_home(request)
