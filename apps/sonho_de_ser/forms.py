from django import forms
from django.db import transaction
from django.utils import timezone

from .models import Estrategia, Plano, PlanoItem, RegistroDiario


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
    Gera um checkbox para cada Estratégia ativa no plano.
    Campos são dinâmicos no formato e<ID_DO_PLANOITEM>.
    """
    def __init__(self, plano: Plano, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plano = plano

        itens = (PlanoItem.objects.filter(plano=plano, ativo=True)
                 .select_related("estrategia", "estrategia__area")
                 .order_by("estrategia__area__inicial", "estrategia__nivel", "estrategia__ordem_nivel"))
        self.itens = list(itens)

        for item in self.itens:
            self.fields[f"e{item.id}"] = forms.BooleanField(
                required=False,
                label=item.estrategia.titulo
            )

    def save(self, data_registro=None):
        data_registro = data_registro or timezone.localdate()

        # Quais checkboxes vieram marcados
        marcados_ids = [
            int(name[1:]) for name, val in self.cleaned_data.items()
            if name.startswith("e") and val
        ]

        # Mapa: planoitem.id -> estrategia_id
        id_to_estr = {pi.id: pi.estrategia_id for pi in self.itens}
        estr_do_plano = list(id_to_estr.values())
        estr_marcadas = [id_to_estr[i] for i in marcados_ids]

        # Zera registros do dia para estratégias do plano (evita duplicidade)
        RegistroDiario.objects.filter(
            usuario=self.plano.usuario,
            data=data_registro,
            estrategia_id__in=estr_do_plano
        ).delete()

        # Cria somente as marcadas
        objs = [
            RegistroDiario(
                usuario=self.plano.usuario,
                data=data_registro,
                estrategia_id=eid,
            )
            for eid in estr_marcadas
        ]
        if objs:
            RegistroDiario.objects.bulk_create(objs, ignore_conflicts=True)

        return data_registro
