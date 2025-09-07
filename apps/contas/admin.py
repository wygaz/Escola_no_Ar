from django.contrib import admin
from .models import Usuario  # mantenha só o que existe aqui

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name", "is_active")
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_active",)

# Se Aluno/Professor/Autor existirem em contas.models, registramos.
# Caso não existam (ou você ainda não migrou), isso não quebra o admin.
try:
    from .models import Aluno, Professor, Autor  # opcional
except Exception:
    Aluno = Professor = Autor = None

for mdl in (Aluno, Professor, Autor):
    if mdl is not None:
        admin.site.register(mdl)
