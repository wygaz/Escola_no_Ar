from django.contrib import admin
from .models import (
    Area,
    Estrategia,
    RegistroDiario,
    MentorProfile,
    Mentoria,
    AnotacaoMentor,
    Plano,
    PlanoItem,
)

# ---------------------------
# Projeto 21
# ---------------------------
class PlanoItemInline(admin.TabularInline):
    model = PlanoItem
    extra = 0

@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "ativo", "criado_em")
    list_filter = ("ativo",)
    search_fields = ("usuario__email", "usuario__first_name", "usuario__last_name")
    inlines = [PlanoItemInline]

# ---------------------------
# Core – Área / Estratégia / Registro
# ---------------------------
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)

@admin.register(Estrategia)
class EstrategiaAdmin(admin.ModelAdmin):
    @admin.display(description="Ativa", boolean=True)
    def is_ativa(self, obj):
        return bool(getattr(obj, "ativo", True))
    list_display = ("id", "__str__", "is_ativa")

@admin.register(RegistroDiario)
class RegistroDiarioAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "data", "estrategia")
    list_filter = ("data",)
    search_fields = ("usuario__email",)

# ---------------------------
# Mentoria
# ---------------------------
@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario")
    search_fields = ("usuario__email",)

@admin.register(Mentoria)
class MentoriaAdmin(admin.ModelAdmin):
    @admin.display(description="Criado em")
    def criado(self, obj):
        return getattr(obj, "criado_em", getattr(obj, "created_at", None))

    @admin.display(description="Encerrado em")
    def encerrado(self, obj):
        # no seu modelo há 'revogada_em'; se for outro nome (encerrada_em), também cobre
        return getattr(obj, "revogada_em", getattr(obj, "encerrada_em", None))

    list_display = ("id", "mentor", "mentorado", "status", "escopo", "criado", "encerrado")
    list_filter = ("status", "escopo")
    search_fields = ("mentor__email", "mentorado__email")

@admin.register(AnotacaoMentor)
class AnotacaoMentorAdmin(admin.ModelAdmin):
    @admin.display(boolean=True, description="Visível p/ aluno")
    def visivel(self, obj):
        return getattr(obj, "visivel_para_aluno", False)

    @admin.display(description="Criado em")
    def criado(self, obj):
        return getattr(obj, "created_at", getattr(obj, "criado_em", None))

    list_display = ("id", "mentoria", "criado", "visivel")
    list_filter = ("visivel_para_aluno", "data")
    search_fields = (
        "texto",
        "mentoria__mentor__email",
        "mentoria__mentorado__email",
    )
