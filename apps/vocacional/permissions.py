from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models_consent import Consentimento
from .models import AvaliacaoGuia

MENTOR_PERFIS = {"MENTOR", "PROF", "ADMIN"}

def require_mentor(view):
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        perfil = getattr(user, "perfil", None)
        if perfil in MENTOR_PERFIS:
            return view(request, *args, **kwargs)
        return HttpResponseForbidden("Acesso restrito a mentores/professores/administradores.")
    return _wrapped

def require_consent(view):
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not Consentimento.objects.filter(user=user, aceito=True).exists():
            return redirect("vocacional:consentimento_check")
        return view(request, *args, **kwargs)
    return _wrapped


def require_guia_feedback(view_func):
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        ok = AvaliacaoGuia.objects.filter(user=user, status="concluida", aceite_termos=True).exists()
        if not ok:
            from django.shortcuts import redirect
            return redirect("vocacional:guia_avaliacao")
        return view_func(request, *args, **kwargs)
    return _wrapped

