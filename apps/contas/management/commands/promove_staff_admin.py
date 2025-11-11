# crie um comando rápido: apps/contas/management/commands/promove_staff_admin.py
from django.core.management.base import BaseCommand
from apps.contas.models import Usuario

class Command(BaseCommand):
    help = "Define perfil=ADMIN para usuários com is_staff=True (se ainda USER)."

    def handle(self, *args, **opts):
        qs = Usuario.objects.filter(is_staff=True, perfil="USER")
        n = qs.update(perfil="ADMIN")
        self.stdout.write(self.style.SUCCESS(f"Promovidos {n} usuários staff -> ADMIN."))
