# apps/core/views_webhooks.py
import hmac
import hashlib
import json

from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.contas.models_acessos import Produto, Acesso  # mantém histórico (arquivo no plural)
from .models import PendingAccess


def _get_header(request, name: str) -> str:
    """
    Django >= 2.2 tem request.headers (case-insensitive).
    Mantemos fallback pro META por segurança.
    """
    val = request.headers.get(name)
    if val:
        return val
    meta_key = "HTTP_" + name.upper().replace("-", "_")
    return request.META.get(meta_key, "")


def _mapear_produtos_para_venda(data: dict):
    """
    Decide quais produtos (slugs) devem ser liberados
    com base nos dados enviados pela Hotmart.

    - Produto real: por nome (contendo "quem sou eu" / "como descobrir minha vocação")
    - Produto de teste Hotmart (postback2): libera o mesmo, só pra validar pipeline
    """
    product = (data.get("product") or {})
    product_name = (product.get("name") or "").lower()

    produtos = []

    # Produto principal: "Quem sou eu? Como descobrir minha vocação?"
    if "quem sou eu" in product_name or "como descobrir minha vocação" in product_name:
        produtos.append(("projeto21_sonhe_alto", "Projeto 21 – Sonhe + Alto"))
        produtos.append(("vocacional_bonus", "Bônus – Teste Vocacional (atual)"))
        return produtos

    # Produto de teste (Hotmart postback2)
    if "postback2" in product_name or "produto test" in product_name:
        produtos.append(("projeto21_sonhe_alto", "Projeto 21 – Sonhe + Alto"))
        produtos.append(("vocacional_bonus", "Bônus – Teste Vocacional (atual)"))
        return produtos

    return []


@csrf_exempt
def hotmart_webhook(request):
    if request.method != "POST":
        return HttpResponseForbidden("Method not allowed")

    body = request.body or b""

    # -------------------------------------------------------------------------
    # 1) Autenticação do Webhook
    #   - Webhook 2.0: header X-HOTMART-HOTTOK (recomendado)
    #   - Fallback legado: X-Hotmart-Hmac-SHA256 (se um dia usar 1.0)
    # -------------------------------------------------------------------------
    secret = (getattr(settings, "HOTMART_WEBHOOK_SECRET", "") or "").strip()
    hottok = (_get_header(request, "X-HOTMART-HOTTOK") or "").strip()

    if secret:
        # Se tiver secret, exigimos hottok quando for 2.0 (o normal)
        if hottok:
            if not hmac.compare_digest(hottok, secret):
                return HttpResponseForbidden("Invalid hottok")
        else:
            # fallback legado por HMAC (opcional)
            signature = (_get_header(request, "X-Hotmart-Hmac-SHA256") or "").strip()
            if signature:
                calc = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
                if not hmac.compare_digest(calc, signature):
                    return HttpResponseForbidden("Invalid signature")
            else:
                # Em produção, melhor não aceitar webhook sem autenticação
                if not settings.DEBUG:
                    return HttpResponseForbidden("Missing authentication header")

    # -------------------------------------------------------------------------
    # 2) Parse JSON (Hotmart 2.0 vem com payload["data"])
    # -------------------------------------------------------------------------
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "detail": "invalid json"}, status=400)

    event = (payload.get("event") or "").strip()  # ex.: PURCHASE_APPROVED
    data = (payload.get("data") or {})            # Hotmart 2.0

    buyer = (data.get("buyer") or {})
    purchase = (data.get("purchase") or {})

    email = (buyer.get("email") or "").strip().lower()
    status = (purchase.get("status") or "").strip().lower()  # "APPROVED" -> "approved"

    if not email:
        return JsonResponse({"ok": False, "detail": "missing_email", "event": event}, status=200)

    # Se for evento de compra aprovada, status deve vir approved
    # (mantemos os antigos também, por segurança)
    allowed_status = {"approved", "completed", "paid"}
    if status not in allowed_status:
        return JsonResponse(
            {"ok": False, "detail": "ignored", "event": event, "status": status},
            status=200,
        )

    # -------------------------------------------------------------------------
    # 3) Mapeamento de produto -> slugs internos
    # -------------------------------------------------------------------------
    produtos = _mapear_produtos_para_venda(data)
    if not produtos:
        product = (data.get("product") or {})
        return JsonResponse(
            {
                "ok": False,
                "detail": "produto_nao_mapeado",
                "event": event,
                "status": status,
                "product_name": product.get("name"),
                "product_id": product.get("id"),
            },
            status=200,  # 200 pra Hotmart não ficar re-tentando eternamente
        )

    # -------------------------------------------------------------------------
    # 4) Concessão (Acesso) ou fila (PendingAccess)
    # -------------------------------------------------------------------------
    Usuario = get_user_model()

    try:
        user = Usuario.objects.get(email__iexact=email)
    except Usuario.DoesNotExist:
        # Usuário ainda não tem conta: cria PendingAccess para CADA produto
        for slug, _nome in produtos:
            PendingAccess.objects.get_or_create(
                email=email,
                produto_slug=slug,
                defaults={"origem": "hotmart"},
            )
        return JsonResponse(
            {"ok": True, "queued": True, "email": email, "produtos": [slug for slug, _ in produtos]},
            status=202,
        )

    # Usuário já existe -> concede acesso direto a TODOS os produtos mapeados
    granted = []
    for slug, nome in produtos:
        produto, _ = Produto.objects.get_or_create(slug=slug, defaults={"nome": nome})
        Acesso.objects.get_or_create(user=user, produto=produto, defaults={"origem": "hotmart"})
        granted.append(slug)

    return JsonResponse({"ok": True, "granted": granted, "email": email, "event": event}, status=200)
