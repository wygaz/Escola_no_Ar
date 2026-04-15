Os logs fecharam o diagnóstico do 403.

Causa real confirmada:
o usuário comum está sendo levado para /portal/dashboard/, que é uma rota restrita de governança/staff.

Evidência objetiva dos logs:
- logout_view registrou final_redirect='/portal/dashboard/'
- depois houve GET /contas/login/?next=/portal/dashboard/
- SafeLoginView.get_success_url() retornou final_success_url='/portal/dashboard/' para usuário comum
- PortalDashboardView.test_func() negou acesso
- o 403 final veio exatamente de /portal/dashboard/

Conclusão:
o problema atual não é mais apenas sessão residual.
A causa operacional do 403 é preservação indevida de next/destino restrito no fluxo logout -> login.

Diretriz de correção:

1. Ajuste principal em logout_view()
No contexto escolar e compartilhado, o logout não deve preservar next de páginas administrativas/governança.
Quero uma política segura:
- ignorar next no logout
- redirecionar sempre para uma página pública segura, preferencialmente /portal/
- sem carregar /portal/dashboard/ para a próxima navegação/login

2. Blindagem adicional em SafeLoginView.get_success_url()
Além de /admin/, tratar também como restrito para usuário não-staff:
- /portal/dashboard
- /portal/dashboard/
- e qualquer rota explicitamente equivalente de governança, se existir

Se um next desses aparecer para usuário comum, deve cair no fallback canônico público, não em dashboard.

3. Manter a limpeza de sessão já feita
A limpeza de impersonate_user_id e portal_mode continua válida, mas agora ela deixa de ser a explicação principal do 403.
O foco do patch deve ser:
- destino restrito herdado
- e neutralização desse destino no logout/login

4. Não reabrir gating
Esse patch continua sendo de autenticação/redirecionamento/governança, não de Guia/Avaliação/bônus.

Pedido de implementação:
quero um patch estreito e explícito que:
- elimine o reaproveitamento de /portal/dashboard/ no logout
- e impeça que usuário comum seja redirecionado para dashboard via next

Depois disso eu repito os testes.