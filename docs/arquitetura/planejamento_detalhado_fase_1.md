# Planejamento Detalhado e Operacional da Fase 1

## 1. Objetivo da Fase 1

## Objetivo arquitetural
Consolidar o `core` como ponto oficial de entrada dos produtos, reduzindo a duplicação estrutural já existente, sem criar camada paralela e sem deslocar para o `core` a lógica interna que continua pertencendo ao `vocacional`.

## Limite da fase
A Fase 1 deve:
- consolidar entrada, navegação inicial e estado resumido por produto;
- separar melhor aluno e governança;
- transformar o portal atual em compatibilidade transitória ou vitrine provisória consolidada;
- reaproveitar integralmente gating, permissões e ativos operacionais já existentes.

A Fase 1 não deve:
- reformar o fluxo interno do Vocacional;
- criar nova modelagem de produtos/acessos;
- criar sistema visual genérico antecipado;
- criar detalhe de produto genérico no `core`.

---

## 2. Escopo incluído

- consolidar a lógica repetida entre `portal()` e `portal_home()`;
- definir o `core` como entrada oficial por produto;
- criar um resolvedor central mínimo de entrada por produto;
- reaproveitar `apps/core/permissions`, `user_has_produto`, `onboarding_status` e `apps/vocacional/gating.py`;
- consolidar governança MVP a partir de `templates/portal/dashboard.html`;
- manter `portal` como compatibilidade transitória, sem deixá-lo competir como segunda vitrine;
- ajustar os principais CTAs globais para que parem de decidir o destino final diretamente;
- consolidar um estado enxuto por produto no `core`, via helper privado ou service mínimo;
- preservar `templates/vocacional/ofertas_refinamento.html` como ativo do Vocacional;
- limitar a migração nesta fase aos pontos principais de entrada global.

## 3. Escopo excluído

- refatoração interna de `apps/vocacional/views.py` além do mínimo necessário;
- mudança de fluxo interno de avaliação, resultado, etapas, passes ou refinamento;
- criação de `produto_detalhe.html` genérico;
- criação de partials genéricas de produto antes de segunda reutilização real;
- criação de CSS novo concorrente ao já existente;
- mudança de `apps/contas/models.py` ou `apps/contas/models_acessos.py`;
- substituição de `templates/vocacional/ofertas_refinamento.html`;
- migração completa de links internos do Vocacional;
- criação de nova governança paralela a `dashboard.html`;
- criação de novo sistema de status, permissões ou acesso.

## 4. Decisões já fechadas para implementação

- `core` será a única entrada oficial de produto nesta fase.
- `vocacional` continua dono do fluxo interno.
- `apps/contas` continua sendo a fonte única de usuário, produto, acesso e permissões.
- a governança MVP partirá de `templates/portal/dashboard.html`.
- `templates/vocacional/ofertas_refinamento.html` permanece como ativo de detalhe/oferta do Vocacional.
- o estado por produto será implementado do jeito mais enxuto possível, preferencialmente como helper privado ou service mínimo.
- `portal` pode existir como compatibilidade transitória, mas não como segunda vitrine oficial.
- os patches da fase devem atacar primeiro os pontos globais de entrada, não os fluxos internos do produto.
- nenhuma abstração visual genérica entra sem segunda reutilização real.
- nenhum gating existente será recriado.

## 5. Ordem recomendada dos patches

## Patch 1. Consolidação do contexto do portal/core
**Objetivo**
- eliminar a duplicação entre `portal()` e `portal_home()`;
- centralizar a montagem de contexto e das decisões básicas de exibição.

**Arquivos/camadas mais prováveis**
- `apps/core/views.py`

**Risco principal**
- mudar sem perceber o comportamento atual de staff, onboarding ou acesso.

**Critério de aceite**
- existe uma única fonte de montagem de contexto;
- `portal()` e `portal_home()` não repetem mais a mesma lógica estrutural;
- comportamento funcional permanece equivalente.

**Dependência**
- nenhuma.

## Patch 2. Dispatcher explícito entre aluno e governança
**Objetivo**
- tornar claro no `core` o papel de cada entrada:
  - aluno vai para a experiência oficial de produtos;
  - staff/superuser vai para governança, salvo modo user.

**Arquivos/camadas mais prováveis**
- `apps/core/views.py`
- `escola_no_ar_site/urls.py`

**Risco principal**
- quebrar o fluxo de staff/superuser ou o modo de teste.

**Critério de aceite**
- staff/superuser não caem no funil do aluno por padrão;
- `portal_mode=user` continua funcionando;
- a intenção de cada rota fica mais clara.

**Dependência**
- Patch 1.

## Patch 3. Resolvedor central mínimo por produto
**Objetivo**
- introduzir uma rota/view no `core` para resolver a entrada oficial de cada produto;
- compor regras existentes sem recodificá-las.

**Arquivos/camadas mais prováveis**
- `apps/core/views.py`
- `apps/core/urls.py`
- possivelmente um helper mínimo em `apps/core/views.py` ou `apps/core/services/` se houver duplicação real

**Risco principal**
- duplicar `vocacional/gating.py` ou `core/permissions.py`.

**Critério de aceite**
- o `core` passa a decidir o ponto oficial de entrada;
- a lógica usada vem das fontes já existentes;
- o Vocacional continua dono do fluxo após a entrada.

**Dependência**
- Patch 1.

## Patch 4. Governança MVP consolidada
**Objetivo**
- consolidar a governança a partir de `templates/portal/dashboard.html`, sem criar painel concorrente;
- alinhar semanticamente dashboard atual e governança.

**Arquivos/camadas mais prováveis**
- `apps/core/views.py`
- `templates/portal/dashboard.html`

**Risco principal**
- manter dashboard e governança como dois conceitos paralelos na prática.

**Critério de aceite**
- existe uma única experiência oficial para staff/superuser;
- o dashboard atual passa a exercer explicitamente o papel de governança MVP.

**Dependência**
- Patch 2.

## Patch 5. Estado enxuto por produto no core
**Objetivo**
- consolidar no `core` um estado resumido por produto para a vitrine oficial;
- fazer isso com o menor nível de abstração possível.

**Arquivos/camadas mais prováveis**
- `apps/core/views.py`
- opcionalmente helper privado no mesmo arquivo
- opcionalmente micro-service se a extração já estiver justificada

**Risco principal**
- criar um novo sistema de status paralelo ao gating e às permissões existentes.

**Critério de aceite**
- o estado por produto é derivado das regras existentes;
- não há duplicação de regra nem nova fonte de verdade;
- a composição fica mais legível e reaproveitável.

**Dependência**
- Patch 1 e Patch 3.

## Patch 6. Atualização dos CTAs principais da vitrine/portal
**Objetivo**
- fazer os cards principais deixarem de apontar diretamente para destinos internos;
- apontar para o resolvedor central.

**Arquivos/camadas mais prováveis**
- `apps/core/templates/core/portal.html`
- possivelmente `templates/base.html` se houver CTA global relevante

**Risco principal**
- ainda deixar atalhos diretos concorrentes na vitrine oficial.

**Critério de aceite**
- os CTAs principais passam pelo `core`;
- a vitrine deixa de decidir o fluxo final por conta própria.

**Dependência**
- Patch 3 e Patch 5.

## Patch 7. Compatibilidade transitória e limpeza de entrada global
**Objetivo**
- revisar os principais pontos globais de entrada ainda hardcoded;
- migrar apenas os que têm papel de entrada oficial, preservando links internos legítimos do Vocacional.

**Arquivos/camadas mais prováveis**
- `templates/vocacional/base_vocacional.html`
- `templates/vocacional/ofertas_refinamento.html`
- outros templates globais que apontem diretamente para o produto

**Risco principal**
- mexer em links internos do produto que não deveriam ser alterados nesta fase.

**Critério de aceite**
- entradas globais relevantes usam o resolvedor;
- links internos do Vocacional permanecem íntegros.

**Dependência**
- Patch 6.

## 6. Sequência mínima recomendada

1. **Patch de consolidação de contexto do portal/core**
   - remover duplicação entre `portal()` e `portal_home()`;
   - criar base estável para os demais patches.

2. **Patch de dispatcher aluno/governança**
   - explicitar o papel de `portal`, `portal_home` e governança;
   - estabilizar o comportamento de staff/superuser.

3. **Patch de resolvedor central mínimo por produto**
   - criar a entrada oficial por produto no `core`;
   - sem criar service excessivo.

4. **Patch de estado enxuto por produto**
   - encapsular, por composição, o status usado na vitrine;
   - ainda sem arquitetura ampla de services se não houver segunda reutilização.

5. **Patch de governança MVP consolidada**
   - consolidar o dashboard atual como governança oficial da fase.

6. **Patch de CTAs principais e vitrine transitória**
   - trocar links diretos da vitrine/portal para o resolvedor;
   - assegurar que `portal` não atue como segunda vitrine concorrente.

7. **Patch de compatibilidade de entradas globais**
   - revisar atalhos principais fora do `core`;
   - migrar só o que for entrada oficial.

## 7. Critérios de revisão contra duplicação

Antes de aceitar qualquer patch, revisar:

- Isso cria uma nova fonte de verdade para acesso, onboarding ou status?
- Isso reimplementa regra já existente em `core/permissions`?
- Isso reimplementa regra já existente em `vocacional/gating.py`?
- Isso cria uma segunda vitrine oficial?
- Isso cria um segundo painel oficial de governança?
- Isso cria um detalhe de produto concorrente ao ativo já existente do Vocacional?
- Isso cria CSS concorrente ao já existente?
- Isso cria partial ou abstraction visual sem segunda reutilização real?
- Isso move lógica interna do Vocacional para o `core`?
- Isso resolve um problema concreto atual ou apenas antecipa generalização?
- Isso melhora a centralização sem aumentar a opacidade?
- Isso mantém compatibilidade com `apps/contas` como fonte única?

Se qualquer resposta for “sim” para duplicação, concorrência ou antecipação desnecessária, o patch deve ser reduzido, adiado ou refeito.

## 8. Checklist de compatibilidade

- `portal` continua acessível durante a transição.
- `portal` não compete semanticamente como segunda vitrine oficial.
- `portal_dashboard` continua funcionando, agora com papel claro de governança MVP.
- `portal_impersonar` e `portal_impersonar_sair` continuam íntegros.
- `staff/superuser` não caem no funil do aluno por padrão.
- `portal_mode=user` continua respeitado.
- `apps/contas` não é alterado como fonte de verdade.
- `user_has_produto` continua sendo reaproveitado.
- `onboarding_status` continua sendo reaproveitado.
- `apps/vocacional/gating.py` continua sendo reaproveitado.
- rotas internas do Vocacional continuam funcionando.
- `templates/vocacional/ofertas_refinamento.html` permanece ativo.
- não surge `produto_detalhe.html` genérico nesta fase.
- não surge governança paralela.
- não surge vitrine oficial paralela.
- não há quebra de login/logout e redirecionamento pós-login.
- não há quebra de onboarding legal e avaliação do guia.
- não há quebra de acesso Premium/refinamento já existente.

## 9. Checklist de testes manuais

## Usuário comum sem acesso
- acessar a entrada pública;
- acessar `portal`;
- verificar a vitrine/entrada oficial;
- clicar no CTA principal do Vocacional;
- confirmar que o fluxo passa pelo `core` e respeita as restrições existentes.

## Usuário com onboarding pendente
- entrar em `portal`;
- verificar status e CTA coerentes;
- clicar na entrada do Vocacional;
- confirmar que o sistema encaminha corretamente para termos, privacidade ou avaliação do guia conforme a regra atual.

## Usuário com acesso completo
- entrar em `portal`;
- clicar no produto Vocacional;
- confirmar que chega ao ponto de entrada correto sem bypass indevido;
- confirmar continuidade normal dentro do Vocacional.

## Staff
- acessar `/portal/`;
- confirmar redirecionamento para governança por padrão;
- acessar modo user;
- testar impersonação;
- retornar para governança sem quebrar sessão ou papel.

## Superuser
- repetir os testes de staff;
- validar que o bypass continua respeitado onde já era previsto;
- validar que não entra no funil comum por padrão.

## Fluxo de entrada do Vocacional
- entrar no Vocacional pela vitrine oficial;
- confirmar que o `core` faz a orquestração inicial;
- confirmar que, após a entrada, o fluxo segue sendo do `vocacional`.

## Links principais da vitrine/portal
- revisar CTAs principais de produto;
- confirmar que não apontam direto para páginas internas quando deveriam passar pelo resolvedor;
- confirmar que links internos legítimos do Vocacional não foram alterados indevidamente.

## 10. Critério de pronto da Fase 1

A Fase 1 só pode ser considerada encerrada quando:

- o `core` passou a exercer de forma clara a entrada oficial por produto;
- `portal()` e `portal_home()` deixaram de repetir a mesma lógica central;
- existe uma única experiência oficial de vitrine/entrada;
- existe uma única experiência oficial de governança MVP para staff/superuser;
- o estado do usuário por produto está consolidado por composição, sem nova fonte de verdade;
- o Vocacional continua dono do fluxo interno sem regressão funcional;
- `apps/contas` continua intacto como fonte única de usuário, produto, acesso e permissões;
- os CTAs principais deixaram de decidir diretamente o destino final do produto;
- não foram criadas abstrações visuais ou estruturais sem reutilização real;
- não surgiu detalhe genérico concorrente ao ativo existente do Vocacional;
- a transição ficou compatível, reversível e auditável patch a patch.

## Encerramento operacional da fase
Se ao fim da implementação ainda existirem:
- duas vitrines com o mesmo papel,
- dois painéis oficiais de governança,
- novo gating paralelo,
- novo status paralelo,
- ou movimentação indevida da lógica interna do Vocacional para o `core`,

então a Fase 1 não está pronta, mesmo que o código esteja funcionando.
