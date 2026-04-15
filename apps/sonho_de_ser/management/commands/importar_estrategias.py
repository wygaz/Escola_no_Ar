import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from unidecode import unidecode

from apps.sonho_de_ser.models import Area, Estrategia


AREA_MAP = {
    "Família": ("F", "Família"),
    "Igreja": ("I", "Igreja"),
    "Escola": ("E", "Escola"),
    "Amigos": ("A", "Amigos"),
    "Comunidade": ("C", "Comunidade"),
    "Eu mesmo": ("M", "Eu mesmo"),
}

NIVEL_MAP = {
    "Básico": "B",
    "Basico": "B",
    "Desafio": "D",
    "Avançado": "A",
    "Avancado": "A",
}


def _norm_label(value: str) -> str:
    return unidecode((value or "").strip())


class Command(BaseCommand):
    help = "Importa áreas e estratégias do Sonhe+Alto para o modelo canônico."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="Apenas_Local/zip/zip_Vocacional_01-02-2026-16h19/apps/projeto21/static/projeto21/data/estrategias.json",
            help="Arquivo JSON ou CSV de origem.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Apaga as estratégias existentes antes de importar.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        source_path = Path(options["file"])
        if not source_path.exists():
            raise CommandError(f"Arquivo não encontrado: {source_path}")

        if options["replace"]:
            Estrategia.objects.all().delete()
            Area.objects.all().delete()

        for _, (inicial, nome) in AREA_MAP.items():
            Area.objects.get_or_create(inicial=inicial, defaults={"nome": nome})

        rows = self._load_rows(source_path)

        created = 0
        updated = 0
        for row_number, row in enumerate(rows, start=2):
            area_nome = (row.get("Area") or row.get("area") or "").strip()
            nivel_nome = (row.get("Dimensao") or row.get("nivel") or "").strip()
            titulo = (row.get("Estrategia") or row.get("estrategia") or "").strip()
            codigo = (row.get("ID") or row.get("codigo") or "").strip()
            area_nome_norm = _norm_label(area_nome)
            nivel_nome_norm = _norm_label(nivel_nome)

            if not area_nome or area_nome_norm not in {_norm_label(k) for k in AREA_MAP}:
                raise CommandError(f"Linha {row_number}: área inválida: {area_nome!r}")
            if not nivel_nome or nivel_nome_norm not in {_norm_label(k) for k in NIVEL_MAP}:
                raise CommandError(f"Linha {row_number}: nível inválido: {nivel_nome!r}")
            if not titulo:
                raise CommandError(f"Linha {row_number}: estratégia vazia.")

            area_canonica = next(k for k in AREA_MAP if _norm_label(k) == area_nome_norm)
            nivel_canonico = next(k for k in NIVEL_MAP if _norm_label(k) == nivel_nome_norm)
            area_inicial, area_label = AREA_MAP[area_canonica]
            area = Area.objects.get(inicial=area_inicial)
            nivel = NIVEL_MAP[nivel_canonico]

            ordem_nivel = int(row.get("OrdemEstrategia") or row.get("ordem_estrategia") or 1)
            ordem_area = int(row.get("OrdemArea") or row.get("ordem_area") or 0)
            ordem_dimensao = int(row.get("OrdemNivel") or row.get("OrdemDimensao") or row.get("ordem_dimensao") or 0)
            pontos = max(1, int(row.get("Peso") or row.get("peso") or 1))
            frequencia = (row.get("Frequencia") or row.get("frequencia") or "").strip()
            periodo = (row.get("Periodo") or row.get("periodo") or "").strip()
            dosagem = (row.get("dosagem") or "").strip()
            objetivo_codigo = (row.get("cod_objetivo") or "").strip()
            objetivo_descricao = (row.get("desc_objetivo") or "").strip()
            descricao = "Frequência: {freq}. Período: {periodo}.".format(
                freq=frequencia or "Não informado",
                periodo=periodo or "Não informado",
            )

            if not codigo:
                codigo = slugify(f"{area_label}-{nivel_nome}-{ordem_nivel}-{titulo}")[:80]

            _, was_created = Estrategia.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "area": area,
                    "titulo": titulo,
                    "descricao": descricao,
                    "objetivo_codigo": objetivo_codigo,
                    "objetivo_descricao": objetivo_descricao,
                    "frequencia_texto": frequencia,
                    "periodo_texto": periodo,
                    "dosagem_texto": dosagem,
                    "nivel": nivel,
                    "ordem_area": ordem_area,
                    "ordem_dimensao": ordem_dimensao,
                    "ordem_nivel": ordem_nivel,
                    "dificuldade": max(1, ordem_dimensao or pontos),
                    "pontos": pontos,
                    "ativo": True,
                },
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Importação concluída: {created} criadas, {updated} atualizadas."
            )
        )

    def _load_rows(self, source_path: Path):
        if source_path.suffix.lower() == ".json":
            with source_path.open("r", encoding="utf-8-sig") as fh:
                data = json.load(fh)
            return data if isinstance(data, list) else list(data.get("items", []))

        with source_path.open("r", encoding="utf-8-sig", newline="") as fh:
            return list(csv.DictReader(fh))
