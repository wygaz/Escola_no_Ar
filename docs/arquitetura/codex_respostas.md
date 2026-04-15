## Índice

- `resposta_apos_1o_cheklist.md`
- `resposta_apos_1o_cheklist_2.md`
- aprovação do Patch 1 com travas adicionais
- autorização para seguir com o Patch 2
- autorização para seguir com o Patch 3
- planejamento rápido do Patch 4
- aprovação do Patch 4
- `algumas_informacoes_regras_de_negocio_e erro_navegacao.md`
- `patch_semantico_do_gating.md`
- `relatorio2_adendo_micro-patch_isolado_de_pos-login_e_Wireframe.md`

## Resposta à intervenção: `resposta_apos_1o_cheklist.md`

### 1. Evidências confirmadas

Bypasses centrais da vitrine/portal para rotas internas, confirmados em `templates/core/portal.html`:

- Sonhe + Alto autenticado: `templates/core/portal.html:108`
  Trecho: `href="{% url 'projeto21:home' %}"`
  Contexto: botão principal `Entrar` do card quando `can_sonhemaisalto`.

- Sonhe + Alto anônimo: `templates/core/portal.html:119`
  Trecho: `href="{% url 'contas:login' %}?next={% url 'projeto21:home' %}"`
  Contexto: login já com `next` para rota interna do produto.

- Vocacional autenticado: `templates/core/portal.html:133`
  Trecho: `href="{% url 'vocacional:etapas' %}"`
  Contexto: botão principal `Entrar` do card quando `can_vocacional`.

- Vocacional anônimo: `templates/core/portal.html:144`
  Trecho: `href="{% url 'contas:login' %}?next={% url 'vocacional:etapas' %}"`
  Contexto: login já com `next` para rota interna do produto.

O resolvedor central existe e deveria ser o eixo oficial em `escola_no_ar_site/urls.py:15` e `apps/core/views.py:443`, mas os cards ainda o bypassam.

Evidência adicional de incoerência de entrada:

- A raiz ainda aponta para `portal`: `escola_no_ar_site/urls.py:11`
- Existe uma `home_funil()` já preparada para levar anônimo ao login: `apps/core/views.py:338`
- Essa view não está sendo usada pela rota raiz.

### 2. Conflito de regra validado

A prioridade atual está definida aqui:

- Gate de acesso: `apps/core/views.py:25`
  Ordem atual:
  1. `onboarding_status(...)`
  2. se `not has_onboarding`: bloqueia
  3. se `setting_flag=True`: exige `user_has_produto(...)`
  4. senão libera

- CTA de bloqueio: `apps/core/views.py:45`
  Ordem atual:
  1. `has_legal`
  2. `has_guia_feedback`
  3. entitlement/produto
  4. fallback genérico

Por que isso conflita:

- Se o usuário recebeu acesso por entitlement/admin, `user_has_produto(...)` pode já ser verdadeiro.
- Mesmo assim, `_can_access_app()` bloqueia antes, porque `has_onboarding` vem primeiro.
- E `_portal_locked_cta()` manda para `legal_aceite` ou `guia_avaliacao` antes de considerar que o produto já foi concedido.

Distinção conceitual correta:

- Pendência de onboarding: itens de regularização do usuário, não necessariamente impeditivos para todo caso.
- Acesso concedido por entitlement/admin: liberação efetiva do produto.
- Gating de produto: regra de entrada daquele produto específico.
- Fluxo vindo do Guia: caminho comercial/orientado por compra do Guia, não sinônimo de toda forma válida de acesso.

Hoje essas quatro coisas estão parcialmente colapsadas numa mesma regra.

### 3. Classificação dos problemas

#### A. Problemas funcionais

- Usuário com acesso concedido por admin pode ser forçado a fazer onboarding do Guia antes de entrar no produto.
- Anônimo faz login com `next` para rota interna, sem passar pelo resolvedor.
- CTA principal do portal ainda decide destino final por conta própria.

#### B. Problemas arquiteturais

- O resolvedor central existe, mas não é a única entrada real.
- A raiz `"/"` ainda não usa a estratégia `home_funil()`.
- O `core` ainda centraliza só parte da orquestração; a vitrine continua com bypasses.

#### C. Problemas de UX/conteúdo

- A entrada ainda comunica “portal operacional”, não “jornada”.
- A caixa de pendências duplica informação em lista e chips em `templates/core/portal.html:43`.
- O aceite legal ainda empurra para uma tela separada, apesar da direção já validada no checklist.

### 4. Mini-plano de correção por patch

#### Patch 1: Regra de acesso alinhada

- Objetivo: separar onboarding, entitlement e gating sem recriar regra do zero.
- Entra: revisão de `_can_access_app`, `_portal_locked_cta`, flags de atenção.
- Não entra: redesign visual grande.
- Arquivos prováveis: `apps/core/views.py`
- Risco principal: alterar comportamento legítimo de onboarding.
- Critério de aceite: acesso concedido por entitlement/admin não é barrado indevidamente pelo fluxo do Guia.

#### Patch 2: CTAs passam pelo resolvedor

- Objetivo: eliminar bypasses centrais do portal.
- Entra: troca dos botões principais e dos `next=` anônimos para `produto_resolver`.
- Não entra: mexer em links internos legítimos do Vocacional.
- Arquivos prováveis: `templates/core/portal.html`
- Risco principal: quebrar navegação anônima ou pós-login.
- Critério de aceite: cards principais do portal não apontam mais direto para `projeto21:home` nem `vocacional:etapas`.

#### Patch 3: Entrada pública coerente

- Objetivo: alinhar `"/"` com a intenção atual de entrada.
- Entra: decidir e aplicar `home_funil()` ou equivalente na rota raiz.
- Não entra: novo template grande de vitrine.
- Arquivos prováveis: `escola_no_ar_site/urls.py`, `apps/core/views.py`
- Risco principal: contradizer fluxo atual validado de usuários autenticados.
- Critério de aceite: `"/"` e `"/portal/"` têm papéis claros e não concorrentes.

#### Patch 4: Pendências enxutas no portal

- Objetivo: reduzir duplicação e preparar o encaixe do wireframe sem redesign completo.
- Entra: simplificação da área de pendências e integração melhor do aceite/continuação.
- Não entra: hero novo, modais, nova linguagem visual completa.
- Arquivos prováveis: `templates/core/portal.html`, talvez `apps/core/views.py`
- Risco principal: misturar correção funcional com redesign amplo.
- Critério de aceite: portal mostra apenas pendências relevantes, sem duplicação desnecessária, e já fica compatível com a direção do wireframe.

#### Patch 5: Entrada acolhedora controlada

- Objetivo: aplicar o wireframe depois de estabilizar regra e navegação.
- Entra: conteúdo, hierarquia e CTA principal variável por estado.
- Não entra: nova camada paralela de templates/serviços.
- Arquivos prováveis: `templates/core/portal.html` e CSS local/compartilhado mínimo.
- Risco principal: embelezar antes de consolidar o eixo funcional.
- Critério de aceite: a página comunica jornada e próximo passo sem reintroduzir bypass ou duplicação.

## Resposta à intervenção: `resposta_apos_1o_cheklist_2.md`

### Plano curto do Patch 1

#### 1. Funções que serão tocadas

- `apps/core/views.py:_can_access_app`
- `apps/core/views.py:_portal_locked_cta`
- `apps/core/views.py:_build_product_state`
- `apps/core/views.py:_apply_portal_attention_flags`
- `apps/core/views.py:_build_portal_user_context`

Escopo provável real: concentrado principalmente nas duas primeiras; as demais só para manter coerência do estado exibido no portal.

#### 2. Mudança conceitual da prioridade

Prioridade atual:

1. onboarding do Guia
2. entitlement/produto
3. entrada no produto

Prioridade proposta:

1. distinguir primeiro se o usuário já tem acesso efetivo ao produto por entitlement/admin;
2. se já tem acesso efetivo, não forçar artificialmente `guia_feedback` como pré-condição universal;
3. manter pendências de onboarding visíveis no portal quando ainda fizerem sentido, mas sem bloquear indevidamente um acesso já concedido;
4. continuar respeitando o gating específico do produto quando o acesso ainda não foi concedido.

Em termos práticos:

- `has_legal` continua sendo pendência séria e deve ser tratada com cautela;
- `has_guia_feedback` deixa de ser gatilho universal quando o produto já foi liberado por entitlement/admin;
- `user_has_produto(...)` passa a participar antes da decisão de empurrar o usuário para “Avaliação do Guia”;
- não haverá “liberação irrestrita”: a exceção vale para o produto efetivamente concedido, não para todo o ecossistema.

#### 3. Risco principal

Abrir exceção demais e enfraquecer onboarding legítimo para casos normais vindos do Guia.

Mitigação:

- alterar só a prioridade mínima necessária;
- limitar a exceção ao produto específico que já está concedido;
- não mexer no gating interno do Vocacional;
- não criar novas fontes de verdade fora das regras já existentes.

#### 4. Critério de aceite

- Usuário com acesso concedido por entitlement/admin a um produto não é mais forçado para `guia_avaliacao` antes de entrar nesse produto.
- Usuário sem acesso concedido continua vendo o fluxo normal de onboarding/comercial.
- O portal continua exibindo pendências reais sem transformar todas em bloqueio universal.
- Não surge regra paralela nem `service` novo.

#### 5. Smoke test mínimo

1. Usuário normal sem produto concedido:
   continua sendo direcionado para termos/guia/compra conforme a regra atual.

2. Usuário com `user_has_produto(...) = True` para Vocacional, sem compra do Guia e sem `has_guia_feedback`:
   consegue entrar no Vocacional sem ser forçado para Avaliação do Guia.

3. Usuário com `user_has_produto(...) = True` para Sonhe + Alto, sem compra do Guia e sem `has_guia_feedback`:
   consegue entrar no Sonhe + Alto sem ser forçado para Avaliação do Guia.

4. Usuário sem `has_legal`:
   continua recebendo tratamento de pendência legal conforme a regra definida para este patch.

5. Staff/superuser com `portal_mode=user`:
   continua respeitando a mesma lógica de usuário, sem bypass indevido novo.

## Resposta à intervenção: aprovação do Patch 1 com travas adicionais

### Implementação realizada

Arquivos alterados:

- `apps/core/views.py`
- `templates/core/portal.html`

Mudança aplicada:

- `has_legal` continua sendo bloqueio separado e não entrou por efeito colateral na exceção.
- A exceção passou a valer apenas para `guia_feedback` quando o usuário já possui acesso efetivo ao produto específico por entitlement/admin.
- A sinalização de pendência no portal deixou de tratar `guia_feedback` como bloqueio universal; agora ela acompanha o bloqueio real por produto.

### Efeito funcional esperado

- Usuário com entitlement/admin para Vocacional pode entrar no Vocacional sem ser forçado para “Avaliação do Guia”, desde que a pendência legal não exista.
- Usuário com entitlement/admin para Sonhe + Alto pode entrar no Sonhe + Alto sem ser forçado para “Avaliação do Guia”, desde que a pendência legal não exista.
- Isso não libera automaticamente outros produtos não concedidos.

### Limitação de validação local

Não consegui concluir `py_compile` nem `manage.py check` porque o `venv` atual aponta para um Python-base inexistente:

- `venv/pyvenv.cfg` referencia `C:\Users\Wanderley\AppData\Local\Programs\Python\Python312\python.exe`
- esse executável não está disponível no ambiente atual

Ou seja, a limitação de validação nesta etapa é do ambiente Python, não do patch em si.

## Resposta à intervenção: autorização para seguir com o Patch 2

### Implementação realizada

Arquivo alterado:

- `templates/core/portal.html`

Mudança aplicada:

- os botões principais do card de Sonhe + Alto agora apontam para `produto_resolver('sonhe-mais-alto')`;
- o fluxo anônimo de Sonhe + Alto agora faz login com `next` para o resolvedor, não para `projeto21:home`;
- os botões principais do card de Vocacional agora apontam para `produto_resolver('vocacional')`;
- o fluxo anônimo de Vocacional agora faz login com `next` para o resolvedor, não para `vocacional:etapas`.

### Evidência objetiva pós-patch

Em `templates/core/portal.html`:

- `:110` Sonhe + Alto autenticado -> `produto_resolver`
- `:120` Sonhe + Alto anônimo -> login com `next=produto_resolver`
- `:135` Vocacional autenticado -> `produto_resolver`
- `:145` Vocacional anônimo -> login com `next=produto_resolver`

### Resultado arquitetural

Os quatro bypasses centrais identificados no portal foram removidos.
O resolvedor central passa a ser a entrada dos CTAs principais da vitrine atual, sem mexer em links internos legítimos dos produtos.

### Validação manual confirmada

Smoke test aprovado com clique real:

1. anônimo -> Sonhe + Alto
2. anônimo -> Vocacional
3. autenticado -> Sonhe + Alto
4. autenticado -> Vocacional

Todos os quatro cenários foram validados como OK.

## Resposta à intervenção: autorização para seguir com o Patch 3

### Implementação realizada

Arquivo alterado:

- `escola_no_ar_site/urls.py`

Mudança aplicada:

- a rota raiz `""` deixou de apontar para `core_views.portal`;
- a rota raiz agora aponta para `core_views.home_funil`.

### Efeito esperado

- usuário anônimo em `"/"` vai para login;
- usuário autenticado em `"/"` vai para `"/portal/"`;
- `"/portal/"` continua sendo a experiência autenticada controlada pelo `core`;
- a raiz deixa de competir semanticamente com o portal autenticado.

### Critério de aceite deste patch

- `"/"` e `"/portal/"` passam a ter papéis claros e não concorrentes;
- a navegação autenticada validada nos patches anteriores permanece intacta;
- não há redesign visual nem nova camada paralela.

### Smoke test mínimo sugerido

1. anônimo acessa `"/"` e vai para login;
2. autenticado acessa `"/"` e vai para `"/portal/"`;
3. staff acessa `"/"` e, após autenticação, mantém o comportamento de governança já validado;
4. `"/portal/"` continua funcionando como antes.

## Resposta à intervenção: planejamento rápido do Patch 4

### Objetivo

Enxugar a área de pendências do portal para remover duplicação e deixar a leitura mais direta, sem redesign amplo e sem mudar o eixo funcional já validado nos patches 1 a 3.

### O que entra

- simplificar a caixa de pendências em `templates/core/portal.html`;
- remover a duplicação entre lista vertical e chips quando estiverem comunicando a mesma pendência;
- manter apenas os itens realmente pendentes;
- preservar os links/CTAs já corretos para cada pendência;
- ajustar o contexto em `apps/core/views.py` apenas se for necessário para sustentar essa simplificação.

### O que não entra

- novo hero;
- wireframe acolhedor completo;
- modais “Saiba mais”;
- mudança grande de hierarquia visual da página;
- nova regra de acesso;
- alteração do resolvedor ou da rota raiz.

### Arquivos mais prováveis

- `templates/core/portal.html`
- `apps/core/views.py` apenas se algum helper/contexto precisar ficar mais enxuto

### Mudança conceitual

A caixa de pendências deve deixar de funcionar como “lista + repetição resumida da mesma lista”.
Ela passa a funcionar como um bloco único de orientação operacional:

- cada pendência aparece uma vez, com ação clara;
- só aparece o que realmente ainda falta;
- pendência informativa não deve competir com CTA principal do produto;
- o portal continua informando, mas com menos ruído.

### Risco principal

Remover informação demais e empobrecer a clareza do onboarding atual.

Mitigação:

- preservar todos os estados pendentes já existentes;
- mexer primeiro na duplicação, não na lógica;
- manter os links de ação explícitos;
- evitar qualquer redesign estrutural maior neste patch.

### Critério de aceite

- a área de pendências continua correta para os mesmos estados já suportados;
- cada pendência relevante aparece uma única vez;
- não há repetição visual desnecessária da mesma informação;
- nenhum CTA funcional é perdido;
- o portal fica mais limpo sem alterar o fluxo validado.

### Smoke test mínimo

1. usuário com `has_legal=False`
2. usuário com `show_guia_feedback_pending=True`
3. usuário com `need_bonus_voc=True`
4. usuário com `need_bonus_sma=True`
5. usuário com múltiplas pendências combinadas
6. usuário sem pendências, confirmando que a caixa some

## Resposta à intervenção: aprovação do Patch 4

### Implementação realizada

Arquivo alterado:

- `templates/core/portal.html`

Mudança aplicada:

- a área de pendências deixou de ter dois blocos comunicando a mesma coisa;
- os antigos chips de status/ação foram removidos;
- cada pendência agora aparece uma única vez, já com ação embutida no próprio item;
- os links funcionais foram preservados:
  - `core:legal_aceite`
  - `vocacional:guia_avaliacao`
  - `guia`

### O que não mudou

- nenhuma regra de acesso foi alterada neste patch;
- nenhum CTA principal de produto foi alterado;
- não houve redesign amplo do portal;
- o wireframe acolhedor continua para a próxima etapa, separado deste ajuste.

### Critério de aceite esperado

- a caixa continua aparecendo só quando `show_attention=True`;
- cada pendência relevante aparece uma única vez;
- o portal fica mais limpo, sem perder ação funcional;
- o fluxo validado nos patches 1 a 3 permanece intacto.

## Resposta à intervenção: `algumas_informacoes_regras_de_negocio_e erro_navegacao.md`

### 1. Regra revisada

A regra corrigida faz sentido e corrige um desvio semântico do entendimento anterior.

Sequência correta:

1. `has_legal`
2. possui Guia válido como pré-requisito
3. `has_guia_feedback`
4. gating específico do produto/bônus

O ponto central é este:

- “possui Guia” não é igual a “comprou o Guia”;
- “possui Guia” também não é igual a “já tem bônus”;
- “possui Guia” deve significar pré-requisito válido do programa, seja por compra, seja por concessão administrativa.

Também fica corrigido que:

- bônus concedido por admin não dispensa Avaliação do Guia;
- mas usuário sem Guia válido não deve cair em Avaliação do Guia antes de resolver a posse válida do Guia.

### 2. Impactos no sistema

#### Gating

Hoje a lógica ainda confunde essas camadas em dois pontos:

- `apps/core/permissions.py:64-69`
  O Guia é tratado como equivalência que libera `vocacional75` e `sonhemaisalto`, e vice-versa na prática de checagem.
- `apps/core/permissions.py:200-210`
  `onboarding_status()` conhece apenas `has_legal` e `has_guia_feedback`; não conhece explicitamente “possui Guia válido”.
- `apps/core/views.py`
  O portal já foi parcialmente ajustado, mas ainda depende dessas premissas de `permissions.py`.
- `apps/vocacional/gating.py:51-67`
  A ordem atual está descrita como `bonus -> legal -> guia -> ok`, o que conflita com a regra corrigida.

#### Governança

Hoje não há uma noção explícita de “ao conceder bônus por admin, garantir posse válida do Guia”.
O admin atual de acessos em `apps/contas/admin.py:87-102` só cadastra `Acesso`; não existe ação assistida para coerência do pré-requisito.

#### Admin de concessão

Em `apps/contas/models_acessos.py`, `Acesso` é genérico e suficiente para suportar a regra, mas o fluxo administrativo ainda não ajuda o operador a:

- conceder Guia junto com bônus;
- sinalizar a origem administrativa do Guia;
- preparar/disparar envio do Guia por e-mail.

#### Status do usuário

Hoje falta um estado explícito entre:

- `has_legal`
- `has_guia_feedback`
- `has_prod_voc` / `has_prod_sma`

Esse estado intermediário é “possui Guia válido”.
Sem ele, o sistema continua misturando:

- compra do Guia,
- posse válida do Guia,
- bônus/produto liberado.

#### Erro de navegação concreto

Há também um bug real e independente da regra:

- `apps/core/views.py:708`
  `guia_redirect_preview()` chama `static(...)`, mas `static` não está importado.
- Efeito: `/guia/` gera `500 NameError`, como mostrado no log.

### 3. Ajuste curto recomendado

Sem abrir camada paralela:

1. introduzir no eixo atual uma checagem explícita de “possui Guia válido”;
2. fazer `onboarding_status()` e o gating do portal/vocacional distinguirem:
   - legal
   - guia válido
   - avaliação do Guia
   - produto específico
3. parar de depender de equivalência implícita “bônus == Guia” para decidir pré-requisito do programa;
4. tratar o bug de `/guia/` como correção imediata separada e pequena;
5. deixar a automação assistida do admin como frente específica de governança, não misturada no mesmo patch semântico.

### 4. Etapa sugerida

Minha recomendação:

- Ainda cabe no fechamento da fase atual:
  - corrigir a semântica de gating no `core` e no `vocacional`;
  - corrigir o bug de `/guia/`.

- Deve virar próxima frente específica de governança/admin:
  - automatizar concessão administrativa do Guia junto com bônus;
  - checkbox padrão “Enviar o Guia para o e-mail do usuário”;
  - memória operacional de pendências e decisões.

Motivo:

- a regra semântica de gating impacta diretamente a entrada oficial do sistema, então ainda faz parte do eixo desta fase;
- já a automação do admin é governança operacional e pode ser tratada como sequência controlada.

### 5. Mini-plano de correção

#### Objetivo

Consolidar a regra correta do Guia como pré-requisito do programa, sem confundir posse válida do Guia com bônus/produto e sem abrir nova camada estrutural.

#### Escopo

- ajustar `apps/core/permissions.py`
- ajustar `apps/core/views.py` no que depende do status composto
- alinhar `apps/vocacional/gating.py` à mesma semântica
- corrigir o bug de `/guia/` em `apps/core/views.py`

Prováveis arquivos tocados:

- `apps/core/permissions.py`
- `apps/core/views.py`
- `apps/vocacional/gating.py`
- opcionalmente `docs/arquitetura/pendencias_governanca.md`

#### Risco principal

Alterar equivalências legadas do Guia e quebrar acessos já cadastrados com slugs antigos.

Mitigação:

- manter compatibilidade de slugs;
- mudar primeiro a ordem semântica da decisão, não os dados;
- não mexer ainda no fluxo interno do Vocacional além do gating de entrada;
- separar o patch semântico do patch de automação administrativa.

#### Critério de aceite

- usuário sem Guia válido não cai em Avaliação do Guia;
- usuário com Guia válido, mas sem avaliação, é direcionado para Avaliação do Guia;
- usuário com Guia válido + avaliação concluída segue para o gating do produto;
- bônus concedido por admin não vira liberação irrestrita de outros produtos;
- `/guia/` deixa de gerar erro 500.

#### Smoke test

1. usuário sem legal
2. usuário com legal, sem Guia válido
3. usuário com legal + Guia válido, sem avaliação
4. usuário com legal + Guia válido + avaliação concluída, sem bônus específico
5. usuário com legal + Guia válido + avaliação concluída + bônus específico
6. usuário com concessão administrativa de bônus sem Guia explícito, para validar a regra após o ajuste
7. acesso a `/guia/`

### 6. Proposta de arquivo vivo de pendências

Concordo com a criação de:

- `docs/arquitetura/pendencias_governanca.md`

Estrutura mínima sugerida:

- regras de negócio já definidas
- decisões de gating já fechadas
- pendências de governança/admin
- automações desejadas
- bugs confirmados
- itens aprovados e ainda não implementados
- decisões que mudaram ao longo do projeto

Sugestão prática:

- manter esse arquivo curto, incremental e datado por blocos;
- usar como memória operacional oficial entre sessões;
- registrar ali especialmente tudo o que foi “aprovado conceitualmente” mas ainda não virou patch.

## Resposta à intervenção: `patch_semantico_do_gating.md`

### Bloco A - plano curto do Hotfix `/guia/`

#### 1. Arquivo/função tocados

- `apps/core/views.py`
- função: `guia_redirect_preview`

#### 2. Correção técnica objetiva

- importar `static` corretamente em `apps/core/views.py`;
- não misturar essa correção com a revisão semântica do gating.

#### 3. Risco principal

- praticamente nulo; o risco real é só aproveitar o hotfix para mexer em mais coisas do que o necessário.

#### 4. Critério de aceite

- `/guia/` deixa de retornar `500 NameError`;
- a página volta a montar `og_image` normalmente;
- o restante do portal/gating permanece intocado.

#### 5. Smoke test mínimo

1. acessar `/guia/`
2. confirmar ausência de `NameError: static is not defined`
3. confirmar carregamento/resposta normal da view

### Bloco B - plano curto do patch semântico do gating

#### 1. Funções/arquivos tocados

- `apps/core/permissions.py`
  - `user_has_produto` ou helper novo local de composição
  - `onboarding_status`
  - possivelmente um helper explícito para “possui Guia válido”
- `apps/core/views.py`
  - funções que compõem o estado/CTA do portal
- `apps/vocacional/gating.py`
  - `next_step`
  - possivelmente `bonus_acquired` ou helper equivalente

#### 2. Mudança conceitual da prioridade

Passar a decidir nesta ordem:

1. `has_legal`
2. possui Guia válido
3. `has_guia_feedback`
4. gating do produto/bônus

Ponto-chave:

- “possui Guia válido” vira um conceito explícito;
- não depende apenas de compra;
- também não deve ser inferido automaticamente de “tem bônus”, porque isso mascara estados inconsistentes de governança.

#### 3. Risco principal

- quebrar compatibilidade histórica de slugs/equivalências e alterar comportamento de usuários já cadastrados com acessos legados.

#### 4. Critério de aceite

- usuário sem Guia válido não cai em Avaliação do Guia;
- usuário com Guia válido, mas sem avaliação, cai em Avaliação do Guia;
- usuário com Guia válido + avaliação concluída segue para o gating do produto;
- bônus admin não vira liberação irrestrita;
- a revisão semântica ocorre sem abrir camada paralela.

#### 5. Smoke test mínimo

1. usuário com `has_legal=False`
2. usuário com legal, sem Guia válido
3. usuário com legal + Guia válido, sem avaliação
4. usuário com legal + Guia válido + avaliação
5. usuário com legal + Guia válido + avaliação + produto específico
6. caso inconsistente de bônus admin sem Guia explícito, para verificar tratamento controlado

### Bloco C - proposta inicial do arquivo vivo

#### 1. Nome final do arquivo

- `docs/arquitetura/pendencias_governanca.md`

#### 2. Estrutura sugerida

- contexto e objetivo do arquivo
- regras de negócio já definidas
- decisões de gating já fechadas
- bugs confirmados
- pendências de governança/admin
- automações desejadas
- itens aprovados e ainda não implementados
- mudanças de entendimento relevantes

#### 3. Primeiro conteúdo a ser registrado

- regra corrigida do Guia:
  - legal -> guia válido -> avaliação do Guia -> produto
- bug `/guia/` com `static` não importado
- decisão de que “bônus admin sem guia explícito” é estado inconsistente de governança, não fluxo normal
- pendência futura:
  - concessão administrativa do Guia junto com bônus
  - checkbox “Enviar o Guia para o e-mail do usuário”

## Resposta à intervenção: aprovação_do_patch_semantico_do gating.md

Implementado em:

- `apps/core/views.py`

Ajuste realizado:

- importação de `static` adicionada para corrigir o `500 NameError` em `guia_redirect_preview()`.

### Patch semântico do gating

Arquivos alterados:

- `apps/core/permissions.py`
- `apps/core/views.py`
- `apps/vocacional/gating.py`
- `apps/vocacional/views_bonus.py`
- `templates/core/portal.html`

Mudanças aplicadas:

- `onboarding_status()` agora distingue explicitamente:
  - `has_legal`
  - `has_valid_guia`
  - `has_guia_feedback`
- o portal/gating passou a seguir a ordem:
  - legal
  - Guia válido
  - Avaliação do Guia
  - produto/bônus
- não foi criada inferência automática de Guia válido a partir da mera existência de bônus;
- o caso `bônus sem Guia explícito` passou a ser tratado como estado inconsistente;
- foi adicionada notificação por e-mail ao admin, com deduplicação por sessão, quando esse estado inconsistente é detectado no eixo do portal.

### Arquivo vivo criado

Criado:

- `docs/arquitetura/pendencias_governanca.md`

Conteúdo inicial registrado:

- regra corrigida do Guia;
- ordem semântica do gating;
- bug confirmado de `/guia/`;
- pendências de governança/admin;
- automações desejadas;
- itens aprovados e ainda não implementados.

## Resposta à intervenção: `aprovacao_da_implementacao_do_patch_semantico_do gating.md`

### 1. Diagnóstico curto do 403 pós-login

A hipótese de `next`/redirect herdado de rota restrita é forte e compatível com o código atual.

Evidências:

- `apps/contas/urls.py:11-15`
  O login ativo na rota oficial usa `auth_views.LoginView` com `redirect_authenticated_user=True`.
- `escola_no_ar_site/settings.py:188`
  Existe fallback seguro em `LOGIN_REDIRECT_URL = "/portal/"`.
- Mas esse fallback só vale quando não há `next`.

O problema mais provável é:

- o usuário comum entra por uma URL como `/contas/login/?next=/admin/` ou outra rota restrita herdada;
- autentica normalmente;
- o Django respeita esse `next`;
- o usuário é enviado para a rota protegida;
- a rota responde com `403` porque ele não é staff/superuser.

### 2. Confirmação sobre `next`/redirect herdado

Sim, o problema parece estar em `next` herdado de rota restrita, não no patch semântico do gating.

Isso é coerente com:

- o comportamento observado após troca de contexto admin -> usuário comum;
- o uso de `redirect_authenticated_user=True`;
- o fato de o login padrão do Django não filtrar semanticamente “destinos proibidos para este perfil”; ele só valida host/URL segura.

### 3. Correção mínima e isolada proposta

Correção mínima:

- trocar o `LoginView` padrão por uma view curta e explícita de login seguro;
- manter o comportamento normal para `next` legítimo;
- bloquear `next` herdado para rotas administrativas/restritas quando o usuário autenticado não tiver permissão para elas;
- nesses casos, fazer fallback para `LOGIN_REDIRECT_URL` ou `portal`.

Ponto de implementação mais provável:

- `apps/contas/views.py`
- `apps/contas/urls.py`

Regra mínima sugerida:

- se `next` aponta para `/admin/` ou outra rota administrativa e o usuário não é staff/superuser:
  - ignorar `next`
  - redirecionar para `portal`

Isso mantém o patch isolado e não mistura com gating.

### 4. Registro da pendência

A pendência já foi registrada em:

- `docs/arquitetura/pendencias_governanca.md`

Como item:

- `403 pós-login por next herdado de rota restrita`

## Resposta à intervenção: `micro-patch_isolado_de_pos-login.md`

### Proposta de micro-patch

#### Arquivos alterados

- `apps/contas/views.py`
- `apps/contas/urls.py`

#### Método sobrescrito

- criar uma `LoginView` segura em `apps/contas/views.py`
- sobrescrever `get_success_url()`

#### Regra para considerar um `next` restrito

Regra mínima e previsível nesta etapa:

- considerar restrito qualquer `next` que aponte para:
  - `/admin/`
  - e, opcionalmente, outros prefixos administrativos explícitos que já existam e sejam inequívocos

Comportamento:

- usuário comum:
  - `next` restrito é ignorado
  - fallback para `settings.LOGIN_REDIRECT_URL` ou `portal`
- staff/superuser:
  - `next` restrito legítimo é preservado
- `next` permitido:
  - segue normalmente

#### Por que isso não interfere na arquitetura do gating

- a lógica fica confinada ao fluxo de login em `apps/contas`
- não altera `core/permissions.py`
- não altera `apps/core/views.py` no eixo de Guia/onboarding/bônus
- não altera `apps/vocacional/gating.py`
- não cria middleware global nem regra paralela de acesso

Em outras palavras:

- o patch só saneia o destino pós-login;
- não redefine quem pode acessar produto, Guia, avaliação ou bônus.

### Critério de aceite operacional

- usuário comum sem `next` -> `/portal/`
- usuário comum com `next=/admin/` -> `/portal/`
- staff/superuser com `next=/admin/` -> `/admin/`
- usuário comum com `next` permitido -> segue normalmente
- nenhum comportamento validado do gating é alterado

## Resposta à intervenção: `adendo_micro-patch_isolado_de_pos-login.md`

### Implementação realizada

Arquivos alterados:

- `apps/contas/views.py`
- `apps/contas/urls.py`

### Método sobrescrito

- `SafeLoginView.get_success_url()`

### Regra aplicada

- o método parte de `super().get_redirect_url()`, preservando a validação segura já feita pelo Django para host/scheme;
- o `path` do destino é normalizado com `urlsplit(redirect_to).path`;
- nesta primeira versão, o único destino tratado como restrito é:
  - `/admin/`
  - ou qualquer path iniciado por `/admin/`

Comportamento:

- usuário comum + `next` administrativo:
  - ignora esse `next`
  - usa `self.get_default_redirect_url()`
- staff/superuser + `next` administrativo:
  - preserva o `next`
- `next` permitido:
  - segue normalmente

### Fonte canônica de fallback

- o fallback final usa `self.get_default_redirect_url()`
- isso mantém `LOGIN_REDIRECT_URL` como origem canônica do redirecionamento padrão

### Por que não interfere no gating

- o patch ficou isolado no login de `apps/contas`
- não altera:
  - `apps/core/permissions.py`
  - `apps/core/views.py`
  - `apps/vocacional/gating.py`
- não cria middleware
- não redefine regras de Guia, avaliação, bônus ou produto

## Resposta à intervenção: continuidade da Fase 1 apos os patches estruturais

### Implementação realizada

Arquivos alterados:

- `apps/core/views.py`
- `templates/core/portal.html`
- `static/css/core_portal.css`

### Escopo desta fatia

- evolução controlada do portal para uma entrada mais acolhedora e explicativa;
- preservação do eixo arquitetural já validado:
  - portal continua no `core`
  - CTAs principais continuam passando pelo `produto_resolver`
  - gating não foi reaberto neste passo

### Mudanças aplicadas

- hero principal com CTA variável por estado do usuário;
- blocos de acolhimento e explicação da navegação;
- cards de produto mais claros para Vocacional, Sonhe + Alto e próximo passo;
- seção final de fechamento com CTA forte;
- extração do visual para `static/css/core_portal.css`, reduzindo CSS inline estrutural;
- helper de contexto em `apps/core/views.py` para definir o CTA principal da entrada.

### O que foi preservado

- área de pendências continua funcionando;
- links funcionais de legal, Guia, avaliação e produtos foram mantidos;
- governança e modo teste continuam acessíveis;
- nenhum ajuste novo em `core/permissions.py` ou `apps/vocacional/gating.py` nesta etapa.

## Resposta à intervenção: `relatorio2_adendo_micro-patch_isolado_de_pos-login_e_Wireframe.md`

### 1. Diagnóstico provável do `403` remanescente

O micro-patch do `next` continua válido, mas os testes reais indicam que ele não fecha sozinho o problema. O código atual aponta para uma segunda causa provável: estado residual de sessão ligado a impersonação/modo teste.

Evidências objetivas no código:

- o middleware `ImpersonateUserMiddleware` usa a session key `impersonate_user_id`;
- ele também preserva `request.real_user` e troca `request.user` em rotas de app;
- o `logout_view()` atual apenas chama `logout(request)` e redireciona, sem limpeza explícita de chaves como `portal_mode`;
- `portal_mode` também é persistido em sessão no `core`;
- há duplicação real de indicação de modo teste:
  - banner global em `templates/base.html`
  - chip local no hero de `templates/core/portal.html`

Leitura arquitetural:

- o caso inicial de `next=/admin/` foi corretamente mitigado em `apps/contas`;
- o `403` remanescente parece mais compatível com troca de contexto no mesmo navegador, sobretudo após uso de admin, governança ou impersonação;
- isso sugere investigação complementar em torno de:
  - limpeza de `impersonate_user_id`
  - limpeza de `portal_mode`
  - comportamento de usuário já autenticado batendo em `/contas/login/` com `redirect_authenticated_user=True`
  - diferença entre sair do modo teste e sair da sessão

Hipótese principal neste momento:

- há pelo menos um fluxo em que o navegador reaproveita sessão/contexto administrativo residual, e esse estado interfere no redirecionamento ou na autorização posterior;
- por isso, o bug deve ser tratado agora como problema de ciclo de sessão/logout/impersonação, e não mais só de `next`.

Matriz curta de reprodução recomendada para fechar a causa:

1. admin normal -> logout -> login usuário comum
2. admin em modo teste -> sair do modo teste -> logout -> login usuário comum
3. admin em modo teste -> logout direto sem sair do modo teste -> login usuário comum
4. repetir os mesmos cenários em janela anônima

Resultado esperado dessa rodada:

- identificar se o `403` depende de `impersonate_user_id`, de `portal_mode`, ou de ambos;
- separar claramente bug de sessão residual de bug de redirect pós-login.

### 2. Plano mínimo de implementação do checkbox de sessão

A implementação pode continuar cirúrgica dentro de `apps/contas`, sem tocar no gating.

Escopo mínimo:

- adicionar um checkbox no login:
  - rótulo: `Permanecer conectado neste dispositivo`
- padrão desmarcado;
- desmarcado:
  - sessão expira ao fechar o navegador;
- marcado:
  - sessão persistente por prazo configurado;
- preservar o redirect seguro já implementado no `SafeLoginView`.

Proposta técnica mínima:

- criar um `AuthenticationForm` customizado, ou estender o form do login atual, para incluir `remember_me`;
- manter `SafeLoginView` como view oficial;
- sobrescrever `form_valid()` no `SafeLoginView` para definir `request.session.set_expiry(...)` depois do login bem-sucedido;
- usar:
  - `0` quando `remember_me` estiver desmarcado;
  - um prazo configurável em `settings`, por exemplo `REMEMBER_ME_AGE`, quando estiver marcado.

Por que esse caminho é o mais seguro:

- mantém a lógica de redirect concentrada em `get_success_url()`;
- mantém a política de expiração concentrada no fluxo oficial da `LoginView`;
- evita ressuscitar a `login_view()` legada em paralelo.

Critério de aceite:

- usuário comum sem marcar a opção:
  - sessão termina ao fechar o navegador;
- usuário que marca a opção:
  - sessão persiste pelo prazo configurado;
- o comportamento do redirect seguro continua idêntico ao patch já aprovado.

### 3. Proposta de MVP administrativo para teste do Guia/status

O MVP deve ser construído em cima da base atual:

- `Usuario`
- `Produto`
- `Acesso`
- `onboarding_status(...)`
- `user_has_produto(...)`

Sem criar status paralelo.

Leitura do que já existe e pode ser reaproveitado:

- `Produto` e `Acesso` já existem em `apps/contas/models_acessos.py`;
- `Acesso` já tem `origem`, `granted_at` e `expires_at`;
- o admin já cadastra e busca `Produto` e `Acesso`;
- a semântica consolidada do funil já existe em `apps/core/permissions.py` e `apps/core/views.py`.

MVP mínimo sugerido:

1. tela simples de governança por usuário, dentro do eixo já existente de dashboard/admin do portal;
2. campo de busca por e-mail;
3. bloco de status consolidado exibindo:
   - `has_legal`
   - `has_valid_guia`
   - origem do Guia, se houver `Acesso` correspondente
   - `has_guia_feedback`
   - acessos ativos por produto
   - inconsistência semântica
   - próximo passo esperado no funil
4. ações mínimas:
   - conceder `guia`
   - remover/concluir o acesso ativo de `guia`
   - opcionalmente conceder produto bônus com `origem=admin`
   - registrar separadamente ação de envio do Guia

Importante para não desalinhar a arquitetura:

- a concessão administrativa do Guia deve continuar sendo só criação/remoção de `Acesso` no produto `guia`;
- o status exibido deve ser derivado da regra real, não salvo em tabela própria;
- o "próximo passo" pode ser calculado com a mesma ordem semântica já consolidada:
  - legal
  - Guia válido
  - avaliação do Guia
  - produto

Entrega mínima recomendada:

- primeiro, visão consolidada + conceder/remover Guia;
- depois, ação operacional de envio/registro do Guia;
- por último, filtros de inconsistência e refinamentos.

### 4. Lista objetiva dos ajustes de portal

Os ajustes pedidos fazem sentido e podem entrar depois dos itens de sessão/governança.

Ajustes objetivos já confirmados:

- remover repetição de conteúdo informativo fora do hero;
- revisar o texto em PT-BR com acentuação correta;
- trocar linguagem excessivamente técnica por linguagem mais acolhedora;
- revisar rótulos:
  - `Obter o Guia` -> preferir `Conhecer o Guia` ou `Saiba mais sobre o Guia`;
- apontar esse CTA para página explicativa do projeto/Guia, não necessariamente compra direta;
- manter uma única página base de portal, variando apenas CTA e estado;
- decidir se o indicador local de modo teste continua:
  - se o banner global permanecer, o chip local deve sair;
  - se a intenção for manter o chip no portal, o banner global deve ser suprimido ali.

Leitura prática de prioridade:

- primeiro: fechar o bug real de sessão residual/403;
- segundo: restaurar o checkbox de permanência;
- terceiro: criar o MVP de governança do Guia;
- quarto: lapidar copy, header, logo e CTA do Guia.

## Resposta à intervenção: `revisando_pos_login_e_criando_MVP_administrativo.md`

### Direção validada

A disciplina de execução faz sentido e mantém o trabalho seguro:

- não ampliar a correção do `403` só por hipótese;
- fechar antes a causa residual real;
- implementar o checkbox de permanência apenas depois disso;
- manter o MVP administrativo enxuto e derivado da regra já existente;
- deixar a lapidação do portal para a etapa seguinte.

### Próximo passo correto para o `403`

O próximo passo não é uma refatoração ampla. É um ajuste mínimo e verificável no ciclo de saída.

Recorte técnico proposto:

1. revisar os fluxos de saída que hoje deixam estado de sessão espalhado;
2. limpar explicitamente as chaves residuais relevantes;
3. descrever com precisão quais chaves são limpas e em que fluxo.

Pelo código atual, as chaves prioritárias são:

- `impersonate_user_id`
- `portal_mode`

Fluxos a tratar separadamente:

- `logout_view()` em `apps/contas/views.py`
- `portal_impersonar_sair()` em `apps/core/views.py`

Objetivo dessa rodada:

- reduzir o risco de reaproveitamento indevido de contexto administrativo;
- transformar a hipótese em comportamento observável e controlado;
- só depois revalidar se o `403` remanescente desaparece.

### Escopo mínimo do checkbox de permanência

A direção anterior permanece boa e fica aprovada como etapa B:

- `SafeLoginView` continua sendo a view oficial;
- o checkbox entra no form do login;
- a política de expiração entra em `form_valid()`;
- padrão seguro:
  - desmarcado => sessão encerra ao fechar o navegador
  - marcado => sessão persiste por tempo configurado

Não vale a pena misturar isso agora com a investigação do `403`.

### Escopo mínimo do MVP administrativo

A primeira entrega deve ficar estritamente neste nível:

- buscar usuário por e-mail;
- mostrar:
  - `has_legal`
  - `has_valid_guia`
  - `has_guia_feedback`
  - acessos ativos
  - próximo passo esperado
- permitir:
  - conceder Guia
  - remover Guia

Isso é suficiente para destravar teste real do gating sem reabrir arquitetura nem criar painel excessivo.

### Ordem operacional consolidada

A. fechar a causa real do `403` com limpeza mínima e explícita de sessão  
B. restaurar o checkbox de permanência  
C. criar o MVP administrativo enxuto de Guia/status  
D. lapidar portal

## Resposta à intervenção: `mudanca_de_direcao_quanto_ao_checkbox.md`

### Mudança de direção confirmada

O checkbox `Permanecer conectado neste dispositivo` sai do plano.

Nova decisão:

- não oferecer opção de persistência de sessão para o aluno;
- adotar política padrão de sessão não persistente;
- reforçar logout explícito com limpeza de estado residual;
- não confundir isso com solução automática do `403`.

### Leitura técnica

Essa mudança é coerente com o contexto escolar/laboratório:

- reduz risco de reaproveitamento indevido do navegador por outro aluno;
- evita introduzir conveniência que enfraqueça a postura de segurança;
- simplifica o fluxo de login em vez de ampliá-lo.

Também corrige um risco de desenho:

- o checkbox estava virando uma frente própria de implementação;
- mas o problema estrutural imediato continua sendo estado residual no mesmo ciclo de uso, não persistência de longo prazo.

### Efeito no plano

A etapa B anterior deixa de existir como implementação de checkbox.

No lugar dela entra:

- consolidação explícita de política de sessão não persistente;
- manutenção do login sem `remember me`;
- reforço do logout e da saída do modo teste com limpeza explícita das chaves residuais relevantes.

Chaves já confirmadas como prioritárias:

- `impersonate_user_id`
- `portal_mode`

Também vale revisar se existe qualquer outra chave auxiliar de contexto administrativo/teste associada ao fluxo atual.

### Nova ordem operacional

A. fechar a causa real do `403` com limpeza mínima e explícita de sessão  
B. consolidar política de sessão não persistente em ambiente escolar  
C. criar o MVP administrativo enxuto de Guia/status  
D. lapidar portal

### Observação de segurança

Sessão não persistente significa:

- o cookie de sessão expira ao fechar o navegador;
- isso ajuda a reduzir reaproveitamento entre alunos;
- mas não substitui limpeza explícita no logout;
- e não deve ser implementado via `beforeunload` ou truques de frontend.

## Resposta à intervenção: continuidade após `mudanca_de_direcao_quanto_ao_checkbox.md`

### Implementação realizada

Arquivos alterados:

- `apps/contas/views.py`
- `apps/core/views.py`
- `escola_no_ar_site/settings.py`

### Item A: limpeza mínima e explícita de sessão

Foi aplicado um patch estreito nos fluxos de saída.

Em `apps/contas/views.py`:

- criei a lista canônica de chaves residuais:
  - `impersonate_user_id`
  - `portal_mode`
- adicionei o helper `_clear_session_context(request)`;
- o `logout_view()` agora limpa explicitamente essas chaves antes de chamar `logout(request)`.

Em `apps/core/views.py`:

- `portal_impersonar_sair()` deixou de gravar `portal_mode="gov"`;
- agora ele limpa explicitamente:
  - `impersonate_user_id`
  - `portal_mode`
- depois redireciona para `portal_dashboard`.

Leitura arquitetural:

- isso reduz acoplamento com estado residual;
- evita carregar para a próxima navegação um modo de sessão que era só transitório;
- mantém a governança acessível porque staff/superuser já caem em governança por padrão, sem depender de `portal_mode="gov"`.

### Item B: política de sessão não persistente

Em `escola_no_ar_site/settings.py`:

- adicionei `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`;
- mantive `SESSION_COOKIE_AGE = 1800`;
- mantive `SESSION_SAVE_EVERY_REQUEST = True`.

Efeito prático:

- a sessão passa a ser cookie de sessão, não persistente;
- além disso, continua havendo expiração por inatividade;
- isso fica alinhado ao contexto escolar sem criar checkbox nem branch extra no login.

### O que não foi alterado

- não mexi no gating;
- não mexi em `core/permissions.py`;
- não mexi no `SafeLoginView` nem reabri a frente de checkbox;
- não mexi ainda no MVP administrativo de Guia/status;
- não mexi ainda na lapidação do portal.

### Validação recomendada

Agora vale repetir a matriz operacional:

1. admin normal -> logout -> login usuário comum -> ✔ 
2. admin em modo teste -> sair modo teste -> logout -> login usuário comum -> 403 Forbidden
3. admin em modo teste -> logout direto -> login usuário comum -> ✔
4. fechar navegador e reabrir -> voltou na reabertura com o login anterior (superusuario)
5. repetir em janela anônima :
    1. admin normal -> logout -> login usuário comum -> 403 Forbidden
    2. admin em modo teste -> sair modo teste -> logout -> login usuário comum -> 403 Forbidden
    3. admin em modo teste -> logout direto -> login usuário comum -> 403 Forbidden
    4. fechar navegador e reabrir -> voltou na reabertura limpo, na tela de login com o campo de usuário limpo.

Como eu não consegui validar com `manage.py check` no sandbox daqui, essa confirmação precisa vir do seu ambiente real.

## Resposta à intervenção: `instrumentar_o_fluxo_e_descobrir_qual_URL_exata.md`

### Implementação de instrumentação

A direção mudou corretamente: em vez de novo patch por hipótese, entrou instrumentação objetiva.

Arquivos alterados:

- `apps/contas/views.py`
- `apps/core/views.py`
- `apps/core/middleware.py`
- `escola_no_ar_site/settings.py`

### O que está logando agora

Em `SafeLoginView.get_success_url()`:

- usuário autenticado
- `is_staff`
- `is_superuser`
- `redirect_to` bruto
- `normalized_path`
- `final_success_url`

Em `logout_view()`:

- usuário antes do logout
- chaves residuais presentes
- valor de `portal_mode`
- valor de `impersonate_user_id`
- redirect final pretendido

Em `portal_impersonar_sair()`:

- usuário antes da limpeza
- existência de `impersonate_user_id`
- valor de `portal_mode`
- chaves limpas
- redirect final emitido

Em `PortalDashboardView.test_func()`:

- log explícito quando usuário não-staff cai na governança
- isso ajuda a confirmar se o `403` está vindo de `UserPassesTestMixin` no dashboard

Em `Debug403LoggingMiddleware`:

- qualquer resposta final `403`
- com:
  - `path`
  - `view_name`
  - `func`
  - usuário
  - `real_user`
  - `portal_mode`
  - `impersonate_user_id`

### Leitura técnica provisória

Com os resultados que você trouxe, o suspeito mais forte agora é este:

- o usuário comum está sendo levado a uma rota protegida de governança, muito possivelmente `/portal/dashboard/`;
- se isso se confirmar, o `403` deve aparecer junto de:
  - `AUTH get_success_url ... final_success_url='/portal/dashboard/'`
  - ou algum redirect intermediário para dashboard
  - seguido de `AUTH PortalDashboardView.test_func denied ...`
  - e do `AUTH 403 path='/portal/dashboard/' ...`

Mas eu não estou fechando o diagnóstico ainda. A instrumentação entrou justamente para parar de inferir.

### O que observar no runserver

Na próxima rodada de testes, procure no console a sequência:

1. `AUTH portal_impersonar_sair ...`
2. `AUTH logout_view before ...`
3. `AUTH get_success_url ...`
4. `AUTH PortalDashboardView.test_func denied ...` se houver queda indevida em governança
5. `AUTH 403 ...`

O ponto decisivo agora é:

- qual `final_success_url` saiu do login;
- qual `path` efetivamente respondeu `403`.

Com isso, o próximo patch já pode ser definitivo e estreito.

## Resposta à intervenção: `resultados_da_instrumentacao_para_revelar_origem_403.md` e `orientacoes_para_solucao_do_403.md`

### Diagnóstico fechado

Os logs fecharam a origem do `403`.

Causa confirmada:

- o usuário comum estava sendo redirecionado para `/portal/dashboard/`;
- essa rota é restrita de governança/staff;
- o bloqueio final vinha de `PortalDashboardView.test_func()` via `UserPassesTestMixin`.

Sequência objetiva confirmada nos logs:

1. `logout_view` preservava `next=/portal/dashboard/`
2. o login carregava `?next=/portal/dashboard/`
3. `SafeLoginView.get_success_url()` devolvia `/portal/dashboard/` para usuário comum
4. `PortalDashboardView.test_func()` negava
5. o `403` final saía de `/portal/dashboard/`

### Patch definitivo aplicado

Arquivo alterado:

- `apps/contas/views.py`

Mudanças:

1. `logout_view()`:
   - deixou de reaproveitar `next`;
   - agora sempre redireciona para o destino público canônico `portal`;
   - o log continua mostrando:
     - `next_url` bruto
     - `normalized_path`
     - `final_redirect`

2. `SafeLoginView.get_success_url()`:
   - a blindagem deixou de cobrir só `/admin`;
   - agora também trata como restrito para usuário não-staff:
     - `/portal/dashboard`
     - `/portal/dashboard/`
     - qualquer subrota iniciada por `/portal/dashboard/`

3. a regra restritiva ficou centralizada em helper único:
   - `_is_restricted_redirect_path(...)`

### O que foi preservado

- não reabri gating;
- não mexi em `core/permissions.py`;
- não mexi no fluxo de Guia/Avaliação/bônus;
- mantive a limpeza de sessão já implementada;
- mantive a instrumentação para confirmar a correção no ambiente real.

### Validação recomendada

Agora vale repetir especialmente estes cenários:

1. admin normal -> logout -> login usuário comum
2. admin em modo teste -> sair modo teste -> logout -> login usuário comum
3. admin em modo teste -> logout direto -> login usuário comum

Resultado esperado:

- nenhum usuário comum deve cair em `/portal/dashboard/`;
- se aparecer `next=/portal/dashboard/`, o login deve cair no fallback público;
- o `403` de governança deve desaparecer nesses fluxos.

## Resposta à intervenção: `encerrado_403_inicio_MVP_administrativo.md`

### Fechamento da frente do `403`

A frente do `403` fica encerrada funcionalmente.

Validação prática confirmada:

- admin normal -> logout -> login usuário comum -> OK
- admin em modo teste -> sair modo teste -> logout -> login usuário comum -> OK
- admin em modo teste -> logout direto -> login usuário comum -> OK

Leitura final consolidada:

- a causa real era a preservação indevida de `next=/portal/dashboard/` no fluxo logout -> login;
- a correção ficou no lugar certo:
  - autenticação
  - redirecionamento
  - governança
- o gating não foi reaberto;
- nenhuma regra paralela foi criada.

### Pendências de higiene técnica abertas

1. reduzir/remover a instrumentação detalhada ou condicioná-la a `DEBUG=True`
2. registrar e corrigir separadamente o `404` do estático:
   - requisitado: `/static/core/img/logo-sonhe-mais-alto.png`
   - arquivo real informado: `static/core/img/Logo_Sonhe_mais_alto_1536x1024_RGB .png`

### Próximo ponto de retomada

Próxima etapa aprovada:

- C. MVP administrativo enxuto de Guia/status

Depois:

- D. lapidação do portal
