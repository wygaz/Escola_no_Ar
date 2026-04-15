# 05_plano_fase_1

## Regra desta fase
Não reescrever tudo.
Fazer a menor fatia arquitetural que já mude o eixo do sistema.

## Entregáveis da Fase 1
1. Estruturar o `core` como centro da navegação de produtos.
2. Criar `produtos.html`.
3. Criar `_produto_card.html`.
4. Criar `core_produtos.css`.
5. Criar `product_registry.py`.
6. Criar `product_status.py`.
7. Criar `product_resolver.py`.
8. Preparar `governanca.html` e `governance.py` em MVP.
9. Reaproveitar, sem copiar cegamente, o que já existe em ofertas/refinamento e etapas.

## Modo de trabalho exigido
1. Inspecionar a base atual.
2. Resumir a arquitetura atual.
3. Identificar conflitos com a arquitetura-alvo.
4. Propor plano de mudança por etapas.
5. Só então implementar a Fase 1.

## Arquivos/áreas a inspecionar
- apps/core
- apps/vocacional
- apps/contas
- rotas pós-login
- templates de etapas/ofertas/portal
- gating e entitlements
- onboarding e avaliação do guia

## Expectativa de implementação
- patches pequenos
- explicação por arquivo
- atenção a compatibilidade
- nada de “big bang refactor”

## Resultado esperado da Fase 1
Ao final da Fase 1, a plataforma já deve ter um centro visível e reutilizável de navegação de produtos, mesmo que nem todo o resto esteja migrado.
