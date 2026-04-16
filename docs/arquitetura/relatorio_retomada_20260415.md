# Relatorio de retomada - 2026-04-15

## Estado atual

Branch de trabalho:

- `checkpoint/saneamento-20260415`

Ultimo commit registrado:

- `8a21e69 refactor: centraliza registry de produtos no core`

Repositorio apos o commit:

- worktree limpo
- validacao no venv do usuario concluida com sucesso

Validacoes executadas pelo usuario:

```powershell
python -m py_compile apps\core\product_registry.py apps\core\views.py
python manage.py check
```

Resultado informado:

- `py_compile OK`
- `manage.py check OK`

## O que foi feito nesta etapa

Foi criada a primeira fatia da Fase 1 da reforma arquitetural: centralizar no app `core` a definicao dos produtos expostos pelo portal.

Arquivo criado:

- `apps/core/product_registry.py`

Arquivo alterado:

- `apps/core/views.py`

Mudanca principal:

- o portal e o `produto_resolver` deixaram de depender de configuracoes hardcoded diretamente na view;
- os metadados de produto passaram a vir do registry central;
- foram preservados os slugs tecnicos, URLs, nomes de rotas, permissoes e templates existentes.

Produtos atualmente registrados:

- `Sonhe + Alto`
- `Vocacional`

## Decisoes preservadas

- Nome publico vigente: `Sonhe + Alto`.
- Nomes antigos como `Projeto 21` e `Sonho de Ser` permanecem apenas como legado tecnico/contextual.
- URLs e namespaces tecnicos ainda nao foram renomeados nesta fase.
- `apps/contas` continua sendo a base unica de usuarios.
- A navegacao de produto deve continuar apontando para o resolvedor central.

## Contexto importante

O ambiente Python acessado diretamente pela sessao do Codex ainda aponta para um runtime inexistente:

- `C:\Users\Wanderley\AppData\Local\Programs\Python\Python312\python.exe`

Por isso, validacoes Python devem ser rodadas no terminal do usuario com o venv ativo, ate que esse ponto seja saneado. Isso nao impediu a validacao da alteracao, pois o usuario confirmou `py_compile OK` e `manage.py check OK`.

## Proximos passos prudentes

1. Testar no navegador, com servidor rodando, as entradas centrais:

```text
/portal/
/produtos/sonhe-mais-alto/entrar/
/produtos/vocacional/entrar/
```

2. Evoluir o registry para alimentar a tela de produtos/cards do portal, reduzindo duplicacao no template sem mexer ainda na identidade visual.

3. Criar ou consolidar um card reutilizavel de produto, respeitando a regra de nao colocar decisao de fluxo no template.

4. Preparar a camada de governanca do superusuario em cima do mesmo registry, em vez de criar caminhos paralelos.

5. Deixar saneamento de CSS para depois, conforme decisao ja tomada.

## Riscos / cuidados

- Nao renomear agora apps, namespaces, tabelas, migrations ou URLs tecnicas ligadas a `projeto21` e `sonho_de_ser`.
- Nao duplicar regras de acesso em templates.
- Nao remover equivalencias de slugs em `apps/core/permissions.py` sem inventario especifico.
- Antes de cada nova fatia, conferir `git status --short` e manter commits pequenos.
