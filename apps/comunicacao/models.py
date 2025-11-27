from django.db import models
from django.conf import settings

class Topico(models.Model):
    titulo = models.CharField(max_length=120)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="topicos")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Mensagem(models.Model):
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE, related_name="mensagens")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="mensagens")
    corpo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg de {self.autor or '—'} em {self.topico}"
