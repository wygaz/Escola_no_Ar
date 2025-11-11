from __future__ import annotations
import random
import json
from apps.contas.models_acessos import tem_acesso
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import path, include, reverse_lazy   # se usar reverse_lazy
from django.contrib import admin
from django.contrib.auth import views as auth_views    # <- FALTAVA ESTA
from .forms import RespostaForm
from .models import Avaliacao, Resposta, Pergunta, AvaliacaoGuia

from .permissions import require_mentor, require_consent, require_guia_feedback
from .services import calcular_resultados, classificar_resultados, notificar_resultado
from urllib.parse import quote  # se ainda usar em outras views
from django.urls import reverse, NoReverseMatch
from .gating import next_url, next_step, gating_state
from django.conf import settings
from django.views.decorators.http import require_http_methods
from .forms import ConsentimentoForm
from .models_consent import Consentimento
# ou: from .services_consent import marcar_consent_ok

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

@login_required
def index(request):
    # sua dashboard
    concluidas, disponiveis, ultima = _avaliacao_stats(request.user)
    return render(request, "vocacional/index.html", {
        "concluidas": concluidas,
        "disponiveis": disponiveis,
        "ultima": ultima,
    })

@login_required
def avaliacao_gate(request):
    step = next_step(request.user)  # retorna "consent", "guia" ou None

    if step == "consent":
        return redirect("vocacional:consentimento_check")
    if step == "guia":
        return redirect("vocacional:guia_avaliacao")
    if step == "limit":
        return redirect("vocacional:index")  # mostra cards de upgrade

    # Se não há pré-requisito, vai direto ao form
    return redirect("vocacional:avaliacao_form")

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


# --------------------------- FORM (ÚNICO) ---------------------------

@login_required
@require_consent
@require_guia_feedback
def avaliacao_form(request: HttpRequest) -> HttpResponse:
    # Se ainda falta algum pré-requisito, redireciona
    step = next_step(request.user)
    if step is not None:
        return redirect(next_url(request.user))

    # ------- a partir daqui, é o seu corpo original do form -------
    from django.conf import settings

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
    messages.info(request, f"[DEBUG] perguntas_qs={perguntas_qs.count()}")

    # gera ordem na 1ª vez
    if not getattr(avaliacao, "ordem_ids", None):
        ids = list(perguntas_qs.values_list("id", flat=True))
        seed = (avaliacao.pk or 0) + (request.user.pk or 0)
        rnd = random.Random(seed)
        rnd.shuffle(ids)
        avaliacao.ordem_ids = ",".join(str(i) for i in ids)
        avaliacao.save(update_fields=["ordem_ids"])

    # aplica ordem
    ids_ordenados = _parse_ids(avaliacao.ordem_ids)
    perguntas_map = {p.id: p for p in perguntas_qs}
    perguntas = [perguntas_map[i] for i in ids_ordenados if i in perguntas_map]

    # failsafe: se ficou vazio (ids antigos)
    if not perguntas:
        ids = list(perguntas_qs.values_list("id", flat=True))
        random.Random((avaliacao.pk or 0) + (request.user.pk or 0)).shuffle(ids)
        avaliacao.ordem_ids = ",".join(map(str, ids))
        avaliacao.save(update_fields=["ordem_ids"])
        perguntas = [perguntas_map[i] for i in ids if i in perguntas_map]

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

        # FINALIZAR →  (avaliacao_form view) === valida 100%, respeita limite 2 e conclui.
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

            # dentro de avaliacao_form(), no if "finalizar" in request.POST:
            concluidas_qs = (
                Avaliacao.objects
                .filter(usuario=request.user, status="concluida")
                .order_by("-finalizado_em", "-pk")
            )

            if concluidas_qs.count() >= 2 and getattr(avaliacao, "status", "rascunho") != "concluida":
                calcular_resultados(avaliacao)  # calcula, mas NÃO muda status
                messages.info(
                    request,
                    "Limite de 2 avaliações concluídas atingido. Mostrando o resultado desta tentativa como pré-visualização."
                )
                return redirect("vocacional:resultado", pk=avaliacao.pk)

            # fluxo normal quando não atingiu o limite
            calcular_resultados(avaliacao)
            avaliacao.status = "concluida"
            avaliacao.finalizado_em = timezone.now()
            avaliacao.save(update_fields=["status", "finalizado_em"])
            messages.success(request, "Avaliação concluída!")
            return redirect("vocacional:resultado", pk=avaliacao.pk)

    # GET — forms + JSON para o front
    itens: list[tuple[Pergunta, RespostaForm]] = []
    for p in perguntas:
        instance = Resposta.objects.filter(avaliacao=avaliacao, pergunta=p).first()
        form = RespostaForm(instance=instance, pergunta=p, prefix=f"p{p.id}")
        itens.append((p, form))

    resp_map = {r.pergunta_id: r for r in Resposta.objects.filter(avaliacao=avaliacao)}
    perguntas_json = []
    for p in perguntas:
        texto_p = getattr(p, "texto", getattr(p, "enunciado", getattr(p, "descricao", str(p))))
        valor = getattr(resp_map.get(p.id), "valor", None)
        perguntas_json.append({"id": p.id, "texto": texto_p, "resposta": valor})

    debug_on = bool(settings.DEBUG or request.GET.get("debug") == "1" or getattr(request.user, "is_staff", False))
    debug_perguntas = []
    if debug_on:
        for pos, p in enumerate(perguntas, start=1):
            r = resp_map.get(p.id)
            texto_p = getattr(p, "texto", getattr(p, "enunciado", getattr(p, "descricao", str(p))))
            debug_perguntas.append({
                "pos": pos,
                "id": p.id,
                "dimensao": getattr(p.dimensao, "nome", ""),
                "texto": texto_p[:120],
                "ativa": getattr(p, "ativo", True),
                "valor": getattr(r, "valor", None),
            })

    ctx = {
        "avaliacao": avaliacao,
        "itens": itens,
        "total": len(itens),
        "perguntas": json.dumps(perguntas_json, ensure_ascii=False),
    }
    ctx["debug_counts"] = {
    "total_qs": perguntas_qs.count(),
    "ordenadas": len(perguntas),
    }
    
    ctx.update({
    "perguntas_json": ctx["perguntas"],   # compat com versões antigas do template/JS
    "total_qs": len(perguntas),           # fallback server-side para mostrar contagem
    })
    
    if debug_on:
        ctx.update({
            "debug_on": True,
            "debug_perguntas": debug_perguntas,
            "debug_ordem_ids": avaliacao.ordem_ids,
            "debug_counts": {
                "total_qs": perguntas_qs.count(),
                "ordenadas": len(perguntas),
                "respondidas": len(resp_map),
            },
        })

    return render(request, "vocacional/avaliacao_form.html", ctx)



def mentor_dashboard(request: HttpRequest) -> HttpResponse:
    qs = Avaliacao.objects.select_related("usuario").order_by("-iniciado_em")[:100]
    return render(request, "vocacional/mentor_dashboard.html", {"avaliacoes": qs})

# --------------------------- RESULTADO / DEMAIS ---------------------------

@login_required
@require_consent
@require_guia_feedback
def resultado(request: HttpRequest, pk: int) -> HttpResponse:
    avaliacao = get_object_or_404(Avaliacao, pk=pk, usuario=request.user)

    # recálculo failsafe
    ctx = classificar_resultados(avaliacao, delta=3)
    
    if not ctx.get("resultados"):
        calcular_resultados(avaliacao)
        if getattr(avaliacao, "status", "") != "concluida":
            avaliacao.status = "concluida"
            avaliacao.finalizado_em = timezone.now()
            avaliacao.save(update_fields=["status", "finalizado_em"])
        ctx = classificar_resultados(avaliacao, delta=3)

    ctx["avaliacao"] = avaliacao

    # Top 3 para compartilhar
    resultados = list(ctx.get("resultados", []))
    linhas = []
    for r in resultados[:3]:
        nome = getattr(r.dimensao, "nome", getattr(r, "dimensao_nome", "Geral"))
        linhas.append(f"- {nome}: {getattr(r, 'percentual', 0):.2f}% (nível {getattr(r, 'nivel', '-')})")
    ctx["wh_text"] = (
        "Meu resultado no Teste Vocacional:\n\n" + "\n".join(linhas) + "\n\n@EscolaNoAr" if linhas else ""
    )

    return render(request, "vocacional/resultado.html", ctx)


@login_required
def enviar_resultado_email(request: HttpRequest, pk: int) -> HttpResponse:
    avaliacao = get_object_or_404(Avaliacao, pk=pk, usuario=request.user)
    try:
        notificar_resultado(request.user, avaliacao)
        messages.success(request, "Resultado enviado por e-mail.")
    except Exception as e:  # pragma: no cover
        messages.error(request, f"Não foi possível enviar o e-mail agora. ({e})")
    return redirect("vocacional:resultado", pk=pk)


def bonus_landing(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("vocacional:index")
    return render(request, "vocacional/bonus.html")

