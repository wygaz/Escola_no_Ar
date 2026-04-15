Pode seguir com o Patch 1 do mini-plano, mas com uma trava de segurança importante.

## Objetivo do patch
Corrigir a prioridade entre:
- onboarding relacionado ao Guia
- acesso concedido por entitlement/admin
- gating do produto

sem reescrever o sistema inteiro de gating e sem mexer ainda no visual.

## Intenção correta
Não quero “afrouxar” onboarding de forma geral.
Quero apenas permitir a exceção legítima em que:
- o usuário não veio do Guia/Hotmart;
- recebeu acesso/bônus por entitlement ou liberação administrativa;
- portanto não deve ser forçado artificialmente para “Avaliação do Guia” antes de acessar o que já foi concedido.

## Regra esperada
A lógica deve passar a distinguir melhor estes casos:

1. fluxo normal vindo do Guia  
2. usuário com pendências reais de onboarding que continuam válidas  
3. usuário com acesso concedido por entitlement/admin, mesmo sem compra do Guia  
4. gating específico do produto

## Restrições
- não criar camada paralela nova;
- não criar `services/`;
- não mover lógica interna do Vocacional para o core;
- não reescrever tudo;
- não mexer ainda em layout/wireframe;
- não quebrar os casos normais já válidos;
- não transformar “entitlement/admin” em liberação irrestrita para tudo.

## O que eu quero na resposta
Antes de qualquer código, me devolva um plano curto deste patch com:
1. função(ões) que serão tocadas;
2. mudança conceitual da prioridade;
3. risco principal;
4. critério de aceite;
5. smoke test mínimo.

Se a proposta estiver enxuta e segura, aí você implementa.

================================= PRÓXIMA INTERVENÇÃO =============================

Plano aprovado para implementação, com duas travas adicionais:

1. `has_legal` não deve entrar automaticamente na mesma exceção de `guia_feedback`. Se houver qualquer flexibilização de pendência legal, ela precisa ser explícita e deliberada, não efeito colateral deste patch.

2. O critério de aceite deve deixar explícito que o usuário com entitlement/admin pode entrar apenas no produto efetivamente concedido, sem transformar isso em liberação para outros produtos não concedidos.

Mantido isso, pode implementar o patch.

================================= PRÓXIMA INTERVENÇÃO =============================

A implementação parece alinhada com o objetivo do patch.

Antes de considerar fechado, vou validar localmente:
- python manage.py check
- smoke test dos 4 cenários previstos

Só peço uma confirmação objetiva:
- qual foi o caminho real do template alterado no repositório?
  - templates/core/portal.html
  - ou apps/core/templates/core/portal.html

Fora isso, a direção do patch está correta.

================================= PRÓXIMA INTERVENÇÃO =============================

Patch aprovado.

A direção está correta:
- removeu os 4 bypasses centrais do portal;
- centralizou os CTAs principais no produto_resolver;
- corrigiu também o fluxo anônimo com next para o resolvedor;
- preservou links internos legítimos dos produtos.

Vou apenas fechar com smoke test de clique real:
1. anônimo -> Sonhe + Alto
2. anônimo -> Vocacional
3. autenticado -> Sonhe + Alto
4. autenticado -> Vocacional

Se esses 4 estiverem coerentes, pode seguir para o próximo patch.

================================= PRÓXIMA INTERVENÇÃO =============================

Plano aprovado.

A mudança faz sentido para a Fase 1:
- "/" deixa de competir semanticamente com "/portal/"
- "/portal/" permanece como experiência autenticada do core
- o patch é enxuto e não abre camada paralela

Acrescente apenas estes dois smoke tests:
5. superuser acessa "/"
6. anônimo acessa "/portal/" diretamente

Se esses cenários também estiverem corretos, pode implementar.

================================= PRÓXIMA INTERVENÇÃO =============================

Plano aprovado.

A direção está correta:
- simplificar a área de pendências sem mexer no eixo funcional;
- remover duplicação visual;
- manter apenas pendências reais com ação clara.

Acrescente só estas travas:
1. não colapsar demais pendências diferentes que coexistem;
2. não deixar chips residuais repetindo o mesmo conteúdo já mostrado no bloco principal.

Acrescente também este smoke test:
7. usuário com has_legal=False + show_guia_feedback_pending=True + bônus pendente ao mesmo tempo

Mantido isso, pode implementar.

================================= PRÓXIMA INTERVENÇÃO =============================

Plano aprovado.

A direção está correta:
- simplificar a área de pendências sem mexer no eixo funcional;
- remover duplicação visual;
- manter apenas pendências reais com ação clara.

Acrescente só estas travas:
1. não colapsar demais pendências diferentes que coexistem;
2. não deixar chips residuais repetindo o mesmo conteúdo já mostrado no bloco principal.

Acrescente também este smoke test:
7. usuário com has_legal=False + show_guia_feedback_pending=True + bônus pendente ao mesmo tempo

Mantido isso, pode implementar.

================================= PRÓXIMA INTERVENÇÃO =============================



================================= PRÓXIMA INTERVENÇÃO =============================



================================= PRÓXIMA INTERVENÇÃO =============================



================================= PRÓXIMA INTERVENÇÃO =============================



================================= PRÓXIMA INTERVENÇÃO =============================



================================= PRÓXIMA INTERVENÇÃO =============================



================================= PRÓXIMA INTERVENÇÃO =============================



================================= PRÓXIMA INTERVENÇÃO =============================



================================= PRÓXIMA INTERVENÇÃO =============================