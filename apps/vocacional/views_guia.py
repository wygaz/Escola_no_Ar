# apps/vocacional/views_guia.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.core.permissions import require_legal
from .gating import next_url
from .models import AvaliacaoGuia, QuestaoGuia, RespostaGuia


@login_required
@require_legal()
def guia_avaliacao(request):
    """Avaliação do Guia (pré-requisito para liberar os bônus)."""
    avaliacao, _ = AvaliacaoGuia.objects.get_or_create(user=request.user)

    questoes = list(QuestaoGuia.objects.order_by("ordem"))

    if request.method == "POST":
        aceite = request.POST.get("aceite") == "1"
        if not aceite:
            messages.error(request, "Para continuar, confirme que leu e concorda com os Termos.")
            return redirect("vocacional:guia_avaliacao")

        for q in questoes:
            val = (request.POST.get(f"q_{q.id}") or "").strip()
            RespostaGuia.objects.update_or_create(
                avaliacao=avaliacao, questao=q, defaults={"texto": val}
            )

        # valida: todas respondidas (texto != "")
        faltando = RespostaGuia.objects.filter(avaliacao=avaliacao, texto="").exists()
        if faltando:
            messages.error(request, "Responda todas as perguntas antes de finalizar.")
            return redirect("vocacional:guia_avaliacao")

        avaliacao.status = "concluida"
        avaliacao.aceite_termos = True
        avaliacao.save(update_fields=["status", "aceite_termos"])
        messages.success(request, "Avaliação registrada. Obrigado!")
        return redirect(next_url(request.user))

    respostas = {
        r.questao_id: r.texto for r in RespostaGuia.objects.filter(avaliacao=avaliacao)
    }

    return render(
        request,
        "vocacional/guia_avaliacao.html",
        {"avaliacao": avaliacao, "questoes": questoes, "respostas": respostas},
    )
