from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, NivelEvolucao, Aluno, Professor, Autor

class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'nome', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'nome', 'senha')}),
        ('Informações pessoais', {'fields': ('pais', 'estado', 'cidade', 'profissao', 'cargo_igreja', 'pontuacao', 'nivel_evolucao')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'senha1', 'senha2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(NivelEvolucao)
admin.site.register(Aluno)
admin.site.register(Professor)
admin.site.register(Autor)
