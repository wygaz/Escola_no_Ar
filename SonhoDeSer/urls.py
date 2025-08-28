from django.urls import path
from . import views

app_name = 'sonho'

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial do app
    path('perfil/', views.perfil_aluno, name='perfil'),
    path('desafio/', views.desafio_dia, name='desafio'),
    path('comunidade/', views.feed_comunidade, name='comunidade'),
]