# apps/core/permissions.py
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login


def require_perfis(*perfis):
    perfis = set(perfis)
    def decorator(view):
        @wraps(view)
        def _wrapped(request, *a, **kw):
            u = request.user
            if not u.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if getattr(u, "perfil", None) in perfis:
                return view(request, *a, **kw)
            return HttpResponseForbidden("Acesso não permitido para seu perfil.")
        return _wrapped
    return decorator