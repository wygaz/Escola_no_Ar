from __future__ import annotations

from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Q, Case, When, IntegerField
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsOwner
from .forms import PlanoForm, RegistroForm
from .serializers import (
    AreaSerializer,
    EstrategiaSerializer,
    RegistroDiarioSerializer,
    MentoriaSerializer,
    AnotacaoMentorSerializer,
)
from .models import (
    Area,
    Estrategia,
    RegistroDiario,
    Mentoria,
    MentorProfile,
    AnotacaoMentor,
    Plano,  # existe no seu models (patch P21)
    # Objetivo,            # importado dentro das views quando necessário
    # PlanoEstrategia,     # importado dentro das views quando necessário
)

User = get_user_model()


# ----------------------------------------------------------------------------
# Helpers defensivos (usados no dashboard e em pontuação)
# ----------------------------------------------------------------------------

def _has_field(Model, name: str) -> bool:
    try:
        Model._meta.get_field(name)
        return True
    except Exception:
        return False


def _data_field(Model) -> str:
    for f in ("data", "created_at", "criado_em"):
        if _has_field(Model, f):
            return f
    return "id"


def _q_concluido(Model) -> Q:
    if _has_field(Model, "feito"):
        return Q(feito=True)
    if _has_field(Model, "concluido"):
        return Q(concluido=True)
    if _has_field(Model, "status"):
        return Q(status__in=["CONCLUIDO", "FEITO", "OK", "DONE"])
    return Q()


def _user_field(Model) -> str | None:
    for f in ("usuario", "aluno", "user", "owner"):
        if _has_field(Model, f):
            return f
    return None


# ----------------------------------------------------------------------------
# Projeto 21 – páginas base (dashboard + stubs)
# ----------------------------------------------------------------------------

class Projeto21DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "sonho_de_ser/projeto21_dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user

        ctx.setdefault("registros_hoje", 0)
        ctx.setdefault("estrategias_count", None)
        ctx.setdefault("adesao_semana", None)

        # Registro de hoje + adesão da semana
        try:
            user_f = _user_field(RegistroDiario)
            if not user_f:
                raise Exception("RegistroDiario sem FK de usuário")

            data_f = _data_field(RegistroDiario)
            q_ok = _q_concluido(RegistroDiario)

            hoje = date.today()

            # Hoje
            if data_f == "data":
                q_hoje = Q(data=hoje)
            else:
                q_hoje = Q(**{f"{data_f}__date": hoje})

            ctx["registros_hoje"] = (
                RegistroDiario.objects.filter(Q(**{user_f: u}) & q_hoje & q_ok).count()
            )

            # Semana
            ini_sem = hoje - timedelta(days=hoje.weekday())
            fim_sem = ini_sem + timedelta(days=6)
            if data_f == "data":
                q_sem = Q(data__gte=ini_sem, data__lte=fim_sem)
            else:
                q_sem = Q(**{f"{data_f}__date__gte": ini_sem, f"{data_f}__date__lte": fim_sem})

            dias_ok = set()
            for r in RegistroDiario.objects.filter(Q(**{user_f: u}) & q_sem & q_ok):
                v = getattr(r, data_f)
                d = v.date() if hasattr(v, "date") else v
                dias_ok.add(d)

            dias_passados = (hoje - ini_sem).days + 1
            ctx["adesao_semana"] = round((len(dias_ok) / max(1, dias_passados)) * 100)
        except Exception:
            pass

        try:
            ctx["estrategias_count"] = Estrategia.objects.filter(ativo=True).count()
        except Exception:
            pass

        return ctx


class Projeto21PlanoView(LoginRequiredMixin, TemplateView):
    template_name = "sonho_de_ser/projeto21_plano.html"


class Projeto21RegistroHojeView(LoginRequiredMixin, TemplateView):
    template_name = "sonho_de_ser/projeto21_registro.html"


class Projeto21HistoricoView(LoginRequiredMixin, TemplateView):
    template_name = "sonho_de_ser/projeto21_historico.html"


class Projeto21PontuacaoView(LoginRequiredMixin, TemplateView):
    template_name = "sonho_de_ser/projeto21_pontuacao.html"


class Projeto21MentorView(LoginRequiredMixin, TemplateView):
    template_name = "sonho_de_ser/projeto21_mentor.html"


# ----------------------------------------------------------------------------
# API – Áreas / Estratégias / Registro Diário / Mentoria / Anotações
# ----------------------------------------------------------------------------

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


class EstrategiaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EstrategiaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = (
            Estrategia.objects.filter(ativo=True)
            .select_related("area")
            .order_by("area__inicial", "codigo")  # ou "titulo" se não houver "codigo"
        )

        area = self.request.query_params.get("area")  # nome da área
        area_inicial = self.request.query_params.get("inicial")  # "F", "I"...
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


class RegistroDiarioViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RegistroDiarioSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        qs = (
            RegistroDiario.objects.filter(usuario=user)
            .select_related("estrategia", "estrategia__area")
            .order_by("-data", "estrategia__codigo")
        )
        data_param = self.request.query_params.get("data")  # YYYY-MM-DD
        estrategia_codigo = self.request.query_params.get("estrategia")
        concluido = self.request.query_params.get("concluido")
        if data_param:
            qs = qs.filter(data=data_param)
        if estrategia_codigo:
            qs = qs.filter(estrategia__codigo__iexact=estrategia_codigo)
        if concluido in {"true", "false", "1", "0"} and _has_field(RegistroDiario, "concluido"):
            qs = qs.filter(concluido=concluido.lower() in {"true", "1"})
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        data_val = serializer.validated_data.get("data") or timezone.localdate()
        serializer.save(usuario=user, data=data_val)

    @action(detail=True, methods=["post"])
    def concluir(self, request, pk=None):
        reg = self.get_object()
        if _has_field(RegistroDiario, "concluido"):
            reg.concluido = True
            reg.save(update_fields=["concluido"])  # + updated_at se existir
        return Response({"detail": "Registro concluído."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reabrir(self, request, pk=None):
        reg = self.get_object()
        if _has_field(RegistroDiario, "concluido"):
            reg.concluido = False
            reg.save(update_fields=["concluido"])  # + updated_at se existir
        return Response({"detail": "Registro reaberto."}, status=status.HTTP_200_OK)


class MentorProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
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


class MentoriaViewSet(viewsets.ModelViewSet):
    serializer_class = MentoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Mentoria.objects.select_related("mentor__usuario", "aluno").all()

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        if user.is_staff:
            return qs.order_by("-inicio")

        try:
            mentor_profile = user.mentor_profile
        except MentorProfile.DoesNotExist:
            mentor_profile = None

        if mentor_profile:
            return qs.filter(models.Q(mentor=mentor_profile) | models.Q(aluno=user)).order_by("-inicio")

        return qs.filter(aluno=user).order_by("-inicio")

    def perform_create(self, serializer):
        user = self.request.user
        try:
            mentor_profile = user.mentor_profile
        except MentorProfile.DoesNotExist:
            return Response({"detail": "Usuário não possui MentorProfile."}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(mentor=mentor_profile)

    @action(detail=True, methods=["post"])
    def encerrar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "encerrada"
        mentoria.fim = timezone.localdate()
        mentoria.save(update_fields=["status", "fim"])  # + updated_at se existir
        return Response({"detail": "Mentoria encerrada."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def pausar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "pausada"
        mentoria.save(update_fields=["status"])  # + updated_at se existir
        return Response({"detail": "Mentoria pausada."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reativar(self, request, pk=None):
        mentoria = self.get_object()
        mentoria.status = "ativa"
        mentoria.fim = None
        mentoria.save(update_fields=["status", "fim"])  # + updated_at se existir
        return Response({"detail": "Mentoria reativada."}, status=status.HTTP_200_OK)


class AnotacaoMentorViewSet(viewsets.ModelViewSet):
    serializer_class = AnotacaoMentorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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

        try:
            mentor_profile = user.mentor_profile
        except MentorProfile.DoesNotExist:
            mentor_profile = None

        if mentor_profile:
            return qs.filter(autor=mentor_profile)

        return qs.filter(mentoria__aluno=user, visibilidade="compartilhada")

    def perform_create(self, serializer):
        user = self.request.user
        try:
            mentor_profile = user.mentor_profile
        except MentorProfile.DoesNotExist:
            return Response({"detail": "Somente mentores podem criar anotações."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(autor=mentor_profile)


# ----------------------------------------------------------------------------
# Projeto 21 – views funcionais (operacionais)
# ----------------------------------------------------------------------------
from .forms import PlanoForm
from .models import Estrategia, Plano

@login_required
def plano_view(request):
    plano, _ = Plano.objects.get_or_create(usuario=request.user, ativo=True)

    if request.method == "POST":
        form = PlanoForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Plano atualizado!")
            return redirect("/projeto21/")
    else:
        form = PlanoForm(usuario=request.user)

    # Agrupa estratégias por área
    qs = (Estrategia.objects.filter(ativo=True)
          .select_related("area")
          .order_by("area__inicial", "nivel", "ordem_nivel"))
    grupos = {}
    for e in qs:
        grupos.setdefault(e.area, []).append(e)

    return render(
        request,
        "sonho_de_ser/projeto21_plano.html",
        {
            "form": form,
            "grupos": grupos,                    # {Area: [Estrategia, ...]}
            "sel": set(form.initial.get("estrategias", [])),  # pks já no plano
        },
    )

@login_required
def registro_view(request):
    """Registro do dia com base nas estratégias do plano atual."""
    plano = Plano.objects.filter(usuario=request.user, ativo=True).first()
    if not plano:
        messages.info(request, "Crie seu plano antes de registrar o dia.")
        return redirect("/projeto21/plano/")

    today = date.today()

    if request.method == "POST":
        form = RegistroForm(plano, request.POST)
        if form.is_valid():
            reg = form.save(today)
            messages.success(request, f"Registro de {reg.data:%d/%m} salvo.")
            return redirect("/projeto21/registro/")
    else:
        form = RegistroForm(plano)

    # Estratégias agrupadas por área
    grupos = {}
    try:
        from .models import PlanoEstrategia
        pes = (
            PlanoEstrategia.objects.filter(plano_objetivo__plano=plano, ativo=True)
            .select_related("plano_objetivo__objetivo__area", "estrategia")
            .order_by(
                "plano_objetivo__objetivo__area__ordem",
                "plano_objetivo__objetivo__ordem",
                "estrategia__ordem",
            )
        )
        for pe in pes:
            area = pe.plano_objetivo.objetivo.area
            grupos.setdefault(area, []).append(pe)
    except Exception:
        pass

    return render(
        request, "sonho_de_ser/projeto21_registro.html", {"form": form, "grupos": grupos, "hoje": today}
    )


@login_required
def historico_view(request):
    """Histórico simples: últimos 30 registros do usuário."""
    plano = Plano.objects.filter(usuario=request.user, ativo=True).first()
    if not plano:
        messages.info(request, "Você ainda não tem um plano ativo.")
        return redirect("/projeto21/plano/")

    regs = (
        RegistroDiario.objects.filter(usuario=request.user)
        .order_by("-data", "-id")[:30]
    )
    return render(request, "sonho_de_ser/projeto21_historico.html", {"registros": regs})


@login_required
def pontuacao_view(request):
    """Adesão semanal com base no RegistroDiario do usuário."""
    plano = Plano.objects.filter(usuario=request.user, ativo=True).first()
    if not plano:
        messages.info(request, "Você ainda não tem um plano ativo.")
        return redirect("/projeto21/plano/")

    # Cálculo leve (sem depender de services.py): percentual por dia e geral
    hoje = date.today()
    ini = hoje - timedelta(days=hoje.weekday())
    serie = []

    # total possível do dia = número de estratégias do plano
    try:
        from .models import PlanoItem
        total_dia = PlanoItem.objects.filter(plano=plano, ativo=True).count()
    except Exception:
        total_dia = 0

    for i in range(7):
        d = ini + timedelta(days=i)
        feitos = RegistroDiario.objects.filter(usuario=request.user, data=d).count()
        perc = int((feitos / total_dia) * 100) if total_dia else 0
        serie.append({"data": d, "percentual": perc})

    possiveis = total_dia * len(serie)
    feitos_total = sum(RegistroDiario.objects.filter(usuario=request.user, data__range=(ini, ini + timedelta(days=6))).values_list("id", flat=True).count() for _ in [0])
    # mais barato:
    feitos_total = sum(p['percentual'] for p in serie) * (total_dia / 100) if total_dia else 0
    geral = int((feitos_total / possiveis) * 100) if possiveis else 0

    info = {"serie": serie, "geral": geral}
    return render(request, "sonho_de_ser/projeto21_pontuacao.html", {"info": info})
