# apps/cursos/views_prof.py
from django.views.generic import ListView
from apps.core.mixins import GroupRequiredMixin, PerfilRequiredMixin
from .models import Curso

class CursosDoProfessorView(GroupRequiredMixin, ListView):
    template_name = "cursos/professor_list.html"
    model = Curso
    groups = ["Professores", "Admins"]  # ou use PerfilRequiredMixin com perfis=["PROF","ADMIN"]
