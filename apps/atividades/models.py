from django.db import models
from django.conf import settings

class Atividade(models.Model):
    titulo = models.CharField(max_length=120)

    def __str__(self):
        return self.titulo

class Submissao(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to="submissoes/", blank=True, null=True)
    nota = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} → {self.atividade}"
