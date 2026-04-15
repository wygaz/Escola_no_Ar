Análise aprovada.

Sua leitura ficou correta e bem separada entre:
- regra de negócio;
- impacto técnico;
- bug isolado;
- frente futura de governança/admin.

Quero que você siga nesta ordem, com disciplina de escopo:

## Ordem de execução

### 1) Hotfix isolado de `/guia/`
Corrigir o erro 500 em `/guia/` causado por `static(...)` sem import em `apps/core/views.py`.

Objetivo:
- tratar isso como bug pequeno e independente;
- não misturar esse ajuste com a revisão semântica do gating.

### 2) Patch semântico do gating
Corrigir a ordem lógica da decisão para refletir a regra de negócio já definida:

1. `has_legal`
2. possui Guia válido como pré-requisito
3. `has_guia_feedback`
4. gating específico do produto/bônus

Regra importante:
- “possui Guia válido” não é igual a “comprou o Guia”;
- “possui Guia válido” pode vir por compra ou por concessão administrativa;
- bônus concedido por admin NÃO dispensa Avaliação do Guia;
- mas usuário sem Guia válido NÃO deve cair em Avaliação do Guia antes de resolver a posse válida do Guia.

### 3) Arquivo vivo de pendências
Criar:
- `docs/arquitetura/pendencias_governanca.md`

Esse arquivo deve servir como memória operacional do projeto e registrar:
- regras de negócio já definidas;
- decisões de gating já fechadas;
- pendências de governança/admin;
- automações desejadas;
- bugs confirmados;
- itens aprovados e ainda não implementados;
- decisões que mudaram ao longo do projeto.

### 4) Frente seguinte de governança/admin
Deixar para a próxima frente, fora do patch semântico:
- concessão administrativa do Guia junto com bônus;
- checkbox padrão “Enviar o Guia para o e-mail do usuário”;
- visão de status por usuário e filtros operacionais;
- tratamento governado do caso inconsistente “bônus admin sem guia explícito”.

## Travas adicionais
- não abrir camada paralela nova;
- não criar `services/` sem necessidade real;
- não mover a lógica interna do Vocacional para o core;
- não fazer redesign visual agora;
- não quebrar compatibilidade de slugs/acessos legados ao revisar equivalências em `permissions.py`;
- priorizar a correção da ordem semântica da decisão antes de mexer em equivalências históricas;
- tratar o caso “bônus admin sem guia explícito” como estado inconsistente de governança, não como fluxo normal desejável.

## Como quero que você prossiga agora
Não saia implementando tudo de uma vez.

Quero que você me devolva, nesta ordem:

### Bloco A — plano curto do Hotfix `/guia/`
Com:
1. arquivo/função tocados
2. correção técnica objetiva
3. risco principal
4. critério de aceite
5. smoke test mínimo

### Bloco B — plano curto do patch semântico do gating
Com:
1. funções/arquivos tocados
2. mudança conceitual da prioridade
3. risco principal
4. critério de aceite
5. smoke test mínimo

### Bloco C — proposta inicial do arquivo vivo
Com:
1. nome final do arquivo
2. estrutura sugerida
3. primeiro conteúdo a ser registrado

Quero resposta curta, técnica e auditável.
Ainda não quero um patch grande misturado.
Quero seguir nessa ordem controlada.