from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.contas.models_acessos import Acesso, Produto
from apps.core.permissions import (
    PROD_GUIA,
    PROD_SONHEMAISALTO,
    PROD_VOCACIONAL_75,
    PROD_VOCACIONAL_150,
    PROD_VOCACIONAL_PREMIUM,
    slugs_equivalentes,
    user_has_produto,
)


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
