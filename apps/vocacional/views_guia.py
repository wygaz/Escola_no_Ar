from __future__ import annotations

import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from apps.core.permissions import require_legal
from .gating import next_url
from .models import AvaliacaoGuia, QuestaoGuia, RespostaGuia


def _is_answered(q: QuestaoGuia, r: RespostaGuia | None) -> bool:
    if not r:
        return False
    if q.tipo in {"likert", "nota10", "nps"}:
        return r.valor is not None
    if q.tipo == "multi":
        return bool(r.multi)
    # radio/texto/aberta
    return bool((r.texto or "").strip())


def _get_leitura_val(questoes: list[QuestaoGuia], respostas_by_qid: dict[int, RespostaGuia]) -> str:
    q1 = next((q for q in questoes if q.codigo == "LEITURA_PERC"), None)
    if not q1:
        return ""
    r = respostas_by_qid.get(q1.id)
    return (r.texto or "").strip() if r else ""


def _visible_questoes(questoes: list[QuestaoGuia], leitura_val: str) -> list[QuestaoGuia]:
    # Q4 só aparece se leitura != 76-100%
    out: list[QuestaoGuia] = []
    for q in questoes:
        if q.codigo == "LEITURA_MOTIVO_NAO_CONCLUIU" and leitura_val == "76-100%":
            continue
        out.append(q)
    return out


def _first_missing_index(questoes_visiveis: list[QuestaoGuia], respostas: dict[int, RespostaGuia]) -> int | None:
    for idx, q in enumerate(questoes_visiveis):
        r = respostas.get(q.id)
        if q.obrigatoria and not _is_answered(q, r):
            return idx
    return None


def _save_answer(avaliacao: AvaliacaoGuia, q: QuestaoGuia, post) -> None:
    """Salva (ou remove) a resposta de uma questão, sem criar 'lixos' vazios."""
    if q.tipo in {"likert", "nota10", "nps"}:
        raw = (post.get(f"q{q.id}") or "").strip()
        if not raw:
            RespostaGuia.objects.filter(avaliacao=avaliacao, questao=q).delete()
            return
        try:
            v = int(raw)
        except (TypeError, ValueError):
            RespostaGuia.objects.filter(avaliacao=avaliacao, questao=q).delete()
            return
        RespostaGuia.objects.update_or_create(
            avaliacao=avaliacao,
            questao=q,
            # texto é NOT NULL no banco: manter string vazia
            defaults={"valor": v, "texto": "", "multi": []},
        )
        return

    if q.tipo == "radio":
        raw = (post.get(f"q{q.id}") or "").strip()
        if not raw:
            RespostaGuia.objects.filter(avaliacao=avaliacao, questao=q).delete()
            return
        RespostaGuia.objects.update_or_create(
            avaliacao=avaliacao,
            questao=q,
            defaults={"texto": raw, "valor": None, "multi": []},
        )
        return

    if q.tipo == "multi":
        vals = post.getlist(f"q{q.id}") if hasattr(post, "getlist") else []
        vals = [v for v in vals if str(v).strip()]
        if not vals:
            RespostaGuia.objects.filter(avaliacao=avaliacao, questao=q).delete()
            return
        RespostaGuia.objects.update_or_create(
            avaliacao=avaliacao,
            questao=q,
            defaults={"multi": vals, "texto": ", ".join(vals), "valor": None},
        )
        return

    # texto/aberta
    raw = (post.get(f"q{q.id}_t") or "").strip()
    if not raw:
        RespostaGuia.objects.filter(avaliacao=avaliacao, questao=q).delete()
        return
    RespostaGuia.objects.update_or_create(
        avaliacao=avaliacao,
        questao=q,
        defaults={"texto": raw, "valor": None, "multi": []},
    )


@login_required
@require_legal
@require_http_methods(["GET", "POST"])
def guia_avaliacao(request):
    """Avaliação do Guia (stepper no frontend; validação no backend)."""
    avaliacao, _ = AvaliacaoGuia.objects.get_or_create(user=request.user)

    questoes = list(QuestaoGuia.objects.filter(ativo=True).order_by("ordem"))
    respostas_qs = RespostaGuia.objects.filter(avaliacao=avaliacao).select_related("questao")
    respostas_by_qid: dict[int, RespostaGuia] = {r.questao_id: r for r in respostas_qs}

    leitura_val = _get_leitura_val(questoes, respostas_by_qid)
    questoes_visiveis = _visible_questoes(questoes, leitura_val)

    force_start = False

    if request.method == "POST":
        # salva todas as respostas que vieram no POST
        # (o stepper mantém tudo no DOM; ao enviar, vem o formulário completo)
        for q in questoes:
            _save_answer(avaliacao, q, request.POST)

        # recarrega respostas após salvar
        respostas_qs = RespostaGuia.objects.filter(avaliacao=avaliacao).select_related("questao")
        respostas_by_qid = {r.questao_id: r for r in respostas_qs}

        leitura_val = _get_leitura_val(questoes, respostas_by_qid)
        questoes_visiveis = _visible_questoes(questoes, leitura_val)

        # limpeza: se Q4 não se aplica, remove rascunho antigo
        if leitura_val == "76-100%":
            RespostaGuia.objects.filter(
                avaliacao=avaliacao,
                questao__codigo="LEITURA_MOTIVO_NAO_CONCLUIU",
            ).delete()

        missing_idx = _first_missing_index(questoes_visiveis, respostas_by_qid)
        if missing_idx is not None:
            messages.error(request, "Responda todas as perguntas obrigatórias para enviar.")
            start_step = missing_idx
            force_start = True
        else:
            # conclui
            avaliacao.status = "concluida"
            avaliacao.save(update_fields=["status"])

            messages.success(request, "Avaliação registrada. Volte ao Portal para escolher o próximo passo.")

            # decisão: sempre volta ao Portal (evita o usuário “se perder”)
            return redirect("portal")

    # GET (ou POST com erros): calcula o step inicial
    missing_idx = _first_missing_index(questoes_visiveis, respostas_by_qid)
    if missing_idx is None:
        # se tudo preenchido, cai no FINAL (índice = len(questoes_visiveis))
        start_step = len(questoes_visiveis)
    else:
        start_step = missing_idx

    # Contexto de respostas simples para o template
    respostas_ctx: dict[int, Any] = {}
    for r in respostas_by_qid.values():
        respostas_ctx[r.questao_id] = {
            "valor": r.valor,
            "texto": r.texto,
            "multi": r.multi or [],
        }

    return render(
        request,
        "vocacional/guia_avaliacao.html",
        {
            "avaliacao": avaliacao,
            "questoes": questoes,
            "respostas": respostas_ctx,
            "start_step": start_step,
            "force_start": 1 if force_start else 0,
            "leitura_val": leitura_val,
        },
    )


@login_required
@require_legal
@require_POST
def guia_autosave(request):
    """Salva rascunho por questão (para retomar onde parou)."""
    avaliacao, _ = AvaliacaoGuia.objects.get_or_create(user=request.user)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "json_invalid"}, status=400)

    qid = int(payload.get("qid") or 0)
    if not qid:
        return JsonResponse({"ok": False, "error": "qid_required"}, status=400)

    try:
        q = QuestaoGuia.objects.get(id=qid, ativo=True)
    except QuestaoGuia.DoesNotExist:
        return JsonResponse({"ok": False, "error": "questao_not_found"}, status=404)

    tipo = payload.get("tipo") or q.tipo
    value = payload.get("value")

    # Normaliza para “post-like”
    class _P:
        def __init__(self, d): self.d = d
        def get(self, k, default=None): return self.d.get(k, default)
        def getlist(self, k): 
            v = self.d.get(k, [])
            return v if isinstance(v, list) else [v]

    d = {}
    if tipo in {"likert", "nota10", "nps", "radio"}:
        d[f"q{qid}"] = "" if value is None else str(value)
    elif tipo == "multi":
        d[f"q{qid}"] = value if isinstance(value, list) else []
    else:
        d[f"q{qid}_t"] = "" if value is None else str(value)

    _save_answer(avaliacao, q, _P(d))

    return JsonResponse({"ok": True})
