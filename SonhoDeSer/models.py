
# Create your models here.
# Projeto: Escola no Ar
# Novo App: sonho (integrado na mesma base)
# Objetivo: módulo vocacional cristão dentro do projeto principal, com identidade própria

# --- Estrutura esperada do projeto Django ---

# escola_no_ar/
# ├── escola/               # app principal (cursos, administração base)
# ├── cursos/               # app para cursos avulsos (ex: Apocalipse, finanças)
# ├── sonho/                # app vocacional "Sonho de Ser"
# ├── usuarios/             # gerenciamento unificado de usuários
# ├── templates/
# │   ├── escola/
# │   ├── cursos/
# │   └── sonho/
# ├── static/
# │   ├── escola/
# │   ├── cursos/
# │   └── sonho/
# ├── media/
# ├── manage.py
# └── settings.py

# --- App: sonho ---
# apps/sonho/
# ├── __init__.py
# ├── admin.py
# ├── apps.py
# ├── models.py
# ├── urls.py
# ├── views.py
# ├── forms.py
# ├── templates/sonho/
# │   ├── base_sonho.html
# │   ├── perfil_aluno.html
# │   ├── painel_mentor.html
# │   ├── painel_escola.html
# │   ├── desafio_dia.html
# │   └── feed_comunidade.html
# ├── static/sonho/
# │   ├── css/sonho.css
# │   └── js/sonho.js
# └── migrations/

# --- Modelos (models.py) ---

from django.db import models
from django.conf import settings

class Escola(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)

    def __str__(self):
        return self.nome

class Perfil(models.Model):
    TIPO_USUARIO = [
        ("aluno", "Aluno"),
        ("mentor", "Mentor"),
        ("admin", "Admin Escolar"),
    ]
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_sonhodeser"  # opcional, mas recomendado
)
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO)
    escola = models.ForeignKey(Escola, on_delete=models.SET_NULL, null=True, blank=True)
    trilha_atual = models.ForeignKey('Trilha', on_delete=models.SET_NULL, null=True, blank=True)
    progresso = models.IntegerField(default=0)

class Trilha(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()

    def __str__(self):
        return self.nome

class Desafio(models.Model):
    trilha = models.ForeignKey(Trilha, on_delete=models.CASCADE)
    ordem = models.PositiveIntegerField()
    titulo = models.CharField(max_length=100)
    texto = models.TextField()
    versiculo = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['ordem']

class RegistroDiario(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    desafio = models.ForeignKey(Desafio, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    resposta_texto = models.TextField(blank=True)
    resposta_audio = models.FileField(upload_to='audios/', blank=True, null=True)
    resposta_imagem = models.ImageField(upload_to='imagens/', blank=True, null=True)

class Selo(models.Model):
    nome = models.CharField(max_length=50)
    icone = models.CharField(max_length=100)
    descricao = models.TextField()

class SeloConquistado(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    selo = models.ForeignKey(Selo, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)

class Postagem(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    texto = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='postagens/', blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)

class Reacao(models.Model):
    post = models.ForeignKey(Postagem, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)

class RelacaoMentorAluno(models.Model):
    mentor = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='mentor_mentees')
    aluno = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='aluno_mentores')
