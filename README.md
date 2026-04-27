# Pacote de documentos para Codex

Este repositório mantém um acervo local de apoio para contextualização de
agentes e continuidade de trabalho arquitetural no projeto Django
`escola_no_ar_site`.

O foco principal desse acervo é:

- `Vocacional`
- `Sonhe + Alto / Projeto21`
- organização do `core` como centro da navegação de produtos e orquestrador de
  fluxo

## Estrutura atual do acervo

### Arquivos de orientação principal

- `AGENTS.md`
- `README.md`

### Documentação histórica organizada por data

- `Apenas_Local/Codex/Docs/indice.md`
- `Apenas_Local/Codex/Docs/YYYY-MM-DD/`

Esse acervo contém:

- visão geral e arquitetura-alvo;
- planejamento de fases;
- relatórios de diagnóstico e retomada;
- decisões semânticas de gating e fluxo;
- checkpoints históricos do trabalho diário;
- snapshots do painel de pendências;
- consolidações de estado atual.

### Evidências visuais organizadas por data

- `Apenas_Local/Codex/Telas_testadas/indice.md`
- `Apenas_Local/Codex/Telas_testadas/YYYY-MM-DD/`

Esse acervo contém:

- telas testadas;
- sintomas observados;
- evidências de erro;
- comparações antes/depois;
- capturas de apoio à validação funcional.

## Arquivos-base mais importantes

Para iniciar a leitura do contexto arquitetural, priorizar:

- `AGENTS.md`
- `Apenas_Local/Codex/Docs/indice.md`
- `Apenas_Local/Codex/Telas_testadas/indice.md`
- `Apenas_Local/Codex/Docs/2026-03-17/00_visao_geral.md`
- `Apenas_Local/Codex/Docs/2026-03-17/01_objetivo_da_reforma.md`
- `Apenas_Local/Codex/Docs/2026-03-17/02_arquitetura_alvo.md`
- `Apenas_Local/Codex/Docs/2026-03-17/03_mapa_de_produtos_e_fluxos.md`
- `Apenas_Local/Codex/Docs/2026-03-17/04_governanca_dashboard.md`
- `Apenas_Local/Codex/Docs/2026-03-17/05_plano_fase_1.md`
- `Apenas_Local/Codex/Docs/2026-04-26/02_situacao_atual_2026-04-26.md`

## Ordem recomendada de uso

1. Ler `AGENTS.md`.
2. Ler `Apenas_Local/Codex/Docs/indice.md`.
3. Ler `Apenas_Local/Codex/Telas_testadas/indice.md`.
4. Abrir primeiro os documentos-base de `2026-03-17`.
5. Em seguida, consultar os checkpoints mais recentes, começando por
   `2026-04-26`.
6. Usar as telas testadas da mesma data como evidência complementar do contexto.
7. Só depois propor diagnóstico, plano ou implementação.

## Observação importante

Os documentos não estão mais centralizados em `docs/arquitetura/` como pacote
único de leitura corrente. Esse diretório deixou de ser o centro do acervo
histórico textual e visual.

O acervo ativo de contextualização para agentes passa a ser:

- `Apenas_Local/Codex/Docs`
- `Apenas_Local/Codex/Telas_testadas`

com classificação por data e índices próprios para retomada.
