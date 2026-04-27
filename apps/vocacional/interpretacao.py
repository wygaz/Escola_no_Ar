from __future__ import annotations

from dataclasses import dataclass
from typing import Any


EXTERNAL_FACTORS = [
    "rotina de trabalho",
    "retorno financeiro",
    "perspectiva de mercado",
    "impacto de IA e automação",
    "custo de formação",
    "viabilidade regional",
]


@dataclass(frozen=True)
class InterpretationInput:
    user_name: str
    top1_nome: str
    top2_nome: str
    top3_nome: str
    gap_12: float
    gap_13: float
    stable_top3: bool = False
    round_count: int = 0
    max_round_reached: bool = False
    refinement_stopped_early: bool = False
    adjacency_profile: str = "moderadamente_proximas"
    confidence_band: str = "moderada"
    non_recommended_areas: tuple[str, ...] = ()


def classify_interpretation_scenario(data: InterpretationInput) -> str:
    if data.max_round_reached or (data.confidence_band == "aberta" and data.round_count >= 1):
        return "encaminhar_mentoria"

    if data.refinement_stopped_early or (data.stable_top3 and data.confidence_band in {"alta", "moderada"}):
        return "resultado_estabilizado"

    if data.confidence_band == "alta" and data.gap_12 >= 0.12 and data.gap_13 >= 0.18:
        return "perfil_bem_definido"

    if data.confidence_band == "moderada" and data.adjacency_profile in {"muito_proximas", "moderadamente_proximas"}:
        return "nucleo_consistente_areas_proximas"

    return "perfil_ainda_aberto"


def build_interpretation_payload(data: InterpretationInput) -> dict[str, Any]:
    scenario = classify_interpretation_scenario(data)

    payload = {
        "scenario": scenario,
        "title": "",
        "summary": "",
        "core_message": "",
        "caution": "",
        "method_note": (
            "Este resultado não determina seu destino. Ele oferece uma avaliação criteriosa, "
            "baseada nas respostas que você forneceu e dependente da sinceridade e da proximidade "
            "dessas respostas com sua realidade pessoal."
        ),
        "next_step": "",
        "show_external_factors": False,
        "external_factors": [],
        "show_mentoring_offer": False,
        "non_recommended_note": "",
    }

    if scenario == "perfil_bem_definido":
        payload.update(
            title="Perfil mais definido",
            summary=f"{data.user_name}, sua avaliação apresentou uma direção mais nítida neste momento.",
            core_message=(
                f"A área que mais se destacou foi {data.top1_nome}. "
                f"{data.top2_nome} e {data.top3_nome} aparecem como afinidades próximas, "
                "mas com menor força."
            ),
            caution=(
                "Isso não significa determinação absoluta, mas uma indicação consistente do seu perfil atual."
            ),
            next_step="Vale aprofundar a observação prática dessa área e comparar com experiências reais.",
        )
    elif scenario == "nucleo_consistente_areas_proximas":
        payload.update(
            title="Áreas próximas com núcleo consistente",
            summary=f"{data.user_name}, seu resultado mostrou uma combinação relevante entre áreas próximas.",
            core_message=(
                f"{data.top1_nome} apareceu em destaque, mas {data.top2_nome} e {data.top3_nome} "
                "também permaneceram próximas porque exigem habilidades e interesses relacionados."
            ),
            caution=(
                "Isso não reduz o valor do resultado. Pode indicar um núcleo vocacional consistente "
                "com mais de uma expressão possível."
            ),
            next_step=(
                "Compare contexto, rotina, ambiente profissional e exigências práticas dessas áreas "
                "antes de concluir sua escolha."
            ),
            show_external_factors=True,
            external_factors=EXTERNAL_FACTORS,
        )
    elif scenario == "resultado_estabilizado":
        payload.update(
            title="Resultado estabilizado após refinamento",
            summary=f"{data.user_name}, após o refinamento, seu perfil ficou mais definido.",
            core_message=(
                f"{data.top1_nome} manteve a posição principal com base mais consistente. "
                f"{data.top2_nome} e {data.top3_nome} continuam relevantes, mas agora com melhor separação interpretativa."
            ),
            caution=(
                "Isso fortalece a leitura do resultado atual e ajuda a reduzir a insegurança da escolha."
            ),
            next_step="A próxima etapa é comparar esse destaque com experiências e decisões concretas.",
        )
    elif scenario == "encaminhar_mentoria":
        payload.update(
            title="Decisão pede aprofundamento orientado",
            summary=(
                f"{data.user_name}, seu resultado revelou áreas próximas que merecem uma análise mais cuidadosa."
            ),
            core_message=(
                "Isso não invalida a avaliação. Em muitos casos, indica um conjunto real de interesses "
                "e habilidades que ainda pede comparação prática mais madura."
            ),
            caution=(
                "Quando isso acontece, insistir apenas em novas perguntas pode não ser o melhor caminho. "
                "Uma leitura orientada pode trazer mais segurança."
            ),
            next_step=(
                "Considere comparar fatores externos de decisão e, se necessário, avançar para uma "
                "mentoria vocacional."
            ),
            show_external_factors=True,
            external_factors=EXTERNAL_FACTORS,
            show_mentoring_offer=True,
        )
    else:
        payload.update(
            title="Perfil ainda aberto",
            summary=(
                f"{data.user_name}, sua avaliação reuniu possibilidades relevantes, mas ainda sem uma separação forte entre elas."
            ),
            core_message=(
                "Isso sugere um perfil mais aberto neste momento, com interesses distribuídos entre áreas "
                "que merecem observação mais aprofundada."
            ),
            caution=(
                "Esse resultado continua sendo útil, porque mostra onde estão suas inclinações mais prováveis. "
                "Ao mesmo tempo, indica que a definição ainda não está suficientemente fechada."
            ),
            next_step=(
                "Vale complementar essa leitura com refinamento, comparação prática entre áreas e observação do seu contexto real."
            ),
            show_external_factors=True,
            external_factors=EXTERNAL_FACTORS,
        )

    if data.non_recommended_areas:
        areas = ", ".join(data.non_recommended_areas)
        payload["non_recommended_note"] = (
            f"Algumas áreas apareceram com pouca sustentação no seu perfil atual, como {areas}. "
            "Isso recomenda prudência antes de tomar uma decisão baseada nelas."
        )

    return payload
