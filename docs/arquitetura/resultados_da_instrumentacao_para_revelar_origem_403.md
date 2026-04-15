====admin em modo teste -> sair modo teste -> logout -> login usuário comum====

[20/Mar/2026 03:36:26] "GET / HTTP/1.1" 302 0
[20/Mar/2026 03:36:26] "GET /contas/login/ HTTP/1.1" 200 6535
[20/Mar/2026 03:36:26] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta@gmail.com is_staff=True is_superuser=True redirect_to='' normalized_path=None final_success_url='/portal/'
[20/Mar/2026 03:36:41] "POST /contas/login/ HTTP/1.1" 302 0
[20/Mar/2026 03:36:41] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:36:41] "GET /portal/dashboard/ HTTP/1.1" 200 2789
[20/Mar/2026 03:36:54] "GET /portal/impersonar/ HTTP/1.1" 200 2041
[20/Mar/2026 03:36:58] "GET /portal/impersonar/?q=wygazeta3%40sonhemaisalto.com.br HTTP/1.1" 200 2951
[20/Mar/2026 03:36:59] "POST /portal/impersonar/?q=wygazeta3%40sonhemaisalto.com.br HTTP/1.1" 302 0
[20/Mar/2026 03:37:03] "GET /portal/ HTTP/1.1" 200 10285
[20/Mar/2026 03:37:03] "GET /static/css/core_portal.css HTTP/1.1" 304 0
AUTH portal_impersonar_sair user=wygazeta@gmail.com had_impersonate_user_id=True portal_mode='user' cleared_keys=['impersonate_user_id', 'portal_mode'] final_redirect='/portal/dashboard/'
[20/Mar/2026 03:37:29] "GET /portal/impersonar/sair/ HTTP/1.1" 302 0
[20/Mar/2026 03:37:29] "GET /portal/dashboard/ HTTP/1.1" 200 2938
AUTH logout_view before user=wygazeta@gmail.com residual_keys=[] portal_mode=None impersonate_user_id=None final_redirect='/portal/dashboard/'
[20/Mar/2026 03:37:31] "GET /contas/logout/?next=/portal/dashboard/ HTTP/1.1" 302 0
[20/Mar/2026 03:37:31] "GET /portal/dashboard/ HTTP/1.1" 302 0
[20/Mar/2026 03:37:31] "GET /contas/login/?next=/portal/dashboard/ HTTP/1.1" 200 6535
[20/Mar/2026 03:37:31] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta3@sonhemaisalto.com.br is_staff=False is_superuser=False redirect_to='/portal/dashboard/' normalized_path='/portal/dashboard/' final_success_url='/portal/dashboard/'
[20/Mar/2026 03:37:59] "POST /contas/login/?next=/portal/dashboard/ HTTP/1.1" 302 0
AUTH PortalDashboardView.test_func denied path='/portal/dashboard/' user=wygazeta3@sonhemaisalto.com.br is_staff=False is_superuser=False portal_mode=None real_user=wygazeta3@sonhemaisalto.com.br
Forbidden (Permission denied): /portal/dashboard/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\views\generic\base.py", line 104, in view
    return self.dispatch(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\contrib\auth\mixins.py", line 73, in dispatch
    return super().dispatch(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\contrib\auth\mixins.py", line 134, in dispatch
    return self.handle_no_permission()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\contrib\auth\mixins.py", line 48, in handle_no_permission
    raise PermissionDenied(self.get_permission_denied_message())
django.core.exceptions.PermissionDenied
AUTH 403 path='/portal/dashboard/' view_name='portal_dashboard' func='View.as_view.<locals>.view' user=wygazeta3@sonhemaisalto.com.br is_staff=False is_superuser=False real_user=wygazeta3@sonhemaisalto.com.br portal_mode=None impersonate_user_id=None
[20/Mar/2026 03:37:59] "GET /portal/dashboard/ HTTP/1.1" 403 135


====admin normal -> logout -> login usuário comum:====

[20/Mar/2026 03:41:43] "GET / HTTP/1.1" 302 0
[20/Mar/2026 03:41:46] "GET /portal/ HTTP/1.1" 200 9434
AUTH logout_view before user=wygazeta3@sonhemaisalto.com.br residual_keys=[] portal_mode=None impersonate_user_id=None final_redirect='/portal/'
[20/Mar/2026 03:42:14] "GET /contas/logout/ HTTP/1.1" 302 0
[20/Mar/2026 03:42:14] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:42:14] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[20/Mar/2026 03:42:14] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta@gmail.com is_staff=True is_superuser=True redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 03:42:34] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:42:34] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:42:34] "GET /portal/dashboard/ HTTP/1.1" 200 2789
AUTH logout_view before user=wygazeta@gmail.com residual_keys=[] portal_mode=None impersonate_user_id=None final_redirect='/portal/dashboard/'
[20/Mar/2026 03:42:45] "GET /contas/logout/?next=/portal/dashboard/ HTTP/1.1" 302 0
[20/Mar/2026 03:42:45] "GET /portal/dashboard/ HTTP/1.1" 302 0
[20/Mar/2026 03:42:45] "GET /contas/login/?next=/portal/dashboard/ HTTP/1.1" 200 6535
[20/Mar/2026 03:42:45] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta2@sonhemaisalto.com.br is_staff=False is_superuser=False redirect_to='/portal/dashboard/' normalized_path='/portal/dashboard/' final_success_url='/portal/dashboard/'
[20/Mar/2026 03:42:55] "POST /contas/login/?next=/portal/dashboard/ HTTP/1.1" 302 0
AUTH PortalDashboardView.test_func denied path='/portal/dashboard/' user=wygazeta2@sonhemaisalto.com.br is_staff=False is_superuser=False portal_mode=None real_user=wygazeta2@sonhemaisalto.com.br
Forbidden (Permission denied): /portal/dashboard/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\views\generic\base.py", line 104, in view
    return self.dispatch(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\contrib\auth\mixins.py", line 73, in dispatch
    return super().dispatch(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\contrib\auth\mixins.py", line 134, in dispatch
    return self.handle_no_permission()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\contrib\auth\mixins.py", line 48, in handle_no_permission
    raise PermissionDenied(self.get_permission_denied_message())
django.core.exceptions.PermissionDenied
AUTH 403 path='/portal/dashboard/' view_name='portal_dashboard' func='View.as_view.<locals>.view' user=wygazeta2@sonhemaisalto.com.br is_staff=False is_superuser=False real_user=wygazeta2@sonhemaisalto.com.br portal_mode=None impersonate_user_id=None
[20/Mar/2026 03:42:55] "GET /portal/dashboard/ HTTP/1.1" 403 135


==== admin em modo teste -> logout direto -> login usuário comum ====

Rodou como desejável.

[20/Mar/2026 03:44:19] "GET / HTTP/1.1" 302 0
[20/Mar/2026 03:44:23] "GET /portal/ HTTP/1.1" 200 9434
AUTH logout_view before user=wygazeta2@sonhemaisalto.com.br residual_keys=[] portal_mode=None impersonate_user_id=None final_redirect='/portal/'
[20/Mar/2026 03:44:43] "GET /contas/logout/ HTTP/1.1" 302 0
[20/Mar/2026 03:44:43] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:44:43] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[20/Mar/2026 03:44:43] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta@gmail.com is_staff=True is_superuser=True redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 03:44:59] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:44:59] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:44:59] "GET /portal/dashboard/ HTTP/1.1" 200 2789
[20/Mar/2026 03:45:47] "GET /portal/impersonar/ HTTP/1.1" 200 2041
[20/Mar/2026 03:45:54] "GET /portal/impersonar/?q=wygazeta3%40sonhemaisalto.com.br HTTP/1.1" 200 2951
[20/Mar/2026 03:45:56] "POST /portal/impersonar/?q=wygazeta3%40sonhemaisalto.com.br HTTP/1.1" 302 0
[20/Mar/2026 03:46:00] "GET /portal/ HTTP/1.1" 200 10285
AUTH logout_view before user=wygazeta@gmail.com residual_keys=['impersonate_user_id', 'portal_mode'] portal_mode='user' impersonate_user_id=4 final_redirect='/portal/'
[20/Mar/2026 03:46:23] "GET /contas/logout/ HTTP/1.1" 302 0
[20/Mar/2026 03:46:23] "GET /portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:46:23] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[20/Mar/2026 03:46:24] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
AUTH get_success_url user=wygazeta2@sonhemaisalto.com.br is_staff=False is_superuser=False redirect_to='/portal/' normalized_path='/portal/' final_success_url='/portal/'
[20/Mar/2026 03:46:32] "POST /contas/login/?next=/portal/ HTTP/1.1" 302 0
[20/Mar/2026 03:46:36] "GET /portal/ HTTP/1.1" 200 9434
