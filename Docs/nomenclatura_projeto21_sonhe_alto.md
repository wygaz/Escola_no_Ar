# docs/nomenclatura_projeto21_sonhe_alto.md

Nome técnico do app:
   projeto21
Nome público/marca: 
   Projeto Sonhe + Alto

Regra:
   - Em código, pastas, rotas, static, templates paths, JSON → usar projeto21.

   - Em textos para o usuário (interface, PDFs, landing, Hotmart) → usar “Sonhe + Alto”.

1. Onde continuar usando projeto21 (interno)

Nestes lugares, a regra é: NÃO mexer mais no nome:

Pasta do app:
apps/projeto21/

Static:
apps/projeto21/static/projeto21/...

Templates do app (caminho):
templates/projeto21/...

# urls.py -> path("...", views.x, name="...") e reverse("projeto21:...") 
Namespace de URLs:
    app_name = "projeto21"
    
Nomes de views, módulos, arquivos Python quando fizer sentido:
views_projeto21.py, forms_projeto21.py (se existirem).

JSON, arquivos auxiliares etc.:
projeto21/data/estrategias.json

Qualquer referência que já foi usada em:
    PDFs gerados,
    links antigos (URLs),
    scripts,
    deploy (collectstatic, etc.).
Ou seja: tudo o que é estrutura e código continua com projeto21.

2. Onde usar “Sonhe + Alto” (externo)
Aqui é “terra livre” pra marca nova — sem quebrar nada técnico:

Textos da landing (títulos, subtítulos, cards):
    “Projeto Sonhe + Alto”
    “Kit Projeto Sonhe + Alto Essencial”
    etc.

Textos internos para o aluno (labels, títulos, instruções):
    “Meu plano de estratégias – Projeto Sonhe + Alto”
    Capa de PDF, capa de guia, capas de kits, imagens, logos.
    Hotmart (nome do produto, descrição, argumentação de venda).
    Materiais de comunicação: redes sociais, apresentações, vídeos.
Se em algum lugar de texto aparecer “Projeto 21” pro aluno, aí sim vale ir trocando pra “Sonhe + Alto” aos poucos, porque isso não quebra sistema.

# Guia para o uso das imagens, com nomenclatura, localização e referências:

1) Lista de nomes de arquivos sugeridos (painel / dashboard do Projeto 21)

Diretório físico sugerido:

apps/projeto21/static/projeto21/dashboard/img/

a) Identidade Sonhe + Alto

Para usar no painel, PDFs, cabeçalhos, etc.:

Logo principal horizontal

Arquivo: sonhe-alto-logo-horizontal.png

Uso: hero da página, cabeçalho interno, PDFs.

Tamanho sugerido: algo como 900×300 ou 1200×400 (fundo transparente).

Ícone quadrado / redondo (para favicon, selo, avatar)

Arquivo: sonhe-alto-logo-icone.png

Uso: ícone pequeno, favicon, avatar no card, etc.

Tamanho sugerido: 512×512.

Ilustração do aquário (versão “herói”)

Arquivo: sonhe-alto-aquario-main.png

Uso: bloco de destaque na página, alguma seção explicando o conceito (peixinho que decide mudar de aquário).

Tamanho sugerido: ~1200×800 (horizontal).

Ícone do aquário (para usar miudinho, se quiser)

Arquivo: sonhe-alto-aquario-icone.png

Uso: junto do título “Projeto Sonhe + Alto” em alguma seção, como um selinho.

Tamanho sugerido: 256×256 ou 320×320.

b) Ícones da Janela de Johari (para os 4 cards)

Quadrante 1 – Área aberta

Arquivo: johari-1-area-aberta.png

Quadrante 2 – Ponto cego

Arquivo: johari-2-ponto-cego.png

Quadrante 3 – Área secreta

Arquivo: johari-3-area-secreta.png

Quadrante 4 – Área desconhecida

Arquivo: johari-4-area-desconhecida.png

Uso: dentro dos cards .hero-johari-card, acima do título de cada quadrante.
Tamanho sugerido: ~512×512 (origem).
No CSS a gente já está limitando para ~72px de largura/altura, então eles serão exibidos pequenininhos, como ícones.

c) (Opcional) Thumbs para os Kits

Se no futuro quiser trocar os emojis por imagens:

kit-essencial-thumb.png

kit-completo-thumb.png

kit-grupos-thumb.png

Uso: lado do título dos cards de cada kit.

2) Mini guia de referência {% static '...' %} para esse painel

Assumindo a estrutura:

apps/projeto21/static/projeto21/dashboard/img/...

a) Logo e aquário Sonhe + Alto

Logo horizontal (por exemplo, num cabeçalho interno do painel):

<img src="{% static 'projeto21/dashboard/img/sonhe-alto-logo-horizontal.png' %}"
     alt="Projeto Sonhe + Alto">


Ícone do logo (ex.: avatar ou selo):

<img src="{% static 'projeto21/dashboard/img/sonhe-alto-logo-icone.png' %}"
     alt="Ícone do Projeto Sonhe + Alto">


Ilustração principal do aquário:

<img src="{% static 'projeto21/dashboard/img/sonhe-alto-aquario-main.png' %}"
     alt="Ilustração do peixinho mudando para um aquário maior">


Ícone pequeno do aquário (se usar em algum botão/seção):

<img src="{% static 'projeto21/dashboard/img/sonhe-alto-aquario-icone.png' %}"
     alt="Ícone do aquário Sonhe + Alto">

b) Ícones da Janela de Johari nos 4 quadrantes

Naquele bloco que eu te passei, é só ativar os <figure> assim:

<article class="hero-johari-card">
  <figure class="hero-johari-icon">
    <img src="{% static 'projeto21/dashboard/img/johari-1-area-aberta.png' %}"
         alt="Área aberta">
  </figure>
  <h3>Área aberta</h3>
  <p>O que eu sei sobre mim e os outros também veem.</p>
</article>

<article class="hero-johari-card">
  <figure class="hero-johari-icon">
    <img src="{% static 'projeto21/dashboard/img/johari-2-ponto-cego.png' %}"
         alt="Ponto cego">
  </figure>
  <h3>Ponto cego</h3>
  <p>O que os outros percebem em mim, mas eu ainda não enxergo.</p>
</article>

<article class="hero-johari-card">
  <figure class="hero-johari-icon">
    <img src="{% static 'projeto21/dashboard/img/johari-3-area-secreta.png' %}"
         alt="Área secreta">
  </figure>
  <h3>Área secreta</h3>
  <p>O que eu sei, mas quase ninguém sabe.</p>
</article>

<article class="hero-johari-card">
  <figure class="hero-johari-icon">
    <img src="{% static 'projeto21/dashboard/img/johari-4-area-desconhecida.png' %}"
         alt="Área desconhecida">
  </figure>
  <h3>Área desconhecida</h3>
  <p>Potenciais que nem eu nem os outros conhecemos ainda.</p>
</article>

c) (Opcional) Thumbs dos kits

Se um dia quiser colocar uma mini imagem em cima do título de cada kit:

<article class="kit-card kit-card-main">
  <figure class="hero-johari-icon">
    <img src="{% static 'projeto21/dashboard/img/kit-essencial-thumb.png' %}"
         alt="Kit Essencial Sonhe + Alto">
  </figure>
  <div class="kit-title"><strong>Kit Projeto Sonhe + Alto Essencial</strong></div>
  ...
</article>
