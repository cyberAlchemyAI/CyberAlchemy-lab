#!/usr/bin/env python3
"""Validate the bounded Definition/v1 artifact-type admission decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from render import OUTPUT, SOURCE, render


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[2]
RECEIPT = ROOT / "receipts/validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    data = load(SOURCE)
    request_path = ROOT / data["admissibility"]["request_ref"]
    admissibility_path = ROOT / data["admissibility"]["receipt_ref"]
    request = load(request_path)
    admissibility = load(admissibility_path)
    candidate_path = LAB_ROOT / data["accepted_candidate"]["path"]
    candidate_view_path = LAB_ROOT / data["accepted_candidate"]["human_projection_path"]
    candidate_receipt_path = LAB_ROOT / data["accepted_candidate"]["validation_receipt_path"]
    candidate = load(candidate_path)
    candidate_receipt = load(candidate_receipt_path)
    foundation_path = LAB_ROOT / data["prerequisite_bindings"]["foundation_admission"]["path"]
    foundation = load(foundation_path)
    root_type_path = LAB_ROOT / data["prerequisite_bindings"]["artifact_type_root"]["path"]
    root_type = load(root_type_path)
    schema_path = LAB_ROOT / data["prerequisite_bindings"]["definition_schema"]["path"]
    owner_path = LAB_ROOT / data["prerequisite_bindings"]["owner_registry"]["path"]
    owners = load(owner_path)
    registry_path = LAB_ROOT / "authority/definitions/registry.json"
    registry = load(registry_path)
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    check(
        "decision-identity",
        data.get("decision_id") == "CAL-DECISION-0015-DEFINITION-V1-ADMISSION"
        and data.get("status") == "owner-admitted",
        f"decision_id={data.get('decision_id')!r} status={data.get('status')!r}",
    )
    check(
        "bounded-authority-effect",
        data.get("authority_effect") == "definition-v1-artifact-type-admission-only",
        f"authority_effect={data.get('authority_effect')!r}",
    )
    direction = data.get("source_direction", {})
    check(
        "machine-canonical-human-generated",
        direction.get("canonical") == SOURCE.name
        and direction.get("human_projection") == OUTPUT.name
        and direction.get("projection_policy") == "generated-only",
        json.dumps(direction, sort_keys=True),
    )

    check(
        "admissibility-request-current",
        sha256(request_path) == data["admissibility"]["request_sha256"],
        f"actual={sha256(request_path)}",
    )
    check(
        "admissibility-receipt-current",
        sha256(admissibility_path) == data["admissibility"]["receipt_sha256"],
        f"actual={sha256(admissibility_path)}",
    )
    check(
        "admissibility-request-digest",
        canonical_digest(request)
        == data["admissibility"]["request_digest"]
        == admissibility.get("requestDigest"),
        f"computed={canonical_digest(request)} receipt={admissibility.get('requestDigest')}",
    )
    selected = data.get("selection", {}).get("option_id")
    check(
        "selected-option-admissible",
        selected == "ADMIT-DEFINITION-V1"
        and admissibility.get("routeOutcome") == "gate"
        and selected in admissibility.get("admissibleOptionIds", [])
        and selected in admissibility.get("presentedOptionIds", []),
        f"selected={selected!r} route={admissibility.get('routeOutcome')!r}",
    )
    selected_request = next((item for item in request.get("candidates", []) if item.get("optionId") == selected), {})
    check(
        "authority-option-owner-gated",
        selected_request.get("hazardClass") == "authority"
        and selected_request.get("reversibility") == "irreversible"
        and "person:<vrondelli>" in (selected_request.get("ownerGate") or ""),
        json.dumps(selected_request, sort_keys=True),
    )
    check(
        "exact-owner-instruction",
        data.get("selection", {}).get("selected_by_principal") == "person:<vrondelli>"
        and data.get("selection", {}).get("selected_under_role") == "artifact-type-owner"
        and data.get("selection", {}).get("selection_source") == "user instruction ADMIT-DEFINITION-V1",
        json.dumps(data.get("selection"), sort_keys=True),
    )

    check(
        "candidate-current",
        sha256(candidate_path) == data["accepted_candidate"]["sha256"]
        and candidate.get("version") == data["accepted_candidate"]["candidate_version"] == "1.0.0-candidate.2"
        and candidate.get("status") == "candidate-unadmitted"
        and candidate.get("authority_effect") == "none",
        f"actual={sha256(candidate_path)} version={candidate.get('version')!r}",
    )
    check(
        "candidate-projection-current",
        sha256(candidate_view_path) == data["accepted_candidate"]["human_projection_sha256"],
        f"actual={sha256(candidate_view_path)}",
    )
    candidate_checks = candidate_receipt.get("checks", [])
    check(
        "candidate-validation-current-pass",
        sha256(candidate_receipt_path) == data["accepted_candidate"]["validation_receipt_sha256"]
        and candidate_receipt.get("result") == data["accepted_candidate"]["validation_result"] == "PASS"
        and len(candidate_checks) == data["accepted_candidate"]["validation_checks"] == 26
        and all(item.get("result") == "PASS" for item in candidate_checks),
        f"actual={sha256(candidate_receipt_path)} result={candidate_receipt.get('result')!r} checks={len(candidate_checks)}",
    )

    stale_prerequisites = []
    for binding_id, binding in data.get("prerequisite_bindings", {}).items():
        path = LAB_ROOT / binding["path"]
        if not path.is_file() or sha256(path) != binding["sha256"]:
            stale_prerequisites.append(binding_id)
    check("prerequisite-digest-closure", not stale_prerequisites, f"stale_or_missing={stale_prerequisites}")
    check(
        "foundation-root-admitted",
        foundation.get("status") == "owner-admitted"
        and "cal.artifact-type.artifact-type/v1" in foundation.get("admitted_artifact_types", []),
        f"foundation_status={foundation.get('status')!r}",
    )
    registered_definition = next(
        (item for item in root_type.get("registered_types", []) if item.get("artifact_type_ref") == "cal.artifact-type.definition/v1"),
        {},
    )
    check(
        "definition-type-registered-with-current-schema",
        registered_definition.get("schema_sha256") == sha256(schema_path) == candidate.get("schema_digest")
        and registered_definition.get("schema_path") == data["prerequisite_bindings"]["definition_schema"]["path"],
        json.dumps(registered_definition, sort_keys=True),
    )
    role_assignments = {item["role_id"]: item["principal_id"] for item in owners.get("role_assignments", [])}
    check(
        "artifact-type-owner-resolves",
        role_assignments.get("artifact-type-owner") == "person:<vrondelli>"
        and role_assignments.get("definition-owner") == "person:<vrondelli>",
        json.dumps(role_assignments, sort_keys=True),
    )

    contract = data.get("admitted_contract", {})
    check(
        "exact-contract-admitted",
        contract.get("artifact_type_ref") == "cal.artifact-type.definition/v1"
        and contract.get("current_source_version") == "1.0.0-candidate.2"
        and contract.get("lifecycle_state") == "admitted"
        and contract.get("schema_ref") == "cal.schema.definition/v1",
        json.dumps(contract, sort_keys=True),
    )
    resolved = {item["residue_id"] for item in data.get("residue_transition", {}).get("resolved", [])}
    remaining = {item["residue_id"] for item in data.get("residue_transition", {}).get("remaining", [])}
    check(
        "residue-transition-bounded",
        resolved == {"CAL-DEFV1-R6"} and remaining == {"CAL-DEFV1-R7", "CAL-DEFV1-R8"},
        f"resolved={sorted(resolved)} remaining={sorted(remaining)}",
    )
    check(
        "canonical-registry-unchanged-empty",
        sha256(registry_path) == "ed7575bd0754136c3075ba1a8d132d4673f2b6f6c1fc258c3734debc8c51b33f"
        and registry.get("entries") == [],
        f"sha256={sha256(registry_path)} entries={len(registry.get('entries', []))}",
    )
    exclusions = " ".join(data.get("excluded_effects", []))
    check(
        "term-runtime-publication-excluded",
        all(term in exclusions for term in ("does not create, admit, or promote the term Definition", "not admitted tools", "No Git commit", "first stable version")),
        exclusions,
    )
    result_record = data.get("admission_result", {})
    check(
        "admission-result-pass",
        result_record.get("result") == "complete-definition-v1-artifact-type-admission"
        and result_record.get("decision_gate_result") == "PASS"
        and result_record.get("blocker_decisions_resolved") == 1
        and result_record.get("blocker_decisions_remaining") == 0,
        json.dumps(result_record, sort_keys=True),
    )

    rendered_a = render(data)
    rendered_b = render(data)
    check(
        "two-run-render-determinism",
        rendered_a == rendered_b,
        f"sha256={hashlib.sha256(rendered_a.encode()).hexdigest()}",
    )
    check(
        "projection-parity",
        OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == rendered_a,
        "DECISION.md must exactly equal render(decision.json)",
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-decision-validation/v0",
        "decision_id": data.get("decision_id"),
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {
            "decision_json_sha256": sha256(SOURCE),
            "decision_md_sha256": sha256(OUTPUT) if OUTPUT.is_file() else None,
            "admissibility_request_sha256": sha256(request_path),
            "admissibility_receipt_sha256": sha256(admissibility_path),
            "definition_v1_candidate_sha256": sha256(candidate_path),
            "definition_v1_candidate_validation_sha256": sha256(candidate_receipt_path),
            "foundation_decision_sha256": sha256(foundation_path),
            "definition_schema_sha256": sha256(schema_path),
            "definition_registry_sha256": sha256(registry_path),
        },
        "claim_ceiling": data.get("claim_ceiling"),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{result}: {sum(item['result'] == 'PASS' for item in checks)}/{len(checks)} checks passed")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
