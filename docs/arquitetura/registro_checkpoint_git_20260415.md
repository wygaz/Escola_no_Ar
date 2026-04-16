# Registro de Checkpoint Git - 15/04/2026

## Finalidade

Este registro documenta a estabilização do repositório após um período com muitas mudanças acumuladas, arquivos deletados e alerta recorrente do VSCode/Git.

O objetivo foi criar um ponto seguro de retomada antes de continuar a refatoração arquitetural e o desenvolvimento do **Sonhe + Alto**.

## Situação inicial

Ao abrir o projeto, o Git/VSCode reclamava de excesso de mudanças ativas.

O diagnóstico mostrou:

- centenas de arquivos rastreados como alterados/deletados;
- muitos arquivos não rastreados;
- dois blobs ausentes no repositório local;
- `git diff --stat` falhando;
- risco de perder referência sobre o que já havia sido feito.

## Problema de integridade corrigido

O `git fsck --full` apontou dois objetos ausentes:

- `apps/publicacoes/Formularios/Avaliacao_e_Reflexao_Final.png`
- `apps/publicacoes/Formularios/Cronograma_semanal_de_Metas.png`

Esses dois arquivos foram recuperados localmente e recolocados em:

```text
apps/publicacoes/Formularios/
```

Depois disso:

- `git fsck --full` deixou de apontar `missing blob`;
- `git diff --stat` voltou a funcionar;
- o problema deixou de ser corrupção prática do Git e passou a ser apenas excesso de mudanças pendentes.

## Snapshot de segurança

Antes do saneamento final, foi criado um snapshot operacional em:

```text
_safety_snapshots/git_triage_20260415_200833
```

Esse snapshot contém:

- status do Git;
- resultado do `git fsck`;
- lista de arquivos modificados;
- lista de arquivos deletados;
- lista de arquivos não rastreados;
- cópia dos arquivos de trabalho de texto/código relevantes.

## Branch criada

Foi criada uma branch local para isolar o checkpoint:

```text
checkpoint/saneamento-20260415
```

## Commit criado

Foi criado o commit local:

```text
6611815 checkpoint: saneamento do worktree e retomada Sonhe + Alto
```

Esse commit incorporou:

- mudanças rastreadas já acumuladas;
- deleções de acervos antigos rastreados;
- código novo;
- migrations novas;
- templates novos;
- CSS compartilhado;
- documentação Markdown/TXT em `docs/arquitetura`;
- decisão de nomenclatura pública do produto como **Sonhe + Alto**;
- ajustes de `.gitignore` para evitar que snapshots, backups e acervos locais voltem a poluir o status.

## Estado após o checkpoint

Após o commit:

```text
git status --short
```

ficou sem saída.

Também foi verificado:

```text
git fsck --full
```

sem indicação de `missing blob` ou erro.

## O que ficou fora do Git

Ficaram fora do Git, por decisão de segurança operacional:

- `_safety_snapshots/`
- `_snapshot_export/`
- `_snapshot_export_clean/`
- `venv_corrompido_backup/`
- backups de banco (`backup_BD_*.json`)
- acervos e materiais avulsos pesados
- scripts e arquivos locais auxiliares não essenciais ao runtime
- imagens/PDFs/DOCXs grandes de documentação que não são necessários ao código

Esses arquivos podem continuar no disco, mas não devem aparecer como pendência do Git.

## Validação realizada

Realizado com sucesso:

- `git fsck --full`
- `git status --short`
- criação de branch
- criação de commit local

Não realizado neste ambiente:

- `py_compile`

Motivo: o Python local do ambiente usado pelo agente apontava para um runtime inexistente:

```text
No Python at 'C:\Users\Wanderley\AppData\Local\Programs\Python\Python312\python.exe'
```

O usuário deve validar no terminal ativo com:

```powershell
python -m py_compile apps\sonho_de_ser\services.py apps\sonho_de_ser\permissions.py apps\sonho_de_ser\serializers.py apps\sonho_de_ser\views.py apps\core\views.py apps\vocacional\views.py
```

## Regra de retomada

A partir deste ponto:

1. Trabalhar preferencialmente na branch `checkpoint/saneamento-20260415` até confirmar estabilidade.
2. Não fazer novas limpezas amplas de Git sem snapshot ou commit anterior.
3. Separar mudanças futuras por fatias menores.
4. Antes de nova refatoração relevante, rodar:

```powershell
git status --short
git fsck --full
python -m py_compile apps\sonho_de_ser\services.py apps\sonho_de_ser\views.py apps\core\views.py apps\vocacional\views.py
```

5. Se o servidor e os fluxos principais estiverem estáveis, decidir depois se:

- mantemos trabalho nesta branch por mais uma fase; ou
- fazemos merge/fast-forward para `master`; ou
- criamos uma branch nova específica para a próxima fase.

## Risco conhecido

O commit é grande porque consolidou muitas pendências acumuladas. Ele resolve o estado operacional do Git, mas não deve virar padrão de trabalho.

Daqui em diante, o padrão deve voltar a ser:

- diagnóstico;
- mudança pequena;
- validação;
- commit pequeno;
- registro objetivo.

