# Patch único v1 — Vocacional (UI + templatetag + Refinamento Top 3)

Este patch adiciona o fluxo de **Refinamento Top 3 (Passe 1/2/3)** com:
- métrica **GAP** (diferença Top1–Top2) + probabilidade do Top1
- regra de parada (stop rule) no Passe 1 e Passe 2
- **Passe 3** (anti-frustração): SJT + contexto (ajuste leve no ranking)
- campos novos para import **idempotente** do banco (códigos)

## 1) Como aplicar

1) Extraia o `.zip` **na raiz do projeto** (onde está o `manage.py`).
2) Rode as migrações:

```bash
python manage.py migrate
```

3) (Opcional) Se você usa `.env`, ajuste as variáveis abaixo.

## 2) Variáveis de ambiente (opcionais)

Ative o refinamento por 3 passes:

```env
VOCACIONAL_PASS_TOTAL=3
```

Ajustes finos (defaults já funcionam):

```env
VOC_REF_PASS1_PER_DIM=2
VOC_REF_PASS2_PER_DIM=3
VOC_REF_PASS2_TOPK=5

VOC_REF_GAP_STOP_P1=0.20
VOC_REF_GAP_STOP_P2=0.15
VOC_REF_TOP1_MIN_P1=0.35
VOC_REF_TOP1_MIN_P2=0.32

VOC_REF_SOFTMAX_TAU=0.80
```

## 3) Como funciona a Stop Rule

- **Passe 1** (balanceado por dimensão):
  - Para se a diferença (GAP) entre Top1 e Top2 já estiver alta **e** o Top1 estiver "forte".

- **Passe 2** (foco nas top-k dimensões do Passe 1):
  - Para se GAP + Top1 forte **e** Top3 estável (mesmo conjunto do Passe 1).

- Se não parar no Passe 2, abre o **Passe 3**.

## 4) Passe 3 (anti-frustração)

- 3 cenários SJT + 2 perguntas de contexto.
- O ajuste é **leve** (não substitui as respostas); ele só ajuda a desempatar e reduzir frustração.

## 5) Import idempotente (banco 600+)

Foram adicionados campos:
- `Dimensao.codigo`
- `Pergunta.codigo`, `Pergunta.invert`, `Pergunta.bloco`
- `Avaliacao.passe_atual`, `Avaliacao.ref_data`

O comando `import_vocacional_json` já detecta esses campos e passa a conseguir rodar sem duplicar (quando você tiver códigos no JSON).
