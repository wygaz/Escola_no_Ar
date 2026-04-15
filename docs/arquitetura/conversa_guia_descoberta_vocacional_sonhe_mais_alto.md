# Conversa de trabalho — Guia de Descoberta / Vocacional / Sonhe+Alto

> Registro organizado da conversa, incluindo também comandos, nomes de arquivos e referências de código mencionados ao longo do diálogo.

---

## 1. Retomada do projeto

**Usuário:**  
Depois de um longo período, voltamos para prosseguir com o Projeto. Em que ponto paramos?

**Assistente:**  
Foi retomado o panorama geral do projeto, com foco principal em **Vocacional** e **Sonhe+Alto**, a partir do estado mais recente disponível e dos materiais enviados.

---

## 2. Reencontro do material e diagnóstico inicial

**Usuário:**  
Você mencionou que eu havia encontrado um arquivo e pediu para avaliar quanto daquilo já estava resolvido.

**Assistente:**  
Foi feita uma leitura diagnóstica do material disponível e concluído que o melhor caminho seria separar o trabalho em dois eixos:

1. um projeto para fechar o **Vocacional** em nível de codificação e funcionamento refinado;  
2. outro projeto para estruturar o ambiente do **Sonhe+Alto**.

Também foi observado que ambos poderiam convergir para:
- um **centro autenticador comum**;
- dois ambientes de produto;
- um integrador central;
- e, depois, uma frente específica de design e identidade visual.

---

## 3. Direção arquitetural geral

**Usuário:**  
Concordei com a ideia de não reinventar nada. A proposta seria consolidar os dois projetos em um centro autenticador e dois ambientes com um integrador.

**Assistente:**  
Foi reforçado que essa era a melhor linha:
- manter o `core` como centro autenticador e de integração;
- manter a estrutura existente;
- evitar recomeço;
- usar o que já foi desenvolvido como base real.

---

## 4. Natureza do Sonhe+Alto

**Usuário:**  
Expliquei que o Sonhe+Alto tem uma natureza mais dinâmica e que ainda não teve a estrutura de administração e acompanhamento do lado do aluno implementada: plano de atividades, progresso, pontuações, conquistas etc. Disse que isso combinaria com a abordagem de browse e dashboard.

**Assistente:**  
Foi validada essa visão. O Sonhe+Alto foi entendido como um produto que deve funcionar como:
- **browse/workspace** para ação;
- **dashboard** para leitura, acompanhamento e incentivo.

---

## 5. Natureza do Vocacional

**Usuário:**  
Descrevi a estrutura de perguntas do Vocacional, com um banco de 1080 questões e três planos:

1. **Básico** — 75 perguntas  
2. **Avançado** — começa com 150 perguntas e pode aumentar  
3. **Premium** — começa após o anterior, incluindo tecnologia para apuração mais precisa

Perguntei o que mais poderia ser feito com esse banco, especialmente com a parte ligada à prática profissional.

**Assistente:**  
Foi entendido que o Vocacional já está muito avançado em lógica e produto, mas ainda precisa:
- formalizar os planos como regra oficial do sistema;
- preparar o banco de questões em camadas;
- separar melhor descoberta vocacional, refinamento e camada profissional;
- fechar o produto de forma escalável.

---

## 6. Solicitação de visão do estado atual do código

**Usuário:**  
Informei que passaria o estado atual do que temos desenvolvido, a partir do GitHub e da árvore de diretórios.

**Assistente:**  
Foi solicitada a base para inspeção, e depois disso foi preparado um caminho para gerar um snapshot limpo do projeto, a fim de permitir uma leitura mais confiável da estrutura real.

---

## 7. Geração do snapshot

**Usuário:**  
Expliquei que o `settings.py` usa `getenv`, que o nome real do app poderia ainda ser outro e informei erros em tentativas de rodar o script de empacotamento.

Foram citados erros ao rodar algo como:

```powershell
powershell -ExecutionPolicy Bypass -File .\empacotar_snapshot_guia_descoberta.ps1
```

Também foram mencionadas mensagens envolvendo:
- `getenv`
- `environ.get`
- cadeias de caracteres sem terminador
- tokens inesperados em expressões do PowerShell

**Assistente:**  
Foram ajustadas as orientações para geração de um zip limpo do projeto, até que o snapshot fosse obtido de forma utilizável.

---

## 8. Snapshot limpo do projeto

**Usuário:**  
Perguntei se seria útil gerar um novo zip sem os zips internos.

**Assistente:**  
Foi confirmado que sim, e que isso ajudaria bastante na leitura do projeto.

Depois disso, foi gerado e enviado um snapshot limpo.

Arquivos mencionados:
- `snapshot_guia_descoberta_2026-03-31_1252.zip`
- `snapshot_guia_descoberta_sem_zips_2026-03-31_1305.zip`

---

## 9. Diagnóstico do snapshot limpo

### 9.1 Core

**Assistente:**  
Com base no snapshot limpo, o `core` foi considerado **bem mais maduro do que parecia**. Já havia:
- portal central pós-login;
- resolvedor de produtos;
- gating por login, LGPD, guia válido, avaliação do guia e produto;
- equivalências de slugs;
- dashboard de governança;
- impersonação/teste;
- proteção de redirect no login.

Arquivos e áreas mencionados:
- `apps/core/views.py`
- `apps/core/permissions.py`
- `apps/core/urls.py`
- `templates/core/portal.html`
- `templates/core/sonhe_mais_alto_landing.html`

Conclusão:
- o `core` já funciona como centro autenticador, integrador e ponto de entrada para os produtos.

### 9.2 Vocacional

**Assistente:**  
O Vocacional foi apontado como o módulo **mais avançado e mais perto de fechamento**.

Já havia:
- modelos para dimensões, perguntas, opções, avaliações, respostas e resultados;
- fluxo de entrada, etapas, formulário e resultado;
- refinamentos e comparações;
- templates ricos;
- lógica forte para o bônus 75 e refinamentos.

Arquivos e elementos mencionados:
- `apps/vocacional/models.py`
- `apps/vocacional/views.py`
- `apps/vocacional/urls.py`
- `apps/vocacional/refinamento.py`
- `apps/vocacional/forced_choice.py`
- `apps/vocacional/data/vocacional/vocacional_75.json`
- `templates/vocacional/avaliacao_form.html`
- `templates/vocacional/resultado.html`
- `templates/vocacional/comparacoes_top3.html`
- `templates/vocacional/ofertas_refinamento.html`

Mas ainda faltava:
- formalização explícita dos três planos;
- preparação real para o banco de 1080 questões;
- separação mais clara entre níveis e camadas do produto.

### 9.3 Projeto21 / Sonhe+Alto

**Assistente:**  
No primeiro diagnóstico, o app `projeto21` parecia conter apenas:
- `Area`
- `Estrategia`
- importador
- view simples
- rota simples
- landing protegida por gating

Arquivos mencionados:
- `apps/projeto21/models.py`
- `apps/projeto21/views.py`
- `apps/projeto21/urls.py`
- `templates/projeto21/landing.html`

Isso levou a uma leitura inicial de que o Sonhe+Alto ainda estava fraco no backend, com pouca estrutura operacional.

---

## 10. Envio do app `sonho_de_ser`

**Usuário:**  
Enviei `sonho_de_ser.zip`.

**Assistente:**  
Após abrir esse app, o diagnóstico mudou bastante.

Foi identificado que o `sonho_de_ser` não era apenas material legado, mas sim um app funcional em construção, contendo:
- `Area`
- `Estrategia`
- `Plano`
- `PlanoItem`
- `RegistroDiario`
- mentoria
- formulários
- views de dashboard, plano, registro, histórico e pontuação
- APIs/viewsets

Arquivos mencionados:
- `sonho_de_ser/models.py`
- `sonho_de_ser/views.py`
- `sonho_de_ser/urls.py`
- `sonho_de_ser/services.py`
- `sonho_de_ser/permissions.py`
- `sonho_de_ser/forms.py`
- `sonho_de_ser/admin.py`

Conclusão:
- o Sonhe+Alto não estava vazio;
- havia um backend real em construção;
- o trabalho deveria ser de **resgate, alinhamento e conclusão**, não de reconstrução do zero.

Problemas citados:
- referência a `PlanoEstrategia` versus `PlanoItem`;
- referências antigas de mentoria;
- divergências entre `services.py`, `permissions.py` e o modelo atual.

---

## 11. Explicação sobre o nome Sonhe+Alto e o antigo Projeto21

**Usuário:**  
Expliquei que o Sonhe+Alto é o antigo Projeto21. Disse que foi feita a mudança de nome, mas que, para evitar um ajuste global, optou-se por manter a mesma estrutura e usar apenas o nome de fachada Sonhe+Alto. Também enviei `projeto21.zip`.

**Assistente:**  
Ao comparar os dois apps, foi concluído que:
- `projeto21` é a base mais antiga e mais leve;
- `sonho_de_ser` é a base mais evoluída e funcional;
- “Sonhe+Alto” é o nome comercial/fachada.

Leitura consolidada:
- **`projeto21`** = legado estrutural, conteúdo e compatibilidade  
- **`sonho_de_ser`** = app canônico de runtime  
- **Sonhe+Alto** = nome público do produto

Recomendação:
- não renomear tudo agora;
- adotar `sonho_de_ser` como base funcional oficial;
- manter `projeto21` como legado/importação;
- preservar “Sonhe+Alto” como fachada.

---

## 12. Definição do papel do Sonhe+Alto como produto

**Usuário:**  
Pedi que fosse considerado o plano de abrir a funcionalidade do Sonhe+Alto para uso do usuário como ferramenta para criar, executar e acompanhar o seu desempenho via browse/dashboard.

**Assistente:**  
Foi então desenhado o conceito central do produto:

O Sonhe+Alto deve funcionar como um ambiente em que o aluno possa:
- montar um plano;
- executar suas estratégias;
- registrar o dia;
- acompanhar progresso;
- receber incentivo e orientação.

Foram definidas duas camadas principais:

### Browse / Workspace
Ambiente operacional do aluno, com páginas como:
- Meu Plano
- Hoje
- Histórico
- Pontuação e Conquistas
- Mentoria

### Dashboard
Ambiente de leitura e acompanhamento, com:
- progresso geral;
- progresso por área;
- adesão semanal;
- streak;
- pontuação;
- próximos passos;
- visão motivacional.

Também foi reforçado que:
- o `core` permanece como porta de entrada;
- o `sonho_de_ser` concentra a operação do produto;
- o `projeto21` permanece como legado.

---

## 13. Plano por arquivos

**Usuário:**  
Aceitei a ideia e pedi um plano por arquivos.

**Assistente:**  
Foi então apresentado um plano técnico de implementação, começando por saneamento estrutural e seguindo até o browse e o dashboard.

### Etapa 1 — congelar a base canônica
Arquivos centrais:
- `apps/sonho_de_ser/models.py`
- `apps/sonho_de_ser/services.py`
- `apps/sonho_de_ser/permissions.py`
- `apps/sonho_de_ser/views.py`
- `apps/sonho_de_ser/forms.py`
- `apps/sonho_de_ser/urls.py`

Objetivo:
- parar a deriva entre versões;
- definir o domínio oficial;
- alinhar nomes e estruturas.

### Etapa 2 — consolidar o domínio
Foco em:
- `Area`
- `Estrategia`
- `Plano`
- `PlanoItem`
- `RegistroDiario`
- mentoria

Objetivo:
- garantir que o banco represente corretamente o produto.

### Etapa 3 — separar a lógica em serviços
Objetivo:
- tirar regra de negócio de views e templates;
- centralizar plano, registro, pontuação, dashboard e mentoria.

Sugestão estrutural:
```text
apps/sonho_de_ser/services/plano.py
apps/sonho_de_ser/services/registro.py
apps/sonho_de_ser/services/pontuacao.py
apps/sonho_de_ser/services/dashboard.py
apps/sonho_de_ser/services/mentoria.py
```

### Etapa 4 — fechar os formulários
Objetivo:
- validar a entrada de dados do aluno;
- dar consistência ao browse.

Arquivo citado:
- `apps/sonho_de_ser/forms.py`

### Etapa 5 — construir o Browse
Objetivo:
- entregar ao aluno um ambiente real de uso.

Templates previstos:
- `templates/sonho_de_ser/plano.html`
- `templates/sonho_de_ser/hoje.html`
- `templates/sonho_de_ser/historico.html`
- `templates/sonho_de_ser/pontuacao.html`

### Etapa 6 — fechar o Dashboard
Objetivo:
- transformar os dados em leitura clara e motivadora.

Template citado:
- `templates/sonho_de_ser/dashboard.html`

### Etapa 7 — consolidar mentoria
Objetivo:
- incorporar acompanhamento de mentor ao ecossistema.

### Etapa 8 — integração com o Core
Objetivo:
- manter entrada única, fachada Sonhe+Alto e coerência com o portal.

Arquivos citados:
- `apps/core/views.py`
- `apps/core/permissions.py`
- `templates/core/portal.html`
- `templates/core/sonhe_mais_alto_landing.html`

---

## 14. Ordem prática proposta para mexer nos arquivos

Foi sugerida esta sequência:

1. `apps/sonho_de_ser/models.py`
2. `apps/sonho_de_ser/services.py`
3. `apps/sonho_de_ser/permissions.py`
4. `apps/sonho_de_ser/forms.py`
5. `apps/sonho_de_ser/views.py`
6. `apps/sonho_de_ser/urls.py`
7. `templates/sonho_de_ser/plano.html`
8. `templates/sonho_de_ser/hoje.html`
9. `templates/sonho_de_ser/historico.html`
10. `templates/sonho_de_ser/pontuacao.html`
11. `templates/sonho_de_ser/dashboard.html`
12. `templates/sonho_de_ser/mentoria*.html`
13. `apps/core/views.py`
14. `apps/core/permissions.py`
15. `templates/core/portal.html`
16. `templates/core/sonhe_mais_alto_landing.html`

Também foi sugerida uma divisão por blocos:

### Bloco A — saneamento estrutural
- `models.py`
- `services.py`
- `permissions.py`
- `forms.py`

### Bloco B — Browse operacional
- `views.py`
- `urls.py`
- templates de plano/hoje/histórico/pontuação

### Bloco C — Dashboard e integração
- dashboard
- mentoria
- integração com `core`

---

## 15. Decisão de pausar a execução pesada

**Usuário:**  
Respondi “OK”.

**Assistente:**  
Foi reforçado que o próximo passo, em termos técnicos, seria começar pelo **Bloco A**, iniciando em `apps/sonho_de_ser/models.py`.

---

## 16. Pausa estratégica

**Usuário:**  
Disse que esperaria um pouco, porque primeiro terminaria o Projeto do Pr. Albino com o Codex antes de começar a mexer nisso. Ressaltei que esse estudo foi preciosíssimo para dar uma visão mais ampla e que, logo que terminasse o outro projeto, pegaríamos firme nesse.

**Assistente:**  
Foi reconhecido que a pausa era prudente e estratégica.

Também foi consolidado que o estudo deixou claro:
- o `core` já serve como centro autenticador/integrador;
- o **Vocacional** está perto do fechamento, mas precisa formalizar melhor os planos e o banco grande;
- o **Sonhe+Alto** não está vazio — ele já tem base real em `sonho_de_ser`;
- o caminho certo para o Sonhe+Alto é **sanear e concluir**, não reconstruir;
- quando chegar a hora, a retomada pode começar por:
  1. eleger `sonho_de_ser` como canônico
  2. saneamento estrutural
  3. browse operacional
  4. dashboard
  5. integração final com o core

---

## 17. Solicitação de registro em Markdown

**Usuário:**  
Pedi que essa conversa inteira fosse colocada em um arquivo `.md`.

**Assistente:**  
Foi iniciado o preparo de um arquivo markdown contendo o registro organizado da conversa.

Depois, o pedido foi ampliado:

**Usuário:**  
Disse que também poderia incluir os códigos.

**Assistente:**  
Foi então decidido gerar esta versão mais completa, incluindo:
- conteúdo da conversa;
- comandos citados;
- nomes de arquivos;
- referências de código;
- caminhos de implementação.

---

## 18. Resumo executivo final

### Estado consolidado ao final da conversa

#### Core
- maduro e aproveitável;
- centro autenticador e integrador.

#### Vocacional
- produto mais perto do fechamento;
- precisa formalizar planos e escalar o banco de questões.

#### Sonhe+Alto
- nome de fachada do antigo Projeto21;
- app canônico de runtime: `sonho_de_ser`;
- `projeto21` fica como legado/compatibilidade;
- caminho certo: saneamento estrutural + browse + dashboard + integração com core.

### Próxima retomada sugerida
Quando o projeto do Pr. Albino terminar, a retomada deve começar por:

```text
1. apps/sonho_de_ser/models.py
2. apps/sonho_de_ser/services.py
3. apps/sonho_de_ser/permissions.py
4. apps/sonho_de_ser/forms.py
5. apps/sonho_de_ser/views.py
6. apps/sonho_de_ser/urls.py
7. templates/sonho_de_ser/*
8. apps/core/views.py
9. apps/core/permissions.py
10. templates/core/*
```

---

## 19. Arquivos e pacotes citados ao longo da conversa

### Snapshots e zips
- `snapshot_guia_descoberta_2026-03-31_1252.zip`
- `snapshot_guia_descoberta_sem_zips_2026-03-31_1305.zip`
- `sonho_de_ser.zip`
- `projeto21.zip`

### Apps e áreas principais
- `apps/core/`
- `apps/vocacional/`
- `apps/projeto21/`
- `apps/sonho_de_ser/`
- `templates/core/`
- `templates/vocacional/`
- `templates/projeto21/`
- `templates/sonho_de_ser/`

### Arquivos mais citados
- `settings.py`
- `urls.py`
- `models.py`
- `views.py`
- `services.py`
- `permissions.py`
- `forms.py`
- `admin.py`

---

## 20. Fechamento

Este markdown foi montado como um registro fiel e organizado da conversa, com foco em:
- preservar o encadeamento das decisões;
- manter o panorama técnico;
- registrar a arquitetura escolhida;
- deixar pronto o ponto de retomada futura.
