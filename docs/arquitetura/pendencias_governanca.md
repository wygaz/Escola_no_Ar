## Contexto

Arquivo vivo de memória operacional para registrar decisões já fechadas, pendências de governança/admin, bugs confirmados e itens aprovados ainda não implementados.

Atualizar este arquivo sempre que uma decisão de negócio mudar ou quando uma pendência relevante for identificada e aceita como real.

## Regras De Negócio Já Definidas

### Guia como pré-requisito

- A Avaliação do Guia é obrigatória para participantes do programa.
- O usuário pode possuir o Guia de duas formas:
  - compra do Guia
  - concessão administrativa explícita do Guia
- “Possui Guia válido” não é igual a “comprou o Guia”.
- “Possui Guia válido” também não deve ser inferido automaticamente apenas da existência de bônus.

### Ordem Semântica Do Gating

Sequência correta:

1. `has_legal`
2. possui Guia válido
3. `has_guia_feedback`
4. gating específico do produto/bônus

### Estado Inconsistente

- “bônus admin sem Guia explícito” não é fluxo normal desejável.
- Esse caso deve ser tratado como estado inconsistente de governança.
- O administrador deve ser alertado quando esse estado for detectado.

## Decisões De Gating Já Fechadas

- `core` continua sendo o eixo de entrada oficial dos produtos.
- CTAs principais do portal passam pelo `produto_resolver`.
- `has_legal` continua com prioridade própria.
- Usuário sem Guia válido não deve cair em Avaliação do Guia.
- Usuário com Guia válido, mas sem avaliação, deve cair em Avaliação do Guia.
- Usuário com Guia válido + avaliação concluída segue para o gating do produto.

## Bugs Confirmados

### `/guia/` com erro 500

- Bug confirmado: `static(...)` sem import em `apps/core/views.py`.
- Status: corrigido no hotfix isolado do `/guia/`.

### 403 pós-login por `next` herdado de rota restrita

- Cenário observado: sair da sessão admin e entrar como usuário comum na mesma navegação gerou `403 Forbidden`.
- Hipótese forte: o login do usuário comum ocorreu, mas o redirecionamento pós-login herdou `next` de rota administrativa/restrita.
- Status: causa confirmada por instrumentação.
- Origem real: preservação indevida de `next=/portal/dashboard/` no fluxo logout -> login.
- Mitigação aplicada:
  - logout não reaproveita mais `next`
  - `SafeLoginView` agora trata `/portal/dashboard/` como destino restrito para usuário não-staff
- Status final: validado e encerrado funcionalmente.

### Estado residual de impersonação / modo teste

- Há evidência concreta de duplicação de sinalização de modo teste:
  - banner global em `base.html`
  - indicador local no portal
- A investigação aberta agora precisa cobrir:
  - logout após admin comum
  - logout após modo teste
  - logout sem sair antes do modo teste
  - comparação com janela anônima
- Status: patch mínimo de limpeza explícita já aplicado em `logout_view()` e `portal_impersonar_sair()`.
- Próximo passo: revalidação operacional do `403` para confirmar se a causa residual foi neutralizada.

## Pendências De Governança/Admin

- automatizar concessão administrativa do Guia junto com bônus;
- adicionar checkbox padrão:
  - `Enviar o Guia para o e-mail do usuário`
- melhorar visão de status por usuário na governança;
- criar MVP de visão consolidada do status semântico do usuário;
- permitir concessão e remoção administrativa explícita do Guia;
- consolidar política de sessão não persistente no login escolar;
- reduzir/remover instrumentação detalhada de autenticação ou condicioná-la a `DEBUG=True`;
- corrigir o `404` do estático `logo-sonhe-mais-alto.png`;
- adicionar filtros operacionais para casos inconsistentes;
- definir tratamento operacional de notificação por e-mail/whatsapp ao admin.

## Automações Desejadas

- ao conceder bônus por admin, oferecer ação assistida para também conceder Guia explícito;
- preparar/disparar envio do Guia ao e-mail do usuário;
- registrar estados inconsistentes relevantes para acompanhamento operacional.

## Itens Aprovados E Ainda Não Implementados

- frente específica de governança/admin para concessão assistida do Guia;
- checkbox padrão de envio do Guia;
- logout com limpeza explícita de chaves residuais de sessão (`impersonate_user_id`, `portal_mode` e correlatas);
- melhoria de visão operacional por usuário;
- possíveis alertas adicionais por whatsapp, se isso entrar no escopo de governança.

## Mudanças De Entendimento Relevantes

### Correção da interpretação anterior

Entendimento superado:

- bônus concedido por admin dispensaria Avaliação do Guia

Entendimento correto:

- bônus concedido por admin não dispensa Avaliação do Guia;
- o que muda é a forma de obtenção do Guia;
- sem Guia válido, a próxima etapa não é Avaliação do Guia.
