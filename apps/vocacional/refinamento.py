from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from django.conf import settings

from .models import Avaliacao, Pergunta, Resposta


# -----------------------------------------------------------------------------
# Métricas (Gap + cobertura) e seleção de perguntas para Passe 1/2
# -----------------------------------------------------------------------------


def _softmax(scores: Dict[str, float], tau: float = 0.8) -> Dict[str, float]:
    if not scores:
        return {}
    tau = float(tau or 0.8)
    tau = max(0.05, min(tau, 5.0))

    m = max(scores.values())
    exps = {k: math.exp((v - m) / tau) for k, v in scores.items()}
    s = sum(exps.values()) or 1.0
    return {k: float(v / s) for k, v in exps.items()}


def _sorted_keys(d: Dict[str, float]) -> List[str]:
    return [k for k, _ in sorted(d.items(), key=lambda kv: kv[1], reverse=True)]


def _rng_for(avaliacao: Avaliacao) -> random.Random:
    seed = int((avaliacao.pk or 0) * 1000003 + (avaliacao.usuario_id or 0))
    return random.Random(seed)


def get_pass_qids(avaliacao: Avaliacao, stage: int, perguntas_qs) -> List[int]:
    """Retorna (e persiste) a lista de pergunta_ids usada no passe `stage`."""
    ref = getattr(avaliacao, "ref_data", {}) or {}
    pass_qids = ref.get("pass_qids", {}) or {}

    key = str(int(stage))
    if key in pass_qids and pass_qids[key]:
        return [int(x) for x in pass_qids[key]]

    used = set()
    for k, ids in pass_qids.items():
        try:
            used |= {int(x) for x in (ids or [])}
        except Exception:
            pass

    stage = int(stage)
    if stage == 1:
        qids = select_pass1_balanced(avaliacao, perguntas_qs, used)
    else:
        # passa 2: foca nas top-k dimensões do passe 1
        prev = (ref.get("passes", {}) or {}).get("1", {})
        top = prev.get("top") or []
        qids = select_pass2_focus(avaliacao, perguntas_qs, used, top)

    pass_qids[key] = qids
    ref["pass_qids"] = pass_qids
    avaliacao.ref_data = ref
    avaliacao.save(update_fields=["ref_data"])
    return qids


def select_pass1_balanced(avaliacao: Avaliacao, perguntas_qs, used_ids: set[int]) -> List[int]:
    per_dim = int(getattr(settings, "VOC_REF_PASS1_PER_DIM", 2) or 2)
    per_dim = max(1, min(per_dim, 10))

    # Ordenação estável: usa a ordem_ids global (se existir) para garantir repetibilidade
    ordem = []
    if getattr(avaliacao, "ordem_ids", ""):
        try:
            ordem = [int(x) for x in str(avaliacao.ordem_ids).split(",") if x.strip().isdigit()]
        except Exception:
            ordem = []

    # Map id->pos para ordenar sempre igual
    pos = {pid: i for i, pid in enumerate(ordem)}

    qids: List[int] = []
    dims = list({p.dimensao_id for p in perguntas_qs})
    dims.sort()

    for dim_id in dims:
        cand = [p.id for p in perguntas_qs if p.dimensao_id == dim_id and p.id not in used_ids]
        cand.sort(key=lambda pid: pos.get(pid, 10**9))
        qids += cand[:per_dim]

    # shuffle leve, mas estável, para evitar blocos por dimensão
    rnd = _rng_for(avaliacao)
    rnd.shuffle(qids)
    return qids


def select_pass2_focus(avaliacao: Avaliacao, perguntas_qs, used_ids: set[int], top_dims_slugs: List[str]) -> List[int]:
    per_dim = int(getattr(settings, "VOC_REF_PASS2_PER_DIM", 3) or 3)
    per_dim = max(1, min(per_dim, 20))
    topk = int(getattr(settings, "VOC_REF_PASS2_TOPK", 5) or 5)

    # slug->dim_id
    slug_to_dim_id = {}
    for p in perguntas_qs:
        if p.dimensao and p.dimensao.slug:
            slug_to_dim_id[p.dimensao.slug] = p.dimensao_id

    chosen_dim_ids = []
    for slug in (top_dims_slugs or [])[:topk]:
        if slug in slug_to_dim_id:
            chosen_dim_ids.append(slug_to_dim_id[slug])

    # fallback: se não tiver top, pega primeiras dimensões
    if not chosen_dim_ids:
        chosen_dim_ids = sorted({p.dimensao_id for p in perguntas_qs})[:topk]

    # mesma ordenação estável do passe 1
    ordem = []
    if getattr(avaliacao, "ordem_ids", ""):
        try:
            ordem = [int(x) for x in str(avaliacao.ordem_ids).split(",") if x.strip().isdigit()]
        except Exception:
            ordem = []
    pos = {pid: i for i, pid in enumerate(ordem)}

    qids: List[int] = []
    for dim_id in chosen_dim_ids:
        cand = [p.id for p in perguntas_qs if p.dimensao_id == dim_id and p.id not in used_ids]
        cand.sort(key=lambda pid: pos.get(pid, 10**9))
        qids += cand[:per_dim]

    rnd = _rng_for(avaliacao)
    rnd.shuffle(qids)
    return qids


# -----------------------------------------------------------------------------
# Cálculo de score e regra de parada
# -----------------------------------------------------------------------------


def compute_scores(avaliacao: Avaliacao, pergunta_ids: List[int]) -> Tuple[Dict[str, float], Dict[str, int]]:
    """Retorna (mean por slug) e (contagem por slug) usando apenas pergunta_ids."""
    if not pergunta_ids:
        return {}, {}

    qs = (
        Resposta.objects
        .filter(avaliacao=avaliacao, pergunta_id__in=pergunta_ids)
        .select_related("pergunta__dimensao")
    )

    soma: Dict[str, float] = {}
    cont: Dict[str, int] = {}

    for r in qs:
        p = r.pergunta
        d = getattr(p, "dimensao", None)
        slug = getattr(d, "slug", None) or str(getattr(d, "id", ""))

        if p.tipo == "likert":
            v = int(r.valor or 0)
            if getattr(p, "invert", False) and v:
                v = 6 - v
        else:
            v = int(getattr(getattr(r, "opcao", None), "valor", 0) or 0)

        if slug not in soma:
            soma[slug] = 0.0
            cont[slug] = 0
        soma[slug] += float(v)
        cont[slug] += 1

    means = {k: (soma[k] / max(cont[k], 1)) for k in soma.keys()}
    return means, cont


def compute_pass_stats(avaliacao: Avaliacao, pergunta_ids: List[int], stage: int) -> dict:
    tau = float(getattr(settings, "VOC_REF_SOFTMAX_TAU", 0.8) or 0.8)

    means, counts = compute_scores(avaliacao, pergunta_ids)
    probs = _softmax(means, tau=tau)
    ordered = _sorted_keys(probs)

    top = ordered[:10]
    gap = 0.0
    top1p = 0.0
    if len(ordered) >= 2:
        gap = float(probs.get(ordered[0], 0.0) - probs.get(ordered[1], 0.0))
        top1p = float(probs.get(ordered[0], 0.0))
    elif len(ordered) == 1:
        top1p = float(probs.get(ordered[0], 0.0))

    # Cobertura: quantas dimensões têm pelo menos 1 item respondido
    covered = sum(1 for k, c in (counts or {}).items() if (c or 0) > 0)
    total_dims = len(probs) if probs else 0
    coverage_ratio = (covered / total_dims) if total_dims else 0.0

    return {
        "stage": int(stage),
        "qids": [int(x) for x in pergunta_ids],
        "means": {k: round(float(v), 4) for k, v in means.items()},
        "counts": counts,
        "probs": {k: round(float(v), 6) for k, v in probs.items()},
        "top": top,
        "gap": round(float(gap), 6),
        "top1p": round(float(top1p), 6),
        "coverage_ratio": round(float(coverage_ratio), 6),
    }


def should_stop(ref_data: dict, stage: int, stats: dict) -> Tuple[bool, str]:
    """Decide parada usando GAP + prob do Top1 + estabilidade do Top3 (no P2)."""
    stage = int(stage)
    gap = float(stats.get("gap") or 0.0)
    top1p = float(stats.get("top1p") or 0.0)

    if stage == 1:
        gap_thr = float(getattr(settings, "VOC_REF_GAP_STOP_P1", 0.20) or 0.20)
        top1_thr = float(getattr(settings, "VOC_REF_TOP1_MIN_P1", 0.35) or 0.35)
        if gap >= gap_thr and top1p >= top1_thr:
            return True, f"STOP_P1(gap>={gap_thr}, top1>={top1_thr})"
        return False, "CONT_P1"

    if stage == 2:
        gap_thr = float(getattr(settings, "VOC_REF_GAP_STOP_P2", 0.15) or 0.15)
        top1_thr = float(getattr(settings, "VOC_REF_TOP1_MIN_P2", 0.32) or 0.32)

        passes = (ref_data.get("passes") or {})
        prev = passes.get("1", {})
        prev_top3 = list((prev.get("top") or [])[:3])
        cur_top3 = list((stats.get("top") or [])[:3])

        stable = (set(prev_top3) == set(cur_top3)) if (prev_top3 and cur_top3) else False
        if gap >= gap_thr and top1p >= top1_thr and stable:
            return True, f"STOP_P2(gap>={gap_thr}, top1>={top1_thr}, stable_top3)"

        return False, "CONT_P2"

    return False, "CONT"


# -----------------------------------------------------------------------------
# Passe 3 (SJT + contexto + mini-experimentos)
# -----------------------------------------------------------------------------


SJT = [
    {
        "id": "sjt1",
        "titulo": "Conflito de prioridades",
        "texto": "Num projeto em grupo, surge um conflito entre prazo e qualidade. O que você faz primeiro?",
        "opcoes": [
            ("a", "Reorganizo o plano e distribuo tarefas, garantindo entrega no prazo.", ["gestao"]),
            ("b", "Reviso os requisitos e defino um padrão mínimo de qualidade antes de seguir.", ["analise"]),
            ("c", "Prototipo rápido e testo com usuários para decidir o melhor caminho.", ["criatividade", "pessoas"]),
            ("d", "Aprofundo o problema técnico e proponho uma solução mais robusta.", ["tecnico"]),
        ],
    },
    {
        "id": "sjt2",
        "titulo": "Aprender algo novo",
        "texto": "Você precisa aprender uma habilidade nova rapidamente. Qual estratégia combina mais com você?",
        "opcoes": [
            ("a", "Vou direto para um projeto prático e aprendo fazendo.", ["tecnico", "criatividade"]),
            ("b", "Sigo um plano estruturado, com metas e checklist.", ["gestao"]),
            ("c", "Procuro alguém para orientar/mentorar e pratico com feedback.", ["pessoas"]),
            ("d", "Leio, pesquiso, comparo fontes e só depois aplico.", ["analise"]),
        ],
    },
    {
        "id": "sjt3",
        "titulo": "Trabalho ideal",
        "texto": "Qual descrição de trabalho te dá mais energia?",
        "opcoes": [
            ("a", "Resolver problemas complexos com lógica e precisão.", ["analise", "tecnico"]),
            ("b", "Criar coisas novas e comunicar ideias.", ["criatividade"]),
            ("c", "Cuidar de pessoas, ensinar ou orientar.", ["pessoas"]),
            ("d", "Organizar processos e liderar para resultados.", ["gestao"]),
        ],
    },
]


# Mapeamento de tags genéricas -> slugs de dimensões (AJUSTE AQUI se quiser)
# A ideia é você ir refinando conforme o seu leque real de dimensões.
TAG_TO_DIM_SLUGS = {
    "tecnico": ["tecnico", "exatas", "dev", "dev_ia", "engenharia"],
    "analise": ["analise", "pesquisa", "dados", "direito", "economia"],
    "criatividade": ["criatividade", "design", "artes", "comunicacao"],
    "pessoas": ["pessoas", "saude", "educacao", "social"],
    "gestao": ["gestao", "negocios", "empreendedorismo"],
}


CONTEXT = [
    {
        "id": "ctx1",
        "titulo": "Ambiente",
        "texto": "Você prefere ambientes mais previsíveis ou mais dinâmicos?",
        "opcoes": [
            ("a", "Previsíveis (rotina, processos claros)", ["gestao", "analise"]),
            ("b", "Dinâmicos (mudanças, improviso, variedade)", ["criatividade", "pessoas"]),
        ],
    },
    {
        "id": "ctx2",
        "titulo": "Foco principal",
        "texto": "No dia a dia, você tende a se motivar mais por…",
        "opcoes": [
            ("a", "Dados, lógica e solução técnica", ["tecnico", "analise"]),
            ("b", "Pessoas, impacto e comunicação", ["pessoas", "criatividade"]),
        ],
    },
]


def apply_pass3_adjustments(base_means: Dict[str, float], sjt_answers: Dict[str, str], ctx_answers: Dict[str, str]) -> Dict[str, float]:
    """Aplica pequenos ajustes nos meios (logits simples) com base em SJT + contexto."""
    means = dict(base_means or {})

    def bump(tags: List[str], delta: float = 0.25):
        if not tags:
            return
        for t in tags:
            for slug in TAG_TO_DIM_SLUGS.get(t, []):
                if slug in means:
                    means[slug] = float(means.get(slug, 0.0)) + float(delta)

    # SJT
    sjt_defs = {q["id"]: q for q in SJT}
    for qid, choice in (sjt_answers or {}).items():
        q = sjt_defs.get(qid)
        if not q:
            continue
        for key, _label, tags in q["opcoes"]:
            if key == choice:
                bump(tags, delta=0.30)

    # Contexto
    ctx_defs = {q["id"]: q for q in CONTEXT}
    for qid, choice in (ctx_answers or {}).items():
        q = ctx_defs.get(qid)
        if not q:
            continue
        for key, _label, tags in q["opcoes"]:
            if key == choice:
                bump(tags, delta=0.20)

    return means


def probs_from_means(means: Dict[str, float]) -> Dict[str, float]:
    tau = float(getattr(settings, "VOC_REF_SOFTMAX_TAU", 0.8) or 0.8)
    return _softmax(means or {}, tau=tau)
