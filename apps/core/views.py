# apps\core\views.py
import logging
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django import forms
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.templatetags.static import static
from django.utils import timezone

from apps.core.permissions import (
    user_has_produto,
    onboarding_status,
    PROD_VOCACIONAL_75,
    PROD_SONHEMAISALTO,
)
from apps.core.product_registry import (
    SONHE_MAIS_ALTO_KEY,
    VOCACIONAL_KEY,
    iter_products,
    get_product_by_key,
    get_product_by_public_slug,
)


logger = logging.getLogger(__name__)


def _can_access_app(request, user, produto_slug: str, setting_flag: str, *, bypass_staff: bool = True) -> bool:
    """Regra central de liberação de acesso no Portal.

    Regra semântica atual:
    - Pendência legal continua obrigatória.
    - Guia válido é pré-requisito explícito do programa.
    - Avaliação do Guia só passa a ser exigida depois de Guia válido.
    - Se setting_flag=True: exige também produto/entitlement.

    Observação: bypass_staff=False força staff a respeitar os gates (modo user).
    """
    return _product_access_facts(
        request,
        user,
        produto_slug,
        setting_flag,
        bypass_staff=bypass_staff,
    )["can_access"]


def _product_access_facts(request, user, produto_slug: str, setting_flag: str, *, bypass_staff: bool = True) -> dict:
    st = onboarding_status(user, request=request, bypass_staff=bypass_staff)
    require_bonus = getattr(settings, setting_flag, True)
    has_access_slug = user_has_produto(user, produto_slug, bypass_staff=bypass_staff)
    has_valid_guia = st.get("has_valid_guia", False)
    has_bonus_path = bool(has_valid_guia or has_access_slug)
    guia_feedback_blocking = bool(require_bonus and has_bonus_path and not st["has_guia_feedback"])

    can_access = False
    if st["has_legal"]:
        if (not require_bonus) or has_access_slug:
            if not guia_feedback_blocking:
                can_access = True if require_bonus else True

    return {
        "status": st,
        "require_bonus": require_bonus,
        "has_valid_guia": has_valid_guia,
        "has_access_slug": has_access_slug,
        "has_bonus_path": has_bonus_path,
        "guia_feedback_blocking": guia_feedback_blocking,
        "inconsistent_bonus_without_guia": False,
        "can_access": can_access,
    }


def _notify_inconsistent_bonus_without_guia(request, user, produto_slug: str) -> None:
    if not getattr(user, "is_authenticated", False):
        return
    if not hasattr(request, "session"):
        return

    session_key = f"admin_alert_bonus_without_guia:{produto_slug}:{getattr(user, 'pk', 'anon')}"
    if request.session.get(session_key):
        return

    destinatario = getattr(settings, "EMAIL_CONTATO", getattr(settings, "DEFAULT_FROM_EMAIL", None))
    if destinatario:
        send_mail(
            subject=f"[Governança] Bônus sem Guia explícito: {produto_slug}",
            message=(
                "Estado inconsistente detectado no gating.\n\n"
                f"Usuário: {getattr(user, 'email', user.pk)}\n"
                f"Produto: {produto_slug}\n"
                f"URL: {request.get_full_path()}\n\n"
                "O usuário possui acesso ao bônus/produto, mas não possui Guia explícito como pré-requisito válido."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=True,
        )

    request.session[session_key] = True
    request.session.modified = True


def _portal_locked_cta(request, user, produto_slug: str, setting_flag: str, *, bypass_staff: bool) -> dict:
    """Mensagem + CTA quando o card está bloqueado no Portal."""
    facts = _product_access_facts(
        request,
        user,
        produto_slug,
        setting_flag,
        bypass_staff=bypass_staff,
    )
    st = facts["status"]

    # 1) Termos/LGPD pendentes
    if not st["has_legal"]:
        return {
            "alert": "Antes de acessar os bônus, aceite Termos e Privacidade.",
            "cta_url": f"{reverse('core:legal_aceite')}?next={reverse('portal')}",
            "cta_label": "Aceitar Termos e Privacidade",
            "tooltip": "Você ainda não concluiu Termos e Privacidade (LGPD).",
        }

    # 2) Produto/entitlement pendente
    if facts["require_bonus"] and not facts["has_access_slug"]:
        return {
            "alert": "Antes de seguir, é necessário possuir o Guia ou receber liberação administrativa do produto.",
            "cta_url": reverse("guia"),
            "cta_label": "Obter Guia",
            "tooltip": "Sem acesso explícito ao produto, o portal continua bloqueado.",
        }

    # 3) Avaliação do Guia pendente
    if facts["guia_feedback_blocking"]:
        return {
            "alert": "Para liberar os bônus, responda a Avaliação do Guia.",
            "cta_url": reverse("vocacional:guia_avaliacao"),
            "cta_label": "Responder Avaliação do Guia",
            "tooltip": "Falta concluir a Avaliação do Guia.",
        }

    return {
        "alert": "Acesso não liberado.",
        "cta_url": reverse("guia"),
        "cta_label": "Como liberar acesso",
        "tooltip": "Acesso não liberado.",
    }


def _portal_bypass_staff(request, user) -> bool:
    return not (user.is_staff or user.is_superuser) or request.session.get("portal_mode") != "user"


def _build_product_state(
    request,
    user,
    *,
    public_slug: str,
    access_slug: str,
    setting_flag: str,
    resolver_slug: str,
    bypass_staff: bool,
) -> dict:
    facts = _product_access_facts(
        request,
        user,
        access_slug,
        setting_flag,
        bypass_staff=bypass_staff,
    )
    block = (
        _portal_locked_cta(
            request,
            user,
            access_slug,
            setting_flag,
            bypass_staff=bypass_staff,
        )
        if not facts["can_access"]
        else {}
    )
    return {
        "public_slug": public_slug,
        "resolver_slug": resolver_slug,
        "access_slug": access_slug,
        "require_bonus": facts["require_bonus"],
        "has_valid_guia": facts["has_valid_guia"],
        "has_access_slug": facts["has_access_slug"],
        "guia_feedback_blocking": facts["guia_feedback_blocking"],
        "inconsistent_bonus_without_guia": facts["inconsistent_bonus_without_guia"],
        "can_access": facts["can_access"],
        "alert": block.get("alert", ""),
        "cta_url": block.get("cta_url", ""),
        "cta_label": block.get("cta_label", ""),
        "tooltip": block.get("tooltip", ""),
    }


def _apply_portal_attention_flags(ctx: dict) -> dict:
    # Exibir a caixa de pendÃªncias apenas quando houver algo a regularizar.
    # Importante: NÃƒO exigimos um "produto Guia" separado.
    # O Guia Ã© inferido pelo onboarding (Termos/LGPD + AvaliaÃ§Ã£o do Guia),
    # e os bÃ´nus sÃ£o controlados pelos prÃ³prios produtos/entitlements.
    need_bonus_sma = bool(ctx.get("req_bonus_sma")) and (not ctx.get("has_prod_sma"))
    need_bonus_voc = bool(ctx.get("req_bonus_voc")) and (not ctx.get("has_prod_voc"))
    product_states = ctx.get("product_states") or {}
    guia_feedback_pending = any(
        state.get("guia_feedback_blocking") for state in product_states.values()
    )

    ctx["need_bonus_sma"] = need_bonus_sma
    ctx["need_bonus_voc"] = need_bonus_voc
    ctx["show_guia_feedback_pending"] = guia_feedback_pending
    ctx["show_attention"] = bool(
        (not ctx.get("has_legal"))
        or guia_feedback_pending
        or need_bonus_sma
        or need_bonus_voc
    )
    return ctx


def _build_portal_user_context(request, user) -> dict:
    bypass_staff = _portal_bypass_staff(request, user)
    st = onboarding_status(user, request=request, bypass_staff=bypass_staff)
    sonhe_product = get_product_by_key(SONHE_MAIS_ALTO_KEY)
    vocacional_product = get_product_by_key(VOCACIONAL_KEY)
    sonhe_state = _build_product_state(
        request,
        user,
        public_slug=sonhe_product.public_slug,
        access_slug=sonhe_product.access_slug,
        setting_flag=sonhe_product.setting_flag,
        resolver_slug=sonhe_product.public_slug,
        bypass_staff=bypass_staff,
    )
    voc_state = _build_product_state(
        request,
        user,
        public_slug=vocacional_product.public_slug,
        access_slug=vocacional_product.access_slug,
        setting_flag=vocacional_product.setting_flag,
        resolver_slug=vocacional_product.public_slug,
        bypass_staff=bypass_staff,
    )
    ctx = {
        "hide_global_header": True,
        "products": {
            SONHE_MAIS_ALTO_KEY: sonhe_product,
            VOCACIONAL_KEY: vocacional_product,
        },
        "product_states": {
            sonhe_product.key: sonhe_state,
            vocacional_product.key: voc_state,
        },
        "can_sonhemaisalto": sonhe_state["can_access"],
        "can_vocacional": voc_state["can_access"],
        "sonhe_alert": sonhe_state["alert"],
        "sonhe_cta_url": sonhe_state["cta_url"],
        "sonhe_cta_label": sonhe_state["cta_label"],
        "sonhe_tooltip": sonhe_state["tooltip"],
        "voc_alert": voc_state["alert"],
        "voc_cta_url": voc_state["cta_url"],
        "voc_cta_label": voc_state["cta_label"],
        "voc_tooltip": voc_state["tooltip"],
        "show_governanca_toggle": bool(user.is_staff or user.is_superuser),
        "has_legal": st["has_legal"],
        "has_valid_guia": st.get("has_valid_guia", False),
        "has_guia_feedback": st["has_guia_feedback"],
        "has_onboarding": st["has_onboarding"],
        "has_prod_guia_like": st.get("has_valid_guia", False),
        "has_prod_voc": voc_state["has_access_slug"],
        "has_prod_sma": sonhe_state["has_access_slug"],
        "req_bonus_voc": voc_state["require_bonus"],
        "req_bonus_sma": sonhe_state["require_bonus"],
    }
    ctx["portal_entry_cta"] = _build_portal_entry_cta(ctx)
    return _apply_portal_attention_flags_v2(ctx)


def _apply_portal_attention_flags_v2(ctx: dict) -> dict:
    need_bonus_sma = bool(ctx.get("req_bonus_sma")) and bool(ctx.get("has_valid_guia")) and (not ctx.get("has_prod_sma"))
    need_bonus_voc = bool(ctx.get("req_bonus_voc")) and bool(ctx.get("has_valid_guia")) and (not ctx.get("has_prod_voc"))
    product_states = ctx.get("product_states") or {}
    guia_feedback_pending = any(
        state.get("guia_feedback_blocking") for state in product_states.values()
    )
    inconsistent_bonus_without_guia = any(
        state.get("inconsistent_bonus_without_guia") for state in product_states.values()
    )
    has_any_product_access = bool(ctx.get("has_prod_sma") or ctx.get("has_prod_voc"))
    show_valid_guia_pending = (not ctx.get("has_valid_guia")) and (not has_any_product_access)

    ctx["need_bonus_sma"] = need_bonus_sma
    ctx["need_bonus_voc"] = need_bonus_voc
    ctx["show_valid_guia_pending"] = show_valid_guia_pending
    ctx["show_guia_feedback_pending"] = guia_feedback_pending
    ctx["has_inconsistent_bonus_without_guia"] = inconsistent_bonus_without_guia
    ctx["show_attention"] = bool(
        (not ctx.get("has_legal"))
        or show_valid_guia_pending
        or guia_feedback_pending
        or need_bonus_sma
        or need_bonus_voc
    )
    return ctx


def _build_portal_entry_cta(ctx: dict) -> dict:
    if not ctx.get("has_legal"):
        return {
            "label": "Continuar",
            "url": reverse("core:legal_aceite") + f"?next={reverse('portal')}",
            "secondary_label": "Como funciona",
            "secondary_url": "#como-funciona",
        }

    if ctx.get("show_guia_feedback_pending"):
        return {
            "label": "Continuar",
            "url": reverse("vocacional:guia_avaliacao") + f"?next={reverse('portal')}",
            "secondary_label": "Como funciona",
            "secondary_url": "#como-funciona",
        }

    if ctx.get("can_vocacional"):
        return {
            "label": "Ir para meu proximo passo",
            "url": reverse("produto_resolver", args=["vocacional"]),
            "secondary_label": "Explorar a plataforma",
            "secondary_url": "#produtos",
        }

    if ctx.get("can_sonhemaisalto"):
        return {
            "label": "Ir para meu proximo passo",
            "url": reverse("produto_resolver", args=["sonhe-mais-alto"]),
            "secondary_label": "Explorar a plataforma",
            "secondary_url": "#produtos",
        }

    if ctx.get("show_valid_guia_pending"):
        return {
            "label": "Obter o Guia",
            "url": reverse("guia"),
            "secondary_label": "Como funciona",
            "secondary_url": "#como-funciona",
        }

    return {
        "label": "Explorar a plataforma",
        "url": "#produtos",
        "secondary_label": "Como funciona",
        "secondary_url": "#como-funciona",
    }


def _sync_portal_mode(request) -> str | None:
    mode = request.GET.get("portal_mode")
    if mode in {"user", "gov"}:
        request.session["portal_mode"] = mode
        return mode
    return request.session.get("portal_mode")


def _should_redirect_to_governance(request, user) -> bool:
    if not (user.is_staff or user.is_superuser):
        return False
    return _sync_portal_mode(request) != "user"


def _resolve_produto_config(produto_slug: str) -> dict | None:
    product = get_product_by_public_slug(produto_slug)
    if product is None:
        return None
    return {
        "access_slug": product.access_slug,
        "setting_flag": product.setting_flag,
        "entry_url_name": product.entry_url_name,
    }


@login_required
def _legacy_portal_home_pre_patch1(request):
    # toggle para testes (fica salvo na sessão)
    mode = request.GET.get("portal_mode")
    if mode in {"user", "gov"}:
        request.session["portal_mode"] = mode

    u = request.user

    # staff/superuser: por padrão vai para governança, a menos que force modo user
    if (u.is_staff or u.is_superuser) and request.session.get("portal_mode") != "user":
        return redirect("portal_dashboard")

    # usuário comum (ou staff em modo user): portal simples (2 opções)
    bypass_staff = not (u.is_staff or u.is_superuser) or request.session.get("portal_mode") != "user"

    can_sonhemaisalto = _can_access_app(
        request, u, PROD_SONHEMAISALTO, "SONHEMAISALTO_REQUIRE_BONUS", bypass_staff=bypass_staff
    )
    can_vocacional = _can_access_app(
        request, u, PROD_VOCACIONAL_75, "VOCACIONAL_REQUIRE_BONUS", bypass_staff=bypass_staff
    )

    sonhe_block = (
        _portal_locked_cta(request, u, PROD_SONHEMAISALTO, "SONHEMAISALTO_REQUIRE_BONUS", bypass_staff=bypass_staff)
        if not can_sonhemaisalto
        else {}
    )
    voc_block = (
        _portal_locked_cta(request, u, PROD_VOCACIONAL_75, "VOCACIONAL_REQUIRE_BONUS", bypass_staff=bypass_staff)
        if not can_vocacional
        else {}
    )

    st = onboarding_status(u, request=request, bypass_staff=bypass_staff)

    ctx = {
        "hide_global_header": True,
        "can_sonhemaisalto": can_sonhemaisalto,
        "can_vocacional": can_vocacional,
        "sonhe_alert": sonhe_block.get("alert", ""),
        "sonhe_cta_url": sonhe_block.get("cta_url", ""),
        "sonhe_cta_label": sonhe_block.get("cta_label", ""),
        "sonhe_tooltip": sonhe_block.get("tooltip", ""),
        "voc_alert": voc_block.get("alert", ""),
        "voc_cta_url": voc_block.get("cta_url", ""),
        "voc_cta_label": voc_block.get("cta_label", ""),
        "voc_tooltip": voc_block.get("tooltip", ""),
        "show_governanca_toggle": bool(u.is_staff or u.is_superuser),

        # status para a "pílula ATENÇÃO"
        "has_legal": st["has_legal"],
        "has_guia_feedback": st["has_guia_feedback"],
        "has_onboarding": st["has_onboarding"],
        
        "has_prod_voc": user_has_produto(u, PROD_VOCACIONAL_75, bypass_staff=bypass_staff),
        "has_prod_sma": user_has_produto(u, PROD_SONHEMAISALTO, bypass_staff=bypass_staff),
        "req_bonus_voc": getattr(settings, "VOCACIONAL_REQUIRE_BONUS", False),
        "req_bonus_sma": getattr(settings, "SONHEMAISALTO_REQUIRE_BONUS", False),
    }


    # Exibir a caixa de pendências apenas quando houver algo a regularizar.
    # Importante: NÃO exigimos um "produto Guia" separado.
    # O Guia é inferido pelo onboarding (Termos/LGPD + Avaliação do Guia),
    # e os bônus são controlados pelos próprios produtos/entitlements.

    need_bonus_sma = bool(ctx.get("req_bonus_sma")) and (not ctx.get("has_prod_sma"))
    need_bonus_voc = bool(ctx.get("req_bonus_voc")) and (not ctx.get("has_prod_voc"))

    ctx["need_bonus_sma"] = need_bonus_sma
    ctx["need_bonus_voc"] = need_bonus_voc

    ctx["show_attention"] = bool(
        (not ctx.get("has_legal"))
        or (not ctx.get("has_guia_feedback"))
        or need_bonus_sma
        or need_bonus_voc
    )

    return render(request, "core/portal.html", ctx)



@login_required
def portal_home(request):
    user = request.user
    if _should_redirect_to_governance(request, user):
        return redirect("portal_dashboard")

    return render(request, "core/portal.html", _build_portal_user_context(request, user))


def _legacy_portal_pre_patch1_public(request):
    ctx = {"hide_global_header": True}
    if request.user.is_authenticated:
        ctx.update(_build_portal_user_context(request, request.user))
    return render(request, "core/portal.html", ctx)


def sonhe_mais_alto_landing(request):
    context = {
        "hide_global_header": True,  # esconde o cabeçalho azul marinho
    }
    return render(request, "core/sonhe_mais_alto_landing.html", context)


def home_funil(request):
    """Entrada do site:
    - Usuário anônimo: vai para tela de login
    - Usuário logado: vai direto para o Portal
    """
    if request.user.is_authenticated:
        return redirect("portal")
    return redirect("contas:login")


class ContatoForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=100)
    email = forms.EmailField(label="E-mail")
    assunto = forms.CharField(label="Assunto", max_length=120, required=False)
    mensagem = forms.CharField(
        label="Mensagem",
        widget=forms.Textarea(attrs={"rows": 5}),
    )


def sobre(request):
    return render(request, "sobre.html")


def _legacy_portal_pre_patch1_authenticated(request):
    # raiz pública (logado ou não). Se estiver logado, já exibe flags de acesso.
    ctx = {"hide_global_header": True}
    if request.user.is_authenticated:
        u = request.user
        bypass_staff = not (u.is_staff or u.is_superuser) or request.session.get("portal_mode") != "user"

        can_sonhemaisalto = _can_access_app(
            request, u, PROD_SONHEMAISALTO, "SONHEMAISALTO_REQUIRE_BONUS", bypass_staff=bypass_staff
        )
        can_vocacional = _can_access_app(
            request, u, PROD_VOCACIONAL_75, "VOCACIONAL_REQUIRE_BONUS", bypass_staff=bypass_staff
        )

        sonhe_block = (
            _portal_locked_cta(request, u, PROD_SONHEMAISALTO, "SONHEMAISALTO_REQUIRE_BONUS", bypass_staff=bypass_staff)
            if not can_sonhemaisalto
            else {}
        )
        voc_block = (
            _portal_locked_cta(request, u, PROD_VOCACIONAL_75, "VOCACIONAL_REQUIRE_BONUS", bypass_staff=bypass_staff)
            if not can_vocacional
            else {}
        )

        st = onboarding_status(u, request=request, bypass_staff=bypass_staff)

        ctx.update(
            {
                "can_sonhemaisalto": can_sonhemaisalto,
                "can_vocacional": can_vocacional,
                "sonhe_alert": sonhe_block.get("alert", ""),
                "sonhe_cta_url": sonhe_block.get("cta_url", ""),
                "sonhe_cta_label": sonhe_block.get("cta_label", ""),
                "sonhe_tooltip": sonhe_block.get("tooltip", ""),
                "voc_alert": voc_block.get("alert", ""),
                "voc_cta_url": voc_block.get("cta_url", ""),
                "voc_cta_label": voc_block.get("cta_label", ""),
                "voc_tooltip": voc_block.get("tooltip", ""),
                "show_governanca_toggle": bool(u.is_staff or u.is_superuser),
                "has_legal": st["has_legal"],
                "has_guia_feedback": st["has_guia_feedback"],
                "has_onboarding": st["has_onboarding"],
                
                "has_prod_voc": user_has_produto(u, PROD_VOCACIONAL_75, bypass_staff=bypass_staff),
                "has_prod_sma": user_has_produto(u, PROD_SONHEMAISALTO, bypass_staff=bypass_staff),
                "req_bonus_voc": getattr(settings, "VOCACIONAL_REQUIRE_BONUS", False),
                "req_bonus_sma": getattr(settings, "SONHEMAISALTO_REQUIRE_BONUS", False),
            }
        )


    # Exibir a caixa de pendências apenas quando houver algo a regularizar.
    # Importante: NÃO exigimos um "produto Guia" separado.
    # O Guia é inferido pelo onboarding (Termos/LGPD + Avaliação do Guia),
    # e os bônus são controlados pelos próprios produtos/entitlements.

    need_bonus_sma = bool(ctx.get("req_bonus_sma")) and (not ctx.get("has_prod_sma"))
    need_bonus_voc = bool(ctx.get("req_bonus_voc")) and (not ctx.get("has_prod_voc"))

    ctx["need_bonus_sma"] = need_bonus_sma
    ctx["need_bonus_voc"] = need_bonus_voc

    ctx["show_attention"] = bool(
        (not ctx.get("has_legal"))
        or (not ctx.get("has_guia_feedback"))
        or need_bonus_sma
        or need_bonus_voc
    )

    return render(request, "core/portal.html", ctx)



def portal(request):
    ctx = {"hide_global_header": True}
    if request.user.is_authenticated:
        return portal_home(request)
    return render(request, "core/portal.html", ctx)


def produto_resolver(request, produto_slug: str):
    config = _resolve_produto_config(produto_slug)
    if config is None:
        messages.error(request, "Produto nÃ£o encontrado.")
        return redirect("portal")

    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    user = request.user
    if _should_redirect_to_governance(request, user):
        return redirect("portal_dashboard")

    bypass_staff = _portal_bypass_staff(request, user)
    if not _can_access_app(
        request,
        user,
        config["access_slug"],
        config["setting_flag"],
        bypass_staff=bypass_staff,
    ):
        block = _portal_locked_cta(
            request,
            user,
            config["access_slug"],
            config["setting_flag"],
            bypass_staff=bypass_staff,
        )
        return redirect(block["cta_url"])

    return redirect(config["entry_url_name"])


# Neutraliza aliases legados do Patch 1 sem manter regra duplicada ativa.
_legacy_portal_home_pre_patch1 = portal_home
_legacy_portal_pre_patch1_public = portal
_legacy_portal_pre_patch1_authenticated = portal


def contato(request):
    if request.method == "POST":
        form = ContatoForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            assunto = cd.get("assunto") or "Contato pelo site Escola no Ar"
            corpo = (
                f"Nome: {cd['nome']}\n"
                f"E-mail: {cd['email']}\n\n"
                f"Mensagem:\n{cd['mensagem']}"
            )

            destinatario = getattr(settings, "EMAIL_CONTATO", getattr(settings, "DEFAULT_FROM_EMAIL", None))

            if destinatario:
                send_mail(
                    subject=assunto,
                    message=corpo,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[destinatario],
                    fail_silently=True,  # evita quebrar se o email não estiver configurado
                )

            messages.success(request, "Mensagem enviada com sucesso! Obrigado pelo contato.")
            return redirect("contato")
    else:
        form = ContatoForm()

    return render(request, "contato.html", {"form": form})


# --------------------------------------------------------------------
# Impersonação ("Testar como usuário")
# --------------------------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def portal_impersonar(request):
    """Tela para staff/superuser escolher um usuário real para testar o fluxo.

    Armazena o usuário alvo na sessão. O middleware do Core troca request.user
    apenas nas rotas "de usuário" (Portal/Vocacional/Projeto21), mantendo
    request.real_user para voltar à governança.
    """
    real = request.user
    if not (getattr(real, "is_staff", False) or getattr(real, "is_superuser", False)):
        messages.error(request, "Apenas staff/superusuário pode testar como outro usuário.")
        return redirect("portal")

    User = get_user_model()

    # Se chegou por POST, assume o usuário selecionado
    if request.method == "POST":
        user_id = (request.POST.get("user_id") or "").strip()
        if not user_id.isdigit():
            messages.error(request, "Selecione um usuário válido.")
            return redirect("portal_impersonar")

        try:
            target = User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
            return redirect("portal_impersonar")

        # Evita impersonar um staff/superuser por engano (quase sempre confunde).
        if getattr(target, "is_staff", False) or getattr(target, "is_superuser", False):
            messages.warning(request, "Dica: prefira um usuário comum (não-staff) para testes de fluxo.")

        request.session["impersonate_user_id"] = target.pk
        request.session["portal_mode"] = "user"  # garante que /portal/ não redirecione para governança
        messages.success(request, f"Agora você está testando como: {getattr(target, 'email', target.pk)}")
        return redirect("portal")

    q = (request.GET.get("q") or "").strip()
    results = []
    if q:
        # Busca simples por e-mail/nome.
        # Mantém compatibilidade com o campo legado 'nome'.
        results = (
            User.objects.filter(
                Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(nome__icontains=q)
            )
            .order_by("email")[:25]
        )

    current = None
    imp_id = request.session.get("impersonate_user_id")
    if imp_id:
        try:
            current = User.objects.get(pk=imp_id)
        except User.DoesNotExist:
            request.session.pop("impersonate_user_id", None)

    ctx = {
        "hide_global_header": True,
        "q": q,
        "results": results,
        "current_impersonated": current,
    }
    return render(request, "portal/impersonar.html", ctx)


@login_required
def portal_impersonar_sair(request):
    """Sai do modo teste e volta para a governança."""
    real = request.user
    if not (getattr(real, "is_staff", False) or getattr(real, "is_superuser", False)):
        return redirect("portal")

    had_impersonate_user_id = "impersonate_user_id" in request.session
    portal_mode = request.session.get("portal_mode")
    request.session.pop("impersonate_user_id", None)
    request.session.pop("portal_mode", None)
    request.session.modified = True
    logger.warning(
        "AUTH portal_impersonar_sair user=%s had_impersonate_user_id=%s portal_mode=%r cleared_keys=%s final_redirect=%r",
        getattr(real, "email", getattr(real, "pk", "anon")),
        had_impersonate_user_id,
        portal_mode,
        ["impersonate_user_id", "portal_mode"],
        reverse("portal_dashboard"),
    )
    messages.info(request, "Modo teste encerrado.")
    return redirect("portal_dashboard")


TEMPLATE_BY_PERFIL = {
    "ADMIN": "portal/admin_home.html",
    "PROF": "portal/prof_home.html",
    "MENTOR": "portal/mentor_home.html",
    "ALUNO": "portal/aluno_home.html",
    "USER": "portal/user_home.html",
}


def _build_governance_subject_context(request, target_user) -> dict:
    from apps.contas.models_acessos import Acesso, Produto

    product_states = {}
    for product in iter_products():
        product_states[product.key] = _build_product_state(
            request,
            target_user,
            public_slug=product.public_slug,
            access_slug=product.access_slug,
            setting_flag=product.setting_flag,
            resolver_slug=product.public_slug,
            bypass_staff=False,
        )

    status = onboarding_status(target_user, request=request, bypass_staff=False)
    active_accesses = list(
        Acesso.objects.filter(user=target_user, expires_at__isnull=True)
        .select_related("produto")
        .order_by("produto__slug", "-granted_at")
    )
    active_access_slugs = {acesso.produto.slug for acesso in active_accesses}
    active_access_product_ids = {acesso.produto_id for acesso in active_accesses}
    available_products = list(Produto.objects.order_by("nome", "slug"))

    return {
        "selected_user": target_user,
        "selected_user_status": status,
        "selected_user_product_states": product_states,
        "selected_user_active_accesses": active_accesses,
        "selected_user_active_access_slugs": active_access_slugs,
        "selected_user_active_access_product_ids": active_access_product_ids,
        "governance_available_products": available_products,
        "governance_product_add_url": reverse("admin:contas_produto_add"),
    }

# --------------------------------------------------------------------
# Governança (dashboard.html) — compatibilidade: urls.py espera este CBV
# --------------------------------------------------------------------
class PortalDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "portal/dashboard.html"

    def test_func(self):
        u = self.request.user
        allowed = bool(getattr(u, 'is_staff', False) or getattr(u, 'is_superuser', False))
        if not allowed:
            logger.warning(
                "AUTH PortalDashboardView.test_func denied path=%r user=%s is_staff=%s is_superuser=%s portal_mode=%r real_user=%s",
                self.request.path,
                getattr(u, "email", getattr(u, "pk", "anon")),
                getattr(u, "is_staff", False),
                getattr(u, "is_superuser", False),
                self.request.session.get("portal_mode"),
                getattr(getattr(self.request, "real_user", None), "email", None),
            )
        return allowed

    def post(self, request, *args, **kwargs):
        from apps.contas.models_acessos import Acesso, Produto

        user_id = (request.POST.get("user_id") or "").strip()
        produto_ids = [pid for pid in request.POST.getlist("produto_ids") if pid and pid.isdigit()]
        action = (request.POST.get("action") or "").strip()
        q = (request.POST.get("q") or "").strip()

        redirect_url = reverse("portal_dashboard")
        query_data = {}
        if q:
            query_data["q"] = q
        if user_id:
            query_data["user_id"] = user_id
        if query_data:
            redirect_url = f"{redirect_url}?{urlencode(query_data)}"

        if action not in {"grant", "revoke"}:
            messages.error(request, "Ação de governança inválida.")
            return redirect(redirect_url)

        if not user_id.isdigit() or not produto_ids:
            messages.error(request, "Selecione um usuário e pelo menos um produto válido.")
            return redirect(redirect_url)

        User = get_user_model()
        try:
            target_user = User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
            return redirect(reverse("portal_dashboard"))

        produtos = list(Produto.objects.filter(pk__in=[int(pid) for pid in produto_ids]).order_by("nome", "slug"))
        if not produtos:
            messages.error(request, "Nenhum produto válido foi encontrado.")
            return redirect(redirect_url)

        if action == "grant":
            created_names = []
            already_names = []
            for produto in produtos:
                active_qs = Acesso.objects.filter(
                    user=target_user,
                    produto=produto,
                    expires_at__isnull=True,
                )
                if active_qs.exists():
                    already_names.append(produto.nome)
                    continue
                Acesso.objects.create(
                    user=target_user,
                    produto=produto,
                    origem="governanca_manual",
                )
                created_names.append(produto.nome)

            if created_names:
                messages.success(
                    request,
                    f"Acessos concedidos para {target_user.email}: {', '.join(created_names)}.",
                )
            if already_names:
                messages.info(
                    request,
                    f"Acessos já ativos para {target_user.email}: {', '.join(already_names)}.",
                )
            return redirect(redirect_url)

        revoked_names = []
        missing_names = []
        for produto in produtos:
            updated = Acesso.objects.filter(
                user=target_user,
                produto=produto,
                expires_at__isnull=True,
            ).update(expires_at=timezone.now())
            if updated:
                revoked_names.append(produto.nome)
            else:
                missing_names.append(produto.nome)

        if revoked_names:
            messages.success(
                request,
                f"Acessos removidos de {target_user.email}: {', '.join(revoked_names)}.",
            )
        if missing_names:
            messages.info(
                request,
                f"Sem acesso ativo para remoção em {target_user.email}: {', '.join(missing_names)}.",
            )
        return redirect(redirect_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        u = self.request.user
        User = get_user_model()

        # Reaproveita a mesma regra do Portal simples
        ctx["can_sonhemaisalto"] = _can_access_app(self.request, u, PROD_SONHEMAISALTO, "SONHEMAISALTO_REQUIRE_BONUS")
        ctx["can_vocacional"] = _can_access_app(self.request, u, PROD_VOCACIONAL_75, "VOCACIONAL_REQUIRE_BONUS")
        q = (self.request.GET.get("q") or "").strip()
        selected_user = None
        results = []

        if q:
            results = list(
                User.objects.filter(
                    Q(email__icontains=q)
                    | Q(first_name__icontains=q)
                    | Q(last_name__icontains=q)
                    | Q(nome__icontains=q)
                ).order_by("email")[:15]
            )

        selected_user_id = (self.request.GET.get("user_id") or "").strip()
        if selected_user_id.isdigit():
            try:
                selected_user = User.objects.get(pk=int(selected_user_id))
            except User.DoesNotExist:
                messages.warning(self.request, "Usuário selecionado não foi encontrado.")
        elif len(results) == 1:
            selected_user = results[0]

        ctx["governance_search_query"] = q
        ctx["governance_search_results"] = results
        if selected_user is not None:
            ctx.update(_build_governance_subject_context(self.request, selected_user))

        # Tudo opcional: se o app/tabela não existir, ignora
        try:
            from apps.sonho_de_ser.models import Mentoria
            ctx["mentorandos_count"] = Mentoria.objects.filter(mentor=u, ativo=True, status="ATIVA").count()
        except Exception:
            pass

        try:
            from apps.cursos.models import Curso, Matricula, Turma
            if getattr(u, "perfil", None) == "PROF":
                ctx["cursos_count"] = Curso.objects.filter(professor=u).count()
                ctx["turmas_count"] = Turma.objects.filter(professor=u).count()
            else:
                ctx["cursos_count"] = Matricula.objects.filter(aluno=u, status="ATIVO").count()
        except Exception:
            pass

        try:
            from apps.atividades.models import AtividadeResposta
            ctx["atividades_pendentes"] = AtividadeResposta.objects.filter(aluno=u, status="PENDENTE").count()
        except Exception:
            pass

        return ctx


# --------------------------------------------------------------------
# Guia (preview + redirect) — compatibilidade: urls.py espera esta view
# --------------------------------------------------------------------
HOTMART_GUIA_URL = "https://pay.hotmart.com/Q103340890M?bid=1765338293599"

def guia_redirect_preview(request):
    """
    Página com Open Graph para gerar preview (WhatsApp/FB/IG),
    e redireciona o usuário para a Hotmart.
    """
    og_title = "Guia de Descoberta"
    og_description = (
        "Menos ansiedade, mais direção: escolhas de curso e profissão para jovens. "
        "Apoio a pais e mentores."
    )

    # Capa de compartilhamento do Guia em static/core/img/capa-guia.png
    og_image = request.build_absolute_uri(static("core/img/capa-guia.png"))
    og_url = request.build_absolute_uri(request.path)

    context = {
        "hotmart_url": HOTMART_GUIA_URL,
        "og_title": og_title,
        "og_description": og_description,
        "og_image": og_image,
        "og_url": og_url,
    }
    return render(request, "core/guia_redirect.html", context)
