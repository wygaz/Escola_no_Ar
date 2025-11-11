# apps/contas/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UsuarioManager  # use só este manager

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    first_name = models.CharField("Nome", max_length=150, blank=True)
    last_name  = models.CharField("Sobrenome", max_length=150, blank=True)
    # legado (mantém compatibilidade com telas antigas)
    nome = models.CharField("Nome completo", max_length=255, blank=True)

    cep = models.CharField(max_length=8, blank=True, null=True)
    numero_endereco = models.CharField(max_length=5, blank=True, null=True)

    pontuacao = models.IntegerField(default=0)

    nivel_evolucao = models.ForeignKey(
        "core.NivelEvolucao",
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    imagem = models.ImageField(upload_to="profiles/", null=True, blank=True)

    PERFIL_CHOICES = [
        ("ADMIN",  "Administrador"),
        ("PROF",   "Professor"),
        ("MENTOR", "Mentor/Tutor"),
        ("ALUNO",  "Aluno"),
        ("USER",   "Usuário"),
    ]
    perfil = models.CharField(
        max_length=10, choices=PERFIL_CHOICES, default="USER", db_index=True
    )

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["first_name", "last_name", "email"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["perfil"]),
        ]

    # -------- compat & conveniências --------
    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return f"{(self.first_name or '').strip()} {(self.last_name or '').strip()}".strip()

    def get_short_name(self):
        return (self.first_name or "").strip()

    @property
    def full_name(self):
        return self.get_full_name()

    def is_admin_portal(self):  # não confundir com is_superuser
        return self.perfil == "ADMIN"
    def is_professor(self): return self.perfil == "PROF"
    def is_mentor(self):    return self.perfil == "MENTOR"
    def is_aluno(self):     return self.perfil == "ALUNO"
    def is_usuario(self):   return self.perfil == "USER"

    def save(self, *args, **kwargs):
        if not self.nome:
            full = self.get_full_name()
            if full:
                self.nome = full
        if self.cep:
            only = "".join(ch for ch in str(self.cep) if ch.isdigit())
            self.cep = only[:8] if only else None
        super().save(*args, **kwargs)

from .models_acessos import Produto, Acesso  # noqa: F401
