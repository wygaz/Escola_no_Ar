# Plano de Recuperacao do Escopo Sonhe + Alto

> Decisao de nomenclatura: para o publico, o produto se chama apenas
> **Sonhe + Alto**. Os nomes historicos `Sonho de Ser`, `Projeto 21`,
> `projeto21` e `sonho_de_ser` podem aparecer neste documento ou no codigo
> apenas como legado tecnico, fonte historica ou compatibilidade temporaria.
> A regra completa esta em `decisao_nomenclatura_sonhe_mais_alto.md`.

## 1. Finalidade

Este documento transforma o escopo historico que passou pelos nomes **Sonho de
Ser** e **Projeto 21**, posteriormente incorporado ao produto **Sonhe + Alto**,
em um guia
pratico de desenvolvimento.

Ele parte de duas fontes principais:

- `Projeto Sonho de Ser.docx`, que registra a visao original de rede social
  vocacional, gamificacao e mentoria.
- `Mapa funcional SonhoDeSer.docx`, que organiza os tipos de usuarios, paginas,
  rotas e modulos sugeridos.

O objetivo nao e recriar o projeto do zero. O objetivo e recuperar o escopo sem
perder o que ja funciona hoje no codigo.

Esta versao tambem incorpora o alinhamento posterior da reforma arquitetural
registrado em `planejamento_geral_reforma_arquitetural.zip`, incluindo:

- `core` como centro oficial de navegacao de produtos;
- governanca como experiencia propria de staff/superuser;
- compatibilidade transitoria do portal atual;
- regra semantica corrigida sobre Guia, avaliacao do Guia e concessao
  administrativa de acesso;
- o valor do wireframe da reforma como correcao de fluxo, nao apenas de layout;
- distincao operacional entre visitante, usuario autenticado comum e
  staff/superuser.

## 2. Principio Arquitetural

O projeto deve continuar obedecendo a diretriz atual:

- `core` e o centro de entrada, catalogo, gating, resolvedor e governanca.
- `apps/contas` permanece como base unica de usuarios.
- `apps/sonho_de_ser` passa a ser o runtime canonico do Sonhe+Alto.
- `apps/projeto21` permanece como fachada legada e compatibilidade de URL.
- `apps/vocacional` continua responsavel pela descoberta vocacional e pelo
  questionario/avaliacao do Guia.

Nao devemos espalhar regra de acesso, fluxo ou gamificacao em templates.

### 2.2 Estado arquitetural presente

Com base no pacote da reforma estrutural, o estado-alvo imediato da plataforma e
este:

- existe uma unica entrada oficial de produtos no `core`, mesmo que o `portal`
  atual ainda exista como camada de compatibilidade;
- `staff/superuser` nao devem cair por padrao no funil do aluno;
- a governanca nasce da estrutura atual de dashboard, sem criar base paralela;
- o `core` orquestra entrada, status, gating agregado e navegacao global;
- os apps de produto mantem posse de seus fluxos internos;
- qualquer evolucao do Sonhe + Alto precisa respeitar esse trilho.

### 2.3 Valor do wireframe da reforma

Os wireframes produzidos na etapa da reforma nao devem ser lidos apenas como
proposta de interface. Eles registram uma correcao de arquitetura de navegacao.

Valor pratico do wireframe:

- recolocar o `core` como centro distribuidor de fluxos e acessos;
- evitar que cards e templates mandem o usuario diretamente para paginas
  internas dispersas;
- diferenciar melhor o percurso de visitante, usuario comum e staff;
- deixar claro que a governanca nao e uma extensao do funil do aluno;
- servir como referencia de fluxo para futuras alteracoes no portal e na
  vitrine oficial.

### 2.1 Parametrizacao de Identidade

Como o escopo final inclui escolas, turmas e possiveis parceiros institucionais,
qualquer evolucao de identidade visual ou textual deve evitar hardcode sempre que
possivel.

Diretriz:

- nomes de programa, escola, turma e parceiro devem poder vir de configuracao ou
  contexto;
- textos institucionais devem ser centralizados quando forem reutilizaveis;
- cores, logos e elementos de marca devem ser preparados para futura
  personalizacao por escola;
- o MVP pode usar a identidade padrao Sonhe+Alto, mas sem impedir
  personalizacao futura;
- templates nao devem conter regras de negocio para decidir identidade ou acesso.

## 3. Escopo Historico Recuperado

### 3.1 Tipos de Usuario

O mapa funcional descreve tres grupos principais:

- Aluno: escolhe programa, realiza desafios, registra progresso e participa da
  comunidade.
- Mentor/Orientador: acompanha alunos, envia mensagens, aprova ou comenta
  atividades e medeia interacoes.
- Admin/Escola: gerencia mentores, acompanha desempenho geral, personaliza
  trilhas e emite certificados.

### 3.1.1 Distincao operacional atual de acesso

Para a navegacao e o gating atuais, a plataforma deve considerar pelo menos
quatro estados operacionais:

- Visitante: nao autenticado. Pode ver paginas publicas, landing e informacoes
  institucionais, mas nao entra no fluxo protegido.
- Usuario autenticado comum: possui conta e pode ter pendencias de termos,
  Guia, avaliacao do Guia e acesso a produto.
- Usuario autenticado com acesso valido ao produto: cumpriu os pre-requisitos do
  trilho e pode entrar no fluxo correspondente.
- Staff/Superuser: por padrao entra na governanca; so percorre o fluxo do aluno
  quando estiver explicitamente em modo de teste.

Essa distincao e importante porque "usuario autenticado" nao significa "usuario
autorizado a navegar em qualquer produto".

### 3.2 Modulos Funcionais

O escopo historico previa:

- autenticacao e cadastro;
- landing publica;
- perfil do aluno;
- programa/desafio de desenvolvimento;
- registro diario;
- gamificacao;
- comunidade moderada;
- area do mentor;
- area da escola/admin;
- certificados e reconhecimento.

### 3.3 Requisito institucional de operacao em grupo

Como o produto deve poder atender contratos com escola, igreja, comunidade ou
outro grupo organizado, a governanca precisa prever operacao institucional em
lote.

Isso inclui:

- cadastro em grupo;
- concessao em grupo por produto;
- concessao em grupo por pacote de produtos;
- leitura de status por grupo/contrato;
- possibilidade de amarrar nesses lotes a concessao do Guia, o envio do Guia e
  a exigencia posterior da Avaliacao do Guia.

Esse requisito nao substitui a governanca individual; ele a amplia para o caso
institucional.

## 4. Estado Atual do Codigo

### 4.1 Ja Recuperado ou em Andamento

- O `core` controla o acesso pelo portal e resolvedor.
- O `core` ja possui `product_registry` inicial para centralizar a definicao dos
  produtos expostos pelo portal.
- O gating considera cadastro, termos, avaliacao do Guia e acesso ao produto.
- `/projeto21/` continua como fachada legada.
- `/projeto21/plano/` aponta para o runtime canonico em `apps/sonho_de_ser`.
- O plano do aluno ja usa area, nivel, objetivo e estrategias filtradas.
- O catalogo de estrategias foi recuperado do JSON legado, com dosagem.
- O check-in diario grava registros por estrategia.
- O historico existe, ainda simples.
- A pontuacao existe como leitura inicial, ainda sem regra completa de
  gamificacao.

### 4.2 Parcial ou Stub

- Dashboard do aluno existe, mas ainda nao expressa a jornada pedagogica.
- Vitrine de produtos/portal ainda carrega hardcodes que precisam migrar para o
  trilho central do `core`.
- Governanca existe, mas ainda precisa amadurecer o papel de painel de comando
  da plataforma.
- Mentor existe como modelos/API parcial, mas a tela web ainda e stub.
- Registro diario existe, mas ainda precisa ficar mais ergonomico.
- Historico precisa virar leitura util da evolucao.
- Pontuacao precisa virar regra formal.

### 4.3 Ainda Nao Recuperado

- Perfil do aluno como pagina real.
- Selos/conquistas.
- Ranking amigavel.
- Comunidade/feed moderado.
- Reacoes positivas.
- Painel escolar/admin por turma.
- Certificados.
- Personalizacao de trilhas por escola.

### 4.4 Artefatos Legados Encontrados

Existem templates antigos em `templates/sonho_de_ser`:

- `perfil_aluno.html`
- `desafio_dia.html`
- `feed_comunidade.html`
- `mentor_home.html`

Esses arquivos indicam intencao de produto, mas ainda nao sao implementacao
confiavel. Alguns possuem `extends` quebrado ou dependem de modelos que nao
existem no runtime atual.

## 5. Regra revisada de acesso, Guia e navegacao

O ponto mais importante da compatibilizacao atual e que o sistema nao pode mais
confundir:

- compra do Guia;
- posse valida do Guia;
- avaliacao do Guia;
- entitlement de produto/bonus;
- liberacao administrativa.

### 5.1 Sequencia logica obrigatoria

A ordem semantica correta do gating e:

1. Termos e consentimento legal.
2. Possui Guia como pre-requisito valido?
3. Avaliacao do Guia concluida?
4. Entitlement/liberacao do produto especifico?
5. Entrada no fluxo interno do produto.

### 5.2 Posse valida do Guia

"Possui Guia" nao significa apenas compra na Hotmart.

O Guia pode se tornar valido por dois caminhos:

- compra regular do Guia;
- concessao administrativa valida, quando a equipe libera esse pre-requisito.

Consequencia:

- bonus concedido por admin nao dispensa avaliacao do Guia;
- usuario sem Guia valido nao deve cair na Avaliacao do Guia;
- primeiro resolve a posse valida do Guia;
- depois a Avaliacao do Guia passa a ser exigida;
- depois entram os gates especificos do produto.

### 5.3 Regra de visitante, usuario e staff

- Visitante: pode conhecer os produtos, mas nao executa fluxo protegido.
- Usuario comum autenticado: pode ver o portal, mas a navegacao real depende do
  estado de onboarding, Guia e entitlement.
- Staff/Superuser: entra em governanca por padrao e nao serve como prova de que
  o gating do aluno esta correto, salvo quando usa modo de teste/persona.

### 5.4 Implicacao para Sonhe + Alto

O Sonhe + Alto deve continuar obedecendo ao mesmo trilho semantico:

- termos e consentimento;
- posse valida do Guia;
- avaliacao do Guia;
- entitlement/liberacao do produto;
- entrada no fluxo interno.

### 5.5 Produto comercial x gating interno

Um ponto de compatibilizacao importante da fase atual e nao confundir:

- produto cadastrado na tabela `Produto`;
- permissao/acesso concedido ao usuario;
- capacidade de gating realmente suportada no codigo.

Hoje o projeto ainda carrega slugs e equivalencias legadas para preservar
compatibilidade. Isso nao deve ser lido como catalogo oficial de negocio.

Diretriz segura:

- `Produto` continua sendo o catalogo dinamico do que pode ser vendido ou
  concedido;
- a governanca pode operar em cima desse catalogo;
- o runtime do sistema deve depender apenas de capacidades de acesso
  explicitamente suportadas;
- um produto comercial pode liberar uma ou mais capacidades de acesso;
- um produto novo cadastrado no admin nao deve criar automaticamente um fluxo
  novo nem exigir um decorador novo por si so.

Consequencia pratica:

- o sistema precisa caminhar para uma camada de mapeamento entre produto
  comercial e capacidades de acesso;
- os decoradores e gates devem checar capacidades conhecidas, nao qualquer item
  dinamico criado no admin;
- a expansao comercial continua possivel, mas so vira fluxo real quando houver
  mapeamento e implementacao correspondente.

### 5.6 Familias de produto vigentes no negocio

Na fase atual, a operacao pratica esta concentrada em tres familias:

1. bonus de aquisicao do Guia:
   inclui Sonhe + Alto e Vocacional 75;
   pode tambem ser concedido pela administracao;
2. Vocacional 150 questoes:
   refinamento intermediario;
   corresponde ao antigo `passe1`;
3. Vocacional Premium:
   pode chegar a 1080 questoes, combinando base vocacional e habilidade
   profissional;
   corresponde ao aprofundamento que antes ficou espalhado como `passe2` e
   `passe3`.

Essas familias devem orientar a governanca e a futura camada de mapeamento,
mesmo que o codigo ainda contenha slugs historicos de transicao.

Os slugs antigos mais numerosos devem ser tratados apenas como alias tecnicos
de compatibilidade, nao como expansao oficial do portfolio.

Diretriz de continuidade:

- depois da limpeza semantica e do saneamento de gating/governanca, os tres
  ambientes comerciais devem receber tratamento proprio mais profissional:
  - Basico
  - Intermediario
  - Premium
- essa evolucao fica registrada como etapa posterior deliberada, para nao se
  perder durante a fase de compatibilizacao tecnica.

- sem pendencia legal;
- com Guia valido;
- com avaliacao do Guia, quando exigida como pre-requisito do programa;
- com entitlement/liberacao do produto correspondente;
- so entao entra no fluxo operacional do aluno.

## 6. Direcao de Produto

O Sonhe+Alto nao deve ser apenas uma lista de tarefas. Ele deve ser uma
ferramenta operacional para o aluno transformar descoberta vocacional em pratica
diaria.

O ciclo principal deve ser:

1. aluno entende a proposta;
2. monta plano por area, nivel e objetivo;
3. registra sua rotina no check-in;
4. acompanha historico e progresso;
5. recebe incentivo por consistencia;
6. eventualmente recebe acompanhamento de mentor/escola.

## 7. Governanca operacional recuperada

O material da reforma estrutural reforca que a governanca nao e apenas um menu
de persona. Ela deve funcionar como painel de comando da plataforma.

Diretrizes preservadas:

- superusuario/staff devem cair na governanca por padrao;
- a governanca deve permitir busca de usuario, inspecao de estado e concessao
  manual segura;
- a governanca nao substitui `apps/contas`, apenas opera sobre a base unica de
  usuarios e acessos;
- a governanca nao deve criar regra paralela de produto;
- qualquer liberacao administrativa deve respeitar a semantica correta de Guia,
  avaliacao e bonus.
- a governanca deve crescer para suportar tambem operacoes em lote por grupo
  institucional, sem criar base paralela de usuarios ou acessos.

MVP coerente:

- cards executivos principais;
- busca de usuario;
- estado resumido do usuario;
- persona de teste;
- concessao manual controlada de acesso;
- memoria viva de pendencias e decisoes em `docs/arquitetura/pendencias_governanca.md`.

## 8. Gamificacao Recuperada

O material historico menciona:

- pontos por consistencia;
- selos por categorias;
- ranking positivo por participacao, nao por comparacao agressiva;
- reconhecimento por escola;
- certificados;
- destaque por qualidades como empatia, inovacao, resiliencia e proatividade;
- selos com linguagem formativa, como `Servo Lider`, `Discipulo Criativo` e
  `Mordomo de Talentos`.

Para o MVP, a gamificacao deve ser pessoal e formativa, nao competitiva.

## 9. Plano de Implementacao em Fases

### Fase A - Fechar o Ciclo Operacional do Aluno

Objetivo: consolidar `plano -> check-in -> historico -> pontuacao`.

Entregas:

- permitir consultar o plano ativo dentro do check-in;
- permitir alterar o plano sem perder o contexto;
- melhorar historico por data, area, objetivo e status;
- garantir que o check-in reflita apenas estrategias ativas do plano;
- documentar a regra basica de registro.

Status: em andamento.

Dependencia de compatibilidade:

- qualquer melhoria de portal, vitrine ou CTA de entrada deve respeitar a regra
  revisada de visitante, Guia valido, avaliacao do Guia e entitlement.

### Fase B - Gamificacao MVP

Objetivo: transformar registros em incentivo simples e confiavel.

Regra inicial sugerida:

- `FEITO`: 100% dos pontos da estrategia;
- `PARCIAL`: 50% dos pontos da estrategia;
- `NAO_FIZ`: 0 ponto;
- pontos da estrategia vem de `Estrategia.pontos`;
- bonus de constancia pode ser calculado depois, sem gravar inicialmente.

Entregas:

- servico central de calculo de pontos;
- pontuacao diaria;
- pontuacao semanal;
- total do plano;
- dashboard com progresso real.

### Fase C - Selos e Conquistas

Objetivo: reconhecer consistencia e marcos formativos.

Selos MVP:

- Primeiro Passo: primeiro check-in;
- Constancia 3: tres dias com registro;
- Semana Firme: sete dias com registro;
- Jornada 21: ciclo de 21 dias com registros;
- selos por area quando houver registros relevantes em Familia, Igreja, Escola,
  Amigos, Comunidade e Eu mesmo.

Evitar ranking nesta fase.

### Fase D - Perfil do Aluno

Objetivo: dar ao aluno uma pagina de identidade e progresso.

Entregas:

- dados basicos do usuario;
- plano ativo;
- progresso geral;
- selos conquistados;
- historico resumido;
- link para trocar/editar plano.

### Fase E - Mentor Operacional

Objetivo: permitir acompanhamento real, sem rede social ainda.

Entregas:

- mentor ve mentorados;
- mentor ve plano e registros;
- mentor adiciona anotacoes;
- aluno pode ver anotacoes permitidas;
- filtros por data, area e status.

### Fase F - Comunidade Moderada

Objetivo: recuperar a ideia de rede social de forma segura.

Entregas futuras:

- feed de vitorias;
- postagens curtas;
- reacoes positivas;
- moderacao por mentor/admin;
- filtro por escola/programa/mentor.

Esta fase deve vir somente depois de plano, registro, pontuacao, selos e mentor
estarem coerentes.

### Fase G - Escola/Admin

Objetivo: recuperar o escopo institucional.

Entregas futuras:

- turmas;
- contratos/grupos institucionais;
- cadastro em lote;
- concessao em lote por produto;
- concessao em lote por grupo de produtos;
- relatorios por turma;
- engajamento;
- gestao de mentores;
- certificados;
- possivel personalizacao de trilhas.

## 10. Compatibilizacao imediata obrigatoria

Antes de abrir novas frentes maiores de UX ou gamificacao, o projeto deve
preservar estas decisoes como contrato:

- o `core` continua sendo a unica entrada oficial de produto;
- o `portal` atual deve caminhar para compatibilidade, nao para nova fonte de
  verdade;
- CTA global de produto deve passar pelo resolvedor central, salvo excecao bem
  documentada;
- nao criar camada paralela para status, permissao, onboarding ou governanca;
- nao tratar concessao administrativa de bonus como liberacao irrestrita do
  ecossistema;
- qualquer ajuste de Sonhe + Alto no portal ou na governanca deve ser validado
  contra essa semantica.

## 11. Proxima Fatia Recomendada

A proxima fatia deve ser pequena e diretamente ligada ao uso real:

1. Preservar a compatibilidade semantica do gating e da governanca enquanto o
   `core` consolida a vitrine/entrada oficial.
2. Tirar hardcodes remanescentes do portal atual usando o `product_registry`.
3. Manter o resolvedor central como entrada obrigatoria dos produtos.
4. Na trilha do aluno, continuar com resumo do plano ativo em
   `/projeto21/registro/` e link claro para alterar o plano.
5. Em seguida, melhorar `/projeto21/historico/`.
6. Depois, formalizar o servico de pontuacao.

Essa sequencia preserva a direcao historica sem abrir frentes grandes demais.

## 12. Riscos

- Reativar a comunidade antes da mentoria e moderacao cria risco operacional.
- Criar ranking cedo demais pode distorcer o incentivo.
- Implementar pontos direto no template quebraria a arquitetura.
- Reaproveitar templates legados sem saneamento pode reintroduzir fluxos mortos.
- Tratar `projeto21` como runtime principal de novo desfaz a consolidacao atual.
- Confundir compra do Guia com posse valida do Guia reabre erro semantico de
  gating.
- Tratar bonus administrativo como atalho que ignora Avaliacao do Guia quebra a
  regra de negocio aprovada.
- Deixar staff navegar como aluno por padrao mascara defeitos de autorizacao.

## 13. Criterio de Sucesso

Esta recuperacao sera bem-sucedida quando:

- o aluno montar um plano coerente;
- usar o sistema como ferramenta diaria, nao como transcricao posterior;
- enxergar progresso e incentivo;
- o mentor conseguir acompanhar sem depender de planilha;
- o `core` continuar centralizando acesso e navegacao;
- `sonho_de_ser` concentrar o dominio real do Sonhe+Alto;
- visitante, usuario comum e staff tenham comportamento coerente e auditavel;
- a concessao administrativa respeitar a semantica correta de Guia e avaliacao;
- a governanca operar como painel proprio, sem virar duplicacao do fluxo do
  aluno.
