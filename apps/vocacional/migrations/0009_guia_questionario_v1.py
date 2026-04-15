from django.db import migrations, models


def seed_guia_questionario(apps, schema_editor):
    QuestaoGuia = apps.get_model('vocacional', 'QuestaoGuia')

    # Garante códigos para questões antigas (se existirem)
    for q in QuestaoGuia.objects.filter(codigo__isnull=True):
        q.codigo = f"LEGACY_{q.id}"
        q.save(update_fields=['codigo'])

    perguntas = [
        # Seção A — Leitura e uso
        (
            'LEITURA_PERC', 1,
            'Quanto do Guia você leu?',
            'radio',
            ['0-25%', '26-50%', '51-75%', '76-100%'],
            True,
        ),
        (
            'EXERCICIOS_FEZ', 2,
            'Você fez os exercícios propostos?',
            'radio',
            ['Fiz a maioria', 'Fiz alguns', 'Não fiz', 'Não lembro'],
            True,
        ),
        (
            'TEMPO_TOTAL', 3,
            'Tempo total aproximado com o Guia',
            'radio',
            ['<30 min', '30-60 min', '1-2h', '2-4h', '4h+'],
            True,
        ),
        (
            'LEITURA_MOTIVO_NAO_CONCLUIU', 4,
            'Se você não concluiu a leitura, qual foi o motivo principal?',
            'multi',
            ['Falta de tempo', 'Achei longo', 'Achei difícil', 'Não prendeu atenção', 'Já sabia o conteúdo', 'Outro'],
            True,
        ),

        # Seção B — Qualidade (Likert 1–5)
        ('QUAL_LINGUAGEM', 5,  'A linguagem é clara e fácil de entender.', 'likert', [], True),
        ('QUAL_ORGANIZACAO', 6,'A organização (capítulos/seções) me ajudou a avançar sem me perder.', 'likert', [], True),
        ('QUAL_EXERCICIOS', 7,'Os exemplos/atividades foram úteis para refletir sobre mim.', 'likert', [], True),
        ('QUAL_APLICABILIDADE', 8,'O Guia é prático e aplicável à vida real.', 'likert', [], True),
        ('QUAL_TAMANHO', 9,'O tamanho do Guia é adequado (nem curto demais, nem longo demais).', 'likert', [], True),
        ('QUAL_VISUAL', 10,'O visual (layout/cores/imagens) ajudou na leitura.', 'likert', [], True),

        # Seção C — Aproveitamento (Antes)
        ('ANTES_TALENTOS', 11,'Antes de ler o Guia, eu tinha clareza dos meus talentos e pontos fortes.', 'likert', [], True),
        ('ANTES_VALORES', 12,'Antes de ler o Guia, eu sabia identificar valores pessoais importantes pra mim.', 'likert', [], True),
        ('ANTES_INTERESSES', 13,'Antes de ler o Guia, eu conseguia ligar interesses a possibilidades de carreira/área.', 'likert', [], True),
        ('ANTES_PLANO', 14,'Antes de ler o Guia, eu tinha um plano inicial de próximos passos.', 'likert', [], True),

        # Seção C — Aproveitamento (Depois)
        ('DEPOIS_TALENTOS', 15,'Depois de ler o Guia, eu tenho mais clareza dos meus talentos e pontos fortes.', 'likert', [], True),
        ('DEPOIS_VALORES', 16,'Depois de ler o Guia, eu identifico melhor meus valores pessoais.', 'likert', [], True),
        ('DEPOIS_INTERESSES', 17,'Depois de ler o Guia, eu consigo ligar interesses a possibilidades de carreira/área.', 'likert', [], True),
        ('DEPOIS_PLANO', 18,'Depois de ler o Guia, eu tenho um plano inicial de próximos passos.', 'likert', [], True),

        # Seção D — Nota/NPS
        ('NOTA_GERAL', 19,'Nota geral do Guia (0 a 10)', 'nota10', [], True),
        ('NPS', 20,'Você recomendaria este Guia a um amigo? (0 a 10)', 'nps', [], True),

        # Seção E — Abertas
        ('ABERTA_VALOR', 21,'O que foi mais valioso pra você?', 'texto', [], True),
        ('ABERTA_MELHORIA', 22,'O que você melhoraria primeiro?', 'texto', [], True),
        ('ABERTA_FALTA', 23,'Tem algum assunto que você esperava ver e faltou?', 'texto', [], False),
    ]

    for codigo, ordem, enunciado, tipo, opcoes, obrigatoria in perguntas:
        QuestaoGuia.objects.update_or_create(
            codigo=codigo,
            defaults={
                'ordem': ordem,
                'enunciado': enunciado,
                'tipo': tipo,
                'opcoes': opcoes,
                'obrigatoria': obrigatoria,
                'ativo': True,
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('vocacional', '0008_refinamento_campos'),
    ]

    operations = [
        migrations.AddField(
            model_name='questaoguia',
            name='codigo',
            field=models.CharField(blank=True, max_length=60, null=True, unique=True, help_text='Código estável da pergunta'),
        ),
        migrations.AddField(
            model_name='questaoguia',
            name='opcoes',
            field=models.JSONField(blank=True, default=list, help_text='Opções (para radio/multi)'),
        ),
        migrations.AddField(
            model_name='questaoguia',
            name='obrigatoria',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='respostaguia',
            name='multi',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(seed_guia_questionario, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='questaoguia',
            name='codigo',
            field=models.CharField(max_length=60, unique=True, help_text='Código estável da pergunta'),
        ),
    ]
