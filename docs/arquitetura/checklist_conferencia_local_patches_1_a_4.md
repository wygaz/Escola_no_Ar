# Checklist de Conferência Local dos Patches 1 a 4

## Pendências gerais
- rodar `python manage.py check`
- confirmar que não houve regressão visual em `apps/core/templates/core/portal.html`
- confirmar que o comportamento de `staff/superuser` com `portal_mode=user` continua correto
- confirmar que os `_legacy_*` não estão sendo chamados por nenhuma rota ativa
- lembrar que a limpeza física dos `_legacy_*` ainda continua pendente antes de encerrar a Fase 1

## Patch 1  Consolidação de contexto

### O que precisa conferir
- `portal()` e `portal_home()` continuam renderizando corretamente
- o contexto do portal continua chegando completo ao template
- `show_attention`, `has_legal`, `has_guia_feedback`, `has_prod_voc`, `has_prod_sma` continuam coerentes
- a tela não perdeu CTAs, alerts ou chips de status

### Teste local mínimo
- anônimo em `/`
- usuário comum em `/portal/`
- conferir se o portal abre sem erro e com os mesmos blocos esperados

## Patch 2  Dispatcher aluno/governança

### O que precisa conferir
- usuário comum continua indo para o fluxo normal do portal
- `staff` e `superuser` vão para governança por padrão
- `portal_mode=user` continua forçando experiência de usuário
- a raiz autenticada `/` segue o mesmo trilho de `/portal/`

### Teste local mínimo
- `staff` em `/portal/`
- `staff` em `/portal/?portal_mode=user`
- `staff` em `/?portal_mode=user`
- `superuser` em `/portal/`
- `superuser` em `/portal/?portal_mode=user`

## Patch 3  Resolvedor central mínimo por produto

### O que precisa conferir
- a rota `produtos/<slug>/entrar/` resolve corretamente
- `vocacional` entra por `vocacional:entrada`, não direto por `etapas`
- `sonhe-mais-alto` entra pelo destino atual configurado
- usuários sem acesso continuam sendo desviados para o CTA correto do gating existente
- usuários não autenticados são levados ao login com `next` correto

### Teste local mínimo
- anônimo clicando no card do Vocacional em `/portal/`
- usuário autenticado sem onboarding clicando no Vocacional
- usuário autenticado com acesso completo clicando no Vocacional
- repetir o mesmo para Sonhe + Alto

## Patch 4  Estado enxuto por produto

### O que precisa conferir
- `product_states` está sendo montado sem quebrar o template atual
- as chaves antigas ainda continuam coerentes:
  - `can_vocacional`
  - `can_sonhemaisalto`
  - `voc_alert`
  - `sonhe_alert`
  - `has_prod_voc`
  - `has_prod_sma`
  - `req_bonus_voc`
  - `req_bonus_sma`
- `has_prod_guia_like` agora existe e não quebrou a caixa de atenção
- não surgiu nenhuma nova fonte de verdade fora de `views.py`

### Teste local mínimo
- usuário sem acesso
- usuário com onboarding pendente
- usuário com acesso completo
- comparar visualmente os estados mostrados no portal com o comportamento esperado do gating atual

## Checklist único de smoke test
- anônimo em `/`
- usuário comum em `/portal/`
- usuário com onboarding pendente em `/portal/`
- usuário com acesso completo em `/portal/`
- `staff` em `/portal/`
- `staff` em `/portal/?portal_mode=user`
- `staff` em `/?portal_mode=user`
- `superuser` em `/portal/`
- `superuser` em `/portal/?portal_mode=user`

## Comando principal

```powershell
python manage.py check
```
