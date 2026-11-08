from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t11_operation_planner", HERE / "plan.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CandidateOperationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.build()

    def setUp(self):
        self.router = module.selected_router()
        self.signer = Ed25519PrivateKey.generate()
        self.now = datetime(2026, 10, 23, tzinfo=timezone.utc)
        self.planner = module.CandidatePlanner(module.ROOT, self.router, module.MATRIX,
                                               self.signer.public_key(), clock=lambda: self.now)
        self.route = self.planner.consumer.matrix["routes"][0]
        self.request = module.request_for(self.planner, self.route)
        self.grant = module.fixture_grant(self.signer, self.route, self.now)

    def unchanged(self):
        self.assertEqual(self.planner.plans, [])
        self.assertEqual(self.planner.heads, {})
        self.assertEqual(self.planner.identities, set())

    def test_all_230_candidate_operation_plans(self):
        result = self.result
        self.assertEqual(result["technical_operation_plans"], 230)
        self.assertEqual(sum(result["by_scope"].values()), 230)
        self.assertEqual(sorted(result["by_scope"].values()), [1, 1, 1, 1, 6, 220])
        self.assertEqual(len({p["plan"]["member_ref"] for p in result["plans"]}), 230)
        self.assertTrue(all(p["plan"]["proposed_operation"] == "admit" and
                            p["plan"]["planning_state"] == "candidate-prepared" and
                            p["plan"]["authority_effect"] == "none" for p in result["plans"]))
        self.assertEqual(result["native_prepare_calls"], 0)
        self.assertEqual(result["original_successful_operational_routes"], 0)
        self.assertFalse(result["T11_complete"])

    def test_one_member_positive_and_duplicate_refusal(self):
        first = self.planner.prepare(self.request, self.grant)
        self.assertEqual(first["plan"]["member_ref"], self.route["member_ref"])
        self.assertNotEqual(first["previous_head"], first["resulting_head"])
        second = module.request_for(self.planner, self.route)
        with self.assertRaisesRegex(module.PlanRefusal, "duplicate candidate identity"):
            self.planner.prepare(second, self.grant)
        self.assertEqual(len(self.planner.plans), 1)
        self.assertEqual(self.planner.head(self.route["body_scope_ref"]), first["resulting_head"])

    def test_wrong_scope_effect_target_and_stale_head_refuse_before_consumer(self):
        for field, value, reason in (
            ("scope_ref", "scope:other", "outside exact scope"),
            ("operation", "revise", "effect or target"),
            ("category", "typed-relation", "effect or target"),
            ("version_ref", "implementation:other@1", "effect or target"),
            ("body_sha256", "0" * 64, "effect or target"),
            ("expected_head", "0" * 64, "stale candidate plan head"),
        ):
            with self.subTest(field=field):
                request = {**self.request, field: value}
                with self.assertRaisesRegex(module.PlanRefusal, reason):
                    self.planner.prepare(request, self.grant)
                self.unchanged()

    def test_wrong_signer_refuses_without_plan(self):
        wrong = module.fixture_grant(Ed25519PrivateKey.generate(), self.route, self.now)
        with self.assertRaises(self.router.RouteRefusal):
            self.planner.prepare(self.request, wrong)
        self.unchanged()

    def test_changed_selected_body_refuses_without_plan(self):
        original = self.router.read_binding

        def substitute(root, binding):
            raw = original(root, binding)
            if binding == self.route["body_binding"]:
                body = json.loads(raw)
                body["name"] = "substituted"
                return module.canonical(body)
            return raw

        with patch.object(self.router, "read_binding", side_effect=substitute):
            with self.assertRaisesRegex(module.PlanRefusal, "consumed bytes"):
                self.planner.prepare(self.request, self.grant)
        self.unchanged()

    def test_changed_selected_router_refuses_before_load(self):
        with patch.object(module, "ROUTER", {**module.ROUTER, "sha256": "0" * 64}):
            with self.assertRaisesRegex(module.PlanRefusal, "selected router code changed"):
                module.selected_router()

    def test_unselected_request_field_refuses(self):
        with self.assertRaisesRegex(module.PlanRefusal, "closed operation request"):
            self.planner.prepare({**self.request, "grant_override": True}, self.grant)
        self.unchanged()

    def test_optimized_replay_is_deterministic(self):
        process = subprocess.run([sys.executable, "-O", "-B", str(HERE / "plan.py")],
                                 capture_output=True, text=True, check=True, timeout=90)
        self.assertEqual(json.loads(process.stdout), self.result)


if __name__ == "__main__":
    unittest.main()
