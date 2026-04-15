# 04_governanca_dashboard

## Papel da governança
A governança não será apenas uma tela de escolha de persona.
Ela deve funcionar como painel de comando da plataforma.

## Objetivos
- dar ao superusuário/staff uma visão clara do estado do site
- permitir testes controlados
- permitir liberação emergencial de acesso
- concentrar operações rápidas
- evitar dependência do fluxo comum do aluno

## Entrada do superusuário
Por padrão, o superusuário deve cair na governança, não no funil do aluno.

## Módulos do dashboard

### visão executiva
- total de usuários
- usuários por produto
- onboarding pendente
- fluxos em andamento
- resultados concluídos
- distribuição por entitlement/produto

### visão do Vocacional
- quantos iniciaram
- quantos concluíram
- quantos estão em andamento
- quantos chegaram ao desempate rápido
- quantos estão em etapas/passes/refinamentos

### visão do Sonhe+Alto
- deixar estrutura preparada para métricas equivalentes

### teste por persona
- visitante sem acesso
- usuário com Guia
- usuário com 75 Plus
- usuário com Premium
- usuário com tudo liberado
- usuário com onboarding pendente
- usuário com fluxo em andamento

### liberação emergencial
- conceder acesso manual por produto
- remover acesso manual por produto
- liberar acesso temporário para suporte/teste
- destravar etapa quando apropriado
- nunca criar base paralela de usuários

### suporte operacional
- busca rápida de usuário
- estado resumido do usuário
- produtos liberados
- pendências
- etapa atual
- ações rápidas seguras

## MVP recomendado
Começar com:
- 3 a 6 cards principais
- busca de usuário
- inspeção rápida do estado do usuário
- concessão manual de acesso
- seleção de persona de teste

## Crescimento futuro
Depois ampliar com:
- auditoria
- histórico de ações críticas
- métricas mais profundas
- ferramentas de suporte mais ricas
