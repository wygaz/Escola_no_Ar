from django.core.management.base import BaseCommand
from apps.vocacional.models import Dimensao, Pergunta, Opcao

DIMENSOES = [
    ("Interesses", "interesses", "O que você gosta de explorar/estudar/praticar."),
    ("Valores", "valores", "O que importa para você ao escolher uma carreira."),
    ("Talentos", "talentos", "Habilidades naturais que facilitam seu desempenho."),
]

PERGUNTAS = {
    "interesses": [
        ("Eu me empolgo em resolver problemas lógicos.", "likert"),
        ("Prefiro atividades ao ar livre e práticas.", "likert"),
    ],
    "valores": [
        ("É importante para mim ajudar pessoas diretamente.", "likert"),
        ("Prefiro estabilidade a risco.", "likert"),
        # Exemplo single com opções
        ("O que mais pesa na escolha de carreira?", "single", [
            ("Impacto social", 5),
            ("Remuneração", 5),
            ("Estabilidade", 5),
            ("Prestígio", 5),
        ]),
    ],
    "talentos": [
        ("Tenho facilidade com comunicação oral.", "likert"),
        ("Aprendo ferramentas digitais rapidamente.", "likert"),
    ],
}

class Command(BaseCommand):
    help = "Cria dimensões e perguntas de exemplo para o módulo Vocacional (idempotente)."

    def handle(self, *args, **kwargs):
        dim_criadas = 0
        pergs_criadas = 0
        opcoes_criadas = 0

        for nome, slug, desc in DIMENSOES:
            dim, _ = Dimensao.objects.get_or_create(
                slug=slug,
                defaults={"nome": nome, "descricao": desc, "peso": 1},
            )
            dim_criadas += 1

            itens = PERGUNTAS.get(slug, [])
            ordem = 0
            for item in itens:
                ordem += 1
                if len(item) == 2:
                    enunciado, tipo = item
                    opcoes = None
                else:
                    enunciado, tipo, opcoes = item

                p, created = dim.perguntas.get_or_create(
                    ordem=ordem,
                    defaults={"enunciado": enunciado, "tipo": tipo, "ativo": True},
                )
                if created:
                    pergs_criadas += 1

                # Se for single, cria opções de exemplo
                if tipo == "single" and opcoes:
                    for i, (label, valor) in enumerate(opcoes, start=1):
                        _, c = Opcao.objects.get_or_create(
                            pergunta=p, ordem=i,
                            defaults={"label": label, "valor": valor},
                        )
                        if c:
                            opcoes_criadas += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed Vocacional ok: dimensões={dim_criadas}, perguntas novas={pergs_criadas}, opções novas={opcoes_criadas}"
        ))
