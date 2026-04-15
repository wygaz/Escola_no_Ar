# Bloco A  Plano detalhado da Fase 1 revisado e congelado

## Decisões de arquitetura já fixadas
- `core` é a entrada oficial e o orquestrador de navegação por produto.
- `vocacional` continua dono do fluxo interno do produto.
- `apps/contas` continua como fonte única de usuário, produto, acesso e permissões.
- a governança de `staff/superuser` existe fora do funil do aluno.
- a Fase 1 não pode criar camada paralela.
- a Fase 1 deve priorizar extração, centralização e reaproveitamento da lógica existente.
- `portal` é apenas compatibilidade transitória nesta fase.
- a governança MVP parte de `templates/portal/dashboard.html`.
- `templates/vocacional/ofertas_refinamento.html` permanece como ativo existente de detalhe/oferta do Vocacional.
- não nasce `apps/core/services/` por padrão nesta fase.
- helper privado em `views.py` ou extração mínima local é a abordagem preferencial.
- service novo só pode existir se aparecer duplicação concreta em pelo menos dois pontos reais do código durante a implementação.

## Ordem final dos patches
Ordem final escolhida:
1. consolidação de contexto do portal/core;
2. dispatcher aluno/governança;
3. resolvedor central mínimo por produto;
4. estado enxuto por produto;
5. governança MVP consolidada;
6. CTAs principais e compatibilidade transitória;
7. patch opcional de fechamento para entradas globais hardcoded fora do `core`.

Essa ordem é melhor porque primeiro estabiliza a base lógica do `core`, depois separa claramente aluno e staff, depois cria a entrada oficial por produto. Só então consolida o estado usado por essa entrada, ajusta a governança sobre base já estável e por fim migra CTAs. O patch 7 fica opcional porque depende do que ainda restar fora do eixo principal após os seis primeiros.

## 1. Objetivo da Fase 1
Consolidar o `core` como ponto oficial de entrada dos produtos, reduzindo a duplicação estrutural existente, sem criar camada paralela e sem deslocar para o `core` a lógica interna que continua pertencendo ao `vocacional`.

### Limite da fase
A Fase 1 deve:
- consolidar entrada oficial, navegação inicial e estado resumido por produto;
- separar claramente aluno e governança;
- transformar o `portal` em compatibilidade transitória;
- reaproveitar gating, permissões e ativos já existentes.

A Fase 1 não deve:
- reformar o fluxo interno do Vocacional;
- criar nova modelagem de produtos/acessos;
- criar detalhe genérico de produto;
- criar sistema visual genérico;
- abrir estrutura de services sem necessidade comprovada.

## 2. Escopo incluído
- consolidar a lógica repetida entre `portal()` e `portal_home()`;
- definir o `core` como entrada oficial por produto;
- criar um resolvedor central mínimo de entrada por produto;
- reaproveitar `apps/core/permissions`, `user_has_produto`, `onboarding_status` e `apps/vocacional/gating.py`;
- consolidar governança MVP a partir de `templates/portal/dashboard.html`;
- manter `portal` apenas como compatibilidade transitória;
- ajustar os principais CTAs globais para que parem de decidir o destino final diretamente;
- consolidar um estado enxuto por produto no `core`, via helper privado ou extração mínima local;
- preservar `templates/vocacional/ofertas_refinamento.html` como ativo do Vocacional;
- limitar a migração aos pontos principais de entrada global.

## 3. Escopo excluído
- refatoração interna de `apps/vocacional/views.py` além do mínimo inevitável;
- mudança de fluxo interno de avaliação, resultado, etapas, passes ou refinamento;
- criação de `produto_detalhe.html` genérico;
- criação de partials genéricas antes da segunda reutilização real;
- criação de CSS novo concorrente;
- mudança de `apps/contas/models.py` ou `apps/contas/models_acessos.py`;
- substituição de `templates/vocacional/ofertas_refinamento.html`;
- migração completa de links internos do Vocacional;
- criação de nova governança paralela a `dashboard.html`;
- criação de novo sistema de status, permissões ou acesso;
- criação de `apps/core/services/` por conveniência.

## 4. Decisões já fechadas para implementação
- `core` será a única entrada oficial de produto nesta fase.
- `portal` não será tratado como vitrine provisória consolidada.
- `portal` será apenas compatibilidade transitória.
- o resolvedor central nasce no `core`.
- a governança MVP reutiliza o dashboard atual, sem painel concorrente.
- o estado por produto nasce do jeito mais enxuto possível.
- helper privado em `views.py` é preferível a service novo.
- service novo só é permitido com duplicação concreta em dois pontos reais.
- os pontos globais de entrada têm prioridade sobre fluxos internos.
- nenhuma abstração visual genérica entra nesta fase.
- nenhum gating existente será recriado.

## 5. Ordem recomendada dos patches

### Patch 1. Consolidação do contexto do portal/core
Objetivo:
- eliminar duplicação entre `portal()` e `portal_home()`;
- centralizar a montagem de contexto e as decisões básicas de exibição.

Arquivos mais prováveis:
- `apps/core/views.py`

Risco principal:
- alterar sem perceber o comportamento atual de staff, onboarding ou acesso.

Critério de aceite:
- existe uma única fonte de montagem de contexto;
- `portal()` e `portal_home()` deixam de repetir a mesma estrutura;
- comportamento funcional permanece equivalente.

Dependência:
- nenhuma.

### Patch 2. Dispatcher explícito entre aluno e governança
Objetivo:
- tornar claro no `core` o papel de cada entrada:
  - aluno vai para a experiência oficial de produtos;
  - staff/superuser vai para governança, salvo modo user.

Arquivos mais prováveis:
- `apps/core/views.py`
- `escola_no_ar_site/urls.py`

Risco principal:
- quebrar o fluxo de staff/superuser ou o modo de teste.

Critério de aceite:
- staff/superuser não caem no funil do aluno por padrão;
- `portal_mode=user` continua funcionando;
- a intenção de cada rota fica clara.

Dependência:
- Patch 1.

### Patch 3. Resolvedor central mínimo por produto
Objetivo:
- introduzir uma rota/view no `core` para resolver a entrada oficial de cada produto;
- compor regras existentes sem recodificá-las.

Arquivos mais prováveis:
- `apps/core/views.py`
- `apps/core/urls.py`
- `escola_no_ar_site/urls.py` se necessário para exposição

Risco principal:
- duplicar `vocacional/gating.py` ou `core/permissions.py`.

Critério de aceite:
- o `core` decide o ponto oficial de entrada;
- a lógica usada vem das fontes já existentes;
- o Vocacional continua dono do fluxo após a entrada.

Dependência:
- Patch 1.

### Patch 4. Estado enxuto por produto
Objetivo:
- consolidar no `core` um estado resumido por produto para a entrada oficial;
- fazer isso com o menor nível de abstração possível.

Arquivos mais prováveis:
- `apps/core/views.py`
- helper privado no mesmo arquivo
- extração mínima local, apenas se necessária

Risco principal:
- criar um novo sistema de status paralelo ao gating e às permissões existentes.

Critério de aceite:
- o estado por produto é derivado das regras existentes;
- não há nova fonte de verdade;
- não nasce `apps/core/services/` sem duplicação concreta.

Dependência:
- Patch 1 e Patch 3.

### Patch 5. Governança MVP consolidada
Objetivo:
- consolidar a governança a partir de `templates/portal/dashboard.html`, sem criar painel concorrente;
- alinhar semanticamente dashboard atual e governança.

Arquivos mais prováveis:
- `apps/core/views.py`
- `templates/portal/dashboard.html`

Risco principal:
- manter dashboard e governança como dois conceitos paralelos.

Critério de aceite:
- existe uma única experiência oficial para staff/superuser;
- o dashboard atual exerce explicitamente o papel de governança MVP.

Dependência:
- Patch 2 e Patch 4.

### Patch 6. CTAs principais e compatibilidade transitória
Objetivo:
- fazer os cards principais deixarem de apontar diretamente para destinos internos;
- apontar para o resolvedor central;
- manter `portal` apenas como compatibilidade transitória.

Arquivos mais prováveis:
- `apps/core/templates/core/portal.html`
- `apps/core/views.py`
- eventualmente algum template global do `core`

Risco principal:
- ainda deixar atalhos diretos concorrentes na entrada oficial;
- manter `portal` semanticamente como segunda vitrine.

Critério de aceite:
- os CTAs principais passam pelo `core`;
- a entrada oficial deixa de decidir o fluxo final por conta própria;
- `portal` fica claramente rebaixado a compatibilidade transitória.

Dependência:
- Patch 3, Patch 4 e Patch 5.

### Patch 7. Fechamento opcional de entradas globais hardcoded
Objetivo:
- revisar entradas globais relevantes ainda hardcoded fora do `core`;
- migrar apenas o que ainda estiver escapando do eixo oficial.

Arquivos mais prováveis:
- `templates/vocacional/base_vocacional.html`
- `templates/vocacional/ofertas_refinamento.html`
- outros templates globais com papel de entrada

Risco principal:
- mexer em links internos legítimos do produto;
- ampliar escopo sem necessidade.

Critério de aceite:
- só é executado se restarem entradas globais relevantes fora do `core`;
- links internos do Vocacional permanecem íntegros.

Dependência:
- Patch 6.

## 6. Sequência mínima recomendada
1. Patch de consolidação de contexto do portal/core.
2. Patch de dispatcher aluno/governança.
3. Patch de resolvedor central mínimo por produto.
4. Patch de estado enxuto por produto.
5. Patch de governança MVP consolidada.
6. Patch de CTAs principais e compatibilidade transitória.
7. Patch opcional de fechamento, apenas se ainda restarem entradas globais relevantes hardcoded fora do `core`.

## 7. Critérios de revisão contra duplicação
Antes de aceitar qualquer patch, revisar:
- Isso cria nova fonte de verdade para acesso, onboarding ou status?
- Isso reimplementa regra já existente em `core/permissions`?
- Isso reimplementa regra já existente em `vocacional/gating.py`?
- Isso cria segunda vitrine oficial?
- Isso cria segundo painel oficial de governança?
- Isso cria detalhe de produto concorrente ao ativo existente do Vocacional?
- Isso cria CSS concorrente?
- Isso antecipa partial ou abstração visual sem segunda reutilização real?
- Isso move lógica interna do Vocacional para o `core`?
- Isso cria `apps/core/services/` por conveniência, sem duplicação concreta?
- Isso resolve problema real atual ou apenas antecipa generalização?

Se qualquer resposta indicar duplicação, concorrência ou abstração precoce, o patch deve ser reduzido, adiado ou refeito.

## 8. Checklist de compatibilidade
- `portal` continua acessível durante a transição.
- `portal` não compete como segunda vitrine oficial.
- `portal_dashboard` continua funcionando com papel claro de governança MVP.
- `portal_impersonar` e `portal_impersonar_sair` continuam íntegros.
- `staff/superuser` não caem no funil do aluno por padrão.
- `portal_mode=user` continua respeitado.
- `apps/contas` não é alterado como fonte de verdade.
- `user_has_produto` continua sendo reaproveitado.
- `onboarding_status` continua sendo reaproveitado.
- `apps/vocacional/gating.py` continua sendo reaproveitado.
- rotas internas do Vocacional continuam funcionando.
- `templates/vocacional/ofertas_refinamento.html` permanece ativo.
- não surge `produto_detalhe.html` genérico.
- não surge governança paralela.
- não surge vitrine paralela.
- não há quebra de login/logout e redirecionamento pós-login.
- não há quebra de onboarding legal e avaliação do guia.
- não há quebra de acesso Premium/refinamento.

## 9. Checklist de testes manuais
### Usuário comum sem acesso
- acessar a entrada pública;
- acessar `portal`;
- verificar a entrada oficial;
- clicar no CTA principal do Vocacional;
- confirmar que o fluxo passa pelo `core` e respeita as restrições existentes.

### Usuário com onboarding pendente
- entrar em `portal`;
- verificar status e CTA coerentes;
- clicar na entrada do Vocacional;
- confirmar encaminhamento correto para termos, privacidade ou avaliação do guia.

### Usuário com acesso completo
- entrar em `portal`;
- clicar no produto Vocacional;
- confirmar chegada ao ponto de entrada correto sem bypass indevido;
- confirmar continuidade normal dentro do Vocacional.

### Staff
- acessar `/portal/`;
- confirmar redirecionamento para governança por padrão;
- acessar modo user;
- testar impersonação;
- retornar para governança sem quebrar sessão ou papel.

### Superuser
- repetir os testes de staff;
- validar que o bypass continua respeitado onde já era previsto;
- validar que não entra no funil comum por padrão.

### Fluxo de entrada do Vocacional
- entrar no Vocacional pela entrada oficial;
- confirmar que o `core` faz a orquestração inicial;
- confirmar que, depois da entrada, o fluxo segue sendo do `vocacional`.

### Links principais da vitrine/portal
- revisar CTAs principais de produto;
- confirmar que não apontam direto para páginas internas quando deveriam passar pelo resolvedor;
- confirmar que links internos legítimos do Vocacional não foram alterados indevidamente.

## 10. Critério de pronto da Fase 1
A Fase 1 só pode ser considerada encerrada quando:
- o `core` exerce de forma clara a entrada oficial por produto;
- `portal()` e `portal_home()` deixaram de repetir a mesma lógica central;
- existe uma única experiência oficial de entrada;
- existe uma única experiência oficial de governança MVP para staff/superuser;
- o estado do usuário por produto está consolidado por composição, sem nova fonte de verdade;
- o Vocacional continua dono do fluxo interno sem regressão funcional;
- `apps/contas` continua intacto como fonte única de usuário, produto, acesso e permissões;
- os CTAs principais deixaram de decidir diretamente o destino final do produto;
- não foram criadas abstrações visuais ou estruturais sem reutilização real;
- não surgiu detalhe genérico concorrente ao ativo existente do Vocacional;
- a transição ficou compatível, reversível e auditável patch a patch.

Se ao fim ainda existirem duas vitrines com o mesmo papel, dois painéis oficiais de governança, novo gating paralelo, novo status paralelo ou movimentação indevida da lógica interna do Vocacional para o `core`, a Fase 1 não está pronta.

---

# Bloco B  Execução patch a patch

## Patch 1  Contexto Unificado do Core
**Objetivo**
- extrair e unificar a montagem de contexto hoje duplicada entre `portal()` e `portal_home()`.

**Arquivos mais prováveis**
- `apps/core/views.py`

**O que não pode acontecer**
- mudança de regra de acesso;
- mudança de bypass de staff;
- criação de service por conveniência.

**Critério de aceite**
- uma única base de contexto atende os dois caminhos;
- comportamento observado permanece equivalente.

**Teste manual mínimo**
- anônimo acessa entrada pública;
- usuário logado acessa `portal`;
- staff acessa `portal`.

**Condição para seguir**
- duplicação estrutural entre `portal()` e `portal_home()` foi removida sem regressão visível.

## Patch 2  Dispatcher Aluno e Governança
**Objetivo**
- explicitar a separação entre entrada do aluno e governança de staff/superuser.

**Arquivos mais prováveis**
- `apps/core/views.py`
- `escola_no_ar_site/urls.py`

**O que não pode acontecer**
- staff cair no funil do aluno por padrão;
- quebra de `portal_mode=user`;
- criação de nova governança concorrente.

**Critério de aceite**
- o roteamento aluno/governança fica claro e previsível.

**Teste manual mínimo**
- staff acessa `/portal/` e cai na governança;
- staff com `portal_mode=user` consegue acessar o modo usuário.

**Condição para seguir**
- a fronteira entre experiência do aluno e governança está estável.

## Patch 3  Resolvedor Central de Produto
**Objetivo**
- criar a entrada oficial de produto no `core`, sem reimplementar gating existente.

**Arquivos mais prováveis**
- `apps/core/views.py`
- `apps/core/urls.py`

**O que não pode acontecer**
- duplicação de `core/permissions`;
- duplicação de `vocacional/gating.py`;
- mover regra interna do Vocacional para o `core`.

**Critério de aceite**
- o `core` resolve a entrada oficial;
- o produto assume o fluxo após a entrada.

**Teste manual mínimo**
- clicar na entrada do Vocacional e confirmar que o caminho passa pelo `core`.

**Condição para seguir**
- existe um ponto central confiável para entrada por produto.

## Patch 4  Estado Enxuto por Produto
**Objetivo**
- compor no `core` o estado resumido necessário para a entrada oficial.

**Arquivos mais prováveis**
- `apps/core/views.py`

**O que não pode acontecer**
- nova fonte de verdade para status;
- criação automática de `apps/core/services/`;
- generalização precoce.

**Critério de aceite**
- o estado é derivado das regras existentes;
- a composição ficou legível e mínima.

**Teste manual mínimo**
- usuário sem acesso;
- usuário com onboarding pendente;
- usuário com acesso completo.

**Condição para seguir**
- o `core` já consegue exibir e decidir entrada com base em estado composto, sem duplicação.

## Patch 5  Governança MVP Consolidada
**Objetivo**
- consolidar o dashboard atual como governança oficial da fase.

**Arquivos mais prováveis**
- `apps/core/views.py`
- `templates/portal/dashboard.html`

**O que não pode acontecer**
- coexistência prática de dashboard e governança como papéis diferentes;
- criação de nova tela concorrente.

**Critério de aceite**
- existe uma única experiência oficial de governança para staff/superuser.

**Teste manual mínimo**
- staff acessa governança;
- superuser acessa governança;
- impersonação continua funcionando.

**Condição para seguir**
- governança está semanticamente consolidada e compatível.

## Patch 6  CTAs Principais e Compatibilidade Transitória
**Objetivo**
- trocar os CTAs principais para usar o resolvedor central;
- rebaixar o `portal` a compatibilidade transitória.

**Arquivos mais prováveis**
- `apps/core/templates/core/portal.html`
- `apps/core/views.py`

**O que não pode acontecer**
- CTAs principais continuarem decidindo destino direto;
- `portal` continuar atuando como segunda vitrine.

**Critério de aceite**
- os pontos principais de entrada passam pelo `core`;
- `portal` fica claramente em papel de compatibilidade.

**Teste manual mínimo**
- revisar clique principal do Vocacional e demais CTAs centrais da entrada.

**Condição para seguir**
- a entrada oficial do sistema já está controlada pelo `core`.

## Patch 7  Fechamento Opcional de Hardcodes Globais
**Objetivo**
- migrar entradas globais relevantes remanescentes fora do `core`, se elas ainda existirem.

**Arquivos mais prováveis**
- `templates/vocacional/base_vocacional.html`
- `templates/vocacional/ofertas_refinamento.html`
- outros templates globais equivalentes

**O que não pode acontecer**
- alteração de links internos legítimos do Vocacional;
- expansão artificial de escopo.

**Critério de aceite**
- só é executado se houver hardcodes globais relevantes remanescentes;
- o eixo oficial fica limpo sem mexer no fluxo interno do produto.

**Teste manual mínimo**
- revisar entradas globais remanescentes e validar que o Vocacional segue íntegro.

**Condição para seguir**
- não restam entradas globais relevantes fora do eixo oficial, ou ficou demonstrado que não há necessidade deste patch.

Essa é a base oficial de execução da Fase 1.
