from django.urls import path
from . import views, views_consent, views_guia, views_bonus, views_debug

app_name = "vocacional"

urlpatterns = [
    path("", views.index, name="index"),
    path("avaliacao/", views.avaliacao_gate, name="avaliacao_gate"),
    path("avaliacao/form/", views.avaliacao_form, name="avaliacao_form"),
    path("resultado/<int:pk>/", views.resultado, name="resultado"),
    path("resultado/<int:pk>/enviar-email/", views.enviar_resultado_email, name="enviar_resultado_email"),    

    # consentimento
    path("consentimento/", views_consent.consentimento_check, name="consentimento_check"),
    path("consentimento/aceitar/", views_consent.consentimento_aceitar, name="consentimento_aceitar"),
    path("consentimento/revogar/", views_consent.consentimento_revogar, name="consentimento_revogar"),    
    path("privacidade/", views_consent.privacidade, name="privacidade"),

    # guia (pré-requisito)
    path("guia/avaliacao/", views_guia.guia_avaliacao, name="guia_avaliacao"),

    # bônus (se usado)
    path("bonus/", views_bonus.bonus, name="bonus"),
    path("bonus/validar/", views_bonus.bonus_validar, name="bonus_validar"),

    # debug
    path("debug/", views_debug.debug, name="debug"),
]