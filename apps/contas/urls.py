# apps/contas/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views  # suas views (ex.: registrar, perfil etc.)

app_name = "contas"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="contas/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    # POST-only
    path("logout/", views.logout_view, name="logout"),

    # REGISTRO (criar conta)
    path("registrar/", views.registrar, name="registrar"),

    # TROCAR SENHA (usuário logado)
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="contas/alterar_senha.html",
            success_url=reverse_lazy("contas:password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="contas/redefinir_sucesso.html"
        ),
        name="password_change_done",
    ),

    # RESET DE SENHA (via e-mail)
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="contas/recuperar_senha.html",
            email_template_name="contas/email_recuperacao.html",
            subject_template_name="contas/assunto_email.txt",
            success_url=reverse_lazy("contas:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="contas/recuperar_senha_enviado.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="contas/redefinir_senha.html",
            success_url=reverse_lazy("contas:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="contas/redefinir_sucesso.html"
        ),
        name="password_reset_complete",
    ),
]
