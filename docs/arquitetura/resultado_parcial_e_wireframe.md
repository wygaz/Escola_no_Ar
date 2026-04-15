Checklist 1 consolidado desde o início

1. [ ✔ ] python manage.py check passou
2. [ ✔ ] / abre sem erro para anônimo
3. [ X ] /portal/ abre sem erro para anônimo -> Eu acho que a entrada do usuário poderia ser a tela de login, com a o portal de acesso poderia abrir apenas ambos poderiam ter 
4. [ X ] portal mantém CTAs, alerts, chips e blocos esperados -> Botão saiba mais para descrição do site com seus objetivos, fluxo de navegação e próximo passo.
5. [ X ] Vocacional para anônimo segue fluxo correto -> Sim, exceto que ele não tenha comprado o Guia e tenha os bônus liberados pelo administrador. Nesse último caso, não faz sentido a Avaliação do Guia. 
6. [ X ] Sonhe + Alto para anônimo segue fluxo correto -> Sim, exceto que ele não tenha comprado o Guia e tenha os bônus liberados pelo administrador. Nesse último caso, não faz sentido a Avaliação do Guia.
7. [✔ ] usuário sem acesso vê estado correto no portal
8. [✔ ] usuário onboarding pendente vê estado correto no portal
9. [✔ ] usuário com acesso completo vê estado correto no portal
10. [ ✔ ] CTA do Vocacional passa pelo resolvedor e respeita o fluxo interno - Não há necessidade de ter uma página exclusiva (http://127.0.0.1:8000/legal/aceite/?next=/portal/) para aceite de termos. Isso pode ser resolvido na mesma página,. Na própria página do Portal já existem as caixinhas de aceite. Existe uma duplicação abaixo da lista dos itens na vertical, em uma linha que repetem. As caixinhas podem ir numa coluna ao lado da lista vertical, compondo uma tabela de duas colunas: uma = item da pendência, e na outra coluna a caixinha de aceitação. Uma vez feita a aceitação, esses itens numca mais deverão aparecer quando esse usuário acessar o site. Deve aparecer apenas o item/ns pendentes.
11. [ ✔ ] CTA do Sonhe + Alto passa pelo resolvedor correto -> Idem ao alnterior
12. [ ✔ ] / e /portal/ não se contradizem quando autenticado
13. [ ✔ ] staff vai para governança por padrão
14. [ ✔ ] staff com ?portal_mode=user entra na experiência de usuário
15. [ ✔ ] superuser vai para governança por padrão
16. [ ✔ ] superuser com ?portal_mode=user entra na experiência de usuário
17. [ ✔ ] product_states não quebrou o template atual
18. [ ✔ ] chaves antigas continuam coerentes
19. [✔  ] has_prod_guia_like existe e não quebrou a caixa de atenção
20. [ ✔ ] _legacy_* não estão sendo usados por rota ativa


Wireframe textual — tela de entrada acolhedora
Nome sugerido da página

Sua jornada começa aqui

1. Hero principal

Imagem:
Uma cena alegre e inspiradora, com sensação de caminho, descoberta, crescimento e esperança. Pode ser:
jovem caminhando em direção à luz;
trilha com horizonte;
ilustração leve com elementos de estudo, propósito e direção.

Título principal:
Sua jornada começa aqui

Subtítulo:
Conheça os caminhos disponíveis na plataforma e descubra o próximo passo mais adequado para você.

Texto curto:
Aqui você encontrará recursos pensados para apoiar seu crescimento, ampliar sua compreensão sobre si mesmo e ajudar na construção do seu propósito.

Botão principal:
Começar agora

Botão secundário:
Como funciona

2. Bloco de acolhimento

Título:
Bem-vindo ao Guia de Descoberta

Texto:
Cada pessoa chega aqui de um jeito diferente. Algumas vêm por meio do Guia, outras recebem acesso especial a conteúdos e bônus. Por isso, sua navegação pode variar conforme seu momento e seu tipo de acesso.

Texto de apoio:
Antes de seguir, conheça rapidamente o que você encontrará aqui.

3. Bloco “O que você vai encontrar aqui?”
Card 1 — Teste Vocacional

Título:
Teste Vocacional

Descrição:
Um espaço para ajudar você a refletir sobre talentos, interesses, habilidades e possibilidades de futuro.

Botões:
Saiba mais
Acessar

Card 2 — Sonhe + Alto

Título:
Sonhe + Alto

Descrição:
Uma jornada de crescimento pessoal, visão de futuro e fortalecimento de propósito.

Botões:
Saiba mais
Conhecer

Card 3 — Sua Jornada

Título:
Seu próximo passo

Descrição:
A plataforma pode indicar diferentes caminhos conforme sua etapa atual, seu acesso e o que já foi concluído.

Botões:
Saiba mais
Ver meu próximo passo

4. Bloco “Como funciona?”

Título:
Como será sua navegação

Texto principal:
Você não precisa entender tudo agora. A plataforma foi organizada para mostrar o que faz sentido para o seu momento.

Passos curtos:

1. Conheça os recursos disponíveis
Veja o que existe na plataforma e entenda para que serve cada área.

2. Identifique sua etapa atual
Dependendo do seu acesso, alguns caminhos podem aparecer primeiro para você.

3. Siga o próximo passo indicado
Você será direcionado para a experiência mais adequada dentro da sua jornada.

Botão:
Entendi

5. Bloco de orientação leve

Título:
Cada pessoa pode ter um caminho diferente — e tudo bem

Texto:
Alguns usuários iniciam pela apresentação da plataforma. Outros seguem diretamente para uma etapa específica. Em certos casos, pode haver acessos liberados diretamente pela administração, sem necessidade de passar por todas as etapas anteriores.

Texto complementar:
Nosso objetivo é tornar essa navegação clara, leve e intuitiva para você.

6. Área de ação final

Título:
Pronto para seguir?

Texto:
Você pode explorar os recursos disponíveis ou ir diretamente para o próximo passo sugerido para o seu perfil.

Botão principal:
Ir para meu próximo passo

Botão secundário:
Explorar a plataforma

Conteúdo dos modais ou telas “Saiba mais”
Saiba mais — Teste Vocacional

Título:
O que é o Teste Vocacional?

Texto:
O Teste Vocacional é um espaço de reflexão e descoberta. Ele ajuda você a perceber melhor suas inclinações, talentos, interesses e possibilidades de futuro, oferecendo uma visão mais clara sobre caminhos que combinam com o seu perfil.

Botão:
Ir para o Teste Vocacional

Saiba mais — Sonhe + Alto

Título:
O que é o Sonhe + Alto?

Texto:
O Sonhe + Alto foi pensado para apoiar sua construção de propósito, visão de vida e crescimento pessoal. É um ambiente de desenvolvimento que ajuda você a pensar mais alto, com clareza e direção.

Botão:
Conhecer Sonhe + Alto

Saiba mais — Seu próximo passo

Título:
Como descubro meu próximo passo?

Texto:
Seu próximo passo depende do seu acesso atual, do que já foi concluído e do caminho que foi liberado para você. A plataforma organiza isso para que você siga sem confusão.

Botão:
Ver meu próximo passo

Sugestão visual
Estrutura

Hero em duas colunas

Texto à esquerda

Imagem à direita

Abaixo, três cards

Depois, um bloco explicativo horizontal

Final com CTA forte

Sensação visual

limpa

acolhedora

moderna

leve

motivadora

Paleta sugerida

azul suave

verde claro

dourado quente

branco predominante

detalhes em laranja suave ou amarelo

Estilo dos botões

arredondados

cor principal sólida

botão secundário com borda leve

hover suave

Sugestão de lógica da página

Visualmente a página é a mesma para todos, mas o botão principal pode mudar conforme o caso.

Exemplo:

usuário anônimo: Começar agora

usuário com acesso liberado: Ir para meu próximo passo

usuário com pendência: Continuar

usuário staff com portal_mode=user: mesma experiência do usuário

staff/superuser normal: vai para governança

Texto pronto final da página
Hero

Sua jornada começa aqui
Conheça os caminhos disponíveis na plataforma e descubra o próximo passo mais adequado para você.

Aqui você encontrará recursos pensados para apoiar seu crescimento, ampliar sua compreensão sobre si mesmo e ajudar na construção do seu propósito.

Botões:
Começar agora
Como funciona

Acolhimento

Bem-vindo ao Guia de Descoberta
Cada pessoa chega aqui de um jeito diferente. Algumas vêm por meio do Guia, outras recebem acesso especial a conteúdos e bônus. Por isso, sua navegação pode variar conforme seu momento e seu tipo de acesso.

Antes de seguir, conheça rapidamente o que você encontrará aqui.

Cards

Teste Vocacional
Um espaço para ajudar você a refletir sobre talentos, interesses, habilidades e possibilidades de futuro.
Saiba mais | Acessar

Sonhe + Alto
Uma jornada de crescimento pessoal, visão de futuro e fortalecimento de propósito.
Saiba mais | Conhecer

Seu próximo passo
A plataforma pode indicar diferentes caminhos conforme sua etapa atual, seu acesso e o que já foi concluído.
Saiba mais | Ver meu próximo passo

Como funciona

Como será sua navegação
Você não precisa entender tudo agora. A plataforma foi organizada para mostrar o que faz sentido para o seu momento.

1. Conheça os recursos disponíveis
2. Identifique sua etapa atual
3. Siga o próximo passo indicado

Fechamento

Pronto para seguir?
Você pode explorar os recursos disponíveis ou ir diretamente para o próximo passo sugerido para o seu perfil.

Botões:
Ir para meu próximo passo
Explorar a plataforma