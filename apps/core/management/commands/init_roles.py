# apps/core/management/commands/init_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

ROLE_DEFS = {
    "Aluno": {
        # codenames das permissões que o aluno precisa
        "atividades": ["add_submissao", "view_submissao"],
 
        "comunicacao": ["view_topico", "view_mensagem", "add_mensagem", "change_mensagem"],

        "contas": ["view_usuario"],

        "core": ["view_nivelevolucao"],

        "cursos": [
            "view_curso","view_modulo","view_aula",
            "view_turma","view_matricula","view_progressoaula"],

        "projeto21": [
            "view_area", "view_estrategia"],
 
        "sonho_de_ser": [
            "view_area", "view_estrategia",
            "view_plano", "add_plano", "change_plano",
            "view_planoitem", "add_planoitem", "change_planoitem",
            "view_registrodiario", "add_registrodiario", "change_registrodiario"],
    },
 
    "Professor": {
        "atividades": ["add_atividade", "change_atividade", "view_atividade"],

        "cursos": ["add_aula", "change_aula", "view_aula"],

        "comunicacao": [
            "view_topico", "add_topico", "change_topico","view_mensagem",
            "add_mensagem", "change_mensagem"],

        "contas": ["view_usuario"],

        "core": ["view_nivelevolucao"],

        "cursos": [
            "view_curso","add_curso","change_curso",
            "view_modulo","add_modulo","change_modulo",
            "view_aula","add_aula","change_aula",
            "view_turma","add_turma","change_turma",
            "view_matricula","add_matricula","change_matricula",
            "view_progressoaula","add_progressoaula","change_progressoaula"],

        "projeto21": [
            "view_area", "view_estrategia",
            "add_area", "change_area",
            "add_estrategia", "change_estrategia"],

        "sonho_de_ser": [
            "view_area", "view_estrategia",
            "view_mentorprofile", "add_mentorprofile", "change_mentorprofile",
            "view_mentoria", "add_mentoria", "change_mentoria",
            "view_anotacaomentor", "add_anotacaomentor", "change_anotacaomentor",
            "view_plano", "view_planoitem",
            "view_registrodiario"],
    },

    "Mentor": {
        "contas": ["view_usuario""view_nivelevolucao"],

        "core": ["view_nivelevolucao"],

        "cursos": ["view_curso","view_modulo","view_aula",
            "view_turma","view_matricula","view_progressoaula"],

        "projeto21": [
            "view_area", "view_estrategia"],

        "sonho_de_ser": [
            "view_area", "view_estrategia",
            "view_mentorprofile", "add_mentorprofile", "change_mentorprofile",
            "view_mentoria", "add_mentoria", "change_mentoria",
            "view_anotacaomentor", "add_anotacaomentor", "change_anotacaomentor",
            "view_plano", "view_planoitem",
            "view_registrodiario"],
    },

    "Autor": {
        "comunicacao": ["view_topico", "add_topico","view_mensagem", "add_mensagem"],

        "licoes": ["add_licao", "change_licao", "view_licao"],

        "contas": ["view_usuario"],

        "core": ["view_nivelevolucao"],

        "projeto21": [
            "view_area", "view_estrategia"],

        "sonho_de_ser": [
            "view_area", "view_estrategia",
            "view_plano", "view_planoitem", "view_registrodiario",
        ],
    },
}

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--only-app",
            help="Aplica as permissões apenas do app especificado (ex.: atividades)",
        )

    help = "Cria/atualiza grupos (Aluno, Professor, Autor) e associa permissões"

    def handle(self, *args, **options):
        only_app = options.get("only_app")

        for role, by_app in ROLE_DEFS.items():
            group, _ = Group.objects.get_or_create(name=role)
            perms_to_set = []
            for app_label, codenames in by_app.items():
                if only_app and app_label != only_app:
                    continue

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
