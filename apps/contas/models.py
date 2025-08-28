from django.db import models

# Create your models here.
# apps/contas/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class NivelEvolucao(models.Model):
    nome_do_nivel = models.CharField(max_length=255)
    pontuacao_minima = models.IntegerField()
    pontuacao_maxima = models.IntegerField()

    def __str__(self):
        return self.nome_do_nivel


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, senha=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        usuario = self.model(email=email, nome=nome, **extra_fields)
        usuario.set_password(senha)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nome, senha=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nome, senha, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    profissao = models.CharField(max_length=100, blank=True, null=True)
    cargo_igreja = models.CharField(max_length=100, blank=True, null=True)
    pontuacao = models.IntegerField(default=0)
    nivel_evolucao = models.ForeignKey(NivelEvolucao, on_delete=models.SET_NULL, null=True, blank=True)
        # Foto de perfil (opcional)
    imagem = models.ImageField(
        upload_to="profiles/",  # vai salvar em MEDIA_ROOT/profiles/
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)



    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email


class Aluno(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    outras_infos = models.CharField(max_length=255, blank=True, null=True)
    pontuacao = models.IntegerField(default=0)
    nivel_evolucao = models.ForeignKey(NivelEvolucao, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Aluno: {self.usuario.nome}"


class Professor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    outras_infos = models.CharField(max_length=255, blank=True, null=True)
    pontuacao = models.IntegerField(default=0)
    nivel_evolucao = models.ForeignKey(NivelEvolucao, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Professor: {self.usuario.nome}"


class Autor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Autor: {self.usuario.nome}"
