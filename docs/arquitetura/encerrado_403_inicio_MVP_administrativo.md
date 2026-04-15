Os testes fecharam bem esta frente.

Validação prática:
- admin normal -> logout -> login usuário comum -> OK
- admin em modo teste -> sair modo teste -> logout -> login usuário comum -> OK
- admin em modo teste -> logout direto -> login usuário comum -> OK

Leitura final:
- o 403 foi resolvido;
- os logs confirmam que o problema anterior era a preservação indevida de next=/portal/dashboard/ no fluxo logout -> login;
- agora o logout neutraliza esse destino para /portal/;
- e o login do usuário comum permanece em /portal/, sem cair em rota staff/governança.

Conclusão arquitetural:
- considero esta frente encerrada funcionalmente;
- a correção ficou no lugar certo (autenticação/redirecionamento/governança);
- sem reabrir gating e sem criar regra paralela.

Peço apenas dois fechamentos de higiene técnica:
1. reduzir/remover a instrumentação detalhada ou condicioná-la a DEBUG=True;
2. registrar como pendência separada o 404 do arquivo estático:
   /static/core/img/logo-sonhe-mais-alto.png

   nome correto -> C:\Users\Wanderley\Apps\escola_no_ar_site\static\core\img\Logo_Sonhe_mais_alto_1536x1024_RGB .png

Com isso, podemos avançar para a próxima etapa:
C. MVP administrativo enxuto de Guia/status
Depois:
D. lapidação do portal