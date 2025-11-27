from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # WEB (P21)
    Projeto21DashboardView,   # CBV do dashboard
    Projeto21MentorView,      # opcional (mentor)
    plano_view,               # FBV (operacional)
    registro_view,            # FBV (operacional)
    historico_view,           # FBV (operacional)
    pontuacao_view,           # FBV (operacional)

    # API (DRF)
    AreaViewSet,
    EstrategiaViewSet,
    RegistroDiarioViewSet,
    MentorProfileViewSet,
    MentoriaViewSet,
    AnotacaoMentorViewSet,
)

app_name = "sonho_de_ser"

# -------- API (mantém o que você já tinha) --------
router = DefaultRouter()
router.register(r"areas", AreaViewSet, basename="area")
router.register(r"estrategias", EstrategiaViewSet, basename="estrategia")
router.register(r"registros", RegistroDiarioViewSet, basename="registrodiario")
router.register(r"mentor-profile", MentorProfileViewSet, basename="mentorprofile")
router.register(r"mentorias", MentoriaViewSet, basename="mentoria")
router.register(r"anotacoes", AnotacaoMentorViewSet, basename="anotacaomentor")

# -------- WEB (P21) --------
urlpatterns = [
    # Páginas do aluno (P21)
    path("", Projeto21DashboardView.as_view(), name="dashboard"),
    path("plano/", plano_view, name="plano"),
    path("registro/", registro_view, name="registro"),
    path("historico/", historico_view, name="historico"),
    path("pontuacao/", pontuacao_view, name="pontuacao"),

    # Painel do mentor (stub/CBV)
    path("mentor/", Projeto21MentorView.as_view(), name="mentor_dashboard"),

    # Namespace da API sob /projeto21/api/
    path("api/", include((router.urls, "sonho_de_ser"), namespace="api")),
]
