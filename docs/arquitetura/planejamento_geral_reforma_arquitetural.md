# Planejamento Geral da Reforma Arquitetural

## Decisões de arquitetura já fixadas
- `core` será o centro oficial de navegação de produtos e o orquestrador de entrada.
- `vocacional` continua dono do fluxo interno do produto.
- `apps/contas` permanece como fonte única de usuário, produto, acesso e permissões.
- `staff/superuser` devem ter experiência própria de governança, fora do funil do aluno.
- A vitrine oficial de produtos deve existir em um único lugar.
- A consolidação deve reaproveitar gating, permissões e templates já existentes antes de criar novas camadas.
- `core/portal.html` deve virar compatibilidade transitória, não segunda vitrine oficial.
- `templates/vocacional/ofertas_refinamento.html` deve ser tratado como ativo existente do Vocacional, não substituído sem necessidade.

## Decisões ainda em aberto
- Se a vitrine oficial final manterá a rota `portal` como alias compatível ou migrará para uma rota mais explícita como `produtos/`.
- Se a governança MVP reutilizará diretamente `templates/portal/dashboard.html` ou passará por uma migração leve para `core/governanca.html`.
- Se será necessário um service dedicado de status por produto ou se a primeira extração pode ficar dentro de `core/views.py` com helpers privados.
- Quando criar detalhe de produto genérico no `core`.
  Só deve acontecer quando houver segundo caso real além do Vocacional.
- Quando criar partials visuais no `core`.
  Só deve acontecer após segunda reutilização real.

## Riscos de duplicação e como evitar
- Duplicar gating existente.
  Evitar: usar `apps/core/permissions`, `user_has_produto`, `onboarding_status` e `apps/vocacional/gating.py` como fontes de verdade.
- Manter `portal` e `produtos` como vitrines concorrentes.
  Evitar: escolher uma tela oficial e transformar a outra em alias ou compat layer.
- Manter `dashboard` e `governanca` como painéis concorrentes.
  Evitar: decidir que a governança MVP nasce da base atual do dashboard e substitui semanticamente esse papel.
- Criar `produto_detalhe.html` concorrente ao Vocacional.
  Evitar: na Fase 1, usar o resolver para mandar ao detalhe/oferta já existente do Vocacional quando aplicável.
- Criar CSS novo concorrente.
  Evitar: extrair apenas o CSS comum realmente necessário do portal atual; não criar sistema visual paralelo.
- Criar services que repliquem regra existente.
  Evitar: services novos só para orquestração e composição, nunca para redefinir regra de produto, onboarding ou entitlement.

## Sequência recomendada de execução
1. Consolidar a fonte de contexto do portal/vitrine no `core`.
2. Definir a única entrada oficial de produtos.
3. Redirecionar staff/superuser para governança de forma clara.
4. Encapsular status por produto reaproveitando regras existentes.
5. Atualizar CTAs principais para passar pelo resolvedor central.
6. Só depois avaliar extrações de template/CSS com reutilização real.
7. Deixar abstrações genéricas e detalhe de produto para fases posteriores, se houver segundo uso concreto.

---

# 1) Planejamento Macro da Reforma Arquitetural

## Objetivo arquitetural geral
Consolidar o projeto em uma arquitetura em que:
- `core` concentra catálogo, entrada oficial, status por produto e orquestração de navegação;
- apps de produto, como `vocacional`, preservam a posse total de seus fluxos internos;
- `apps/contas` continua sendo a base única de autenticação, acesso e permissões;
- `staff/superuser` operam por uma experiência de governança própria;
- a expansão para novos produtos ocorre sem criar navegação paralela nem duplicação estrutural.

## Princípios e restrições
- Reaproveitar antes de criar.
- Encapsular antes de abstrair.
- Adiar generalização até existir segunda reutilização real.
- Não mover lógica interna de produto para o `core`.
- Não criar camada paralela para status, acesso, onboarding ou governança.
- Preservar nomes de rotas críticas enquanto houver dependência.
- Fazer mudanças pequenas, reversíveis e verificáveis.
- Cada fase deve reduzir ambiguidade, não aumentá-la.

## Fronteiras entre apps e camadas

### `core`
Responsável por:
- entrada oficial dos produtos;
- vitrine oficial de produtos;
- composição de status do usuário por produto;
- resolvedor de entrada por produto;
- governança de staff/superuser;
- compatibilidade transitória entre portal antigo e arquitetura-alvo.

Não responsável por:
- fluxo interno do Vocacional;
- regras internas de etapas, passes, resultado e refinamento.

### `vocacional`
Responsável por:
- avaliação;
- continuidade do teste;
- resultado;
- desempate rápido;
- refinamento;
- ofertas e detalhes operacionais do próprio produto.

Não responsável por:
- vitrine oficial do ecossistema;
- decisão de qual produto o usuário deve abrir a partir do hub global.

### `apps/contas`
Responsável por:
- usuário;
- autenticação;
- produto;
- acesso;
- permissões e compatibilidade com entitlements.

Não responsável por:
- orquestração de navegação;
- lógica de produto.

### Governança
Responsável por:
- experiência própria de staff/superuser;
- teste por persona;
- atalhos operacionais;
- visão consolidada de estado.

Não responsável por:
- substituir `apps/contas`;
- controlar lógica interna do Vocacional.

## Fases sugeridas

## Fase 1
### Objetivo
Consolidar o `core` como entrada oficial e eliminar a duplicação principal de portal/vitrine/status.

### Entregáveis
- uma única fonte de contexto para portal/vitrine;
- uma entrada oficial de produto no `core`;
- status consolidado por produto reaproveitando regras existentes;
- governança MVP sem painel concorrente;
- `portal` rebaixado a compatibilidade transitória se necessário.

### Riscos
- manter duas vitrines;
- duplicar status/gating;
- mexer demais no Vocacional.

### Critérios de aceite
- existe um único lugar oficial para entrar nos produtos;
- staff/superuser não caem no funil do aluno por padrão;
- o Vocacional continua funcionando sem migração interna;
- não houve nova fonte de verdade para acesso/onboarding.

### Não entra
- refactor profundo do Vocacional;
- detalhe genérico de produto;
- sistema visual genérico de cards/partials sem reuso comprovado.

## Fase 2
### Objetivo
Migrar pontos de entrada secundários e consolidar governança operacional.

### Entregáveis
- CTAs secundários passando pelo resolvedor central onde fizer sentido;
- governança com fluxo mais claro de teste por persona;
- redução adicional de links diretos espalhados em templates globais.

### Riscos
- trocar links internos legítimos do Vocacional;
- criar governança paralela ao dashboard existente.

### Critérios de aceite
- links de entrada globais passam pelo `core`;
- governança tem papel inequívoco e único para staff/superuser.

### Não entra
- reescrita visual ampla;
- mudança de modelos de dados.

## Fase 3
### Objetivo
Padronizar a integração de múltiplos produtos no catálogo oficial.

### Entregáveis
- padrão de registro de produto consolidado;
- integração de Sonhe+Alto no mesmo eixo do `core`;
- regras de status e CTA reproduzíveis para segundo produto real.

### Riscos
- abstração prematura;
- padronizar antes de validar com mais de um produto.

### Critérios de aceite
- pelo menos dois produtos usam o mesmo trilho de entrada oficial;
- sem duplicar regras de acesso nem templates sem necessidade.

### Não entra
- grandes reescritas de fluxos internos dos produtos.

## Fase 4
### Objetivo
Evoluir governança e observabilidade operacional.

### Entregáveis
- visão consolidada por produto;
- busca de usuário;
- inspeção resumida de estado;
- ações operacionais seguras e controladas.

### Riscos
- misturar suporte operacional com lógica de produto;
- inflar a governança cedo demais.

### Critérios de aceite
- staff/superuser têm ferramenta operacional separada do fluxo do aluno;
- uso de impersonação e inspeção continua compatível.

### Não entra
- CRM interno;
- automações administrativas profundas sem necessidade real.

## Compatibilidade e migração gradual
- Rotas antigas devem ser mantidas como aliases ou compat layers enquanto houver dependência.
- O `portal` atual não deve desaparecer de uma vez; deve perder centralidade aos poucos.
- O Vocacional deve continuar com seus nomes de rota e fluxo interno.
- O `core` deve compor contexto usando regras já existentes, nunca reimplementá-las.
- Cada fase deve permitir rollback local sem exigir revert geral.
