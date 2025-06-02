from django.contrib import admin
from .models import (
    Usuario, Curso, Modulo, Aula, Turma, Matricula,
    Atividade, NivelEvolucao, Conteudo, Comentario,
    ProgressoAula, RespostaAtividade, Notificacao,
    PontuacaoHistorico
)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'tipo', 'pontuacao', 'nivel')
    list_filter = ('tipo', 'nivel')
    search_fields = ('username', 'email')

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'versao', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'titulo')

@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'ordem', 'ativo')
    list_filter = ('curso',)

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'data_inicio', 'ativo')
    list_filter = ('modulo__curso', 'ativo')
    search_fields = ('titulo',)

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'ano', 'mes', 'curso', 'ativo')
    list_filter = ('curso', 'ano', 'mes', 'ativo')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'turma', 'papel', 'data_matricula', 'pontuacao')
    list_filter = ('papel', 'turma__curso')

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'aula', 'tipo', 'prazo')
    list_filter = ('tipo', 'aula__modulo__curso')
    search_fields = ('titulo',)

@admin.register(NivelEvolucao)
class NivelEvolucaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pontuacao_minima', 'pontuacao_maxima')

@admin.register(Conteudo)
class ConteudoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'autor', 'data_publicacao', 'publico')
    list_filter = ('tipo', 'publico')
    search_fields = ('titulo', 'descricao')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'conteudo', 'data_comentario', 'visivel')
    list_filter = ('visivel', 'data_comentario')
    search_fields = ('texto',)

@admin.register(ProgressoAula)
class ProgressoAulaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'aula', 'concluido', 'data_conclusao')
    list_filter = ('concluido',)

@admin.register(RespostaAtividade)
class RespostaAtividadeAdmin(admin.ModelAdmin):
    list_display = ('atividade', 'matricula', 'correta', 'data_resposta')
    list_filter = ('correta',)

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensagem', 'lida', 'data_envio')
    list_filter = ('lida',)

@admin.register(PontuacaoHistorico)
class PontuacaoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'descricao', 'pontos', 'data')
    list_filter = ('data',)
