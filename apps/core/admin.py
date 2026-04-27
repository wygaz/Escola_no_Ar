from django.contrib import admin
from .models import (
    GuiaPromotionalDelivery,
    Instituicao,
    InstituicaoUsuario,
    InstitutionalDemoAccess,
    IntroPresentationProgress,
    NivelEvolucao,
    PendingAccess,
)

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


@admin.register(GuiaPromotionalDelivery)
class GuiaPromotionalDeliveryAdmin(admin.ModelAdmin):
    list_display = ("recipient_email", "user", "status", "source", "sent_by", "sent_at")
    list_filter = ("status", "source", "sent_at")
    search_fields = ("recipient_email", "user__email")
    readonly_fields = ("sent_at",)


@admin.register(InstitutionalDemoAccess)
class InstitutionalDemoAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "institution_name", "source", "granted_by", "starts_at", "expires_at", "revoked_at")
    list_filter = ("source", "starts_at", "expires_at", "revoked_at")
    search_fields = ("user__email", "institution_name")
    readonly_fields = ("starts_at",)


@admin.register(IntroPresentationProgress)
class IntroPresentationProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "completed_at")
    search_fields = ("user__email",)
    readonly_fields = ("completed_at",)


class InstituicaoUsuarioInline(admin.TabularInline):
    model = InstituicaoUsuario
    extra = 0
    autocomplete_fields = ("usuario",)


@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "cidade", "estado", "email", "telefone", "ativo")
    list_filter = ("tipo", "ativo")
    search_fields = ("nome", "email", "telefone", "cidade", "estado", "documento")
    inlines = [InstituicaoUsuarioInline]


@admin.register(InstituicaoUsuario)
class InstituicaoUsuarioAdmin(admin.ModelAdmin):
    list_display = ("instituicao", "usuario", "natureza_vinculo_display", "papel", "principal", "ativo")
    list_filter = ("papel", "principal", "ativo", "instituicao__tipo")
    search_fields = ("instituicao__nome", "usuario__email", "usuario__first_name", "usuario__last_name")
    autocomplete_fields = ("instituicao", "usuario")

    @admin.display(description="Natureza")
    def natureza_vinculo_display(self, obj):
        return obj.get_natureza_vinculo_display()
