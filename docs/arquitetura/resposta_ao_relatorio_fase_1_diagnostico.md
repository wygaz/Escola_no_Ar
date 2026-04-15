Quero que você transforme a revisão arquitetural abaixo em um **planejamento macro do projeto** e, em seguida, em um **planejamento detalhado da Fase 1**, com foco absoluto em evitar duplicação, preservar compatibilidade e reaproveitar a estrutura já existente.

## Contexto consolidado

Estamos finalizando uma reforma arquitetural do projeto Django **Guia de Descoberta**, com foco em **Vocacional** e **Sonhe+Alto**.

Pontos já consolidados:
- o app **core** deve se tornar o **centro oficial da navegação de produtos** e o **orquestrador de fluxo**;
- o app **vocacional** continua **dono do fluxo interno do produto**;
- a **governança** deve virar experiência própria de **staff/superuser**;
- a **vitrine oficial de produtos** deve nascer no **core**;
- devemos evitar duplicação de lógica, CSS, templates e fontes de verdade;
- **apps/contas** continua sendo a base oficial de usuários, permissões e acessos;
- não queremos criar uma camada paralela nova;
- queremos **extração, centralização e reaproveitamento da lógica existente**.

## Diretriz crítica

A Fase 1 **não pode** criar arquitetura concorrente ao que já existe.
Ela deve funcionar como **consolidação guiada**, não como “novo sistema ao lado do antigo”.

### Regras obrigatórias
- **não recriar gating** já existente em `core/permissions`, `user_has_produto`, `onboarding_status` ou `vocacional/gating`;
- **não manter duas vitrines oficiais** com o mesmo papel;
- **não manter duas governanças oficiais** com o mesmo papel;
- **não criar detalhe de produto concorrente** ao que já existe no Vocacional;
- **não criar partials, services ou templates preventivamente** sem reutilização real;
- **não deslocar a lógica interna do Vocacional para o core**;
- o `core` deve **orquestrar** entrada/navegação/status, não assumir a lógica interna do produto.

## Direção recomendada

### O que deve acontecer
1. `core` vira a **entrada oficial** dos produtos;
2. `vocacional` continua **dono do fluxo interno**;
3. `apps/contas` continua **fonte única** de usuário, produto e acesso;
4. staff/superuser passam a ter **experiência própria de governança**, sem cair no funil do aluno;
5. `portal()` e `portal_home()` devem deixar de repetir lógica;
6. o estado do usuário por produto deve ser **consolidado**, não reinventado;
7. a vitrine oficial deve existir em um único lugar.

### O que deve ser reaproveitado
- `apps/core/permissions`
- `user_has_produto`
- `onboarding_status`
- `apps/vocacional/gating.py`
- `templates/portal/dashboard.html` como possível base da governança MVP
- `templates/vocacional/ofertas_refinamento.html` como detalhe/oferta já existente do Vocacional
- `core/portal.html` apenas como ponto de compatibilidade transitória, não como segunda vitrine final

## Sinalização de risco
Quero que você trate como risco alto:
- duplicar gating existente;
- manter `portal` e `produtos` como vitrines concorrentes;
- manter `dashboard` e `governanca` como painéis concorrentes;
- criar `produto_detalhe.html` para competir com `ofertas_refinamento.html`;
- criar CSS novo concorrente ao já existente;
- criar service novo que replique regra já existente.

## Sua tarefa

Quero que você produza **dois planejamentos**:

# 1) Planejamento macro da reforma arquitetural
Esse planejamento deve cobrir o projeto como um todo, não só a Fase 1.

Estruture em:
- objetivo arquitetural geral;
- princípios e restrições;
- fronteiras entre `core`, `vocacional`, `contas` e governança;
- fases sugeridas em ordem;
- objetivo de cada fase;
- entregáveis por fase;
- riscos por fase;
- critérios de aceite por fase;
- compatibilidade e migração gradual;
- o que explicitamente **não** entra em cada fase.

Importante:
- esse planejamento macro deve mostrar que a Fase 1 é apenas a primeira etapa de uma consolidação maior;
- ele deve ser realista, incremental e sem “big bang rewrite”.

# 2) Planejamento detalhado da Fase 1
Depois do planejamento macro, detalhe a Fase 1 em nível operacional.

Quero que você entregue:
- objetivo específico da Fase 1;
- escopo incluído;
- escopo excluído;
- arquivos/camadas que devem ser tocados primeiro;
- arquivos/camadas que devem ser preservados;
- ordem sugerida dos patches;
- dependências entre patches;
- critérios de revisão para evitar duplicação;
- checklist de compatibilidade;
- checklist de testes manuais;
- critérios de pronto da Fase 1.

## Direção da Fase 1
A Fase 1 deve priorizar algo nessa linha:
- reduzir duplicação entre `portal()` e `portal_home()`;
- consolidar no `core` a entrada oficial e o status do usuário por produto;
- manter o Vocacional como dono do fluxo interno;
- reaproveitar templates existentes antes de criar novos;
- criar apenas o mínimo de services necessário;
- adiar abstrações visuais genéricas até haver reutilização real.

## Formato da resposta
Quero a resposta em formato técnico, claro e objetivo, com títulos e subtítulos.

Inclua:
- uma seção chamada **“Decisões de arquitetura já fixadas”**
- uma seção chamada **“Decisões ainda em aberto”**
- uma seção chamada **“Riscos de duplicação e como evitar”**
- uma seção chamada **“Sequência recomendada de execução”**

## Muito importante
Sempre que houver dúvida entre:
- criar algo novo
ou
- reaproveitar/encapsular algo existente

prefira **reaproveitar/encapsular**.

Sempre que houver dúvida entre:
- abstrair agora
ou
- adiar até haver segunda reutilização real

prefira **adiar**.

O resultado precisa me ajudar a conduzir os próximos patches sem criar camada paralela.