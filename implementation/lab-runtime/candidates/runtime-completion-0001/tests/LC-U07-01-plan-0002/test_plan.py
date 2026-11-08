"""Inert original-registry fixture; no protected plan or producer import."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[6]
MODULE = ROOT / "implementation/lab-runtime/candidates/runtime-completion-0001/workflow/plan_v2.py"
REGISTRY_SOURCE = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v30/workflow_output_registry.py"
EXPECTED_REGISTRY = "90a0a0392ed3c53f2e4aa35c79043b1459fe382bb457497675635213afaf0f92"
spec = importlib.util.spec_from_file_location("inert_route_plan", MODULE)
route_plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route_plan)


def registry():
    source = ast.parse(REGISTRY_SOURCE.read_text())
    rows = next(ast.literal_eval(node.value) for node in source.body
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "REGISTRY"
                                                       for t in node.targets))
    if len(rows) != 28 or hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":"),
                                                   ensure_ascii=False).encode()).hexdigest() != EXPECTED_REGISTRY:
        raise RuntimeError("original registry selection changed")
    return rows


def binding(path):
    return {"path": path, "sha256": "a" * 64}


def fixture():
    selected = registry()
    routes = {}
    for n, (ref, row) in enumerate(selected.items()):
        routes[ref] = {"transition_ref": ref, "definition_binding": row["definition_binding"],
                       "allowed_output_carriers": row["output_carriers"].copy(),
                       "producer_binding": binding(row["original_producer_path"]),
                       "producer_entrypoint": "produce", "producer_instance_contract": "selected-instance",
                       "resolver_binding": binding("fixture/resolver.py"), "resolver_entrypoint": "resolve",
                       "invocation_ref": f"invocation-{n}", "invocation_input_binding": binding(f"fixture/input-{n}.json"),
                       "output_slot_ref": f"slot-{n}", "output_scope_ref": "scope", "output_custody": "selected",
                       "scope_contract_binding": binding(f"fixture/scope-{n}.json"),
                       "producer_control_binding": binding(f"fixture/control-{n}.json"),
                       "authority_stage": "technical-contract"}
    return selected, {"schema_version": "lab-private-workflow-output-route-plan/v5-inert-candidate",
                      "principal_ref": "principal", "scope_ref": "scope", "source_cut": "cut",
                      "registry_sha256": EXPECTED_REGISTRY, "authority_effect": "none", "routes": routes}


def check(selected, plan):
    return route_plan.validate(plan, selected, expected_registry_sha256=EXPECTED_REGISTRY,
                               principal_ref="principal", scope_ref="scope", source_cut="cut")


class RoutePlanTests(unittest.TestCase):
    def test_exact_original_28_inert(self):
        selected, plan = fixture()
        self.assertEqual(check(selected, plan), {"schema_version": "lab-inert-route-validation/v1",
                                                 "registry_sha256": EXPECTED_REGISTRY, "route_count": 28,
                                                 "authority_effect": "none", "producer_invocations": 0})

    def test_omitted_extra_and_duplicate_route_refuse(self):
        selected, plan = fixture()
        plan["routes"].pop(next(iter(plan["routes"])))
        with self.assertRaisesRegex(route_plan.PlanRefusal, "ROUTE_COVERAGE"): check(selected, plan)
        selected, plan = fixture()
        plan["routes"]["extra"] = next(iter(plan["routes"].values()))
        with self.assertRaisesRegex(route_plan.PlanRefusal, "ROUTE_COVERAGE"): check(selected, plan)
        selected, plan = fixture()
        keys = list(plan["routes"])
        plan["routes"][keys[1]]["output_slot_ref"] = plan["routes"][keys[0]]["output_slot_ref"]
        with self.assertRaisesRegex(route_plan.PlanRefusal, "ROUTE_DUPLICATE"): check(selected, plan)

    def test_wrong_carrier_definition_and_origin_refuse(self):
        for key, value, code in (("allowed_output_carriers", ["wrong"], "ROUTE_CARRIERS"),
                                 ("definition_binding", binding("wrong.json"), "ROUTE_DEFINITION"),
                                 ("producer_binding", binding("fixture/wrong.py"), "ROUTE_PRODUCER_ORIGIN")):
            selected, plan = fixture()
            next(iter(plan["routes"].values()))[key] = value
            with self.assertRaisesRegex(route_plan.PlanRefusal, code): check(selected, plan)

    def test_scope_cut_registry_and_authority_refuse(self):
        for key, value, code in (("principal_ref", "other", "PLAN_SCOPE_CUT"),
                                 ("scope_ref", "other", "PLAN_SCOPE_CUT"),
                                 ("source_cut", "other", "PLAN_SCOPE_CUT"),
                                 ("authority_effect", "write", "PLAN_PROFILE"),
                                 ("registry_sha256", "b" * 64, "REGISTRY_ORIGINAL")):
            selected, plan = fixture()
            plan[key] = value
            with self.assertRaisesRegex(route_plan.PlanRefusal, code): check(selected, plan)
        selected, plan = fixture()
        next(iter(selected.values()))["family"] = "changed"
        with self.assertRaisesRegex(route_plan.PlanRefusal, "REGISTRY_ORIGINAL"): check(selected, plan)

    def test_callable_and_hidden_effect_cannot_enter_preflight(self):
        class Bomb:
            called = False
            def __call__(self):
                self.called = True
                raise RuntimeError("producer invoked")
        selected, plan = fixture()
        bomb = Bomb()
        next(iter(plan["routes"].values()))["producer_instance_contract"] = bomb
        with self.assertRaisesRegex(route_plan.PlanRefusal, "PLAN_DATA"): check(selected, plan)
        self.assertFalse(bomb.called)

    def test_hostile_equality_never_runs_during_preflight(self):
        class Hostile:
            called = False
            def __eq__(self, other):
                self.called = True
                raise RuntimeError("hidden effect")
        for target in ("schema_version", "authority_stage"):
            selected, plan = fixture()
            hostile = Hostile()
            if target == "schema_version":
                plan[target] = hostile
            else:
                next(iter(plan["routes"].values()))[target] = hostile
            with self.assertRaisesRegex(route_plan.PlanRefusal, "PLAN_DATA"):
                check(selected, plan)
            self.assertFalse(hostile.called)


if __name__ == "__main__":
    unittest.main()
