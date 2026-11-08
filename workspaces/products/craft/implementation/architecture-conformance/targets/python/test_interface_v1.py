import copy
import dataclasses
import importlib.util
import json
import pathlib
import sys
import unittest

MODULE_PATH = pathlib.Path(__file__).with_name("remaining_types") / "interface_v1.py"
SPEC = importlib.util.spec_from_file_location("interface_v1", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def baseline() -> dict:
    descriptor = {
        "contract_id":"SettlementPort", "exact_version":"1.2.0", "compatibility_direction":"consumer-to-provider",
        "inside_boundary":"settlement-domain", "outside_boundary":"settlement-consumers",
        "domain_contract_id":"SettlementPort/domain-v1", "transport_adapter_id":"SettlementHttpAdapter/v1",
        "exposed_bindings":[
            {"binding_id":"completeSettlement","kind":"Operation","public_contract_id":"CompleteSettlement/v1"},
            {"binding_id":"findSettlement","kind":"Query","public_contract_id":"FindSettlement/v1"},
        ],
        "mapping_obligations":[
            {"binding_id":"completeSettlement","direction":"request","mapping_id":"CompleteSettlementRequestMap/v1"},
            {"binding_id":"completeSettlement","direction":"response","mapping_id":"SettlementResponseMap/v1"},
            {"binding_id":"findSettlement","direction":"response","mapping_id":"SettlementResponseMap/v1"},
        ],
    }
    observation = {
        **descriptor, "version":"1.2.0",
        "exposed_bindings":[{**item,"internal_type_ids":[]} for item in descriptor["exposed_bindings"]],
        "consumer_routes":[{"consumer_id":"settlement-http-client","side":"outside","adapter_id":"SettlementHttpAdapter/v1"}],
        "compatibility_checks":[
            {"consumer_version":"1.0.0","provider_version":"1.2.0","accepted":True},
            {"consumer_version":"2.0.0","provider_version":"1.2.0","accepted":False},
        ],
    }
    return {"descriptor":descriptor,"observation":observation,
            "w3_descriptor":{"contract_id":"SettlementPort","exact_version":"1.2.0","exposed_bindings":[{"binding_id":"completeSettlement","kind":"Operation"},{"binding_id":"findSettlement","kind":"Query"}]},
            "w3_observation":{"contract_id":"SettlementPort","version":"1.2.0","exposed_bindings":[{"binding_id":"completeSettlement","kind":"Operation"},{"binding_id":"findSettlement","kind":"Query"}]}}


class InterfaceV1Test(unittest.TestCase):
    def test_native_boundary_is_frozen_and_normalizes(self) -> None:
        boundary = MODULE.VersionedBoundary("SettlementPort", "1.2.0", "domain", "outside", "Port/v1", "Http/v1")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            boundary.version = "2.0.0"
        result = MODULE.evaluate_case(baseline())
        self.assertEqual(result["portable"]["exposed_bindings"], ["Operation:completeSettlement", "Query:findSettlement"])
        self.assertEqual(result["native_evidence"]["language"], "python")

    def test_replays_all_ten_family_semantic_controls(self) -> None:
        root = pathlib.Path(__file__).parents[3]
        hostile_dir = root / "architecture-conformance/families/versioned-interface-boundary/hostiles"
        semantic = sorted(path for path in hostile_dir.glob("*.json") if json.loads(path.read_text())["hostile_class"] == "type-semantic")
        self.assertEqual(len(semantic), 10)
        for path in semantic:
            hostile = json.loads(path.read_text())
            case = baseline()
            case["observation"].update(copy.deepcopy(hostile["mutation"]))
            verdict, findings = MODULE.evaluate_interface(case["descriptor"], case["observation"])
            self.assertEqual((verdict, findings), ("reject", (hostile["expected_code"],)), hostile["hostile_id"])


if __name__ == "__main__":
    unittest.main()
