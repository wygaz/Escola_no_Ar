# apps/core/hotmart_integration.py

"""
Integração com Hotmart – funções auxiliares.

Objetivo principal:
- Receber dados de uma venda (e-mail, nome)
- Garantir que exista um Usuario com esse e-mail
- (Depois) marcar o acesso ao produto/bônus correspondente.
"""

from django.db import transaction
from django.utils.text import slugify

from apps.contas.models import Usuario
# Quando os modelos de produto/acesso estiverem prontos,
# descomente e ajuste os imports abaixo:
#
# from apps.core.models import Produto, Acesso  # EXEMPLO – ajuste para o lugar certo


@transaction.atomic
def processar_venda_hotmart(email: str, nome_completo: str | None = None) -> Usuario:
    """
    Recebe o e-mail (obrigatório) e o nome (opcional) do comprador,
    garante que exista um Usuario correspondente e, no futuro,
    poderá marcar o acesso ao produto.

    Retorna o Usuario.
    """
    if not email:
        raise ValueError("processar_venda_hotmart: email é obrigatório")

    email = email.strip().lower()
    nome_completo = (nome_completo or "").strip()

    # Quebrar nome em first_name / last_name (bem simples)
    partes = nome_completo.split()
    first_name = partes[0] if partes else ""
    last_name = " ".join(partes[1:]) if len(partes) > 1 else ""

    # Criar ou buscar o usuário
    usuario, created = Usuario.objects.get_or_create(
        email=email,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "perfil": getattr(Usuario, "PERFIL_ALUNO", getattr(Usuario, "PERFIL_USER", "USER")),
            "is_active": True,
        },
    )

    # 🔐 NÃO definimos senha aqui.
    # A ideia é enviar depois um e-mail de "definir senha" usando o fluxo padrão
    # de password_reset do Django, em vez de usar CPF como senha.

    # ------------------------------------------------------------
    # (FUTURO) Aqui será o lugar certo para ligar o bônus/produto:
    #
    # slug_produto = "projeto21"  # por exemplo
    # produto = Produto.objects.get(slug=slug_produto)
    # Acesso.objects.get_or_create(
    #     usuario=usuario,
    #     produto=produto,
    #     defaults={"ativo": True},
    # )
    # ------------------------------------------------------------

    return usuario
