Quero que você faça uma revisão final do planejamento detalhado da Fase 1 antes de codar, aplicando estas correções de governança da própria fase.

## Corrija e congele estas decisões antes da implementação

### 1) Unificar a ordem dos patches
Hoje há uma inconsistência no documento:
- na seção “Ordem recomendada dos patches”, o Patch 4 é governança e o Patch 5 é estado por produto;
- na seção “Sequência mínima recomendada”, o estado por produto aparece antes da governança.

Quero que você:
- escolha uma única ordem final;
- explique em 3 a 6 linhas por que essa ordem é a melhor;
- ajuste o plano para ficar internamente consistente.

### 2) Fechar a definição do `portal`
Na Fase 1, o `portal` deve ser tratado apenas como:
- **compatibilidade transitória**

e não como:
- “vitrine provisória consolidada”

Quero que você normalize essa linguagem no planejamento para eliminar ambiguidade.

### 3) Travar a criação precoce de services
Quero que fique explícito que:
- **não deve nascer uma pasta `apps/core/services/` nesta fase por padrão**;
- helper privado em `views.py` ou extração mínima local é preferível;
- só pode nascer service novo se aparecer duplicação concreta em pelo menos dois pontos reais do código durante a implementação.

Transforme isso em regra escrita da Fase 1.

### 4) Reclassificar o Patch 7
O patch de “compatibilidade transitória e limpeza de entrada global” não deve ser presumido como obrigatório.
Quero que ele vire:
- **patch opcional de fechamento**, executado apenas se ainda restarem entradas globais relevantes hardcoded fora do `core`.

Atualize essa classificação no plano.

---

## Depois dessas correções
Quero que você me devolva o resultado em dois blocos:

# Bloco A — “Plano detalhado da Fase 1 revisado e congelado”
Versão limpa, já corrigida, pronta para execução.

# Bloco B — “Execução patch a patch”
Transforme a fase em uma fila operacional real.

Para cada patch, entregue:
- nome curto;
- objetivo;
- arquivos mais prováveis;
- o que não pode acontecer;
- critério de aceite;
- teste manual mínimo;
- condição para seguir ao próximo patch.

## Regras de execução
- nada de camada paralela;
- nada de abstração precoce;
- nada de service novo por conveniência;
- nada de mover lógica interna do Vocacional para o core;
- nada de criar nova vitrine concorrente;
- nada de criar nova governança concorrente.

## Muito importante
Quero que você trate esta saída como a base oficial da execução da Fase 1.
Não quero ainda código.
Quero um plano revisado, congelado e pronto para ser executado patch a patch.