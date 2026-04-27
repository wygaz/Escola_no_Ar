import inspect

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from .interpretacao import InterpretationInput, build_interpretation_payload, classify_interpretation_scenario
from .models import Avaliacao, Dimensao, Pergunta, Resultado
from .refinamento import get_pass_qids, resolve_refinement_focus_slugs, select_refinement_round_questions
from .views import (
    _canonical_top3_slugs,
    _create_fresh_avaliacao,
    _get_latest_fc_summary,
    _get_latest_result_avaliacao,
    _has_forced_choice_progress,
    comparacoes_top3,
    entrada,
)


@override_settings(VOC_REF_ROUND_SIZE=5)
class RefinamentoSelectionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="refinamento@example.com",
            password="senha-segura-123",
            nome="Teste",
        )
        self.avaliacao = Avaliacao.objects.create(usuario=self.user, status="rascunho")

        self.dim_a = Dimensao.objects.create(nome="Engenharia", slug="engenharia")
        self.dim_b = Dimensao.objects.create(nome="Software", slug="software")
        self.dim_c = Dimensao.objects.create(nome="Design", slug="design")
        self.dim_d = Dimensao.objects.create(nome="Saude", slug="saude")

        self.perguntas = []
        ordem = 1
        for dim in (self.dim_a, self.dim_b, self.dim_c, self.dim_d):
            for idx in range(1, 7):
                self.perguntas.append(
                    Pergunta.objects.create(
                        dimensao=dim,
                        codigo=f"{dim.slug}_{idx}",
                        enunciado=f"Pergunta {idx} de {dim.nome}",
                        ordem=ordem,
                        tipo="likert",
                        ativo=True,
                    )
                )
                ordem += 1

        Resultado.objects.create(avaliacao=self.avaliacao, dimensao=self.dim_a, pontuacao=95, percentual=95, nivel="alto")
        Resultado.objects.create(avaliacao=self.avaliacao, dimensao=self.dim_b, pontuacao=90, percentual=90, nivel="alto")
        Resultado.objects.create(avaliacao=self.avaliacao, dimensao=self.dim_c, pontuacao=85, percentual=85, nivel="alto")
        Resultado.objects.create(avaliacao=self.avaliacao, dimensao=self.dim_d, pontuacao=10, percentual=10, nivel="baixo")

    def test_resolve_refinement_focus_slugs_uses_resultado_top3(self):
        focus = resolve_refinement_focus_slugs(self.avaliacao, Pergunta.objects.filter(ativo=True), limit=3)
        self.assertEqual(focus, ["engenharia", "software", "design"])

    def test_select_refinement_round_questions_stays_inside_focus(self):
        qids = select_refinement_round_questions(
            self.avaliacao,
            Pergunta.objects.filter(ativo=True).select_related("dimensao"),
            used_ids=set(),
            focus_slugs=["engenharia", "software", "design"],
        )
        self.assertEqual(len(qids), 5)

        slugs = set(
            Pergunta.objects.filter(id__in=qids)
            .select_related("dimensao")
            .values_list("dimensao__slug", flat=True)
        )
        self.assertTrue(slugs.issubset({"engenharia", "software", "design"}))
        self.assertNotIn("saude", slugs)

    def test_get_pass_qids_excludes_used_questions_and_records_round_plan(self):
        perguntas_qs = Pergunta.objects.filter(ativo=True).select_related("dimensao")

        first_round = get_pass_qids(self.avaliacao, 1, perguntas_qs)
        self.assertEqual(len(first_round), 5)

        self.avaliacao.ref_data = {
            **(self.avaliacao.ref_data or {}),
            "passes": {"1": {"top": ["engenharia", "software", "design"]}},
        }
        self.avaliacao.save(update_fields=["ref_data"])

        second_round = get_pass_qids(self.avaliacao, 2, perguntas_qs)
        self.assertEqual(len(second_round), 5)
        self.assertTrue(set(first_round).isdisjoint(set(second_round)))

        self.avaliacao.refresh_from_db()
        round_plan = (self.avaliacao.ref_data or {}).get("round_plan") or {}
        self.assertEqual(round_plan.get("1", {}).get("focus_top3"), ["engenharia", "software", "design"])
        self.assertEqual(round_plan.get("2", {}).get("focus_top3"), ["engenharia", "software", "design"])

    def test_canonical_top3_slugs_respects_final_ranking(self):
        self.avaliacao.ref_data = {
            "final": {
                "ranking": ["design", "engenharia", "software", "saude"]
            }
        }
        self.avaliacao.save(update_fields=["ref_data"])

        self.assertEqual(
            _canonical_top3_slugs(self.avaliacao),
            ["design", "engenharia", "software"],
        )


class ReinicioAvaliacaoTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="reinicio@example.com",
            password="senha-segura-123",
            nome="Reinicio",
        )

    def test_create_fresh_avaliacao_cancels_previous_drafts_and_creates_new_one(self):
        old_a = Avaliacao.objects.create(usuario=self.user, status="rascunho", ordem_ids="1,2,3", ref_data={"passes": {"1": {"top": ["x"]}}})
        old_b = Avaliacao.objects.create(usuario=self.user, status="rascunho", ordem_ids="4,5,6", ref_data={"final": {"top3": ["y"]}})

        fresh = _create_fresh_avaliacao(self.user)

        old_a.refresh_from_db()
        old_b.refresh_from_db()

        self.assertEqual(old_a.status, "cancelada")
        self.assertEqual(old_b.status, "cancelada")
        self.assertEqual(fresh.status, "rascunho")
        self.assertEqual(fresh.ordem_ids, "")
        self.assertEqual(fresh.ref_data, {})


class VocacionalResumeRoutingTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="resume@example.com",
            password="senha-segura-123",
            nome="Resume",
        )
        self.factory = RequestFactory()
        self.raw_entrada = inspect.unwrap(entrada)

    def test_latest_result_avaliacao_prefers_preview_draft_over_older_completed(self):
        older_done = Avaliacao.objects.create(
            usuario=self.user,
            status="concluida",
        )
        newer_preview = Avaliacao.objects.create(
            usuario=self.user,
            status="rascunho",
        )
        dim = Dimensao.objects.create(nome="Esportes", slug="esportes")
        Resultado.objects.create(
            avaliacao=older_done,
            dimensao=dim,
            pontuacao=80,
            percentual=80,
            nivel="alto",
        )
        Resultado.objects.create(
            avaliacao=newer_preview,
            dimensao=dim,
            pontuacao=90,
            percentual=90,
            nivel="alto",
        )

        latest = _get_latest_result_avaliacao(self.user)
        self.assertEqual(latest.pk, newer_preview.pk)

    def test_entrada_redirects_to_latest_preview_result_when_it_exists(self):
        preview = Avaliacao.objects.create(
            usuario=self.user,
            status="rascunho",
        )
        dim = Dimensao.objects.create(nome="Financas", slug="financas")
        Resultado.objects.create(
            avaliacao=preview,
            dimensao=dim,
            pontuacao=88,
            percentual=88,
            nivel="alto",
        )

        request = self.factory.get("/vocacional/entrada/")
        request.user = self.user
        response = self.raw_entrada(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/vocacional/resultado/{preview.pk}/")


class InterpretacaoVocacionalTests(TestCase):
    def test_classify_well_defined_profile(self):
        data = InterpretationInput(
            user_name="Wanderley",
            top1_nome="Desenvolvimento de Software e IA",
            top2_nome="Engenharia e Inovação",
            top3_nome="Design e Moda",
            gap_12=0.18,
            gap_13=0.24,
            confidence_band="alta",
            adjacency_profile="moderadamente_proximas",
        )
        self.assertEqual(classify_interpretation_scenario(data), "perfil_bem_definido")

    def test_classify_proximate_core_profile(self):
        data = InterpretationInput(
            user_name="Wanderley",
            top1_nome="Desenvolvimento de Software e IA",
            top2_nome="Engenharia e Inovação",
            top3_nome="Robótica",
            gap_12=0.05,
            gap_13=0.12,
            confidence_band="moderada",
            adjacency_profile="muito_proximas",
            stable_top3=True,
        )
        payload = build_interpretation_payload(data)
        self.assertEqual(payload["scenario"], "resultado_estabilizado")
        self.assertIn("perfil ficou mais definido", payload["summary"])

    def test_classify_open_profile_with_mentoring(self):
        data = InterpretationInput(
            user_name="Wanderley",
            top1_nome="Turismo",
            top2_nome="Comunicação",
            top3_nome="Sociais",
            gap_12=0.03,
            gap_13=0.05,
            confidence_band="aberta",
            adjacency_profile="muito_proximas",
            round_count=4,
            max_round_reached=True,
            non_recommended_areas=("Direito", "Finanças"),
        )
        payload = build_interpretation_payload(data)
        self.assertEqual(payload["scenario"], "encaminhar_mentoria")
        self.assertTrue(payload["show_external_factors"])
        self.assertTrue(payload["show_mentoring_offer"])
        self.assertIn("Direito", payload["non_recommended_note"])


@override_settings(VOC_FC_BLOCKS_TOP3=10)
class ForcedChoiceProgressionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="fc@example.com",
            password="senha-segura-123",
            nome="Forced Choice",
        )
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        self.factory = RequestFactory()
        self.raw_view = inspect.unwrap(comparacoes_top3)

        self.dim_a = Dimensao.objects.create(nome="Engenharia", slug="engenharia")
        self.dim_b = Dimensao.objects.create(nome="Software", slug="software")
        self.dim_c = Dimensao.objects.create(nome="Design", slug="design")

        ordem = 1
        for dim in (self.dim_a, self.dim_b, self.dim_c):
            for idx in range(1, 4):
                Pergunta.objects.create(
                    dimensao=dim,
                    codigo=f"{dim.slug}_{idx}",
                    enunciado=f"Pergunta {idx} de {dim.nome}",
                    ordem=ordem,
                    tipo="likert",
                    ativo=True,
                )
                ordem += 1

        self.avaliacao = Avaliacao.objects.create(
            usuario=self.user,
            status="concluida",
            ref_data={"final": {"ranking": ["engenharia", "software", "design"]}},
        )

        Resultado.objects.create(avaliacao=self.avaliacao, dimensao=self.dim_a, pontuacao=95, percentual=95, nivel="alto")
        Resultado.objects.create(avaliacao=self.avaliacao, dimensao=self.dim_b, pontuacao=90, percentual=90, nivel="alto")
        Resultado.objects.create(avaliacao=self.avaliacao, dimensao=self.dim_c, pontuacao=85, percentual=85, nivel="alto")

    def _prepare_request(self, request):
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()
        setattr(request, "_messages", FallbackStorage(request))
        request.user = self.user
        return request

    def test_forced_choice_does_not_reset_when_available_blocks_are_fewer_than_target(self):
        get_request = self._prepare_request(
            self.factory.get(f"/vocacional/comparacoes/{self.avaliacao.pk}/")
        )
        response = self.raw_view(get_request, self.avaliacao.pk)
        self.assertEqual(response.status_code, 200)

        self.avaliacao.refresh_from_db()
        fc = (self.avaliacao.ref_data or {}).get("fc_top3") or {}
        self.assertEqual(fc.get("block_count"), 3)
        self.assertEqual(len(fc.get("blocks") or []), 3)

        post_request = self._prepare_request(
            self.factory.post(
                f"/vocacional/comparacoes/{self.avaliacao.pk}/",
                data={"pick": "A"},
            )
        )
        post_response = self.raw_view(post_request, self.avaliacao.pk)
        self.assertEqual(post_response.status_code, 302)

        self.avaliacao.refresh_from_db()
        fc = (self.avaliacao.ref_data or {}).get("fc_top3") or {}
        self.assertEqual(fc.get("answers"), ["A"])

        second_get_request = self._prepare_request(
            self.factory.get(f"/vocacional/comparacoes/{self.avaliacao.pk}/")
        )
        second_response = self.raw_view(second_get_request, self.avaliacao.pk)
        self.assertEqual(second_response.status_code, 200)

        self.avaliacao.refresh_from_db()
        fc = (self.avaliacao.ref_data or {}).get("fc_top3") or {}
        self.assertEqual(fc.get("answers"), ["A"])
        self.assertEqual(len(fc.get("blocks") or []), 3)

    def test_has_forced_choice_progress_when_next_round_is_open(self):
        self.avaliacao.ref_data = {
            "fc_top3": {
                "rounds_done": 1,
                "active_round": 2,
                "answers": [],
                "done": False,
            }
        }
        self.avaliacao.save(update_fields=["ref_data"])

        self.assertTrue(_has_forced_choice_progress(self.avaliacao))

    def test_get_latest_fc_summary_prefers_history(self):
        self.avaliacao.ref_data = {
            "fc_top3": {
                "weighted_scores": {"engenharia": 1.2},
            },
            "fc_top3_history": {
                "1": {"weighted_scores": {"engenharia": 1.2}},
                "2": {"weighted_scores": {"esportes": 5.0, "financas": 0.0}},
            },
        }
        self.avaliacao.save(update_fields=["ref_data"])

        summary = _get_latest_fc_summary(self.avaliacao.ref_data)
        self.assertEqual(summary.get("weighted_scores", {}).get("esportes"), 5.0)
