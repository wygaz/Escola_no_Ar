# escola_no_ar_site/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth global usando SEUS templates (templates/contas/*.html)
    path("login/",
         auth_views.LoginView.as_view(template_name="contas/login.html"),
         name="login"),
    path("logout/",
         auth_views.LogoutView.as_view(template_name="contas/logged_out.html"),
         name="logout"),

    # Recuperação de senha (aponta para seus arquivos)
    path("password_reset/",
         auth_views.PasswordResetView.as_view(
             template_name="contas/recuperar_senha.html",
             email_template_name="contas/email_recuperacao.html",
             subject_template_name="contas/assunto_email.txt",
         ),
         name="password_reset"),
    path("password_reset/done/",
         auth_views.PasswordResetDoneView.as_view(
             template_name="contas/recuperar_senha_enviado.html"
         ),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
             template_name="contas/redefinir_senha.html"
         ),
         name="password_reset_confirm"),
    path("reset/done/",
         auth_views.PasswordResetCompleteView.as_view(
             template_name="contas/redefinir_sucesso.html"
         ),
         name="password_reset_complete"),

    # Apps
    path("", include("apps.contas.urls")),              # home/perfil/cadastro
    path("sonhodeser/", include("apps.sonho_de_ser.urls")),
    path("cursos/", include("apps.cursos.urls")),
   # path("atividades/", include("apps.atividades.urls")),
    path("api/", include("apps.sonho_de_ser.urls")),
    # vocacional entra depois
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


