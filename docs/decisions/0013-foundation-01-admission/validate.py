#!/usr/bin/env python3
"""Validate the exact, narrowly scoped Foundation-01 admission decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from render import OUTPUT, SOURCE, render


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[2]
SOURCE_REPOSITORY = Path("/home/vrondelli/projects/domainspec-core")
RECEIPT = ROOT / "receipts" / "validation.json"

EXPECTED_MANIFEST_SHA256 = "cebb2837d492b6aa692033de7767ee5c7a0b56a7e2033681a5752362fdaa9c7c"
EXPECTED_FOUNDATION_RECEIPT_SHA256 = "fb59703a27e029178c7d1c0e467420761a3025392e67aad9e3ccb07acc47926c"
EXPECTED_PRINCIPAL = "person:<vrondelli>"
EXPECTED_TYPES = {
    "cal.artifact-type.artifact-type/v1",
    "cal.artifact-type.lifecycle-profile/v1",
    "cal.artifact-type.evaluation-profile/v1",
    "cal.artifact-type.owner-registry/v1",
    "cal.artifact-type.source-admission/v1",
    "cal.artifact-type.definition-registry/v1",
    "cal.artifact-type.drift-audit/v1",
    "cal.artifact-type.foundation-manifest/v1",
}
EXPECTED_ROLES = {
    "artifact-mechanics-owner",
    "artifact-type-owner",
    "definition-owner",
    "source-admission-owner",
    "evidence-conformance-owner",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_heading_digest(path: Path, selector: str) -> str | None:
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.startswith(f"## {selector}:")]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return hashlib.sha256("".join(lines[start:end]).encode("utf-8")).hexdigest()


def main() -> int:
    data = load(SOURCE)
    request_path = ROOT / data["admissibility"]["request_ref"]
    admissibility_path = ROOT / data["admissibility"]["receipt_ref"]
    request = load(request_path)
    admissibility = load(admissibility_path)
    manifest_path = LAB_ROOT / data["accepted_candidate"]["manifest_path"]
    foundation_receipt_path = LAB_ROOT / data["accepted_candidate"]["validation_receipt_path"]
    manifest = load(manifest_path)
    foundation_receipt = load(foundation_receipt_path)
    artifact_type = load(LAB_ROOT / "authority/artifact-types/artifact-type/v1/artifact.json")
    owners = load(LAB_ROOT / "authority/owners/foundation-01/v1/owners.json")
    source_admission_candidates = load(
        LAB_ROOT / "authority/decisions/source-admission/foundation-01/v1/admissions.json"
    )
    registry = load(LAB_ROOT / "authority/definitions/registry.json")
    drift_audit = load(LAB_ROOT / "authority/definitions/drift-audit.json")
    lifecycle = load(LAB_ROOT / "authority/profiles/definition/v1/lifecycle.json")
    evaluation = load(LAB_ROOT / "authority/profiles/definition/v1/evaluation.json")
    definition_type = load(LAB_ROOT / "authority/artifact-types/definition/v1/artifact.json")
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    check(
        "decision-identity",
        data.get("decision_id") == "CAL-DECISION-0013-FOUNDATION-01-ADMISSION"
        and data.get("status") == "owner-admitted",
        f"decision_id={data.get('decision_id')!r} status={data.get('status')!r}",
    )
    check(
        "bounded-authority-effect",
        data.get("authority_effect") == "foundation-01-semantic-admission-only",
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
        admissibility.get("routeOutcome") == "gate"
        and selected == "FOUNDATION-01-ADMIT"
        and selected in admissibility.get("admissibleOptionIds", [])
        and selected in admissibility.get("presentedOptionIds", []),
        f"selected={selected!r} route={admissibility.get('routeOutcome')!r}",
    )
    admission_request = next(
        (item for item in request.get("candidates", []) if item.get("optionId") == "FOUNDATION-01-ADMIT"),
        {},
    )
    check(
        "authority-option-has-owner-gate",
        admission_request.get("hazardClass") == "authority"
        and admission_request.get("reversibility") == "irreversible"
        and EXPECTED_PRINCIPAL in (admission_request.get("ownerGate") or ""),
        json.dumps(admission_request, sort_keys=True),
    )
    expected_token = (
        "user token FOUNDATION-01-ADMIT "
        f"manifest={EXPECTED_MANIFEST_SHA256} receipt={EXPECTED_FOUNDATION_RECEIPT_SHA256}"
    )
    check(
        "exact-owner-selection-token",
        data.get("selection", {}).get("selected_by_principal") == EXPECTED_PRINCIPAL
        and data.get("selection", {}).get("selection_source") == expected_token,
        f"source={data.get('selection', {}).get('selection_source')!r}",
    )

    check(
        "manifest-current",
        sha256(manifest_path) == data["accepted_candidate"]["manifest_sha256"] == EXPECTED_MANIFEST_SHA256,
        f"actual={sha256(manifest_path)}",
    )
    check(
        "foundation-receipt-current",
        sha256(foundation_receipt_path)
        == data["accepted_candidate"]["validation_receipt_sha256"]
        == EXPECTED_FOUNDATION_RECEIPT_SHA256,
        f"actual={sha256(foundation_receipt_path)}",
    )
    receipt_checks = foundation_receipt.get("checks", [])
    check(
        "foundation-validation-pass",
        foundation_receipt.get("result") == data["accepted_candidate"]["validation_result"] == "PASS"
        and len(receipt_checks) == data["accepted_candidate"]["validation_checks"] == 28
        and all(item.get("result") == "PASS" for item in receipt_checks),
        f"result={foundation_receipt.get('result')!r} checks={len(receipt_checks)}",
    )
    stale_materials = []
    for item in manifest.get("materials", []):
        path = LAB_ROOT / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            stale_materials.append(item["material_id"])
    check("manifest-material-closure", not stale_materials, f"stale_or_missing={stale_materials}")

    admitted_types = data.get("admitted_artifact_types", [])
    registered_types = {item["artifact_type_ref"] for item in artifact_type.get("registered_types", [])}
    check(
        "exact-admitted-type-set",
        set(admitted_types) == EXPECTED_TYPES and len(admitted_types) == len(EXPECTED_TYPES),
        f"admitted={sorted(admitted_types)}",
    )
    check(
        "admitted-types-registered",
        set(admitted_types) <= registered_types,
        f"unregistered={sorted(set(admitted_types) - registered_types)}",
    )
    check(
        "definition-type-explicitly-excluded",
        "cal.artifact-type.definition/v1" in registered_types
        and "cal.artifact-type.definition/v1" not in set(admitted_types)
        and all("authority/artifact-types/definition/v1/artifact.json" != item.get("path") for item in data.get("admitted_records", [])),
        f"definition_status={definition_type.get('status')!r}",
    )

    stale_admitted_records = []
    for item in data.get("admitted_records", []):
        path = LAB_ROOT / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            stale_admitted_records.append(item["record_id"])
    check(
        "admitted-record-digest-closure",
        len(data.get("admitted_records", [])) == 8 and not stale_admitted_records,
        f"count={len(data.get('admitted_records', []))} stale_or_missing={stale_admitted_records}",
    )
    stale_schemas = []
    for item in data.get("admitted_schema_bindings", []):
        path = LAB_ROOT / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            stale_schemas.append(item["schema_ref"])
    check(
        "admitted-schema-binding-closure",
        len(data.get("admitted_schema_bindings", [])) == 2 and not stale_schemas,
        f"stale_or_missing={stale_schemas}",
    )

    principal_ids = {item["principal_id"] for item in owners.get("principals", [])}
    assignment_roles = {item["role_id"] for item in owners.get("role_assignments", [])}
    determination_roles = {item["role_id"] for item in data.get("role_scoped_determinations", [])}
    check(
        "bootstrap-principal-exact",
        principal_ids == {EXPECTED_PRINCIPAL}
        and data.get("bootstrap_owner_identity", {}).get("principal_id") == EXPECTED_PRINCIPAL,
        f"principals={sorted(principal_ids)}",
    )
    check(
        "role-scope-closure",
        assignment_roles == determination_roles == EXPECTED_ROLES
        and all(item.get("principal_id") == EXPECTED_PRINCIPAL for item in data.get("role_scoped_determinations", [])),
        f"assignments={sorted(assignment_roles)} determinations={sorted(determination_roles)}",
    )

    candidate_admissions = [
        {
            "admission_id": item["admission_id"],
            "selector": item["selector"],
            "selected_sha256": item["selected_sha256"],
            "target_use": item["target_use"],
        }
        for item in source_admission_candidates.get("admissions", [])
    ]
    check(
        "source-admission-exact-scope",
        data.get("source_admissions") == candidate_admissions and len(candidate_admissions) == 3,
        f"selectors={[item['selector'] for item in candidate_admissions]}",
    )
    source_file = SOURCE_REPOSITORY / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"
    live_selector_digests = {
        item["selector"]: selected_heading_digest(source_file, item["selector"])
        for item in data.get("source_admissions", [])
    }
    admitted_selector_digests = {
        item["selector"]: item["selected_sha256"] for item in data.get("source_admissions", [])
    }
    check(
        "source-selector-live-currentness",
        live_selector_digests == admitted_selector_digests,
        f"actual={live_selector_digests}",
    )

    definition_state = data.get("definition_authority_state", {})
    registry_path = LAB_ROOT / definition_state.get("canonical_registry_path", "")
    index_path = LAB_ROOT / definition_state.get("generated_index_path", "")
    audit_path = LAB_ROOT / definition_state.get("drift_audit_path", "")
    check(
        "empty-canonical-definition-registry",
        registry.get("entries") == []
        and definition_state.get("admitted_entry_count") == 0
        and sha256(registry_path) == definition_state.get("registry_sha256"),
        f"entries={len(registry.get('entries', []))}",
    )
    check(
        "definition-index-bound",
        index_path.is_file()
        and sha256(index_path) == definition_state.get("generated_index_sha256")
        and registry.get("source_direction", {}).get("projection_policy") == "generated-only",
        f"index_sha256={sha256(index_path) if index_path.is_file() else None}",
    )
    check(
        "drift-surface-bounded",
        audit_path.is_file()
        and sha256(audit_path) == definition_state.get("drift_audit_sha256")
        and drift_audit.get("summary", {}).get("undefined_critical_terms") == 1
        and definition_state.get("drift_snapshot_posture") == "accepted-pre-admission-baseline-not-current-postimage"
        and "Refresh" in definition_state.get("required_next_audit", ""),
        f"audit_sha256={sha256(audit_path) if audit_path.is_file() else None}",
    )

    preserved_statuses = {
        artifact_type.get("status"),
        lifecycle.get("status"),
        evaluation.get("status"),
        owners.get("status"),
        source_admission_candidates.get("status"),
        registry.get("status"),
        drift_audit.get("status"),
        manifest.get("status"),
        definition_type.get("status"),
    }
    check(
        "candidate-input-bytes-preserved",
        preserved_statuses == {"candidate-unadmitted"}
        and all(item.get("candidate_status") == "pending-exact-owner-decision" for item in source_admission_candidates.get("admissions", []))
        and data["accepted_candidate"].get("candidate_bytes_policy") == "immutable-inputs-preserved",
        f"embedded_statuses={sorted(preserved_statuses)}",
    )

    d65 = {item["stage"]: item["status"] for item in manifest.get("d65_boundary", [])}
    check(
        "d65-claims-remain-missing",
        d65
        == {
            "canonical definitions": "candidate",
            "Product Capability": "missing",
            "capability-local business ontology": "missing",
            "DomainSpec v2 authored source": "missing",
            "deterministic compiled graph and system ontology": "missing",
            "exact implementation binding": "not_evaluable",
            "conformance evidence": "not_evaluable",
        },
        f"stages={d65}",
    )
    exclusions = " ".join(data.get("excluded_effects", []))
    check(
        "runtime-publication-stable-version-excluded",
        all(term in exclusions for term in ("not admitted runtimes", "No Git commit", "first stable version", "No Product Capability")),
        exclusions,
    )
    result_record = data.get("admission_result", {})
    check(
        "admission-result-bounded-pass",
        result_record.get("result") == "complete-semantic-foundation-admission"
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
            "foundation_manifest_sha256": sha256(manifest_path),
            "foundation_validation_sha256": sha256(foundation_receipt_path),
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
