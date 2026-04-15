Os testes mudaram o diagnóstico.

Resultados observados:

Navegador normal:
1. admin normal -> logout -> login usuário comum -> OK
2. admin em modo teste -> sair modo teste -> logout -> login usuário comum -> 403
3. admin em modo teste -> logout direto -> login usuário comum -> OK
4. fechar navegador e reabrir -> voltou com login anterior (superusuário)

Janela anônima:
1. admin normal -> logout -> login usuário comum -> 403
2. admin em modo teste -> sair modo teste -> logout -> login usuário comum -> 403
3. admin em modo teste -> logout direto -> login usuário comum -> 403
4. fechar navegador e reabrir -> voltou limpo, na tela de login

Leitura arquitetural:
- o problema não parece estar resolvido;
- e agora não parece ser apenas sessão residual;
- o fluxo “sair modo teste” continua especialmente suspeito, porque no navegador normal ele é o único que quebra;
- mas o incognito mostra que existe também uma falha mais estrutural no destino/redirect pós-login, porque ali todos os fluxos deram 403.

Próximo passo exigido:
não quero mais correção por hipótese.
Quero instrumentação objetiva para identificar QUAL URL exata está respondendo 403 e em QUAL ponto do fluxo.

Peço esta investigação mínima:

1. Em SafeLoginView.get_success_url():
   - logar usuário autenticado
   - is_staff / is_superuser
   - redirect_to bruto
   - path normalizado
   - success_url final retornada

2. Em portal_impersonar_sair():
   - logar usuário antes da limpeza
   - existência de impersonate_user_id
   - valor de portal_mode
   - chaves limpas
   - redirect final emitido

3. Em logout_view():
   - logar usuário antes do logout
   - chaves residuais presentes
   - redirect final após logout

4. Identificar a URL do 403
   Quero saber exatamente:
   - qual rota está devolvendo 403
   - qual view/decorator/mixin gerou esse 403
   - se isso ocorre antes ou depois do login bem-sucedido

5. Revisar o destino de portal_impersonar_sair()
   Como o caso problemático no navegador normal é especificamente:
   admin em modo teste -> sair modo teste -> logout -> login usuário comum -> 403
   quero revisão especial desse fluxo e do redirecionamento para portal_dashboard.

6. Revisar se /portal/ ou alguma view intermediária está exigindo staff/gov indevidamente
   porque o incognito sugere que o usuário comum pode estar sendo levado a uma rota que ainda responde 403 mesmo sem /admin/.

Importante:
- não quero agora nova mudança ampla;
- quero primeiro diagnóstico observável com logs;
- depois disso decidimos o patch exato.

Observação adicional:
- o teste de fechar/reabrir navegador confirmou a cautela já registrada:
  SESSION_EXPIRE_AT_BROWSER_CLOSE deve ser entendido como sessão não persistente, e não como garantia absoluta de logout server-side, especialmente com restauração de sessão do navegador.