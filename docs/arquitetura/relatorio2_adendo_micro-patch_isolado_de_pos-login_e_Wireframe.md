Trouxe o resultado parcial dos testes e minha leitura arquitetural é a seguinte:

1) O micro-patch do pós-login ainda não pode ser dado como encerrado
Porque o 403 continua ocorrendo em teste real. Portanto, a hipótese do next restrito pode até estar correta para um caso, mas não explica tudo. Agora precisamos tratar isso como investigação complementar de fluxo de sessão/logout, e não mais como simples ajuste de next.

Diretriz:
- não considerar “fechar o navegador” como solução final;
- isso pode ser no máximo um workaround temporário;
- a correção precisa atacar a causa real.

Quero que você investigue especialmente estes vetores:
- logout saindo do admin e entrando com usuário comum no mesmo navegador;
- interação com portal_mode / modo teste / impersonação;
- limpeza de session keys ao sair do modo teste;
- eventual persistência de next, test-mode ou flags administrativas após troca de usuário;
- diferença entre login vindo do /admin/, do /contas/login/ e acesso ao /portal/ já autenticado.

Peço uma matriz curta de reprodução:
a) admin normal -> logout -> login usuário comum
b) admin em modo teste -> sair modo teste -> logout -> login usuário comum
c) admin -> fechar aba/navegador -> reabrir -> acessar portal
d) repetir em janela anônima para comparar

Suspeita adicional importante:
na tela do portal há sinais de duplicação de avisos de modo teste no topo. Isso sugere que pode existir estado residual ou renderização duplicada de banner/contexto. Quero checagem disso também.

2) Checkbox de permanência de sessão deve voltar como requisito explícito
Isso agora ficou claro como requisito funcional do contexto escolar/laboratório.

Quero uma implementação simples e segura:
- checkbox no login: “Permanecer conectado neste dispositivo”
- padrão: desmarcado
- desmarcado => sessão expira ao fechar o navegador
- marcado => sessão persistente por tempo configurado
- isso deve ser feito sem quebrar o login atual nem o fluxo do redirect seguro

Importante:
- em ambiente escolar, o padrão precisa favorecer segurança, não conveniência;
- portanto, o default não deve manter o aluno logado após fechar o navegador.

3) Precisamos de ferramental mínimo de governança para conseguir testar o gating corretamente
Hoje já existe a regra semântica de:
1. has_legal
2. possui Guia válido
3. Avaliação do Guia
4. produto/bônus

Mas o teste operacional ficou travado porque não há ferramenta administrativa simples para:
- marcar/conceder posse do Guia ao usuário
- visualizar o status consolidado do usuário
- opcionalmente registrar/envio do Guia
- enxergar qual é o próximo passo esperado daquele usuário

Quero um MVP administrativo/testável, sem reinventar a arquitetura:
- continuar usando Usuario + Produto + Acesso como base única
- não criar status paralelo
- não criar base paralela
- não reabrir o gating

Esse MVP deve mostrar, pelo menos:
- has_legal
- possui_guia
- origem do Guia (compra/admin, se já existir isso no modelo/contexto)
- has_guia_feedback
- produtos/acessos ativos
- inconsistência semântica, se houver
- próximo passo esperado no funil

E deve permitir, no mínimo:
- conceder Guia por admin
- remover concessão
- se possível, disparar ou registrar envio do Guia como ação administrativa separada

4) A nova tela do portal ficou boa, mas ainda precisa de lapidação de conteúdo
A direção visual está aprovada, porém peço os seguintes ajustes de UX/copy:
- remover repetição de textos informativos no topo, fora do hero
- revisar todo o texto em PT-BR com acentuação correta
- trocar linguagem mais técnica por linguagem mais acolhedora para público escolar
  Exemplo: trocar “na plataforma” por “neste espaço”
- rever o rótulo “Obter o Guia”
  Hoje ele está pouco autoexplicativo e parece compra direta sem contexto
  Melhor opção nesta fase:
  - “Conhecer o Guia”
  - ou “Saiba mais sobre o Guia”
- esse botão deve apontar para página explicativa/vitrine do projeto, não necessariamente direto para compra
- manter coerência com o wireframe: mesma página base para todos, CTA principal variando por estado do usuário
- planejar inclusão de logotipo e cabeçalho oficial, mas isso pode entrar como pendência se não for o foco imediato

5) Ordem prática sugerida
Para não misturar escopos, quero seguir nesta ordem:
A. fechar diagnóstico real do 403 remanescente
B. restaurar checkbox de permanência de sessão
C. criar MVP de governança/teste para Guia + status consolidado
D. lapidar portal (copy, repetição, header/logo, links do Guia)

Peço que sua próxima resposta venha separada em:
- diagnóstico provável do 403 remanescente
- plano mínimo de implementação do checkbox de sessão
- proposta de MVP administrativo para teste do Guia/status
- lista objetiva dos ajustes de portal