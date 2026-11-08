#!/usr/bin/env python3
"""Validate the bounded D65-S6 exact implementation-binding candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[3]
BINDING_PATH = HERE / "binding.json"
SCHEMA_PATH = HERE / "schema.json"
OWNER_REQUEST_PATH = HERE / "owner-decision-request.json"
ADMISSIBILITY_REQUEST_PATH = HERE / "admissibility-request.json"
VALIDATION_RECEIPT_PATH = HERE / "receipts" / "validation.json"
ADMISSIBILITY_RECEIPT_PATH = HERE / "receipts" / "admissibility.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rust_symbol_resolves(source: str, symbol: str) -> bool:
    if "::" in symbol:
        owner, member = symbol.split("::", 1)
        if owner == "EventStore":
            return bool(re.search(rf"\bpub\s+fn\s+{re.escape(member)}\s*\(", source))
        if owner == "OntologySubjectIdentity":
            return bool(re.search(rf"\bpub\s+fn\s+{re.escape(member)}\s*\(", source))
        if owner == "GovernanceJoinPolicy":
            return "pub enum GovernanceJoinPolicy" in source and bool(
                re.search(rf"\b{re.escape(member)}\b", source)
            )
        if owner == "OntologySemanticState":
            return "pub enum OntologySemanticState" in source and bool(
                re.search(rf"\b{re.escape(member)}\b", source)
            )
        return False
    declarations = (
        rf"\bpub\s+(?:struct|enum|type|const|fn)\s+{re.escape(symbol)}\b",
        rf"\bfn\s+{re.escape(symbol)}\s*\(",
    )
    return any(re.search(pattern, source) for pattern in declarations)


def validate() -> tuple[dict[str, object], dict[str, object]]:
    failures: list[str] = []
    checks: dict[str, bool] = {}

    binding = load(BINDING_PATH)
    schema = load(SCHEMA_PATH)
    schema_errors = sorted(Draft202012Validator(schema).iter_errors(binding), key=lambda e: list(e.path))
    checks["schema_validation"] = not schema_errors
    failures.extend(f"SCHEMA:{'/'.join(map(str, error.path))}:{error.message}" for error in schema_errors)

    artifact_by_id: dict[str, dict[str, str]] = {}
    artifact_failures: list[str] = []
    for artifact in binding.get("bound_artifacts", []):
        artifact_by_id[artifact["artifact_id"]] = artifact
        path = LAB / artifact["path"]
        if not path.is_file():
            artifact_failures.append(f"BOUND_ARTIFACT_MISSING:{artifact['artifact_id']}:{artifact['path']}")
        elif sha256(path) != artifact["sha256"]:
            artifact_failures.append(f"BOUND_ARTIFACT_DRIFT:{artifact['artifact_id']}:{artifact['path']}")
    checks["VAL-BINDING-CURRENTNESS"] = not artifact_failures
    failures.extend(artifact_failures)

    prospective_failures: list[str] = []
    for target in binding.get("planned_adapters", []):
        if "sha256" in target:
            prospective_failures.append(f"PROSPECTIVE_DIGEST_FORBIDDEN:{target['adapter_id']}")
        if target.get("status") != "prospective-unimplemented" or target.get("realization_claim") != "none":
            prospective_failures.append(f"PROSPECTIVE_POSTURE_INVALID:{target['adapter_id']}")
        if (LAB / target["target_path"]).exists():
            prospective_failures.append(f"PROSPECTIVE_TARGET_ALREADY_EXISTS:{target['target_path']}")
    checks["prospective_targets_absent"] = not prospective_failures
    failures.extend(prospective_failures)

    lib_path = LAB / binding["existing_rust_surface"]["library_path"]
    rust_source = lib_path.read_text(encoding="utf-8") if lib_path.is_file() else ""
    declared_symbols: set[str] = set()
    for group in binding.get("existing_rust_surface", {}).get("symbol_groups", []):
        declared_symbols.update(group["symbols"])
    for contract in binding.get("system_contract_bindings", []):
        declared_symbols.update(contract["runtime_symbols"])
        if contract["source_ref"] not in artifact_by_id:
            failures.append(f"CONTRACT_SOURCE_REF_UNRESOLVED:{contract['contract_id']}")
    unresolved_symbols = sorted(symbol for symbol in declared_symbols if not rust_symbol_resolves(rust_source, symbol))

    tests_path = LAB / artifact_by_id.get("W8-RUST-TESTS", {}).get("path", "")
    test_source = tests_path.read_text(encoding="utf-8") if tests_path.is_file() else ""
    unresolved_tests = sorted(
        test["test_symbol"]
        for test in binding.get("existing_rust_surface", {}).get("test_bindings", [])
        if not re.search(rf"\bfn\s+{re.escape(test['test_symbol'])}\s*\(\)", test_source)
    )
    checks["VAL-SYMBOL-CLOSURE"] = not unresolved_symbols and not unresolved_tests
    failures.extend(f"RUST_SYMBOL_UNRESOLVED:{symbol}" for symbol in unresolved_symbols)
    failures.extend(f"RUST_TEST_UNRESOLVED:{symbol}" for symbol in unresolved_tests)

    plan = load(LAB / artifact_by_id["D65-PLAN-REV14"]["path"])
    stages = {stage["stage_id"]: stage for stage in plan["stages"]}
    checks["d65_frontier"] = (
        plan.get("revision") == 14
        and plan.get("first_blocking_gate") == "G-D65-BINDING"
        and stages.get("D65-S5", {}).get("state") == "PASS"
        and stages.get("D65-S6", {}).get("state") == "BLOCK"
        and plan.get("execution", {}).get("authorized") is False
    )

    admission = load(LAB / artifact_by_id["D65-S5-ADMISSION"]["path"])
    event_contract = load(LAB / artifact_by_id["D65-S5-EVENT-CONTRACT"]["path"])
    system_ontology = load(LAB / artifact_by_id["D65-S5-SYSTEM-ONTOLOGY"]["path"])
    version_manifest = load(LAB / artifact_by_id["D65-S5-VERSION-MANIFEST"]["path"])
    checks["admitted_system_ontology_identity"] = (
        admission.get("status") == "selected"
        and admission.get("selection", {}).get("option_id") == "D65SYS-1"
        and admission.get("next_gate") == "G-D65-BINDING"
        and admission.get("candidate_refs", {}).get("graph_sha256") == artifact_by_id["D65-S5-GRAPH"]["sha256"]
        and admission.get("candidate_refs", {}).get("event_contract_sha256") == artifact_by_id["D65-S5-EVENT-CONTRACT"]["sha256"]
        and admission.get("candidate_refs", {}).get("system_ontology_sha256") == artifact_by_id["D65-S5-SYSTEM-ONTOLOGY"]["sha256"]
        and system_ontology.get("ontology_id") == binding.get("ontology_id")
        and system_ontology.get("source", {}).get("event_contract_sha256") == artifact_by_id["D65-S5-EVENT-CONTRACT"]["sha256"]
        and system_ontology.get("event_calculus", {}).get("contract") == event_contract
        and version_manifest.get("admission_decision", {}).get("sha256") == artifact_by_id["D65-S5-ADMISSION"]["sha256"]
        and version_manifest.get("source_graph", {}).get("sha256") == artifact_by_id["D65-S5-GRAPH"]["sha256"]
        and version_manifest.get("canonical_replay_source") is False
    )

    w8_decision = load(LAB / artifact_by_id["W8-ACCEPTANCE"]["path"])
    w8_manifest = load(LAB / artifact_by_id["W8-EPOCH-MANIFEST"]["path"])
    w8_verdict = load(LAB / artifact_by_id["W8-EPOCH-VERDICT"]["path"])
    w8_binding = load(LAB / artifact_by_id["W8-CONSTRUCTION-BINDING"]["path"])
    w8_dependency_map = {item["path"]: item["sha256"] for item in w8_manifest.get("dependencies", [])}
    w8_artifact_map = {item["path"]: item["sha256"] for item in w8_binding.get("artifact_bindings", [])}
    runtime_ids = ["W8-CARGO-MANIFEST", "W8-CARGO-LOCK", "W8-RUST-LIBRARY", "W8-RUST-CLI", "W8-RUST-TESTS"]
    checks["VAL-W8-BASELINE-CURRENTNESS"] = (
        w8_decision.get("status") == "selected"
        and w8_decision.get("selection", {}).get("option_id") == "W8ACC-1"
        and w8_decision.get("accepted_w8_epoch", {}).get("manifest_ref", {}).get("sha256") == artifact_by_id["W8-EPOCH-MANIFEST"]["sha256"]
        and w8_decision.get("accepted_w8_epoch", {}).get("verdict_ref", {}).get("sha256") == artifact_by_id["W8-EPOCH-VERDICT"]["sha256"]
        and w8_verdict.get("result") == "PASS"
        and not w8_verdict.get("blockers")
        and w8_dependency_map.get("ontology-lifecycle/conformance/construction-binding.json") == artifact_by_id["W8-CONSTRUCTION-BINDING"]["sha256"]
        and all(w8_artifact_map.get(artifact_by_id[item]["path"]) == artifact_by_id[item]["sha256"] for item in runtime_ids)
    )

    proposal_text = (LAB / artifact_by_id["CONTEXT-ARCHITECTURE-DRAFT"]["path"]).read_text(encoding="utf-8")
    context_records = [load(LAB / record["path"]) for record in binding["context_boundary"]["records"]]
    checks["context_residue_preserved"] = (
        "- Status: `draft`" in proposal_text
        and "- Decision posture: `not-selected`" in proposal_text
        and all(record.get("status") == "candidate-unadmitted" for record in context_records)
        and all(record.get("authority_effect") == "none" for record in context_records)
        and all(record.get("context_map_refs") == [] for record in context_records)
        and binding.get("context_boundary", {}).get("cross_context_map_state") == "unselected"
    )

    validation_ids = {item["validation_id"] for item in binding.get("validation_contracts", [])}
    checks["validation_contract_coverage"] = validation_ids == {
        "VAL-BINDING-CURRENTNESS",
        "VAL-SYMBOL-CLOSURE",
        "VAL-W8-BASELINE-CURRENTNESS",
    }
    checks["authority_boundary"] = (
        binding.get("status") == "candidate-pending-owner-acceptance"
        and binding.get("gate", {}).get("state") == "BLOCK"
        and binding.get("authority_effect") == "none"
        and binding.get("implementation_authorized") is False
    )

    if OWNER_REQUEST_PATH.is_file():
        owner_request = load(OWNER_REQUEST_PATH)
        checks["owner_options_complete"] = (
            owner_request.get("candidate_sha256") == sha256(BINDING_PATH)
            and [option.get("option_id") for option in owner_request.get("options", [])]
            == ["D65BIND-1", "D65BIND-2", "D65BIND-3", "D65BIND-4"]
            and owner_request.get("gate_state") == "BLOCK"
        )
    else:
        checks["owner_options_complete"] = False

    if ADMISSIBILITY_REQUEST_PATH.is_file():
        admissibility_request = load(ADMISSIBILITY_REQUEST_PATH)
        checks["admissibility_request_current"] = (
            admissibility_request.get("candidate_sha256") == sha256(BINDING_PATH)
            and admissibility_request.get("schema_sha256") == sha256(SCHEMA_PATH)
            and admissibility_request.get("requested_outcome") == "gate"
            and admissibility_request.get("implementation_authorized") is False
        )
    else:
        checks["admissibility_request_current"] = False

    for check, passed in checks.items():
        if not passed and not any(failure.startswith(f"CHECK_FAILED:{check}") for failure in failures):
            failures.append(f"CHECK_FAILED:{check}")

    candidate_valid = not failures
    validation_receipt: dict[str, object] = {
        "schema_version": "cal.d65-s6-binding-validation-receipt/v1",
        "binding_id": binding.get("binding_id"),
        "candidate_sha256": sha256(BINDING_PATH),
        "schema_sha256": sha256(SCHEMA_PATH),
        "candidate_valid": candidate_valid,
        "result": "PASS" if candidate_valid else "BLOCK",
        "checks": checks,
        "bound_artifact_count": len(binding.get("bound_artifacts", [])),
        "existing_symbol_count": len(declared_symbols),
        "unresolved_symbols": unresolved_symbols,
        "unresolved_tests": unresolved_tests,
        "prospective_target_count": len(binding.get("planned_adapters", [])),
        "failures": failures,
        "gate_id": "G-D65-BINDING",
        "gate_state": "BLOCK",
        "gate_blocker": "Human implementation-owner selection is still required even when candidate_valid is true.",
        "implementation_authorized": False,
        "authority_effect": "none",
        "claim_ceiling": "PASS validates only currentness, symbol closure, W8 baseline closure, prospective-target absence, and authority boundaries for the D65-S6 candidate. It cannot accept the candidate or authorize implementation."
    }
    admissibility_receipt: dict[str, object] = {
        "schema_version": "cal.d65-s6-binding-admissibility-receipt/v1",
        "binding_id": binding.get("binding_id"),
        "candidate_sha256": sha256(BINDING_PATH),
        "prefilter_result": "PASS" if candidate_valid else "BLOCK",
        "route_outcome": "gate" if candidate_valid else "blocked",
        "admissible_for_owner_decision": candidate_valid,
        "presented_option_ids": ["D65BIND-1", "D65BIND-2", "D65BIND-3", "D65BIND-4"],
        "gate_id": "G-D65-BINDING",
        "gate_state": "BLOCK",
        "implementation_authorized": False,
        "authority_effect": "none",
        "claim_ceiling": "Admissibility PASS exposes the exact candidate to the human gate only; it is not selection, acceptance, conformance, or implementation authority."
    }
    return validation_receipt, admissibility_receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipts", action="store_true")
    args = parser.parse_args()
    validation_receipt, admissibility_receipt = validate()
    if args.write_receipts:
        canonical_write(VALIDATION_RECEIPT_PATH, validation_receipt)
        canonical_write(ADMISSIBILITY_RECEIPT_PATH, admissibility_receipt)
    print(json.dumps(validation_receipt, indent=2, sort_keys=True))
    return 0 if validation_receipt["candidate_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
