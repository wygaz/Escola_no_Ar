# apps/contas/management/commands/seed_grupos.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

GRUPOS = ["Admins", "Professores", "Mentores", "Alunos", "Usuarios"]

# Quais apps tentar mapear permissões (ajuste conforme seus apps reais)
APPS_COM_PERMISSOES = ["cursos", "atividades", "comunicacao", "sonho_de_ser"]

def perms_por_prefixo(perms, *prefixos):
    wanted = []
    for p in perms:
        if any(p.codename.startswith(pref) for pref in prefixos):
            wanted.append(p)
    return wanted

class Command(BaseCommand):
    help = "Cria/atualiza grupos padrão e associa permissões por app."

    def handle(self, *args, **opts):
        grupos = {name: Group.objects.get_or_create(name=name)[0] for name in GRUPOS}

        # Limpa permissões atuais para evitar acúmulo indesejado (opcional)
        for g in grupos.values():
            g.permissions.clear()

        # Colete permissões disponíveis nos apps configurados
        permissoes_por_app = []
        for app_label in APPS_COM_PERMISSOES:
            try:
                cts = ContentType.objects.filter(app_label=app_label)
                if not cts.exists():
                    continue
                perms = Permission.objects.filter(content_type__in=cts)
                permissoes_por_app.extend(list(perms))
            except Exception:
                # App pode não existir ainda: segue em frente
                continue

        # Conjuntos úteis
        perms_view   = perms_por_prefixo(permissoes_por_app, "view_")
        perms_change = perms_por_prefixo(permissoes_por_app, "change_")
        perms_add    = perms_por_prefixo(permissoes_por_app, "add_")
        perms_delete = perms_por_prefixo(permissoes_por_app, "delete_")

        # Regras simples (ajuste conforme seu fluxo):
        # Admins: geralmente não precisa, pois terá is_superuser. Mas dá pra setar tudo:
        grupos["Admins"].permissions.add(*permissoes_por_app)

        # Professores: ver e alterar conteúdo pedagógico (view/change em cursos/atividades)
        grupos["Professores"].permissions.add(*perms_view, *perms_change, *perms_add)

        # Mentores: ver (e anotar) em sonhode_ser; aqui usamos view/change/add genérico
        # ajuste se tiver modelos específicos de "AnotacaoMentor", etc.
        grupos["Mentores"].permissions.add(*perms_view, *perms_add)

        # Alunos e Usuarios: geralmente apenas view
        grupos["Alunos"].permissions.add(*perms_view)
        grupos["Usuarios"].permissions.add(*perms_view)

        self.stdout.write(self.style.SUCCESS("Grupos e permissões configurados."))
