# apps/sonho_de_ser/urls_projeto21.py
from django.urls import path
from .views import (
    Projeto21DashboardView, Projeto21MentorView,
    Projeto21PlanoView, Projeto21RegistroHojeView,
    Projeto21HistoricoView, Projeto21PontuacaoView,
)
app_name = "projeto21"  # opcional, para namespacing de URLs

urlpatterns = [
    path("", Projeto21DashboardView.as_view(), name="dashboard"),
    path("mentor/", Projeto21MentorView.as_view(), name="mentor"),
    path("plano/", Projeto21PlanoView.as_view(), name="plano"),
    path("registro/", Projeto21RegistroHojeView.as_view(), name="registro"),
    path("historico/", Projeto21HistoricoView.as_view(), name="historico"),
    path("pontuacao/", Projeto21PontuacaoView.as_view(), name="pontuacao"),
]
