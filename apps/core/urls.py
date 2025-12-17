# apps/core/urls.py
from django.urls import path
from . import views
from .views_webhooks import hotmart_webhook  # <- IMPORT RELATIVO (correto aqui)

urlpatterns = [
    path("hotmart/", hotmart_webhook, name="hotmart_webhook"),
    path("sobre/", views.sobre, name="sobre"),
    path("contato/", views.contato, name="contato"),
    path("sonhe-mais-alto/", views.sonhe_mais_alto_landing, name="sonhe_mais_alto"),
]