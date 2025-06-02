from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_usuario, name='cadastro'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/alterar-imagem/', views.alterar_imagem, name='alterar_imagem'),
    path('perfil/alterar-senha/', views.alterar_senha, name='alterar_senha'),
]
