Patch v4 — Correção do logout (erro 405)

O que faz:
- apps/contas/views.py: logout_view passa a aceitar GET e POST (não dá mais 405).
  Se vier ?next=... (ou POST next=...), redireciona com segurança.
  Caso contrário, volta para a rota nomeada "portal".

- apps/contas/urls.py: comentário ajustado (rota continua /contas/logout/).

Como aplicar:
1) Feche o servidor (CTRL-BREAK).
2) Extraia este zip na raiz do projeto (mesmo nível de manage.py), permitindo sobrescrever.
3) Suba novamente o servidor.

Teste:
- Clique em "Sair" em qualquer página (P21 / Vocacional / Portal). Deve deslogar e voltar ao Portal.
