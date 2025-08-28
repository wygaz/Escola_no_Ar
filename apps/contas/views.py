from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, PerfilForm, AlterarSenhaForm
from django.contrib.auth import get_user_model
from .forms import FormularioImagem

from django.template.loader import get_template
from django.http import HttpResponse
def testar_template(request):
    try:
        template = get_template('contas/login.html')
        return HttpResponse("✅ Template localizado com sucesso.")
    except Exception as e:
        return HttpResponse(f"❌ Erro ao localizar o template: {e}")

Usuario = get_user_model()

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']
            usuario = authenticate(request, email=email, password=senha)
            if usuario is not None:
                login(request, usuario)
                return redirect('perfil')
            else:
                messages.error(request, 'E-mail ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'contas/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

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
