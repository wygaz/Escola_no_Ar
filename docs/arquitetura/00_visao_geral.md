# 00_visao_geral

## O que este projeto está se tornando
O Guia de Descoberta deixou de ser apenas um fluxo isolado de páginas.
Ele amadureceu para o nível de uma plataforma de produtos educacionais e de descoberta vocacional, com múltiplos produtos, permissões, continuidade de jornada, ofertas complementares e governança administrativa.

## Onde estamos
Hoje o projeto já contém:
- Vocacional em funcionamento parcial/avançado
- ofertas e refinamentos
- necessidade de governança
- necessidade de teste por persona/plano
- necessidade de integração futura com Sonhe+Alto

## O problema central
A navegação e a decisão de fluxo ainda estão muito espalhadas entre templates, views específicas e estados herdados do usuário.
Isso causa:
- ambiguidade de entrada
- dificuldade para testar
- risco de duplicação
- risco de direcionamento incorreto
- dificuldade de expansão

## A virada estrutural
A plataforma precisa migrar de:
“cada tela resolve seu próprio fluxo”

para:
“o core resolve o fluxo e os apps executam o conteúdo específico”

## Resultado esperado
Ao final da reforma:
- haverá uma vitrine oficial de produtos,
- um orquestrador central de fluxo,
- governança própria para admin,
- e um trilho comum para produtos atuais e futuros.
