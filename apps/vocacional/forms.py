# apps/vocacional/forms.py
from django import forms
from .models import Resposta, Pergunta, Opcao

class RespostaForm(forms.ModelForm):
    class Meta:
        model = Resposta
        fields = ["opcao", "valor"]

    def __init__(self, *args, **kwargs):
        pergunta = kwargs.pop("pergunta")
        super().__init__(*args, **kwargs)
        self.fields["opcao"].required = False
        if pergunta.tipo == "likert":
            self.fields["valor"] = forms.ChoiceField(
                choices=[(i, str(i)) for i in range(1, 6)],
                widget=forms.RadioSelect,
                label="",
            )
            self.fields["opcao"].widget = forms.HiddenInput()
        else:
            self.fields["opcao"].queryset = Opcao.objects.filter(pergunta=pergunta).order_by("ordem")
            self.fields["opcao"].widget = forms.RadioSelect()
            self.fields["valor"].widget = forms.HiddenInput()


class ConsentimentoForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=150)
    # e-mail só para exibição; não será usado do POST
    email = forms.EmailField(label="E-mail", required=False, disabled=True)
    
