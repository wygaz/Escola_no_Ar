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
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Consentimento"
        verbose_name_plural = "Consentimentos"
        ordering = ["-aceito_em"]

    def __str__(self):
        return f"{self.user} — {self.email} ({'ativo' if self.ativo else 'revogado'})"

    def revogar(self):
        if self.ativo:
            self.ativo = False
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
