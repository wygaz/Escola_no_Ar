from django.core.management.base import BaseCommand
from django.db import transaction
from apps.sonho_de_ser.models import Area, Estrategia
import pandas as pd

AREA_MAP = {
    "Família": "F",
    "Igreja": "I",
    "Escola": "E",
    "Amigos": "A",
    "Comunidade": "C",
    "Eu mesmo": "M",
}


class Command(BaseCommand):
    help = "Importa estratégias do XLSX v3 balanceado (aba Estrategias_v3)."

    def add_arguments(self, parser):
        parser.add_argument("xlsx_path", type=str, help="Caminho do arquivo .xlsx")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts["xlsx_path"]
        df = pd.read_excel(path, sheet_name="Estrategias_v3")

        # Garante áreas
        for nome, inic in AREA_MAP.items():
            Area.objects.get_or_create(inicial=inic, defaults={"nome": nome})

        # Importa estratégias
        criadas, atualizadas = 0, 0
        for _, r in df.iterrows():
            codigo = str(r["Código"]).strip()
            nome_area = str(r["Área"]).strip()
            nivel = str(r["Nível"]).strip()
            pontos = int(r["Pontos"]) if pd.notna(r["Pontos"]) else 5
            texto = str(r["Estratégia"]).strip()

            try:
                area = Area.objects.get(nome=nome_area)
            except Area.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Área desconhecida: {nome_area}. Pulando {codigo}.")
                )
                continue

            obj, created = Estrategia.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "area": area,
                    "nivel": nivel,
                    "pontos": pontos,
                    "texto": texto,
                    "ativo": True,
                },
            )
            criadas += int(created)
            atualizadas += int(not created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Import concluído: criadas={criadas}, atualizadas={atualizadas}"
            )
        )
