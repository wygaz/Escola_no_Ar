# 02_arquitetura_alvo

## Princípio central
O app `core` será o centro da navegação de produtos.
Os apps específicos continuarão sendo donos apenas de seus fluxos internos.

## Organização de responsabilidades

### core
Responsável por:
- catálogo oficial de produtos
- página oficial de produtos
- card reutilizável de produto
- status do usuário por produto
- resolvedor de fluxo
- governança e teste por persona
- componentes visuais compartilhados

### vocacional
Responsável por:
- avaliação
- resultado
- desempate rápido
- etapas/refinamentos
- regras internas do teste

### sonhe+alto / projeto21
Responsável por:
- entrar futuramente no mesmo padrão arquitetural
- sem criar navegação paralela fora do `core`

## Estrutura-alvo sugerida

apps/core/
- urls.py
- views.py
- services/
  - product_registry.py
  - product_status.py
  - product_resolver.py
  - governance.py
- templates/core/
  - produtos.html
  - produto_detalhe.html
  - governanca.html
  - partials/
    - _produto_card.html
    - _produto_status.html
    - _produto_cta.html
- static/css/
  - core_produtos.css

## Regra de ouro
Os cards de produto não devem decidir o fluxo.
Eles devem chamar o resolvedor central.

## Benefício esperado
Essa arquitetura reduz ambiguidade, reduz duplicação e deixa o projeto preparado para crescimento.
