"""
Django settings para o projeto Escola no Ar.

- Usuário custom (contas.Usuario)
- Templates globais em BASE_DIR/templates + templates nos apps (APP_DIRS=True)
- WhiteNoise para estáticos (produção)
- .env via django-environ
"""

import sys
import os
import dj_database_url
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.pop("DATABASE_URL", None)
load_dotenv(BASE_DIR / ".env", override=True)

# -----------------------------------------------------------------------------
# Caminhos base
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Facilita imports de apps/ (ex.: "import contas" direto se quiser)
# Se seus apps estão em BASE_DIR/apps
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# -----------------------------------------------------------------------------
# Segurança & Debug (dotenv + dj_database_url)
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-insegura")
#DEBUG = os.getenv("DEBUG", "False") == "True"
DEBUG=True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "escolanoar-production.up.railway.app,localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "https://escolanoar-production.up.railway.app,http://localhost:8000,http://127.0.0.1:8000"
).split(",")


# -----------------------------------------------------------------------------
# Apps
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    # Apps internos (devem vir antes do Django Admin quando há dependência de user model)
    "apps.contas.apps.ContasConfig",  # Precisa vir antes de admin
    "apps.core.apps.CoreConfig",

    # Django core
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    # "django_extensions",  # opcional

    # Apps internos adicionais
    "apps.atividades.apps.AtividadesConfig",
    "apps.comunicacao.apps.ComunicacaoConfig",
    "apps.cursos.apps.CursosConfig",
    "apps.sonho_de_ser.apps.SonhoDeSerConfig",
    "apps.vocacional.apps.VocacionalConfig",
    "apps.projeto21.apps.Projeto21Config",
    
    # Terceiros
    "rest_framework",
]

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        # "rest_framework.authentication.TokenAuthentication",
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
    "whitenoise.middleware.WhiteNoiseMiddleware",  # estáticos em produção

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "escola_no_ar_site.urls"

# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # >>> adiciona esta linha:
                "apps.core.context_processors.ui",
            ],
        },
    },
]


WSGI_APPLICATION = "escola_no_ar_site.wsgi.application"

# -----------------------------------------------------------------------------
# Banco de Dados
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Banco de Dados
# -----------------------------------------------------------------------------
import dj_database_url
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Produção (Railway) – usa a URL do Postgres
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    # Ambiente local – usa seu Postgres de desenvolvimento
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "escola_no_ar_local",
            "USER": "postgres",
            "PASSWORD": "",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }

# -----------------------------------------------------------------------------
# Usuário custom + Autenticação
# -----------------------------------------------------------------------------
AUTH_USER_MODEL = "contas.Usuario"

# URLs de login/logout (ajuste para casar com suas rotas de contas/)
LOGIN_URL = "contas:login"
LOGIN_REDIRECT_URL = "portal"
LOGOUT_REDIRECT_URL = "portal"   # fallback se não vier ?next

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# i18n
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Estáticos & Mídia
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")   # destino do collectstatic

# Se tiver pasta global de assets locais:
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# -----------------------------------------------------------------------------
# E-mail
# -----------------------------------------------------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND") or (
    "django.core.mail.backends.console.EmailBackend" if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend"
)
# 2) Config SMTP (só será usado se EMAIL_BACKEND = smtp)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"


# 3) From padrão
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL") or EMAIL_HOST_USER or "no-reply@escolanoar.com.br"
SERVER_EMAIL = os.getenv("SERVER_EMAIL") or DEFAULT_FROM_EMAIL

# 4) Fallback: se escolheu SMTP mas faltam credenciais, força console para não quebrar em dev
if EMAIL_BACKEND.endswith("smtp.EmailBackend"):
    if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# 5) Contatos
DEFAULT_FROM_EMAIL = "nao-responder@escolanoar.com.br"
EMAIL_CONTATO = "wygazeta@gmail.com.com"

# -----------------------------------------------------------------------------
# Defaults de AutoField
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- VOCACIONAL (feature flags) ----
VOCACIONAL_REQUIRE_BONUS = False      # pausa o bônus por enquanto
VOCACIONAL_REQUIRE_CONSENT = True     # manter aceite obrigatório
VOCACIONAL_REQUIRE_GUIA = True        # manter avaliação do guia obrigatória

# --- LOGGING (adicionar/mesclar) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "vocacional": {
            "handlers": ["console"],
            "level": "DEBUG",   # mude para INFO em produção
            "propagate": False,
        },
    },
}

