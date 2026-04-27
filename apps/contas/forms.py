# apps/contas/forms.py
import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Usuario

User = get_user_model()


class UsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput)
    aceite_termos = forms.BooleanField(
        label="Li e aceito os Termos de Uso",
        required=True,
    )
    aceite_privacidade = forms.BooleanField(
        label="Li e aceito a Política de Privacidade",
        required=True,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")

        if p1:
            extra_errors = []
            if len(p1) < 8:
                extra_errors.append("A senha deve ter pelo menos 8 caracteres.")
            if not re.search(r"[a-z]", p1):
                extra_errors.append("Inclua pelo menos 1 letra minúscula.")
            if not re.search(r"[A-Z]", p1):
                extra_errors.append("Inclua pelo menos 1 letra maiúscula.")
            if not re.search(r"\d", p1):
                extra_errors.append("Inclua pelo menos 1 número.")

            try:
                dummy_user = User(email=(cleaned.get("email") or "").strip().lower())
                validate_password(p1, user=dummy_user)
            except ValidationError as e:
                extra_errors.extend(list(e.messages))

            if extra_errors:
                for msg in extra_errors:
                    self.add_error("password1", msg)

        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Confirmação de senha deve ser igual à senha.")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.persist_legal_acceptance(user)
        return user

    def persist_legal_acceptance(self, user):
        from django.utils import timezone
        from apps.vocacional.models import AvaliacaoGuia
        from apps.vocacional.models_consent import Consentimento

        ag, _ = AvaliacaoGuia.objects.get_or_create(user=user)
        if not ag.aceite_termos:
            ag.aceite_termos = True
            ag.save(update_fields=["aceite_termos"])

        Consentimento.objects.update_or_create(
            user=user,
            defaults={
                "nome": user.get_full_name() or user.email,
                "email": user.email,
                "aceito": True,
                "revogado_em": None,
                "aceito_em": timezone.now(),
            },
        )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuário ou e-mail"
        self.fields["password"].label = "Senha"
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Digite seu usuário ou e-mail",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "placeholder": "Digite sua senha",
                "autocomplete": "current-password",
            }
        )

    def _normalize_identity(self, ident: str) -> str:
        ident = (ident or "").strip().lower()
        if ident and "@" not in ident:
            qs = User.objects.filter(email__istartswith=ident + "@")
            if qs.count() == 1:
                ident = qs.first().email.lower()
        return ident

    def clean(self):
        ident = self._normalize_identity(
            self.cleaned_data.get("username") or self.data.get("username") or ""
        )
        password = self.cleaned_data.get("password") or self.data.get("password") or ""

        if ident:
            self.cleaned_data["username"] = ident

        if ident and password:
            self.user_cache = (
                authenticate(self.request, username=ident, password=password)
                or authenticate(self.request, email=ident, password=password)
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class PasswordResetIdentityForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Usuário ou e-mail"
        self.fields["email"].widget.attrs.update(
            {
                "placeholder": "Digite seu usuário ou e-mail",
                "autocomplete": "username",
            }
        )

    def clean_email(self):
        ident = (self.cleaned_data.get("email") or "").strip().lower()
        if ident and "@" not in ident:
            qs = User.objects.filter(email__istartswith=ident + "@")
            if qs.count() == 1:
                ident = qs.first().email.lower()
        return ident


class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "cep", "numero_endereco", "imagem"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "cep": forms.TextInput(attrs={"class": "form-control"}),
            "numero_endereco": forms.TextInput(attrs={"class": "form-control"}),
            "imagem": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class FormularioImagem(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["imagem"]
        widgets = {
            "imagem": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


PerfilForm = UsuarioPerfilForm


class AlterarSenhaForm(PasswordChangeForm):
    pass
