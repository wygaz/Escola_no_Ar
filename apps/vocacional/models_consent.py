from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Consentimento(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    aceito_em = models.DateTimeField(default=timezone.now)
    revogado_em = models.DateTimeField(null=True, blank=True)
    aceito = models.BooleanField(default=True)

    class Meta:
        ordering = ["-aceito_em"]
        verbose_name = "Consentimento"
        verbose_name_plural = "Consentimentos"

    def __str__(self):
        return f"{self.user} — {self.email} ({'aceito' if self.aceito else 'revogado'})"

    def revogar(self):
        if self.aceito:
            self.aceito = False
            self.revogado_em = timezone.now()
            self.save()


class Progresso(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    etapa = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Progresso"
        verbose_name_plural = "Progressos"
        ordering = ["-atualizado_em"]

    def __str__(self):
        return f"{self.user} — {self.etapa}"
