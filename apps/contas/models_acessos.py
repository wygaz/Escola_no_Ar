# apps/contas/models_acessos.py
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Produto(models.Model):
    slug = models.SlugField(unique=True)        # ex.: "vocacional"
    nome = models.CharField(max_length=80)

    class Meta:
        app_label = "contas"
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self) -> str:  # type: ignore[override]
        return self.nome


class Acesso(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="acessos"
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, related_name="acessos"
    )
    origem = models.CharField(max_length=30, default="organico")  # ex.: guia_bonus
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "contas"
        # Garante no máximo 1 acesso ATIVO por user+produto
        constraints = [
            models.UniqueConstraint(
                fields=["user", "produto"],
                condition=Q(expires_at__isnull=True),
                name="uniq_acesso_ativo_por_user_produto",
            )
        ]
        indexes = [models.Index(fields=["user", "produto"])]
        verbose_name = "Acesso a Produto"
        verbose_name_plural = "Acessos a Produtos"

    @property
    def ativo(self) -> bool:
        return self.expires_at is None

    def __str__(self) -> str:  # type: ignore[override]
        status = "ativo" if self.ativo else "expirado"
        return f"{self.user} → {self.produto} ({status})"


# ---- helper para o gate de produto ----
def tem_acesso(user, produto_slug: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False

    # Aqui Acesso já está no mesmo arquivo, não precisa importar
    qs = Acesso.objects.filter(user=user, produto__slug=produto_slug)

    # Se existir expires_at no modelo, ignora acessos expirados
    if hasattr(Acesso, "expires_at"):
        qs = qs.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))

    return qs.exists()

