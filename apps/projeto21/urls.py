# apps/projeto21/urls.py
from django.urls import path

from . import views
from apps.sonho_de_ser import views as sonho_views

app_name = "projeto21"

urlpatterns = [
    path("", views.projeto21_home, name="home"),
    path("plano/", sonho_views.plano_view, name="plano"),
    path("registro/", sonho_views.registro_view, name="registro"),
    path("historico/", sonho_views.historico_view, name="historico"),
    path("pontuacao/", sonho_views.pontuacao_view, name="pontuacao"),
    path("mentor/", sonho_views.Projeto21MentorView.as_view(), name="mentor_dashboard"),
]
