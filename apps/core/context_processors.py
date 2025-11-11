# apps/core/context_processors.py
from .capabilities import get_caps, has_cap


def ui(request):
    user = request.user
    nav_items = []
    if user.is_authenticated:
        perfil = getattr(user, "perfil", "USER")
        # comuns
        nav_items.append({"label": "Portal", "href": "/portal/"})
        # por papel
        if perfil == "ADMIN":
            nav_items += [
            {"label": "Administração", "href": "/admin/"},
            {"label": "Relatórios", "href": "/relatorios/"},
            ]
        if perfil in {"PROF"}:
            nav_items += [
            {"label": "Meus Cursos", "href": "/cursos/"},
            {"label": "Minhas Turmas", "href": "/turmas/"},
            {"label": "Avaliações", "href": "/avaliacoes/"},
            ]
        if perfil in {"MENTOR", "PROF", "ADMIN"}:
            nav_items += [
            {"label": "Mentorias", "href": "/mentorias/"},
            {"label": "Projeto 21 (Mentor)", "href": "/projeto21/mentor/"},
            {"label": "Vocacional (Mentor)", "href": "/vocacional/mentor/"},
            ]
        # produtos (gated)
        if has_cap(user, "p21", level="starter"):
            nav_items.append({"label": "Projeto 21", "href": "/projeto21/"})
        if has_cap(user, "vocacional", level="starter"):
            nav_items.append({"label": "Vocacional", "href": "/vocacional/"})
    return {
        "nav_items": nav_items,
        "caps": get_caps(user) if user.is_authenticated else None,
}