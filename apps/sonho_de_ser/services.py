from datetime import date, timedelta
from collections import defaultdict
from django.db.models import Count, Q
from .models import Plano, RegistroDiario, PlanoEstrategia




def semana_atual_range(hoje: date):
    # Segunda..Domingo (ISO)
    start = hoje - timedelta(days=hoje.weekday())
    end = start + timedelta(days=6)
    return start, end




def adesao_semana(plano: Plano, hoje: date):
    inicio, fim = semana_atual_range(hoje)
    regs = RegistroDiario.objects.filter(plano=plano, data__range=(inicio, fim)).order_by("data")
    out = []
    for r in regs:
        out.append({"data": r.data, "percentual": r.percentual})
    # Geral da semana
    pe_total = PlanoEstrategia.objects.filter(plano_objetivo__plano=plano, ativo=True).count()
    feitos = 0
    possiveis = 0
    for r in regs:
        possiveis += pe_total
        feitos += r.itens.filter(feito=True).count()
    geral = int((feitos / possiveis) * 100) if possiveis else 0
    return {"serie": out, "geral": geral}