# Relatorio de limpeza do ambiente - 2026-04-16 - lote 1

## Escopo executado

Foi executado apenas o `Lote 1` do plano de limpeza do ambiente de desenvolvimento.

Referência:

- `docs/arquitetura/plano_limpeza_ambiente_desenvolvimento.md`

Critério aplicado:

- mover somente material local/ignorado e diretórios auxiliares que não fazem parte do runtime do sistema.

## Destino usado

Quarentena local:

- `Apenas_Local/Doc.quarentena/2026-04-16_lote1/`

Subpastas criadas:

- `Apenas_Local/Doc.quarentena/2026-04-16_lote1/diretorios`
- `Apenas_Local/Doc.quarentena/2026-04-16_lote1/arquivos_raiz`

## Diretorios movidos

- `_snapshot_export`
- `_snapshot_export_clean`
- `_safety_snapshots`
- `hotfix_entrada_is_ref`
- `escopo_vocacional`
- `Outros_docs_em_geral`
- `venv_corrompido_backup`

## Arquivos da raiz movidos

- `backup_BD_18-02-2026.json`
- `email_recuperacao_fix.html`
- `empacotar_snapshot_guia_descoberta.ps1`
- `Gerar_kit_chat_escopo_vocacional.ps1`
- `gerar_kit_chat_vocacional.py`
- `hotfix_entrada_is_ref.zip`
- `Kit_Chat_escopo_vocacional_PATCHED_v8.zip`
- `Logo_Sonhe_mais_alto_1536x1024_RGB .png`
- `MANIFEST.txt`
- `pacote_codex_guia_descoberta.zip`
- `patch_abcfinal_sem_repeticao.zip`
- `patch_fix_entrada_and_equivalencias.zip`
- `patch_fix_fc_text_and_guia_static.zip`
- `patch_fix_questao_counter_e_abc_textos.zip`
- `patch_fluxo_logout_e_registro_v11.zip`
- `patch_impersonacao_mvp.zip`
- `patch_ofertas_refinamento_e_ui_v1.zip`
- `patch_portal_sem_produto_guia.zip`
- `patch_portal_v12_fix1.zip`
- `patch_portal_vocacional_precisao_v12.zip`
- `patch_vocacional_entitlements_routing.zip`
- `patch_vocacional_etapas_passes_v9.zip`
- `patch_vocacional_forced_choice_v13.zip`
- `patch_vocacional_refinamento_ui_v10.zip`
- `patch_vocacional_split_bonus_refinamento_v2.zip`
- `Sequencia de comandos para preparacao dos artigos para publicacao e geracao de sermoes.txt`
- `Sonhe_Mais_Alto.zip`
- `Sonhe_mais_alto_1536x1024_RGB.png`

## Resultado

A raiz do projeto ficou significativamente mais limpa, preservando:

- arquivos de runtime;
- arquivos de repositório;
- certificados locais;
- scripts operacionais;
- documentação ainda rastreada e que precisa de classificação fina.

## Impacto no Git

Nenhum arquivo de código foi alterado.

Após o lote 1, o Git registrou apenas documentação nova desta sessão.

## Pendência imediata

O `Lote 2` deve tratar os arquivos rastreados da raiz e o diretório legado `Projeto21/`, com decisão individual entre:

- mover para `docs/`, quando forem documentação útil;
- mover para quarentena local, quando forem histórico ou redundância;
- manter na raiz, apenas se forem realmente operacionais.
