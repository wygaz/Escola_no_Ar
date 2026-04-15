# Guia de Desenvolvimento Sonhe+Alto

## Objetivo deste documento

Este arquivo e um guia interno de desenvolvimento.
Ele nao substitui o livreto do produto.
Ele traduz a promessa do produto Sonhe+Alto para uma arquitetura de software executavel, incremental e coerente com o que ja existe no projeto.

A meta nao e reconstruir do zero.
A meta e consolidar, sanear e concluir.

---

## 1. Leitura de produto consolidada

O livreto `Guia_Descoberta_Quem_Sou_Eu-envio.docx` deixa claro o papel do Sonhe+Alto:

- o Vocacional e a etapa de descoberta;
- o livreto consolida a compreensao e faz a chamada para acao;
- o Sonhe+Alto e a etapa pratica;
- o aluno precisa transformar reflexao em rotina, estrategia, registro, pontuacao e progresso;
- a jornada tem carater operacional, nao apenas visual.

O produto prometido ao aluno inclui:

- 6 areas da vida: Familia, Igreja, Escola, Amigos, Comunidade, Eu mesmo;
- objetivos por area;
- estrategias/habitos praticos;
- plano com inicio, periodo e acompanhamento;
- registro diario;
- progresso por semana e por area;
- pontuacao;
- niveis;
- acompanhamento por mentor/professor;
- jornada de 21 dias como motor inicial.

Conclusao:

- Browse = ambiente operacional de execucao do aluno;
- Dashboard = ambiente de leitura e acompanhamento do progresso;
- o sistema precisa refletir essa divisao claramente.

---

## 2. Arquitetura alvo pe-no-chao

### 2.1 Papel de cada modulo

- `core` = porta de entrada, gating, resolver de produto, governanca e navegacao central;
- `vocacional` = descoberta, avaliacao, resultado, refinamento e ponte pedagogica;
- `sonho_de_ser` = runtime canonico do Sonhe+Alto;
- `projeto21` = legado estrutural, compatibilidade e fonte de reaproveitamento visual/conceitual.

### 2.2 Leitura pratica

- o nome publico continua sendo Sonhe+Alto;
- `projeto21` nao deve ser expandido como app principal;
- `sonho_de_ser` deve concentrar o dominio e o runtime;
- `projeto21` deve ser tratado como casca legacy e camada de compatibilidade enquanto a migracao acontece;
- o `core` continua sendo o centro oficial de acesso.

---

## 3. Estado real do codigo

## 3.1 Core

O `core` ja esta funcionalmente maduro como integrador:

- possui `produto_resolver`;
- possui gating por login, legal, guia e produto;
- trata Sonhe+Alto por `PROD_SONHEMAISALTO`;
- o portal aponta para `produto_resolver('sonhe-mais-alto')`;
- a landing de Sonhe+Alto ainda aponta para `/projeto21/`;
- ha compatibilidade de slugs para `projeto21`, `projeto21_sonhe_alto` e `sonhemaisalto`.

Leitura:

- a entrada esta centralizada do jeito certo;
- a saida do resolver ainda desemboca no legado web do Projeto21.

## 3.2 App `apps/projeto21`

O app `projeto21` hoje esta leve e legacy:

- `models.py` tem somente `Area` e `Estrategia` em formato antigo;
- `views.py` tem basicamente uma landing protegida por gating;
- `urls.py` entrega `home` e um alias de `plano`, ambos para a mesma landing;
- o valor principal de `projeto21` hoje esta mais em materiais auxiliares e no nome legado do que em runtime real.

Leitura:

- `projeto21` nao e o backend principal do produto;
- ele funciona como fachada legacy e compatibilidade de rota/nome;
- seus modelos antigos nao devem voltar a comandar a arquitetura.

## 3.3 App `apps/sonho_de_ser`

O app `sonho_de_ser` e o ponto mais importante para a retomada.
Ele contem:

- modelos para `Area`, `Estrategia`, `RegistroDiario`, `MentorProfile`, `Mentoria`, `AnotacaoMentor`, `Plano` e `PlanoItem`;
- formularios para plano e registro;
- views web para dashboard, plano, registro, historico, pontuacao e mentor;
- API DRF para areas, estrategias, registros, perfis de mentor, mentorias e anotacoes;
- templates proprios de `projeto21_dashboard`, `projeto21_plano`, `projeto21_registro` etc.

Leitura:

- `sonho_de_ser` ja e a base mais promissora para o runtime canonico;
- porem o codigo esta parcialmente convergente e parcialmente quebrado por deriva entre versoes.

---

## 4. Desalinhamentos tecnicos confirmados

## 4.1 Deriva entre modelos e services

`apps/sonho_de_ser/models.py` ja trabalha com `Plano` e `PlanoItem`.

Mas `apps/sonho_de_ser/services.py` ainda referencia:

- `PlanoEstrategia`
- `RegistroDiario` com relacoes e campos de uma versao antiga

Leitura:

- `services.py` nao esta alinhado ao modelo atual;
- nao deve ser tratado como fonte confiavel sem saneamento.

## 4.2 Deriva entre modelos e serializers

`serializers.py` assume campos que nao aparecem no `models.py` atual, por exemplo:

- `RegistroDiario.concluido`
- `RegistroDiario.nota`
- `RegistroDiario.observacao`
- campos de `MentorProfile` como `bio`, `telefone`, `ativo`, `criado_em`
- campos de `Mentoria` como `aluno`, `inicio`, `fim`, `notas`, `atualizado_em`
- campos de `AnotacaoMentor` como `autor`, `visibilidade`, `criado_em`

Leitura:

- a API nao esta coerente com o dominio atual;
- parte desse codigo parece vinda de uma versao anterior ou paralela do modelo.

## 4.3 Deriva entre models e permissions

`permissions.py` usa `Mentoria` como se tivesse:

- `mentor` apontando para `MentorProfile`
- `aluno`
- `status="ativa"`

Mas o modelo atual de `Mentoria` define:

- `mentor` como `AUTH_USER_MODEL`
- `mentorado`
- `status` em maiusculas (`ATIVA`, `PENDENTE`, etc.)

Leitura:

- ha ruptura real entre regra de permissao e modelo persistido.

## 4.4 Views parcialmente funcionais

As views web se dividem em dois grupos:

- um grupo de stubs/template views;
- um grupo de views operacionais mais recentes (`plano_view`, `registro_view`, `historico_view`, `pontuacao_view`).

Problemas confirmados:

- `Projeto21HistoricoView` aponta para `templates/sonho_de_ser/projeto21_historico.html`, mas esse template nao existe;
- `Projeto21RegistroHojeView` aponta para template, mas o template atual ainda esta em stub;
- parte das views ainda carrega marcas de arquitetura antiga;
- ha calculos de progresso ainda improvisados no corpo das views.

## 4.5 Dashboard ainda e casca visual

`templates/sonho_de_ser/projeto21_dashboard.html` ja expressa a divisao certa entre:

- Meu Plano
- Registro Diario
- Pontuacao e Progresso
- Mentor

Mas o dashboard ainda depende de indicadores simples e incompletos:

- `registros_hoje`
- `estrategias_count`
- `adesao_semana`

Leitura:

- a estrutura visual do dashboard existe;
- o dashboard como modulo de leitura do produto ainda nao existe de forma robusta.

## 4.6 Landing legacy mais rica que o runtime

`templates/projeto21/landing.html` e uma landing longa, rica e cheia de material promocional/operacional.
Ela ja incorpora:

- narrativa do produto;
- geracao de kits;
- explicacoes pedagogicas;
- linguagem de Sonhe+Alto.

Leitura:

- a fachada publica esta mais desenvolvida do que o runtime do aluno;
- ha material reaproveitavel ali, mas ele nao deve ditar a arquitetura de dominio.

---

## 5. O que ja existe de valor reaproveitavel

## 5.1 Em `sonho_de_ser`

Reaproveitar:

- `Area` com as 6 iniciais canonicas;
- `Estrategia` com area, nivel, pontos, ordem e ativacao;
- `Plano` e `PlanoItem` como base minima do Browse;
- `RegistroDiario` como prova de execucao diaria;
- formularios de plano e registro como base inicial;
- templates de dashboard/plano/pontuacao como casca inicial;
- URLs web e rotas de API como espinha de navegacao.

## 5.2 Em `projeto21`

Reaproveitar:

- compatibilidade de naming e rotas;
- landing publica/protegida;
- materiais auxiliares e datasets;
- elementos textuais e visuais que ajudem a montar a experiencia Sonhe+Alto.

Nao reaproveitar como fonte de verdade:

- o modelo antigo de `Area`/`Estrategia`;
- qualquer tentativa de fazer o dominio principal morar em `apps/projeto21`.

## 5.3 No `core`

Reaproveitar:

- resolver central;
- gating centralizado;
- equivalencias de slug;
- portal e CTA central;
- permissao semantica de acesso ao produto.

---

## 6. Gaps entre promessa do produto e implementacao

Hoje o produto promete mais do que a base atual entrega de forma consistente.

### 6.1 Browse prometido

O aluno deveria conseguir:

- escolher area;
- escolher objetivo;
- selecionar estrategias/habitos;
- montar um plano;
- registrar a execucao diaria;
- revisar historico;
- manter constancia.

### 6.2 Browse realmente existente

Hoje existe parcialmente:

- selecao de estrategias;
- plano ativo;
- registro diario basico;
- historico parcial;
- algumas telas e stubs.

### 6.3 Dashboard prometido

O aluno deveria enxergar:

- progresso por area;
- progresso semanal;
- pontuacao total;
- nivel atual;
- avancos da jornada;
- proximos passos;
- apoio de mentor.

### 6.4 Dashboard realmente existente

Hoje existe parcialmente:

- card de entrada;
- contagem simplificada;
- adesao semanal simplificada;
- links para areas do runtime.

### 6.5 Mentoria prometida

O produto sugere:

- apoio de mentor/professor;
- check-ins;
- acompanhamento.

### 6.6 Mentoria realmente existente

Hoje existe um dominio de mentoria no `models.py`, mas:

- serializers, permissions e views estao desalinhados;
- o fluxo nao parece confiavel para evolucao sem saneamento.

---

## 7. Decisao arquitetural de retomada

### 7.1 Decisao principal

Adotar `apps/sonho_de_ser` como base canonica de runtime do Sonhe+Alto.

### 7.2 Decisao de compatibilidade

Manter `apps/projeto21` como:

- legado;
- fachada;
- compatibilidade de rota/nome;
- fonte de reaproveitamento visual e de materiais.

### 7.3 Decisao de integracao

Manter o `core` como:

- centro de entrada;
- resolvedor de fluxo;
- orquestrador de acesso;
- dono do gating.

### 7.4 O que nao fazer

- nao reconstruir o produto em um terceiro app;
- nao promover `apps/projeto21` de volta a modulo principal;
- nao tentar resolver com dashboard cosmetico;
- nao expandir APIs antigas sem alinhar o modelo;
- nao espalhar regra de negocio em templates.

---

## 8. Plano de execucao em fases pequenas

## Fase A - Auditoria e congelamento da arquitetura

Objetivo:

- consolidar diagnostico;
- congelar a arquitetura canonica;
- registrar gaps.

Saida esperada:

- este guia.

Status:

- concluida com a criacao deste documento.

## Fase B - Saneamento do dominio canonico

Objetivo:

- alinhar `models.py`, `forms.py`, `permissions.py`, `serializers.py`, `services.py` e `views.py` em torno do mesmo dominio.

Arquivos principais:

- `apps/sonho_de_ser/models.py`
- `apps/sonho_de_ser/forms.py`
- `apps/sonho_de_ser/permissions.py`
- `apps/sonho_de_ser/serializers.py`
- `apps/sonho_de_ser/services.py`
- `apps/sonho_de_ser/views.py`

Entregaveis minimos:

- eliminar referencias a classes antigas como `PlanoEstrategia`;
- definir o contrato real de `RegistroDiario`;
- alinhar `Mentoria` e `MentorProfile`;
- remover ruptura entre serializer e modelo;
- garantir que as URLs web apontem apenas para views/templates existentes.

## Fase C - Browse minimo funcional

Objetivo:

- entregar a menor fatia util do produto para o aluno.

Capacidades minimas:

- abrir dashboard inicial;
- montar plano por estrategias;
- registrar o dia;
- ver historico recente;
- ver progresso semanal basico.

Arquivos principais:

- `apps/sonho_de_ser/views.py`
- `apps/sonho_de_ser/forms.py`
- `templates/sonho_de_ser/projeto21_plano.html`
- `templates/sonho_de_ser/projeto21_registro.html`
- `templates/sonho_de_ser/projeto21_historico.html` a criar
- `templates/sonho_de_ser/projeto21_dashboard.html`

## Fase D - Dashboard real ligado ao dominio

Objetivo:

- transformar o dashboard em leitura de progresso de verdade.

Capacidades minimas:

- progresso semanal real;
- progresso por area;
- total de estrategias ativas no plano;
- adesao;
- pontuacao;
- nivel atual;
- proximos passos.

Arquivos principais:

- `apps/sonho_de_ser/services.py`
- `apps/sonho_de_ser/views.py`
- `templates/sonho_de_ser/projeto21_dashboard.html`
- `templates/sonho_de_ser/projeto21_pontuacao.html`

## Fase E - Mentoria e check-ins

Objetivo:

- colocar a camada de acompanhamento em funcionamento coerente.

Capacidades minimas:

- vinculo mentor-mentorado coerente;
- anotacoes;
- visibilidade adequada;
- tela util para mentor.

Arquivos principais:

- `apps/sonho_de_ser/models.py`
- `apps/sonho_de_ser/permissions.py`
- `apps/sonho_de_ser/serializers.py`
- `apps/sonho_de_ser/views.py`
- `templates/sonho_de_ser/projeto21_mentor.html`

## Fase F - Integracao final com Core e limpeza de legado

Objetivo:

- apontar a experiencia oficialmente para o runtime canonico;
- reduzir confusao entre `projeto21` e `sonho_de_ser`.

Capacidades minimas:

- resolver central apontando para a entrada certa;
- landing e portal com CTA coerente;
- legado mantido apenas onde ainda for necessario;
- nomenclatura mais clara para o time sem quebrar compatibilidade.

Arquivos principais:

- `apps/core/views.py`
- `apps/core/permissions.py`
- `templates/core/portal.html`
- `templates/core/sonhe_mais_alto_landing.html`
- `apps/projeto21/views.py`
- `apps/projeto21/urls.py`

---

## 9. Menor fatia util recomendada para iniciar implementacao

A primeira fatia util nao deve tentar resolver tudo.

Deve entregar apenas isto:

- plano ativo do aluno em `sonho_de_ser`;
- registro diario funcional;
- historico funcional;
- dashboard simples, mas verdadeiro;
- tudo coerente com `Plano`, `PlanoItem` e `RegistroDiario`.

Essa fatia ja permite:

- sair do terreno de template vazio;
- validar o runtime do aluno;
- preparar pontuacao e mentoria depois;
- avançar sem big bang.

---

## 10. Ordem pratica recomendada

### Bloco 1 - saneamento obrigatorio

1. `apps/sonho_de_ser/models.py`
2. `apps/sonho_de_ser/forms.py`
3. `apps/sonho_de_ser/permissions.py`
4. `apps/sonho_de_ser/serializers.py`
5. `apps/sonho_de_ser/services.py`
6. `apps/sonho_de_ser/views.py`
7. `apps/sonho_de_ser/urls.py`

### Bloco 2 - Browse minimo

1. `templates/sonho_de_ser/projeto21_plano.html`
2. `templates/sonho_de_ser/projeto21_registro.html`
3. `templates/sonho_de_ser/projeto21_historico.html`
4. `templates/sonho_de_ser/projeto21_dashboard.html`
5. `templates/sonho_de_ser/projeto21_pontuacao.html`

### Bloco 3 - integracao e legado

1. `apps/core/views.py`
2. `templates/core/portal.html`
3. `templates/core/sonhe_mais_alto_landing.html`
4. `apps/projeto21/views.py`
5. `apps/projeto21/urls.py`

---

## 11. Criterios de pronto por fase

Uma fase so pode ser considerada concluida quando:

- a logica central ficou mais clara do que antes;
- a duplicacao diminuiu;
- os templates ficaram subordinados ao dominio, nao o contrario;
- o runtime do aluno ficou mais verdadeiro;
- `core` continuou sendo a entrada oficial;
- nao foi criado atalho estrutural novo fora da arquitetura alvo.

---

## 12. Proximo passo imediato

Comecar pela Fase B.

Mais especificamente:

- ler e alinhar `apps/sonho_de_ser/models.py`;
- mapear quais campos sao realmente canonicos;
- corrigir `permissions.py`, `serializers.py` e `services.py` para esse modelo;
- so depois mexer nas telas do Browse.

Essa e a retomada mais segura, incremental e fiel ao produto.
