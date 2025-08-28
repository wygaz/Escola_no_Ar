from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import Usuario

Usuario = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'pais', 'estado', 'cidade', 'profissao', 'cargo_igreja']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'profissao': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_igreja': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AlterarSenhaForm(PasswordChangeForm):
    old_password = forms.CharField(label='Senha atual', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label='Nova senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label='Confirmação da nova senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class FormularioImagem(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['imagem']