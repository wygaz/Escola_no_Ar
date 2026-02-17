# apps/vocacional/urls.py
from django.urls import path
from django.views.generic import TemplateView

from . import views
from . import views_consent
from . import views_guia

app_name = "vocacional"

urlpatterns = [
    # Home do módulo (dashboard/index)
    path("", views.index, name="index"),

    # Mantém compatibilidade: templates/portal costumam chamar "avaliacao_gate"
    # e outros chamam "avaliacao_form". Ambos levam para o mesmo formulário.
    path("avaliacao/", views.avaliacao_form, name="avaliacao_gate"),
    path("avaliacao/form/", views.avaliacao_form, name="avaliacao_form"),
    path("guia/avaliacao/", views_guia.guia_avaliacao, name="guia_avaliacao"),

    # Resultado
    path("resultado/<int:pk>/", views.resultado, name="resultado"),

    # Mentor (sem depender de função em views.py)
    path(
        "mentor/",
        TemplateView.as_view(template_name="vocacional/mentor_home.html"),
        name="mentor_dashboard",
    ),

    # Termos / Privacidade / Consentimento
    path("termos/", views_consent.termos, name="termos"),
    path("privacidade/", views_consent.privacidade, name="privacidade"),

    path("consentimento/", views_consent.consentimento_check, name="consentimento_check"),
    path("consentimento/aceitar/", views_consent.consentimento_aceitar, name="consentimento_aceitar"),
    path("consentimento/revogar/", views_consent.consentimento_revogar, name="consentimento_revogar"),
]
