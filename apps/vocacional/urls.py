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
    path("entrada/", views.entrada, name="entrada"),
    path("etapas/", views.etapas, name="etapas"),

    # Bônus (75) e Refinamento (Passes) usam a mesma view base (avaliacao_form)
    path("bonus/", views.avaliacao_form, name="bonus_form"),
    path("refinamento/", views.avaliacao_form, name="refinamento_form"),

    # Mantém compatibilidade: templates/portal costumam chamar "avaliacao_gate"
    # e outros chamam "avaliacao_form". Ambos levam para o mesmo formulário.
    path("avaliacao/", views.avaliacao_form, name="avaliacao_gate"),
    path("avaliacao/form/", views.avaliacao_form, name="avaliacao_form"),
    path("passe3/", views.passe3, name="passe3"),
    path("comparacoes/<int:pk>/", views.comparacoes_top3, name="comparacoes_top3"),
    path("guia/avaliacao/", views_guia.guia_avaliacao, name="guia_avaliacao"),
    path("guia/autosave/", views_guia.guia_autosave, name="guia_autosave"),


    path("ofertas/<int:pk>/", views.ofertas_refinamento, name="ofertas_refinamento"),
    # Resultado
    path("resultado/<int:pk>/", views.resultado, name="resultado"),
    path("reiniciar/", views.reiniciar_teste, name="reiniciar_teste"),

    # Compartilhamento do resultado
    path("resultado/<int:pk>/email/", views.enviar_resultado_email, name="enviar_resultado_email"),
    path("resultado/<int:pk>/whatsapp/", views.resultado_whatsapp, name="resultado_whatsapp"),

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
