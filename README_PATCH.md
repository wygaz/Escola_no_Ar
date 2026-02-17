# Patch – Portal + Acessos (Vocacional / Sonhe + Alto)

Copie/mescle estes arquivos no seu projeto (raiz do repositório), respeitando os caminhos.

## O que este patch faz
- Centraliza a checagem de acesso em `apps/core/permissions.py` com:
  - slugs de referência: `vocacional` e `sonhemaisalto`
  - equivalências para aceitar slugs antigos (ex.: `vocacional_guia`, `vocacional_bonus`, etc.)
- Atualiza Portal (público) para mostrar 2 opções e indicar "Acesso liberado" ou "não liberado".
- Ajusta Vocacional/Projeto21 para usar slugs de referência e a checagem central.
- Adiciona aceite de Termos (checkbox) na página /vocacional/termos/ e registra em `AvaliacaoGuia.aceite_termos`.

## Depois de aplicar
1) Verifique se seus `Produto.slug` no Admin estão coerentes (ex.: `vocacional` e `sonhemaisalto`).
   - Se ainda estiver usando slugs antigos, tudo deve funcionar por causa das equivalências.
2) Teste com o usuário "Alberto":
   - Portal deve mostrar os botões como liberados se ele tiver Acesso com qualquer slug equivalente.
3) Se você quiser “enxugar” no futuro:
   - remova slugs antigos do dict `EQUIVALENCIAS`.
