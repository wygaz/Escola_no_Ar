Agora quero que você faça a continuação do planejamento já produzido, transformando-o em um **planejamento detalhado e operacional da Fase 1**.

Use como base o planejamento macro já definido e preserve integralmente estas diretrizes:

## Regras fixas
- `core` é a entrada oficial e o orquestrador de navegação por produto;
- `vocacional` continua dono do fluxo interno do produto;
- `apps/contas` continua como fonte única de usuário, produto, acesso e permissões;
- governança de `staff/superuser` deve existir fora do funil do aluno;
- a Fase 1 não pode criar camada paralela;
- a Fase 1 deve priorizar extração, centralização e reaproveitamento da lógica existente.

## Restrições obrigatórias
- não duplicar gating existente;
- não duplicar status por produto;
- não duplicar vitrine oficial;
- não duplicar governança oficial;
- não criar `produto_detalhe.html` genérico nesta fase;
- não criar partials ou abstrações visuais antes da segunda reutilização real;
- não mover lógica interna do Vocacional para o `core`.

## Decisões provisórias para a Fase 1
Considere como decisão de trabalho desta fase:
- a governança MVP deve partir de `templates/portal/dashboard.html`, sem criar nova governança paralela;
- `templates/vocacional/ofertas_refinamento.html` deve continuar sendo o ativo existente de detalhe/oferta do Vocacional;
- o status por produto deve começar do jeito mais enxuto possível, preferindo helper privado ou service mínimo, sem abrir estrutura excessiva cedo demais;
- `portal` pode permanecer como compatibilidade transitória, mas não como segunda vitrine final;
- as mudanças da Fase 1 devem atingir prioritariamente os pontos de entrada globais, não os fluxos internos do Vocacional.

## Conflitos concretos que a Fase 1 precisa atacar
Considere como alvos explícitos:
- `portal` ainda não é uma vitrine oficial de produtos;
- os cards ainda decidem destino direto;
- `portal()` e `portal_home()` repetem lógica;
- a governança ainda está acoplada ao portal/dashboard atual;
- há links hardcoded no Vocacional, mas nesta fase só os pontos de entrada principais devem migrar para o resolvedor central.

## Sua tarefa
Quero um **planejamento detalhado da Fase 1**, com foco operacional.

Estruture em:

# 1. Objetivo da Fase 1
Defina com precisão o objetivo arquitetural e o limite da fase.

# 2. Escopo incluído
Liste exatamente o que entra nesta fase.

# 3. Escopo excluído
Liste exatamente o que não entra nesta fase.

# 4. Decisões já fechadas para implementação
Liste o que não deve mais ficar em aberto nesta fase.

# 5. Ordem recomendada dos patches
Quero a fase quebrada em patches pequenos, reversíveis e auditáveis.

Para cada patch, informe:
- nome do patch;
- objetivo;
- arquivos/camadas mais prováveis;
- risco principal;
- critério de aceite;
- dependência em relação ao patch anterior.

# 6. Sequência mínima recomendada
Monte uma sequência parecida com:
- patch de consolidação de contexto do portal/core;
- patch de entrada oficial por produto;
- patch de governança MVP;
- patch de status por produto;
- patch de CTAs principais e compatibilidade transitória;
mas refine isso tecnicamente.

# 7. Critérios de revisão contra duplicação
Quero uma seção com critérios que devem ser usados para revisar cada patch antes de aceitar.

Exemplos:
- “isso cria nova fonte de verdade?”
- “isso duplica regra já existente?”
- “isso cria tela concorrente?”
- “isso cria CSS concorrente?”
- “isso antecipa abstração sem segundo uso real?”

# 8. Checklist de compatibilidade
Checklist objetivo para garantir:
- rotas antigas ainda funcionam quando necessário;
- Vocacional continua íntegro;
- staff/superuser não caem no funil do aluno;
- não houve quebra de onboarding/acesso;
- não houve troca indevida de templates ativos.

# 9. Checklist de testes manuais
Quero testes manuais por perfil:
- usuário comum sem acesso;
- usuário com acesso/onboarding pendente;
- usuário com acesso completo;
- staff;
- superuser;
- fluxo de entrada do Vocacional;
- links principais da vitrine/portal.

# 10. Critério de pronto da Fase 1
Defina quando a fase pode ser considerada encerrada de verdade.

## Muito importante
Prefira sempre:
- reaproveitar/encapsular em vez de criar novo;
- adiar abstração em vez de generalizar cedo;
- mover apenas a entrada oficial nesta fase, não o fluxo interno do produto.

Quero a resposta em formato técnico, objetivo e utilizável como guia real dos próximos patches.
