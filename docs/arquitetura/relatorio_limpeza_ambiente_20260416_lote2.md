# Relatorio de limpeza do ambiente - 2026-04-16 - lote 2

## Escopo executado

Foi tratado o diretório legado de raiz `Projeto21/`, separado do app ativo `apps/projeto21/`.

Decisão aplicada:

- considerar o diretório de raiz `Projeto21/` como material legado descartável;
- preservar uma cópia local em quarentena;
- remover do repositório apenas os arquivos rastreados desse diretório.

## Destino local

Quarentena local:

- `Apenas_Local/Doc.quarentena/2026-04-16_lote2/diretorios/Projeto21`

## Conteúdo preservado localmente

O diretório movido para quarentena contém:

- `gerar_estrategias_json.py`
- `Projeto21_COMPETENCIAS_PREENCHIDAS.xlsx`
- `Projeto21_com_frequencia_de_todas_areas_com_manual.xlsx`
- `Projeto21_com_frequencia_e_objetivos_geral.xlsx`
- `Projeto21_com_frequencia_e_objetivos_por_estrategias.xlsx`

## Conteúdo removido do Git

Arquivos rastreados removidos do repositório:

- `Projeto21/gerar_estrategias_json.py`
- `Projeto21/Projeto21_com_frequencia_de_todas_areas_com_manual.xlsx`
- `Projeto21/Projeto21_com_frequencia_e_objetivos_geral.xlsx`
- `Projeto21/Projeto21_com_frequencia_e_objetivos_por_estrategias.xlsx`

## Observação importante

Essa limpeza não toca o app Django ativo:

- `apps/projeto21/`

O impacto desta etapa recai apenas sobre o diretório legado de apoio que ficava na raiz.

## Resultado

- a raiz do projeto ficou mais limpa;
- o material legado foi preservado fora do repositório, em quarentena local;
- o histórico do Git deixa de carregar esse diretório paralelo.
