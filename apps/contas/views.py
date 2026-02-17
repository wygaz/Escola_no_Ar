from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, PerfilForm, AlterarSenhaForm, UsuarioCreationForm
from django.contrib.auth import get_user_model
from .forms import FormularioImagem
from django.template.loader import get_template
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import login


def registrar(request):
    default_next = "/projeto21/"
    next_url = request.POST.get("next") or request.GET.get("next") or default_next

    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # evita open redirect
            if not url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = default_next

            return redirect(next_url)
    else:
        form = UsuarioCreationForm()
    return render(request, "contas/criar_conta.html", {"form": form, "next": next_url})


def testar_template(request):
    try:
        template = get_template('contas/login.html')
        return HttpResponse("✅ Template localizado com sucesso.")
    except Exception as e:
        return HttpResponse(f"❌ Erro ao localizar o template: {e}")

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        ident = (request.POST.get("email") or request.POST.get("username") or "").strip().lower()
        password = request.POST.get("password") or ""
        remember = (request.POST.get("remember_me") == "on")
        request.session.set_expiry(1209600 if remember else 0)  # 14 dias vs. sessão

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
            request.session.set_expiry(1209600 if remember else 0)
            next_url = (request.POST.get("next")
                        or request.GET.get("next")
                        or reverse("vocacional:avaliacao_gate"))
            return redirect(next_url)

        messages.error(request, "E-mail ou senha inválidos.")

    ctx = {"next": request.GET.get("next", "")}
    return render(request, "contas/login.html", ctx)

@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Logout simples.

    - Aceita GET e POST (evita 405 em botões/link antigos).
    - Se vier ?next=/... ou POST next, redireciona com segurança.
    """
    next_url = request.POST.get("next") or request.GET.get("next")

    logout(request)

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect("portal")
# pega o destino desejado (pode vir por POST ou GET)
    next_url = request.POST.get("next") or request.GET.get("next")
    logout(request)

    if next_url:
        return redirect(resolve_url(next_url))

    # fallback padrão
    return redirect("contas:login")

@login_required
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