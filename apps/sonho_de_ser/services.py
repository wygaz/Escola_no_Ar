from __future__ import annotations

from datetime import date, timedelta

from .models import Plano, RegistroDiario


def semana_atual_range(hoje: date) -> tuple[date, date]:
    inicio = hoje - timedelta(days=hoje.weekday())
    fim = inicio + timedelta(days=6)
    return inicio, fim


def progresso_do_dia(plano: Plano, quando: date) -> dict:
    estrategias_ids = list(
        plano.itens.filter(ativo=True).values_list("estrategia_id", flat=True)
    )
    total = len(estrategias_ids)
    if total == 0:
        return {"data": quando, "feitos": 0, "total": 0, "percentual": 0}

    feitos = RegistroDiario.objects.filter(
        usuario=plano.usuario,
        data=quando,
        estrategia_id__in=estrategias_ids,
    ).count()
    percentual = int((feitos / total) * 100) if total else 0
    return {"data": quando, "feitos": feitos, "total": total, "percentual": percentual}


def progresso_da_semana(plano: Plano, hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    inicio, _ = semana_atual_range(hoje)

    serie = []
    feitos_total = 0
    possiveis_total = 0
    for i in range(7):
        dia = inicio + timedelta(days=i)
        info = progresso_do_dia(plano, dia)
        serie.append(info)
        feitos_total += info["feitos"]
        possiveis_total += info["total"]

    geral = int((feitos_total / possiveis_total) * 100) if possiveis_total else 0
    return {"serie": serie, "geral": geral}


def resumo_dashboard(plano: Plano | None, hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    base = {
        "plano": plano,
        "registros_hoje": 0,
        "estrategias_ativas": 0,
        "adesao_semana": 0,
        "serie_semana": [],
        "historico_recente": [],
    }
    if plano is None:
        return base

    progresso_hoje = progresso_do_dia(plano, hoje)
    semana = progresso_da_semana(plano, hoje)
    historico = list(
        RegistroDiario.objects.filter(usuario=plano.usuario)
        .select_related("estrategia", "estrategia__area")
        .order_by("-data", "estrategia__area__inicial", "estrategia__ordem_nivel")[:10]
    )

    base.update(
        {
            "registros_hoje": progresso_hoje["feitos"],
            "estrategias_ativas": progresso_hoje["total"],
            "adesao_semana": semana["geral"],
            "serie_semana": semana["serie"],
            "historico_recente": historico,
        }
    )
    return base
