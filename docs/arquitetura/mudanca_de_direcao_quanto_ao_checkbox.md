Mudança de direção aprovada para o contexto escolar:

Decisão:
- não implementar checkbox “Permanecer conectado neste dispositivo”;
- a política padrão deve ser sessão não persistente;
- ao clicar em “Sair”, fazer logout completo e limpeza explícita de estado residual;
- a sessão deve expirar ao fechar o navegador, sem opção de persistência para o aluno.

Justificativa:
- estamos em ambiente escolar/laboratório;
- o risco de reutilização indevida do ambiente por outro aluno é alto;
- por responsabilidade de segurança, é melhor não oferecer conveniência que amplie esse risco.

Importante:
- não tratar isso como substituto automático da correção do 403;
- expiração ao fechar o navegador ajuda, mas não resolve sozinha estados residuais no mesmo ciclo de uso;
- portanto, a limpeza explícita de sessão continua necessária.

Diretriz técnica:
1. remover a etapa B anterior do checkbox de permanência;
2. manter sessão como cookie de sessão, sem “remember me”;
3. fortalecer o logout explícito:
   - limpar impersonate_user_id
   - limpar portal_mode
   - limpar quaisquer chaves de contexto de modo teste/impersonação relevantes
   - depois encerrar a sessão
4. revisar portal_impersonar_sair() com o mesmo rigor, para não deixar contexto administrativo residual
5. só depois revalidar o 403

Nova ordem operacional:
A. fechar a causa real do 403 com limpeza mínima e explícita de sessão
B. consolidar política de sessão não persistente em ambiente escolar
C. criar o MVP administrativo enxuto de Guia/status
D. lapidar portal

Cautela importante:
- “logout compulsório ao fechar o navegador” deve ser entendido como sessão não persistente, e não como garantia absoluta de evento de logout no servidor;
- portanto, não usar isso como única camada de segurança;
- não usar JS/beforeunload como mecanismo principal de segurança;
- se houver algum recurso visual de alerta, ele deve ser apenas complementar, nunca o controle principal.