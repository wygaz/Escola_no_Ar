from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_expand_instituicao_fields"),
        ("contas", "0003_usuario_email_confirmado_em"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="instituicao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="usuarios",
                to="core.instituicao",
            ),
        ),
    ]
