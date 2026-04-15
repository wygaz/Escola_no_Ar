# 01_objetivo_da_reforma

## Objetivo macro
Refatorar a plataforma para que o app `core` se torne o centro oficial:
- da navegação de produtos,
- da vitrine de produtos,
- do resolvedor de fluxo,
- e da governança administrativa.

## Objetivo específico
Permitir que:
- o aluno veja produtos de forma clara,
- cada produto tenha um ponto de entrada oficial,
- o sistema decida automaticamente o próximo passo,
- o superusuário não caia no fluxo comum do aluno,
- e a plataforma possa crescer sem remendos.

## O que preservar
- modelo de usuário atual em `apps/contas`
- permissões e entitlements já existentes
- fluxos internos válidos do Vocacional
- estrutura modular por app
- compatibilidade com histórico do projeto

## O que mudar
- centralizar decisão de fluxo no `core`
- separar vitrine comercial de página operacional
- eliminar links hardcoded espalhados
- criar uma camada de governança para admin
- criar uma base reutilizável para produtos futuros

## Restrições
- não duplicar lógica
- não duplicar CSS se puder ser compartilhado
- não criar nova base de usuários
- não recriar o projeto do zero
- não fazer refatoração opaca sem explicação
