# core/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

# Reaproveita seu nível de evolução (pode mover daqui se preferir manter em 'contas')
class NivelEvolucao(models.Model):
    nome_do_nivel = models.CharField(max_length=255)
    pontuacao_minima = models.IntegerField()
    pontuacao_maxima = models.IntegerField()
    def __str__(self): return self.nome_do_nivel

class GamificadoProfile(TimeStampedModel):
    """
    Perfil abstrato que adiciona pontuação e nível de evolução a qualquer app.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)s"
    )
    pontuacao = models.IntegerField(default=0)
    nivel_evolucao = models.ForeignKey(
        NivelEvolucao, on_delete=models.SET_NULL, null=True, blank=True
    )
    class Meta:
        abstract = True

# apps/core/models.py
from django.db import models
from django.utils import timezone

class PendingAccess(models.Model):
    email = models.EmailField(db_index=True)
    produto_slug = models.SlugField(db_index=True)
    origem = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Acesso pendente"
        verbose_name_plural = "Acessos pendentes"
        indexes = [
            models.Index(fields=["email", "produto_slug"]),
        ]

    def __str__(self):
        status = "processado" if self.processed_at else "pendente"
        return f"{self.email} -> {self.produto_slug} ({status})"

    def marcar_processado(self):
        self.processed_at = timezone.now()
        self.save(update_fields=["processed_at"])


def claim_pending_access(user):
    """
    Concilia todos os PendingAccess do e-mail do usuário,
    concedendo Acesso (Produto/Acesso) e marcando como processados.
    """
    from django.db import transaction
    from apps.contas.models_acessos import Produto, Acesso

    pendings = list(PendingAccess.objects.filter(email__iexact=user.email, processed_at__isnull=True))
    if not pendings:
        return 0

    with transaction.atomic():
        count = 0
        for p in pendings:
            produto, _ = Produto.objects.get_or_create(
                slug=p.produto_slug, defaults={"nome": p.produto_slug.replace("_", " ").title()}
            )
            Acesso.objects.get_or_create(user=user, produto=produto, defaults={"origem": p.origem or "pending"})
            p.marcar_processado()
            count += 1
    return count


class GuiaPromotionalDelivery(models.Model):
    STATUS = (
        ("sent", "Enviado"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guia_promotional_deliveries",
    )
    recipient_email = models.EmailField()
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guia_promotional_deliveries_sent",
    )
    source = models.CharField(max_length=50, default="governanca_promocional")
    status = models.CharField(max_length=20, choices=STATUS, default="sent")
    sent_at = models.DateTimeField(default=timezone.now, db_index=True)
    attachment_name = models.CharField(max_length=255, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Envio promocional do Guia"
        verbose_name_plural = "Envios promocionais do Guia"
        ordering = ["-sent_at", "-id"]

    def __str__(self):
        return f"{self.recipient_email} - {self.get_status_display()} em {self.sent_at:%d/%m/%Y %H:%M}"


class InstitutionalDemoAccess(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="institutional_demo_accesses",
    )
    institution_name = models.CharField(max_length=255, blank=True, default="")
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="institutional_demo_accesses_granted",
    )
    source = models.CharField(max_length=50, default="governanca_demo")
    starts_at = models.DateTimeField(default=timezone.now, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True, db_index=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Acesso demo institucional"
        verbose_name_plural = "Acessos demo institucionais"
        ordering = ["-starts_at", "-id"]

    def __str__(self):
        institution = self.institution_name or "Demo institucional"
        return f"{self.user} - {institution} ate {self.expires_at:%d/%m/%Y %H:%M}"


class IntroPresentationProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="intro_presentation_progress",
    )
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "Conclusao da apresentacao inicial"
        verbose_name_plural = "Conclusoes da apresentacao inicial"

    def __str__(self):
        status = "concluida" if self.completed_at else "pendente"
        return f"{self.user} - apresentacao {status}"

    def mark_completed(self):
        self.completed_at = timezone.now()
        self.save(update_fields=["completed_at"])


class Instituicao(TimeStampedModel):
    TIPO_CHOICES = (
        ("escola", "Escola"),
        ("igreja", "Igreja"),
        ("comunidade", "Comunidade"),
        ("organizacao", "Organizacao"),
        ("outro", "Outro"),
    )

    nome = models.CharField(max_length=255, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="escola", db_index=True)
    logo = models.ImageField(upload_to="instituicoes/", null=True, blank=True)
    email = models.EmailField(blank=True, default="")
    telefone = models.CharField(max_length=30, blank=True, default="")
    site = models.URLField(blank=True, default="")
    documento = models.CharField(max_length=30, blank=True, default="")
    endereco = models.CharField(max_length=255, blank=True, default="")
    complemento = models.CharField(max_length=255, blank=True, default="")
    bairro = models.CharField(max_length=120, blank=True, default="")
    cidade = models.CharField(max_length=120, blank=True, default="")
    estado = models.CharField(max_length=2, blank=True, default="")
    cep = models.CharField(max_length=12, blank=True, default="")
    ativo = models.BooleanField(default=True, db_index=True)
    observacoes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Instituicao"
        verbose_name_plural = "Instituicoes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class InstituicaoUsuario(TimeStampedModel):
    PAPEL_CHOICES = (
        ("contato_institucional", "Contato administrativo/institucional"),
        ("contato_financeiro", "Contato financeiro"),
        ("contato_academico", "Contato academico"),
        ("aluno", "Aluno"),
        ("mentor", "Mentor"),
        ("funcionario", "Funcionario"),
        ("orientador", "Orientador"),
        ("membro", "Membro"),
    )

    REPRESENTACAO_PAPEIS = {
        "contato_institucional",
        "contato_financeiro",
        "contato_academico",
    }
    PARTICIPACAO_PAPEIS = {
        "aluno",
        "mentor",
        "funcionario",
        "orientador",
        "membro",
    }

    instituicao = models.ForeignKey(
        Instituicao,
        on_delete=models.CASCADE,
        related_name="vinculos_usuarios",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vinculos_institucionais",
    )
    papel = models.CharField(max_length=30, choices=PAPEL_CHOICES, default="membro", db_index=True)
    principal = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True, db_index=True)
    observacoes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Vinculo institucional"
        verbose_name_plural = "Vinculos institucionais"
        ordering = ["instituicao__nome", "papel", "usuario__email"]
        constraints = [
            models.UniqueConstraint(
                fields=["instituicao", "usuario", "papel"],
                name="uniq_instituicao_usuario_papel",
            )
        ]

    def __str__(self):
        return f"{self.instituicao} - {self.usuario} ({self.get_papel_display()})"

    @property
    def natureza_vinculo(self):
        if self.papel in self.REPRESENTACAO_PAPEIS:
            return "representacao"
        return "participacao"

    def get_natureza_vinculo_display(self):
        return "Representacao institucional" if self.natureza_vinculo == "representacao" else "Participacao institucional"
