from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('editar-perfil/', views.editar_perfil_view, name='editar_perfil'),
    path('alterar-senha/', views.alterar_senha_view, name='alterar_senha'),
    path('testar-template/', views.testar_template, name='testar_template'),
    path('recuperar-senha/', auth_views.PasswordResetView.as_view(
        template_name='contas/recuperar_senha.html',
        email_template_name='contas/email_recuperacao.html',
        subject_template_name='contas/assunto_email.txt',
        success_url='/recuperar-senha/enviado/'
    ), name='password_reset'),

    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='contas/recuperar_senha_enviado.html'
    ), name='password_reset_done'),

    path('redefinir/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='contas/redefinir_senha.html',
        success_url='/redefinir/sucesso/'
    ), name='password_reset_confirm'),

    path('redefinir/sucesso/', auth_views.PasswordResetCompleteView.as_view(
        template_name='contas/redefinir_sucesso.html'
    ), name='password_reset_complete'),

    path('alterar-imagem/', views.alterar_imagem_view, name='alterar_imagem'),
]
