from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from apps.vocacional.models import AvaliacaoGuia
from apps.vocacional.models_consent import Consentimento


class RegistroLegalTests(TestCase):
    def test_registration_requires_termos_and_privacidade(self):
        response = self.client.post(
            reverse("contas:registrar"),
            {
                "first_name": "Zenilton",
                "last_name": "Sem Nada",
                "email": "zenilton@example.com",
                "password1": "SenhaForte123",
                "password2": "SenhaForte123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(email="zenilton@example.com").exists()
        )

    def test_registration_persists_termos_and_consentimento(self):
        response = self.client.post(
            reverse("contas:registrar"),
            {
                "first_name": "Zenilton",
                "last_name": "Sem Nada",
                "email": "zenilton@example.com",
                "password1": "SenhaForte123",
                "password2": "SenhaForte123",
                "aceite_termos": "on",
                "aceite_privacidade": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("contas:confirmacao_email_enviada"))
        user = get_user_model().objects.get(email="zenilton@example.com")
        ag = AvaliacaoGuia.objects.get(user=user)
        consent = Consentimento.objects.get(user=user)

        self.assertFalse(user.is_active)
        self.assertTrue(ag.aceite_termos)
        self.assertTrue(consent.aceito)
        self.assertIsNone(consent.revogado_em)
        self.assertEqual(len(mail.outbox), 1)

    def test_confirmar_email_ativa_conta(self):
        user = get_user_model().objects.create_user(
            email="zenilton@example.com",
            password="SenhaForte123",
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            reverse("contas:confirmar_email", args=[uid, token])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("portal"))
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.email_confirmado_em)
