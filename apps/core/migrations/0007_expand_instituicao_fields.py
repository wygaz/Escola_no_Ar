from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_instituicao_instituicaousuario"),
    ]

    operations = [
        migrations.AddField(
            model_name="instituicao",
            name="bairro",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="instituicao",
            name="cep",
            field=models.CharField(blank=True, default="", max_length=12),
        ),
        migrations.AddField(
            model_name="instituicao",
            name="cidade",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="instituicao",
            name="complemento",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="instituicao",
            name="documento",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.AddField(
            model_name="instituicao",
            name="endereco",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="instituicao",
            name="estado",
            field=models.CharField(blank=True, default="", max_length=2),
        ),
    ]
