from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Dict, List, Sequence

from django.conf import settings

from .models import Pergunta, Avaliacao


@dataclass
class FCItem:
    qid: int
    dim_slug: str
    text: str


def _rng_for(avaliacao: Avaliacao) -> random.Random:
    seed = int((avaliacao.pk or 0) * 1000003 + (avaliacao.usuario_id or 0) * 9176)
    return random.Random(seed)


# Stopwords curtas (PT-BR) só para heurística de "excludência" no A/B/C.
# Não é NLP pesado; é só para evitar perguntas genéricas demais.
_STOP = {
    "a","o","os","as","um","uma","uns","umas","de","do","da","dos","das","e","ou","em","no","na","nos","nas",
    "por","para","com","sem","que","se","eu","vc","você","me","minha","meu","meus","minhas","seu","sua","seus","suas",
    "é","ser","estar","ter","faz","fazer","sou","estou","tenho","muito","muita","mais","menos","bem","mal","isso","isto",
    "aquilo","como","quando","onde","porque","porquê","pra","já","não","sim",
}

_word_re = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


def _tokens(text: str) -> set[str]:
    if not text:
        return set()
    words = [w.lower() for w in _word_re.findall(text)]
    return {w for w in words if len(w) >= 4 and w not in _STOP}


def _text_for(p: Pergunta) -> str:
    # Campo canônico é enunciado, mas deixamos fallback por segurança.
    return (getattr(p, "enunciado", None) or getattr(p, "texto", None) or getattr(p, "pergunta", None) or str(p) or "").strip()


def _pool_for(slug: str) -> List[FCItem]:
    qs = (
        Pergunta.objects
        .filter(ativo=True, tipo="likert", dimensao__slug=slug)
        .only("id", "enunciado", "dimensao_id")
        .select_related("dimensao")
    )
    out: List[FCItem] = []
    for p in qs:
        qid_value = (p.codigo or str(p.id))
        text_value = (p.enunciado or "").strip()
        out.append(FCItem(qid=qid_value, dim_slug=slug, text=text_value))
    return out


def _rank_discriminative(pools: Dict[str, List[FCItem]]) -> Dict[str, List[FCItem]]:
    """Ordena cada pool por uma heurística simples de "excludência".

    Ideia:
    - preferir perguntas com vocabulário mais específico daquela dimensão,
      evitando as extremamente genéricas que poderiam servir para qualquer área.
    - Não é psicometria; é um filtro prático para melhorar o A/B/C.
    """
    all_tokens = {slug: set().union(*(_tokens(it.text) for it in items)) for slug, items in pools.items()}
    ranked: Dict[str, List[FCItem]] = {}

    for slug, items in pools.items():
        other = set()
        for s2, toks in all_tokens.items():
            if s2 != slug:
                other |= toks

        scored = []
        for it in items:
            toks = _tokens(it.text)
            uniq = len(toks - other)
            spec = len(toks)
            # pesos leves: unicidade > especificidade > tamanho do texto
            score = (uniq * 3.0) + (spec * 1.0) + (min(len(it.text), 180) / 180.0)
            scored.append((score, it.qid, it))

        scored.sort(key=lambda x: (-x[0], x[1]))
        ranked[slug] = [it for _, __, it in scored]

    return ranked


def build_fc_blocks_top3(avaliacao: Avaliacao, top_slugs: Sequence[str]) -> List[Dict[str, FCItem]]:
    """Gera blocos forced-choice (A/B/C) para os 3 slugs informados.

    Cada bloco contém 3 enunciados (um de cada dimensão) e o usuário escolhe
    "o que mais tem a ver comigo". É uma forma simples (e engajadora)
    de desempatar Top1 vs Top2 quando está muito próximo.

    O gerador privilegia itens mais "excludentes" (menos genéricos).
    """

    top = list(top_slugs or [])[:3]
    if len(top) < 3:
        return []

    pools = {s: _pool_for(s) for s in top}
    min_len = min((len(v) for v in pools.values()), default=0)
    if min_len <= 0:
        return []

    wanted = int(getattr(settings, "VOC_FC_BLOCKS_TOP3", 5) or 5)
    wanted = max(3, min(wanted, 40))
    n_blocks = min(wanted, min_len)

    ranked = _rank_discriminative(pools)

    for s in top:
      items = ranked.get(s) or []

    chosen = {s: ranked[s][:n_blocks] for s in top}

    rnd = _rng_for(avaliacao)

    blocks: List[Dict[str, FCItem]] = []
    for i in range(n_blocks):
        trio = [chosen[top[0]][i], chosen[top[1]][i], chosen[top[2]][i]]
        rnd.shuffle(trio)  # reduz viés de posição A/B/C
        blocks.append({"A": trio[0], "B": trio[1], "C": trio[2]})

    return blocks


def score_fc_answers(blocks: List[Dict[str, FCItem]], answers: List[str]) -> Dict[str, int]:
    scores: Dict[str, int] = {}
    for i, pick in enumerate(answers or []):
        if i >= len(blocks):
            break
        pick = (pick or "").upper()
        if pick not in ("A", "B", "C"):
            continue
        item = blocks[i].get(pick)
        if not item:
            continue
        scores[item.dim_slug] = int(scores.get(item.dim_slug, 0) + 1)
    return scores
