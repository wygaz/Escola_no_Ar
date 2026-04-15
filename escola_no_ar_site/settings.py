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

# ---------------------------------------------
# ENV / Banco de Dados (Escola no Ar)
# ---------------------------------------------

# ENV_NAME escolhe qual .env carregar *se* existir (local/remote/prod)
ENV_NAME = os.getenv("ENV_NAME", "local")
env_file = BASE_DIR / f".env.{ENV_NAME}"
if env_file.exists():
    # override=True garante que o .env *sempre* vence no ambiente local
    load_dotenv(env_file, override=True)

# Escolhe a URL do banco por prioridade:
# 1) DATABASE_URL (sempre preferida)
# 2) DATABASE_PUBLIC_URL (fallback para acesso externo quando estiver rodando local)
_db_url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL")

if not _db_url:
    raise RuntimeError(
        "DATABASE_URL não definido. "
        "Defina DATABASE_URL (produção/contêiner) ou use o valor de "
        "DATABASE_PUBLIC_URL quando for acessar remotamente a partir do Django local."
    )

# Railway/Postgres normalmente requer SSL (obrigatório fora de redes 100% locais)
DB_SSL_REQUIRE = os.getenv("DB_SSL_REQUIRE", "1").strip().lower() in ("1", "true", "yes")

DATABASES = {
    "default": dj_database_url.parse(
        _db_url,
        conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "600")),
        ssl_require=DB_SSL_REQUIRE,
    )
}



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

# ------- ALLOWED_HOSTS -------

_default_allowed = (
    "www.sonhemaisalto.com.br,"
    "sonhemaisalto.com.br,"
    "escolanoar-production.up.railway.app,"
    "localhost,127.0.0.1"
)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", _default_allowed).split(",")
    if h.strip()
]

# ------- CSRF_TRUSTED_ORIGINS -------

_default_csrf = (
    "https://www.sonhemaisalto.com.br,"
    "https://escolanoar-production.up.railway.app,"
    "http://localhost:8000,"
    "http://127.0.0.1:8000"
)

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv("CSRF_TRUSTED_ORIGINS", _default_csrf).split(",")
    if o.strip()
]

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
    # Permite staff/superuser "testar como" um usuário real (impersonação)
    # sem sair do login.
    "apps.core.middleware.ImpersonateUserMiddleware",
    "apps.core.middleware.Debug403LoggingMiddleware",
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
# Usuário custom + Autenticação
# -----------------------------------------------------------------------------
AUTH_USER_MODEL = "contas.Usuario"

# URLs de login/logout (ajuste para casar com suas rotas de contas/)
LOGIN_URL = "contas:login"
LOGIN_REDIRECT_URL = "/portal/"  # após login, cair no Portal enxuto
LOGOUT_REDIRECT_URL = "contas:login" # fallback se não vier ?next

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

# DEBUG (aceita 0/1, true/false, yes/no, on/off)
DEBUG = os.getenv("DEBUG", "0").strip().lower() in ("1", "true", "yes", "on")

def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")

# -----------------------------------------------------------------------------
# Gating de Bônus / Produtos (Hotmart → Produto/Acesso)
# -----------------------------------------------------------------------------
# Obs.: Sonhe + Alto (Projeto21) já valida via Acesso(produto__slug="projeto21_sonhe_alto")
# Aqui, ligamos o mesmo tipo de proteção para o Vocacional.

# Se True: o Vocacional só fica disponível para quem tem Acesso ao slug "vocacional_bonus".
VOCACIONAL_REQUIRE_BONUS = env_bool("VOCACIONAL_REQUIRE_BONUS", "1")

# Se True: o Sonhe + Alto só fica disponível para quem tem Acesso ao produto (por equivalência, Guia).
SONHEMAISALTO_REQUIRE_BONUS = env_bool("SONHEMAISALTO_REQUIRE_BONUS", "1")

# Se quiser pausar etapas do funil do Vocacional (consentimento/avaliação do guia),
# dá pra desligar separadamente via env.
VOCACIONAL_REQUIRE_CONSENT = env_bool("VOCACIONAL_REQUIRE_CONSENT", "1")
VOCACIONAL_REQUIRE_GUIA = env_bool("VOCACIONAL_REQUIRE_GUIA", "1")

# Quantos passes o fluxo de refinamento do Top 3 usa.
# - 1: fluxo atual (um único questionário)
# - 3: Passe 1 / Passe 2 / Passe 3 (SJT + contexto + mini-experimentos)
VOCACIONAL_PASS_TOTAL = int(os.getenv("VOCACIONAL_PASS_TOTAL", "1"))

# ----------------------------------------------------------------------------
# Refinamento Top 3 (métrica GAP + cobertura + regra de parada)
# ----------------------------------------------------------------------------
VOC_REF_PASS1_PER_DIM = int(os.getenv("VOC_REF_PASS1_PER_DIM", "2"))
VOC_REF_PASS2_PER_DIM = int(os.getenv("VOC_REF_PASS2_PER_DIM", "3"))
VOC_REF_PASS2_TOPK = int(os.getenv("VOC_REF_PASS2_TOPK", "5"))

VOC_REF_GAP_STOP_P1 = float(os.getenv("VOC_REF_GAP_STOP_P1", "0.20"))
VOC_REF_GAP_STOP_P2 = float(os.getenv("VOC_REF_GAP_STOP_P2", "0.15"))
VOC_REF_TOP1_MIN_P1 = float(os.getenv("VOC_REF_TOP1_MIN_P1", "0.35"))
VOC_REF_TOP1_MIN_P2 = float(os.getenv("VOC_REF_TOP1_MIN_P2", "0.32"))

# Temperatura do softmax (menor => mais "duro"). 0.6–1.0 costuma ser bom.
VOC_REF_SOFTMAX_TAU = float(os.getenv("VOC_REF_SOFTMAX_TAU", "0.80"))

# -----------------------------------------------------------------------------
# E-mail
# -----------------------------------------------------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND") or (
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG else
    "django.core.mail.backends.smtp.EmailBackend"
)

# Config SMTP (só será usado se EMAIL_BACKEND = smtp)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

# TLS/SSL (aceita 1/0 também)
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", "1")   # padrão True (587)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", "0")   # padrão False

# Evita configuração inválida
if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ValueError("Defina apenas EMAIL_USE_TLS ou EMAIL_USE_SSL (não ambos).")

# From padrão
DEFAULT_FROM_EMAIL = (
    os.getenv("DEFAULT_FROM_EMAIL")
    or EMAIL_HOST_USER
    or "nao_responda@sonhemaisalto.com.br"
)
SERVER_EMAIL = os.getenv("SERVER_EMAIL") or DEFAULT_FROM_EMAIL

# Fallback: se escolheu SMTP mas faltam credenciais, força console (útil em dev)
if EMAIL_BACKEND.endswith("smtp.EmailBackend"):
    if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Contatos (NÃO sobrescreve o remetente do SMTP)
EMAIL_CONTATO = os.getenv("EMAIL_CONTATO", "wygazeta@gmail.com")




# -----------------------------------------------------------------------------
# Sessões (útil em computador compartilhado)
# - Política padrão: cookie de sessão não persistente
# - Também expira após 30 min de inatividade
# - Pode sobrescrever via ENV: SESSION_COOKIE_AGE (em segundos)
# -----------------------------------------------------------------------------
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', '1800'))
SESSION_SAVE_EVERY_REQUEST = True
