from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email, first_name="", last_name="", senha=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório")
        email = self.normalize_email(email)
        usuario = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        usuario.set_password(senha)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, first_name="", last_name="", senha=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, first_name, last_name, senha, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    # novos campos separados
    first_name = models.CharField("Nome", max_length=150, blank=True)
    last_name  = models.CharField("Sobrenome", max_length=150, blank=True)

    # LEGADO: mantém o 'nome' para não quebrar formulários/temas antigos
    nome = models.CharField("Nome completo", max_length=255, blank=True)

    cep = models.CharField(max_length=8, blank=True, null=True)
    numero_endereco = models.CharField(max_length=5, blank=True, null=True)

    pontuacao = models.IntegerField(default=0)

    nivel_evolucao = models.ForeignKey(
        "core.NivelEvolucao",   # <- referência por app_label.Model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    imagem = models.ImageField(upload_to="profiles/", null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        full = self.get_full_name()
        return full or self.email

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full

    def get_short_name(self):
        return (self.first_name or "").strip()

    def save(self, *args, **kwargs):
        # Preenche 'nome' automaticamente se estiver vazio
        if not self.nome:
            full = self.get_full_name()
            if full:
                self.nome = full
        super().save(*args, **kwargs)

