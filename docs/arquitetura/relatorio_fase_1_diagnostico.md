# Relatório de Diagnóstico para Reforma Arquitetural

## Escopo deste relatório
Este documento consolida:
- diagnóstico da arquitetura atual,
- conflitos com a arquitetura-alvo,
- proposta de Fase 1,
- lista exata de arquivos a mexer,
- riscos e cuidados.

Este relatório não implementa mudanças.
Ele serve como base para a primeira rodada de patches incrementais.

## 1. Diagnóstico da arquitetura atual

Hoje o projeto já possui um hub pós-login no `core`, mas esse hub ainda funciona mais como `portal` operacional do que como catálogo oficial e orquestrador central de produtos.

### Eixo atual de navegação
- A entrada pública e pós-login está em `escola_no_ar_site/urls.py`.
- `""` aponta para `core_views.portal`.
- `"/portal/"` aponta para `core_views.portal_home`.
- O app `core` já centraliza parte do gating comercial e do onboarding.
- O app `vocacional` ainda controla boa parte da entrada real no fluxo do produto.

### O que o `core` já faz hoje
- concentra o portal atual;
- concentra parte da lógica de acesso por produto;
- concentra o status de onboarding;
- já trouxe o aceite legal para o `core` com uma tela única de Termos + Privacidade;
- possui um dashboard mínimo de governança para staff/superuser;
- possui suporte a impersonação para teste de fluxo.

### O que o `vocacional` ainda faz hoje
- controla a entrada no fluxo do Vocacional;
- define `next_step` e `next_url` do seu funil;
- define `entrada`, `avaliacao_gate`, `etapas`, `resultado`, `comparacoes_top3`;
- mantém templates com links diretos para páginas internas;
- mistura regras de produto, funil, refinamento e continuidade dentro do app.

### O que `apps/contas` já preserva corretamente
- base única de usuários;
- base única de produtos e acessos;
- modelo `Usuario` atual;
- modelo `Produto`;
- modelo `Acesso`;
- compatibilidade com permissões/entitlements existentes.

### Estado arquitetural resumido
O projeto já deu passos na direção correta, mas ainda está em um meio-termo:
- o `core` já participa da navegação;
- o `core` ainda não é o centro oficial;
- o `vocacional` ainda resolve parte importante do fluxo de entrada;
- os templates ainda têm CTAs diretos para destinos internos.

## 2. Conflitos com a arquitetura-alvo

### Conflito 1: o `core` ainda não possui uma camada formal de produtos
Ainda não existe uma camada explícita com:
- `product_registry.py`,
- `product_status.py`,
- `product_resolver.py`,
- `governance.py`.

Hoje essa responsabilidade está espalhada entre:
- `apps/core/views.py`,
- `apps/core/permissions.py`,
- `apps/vocacional/gating.py`.

### Conflito 2: o hub atual não é uma vitrine oficial de produtos
Hoje a tela principal é `portal.html`.
Ela funciona como ponto de acesso, mas ainda não é uma vitrine estruturada por produto com:
- catálogo oficial,
- status oficial por produto,
- CTA oficial mediado por resolvedor,
- detalhe de produto.

### Conflito 3: cards ainda decidem destino direto
Os cards do portal atual enviam o usuário diretamente para:
- `projeto21:home`
- `vocacional:etapas`

Isso conflita com a regra de ouro definida nos docs:
os cards não devem decidir o fluxo; devem chamar o resolvedor central.

### Conflito 4: o Vocacional ainda possui resolvedor implícito de entrada
Hoje o app `vocacional` possui sua própria lógica de resolução em:
- `gating.py`
- `entrada`
- `avaliacao_gate`
- `etapas`

Isso é válido como fluxo interno do produto, mas ainda ocupa parte do papel que deveria começar no `core`.

### Conflito 5: duplicação de lógica no `core`
As views `portal()` e `portal_home()` repetem montagem de contexto e regras próximas.
Isso indica que o hub atual ainda não está organizado como camada reutilizável.

### Conflito 6: CSS e composição ainda não estão compartilhados do jeito desejado
O template `core/portal.html` ainda carrega CSS inline relevante.
Isso conflita com a diretriz de centralizar estilo compartilhável.

### Conflito 7: governança ainda está acoplada ao portal atual
O comportamento de staff/superuser já existe, mas ainda está distribuído entre:
- `portal_home`,
- `PortalDashboardView`,
- `middleware` de impersonação,
- templates de dashboard.

Ainda não existe uma camada clara de governança no formato proposto.

### Conflito 8: templates do Vocacional ainda possuem atalhos hardcoded
Há vários links diretos para:
- `portal`,
- `vocacional:avaliacao_form`,
- `vocacional:etapas`,
- `projeto21:home`

Nem todo link precisa ser removido nesta fase, mas os pontos de entrada de produto devem migrar para o resolvedor central.

## 3. Proposta de Fase 1

## Objetivo da Fase 1
Mudar o eixo da navegação sem reescrever o projeto nem quebrar o Vocacional.

O foco não é migrar tudo.
O foco é fazer o `core` passar a ser o centro visível e reutilizável da navegação de produtos.

### Entregável arquitetural da Fase 1
- criar o catálogo oficial de produtos no `core`;
- criar o resolvedor central de entrada por produto;
- separar apresentação de produto da lógica de destino;
- preparar governança MVP no mesmo eixo;
- reaproveitar a lógica atual de acesso/onboarding em vez de duplicá-la.

### Estratégia
1. Manter `apps/contas` intacto como fonte de usuário e acesso.
2. Manter o fluxo interno do `vocacional` intacto.
3. Colocar no `core` a camada oficial de:
   - registry,
   - status,
   - resolver,
   - governança.
4. Criar `produtos.html` como vitrine oficial.
5. Fazer os cards chamarem o resolvedor central.
6. Preservar `portal` como compatibilidade durante a transição.

### O que a Fase 1 deve fazer
- introduzir serviços em `apps/core/services/`;
- definir produtos oficiais por slug público;
- montar status do usuário por produto com reaproveitamento do que já existe;
- criar rota de catálogo;
- criar rota de detalhe;
- criar rota de resolver;
- preparar rota/página de governança MVP;
- extrair CSS compartilhado;
- atualizar pontos principais de entrada para usar o resolvedor.

### O que a Fase 1 não deve fazer
- não reescrever o Vocacional;
- não trocar a base de autenticação;
- não criar modelo novo de usuários;
- não migrar todo template interno do Vocacional;
- não alterar profundamente modelos de produto/acesso;
- não fazer big bang refactor.

## 4. Lista exata de arquivos a mexer

## Arquivos existentes a alterar
- `escola_no_ar_site/urls.py`
- `apps/core/urls.py`
- `apps/core/views.py`
- `apps/core/templates/core/portal.html`
- `templates/portal/dashboard.html`
- `templates/base.html`
- `templates/vocacional/ofertas_refinamento.html`
- `templates/vocacional/base_vocacional.html`

## Arquivos novos a criar
- `apps/core/services/__init__.py`
- `apps/core/services/product_registry.py`
- `apps/core/services/product_status.py`
- `apps/core/services/product_resolver.py`
- `apps/core/services/governance.py`
- `apps/core/templates/core/produtos.html`
- `apps/core/templates/core/produto_detalhe.html`
- `apps/core/templates/core/governanca.html`
- `apps/core/templates/core/partials/_produto_card.html`
- `apps/core/templates/core/partials/_produto_status.html`
- `apps/core/templates/core/partials/_produto_cta.html`
- `static/css/core_produtos.css`

## Arquivos que idealmente não devem ser alterados nesta fase
- `apps/contas/models.py`
- `apps/contas/models_acessos.py`
- `apps/vocacional/models.py`
- `apps/vocacional/views.py`

Observação:
`apps/vocacional/views.py` só deveria ser tocado se surgir alguma incompatibilidade mínima inevitável no momento de integrar o resolvedor central.

## 5. Riscos e cuidados

### Risco 1: duplicar gating existente
O maior risco é recriar regras de acesso que já existem.

Mitigação:
- reaproveitar `apps.core.permissions`;
- reaproveitar `user_has_produto`;
- reaproveitar `onboarding_status`;
- não duplicar equivalências de slug em mais de um lugar.

### Risco 2: quebrar entrada atual do Vocacional
Hoje o Vocacional já funciona com regras próprias de continuidade.

Mitigação:
- o resolvedor central do `core` deve decidir apenas o ponto oficial de entrada;
- o fluxo interno continua sendo responsabilidade do `vocacional`.

### Risco 3: quebrar staff/superuser e impersonação
O projeto já tem comportamento especial para staff/superuser e modo teste.

Mitigação:
- preservar `portal_mode`;
- preservar `ImpersonateUserMiddleware`;
- preservar a regra de que superuser/staff cai em governança por padrão.

### Risco 4: trocar links cedo demais dentro do Vocacional
Há links internos legítimos dentro do módulo.

Mitigação:
- nesta fase, trocar apenas links de entrada de produto;
- não mexer em links claramente internos do fluxo.

### Risco 5: CSS novo competir com estilo existente
O portal atual e o Vocacional já têm estilos próprios.

Mitigação:
- criar um CSS específico para catálogo de produtos;
- evitar sobrescrever classes globais antigas;
- usar nomes de classe próprios da camada `core`.

### Risco 6: governança virar fluxo paralelo confuso
Se a governança for implementada só como outra tela de portal, o problema continua.

Mitigação:
- separar semanticamente catálogo de produtos e governança;
- manter governança como experiência própria para staff/superuser.

### Risco 7: regressão de compatibilidade em rotas existentes
Há dependência em nomes como:
- `portal`
- `portal_dashboard`
- `portal_impersonar`
- `vocacional:avaliacao_gate`
- `vocacional:etapas`

Mitigação:
- preservar nomes existentes;
- introduzir novas rotas sem remover as atuais nesta fase.

## Conclusão

O projeto já possui elementos importantes da arquitetura-alvo, mas ainda opera com navegação e decisão de fluxo distribuídas entre `core`, `vocacional` e templates.

A Fase 1 deve:
- consolidar o `core` como centro da navegação de produtos,
- criar a vitrine oficial,
- introduzir o resolvedor central,
- preparar governança MVP,
- e preservar integralmente `apps/contas`, permissões existentes e o fluxo interno já funcional do Vocacional.

Essa abordagem permite uma reforma progressiva, explicável e segura, sem recriar o projeto do zero.
