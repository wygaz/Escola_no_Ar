import json
from pathlib import Path

from django.apps import apps as djapps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Importa perguntas do Vocacional (formato: meta/dims/grupos[].itens[])."

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str, help="Caminho do arquivo JSON")
        parser.add_argument("--wipe", action="store_true",
                            help="Apaga Pergunta/Dimensao antes de importar")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = Path(opts["json_path"])
        if not path.exists():
            raise CommandError(f"Arquivo não encontrado: {path}")

        # Modelos
        Pergunta = djapps.get_model("vocacional", "Pergunta")
        try:
            Dimensao = djapps.get_model("vocacional", "Dimensao")
        except LookupError:
            Dimensao = None

        # Campos existentes nos modelos (somente concretos)
        p_fields = {f.name for f in Pergunta._meta.get_fields() if getattr(f, "concrete", False)}
        d_fields = {f.name for f in Dimensao._meta.get_fields() if getattr(f, "concrete", False)} if Dimensao else set()

        # Mapeamentos flexíveis (nome real do campo no seu modelo)
        text_field = "texto" if "texto" in p_fields else ("enunciado" if "enunciado" in p_fields else None)
        if not text_field:
            raise CommandError(f"Modelo Pergunta sem campo 'texto' ou 'enunciado' (campos: {sorted(p_fields)})")

        tipo_field   = "tipo"     if "tipo"     in p_fields else None
        ativo_field  = "ativo"    if "ativo"    in p_fields else None
        ordem_field  = "ordem"    if "ordem"    in p_fields else None
        dim_field    = "dimensao" if "dimensao" in p_fields else None
        code_field   = "codigo"   if "codigo"   in p_fields else ("slug" if "slug" in p_fields else None)

        invert_field = None
        for cand in ("invert", "inversa", "inverso", "reversa", "reverso"):
            if cand in p_fields:
                invert_field = cand
                break

        # Lê JSON
        data = json.loads(path.read_text(encoding="utf-8"))
        if not (isinstance(data, dict) and "grupos" in data):
            raise CommandError("Formato não reconhecido: esperava um dict com chave 'grupos' (e opcional 'dims').")

        grupos    = data.get("grupos") or []
        dims_info = data.get("dims")   or {}

        # Limpa antes (se pedido)
        if opts["wipe"]:
            Pergunta.objects.all().delete()
            if Dimensao:
                Dimensao.objects.all().delete()

        # Dimensões a partir de `dims`
        dim_objs = {}
        if Dimensao:
            for code, info in dims_info.items():
                nome = (info or {}).get("nome") or code
                defaults = {}
                if "peso" in d_fields and isinstance(info, dict) and "peso" in info:
                    defaults["peso"] = info["peso"]
                if "slug" in d_fields:
                    defaults["slug"] = str(code).lower()
                if "codigo" in d_fields:
                    defaults["codigo"] = code
                dim_objs[code], _ = Dimensao.objects.get_or_create(nome=nome, defaults=defaults)

        # Importa perguntas
        counters = {}  # ordem sequencial por dimensão
        total = 0

        for g in grupos:
            itens = g.get("itens") or []
            for item in itens:
                # Texto da pergunta (fallback múltiplo)
                texto = (
                    item.get("texto")
                    or item.get("enunciado")
                    or item.get("pergunta")
                    or item.get("titulo")
                    or ""
                )
                texto = str(texto).strip()
                if not texto:
                    # pula itens sem conteúdo
                    continue

                # Tipo (default likert)
                tipo = (item.get("tipo") or "likert").lower()

                # Código da dimensão no JSON (vários aliases)
                code = item.get("dim") or item.get("area") or item.get("categoria") or None

                # Resolve objeto da dimensão (se existir o modelo)
                dim_obj = None
                if Dimensao and code:
                    dim_obj = dim_objs.get(code)
                    if not dim_obj:
                        defaults = {}
                        if "slug" in d_fields:
                            defaults["slug"] = str(code).lower()
                        dim_obj, _ = Dimensao.objects.get_or_create(
                            nome=str(code), defaults=defaults
                        )
                        dim_objs[code] = dim_obj

                # Ordem sequencial por dimensão (ou geral "_")
                key = code or "_"
                counters[key] = counters.get(key, 0) + 1
                ordem = counters[key]

                # Monta defaults para a Pergunta
                obj = {text_field: texto}
                if tipo_field:
                    obj[tipo_field] = "likert" if tipo in ("likert", "escala") else tipo
                if ativo_field:
                    obj[ativo_field] = True
                if ordem_field:
                    obj[ordem_field] = ordem
                if dim_field and dim_obj:
                    obj[dim_field] = dim_obj
                if invert_field and ("invert" in item):
                    obj[invert_field] = bool(item["invert"])

                # Identificador único (se o seu modelo tiver 'codigo' ou 'slug')
                if code_field:
                    ident = item.get("code") or item.get("id") or slugify(texto)[:60]
                    _, created = Pergunta.objects.update_or_create(
                        **{code_field: ident},
                        defaults=obj,
                    )
                else:
                    Pergunta.objects.create(**obj)
                    created = True

                if created:
                    total += 1

        self.stdout.write(self.style.SUCCESS(f"Importadas {total} perguntas do arquivo {path.name}."))
