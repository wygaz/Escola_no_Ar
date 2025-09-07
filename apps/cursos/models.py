from django.db import models
from django.conf import settings

class Curso(models.Model):
    titulo = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.titulo

class Classe(models.Model):
    nome = models.CharField(max_length=120)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="classes")
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="classes_professor"
    )

    def __str__(self):
        return f"{self.nome} ({self.curso})"

class Matricula(models.Model):
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matriculas"
    )
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.aluno} → {self.classe}"
