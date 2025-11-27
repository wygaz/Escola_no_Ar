import json
import math
from pathlib import Path

import pandas as pd


def limpar_numero(valor):
    """Converte para número normal; se for NaN/inf ou vazio, vira None."""
    if valor is None:
        return None
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return None

    if math.isnan(v) or math.isinf(v):
        return None

    return int(v) if v.is_integer() else v


# Caminhos – ajuste se estiver em outra pasta
EXCEL_PATH = Path(
    r"C:\Users\Wanderley\Apps\escola_no_ar_site\Projeto21\Projeto21_com_frequencia_de_todas_areas_com_manual.xlsx"
)

OUT_PATH = Path(
    r"C:\Users\Wanderley\Apps\escola_no_ar_site\apps\projeto21\static\projeto21\data\estrategias.json"
)

# Abas que realmente têm estratégias
SHEETS = ["Familia", "Escola", "Amigos", "Comunidade", "Igreja", "Eu mesmo"]

frames = []

for sheet in SHEETS:
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet)

    # Renomeia para nomes simples
    df = df.rename(
        columns={
            "Area": "area",
            "Nivel": "nivel",
            "Estrategia": "estrategia",
            "Descrição da Dosagem": "dosagem",
            "CODIGO": "codigo",
            "Peso": "peso",
        }
    )

    # Remove linhas claramente técnicas / notas
    df = df[df["estrategia"].notna() & df["codigo"].notna()]
    df = df[~df["area"].astype(str).str.startswith("Nota")]

    # Garante colunas numéricas limpas
    for col in ["peso", "OrdemArea", "OrdemNivel", "OrdemEstrategia"]:
        if col in df.columns:
            df[col] = df[col].apply(limpar_numero)

    subset_cols = [
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
    frames.append(df[subset_cols])

# Junta tudo
all_df = pd.concat(frames, ignore_index=True)

# Ordena por área / nível / ordem da estratégia
all_df = all_df.sort_values(["OrdemArea", "OrdemNivel", "OrdemEstrategia"])

records = all_df.to_dict(orient="records")

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUT_PATH.open("w", encoding="utf-8") as f:
    # allow_nan=False impede que escape algum NaN escondido
    json.dump(records, f, ensure_ascii=False, indent=2, allow_nan=False)

print(f"Gerado {len(records)} registros em {OUT_PATH}")
