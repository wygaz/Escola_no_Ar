# apps/contas/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models_acessos import Produto, Acesso

Usuario = get_user_model()


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display  = ("id", "email", "first_name", "last_name", "perfil", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name", "nome")
    list_filter   = ("perfil", "is_active", "is_staff")
    ordering      = ("first_name", "last_name", "email")


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display        = ("slug", "nome")
    search_fields       = ("slug", "nome")
    prepopulated_fields = {"slug": ("nome",)}  # opcional


@admin.register(Acesso)
class AcessoAdmin(admin.ModelAdmin):
    list_display       = ("user", "produto", "origem", "granted_at", "expires_at", "ativo")
    list_filter        = ("produto", "origem")
    search_fields      = ("user__email", "user__first_name", "user__last_name")
    autocomplete_fields = ("user", "produto")
    date_hierarchy     = "granted_at"
