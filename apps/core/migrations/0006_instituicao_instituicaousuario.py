from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_intropresentationprogress"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Instituicao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("nome", models.CharField(max_length=255, unique=True)),
                ("tipo", models.CharField(choices=[("escola", "Escola"), ("igreja", "Igreja"), ("comunidade", "Comunidade"), ("organizacao", "Organizacao"), ("outro", "Outro")], db_index=True, default="escola", max_length=20)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="instituicoes/")),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("telefone", models.CharField(blank=True, default="", max_length=30)),
                ("site", models.URLField(blank=True, default="")),
                ("ativo", models.BooleanField(db_index=True, default=True)),
                ("observacoes", models.TextField(blank=True, default="")),
            ],
            options={
                "verbose_name": "Instituicao",
                "verbose_name_plural": "Instituicoes",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="InstituicaoUsuario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("papel", models.CharField(choices=[("contato_institucional", "Contato institucional"), ("contato_financeiro", "Contato financeiro"), ("contato_academico", "Contato academico"), ("orientador", "Orientador"), ("membro", "Membro")], db_index=True, default="membro", max_length=30)),
                ("principal", models.BooleanField(default=False)),
                ("ativo", models.BooleanField(db_index=True, default=True)),
                ("observacoes", models.TextField(blank=True, default="")),
                ("instituicao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vinculos_usuarios", to="core.instituicao")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vinculos_institucionais", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Vinculo institucional",
                "verbose_name_plural": "Vinculos institucionais",
                "ordering": ["instituicao__nome", "papel", "usuario__email"],
            },
        ),
        migrations.AddConstraint(
            model_name="instituicaousuario",
            constraint=models.UniqueConstraint(fields=("instituicao", "usuario", "papel"), name="uniq_instituicao_usuario_papel"),
        ),
    ]
