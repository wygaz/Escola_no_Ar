VOCACIONAL — Sprint 1 Add-ons (Consentimento LGPD + Gate)

Arquivos novos (copie mantendo a mesma estrutura de pastas do seu projeto):
- apps/vocacional/models_consent.py
- apps/vocacional/views_consent.py
- apps/vocacional/templatetags/consent_tags.py
- templates/vocacional/consentimento_form.html
- templates/vocacional/privacidade.html

PASSO 1 — models.py
Abra apps/vocacional/models.py e adicione ao final do arquivo:
----------------------------------------------------------------
from .models_consent import *  # Consentimento, Progresso
----------------------------------------------------------------

PASSO 2 — permissions.py
Abra apps/vocacional/permissions.py e acrescente abaixo do require_mentor:
----------------------------------------------------------------
from django.shortcuts import redirect
from .models_consent import Consentimento

def require_consent(view):
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        ativo = Consentimento.objects.filter(user=user, ativo=True).exists()
        if not ativo:
            return redirect("vocacional:consentimento_check")
        return view(request, *args, **kwargs)
    return _wrapped
----------------------------------------------------------------

PASSO 3 — urls.py
Abra apps/vocacional/urls.py e ajuste os imports/rotas:
----------------------------------------------------------------
from django.urls import path, include
from . import views
from . import views_consent  # ADICIONE

app_name = "vocacional"

urlpatterns = [
    path("", views.index, name="index"),
    path("avaliacao/", views.avaliacao_form, name="avaliacao_form"),
    path("resultado/<int:pk>/", views.resultado, name="resultado"),
    path("mentor/", views.mentor_dashboard, name="mentor_dashboard"),
    # NOVAS ROTAS DE CONSENTIMENTO/PRIVACIDADE
    path("consentimento/", views_consent.consentimento_check, name="consentimento_check"),
    path("consentimento/aceitar/", views_consent.consentimento_aceitar, name="consentimento_aceitar"),
    path("consentimento/revogar/", views_consent.consentimento_revogar, name="consentimento_revogar"),
    path("privacidade/", views_consent.privacidade, name="privacidade"),
]
----------------------------------------------------------------

PASSO 4 — index.html
Opcional mas recomendado: condicionar o botão "Iniciar/Continuar" ao consentimento.

Edite templates/vocacional/index.html:
- No topo do template (após a linha do extends), carregue a tag:
  {% load consent_tags %}

- Troque o bloco dos botões por:
----------------------------------------------------------------
<div class="actions">
  {% if request.user|consentimento_ativo %}
    <a class="btn" href="{% url 'vocacional:avaliacao_form' %}">Iniciar / Continuar Avaliação</a>
    {% if ultima and ultima.status == 'concluida' %}
      <a class="btn btn-secondary" href="{% url 'vocacional:resultado' ultima.pk %}">Ver último resultado</a>
    {% endif %}
  {% else %}
    <a class="btn" href="{% url 'vocacional:consentimento_check' %}">Consentimento & Acesso</a>
  {% endif %}
  {% if request.user.perfil in 'MENTOR,PROF,ADMIN' %}
    <a class="btn" href="{% url 'vocacional:mentor_dashboard' %}">Painel do Mentor</a>
  {% endif %}
</div>
----------------------------------------------------------------

PASSO 5 — Proteger as views do fluxo
No apps/vocacional/views.py importe e aplique o decorator:
----------------------------------------------------------------
from .permissions import require_consent  # importar

@require_consent
def avaliacao_form(request):
    ...

@require_consent
def resultado(request, pk):
    ...
----------------------------------------------------------------

PASSO 6 — Migrações
Rode:
  python manage.py makemigrations vocacional
  python manage.py migrate

Pronto. O Vocacional agora exige consentimento LGPD antes de iniciar a avaliação, oferece página de privacidade com revogação e mantém base para Sessão Guiada via modelo Progresso.
