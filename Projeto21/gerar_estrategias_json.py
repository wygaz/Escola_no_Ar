import json
import math
from pathlib import Path

import pandas as pd


def limpar_numero(valor):
    """
    Converte para número normal; se for NaN/inf ou vazio, vira None.
    Evita NaN/infinito no json.dump(allow_nan=False).
    """
    if valor is None:
        return None
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return None

    if math.isnan(v) or math.isinf(v):
        return None

    return int(v) if v.is_integer() else v


# ============================================================
# Caminhos – AJUSTE aqui para o seu ambiente, se precisar
# ============================================================
EXCEL_PATH = Path(
    r"C:\Users\Wanderley\Apps\escola_no_ar_site\Projeto21\Projeto21_com_frequencia_e_objetivos_geral.xlsx"
)

OUT_PATH = Path(
    r"C:\Users\Wanderley\Apps\escola_no_ar_site\apps\projeto21\static\projeto21\data\estrategias.json"
)

# Nome da aba única que contém TODAS as estratégias
SHEET_NAME = "Geral"   # exatamente como está na planilha


def main():
    print(f"[Projeto21] Lendo arquivo: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

    linhas_originais = len(df)

    # --------------------------------------------------------
    # Renomeia colunas para nomes canônicos
    # (não remove as demais – só dá nome fixo às que interessam)
    # --------------------------------------------------------
    df = df.rename(
        columns={
            "Area": "area",
            "Área": "area",
            "Nivel": "nivel",
            "Nível": "nivel",
            "Estrategia": "estrategia",
            "Estratégia": "estrategia",
            "Descrição da Dosagem": "dosagem",
            "Descricao da Dosagem": "dosagem",
            "CODIGO": "codigo",
            "Código": "codigo",
            "Peso": "peso",
            # Colunas que você acrescentou na 3ª planilha:
            "CodArea": "cod_area",
            "CodObjetivoSugerido": "cod_objetivo",
            "DescObjetivoSugerida": "desc_objetivo",
            "ScoreAlinhamento": "score_alinhamento",
        }
    )

    # Colunas críticas que precisamos ter
    col_criticas = ["area", "nivel", "estrategia", "codigo"]
    faltando = [c for c in col_criticas if c not in df.columns]
    if faltando:
        raise RuntimeError(
            f"Colunas críticas faltando na aba '{SHEET_NAME}': {faltando}"
        )

    # --------------------------------------------------------
    # Limpeza de linhas
    # --------------------------------------------------------
    # Garante que estrategia/codigo sejam string e tira espaços
    df["estrategia"] = df["estrategia"].astype(str).str.strip()
    df["codigo"] = df["codigo"].astype(str).str.strip()

    # Remove linhas sem estratégia ou código
    df = df[df["estrategia"].ne("") & df["codigo"].ne("")]
    # Remove eventuais linhas de nota técnica
    df = df[~df["area"].astype(str).str.startswith("Nota")]

    linhas_validas = len(df)
    print(
        f"[Projeto21]  - Aba '{SHEET_NAME}': "
        f"{linhas_originais} linhas de origem, {linhas_validas} após filtro."
    )

    if linhas_validas == 0:
        raise RuntimeError("Nenhuma linha válida encontrada na aba 'Geral'.")

    # --------------------------------------------------------
    # Limpa campos numéricos que podem ter NaN/inf
    # --------------------------------------------------------
    for col in ["peso", "OrdemArea", "OrdemNivel", "OrdemEstrategia", "score_alinhamento"]:
        if col in df.columns:
            df[col] = df[col].apply(limpar_numero)

    # --------------------------------------------------------
    # Seleciona as colunas que vão para o JSON
    # --------------------------------------------------------
    # Colunas básicas (iguais ao JSON antigo)
    base_cols = [
        "area",
        "nivel",
        "codigo",
        "estrategia",
        "dosagem",
        "peso",
        "OrdemArea",
        "OrdemNivel",
        "OrdemEstrategia",
    ]

    # Novas colunas de vínculo com o Projeto 21
    extra_cols = [
        "cod_area",          # A01, A02, A03...
        "cod_objetivo",      # A01O01...
        "desc_objetivo",     # descrição do objetivo
        "score_alinhamento", # só para conferência
    ]

    subset_cols = [c for c in base_cols if c in df.columns] + [
        c for c in extra_cols if c in df.columns
    ]

    df = df[subset_cols]

    # --------------------------------------------------------
    # Ordena por área / nível / ordem da estratégia (se existirem)
    # --------------------------------------------------------
    sort_cols = [c for c in ["OrdemArea", "OrdemNivel", "OrdemEstrategia"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols)

    # DataFrame -> lista de dicionários
    records = df.to_dict(orient="records")

    # Faz um último saneamento de NaN/infinito
    for rec in records:
        for key, value in rec.items():
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                rec[key] = None

    # --------------------------------------------------------
    # Grava o JSON
    # --------------------------------------------------------
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, allow_nan=False)

    print(f"[Projeto21] Gerado {len(records)} registros em {OUT_PATH}")


if __name__ == "__main__":
    main()
