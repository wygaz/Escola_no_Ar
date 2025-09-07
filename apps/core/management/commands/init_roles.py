# apps/core/management/commands/init_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

ROLE_DEFS = {
    "Aluno": {
        # codenames das permissões que o aluno precisa
        "atividades": ["add_submissao", "view_submissao"],
        "comunicacao": ["add_comentario", "view_comentario"],
        "escola_no_ar": ["view_conteudo"],
        "sonho_de_ser": ["add_registrodiario", "view_registrodiario"],
    },
    "Professor": {
        "atividades": ["add_atividade", "change_atividade", "view_atividade"],
        "cursos": ["add_aula", "change_aula", "view_aula"],
        "comunicacao": ["add_comentario", "delete_comentario", "view_comentario"],
        "escola_no_ar": ["add_conteudo", "change_conteudo", "view_conteudo"],
        "sonho_de_ser": ["change_desafio", "view_desafio"],
    },
    "Autor": {
        "licoes": ["add_licao", "change_licao", "view_licao"],
        "escola_no_ar": ["add_conteudo", "change_conteudo", "view_conteudo"],
    },
}

class Command(BaseCommand):
    help = "Cria/atualiza grupos (Aluno, Professor, Autor) e associa permissões"

    def handle(self, *args, **options):
        for role, by_app in ROLE_DEFS.items():
            group, _ = Group.objects.get_or_create(name=role)
            perms_to_set = []
            for app_label, codenames in by_app.items():
                for code in codenames:
                    try:
                        perm = Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=code,
                        )
                        perms_to_set.append(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f"[WARN] Permissão {app_label}.{code} não existe (crie o Model e rode makemigrations/migrate)."
                        ))
            group.permissions.set(perms_to_set)
            group.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] Grupo {role} atualizado"))
