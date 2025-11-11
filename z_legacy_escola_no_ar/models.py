from django.db import models
from django.conf import settings
from .models_auxiliares import NivelEvolucao


# Curso e Estrutura
class Curso(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    titulo = models.CharField(max_length=100)
    versao = models.CharField(max_length=10)  # ex: 2025_JUN
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} ({self.versao})"


class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    ordem = models.IntegerField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} - {self.curso.codigo}"


class Aula(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    conteudo = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} (Módulo {self.modulo.ordem})"


# Turma e Matrícula
class Turma(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=12, unique=True)
    ano = models.IntegerField()
    mes = models.IntegerField()
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"
class Matricula(models.Model):
    class Papel(models.TextChoices):
        ALUNO = "aluno", "Aluno"
        PROFESSOR = "professor", "Professor"
        AUTOR = "autor", "Autor"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matriculas",
    )
    turma = models.ForeignKey(
        "Turma",  # se estiver em outro app: "app.Turma"
        on_delete=models.CASCADE,
        related_name="matriculas",
    )
    papel = models.CharField(max_length=20, choices=Papel.choices)
    data_matricula = models.DateTimeField(auto_now_add=True)
    pontuacao = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "turma"], name="uniq_usuario_turma"
            ),
        ]
        indexes = [
            models.Index(fields=["turma", "papel"], name="idx_turma_papel"),
        ]

    def __str__(self):
        return f"{self.usuario} em {self.turma} ({self.get_papel_display()})"

    @property
    def is_professor(self) -> bool:
        return self.papel == self.Papel.PROFESSOR

    @property
    def is_aluno(self) -> bool:
        return self.papel == self.Papel.ALUNO



# Atividades
class Atividade(models.Model):
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10)  # Ex: QUIZ, CRZ, etc.
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    prazo = models.DateField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


# Conteúdo didático e colaborativo
class Conteudo(models.Model):
    tipo = models.CharField(max_length=10, choices=[
        ('texto', 'Texto'),
        ('podcast', 'Podcast'),
        ('video', 'Vídeo'),
    ])
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)
    publico = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo


# Comentários com encadeamento e controle
class Comentario(models.Model):
    conteudo = models.ForeignKey(Conteudo, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField("Comentário")
    outras_infos = models.CharField("Complemento (opcional)", max_length=255, blank=True)
    data_comentario = models.DateTimeField(auto_now_add=True)
    resposta_a = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='respostas')
    curtidas = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='curtidas_comentario', blank=True)
    visivel = models.BooleanField(default=True)

    class Meta:
        ordering = ['-data_comentario']

    def __str__(self):
        return f"{self.autor.email}: {self.texto[:50]}..."


# Progresso por aula
class ProgressoAula(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    concluido = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('matricula', 'aula')


# Respostas de atividades
class RespostaAtividade(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    resposta = models.TextField()
    correta = models.BooleanField(null=True, blank=True)
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('atividade', 'matricula')


# Notificações
class Notificacao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensagem = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    lida = models.BooleanField(default=False)
    data_envio = models.DateTimeField(auto_now_add=True)


# Histórico de pontuação
class PontuacaoHistorico(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=255)
    pontos = models.IntegerField()
    data = models.DateTimeField(auto_now_add=True)
