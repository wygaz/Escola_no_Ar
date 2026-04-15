Quero tratar este ponto como micro-patch isolado de pós-login, sem misturar com o patch semântico do gating.

Contexto já validado no projeto Escola no Ar / Guia de Descoberta:
- hotfix de /guia/ aprovado;
- patch semântico do gating aprovado funcionalmente;
- ordem correta do gating:
  1. has_legal
  2. possui Guia válido
  3. Avaliação do Guia
  4. produto/bônus
- “possui Guia válido” pode vir por compra ou por concessão administrativa;
- bônus concedido por admin NÃO dispensa Avaliação do Guia;
- usuário sem Guia válido NÃO deve cair em Avaliação do Guia;
- aviso de inconsistência para “bônus sem Guia explícito” está coerente com a regra.

Ponto novo e separado:
- houve 403 Forbidden ao sair da sessão de admin e entrar com usuário comum;
- hipótese forte: next/redirect herdado de rota restrita (/admin/ ou equivalente);
- isso parece ser problema de redirect pós-login, não problema do patch semântico do gating.

Diretriz arquitetural importante:
- não misturar esta correção com regras de Guia, Avaliação, bônus, produto, onboarding ou gating;
- não criar gating paralelo;
- não criar status paralelo;
- não criar base paralela de usuários;
- preservar apps/contas.Usuario + Produto + Acesso como base única;
- manter o core como entrada/orquestração e o Vocacional como dono do fluxo interno.

Recomendação de implementação:
- criar uma LoginView segura em apps/contas/views.py;
- ajustar apps/contas/urls.py para usar essa view;
- a view deve filtrar o next quando ele apontar para rota restrita incompatível com o perfil do usuário;
- para usuário comum, se next for /admin/ ou outra rota claramente restrita, ignorar esse next e cair em /portal/ ou LOGIN_REDIRECT_URL;
- para staff/superuser, preservar o next legítimo;
- manter o uso normal de next para destinos permitidos.

O que quero evitar:
- mexer no patch semântico do gating;
- alterar regras de has_legal, possui_guia, has_guia_feedback ou produto/bônus;
- espalhar essa lógica em vários pontos do projeto;
- criar middleware global para um problema que parece local do login;
- fazer introspecção excessiva de permissões nesta etapa.

Escopo ideal deste micro-patch:
1. interceptar o redirect pós-login;
2. validar o next;
3. bloquear destino restrito para usuário comum;
4. aplicar fallback seguro para /portal/ ou LOGIN_REDIRECT_URL.

Critérios de aceite:
- usuário comum sem next → /portal/
- usuário comum com next=/admin/ → /portal/
- staff/superuser com next=/admin/ → /admin/
- usuário comum com next permitido → segue normalmente
- nenhuma alteração no comportamento funcional já validado do gating

Peço que a solução seja cirúrgica e previsível, focada só no 403 pós-login.
Ao propor o patch, por favor destaque exatamente:
- arquivos alterados,
- método sobrescrito,
- regra usada para considerar um next restrito,
- e por que isso não interfere na arquitetura do gating.