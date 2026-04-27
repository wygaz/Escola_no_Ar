# apps\core\views.py
import logging
import csv
import io
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib import messages
from django import forms
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.templatetags.static import static
from django.utils import timezone

from apps.core.permissions import (
    PROD_GUIA,
    get_active_demo_access,
    get_active_access_queryset,
    user_has_produto,
    onboarding_status,
    PROD_VOCACIONAL_75,
    PROD_SONHEMAISALTO,
    PROD_VOCACIONAL_150,
    PROD_VOCACIONAL_PREMIUM,
    slugs_equivalentes,
)
from apps.core.product_registry import (
    SONHE_MAIS_ALTO_KEY,
    VOCACIONAL_KEY,
    iter_products,
    get_product_by_key,
    get_product_by_public_slug,
)


logger = logging.getLogger(__name__)

GUIA_PROMOTIONAL_FILENAME = "Guia_de_Descoberta_envio.pdf"
GOVERNANCE_IMPORT_SESSION_KEY = "governance_import_preview_v1"


def _get_promotional_guide_pdf_path() -> Path:
    configured = getattr(settings, "GUIA_PROMOTIONAL_FILE", "")
    if configured:
        return Path(configured)
    return Path(str(settings.BASE_DIR)) / "storage" / "guia" / GUIA_PROMOTIONAL_FILENAME


def _send_promotional_guide_email(*, target_user, sent_by):
    pdf_path = _get_promotional_guide_pdf_path()
    if not pdf_path.exists():
        return False, (
            f"O arquivo promocional do Guia nao foi encontrado em {pdf_path}. "
            "Coloque o PDF canônico antes de tentar o envio."
        )

    if not getattr(target_user, "email", ""):
        return False, "O usuario nao possui e-mail cadastrado para receber o Guia."

    subject = "Guia de Descoberta - envio promocional"
    body = (
        f"Ola, {getattr(target_user, 'first_name', '') or target_user.email}!\n\n"
        "Segue o Guia de Descoberta em envio promocional.\n"
        "Depois da leitura, a Avaliacao do Guia continua obrigatoria para seguir no fluxo.\n\n"
        "Atenciosamente,\n"
        "Equipe Sonhe + Alto"
    )
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[target_user.email],
    )
    message.attach_file(str(pdf_path))
    message.send(fail_silently=False)
    return True, pdf_path.name


def _build_demo_intro_context(request, user, *, next_product_slug: str | None = None) -> dict:
    demo_access = get_active_demo_access(user)
    sonhe_product = get_product_by_key(SONHE_MAIS_ALTO_KEY)
    vocacional_product = get_product_by_key(VOCACIONAL_KEY)
    accepted_targets = {sonhe_product.public_slug, vocacional_product.public_slug}
    target_slug = next_product_slug if next_product_slug in accepted_targets else sonhe_product.public_slug
    target_product = get_product_by_public_slug(target_slug) or sonhe_product

    return {
        "hide_global_header": True,
        "demo_access": demo_access,
        "demo_target_product": target_product,
        "demo_target_url": f"{reverse('produto_resolver', args=[target_product.public_slug])}?demo_ready=1",
        "demo_vocacional_url": f"{reverse('produto_resolver', args=[vocacional_product.public_slug])}?demo_ready=1",
        "demo_sonhe_url": f"{reverse('produto_resolver', args=[sonhe_product.public_slug])}?demo_ready=1",
        "demo_portal_url": reverse("portal"),
        "sonhe_product": sonhe_product,
        "vocacional_product": vocacional_product,
    }


def _normalize_intro_target_slug(next_product_slug: str | None = None) -> str:
    sonhe_product = get_product_by_key(SONHE_MAIS_ALTO_KEY)
    vocacional_product = get_product_by_key(VOCACIONAL_KEY)
    accepted_targets = {sonhe_product.public_slug, vocacional_product.public_slug}
    if next_product_slug in accepted_targets:
        return next_product_slug
    return sonhe_product.public_slug


def _portal_next_step_url(next_product_slug: str | None = None) -> str:
    target_slug = _normalize_intro_target_slug(next_product_slug)
    return f"{reverse('portal_next_step')}?{urlencode({'next_product': target_slug})}"


def _build_next_step_context(request, user, *, next_product_slug: str | None = None) -> dict:
    st = onboarding_status(user, request=request, bypass_staff=True, allow_demo=False)
    target_slug = _normalize_intro_target_slug(next_product_slug)
    target_product = get_product_by_public_slug(target_slug) or get_product_by_key(SONHE_MAIS_ALTO_KEY)
    next_step_return_url = _portal_next_step_url(target_slug)

    sequence = [
        {
            "label": "Aceitar Termos e Consentimento",
            "description": "Regularize a base legal de uso para prosseguir com seguranca no fluxo.",
            "done": bool(st.get("has_legal")),
        },
        {
            "label": "Receber ou adquirir o Guia",
            "description": "A posse valida do Guia e o pre-requisito pedagogico de entrada na jornada.",
            "done": bool(st.get("has_valid_guia")),
        },
        {
            "label": "Responder a Avaliacao do Guia",
            "description": "Conclua a avaliacao da leitura antes de entrar efetivamente na trilha escolhida.",
            "done": bool(st.get("has_guia_feedback")),
        },
        {
            "label": f"Entrar em {target_product.public_name}",
            "description": "Com a etapa preparatoria concluida, a trilha escolhida fica pronta para uso normal.",
            "done": bool(st.get("has_onboarding")),
        },
    ]

    if not st.get("has_legal"):
        current_step = {
            "label": "Aceitar Termos e Consentimento",
            "description": "Antes de iniciar a jornada, confirme Termos e Privacidade para liberar a base legal do seu acesso.",
            "cta_label": "Aceitar Termos e Consentimento",
            "cta_url": f"{reverse('core:legal_aceite')}?{urlencode({'next': next_step_return_url})}",
        }
    elif not st.get("has_valid_guia"):
        current_step = {
            "label": "Receber ou adquirir o Guia",
            "description": "O próximo passo é adquirir o Guia de Descoberta. Para o usuário final, isso acontece pela compra oficial do Guia.",
            "cta_label": "Entender como obter o Guia",
            "cta_url": reverse("guia"),
        }
    elif not st.get("has_guia_feedback"):
        current_step = {
            "label": "Responder a Avaliacao do Guia",
            "description": "Voce ja tem o Guia. Agora falta responder a avaliacao da leitura antes de seguir para a trilha escolhida.",
            "cta_label": "Responder a Avaliacao do Guia",
            "cta_url": f"{reverse('vocacional:guia_avaliacao')}?{urlencode({'next': next_step_return_url})}",
        }
    else:
        current_step = {
            "label": f"Entrar em {target_product.public_name}",
            "description": "Sua etapa preparatoria foi concluida. Agora voce pode seguir para a trilha escolhida.",
            "cta_label": f"Ir para {target_product.public_name}",
            "cta_url": reverse("produto_resolver", args=[target_product.public_slug]),
        }

    return {
        "hide_global_header": True,
        "target_product": target_product,
        "next_step_sequence": sequence,
        "current_step": current_step,
        "is_ready_for_target": bool(st.get("has_onboarding")),
    }


def _normalize_institution_contact_role(raw_value: str) -> str | None:
    value = (raw_value or "").strip().lower()
    aliases = {
        "contato_adm": "contato_institucional",
        "contato_admin": "contato_institucional",
        "contato_administrativo": "contato_institucional",
        "contato_institucional": "contato_institucional",
        "administrativo": "contato_institucional",
        "institucional": "contato_institucional",
        "contato_financ": "contato_financeiro",
        "contato_financeiro": "contato_financeiro",
        "financeiro": "contato_financeiro",
        "contato_acad": "contato_academico",
        "contato_academico": "contato_academico",
        "academico": "contato_academico",
        "pedagogico": "contato_academico",
        "orientador": "orientador",
        "mentor": "mentor",
        "funcionario": "funcionario",
    }
    return aliases.get(value)


def _parse_governance_import_csv(uploaded_file, *, selected_institution=None, import_kind: str = "students") -> dict:
    if import_kind == "contacts":
        required_columns = {"nome", "sobrenome", "email", "papel"}
        optional_columns = {"principal", "instituicao", "observacao"}
    else:
        required_columns = {"nome", "sobrenome", "email"}
        optional_columns = {"ra", "serie", "turma", "mentor", "instituicao"}

    try:
        raw = uploaded_file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        raw = uploaded_file.read().decode("latin-1")

    reader = csv.DictReader(io.StringIO(raw))
    fieldnames = [name.strip().lower() for name in (reader.fieldnames or []) if name and name.strip()]
    missing_columns = sorted(required_columns - set(fieldnames))
    rows = []
    errors = []

    if missing_columns:
        return {
            "fieldnames": fieldnames,
            "missing_columns": missing_columns,
            "rows": [],
            "errors": [f"Colunas obrigatorias ausentes: {', '.join(missing_columns)}."],
        }

    User = get_user_model()
    for index, row in enumerate(reader, start=2):
        normalized = {str(k).strip().lower(): (str(v).strip() if v is not None else "") for k, v in row.items()}
        email = normalized.get("email", "").lower()
        nome = normalized.get("nome", "")
        sobrenome = normalized.get("sobrenome", "")
        if not email or not nome or not sobrenome:
            errors.append(f"Linha {index}: nome, sobrenome e email sao obrigatorios.")
            continue

        existing_user = User.objects.filter(email__iexact=email).first()
        institution_name = normalized.get("instituicao", "").strip()
        institution_label = selected_institution.nome if selected_institution else institution_name
        extra_metadata = {
            key: normalized.get(key, "").strip()
            for key in optional_columns
            if normalized.get(key, "").strip()
        }
        papel = ""
        principal = False
        if import_kind == "contacts":
            papel = _normalize_institution_contact_role(normalized.get("papel", ""))
            if not papel:
                errors.append(f"Linha {index}: papel institucional invalido.")
                continue
            principal = normalized.get("principal", "").strip().lower() in {"1", "sim", "s", "true", "x"}
        rows.append(
            {
                "line_number": index,
                "nome": nome,
                "sobrenome": sobrenome,
                "email": email,
                "papel": papel,
                "principal": principal,
                "institution_name": institution_label,
                "existing_user_id": existing_user.id if existing_user else None,
                "existing_user": bool(existing_user),
                "extra_metadata": extra_metadata,
            }
        )

    return {
        "fieldnames": fieldnames,
        "missing_columns": [],
        "rows": rows,
        "errors": errors,
        "import_kind": import_kind,
    }


def _serialize_institutional_metadata(extra_metadata: dict) -> str:
    keys = ["ra", "serie", "turma", "mentor", "instituicao"]
    lines = ["Importacao institucional em lote"]
    for key in keys:
        value = (extra_metadata or {}).get(key)
        if value:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _get_governance_import_preview(request) -> dict | None:
    return request.session.get(GOVERNANCE_IMPORT_SESSION_KEY)


def _get_intro_progress(user):
    if not getattr(user, "is_authenticated", False):
        return None
    try:
        from apps.core.models import IntroPresentationProgress
    except Exception:
        return None
    return IntroPresentationProgress.objects.filter(user=user).first()


def _has_completed_intro(user) -> bool:
    progress = _get_intro_progress(user)
    return bool(progress and progress.completed_at)


def _should_force_intro(request, user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if _should_redirect_to_governance(request, user):
        return False
    if get_active_demo_access(user):
        return not _has_completed_intro(user)
    return not _has_completed_intro(user)


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
    demo_access = get_active_demo_access(user)
    demo_override = bool(demo_access and not (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)))
    st = onboarding_status(user, request=request, bypass_staff=bypass_staff, allow_demo=True)
    require_bonus = getattr(settings, setting_flag, True)
    has_access_slug = user_has_produto(
        user,
        produto_slug,
        request=request,
        bypass_staff=bypass_staff,
        allow_demo=False,
    )
    has_valid_guia = onboarding_status(
        user,
        request=request,
        bypass_staff=bypass_staff,
        allow_demo=False,
    ).get("has_valid_guia", False)
    has_bonus_path = bool(has_valid_guia or has_access_slug)
    guia_feedback_blocking = bool(require_bonus and has_bonus_path and not st["has_guia_feedback"])

    can_access = False
    if demo_override:
        can_access = True
    elif st["has_legal"]:
        if (not require_bonus) or has_access_slug:
            if not guia_feedback_blocking:
                can_access = True if require_bonus else True

    return {
        "status": st,
        "demo_override": demo_override,
        "demo_access": demo_access,
        "require_bonus": require_bonus,
        "has_valid_guia": has_valid_guia,
        "has_access_slug": has_access_slug,
        "has_bonus_path": has_bonus_path,
        "guia_feedback_applicable": bool(require_bonus and has_bonus_path),
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
        "demo_override": facts["demo_override"],
        "guia_feedback_applicable": facts["guia_feedback_applicable"],
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
    ctx = _apply_portal_attention_flags_v2(ctx)
    ctx.update(_build_portal_stage_context(ctx))
    return ctx


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


def _build_portal_stage_context(ctx: dict) -> dict:
    has_legal = bool(ctx.get("has_legal"))
    has_valid_guia = bool(ctx.get("has_valid_guia"))
    has_guia_feedback = bool(ctx.get("has_guia_feedback"))
    has_onboarding = bool(ctx.get("has_onboarding"))
    can_vocacional = bool(ctx.get("can_vocacional"))
    can_sonhemaisalto = bool(ctx.get("can_sonhemaisalto"))
    need_bonus_sma = bool(ctx.get("need_bonus_sma"))
    need_bonus_voc = bool(ctx.get("need_bonus_voc"))

    if not has_legal:
        hero = {
            "eyebrow": "Etapa obrigatoria",
            "title": "Sua jornada continua pela base legal",
            "lead_primary": "A apresentacao inicial ja ficou para tras. Agora o portal mostra a etapa real que falta para regularizar seu acesso.",
            "lead_secondary": "Depois da base legal concluida, a plataforma segue mostrando apenas o proximo passo necessario.",
            "status_title": "Falta concluir Termos e Privacidade",
            "status_copy": "Sem essa etapa, o restante da jornada continua bloqueado.",
        }
    elif not has_valid_guia:
        hero = {
            "eyebrow": "Preparacao da jornada",
            "title": "Seu proximo passo e obter o Guia",
            "lead_primary": "O portal agora funciona como distribuidor de progresso. Neste momento, ele indica que o Guia de Descoberta e o pre-requisito pedagogico que falta.",
            "lead_secondary": "Depois disso, a proxima orientacao passa a ser a Avaliacao do Guia.",
            "status_title": "Aguardando posse valida do Guia",
            "status_copy": "Essa e a etapa que sustenta a entrada nas trilhas.",
        }
    elif not has_guia_feedback:
        hero = {
            "eyebrow": "Quase pronto",
            "title": "Falta concluir a Avaliacao do Guia",
            "lead_primary": "Voce ja tem o Guia. Agora o portal aponta a ultima etapa de preparacao antes da entrada efetiva nas trilhas.",
            "lead_secondary": "Concluida essa avaliacao, o fluxo volta a ser distribuido conforme os acessos disponiveis.",
            "status_title": "Aguardando avaliacao da leitura",
            "status_copy": "Essa etapa fecha a preparacao pedagogica da jornada.",
        }
    elif need_bonus_sma or need_bonus_voc:
        pendencias = []
        if need_bonus_sma:
            pendencias.append("Sonhe + Alto")
        if need_bonus_voc:
            pendencias.append("Vocacional")
        hero = {
            "eyebrow": "Acesso pendente",
            "title": "Sua preparacao foi concluida, mas ainda falta liberar a trilha",
            "lead_primary": "A etapa inicial ja esta pronta. Agora o portal orienta apenas a liberacao do pacote que ainda falta para sua jornada continuar.",
            "lead_secondary": f"Pendencia atual: {', '.join(pendencias)}.",
            "status_title": "Onboarding concluido",
            "status_copy": "O restante depende apenas da liberacao do pacote correspondente.",
        }
    elif has_onboarding and (can_vocacional or can_sonhemaisalto):
        trilhas = []
        if can_sonhemaisalto:
            trilhas.append("Sonhe + Alto")
        if can_vocacional:
            trilhas.append("Vocacional")
        hero = {
            "eyebrow": "Portal de continuidade",
            "title": "Seu portal agora distribui trilhas e progresso",
            "lead_primary": "A apresentacao e a preparacao inicial ja foram resolvidas. A partir daqui, o portal serve para orientar seu proximo movimento e levar voce rapido ao ambiente certo.",
            "lead_secondary": f"Trilhas prontas neste momento: {', '.join(trilhas)}.",
            "status_title": "Jornada liberada",
            "status_copy": "Voce pode seguir direto para a trilha indicada ou revisar o estado geral da sua jornada.",
        }
    else:
        hero = {
            "eyebrow": "Seu portal",
            "title": "Aqui voce acompanha sua etapa real",
            "lead_primary": "O portal deixou de ser uma recepcao generica. Agora ele mostra o que ja foi concluido e qual e o proximo passo coerente da sua jornada.",
            "lead_secondary": "Veja abaixo a leitura do seu momento e a prontidao das trilhas.",
            "status_title": "Leitura atual da jornada",
            "status_copy": "O objetivo e reduzir duvidas e tornar a navegacao mais objetiva.",
        }

    readiness = [
        {"title": "Base legal", "description": "Termos e Privacidade regularizados.", "done": has_legal},
        {"title": "Guia", "description": "Posse valida do Guia de Descoberta.", "done": has_valid_guia},
        {"title": "Avaliacao do Guia", "description": "Leitura concluida e qualificada.", "done": has_guia_feedback},
        {
            "title": "Trilhas",
            "description": "Portal pronto para levar voce ao ambiente certo.",
            "done": has_onboarding and (can_vocacional or can_sonhemaisalto),
        },
    ]

    return {"portal_hero": hero, "portal_readiness": readiness}


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

    if _should_force_intro(request, user):
        next_product_slug = (request.GET.get("next_product") or "").strip()
        return render(
            request,
            "core/portal_demo.html",
            _build_demo_intro_context(request, user, next_product_slug=next_product_slug),
        )

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


@login_required
def portal_demo(request):
    user = request.user
    if _should_redirect_to_governance(request, user):
        return redirect("portal_dashboard")

    if request.method == "POST":
        from apps.core.models import IntroPresentationProgress

        next_product_slug = (request.POST.get("next_product") or "").strip()
        next_product_slug = _normalize_intro_target_slug(next_product_slug)

        progress, _ = IntroPresentationProgress.objects.get_or_create(user=user)
        if not progress.completed_at:
            progress.mark_completed()

        if get_active_demo_access(user):
            return redirect(reverse("produto_resolver", args=[next_product_slug]) + "?demo_ready=1")
        return redirect(_portal_next_step_url(next_product_slug))

    if not _should_force_intro(request, user):
        return redirect("portal")

    next_product_slug = (request.GET.get("next_product") or "").strip()
    return render(
        request,
        "core/portal_demo.html",
        _build_demo_intro_context(request, user, next_product_slug=next_product_slug),
    )


@login_required
def portal_next_step(request):
    user = request.user
    if _should_redirect_to_governance(request, user):
        return redirect("portal_dashboard")

    if _should_force_intro(request, user):
        next_product_slug = (request.GET.get("next_product") or "").strip()
        return redirect(f"{reverse('portal_demo')}?{urlencode({'next_product': _normalize_intro_target_slug(next_product_slug)})}")

    next_product_slug = (request.GET.get("next_product") or "").strip()
    context = _build_next_step_context(request, user, next_product_slug=next_product_slug)
    if context["is_ready_for_target"]:
        return redirect(reverse("produto_resolver", args=[context["target_product"].public_slug]))
    return render(request, "core/portal_next_step.html", context)


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

    if _should_force_intro(request, user) and request.GET.get("demo_ready") != "1":
        demo_url = reverse("portal_demo")
        return redirect(f"{demo_url}?next_product={produto_slug}")

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
    from apps.core.models import GuiaPromotionalDelivery

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

    status = onboarding_status(target_user, request=request, bypass_staff=False, allow_demo=False)
    active_demo_access = get_active_demo_access(target_user)
    active_accesses = list(
        get_active_access_queryset(target_user)
        .select_related("produto")
        .order_by("produto__slug", "-granted_at")
    )
    active_access_slugs = {acesso.produto.slug for acesso in active_accesses}
    active_access_product_ids = {acesso.produto_id for acesso in active_accesses}
    available_products = list(Produto.objects.order_by("nome", "slug"))
    guia_products = [produto for produto in available_products if produto.slug in set(slugs_equivalentes(PROD_GUIA))]
    latest_guide_delivery = (
        GuiaPromotionalDelivery.objects.filter(user=target_user)
        .select_related("sent_by")
        .order_by("-sent_at", "-id")
        .first()
    )
    family_defs = [
        {
            "key": "basic",
            "label": "Basico",
            "slug_ref": PROD_VOCACIONAL_75,
            "description": "Bonus do Guia: Sonhe + Alto e Vocacional 75.",
        },
        {
            "key": "intermediate",
            "label": "Intermediario",
            "slug_ref": PROD_VOCACIONAL_150,
            "description": "Vocacional 150, equivalente ao antigo passe1.",
        },
        {
            "key": "premium",
            "label": "Premium",
            "slug_ref": PROD_VOCACIONAL_PREMIUM,
            "description": "Vocacional Premium, equivalente aos antigos passe2 e passe3.",
        },
    ]

    grouped_products = []
    access_packages = []
    assigned_product_ids = set()
    for family in family_defs:
        accepted_slugs = set(slugs_equivalentes(family["slug_ref"]))
        products = [produto for produto in available_products if produto.slug in accepted_slugs]
        assigned_product_ids.update(produto.id for produto in products)
        package_label = family["label"]
        package_description = family["description"]
        if family["key"] == "basic":
            package_label = "Bônus do Guia"
            package_description = "Uma única operação libera Sonhe + Alto e Vocacional 75."
        grouped_products.append(
            {
                **family,
                "products": products,
                "active": bool(
                    user_has_produto(
                        target_user,
                        family["slug_ref"],
                        request=request,
                        bypass_staff=False,
                        allow_demo=False,
                    )
                ),
            }
        )
        access_packages.append(
            {
                "key": family["key"],
                "label": package_label,
                "description": package_description,
                "products": products,
                "active": bool(
                    user_has_produto(
                        target_user,
                        family["slug_ref"],
                        request=request,
                        bypass_staff=False,
                        allow_demo=False,
                    )
                ),
            }
        )

    uncategorized_products = [produto for produto in available_products if produto.id not in assigned_product_ids]
    inconsistencies = []
    has_valid_guia = bool(status.get("has_valid_guia"))
    has_intermediate = bool(
        user_has_produto(
            target_user,
            PROD_VOCACIONAL_150,
            request=request,
            bypass_staff=False,
            allow_demo=False,
        )
    )
    has_premium = bool(
        user_has_produto(
            target_user,
            PROD_VOCACIONAL_PREMIUM,
            request=request,
            bypass_staff=False,
            allow_demo=False,
        )
    )

    if (has_intermediate or has_premium) and not has_valid_guia:
        levels = []
        if has_intermediate:
            levels.append("Intermediario")
        if has_premium:
            levels.append("Premium")
        inconsistencies.append(
            {
                "level": "critical",
                "title": "Inconsistencia de governanca",
                "message": (
                    f"Produto adicional concedido sem posse valida do Guia: {', '.join(levels)}. "
                    "O fluxo permanece bloqueado ate regularizar o pre-requisito."
                ),
            }
        )

    status["has_intro_completed"] = _has_completed_intro(target_user)

    return {
        "selected_user": target_user,
        "selected_user_status": status,
        "selected_user_product_states": product_states,
        "selected_user_active_accesses": active_accesses,
        "selected_user_active_access_slugs": active_access_slugs,
        "selected_user_active_access_product_ids": active_access_product_ids,
        "governance_guia_products": guia_products,
        "governance_guia_active": has_valid_guia,
        "governance_latest_guide_delivery": latest_guide_delivery,
        "governance_demo_access": active_demo_access,
        "governance_available_products": available_products,
        "governance_product_groups": grouped_products,
        "governance_access_packages": access_packages,
        "governance_uncategorized_products": uncategorized_products,
        "governance_inconsistencies": inconsistencies,
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
        from apps.core.models import (
            GuiaPromotionalDelivery,
            Instituicao,
            InstituicaoUsuario,
            InstitutionalDemoAccess,
        )

        user_id = (request.POST.get("user_id") or "").strip()
        produto_ids = [pid for pid in request.POST.getlist("produto_ids") if pid and pid.isdigit()]
        package_keys = [pkg for pkg in request.POST.getlist("package_keys") if pkg]
        action = (request.POST.get("action") or "").strip()
        q = (request.POST.get("q") or "").strip()
        demo_institution_name = (request.POST.get("demo_institution_name") or "").strip()
        demo_days_raw = (request.POST.get("demo_days") or "").strip()
        import_institution_id = (request.POST.get("import_institution_id") or "").strip()
        import_kind = (request.POST.get("import_kind") or "students").strip()
        if import_kind not in {"students", "contacts"}:
            import_kind = "students"

        redirect_url = reverse("portal_dashboard")
        query_data = {}
        if q:
            query_data["q"] = q
        if user_id:
            query_data["user_id"] = user_id
        if query_data:
            redirect_url = f"{redirect_url}?{urlencode(query_data)}"

        if action not in {"grant", "revoke", "send_guia", "revoke_guia", "grant_demo", "revoke_demo", "import_preview", "import_commit", "import_clear"}:
            messages.error(request, "Ação de governança inválida.")
            return redirect(redirect_url)

        if action == "import_clear":
            request.session.pop(GOVERNANCE_IMPORT_SESSION_KEY, None)
            request.session.modified = True
            messages.success(request, "Preview da importacao em lote limpo.")
            return redirect(redirect_url)

        if action == "import_preview":
            selected_institution = None
            if import_institution_id.isdigit():
                selected_institution = Instituicao.objects.filter(pk=int(import_institution_id)).first()

            uploaded_file = request.FILES.get("csv_file")
            if not uploaded_file:
                messages.error(request, "Selecione um arquivo CSV para importar.")
                return redirect(redirect_url)

            preview = _parse_governance_import_csv(
                uploaded_file,
                selected_institution=selected_institution,
                import_kind=import_kind,
            )
            preview["institution_id"] = selected_institution.id if selected_institution else None
            preview["institution_name"] = selected_institution.nome if selected_institution else ""
            preview["import_kind"] = import_kind
            request.session[GOVERNANCE_IMPORT_SESSION_KEY] = preview
            request.session.modified = True
            if preview["missing_columns"]:
                messages.error(request, "O CSV esta incompleto. Revise as colunas obrigatorias.")
            elif preview["errors"]:
                messages.warning(request, f"Preview gerado com pendencias. Linhas validas: {len(preview['rows'])}.")
            else:
                messages.success(request, f"Preview do lote gerado com {len(preview['rows'])} linhas validas.")
            return redirect(redirect_url)

        if action == "import_commit":
            preview = _get_governance_import_preview(request)
            if not preview or not preview.get("rows"):
                messages.error(request, "Nao existe preview valido para importar.")
                return redirect(redirect_url)

            institution = None
            if preview.get("institution_id"):
                institution = Instituicao.objects.filter(pk=int(preview["institution_id"])).first()
            if institution is None:
                messages.error(request, "Selecione uma instituicao valida antes de confirmar a importacao.")
                return redirect(redirect_url)

            User = get_user_model()
            created_count = 0
            assigned_count = 0
            conflict_emails = []
            import_kind = preview.get("import_kind") or "students"
            for item in preview["rows"]:
                user = User.objects.filter(email__iexact=item["email"]).first()
                if user is None:
                    defaults = {
                        "email": item["email"],
                        "first_name": item["nome"],
                        "last_name": item["sobrenome"],
                        "perfil": "ALUNO" if import_kind == "students" else "USER",
                        "is_active": False,
                    }
                    if import_kind == "students":
                        defaults["instituicao"] = institution
                    user = User.objects.create(**defaults)
                    user.set_unusable_password()
                    user.save(update_fields=["password"])
                    created_count += 1
                else:
                    changed_fields = []
                    if import_kind == "students":
                        if user.instituicao_id and user.instituicao_id != institution.id:
                            conflict_emails.append(user.email)
                            continue
                        if user.instituicao_id != institution.id:
                            user.instituicao = institution
                            changed_fields.append("instituicao")
                        if user.perfil == "USER":
                            user.perfil = "ALUNO"
                            changed_fields.append("perfil")
                    if not user.first_name and item["nome"]:
                        user.first_name = item["nome"]
                        changed_fields.append("first_name")
                    if not user.last_name and item["sobrenome"]:
                        user.last_name = item["sobrenome"]
                        changed_fields.append("last_name")
                    if changed_fields:
                        user.save(update_fields=changed_fields)

                if import_kind == "contacts":
                    observacoes = (item.get("extra_metadata") or {}).get("observacao", "")
                    vinculo, created = InstituicaoUsuario.objects.get_or_create(
                        instituicao=institution,
                        usuario=user,
                        papel=item["papel"],
                        defaults={
                            "principal": bool(item.get("principal")),
                            "ativo": True,
                            "observacoes": observacoes,
                        },
                    )
                    if not created:
                        update_fields = []
                        if bool(item.get("principal")) and not vinculo.principal:
                            vinculo.principal = True
                            update_fields.append("principal")
                        if observacoes and observacoes not in (vinculo.observacoes or ""):
                            vinculo.observacoes = "\n\n".join(filter(None, [vinculo.observacoes, observacoes]))
                            update_fields.append("observacoes")
                        if update_fields:
                            vinculo.save(update_fields=update_fields)
                assigned_count += 1

            request.session.pop(GOVERNANCE_IMPORT_SESSION_KEY, None)
            request.session.modified = True
            item_label = "aluno(s)" if import_kind == "students" else "contato(s) institucional(is)"
            messages.success(
                request,
                f"Importacao concluida para {institution.nome}: {created_count} usuario(s) criado(s) e {assigned_count} {item_label} processado(s).",
            )
            messages.info(
                request,
                "Usuarios novos foram criados como inativos, com senha inutilizavel, aguardando fluxo posterior de ativacao.",
            )
            if conflict_emails:
                messages.warning(
                    request,
                    "Alguns e-mails ja estavam vinculados a outra instituicao e nao foram alterados: "
                    + ", ".join(conflict_emails[:5])
                    + ("..." if len(conflict_emails) > 5 else ""),
                )
            return redirect(redirect_url)

        if not user_id.isdigit():
            messages.error(request, "Selecione um usuário válido.")
            return redirect(redirect_url)

        if action in {"grant", "revoke"} and not (produto_ids or package_keys):
            messages.error(request, "Selecione um usuário e pelo menos um produto válido.")
            return redirect(redirect_url)

        User = get_user_model()
        try:
            target_user = User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
            return redirect(reverse("portal_dashboard"))

        if action in {"grant_demo", "revoke_demo"}:
            now = timezone.now()
            active_demo_qs = InstitutionalDemoAccess.objects.filter(
                user=target_user,
                starts_at__lte=now,
                expires_at__gt=now,
                revoked_at__isnull=True,
            )

            if action == "grant_demo":
                try:
                    demo_days = int(demo_days_raw or "7")
                except ValueError:
                    demo_days = 7
                if demo_days not in {3, 7, 15, 30}:
                    demo_days = 7

                active_demo_qs.update(revoked_at=now)
                demo_access = InstitutionalDemoAccess.objects.create(
                    user=target_user,
                    institution_name=demo_institution_name,
                    granted_by=request.user,
                    source="governanca_demo",
                    starts_at=now,
                    expires_at=now + timedelta(days=demo_days),
                    notes="Acesso demo institucional concedido pela governanca.",
                )
                institution_fragment = f" para {demo_access.institution_name}" if demo_access.institution_name else ""
                messages.success(
                    request,
                    f"Demo institucional ativada{institution_fragment} para {target_user.email} ate {demo_access.expires_at:%d/%m/%Y %H:%M}.",
                )
                messages.info(
                    request,
                    "A demo libera navegacao de apresentacao sem marcar Posse do Guia, Avaliacao do Guia ou compra real.",
                )
                return redirect(redirect_url)

            updated = active_demo_qs.update(revoked_at=now)
            if updated:
                messages.success(
                    request,
                    f"Demo institucional encerrada para {target_user.email}.",
                )
            else:
                messages.info(
                    request,
                    f"{target_user.email} nao possui demo institucional ativa.",
                )
            return redirect(redirect_url)

        if action in {"send_guia", "revoke_guia"}:
            guia_products = list(
                Produto.objects.filter(slug__in=slugs_equivalentes(PROD_GUIA)).order_by("nome", "slug")
            )
            if not guia_products:
                messages.error(
                    request,
                    "Nenhum produto do Guia está cadastrado. Cadastre o produto correspondente antes de operar essa ação.",
                )
                return redirect(redirect_url)

            if action == "send_guia":
                success, payload = _send_promotional_guide_email(target_user=target_user, sent_by=request.user)
                if not success:
                    messages.error(request, payload)
                    return redirect(redirect_url)

                if not guia_products:
                    messages.error(
                        request,
                        "Nenhum produto do Guia foi encontrado para registrar a posse valida apos o envio.",
                    )
                    return redirect(redirect_url)

                created_names = []
                already_names = []
                for produto in guia_products:
                    active_qs = get_active_access_queryset(target_user).filter(produto=produto)
                    if active_qs.exists():
                        already_names.append(produto.nome)
                        continue
                    Acesso.objects.create(
                        user=target_user,
                        produto=produto,
                        origem="guia_envio_promocional",
                    )
                    created_names.append(produto.nome)

                GuiaPromotionalDelivery.objects.create(
                    user=target_user,
                    recipient_email=target_user.email,
                    sent_by=request.user,
                    source="governanca_promocional",
                    attachment_name=payload,
                    notes="Envio promocional do Guia disparado pela governanca.",
                )
                messages.success(
                    request,
                    f"Guia enviado por e-mail para {target_user.email}. Produtos ativados: {', '.join(created_names or already_names)}. A Avaliacao do Guia continua obrigatoria.",
                )
                if already_names:
                    messages.info(
                        request,
                        f"Produtos do Guia ja ativos para {target_user.email}: {', '.join(already_names)}.",
                    )
                return redirect(redirect_url)

            updated = get_active_access_queryset(target_user).filter(
                produto__slug__in=slugs_equivalentes(PROD_GUIA),
            ).update(expires_at=timezone.now())
            if updated:
                messages.success(
                    request,
                    f"Posse do Guia removida de {target_user.email}.",
                )
            else:
                messages.info(
                    request,
                    f"{target_user.email} não possui produto de Guia ativo para remoção.",
                )
            return redirect(redirect_url)

        package_slug_refs = {
            "basic": PROD_VOCACIONAL_75,
            "intermediate": PROD_VOCACIONAL_150,
            "premium": PROD_VOCACIONAL_PREMIUM,
        }
        package_slugs = set()
        for package_key in package_keys:
            slug_ref = package_slug_refs.get(package_key)
            if slug_ref:
                package_slugs.update(slugs_equivalentes(slug_ref))

        selected_ids = {int(pid) for pid in produto_ids}
        if package_slugs:
            selected_ids.update(
                Produto.objects.filter(slug__in=package_slugs).values_list("id", flat=True)
            )

        produtos = list(Produto.objects.filter(pk__in=selected_ids).order_by("nome", "slug"))
        if not produtos:
            messages.error(request, "Nenhum produto válido foi encontrado.")
            return redirect(redirect_url)

        if action == "grant":
            created_names = []
            already_names = []
            for produto in produtos:
                active_qs = get_active_access_queryset(target_user).filter(produto=produto)
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
            updated = get_active_access_queryset(target_user).filter(
                produto=produto,
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
        from apps.core.models import Instituicao

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
        ctx["governance_institutions"] = list(Instituicao.objects.filter(ativo=True).order_by("nome"))
        ctx["governance_import_preview"] = _get_governance_import_preview(self.request)
        ctx["governance_import_kind"] = (
            (ctx["governance_import_preview"] or {}).get("import_kind") or "students"
        )
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
