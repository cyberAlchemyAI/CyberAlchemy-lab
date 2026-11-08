#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
ENVELOPE = HERE / "envelope.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipts/prototype.json"
EXPECTED_STEPS = [
    "EX-P1-PREFLIGHT", "EX-P2-CAPTURE-PREIMAGE", "EX-P3-STAGE",
    "EX-P4-ACTIVATE", "EX-P5-MIGRATE", "EX-P6-VERIFY-TARGET",
    "EX-P7-CUTOVER", "EX-P8-VERIFY-POSTIMAGE", "EX-P9-ROLLBACK",
    "EX-P10-VERIFY-ROLLBACK",
]


class PrototypeFailure(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PrototypeFailure(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_activation(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("cal_d65_activation", path)
    if spec is None or spec.loader is None:
        raise PrototypeFailure("activation runner cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def schema_errors(envelope: dict[str, Any]) -> list[str]:
    return [error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(envelope)]


def reference_pairs(envelope: dict[str, Any]) -> list[tuple[str, str]]:
    authorization = envelope["authorization"]
    product = envelope["product"]
    migration = envelope["migration"]
    return [
        (authorization["decision_path"], authorization["decision_sha256"]),
        (authorization["decision_validation_path"], authorization["decision_validation_sha256"]),
        (product["manifest_path"], product["manifest_sha256"]),
        (migration["contract_path"], migration["contract_sha256"]),
        (migration["runner_path"], migration["runner_sha256"]),
        (migration["source_events_path"], migration["source_events_sha256"]),
        (migration["inventory_path"], migration["inventory_sha256"]),
        (migration["expected_projection_path"], migration["expected_projection_sha256"]),
    ]


def validate_refs(envelope: dict[str, Any]) -> dict[str, str]:
    current: dict[str, str] = {}
    for path_text, expected in reference_pairs(envelope):
        path = LAB / path_text
        actual = digest(path) if path.is_file() else "missing"
        if actual != expected:
            raise PrototypeFailure(f"dependency drift: {path_text}")
        current[path_text] = actual
    return current


def validate_authority(envelope: dict[str, Any]) -> None:
    authorization = envelope["authorization"]
    decision = load(LAB / authorization["decision_path"])
    validation = load(LAB / authorization["decision_validation_path"])
    if decision.get("decision_source", {}).get("selected_option_id") != "D65CUT-1":
        raise PrototypeFailure("D65CUT-1 is not the selected owner decision")
    if decision.get("authorization", {}).get("successor_execution_envelope_authorized") is not True:
        raise PrototypeFailure("successor execution envelope is not authorized")
    if decision.get("authorization", {}).get("successor_execution_ready") is not False:
        raise PrototypeFailure("source decision unexpectedly claims execution readiness")
    if validation.get("result") != "PASS" or validation.get("authorization_state") != "conditional-authorized":
        raise PrototypeFailure("authorization decision validation is not current")
    if validation.get("successor_execution_envelope_authorized") is not True:
        raise PrototypeFailure("decision validation does not authorize the envelope")


def validate_boundary(envelope: dict[str, Any]) -> None:
    target = envelope["prototype_target"]
    policy = envelope["execution_policy"]
    if target != {
        "kind": "generated-temporary-directory",
        "identity": "cal.prototype.disposable-target/epoch-002",
        "locator": "generated-at-runtime",
        "lifetime": "single-process",
        "live": False,
        "production_data": False,
        "credential_kind": "none",
        "external_effects": False,
    }:
        raise PrototypeFailure("prototype target boundary changed")
    if policy.get("prototype_execution_ready") is not True or policy.get("live_execution_ready") is not False:
        raise PrototypeFailure("prototype/live readiness boundary changed")
    if envelope.get("runtime_activated") is not False or envelope.get("migration_performed") is not False or envelope.get("cutover_performed") is not False or envelope.get("external_effects") is not False:
        raise PrototypeFailure("envelope claims a live effect")


def validate_sequence(envelope: dict[str, Any]) -> None:
    positions = [step.get("position") for step in envelope.get("steps", [])]
    step_ids = [step.get("step_id") for step in envelope.get("steps", [])]
    if positions != list(range(1, 11)) or step_ids != EXPECTED_STEPS:
        raise PrototypeFailure("execution sequence changed")


def assert_rollback(actual_bytes: bytes, expected_bytes: bytes, actual_state: dict[str, Any], expected_state: dict[str, Any]) -> None:
    if actual_bytes != expected_bytes:
        raise PrototypeFailure("event preimage was not restored")
    if actual_state != expected_state:
        raise PrototypeFailure("runtime pointer preimage was not restored")


def execute_prototype(envelope: dict[str, Any], activation: ModuleType) -> dict[str, Any]:
    migration = envelope["migration"]
    source_path = LAB / migration["source_events_path"]
    inventory_path = LAB / migration["inventory_path"]
    expected_path = LAB / migration["expected_projection_path"]
    source_bytes = source_path.read_bytes()
    source = activation.load_event_bytes(source_bytes)
    inventory = load(inventory_path)
    expected = load(expected_path)
    target = activation.migrate(source, inventory)
    target_bytes = activation.event_bytes(target)
    trace: list[dict[str, Any]] = []

    def record(step_id: str, detail: dict[str, Any]) -> None:
        trace.append({"step_id": step_id, "result": "PASS", "detail": detail})

    validate_refs(envelope)
    validate_authority(envelope)
    validate_boundary(envelope)
    validate_sequence(envelope)
    record("EX-P1-PREFLIGHT", {"dependencies": len(reference_pairs(envelope)), "mode": "prototype"})

    temporary_path: Path | None = None
    with tempfile.TemporaryDirectory(prefix="cal-d65-execution-prototype-") as temporary:
        temporary_path = Path(temporary)
        active_events = temporary_path / "active-events.jsonl"
        staged_events = temporary_path / "staged-events.jsonl"
        state_file = temporary_path / "runtime-state.json"
        initial_state = {"runtime": "epoch-001", "runtime_state": "inactive", "traffic_target": "epoch-001", "live": False}
        active_events.write_bytes(source_bytes)
        state_file.write_bytes(canonical(initial_state))
        preimage_event_sha = digest(active_events)
        preimage_state_sha = digest(state_file)
        source_projection = activation.project(source)
        record("EX-P2-CAPTURE-PREIMAGE", {"event_sha256": preimage_event_sha, "state_sha256": preimage_state_sha, "source_cursor": source_projection["source_cursor"]})

        staged_events.write_bytes(target_bytes)
        staged_projection = activation.project(activation.load_event_bytes(staged_events.read_bytes()))
        activation.validate_target(staged_projection, expected)
        record("EX-P3-STAGE", {"events": len(target), "event_set_digest": staged_projection["source_event_set_digest"]})

        activated_state = {"runtime": "epoch-002", "runtime_state": "prototype-active", "traffic_target": "epoch-001", "live": False}
        state_file.write_bytes(canonical(activated_state))
        record("EX-P4-ACTIVATE", {"runtime_state": "prototype-active", "traffic_target": "epoch-001"})

        active_events.write_bytes(staged_events.read_bytes())
        record("EX-P5-MIGRATE", {"source_events": len(source), "target_events": len(target)})

        target_projection = activation.project(activation.load_event_bytes(active_events.read_bytes()))
        activation.validate_target(target_projection, expected)
        record("EX-P6-VERIFY-TARGET", {"projection_digest": target_projection["projection_digest"], "nodes": len(target_projection["nodes"]), "relations": len(target_projection["relations"])})

        cutover_state = {"runtime": "epoch-002", "runtime_state": "prototype-active", "traffic_target": "epoch-002", "live": False}
        state_file.write_bytes(canonical(cutover_state))
        record("EX-P7-CUTOVER", {"traffic_target": "epoch-002", "live": False})

        postimage_event_sha = digest(active_events)
        postimage_state_sha = digest(state_file)
        if target_projection["source_event_set_digest"] != migration["target_event_set_digest"] or target_projection["projection_digest"] != migration["target_projection_digest"]:
            raise PrototypeFailure("target postimage digest mismatch")
        record("EX-P8-VERIFY-POSTIMAGE", {"event_sha256": postimage_event_sha, "state_sha256": postimage_state_sha})

        active_events.write_bytes(source_bytes)
        state_file.write_bytes(canonical(initial_state))
        staged_events.unlink()
        record("EX-P9-ROLLBACK", {"restored_event_sha256": digest(active_events), "restored_state_sha256": digest(state_file)})

        restored_state = json.loads(state_file.read_text(encoding="utf-8"))
        restored_projection = activation.project(activation.load_event_bytes(active_events.read_bytes()))
        assert_rollback(active_events.read_bytes(), source_bytes, restored_state, initial_state)
        if restored_projection != source_projection or staged_events.exists():
            raise PrototypeFailure("calculated source projection or staged cleanup was not restored")
        record("EX-P10-VERIFY-ROLLBACK", {"bytes_equal": True, "projection_equal": True, "staged_removed": True})

    if temporary_path is None or temporary_path.exists():
        raise PrototypeFailure("temporary target was not removed")
    return {
        "trace": trace,
        "trace_digest": hashlib.sha256(canonical(trace)).hexdigest(),
        "source_event_count": len(source),
        "target_event_count": len(target),
        "target_projection_digest": expected["projection_digest"],
        "rollback_result": "PASS",
        "temporary_target_removed": True,
    }


def mutation_tournament(envelope: dict[str, Any], activation: ModuleType) -> list[dict[str, str]]:
    source = activation.load_event_bytes((LAB / envelope["migration"]["source_events_path"]).read_bytes())
    inventory = load(LAB / envelope["migration"]["inventory_path"])
    expected = load(LAB / envelope["migration"]["expected_projection_path"])
    target = activation.migrate(source, inventory)
    probes: list[dict[str, str]] = []

    def probe(probe_id: str, action: Callable[[], None]) -> None:
        try:
            action()
        except (PrototypeFailure, activation.ActivationFailure):
            probes.append({"probe_id": probe_id, "result": "PASS"})
        else:
            probes.append({"probe_id": probe_id, "result": "BLOCK"})

    stale = copy.deepcopy(envelope)
    stale["authorization"]["decision_sha256"] = "0" * 64
    probe("stale-decision-digest", lambda: validate_refs(stale))

    live = copy.deepcopy(envelope)
    live["prototype_target"]["live"] = True
    probe("live-target-injection", lambda: (_ for _ in ()).throw(PrototypeFailure("schema")) if schema_errors(live) else None)

    credential = copy.deepcopy(envelope)
    credential["prototype_target"]["credential_kind"] = "token"
    probe("credential-injection", lambda: validate_boundary(credential))

    reordered = copy.deepcopy(envelope)
    reordered["steps"][4], reordered["steps"][5] = reordered["steps"][5], reordered["steps"][4]
    probe("step-reordering", lambda: validate_sequence(reordered))

    corrupted_source = (LAB / envelope["migration"]["source_events_path"]).read_bytes() + b"corruption\n"
    probe("source-preimage-drift", lambda: assert_rollback(corrupted_source, (LAB / envelope["migration"]["source_events_path"]).read_bytes(), {}, {}))

    partial = activation.normalize_and_seal(source + target[len(source):len(source) + 2])
    probe("partial-migration", lambda: activation.validate_target(activation.project(partial), expected))

    wrong_expected = copy.deepcopy(expected)
    wrong_expected["projection_digest"] = "0" * 64
    probe("target-projection-substitution", lambda: activation.validate_target(activation.project(target), wrong_expected))

    no_challenge = activation.normalize_and_seal([event for event in target if event["subject_kind"] != "challenge-contract"])
    probe("missing-challenge-contract", lambda: activation.project(no_challenge))

    probe("rollback-corruption", lambda: assert_rollback(b"wrong", b"right", {"runtime": "wrong"}, {"runtime": "right"}))

    external = copy.deepcopy(envelope)
    external["prototype_target"]["external_effects"] = True
    probe("external-effect-escalation", lambda: validate_boundary(external))
    return probes


def live_refusal(envelope: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "cal.d65-execution-prototype-live-refusal/v1",
        "envelope_id": envelope.get("envelope_id"),
        "result": "BLOCK",
        "reason": "prototype envelope has no exact live target, credential identity, maintenance boundary, live preimages, live fail-closed sequence, or independent live validation",
        "missing_prerequisites": envelope.get("live_prerequisites", []),
        "runtime_activated": False,
        "migration_performed": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("prototype", "live"), default="prototype")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    envelope = load(ENVELOPE)
    if args.mode == "live":
        print(json.dumps(live_refusal(envelope), indent=2, sort_keys=True))
        return 2

    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    try:
        errors = schema_errors(envelope)
        add("envelope-schema", not errors, errors)
        if errors:
            raise PrototypeFailure("envelope schema invalid")
        activation = load_activation(LAB / envelope["migration"]["runner_path"])
        execution = execute_prototype(envelope, activation)
        add("ordered-prototype-execution", len(execution["trace"]) == 10, {"steps": len(execution["trace"]), "trace_digest": execution["trace_digest"]})
        add("canonical-event-migration", execution["source_event_count"] == 7 and execution["target_event_count"] == 11, {"source": execution["source_event_count"], "target": execution["target_event_count"], "projection_digest": execution["target_projection_digest"]})
        add("exact-rollback-and-cleanup", execution["rollback_result"] == "PASS" and execution["temporary_target_removed"] is True, {"rollback": execution["rollback_result"], "temporary_target_removed": execution["temporary_target_removed"]})
        probes = mutation_tournament(envelope, activation)
        add("prototype-mutation-tournament", len(probes) == 10 and all(item["result"] == "PASS" for item in probes), probes)
        add("live-mode-boundary", envelope["execution_policy"]["live_execution_ready"] is False and envelope["prototype_target"]["live"] is False, live_refusal(envelope))
    except (OSError, json.JSONDecodeError, PrototypeFailure, KeyError) as exc:
        add("prototype-exception", False, str(exc))
        execution = {}
        probes = []

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-execution-envelope-prototype-evidence/v1",
        "envelope_id": envelope.get("envelope_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "execution_trace": execution.get("trace", []),
        "execution_trace_digest": execution.get("trace_digest"),
        "source_event_count": execution.get("source_event_count"),
        "target_event_count": execution.get("target_event_count"),
        "target_projection_digest": execution.get("target_projection_digest"),
        "rollback_result": execution.get("rollback_result", "not_evaluable"),
        "mutation_probes_passed": sum(item.get("result") == "PASS" for item in probes),
        "mutation_probes_total": len(probes),
        "prototype_execution_ready": result == "PASS",
        "live_execution_ready": False,
        "live_mode_refusal": "PASS" if result == "PASS" else "not_evaluable",
        "temporary_target_removed": execution.get("temporary_target_removed", False),
        "runtime_activated": False,
        "migration_performed": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none",
        "inputs": [
            {"path": str(ENVELOPE.relative_to(LAB)), "sha256": digest(ENVELOPE)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": envelope["authorization"]["decision_path"], "sha256": envelope["authorization"]["decision_sha256"]},
            {"path": envelope["migration"]["source_events_path"], "sha256": envelope["migration"]["source_events_sha256"]}
        ],
        "claim_ceiling": "PASS proves the disposable execution-envelope prototype, its ordered state machine, event-calculated target, hostile mutation detection, live-mode refusal, exact rollback, and cleanup. It performs no live runtime activation, migration, cutover, credential use, destructive action, publication, deployment, or external effect."
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("envelope_id", "result", "failed_checks", "execution_trace_digest", "source_event_count", "target_event_count", "rollback_result", "mutation_probes_passed", "mutation_probes_total", "prototype_execution_ready", "live_execution_ready", "live_mode_refusal", "temporary_target_removed", "runtime_activated", "cutover_performed", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
