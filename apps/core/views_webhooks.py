# apps/core/views_webhooks.py
import hmac, hashlib, json
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.contas.models_acessos import Produto, Acesso  # mantém histórico (arquivo no plural)
from .models import PendingAccess
# from .hotmart_integration import processar_venda_hotmart  # (podemos deixar para uso futuro)


def _mapear_produtos_para_venda(payload):
    """
    Decide quais produtos (slugs) devem ser liberados
    com base nos dados enviados pela Hotmart.

    Por enquanto: se o nome do produto contiver
    'quem sou eu' ou 'como descobrir minha vocação',
    vamos liberar:
      - Projeto 21 / Sonhe + Alto
      - Vocacional (bônus atual) -> slug: vocacional_bonus
    """

    product = (payload.get("product", {}) or {})
    product_name = (product.get("name") or "").lower()

    produtos = []

    # Produto principal: "Quem sou eu? Como descobrir minha vocação?"
    if "quem sou eu" in product_name or "como descobrir minha vocação" in product_name:
        produtos.append(("projeto21_sonhe_alto", "Projeto 21 – Sonhe + Alto"))
        produtos.append(("vocacional_bonus", "Bônus – Teste Vocacional (atual)"))

    return produtos


@csrf_exempt
def hotmart_webhook(request):
    if request.method != "POST":
        return HttpResponseForbidden("Method not allowed")

    # 1) Validação da assinatura/HMAC
    secret = getattr(settings, "HOTMART_WEBHOOK_SECRET", None)
    signature = request.headers.get("X-Hotmart-Hmac-SHA256", "")
    body = request.body

    if secret:
        calc = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, signature):
            return HttpResponseForbidden("Invalid signature")

    # 2) Parse do JSON
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "detail": "invalid json"}, status=400)

    buyer = (payload.get("buyer", {}) or {})
    purchase = (payload.get("purchase", {}) or {})

    email = (buyer.get("email") or "").strip().lower()
    status = (purchase.get("status") or "").lower()  # ex.: "approved"

    if not email or status not in {"approved", "completed", "paid"}:
        return JsonResponse({"ok": False, "detail": "ignored"})

    # 3) Ver quais produtos essa venda deve liberar
    produtos = _mapear_produtos_para_venda(payload)
    if not produtos:
        # Produto não mapeado ainda – registra mas não quebra
        return JsonResponse({"ok": False, "detail": "produto_nao_mapeado"}, status=200)

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
        # 202: aceito/registrado; será conciliado no login/registro
        return JsonResponse(
            {"ok": True, "queued": True, "produtos": [slug for slug, _ in produtos]},
            status=202,
        )

    # Usuário já existe -> concede acesso direto a TODOS os produtos mapeados
    granted = []
    for slug, nome in produtos:
        produto, _ = Produto.objects.get_or_create(
            slug=slug,
            defaults={"nome": nome},
        )
        Acesso.objects.get_or_create(
            user=user,
            produto=produto,
            defaults={"origem": "hotmart"},
        )
        granted.append(slug)

    return JsonResponse({"ok": True, "granted": granted})
