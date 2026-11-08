import copy
import dataclasses
import importlib.util
import json
import pathlib
import sys
import unittest

MODULE_PATH = pathlib.Path(__file__).with_name("remaining_types") / "event_v1.py"
SPEC = importlib.util.spec_from_file_location("event_v1", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def baseline() -> dict:
    descriptor = {"schema_version": "domainspec.past-tense-event/v1", "descriptor_id": "event.settlement-created-v1", "semantic_plan_epoch_id": "WP-RMT-002/S1/2026-08-16", "semantic_contract_digest": "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7", "event_name": "SettlementCreated", "tense": "past", "payload_contract_id": "SettlementCreatedPayload/v1", "payload_version": "1", "payload_immutable": True, "occurrence_identity_contract_id": "SettlementOccurrenceId/v1", "persistence_checkpoint": "durable-outbox-append", "publication_policy_id": "at-least-once-idempotent/v1", "consumer_contract_ids": ["SettlementProjectionConsumer/v1"], "distributed_exactly_once_claim": False, "durable_handle": "durable-occurrence/v1", "admission_status": "candidate", "authority_effect": "none"}
    handle = {"occurrence_id": "settlement:req-1", "persistence_checkpoint": "durable-outbox-append", "publication_attempt_id": "publish:req-1:1", "acknowledgement_state": "unknown", "delivery_observation": "at-least-once-observed", "consumption_observation": "accepted"}
    observed = {"event_name": "SettlementCreated", "tense": "past", "payload_contract_id": "SettlementCreatedPayload/v1", "payload_version": "1", "payload_mutable": False, "occurrence_identity_contract_id": "SettlementOccurrenceId/v1", "occurrence_id": "settlement:req-1", "occurrence_id_stable": True, "occurrence_id_reused": False, "durable_checkpoints": ["durable-outbox-append"], "publication_policy_id": "at-least-once-idempotent/v1", "publication_after_commit": True, "consumer_contract_ids": ["SettlementProjectionConsumer/v1"], "consumer_payload_checks": [{"consumer_contract_id": "SettlementProjectionConsumer/v1", "payload_version": "1", "accepted": True}], "distributed_exactly_once_claim": False, "durable_occurrence": handle, "s1_observation": None}
    return {"descriptor": descriptor, "observation": observed, "w3_descriptor": {"fact_checkpoint": "durable-outbox-append"}, "w3_observation": {"tense": "past", "durable_checkpoints": ["durable-outbox-append"], "distributed_exactly_once_claim": False}}


def apply_hostile(case: dict, hostile: dict) -> dict:
    result = copy.deepcopy(case)
    mutation = copy.deepcopy(hostile["mutation"])
    if "durable_occurrence" in mutation:
        result["observation"]["durable_occurrence"].update(mutation.pop("durable_occurrence"))
    result["observation"].update(mutation)
    return result


class EventV1Test(unittest.TestCase):
    def test_native_handle_is_frozen_and_retry_stable(self) -> None:
        handle = MODULE.DurableOccurrence("settlement:req-1", "durable-outbox-append", "publish:req-1:1", "unknown", "at-least-once-observed", "accepted")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            handle.occurrence_id = "other"
        result = MODULE.evaluate_case(baseline())
        self.assertEqual(result["portable"]["occurrence_id"], result["portable"]["retry_occurrence_id"])
        self.assertFalse(result["portable"]["distributed_exactly_once_claim"])
        incoherent = baseline(); incoherent["observation"]["durable_occurrence"]["occurrence_id"] = "other"
        with self.assertRaisesRegex(ValueError, "RMT_EVENT_DURABLE_HANDLE_INVALID"):
            MODULE.evaluate_case(incoherent)

    def test_replays_all_ten_base_semantic_controls(self) -> None:
        root = pathlib.Path(__file__).parents[3]
        hostile_dir = root / "architecture-conformance/families/past-tense-event/hostiles"
        semantic = sorted(path for path in hostile_dir.glob("*.json") if json.loads(path.read_text())["hostile_class"] == "type-semantic")
        self.assertEqual(len(semantic), 10)
        for path in semantic:
            hostile = json.loads(path.read_text())
            verdict, findings = MODULE.evaluate_event(*[apply_hostile(baseline(), hostile)[key] for key in ("descriptor", "observation")])
            self.assertEqual((verdict, findings), ("reject", (hostile["expected_code"],)), hostile["hostile_id"])

    def test_derives_all_nine_s1_controls_and_rejects_incoherent_residue(self) -> None:
        root = pathlib.Path(__file__).parents[3]
        hostile_dir = root / "architecture-conformance/families/past-tense-event/hostiles"
        controls = sorted(path for path in hostile_dir.glob("*.json") if json.loads(path.read_text())["hostile_class"] == "s1-cross-boundary")
        self.assertEqual(len(controls), 9)
        for path in controls:
            hostile = json.loads(path.read_text())
            case = apply_hostile(baseline(), hostile)
            result = MODULE.evaluate_case(case)
            self.assertEqual((result["portable"]["result"], result["portable"]["diagnostic_code"]), ("reject", hostile["expected_code"]), hostile["hostile_id"])
            malformed = copy.deepcopy(case); malformed["observation"]["s1_observation"]["extra"] = True
            with self.assertRaisesRegex(ValueError, "RMT_EVENT_S1_DECODE_INVALID"):
                MODULE.evaluate_case(malformed)

    def test_rejects_open_observation_and_stale_binding(self) -> None:
        opened = baseline(); opened["observation"]["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "RMT_EVENT_OBSERVATION_DECODE_INVALID"):
            MODULE.evaluate_case(opened)
        stale = baseline(); stale["descriptor"]["semantic_contract_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "RMT_EVENT_PYTHON_BINDING_STALE"):
            MODULE.evaluate_case(stale)


if __name__ == "__main__":
    unittest.main()
