# apps/contas/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import Usuario
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re

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

        # 1) força da senha (usa PASSWORD_VALIDATORS do settings.py)
        if p1:
            extra_errors = []
            # validações extras solicitadas
            if len(p1) < 8:
                extra_errors.append("A senha deve ter pelo menos 8 caracteres.")
            if not re.search(r"[a-z]", p1):
                extra_errors.append("Inclua pelo menos 1 letra minúscula.")
            if not re.search(r"[A-Z]", p1):
                extra_errors.append("Inclua pelo menos 1 letra maiúscula.")
            if not re.search(r"\d", p1):
                extra_errors.append("Inclua pelo menos 1 número.")

            # validações do Django (common password, numeric only etc.)
            try:
                dummy_user = User(email=(cleaned.get("email") or "").strip().lower())
                validate_password(p1, user=dummy_user)
            except ValidationError as e:
                extra_errors.extend(list(e.messages))

            if extra_errors:
                for msg in extra_errors:
                    self.add_error("password1", msg)

        # 2) confirmação igual
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Confirmação de senha deve ser igual à senha.")

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
