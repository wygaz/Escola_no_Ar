# apps/contas/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import Usuario

class LoginForm(AuthenticationForm):
    # se seu USERNAME_FIELD é email, isso já funciona;
    # opcionalmente personalize o label/placeholder:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "E-mail"
        self.fields["password"].label = "Senha"

class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "cep", "numero_endereco", "imagem"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control"}),
            "email":      forms.EmailInput(attrs={"class": "form-control"}),
            "cep":        forms.TextInput(attrs={"class": "form-control"}),
            "numero_endereco": forms.TextInput(attrs={"class": "form-control"}),
            "imagem":     forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class FormularioImagem(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["imagem"]
        widgets = {
            "imagem": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
# alias para não quebrar imports antigos
PerfilForm = UsuarioPerfilForm

class AlterarSenhaForm(PasswordChangeForm):
    pass
