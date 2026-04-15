A proposta está bem alinhada e eu aprovo a direção do micro-patch isolado em apps/contas.

Peço apenas estes ajustes de precisão para manter a solução cirúrgica, segura e sem brechas:

1. Ao tratar o redirect, não usar request.GET['next'] bruto.
   Prefira partir de super().get_redirect_url(), para preservar a validação segura já feita pelo Django quanto a host/scheme.

2. A regra de restrição deve inspecionar o path normalizado do destino, não a URL bruta em string.
   A ideia é avaliar o caminho efetivo do redirect e, sobre ele, decidir se é restrito.

3. Nesta primeira versão, manter a regra mínima:
   - tratar como restrito apenas /admin/
   - só incluir outros prefixos se já existirem no projeto e forem inequivocamente administrativos
   Isso evita scope creep e bloqueios indevidos em rotas legítimas do core/vocacional.

4. O fallback deve usar uma única fonte canônica:
   - preferencialmente self.get_default_redirect_url() ou settings.LOGIN_REDIRECT_URL
   - evitar duplicar "/portal/" em vários pontos, se o settings já for a origem oficial

Observação importante:
como o login atual usa redirect_authenticated_user=True, sobrescrever get_success_url() é uma boa escolha porque a sanitização do destino cobre tanto:
- o pós-login normal
- quanto o redirecionamento de usuário já autenticado que acessa /login/ com next herdado

Portanto, a linha mestra continua aprovada:
- patch só em apps/contas/views.py e apps/contas/urls.py
- sem tocar no gating
- sem tocar em core/permissions
- sem tocar em apps/vocacional/gating.py
- sem middleware global
- sem regra paralela de acesso

Se possível, na implementação, deixe explícito:
- qual método chama super().get_redirect_url()
- como o path é normalizado
- qual condição define usuário administrativo
- e que o fallback final usa LOGIN_REDIRECT_URL / get_default_redirect_url()

Critério de aceite permanece:
- usuário comum sem next -> /portal/
- usuário comum com next=/admin/ -> /portal/
- staff/superuser com next=/admin/ -> /admin/
- usuário comum com next permitido -> segue normalmente
- nenhum comportamento validado do gating é alterado