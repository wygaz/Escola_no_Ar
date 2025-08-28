from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Escola, Perfil, Trilha, Desafio, RegistroDiario,
    Selo, SeloConquistado, Postagem, Reacao, RelacaoMentorAluno
)

admin.site.register(Escola)
admin.site.register(Perfil)
admin.site.register(Trilha)
admin.site.register(Desafio)
admin.site.register(RegistroDiario)
admin.site.register(Selo)
admin.site.register(SeloConquistado)
admin.site.register(Postagem)
admin.site.register(Reacao)
admin.site.register(RelacaoMentorAluno)
