from django.contrib import admin
from .models import Area, Estrategia

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome")
    search_fields = ("codigo", "nome")

@admin.register(Estrategia)
class EstrategiaAdmin(admin.ModelAdmin):
    list_display = (
        "id_sig", "area", "dimensao", "freq_codigo", "periodo_codigo",
        "peso", "ordem_area", "ordem_dimensao", "ordem_estrategia", "ativo"
    )
    list_filter = ("area", "dimensao", "freq_codigo", "periodo_codigo", "ativo")
    search_fields = ("id_sig", "estrategia", "frequencia", "periodo")
