# apps/contas/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from django import forms

from .models_acessos import Produto, Acesso


Usuario = get_user_model()


# ---------- Forms do Usuario (sem username) ----------
class UsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Senha"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirmação de senha"), widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ("email", "first_name", "last_name", "nome", "perfil", "is_active", "is_staff")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_("As senhas não conferem."))
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Senha"))

    class Meta:
        model = Usuario
        fields = (
            "email", "password", "first_name", "last_name", "nome",
            "perfil", "is_active", "is_staff", "is_superuser",
            "groups", "user_permissions",
        )

    def clean_password(self):
        return self.initial["password"]


@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm

    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "perfil", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name", "nome")
    list_filter = ("perfil", "is_active", "is_staff")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Informações pessoais"), {"fields": ("first_name", "last_name", "nome", "imagem")}),
        (_("Permissões"), {"fields": ("perfil", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Importante"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "nome", "perfil", "is_active", "is_staff", "password1", "password2"),
        }),
    )


# ---------- Produto / Acesso ----------
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("slug", "nome")
    search_fields = ("slug", "nome")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Acesso)
class AcessoAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user", "produto")
    list_display = ("user", "produto", "origem", "granted_at", "expires_at", "ativo_admin")
    list_filter = ("produto", "origem")
    search_fields = ("user__email", "user__first_name", "user__last_name", "user__nome", "produto__slug", "produto__nome")

    @admin.display(boolean=True, description="Ativo")
    def ativo_admin(self, obj):
        # tenta property "ativo"; se não existir, calcula pelo expires_at
        if hasattr(obj, "ativo"):
            return bool(getattr(obj, "ativo"))
        if getattr(obj, "expires_at", None) is None:
            return True
        from django.utils import timezone
        return obj.expires_at > timezone.now()
