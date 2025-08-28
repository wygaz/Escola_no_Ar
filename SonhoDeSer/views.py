from django.shortcuts import render

def home(request):
    return render(request, 'sonho/base_sonho.html')

def perfil_aluno(request):
    return render(request, 'sonho/perfil_aluno.html')

def desafio_dia(request):
    return render(request, 'sonho/desafio_dia.html')

def feed_comunidade(request):
    return render(request, 'sonho/feed_comunidade.html')
