# Decisão de Nomenclatura - Sonhe + Alto

## Decisão

Para o público, o produto passa a se chamar apenas **Sonhe + Alto**.

Os nomes anteriores **Sonho de Ser**, **Projeto 21** e variações semelhantes ficam abandonados como nomes públicos. Eles podem permanecer temporariamente no código apenas como legado técnico, enquanto a refatoração segura não for concluída.

## Regra prática

- Interfaces públicas devem usar **Sonhe + Alto**.
- Textos de portal, landing, dashboard, plano, check-in, histórico, pontuação, mentoria, contato, termos e materiais visíveis ao aluno devem usar **Sonhe + Alto**.
- `Projeto 21` não deve aparecer como marca pública nova.
- `Sonho de Ser` não deve aparecer como marca pública nova.
- `projeto21` e `sonho_de_ser` podem continuar como nomes técnicos internos até segunda ordem.
- URLs como `/projeto21/` podem continuar por compatibilidade, mas a tela exibida deve falar **Sonhe + Alto**.

## Motivo

A mudança global imediata de nomes técnicos pode gerar risco alto:

- migrations e tabelas podem depender de app labels existentes;
- URLs antigas podem estar em uso;
- permissões e slugs de produto podem depender de equivalências legadas;
- templates e código ainda reaproveitam estruturas antigas;
- renomear apps Django exige sequência controlada de migração.

Portanto, a decisão segura é separar duas camadas:

1. **Nome público:** Sonhe + Alto.
2. **Nome técnico legado:** preservado provisoriamente para compatibilidade.

## Política de saneamento

A limpeza deve ocorrer em fases:

### Fase 1 - Interface pública

Trocar rótulos visíveis ao usuário para **Sonhe + Alto**, sem mudar rotas, apps ou modelos.

### Fase 2 - Centralização de constantes

Criar uma fonte única para nomes de produto, slugs públicos, equivalências e textos reutilizáveis.

### Fase 3 - Rotas e compatibilidade

Manter redirects ou aliases para URLs legadas, mas expor URLs públicas coerentes com o produto.

### Fase 4 - Refatoração técnica

Avaliar se vale renomear apps, modelos, tabelas ou namespaces. Esta fase só deve ocorrer quando houver testes e backup confiável, porque o risco é maior.

## Critério de aceite

Uma tela está correta quando:

- o aluno vê **Sonhe + Alto**;
- o mentor vê **Sonhe + Alto**;
- o administrador pode enxergar nomes técnicos apenas quando isso for necessário para governança;
- o código pode manter nomes legados apenas quando isso preservar compatibilidade.

