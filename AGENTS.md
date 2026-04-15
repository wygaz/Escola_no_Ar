# AGENTS.md

## Projeto
Este repositório contém a plataforma Escola no Ar, com foco atual em:
- Vocacional
- Sonhe+Alto / Projeto21
- expansão futura para outros produtos

## Diretriz principal
Não trate este projeto como um conjunto de telas isoladas.
A prioridade é consolidar uma arquitetura em que o app `core` se torne o centro da navegação de produtos e do orquestrador de fluxo, enquanto os apps específicos mantêm seus fluxos internos.

## Objetivo atual
Executar uma reforma arquitetural progressiva, segura e explicável, sem recriar o projeto do zero.

## Regras duráveis
- Preserve `apps/contas` como base única de usuários.
- Não crie base paralela de autenticação.
- Não duplique lógica se houver ponto central reutilizável.
- Não duplique CSS quando puder centralizar.
- Não espalhe regras de fluxo em templates.
- Não use templates como controlador de negócio.
- Preserve compatibilidade com entitlements/permissões existentes.
- Respeite a estrutura modular por app.
- Prefira mudanças pequenas, coesas e verificáveis.
- Preserve o que já funciona no Vocacional, salvo quando houver conflito estrutural real.

## Arquitetura desejada
- `core` = catálogo de produtos + resolvedor de fluxo + governança
- `vocacional` = avaliação, resultado, desempate rápido, refinamentos
- `sonhe+alto/projeto21` = integrar depois no mesmo padrão

## Padrão de trabalho
1. Diagnosticar antes de refatorar.
2. Propor plano em fases antes de grandes mudanças.
3. Implementar primeiro a menor fatia útil.
4. Explicar por que cada arquivo foi alterado.
5. Informar riscos de compatibilidade.
6. Evitar reescrever tudo quando um refactor incremental resolver.

## Done means
Uma fase só está concluída quando:
- a navegação ficou mais clara do que antes,
- a lógica ficou mais centralizada,
- houve redução de duplicação,
- os fluxos atuais continuam íntegros,
- e os arquivos alterados fazem sentido na arquitetura alvo.

## Prioridade imediata
Fase 1:
- estruturar o `core` como centro da navegação de produtos,
- criar `produtos.html`,
- criar card reutilizável,
- criar CSS compartilhado,
- criar registry/status/resolver,
- preparar governança do superusuário.

## Proibição prática
Não criar atalhos hardcoded novos em templates para resolver fluxo de produto.
Toda navegação de produto deve apontar para o resolvedor central, salvo exceções justificadas.
