from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Avaliacao, Resposta, Resultado, Pergunta
from django.core.mail import send_mail
from django.conf import settings

NIVEIS = [
    (0, "baixo"),
    (40, "médio"),
    (70, "alto"),
]

def classificar(percentual: Decimal) -> str:
    p = float(percentual)
    nivel = "alto"
    for lim, rotulo in NIVEIS:
        if p < lim:
            break
        nivel = rotulo
    return nivel

def calcular_resultados(avaliacao: Avaliacao):
    soma = defaultdict(Decimal)
    max_por_dim = defaultdict(Decimal)

    perguntas = Pergunta.objects.filter(ativo=True).select_related("dimensao")
    max_likert = Decimal(5)  # escala 1..5

    # ---- Soma por dimensão (com inversão em Likert) -------------------------
    for r in Resposta.objects.filter(avaliacao=avaliacao).select_related("pergunta__dimensao"):
        p = r.pergunta
        d = p.dimensao
        peso = Decimal(getattr(d, "peso", 1) or 1)

        if p.tipo == "likert":
            bruto = Decimal(r.valor or 0)
            # aceita vários nomes possíveis para o flag de inversão
            inverso = any(getattr(p, k, False) for k in ("inversa", "invert", "inverso", "reverso"))
            valor = (Decimal(6) - bruto) if (inverso and bruto) else bruto
        else:
            # múltipla escolha etc.
            valor = Decimal(r.opcao.valor if getattr(r, "opcao", None) else 0)

        soma[d.id] += valor * peso

    # ---- Máximo por dimensão (para percentual) ------------------------------
    for p in perguntas:
        d = p.dimensao
        peso = Decimal(getattr(d, "peso", 1) or 1)
        if p.tipo == "likert":
            max_por_dim[d.id] += max_likert * peso
        else:
            try:
                max_opcao = max(Decimal(o.valor) for o in p.opcoes.all())
            except ValueError:
                max_opcao = Decimal(0)
            max_por_dim[d.id] += max_opcao * peso

    # ---- Persistência dos resultados ----------------------------------------
    Resultado.objects.filter(avaliacao=avaliacao).delete()
    for dim_id, total in soma.items():
        max_total = max_por_dim.get(dim_id) or Decimal(1)
        perc = (total / max_total) * Decimal(100)
        # sua função/heurística de classificação
        nivel = classificar(perc)

        Resultado.objects.create(
            avaliacao=avaliacao,
            dimensao_id=dim_id,
            pontuacao=int(total),                        # mantém seus campos
            percentual=perc.quantize(Decimal("0.01")),
            nivel=nivel,
        )

    avaliacao.status = "concluida"
    avaliacao.finalizado_em = timezone.now()
    avaliacao.save(update_fields=["status", "finalizado_em"])
    return avaliacao


def notificar_resultado(user, avaliacao):
    """Envia por e-mail um resumo (top 3 por percentual)."""
    # ordene pelos campos que você JÁ tem no modelo Resultado
    tops = list(avaliacao.resultados.select_related("dimensao").order_by("-percentual")[:3])

    linhas = []
    for r in tops:
        nome = getattr(r.dimensao, "nome", getattr(r, "dimensao_nome", "Geral"))
        linhas.append(f"- {nome}: {r.percentual:.2f}% (nível: {r.nivel})")

    msg = "Seu resultado do Teste Vocacional:\n\n" + "\n".join(linhas) + "\n\nObrigado por participar!"

    if user.email:
        send_mail(
            subject="Seu resultado do Teste Vocacional",
            message=msg,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@escolanoar"),
            recipient_list=[user.email],
            fail_silently=True,
        )
    # Gancho p/ WhatsApp fica aqui quando integrar (Twilio/Cloud API).

    from collections import defaultdict

def classificar_resultados(avaliacao, delta=3):
    """
    Retorna dict com: ranking (desc), top3, bottom3 e grupos_semelhantes (lista de listas)
    delta: diferença máxima em 'percentual' para agrupar em faixa semelhante.
    """
    qs = (avaliacao.resultados
          .select_related("dimensao")
          .all())

    items = []
    for r in qs:
        nome = getattr(getattr(r, "dimensao", None), "nome", None) or getattr(r, "dimensao_nome", "Geral")
        items.append({
            "nome": nome,
            "pontuacao": r.pontuacao,
            "percentual": r.percentual,
            "nivel": r.nivel,
        })

    ranking = sorted(items, key=lambda x: x["percentual"], reverse=True)

    top3 = ranking[:3]
    bottom3 = list(reversed(sorted(items, key=lambda x: x["percentual"])))[:3]  # 3 menores

    # agrupar faixas semelhantes (consecutivos com diferença <= delta)
    grupos = []
    bucket = [ranking[0]] if ranking else []
    for prev, cur in zip(ranking, ranking[1:]):
        if abs(cur["percentual"] - prev["percentual"]) <= delta:
            bucket.append(cur)
        else:
            if len(bucket) >= 2: grupos.append(bucket)
            bucket = [cur]
    if len(bucket) >= 2: grupos.append(bucket)

    return {
        "ranking": ranking,
        "top3": top3,
        "bottom3": bottom3,
        "grupos_semelhantes": grupos,
        "delta": delta,
    }
