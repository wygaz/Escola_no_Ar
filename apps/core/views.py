from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
# apps/core/views.py (adicione/ajuste sua PortalView)
from django.contrib.auth.decorators import login_required

TEMPLATE_BY_PERFIL = {
"ADMIN": "portal/admin_home.html",
"PROF": "portal/prof_home.html",
"MENTOR": "portal/mentor_home.html",
"ALUNO": "portal/aluno_home.html",
"USER": "portal/user_home.html",
}

@login_required
def portal_home(request):
    perfil = getattr(request.user, "perfil", "USER")
    tpl = TEMPLATE_BY_PERFIL.get(perfil, TEMPLATE_BY_PERFIL["USER"])
    return render(request, tpl, {})

class PortalDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "portal/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user

        # Tudo opcional: se o app/tabela não existir, simplesmente ignora
        try:
            from apps.sonho_de_ser.models import Mentoria
            ctx["mentorandos_count"] = Mentoria.objects.filter(
                mentor=u, ativo=True, status="ATIVA"
            ).count()
        except Exception:
            pass

        try:
            # Se já tiver app de cursos/turmas/matrículas
            from apps.cursos.models import Curso, Matricula, Turma
            if getattr(u, "perfil", None) == "PROF":
                ctx["cursos_count"] = Curso.objects.filter(professor=u).count()
                ctx["turmas_count"] = Turma.objects.filter(professor=u).count()
            else:
                ctx["cursos_count"] = Matricula.objects.filter(aluno=u, status="ATIVO").count()
        except Exception:
            pass

        # exemplo: atividades pendentes (se existir)
        try:
            from apps.atividades.models import AtividadeResposta
            ctx["atividades_pendentes"] = AtividadeResposta.objects.filter(
                aluno=u, status="PENDENTE"
            ).count()
        except Exception:
            pass

        return ctx
class RelatoriosView(LoginRequiredMixin, TemplateView):
    template_name = "core/relatorios.html"
class CursosHomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/cursos_home.html"
class TurmasHomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/turmas_home.html"
class AvaliacoesHomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/avaliacoes_home.html"
class MentoriasHomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/mentorias_home.html"
class MeusCursosView(LoginRequiredMixin, TemplateView):
    template_name = "core/meus_cursos.html"
class MinhasAtividadesView(LoginRequiredMixin, TemplateView):
    template_name = "core/minhas_atividades.html"
class MinhasNotasView(LoginRequiredMixin, TemplateView):
    template_name = "core/minhas_notas.html"
class VocacionalMentorView(LoginRequiredMixin, TemplateView):
    template_name = "vocacional/mentor_home.html"


def raiz_inteligente(request):
    return redirect("/portal/") if request.user.is_authenticated else redirect("/contas/login/")
