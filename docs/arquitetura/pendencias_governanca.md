## Contexto

Arquivo vivo de memoria operacional para registrar decisoes ja fechadas,
pendencias de governanca/admin, bugs confirmados e itens aprovados ainda nao
implementados.

Atualizar este arquivo sempre que uma decisao de negocio mudar ou quando uma
pendencia relevante for identificada e aceita como real.

## Regras De Negocio Ja Definidas

### Guia como pre-requisito

- A Avaliacao do Guia e obrigatoria para participantes do programa.
- O usuario pode possuir o Guia de duas formas:
  - compra do Guia
  - concessao administrativa explicita do Guia
- "Possui Guia valido" nao e igual a "comprou o Guia".
- "Possui Guia valido" tambem nao deve ser inferido automaticamente apenas da
  existencia de bonus.

### Ordem Semantica Do Gating

Sequencia correta:

1. `has_legal`
2. possui Guia valido
3. `has_guia_feedback`
4. gating especifico do produto/bonus

### Estado Inconsistente

- "bonus admin sem Guia explicito" nao e fluxo normal desejavel.
- Esse caso deve ser tratado como estado inconsistente de governanca.
- O administrador deve ser alertado quando esse estado for detectado.

## Decisoes De Gating Ja Fechadas

- `core` continua sendo o eixo de entrada oficial dos produtos.
- CTAs principais do portal passam pelo `produto_resolver`.
- `has_legal` continua com prioridade propria.
- Usuario sem Guia valido nao deve cair em Avaliacao do Guia.
- Usuario com Guia valido, mas sem avaliacao, deve cair em Avaliacao do Guia.
- Usuario com Guia valido + avaliacao concluida segue para o gating do produto.

## Bugs Confirmados

### `/guia/` com erro 500

- Bug confirmado: `static(...)` sem import em `apps/core/views.py`.
- Status: corrigido no hotfix isolado do `/guia/`.

### 403 pos-login por `next` herdado de rota restrita

- Cenario observado: sair da sessao admin e entrar como usuario comum na mesma
  navegacao gerou `403 Forbidden`.
- Hipotese forte: o login do usuario comum ocorreu, mas o redirecionamento
  pos-login herdou `next` de rota administrativa/restrita.
- Status: causa confirmada por instrumentacao.
- Origem real: preservacao indevida de `next=/portal/dashboard/` no fluxo
  logout -> login.
- Mitigacao aplicada:
  - logout nao reaproveita mais `next`
  - `SafeLoginView` agora trata `/portal/dashboard/` como destino restrito para
    usuario nao-staff
- Status final: validado e encerrado funcionalmente.

### Estado residual de impersonacao / modo teste

- Ha evidencia concreta de duplicacao de sinalizacao de modo teste:
  - banner global em `base.html`
  - indicador local no portal
- A investigacao aberta agora precisa cobrir:
  - logout apos admin comum
  - logout apos modo teste
  - logout sem sair antes do modo teste
  - comparacao com janela anonima
- Status: patch minimo de limpeza explicita ja aplicado em `logout_view()` e
  `portal_impersonar_sair()`.
- Proximo passo: revalidacao operacional do `403` para confirmar se a causa
  residual foi neutralizada.

## Pendencias De Governanca/Admin

- implementar busca operacional de usuarios;
- implementar busca/listagem operacional por produto e entitlement;
- permitir concessao manual de acesso por produto;
- permitir remocao manual de acesso por produto;
- automatizar concessao administrativa do Guia junto com bonus;
- adicionar checkbox padrao:
  - `Enviar o Guia para o e-mail do usuario`
- registrar explicitamente a aquisicao/concessao administrativa do Guia;
- garantir que a concessao de bonus ao aluno beneficiario permita amarrar:
  - concessao de Guia valido
  - envio/preparacao de envio do Guia
  - exigencia posterior de Avaliacao do Guia
- melhorar visao de status por usuario na governanca;
- criar MVP de visao consolidada do status semantico do usuario;
- permitir concessao e remocao administrativa explicita do Guia;
- consolidar politica de sessao nao persistente no login escolar;
- reduzir/remover instrumentacao detalhada de autenticacao ou condiciona-la a
  `DEBUG=True`;
- corrigir o `404` do estatico `logo-sonhe-mais-alto.png`;
- adicionar filtros operacionais para casos inconsistentes;
- definir tratamento operacional de notificacao por e-mail/whatsapp ao admin.

## Automacoes Desejadas

- ao conceder bonus por admin, oferecer acao assistida para tambem conceder Guia
  explicito;
- preparar/disparar envio do Guia ao e-mail do usuario;
- registrar a origem da posse do Guia:
  - compra
  - concessao administrativa
- manter rastreavel a data de concessao/envio do Guia para suporte e auditoria;
- registrar estados inconsistentes relevantes para acompanhamento operacional.

## Itens Aprovados E Ainda Nao Implementados

- frente especifica de governanca/admin para concessao assistida do Guia;
- checkbox padrao de envio do Guia;
- busca rapida de usuario na governanca;
- concessao e remocao manual de acesso por produto diretamente na governanca;
- registro explicito da aquisicao/concessao do Guia para o aluno beneficiario do
  bonus;
- amarracao semantica entre bonus administrativo, Guia valido e exigencia do
  questionario de avaliacao;
- logout com limpeza explicita de chaves residuais de sessao
  (`impersonate_user_id`, `portal_mode` e correlatas);
- melhoria de visao operacional por usuario;
- possiveis alertas adicionais por whatsapp, se isso entrar no escopo de
  governanca.

## MVP Operacional De Governanca

Para a governanca ser efetiva no estado atual do projeto, o MVP precisa incluir:

1. busca de usuario;
2. leitura resumida do estado semantico do usuario;
3. visualizacao dos produtos/acessos atuais;
4. concessao manual por produto;
5. remocao manual por produto;
6. concessao explicita do Guia;
7. opcao padrao para envio do Guia ao aluno;
8. registro da origem e da data da posse do Guia;
9. garantia de que o aluno com Guia valido continue obrigado a preencher a
   Avaliacao do Guia;
10. filtros para identificar estados inconsistentes.

## Sequencia Minima Recomendada

1. inspecao/busca de usuario;
2. leitura do estado semantico consolidado;
3. concessao/remocao manual de produto;
4. concessao/remocao explicita do Guia;
5. acao assistida de envio do Guia;
6. registro e rastreabilidade da posse do Guia;
7. filtros operacionais para inconsistencia.

## Mudancas De Entendimento Relevantes

### Correcao da interpretacao anterior

Entendimento superado:

- bonus concedido por admin dispensaria Avaliacao do Guia

Entendimento correto:

- bonus concedido por admin nao dispensa Avaliacao do Guia;
- o que muda e a forma de obtencao do Guia;
- sem Guia valido, a proxima etapa nao e Avaliacao do Guia.
