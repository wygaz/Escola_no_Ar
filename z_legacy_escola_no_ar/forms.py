from django import forms
from django.contrib.auth.forms import UserCreationForm  # ✅ Importação necessária
from .models import Usuario

class FormularioCadastro(UserCreationForm):
    nome_completo = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='E-mail')
    tipo = forms.ChoiceField(label='Tipo de usuário', choices=Usuario._meta.get_field('tipo').choices)
    foto_perfil = forms.ImageField(label='Foto de perfil (opcional)', required=False)

    class Meta:
        model = Usuario
        fields = ['nome_completo', 'email', 'tipo', 'foto_perfil', 'password1', 'password2']
