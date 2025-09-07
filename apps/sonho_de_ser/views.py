from __future__ import annotations

from django.db import models, IntegrityError, transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import (
    Area,
    Estrategia,
    RegistroDiario,
    Mentoria,
    MentorProfile,
    AnotacaoMentor,
)
from .serializers import (
    AreaSerializer,
    EstrategiaSerializer,
    RegistroDiarioSerializer,
    MentoriaSerializer,
    AnotacaoMentorSerializer,
)
from .permissions import IsOwner  # já existente no seu app

User = get_user_model()


# ---------------------------
#   ÁREAS (somente leitura)
# ---------------------------
class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_map = Case(
            When(inicial="F", then=0),
            When(inicial="I", then=1),
            When(inicial="E", then=2),
            When(inicial="A", then=3),
            When(inicial="C", then=4),
            When(inicial="M", then=5),
            default=99,
            output_field=IntegerField(),
        )
        qs = Area.objects.all().order_by(order_map, "nome")

        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(models.Q(nome__icontains=q) | models.Q(inicial__iexact=q))
        return qs

# ---------------------------------
#   ESTRATÉGIAS (somente leitura)
# ---------------------------------
class EstrategiaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EstrategiaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = (
            Estrategia.objects.filter(ativo=True)
            .select_related("area")
            .order_by("area__inicial", "codigo")   # ou "titulo" se não houver "codigo"
        )

        # filtros aceitando nome ou inicial de área
        area = self.request.query_params.get("area")         # nome (ex.: "Família")
        area_inicial = self.request.query_params.get("inicial")  # ex.: "F"
        q = self.request.query_params.get("q")

        if area_inicial:
            qs = qs.filter(area__inicial__iexact=area_inicial)
        if area:
            qs = qs.filter(area__nome__iexact=area)

        if q:
            qs = qs.filter(
                models.Q(titulo__icontains=q)
                | models.Q(codigo__icontains=q)
                | models.Q(descricao__icontains=q)
            )
        return qs



# -------------------------------------------------------
#   REGISTRO DIÁRIO (lista do usuário + criação/atualiza)
# -------------------------------------------------------
class RegistroDiarioViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RegistroDiarioSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Apenas os registros do próprio usuário.
        Filtros: data, estrategia_codigo, concluido
        """
        user = self.request.user
        qs = (
            RegistroDiario.objects.filter(usuario=user)
            .select_related("estrategia", "estrategia__area")
            .order_by("-data", "estrategia__codigo")
        )

        data = self.request.query_params.get("data")  # YYYY-MM-DD
        estrategia_codigo = self.request.query_params.get("estrategia")
        concluido = self.request.query_params.get("concluido")

        if data:
            qs = qs.filter(data=data)
        if estrategia_codigo:
            qs = qs.filter(estrategia__codigo__iexact=estrategia_codigo)
        if concluido in {"true", "false", "1", "0"}:
            qs = qs.filter(concluido=concluido.lower() in {"true", "1"})
        return qs

    def perform_create(self, serializer):
        """
        Garante o usuário logado e respeita a unicidade (usuario, estrategia, data).
        Se data não vier, usa data local de hoje.
        """
        user = self.request.user
        data = serializer.validated_data.get("data") or timezone.localdate()
        serializer.save(usuario=user, data=data)

    @action(detail=True, methods=["post"])
    def concluir(self, request, pk=None):
        reg = self.get_object()
        reg.concluido = True
        reg.save(update_fields=["concluido", "atualizado_em"])
        return Response({"detail": "Registro concluído."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reabrir(self, request, pk=None):
        reg = self.get_object()
        reg.concluido = False
        reg.save(update_fields=["concluido", "atualizado_em"])
        return Response({"detail": "Registro reaberto."}, status=status.HTTP_200_OK)


# -------------------------------------------------------
#   MENTOR PROFILE (acesso do próprio mentor)
# -------------------------------------------------------
class MentorProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Staff vê todos; usuário comum vê apenas o próprio perfil (se existir).
    """
    queryset = MentorProfile.objects.select_related("usuario").all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(usuario=self.request.user)
        return qs

    @action(detail=False, methods=["get"])
    def me(self, request):
        try:
            mp = MentorProfile.objects.get(usuario=request.user)
        except MentorProfile.DoesNotExist:
            return Response({"detail": "MentorProfile inexistente."}, status=status.HTTP_404_NOT_FOUND)
        ser = self.get_serializer(mp)
        return Response(ser.data)


# ---------------------------------------------
#   MENTORIA (vínculo mentor → aluno)
# ---------------------------------------------
class MentoriaViewSet(viewsets.ModelViewSet):
    """
    O mentor (dono do MentorProfile) gerencia suas mentorias.
    Staff pode tudo; aluno enxerga apenas onde é aluno.
    """
    serializer_class = MentoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Mentoria.objects.select_related("mentor__usuario", "aluno").all()

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        # Staff tem visão completa
        if user.is_staff:
            return qs.order_by("-inicio")

        # Se for mentor, vê as que pertencem ao seu perfil
        try:
            mentor_profile = user.mentor_profile  # reverse OneToOne
        except MentorProfile.DoesNotExist:
            mentor_profile = None

        if mentor_profile:
            return qs.filter(
                models.Q(mentor=mentor_profile) | models.Q(aluno=user)
            ).order_by("-inicio")

        # Não-mentor: vê apenas onde é aluno
        return qs.filter(aluno=user).order_by("-inicio")

    def perform_create(self, serializer):
        """
        Ao criar: amarra automaticamente o mentor = request.user.mentor_profile
        """
        user = self.request.user
        try:
            mentor_profile = user.mentor_profile
        except MentorProfile.DoesNotExist:
            return Response(
                {"detail": "Usuário não possui MentorProfile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(mentor=mentor_profile)

    @action(detail=True, methods=["post"])
    def encerrar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "encerrada"
        mentoria.fim = timezone.localdate()
        mentoria.save(update_fields=["status", "fim", "atualizado_em"])
        return Response({"detail": "Mentoria encerrada."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def pausar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "pausada"
        mentoria.save(update_fields=["status", "atualizado_em"])
        return Response({"detail": "Mentoria pausada."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reativar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "ativa"
        mentoria.fim = None
        mentoria.save(update_fields=["status", "fim", "atualizado_em"])
        return Response({"detail": "Mentoria reativada."}, status=status.HTTP_200_OK)


# -------------------------------------------------------
#   ANOTAÇÕES DO MENTOR (autor = mentor logado)
# -------------------------------------------------------
class AnotacaoMentorViewSet(viewsets.ModelViewSet):
    serializer_class = AnotacaoMentorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Staff vê todas. Mentor vê apenas as próprias (autor = seu MentorProfile).
        Aluno vê apenas as 'compartilhadas' nas mentorias em que é aluno.
        Filtro opcional: ?mentoria=<id>
        """
        user = self.request.user
        qs = (
            AnotacaoMentor.objects.select_related(
                "mentoria", "mentoria__mentor__usuario", "autor__usuario"
            )
            .all()
            .order_by("-data")
        )

        mentoria_id = self.request.query_params.get("mentoria")
        if mentoria_id:
            qs = qs.filter(mentoria_id=mentoria_id)

        if user.is_staff:
            return qs

        # se mentor
        try:
            mentor_profile = user.mentor_profile
        except MentorProfile.DoesNotExist:
            mentor_profile = None

        if mentor_profile:
            return qs.filter(autor=mentor_profile)

        # se aluno
        return qs.filter(mentoria__aluno=user, visibilidade="compartilhada")

    def perform_create(self, serializer):
        """
        Autor = mentor logado; valida existência de MentorProfile.
        """
        user = self.request.user
        try:
            mentor_profile = user.mentor_profile
        except MentorProfile.DoesNotExist:
            return Response(
                {"detail": "Somente mentores podem criar anotações."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.save(autor=mentor_profile)
