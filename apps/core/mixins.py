# apps/core/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class GroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    groups = []

    def test_func(self):
        u = self.request.user
        if not u.is_authenticated:
            return False
        if u.is_superuser:
            return True
        return u.groups.filter(name__in=self.groups).exists()

class PerfilRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    perfis = []  # ex.: ["ADMIN", "PROF"]

    def test_func(self):
        u = self.request.user
        if not u.is_authenticated:
            return False
        if u.is_superuser:
            return True
        perfil = getattr(u, "perfil", None)
        return perfil in self.perfis
