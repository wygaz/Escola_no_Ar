from django.conf import settings
from django.db import models
from django.utils import timezone
from .models_consent import *  # Consentimento, Progresso

User = settings.AUTH_USER_MODEL

class Dimensao(models.Model):
    """Eixos do teste: Interesses, Valores, Talentos, etc."""
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    descricao = models.TextField(blank=True)
    peso = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

class Pergunta(models.Model):
    TIPO = (
        ("likert", "Likert 1–5"),
        ("single", "Escolha única"),
    )
    dimensao = models.ForeignKey(Dimensao, on_delete=models.CASCADE, related_name="perguntas")
    enunciado = models.TextField()
    ordem = models.PositiveIntegerField(default=0)
    tipo = models.CharField(max_length=10, choices=TIPO, default="likert")
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["dimensao__nome", "ordem", "id"]

    def __str__(self):
        return f"[{self.dimensao.nome}] {self.enunciado[:60]}"

class Opcao(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name="opcoes")
    label = models.CharField(max_length=120)
    valor = models.IntegerField(help_text="Pontuação desta opção para a dimensão")
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["pergunta", "ordem", "id"]
        unique_together = ("pergunta", "ordem")

    def __str__(self):
        return f"{self.label} ({self.valor})"

class Avaliacao(models.Model):
    STATUS = (
        ("rascunho", "Rascunho"),
        ("concluida", "Concluída"),
        ("cancelada", "Cancelada"),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avaliacoes_vocacionais")
    mentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="avaliacoes_mentoria")
    iniciado_em = models.DateTimeField(default=timezone.now)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="rascunho")
    ordem_ids = models.TextField(blank=True, default="")  # ids das perguntas, separados por vírgula

    class Meta:
        ordering = ["-iniciado_em"]

    def __str__(self):
        return f"Avaliação #{self.pk} de {self.usuario} ({self.get_status_display()})"

class Resposta(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name="respostas")
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    opcao = models.ForeignKey(Opcao, on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.IntegerField(default=0)

    class Meta:
        unique_together = ("avaliacao", "pergunta")
        ordering = ["pergunta__ordem", "pergunta_id"]

class Resultado(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name="resultados")
    dimensao = models.ForeignKey(Dimensao, on_delete=models.CASCADE)
    pontuacao = models.IntegerField(default=0)
    percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nivel = models.CharField(max_length=40, blank=True, help_text="Ex.: baixo, médio, alto")

    class Meta:
        unique_together = ("avaliacao", "dimensao")
        ordering = ["-pontuacao"]



# --- Avaliação do Guia (pré-requisito) ---------------------------------------
class AvaliacaoGuia(models.Model):
    STATUS = (("rascunho","Rascunho"), ("concluida","Concluída"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS, default="rascunho")
    aceite_termos = models.BooleanField(default=False)
    criado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user"], name="unique_avaliacao_guia_por_user")
        ]
        verbose_name = "Avaliação do Guia"
        verbose_name_plural = "Avaliações do Guia"
        ordering = ["-atualizado_em"]

class QuestaoGuia(models.Model):
    TIPO = (("likert","Likert 1-5"), ("texto","Texto"))
    ordem = models.PositiveIntegerField(default=1)
    enunciado = models.CharField(max_length=255)
    tipo = models.CharField(max_length=12, choices=TIPO, default="likert")
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem"]

    def __str__(self): return f"{self.ordem}. {self.enunciado}"

class RespostaGuia(models.Model):
    avaliacao = models.ForeignKey(AvaliacaoGuia, on_delete=models.CASCADE, related_name="respostas")
    questao = models.ForeignKey(QuestaoGuia, on_delete=models.CASCADE)
    valor = models.IntegerField(null=True, blank=True)  # Likert 1..5
    texto = models.TextField(blank=True, default="")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("avaliacao","questao")]
