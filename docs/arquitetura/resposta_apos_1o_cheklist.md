Quero que você transforme o diagnóstico que acabou de fazer em uma validação objetiva + mini-plano de correção, antes de tocar no código.

## Objetivo
Não quero ainda implementação.
Quero primeiro:
1. confirmação técnica dos pontos levantados;
2. separação entre problema funcional, problema arquitetural e problema de UX;
3. proposta curta de correção por patch.

## Ponto 1 — Confirmar com evidência de código
Você afirmou que ainda existem pontos centrais da vitrine/portal bypassando o resolvedor e apontando direto para rotas como:
- projeto21:home
- vocacional:etapas

Quero que você confirme isso com evidência objetiva:
- arquivo
- linha
- trecho
- contexto do link/botão/card

Se houver mais bypasses relevantes, liste também.

## Ponto 2 — Confirmar o conflito de regra de negócio
Você afirmou que hoje:
- `has_onboarding` entra antes de qualquer outra coisa;
- `_portal_locked_cta` prioriza legal e guia_feedback;
- isso conflita com o caso de usuários com bônus/acesso liberado por entitlement/admin, sem compra do Guia.

Quero que você valide isso tecnicamente e me mostre:
- em que função(ões) essa prioridade está definida;
- qual é a ordem atual da decisão;
- por que isso força “Avaliação do Guia” num caso que deveria seguir outro fluxo;
- qual seria a distinção conceitual correta entre:
  - pendência de onboarding
  - acesso concedido por entitlement/admin
  - gating de produto
  - fluxo vindo do Guia

## Ponto 3 — Separar os problemas por natureza
Quero que você classifique os achados em 3 grupos:

### A. Problemas funcionais
Coisas que afetam o comportamento real do usuário.

### B. Problemas arquiteturais
Coisas que mantêm duplicação, bypass ou centralização incompleta.

### C. Problemas de UX/conteúdo
Coisas que deixam a entrada pesada, pouco acolhedora ou confusa.

## Ponto 4 — Mini-plano de correção por patch
Com base nisso, quero um plano curto, em ordem, sem sair codando ainda.

Para cada patch proposto, informe:
- nome curto;
- objetivo;
- o que entra;
- o que não entra;
- arquivos mais prováveis;
- risco principal;
- critério de aceite.

## Restrições
- não abrir camada paralela;
- não inventar nova regra de acesso do zero;
- não mover a lógica interna do Vocacional para o core;
- não sair implementando wireframe bonito antes de corrigir o eixo funcional;
- não misturar, no mesmo patch, correção de regra com redesign visual grande.

## Resultado esperado
Quero uma resposta curta, técnica e auditável, com estas seções:
1. Evidências confirmadas
2. Conflito de regra validado
3. Classificação dos problemas
4. Mini-plano de correção por patch

Ainda não quero código.
Quero primeiro um mapa de correção confiável.