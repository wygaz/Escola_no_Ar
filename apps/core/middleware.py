from __future__ import annotations

import logging

from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


class ImpersonateUserMiddleware:
    """Permite que staff/superuser "teste como" um usuário real.

    - O staff continua logado.
    - Para URLs de apps (Portal/Vocacional/Projeto21), request.user é trocado
      temporariamente pelo usuário alvo (impersonado), com request.real_user
      preservado.
    - Para URLs administrativas (admin, governança, tela de escolher usuário),
      não aplicamos a troca.

    Segurança:
    - Só funciona se o usuário real for staff/superuser.
    - Se o usuário alvo não existir mais, limpa a sessão.
    """

    SESSION_KEY = "impersonate_user_id"

    # Rotas onde NÃO devemos trocar request.user
    EXCLUDE_PREFIXES = (
        "/admin/",
        "/portal/dashboard/",
        "/portal/impersonar/",
        "/contas/login",
        "/contas/logout",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Preserve sempre o usuário real.
        request.real_user = getattr(request, "user", None)
        request.impersonated_user = None

        try:
            imp_id = request.session.get(self.SESSION_KEY)
        except Exception:
            imp_id = None

        if imp_id and request.real_user and getattr(request.real_user, "is_authenticated", False):
            # Só staff/superuser pode impersonar
            if getattr(request.real_user, "is_staff", False) or getattr(request.real_user, "is_superuser", False):
                path = getattr(request, "path", "") or ""
                if not path.startswith(self.EXCLUDE_PREFIXES):
                    User = get_user_model()
                    try:
                        imp = User.objects.get(pk=imp_id)
                        request.impersonated_user = imp
                        request.user = imp
                        request.is_impersonating = True
                    except User.DoesNotExist:
                        # Se não existe mais, limpa para não quebrar o fluxo.
                        request.session.pop(self.SESSION_KEY, None)
                        request.is_impersonating = False

        return self.get_response(request)


class Debug403LoggingMiddleware:
    """Instrumenta respostas 403 para localizar rota e ponto provável do bloqueio."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if getattr(response, "status_code", None) == 403:
            match = getattr(request, "resolver_match", None)
            view_name = getattr(match, "view_name", None)
            func = getattr(match, "func", None)
            func_name = getattr(func, "__qualname__", getattr(func, "__name__", None))
            logger.warning(
                "AUTH 403 path=%r view_name=%r func=%r user=%s is_staff=%s is_superuser=%s real_user=%s portal_mode=%r impersonate_user_id=%r",
                getattr(request, "path", ""),
                view_name,
                func_name,
                getattr(getattr(request, "user", None), "email", getattr(getattr(request, "user", None), "pk", "anon")),
                getattr(getattr(request, "user", None), "is_staff", False),
                getattr(getattr(request, "user", None), "is_superuser", False),
                getattr(getattr(request, "real_user", None), "email", None),
                request.session.get("portal_mode", None),
                request.session.get("impersonate_user_id", None),
            )
        return response
