Li sua resposta e, no geral, considero a direção aprovada.

Validação:
- o raciocínio de que o micro-patch do next não fecha sozinho o 403 faz sentido;
- a hipótese de estado residual de sessão ligado a impersonação/modo teste é plausível;
- a volta do checkbox “Permanecer conectado neste dispositivo” é requisito funcional importante no contexto escolar;
- o MVP administrativo para conceder Guia e visualizar status é necessário para conseguirmos testar o gating de forma correta;
- os ajustes de portal podem ficar para depois dessas correções estruturais.

Peço apenas uma disciplina de execução:

1. Antes de ampliar correções do 403, fechar a reprodução do bug
Quero evidência prática de qual estado residual está causando o problema:
- impersonate_user_id
- portal_mode
- ambos
- ou redirect_authenticated_user em combinação com sessão reaproveitada

2. Não quero mudança grande baseada só em hipótese
Se possível, faça primeiro um ajuste mínimo de logout/saída de modo teste com limpeza explícita das chaves residuais relevantes, e descreva exatamente quais chaves serão limpas e em quais fluxos.

3. Checkbox de permanência pode seguir depois disso
A proposta técnica com form customizado + set_expiry no SafeLoginView está boa.

4. MVP administrativo deve ser enxuto
Primeira entrega:
- buscar usuário por e-mail
- mostrar has_legal
- mostrar possui_guia
- mostrar has_guia_feedback
- mostrar acessos ativos
- mostrar próximo passo esperado
- permitir conceder/remover Guia por admin

5. Portal
Pode entrar depois:
- remover textos repetidos no topo
- revisar PT-BR e acentuação
- trocar “na plataforma” por “neste espaço”
- trocar “Obter o Guia” por CTA mais explicativo
- apontar para página-vitrine/explicativa
- prever logo/cabeçalho oficial

Resumo da prioridade:
A. fechar causa real do 403
B. restaurar checkbox de permanência
C. criar MVP administrativo de Guia/status
D. lapidar portal