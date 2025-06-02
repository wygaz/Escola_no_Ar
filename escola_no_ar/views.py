from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from django.contrib.auth import update_session_auth_hash


def cadastro_usuario(request):
    from .forms import FormularioCadastro
    if request.method == 'POST':
        form = FormularioCadastro(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('login')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = FormularioCadastro()

    return render(request, 'cadastro.html', {'form': form})


def login_view(request):
    return render(request, 'login.html')

def cadastro_view(request):
    return render(request, 'cadastro.html')

@login_required
def perfil_usuario(request):
    return render(request, 'perfil.html')

@login_required
def alterar_imagem(request):
    if request.method == 'POST':
        imagem = request.FILES.get('foto_perfil')

        if not imagem:
            messages.error(request, 'Nenhum arquivo foi enviado.')
            return redirect('perfil_usuario')

        # ✅ Tipos de imagem permitidos
        tipos_permitidos = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp']
        if imagem.content_type not in tipos_permitidos:
            messages.error(request, 'Formato inválido. Envie uma imagem JPG, PNG, GIF ou WEBP.')
            return redirect('perfil_usuario')

        # ✅ Limite de tamanho (2 MB = 2 * 1024 * 1024 bytes)
        if imagem.size > 2 * 1024 * 1024:
            messages.error(request, 'Arquivo muito grande. O limite é 2 MB.')
            return redirect('perfil_usuario')

        # ✅ Atualiza a imagem
        usuario = request.user
        usuario.foto_perfil = imagem
        usuario.save()
        messages.success(request, 'Foto de perfil atualizada com sucesso!')

    return redirect('perfil_usuario')


@login_required
def alterar_senha(request):
    if request.method == 'POST':
        usuario = request.user
        senha_atual = request.POST.get('senha_atual')
        nova_senha1 = request.POST.get('nova_senha1')
        nova_senha2 = request.POST.get('nova_senha2')

        if not usuario.check_password(senha_atual):
            messages.error(request, 'Senha atual incorreta.')
            return redirect('perfil_usuario')

        if nova_senha1 != nova_senha2:
            messages.error(request, 'As novas senhas não coincidem.')
            return redirect('perfil_usuario')

        usuario.set_password(nova_senha1)
        usuario.save()
        update_session_auth_hash(request, usuario)
        messages.success(request, 'Senha alterada com sucesso!')
        return redirect('perfil_usuario')

    messages.error(request, 'Requisição inválida.')
    return redirect('perfil_usuario')
