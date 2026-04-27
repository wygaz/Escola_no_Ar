from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import InstituicaoUsuario


class Command(BaseCommand):
    help = (
        "Migra vinculos legados de aluno em InstituicaoUsuario para "
        "Usuario.instituicao, preservando o registro legado como inativo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Aplica as alteracoes no banco. Sem esta flag, executa apenas simulacao.",
        )

    def handle(self, *args, **options):
        apply_changes = bool(options.get("apply"))
        qs = (
            InstituicaoUsuario.objects.select_related("usuario", "instituicao")
            .filter(papel="aluno")
            .order_by("instituicao__nome", "usuario__email", "id")
        )

        total = qs.count()
        assign_count = 0
        already_aligned_count = 0
        deactivated_count = 0
        conflict_count = 0
        conflicts = []

        self.stdout.write(
            f"VINCULOS_ALUNO_ENCONTRADOS={total} modo={'APPLY' if apply_changes else 'DRY-RUN'}"
        )

        @transaction.atomic
        def _apply():
            nonlocal assign_count, already_aligned_count, deactivated_count, conflict_count, conflicts

            for vinculo in qs:
                user = vinculo.usuario
                institution = vinculo.instituicao

                if user.instituicao_id and user.instituicao_id != institution.id:
                    conflict_count += 1
                    conflicts.append(
                        f"{user.email}: usuario={user.instituicao.nome} / vinculo={institution.nome}"
                    )
                    continue

                changed_fields = []
                if user.instituicao_id is None:
                    user.instituicao = institution
                    changed_fields.append("instituicao")
                    assign_count += 1
                else:
                    already_aligned_count += 1

                if changed_fields:
                    user.save(update_fields=changed_fields)

                if vinculo.ativo:
                    note = "Migrado para Usuario.instituicao pelo saneamento de vinculos legados."
                    vinculo.ativo = False
                    if note not in (vinculo.observacoes or ""):
                        vinculo.observacoes = "\n\n".join(filter(None, [vinculo.observacoes, note]))
                    vinculo.save(update_fields=["ativo", "observacoes"])
                    deactivated_count += 1

        if apply_changes:
            _apply()
        else:
            for vinculo in qs:
                user = vinculo.usuario
                institution = vinculo.instituicao
                if user.instituicao_id and user.instituicao_id != institution.id:
                    conflict_count += 1
                    conflicts.append(
                        f"{user.email}: usuario={user.instituicao.nome} / vinculo={institution.nome}"
                    )
                    continue
                if user.instituicao_id is None:
                    assign_count += 1
                else:
                    already_aligned_count += 1
                if vinculo.ativo:
                    deactivated_count += 1

        self.stdout.write(f"USUARIOS_COM_INSTITUICAO_A_ATRIBUIR={assign_count}")
        self.stdout.write(f"USUARIOS_JA_ALINHADOS={already_aligned_count}")
        self.stdout.write(f"VINCULOS_A_INATIVAR={deactivated_count}")
        self.stdout.write(f"CONFLITOS={conflict_count}")

        if conflicts:
            self.stdout.write("CONFLITOS_DETALHE:")
            for item in conflicts[:20]:
                self.stdout.write(f"- {item}")

        if not apply_changes:
            self.stdout.write("Simulacao concluida. Rode com --apply para efetivar.")
        else:
            self.stdout.write(self.style.SUCCESS("Saneamento concluido."))
