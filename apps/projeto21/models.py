from django.db import models
from django.core.validators import RegexValidator

class Area(models.Model):
    nome = models.CharField(max_length=60, unique=True)
    codigo = models.CharField(max_length=2, unique=True)

    class Meta:
        ordering = ("codigo",)

    def __str__(self):
        return f"{self.codigo} — {self.nome}"


class Estrategia(models.Model):
    DIMENSOES = (
        ("Básico", "Básico"),
        ("Desafio", "Desafio"),
        ("Avançado", "Avançado"),
    )

    id_sig = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z][a-z][BDA]\d{3}-[13]\w\d{2}[sd]$",
                message="ID deve seguir o padrão FaB001-1d21d, IgD001-3s03s etc."
            )
        ]
    )

    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="estrategias")
    dimensao = models.CharField(max_length=10, choices=DIMENSOES)

    estrategia = models.TextField()

    frequencia = models.CharField(max_length=30)
    periodo = models.CharField(max_length=30)

    freq_codigo = models.CharField(max_length=3)
    periodo_codigo = models.CharField(max_length=4)

    peso = models.PositiveSmallIntegerField(default=1)
    ordem_area = models.PositiveSmallIntegerField(default=0)
    ordem_dimensao = models.PositiveSmallIntegerField(default=0)
    ordem_estrategia = models.PositiveSmallIntegerField(default=0)

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("ordem_area", "ordem_dimensao", "ordem_estrategia")

    def __str__(self):
        return f"{self.id_sig} — {self.estrategia[:60]}"
