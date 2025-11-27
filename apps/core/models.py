# core/models.py
from django.db import models
from django.conf import settings
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
