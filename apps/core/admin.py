from django.contrib import admin
from .models import NivelEvolucao
from .models import PendingAccess

''' Comentado para ativar apenas o mínimo
@admin.register(NivelEvolucao)
class NivelEvolucaoAdmin(admin.ModelAdmin):
    list_display = ("nome_do_nivel", "pontuacao_minima", "ordem")
    search_fields = ("nome_do_nivel",)
    ordering = ("ordem",)
'''

@admin.register(NivelEvolucao)
class NivelEvolucaoAdmin(admin.ModelAdmin):
    # use apenas o que com certeza existe
    list_display = ("id", "__str__")
    # nada de ordering/list_filter em SAFE MODE

@admin.register(PendingAccess)
class PendingAccessAdmin(admin.ModelAdmin):
    list_display = ("email", "produto_slug", "origem", "created_at", "processed_at")
    list_filter = ("produto_slug", "origem", "processed_at")
    search_fields = ("email",)
    readonly_fields = ("created_at", "processed_at")