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

## 2. Principio Arquitetural

O projeto deve continuar obedecendo a diretriz atual:

- `core` e o centro de entrada, catalogo, gating, resolvedor e governanca.
- `apps/contas` permanece como base unica de usuarios.
- `apps/sonho_de_ser` passa a ser o runtime canonico do Sonhe+Alto.
- `apps/projeto21` permanece como fachada legada e compatibilidade de URL.
- `apps/vocacional` continua responsavel pela descoberta vocacional e pelo
  questionario/avaliacao do Guia.

Nao devemos espalhar regra de acesso, fluxo ou gamificacao em templates.

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

## 4. Estado Atual do Codigo

### 4.1 Ja Recuperado ou em Andamento

- O `core` controla o acesso pelo portal e resolvedor.
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

## 5. Direcao de Produto

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

## 6. Gamificacao Recuperada

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

## 7. Plano de Implementacao em Fases

### Fase A - Fechar o Ciclo Operacional do Aluno

Objetivo: consolidar `plano -> check-in -> historico -> pontuacao`.

Entregas:

- permitir consultar o plano ativo dentro do check-in;
- permitir alterar o plano sem perder o contexto;
- melhorar historico por data, area, objetivo e status;
- garantir que o check-in reflita apenas estrategias ativas do plano;
- documentar a regra basica de registro.

Status: em andamento.

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
- relatorios por turma;
- engajamento;
- gestao de mentores;
- certificados;
- possivel personalizacao de trilhas.

## 8. Proxima Fatia Recomendada

A proxima fatia deve ser pequena e diretamente ligada ao uso real:

1. Na tela `/projeto21/registro/`, exibir um resumo do plano ativo.
2. Adicionar link claro para alterar o plano.
3. Manter o check-in focado nas estrategias escolhidas.
4. Em seguida, melhorar `/projeto21/historico/`.
5. Depois, formalizar o servico de pontuacao.

Essa sequencia preserva a direcao historica sem abrir frentes grandes demais.

## 9. Riscos

- Reativar a comunidade antes da mentoria e moderacao cria risco operacional.
- Criar ranking cedo demais pode distorcer o incentivo.
- Implementar pontos direto no template quebraria a arquitetura.
- Reaproveitar templates legados sem saneamento pode reintroduzir fluxos mortos.
- Tratar `projeto21` como runtime principal de novo desfaz a consolidacao atual.

## 10. Criterio de Sucesso

Esta recuperacao sera bem-sucedida quando:

- o aluno montar um plano coerente;
- usar o sistema como ferramenta diaria, nao como transcricao posterior;
- enxergar progresso e incentivo;
- o mentor conseguir acompanhar sem depender de planilha;
- o `core` continuar centralizando acesso e navegacao;
- `sonho_de_ser` concentrar o dominio real do Sonhe+Alto.
