# apps/core/urls.py
from django.urls import path
from .views_webhooks import hotmart_webhook  # <- IMPORT RELATIVO (correto aqui)

urlpatterns = [
    path("hotmart/", hotmart_webhook, name="hotmart_webhook"),
]