#!/usr/bin/env python3
"""Validate the exact CTX07 normalized artifact-type admission overlay."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"
RECEIPT = ROOT / "receipts/admission-validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_renderer():
    path = ROOT / "render.py"
    spec = importlib.util.spec_from_file_location("ctx07_decision_renderer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render


def main() -> int:
    decision = load(SOURCE)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    expected_id = "CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION"
    expected_token = "ADMIT-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPES-V2"
    check(
        "decision-identity",
        decision.get("decision_id") == expected_id
        and decision.get("status") == "owner-admitted"
        and decision.get("authority_effect") == "two-normalized-context-artifact-type-versions-admitted-for-new-construction",
        {"id": decision.get("decision_id"), "status": decision.get("status"), "effect": decision.get("authority_effect")},
    )

    selection = decision.get("selection", {})
    check(
        "exact-owner-selection",
        selection.get("option_id") == selection.get("selection_token") == expected_token
        and selection.get("selected_role") == "artifact-type-owner"
        and selection.get("selected_by_principal") == "person:<vrondelli>"
        and expected_token in selection.get("selection_source", ""),
        selection,
    )

    authority = decision["authority_basis"]
    owner_path = LAB / authority["owner_registry_path"]
    assignments = load(owner_path)["role_assignments"]
    assignment = next((item for item in assignments if item["role_id"] == authority["owner_role"]), None)
    check(
        "artifact-type-owner-authority-current",
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
        prerequisite_results.append(
            {"path": item["path"], "expected": item["sha256"], "actual": sha(path), "status": record.get("status")}
        )
    check(
        "prerequisite-admissions-current",
        all(item["expected"] == item["actual"] and item["status"] == "owner-admitted" for item in prerequisite_results),
        prerequisite_results,
    )

    evidence = decision["candidate_evidence"]
    pack_path = LAB / evidence["pack_path"]
    pack_projection_path = LAB / evidence["pack_projection_path"]
    validation_path = LAB / evidence["validation_path"]
    conformance_path = LAB / evidence["conformance_path"]
    pack = load(pack_path)
    validation = load(validation_path)
    conformance = load(conformance_path)
    check(
        "candidate-evidence-current",
        sha(pack_path) == evidence["pack_sha256"]
        and sha(pack_projection_path) == evidence["pack_projection_sha256"]
        and sha(validation_path) == evidence["validation_sha256"]
        and validation.get("result") == evidence["validation_result"] == "PASS"
        and validation.get("promotion_eligibility") == evidence["promotion_eligibility"]
        and validation.get("summary", {}).get("total") == evidence["validation_checks"] == 23
        and sha(conformance_path) == evidence["conformance_sha256"]
        and conformance.get("result") == evidence["conformance_result"] == "PASS"
        and conformance.get("summary", {}).get("total") == evidence["conformance_tests"] == 3
        and conformance.get("current_gate_state") == evidence["conformance_gate_state"],
        {
            "pack": sha(pack_path),
            "projection": sha(pack_projection_path),
            "validation": sha(validation_path),
            "validation_summary": validation.get("summary"),
            "conformance": sha(conformance_path),
            "conformance_summary": conformance.get("summary"),
            "gate": conformance.get("current_gate_state"),
        },
    )

    mechanics_results = []
    for name in ("schema", "generator", "validator"):
        binding = decision["shared_mechanics_evidence"][name]
        path = LAB / binding["path"]
        mechanics_results.append(
            {"name": name, "path": binding["path"], "expected": binding["sha256"], "actual": sha(path)}
        )
    check(
        "shared-mechanics-current-and-nonauthoritative",
        all(item["expected"] == item["actual"] for item in mechanics_results)
        and decision["shared_mechanics_evidence"]["authority_effect"] == "none"
        and decision["shared_mechanics_evidence"]["runtime_admission"] == "not-granted",
        mechanics_results,
    )

    admitted = decision["admitted_artifact_types"]
    pack_types = pack["artifact_types"]
    check(
        "exact-two-type-closure",
        [item["artifact_type_ref"] for item in admitted] == [item["artifact_type_ref"] for item in pack_types]
        == ["cal.artifact-type.bounded-context/v2", "cal.artifact-type.context-map/v2"],
        [item["artifact_type_ref"] for item in admitted],
    )

    material_results = []
    for item in admitted:
        artifact_path = LAB / item["artifact_path"]
        projection_path = LAB / item["human_projection_path"]
        schema_path = LAB / item["schema_path"]
        receipt_path = LAB / item["validation_receipt_path"]
        definition_path = LAB / item["definition_path"]
        predecessor_path = LAB / item["predecessor_path"]
        artifact = load(artifact_path)
        receipt = load(receipt_path)
        material_results.append(
            {
                "ref": item["artifact_type_ref"],
                "artifact": sha(artifact_path),
                "expected_artifact": item["artifact_sha256"],
                "projection": sha(projection_path),
                "expected_projection": item["human_projection_sha256"],
                "schema": sha(schema_path),
                "expected_schema": item["schema_sha256"],
                "receipt": sha(receipt_path),
                "expected_receipt": item["validation_receipt_sha256"],
                "receipt_result": receipt.get("result"),
                "receipt_total": receipt.get("summary", {}).get("total"),
                "expected_receipt_total": item["validation_checks"],
                "definition": sha(definition_path),
                "expected_definition": item["definition_sha256"],
                "predecessor": sha(predecessor_path),
                "expected_predecessor": item["predecessor_sha256"],
                "candidate_status": artifact.get("status"),
                "candidate_authority": artifact.get("authority_effect"),
                "definition_ref": artifact.get("definition_binding", {}).get("definition_id", "")
                + "@"
                + artifact.get("definition_binding", {}).get("version", ""),
                "expected_definition_ref": item["definition_ref"],
            }
        )
    check(
        "admitted-materials-current",
        all(
            row["artifact"] == row["expected_artifact"]
            and row["projection"] == row["expected_projection"]
            and row["schema"] == row["expected_schema"]
            and row["receipt"] == row["expected_receipt"]
            and row["receipt_result"] == "PASS"
            and row["receipt_total"] == row["expected_receipt_total"]
            and row["definition"] == row["expected_definition"]
            and row["predecessor"] == row["expected_predecessor"]
            and row["candidate_status"] == "candidate-unadmitted"
            and row["candidate_authority"] == "none"
            and row["definition_ref"] == row["expected_definition_ref"]
            for row in material_results
        ),
        material_results,
    )

    registry_path = LAB / "authority/definitions/registry.json"
    registry = load(registry_path)
    expected_lookup = {
        "cal.definition.bounded-context": "cal.definition.bounded-context@2.0.0-candidate.1",
        "cal.definition.context-map": "cal.definition.context-map@2.0.0-candidate.1",
    }
    check(
        "normalized-definitions-current",
        sha(registry_path) == "c219fe0d18ac77103164141ea10168648110cb0ee2388604734b2545263068d5"
        and all(registry["current_lookup"].get(key) == value for key, value in expected_lookup.items()),
        {"sha256": sha(registry_path), "lookup": {key: registry["current_lookup"].get(key) for key in expected_lookup}},
    )

    bc_artifact = load(LAB / admitted[0]["artifact_path"])
    cm_artifact = load(LAB / admitted[1]["artifact_path"])
    generated_projection_path = LAB / admitted[1]["generated_membership_projection_path"]
    generated_projection = load(generated_projection_path)
    check(
        "reference-normalization-contract",
        "context_map_refs" in bc_artifact["instance_contract"]["forbidden_canonical_fields"]
        and cm_artifact["instance_contract"]["canonical_relation_owner"] is True
        and sha(generated_projection_path) == admitted[1]["generated_membership_projection_sha256"]
        and generated_projection.get("canonical") is False
        and generated_projection.get("authority_effect") == "none"
        and all(set(item) == {"context_ref", "context_map_refs"} for item in generated_projection["memberships"]),
        {
            "bounded_context_forbidden": bc_artifact["instance_contract"]["forbidden_canonical_fields"],
            "context_map_relation_owner": cm_artifact["instance_contract"]["canonical_relation_owner"],
            "projection_sha256": sha(generated_projection_path),
            "projection_canonical": generated_projection.get("canonical"),
            "projection_authority": generated_projection.get("authority_effect"),
        },
    )

    source_direction = decision.get("source_direction", {})
    check(
        "machine-canonical-human-generated",
        source_direction.get("canonical") == "decision.json"
        and source_direction.get("human_projection") == "DECISION.md"
        and source_direction.get("projection_policy") == "generated-only"
        and OUTPUT.is_file()
        and OUTPUT.read_text(encoding="utf-8") == load_renderer()(decision),
        source_direction,
    )

    expected_result = {
        "result": "complete-ctx07-normalized-context-artifact-type-admission",
        "artifact_types_admitted": 2,
        "artifact_type_versions_current_for_new_normalized_construction": 2,
        "predecessors_withdrawn": 0,
        "predecessors_superseded": 0,
        "definitions_revised": 0,
        "context_instances_created": 0,
        "context_maps_created": 0,
        "migration_executions_authorized": 0,
        "tooling_runtimes_admitted": 0,
    }
    check("admission-cardinality-and-boundary", decision.get("admission_result") == expected_result, decision.get("admission_result"))
    check(
        "successor-effects-excluded",
        all(
            term in decision.get("claim_ceiling", "")
            for term in ("only the exact Bounded Context/v2 and Context Map/v2", "does not admit tooling as runtime authority", "stable-release state")
        )
        and any("No CTX07 candidate" in item for item in decision["excluded_effects"])
        and any("No Governance or Ontology Lifecycle" in item for item in decision["excluded_effects"])
        and any("No successor Context Map" in item for item in decision["excluded_effects"]),
        {"claim_ceiling": decision.get("claim_ceiling"), "excluded_effects": decision["excluded_effects"]},
    )

    failed = [item for item in checks if item["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-ctx07-artifact-type-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": result,
        "authority_effect": "evidence-for-exact-ctx07-artifact-type-owner-decision-overlay",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "admission_state": "complete-ctx07-normalized-context-artifact-type-admission" if result == "PASS" else "not_evaluable",
        "next_gate": "author-normalized-governance-and-ontology-lifecycle-successor-context-epochs",
        "materials": {
            "decision_sha256": sha(SOURCE),
            "decision_projection_sha256": sha(OUTPUT) if OUTPUT.is_file() else None,
            "pack_sha256": sha(pack_path),
            "pack_validation_sha256": sha(validation_path),
            "conformance_sha256": sha(conformance_path),
            "bounded_context_v2_sha256": material_results[0]["artifact"],
            "context_map_v2_sha256": material_results[1]["artifact"],
        },
        "claim_ceiling": decision["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX07_ARTIFACT_TYPE_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_GATE={receipt['next_gate']}")
    for item in failed:
        print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
