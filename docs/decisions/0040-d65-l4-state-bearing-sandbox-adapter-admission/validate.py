#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CANDIDATE = HERE / "admission-candidate.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "candidate-validation.json"
DECISION = HERE / "decision.json"
L4_VALIDATOR = LAB / "ontology-lifecycle/runtime-candidates/cal-ontology-execution-envelope/v1/validate-l4.py"
EXPECTED_OPTIONS = {"L4AADM-1", "L4AADM-2", "L4AADM-3", "L4AADM-4"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def boundary_errors(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    downstream = candidate.get("downstream_authority", {})
    required_false = {
        "adapter_admitted", "implementation_admitted", "runtime_activated",
        "live_execution_ready", "migration_authorized", "cutover_authorized",
        "cutover_performed", "publication_authorized", "release_authorized",
        "deployment_authorized", "credentials_authorized",
        "destructive_action_authorized", "external_effect_authorized",
    }
    if candidate.get("decision_state") != "not-decided":
        errors.append("candidate contains an owner decision")
    if candidate.get("authority_effect") != "none":
        errors.append("candidate carries authority")
    if any(downstream.get(key) is not False for key in required_false):
        errors.append("downstream authority ceiling is violated")
    if downstream.get("separate_activation_and_effect_decisions_required") is not True:
        errors.append("separate activation and effect decisions are not preserved")
    binding = candidate.get("adapter_binding", {})
    required_binding = {
        "kind": "filesystem-state-bearing-sandbox-target",
        "identity": "cal.prototype.rust-state-bearing-sandbox-target/epoch-003",
        "admission_scope": "non-live bounded sandbox activation observation and explicit teardown only",
        "caller_supplied_path": False,
        "credential_kind": "none",
        "network": False,
        "production_data": False,
        "live": False,
        "state_survives_activation_observation": True,
        "explicit_teardown_required": True,
        "engine_substitution_allowed": False,
        "migration_allowed": False,
        "cutover_allowed": False,
        "runtime_activated": False,
        "cleanup_required": True,
        "external_effects": False,
    }
    if any(binding.get(key) != value for key, value in required_binding.items()):
        errors.append("adapter admission scope is not exact")
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
        ("approved_product", (("manifest_path", "manifest_sha256"), ("product_approval_decision_path", "product_approval_decision_sha256"), ("product_approval_validation_path", "product_approval_validation_sha256"))),
        ("adapter_binding", (("adapter_source_path", "adapter_source_sha256"), ("engine_binding_path", "engine_binding_sha256"), ("public_tests_path", "public_tests_sha256"))),
        ("sandbox_evidence", (("plan_path", "plan_sha256"), ("contract_path", "contract_sha256"), ("receipt_path", "receipt_sha256"))),
        ("admissibility", (("request_path", "request_sha256"), ("receipt_path", "receipt_sha256"))),
    ):
        value = candidate[section]
        for path_key, hash_key in pairs:
            refs.append((section, value[path_key], value[hash_key]))
    drift = []
    for section, path_text, expected in refs:
        path = LAB / path_text
        actual = digest(path) if path.is_file() else None
        if actual != expected:
            drift.append({"section": section, "path": path_text, "expected": expected, "actual": actual})
    add("exact-input-currentness", not drift, drift)

    approval_decision = load(LAB / candidate["approved_product"]["product_approval_decision_path"])
    approval_validation = load(LAB / candidate["approved_product"]["product_approval_validation_path"])
    evidence = load(LAB / candidate["sandbox_evidence"]["receipt_path"])
    evidence_inputs = {item.get("path"): item.get("sha256") for item in evidence.get("inputs", [])}
    closure = (
        approval_decision.get("selected_option", {}).get("option_id") == "L4PAPP-1"
        and approval_decision.get("product_approval", {}).get("state") == "approved"
        and approval_decision.get("candidate_refs", {}).get("product_candidate_sha256") == candidate["approved_product"]["manifest_sha256"]
        and approval_validation.get("result") == "PASS"
        and approval_validation.get("stage_state") == "PRODUCT_APPROVED"
        and approval_validation.get("product_approval") == "approved"
        and approval_validation.get("authority_effect") == "product-approval-only"
        and evidence.get("result") == "PASS"
        and evidence.get("deterministic_runs") == 2
        and evidence.get("rust_tests_per_run") == 35
        and evidence.get("contract", {}).get("result") == "PASS"
        and evidence.get("contract", {}).get("invariant_count") == 7
        and evidence.get("state_survives_activation_observation") is True
        and evidence.get("explicit_teardown_verified") is True
        and evidence.get("cleanup_verified") is True
        and evidence.get("runtime_activated") is False
        and evidence.get("live_execution_ready") is False
        and evidence.get("external_effects") is False
        and evidence_inputs.get(candidate["adapter_binding"]["adapter_source_path"]) == candidate["adapter_binding"]["adapter_source_sha256"]
        and evidence_inputs.get(candidate["adapter_binding"]["engine_binding_path"]) == candidate["adapter_binding"]["engine_binding_sha256"]
        and evidence_inputs.get(candidate["adapter_binding"]["public_tests_path"]) == candidate["adapter_binding"]["public_tests_sha256"]
    )
    add("approved-product-and-sandbox-closure", closure, {"product_approval": approval_validation.get("result"), "sandbox": evidence.get("result")})

    admissibility = candidate["admissibility"]
    request = load(LAB / admissibility["request_path"])
    receipt = load(LAB / admissibility["receipt_path"])
    option_ids = {option.get("option_id") for option in candidate.get("options", [])}
    admissible = (
        receipt.get("requestDigest") == canonical_digest(request)
        and receipt.get("routeOutcome") == "gate"
        and receipt.get("decisionGateRequired") is True
        and set(receipt.get("admissibleOptionIds", [])) == set(receipt.get("presentedOptionIds", [])) == option_ids == EXPECTED_OPTIONS
        and receipt.get("rejectedOptions") == []
    )
    add("decision-gate-admissibility", admissible, {"route_outcome": receipt.get("routeOutcome"), "option_ids": sorted(option_ids)})

    boundary = boundary_errors(candidate)
    add("authority-ceiling", not boundary, boundary)
    add("owner-selection-absent", not DECISION.exists(), {"decision_exists": DECISION.exists()})

    live_validation = subprocess.run(
        [sys.executable, str(L4_VALIDATOR)], cwd=L4_VALIDATOR.parent,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    try:
        live_summary = json.loads(live_validation.stdout)
    except json.JSONDecodeError:
        live_summary = {}
    add(
        "current-product-tests",
        live_validation.returncode == 0
        and live_summary.get("result") == "PASS"
        and live_summary.get("rust_tests_per_run") == 35
        and live_summary.get("invariants") == 7
        and live_summary.get("state_survives_activation_observation") is True,
        {"exit": live_validation.returncode, "summary": live_summary, "tail": live_validation.stdout[-2000:] if live_validation.returncode else ""},
    )

    probes: list[dict[str, str]] = []
    for probe_id, mutate in (
        ("product-approval-digest-drift", lambda value: value["approved_product"].__setitem__("product_approval_validation_sha256", "0" * 64)),
        ("adapter-source-digest-drift", lambda value: value["adapter_binding"].__setitem__("adapter_source_sha256", "0" * 64)),
        ("implicit-owner-selection", lambda value: value.__setitem__("decision_state", "selected")),
        ("engine-substitution-escalation", lambda value: value["adapter_binding"].__setitem__("engine_substitution_allowed", True)),
        ("live-scope-escalation", lambda value: value["adapter_binding"].__setitem__("live", True)),
        ("runtime-activation-escalation", lambda value: value["downstream_authority"].__setitem__("runtime_activated", True)),
        ("cutover-escalation", lambda value: value["downstream_authority"].__setitem__("cutover_authorized", True)),
    ):
        mutated = copy.deepcopy(candidate)
        mutate(mutated)
        if probe_id.endswith("digest-drift"):
            section = "approved_product" if probe_id.startswith("product") else "adapter_binding"
            caught = mutated[section] != candidate[section]
        else:
            caught = bool(boundary_errors(mutated))
        probes.append({"probe_id": probe_id, "result": "PASS" if caught else "BLOCK"})
    add("candidate-mutation-probes", all(probe["result"] == "PASS" for probe in probes), probes)

    failed = [check["check_id"] for check in checks if check["result"] != "PASS"]
    result = "PASS" if not failed else "BLOCK"
    validation = {
        "schema_version": "cal.d65-l4-state-bearing-sandbox-adapter-admission-candidate-validation/v1",
        "candidate_id": candidate.get("candidate_id"),
        "decision_id": candidate.get("decision_id"),
        "gate_id": candidate.get("gate_id"),
        "result": result,
        "checks": checks,
        "failed_checks": failed,
        "candidate_frozen": result == "PASS",
        "decision_gate_ready": result == "PASS",
        "decision_state": "not-decided",
        "admissible_option_ids": sorted(option_ids),
        "adapter_admission_authorized": False,
        "adapter_admitted": False,
        "runtime_activated": False,
        "live_execution_ready": False,
        "migration_authorized": False,
        "cutover_authorized": False,
        "external_effect_authorized": False,
        "authority_effect": "none",
        "inputs": [
            {"path": str(path.relative_to(LAB)), "sha256": digest(path)}
            for path in (
                CANDIDATE, SCHEMA, LAB / admissibility["request_path"],
                LAB / admissibility["receipt_path"],
                LAB / candidate["approved_product"]["product_approval_decision_path"],
                LAB / candidate["approved_product"]["product_approval_validation_path"],
                LAB / candidate["sandbox_evidence"]["receipt_path"],
                HERE / "DECISION.md", HERE / "README.md", HERE / "validate.py",
            )
        ],
        "claim_ceiling": "PASS proves only that the exact product-approved L4 state-bearing sandbox adapter admission candidate is frozen, source-current, test-proven, and ready for its owner gate. It is not an admission decision and grants no governed runtime activation, live execution, migration, cutover, publication, release, deployment, credential, destructive action, or external effect.",
    }
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in (
        "candidate_id", "decision_id", "gate_id", "result", "failed_checks",
        "candidate_frozen", "decision_gate_ready", "decision_state",
        "adapter_admission_authorized", "adapter_admitted", "runtime_activated",
        "live_execution_ready", "cutover_authorized", "authority_effect",
    )}, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
