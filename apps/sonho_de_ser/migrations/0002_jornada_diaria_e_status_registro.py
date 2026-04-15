from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sonho_de_ser", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="JornadaDiaria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateField()),
                ("intencao_do_dia", models.TextField(blank=True)),
                ("principal_vitoria", models.TextField(blank=True)),
                ("principal_dificuldade", models.TextField(blank=True)),
                ("observacoes_gerais", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jornadas_diarias",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-data", "-id"],
            },
        ),
        migrations.AddField(
            model_name="registrodiario",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="registrodiario",
            name="jornada",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registros",
                to="sonho_de_ser.jornadadiaria",
            ),
        ),
        migrations.AddField(
            model_name="registrodiario",
            name="observacao",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="registrodiario",
            name="status",
            field=models.CharField(
                choices=[("NAO_FIZ", "Nao fiz"), ("PARCIAL", "Parcial"), ("FEITO", "Feito")],
                default="FEITO",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="registrodiario",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterModelOptions(
            name="registrodiario",
            options={"ordering": ["-data", "estrategia__area__inicial", "estrategia__ordem_nivel", "id"]},
        ),
        migrations.AddConstraint(
            model_name="jornadadiaria",
            constraint=models.UniqueConstraint(fields=("usuario", "data"), name="uniq_jornada_por_usuario_data"),
        ),
    ]
