# apps/vocacional/views.py 28/10/25 - 14:41
# --------------------------------------------------------------
# Principais ajustes desta revisão
# - Corrige fluxo de POST para diferenciar "Salvar" (autosave/XHR) de "Finalizar".
# - Garante persistência e aplicação da ordem das questões via campo CSV (ordem_ids).
# - Suporta autosave por fetch/XHR (retorna JSON quando solicitado) e fallback com mensagens.
# - Remove código inalcançável; organiza imports; adiciona geração de wh_text (Top 3) no resultado.
# - Mantém compatibilidade com RespostaForm(pergunta=..., prefix=...).

from __future__ import annotations

import random
import json
from urllib.parse import quote  # (mantido se você usar em outras views)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RespostaForm
from .models import Avaliacao, Resposta, Pergunta, AvaliacaoGuia
from .permissions import require_mentor, require_consent, require_guia_feedback
from .services import (
    calcular_resultados,
    notificar_resultado,
    classificar_resultados,
)

# --------------------------- util ---------------------------

def _parse_ids(s: str) -> list[int]:
    """Aceita CSV ("1,2,3") ou JSON ("[1,2,3]") e devolve lista de ints."""
    s = (s or "").strip()
    if not s:
        return []
    if s.startswith("["):
        try:
            return [int(x) for x in json.loads(s)]
        except Exception:
            pass
    return [int(x) for x in s.split(",") if x.strip().isdigit()]


# --------------------------- views ---------------------------

@require_consent
@require_guia_feedback
def avaliacao_form(request: HttpRequest) -> HttpResponse:
    """Form misto (sem cabeçalhos de área), 1 pergunta por vez no template.

    - Persiste a ordem das questões por usuário (campo Avaliacao.ordem_ids).
    - Suporta autosave via fetch (XMLHttpRequest) e também via submit padrão.
    - "Finalizar" valida se todas foram respondidas e redireciona ao resultado.
    """
    avaliacao, _ = Avaliacao.objects.get_or_create(usuario=request.user, status="rascunho")

    # perguntas ativas
    perguntas_qs = Pergunta.objects.filter(ativo=True).select_related("dimensao")

    # gera ordem apenas na 1ª vez (e salva como CSV para facilitar)
    if not getattr(avaliacao, "ordem_ids", None):
        ids = list(perguntas_qs.values_list("id", flat=True))
        seed = (avaliacao.pk or 0) + (request.user.pk or 0)
        rnd = random.Random(seed)
        rnd.shuffle(ids)
        avaliacao.ordem_ids = ",".join(str(i) for i in ids)
        avaliacao.save(update_fields=["ordem_ids"])

    # aplica ordem persistida
    ids_ordenados = _parse_ids(avaliacao.ordem_ids)
    perguntas_map = {p.id: p for p in perguntas_qs}
    perguntas = [perguntas_map[i] for i in ids_ordenados if i in perguntas_map]

    if request.method == "POST":
        salvas = 0
        for p in perguntas:
            prefix = f"p{p.id}"
            instance = Resposta.objects.filter(avaliacao=avaliacao, pergunta=p).first()
            form = RespostaForm(request.POST, instance=instance, pergunta=p, prefix=prefix)
            if form.is_valid():
                r = form.save(commit=False)
                r.avaliacao = avaliacao
                r.pergunta = p
                if p.tipo == "single":  # normaliza single-choice copiando valor da opção
                    r.valor = r.opcao.valor if r.opcao else 0
                r.save()
                salvas += 1

        # Se é autosave AJAX, responde JSON e não redireciona
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "salvas": salvas})

        # Se clicou em Finalizar, valide 100% respondidas e siga para o resultado
        if "finalizar" in request.POST:
            total_qs = perguntas_qs.count()
            respondidas = Resposta.objects.filter(avaliacao=avaliacao).count()
            if respondidas < total_qs:
                faltam = total_qs - respondidas
                messages.warning(
                    request,
                    f"Faltam {faltam} questão(ões) para finalizar. Complete todas antes de concluir.",
                )
                return redirect("vocacional:avaliacao_form")

            calcular_resultados(avaliacao)
            messages.success(request, "Avaliação concluída!")
            return redirect("vocacional:resultado", pk=avaliacao.pk)

        # Submit normal (botão Salvar)
        messages.info(request, f"{salvas} respostas salvas.")
        return redirect("vocacional:avaliacao_form")

    # GET — monta itens para o template
    itens: list[tuple[Pergunta, RespostaForm]] = []
    for p in perguntas:
        instance = Resposta.objects.filter(avaliacao=avaliacao, pergunta=p).first()
        form = RespostaForm(instance=instance, pergunta=p, prefix=f"p{p.id}")
        itens.append((p, form))

    ctx = {"avaliacao": avaliacao, "itens": itens, "total": len(itens)}
    return render(request, "vocacional/avaliacao_form.html", ctx)


@require_mentor
def mentor_dashboard(request: HttpRequest) -> HttpResponse:
    qs = Avaliacao.objects.select_related("usuario").order_by("-iniciado_em")[:100]
    return render(request, "vocacional/mentor_dashboard.html", {"avaliacoes": qs})


@login_required
def index(request: HttpRequest) -> HttpResponse:
    ultima = Avaliacao.objects.filter(usuario=request.user).order_by("-iniciado_em").first()
    precisa_guia = not AvaliacaoGuia.objects.filter(
        user=request.user, status="concluida", aceite_termos=True
    ).exists()
    return render(
        request,
        "vocacional/index.html",
        {"ultima": ultima, "precisa_guia": precisa_guia},
    )


@require_consent
@require_guia_feedback
def resultado(request: HttpRequest, pk: int) -> HttpResponse:
    avaliacao = get_object_or_404(Avaliacao, pk=pk, usuario=request.user)

    # classificar_resultados deve devolver ao menos "resultados" em ctx
    ctx = classificar_resultados(avaliacao, delta=3)
    ctx["avaliacao"] = avaliacao

    # Texto para compartilhar (Top 3)
    resultados = list(ctx.get("resultados", []))
    linhas = []
    for r in resultados[:3]:
        nome = getattr(r.dimensao, "nome", getattr(r, "dimensao_nome", "Geral"))
        linhas.append(f"- {nome}: {getattr(r, 'percentual', 0):.2f}% (nível {getattr(r, 'nivel', '-')})")
    ctx["wh_text"] = (
        "Meu resultado no Teste Vocacional:\n\n" + "\n".join(linhas) + "\n\n@EscolaNoAr"
        if linhas
        else ""
    )

    return render(request, "vocacional/resultado.html", ctx)


@login_required
def enviar_resultado_email(request: HttpRequest, pk: int) -> HttpResponse:
    avaliacao = get_object_or_404(Avaliacao, pk=pk, usuario=request.user)
    try:
        notificar_resultado(request.user, avaliacao)
        messages.success(request, "Resultado enviado por e-mail.")
    except Exception as e:  # pragma: no cover (logging opcional)
        messages.error(request, f"Não foi possível enviar o e-mail agora. ({e})")
    return redirect("vocacional:resultado", pk=pk)
