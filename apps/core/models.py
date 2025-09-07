# core/models.py
from django.db import models
from django.conf import settings

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
