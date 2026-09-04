#!/usr/bin/env python3
"""Validate the exact CTX04 Context Map admission overlay."""

import hashlib
import json
from pathlib import Path

from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
RECEIPT = ROOT / "receipts/admission-validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    decision = load(SOURCE)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check(
        "decision-identity",
        decision.get("decision_id") == "CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION"
        and decision.get("status") == "owner-admitted"
        and decision.get("authority_effect") == "one-exact-context-map-and-map-local-relationship-pattern-admitted",
        {"id": decision.get("decision_id"), "status": decision.get("status"), "effect": decision.get("authority_effect")},
    )

    selection = decision["selection"]
    check(
        "explicit-owner-approval",
        selection.get("option_id") == "ADMIT-CTX04-GOVERNANCE-ONTOLOGY-LIFECYCLE-MAP-V1"
        and selection.get("selection_token") == "approved"
        and selection.get("selected_by_principal") == "person:<vrondelli>"
        and selection.get("selected_authority") == "role:context-map-owner"
        and "Exact user instruction" in selection.get("selection_source", ""),
        selection,
    )

    basis = decision["authority_basis"]
    owner_decision_path = LAB / basis["operational_owner_decision_path"]
    owner_registry_path = LAB / basis["owner_registry_path"]
    owner_decision = load(owner_decision_path)
    owner_registry = load(owner_registry_path)
    assignments = {item["role_id"]: item for item in owner_registry["role_assignments"]}
    map_owner = assignments.get("context-map-owner", {})
    check(
        "context-map-owner-authority-current",
        sha(owner_decision_path) == basis["operational_owner_decision_sha256"]
        and owner_decision.get("status") == "owner-admitted"
        and sha(owner_registry_path) == basis["owner_registry_sha256"]
        and map_owner.get("principal_id") == basis["principal_id"] == "person:<vrondelli>"
        and map_owner.get("decision_separation") == "required",
        {"decision": sha(owner_decision_path), "registry": sha(owner_registry_path), "assignment": map_owner},
    )

    prerequisite_results = []
    for item in decision["prerequisite_admissions"]:
        path = LAB / item["path"]
        actual = sha(path)
        status = load(path).get("status")
        prerequisite_results.append({"path": item["path"], "expected": item["sha256"], "actual": actual, "status": status})
    check(
        "prerequisite-admissions-current",
        all(item["expected"] == item["actual"] and item["status"] == "owner-admitted" for item in prerequisite_results),
        prerequisite_results,
    )

    planning = decision["planning_basis"]
    planning_path = LAB / planning["path"]
    planning_decision = load(planning_path)
    boundary = planning_decision["selected_context_model"]["governance_boundary"]
    check(
        "planning-direction-current",
        sha(planning_path) == planning["sha256"]
        and planning_decision.get("status") == planning["required_status"]
        and boundary.get("upstream_context") == "Governance"
        and boundary.get("downstream_context") == "Ontology Lifecycle"
        and boundary.get("reverse_dependency_default") == "forbidden-unless-separately-authored-and-owner-selected",
        {"sha256": sha(planning_path), "status": planning_decision.get("status"), "boundary": boundary},
    )

    evidence = decision["candidate_evidence"]
    pack_path = LAB / evidence["pack_path"]
    pack_projection_path = LAB / evidence["pack_projection_path"]
    validation_path = LAB / evidence["validation_path"]
    conformance_path = LAB / evidence["conformance_path"]
    validation = load(validation_path)
    conformance = load(conformance_path)
    check(
        "candidate-pack-evidence-current",
        sha(pack_path) == evidence["pack_sha256"]
        and sha(pack_projection_path) == evidence["pack_projection_sha256"]
        and sha(validation_path) == evidence["validation_sha256"]
        and validation.get("result") == evidence["validation_result"] == "PASS"
        and validation.get("summary", {}).get("total") == evidence["validation_checks"],
        {"pack": sha(pack_path), "projection": sha(pack_projection_path), "validation": sha(validation_path), "summary": validation.get("summary")},
    )
    check(
        "candidate-conformance-current",
        sha(conformance_path) == evidence["conformance_sha256"]
        and conformance.get("result") == evidence["conformance_result"] == "PASS"
        and conformance.get("projection_parity") is True,
        {"sha256": sha(conformance_path), "result": conformance.get("result"), "projection_parity": conformance.get("projection_parity")},
    )

    binding = decision["admitted_map"]
    map_path = LAB / binding["path"]
    map_projection_path = LAB / binding["human_projection_path"]
    context_map = load(map_path)
    check(
        "exact-map-byte-binding-current",
        sha(map_path) == binding["sha256"] and sha(map_projection_path) == binding["human_projection_sha256"],
        {"machine": sha(map_path), "projection": sha(map_projection_path)},
    )
    check(
        "immutable-candidate-bytes-preserved",
        context_map.get("status") == binding["candidate_status"] == "candidate-unadmitted"
        and context_map.get("authority_effect") == "none"
        and binding.get("decision_overlay_status") == "admitted",
        {"status": context_map.get("status"), "effect": context_map.get("authority_effect"), "overlay": binding.get("decision_overlay_status")},
    )
    check(
        "map-identity-type-version-exact",
        context_map.get("context_map_id") == binding["context_map_id"] == "cal.context-map.governance-ontology-lifecycle"
        and context_map.get("version") == binding["version"]
        and context_map.get("classification", {}).get("artifact_type_ref") == binding["artifact_type_ref"] == "cal.artifact-type.context-map/v1",
        {"id": context_map.get("context_map_id"), "version": context_map.get("version"), "type": context_map.get("classification", {}).get("artifact_type_ref")},
    )

    expected_relationship = decision["admitted_relationship"]
    relationships = context_map.get("relationships", [])
    relationship = relationships[0] if len(relationships) == 1 else {}
    exact_keys = ("relationship_id", "source_context_ref", "target_context_ref", "direction", "relationship_kind_ref")
    check(
        "single-directional-relationship-exact",
        len(relationships) == 1
        and all(relationship.get(key) == expected_relationship.get(key) for key in exact_keys)
        and expected_relationship.get("decision_overlay_status") == "admitted",
        relationship,
    )
    check(
        "map-local-pattern-scope-preserved",
        expected_relationship.get("relationship_kind_scope") == "admitted-only-as-the-map-local-pattern-of-this-exact-relationship"
        and expected_relationship.get("global_relationship_kind_status") == "not-admitted"
        and context_map["relationships"][0]["relationship_kind_ref"].startswith("candidate:"),
        expected_relationship,
    )
    check(
        "authority-non-transfer-preserved",
        all(term in relationship.get("authority_boundary", "") for term in ("sole semantic and decision authority", "cannot create", "never authority")),
        relationship.get("authority_boundary"),
    )
    check(
        "reverse-dependency-absent",
        relationship.get("source_context_ref") == "cal.context.governance/v1"
        and relationship.get("target_context_ref") == "cal.context.ontology-lifecycle/v1"
        and not any(item.get("source_context_ref") == "cal.context.ontology-lifecycle/v1" for item in relationships),
        relationships,
    )

    governance_context = load(LAB / "contexts/governance/v1/context.json")
    lifecycle_context = load(LAB / "contexts/ontology-lifecycle/v1/context.json")
    check(
        "endpoint-artifacts-remain-unmutated",
        governance_context.get("context_map_refs") == []
        and lifecycle_context.get("context_map_refs") == []
        and decision["admission_result"]["endpoint_artifacts_mutated"] == 0,
        {"governance": governance_context.get("context_map_refs"), "ontology_lifecycle": lifecycle_context.get("context_map_refs")},
    )

    result_data = decision["admission_result"]
    check(
        "admission-cardinality",
        result_data == {
            "result": "complete-governance-to-ontology-lifecycle-context-map-admission",
            "context_maps_admitted": 1,
            "directional_relationships_admitted": 1,
            "global_relationship_kinds_admitted": 0,
            "reverse_dependencies_admitted": 0,
            "endpoint_artifacts_mutated": 0,
            "migration_manifests_admitted": 0,
            "runtime_adapters_admitted": 0,
        },
        result_data,
    )
    check("projection-determinism-and-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(decision), str(OUTPUT))
    check(
        "successor-effects-excluded",
        all(term in decision.get("claim_ceiling", "") for term in ("only the exact Governance-to-Ontology-Lifecycle Context Map", "global relationship kind", "reverse dependency", "migration", "stable release"))
        and any("No endpoint context" in item for item in decision["excluded_effects"])
        and any("No source governance ontology" in item for item in decision["excluded_effects"])
        and any("No migration planning" in item for item in decision["excluded_effects"]),
        {"claim_ceiling": decision.get("claim_ceiling"), "excluded_effects": decision["excluded_effects"]},
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-context-map-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": result,
        "authority_effect": "evidence-for-exact-context-map-decision-overlay",
        "checks": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "failed": sum(item["result"] == "FAIL" for item in checks),
            "total": len(checks),
        },
        "admission_state": "complete-governance-to-ontology-lifecycle-context-map-admission" if result == "PASS" else "not_evaluable",
        "next_gate": "successor-endpoint-context-epochs-and-migration-manifest-require-separate-authorship",
        "claim_ceiling": decision["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX04_CONTEXT_MAP_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_GATE={receipt['next_gate']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
