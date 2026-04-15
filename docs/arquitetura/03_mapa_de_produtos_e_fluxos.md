# 03_mapa_de_produtos_e_fluxos

## Produtos iniciais da vitrine oficial
- Guia Vocacional
- Vocacional 75 Plus
- Vocacional Premium
- Sonhe+Alto (preparar desde já)

## Conceito
Cada produto terá:
- nome público
- slug público
- imagem/folheto
- descrição curta
- benefício principal
- status do usuário
- ação principal

## Exemplo de slugs públicos
- guia-vocacional
- vocacional-75-plus
- vocacional-premium
- sonhe-mais-alto

## Estados oficiais do produto
- sem_acesso
- disponivel
- em_andamento
- concluido
- recomendado

## Ações oficiais
- conhecer
- liberar
- iniciar
- continuar
- ver_progresso
- ver_resultado

## Fluxo oficial por produto

### Guia Vocacional
Entrada:
- catálogo de produtos
- detalhe do produto
- resolvedor central

Saídas possíveis:
- ver detalhes
- acessar conteúdo
- avaliar o guia
- destravar próximos passos

### Vocacional 75 Plus
Entrada:
- catálogo de produtos
- detalhe do produto
- resolvedor central

Saídas possíveis:
- iniciar avaliação
- continuar avaliação
- ver resultado
- fazer desempate rápido
- seguir para Premium

### Vocacional Premium
Entrada:
- catálogo de produtos
- detalhe do produto
- resolvedor central

Saídas possíveis:
- ver etapas
- continuar do ponto atual
- entrar em refinamento
- ver resultado refinado

### Sonhe+Alto
Preparar estrutura para:
- catálogo
- detalhe
- entrada via resolvedor
- continuidade futura do fluxo

## Regra operacional
Nenhum card de produto deve mandar direto para páginas internas dispersas sem passar pelo resolvedor, salvo exceção bem documentada.
