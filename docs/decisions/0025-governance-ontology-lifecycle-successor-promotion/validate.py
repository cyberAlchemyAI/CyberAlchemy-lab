#!/usr/bin/env python3
"""Validate the exact CTX05 successor and migration-plan admission overlay."""

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
        decision.get("decision_id") == "CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION"
        and decision.get("status") == "owner-admitted"
        and decision.get("authority_effect") == "four-successor-artifacts-two-lineage-records-and-one-migration-plan-admitted",
        {"id": decision.get("decision_id"), "status": decision.get("status"), "effect": decision.get("authority_effect")},
    )
    selection = decision["selection"]
    exact_token = "ADMIT-CTX05-SUCCESSORS-AND-MIGRATION-V1"
    check(
        "exact-owner-selection",
        selection.get("option_id") == exact_token
        and selection.get("selection_token") == exact_token
        and selection.get("selected_by_principal") == "person:<vrondelli>"
        and exact_token in selection.get("selection_source", ""),
        selection,
    )

    basis = decision["authority_basis"]
    owner_decision_path = LAB / basis["operational_owner_decision_path"]
    owner_registry_path = LAB / basis["owner_registry_path"]
    owner_decision = load(owner_decision_path)
    owner_registry = load(owner_registry_path)
    check(
        "owner-authority-inputs-current",
        sha(owner_decision_path) == basis["operational_owner_decision_sha256"]
        and owner_decision.get("status") == "owner-admitted"
        and sha(owner_registry_path) == basis["owner_registry_sha256"]
        and basis["principal_id"] == "person:<vrondelli>",
        {"decision": sha(owner_decision_path), "registry": sha(owner_registry_path)},
    )
    assignments = {item["role_id"]: item for item in owner_registry["role_assignments"]}
    selected_roles = {item.removeprefix("role:") for item in selection["selected_authorities"]}
    required_roles = {
        "governance-context-owner",
        "governance-language-owner",
        "ontology-lifecycle-context-owner",
        "ontology-lifecycle-language-owner",
        "context-lineage-owner",
        "context-migration-owner",
    }
    check(
        "six-separated-owner-roles-active",
        selected_roles == required_roles
        and all(assignments.get(role, {}).get("principal_id") == "person:<vrondelli>" and assignments[role].get("decision_separation") == "required" for role in required_roles),
        {role: assignments.get(role) for role in sorted(required_roles)},
    )

    prerequisite_results = []
    for item in decision["prerequisite_admissions"]:
        path = LAB / item["path"]
        prerequisite_results.append({"path": item["path"], "expected": item["sha256"], "actual": sha(path), "status": load(path).get("status")})
    check("prerequisite-admissions-current", all(item["expected"] == item["actual"] and item["status"] == "owner-admitted" for item in prerequisite_results), prerequisite_results)

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
        and conformance.get("summary", {}).get("protected_total") == evidence["protected_hashes"],
        {"sha256": sha(conformance_path), "result": conformance.get("result"), "summary": conformance.get("summary")},
    )

    artifact_results = []
    artifacts = {}
    for binding in decision["admitted_artifacts"]:
        path = LAB / binding["path"]
        projection = LAB / binding["human_projection_path"]
        data = load(path)
        artifacts[binding["artifact_id"]] = data
        artifact_results.append({
            "artifact_id": binding["artifact_id"],
            "machine": sha(path),
            "expected_machine": binding["sha256"],
            "projection": sha(projection),
            "expected_projection": binding["human_projection_sha256"],
            "status": data.get("status"),
            "effect": data.get("authority_effect"),
        })
    check("seven-artifact-byte-bindings-current", len(artifact_results) == 7 and all(item["machine"] == item["expected_machine"] and item["projection"] == item["expected_projection"] for item in artifact_results), artifact_results)
    check("immutable-candidate-bytes-preserved", all(item["status"] == "candidate-unadmitted" and item["effect"] == "none" for item in artifact_results), artifact_results)

    expected_types_and_owners = {
        "cal.context.governance/v2": ("cal.artifact-type.bounded-context/v1", "governance-context-owner", "admitted"),
        "cal.language.governance/v2": ("cal.artifact-type.ubiquitous-language/v1", "governance-language-owner", "admitted"),
        "cal.context.ontology-lifecycle/v2": ("cal.artifact-type.bounded-context/v1", "ontology-lifecycle-context-owner", "admitted"),
        "cal.language.ontology-lifecycle/v2": ("cal.artifact-type.ubiquitous-language/v1", "ontology-lifecycle-language-owner", "admitted"),
        "cal.context-lineage.governance.v1-to-v2": ("cal.artifact-type.context-lineage-record/v1", "context-lineage-owner", "admitted"),
        "cal.context-lineage.ontology-lifecycle.v1-to-v2": ("cal.artifact-type.context-lineage-record/v1", "context-lineage-owner", "admitted"),
        "cal.context-migration.governance-ontology-lifecycle-v1-to-v2": ("cal.artifact-type.context-migration-manifest/v1", "context-migration-owner", "admitted-plan-only"),
    }
    actual_types_and_owners = {item["artifact_id"]: (item["artifact_type_ref"], item["owner_role"], item["decision_overlay_status"]) for item in decision["admitted_artifacts"]}
    check("artifact-type-owner-overlay-closure", actual_types_and_owners == expected_types_and_owners, actual_types_and_owners)

    gov_context = artifacts["cal.context.governance/v2"]
    gov_language = artifacts["cal.language.governance/v2"]
    lifecycle_context = artifacts["cal.context.ontology-lifecycle/v2"]
    lifecycle_language = artifacts["cal.language.ontology-lifecycle/v2"]
    check(
        "reciprocal-v2-context-language-pairs",
        gov_context["ubiquitous_language_ref"] == "cal.language.governance/v2"
        and gov_language["bounded_context_ref"] == "cal.context.governance/v2"
        and lifecycle_context["ubiquitous_language_ref"] == "cal.language.ontology-lifecycle/v2"
        and lifecycle_language["bounded_context_ref"] == "cal.context.ontology-lifecycle/v2",
        {"governance": [gov_context["ubiquitous_language_ref"], gov_language["bounded_context_ref"]], "ontology_lifecycle": [lifecycle_context["ubiquitous_language_ref"], lifecycle_language["bounded_context_ref"]]},
    )

    map_ref = "cal.context-map.governance-ontology-lifecycle/v1"
    context_map = load(LAB / "contexts/maps/governance-ontology-lifecycle/v1/map.json")
    check(
        "map-reference-and-endpoint-boundary-preserved",
        gov_context["context_map_refs"] == [map_ref]
        and lifecycle_context["context_map_refs"] == [map_ref]
        and context_map["context_refs"] == ["cal.context.governance/v1", "cal.context.ontology-lifecycle/v1"]
        and decision["admission_result"]["context_map_endpoints_revised"] == 0,
        {"governance": gov_context["context_map_refs"], "ontology_lifecycle": lifecycle_context["context_map_refs"], "map_endpoints": context_map["context_refs"]},
    )

    gov_lineage = artifacts["cal.context-lineage.governance.v1-to-v2"]
    lifecycle_lineage = artifacts["cal.context-lineage.ontology-lifecycle.v1-to-v2"]
    check(
        "exact-successor-lineage-relations",
        gov_lineage["predecessor_context_ref"] == "cal.context.governance/v1"
        and gov_lineage["successor_context_refs"] == ["cal.context.governance/v2"]
        and lifecycle_lineage["predecessor_context_ref"] == "cal.context.ontology-lifecycle/v1"
        and lifecycle_lineage["successor_context_refs"] == ["cal.context.ontology-lifecycle/v2"]
        and all(item["lineage_kind"] == "successor" for item in (gov_lineage, lifecycle_lineage)),
        {"governance": [gov_lineage["predecessor_context_ref"], gov_lineage["successor_context_refs"]], "ontology_lifecycle": [lifecycle_lineage["predecessor_context_ref"], lifecycle_lineage["successor_context_refs"]]},
    )
    check("lineage-inference-remains-denied", all(item["equivalence_inferred"] is False and item["admission_inferred"] is False for item in (gov_lineage, lifecycle_lineage)) and decision["admission_result"]["equivalences_inferred"] == 0 and decision["admission_result"]["predecessors_superseded"] == 0, {"governance": [gov_lineage["equivalence_inferred"], gov_lineage["admission_inferred"]], "ontology_lifecycle": [lifecycle_lineage["equivalence_inferred"], lifecycle_lineage["admission_inferred"]]})

    migration = artifacts["cal.context-migration.governance-ontology-lifecycle-v1-to-v2"]
    preimage_results = []
    for item in migration["preimages"]:
        preimage_results.append({"path": item["path"], "expected": item["sha256"], "actual": sha(LAB / item["path"])})
    check("migration-five-preimages-current", len(preimage_results) == 5 and all(item["expected"] == item["actual"] for item in preimage_results), preimage_results)
    check("migration-plan-remains-non-effectful", migration["immutable"] is True and migration["execution_authority"] is False and decision["admission_result"]["migration_execution_authorizations"] == 0 and decision["admission_result"]["physical_source_packages_relocated"] == 0, {"immutable": migration["immutable"], "execution_authority": migration["execution_authority"], "result": decision["admission_result"]})
    rollback = migration["rollback_boundary"]
    check("rollback-boundary-preserved", all(term in rollback for term in ("no cutover", "undeleted", "restore every consumer", "five declared preimage digests", "new owner decision")), rollback)

    result_data = decision["admission_result"]
    check(
        "admission-cardinality",
        result_data == {
            "result": "complete-ctx05-successor-and-migration-plan-admission",
            "bounded_context_successors_admitted": 2,
            "ubiquitous_language_successors_admitted": 2,
            "lineage_records_admitted": 2,
            "migration_plans_admitted": 1,
            "migration_execution_authorizations": 0,
            "equivalences_inferred": 0,
            "predecessors_superseded": 0,
            "context_map_endpoints_revised": 0,
            "physical_source_packages_relocated": 0,
        },
        result_data,
    )
    check("projection-determinism-and-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(decision), str(OUTPUT))
    check(
        "successor-effects-excluded",
        all(term in decision["claim_ceiling"] for term in ("only the exact four CTX05 successor", "does not infer equivalence", "migration execution", "physical source relocation", "stable release"))
        and any("No v1 context" in item for item in decision["excluded_effects"])
        and any("No source-domain package" in item for item in decision["excluded_effects"])
        and any("No migration execution" in item for item in decision["excluded_effects"]),
        {"claim_ceiling": decision["claim_ceiling"], "excluded_effects": decision["excluded_effects"]},
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-ctx05-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": result,
        "authority_effect": "evidence-for-exact-ctx05-decision-overlay",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "admission_state": "complete-ctx05-successor-and-migration-plan-admission" if result == "PASS" else "not_evaluable",
        "next_gate": "successor-context-map-epoch-authorship-before-cutover",
        "claim_ceiling": decision["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX05_SUCCESSOR_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_GATE={receipt['next_gate']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
