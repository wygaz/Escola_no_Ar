from django.db import models

class NivelEvolucao(models.Model):
    nome = models.CharField(max_length=50)
    pontuacao_minima = models.IntegerField()
    pontuacao_maxima = models.IntegerField()

    def __str__(self):
        return self.nome
