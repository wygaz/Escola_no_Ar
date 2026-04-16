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

### Produto comercial nao e igual a capacidade de acesso

- O cadastro em `Produto` representa o item comercial/administrativo que pode
  ser vendido, concedido ou removido.
- O gating do sistema nao deve depender diretamente de qualquer produto novo
  cadastrado no admin.
- O runtime precisa trabalhar com um conjunto controlado de capacidades de
  acesso realmente suportadas no codigo.
- Um produto pode conceder uma ou mais capacidades de acesso.
- Produtos novos so podem liberar fluxo real depois de serem explicitamente
  mapeados para capacidades suportadas.
- Isso evita que um produto criado no admin pareca pronto sem existir fluxo,
  decorador, telas ou regras implementadas para ele.

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

### Demo institucional nao e compra nem posse do Guia

- o sistema precisa suportar um trilho proprio de demonstracao para prospeccao;
- esse trilho nao deve marcar:
  - compra;
  - posse valida do Guia;
  - avaliacao do Guia concluida;
- a demo deve ser rastreavel, temporaria e concedida apenas por staff/superuser;
- a demo pode servir tanto para conta demo institucional quanto para usuario
  real da instituicao em prospeccao;
- a demo deve ser compativel com futura parametrizacao por escola, logo e grupo
  de usuarios.

### Kit de degustacao institucional

- a prospeccao precisa oferecer uma forma rapida de experimentar o produto sem
  exigir o preenchimento integral das perguntas reais;
- o kit de degustacao nao deve expor o banco real de perguntas em lista aberta;
- o kit pode usar:
  - perfis demo prontos;
  - ajustes controlados de perfil;
  - miniquestionario proprio de demonstracao;
- o resultado gerado nessa trilha deve ser entendido como resultado demo, nao
  como avaliacao oficial do produto.

## Decisoes De Gating Ja Fechadas

- `core` continua sendo o eixo de entrada oficial dos produtos.
- CTAs principais do portal passam pelo `produto_resolver`.
- `has_legal` continua com prioridade propria.
- Usuario sem Guia valido nao deve cair em Avaliacao do Guia.
- Usuario com Guia valido, mas sem avaliacao, deve cair em Avaliacao do Guia.
- Usuario com Guia valido + avaliacao concluida segue para o gating do produto.
- Produtos comerciais e capacidades internas de acesso precisam ser tratados
  como camadas relacionadas, mas distintas.

### Familias operacionais vigentes

No momento, a operacao deve ser pensada sobre tres familias principais:

1. bonus de aquisicao do Guia:
   - pode vir da compra ou de concessao administrativa;
   - inclui acesso ao Sonhe + Alto e ao Vocacional 75;
2. Vocacional 150 questoes:
   - refinamento intermediario;
   - corresponde ao antigo `passe1`;
3. Vocacional Premium:
   - pode chegar a 1080 questoes;
   - combina base vocacional e habilidade profissional.
   - corresponde ao aprofundamento antes espalhado em `passe2` e `passe3`.

Essas familias operacionais sao a referencia de negocio atual, mesmo que ainda
existam slugs e equivalencias legadas no codigo.

Decisao de compatibilidade:

- a lista historica mais extensa de slugs internos nao representa mais a
  semantica oficial de negocio;
- ela permanece apenas para compatibilidade tecnica do runtime atual;
- a semantica oficial deve ser lida pelas 3 familias acima.

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
- separar no planejamento e no codigo o conceito de:
  - produto comercial
  - pacote de concessao
  - capacidade interna de acesso/gating;
- implementar operacoes em lote por grupo institucional;
- implementar acesso de demonstracao institucional temporario e rastreavel;
- implementar kit de degustacao institucional acoplado a demo;
- permitir cadastro em grupo para contratos com escola, igreja, comunidade e
  organizacoes equivalentes;
- permitir concessao em grupo por produto;
- permitir concessao em grupo por pacote/grupo de produtos;
- permitir remocao em grupo por produto quando houver necessidade operacional
  legitima;
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
- substituir a ideia de "conceder Guia" por fluxo proprio de envio promocional
  registrado, sem marcar posse valida por clique manual;
- consolidar politica de sessao nao persistente no login escolar;
- reduzir/remover instrumentacao detalhada de autenticacao ou condiciona-la a
  `DEBUG=True`;
- corrigir o `404` do estatico `logo-sonhe-mais-alto.png`;
- adicionar filtros operacionais para casos inconsistentes;
- definir tratamento operacional de notificacao por e-mail/whatsapp ao admin.
- revisar e reduzir a semantica exposta de acessos legados hoje espalhada em
  slugs de compatibilidade.

## Automacoes Desejadas

- ao conceder bonus por admin, oferecer acao assistida para tambem conceder Guia
  explicito;
- ao conceder um produto comercial, expandir automaticamente as capacidades de
  acesso correspondentes, quando houver mapeamento definido;
- ao operar contrato institucional, permitir fluxo assistido de cadastro e
  concessao em lote;
- permitir concessao de demo institucional com expiracao automatica;
- permitir parametrizacao basica da demo por instituicao:
  - nome;
  - logo;
  - identidade visual minima;
- permitir perfis demo prontos para degustacao institucional;
- permitir recalculo por ajustes controlados sem expor o questionario real;
- permitir modelos reaproveitaveis de concessao por grupo de produtos;
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
- cadastro em grupo para contratos institucionais;
- concessao em grupo por produto;
- concessao em grupo por grupo/pacote de produtos;
- concessao e remocao manual de acesso por produto diretamente na governanca;
- registro explicito da aquisicao/concessao do Guia para o aluno beneficiario do
  bonus;
- amarracao semantica entre bonus administrativo, Guia valido e exigencia do
  questionario de avaliacao;
- trilho proprio de demo institucional para prospeccao remota, sem falsificar
  compra, posse do Guia ou avaliacao;
- kit de degustacao institucional com perfis prontos, ajustes controlados e
  resultado demo;
- separacao tecnica entre cadastro de produto e capacidade efetiva de gating,
  sem exigir um decorador novo para cada produto comercial;
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

Extensao institucional prevista:

11. cadastro e concessao em lote por grupo institucional;
12. suporte a contrato por escola, igreja, comunidade ou grupo equivalente;
13. suporte a concessao por pacote de produtos, nao apenas por item isolado.
14. suporte a demo institucional temporaria, rastreavel e parametrizavel.
15. suporte a kit de degustacao institucional sem exposicao do banco real de
    perguntas.

## Sequencia Minima Recomendada

1. inspecao/busca de usuario;
2. leitura do estado semantico consolidado;
3. concessao/remocao manual de produto;
4. concessao/remocao explicita do Guia;
5. acao assistida de envio do Guia;
6. registro e rastreabilidade da posse do Guia;
7. filtros operacionais para inconsistencia.

Sequencia institucional posterior:

8. cadastro em lote por grupo;
9. concessao em lote por produto;
10. concessao em lote por grupo de produtos;
11. filtros por contrato/grupo institucional.
12. demo institucional para prospeccao remota, com expiracao e identidade da
    instituicao.
13. kit de degustacao institucional com perfis prontos e simulacao guiada.

## Mudancas De Entendimento Relevantes

### Correcao da interpretacao anterior

Entendimento superado:

- bonus concedido por admin dispensaria Avaliacao do Guia

Entendimento correto:

- bonus concedido por admin nao dispensa Avaliacao do Guia;
- o que muda e a forma de obtencao do Guia;
- sem Guia valido, a proxima etapa nao e Avaliacao do Guia.
