from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.contas.models_acessos import Acesso, Produto
from apps.core.models import Instituicao, InstituicaoUsuario, InstitutionalDemoAccess, IntroPresentationProgress
from apps.core.views import _parse_governance_import_csv
from apps.vocacional.gating import next_step
from apps.core.permissions import (
    PROD_GUIA,
    PROD_SONHEMAISALTO,
    PROD_VOCACIONAL_75,
    PROD_VOCACIONAL_150,
    PROD_VOCACIONAL_PREMIUM,
    get_active_access_queryset,
    onboarding_status,
    slugs_equivalentes,
    user_has_demo_access,
    user_has_produto,
)
from apps.vocacional.models_consent import Consentimento


class ProductPermissionCleanupTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="aluno@example.com",
            password="teste123",
            first_name="Aluno",
            last_name="Teste",
        )

    def _grant(self, slug: str, nome: str | None = None) -> None:
        produto = Produto.objects.create(slug=slug, nome=nome or slug)
        Acesso.objects.create(user=self.user, produto=produto, origem="teste")

    def test_bonus_guia_keeps_base_product_equivalences(self):
        self._grant("guia_descoberta", "Guia Descoberta")

        self.assertTrue(user_has_produto(self.user, PROD_GUIA))
        self.assertTrue(user_has_produto(self.user, PROD_VOCACIONAL_75))
        self.assertTrue(user_has_produto(self.user, PROD_SONHEMAISALTO))

    def test_vocacional_150_accepts_only_intermediate_family_aliases(self):
        self._grant("passe1", "Passe 1")

        self.assertTrue(user_has_produto(self.user, PROD_VOCACIONAL_150))
        self.assertFalse(user_has_produto(self.user, PROD_VOCACIONAL_PREMIUM))

    def test_vocacional_premium_accepts_pass_2_and_pass_3_aliases(self):
        self._grant("passe2", "Passe 2")

        self.assertTrue(user_has_produto(self.user, PROD_VOCACIONAL_PREMIUM))
        self.assertFalse(user_has_produto(self.user, PROD_VOCACIONAL_150))

    def test_vocacional_150_aliases_do_not_include_passe2_or_passe3(self):
        aliases = slugs_equivalentes(PROD_VOCACIONAL_150)

        self.assertIn("passe1", aliases)
        self.assertNotIn("passe2", aliases)
        self.assertNotIn("passe3", aliases)

    def test_vocacional_premium_aliases_include_only_premium_passes(self):
        aliases = slugs_equivalentes(PROD_VOCACIONAL_PREMIUM)

        self.assertIn("passe2", aliases)
        self.assertIn("passe3", aliases)
        self.assertNotIn("passe1", aliases)

    def test_demo_access_liberates_runtime_without_falsifying_real_status(self):
        InstitutionalDemoAccess.objects.create(
            user=self.user,
            institution_name="Escola Demo",
            expires_at=timezone.now() + timedelta(days=7),
        )

        runtime_status = onboarding_status(self.user)
        semantic_status = onboarding_status(self.user, allow_demo=False)

        self.assertTrue(user_has_demo_access(self.user))
        self.assertTrue(runtime_status["has_onboarding"])
        self.assertFalse(semantic_status["has_onboarding"])
        self.assertTrue(user_has_produto(self.user, PROD_VOCACIONAL_75))
        self.assertFalse(user_has_produto(self.user, PROD_VOCACIONAL_75, allow_demo=False))
        self.assertIsNone(next_step(self.user))

    def test_expired_demo_access_does_not_bypass_runtime(self):
        InstitutionalDemoAccess.objects.create(
            user=self.user,
            institution_name="Escola Expirada",
            starts_at=timezone.now() - timedelta(days=10),
            expires_at=timezone.now() - timedelta(days=1),
        )

        runtime_status = onboarding_status(self.user)

        self.assertFalse(user_has_demo_access(self.user))
        self.assertFalse(runtime_status["has_onboarding"])

    def test_first_access_redirects_to_intro_before_portal(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("portal"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/portal_demo.html")

    def test_completing_intro_marks_progress_and_redirects(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portal_demo"),
            {"next_product": "sonhe-mais-alto"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("portal_next_step"), response["Location"])
        self.assertTrue(
            IntroPresentationProgress.objects.filter(
                user=self.user,
                completed_at__isnull=False,
            ).exists()
        )

    def test_next_step_guides_user_to_guide_feedback_when_guide_exists(self):
        guide_product = Produto.objects.create(slug="sonhemaisalto_guia", nome="Guia")
        Acesso.objects.create(user=self.user, produto=guide_product, origem="teste")
        IntroPresentationProgress.objects.create(
            user=self.user,
            completed_at=timezone.now(),
        )
        Consentimento.objects.create(
            user=self.user,
            nome="Aluno Teste",
            email=self.user.email,
            aceito=True,
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("portal_next_step"),
            {"next_product": "vocacional"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/portal_next_step.html")
        self.assertContains(response, "Responder a Avaliacao do Guia")

    def test_next_step_redirects_to_target_when_onboarding_is_complete(self):
        guide_product = Produto.objects.create(slug="sonhemaisalto_guia", nome="Guia")
        Acesso.objects.create(user=self.user, produto=guide_product, origem="teste")
        IntroPresentationProgress.objects.create(
            user=self.user,
            completed_at=timezone.now(),
        )
        Consentimento.objects.create(
            user=self.user,
            nome="Aluno Teste",
            email=self.user.email,
            aceito=True,
        )
        from apps.vocacional.models import AvaliacaoGuia

        AvaliacaoGuia.objects.create(
            user=self.user,
            aceite_termos=True,
            status="concluida",
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("portal_next_step"),
            {"next_product": "vocacional"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse("produto_resolver", args=["vocacional"]),
        )

    def test_completed_intro_stops_forcing_presentation(self):
        IntroPresentationProgress.objects.create(
            user=self.user,
            completed_at=timezone.now(),
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("portal"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/portal.html")

    def test_demo_active_does_not_repeat_intro_after_completion(self):
        IntroPresentationProgress.objects.create(
            user=self.user,
            completed_at=timezone.now(),
        )
        InstitutionalDemoAccess.objects.create(
            user=self.user,
            institution_name="Escola Demo",
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("portal"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/portal.html")

    def test_legacy_consent_counts_as_terms_for_status_reading(self):
        Consentimento.objects.create(
            user=self.user,
            nome="Aluno Teste",
            email=self.user.email,
            aceito=True,
        )

        status = onboarding_status(self.user, allow_demo=False)

        self.assertTrue(status["has_termos"])
        self.assertTrue(status["has_consent"])
        self.assertTrue(status["has_legal"])

    def test_active_access_queryset_includes_future_expiration(self):
        produto = Produto.objects.create(slug="vocacional75plus", nome="Intermediario")
        acesso = Acesso.objects.create(
            user=self.user,
            produto=produto,
            origem="legado",
            expires_at=timezone.now() + timedelta(days=3),
        )

        qs = get_active_access_queryset(self.user)

        self.assertIn(acesso, list(qs))


class GovernanceAccessConsistencyTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="teste123",
            is_staff=True,
            is_superuser=True,
        )
        self.user = User.objects.create_user(
            email="alvo@example.com",
            password="teste123",
        )
        self.produto = Produto.objects.create(slug="vocacional75plus", nome="Intermediario")

    def test_governance_grant_does_not_duplicate_future_active_access(self):
        Acesso.objects.create(
            user=self.user,
            produto=self.produto,
            origem="legado",
            expires_at=timezone.now() + timedelta(days=2),
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("portal_dashboard"),
            {
                "action": "grant",
                "user_id": str(self.user.id),
                "produto_ids": [str(self.produto.id)],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Acesso.objects.filter(user=self.user, produto=self.produto).count(),
            1,
        )

    def test_governance_revoke_reaches_future_active_access(self):
        acesso = Acesso.objects.create(
            user=self.user,
            produto=self.produto,
            origem="legado",
            expires_at=timezone.now() + timedelta(days=2),
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("portal_dashboard"),
            {
                "action": "revoke",
                "user_id": str(self.user.id),
                "produto_ids": [str(self.produto.id)],
            },
        )

        self.assertEqual(response.status_code, 302)
        acesso.refresh_from_db()
        self.assertLessEqual(acesso.expires_at, timezone.now())


class LegacyInstitutionLinkCleanupTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="aluno-legado@example.com",
            password="teste123",
            perfil="ALUNO",
        )
        self.institution = Instituicao.objects.create(
            nome="Escola Legada",
            tipo="escola",
        )
        self.vinculo = InstituicaoUsuario.objects.create(
            instituicao=self.institution,
            usuario=self.user,
            papel="aluno",
            ativo=True,
            observacoes="ra: 12345",
        )

    def test_cleanup_command_dry_run_does_not_mutate(self):
        stdout = StringIO()

        call_command("sanear_vinculos_aluno_legados", stdout=stdout)

        self.user.refresh_from_db()
        self.vinculo.refresh_from_db()
        self.assertIsNone(self.user.instituicao)
        self.assertTrue(self.vinculo.ativo)

    def test_cleanup_command_apply_assigns_instituicao_and_inactivates_link(self):
        stdout = StringIO()

        call_command("sanear_vinculos_aluno_legados", "--apply", stdout=stdout)

        self.user.refresh_from_db()
        self.vinculo.refresh_from_db()
        self.assertEqual(self.user.instituicao, self.institution)
        self.assertFalse(self.vinculo.ativo)
        self.assertIn("Migrado para Usuario.instituicao", self.vinculo.observacoes)


class GovernanceImportTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            email="admin-import@example.com",
            password="teste123",
            is_staff=True,
            is_superuser=True,
        )
        self.institution = Instituicao.objects.create(
            nome="Escola Importacao",
            tipo="escola",
        )

    def test_contact_csv_parser_requires_and_normalizes_role(self):
        uploaded = SimpleUploadedFile(
            "contatos.csv",
            b"nome,sobrenome,email,papel,principal\nAna,Silva,ana@example.com,contato_financ,sim\n",
            content_type="text/csv",
        )

        preview = _parse_governance_import_csv(
            uploaded,
            selected_institution=self.institution,
            import_kind="contacts",
        )

        self.assertFalse(preview["errors"])
        self.assertEqual(preview["rows"][0]["papel"], "contato_financeiro")
        self.assertTrue(preview["rows"][0]["principal"])

    def test_student_import_assigns_instituicao_directly_to_usuario(self):
        self.client.force_login(self.admin)
        csv_file = SimpleUploadedFile(
            "alunos.csv",
            b"nome,sobrenome,email,ra\nBruno,Souza,bruno@example.com,123\n",
            content_type="text/csv",
        )

        preview_response = self.client.post(
            reverse("portal_dashboard"),
            {
                "action": "import_preview",
                "import_kind": "students",
                "import_institution_id": str(self.institution.id),
                "csv_file": csv_file,
            },
        )
        self.assertEqual(preview_response.status_code, 302)

        commit_response = self.client.post(
            reverse("portal_dashboard"),
            {
                "action": "import_commit",
                "import_kind": "students",
            },
        )
        self.assertEqual(commit_response.status_code, 302)

        user = get_user_model().objects.get(email="bruno@example.com")
        self.assertEqual(user.instituicao, self.institution)
        self.assertEqual(user.perfil, "ALUNO")
        self.assertFalse(
            InstituicaoUsuario.objects.filter(
                instituicao=self.institution,
                usuario=user,
                papel="aluno",
            ).exists()
        )
