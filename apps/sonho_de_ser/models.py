from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel
from django.core.exceptions import ValidationError

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
    # === Relacionamentos (mantidos) ===
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

    # === Permissões granulares (mantidas) ===
    pode_ver_registros = models.BooleanField(default=True)
    pode_criar_anotacoes = models.BooleanField(default=True)

    # === Sinalização legacy (mantida) ===
    ativo = models.BooleanField(default=True)

    # === Datas (mantidas + novas) ===
    criado_em = models.DateTimeField(auto_now_add=True)
    # OBS: 'consentido_em' existia; mantemos. Em fluxos com aceite explícito,
    # use também 'aceita_pelo_mentorado_em' (abaixo).
    consentido_em = models.DateTimeField(auto_now_add=True)

    # === NOVO: ciclo de vida ===
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("ATIVA",    "Ativa"),
        ("PAUSADA",  "Pausada"),
        ("ENCERRADA","Encerrada"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="ATIVA",
        db_index=True,
    )

    # Quando o mentorado aceitou explicitamente o vínculo (se usar convite)
    aceita_pelo_mentorado_em = models.DateTimeField(null=True, blank=True)
    # Quando o vínculo foi encerrado/revogado
    revogada_em = models.DateTimeField(null=True, blank=True)

    # Opcional: foco principal da mentoria (para filtrar dashboards)
    ESCOPO_CHOICES = [
        ("PROJ21", "Projeto 21"),
        ("VOCAC",  "Vocacional"),
        ("CURSO",  "Curso/Acadêmico"),
        ("OUTRO",  "Outro"),
    ]
    escopo = models.CharField(
        max_length=10,
        choices=ESCOPO_CHOICES,
        default="PROJ21",
        db_index=True,
    )

    # Observações gerais do vínculo (acordos, metas, etc.)
    observacoes = models.TextField(blank=True)

    class Meta:
        constraints = [
            # Mantém unicidade do par
            models.UniqueConstraint(
                fields=["mentor", "mentorado"], name="unique_mentoria_par"
            ),
        ]
        indexes = [
            models.Index(fields=["mentor", "ativo"]),
            models.Index(fields=["mentorado", "ativo"]),
            models.Index(fields=["status"]),
            models.Index(fields=["escopo"]),
        ]
        ordering = ["-ativo", "-criado_em"]

    # ====== Helpers & validações ======
    def __str__(self):
        return f"Mentoria({self.mentor} → {self.mentorado}, {self.status}, escopo={self.escopo})"

    def clean(self):
        # Impede auto-mentoria
        if self.mentor_id and self.mentorado_id and self.mentor_id == self.mentorado_id:
            raise ValidationError("Mentor e mentorado não podem ser a mesma pessoa.")

        # (Opcional) Regras por perfil — só valide se tiver os perfis configurados
        # Tenta acessar .perfil com fallback seguro
        mentor_perfil = getattr(self.mentor, "perfil", None)
        mentorado_perfil = getattr(self.mentorado, "perfil", None)

        # Se perfis existirem, aplica heurísticas leves (não bloqueia admins)
        if mentor_perfil and mentor_perfil not in {"MENTOR", "PROF", "ADMIN"} and not getattr(self.mentor, "is_superuser", False):
            raise ValidationError("O usuário definido como mentor não possui perfil de Mentor/Professor/Admin.")

        if mentorado_perfil and mentorado_perfil not in {"ALUNO", "USER"}:
            raise ValidationError("O mentorado deve ser um Aluno/Usuário.")

    @property
    def is_pendente(self):
        return self.status == "PENDENTE"

    @property
    def is_ativa(self):
        return self.status == "ATIVA" and self.ativo

    @property
    def is_encerrada(self):
        return self.status == "ENCERRADA" or bool(self.revogada_em)


class AnotacaoMentor(models.Model):
    mentoria = models.ForeignKey(
        Mentoria, on_delete=models.CASCADE, related_name="anotacoes"
    )
    data = models.DateField(auto_now_add=True)
    texto = models.CharField(max_length=500)
    visivel_para_aluno = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

# ====== Projeto 21 – Plano do aluno (compatível com seu modelo atual) ======
from django.utils import timezone

class Plano(models.Model):
    """
    Plano ativo do aluno para 21 dias (ou mais).
    Em vez de criar um modelo novo de 'Registro com itens', mantemos o seu
    RegistroDiario por estratégia e calculamos progresso usando os itens do plano.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planos_p21",
        db_index=True,
    )
    criado_em = models.DateTimeField(default=timezone.now)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-ativo", "-criado_em"]
        indexes = [
            models.Index(fields=["usuario", "ativo"]),
        ]

    def __str__(self):
        status = "ativo" if self.ativo else "inativo"
        return f"Plano #{self.pk} de {self.usuario} ({status})"

    @property
    def total_estrategias(self) -> int:
        return self.itens.filter(ativo=True).count()


class PlanoItem(models.Model):
    """
    Item do plano apontando para uma Estratégia existente.
    Mantém seu modelo de Estratégia (área, nível, pontos etc.) sem duplicar nada.
    """
    plano = models.ForeignKey(
        Plano, on_delete=models.CASCADE, related_name="itens"
    )
    estrategia = models.ForeignKey(
        "sonho_de_ser.Estrategia",
        on_delete=models.CASCADE,
        related_name="planos_incluindo",
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("plano", "estrategia")
        ordering = [
            "estrategia__area__inicial",
            "estrategia__nivel",
            "estrategia__ordem_nivel",
            "id",
        ]
        indexes = [
            models.Index(fields=["plano", "ativo"]),
            models.Index(fields=["estrategia"]),
        ]

    def __str__(self):
        return f"{self.plano_id} · {self.estrategia.titulo}"


# ====== Helpers de progresso (usam SEU RegistroDiario existente) ======

from datetime import date, timedelta

def _semana_atual_range(d: date):
    ini = d - timedelta(days=d.weekday())       # segunda
    fim = ini + timedelta(days=6)               # domingo
    return ini, fim


def progresso_do_dia(plano: Plano, quando: date) -> dict:
    """
    Calcula % do dia considerando as estratégias ATIVAS do plano.
    Usa o seu RegistroDiario (usuario, data, estrategia).
    """
    from .models import RegistroDiario  # evitar import circular

    estrategias_ids = list(
        plano.itens.filter(ativo=True).values_list("estrategia_id", flat=True)
    )
    total = len(estrategias_ids)
    if total == 0:
        return {"data": quando, "feitos": 0, "total": 0, "percentual": 0}

    feitos = (
        RegistroDiario.objects.filter(
            usuario=plano.usuario,
            data=quando,
            estrategia_id__in=estrategias_ids,
        ).count()
    )
    perc = int((feitos / total) * 100)
    return {"data": quando, "feitos": feitos, "total": total, "percentual": perc}


def progresso_da_semana(plano: Plano, hoje: date | None = None) -> dict:
    """
    Série de adesão por dia + adesão geral da semana atual.
    """
    hoje = hoje or date.today()
    ini, fim = _semana_atual_range(hoje)
    serie = []
    feitos_total, possiveis_total = 0, 0
    for i in range(7):
        dia = ini + timedelta(days=i)
        info = progresso_do_dia(plano, dia)
        serie.append({"data": dia, "percentual": info["percentual"]})
        feitos_total += info["feitos"]
        possiveis_total += info["total"]

    geral = int((feitos_total / possiveis_total) * 100) if possiveis_total else 0
    return {"serie": serie, "geral": geral}
