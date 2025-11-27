from django.contrib import admin
from .models import Dimensao, Pergunta, Opcao, Avaliacao, Resposta, Resultado, AvaliacaoGuia, QuestaoGuia, RespostaGuia


class OpcaoInline(admin.TabularInline):
    model = Opcao
    extra = 0

@admin.register(Dimensao)
class DimensaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "peso")
    prepopulated_fields = {"slug": ("nome",)}

@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ("enunciado", "dimensao", "ordem", "tipo", "ativo")
    list_filter = ("dimensao", "ativo", "tipo")
    inlines = [OpcaoInline]

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "status", "iniciado_em", "finalizado_em",
                    "email_enviado_em", "whatsapp_enviado_em")
    list_filter = ("status",)
    search_fields = ("usuario__email", "usuario__first_name", "usuario__last_name")
    readonly_fields = ("email_enviado_em", "whatsapp_enviado_em")
@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ("avaliacao", "pergunta", "opcao", "valor")

@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = ("avaliacao", "dimensao", "pontuacao", "percentual", "nivel")

class RespostaGuiaInline(admin.TabularInline):
    model = RespostaGuia
    extra = 0
    fields = ("questao", "valor", "texto", "atualizado_em")
    readonly_fields = ("atualizado_em",)
    autocomplete_fields = ("questao",)

@admin.register(AvaliacaoGuia)
class AvaliacaoGuiaAdmin(admin.ModelAdmin):
    list_display = ("id","user","status","aceite_termos","criado_em","atualizado_em")
    list_filter = ("status","aceite_termos")
    search_fields = ("user__email","user__first_name","user__last_name")
    inlines = [RespostaGuiaInline]  # <- aqui vai a CLASSE inline, não o modelo

@admin.register(QuestaoGuia)
class QuestaoGuiaAdmin(admin.ModelAdmin):
    list_display = ("ordem","tipo","ativo","enunciado")
    list_filter = ("tipo","ativo")
    search_fields = ("enunciado",)
    ordering = ("ordem",)

@admin.register(RespostaGuia)
class RespostaGuiaAdmin(admin.ModelAdmin):
    list_display = ("id","avaliacao","questao","valor","atualizado_em")
    list_filter = ("questao__tipo",)
    search_fields = ("avaliacao__user__email","questao__enunciado","texto")
    autocomplete_fields = ("avaliacao","questao")
