# Plano de limpeza do ambiente de desenvolvimento

## Objetivo

Organizar o repositório local para deixar a raiz e o entorno do projeto mais limpos, sem apagar conteúdo e sem comprometer o funcionamento do sistema.

Princípio:

- nada será excluído nesta etapa;
- primeiro organizar, depois eventualmente eliminar;
- tudo que for incerto vai para quarentena local;
- tudo que for documentação ativa do projeto vai para `docs/`;
- tudo que for necessário ao runtime continua no lugar.

## Destinos oficiais

### 1. `docs/`

Para:

- planejamento arquitetural;
- relatórios de retomada;
- decisões de nomenclatura;
- documentação de governança;
- guias internos de desenvolvimento;
- documentação útil e recente do projeto.

### 2. `Apenas_Local/Doc.quarentena/`

Para:

- arquivos históricos;
- pacotes de patch antigos;
- snapshots;
- zips de trabalho;
- backups locais;
- logos soltos fora de `static/`;
- scripts auxiliares locais;
- diretórios paralelos usados como acervo, rascunho ou export local.

### 3. Raiz do projeto

Devem ficar apenas arquivos de operação, repositório e runtime, por exemplo:

- `manage.py`
- `requirements.txt`
- `.gitignore`
- `.env*`
- `.python-version`
- `AGENTS.md`
- `Procfile`
- scripts realmente usados para subir/operar localmente
- certificados locais, se ainda forem usados

## Regras de segurança

- não mover nada de `apps/*/templates`, `apps/*/static`, `templates/`, `static/`, `media/`, `migrations/` ou código Python ativo sem checagem específica;
- não usar a quarentena para esconder arquivo de sistema em uso;
- antes de mover arquivos rastreados pelo Git, decidir se eles devem ir para `docs/` ou sair do repositório;
- manter a limpeza em lotes pequenos e verificáveis.

## Estratégia em lotes

### Lote 1

Mover apenas material claramente local/ignorado:

- snapshots;
- diretórios de export;
- zips de patch;
- backups locais;
- imagens soltas fora de `static/`;
- diretórios auxiliares ignorados pelo Git.

Impacto esperado:

- limpeza local significativa;
- risco funcional muito baixo;
- impacto zero ou mínimo no histórico do repositório.

### Lote 2

Reorganizar arquivos rastreados da raiz que são documentação ou acervo, por exemplo:

- `README_PATCH.md`
- `README_PATCH_LOGOUT_v4.txt`
- `Solucao_para_consentimento.txt`
- `Arvore_Oficial_do_Core`
- material legado de apoio hoje espalhado fora de `docs/`

Critério:

- se for documentação útil e atual, mover para `docs/`;
- se for histórico ou redundante, mover para quarentena local.

### Lote 3

Avaliar material editorial e de apoio embutido dentro de apps, com muito mais cuidado:

- planilhas auxiliares;
- DOCX/PDF de publicação;
- materiais de formulário;
- arquivos duplicados antigos;
- rascunhos de livreto.

Esse lote exige checagem de uso e não deve ser misturado com a limpeza da raiz.

## Decisão operacional desta sessão

Executar apenas o `Lote 1`.

Motivo:

- é a faixa mais segura;
- entrega limpeza visível imediatamente;
- evita mover arquivos rastreados úteis sem classificação fina;
- preserva o princípio de segurança em primeiro lugar.
