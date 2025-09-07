from django.db import models
from django.conf import settings

class Topico(models.Model):
    titulo = models.CharField(max_length=120)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

class Mensagem(models.Model):
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    corpo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
