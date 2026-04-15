from django.conf import settings
from django.db import models
from django.utils import timezone

from .models_consent import *  # Consentimento, Progresso

User = settings.AUTH_USER_MODEL
class Dimensao(models.Model):
    """Eixos do teste: Interesses, Valores, Talentos, etc."""

    nome = models.CharField(max_length=100, unique=True)

    # Código estável (ex.: DEV_IA). Facilita import idempotente.
    # (Útil quando você expandir o banco para 600+ itens.)
    codigo = models.CharField(max_length=40, unique=True, null=True, blank=True)

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
    # Código estável (ex.: DEVIA_01). Facilita import idempotente e rastreio.
    codigo = models.CharField(max_length=40, unique=True, null=True, blank=True)
    enunciado = models.TextField()
    ordem = models.PositiveIntegerField(default=0)
    tipo = models.CharField(max_length=10, choices=TIPO, default="likert")
    ativo = models.BooleanField(default=True)
    # Itens invertidos (Likert): 1↔5, 2↔4.
    invert = models.BooleanField(default=False)
    # Bloco/subescala (para cobertura futura e seleção por cluster)
    bloco = models.CharField(max_length=40, blank=True, default="")

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

    FLUXO = (
        ("bonus75", "Bônus 75"),
        ("ref", "Refinamento"),
    )
    fluxo = models.CharField(max_length=12, choices=FLUXO, default="bonus75", db_index=True)


    ordem_ids = models.TextField(blank=True, default="")  # ids das perguntas, separados por vírgula
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    whatsapp_enviado_em = models.DateTimeField(null=True, blank=True)

    # Refinamento Top 3 (Passe 1/2/3)
    passe_atual = models.PositiveSmallIntegerField(default=1)
    ref_data = models.JSONField(default=dict, blank=True)

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
    STATUS = (("rascunho", "Rascunho"), ("concluida", "Concluída"))
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
    TIPO = (
        ("radio", "Radio"),
        ("multi", "Múltipla escolha"),
        ("likert", "Likert 1-5"),
        ("texto", "Texto"),
        ("nota10", "Nota 0-10"),
        ("nps", "NPS 0-10"),
    )
    ordem = models.PositiveIntegerField(default=1)
    enunciado = models.CharField(max_length=255)
    tipo = models.CharField(max_length=12, choices=TIPO, default="likert")
    ativo = models.BooleanField(default=True)
    codigo = models.CharField(max_length=60, unique=True)
    opcoes = models.JSONField(default=list, blank=True)
    obrigatoria = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem"]

    def __str__(self):
        return f"{self.ordem}. {self.enunciado}"


class RespostaGuia(models.Model):
    avaliacao = models.ForeignKey(AvaliacaoGuia, on_delete=models.CASCADE, related_name="respostas")
    questao = models.ForeignKey(QuestaoGuia, on_delete=models.CASCADE)
    valor = models.IntegerField(null=True, blank=True)  # Likert 1..5
    texto = models.TextField(blank=True, default="")
    multi = models.JSONField(default=list, blank=True)      # <- FALTAVA (para multi)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("avaliacao", "questao")]

