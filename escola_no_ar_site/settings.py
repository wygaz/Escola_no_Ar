"""
Django settings para o projeto Escola no Ar.

Este arquivo foi enxugado e comentado para:
- Centralizar a autenticação com usuário custom (contas.Usuario)
- Usar templates globais em BASE_DIR/templates + templates nos apps (APP_DIRS=True)
- Manter ordem correta dos apps (user antes dos dependentes)
- Habilitar WhiteNoise para arquivos estáticos (produção)
- Ler DATABASE_URL/SECRET_KEY/DEBUG de .env via django-environ
"""

from pathlib import Path
import os
import sys
import environ

# -----------------------------------------------------------------------------
# Caminhos base do projeto
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Facilita imports de apps/ (ex.: "import contas" direto)
# Se seus apps estão em BASE_DIR / "apps"
sys.path.insert(0, str(BASE_DIR / "apps"))

# -----------------------------------------------------------------------------
# Variáveis de ambiente (.env)
# -----------------------------------------------------------------------------
# .env típico:
# DEBUG=True
# SECRET_KEY=chave-secreta
# DATABASE_URL=postgres://usuario:senha@localhost:5432/escolanoar
# ALLOWED_HOSTS=localhost,127.0.0.1,escolanoar.com.br,www.escolanoar.com.br
# CSRF_TRUSTED_ORIGINS=https://escolanoar.com.br,https://www.escolanoar.com.br
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# -----------------------------------------------------------------------------
# Segurança & Debug
# -----------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="chave-padrao-insegura")
DEBUG = env("DEBUG", default=False)

# Hosts e CSRF
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"],
)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:8000", "http://127.0.0.1:8000"],
)

# -----------------------------------------------------------------------------
# Aplicativos
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    # django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # apps internos
     "apps.core.apps.CoreConfig",
    "apps.contas.apps.ContasConfig",
    "apps.sonho_de_ser.apps.SonhoDeSerConfig",
    "rest_framework",
]

# Configuração do Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        # "rest_framework.authentication.TokenAuthentication",  # opcional
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
# -----------------------------------------------------------------------------
# Middlewares
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise: serve arquivos estáticos em produção sem precisar de Nginx
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "escola_no_ar_site.urls"

# -----------------------------------------------------------------------------
# Templates (globais e por app)
# -----------------------------------------------------------------------------
# - DIRS aponta para BASE_DIR/templates (login, base, includes, etc.)
# - APP_DIRS=True permite Django procurar templates dentro de cada app:
#   apps/<app>/templates/<app>/...
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "escola_no_ar_site.wsgi.application"

# -----------------------------------------------------------------------------
# Banco de Dados
# -----------------------------------------------------------------------------
# Lê do .env: DATABASE_URL
# Exemplos:
# - sqlite:   sqlite:///db.sqlite3
# - postgres: postgres://usuario:senha@localhost:5432/escolanoar
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="sqlite:///db.sqlite3",   # fallback em dev
    )
}
# Para Postgres, ajuda a padronizar o client encoding
if DATABASES["default"]["ENGINE"].endswith("postgresql") or "postgres" in DATABASES["default"]["ENGINE"]:
    DATABASES["default"].setdefault("OPTIONS", {})
    # Garante client UTF8
    DATABASES["default"]["OPTIONS"].setdefault("options", "-c client_encoding=UTF8")

# -----------------------------------------------------------------------------
# Usuário custom + Autenticação
# -----------------------------------------------------------------------------
AUTH_USER_MODEL = "contas.Usuario"

# Fluxo de login/logout (views padrão do Django + seus templates)
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/sonhodeser/"  # pós-login cai direto no app sonho_de_ser
LOGOUT_REDIRECT_URL = "/login/"

# Validações de senha (mantenha o padrão do Django)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# Internacionalização
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Arquivos estáticos e mídia
# -----------------------------------------------------------------------------
# Estáticos (coletados em produção com collectstatic)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # destino do collectstatic (produção)

# (Opcional) Se você tiver uma pasta global "static/" no projeto para assets:
# STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise: serve estáticos comprimidos e com manifest em prod
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Mídia (uploads de usuários, ex.: fotos de perfil)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------------------------------------------------
# E-mail (reset de senha, notificações)
# -----------------------------------------------------------------------------
# Em desenvolvimento, envia para o console. Em produção, configure SMTP:
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Escola no Ar <naoresponda@escolanoar.com.br>"

# -----------------------------------------------------------------------------
# Defaults de ID de auto increment
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
