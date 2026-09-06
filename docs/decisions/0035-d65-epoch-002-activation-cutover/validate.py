#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CANDIDATE = HERE / "activation-cutover-candidate.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "candidate-validation.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def boundary_errors(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    state = candidate.get("existing_state", {})
    effects = candidate.get("candidate_non_effects", {})
    if candidate.get("decision_state") != "not-decided":
        errors.append("candidate contains an owner decision")
    if candidate.get("authority_effect") != "none":
        errors.append("candidate carries authority")
    if state.get("implementation_admitted") is not True or state.get("runtime_activated") is not False:
        errors.append("existing admitted-inactive state changed")
    for key in ("runtime_activated", "migration_authorized", "cutover_authorized", "cutover_performed", "publication_authorized", "release_authorized", "deployment_authorized", "external_effect_authorized"):
        if effects.get(key) is not False:
            errors.append(f"candidate_non_effects.{key} must remain false")
    if effects.get("separate_execution_envelope_required") is not True:
        errors.append("separate execution envelope is not required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    candidate = load(CANDIDATE)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_errors = [error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(candidate)]
    add("candidate-schema", not schema_errors, schema_errors)

    refs: list[tuple[str, str, str]] = []
    for section, pairs in (
        ("admitted_product", (("manifest_path", "manifest_sha256"), ("admission_decision_path", "admission_decision_sha256"), ("admission_validation_path", "admission_validation_sha256"))),
        ("shadow_evidence", (("plan_path", "plan_sha256"), ("contract_path", "contract_sha256"), ("source_events_path", "source_events_sha256"), ("migration_inventory_path", "migration_inventory_sha256"), ("expected_projections_path", "expected_projections_sha256"), ("receipt_path", "receipt_sha256"))),
        ("admissibility", (("request_path", "request_sha256"), ("receipt_path", "receipt_sha256"))),
    ):
        section_value = candidate[section]
        for path_key, hash_key in pairs:
            refs.append((section, section_value[path_key], section_value[hash_key]))
    drift = []
    for section, path_text, expected in refs:
        path = LAB / path_text
        actual = digest(path) if path.is_file() else None
        if actual != expected:
            drift.append({"section": section, "path": path_text, "expected": expected, "actual": actual})
    add("exact-input-currentness", not drift, drift)

    admission = load(LAB / candidate["admitted_product"]["admission_validation_path"])
    shadow = load(LAB / candidate["shadow_evidence"]["receipt_path"])
    closure = (
        admission.get("result") == "PASS"
        and admission.get("implementation_admitted") is True
        and admission.get("runtime_activated") is False
        and admission.get("cutover_authorized") is False
        and shadow.get("result") == "PASS"
        and shadow.get("deterministic_runs") == 2
        and shadow.get("source_event_count") == 7
        and shadow.get("target_event_count") == 11
        and shadow.get("rust_public_contract_tests_per_run") == 4
        and shadow.get("mutation_probes_passed") == shadow.get("mutation_probes_total") == 10
        and shadow.get("rollback_result") == "PASS"
        and shadow.get("protected_byte_drift") == []
        and shadow.get("final_gate_eligible") is True
        and shadow.get("runtime_activated") is False
        and shadow.get("cutover_authorized") is False
        and shadow.get("cutover_performed") is False
    )
    add("admission-and-shadow-evidence-closure", closure, {"admission": admission.get("result"), "shadow": shadow.get("result"), "rollback": shadow.get("rollback_result")})

    admissibility = candidate["admissibility"]
    request = load(LAB / admissibility["request_path"])
    prefilter = load(LAB / admissibility["receipt_path"])
    option_ids = {option.get("option_id") for option in candidate.get("options", [])}
    admissible = (
        prefilter.get("requestDigest") == canonical_digest(request) == admissibility.get("request_digest")
        and prefilter.get("routeOutcome") == "gate"
        and prefilter.get("decisionGateRequired") is True
        and set(prefilter.get("admissibleOptionIds", [])) == option_ids == {"D65CUT-1", "D65CUT-2", "D65CUT-3", "D65CUT-4"}
        and prefilter.get("rejectedOptions") == []
    )
    add("decision-gate-admissibility", admissible, {"route_outcome": prefilter.get("routeOutcome"), "option_ids": sorted(option_ids), "rejected": prefilter.get("rejectedOptions")})

    boundary = boundary_errors(candidate)
    add("candidate-authority-ceiling", not boundary, boundary)

    probes: list[dict[str, str]] = []
    for probe_id, mutate in (
        ("admission-digest-drift", lambda value: value["admitted_product"].__setitem__("admission_validation_sha256", "0" * 64)),
        ("implicit-owner-selection", lambda value: value.__setitem__("decision_state", "selected")),
        ("runtime-activation-escalation", lambda value: value["candidate_non_effects"].__setitem__("runtime_activated", True)),
        ("cutover-performance-escalation", lambda value: value["candidate_non_effects"].__setitem__("cutover_performed", True)),
    ):
        mutated = copy.deepcopy(candidate)
        mutate(mutated)
        if probe_id == "admission-digest-drift":
            caught = mutated["admitted_product"]["admission_validation_sha256"] != digest(LAB / mutated["admitted_product"]["admission_validation_path"])
        else:
            caught = bool(boundary_errors(mutated))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("candidate-mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-activation-cutover-candidate-validation/v1",
        "candidate_id": candidate.get("candidate_id"),
        "gate_id": candidate.get("gate_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "candidate_frozen": result == "PASS",
        "decision_gate_ready": result == "PASS",
        "decision_state": "not-decided",
        "admissible_routing": prefilter.get("routeOutcome"),
        "admissible_option_ids": sorted(option_ids),
        "existing_implementation_admitted": True,
        "runtime_activated": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "cutover_performed": False,
        "authority_effect": "none",
        "inputs": [
            {"path": str(CANDIDATE.relative_to(LAB)), "sha256": digest(CANDIDATE)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": candidate["shadow_evidence"]["receipt_path"], "sha256": candidate["shadow_evidence"]["receipt_sha256"]},
            {"path": candidate["admissibility"]["receipt_path"], "sha256": candidate["admissibility"]["receipt_sha256"]}
        ],
        "claim_ceiling": "PASS proves only that one exact activation/cutover authority candidate is frozen, source-current, shadow-tested, rollback-proven, structurally prefiltered, and ready for its owner gate. It is not a decision and performs or authorizes no runtime activation, migration, cutover, publication, release, deployment, or external effect."
    }
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("candidate_id", "gate_id", "result", "failed_checks", "candidate_frozen", "decision_gate_ready", "decision_state", "admissible_routing", "admissible_option_ids", "runtime_activated", "cutover_authorized", "cutover_performed", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
