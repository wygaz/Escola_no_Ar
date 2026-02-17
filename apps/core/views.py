# apps\core\views.py
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django import forms
from django.templatetags.static import static
from apps.core.permissions import user_has_produto, PROD_VOCACIONAL, PROD_SONHEMAISALTO, require_legal

@login_required
@require_legal()
def portal_home(request):
    # toggle para testes (fica salvo na sessão)
    mode = request.GET.get("portal_mode")
    if mode in {"user", "gov"}:
        request.session["portal_mode"] = mode

    u = request.user

    # staff/superuser: por padrão vai para governança, a menos que force modo user
    if (u.is_staff or u.is_superuser) and request.session.get("portal_mode") != "user":
        return redirect("portal_dashboard")

    # usuário comum (ou staff em modo user): portal simples (2 opções)
    ctx = {
        "hide_global_header": True,
        "can_sonhemaisalto": user_has_produto(u, PROD_SONHEMAISALTO),
        "can_vocacional": user_has_produto(u, PROD_VOCACIONAL),
        "show_governanca_toggle": bool(u.is_staff or u.is_superuser),
    }
    return render(request, "core/portal.html", ctx)




def sonhe_mais_alto_landing(request):
    context = {
        "hide_global_header": True,  # esconde o cabeçalho azul marinho
    }
    return render(request, "core/sonhe_mais_alto_landing.html", context)

def home_funil(request):
    """Entrada do site:
    - Usuário anônimo: vai para tela de login
    - Usuário logado: vai direto para Projeto 21
    """
    if request.user.is_authenticated:
        # Se você tiver um nome de url para essa página, use reverse:
        # return redirect("projeto21:home")
        return redirect("portal")
    return redirect("contas:login")

class ContatoForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=100)
    email = forms.EmailField(label="E-mail")
    assunto = forms.CharField(label="Assunto", max_length=120, required=False)
    mensagem = forms.CharField(
        label="Mensagem",
        widget=forms.Textarea(attrs={"rows": 5}),
    )

def sobre(request):
    return render(request, "sobre.html")

def portal(request):
    # raiz pública (logado ou não). Se estiver logado, já exibe flags de acesso.
    ctx = {"hide_global_header": True}
    if request.user.is_authenticated:
        u = request.user
        ctx.update({
            "can_sonhemaisalto": user_has_produto(u, PROD_SONHEMAISALTO),
            "can_vocacional": user_has_produto(u, PROD_VOCACIONAL),
            "show_governanca_toggle": bool(u.is_staff or u.is_superuser),
        })
    return render(request, "core/portal.html", ctx)

def contato(request):
    if request.method == "POST":
        form = ContatoForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            assunto = cd.get("assunto") or "Contato pelo site Escola no Ar"
            corpo = (
                f"Nome: {cd['nome']}\n"
                f"E-mail: {cd['email']}\n\n"
                f"Mensagem:\n{cd['mensagem']}"
            )

            destinatario = getattr(
                settings, "EMAIL_CONTATO", getattr(settings, "DEFAULT_FROM_EMAIL", None)
            )

            if destinatario:
                send_mail(
                    subject=assunto,
                    message=corpo,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[destinatario],
                    fail_silently=True,   # evita quebrar se o email não estiver configurado
                )

            messages.success(request, "Mensagem enviada com sucesso! Obrigado pelo contato.")
            return redirect("contato")
    else:
        form = ContatoForm()

    return render(request, "contato.html", {"form": form})


TEMPLATE_BY_PERFIL = {
"ADMIN": "portal/admin_home.html",
"PROF": "portal/prof_home.html",
"MENTOR": "portal/mentor_home.html",
"ALUNO": "portal/aluno_home.html",
"USER": "portal/user_home.html",
}
class PortalDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "portal/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        u = self.request.user  # <<< PRIMEIRO!

        ctx["can_sonhemaisalto"] = user_has_produto(u, PROD_SONHEMAISALTO)
        ctx["can_vocacional"] = user_has_produto(u, PROD_VOCACIONAL)

        # Tudo opcional: se o app/tabela não existir, simplesmente ignora
        try:
            from apps.sonho_de_ser.models import Mentoria
            ctx["mentorandos_count"] = Mentoria.objects.filter(
                mentor=u, ativo=True, status="ATIVA"
            ).count()
        except Exception:
            pass

        try:
            from apps.cursos.models import Curso, Matricula, Turma
            if getattr(u, "perfil", None) == "PROF":
                ctx["cursos_count"] = Curso.objects.filter(professor=u).count()
                ctx["turmas_count"] = Turma.objects.filter(professor=u).count()
            else:
                ctx["cursos_count"] = Matricula.objects.filter(aluno=u, status="ATIVO").count()
        except Exception:
            pass

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
    return redirect("portal") if request.user.is_authenticated else redirect("/contas/login/")


HOTMART_GUIA_URL = "https://pay.hotmart.com/Q103340890M?bid=1765338293599"

def guia_redirect_preview(request):
    """
    Página com Open Graph para gerar preview (WhatsApp/FB/IG),
    e redireciona o usuário para a Hotmart.
    """
    og_title = "Guia Sonhe + Alto"
    og_description = (
        "Menos ansiedade, mais direção: escolhas de curso e profissão para jovens. "
        "Apoio a pais e mentores."
    )

    # Coloque sua capa em: static/core/img/capa-guia.jpg
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
    og_url = request.build_absolute_uri(request.path)

    context = {
        "hotmart_url": HOTMART_GUIA_URL,
        "og_title": og_title,
        "og_description": og_description,
        "og_image": og_image,
        "og_url": og_url,
    }
    return render(request, "core/guia_redirect.html", context)
