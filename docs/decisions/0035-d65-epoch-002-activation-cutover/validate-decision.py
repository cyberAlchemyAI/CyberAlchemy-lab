#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
DECISION = HERE / "decision.json"
SCHEMA = HERE / "decision-schema.json"
RECEIPT = HERE / "decision-validation.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decision_errors(decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    authorization = decision.get("authorization", {})
    effects = decision.get("current_effect_state", {})
    prerequisites = decision.get("execution_prerequisites", [])
    if decision.get("authority_effect") != "activation-migration-cutover-authorization":
        errors.append("authority effect does not match D65CUT-1")
    if authorization.get("state") != "conditional-authorized" or authorization.get("successor_execution_envelope_authorized") is not True:
        errors.append("successor envelope authority is not recorded")
    if authorization.get("successor_execution_ready") is not False:
        errors.append("execution was made ready without exact prerequisites")
    if len(prerequisites) != 6 or any(item.get("state") != "missing" for item in prerequisites):
        errors.append("execution prerequisites are not explicitly missing")
    for key in ("activation_authorized", "migration_authorized", "cutover_authorized"):
        if effects.get(key) is not True:
            errors.append(f"{key} does not reflect D65CUT-1")
    for key in ("runtime_activated", "migration_performed", "cutover_performed", "credential_use_authorized", "destructive_action_authorized", "publication_authorized", "release_authorized", "deployment_authorized", "external_effect_performed"):
        if effects.get(key) is not False:
            errors.append(f"{key} exceeds the present decision effect")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    decision = load(DECISION)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    schema_errors = [error.message for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(decision)]
    add("decision-schema", not schema_errors, schema_errors)

    refs = decision["candidate_refs"]
    ref_pairs = (
        ("candidate_path", "candidate_sha256"),
        ("candidate_validation_path", "candidate_validation_sha256"),
        ("admissibility_request_path", "admissibility_request_sha256"),
        ("admissibility_receipt_path", "admissibility_receipt_sha256"),
        ("shadow_receipt_path", "shadow_receipt_sha256"),
        ("product_manifest_path", "product_manifest_sha256"),
    )
    drift = []
    for path_key, hash_key in ref_pairs:
        path = LAB / refs[path_key]
        actual = digest(path) if path.is_file() else None
        if actual != refs[hash_key]:
            drift.append({"path": refs[path_key], "expected": refs[hash_key], "actual": actual})
    add("exact-input-currentness", not drift, drift)

    candidate = load(LAB / refs["candidate_path"])
    candidate_validation = load(LAB / refs["candidate_validation_path"])
    admissibility = load(LAB / refs["admissibility_receipt_path"])
    shadow = load(LAB / refs["shadow_receipt_path"])
    closure = (
        candidate_validation.get("result") == "PASS"
        and candidate_validation.get("decision_gate_ready") is True
        and candidate_validation.get("candidate_frozen") is True
        and candidate_validation.get("decision_state") == "not-decided"
        and admissibility.get("routeOutcome") == "gate"
        and "D65CUT-1" in admissibility.get("admissibleOptionIds", [])
        and shadow.get("result") == "PASS"
        and shadow.get("final_gate_eligible") is True
        and candidate.get("candidate_id") == decision["authorization"]["activation_cutover_candidate_id"]
        and refs["candidate_sha256"] == decision["authorization"]["identity"]
    )
    add("candidate-gate-and-shadow-closure", closure, {"candidate": candidate_validation.get("result"), "routing": admissibility.get("routeOutcome"), "shadow": shadow.get("result")})

    selected = next((option for option in candidate.get("options", []) if option.get("option_id") == "D65CUT-1"), None)
    selection_errors: list[str] = []
    if selected is None:
        selection_errors.append("D65CUT-1 missing from candidate")
    else:
        if decision["selected_option"]["meaning"] != selected.get("meaning"):
            selection_errors.append("selected option meaning changed")
        if decision["selected_option"]["authority_effect"] != selected.get("if_selected_authority_effect"):
            selection_errors.append("selected authority effect changed")
    if decision["decision_source"] != {"kind": "explicit-user-selection", "verbatim": "D65CUT-1", "selected_option_id": "D65CUT-1", "observed_count": 1}:
        selection_errors.append("decision source does not match exact user selection")
    add("exact-owner-selection", not selection_errors, selection_errors)

    boundary = decision_errors(decision)
    add("conditional-authorization-and-effect-ceiling", not boundary, boundary)

    probes: list[dict[str, str]] = []
    for probe_id, mutate in (
        ("candidate-digest-substitution", lambda value: value["candidate_refs"].__setitem__("candidate_sha256", "0" * 64)),
        ("option-substitution", lambda value: value["decision_source"].__setitem__("selected_option_id", "D65CUT-2")),
        ("premature-execution-ready", lambda value: value["authorization"].__setitem__("successor_execution_ready", True)),
        ("cutover-performed-escalation", lambda value: value["current_effect_state"].__setitem__("cutover_performed", True)),
        ("credential-auto-authorization", lambda value: value["current_effect_state"].__setitem__("credential_use_authorized", True)),
    ):
        mutated = copy.deepcopy(decision)
        mutate(mutated)
        if probe_id == "candidate-digest-substitution":
            caught = mutated["candidate_refs"]["candidate_sha256"] != digest(LAB / mutated["candidate_refs"]["candidate_path"])
        elif probe_id == "option-substitution":
            caught = mutated["decision_source"]["selected_option_id"] != "D65CUT-1"
        else:
            caught = bool(decision_errors(mutated))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("decision-mutation-probes", all(item["result"] == "PASS" for item in probes), probes)

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    receipt = {
        "schema_version": "cal.d65-activation-cutover-decision-validation/v1",
        "decision_id": decision.get("decision_id"),
        "gate_id": decision.get("gate_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "decision_gate_result": "PASS" if result == "PASS" else "BLOCK",
        "decisions_resolved": 1 if result == "PASS" else 0,
        "blockers_remaining": 0 if result == "PASS" else 1,
        "selected_option_id": "D65CUT-1" if result == "PASS" else None,
        "authorization_state": "conditional-authorized" if result == "PASS" else "not_evaluable",
        "successor_execution_envelope_authorized": result == "PASS",
        "successor_execution_ready": False,
        "unmet_execution_prerequisites": [item["prerequisite_id"] for item in decision.get("execution_prerequisites", []) if item.get("state") != "PASS"],
        "runtime_activated": False,
        "migration_performed": False,
        "cutover_performed": False,
        "credential_use_authorized": False,
        "publication_authorized": False,
        "deployment_authorized": False,
        "authority_effect": "activation-migration-cutover-authorization" if result == "PASS" else "none",
        "inputs": [
            {"path": str(DECISION.relative_to(LAB)), "sha256": digest(DECISION)},
            {"path": str(SCHEMA.relative_to(LAB)), "sha256": digest(SCHEMA)},
            {"path": refs["candidate_path"], "sha256": refs["candidate_sha256"]},
            {"path": refs["candidate_validation_path"], "sha256": refs["candidate_validation_sha256"]}
        ],
        "claim_ceiling": "PASS proves the owner selected D65CUT-1 against the exact frozen candidate, granting conditional authority for a separately bounded successor activation, canonical-event migration, cutover, and rollback envelope. It proves no execution readiness and performs no runtime, data, credential, publication, deployment, destructive, or external effect."
    }
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("decision_id", "gate_id", "result", "decision_gate_result", "decisions_resolved", "blockers_remaining", "selected_option_id", "authorization_state", "successor_execution_envelope_authorized", "successor_execution_ready", "unmet_execution_prerequisites", "runtime_activated", "cutover_performed", "authority_effect")}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
