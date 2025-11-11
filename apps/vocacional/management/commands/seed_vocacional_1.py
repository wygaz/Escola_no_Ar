from django.core.management.base import BaseCommand
from apps.vocacional.models import Dimensao, Pergunta

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
    ],
    "talentos": [
        ("Tenho facilidade com comunicação oral.", "likert"),
        ("Aprendo ferramentas digitais rapidamente.", "likert"),
    ],
}

class Command(BaseCommand):
    help = "Cria dimensões e perguntas de exemplo para o Vocacional"

    def handle(self, *args, **kwargs):
        created = 0
        for nome, slug, desc in DIMENSOES:
            d, _ = Dimensao.objects.get_or_create(slug=slug, defaults={"nome": nome, "descricao": desc})
            perguntas = PERGUNTAS.get(slug, [])
            for i, (enunciado, tipo) in enumerate(perguntas, start=1):
                d.perguntas.get_or_create(ordem=i, defaults={"enunciado": enunciado, "tipo": tipo, "ativo": True})
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Seed do Vocacional: dimensões garantidas = {created}"))
