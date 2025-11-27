# apps/core/views_webhooks.py
import hmac, hashlib, json
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.contas.models_acessos import Produto, Acesso  # mantém histórico (arquivo no plural)
from .models import PendingAccess

@csrf_exempt
def hotmart_webhook(request):
    if request.method != "POST":
        return HttpResponseForbidden("Method not allowed")

    secret = getattr(settings, "HOTMART_WEBHOOK_SECRET", None)
    signature = request.headers.get("X-Hotmart-Hmac-SHA256", "")
    body = request.body

    if secret:
        calc = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, signature):
            return HttpResponseForbidden("Invalid signature")

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "detail": "invalid json"}, status=400)

    email = (payload.get("buyer", {}) or {}).get("email")
    status = (payload.get("purchase", {}) or {}).get("status")  # ex.: "approved"

    if not email or status not in {"approved", "completed"}:
        return JsonResponse({"ok": False, "detail": "ignored"})

    Usuario = get_user_model()
    try:
        user = Usuario.objects.get(email__iexact=email)
    except Usuario.DoesNotExist:
        # Usuário ainda não tem conta -> cria fila de acesso
        PendingAccess.objects.get_or_create(
            email=email,
            produto_slug="vocacional_bonus",
            defaults={"origem": "hotmart"},
        )
        # 202: aceito/registrado; será conciliado no login
        return JsonResponse({"ok": True, "queued": True}, status=202)

    # Usuário já existe -> concede direto
    produto, _ = Produto.objects.get_or_create(slug="vocacional_bonus", defaults={"nome": "Bônus do Guia"})
    Acesso.objects.get_or_create(user=user, produto=produto, defaults={"origem": "hotmart"})
    return JsonResponse({"ok": True, "granted": True})
