from django.db import models
from django.conf import settings

class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="cursos_autor")
    def __str__(self): return self.titulo

class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="modulos")
    titulo = models.CharField(max_length=200)
    ordem = models.PositiveIntegerField(default=1)
    def __str__(self): return f"{self.curso} · {self.titulo}"

class Aula(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="aulas")
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField(blank=True)
    ordem = models.PositiveIntegerField(default=1)
    disponivel = models.BooleanField(default=True)
    def __str__(self): return f"{self.modulo} · {self.titulo}"

class Turma(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="turmas")
    nome = models.CharField(max_length=120)
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="turmas_professor")
    inicio = models.DateField(null=True, blank=True)
    fim = models.DateField(null=True, blank=True)
    def __str__(self): return f"{self.nome} ({self.curso})"

class Matricula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="matriculas")
    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="matriculas")
    criado_em = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = [("turma", "aluno")]
    def __str__(self): return f"{self.aluno} @ {self.turma}"

class ProgressoAula(models.Model):
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="progresso")
    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progresso_aulas")
    concluida = models.BooleanField(default=False)
    atualizado_em = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = [("aula", "aluno")]
    def __str__(self): return f"{self.aluno} · {self.aula} · {'OK' if self.concluida else '—'}"
