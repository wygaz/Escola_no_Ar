# apps/contas/models_aux.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UsuarioManager  # seu manager custom


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    first_name = models.CharField("Nome", max_length=150, blank=True)
    last_name  = models.CharField("Sobrenome", max_length=150, blank=True)

    PERFIL_CHOICES = [
        ("ADMIN", "Administrador"),
        ("PROF",  "Professor"),
        ("MENTOR","Mentor/Tutor"),
        ("ALUNO", "Aluno"),
        ("USER",  "Usuário"),
    ]
    perfil = models.CharField(max_length=10, choices=PERFIL_CHOICES, default="USER")

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)   # acesso /admin
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    objects = UsuarioManager()

    def __str__(self):
        return self.email
