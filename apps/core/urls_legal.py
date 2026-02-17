from django.urls import path

from . import views_legal


app_name = "core"


urlpatterns = [
    path("termos/", views_legal.termos, name="termos"),
    path("privacidade/", views_legal.privacidade, name="privacidade"),
    path("aceite/", views_legal.legal_aceite, name="legal_aceite"),
    # alias (compat)
    path("consentimento/", views_legal.legal_aceite, name="consentimento"),
]
