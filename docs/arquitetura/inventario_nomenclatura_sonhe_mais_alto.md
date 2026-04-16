# Inventário de Nomenclatura - Sonhe + Alto

## Objetivo

Mapear onde ainda aparecem os nomes históricos **Projeto 21**, **Projeto21**, **Sonho de Ser**, `projeto21` e `sonho_de_ser`, separando o que é:

- texto público a corrigir;
- nome técnico legado a preservar temporariamente;
- slug/permissão/equivalência de acesso;
- documentação histórica;
- acervo/material antigo fora do fluxo principal.

A decisão vigente é:

```text
Nome público: Sonhe + Alto
Nomes históricos: apenas legado técnico, documentação histórica ou compatibilidade.
```

## Resumo Executivo

Não é recomendável fazer substituição global.

Há três realidades diferentes misturadas:

- **Interface pública:** deve ser padronizada para Sonhe + Alto.
- **Código técnico Django:** `apps/projeto21`, `apps/sonho_de_ser`, namespace `projeto21`, migrations e imports devem permanecer por enquanto.
- **Dados e slugs legados:** `projeto21`, `projeto21_sonhe_alto`, `sonhemaisalto`, `sonhemaisalto_guia` precisam continuar como equivalências de acesso.

## Ocorrências Públicas Que Devem Ser Corrigidas

Estas são visíveis ao usuário, mentor, escola ou administrador e podem ser ajustadas com baixo risco.

### Portal/Core

| Arquivo | Ocorrência | Ação |
| --- | --- | --- |
| `apps/core/templates/core/portal.html` | tooltip menciona `Projeto 21` | trocar para descrição sem nome antigo |
| `apps/core/templates/core/portal.html` | título `Projeto Sonhe + Alto` | trocar para `Sonhe + Alto` |
| `apps/core/templates/core/portal.html` | texto `Plano de vida... (Projeto 21)` | remover referência a `Projeto 21` |
| `templates/core/legal/privacidade.html` | `Projeto Sonhe + Alto (Projeto 21)` | trocar para `Sonhe + Alto` |
| `templates/core/index.html` | subtítulo `Projeto 21 · Escola no Ar` | trocar para `Sonhe + Alto · Escola no Ar` |
| `templates/core/mentorias_home.html` | botão `Projeto 21 (Mentor)` | trocar para `Sonhe + Alto (Mentor)` |

### Contas

| Arquivo | Ocorrência | Ação |
| --- | --- | --- |
| `templates/contas/criar_conta.html` | `Projeto Sonhe + Alto` | trocar para `Sonhe + Alto` |
| `templates/contas/registrar.html` | `Projeto Sonhe + Alto` | trocar para `Sonhe + Alto` |

Observação: links para `/projeto21/` podem permanecer temporariamente como URL de compatibilidade, desde que o texto visível esteja correto.

### Landing Legada do Produto

| Arquivo | Ocorrência | Ação |
| --- | --- | --- |
| `templates/projeto21/landing.html` | `<title>Projeto Sonhe + Alto</title>` | trocar para `Sonhe + Alto` |
| `templates/projeto21/landing.html` | `Projeto Sonhe + Alto` em textos e kits | trocar para `Sonhe + Alto`, salvo quando estiver se referindo a material impresso legado |
| `templates/projeto21/landing.html` | logs JS `[Projeto21]` | pode permanecer como diagnóstico técnico, mas idealmente trocar para `[SonheAlto]` depois |
| `templates/projeto21/landing.html` | IDs/anchors como `kits-projeto21` | manter por enquanto para evitar quebrar navegação interna |

### Runtime do Aluno

Os templates principais já estão quase padronizados:

- `templates/sonho_de_ser/projeto21_dashboard.html`
- `templates/sonho_de_ser/projeto21_plano.html`
- `templates/sonho_de_ser/projeto21_registro.html`
- `templates/sonho_de_ser/projeto21_historico.html`
- `templates/sonho_de_ser/projeto21_pontuacao.html`
- `templates/sonho_de_ser/projeto21_mentor.html`

Ainda há links para `/projeto21/`. Isso é aceitável por enquanto como compatibilidade técnica.

### Template Antigo Ainda Problemático

| Arquivo | Ocorrência | Ação |
| --- | --- | --- |
| `templates/sonho_de_ser/base_sonhodeser.html` | `<title>Sonho de Ser</title>` | se ainda for usado, trocar para `Sonhe + Alto`; se for legado morto, marcar como obsoleto |
| `templates/sonho_de_ser/base_sonhodeser.html` | navbar `Sonho de Ser` | mesma decisão acima |

## Ocorrências Técnicas Que Devem Permanecer Por Enquanto

Estas ocorrências não devem ser trocadas em uma primeira rodada, porque impactam Django, migrations, URLs, imports ou compatibilidade.

### Apps e Namespaces

| Ocorrência | Motivo |
| --- | --- |
| `apps/projeto21` | app Django legado e namespace público/compatibilidade |
| `apps/sonho_de_ser` | app Django canônico atual do runtime |
| `app_name = "projeto21"` | usado em URLs e reverse |
| `app_name = "sonho_de_ser"` | usado internamente |
| `Projeto21DashboardView`, `Projeto21MentorView` | nomes de classe legados; trocar exige ajuste coordenado |
| `templates/sonho_de_ser/projeto21_*.html` | nomes de templates; trocar exige ajuste coordenado nas views |

### Migrations

Não alterar nomes dentro de migrations já aplicadas:

- `apps/projeto21/migrations/0001_initial.py`
- `apps/sonho_de_ser/migrations/*.py`

Motivo: migrations são histórico técnico. Alterar por estética aumenta risco sem benefício prático.

### Settings e URLs

| Arquivo | Ocorrência | Ação |
| --- | --- | --- |
| `escola_no_ar_site/settings.py` | `apps.sonho_de_ser.apps.SonhoDeSerConfig` | manter |
| `escola_no_ar_site/settings.py` | `apps.projeto21.apps.Projeto21Config` | manter |
| `escola_no_ar_site/urls.py` | `path("projeto21/", ...)` | manter como compatibilidade |
| `escola_no_ar_site/urls.py` | `path("sonhe-mais-alto/", ...)` | manter e expandir futuramente |

## Slugs e Permissões

Estas ocorrências são regras de negócio e acesso. Não trocar sem migração de dados.

| Ocorrência | Local | Ação |
| --- | --- | --- |
| `PROD_SONHEMAISALTO = "sonhemaisalto"` | `apps/core/permissions.py` | manter |
| `sonhemaisalto` | equivalências de produto | manter |
| `sonhemaisalto_bonus` | equivalências de produto | manter |
| `sonhemaisalto_guia` | equivalências de produto | manter |
| `projeto21_sonhe_alto` | equivalência legada | manter |
| `projeto21` | equivalência legada | manter |

Recomendação futura: centralizar esses valores em um registry de produto, sem remover equivalências legadas.

## Ocorrências em Governança/Admin

| Arquivo | Ocorrência | Ação |
| --- | --- | --- |
| `apps/core/context_processors.py` | `Projeto 21 (Mentor)` | trocar label público para `Sonhe + Alto (Mentor)` |
| `apps/core/context_processors.py` | `Projeto 21` | trocar label público para `Sonhe + Alto` |
| `apps/core/views_webhooks.py` | label `Projeto 21 – Sonhe + Alto` | trocar label exibido para `Sonhe + Alto`; manter slug `projeto21_sonhe_alto` |
| `apps/projeto21/apps.py` | `verbose_name = 'Projeto 21'` | pode trocar para `Sonhe + Alto` se não quebrar admin; baixo risco, mas confirmar no admin |
| `apps/sonho_de_ser/apps.py` | `verbose_name = "Sonho de Ser"` | pode trocar para `Sonhe + Alto` se não quebrar admin; baixo risco, mas confirmar no admin |

## Documentação Histórica

Em `docs/arquitetura`, muitos documentos mencionam `Projeto 21`, `Sonho de Ser`, `projeto21` e `sonho_de_ser`.

Ação recomendada:

- não reescrever documentação histórica;
- manter menções quando explicam origem, legado ou decisão técnica;
- nos documentos vivos, adicionar nota de nomenclatura quando necessário;
- novos documentos devem usar `Sonhe + Alto` como nome público.

Documentos vivos relevantes:

- `decisao_nomenclatura_sonhe_mais_alto.md`
- `plano_recuperacao_escopo_sonho_de_ser.md`
- `guia_de_desenvolvimento_sonhe_mais_alto.md`
- `registro_checkpoint_git_20260415.md`

## Acervo e Materiais Antigos

Foram encontradas ocorrências em:

- `apps/publicacoes/Final/*.html`
- `apps/publicacoes/Guia_Projeto_de_Vida/*.html`
- `apps/publicacoes/Projeto21/*.html`

Esses arquivos parecem acervo/protótipos/materiais históricos, não fluxo operacional principal.

Ação recomendada:

- não mexer agora;
- decidir depois se serão removidos, movidos para acervo externo ou revisados como material publicado;
- não deixar esses arquivos influenciarem a arquitetura do runtime.

## Primeira Rodada Recomendada

Escopo seguro para a próxima alteração:

1. Corrigir labels públicos em:
   - `apps/core/templates/core/portal.html`
   - `templates/core/legal/privacidade.html`
   - `templates/core/index.html`
   - `templates/core/mentorias_home.html`
   - `templates/contas/criar_conta.html`
   - `templates/contas/registrar.html`
   - `apps/core/context_processors.py`
   - `apps/core/views_webhooks.py`

2. Corrigir `verbose_name` dos apps, se o admin for conferido:
   - `apps/projeto21/apps.py`
   - `apps/sonho_de_ser/apps.py`

3. Não alterar ainda:
   - rotas `/projeto21/`;
   - namespace `projeto21`;
   - app labels;
   - imports;
   - migrations;
   - slugs de produto;
   - nomes de templates.

## Segunda Rodada Recomendada

Criar uma fonte única de identidade do produto no `core`, por exemplo:

```text
apps/core/product_registry.py
```

ou:

```text
apps/core/services/product_registry.py
```

Esse registry deve conter:

- nome público: `Sonhe + Alto`;
- slug público: `sonhe-mais-alto`;
- slugs de acesso equivalentes;
- URL pública preferencial;
- URL técnica de compatibilidade;
- descrição curta;
- nomes legados documentados.

## Critério de Aceite da Padronização

A primeira fase estará concluída quando:

- nenhuma tela pública relevante mostrar `Projeto 21` ou `Sonho de Ser` como marca;
- URLs legadas continuarem funcionando;
- o portal continuar resolvendo acesso pelo `core`;
- `git status --short` ficar limpo após commit;
- o servidor abrir:
  - `/portal/`
  - `/sonhe-mais-alto/`
  - `/projeto21/`
  - `/projeto21/plano/`
  - `/projeto21/registro/`
  - `/projeto21/historico/`
  - `/projeto21/pontuacao/`

