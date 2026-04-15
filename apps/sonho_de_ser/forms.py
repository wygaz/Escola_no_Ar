from django import forms
from django.db import transaction
from django.utils import timezone

from .models import Estrategia, JornadaDiaria, Plano, PlanoItem, RegistroDiario


# -------------------------------
# Plano: selecionar Estratégias
# -------------------------------
class PlanoForm(forms.Form):
    estrategias = forms.ModelMultipleChoiceField(
        queryset=Estrategia.objects.filter(ativo=True)
        .select_related("area")
        .order_by("area__inicial", "nivel", "ordem_nivel"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Selecione as estratégias do seu plano",
    )

    def __init__(self, *args, **kwargs):
        # passe usuario= na construção do form
        self.usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)

        # Pré-seleciona as estratégias já presentes no plano ativo
        if self.usuario:
            plano = Plano.objects.filter(usuario=self.usuario, ativo=True).first()
            if plano:
                atuais = PlanoItem.objects.filter(plano=plano, ativo=True) \
                    .values_list("estrategia_id", flat=True)
                self.initial.setdefault("estrategias", list(atuais))

    @transaction.atomic
    def save(self) -> Plano:
        assert self.usuario is not None, "Passe usuario= ao construir o PlanoForm"
        plano, _ = Plano.objects.get_or_create(usuario=self.usuario, ativo=True)

        selecionadas = set(
            self.cleaned_data.get("estrategias", []).values_list("id", flat=True)
        )

        # Inativa o que saiu do plano
        PlanoItem.objects.filter(plano=plano) \
            .exclude(estrategia_id__in=selecionadas).update(ativo=False)

        # Cria/reativa o que entrou
        for eid in selecionadas:
            item, created = PlanoItem.objects.get_or_create(plano=plano, estrategia_id=eid)
            if not created and not item.ativo:
                item.ativo = True
                item.save(update_fields=["ativo"])

        return plano


# -------------------------------
# Registro diário: checkboxes do plano
# -------------------------------
class RegistroForm(forms.Form):
    """
    Gera um check-in diario do aluno com:
    - reflexao geral do dia
    - status por estrategia do plano
    - observacao opcional por estrategia
    """
    STATUS_CHOICES = (
        ("", "Nao informar agora"),
        ("NAO_FIZ", "Nao fiz"),
        ("PARCIAL", "Fiz parcialmente"),
        ("FEITO", "Fiz"),
    )

    intencao_do_dia = forms.CharField(
        required=False,
        label="Intencao do dia",
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
    )
    principal_vitoria = forms.CharField(
        required=False,
        label="Principal vitoria",
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
    )
    principal_dificuldade = forms.CharField(
        required=False,
        label="Principal dificuldade",
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
    )
    observacoes_gerais = forms.CharField(
        required=False,
        label="Observacoes gerais",
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
    )

    def __init__(self, plano: Plano, *args, **kwargs):
        self.data_registro = kwargs.pop("data_registro", timezone.localdate())
        carregar_existentes = kwargs.pop("carregar_existentes", True)
        super().__init__(*args, **kwargs)
        self.plano = plano

        itens = (PlanoItem.objects.filter(plano=plano, ativo=True)
                 .select_related("estrategia", "estrategia__area")
                 .order_by("estrategia__area__inicial", "estrategia__nivel", "estrategia__ordem_nivel"))
        self.itens = list(itens)

        existentes = {}
        if carregar_existentes:
            existentes = {
                registro.estrategia_id: registro
                for registro in RegistroDiario.objects.filter(
                    usuario=plano.usuario,
                    data=self.data_registro,
                    estrategia_id__in=[item.estrategia_id for item in self.itens],
                )
            }

        for item in self.itens:
            self.fields[f"status_{item.id}"] = forms.ChoiceField(
                required=False,
                choices=self.STATUS_CHOICES,
                label=item.estrategia.titulo,
                widget=forms.Select(attrs={"class": "form-select"}),
            )
            self.fields[f"obs_{item.id}"] = forms.CharField(
                required=False,
                label=f"Observacao sobre {item.estrategia.titulo}",
                widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            )
            existente = existentes.get(item.estrategia_id)
            if existente:
                self.initial.setdefault(f"status_{item.id}", existente.status)
                self.initial.setdefault(f"obs_{item.id}", existente.observacao)

    def save(self, data_registro=None):
        data_registro = data_registro or timezone.localdate()
        jornada, _ = JornadaDiaria.objects.get_or_create(
            usuario=self.plano.usuario,
            data=data_registro,
        )
        jornada.intencao_do_dia = self.cleaned_data.get("intencao_do_dia", "")
        jornada.principal_vitoria = self.cleaned_data.get("principal_vitoria", "")
        jornada.principal_dificuldade = self.cleaned_data.get("principal_dificuldade", "")
        jornada.observacoes_gerais = self.cleaned_data.get("observacoes_gerais", "")
        jornada.save()

        for item in self.itens:
            status = self.cleaned_data.get(f"status_{item.id}") or ""
            observacao = self.cleaned_data.get(f"obs_{item.id}", "")

            if not status:
                RegistroDiario.objects.filter(
                    usuario=self.plano.usuario,
                    data=data_registro,
                    estrategia=item.estrategia,
                ).delete()
                continue

            RegistroDiario.objects.update_or_create(
                usuario=self.plano.usuario,
                data=data_registro,
                estrategia=item.estrategia,
                defaults={
                    "jornada": jornada,
                    "status": status,
                    "observacao": observacao,
                },
            )

        return jornada
