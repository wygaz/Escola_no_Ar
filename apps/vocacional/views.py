from __future__ import annotations
from pathlib import Path
import json, random
from apps.contas.models_acessos import tem_acesso
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction
from django.urls import path, include, reverse_lazy   # se usar reverse_lazy
from django.contrib import admin
from django.contrib.auth import views as auth_views    # <- FALTAVA ESTA
from .forms import RespostaForm
from .models import Avaliacao, Resposta, Pergunta, AvaliacaoGuia, Dimensao
from .permissions import require_mentor
from .services import calcular_resultados, classificar_resultados, notificar_resultado
from .forced_choice import build_fc_blocks_top3, score_fc_answers

from .refinamento import (

    get_pass_qids,
    compute_pass_stats,
    should_stop,
    SJT,
    CONTEXT,
    apply_pass3_adjustments,
    probs_from_means,
)
from urllib.parse import quote, urlencode  # se ainda usar em outras views
from django.urls import reverse, NoReverseMatch
from .gating import next_url, next_step
from django.conf import settings
from django.views.decorators.http import require_http_methods, require_POST
from .forms import ConsentimentoForm
from .models_consent import Consentimento
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from collections import defaultdict
from apps.core.permissions import (
    require_produto,
    user_has_produto,
    require_consent,
    require_guia_feedback,
    PROD_VOCACIONAL_75,
    PROD_VOCACIONAL_150,
    PROD_VOCACIONAL_PREMIUM,

)
# -----------------------------------------------------------------------------
# Toggle de produto/entitlement
# - Quando VOCACIONAL_REQUIRE_BONUS=True: exige o Vocacional 75
# - Quando False (padrão em dev): libera com onboarding (Termos+LGPD+Guia)
# -----------------------------------------------------------------------------

def maybe_require_produto(view_func):
    if getattr(settings, "VOCACIONAL_REQUIRE_BONUS", False):
        return require_produto(PROD_VOCACIONAL_75)(view_func)
    return view_func

def _refinement_max_stage(user, request=None) -> int:
    """Retorna o limite de etapas liberadas pelos produtos adicionais."""
    try:
        if user_has_produto(user, PROD_VOCACIONAL_PREMIUM, request=request, bypass_staff=True):
            return 3
        if user_has_produto(user, PROD_VOCACIONAL_150, request=request, bypass_staff=True):
            return 1
    except Exception:
        return 3
    return 0


# -----------------------------------------------------------------------------
# Seed automático (DEV): se não houver perguntas no BD, carrega do JSON do app
# -----------------------------------------------------------------------------

def ensure_vocacional_seeded() -> None:
    """Garante que existam Perguntas ativas no BD.

    Em desenvolvimento/local, é comum esquecer de rodar o comando de import.
    Se não houver nenhuma Pergunta ativa, carregamos automaticamente do JSON
    `apps/vocacional/data/vocacional/vocacional_75.json`.
    """
    if Pergunta.objects.filter(ativo=True).exists():
        return

    json_path = Path(__file__).resolve().parent / "data" / "vocacional" / "vocacional_75.json"
    if not json_path.exists():
        # Sem JSON: não faz nada (a tela mostrará 0/0)
        return

    data = json.loads(json_path.read_text(encoding="utf-8"))
    grupos = data.get("grupos") or []
    dims_info = data.get("dims") or {}

    with transaction.atomic():
        # Dimensões
        dim_objs = {}
        for code, info in dims_info.items():
            nome = (info or {}).get("nome") if isinstance(info, dict) else None
            nome = nome or str(code)

            dim, _ = Dimensao.objects.get_or_create(
                codigo=str(code),
                defaults={
                    "nome": nome,
                    "slug": slugify(str(code))[:120],
                    "peso": (info or {}).get("peso", 1.0) if isinstance(info, dict) else 1.0,
                },
            )
            # mantém nome/peso atualizados
            changed = False
            if dim.nome != nome:
                dim.nome = nome
                changed = True
            if isinstance(info, dict) and "peso" in info and getattr(dim, "peso", None) != info["peso"]:
                dim.peso = info["peso"]
                changed = True
            if changed:
                dim.save()
            dim_objs[str(code)] = dim

        # Perguntas
        ordem = 0
        for g in grupos:
            for item in (g.get("itens") or []):
                texto = str(item.get("texto") or "").strip()
                if not texto:
                    continue

                ordem += 1
                codigo = (item.get("id") or item.get("code") or slugify(texto)[:80]).strip()
                dim_code = str(item.get("dim") or "")
                dim = dim_objs.get(dim_code) if dim_code else None

                Pergunta.objects.update_or_create(
                    codigo=codigo,
                    defaults={
                        "enunciado": texto,
                        "dimensao": dim,
                        "tipo": "likert",
                        "ativo": True,
                        "ordem": ordem,
                        "invert": bool(item.get("invert")) if "invert" in item else False,
                    },
                )


@login_required
def mentor_dashboard(request):
    # por enquanto é só a página base; depois a gente coloca dados/histórico
    return render(request, "vocacional/mentor_home.html")



@login_required
@maybe_require_produto
def avaliacao_gate(request):
    return redirect(next_url(request.user))

# --------------------------- FORM (ÚNICO) ---------------------------

@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def avaliacao_form(request: HttpRequest) -> HttpResponse:
    # Se ainda falta algum pré-requisito, redireciona
    step = next_step(request.user)
    if step is not None:
        return redirect(next_url(request.user))

    # ---------------------------------------------------------
    # O Vocacional Premium libera as etapas adicionais de
    # aprofundamento quando o projeto estiver configurado
    # com mais de um passe.
    # ---------------------------------------------------------
    pass_total_setting = int(getattr(settings, "VOCACIONAL_PASS_TOTAL", 1) or 1)
    if pass_total_setting > 1:
        max_stage = _refinement_max_stage(request.user, request=request)
        if max_stage < 1:
            messages.info(
                request,
                "O Vocacional 150 e o Vocacional Premium liberam as etapas adicionais de aprofundamento. "
                "Para continuar, é necessário liberar um desses produtos."
            )
            return redirect("vocacional:etapas")

    # rascunho mais recente (ou cria)
    avaliacao = (
        Avaliacao.objects
        .filter(usuario=request.user, status="rascunho")
        .order_by("-iniciado_em", "-pk")
        .first()
    )
    if not avaliacao:
        avaliacao = Avaliacao.objects.create(usuario=request.user, status="rascunho")

    # auto-seed (dev/local): se não existir nenhuma pergunta ativa, importa do JSON
    ensure_vocacional_seeded()
    # perguntas ativas
    perguntas_qs = Pergunta.objects.filter(ativo=True).select_related("dimensao")

        # -------- 1) Gera ordem estável na primeira vez --------
    if not getattr(avaliacao, "ordem_ids", None):
        ids = list(perguntas_qs.values_list("id", flat=True))
        seed = (avaliacao.pk or 0) + (request.user.pk or 0)
        rnd = random.Random(seed)
        rnd.shuffle(ids)
        avaliacao.ordem_ids = ",".join(str(i) for i in ids)
        avaliacao.save(update_fields=["ordem_ids"])

    # -------- 2) Aplica ordem --------
    ids_ordenados = _parse_ids(avaliacao.ordem_ids or "")
    perguntas_map = {p.id: p for p in perguntas_qs}
    perguntas = [perguntas_map[i] for i in ids_ordenados if i in perguntas_map]

    # failsafe: se ficou vazio (ids antigos)
    if not perguntas:
        ids = list(perguntas_qs.values_list("id", flat=True))
        random.Random((avaliacao.pk or 0) + (request.user.pk or 0)).shuffle(ids)
        avaliacao.ordem_ids = ",".join(map(str, ids))
        avaliacao.save(update_fields=["ordem_ids"])
        perguntas = [perguntas_map[i] for i in ids if i in perguntas_map]

    # ---------------------------------------------------------
    # Refinamento Top 3 (Passe 1/2/3)
    # - Se VOCACIONAL_PASS_TOTAL == 1, mantém fluxo atual.
    # - Se > 1, mostra apenas o subconjunto de perguntas do passe atual.
    # ---------------------------------------------------------
    pass_total = int(getattr(settings, "VOCACIONAL_PASS_TOTAL", 1) or 1)
    pass_stage = int(getattr(avaliacao, "passe_atual", 1) or 1)
    pass_stage = max(1, min(pass_stage, pass_total))

    max_stage = _refinement_max_stage(request.user, request=request) if pass_total > 1 else 1
    if pass_total > 1 and pass_stage > max_stage:
        # Se a avaliação ficou "adiantada" sem liberação correspondente, volta para o hub.
        avaliacao.passe_atual = max_stage
        avaliacao.save(update_fields=["passe_atual"])
        messages.warning(request, "Este passe ainda não está liberado para sua conta.")
        return redirect("vocacional:etapas")

    pass_qids: list[int] = []
    if pass_total > 1:
        pass_qids = get_pass_qids(avaliacao, pass_stage, perguntas)
        pmap = {p.id: p for p in perguntas}
        perguntas = [pmap[i] for i in pass_qids if i in pmap]

    # -------- 3) POST: salvar respostas + finalizar --------
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
                if p.tipo == "single":
                    r.valor = r.opcao.valor if r.opcao else 0
                r.save()
                salvas += 1

        # autosave AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "salvas": salvas})

        action = request.POST.get("action")  # "save" ou "finish"

        # FINALIZAR
        if action == "finish" or "finalizar" in request.POST:
            # No refinamento, a checagem de completude é por passe.
            if pass_total > 1:
                total_qs = len(pass_qids)
                respondidas = Resposta.objects.filter(
                    avaliacao=avaliacao,
                    pergunta_id__in=pass_qids,
                ).count()
            else:
                total_qs = perguntas_qs.count()
                respondidas = Resposta.objects.filter(avaliacao=avaliacao).count()

            if respondidas < total_qs:
                faltam = total_qs - respondidas
                messages.warning(request, f"Faltam {faltam} questão(ões) para concluir esta etapa.")
                return redirect("vocacional:avaliacao_form")

            # -----------------------------------------------------
            # Refinamento: fecha o passe e decide parar/continuar
            # -----------------------------------------------------
            if pass_total > 1 and pass_stage < pass_total:
                ref = getattr(avaliacao, "ref_data", {}) or {}
                passes = ref.get("passes", {}) or {}

                stats = compute_pass_stats(avaliacao, pass_qids, stage=pass_stage)
                passes[str(pass_stage)] = stats
                ref["passes"] = passes

                stop, reason = should_stop(ref, pass_stage, stats)
                ref.setdefault("stop", {})
                ref["stop"].update({"stage": pass_stage, "stop": bool(stop), "reason": reason})

                # salva ref_data cedo
                avaliacao.ref_data = ref
                avaliacao.save(update_fields=["ref_data"])

                if stop:
                    # Finaliza já no passe atual (com base apenas nas perguntas respondidas até aqui)
                    # Junta todos os qids usados nos passes até agora
                    all_qids = []
                    for k, ids in (ref.get("pass_qids", {}) or {}).items():
                        try:
                            if int(k) <= int(pass_stage):
                                all_qids += [int(x) for x in (ids or [])]
                        except Exception:
                            pass
                    all_qids = sorted(set(all_qids))

                    concluidas_qs = (
                        Avaliacao.objects
                        .filter(usuario=request.user, status="concluida")
                        .order_by("-finalizado_em", "-pk")
                    )

                    if concluidas_qs.count() >= 2 and getattr(avaliacao, "status", "rascunho") != "concluida":
                        calcular_resultados(avaliacao, pergunta_ids=all_qids, finalize=False)
                        messages.info(request, "Limite de 2 avaliações concluídas atingido. Mostrando esta tentativa como pré-visualização.")
                        return redirect("vocacional:resultado", pk=avaliacao.pk)

                    calcular_resultados(avaliacao, pergunta_ids=all_qids, finalize=True)
                    messages.success(request, f"Avaliação concluída no Passe {pass_stage}! ({reason})")
                    return redirect("vocacional:resultado", pk=avaliacao.pk)

                # continua para o próximo passe
                # Se o próximo passe não estiver liberado, finaliza aqui mesmo
                if (pass_stage + 1) > max_stage:
                    ref = getattr(avaliacao, "ref_data", {}) or {}
                    # Junta todos os qids usados nos passes até agora
                    all_qids = []
                    for k, ids in (ref.get("pass_qids", {}) or {}).items():
                        try:
                            if int(k) <= int(pass_stage):
                                all_qids += [int(x) for x in (ids or [])]
                        except Exception:
                            pass
                    all_qids = sorted(set(all_qids or pass_qids))

                    calcular_resultados(avaliacao, pergunta_ids=all_qids, finalize=True)
                    messages.success(
                        request,
                        f"Passe {pass_stage} concluído! Seu resultado foi gerado. "
                        f"Para continuar com o Passe {pass_stage + 1}, é necessário desbloquear esse serviço."
                    )
                    return redirect("vocacional:resultado", pk=avaliacao.pk)

                avaliacao.passe_atual = pass_stage + 1
                avaliacao.save(update_fields=["passe_atual"])
                messages.info(request, f"Passe {pass_stage} concluído. Vamos ao Passe {pass_stage + 1}.")
                if pass_stage + 1 >= 3:
                    return redirect("vocacional:passe3")
                return redirect("vocacional:avaliacao_form")

            concluidas_qs = (
                Avaliacao.objects
                .filter(usuario=request.user, status="concluida")
                .order_by("-finalizado_em", "-pk")
            )

            if (
                concluidas_qs.count() >= 2
                and getattr(avaliacao, "status", "rascunho") != "concluida"
            ):
                calcular_resultados(avaliacao, finalize=False)
                messages.info(
                    request,
                    "Limite de 2 avaliações concluídas atingido. Mostrando o resultado desta tentativa como pré-visualização."
                )
                return redirect("vocacional:resultado", pk=avaliacao.pk)

            calcular_resultados(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.finalizado_em = timezone.now()
            avaliacao.save(update_fields=["status", "finalizado_em"])
            messages.success(request, "Avaliação concluída!")
            return redirect("vocacional:resultado", pk=avaliacao.pk)

        # Se não for finalizar, é salvar normal
        messages.info(request, f"{salvas} respostas salvas.")
        return redirect("vocacional:avaliacao_form")

    # GET — forms + JSON para o front
    itens: list[tuple[Pergunta, RespostaForm]] = []
    for p in perguntas:
        instance = Resposta.objects.filter(avaliacao=avaliacao, pergunta=p).first()
        form = RespostaForm(instance=instance, pergunta=p, prefix=f"p{p.id}")
        itens.append((p, form))

    # respostas já salvas
    resp_qs = Resposta.objects.filter(avaliacao=avaliacao)
    if pass_total > 1 and pass_qids:
        resp_qs = resp_qs.filter(pergunta_id__in=pass_qids)
    resp_map = {r.pergunta_id: r for r in resp_qs}

    # JSON final para o front
    perguntas_json: list[dict] = []
    for p in perguntas:
        texto_p = (
            getattr(p, "texto", None)
            or getattr(p, "pergunta", None)
            or getattr(p, "enunciado", None)
            or getattr(p, "descricao", None)
            or str(p)
        )
        valor = getattr(resp_map.get(p.id), "valor", None)
        perguntas_json.append({
            "id": p.id,
            "texto": texto_p,
            "dimensao": getattr(getattr(p, "dimensao", None), "slug", None),
            "resposta": valor,
        })

    total_perguntas = len(perguntas_json)
    total_respondidas = len([r for r in resp_map.values() if getattr(r, "valor", None) is not None])
    total_pct = int(round((total_respondidas / total_perguntas) * 100)) if total_perguntas else 0

    # ---------------------------------------------------------
    # UI: suporte a múltiplos passes (Passe 1/2/3) sem quebrar o
    # fluxo atual (1 passe). O refinamento completo será ativado
    # quando VOCACIONAL_PASS_TOTAL > 1.
    # ---------------------------------------------------------
    pass_total = int(getattr(settings, "VOCACIONAL_PASS_TOTAL", 1) or 1)
    pass_stage = int(getattr(avaliacao, "passe_atual", 1) or 1)
    pass_stage = max(1, min(pass_stage, pass_total))

    if pass_total > 1 and pass_stage < pass_total:
        finish_label = f"Concluir Passe {pass_stage} (ir ao Passe {pass_stage + 1})"
    else:
        finish_label = "Finalizar"

    ctx = {
        "avaliacao": avaliacao,
        "itens": itens,
        "total": len(itens),

        # JSON que o template injeta no window.quizData
        "perguntas": json.dumps(perguntas_json, ensure_ascii=False),

        # para o cabeçalho do progresso inicial (0/75 etc.)
        "total_perguntas": total_perguntas,
        "total_respondidas": total_respondidas,
        "total_pct": total_pct,

        # UI (opcional): indicador de passe
        "pass_total": pass_total,
        "pass_stage": pass_stage,
        "finish_label": finish_label,

        "hide_global_header": True,
    }

    ctx["ultima_concluida"] = (
        Avaliacao.objects
        .filter(usuario=request.user, status="concluida")
        .order_by("-finalizado_em", "-pk")
        .first()
    )

    return render(request, "vocacional/avaliacao_form.html", ctx)

@require_consent()
@require_guia_feedback
def ofertas_refinamento(request, pk):
    """
    Tela com duas opções quando Top1 e Top2 estão próximos:
    - Vocacional 150 -> libera confrontos diretos
    - Premium (Passes 1-3) -> refinamento completo
    """
    avaliacao = get_object_or_404(Avaliacao, pk=pk, usuario=request.user)

    has_vocacional_150 = user_has_produto(request.user, PROD_VOCACIONAL_150, request=request)
    has_premium = user_has_produto(request.user, PROD_VOCACIONAL_PREMIUM, request=request)

    ctx = {
        "avaliacao": avaliacao,
        "has_vocacional_150": has_vocacional_150,
        "has_premium": has_premium,
        "ref_max_stage": _refinement_max_stage(request.user, request=request),
        "premium_stage_limit": _refinement_max_stage(request.user, request=request),
    }
    return render(request, "vocacional/ofertas_refinamento.html", ctx)

@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
@require_produto(PROD_VOCACIONAL_PREMIUM, redirect_name="vocacional:etapas")
def passe3(request):
    """Passe 3 (anti-frustração): SJT + contexto + mini-experimentos.

    Só aparece se VOCACIONAL_PASS_TOTAL >= 3 e a avaliação atual estiver no passe 3.
    """

    pass_total = int(getattr(settings, "VOCACIONAL_PASS_TOTAL", 1) or 1)
    if pass_total < 3:
        return redirect("vocacional:avaliacao_form")

    avaliacao = (
        Avaliacao.objects
        .filter(usuario=request.user, status="rascunho")
        .order_by("-iniciado_em", "-pk")
        .first()
    )
    if not avaliacao:
        messages.info(request, "Você não tem uma avaliação em andamento.")
        return redirect("vocacional:index")

    if int(getattr(avaliacao, "passe_atual", 1) or 1) < 3:
        return redirect("vocacional:avaliacao_form")

    ref = getattr(avaliacao, "ref_data", {}) or {}
    passes = ref.get("passes", {}) or {}

    base = passes.get("2") or passes.get("1") or {}
    base_means = base.get("means") or {}
    base_probs = base.get("probs") or probs_from_means(base_means)
    top = base.get("top") or [k for k, _v in sorted(base_probs.items(), key=lambda kv: kv[1], reverse=True)][:5]

    if request.method == "POST":
        # coletar respostas
        sjt_answers = {}
        for q in SJT:
            v = (request.POST.get(q["id"]) or "").strip()
            if not v:
                messages.warning(request, "Responda todos os cenários (SJT) antes de continuar.")
                return redirect("vocacional:passe3")
            sjt_answers[q["id"]] = v

        ctx_answers = {}
        for q in CONTEXT:
            v = (request.POST.get(q["id"]) or "").strip()
            if not v:
                messages.warning(request, "Responda todas as perguntas de contexto antes de continuar.")
                return redirect("vocacional:passe3")
            ctx_answers[q["id"]] = v

        # ajustes
        adj_means = apply_pass3_adjustments(base_means, sjt_answers, ctx_answers)
        final_probs = probs_from_means(adj_means)
        final_rank = [k for k, _v in sorted(final_probs.items(), key=lambda kv: kv[1], reverse=True)]

        # guarda no JSON (para exibir no resultado e para auditoria)
        ref.setdefault("passes", {})
        ref["passes"]["3"] = {
            "stage": 3,
            "sjt": sjt_answers,
            "context": ctx_answers,
            "base_top": top,
        }
        ref["final"] = {
            "ranking": final_rank,
            "top3": final_rank[:3],
            "probs": {k: round(float(v), 6) for k, v in final_probs.items()},
        }
        avaliacao.ref_data = ref

        # junta todos os qids já usados (passe1 + passe2)
        all_qids = []
        for k, ids in (ref.get("pass_qids", {}) or {}).items():
            try:
                if int(k) <= 2:
                    all_qids += [int(x) for x in (ids or [])]
            except Exception:
                pass
        all_qids = sorted(set(all_qids))

        concluidas_qs = (
            Avaliacao.objects
            .filter(usuario=request.user, status="concluida")
            .order_by("-finalizado_em", "-pk")
        )

        if concluidas_qs.count() >= 2 and getattr(avaliacao, "status", "rascunho") != "concluida":
            avaliacao.save(update_fields=["ref_data"])
            calcular_resultados(avaliacao, pergunta_ids=all_qids, finalize=False)
            messages.info(request, "Limite de 2 avaliações concluídas atingido. Mostrando esta tentativa como pré-visualização.")
            return redirect("vocacional:resultado", pk=avaliacao.pk)

        avaliacao.save(update_fields=["ref_data"])
        calcular_resultados(avaliacao, pergunta_ids=all_qids, finalize=True)
        messages.success(request, "Passe 3 concluído! Resultado atualizado.")
        return redirect("vocacional:resultado", pk=avaliacao.pk)

    return render(request, "vocacional/passe3.html", {
        "avaliacao": avaliacao,
        "top": top,
        "sjt": SJT,
        "contexto": CONTEXT,
    })



@login_required
def consentimento_check(request):
    form = ConsentimentoForm(initial={
        "nome": request.user.first_name or "",
        "email": request.user.email,
    })
    return render(request, "vocacional/consentimento.html", {"form": form})

@login_required
@require_http_methods(["POST"])
def consentimento_aceitar(request):
    form = ConsentimentoForm(request.POST, initial={"email": request.user.email})
    if not form.is_valid():
        messages.error(request, "Confira os dados informados.")
        return render(request, "vocacional/consentimento.html", {"form": form})

    # atualiza nome do usuário (opcional)
    novo_nome = (form.cleaned_data.get("nome") or "").strip()
    if novo_nome and novo_nome != (request.user.first_name or ""):
        request.user.first_name = novo_nome
        request.user.save(update_fields=["first_name"])

    # marca consentimento OK (ajuste ao seu modelo real)
    # Exemplo 1: usando um model Consentimento
    # Consentimento.objects.update_or_create(
    #     user=request.user, defaults={"aceito": True, "aceito_em": timezone.now()}
    # )

    # Exemplo 2: usando um service helper
    # marcar_consent_ok(request.user)

    messages.success(request, "Consentimento registrado. Obrigado!")
    return redirect(next_url(request.user))

def _avaliacao_stats(user):
    concluidas = Avaliacao.objects.filter(usuario=user, status="concluida").count()
    disponiveis = max(0, 2 - concluidas)
    ultima = (
        Avaliacao.objects
        .filter(usuario=user, status="concluida")
        .order_by("-finalizado_em", "-pk")
        .first()
    )
    return concluidas, disponiveis, ultima
'''
@login_required
@maybe_require_produto
def index(request):
    # sua dashboard
    concluidas, disponiveis, ultima = _avaliacao_stats(request.user)
    return render(request, "vocacional/index.html", {
        "concluidas": concluidas,
        "disponiveis": disponiveis,
        "ultima": ultima,
    })
'''

@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def index(request):
    last_done = (
        Avaliacao.objects
        .filter(usuario=request.user, status="concluida")
        .order_by("-finalizado_em", "-pk")
        .first()
    )
    draft = (
        Avaliacao.objects
        .filter(usuario=request.user, status="rascunho")
        .order_by("-iniciado_em", "-pk")
        .first()
    )
    concluidas = Avaliacao.objects.filter(usuario=request.user, status="concluida").count()

    return render(request, "vocacional/index.html", {
        "last_done": last_done,
        "draft": draft,
        "concluidas": concluidas,
        "limite": 2,
    })


@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def etapas(request):
    u = request.user
    if not (u.is_staff or u.is_superuser or _refinement_max_stage(u, request=request) >= 1):
        messages.info(
            request,
            "As etapas de aprofundamento fazem parte do Vocacional 150 e do Vocacional Premium. "
            "Comece pelo Vocacional 75."
        )
        return redirect("vocacional:avaliacao_gate")  # /vocacional/avaliacao/
    
    """Central de etapas do Vocacional (cards/botões).

    Objetivo: deixar claro o funil (compra → legal → avaliação do guia) e, depois,
    a progressão do teste (Passe 1 / Passe 2 / Passe 3).

    Observação importante:
    - Os Passes 1/2/3 (refinamento) NÃO fazem parte do bônus do Guia; a liberação
      desses passes será tratada separadamente (serviço adicional).
    """

    # Estado do funil (compra/legal/guia)
    step = next_step(request.user)
    next_link = next_url(request.user) if step is not None else None

    try:
        from .gating import bonus_acquired, termos_ok, consent_ok, guia_done
        bonus_ok = (not getattr(settings, "VOCACIONAL_REQUIRE_BONUS", False)) or bonus_acquired(request.user)
        legal_ok = (termos_ok(request.user) and consent_ok(request.user))
        guia_ok = guia_done(request.user)
    except Exception:
        bonus_ok = True
        legal_ok = True
        guia_ok = True

    
    premium_stage_limit = _refinement_max_stage(request.user, request=request)
    ref1_ok = premium_stage_limit >= 1
    ref2_ok = premium_stage_limit >= 2
    ref3_ok = premium_stage_limit >= 3
    max_stage = premium_stage_limit

# Última avaliação em andamento (rascunho)
    draft = (
        Avaliacao.objects
        .filter(usuario=request.user, status="rascunho")
        .order_by("-iniciado_em", "-pk")
        .first()
    )

    pass_total = int(getattr(settings, "VOCACIONAL_PASS_TOTAL", 1) or 1)
    pass_total = max(1, min(pass_total, 3))

    # Métricas simples de progresso por passe (apenas para UI)
    def _seed_order_if_missing(avaliacao: Avaliacao) -> None:
        if getattr(avaliacao, "ordem_ids", ""):
            return
        perguntas_ids = list(Pergunta.objects.filter(ativo=True).values_list("id", flat=True))
        seed = (avaliacao.pk or 0) + (request.user.pk or 0)
        rnd = random.Random(seed)
        rnd.shuffle(perguntas_ids)
        avaliacao.ordem_ids = ",".join(str(i) for i in perguntas_ids)
        avaliacao.save(update_fields=["ordem_ids"])

    def _ordered_perguntas(avaliacao: Avaliacao) -> list[Pergunta]:
        perguntas_qs = Pergunta.objects.filter(ativo=True).select_related("dimensao")
        ids_ordenados = _parse_ids(getattr(avaliacao, "ordem_ids", "") or "")
        pmap = {p.id: p for p in perguntas_qs}
        perguntas = [pmap[i] for i in ids_ordenados if i in pmap]
        if not perguntas:
            # fallback
            perguntas = list(perguntas_qs)
        return perguntas

    def _stage_progress(avaliacao: Avaliacao, stage: int) -> dict:
        perguntas_qs = Pergunta.objects.filter(ativo=True)
        total = perguntas_qs.count()
        qids = None

        if pass_total > 1:
            _seed_order_if_missing(avaliacao)
            perguntas = _ordered_perguntas(avaliacao)
            qids = get_pass_qids(avaliacao, stage, perguntas)
            total = len(qids)

        if not total:
            return {"total": 0, "respondidas": 0, "pct": 0, "qids": qids}

        rq = Resposta.objects.filter(avaliacao=avaliacao)
        if qids:
            rq = rq.filter(pergunta_id__in=qids)
        respondidas = rq.count()

        pct = int(round((respondidas / total) * 100)) if total else 0
        pct = max(0, min(pct, 100))
        return {"total": total, "respondidas": respondidas, "pct": pct, "qids": qids}

    progress = {}
    current_stage = 1
    if draft:
        current_stage = int(getattr(draft, "passe_atual", 1) or 1)
        current_stage = max(1, min(current_stage, pass_total))
        for s in range(1, pass_total + 1):
            progress[str(s)] = _stage_progress(draft, s)

    # Disponibilidade por passe (UX + entitlement de refinamento)
    pass2_available = bool(draft and current_stage >= 2 and pass_total >= 2 and ref2_ok)
    pass3_available = bool(draft and current_stage >= 3 and pass_total >= 3 and ref3_ok)

    # Último resultado
    last_done = (
        Avaliacao.objects
        .filter(usuario=request.user, status="concluida")
        .order_by("-finalizado_em", "-pk")
        .first()
    )

    return render(request, "vocacional/etapas.html", {
        "step": step,
        "next_link": next_link,
        "bonus_ok": bonus_ok,
        "legal_ok": legal_ok,
        "guia_ok": guia_ok,
        "draft": draft,
        "last_done": last_done,
        "pass_total": pass_total,
        "current_stage": current_stage,
        "progress": progress,
        "pass2_available": pass2_available,
        "pass3_available": pass3_available,
        "ref1_ok": ref1_ok,
        "ref2_ok": ref2_ok,
        "ref3_ok": ref3_ok,
        "ref_max_stage": max_stage,

    })




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


# --------------------------- RESULTADO / DEMAIS ---------------------------


@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def resultado(request, pk):
    av = get_object_or_404(Avaliacao, pk=pk, usuario=request.user)

    def nivel_por_media(m: float) -> str:
        # ajuste os cortes se quiser
        if m >= 4.2: return "Muito alto"
        if m >= 3.4: return "Alto"
        if m >= 2.6: return "Médio"
        if m >= 1.8: return "Baixo"
        return "Muito baixo"

    # ---- agrega respostas por dimensão ----
    respostas = (
        Resposta.objects
        .filter(avaliacao=av)
        .select_related("pergunta__dimensao")
    )
    soma, cont, total_qs = {}, {}, 0
    for r in respostas:
        dim = getattr(getattr(r, "pergunta", None), "dimensao", None)
        if not dim:
            continue
        p = getattr(r, "pergunta", None)
        if not p:
            continue

        if getattr(p, "tipo", "likert") == "single":
            v = float(getattr(getattr(r, "opcao", None), "valor", 0) or 0)
        else:
            v = float(getattr(r, "valor", 0) or 0)
            if getattr(p, "invert", False) and v:
                v = 6.0 - v
        soma[dim] = soma.get(dim, 0) + v
        cont[dim] = cont.get(dim, 0) + 1
        total_qs += 1

    # ---- monta e ordena lista completa ----
    resultados_full = []
    for dim, s in soma.items():
        n = cont[dim] or 1
        media = s / n
        resultados_full.append({
            "dimensao": dim,                 # objeto (tem .nome/.slug)
            "dimensao_nome": getattr(dim, "nome", str(dim)),
            "media": round(media, 2),        # 1..5
            "qtd": n,
            "pct": int(round((media / 5.0) * 100)),
            "nivel": nivel_por_media(media),
        })
    resultados_full.sort(key=lambda x: x["media"], reverse=True)

    # Se houver ranking final (Passe 3), reordena de acordo
    ref = getattr(av, "ref_data", {}) or {}
    final_rank = ((ref.get("final") or {}).get("ranking") or [])
    if final_rank:
        pos = {slug: i for i, slug in enumerate(final_rank)}
        resultados_full.sort(key=lambda x: (pos.get(getattr(x["dimensao"], "slug", ""), 999), -x["media"]))

    # ---- Top N (para texto e whatsapp) ----
    TOP_N = 3
    # ---- precisão percebida (confiança) ----
    means_by_slug = {}
    for r in resultados_full:
        dim = r.get("dimensao")
        slug = getattr(dim, "slug", None) or r.get("dimensao_nome")
        if slug:
            means_by_slug[str(slug)] = float(r.get("media") or 0.0)

    probs = probs_from_means(means_by_slug)
    ordered = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)
    top1_slug = ordered[0][0] if ordered else None
    top2_slug = ordered[1][0] if len(ordered) > 1 else None

    top1p = float(probs.get(top1_slug, 0.0)) if top1_slug else 0.0
    gap = float(top1p - float(probs.get(top2_slug, 0.0))) if (top1_slug and top2_slug) else 0.0

    gap_ok = float(getattr(settings, "VOC_RESULT_GAP_OK", 0.12) or 0.12)
    top1_ok = float(getattr(settings, "VOC_RESULT_TOP1_OK", 0.30) or 0.30)

    needs_refine = bool(gap < gap_ok or top1p < top1_ok)

    if gap >= 0.20:
        conf_label = "Alta"
    elif gap >= gap_ok:
        conf_label = "Média"
    else:
        conf_label = "Baixa"

    ref_max_stage = _refinement_max_stage(request.user, request=request)

    confidence = {
        "gap": round(gap, 4),
        "gap_ok": gap_ok,
        "top1p": round(top1p, 4),
        "top1_ok": top1_ok,
        "label": conf_label,
        "needs_refine": needs_refine,
        "top1_slug": top1_slug,
        "top2_slug": top2_slug,
        "ref_max_stage": ref_max_stage,
    }

    top3 = resultados_full[:TOP_N]

    # ---- texto/links auxiliares ----
    resultado_url = request.build_absolute_uri(
        reverse("vocacional:resultado", args=[av.pk])
    )
    top_names = [r["dimensao_nome"] for r in top3] or ["meu resultado"]
    wh_text = f"Meu resultado da Avaliação Vocacional: {', '.join(top_names)}. Veja aqui: {resultado_url}"

    ctx = {
        "avaliacao": av,
        "total_qs": total_qs,

        "ref": ref,
        "stop_info": ref.get("stop") or {},
        "final_info": ref.get("final") or {},

        # sinalização de precisão (Top1 vs Top2)
        "confidence": confidence,

        # AGORA o template renderiza TODOS (toggle esconde/mostra)
        "resultados": resultados_full,

        "resultados_top3": top3,
        "resultados_all": resultados_full,

        "top_n": TOP_N,
        "wh_text": wh_text,
        "resultado_url": resultado_url,

        "hide_global_header": True,
        "hide_global_footer": True,
    }
    return render(request, "vocacional/resultado.html", ctx)



@require_POST
@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def enviar_resultado_email(request: HttpRequest, pk: int) -> HttpResponse:
    avaliacao = get_object_or_404(Avaliacao, pk=pk, usuario=request.user)

    # evita reenvio se já marcado (opcional)
    if getattr(avaliacao, "email_enviado_em", None):
        messages.info(request, f"Este resultado já foi enviado em {avaliacao.email_enviado_em:%d/%m %H:%M}.")
        return redirect("vocacional:resultado", pk=pk)

    try:
        notificar_resultado(request.user, avaliacao)  # sua função existente
    except Exception as e:  # pragma: no cover
        messages.error(request, f"Não foi possível enviar o e-mail agora. ({e})")
    else:
        avaliacao.email_enviado_em = timezone.now()
        avaliacao.save(update_fields=["email_enviado_em"])
        messages.success(request, "Resultado enviado por e-mail.")
    return redirect("vocacional:resultado", pk=pk)

@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def meu_resultado(request):
    av = (Avaliacao.objects
          .filter(usuario=request.user, status="concluida")
          .order_by("-finalizado_em", "-pk")
          .first())
    if not av:
        messages.info(request, "Você ainda não concluiu uma avaliação.")
        return redirect("vocacional:avaliacao_form")
    return redirect("vocacional:resultado", pk=av.pk)

@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def resultado_whatsapp(request: HttpRequest, pk: int) -> HttpResponse:
    av = get_object_or_404(Avaliacao, pk=pk, usuario=request.user)

    # monta o texto como na view resultado (top 3 dimensões + link)
    respostas = (Resposta.objects
                 .filter(avaliacao=av)
                 .select_related("pergunta__dimensao"))
    soma, cont = {}, {}
    for r in respostas:
        dim = getattr(getattr(r, "pergunta", None), "dimensao", None)
        if not dim: 
            continue
        soma[dim] = soma.get(dim, 0) + float(getattr(r, "valor", 0) or 0)
        cont[dim] = cont.get(dim, 0) + 1
    items = []
    for dim, s in soma.items():
        n = cont[dim] or 1
        media = s / n
        items.append((getattr(dim, "nome", str(dim)), media))
    items.sort(key=lambda t: t[1], reverse=True)
    top = ", ".join([t[0] for t in items[:3]]) or "meu resultado"

    url = request.build_absolute_uri(reverse("vocacional:resultado", args=[av.pk]))
    wh_text = f"Meu resultado da Avaliação Vocacional: {top}. Veja aqui: {url}"


    # marca timestamp (idempotente)
    if not getattr(av, "whatsapp_enviado_em", None):
        av.whatsapp_enviado_em = timezone.now()
        av.save(update_fields=["whatsapp_enviado_em"])

    # redireciona ao WhatsApp
    return HttpResponseRedirect("https://api.whatsapp.com/send?" + urlencode({"text": wh_text}))

@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def entrada(request):
    """
    Roteamento inicial do Vocacional.
    - Se tiver refinamento liberado (Pass 1/2/3) -> /vocacional/etapas/
    - Senão -> Bônus 75 (avaliacao_gate)
    """
    u = request.user

    has_ref = _refinement_max_stage(u, request=request) >= 1

    if has_ref:
        return redirect("vocacional:etapas")

    # No seu urls.py o nome é "avaliacao_gate" (rota /vocacional/avaliacao/)
    return redirect("vocacional:avaliacao_gate")


# -----------------------------------------------------------------------------
# Confrontos diretos (Forced-Choice) para desempatar Top 3
# -----------------------------------------------------------------------------

@login_required
@maybe_require_produto
@require_consent()
@require_guia_feedback
def comparacoes_top3(request):
    """Refinamento final por confrontos diretos (A/B/C) entre o Top 3 atual.

    Importante:
    - Este módulo é pensado para a fase de refinamento (Pass 3), como "desempate"
      quando Top1 vs Top2 estão muito próximos.
    - Por enquanto, mantemos como um refinamento adicional (não altera o resultado
      oficial salvo em Resultado); ele serve para comparar abordagens e melhorar UX.
    """
    ensure_vocacional_seeded()

    # Avaliação alvo: para A/B/C, usamos a avaliação mais recente CONCLUÍDA.
    avaliacao = (
        Avaliacao.objects
        .filter(usuario=request.user, status="concluida")
        .order_by("-iniciado_em", "-pk")
        .first()
    )
    if not avaliacao:
        messages.info(request, "Você ainda não concluiu uma avaliação. Faça o Vocacional 75 primeiro.")
        return redirect("vocacional:avaliacao_gate")

    # Liberação do A/B/C:
    # - Premium (Passe 3) OU
    # - Vocacional 150
    has_vocacional_150 = user_has_produto(request.user, PROD_VOCACIONAL_150, request=request)
    ref_max = _refinement_max_stage(request.user, request=request)
    has_premium_fc = (ref_max >= 3) or (request.user.is_staff or request.user.is_superuser)

    if not (has_vocacional_150 or has_premium_fc):
        messages.info(
            request,
            "Para usar Confrontos Diretos (A/B/C), você pode adquirir o Vocacional 150 "
            "ou desbloquear o Premium (Passe 3)."
        )
        # Se existir a tela de ofertas, manda para lá; senão volta ao resultado.
        try:
            return redirect("vocacional:ofertas_refinamento", pk=avaliacao.pk)
        except Exception:
            return redirect("vocacional:resultado", pk=avaliacao.pk)


    # Top 3 base (usa respostas já existentes)
    answered_qids = list(
        Resposta.objects
        .filter(avaliacao=avaliacao)
        .values_list("pergunta_id", flat=True)
        .distinct()
    )
    stats = compute_pass_stats(avaliacao, answered_qids, stage=int(getattr(avaliacao, "passe_atual", 1) or 1))
    top3 = list((stats.get("top") or [])[:3])

    if len(top3) < 3:
        messages.warning(request, "Ainda não há dados suficientes para formar um Top 3. Responda mais perguntas primeiro.")
        return redirect("vocacional:etapas")

    ref = (avaliacao.ref_data or {})
    fc = (ref.get("fc_top3") or {})

    # Reset explícito (para testes / ajustes de banco)
    if request.GET.get("reset") == "1":
        ref.pop("fc_top3", None)
        fc = {}
        avaliacao.ref_data = ref
        avaliacao.save(update_fields=["ref_data"])
        messages.info(request, "Confrontos reiniciados.")
        return redirect("vocacional:comparacoes_top3")

    def _missing_text(blocks_list: list) -> bool:
        for b in (blocks_list or []):
            for k in ("A", "B", "C"):
                it = (b or {}).get(k) or {}
                if not (it.get("text") or "").strip():
                    return True
        return False

    # Inicializa/reconstrói blocos se:
    # - ainda não existir
    # - top3 mudou
    # - existe bloco com texto vazio (dados antigos)
    if (not fc.get("blocks")) or (fc.get("top3") != top3) or _missing_text(fc.get("blocks") or []):
        raw_blocks = build_fc_blocks_top3(avaliacao, top3)

        def _get_pergunta_from_qid(raw_qid):
            """
            raw_qid pode vir como:
            - pk numérico (id)
            - codigo (string estável)
            """
            s = str(raw_qid).strip() if raw_qid is not None else ""
            if not s:
                return None
            if s.isdigit():
                try:
                    return Pergunta.objects.only("id", "codigo", "enunciado").get(pk=int(s))
                except Pergunta.DoesNotExist:
                    return None
            try:
                return Pergunta.objects.only("id", "codigo", "enunciado").get(codigo=s)
            except Pergunta.DoesNotExist:
                return None

        blocks = []
        for b in raw_blocks:
            bb = {}
            for k, v in b.items():
                p = _get_pergunta_from_qid(v.qid)
                if p:
                    bb[k] = {
                        "qid": p.pk,                         # mantém compatível com int(...) depois
                        "codigo": p.codigo,                  # opcional, mas útil pra debug
                        "dim": v.dim_slug,
                        "text": (p.enunciado or "").strip(), # <<< enunciado real
                    }
                else:
                    # fallback: não deixa vazio, e força o rebuild depois
                    bb[k] = {
                        "qid": str(v.qid),
                        "codigo": str(v.qid),
                        "dim": v.dim_slug,
                        "text": "(sem enunciado)",
                    }
            blocks.append(bb)

        fc = {
            "top3": top3,
            "blocks": blocks,
            "answers": [],
            "done": False,
        }

        ref["fc_top3"] = fc
        avaliacao.ref_data = ref
        avaliacao.save(update_fields=["ref_data"])
        ref["fc_top3"] = fc
        avaliacao.ref_data = ref
        avaliacao.save(update_fields=["ref_data"])

    blocks = fc.get("blocks") or []
    answers = list(fc.get("answers") or [])
    idx = len(answers)

    # POST: registra escolha e avança
    if request.method == "POST":
        pick = (request.POST.get("pick") or "").upper().strip()
        if pick not in ("A", "B", "C"):
            messages.error(request, "Selecione uma opção (A, B ou C).")
            return redirect("vocacional:comparacoes_top3")

        answers.append(pick)
        fc["answers"] = answers
        # Finaliza?
        if len(answers) >= len(blocks):
            fc["done"] = True

        ref["fc_top3"] = fc
        avaliacao.ref_data = ref
        avaliacao.save(update_fields=["ref_data"])
        return redirect("vocacional:comparacoes_top3")

    # Render
    if not blocks:
        messages.warning(request, "Não há perguntas suficientes para montar confrontos diretos para esse Top 3.")
        return redirect("vocacional:etapas")

    # Se concluído, mostra resumo comparativo
    if fc.get("done"):
        # Reconstrói FCItem para score
        from .forced_choice import FCItem
        b2 = []
        for b in blocks:
            bb = {}
            for k in ("A", "B", "C"):
                it = b.get(k) or {}
                bb[k] = FCItem(qid=int(it.get("qid")), dim_slug=str(it.get("dim")), text=str(it.get("text")))
            b2.append(bb)
        scores = score_fc_answers(b2, answers)
        # ranking final (fc)
        ordered_fc = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

        # Aplica o desempate ao ranking final (sem mexer nos valores/médias):
        # - Mantém a ordem base do modelo (softmax) para o restante
        # - Reordena apenas o Top3 conforme o forced-choice
        try:
            base_rank = [slug for slug, _p in sorted((stats.get("probs") or {}).items(), key=lambda kv: kv[1], reverse=True)]
        except Exception:
            base_rank = []
        if not base_rank:
            base_rank = list(top3)

        fc_rank = [slug for slug, _pts in ordered_fc if slug in top3]

        # monta ranking final: fc_rank primeiro, depois o resto da base_rank
        final_rank = []
        for s in fc_rank:
            if s not in final_rank:
                final_rank.append(s)
        for s in base_rank:
            if s not in final_rank:
                final_rank.append(s)

        ref = (avaliacao.ref_data or {})
        ref.setdefault("final", {})
        ref["final"]["ranking"] = final_rank
        ref["final"]["source"] = "fc_top3"
        # guarda também resumo do FC
        ref.setdefault("fc_top3", {})
        ref["fc_top3"]["scores"] = dict(scores)
        ref["fc_top3"]["final_rank_top3"] = fc_rank
        avaliacao.ref_data = ref
        avaliacao.save(update_fields=["ref_data"])

        # nomes bonitos para exibir
        slug_to_name = {d.slug: d.nome for d in Dimensao.objects.all()}
        top3_names = [slug_to_name.get(s, s) for s in top3]
        ordered_fc_names = [(slug_to_name.get(slug, slug), pts) for slug, pts in ordered_fc]

        return render(
            request,
            "vocacional/comparacoes_top3.html",
            {
                "mode": "done",
                "avaliacao": avaliacao,
                "top3": top3,
                "top3_names": top3_names,
                "scores": scores,
                "ordered_fc": ordered_fc_names,
                "n_blocks": len(blocks),
            },
        )

    # Ainda em andamento: mostra próximo bloco
    block = blocks[idx]

    # Corrige blocos antigos (text vazio) resolvendo pelo identificador salvo em "qid".
    # Regra:
    # - se "qid" for numérico -> tenta pk
    # - senão -> tenta Pergunta.codigo (identificador externo estável)
    # Se não resolver, marca para rebuild e recria os confrontos via reset=1.
    updated = False
    needs_rebuild = False

    # fallback para nome bonito (se não achar pergunta)
    slug_to_name = {d.slug: d.nome for d in Dimensao.objects.all()}

    def _resolve_enunciado(qid_value):
        s = str(qid_value).strip() if qid_value is not None else ""
        if not s:
            return None

        # 1) tenta pk numérico
        if s.isdigit():
            try:
                return (
                    Pergunta.objects
                    .values_list("enunciado", flat=True)
                    .get(pk=int(s)) or ""
                ).strip()
            except Pergunta.DoesNotExist:
                pass

        # 2) tenta codigo (correto no seu model)
        try:
            return (
                Pergunta.objects
                .values_list("enunciado", flat=True)
                .get(codigo=s) or ""
            ).strip()
        except Pergunta.DoesNotExist:
            return None

    for k in ("A", "B", "C"):
        it = (block or {}).get(k) or {}
        txt = (it.get("text") or "").strip()
        if txt:
            continue

        resolved = _resolve_enunciado(it.get("qid"))
        if resolved:
            it["text"] = resolved
            block[k] = it
            updated = True
        else:
            # Não conseguiu resolver -> confronto está stale (reseed/reimport)
            # Coloca fallback visível e força rebuild
            dim_slug = (it.get("dim") or "").strip()
            it["text"] = slug_to_name.get(dim_slug, dim_slug) or "(sem enunciado)"
            block[k] = it
            needs_rebuild = True

    if needs_rebuild:
        messages.warning(request, "Confrontos estavam desatualizados. Recriando perguntas…")
        url = reverse("vocacional:comparacoes_top3") + "?reset=1"
        return HttpResponseRedirect(url)

    if updated:
        # salva bloco corrigido
        ref = (avaliacao.ref_data or {})
        fc = (ref.get("fc_top3") or {})
        bl = fc.get("blocks") or []
        if idx < len(bl):
            bl[idx] = block
            fc["blocks"] = bl
            ref["fc_top3"] = fc
            avaliacao.ref_data = ref
            avaliacao.save(update_fields=["ref_data"])

    progress = {
        "idx": idx + 1,
        "total": len(blocks),
        "pct": int(round((idx / max(len(blocks), 1)) * 100)),
    }

    return render(
        request,
        "vocacional/comparacoes_top3.html",
        {
            "mode": "run",
            "avaliacao": avaliacao,
            "top3": top3,
            "progress": progress,
            "fc_block": block,
        },
    )
