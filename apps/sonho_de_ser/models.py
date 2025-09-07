from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel

class Area(models.Model):
    """Áreas do Projeto 21 (iniciais: F, I, E, A, C, M)."""
    INICIAIS = (
        ("F", "Família"),
        ("I", "Igreja"),
        ("E", "Escola"),
        ("A", "Amigos"),
        ("C", "Comunidade"),
        ("M", "Eu mesmo"),
    )
    inicial = models.CharField(max_length=1, choices=INICIAIS, unique=True)
    nome = models.CharField(max_length=40, unique=True)


    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"

    def __str__(self) -> str:
        return self.nome


class Estrategia(TimeStampedModel):
    NIVEL_CHOICES = (
        ("B", "Básico"),
        ("D", "Desafio"),
        ("A", "Avançado"),
    )

    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="estrategias")
    titulo = models.CharField(max_length=180)
    codigo = models.SlugField(max_length=80, unique=True)
    descricao = models.TextField(blank=True)

    nivel = models.CharField(max_length=1, choices=NIVEL_CHOICES, default="B")
    ordem_nivel = models.PositiveSmallIntegerField(default=1)  # 1..N dentro do nível

    dificuldade = models.PositiveSmallIntegerField(default=1)
    pontos = models.PositiveSmallIntegerField(default=1)
    ativo = models.BooleanField(default=True)

    class Meta:
        # ordena por Área, depois Nível, depois a ordem dentro do nível
        ordering = ["area__inicial", "nivel", "ordem_nivel", "titulo"]
        constraints = [
            # evita duplicar a mesma posição no mesmo nível e área
            models.UniqueConstraint(
                fields=["area", "nivel", "ordem_nivel"],
                name="unq_area_nivel_ordem",
            ),
        ]

class RegistroDiario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registros_diarios",
        db_index=True,
    )
    data = models.DateField()
    estrategia = models.ForeignKey("sonho_de_ser.Estrategia", on_delete=models.CASCADE)
    # ...

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "data", "estrategia"],
                name="uniq_registro_por_usuario_data_estrategia",
            )
        ]

# -------- Mentoria --------
class MentorProfile(models.Model):
    ROLE = (
        ("Professor", "Professor"),
        ("Responsável", "Responsável"),
        ("Líder", "Líder religioso"),
        ("Parente", "Parente"),
        ("Outro", "Outro"),
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentor_profile",
    )
    papel = models.CharField(max_length=16, choices=ROLE)

class Mentoria(models.Model):
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentorias_como_mentor",
    )
    mentorado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentorias_recebidas",
    )

    pode_ver_registros = models.BooleanField(default=True)
    pode_criar_anotacoes = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    consentido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["mentor", "mentorado"], name="unique_mentoria_par"
            )
        ]


class AnotacaoMentor(models.Model):
    mentoria = models.ForeignKey(
        Mentoria, on_delete=models.CASCADE, related_name="anotacoes"
    )
    data = models.DateField(auto_now_add=True)
    texto = models.CharField(max_length=500)
    visivel_para_aluno = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
