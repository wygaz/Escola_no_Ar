import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import PerfilForm, AlterarSenhaForm, LoginForm, UsuarioCreationForm
from django.contrib.auth import get_user_model
from .forms import FormularioImagem
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlsplit


logger = logging.getLogger(__name__)


def _send_email_confirmation(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    confirm_url = request.build_absolute_uri(
        reverse("contas:confirmar_email", args=[uid, token])
    )
    context = {
        "user": user,
        "confirm_url": confirm_url,
        "site_name": "Escola no Ar",
    }
    body = render_to_string("contas/email_confirmacao_cadastro.html", context)
    send_mail(
        subject="Confirme seu e-mail - Escola no Ar",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def registrar(request):
    default_next = reverse("portal")  # antes: "/projeto21/"
    next_url = request.POST.get("next") or request.GET.get("next") or default_next

    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            form.persist_legal_acceptance(user)
            _send_email_confirmation(request, user)

            # evita open redirect
            if not url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = default_next

            request.session["registration_next_url"] = next_url
            return redirect("contas:confirmacao_email_enviada")
    else:
        form = UsuarioCreationForm()
    return render(request, "contas/criar_conta.html", {"form": form, "next": next_url})


def confirmacao_email_enviada(request):
    return render(request, "contas/confirmacao_email_enviada.html")


def confirmar_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "O link de confirmação é inválido ou expirou.")
        return redirect("contas:login")

    update_fields = []
    if not user.is_active:
        user.is_active = True
        update_fields.append("is_active")
    if not user.email_confirmado_em:
        user.email_confirmado_em = timezone.now()
        update_fields.append("email_confirmado_em")
    if update_fields:
        user.save(update_fields=update_fields)

    login(request, user)
    messages.success(request, "E-mail confirmado com sucesso. Sua conta já está ativa.")
    next_url = request.session.pop("registration_next_url", None) or reverse("portal")
    return redirect(next_url)


def testar_template(request):
    try:
        template = get_template('contas/login.html')
        return HttpResponse("✅ Template localizado com sucesso.")
    except Exception as e:
        return HttpResponse(f"❌ Erro ao localizar o template: {e}")

User = get_user_model()

SESSION_CONTEXT_KEYS = (
    "impersonate_user_id",
    "portal_mode",
)


def _clear_session_context(request) -> None:
    for key in SESSION_CONTEXT_KEYS:
        request.session.pop(key, None)


def _normalized_redirect_path(url: str | None) -> str:
    if not url:
        return "/"
    return urlsplit(url).path or "/"


def _is_restricted_redirect_path(path: str) -> bool:
    return (
        path == "/admin"
        or path == "/admin/"
        or path.startswith("/admin/")
        or path == "/portal/dashboard"
        or path == "/portal/dashboard/"
        or path.startswith("/portal/dashboard/")
    )


class SafeLoginView(LoginView):
    authentication_form = LoginForm

    def get_success_url(self):
        redirect_to = super().get_redirect_url()
        user = self.request.user
        normalized_path = None
        final_success_url = None
        if redirect_to:
            normalized_path = _normalized_redirect_path(redirect_to)
            is_restricted_target = _is_restricted_redirect_path(normalized_path)
            is_admin_user = bool(
                getattr(user, "is_staff", False)
                or getattr(user, "is_superuser", False)
            )
            if is_restricted_target and not is_admin_user:
                final_success_url = self.get_default_redirect_url()
            else:
                final_success_url = redirect_to
        else:
            final_success_url = self.get_default_redirect_url()

        logger.warning(
            "AUTH get_success_url user=%s is_staff=%s is_superuser=%s redirect_to=%r normalized_path=%r final_success_url=%r",
            getattr(user, "email", getattr(user, "pk", "anon")),
            getattr(user, "is_staff", False),
            getattr(user, "is_superuser", False),
            redirect_to,
            normalized_path,
            final_success_url,
        )
        return final_success_url

def login_view(request):
    if request.method == "POST":
        ident = (request.POST.get("email") or request.POST.get("username") or "").strip().lower()
        password = request.POST.get("password") or ""
        remember = (request.POST.get("remember_me") == "on")
        request.session.set_expiry(1209600 if remember else 1800)  # 14 dias vs. 30 min

        # atalho: se digitar só o local-part, tenta resolver para 1 e-mail único
        if ident and "@" not in ident:
            qs = User.objects.filter(email__istartswith=ident + "@")
            if qs.count() == 1:
                ident = qs.first().email.lower()

        # USERNAME_FIELD=email → funciona passar username=ident ou email=ident
        user = (authenticate(request, username=ident, password=password)
                or authenticate(request, email=ident, password=password))

        if user and user.is_active:
            login(request, user)
            # lembrar: 14 dias; não lembrar: expira ao fechar o navegador
            request.session.set_expiry(1209600 if remember else 1800)
            next_url = (request.POST.get("next")
                        or request.GET.get("next")
                        or reverse("vocacional:avaliacao_gate"))
            return redirect(next_url)

        messages.error(request, "E-mail ou senha inválidos.")

    ctx = {"next": request.GET.get("next", "")}
    return render(request, "contas/login.html", ctx)

@require_http_methods(["GET", "POST"])
def logout_view(request):
    # opcional: respeita next (quando vier), senão volta ao Portal
    user = getattr(request, "user", None)
    next_url = request.POST.get("next") or request.GET.get("next")
    residual_keys = [key for key in SESSION_CONTEXT_KEYS if key in request.session]
    normalized_path = _normalized_redirect_path(next_url)
    final_redirect = reverse("portal")
    logger.warning(
        "AUTH logout_view before user=%s residual_keys=%s portal_mode=%r impersonate_user_id=%r next_url=%r normalized_path=%r final_redirect=%r",
        getattr(user, "email", getattr(user, "pk", "anon")),
        residual_keys,
        request.session.get("portal_mode"),
        request.session.get("impersonate_user_id"),
        next_url,
        normalized_path,
        final_redirect,
    )
    _clear_session_context(request)
    logout(request)
    return redirect("portal")

def perfil_view(request):
    return render(request, 'contas/perfil.html', {'usuario': request.user})

@login_required
def editar_perfil_view(request):
    usuario = request.user
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=usuario)
    return render(request, 'contas/editar_perfil.html', {'form': form})

@login_required
def alterar_senha_view(request):
    if request.method == 'POST':
        form = AlterarSenhaForm(user=request.user, data=request.POST)
        if form.is_valid():
            usuario = form.save()
            update_session_auth_hash(request, usuario)
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('perfil')
    else:
        form = AlterarSenhaForm(user=request.user)
    return render(request, 'contas/alterar_senha.html', {'form': form})


@login_required
def alterar_imagem_view(request):
    if request.method == 'POST':
        form = FormularioImagem(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imagem alterada com sucesso.')
            return redirect('perfil')
    else:
        form = FormularioImagem(instance=request.user)
    return render(request, 'contas/alterar_imagem.html', {'form': form})
