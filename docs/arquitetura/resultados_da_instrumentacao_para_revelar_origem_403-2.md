====admin em modo teste -> sair modo teste -> logout -> login usuário comum====

Rodou satisfatoriamente, sem 403

[20/Mar/2026 04:15:17] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta@gmail.com is_staff=True is_superuser=True redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 04:15:28] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:15:28] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:15:28] "GET /portal/dashboard/ HTTP/1.1" 200 2789
[20/Mar/2026 04:15:31] "GET /portal/impersonar/ HTTP/1.1" 200 2041
[20/Mar/2026 04:15:45] "GET /portal/impersonar/?q=wygazeta3%40sonhemaisalto.com.br HTTP/1.1" 200 2951
[20/Mar/2026 04:15:48] "POST /portal/impersonar/?q=wygazeta3%40sonhemaisalto.com.br HTTP/1.1" 302 0
[20/Mar/2026 04:15:51] "GET /portal/ HTTP/1.1" 200 10285
AUTH portal_impersonar_sair user=wygazeta@gmail.com had_impersonate_user_id=True portal_mode='user' cleared_keys=['impersonate_user_id', 'portal_mode'] final_redirect='/portal/dashboard/'
[20/Mar/2026 04:15:55] "GET /portal/impersonar/sair/ HTTP/1.1" 302 0
[20/Mar/2026 04:15:55] "GET /portal/dashboard/ HTTP/1.1" 200 2938
AUTH logout_view before user=wygazeta@gmail.com residual_keys=[] portal_mode=None impersonate_user_id=None next_url='/portal/dashboard/' normalized_path='/portal/dashboard/' final_redirect='/portal/'
[20/Mar/2026 04:16:02] "GET /contas/logout/?next=/portal/dashboard/ HTTP/1.1" 302 0
[20/Mar/2026 04:16:02] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:16:02] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[20/Mar/2026 04:16:02] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta5@sonhemaisalto.com.br is_staff=False is_superuser=False redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 04:16:18] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:16:18] "GET /portal/ HTTP/1.1" 200 9274



====admin normal -> logout -> login usuário comum:====

Rodou satisfatoriamente, sem 403

[20/Mar/2026 04:11:39] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta@gmail.com is_staff=True is_superuser=True redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 04:11:48] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:11:48] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:11:48] "GET /portal/dashboard/ HTTP/1.1" 200 2789
AUTH logout_view before user=wygazeta@gmail.com residual_keys=[] portal_mode=None impersonate_user_id=None next_url='/portal/dashboard/' normalized_path='/portal/dashboard/' final_redirect='/portal/'
[20/Mar/2026 04:12:01] "GET /contas/logout/?next=/portal/dashboard/ HTTP/1.1" 302 0
[20/Mar/2026 04:12:01] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:12:01] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[20/Mar/2026 04:12:01] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta2@sonhemaisalto.com.br is_staff=False is_superuser=False redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 04:12:09] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:12:12] "GET /portal/ HTTP/1.1" 200 9434



==== admin em modo teste -> logout direto -> login usuário comum ====

[20/Mar/2026 04:18:37] "GET / HTTP/1.1" 302 0
[20/Mar/2026 04:18:37] "GET /portal/ HTTP/1.1" 200 9274
AUTH logout_view before user=wygazeta5@sonhemaisalto.com.br residual_keys=[] portal_mode=None impersonate_user_id=None next_url=None normalized_path='/' final_redirect='/portal/'
[20/Mar/2026 04:18:47] "GET /contas/logout/ HTTP/1.1" 302 0
[20/Mar/2026 04:18:47] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:18:47] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[20/Mar/2026 04:18:47] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta@gmail.com is_staff=True is_superuser=True redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 04:18:55] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:18:55] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:18:55] "GET /portal/dashboard/ HTTP/1.1" 200 2789
[20/Mar/2026 04:19:02] "GET /portal/impersonar/ HTTP/1.1" 200 2041
[20/Mar/2026 04:19:23] "GET /portal/impersonar/?q=wygazeta2%40sonhemaisalto.com.br HTTP/1.1" 200 2951
[20/Mar/2026 04:19:29] "POST /portal/impersonar/?q=wygazeta2%40sonhemaisalto.com.br HTTP/1.1" 302 0
[20/Mar/2026 04:19:32] "GET /portal/ HTTP/1.1" 200 10285
AUTH logout_view before user=wygazeta@gmail.com residual_keys=['impersonate_user_id', 'portal_mode'] portal_mode='user' impersonate_user_id=3 next_url=None normalized_path='/' final_redirect='/portal/'
[20/Mar/2026 04:19:38] "GET /contas/logout/ HTTP/1.1" 302 0
[20/Mar/2026 04:19:38] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:19:38] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[20/Mar/2026 04:19:38] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta1@sonhemaisalto.com.br is_staff=False is_superuser=False redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 04:19:49] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:19:49] "GET /portal/ HTTP/1.1" 200 9510
[20/Mar/2026 04:19:59] "GET /guia/ HTTP/1.1" 200 1156
AUTH logout_view before user=wygazeta1@sonhemaisalto.com.br residual_keys=[] portal_mode=None impersonate_user_id=None next_url=None normalized_path='/' final_redirect='/portal/'
[20/Mar/2026 04:20:12] "GET /contas/logout/ HTTP/1.1" 302 0
[20/Mar/2026 04:20:12] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 04:20:12] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[20/Mar/2026 04:20:12] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
