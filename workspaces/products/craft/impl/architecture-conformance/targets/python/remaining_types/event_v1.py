"""Candidate-local native Python witness for WP-RMT-002 Event."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class DurableOccurrence:
    occurrence_id: str
    persistence_checkpoint: str
    publication_attempt_id: str
    acknowledgement_state: str
    delivery_observation: str
    consumption_observation: str


OBSERVATION_KEYS = {
    "event_name", "tense", "payload_contract_id", "payload_version", "payload_mutable",
    "occurrence_identity_contract_id", "occurrence_id", "occurrence_id_stable",
    "occurrence_id_reused", "durable_checkpoints", "publication_policy_id",
    "publication_after_commit", "consumer_contract_ids", "consumer_payload_checks",
    "distributed_exactly_once_claim", "durable_occurrence", "s1_observation",
}
HANDLE_KEYS = {"occurrence_id", "persistence_checkpoint", "publication_attempt_id", "acknowledgement_state", "delivery_observation", "consumption_observation"}
CASE_KEYS = {"w3_descriptor", "w3_observation", "descriptor", "observation"}
DESCRIPTOR_KEYS = {"schema_version", "descriptor_id", "semantic_plan_epoch_id", "semantic_contract_digest", "event_name", "tense", "payload_contract_id", "payload_version", "payload_immutable", "occurrence_identity_contract_id", "persistence_checkpoint", "publication_policy_id", "consumer_contract_ids", "distributed_exactly_once_claim", "durable_handle", "admission_status", "authority_effect"}
COMMON_S1_KEYS = {"schema_version", "scenario", "occurrence_id"}
S1_KEYS = {
    "after-outbox-before-publish-failure": COMMON_S1_KEYS | {"transaction_committed", "state_preserved", "outbox_occurrence_present", "publication_attempted", "publication_attempt_id"},
    "send-failure": COMMON_S1_KEYS | {"transaction_committed", "state_preserved", "outbox_occurrence_present", "publication_attempted", "publication_succeeded", "publication_attempt_id", "retry_occurrence_id", "durable_rollback"},
    "success-ack-timeout": COMMON_S1_KEYS | {"transaction_committed", "state_preserved", "publication_attempted", "publication_succeeded", "acknowledgement_ambiguous", "retry_occurrence_id", "reconciliation"},
    "duplicate-reordered-delivery": COMMON_S1_KEYS | {"delivery_trace", "consumer_effect_count", "idempotent_consume", "history_rewritten"},
    "poison-occurrence": COMMON_S1_KEYS | {"transaction_committed", "outbox_occurrence_present", "poison_kind", "handling", "durable_history_preserved"},
    "recovery-replay": COMMON_S1_KEYS | {"fresh_process_restart", "outbox_recovered", "prior_occurrence_id", "recovered_occurrence_id", "prior_outcome", "recovered_outcome"},
    "future-version": COMMON_S1_KEYS | {"occurrence_schema_version", "supported_schema_version", "decode_status", "closed_decode"},
    "occurrence-reuse": COMMON_S1_KEYS | {"existing_fact_fingerprint", "distinct_fact_fingerprint", "reused_occurrence_id", "reuse_rejected"},
    "non-idempotent-retry": COMMON_S1_KEYS | {"original_occurrence_id", "retry_occurrence_id", "consumer_effect_count", "retry_rejected"},
}


def decode_s1(value: object) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("schema_version") != "durable-occurrence-fault-observation/v1":
        raise ValueError("RMT_EVENT_S1_DECODE_INVALID")
    scenario = value.get("scenario")
    if not isinstance(scenario, str) or scenario not in S1_KEYS or set(value) != S1_KEYS[scenario]:
        raise ValueError("RMT_EVENT_S1_DECODE_INVALID")
    string_or_null = {"schema_version", "scenario", "occurrence_id", "publication_attempt_id", "retry_occurrence_id", "reconciliation", "poison_kind", "handling", "prior_occurrence_id", "recovered_occurrence_id", "prior_outcome", "recovered_outcome", "decode_status", "existing_fact_fingerprint", "distinct_fact_fingerprint", "reused_occurrence_id", "original_occurrence_id"}
    numbers = {"consumer_effect_count", "occurrence_schema_version", "supported_schema_version"}
    for key, item in value.items():
        if key in string_or_null and item is not None and not isinstance(item, str):
            raise ValueError("RMT_EVENT_S1_DECODE_INVALID")
        if key in numbers and type(item) is not int:
            raise ValueError("RMT_EVENT_S1_DECODE_INVALID")
        if key == "delivery_trace" and (not isinstance(item, list) or not all(isinstance(entry, str) for entry in item)):
            raise ValueError("RMT_EVENT_S1_DECODE_INVALID")
        if key not in string_or_null | numbers | {"delivery_trace"} and not isinstance(item, bool):
            raise ValueError("RMT_EVENT_S1_DECODE_INVALID")
    return value


def decode_observation(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != OBSERVATION_KEYS:
        raise ValueError("RMT_EVENT_OBSERVATION_DECODE_INVALID")
    handle = value.get("durable_occurrence")
    checks = value.get("consumer_payload_checks")
    if not isinstance(handle, dict) or set(handle) != HANDLE_KEYS or not all(isinstance(item, str) for item in handle.values()):
        raise ValueError("RMT_EVENT_OBSERVATION_DECODE_INVALID")
    if not isinstance(checks, list) or any(not isinstance(check, dict) or set(check) != {"consumer_contract_id", "payload_version", "accepted"} or not isinstance(check["consumer_contract_id"], str) or not isinstance(check["payload_version"], str) or not isinstance(check["accepted"], bool) for check in checks):
        raise ValueError("RMT_EVENT_OBSERVATION_DECODE_INVALID")
    for key in ("event_name", "tense", "payload_contract_id", "payload_version", "occurrence_identity_contract_id", "occurrence_id", "publication_policy_id"):
        if not isinstance(value[key], str):
            raise ValueError("RMT_EVENT_OBSERVATION_DECODE_INVALID")
    for key in ("payload_mutable", "occurrence_id_stable", "occurrence_id_reused", "publication_after_commit", "distributed_exactly_once_claim"):
        if not isinstance(value[key], bool):
            raise ValueError("RMT_EVENT_OBSERVATION_DECODE_INVALID")
    for key in ("durable_checkpoints", "consumer_contract_ids"):
        if not isinstance(value[key], list) or not all(isinstance(item, str) for item in value[key]):
            raise ValueError("RMT_EVENT_OBSERVATION_DECODE_INVALID")
    value["s1_observation"] = decode_s1(value["s1_observation"])
    return value


def classify_s1(observed: dict[str, object], s1: dict[str, object]) -> str:
    if s1["occurrence_id"] != observed["occurrence_id"]:
        raise ValueError("RMT_EVENT_S1_OBSERVATION_INVALID")
    scenario = s1["scenario"]
    valid = False
    code = ""
    if scenario == "after-outbox-before-publish-failure":
        valid = all((s1["transaction_committed"], s1["state_preserved"], s1["outbox_occurrence_present"], not s1["publication_attempted"], s1["publication_attempt_id"] is None)); code = "RMT_S1_AFTER_OUTBOX_BEFORE_PUBLISH_FAILURE"
    elif scenario == "send-failure":
        valid = all((s1["transaction_committed"], s1["state_preserved"], s1["outbox_occurrence_present"], s1["publication_attempted"], not s1["publication_succeeded"], bool(s1["publication_attempt_id"]), s1["retry_occurrence_id"] == s1["occurrence_id"], not s1["durable_rollback"])); code = "RMT_S1_SEND_FAILURE"
    elif scenario == "success-ack-timeout":
        valid = all((s1["transaction_committed"], s1["state_preserved"], s1["publication_attempted"], s1["publication_succeeded"], s1["acknowledgement_ambiguous"], s1["retry_occurrence_id"] == s1["occurrence_id"], s1["reconciliation"] in ("idempotent-retry", "same-occurrence-reconcile"))); code = "RMT_S1_ACKNOWLEDGEMENT_AMBIGUOUS"
    elif scenario == "duplicate-reordered-delivery":
        trace = s1["delivery_trace"]; valid = len(trace) >= 2 and (len(set(trace)) < len(trace) or trace != sorted(trace)) and s1["consumer_effect_count"] == 1 and s1["idempotent_consume"] and not s1["history_rewritten"]; code = "RMT_S1_DUPLICATE_REORDERED_DELIVERY"
    elif scenario == "poison-occurrence":
        valid = all((s1["transaction_committed"], s1["outbox_occurrence_present"], s1["poison_kind"] in ("unpublishable", "unconsumable"), s1["handling"] in ("quarantine", "forward"), s1["durable_history_preserved"])); code = "RMT_S1_POISON_OCCURRENCE"
    elif scenario == "recovery-replay":
        valid = all((s1["fresh_process_restart"], s1["outbox_recovered"], s1["prior_occurrence_id"] == s1["occurrence_id"], s1["recovered_occurrence_id"] == s1["prior_occurrence_id"], s1["prior_outcome"] == "committed", s1["recovered_outcome"] == s1["prior_outcome"])); code = "RMT_S1_RECOVERY_REPLAY_MISMATCH"
    elif scenario == "future-version":
        valid = s1["occurrence_schema_version"] > s1["supported_schema_version"] == 1 and s1["decode_status"] == "rejected" and s1["closed_decode"]; code = "RMT_S1_FUTURE_VERSION"
    elif scenario == "occurrence-reuse":
        valid = bool(s1["existing_fact_fingerprint"]) and bool(s1["distinct_fact_fingerprint"]) and s1["existing_fact_fingerprint"] != s1["distinct_fact_fingerprint"] and s1["reused_occurrence_id"] == s1["occurrence_id"] and s1["reuse_rejected"]; code = "RMT_S1_OCCURRENCE_REUSE"
    elif scenario == "non-idempotent-retry":
        valid = s1["original_occurrence_id"] == s1["occurrence_id"] and (s1["retry_occurrence_id"] != s1["original_occurrence_id"] or s1["consumer_effect_count"] > 1) and s1["retry_rejected"]; code = "RMT_S1_NON_IDEMPOTENT_RETRY"
    if not valid:
        raise ValueError("RMT_EVENT_S1_OBSERVATION_INVALID")
    return code


def durable_handle_is_coherent(descriptor: dict[str, object], observed: dict[str, object]) -> bool:
    handle = observed["durable_occurrence"]
    if handle["occurrence_id"] != observed["occurrence_id"] or handle["persistence_checkpoint"] != descriptor["persistence_checkpoint"]:
        return False
    s1 = observed["s1_observation"]
    if s1 is None:
        return bool(handle["publication_attempt_id"]) and handle["acknowledgement_state"] == "unknown" and handle["delivery_observation"] == "at-least-once-observed" and handle["consumption_observation"] == "accepted"
    scenario = s1["scenario"]
    if scenario == "after-outbox-before-publish-failure":
        return handle["publication_attempt_id"] == "" and handle["acknowledgement_state"] == "unknown" and handle["delivery_observation"] == "not-observed" and handle["consumption_observation"] == "not-observed"
    if scenario == "send-failure":
        return handle["publication_attempt_id"] == s1["publication_attempt_id"] and handle["acknowledgement_state"] == "failed" and handle["delivery_observation"] == "not-observed" and handle["consumption_observation"] == "not-observed"
    if scenario == "success-ack-timeout":
        return bool(handle["publication_attempt_id"]) and handle["acknowledgement_state"] == "unknown"
    if scenario == "duplicate-reordered-delivery":
        return bool(handle["publication_attempt_id"]) and handle["acknowledgement_state"] == "acknowledged" and handle["delivery_observation"] == "at-least-once-observed" and handle["consumption_observation"] == "accepted"
    if scenario == "poison-occurrence":
        return s1["poison_kind"] == "unconsumable" and bool(handle["publication_attempt_id"]) and handle["acknowledgement_state"] == "acknowledged" and handle["delivery_observation"] == "at-least-once-observed" and handle["consumption_observation"] == "rejected"
    return bool(handle["publication_attempt_id"]) and handle["acknowledgement_state"] == "unknown" and handle["delivery_observation"] == "at-least-once-observed" and handle["consumption_observation"] == "accepted"


def evaluate_event(descriptor: dict[str, object], raw_observed: dict[str, object]) -> tuple[str, tuple[str, ...]]:
    observed = decode_observation(raw_observed)
    findings: list[str] = []
    if observed["tense"] != "past" or not str(descriptor["event_name"]).endswith("ed") or observed["event_name"] != descriptor["event_name"]: findings.append("RMT_EVENT_NON_PAST_TENSE")
    if observed["payload_mutable"]: findings.append("RMT_EVENT_MUTABLE_PAYLOAD")
    if not observed["occurrence_id"] or not observed["occurrence_id_stable"]: findings.append("RMT_EVENT_UNSTABLE_OCCURRENCE_ID")
    if observed["occurrence_id_reused"]: findings.append("RMT_EVENT_REUSED_OCCURRENCE_ID")
    checkpoints = observed["durable_checkpoints"]
    if not checkpoints: findings.append("RMT_EVENT_CHECKPOINT_MISSING")
    elif len(checkpoints) != 1: findings.append("RMT_EVENT_CHECKPOINT_DUPLICATE")
    if not observed["publication_after_commit"]: findings.append("RMT_EVENT_PUBLISH_BEFORE_COMMIT")
    if observed["distributed_exactly_once_claim"]: findings.append("RMT_EVENT_EXACTLY_ONCE_OVERCLAIM")
    declared, actual = set(descriptor["consumer_contract_ids"]), set(observed["consumer_contract_ids"])
    if declared != actual or any(check["consumer_contract_id"] not in declared or not check["accepted"] for check in observed["consumer_payload_checks"]): findings.append("RMT_EVENT_CONSUMER_OVERCLAIM")
    if observed["payload_version"] != descriptor["payload_version"] or any(check["payload_version"] != descriptor["payload_version"] for check in observed["consumer_payload_checks"]): findings.append("RMT_EVENT_SCHEMA_VERSION_DRIFT")
    if not durable_handle_is_coherent(descriptor, observed):
        raise ValueError("RMT_EVENT_DURABLE_HANDLE_INVALID")
    if observed["s1_observation"] is not None:
        findings.append(classify_s1(observed, observed["s1_observation"]))
    return ("pass" if not findings else "reject"), tuple(findings)


def evaluate_case(case: dict[str, object]) -> dict[str, object]:
    if not isinstance(case, dict) or set(case) != CASE_KEYS or not isinstance(case.get("descriptor"), dict) or set(case["descriptor"]) != DESCRIPTOR_KEYS:
        raise ValueError("RMT_EVENT_CASE_DECODE_INVALID")
    descriptor, observed = case["descriptor"], decode_observation(case["observation"])
    if descriptor.get("semantic_plan_epoch_id") != "WP-RMT-002/S1/2026-08-16" or descriptor.get("semantic_contract_digest") != "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7":
        raise ValueError("RMT_EVENT_PYTHON_BINDING_STALE")
    verdict, findings = evaluate_event(descriptor, observed)
    w3_descriptor, w3_observed, w3 = case["w3_descriptor"], case["w3_observation"], []
    if w3_observed["tense"] != "past": w3.append("ARCH_EVENT_NOT_PAST_FACT")
    if w3_observed["durable_checkpoints"] != [w3_descriptor["fact_checkpoint"]]: w3.append("ARCH_EVENT_CHECKPOINT_INVALID")
    if w3_observed["distributed_exactly_once_claim"]: w3.append("ARCH_EVENT_EXACTLY_ONCE_INFLATION")
    if w3:
        raise ValueError(f"RMT_EVENT_PYTHON_REJECTED:{','.join(w3)}")
    native = {"language": "python", "mechanism": "frozen-dataclass-event-and-durable-handle"}
    if observed["s1_observation"] is not None:
        if verdict != "reject" or len(findings) != 1:
            raise ValueError("RMT_EVENT_PYTHON_S1_CLASSIFICATION_INVALID")
        portable = {"schema_version": "domainspec.event-s1-portable-result/v1", "result": "reject", "meta_type": "Event", "diagnostic_code": findings[0], "scenario": observed["s1_observation"]["scenario"], "occurrence_id": observed["occurrence_id"], "durable_occurrence": observed["durable_occurrence"], "required_residue": observed["s1_observation"], "distributed_exactly_once_claim": False, "semantic_plan_epoch_id": descriptor["semantic_plan_epoch_id"], "semantic_contract_digest": descriptor["semantic_contract_digest"], "authority_effect": "none"}
        return {"portable": portable, "native_evidence": native}
    if verdict != "pass":
        raise ValueError(f"RMT_EVENT_PYTHON_REJECTED:{','.join(findings)}")
    portable = {"schema_version": "domainspec.event-portable-result/v1", "result": "pass", "meta_type": "Event", "event_name": descriptor["event_name"], "tense": "past", "payload_contract_id": descriptor["payload_contract_id"], "payload_version": descriptor["payload_version"], "payload_immutable": True, "occurrence_identity_contract_id": descriptor["occurrence_identity_contract_id"], "occurrence_id": observed["occurrence_id"], "retry_occurrence_id": observed["occurrence_id"], "persistence_checkpoint": descriptor["persistence_checkpoint"], "publication_is_separate_from_commit": True, "publication_policy_id": descriptor["publication_policy_id"], "consumer_contract_ids": sorted(descriptor["consumer_contract_ids"]), "durable_occurrence": observed["durable_occurrence"], "distributed_exactly_once_claim": False, "semantic_plan_epoch_id": descriptor["semantic_plan_epoch_id"], "semantic_contract_digest": descriptor["semantic_contract_digest"], "authority_effect": "none"}
    return {"portable": portable, "native_evidence": native}


if __name__ == "__main__" and sys.argv[1:] == ["--evaluate"]:
    try:
        print(json.dumps(evaluate_case(json.load(sys.stdin)), sort_keys=True, separators=(",", ":")))
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error
