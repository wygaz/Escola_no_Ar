(venv) PS C:\Users\Wanderley\Apps\escola_no_ar_site> python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
March 19, 2026 - 17:26:15
Django version 5.0.2, using settings 'escola_no_ar_site.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.

[19/Mar/2026 17:26:36] "GET / HTTP/1.1" 302 0
[19/Mar/2026 17:26:36] "GET /contas/login/ HTTP/1.1" 200 6535
[19/Mar/2026 17:26:36] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
[19/Mar/2026 17:26:53] "GET /contas/registrar/ HTTP/1.1" 200 5880
[19/Mar/2026 17:26:54] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
[19/Mar/2026 17:28:49] "POST /contas/registrar/ HTTP/1.1" 200 6027
[19/Mar/2026 17:28:49] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
[19/Mar/2026 17:29:39] "GET /contas/registrar/ HTTP/1.1" 200 5880
[19/Mar/2026 17:29:43] "GET /contas/login/ HTTP/1.1" 200 6535
[19/Mar/2026 17:30:22] "POST /contas/login/ HTTP/1.1" 302 0
[19/Mar/2026 17:30:22] "GET /portal/ HTTP/1.1" 200 4803
[19/Mar/2026 17:30:37] "GET /vocacional/guia/avaliacao/?next=/portal/ HTTP/1.1" 200 46673
[19/Mar/2026 17:30:45] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:30:49] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:30:50] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:30:50] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:30:51] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:30:54] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:31:01] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:31:02] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:31:07] "POST /vocacional/guia/autosave/ HTTP/1.1" 200 12
[19/Mar/2026 17:31:16] "POST /vocacional/guia/avaliacao/?next=/portal/ HTTP/1.1" 302 0
[19/Mar/2026 17:31:16] "GET /portal/ HTTP/1.1" 200 4742
Internal Server Error: /guia/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\apps\core\views.py", line 708, in guia_redirect_preview
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
                                          ^^^^^^
NameError: name 'static' is not defined
[19/Mar/2026 17:31:29] "GET /guia/ HTTP/1.1" 500 74952
Internal Server Error: /guia/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\apps\core\views.py", line 708, in guia_redirect_preview
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
                                          ^^^^^^
NameError: name 'static' is not defined
[19/Mar/2026 17:31:36] "GET /guia/ HTTP/1.1" 500 74952
[19/Mar/2026 17:33:03] "GET /portal/?show_guia_feedback_pending=True HTTP/1.1" 200 4540
[19/Mar/2026 17:33:17] "GET /portal/?show_guia_feedback_pending=False HTTP/1.1" 200 4540
[19/Mar/2026 17:33:29] "GET /portal/?show_guia_feedback_pending=False HTTP/1.1" 200 4540
[19/Mar/2026 17:33:40] "GET /portal/?show_guia_feedback_pending=False HTTP/1.1" 200 4540
[19/Mar/2026 17:33:58] "GET /portal/?show_guia_feedback_pending=True HTTP/1.1" 200 4540
[19/Mar/2026 17:40:05] "GET /portal/ HTTP/1.1" 200 4540
[19/Mar/2026 17:40:05] "GET /vocacional/guia/avaliacao/?next=/portal/ HTTP/1.1" 200 46767
Internal Server Error: /guia/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\apps\core\views.py", line 708, in guia_redirect_preview
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
                                          ^^^^^^
NameError: name 'static' is not defined
[19/Mar/2026 17:40:23] "GET /guia/ HTTP/1.1" 500 74952
[19/Mar/2026 17:40:42] "GET /contas/login/ HTTP/1.1" 302 0
[19/Mar/2026 17:41:15] "GET /contas/logout/ HTTP/1.1" 302 0
[19/Mar/2026 17:41:15] "GET /portal/ HTTP/1.1" 302 0
[19/Mar/2026 17:41:15] "GET /contas/login/?next=/portal/ HTTP/1.1" 200 6535
[19/Mar/2026 17:41:15] "GET /static/core/img/logo-sonhe-mais-alto.png HTTP/1.1" 404 1858
[19/Mar/2026 17:41:45] "GET /admin HTTP/1.1" 301 0
[19/Mar/2026 17:41:46] "GET /admin/ HTTP/1.1" 302 0
[19/Mar/2026 17:41:46] "GET /admin/login/?next=/admin/ HTTP/1.1" 200 4188
[19/Mar/2026 17:41:46] "GET /static/admin/css/base.css HTTP/1.1" 304 0
[19/Mar/2026 17:41:46] "GET /static/admin/css/dark_mode.css HTTP/1.1" 304 0
[19/Mar/2026 17:41:46] "GET /static/admin/css/login.css HTTP/1.1" 304 0
[19/Mar/2026 17:41:46] "GET /static/admin/css/responsive.css HTTP/1.1" 304 0
[19/Mar/2026 17:41:46] "GET /static/admin/css/nav_sidebar.css HTTP/1.1" 304 0
[19/Mar/2026 17:41:46] "GET /static/admin/js/theme.js HTTP/1.1" 304 0
[19/Mar/2026 17:41:46] "GET /static/admin/js/nav_sidebar.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:03] "POST /admin/login/?next=/admin/ HTTP/1.1" 200 4386
[19/Mar/2026 17:42:31] "POST /admin/login/?next=/admin/ HTTP/1.1" 302 0
[19/Mar/2026 17:42:31] "GET /admin/ HTTP/1.1" 200 20421
[19/Mar/2026 17:42:31] "GET /static/admin/css/dashboard.css HTTP/1.1" 304 0
[19/Mar/2026 17:42:31] "GET /static/admin/img/icon-changelink.svg HTTP/1.1" 304 0
[19/Mar/2026 17:42:31] "GET /static/admin/img/icon-addlink.svg HTTP/1.1" 304 0
[19/Mar/2026 17:42:31] "GET /static/admin/img/icon-deletelink.svg HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /admin/contas/acesso/ HTTP/1.1" 200 24407
[19/Mar/2026 17:42:35] "GET /static/admin/css/changelists.css HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/core.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/jquery.init.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/actions.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/vendor/jquery/jquery.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/admin/RelatedObjectLookups.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/prepopulate.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/urlify.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/vendor/xregexp/xregexp.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/img/icon-yes.svg HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/img/search.svg HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/js/filters.js HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /admin/jsi18n/ HTTP/1.1" 200 8958
[19/Mar/2026 17:42:35] "GET /static/admin/img/tooltag-add.svg HTTP/1.1" 304 0
[19/Mar/2026 17:42:35] "GET /static/admin/img/icon-viewlink.svg HTTP/1.1" 304 0
[19/Mar/2026 17:43:17] "GET /admin/ HTTP/1.1" 200 20421
[19/Mar/2026 17:43:21] "GET /admin/contas/usuario/ HTTP/1.1" 200 26866
[19/Mar/2026 17:43:21] "GET /static/admin/img/icon-no.svg HTTP/1.1" 304 0
[19/Mar/2026 17:43:21] "GET /admin/jsi18n/ HTTP/1.1" 200 8958
[19/Mar/2026 17:43:21] "GET /static/admin/img/sorting-icons.svg HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /admin/contas/usuario/11/change/ HTTP/1.1" 200 38239
[19/Mar/2026 17:43:51] "GET /static/admin/css/forms.css HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/js/admin/DateTimeShortcuts.js HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/js/calendar.js HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/js/SelectBox.js HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/js/SelectFilter2.js HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /admin/jsi18n/ HTTP/1.1" 200 8958
[19/Mar/2026 17:43:51] "GET /static/admin/js/prepopulate_init.js HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/css/widgets.css HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/js/change_form.js HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/img/icon-unknown.svg HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/img/icon-unknown-alt.svg HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/img/selector-icons.svg HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/img/icon-calendar.svg HTTP/1.1" 304 0
[19/Mar/2026 17:43:51] "GET /static/admin/img/icon-clock.svg HTTP/1.1" 304 0
Internal Server Error: /guia/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\apps\core\views.py", line 708, in guia_redirect_preview
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
                                          ^^^^^^
NameError: name 'static' is not defined
[19/Mar/2026 17:59:31] "GET /guia/ HTTP/1.1" 500 74980
Internal Server Error: /guia/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\apps\core\views.py", line 708, in guia_redirect_preview
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
                                          ^^^^^^
NameError: name 'static' is not defined
[19/Mar/2026 17:59:35] "GET /guia/ HTTP/1.1" 500 74980
Internal Server Error: /guia/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\apps\core\views.py", line 708, in guia_redirect_preview
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
                                          ^^^^^^
NameError: name 'static' is not defined
[19/Mar/2026 17:59:42] "GET /guia/ HTTP/1.1" 500 74980
Internal Server Error: /guia/
Internal Server Error: /guia/
Internal Server Error: /guia/
Internal Server Error: /guia/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\apps\core\views.py", line 708, in guia_redirect_preview
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
                                          ^^^^^^
NameError: name 'static' is not defined
[19/Mar/2026 18:00:31] "GET /guia/ HTTP/1.1" 500 74980
Internal Server Error: /guia/
Traceback (most recent call last):
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Wanderley\Apps\escola_no_ar_site\apps\core\views.py", line 708, in guia_redirect_preview
    og_image = request.build_absolute_uri(static("core/img/capa-guia.jpg"))
                                          ^^^^^^
NameError: name 'static' is not defined
[19/Mar/2026 18:01:08] "GET /guia/ HTTP/1.1" 500 74980

===================================== FIM DO ERRO ====================================

Quero corrigir e consolidar a regra de negócio do Guia, do gating e da governança administrativa com base numa definição mais precisa.

## Regra de negócio corrigida
A Avaliação do Guia é obrigatória para todos os participantes do programa.

O usuário pode possuir o Guia de duas formas:
1. compra do Guia
2. concessão administrativa do Guia

Portanto:
- bônus liberado por admin NÃO dispensa Avaliação do Guia;
- o que muda é apenas a forma de obtenção do Guia;
- se o usuário não possui o Guia (nem por compra nem por concessão administrativa), ele NÃO deve ser enviado para a Avaliação do Guia;
- primeiro ele precisa resolver termos e posse válida do Guia;
- só depois a Avaliação do Guia passa a ser exigência válida;
- só depois entram os bônus/produtos específicos.

## Ordem lógica esperada
A decisão correta deve respeitar esta sequência:

1. Termos
2. Possui o Guia? (por compra ou concessão administrativa)
3. Avaliação do Guia
4. Gating específico do produto/bônus

## Correção conceitual importante
A variável relevante não é apenas:
- “comprou o Guia?”

Ela precisa refletir algo como:
- “possui Guia como pré-requisito válido”

seja por compra, seja por concessão administrativa.

## Regra adicional de governança/admin
Ao conceder bônus por administração, o sistema deveria automaticamente considerar:
- `possui_guia = True`

porque o Guia é pré-requisito obrigatório do programa.

Além disso, a própria concessão administrativa de bônus deveria idealmente oferecer uma ação assistida para evitar esquecimento do admin:

- checkbox marcada por default:
  **"Enviar o Guia para o e-mail do usuário"**

Assim, ao conceder o bônus:
- o sistema sinaliza posse válida do Guia;
- e já dispara ou prepara o envio do Guia ao e-mail do usuário.

## Intenção funcional
Quero evitar este erro semântico:
- usuário sem Guia cair em “Avaliação do Guia”

O correto é:
- sem Guia → resolver obtenção do Guia
- com Guia, mas sem avaliação → responder Avaliação do Guia
- com Guia + avaliação → seguir para bônus/produto
- com pendência legal → termos continuam sendo tratados com prioridade própria

## O que eu quero agora
Não quero código ainda.

Quero que você:
1. revise o entendimento atual da regra à luz dessa correção;
2. identifique onde a lógica atual ainda confunde:
   - compra do Guia
   - posse válida do Guia
   - avaliação do Guia
   - bônus/produto
   - concessão administrativa
3. diga onde isso impacta:
   - gating
   - governança
   - admin de concessão
   - status do usuário
4. proponha um ajuste curto de regra, sem redesign e sem camada paralela;
5. diga quais funções/arquivos provavelmente precisariam ser tocados;
6. proponha em qual etapa isso deve entrar:
   - se ainda cabe no fechamento da fase atual
   - ou se deve virar próxima frente específica de governança/admin
7. me devolva um mini-plano de correção com:
   - objetivo
   - escopo
   - risco principal
   - critério de aceite
   - smoke test

## Requisito adicional de governança
Também quero que você proponha a criação de um arquivo vivo de pendências/decisões do projeto, para servir como memória operacional e evitar esquecimentos nas próximas interações.

Sugestão de nome:
- `docs/arquitetura/pendencias_governanca.md`

Esse arquivo deve registrar pelo menos:
- regras de negócio já definidas;
- pendências de governança;
- decisões sobre gating;
- pendências de admin;
- automações desejadas;
- itens aprovados e ainda não implementados.

## Restrições
- não abrir camada paralela nova;
- não criar `services/` sem necessidade real;
- não mover a lógica interna do Vocacional para o core;
- não fazer redesign visual agora;
- não misturar, no mesmo patch, correção semântica de regra com grande refatoração de UX;
- não tratar bônus por admin como liberação irrestrita de todo o ecossistema.

## Resultado esperado
Quero uma resposta curta, técnica e auditável, com estas seções:
1. Regra revisada
2. Impactos no sistema
3. Ajuste curto recomendado
4. Etapa sugerida
5. Mini-plano de correção
6. Proposta de arquivo vivo de pendências