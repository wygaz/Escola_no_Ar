from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AreaViewSet,
    EstrategiaViewSet,
    RegistroDiarioViewSet,
    MentorProfileViewSet,
    MentoriaViewSet,
    AnotacaoMentorViewSet,
)

router = DefaultRouter()
router.register(r"areas", AreaViewSet, basename="area")
router.register(r"estrategias", EstrategiaViewSet, basename="estrategia")
router.register(r"registros", RegistroDiarioViewSet, basename="registrodiario")
router.register(r"mentor-profile", MentorProfileViewSet, basename="mentorprofile")
router.register(r"mentorias", MentoriaViewSet, basename="mentoria")
router.register(r"anotacoes", AnotacaoMentorViewSet, basename="anotacaomentor")

urlpatterns = [
    path("", include(router.urls)),
]
