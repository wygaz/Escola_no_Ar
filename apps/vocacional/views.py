from __future__ import annotations
import json, random
from apps.contas.models_acessos import tem_acesso
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import path, include, reverse_lazy   # se usar reverse_lazy
from django.contrib import admin
from django.contrib.auth import views as auth_views    # <- FALTAVA ESTA
from .forms import RespostaForm
from .models import Avaliacao, Resposta, Pergunta, AvaliacaoGuia
from .permissions import require_mentor
from .services import calcular_resultados, classificar_resultados, notificar_resultado
from urllib.parse import quote, urlencode  # se ainda usar em outras views
from django.urls import reverse, NoReverseMatch
from .gating import next_url, next_step
from django.conf import settings
from django.views.decorators.http import require_http_methods
from .forms import ConsentimentoForm
from .models_consent import Consentimento
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from collections import defaultdict
from django.views.decorators.http import require_POST
from apps.core.permissions import require_produto, PROD_VOCACIONAL, require_consent, require_guia_feedback


@login_required
def mentor_dashboard(request):
    # por enquanto é só a página base; depois a gente coloca dados/histórico
    return render(request, "vocacional/mentor_home.html")



@login_required
@require_produto(PROD_VOCACIONAL)
def avaliacao_gate(request):
    return redirect(next_url(request.user))

# --------------------------- FORM (ÚNICO) ---------------------------

@login_required
@require_produto(PROD_VOCACIONAL)
@require_consent()
@require_guia_feedback
def avaliacao_form(request: HttpRequest) -> HttpResponse:
    # Se ainda falta algum pré-requisito, redireciona
    step = next_step(request.user)
    if step is not None:
        return redirect(next_url(request.user))

    # rascunho mais recente (ou cria)
    avaliacao = (
        Avaliacao.objects
        .filter(usuario=request.user, status="rascunho")
        .order_by("-iniciado_em", "-pk")
        .first()
    )
    if not avaliacao:
        avaliacao = Avaliacao.objects.create(usuario=request.user, status="rascunho")

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
        print("POST action=", request.POST.get("action"))

        # FINALIZAR
        if action == "finish" or "finalizar" in request.POST:
            total_qs = perguntas_qs.count()
            respondidas = Resposta.objects.filter(avaliacao=avaliacao).count()
            if respondidas < total_qs:
                faltam = total_qs - respondidas
                messages.warning(
                    request,
                    f"Faltam {faltam} questão(ões) para finalizar. Complete todas antes de concluir.",
                )
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
                calcular_resultados(avaliacao)
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
    resp_map = {
        r.pergunta_id: r
        for r in Resposta.objects.filter(avaliacao=avaliacao)
    }

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

    debug_on = bool(
        settings.DEBUG
        or request.GET.get("debug") == "1"
        or getattr(request.user, "is_staff", False)
    )

    total_perguntas = len(perguntas_json)
    total_respondidas = len([r for r in resp_map.values() if getattr(r, "valor", None) is not None])
    total_pct = int(round((total_respondidas / total_perguntas) * 100)) if total_perguntas else 0

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

        "hide_global_header": True,
    }

    ctx["ultima_concluida"] = (
        Avaliacao.objects
        .filter(usuario=request.user, status="concluida")
        .order_by("-finalizado_em", "-pk")
        .first()
    )

    if debug_on:
        ctx.update({
            "debug_on": True,
            "debug_perguntas": [
                {
                    "pos": i,
                    "id": it["id"],
                    "dimensao": it["dimensao"],
                    "texto": (it["texto"] or "")[:120],
                    "valor": it["resposta"],
                }
                for i, it in enumerate(perguntas_json, start=1)
            ],
            "debug_counts": {
                "total_qs": total_perguntas,
                "ordenadas": total_perguntas,
                "respondidas": total_respondidas,
            },
        })

    return render(request, "vocacional/avaliacao_form.html", ctx)



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
@require_produto(PROD_VOCACIONAL)
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
@require_produto(PROD_VOCACIONAL)
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
@require_produto(PROD_VOCACIONAL)
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
        v = float(getattr(r, "valor", 0) or 0)
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

    # ---- Top N (para texto e whatsapp) ----
    TOP_N = 3
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
@require_produto(PROD_VOCACIONAL)
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
@require_produto(PROD_VOCACIONAL)
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
@require_produto(PROD_VOCACIONAL)
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


