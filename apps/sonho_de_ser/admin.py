''' Desativando este para ativar apenas o mínimo

from django.contrib import admin
from .models import MentorProfile, Mentoria, AnotacaoMentor, Area, Estrategia, RegistroDiario

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ("usuario", "telefone", "ativo", "criado_em")
    search_fields = ("usuario__email", "usuario__first_name", "usuario__last_name")
    list_filter = ("ativo",)

@admin.register(Mentoria)
class MentoriaAdmin(admin.ModelAdmin):
    list_display = ("mentor", "aluno", "status", "inicio", "fim")
    list_filter = ("status",)
    search_fields = ("mentor__usuario__email", "aluno__email")

@admin.register(AnotacaoMentor)
class AnotacaoMentorAdmin(admin.ModelAdmin):
    list_display = ("mentoria", "autor", "visibilidade", "data")
    list_filter = ("visibilidade",)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "ordem", "criado_em")
    search_fields = ("nome", "codigo")
    ordering = ("ordem",)

@admin.register(Estrategia)
class EstrategiaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "codigo", "area", "ordem", "pontos", "ativo")
    list_filter = ("area", "ativo")
    search_fields = ("titulo", "codigo")

@admin.register(RegistroDiario)
class RegistroDiarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "estrategia", "data", "concluido", "nota")
    list_filter = ("concluido", "data")
    search_fields = ("usuario__email", "estrategia__titulo", "estrategia__codigo")
'''

from django.contrib import admin
from .models import Area, Estrategia, MentorProfile, Mentoria, RegistroDiario, AnotacaoMentor

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")

@admin.register(Estrategia)
class EstrategiaAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")

@admin.register(Mentoria)
class MentoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")

@admin.register(RegistroDiario)
class RegistroDiarioAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")

@admin.register(AnotacaoMentor)
class AnotacaoMentorAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")
