#!/usr/bin/env python3
"""Validate the exact CTX06 Definition admission and live postimages."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from render import (
    DECISION_OUTPUT,
    DECISION_SOURCE,
    DRIFT_OUTPUT,
    DRIFT_SOURCE,
    REGISTRY_OUTPUT,
    REGISTRY_SOURCE,
    render_decision,
    render_drift,
    render_registry,
)

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
RECEIPT = ROOT / "receipts/admission-validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    decision = load(DECISION_SOURCE)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check(
        "decision-identity",
        decision.get("decision_id") == "CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION"
        and decision.get("status") == "owner-admitted"
        and decision.get("authority_effect") == "two-successor-definition-versions-admitted-and-current-lookup-selected",
        {"id": decision.get("decision_id"), "status": decision.get("status"), "effect": decision.get("authority_effect")},
    )
    selection = decision["selection"]
    exact_token = "ADMIT-CTX06-REFERENCE-NORMALIZATION-DEFINITIONS-V2"
    check(
        "exact-owner-selection",
        selection.get("option_id") == exact_token
        and selection.get("selection_token") == exact_token
        and selection.get("selected_by_principal") == "person:<vrondelli>"
        and selection.get("selected_role") == "definition-owner"
        and exact_token in selection.get("selection_source", ""),
        selection,
    )

    authority = decision["authority_basis"]
    owner_path = LAB / authority["owner_registry_path"]
    owner_registry = load(owner_path)
    assignment = next((item for item in owner_registry["role_assignments"] if item["role_id"] == authority["owner_role"]), None)
    check(
        "definition-owner-authority-current",
        sha(owner_path) == authority["owner_registry_sha256"]
        and assignment is not None
        and assignment["principal_id"] == authority["principal_id"] == "person:<vrondelli>"
        and assignment["decision_separation"] == "required",
        {"sha256": sha(owner_path), "assignment": assignment},
    )

    prerequisite_results = []
    for item in decision["prerequisite_admissions"]:
        path = LAB / item["path"]
        record = load(path)
        prerequisite_results.append({"path": item["path"], "expected": item["sha256"], "actual": sha(path), "status": record.get("status")})
    check("prerequisite-admissions-current", all(item["expected"] == item["actual"] and item["status"] == "owner-admitted" for item in prerequisite_results), prerequisite_results)

    evidence = decision["candidate_evidence"]
    candidate_path = LAB / evidence["candidate_path"]
    candidate_projection_path = LAB / evidence["candidate_projection_path"]
    validation_path = LAB / evidence["validation_path"]
    candidate = load(candidate_path)
    validation = load(validation_path)
    check(
        "candidate-evidence-current",
        sha(candidate_path) == evidence["candidate_sha256"]
        and sha(candidate_projection_path) == evidence["candidate_projection_sha256"]
        and sha(validation_path) == evidence["validation_sha256"]
        and validation.get("result") == evidence["validation_result"] == "PASS"
        and validation.get("promotion_eligibility") == evidence["promotion_eligibility"] == "eligible-for-exact-owner-decision"
        and validation.get("summary", {}).get("total") == evidence["validation_checks"] == 36,
        {"candidate": sha(candidate_path), "projection": sha(candidate_projection_path), "validation": sha(validation_path), "summary": validation.get("summary")},
    )

    schema_path = LAB / "authority/artifact-types/definition/v1/schema.json"
    schema = load(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    definition_results = []
    for item in decision["admitted_definitions"]:
        path = LAB / item["path"]
        projection = LAB / item["human_projection_path"]
        record = load(path)
        successor_relation = next((rel for rel in record["typed_relations"] if rel["relation_kind_ref"] == "relation.successor-of"), None)
        definition_results.append(
            {
                "definition_id": item["definition_id"],
                "version": record.get("version"),
                "machine": sha(path),
                "expected_machine": item["sha256"],
                "projection": sha(projection),
                "expected_projection": item["human_projection_sha256"],
                "schema_errors": [error.message for error in validator.iter_errors(record)],
                "successor_target": successor_relation.get("to_ref") if successor_relation else None,
                "expected_predecessor": item["predecessor_ref"],
                "plain_normative": record["voices"]["plain_language"]["normative"],
                "domain_normative": record["voices"]["domain_context"]["normative"],
            }
        )
    check(
        "two-exact-definition-bindings-current",
        len(definition_results) == 2
        and all(
            item["machine"] == item["expected_machine"]
            and item["projection"] == item["expected_projection"]
            and not item["schema_errors"]
            and item["version"] == "2.0.0-candidate.1"
            and item["successor_target"] == item["expected_predecessor"]
            and item["plain_normative"] is False
            and item["domain_normative"] is False
            for item in definition_results
        ),
        definition_results,
    )
    bc = load(LAB / decision["admitted_definitions"][0]["path"])
    cm = load(LAB / decision["admitted_definitions"][1]["path"])
    check(
        "normalized-reference-ownership",
        "context_map_refs" not in bc["voices"]["scientific_formal"]["formal_expression"].split(");", 1)[0]
        and "CanonicalOwner(ContextMapMembership) = ContextMap" in bc["voices"]["scientific_formal"]["formal_expression"]
        and "CanonicalOwner(context_refs,relationships) = ContextMap" in cm["voices"]["scientific_formal"]["formal_expression"]
        and "ReverseMembershipIndex" in bc["voices"]["scientific_formal"]["formal_expression"]
        and "ReverseMembershipIndex" in cm["voices"]["scientific_formal"]["formal_expression"],
        {"bounded_context": bc["voices"]["scientific_formal"]["formal_expression"], "context_map": cm["voices"]["scientific_formal"]["formal_expression"]},
    )

    candidate_postimage_results = []
    for item in decision["candidate_postimages"].values():
        path = LAB / item["path"]
        candidate_postimage_results.append({"path": item["path"], "expected": item["sha256"], "actual": sha(path)})
    check("candidate-postimages-preserved", all(item["expected"] == item["actual"] for item in candidate_postimage_results), candidate_postimage_results)

    registry = load(REGISTRY_SOURCE)
    registry_binding = decision["canonical_postimages"]["registry"]
    current_expected = {
        "cal.definition.bounded-context": "cal.definition.bounded-context@2.0.0-candidate.1",
        "cal.definition.context-map": "cal.definition.context-map@2.0.0-candidate.1",
    }
    new_entries = [item for item in registry["entries"] if item["admission_decision_ref"] == decision["decision_id"]]
    old_entries = [item for item in registry["entries"] if item["definition_id"] in current_expected and item["version"] == "1.0.0-candidate.1"]
    check(
        "canonical-registry-current",
        sha(REGISTRY_SOURCE) == registry_binding["sha256"]
        and len(registry["entries"]) == registry_binding["entry_count"] == 10
        and len(registry["current_lookup"]) == registry_binding["current_term_count"] == 8
        and all(registry["current_lookup"].get(key) == value for key, value in current_expected.items())
        and len(new_entries) == 2
        and all(item["lifecycle_state"] == "admitted" for item in new_entries)
        and len(old_entries) == 2
        and all(item["lifecycle_state"] == "admitted" and item["admission_decision_ref"] == "CAL-DECISION-0018-DEFINITION-AND-CTX00-PROMOTION" for item in old_entries),
        {"sha256": sha(REGISTRY_SOURCE), "entries": len(registry["entries"]), "current_lookup": registry["current_lookup"], "new_entries": new_entries, "old_entries": old_entries},
    )
    renderer_path = ROOT / "render.py"
    check(
        "projection-generator-current",
        registry["source_direction"]["generator_sha256"] == sha(renderer_path)
        and load(DRIFT_SOURCE)["source_direction"]["generator_sha256"] == sha(renderer_path),
        {"actual": sha(renderer_path), "registry": registry["source_direction"]["generator_sha256"], "drift": load(DRIFT_SOURCE)["source_direction"]["generator_sha256"]},
    )
    index_binding = decision["canonical_postimages"]["generated_index"]
    check(
        "generated-index-parity",
        sha(REGISTRY_OUTPUT) == index_binding["sha256"] and REGISTRY_OUTPUT.read_text(encoding="utf-8") == render_registry(registry).rstrip() + "\n",
        sha(REGISTRY_OUTPUT),
    )

    drift = load(DRIFT_SOURCE)
    drift_binding = decision["canonical_postimages"]["drift_audit"]
    check(
        "current-drift-audit",
        sha(DRIFT_SOURCE) == drift_binding["sha256"]
        and drift["registry_sha256"] == registry_binding["sha256"]
        and drift["admission_decision_ref"] == decision["decision_id"]
        and drift["summary"]["admitted_definition_versions"] == 10
        and drift["summary"]["current_definition_terms"] == 8
        and drift["summary"]["undefined_critical_terms"] == 0
        and drift["summary"]["conflicting_current_consumer_groups"] == 4
        and drift["summary"]["historical_epochs_rewritten"] == 0,
        {"sha256": sha(DRIFT_SOURCE), "summary": drift["summary"]},
    )
    drift_view_binding = decision["canonical_postimages"]["generated_drift_view"]
    check(
        "generated-drift-parity",
        sha(DRIFT_OUTPUT) == drift_view_binding["sha256"] and DRIFT_OUTPUT.read_text(encoding="utf-8") == render_drift(drift).rstrip() + "\n",
        sha(DRIFT_OUTPUT),
    )

    candidate_predecessors = {item["predecessor_path"]: item["predecessor_sha256"] for item in candidate["definitions"]}
    predecessor_results = [{"path": path, "expected": expected, "actual": sha(LAB / path)} for path, expected in candidate_predecessors.items()]
    check("v1-definition-bytes-preserved", all(item["expected"] == item["actual"] for item in predecessor_results), predecessor_results)

    admission_result = decision["admission_result"]
    check(
        "admission-cardinality-and-boundary",
        admission_result == {
            "result": "complete-ctx06-definition-successor-admission",
            "definition_evaluation_gate": "DEF-EVAL-07-PASS-BY-OWNER-SELECTION",
            "successor_definitions_admitted": 2,
            "canonical_definition_versions": 10,
            "current_definition_terms": 8,
            "predecessors_withdrawn": 0,
            "predecessors_superseded": 0,
            "artifact_types_revised": 0,
            "context_instances_revised": 0,
            "context_maps_revised": 0,
            "migration_executions_authorized": 0,
        },
        admission_result,
    )
    check("decision-projection-parity", DECISION_OUTPUT.is_file() and DECISION_OUTPUT.read_text(encoding="utf-8") == render_decision(decision).rstrip() + "\n", str(DECISION_OUTPUT))
    check(
        "successor-effects-excluded",
        all(term in decision["claim_ceiling"] for term in ("only the exact Bounded Context/v2 and Context Map/v2 Definition versions", "does not revise or admit artifact types", "stable-release state"))
        and any("No v1 Definition" in item for item in decision["excluded_effects"])
        and any("No Bounded Context/v2 or Context Map/v2 artifact type" in item for item in decision["excluded_effects"])
        and any("No successor Context Map" in item for item in decision["excluded_effects"]),
        {"claim_ceiling": decision["claim_ceiling"], "excluded_effects": decision["excluded_effects"]},
    )

    failed = [item for item in checks if item["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-ctx06-definition-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": result,
        "authority_effect": "evidence-for-exact-ctx06-definition-admission",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "admission_state": "complete-ctx06-definition-successor-admission" if result == "PASS" else "not_evaluable",
        "next_gate": "author-normalized-bounded-context-and-context-map-v2-artifact-types",
        "materials": {
            "decision_sha256": sha(DECISION_SOURCE),
            "decision_projection_sha256": sha(DECISION_OUTPUT),
            "registry_sha256": sha(REGISTRY_SOURCE),
            "definition_index_sha256": sha(REGISTRY_OUTPUT),
            "drift_audit_sha256": sha(DRIFT_SOURCE),
            "drift_projection_sha256": sha(DRIFT_OUTPUT),
        },
        "claim_ceiling": decision["claim_ceiling"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX06_DEFINITION_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_GATE={receipt['next_gate']}")
    for item in failed:
        print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
