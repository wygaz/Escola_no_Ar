from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Pergunta, Avaliacao
from .gating import gating_state, next_url

@login_required
def debug(request):
    a = (Avaliacao.objects
         .filter(usuario=request.user, status="rascunho")
         .order_by("-pk").first())
    return JsonResponse({
        "user": request.user.get_username(),
        "perguntas_ativas": Pergunta.objects.filter(ativo=True).count(),
        "avaliacao_id": getattr(a, "pk", None),
        "ordem_ids": getattr(a, "ordem_ids", ""),
        "next_url": next_url(request.user),
        "gating": gating_state(request.user),
    })
