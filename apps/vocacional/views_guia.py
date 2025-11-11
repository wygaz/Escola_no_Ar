# apps/vocacional/views_guia.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction
from .models import AvaliacaoGuia, QuestaoGuia, RespostaGuia
from .gating import next_url

def _ensure_perguntas():
    if not QuestaoGuia.objects.exists():
        base = [
            ("O guia foi claro e fácil de entender?", "likert"),
            ("O conteúdo te ajudou a refletir sobre sua vocação?", "likert"),
            ("Você recomendaria o guia para um amigo?", "likert"),
            ("Quais pontos mais te ajudaram? (resposta breve)", "texto"),
            ("O que podemos melhorar? (resposta breve)", "texto"),
        ]
        for i, (t, tipo) in enumerate(base, start=1):
            QuestaoGuia.objects.create(ordem=i, enunciado=t, tipo=tipo)

@login_required
def guia_avaliacao(request):
    """Pré-requisito: responder 5 itens + aceitar termos.
       Concluído ⇒ marca aceito e envia para o formulário do teste.
    """
    _ensure_perguntas()
    aval, _ = AvaliacaoGuia.objects.get_or_create(
        user=request.user, defaults={"status": "rascunho"}
    )
    perguntas = list(QuestaoGuia.objects.filter(ativo=True).order_by("ordem"))

    if request.method == "POST":
        aceite = request.POST.get("aceite_termos") == "on"
        with transaction.atomic():
            for q in perguntas:
                if q.tipo == "likert":
                    raw = request.POST.get(f"q{q.id}")
                    val = int(raw) if raw and raw.isdigit() else None
                    RespostaGuia.objects.update_or_create(
                        avaliacao=aval, questao=q, defaults={"valor": val, "texto": ""}
                    )
                else:
                    txt = (request.POST.get(f"q{q.id}_t") or "").strip()
                    RespostaGuia.objects.update_or_create(
                        avaliacao=aval, questao=q, defaults={"texto": txt, "valor": None}
                    )

            # validação final
            faltando = []
            for q in perguntas:
                r = RespostaGuia.objects.filter(avaliacao=aval, questao=q).first()
                if q.tipo == "likert" and not (r and r.valor):
                    faltando.append(q.id)
                if q.tipo == "texto" and not (r and r.texto):
                    faltando.append(q.id)

            if faltando or not aceite:
                if faltando:
                    messages.error(request, "Responda todas as perguntas (1 a 5 e os dois textos).")
                if not aceite:
                    messages.error(request, "Você precisa aceitar os Termos para continuar.")
            else:
                aval.status = "concluida"
                aval.aceite_termos = True
                aval.save()
                messages.success(request, "Obrigado! Avaliação do guia registrada.")
                return redirect(next_url(request.user))

        return redirect("vocacional:guia_avaliacao")

    return render(request, "vocacional/guia_avaliacao.html", {
        "perguntas": perguntas,
        "avaliacao": aval,
    })
