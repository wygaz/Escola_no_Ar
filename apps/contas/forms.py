# apps/contas/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import Usuario
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]  # acrescente "nome" se quiser

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("As senhas não conferem.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

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
