from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contas", "0002_ajuste_usuario"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="email_confirmado_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
