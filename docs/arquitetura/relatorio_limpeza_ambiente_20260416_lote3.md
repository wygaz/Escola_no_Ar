# Relatorio de limpeza do ambiente - 2026-04-16 - lote 3

## Escopo executado

Foi feita a limpeza dos arquivos rastreados de raiz considerados legados e sem valor operacional atual.

Critério aplicado:

- arquivos documentais antigos ou de patch: retirar do repositório e preservar localmente em quarentena;
- arquivo técnico de apoio/copias de sistema: retirar do repositório e preservar em `Apenas_Local/Olds/`.

## Arquivos documentais movidos para quarentena local

Destino:

- `Apenas_Local/Doc.quarentena/2026-04-16_lote2/arquivos_rastreados_raiz`

Arquivos:

- `Arvore_Oficial_do_Core`
- `README.txt`
- `README_PATCH.md`
- `README_PATCH_LOGOUT_v4.txt`
- `Solucao_para_consentimento.txt`

## Arquivo técnico movido para Olds

Destino:

- `Apenas_Local/Olds/`

Arquivo:

- `_inspect_apps.py`

## Efeito no Git

Os arquivos acima deixaram de ser rastreados no repositório.

## Justificativa

- o conteúdo era legado, redundante ou já superado pela documentação atual em `docs/arquitetura`;
- não fazia parte do runtime do sistema;
- a preservação local mantém uma trilha de segurança caso algo precise ser consultado no futuro.

## Resultado

A raiz do projeto ficou mais próxima do objetivo de conter apenas:

- arquivos operacionais;
- arquivos de repositório;
- documentação realmente ativa.
