from __future__ import annotations

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, IntegerField, Q, When
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import PlanoForm, RegistroForm
from .models import (
    AnotacaoMentor,
    Area,
    Estrategia,
    MentorProfile,
    Mentoria,
    Plano,
    PlanoItem,
    RegistroDiario,
)
from .permissions import IsOwner
from .serializers import (
    AnotacaoMentorSerializer,
    AreaSerializer,
    EstrategiaSerializer,
    MentorProfileSerializer,
    MentoriaSerializer,
    RegistroDiarioSerializer,
)
from .services import progresso_da_semana, resumo_dashboard


class Projeto21DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "sonho_de_ser/projeto21_dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        plano = Plano.objects.filter(usuario=self.request.user, ativo=True).first()
        ctx.update(resumo_dashboard(plano))
        return ctx


class Projeto21MentorView(LoginRequiredMixin, TemplateView):
    template_name = "sonho_de_ser/projeto21_mentor.html"


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
            qs = qs.filter(Q(nome__icontains=q) | Q(inicial__iexact=q))
        return qs


class EstrategiaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EstrategiaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = (
            Estrategia.objects.filter(ativo=True)
            .select_related("area")
            .order_by("area__inicial", "nivel", "ordem_nivel", "titulo")
        )

        area = self.request.query_params.get("area")
        area_inicial = self.request.query_params.get("inicial")
        q = self.request.query_params.get("q")

        if area_inicial:
            qs = qs.filter(area__inicial__iexact=area_inicial)
        if area:
            qs = qs.filter(area__nome__iexact=area)
        if q:
            qs = qs.filter(
                Q(titulo__icontains=q)
                | Q(codigo__icontains=q)
                | Q(descricao__icontains=q)
            )
        return qs


class RegistroDiarioViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RegistroDiarioSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        qs = (
            RegistroDiario.objects.filter(usuario=self.request.user)
            .select_related("estrategia", "estrategia__area")
            .order_by("-data", "estrategia__area__inicial", "estrategia__ordem_nivel")
        )
        data_param = self.request.query_params.get("data")
        estrategia_codigo = self.request.query_params.get("estrategia")
        if data_param:
            qs = qs.filter(data=data_param)
        if estrategia_codigo:
            qs = qs.filter(estrategia__codigo__iexact=estrategia_codigo)
        return qs

    def perform_create(self, serializer):
        data_val = serializer.validated_data.get("data") or date.today()
        serializer.save(usuario=self.request.user, data=data_val)

    @action(detail=False, methods=["get"])
    def hoje(self, request):
        hoje = date.today()
        serializer = self.get_serializer(
            self.get_queryset().filter(data=hoje),
            many=True,
        )
        return Response(serializer.data)


class MentorProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MentorProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = MentorProfile.objects.select_related("usuario").all()

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(usuario=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        try:
            profile = MentorProfile.objects.get(usuario=request.user)
        except MentorProfile.DoesNotExist:
            return Response({"detail": "MentorProfile inexistente."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class MentoriaViewSet(viewsets.ModelViewSet):
    serializer_class = MentoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Mentoria.objects.select_related("mentor", "mentorado").all()

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param.upper())

        if user.is_staff:
            return qs.order_by("-criado_em")

        return qs.filter(Q(mentor=user) | Q(mentorado=user)).order_by("-criado_em")

    def perform_create(self, serializer):
        serializer.save(mentor=self.request.user)

    @action(detail=True, methods=["post"])
    def encerrar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "ENCERRADA"
        mentoria.ativo = False
        mentoria.save(update_fields=["status", "ativo"])
        return Response({"detail": "Mentoria encerrada."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def pausar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "PAUSADA"
        mentoria.save(update_fields=["status"])
        return Response({"detail": "Mentoria pausada."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reativar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "ATIVA"
        mentoria.ativo = True
        mentoria.save(update_fields=["status", "ativo"])
        return Response({"detail": "Mentoria reativada."}, status=status.HTTP_200_OK)


class AnotacaoMentorViewSet(viewsets.ModelViewSet):
    serializer_class = AnotacaoMentorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = AnotacaoMentor.objects.select_related("mentoria", "mentoria__mentor", "mentoria__mentorado").order_by("-data", "-created_at")
        mentoria_id = self.request.query_params.get("mentoria")
        if mentoria_id:
            qs = qs.filter(mentoria_id=mentoria_id)

        if user.is_staff:
            return qs

        return qs.filter(
            Q(mentoria__mentor=user)
            | Q(mentoria__mentorado=user, visivel_para_aluno=True)
        )


@login_required
def plano_view(request):
    Plano.objects.filter(usuario=request.user, ativo=True).first() or Plano.objects.create(
        usuario=request.user,
        ativo=True,
    )

    if request.method == "POST":
        form = PlanoForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Plano atualizado.")
            return redirect("/projeto21/")
    else:
        form = PlanoForm(usuario=request.user)

    estrategias = list(
        Estrategia.objects.filter(ativo=True)
        .select_related("area")
        .order_by(
            "ordem_area",
            "area__inicial",
            "ordem_dimensao",
            "nivel",
            "objetivo_codigo",
            "ordem_nivel",
            "titulo",
        )
    )
    catalogo = [
        {
            "id": estrategia.id,
            "area_inicial": estrategia.area.inicial,
            "area_nome": estrategia.area.nome,
            "nivel": estrategia.get_nivel_display(),
            "objetivo_codigo": estrategia.objetivo_codigo,
            "objetivo_descricao": estrategia.objetivo_descricao,
            "titulo": estrategia.titulo,
            "codigo": estrategia.codigo,
            "dosagem": estrategia.dosagem_texto,
            "frequencia": estrategia.frequencia_texto,
            "periodo": estrategia.periodo_texto,
            "pontos": estrategia.pontos,
        }
        for estrategia in estrategias
    ]

    return render(
        request,
        "sonho_de_ser/projeto21_plano.html",
        {
            "form": form,
            "sel": set(form.initial.get("estrategias", [])),
            "catalogo": catalogo,
        },
    )


@login_required
def registro_view(request):
    plano = Plano.objects.filter(usuario=request.user, ativo=True).first()
    if not plano:
        messages.info(request, "Crie seu plano antes de registrar o dia.")
        return redirect("/projeto21/plano/")

    hoje = date.today()

    limpar_form = request.GET.get("salvo") == "1"

    if request.method == "POST":
        form = RegistroForm(plano, request.POST, data_registro=hoje)
        if form.is_valid():
            jornada = form.save(hoje)
            messages.success(request, f"Check-in de {jornada.data:%d/%m} salvo.")
            return redirect("/projeto21/registro/?salvo=1")
    else:
        form = RegistroForm(plano, data_registro=hoje, carregar_existentes=not limpar_form)

    grupos: dict[Area, list[dict]] = {}
    plano_resumo: dict[Area, list[dict]] = {}
    for item in (
        PlanoItem.objects.filter(plano=plano, ativo=True)
        .select_related("estrategia", "estrategia__area")
        .order_by(
            "estrategia__area__inicial",
            "estrategia__nivel",
            "estrategia__objetivo_codigo",
            "estrategia__ordem_nivel",
        )
    ):
        grupos.setdefault(item.estrategia.area, []).append(
            {
                "item": item,
                "status_field": form[f"status_{item.id}"],
                "obs_field": form[f"obs_{item.id}"],
            }
        )
        area_objetivos = plano_resumo.setdefault(item.estrategia.area, [])
        objetivo = next(
            (
                row
                for row in area_objetivos
                if row["codigo"] == item.estrategia.objetivo_codigo
            ),
            None,
        )
        if objetivo is None:
            objetivo = {
                "codigo": item.estrategia.objetivo_codigo,
                "descricao": item.estrategia.objetivo_descricao or "Objetivo sem descricao",
                "itens": [],
            }
            area_objetivos.append(objetivo)
        objetivo["itens"].append(item)

    registros_hoje = set(
        RegistroDiario.objects.filter(usuario=request.user, data=hoje).values_list(
            "estrategia_id", flat=True
        )
    )

    return render(
        request,
        "sonho_de_ser/projeto21_registro.html",
        {
            "form": form,
            "grupos": grupos,
            "plano": plano,
            "plano_resumo": plano_resumo,
            "hoje": hoje,
            "checkin_salvo": request.GET.get("salvo") == "1",
            "registros_hoje": registros_hoje,
        },
    )


@login_required
def historico_view(request):
    plano = Plano.objects.filter(usuario=request.user, ativo=True).first()
    if not plano:
        messages.info(request, "Voce ainda nao tem um plano ativo.")
        return redirect("/projeto21/plano/")

    registros = (
        RegistroDiario.objects.filter(usuario=request.user)
        .select_related("jornada", "estrategia", "estrategia__area")
        .order_by("-data", "estrategia__area__inicial", "estrategia__ordem_nivel")[:30]
    )
    return render(
        request,
        "sonho_de_ser/projeto21_historico.html",
        {"registros": registros},
    )


@login_required
def pontuacao_view(request):
    plano = Plano.objects.filter(usuario=request.user, ativo=True).first()
    if not plano:
        messages.info(request, "Voce ainda nao tem um plano ativo.")
        return redirect("/projeto21/plano/")

    info = progresso_da_semana(plano)
    return render(
        request,
        "sonho_de_ser/projeto21_pontuacao.html",
        {"info": info, "plano": plano},
    )
