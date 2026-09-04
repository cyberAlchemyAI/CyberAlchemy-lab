#!/usr/bin/env python3
"""Validate the exact CTX03 context-language admission overlay."""

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

    check("decision-identity", decision.get("decision_id") == "CAL-DECISION-0023-GOVERNANCE-AND-ONTOLOGY-LIFECYCLE-CONTEXT-PROMOTION" and decision.get("status") == "owner-admitted" and decision.get("authority_effect") == "four-exact-context-language-artifacts-admitted", {"id": decision.get("decision_id"), "status": decision.get("status"), "effect": decision.get("authority_effect")})

    selection = decision["selection"]
    check("explicit-owner-approval", selection.get("option_id") == "ADMIT-CTX03-GOVERNANCE-AND-ONTOLOGY-LIFECYCLE-V1" and selection.get("selection_token") == "approved" and selection.get("selected_by_principal") == "person:<vrondelli>" and "Exact user instruction" in selection.get("selection_source", ""), selection)

    basis = decision["authority_basis"]
    owner_decision_path = LAB / basis["operational_owner_decision_path"]
    owner_registry_path = LAB / basis["owner_registry_path"]
    owner_decision = load(owner_decision_path)
    owner_registry = load(owner_registry_path)
    check("owner-authority-bindings-current", sha(owner_decision_path) == basis["operational_owner_decision_sha256"] and owner_decision.get("status") == "owner-admitted" and sha(owner_registry_path) == basis["owner_registry_sha256"] and basis["principal_id"] == "person:<vrondelli>", {"decision": sha(owner_decision_path), "registry": sha(owner_registry_path)})
    assignments = {item["role_id"]: item for item in owner_registry["role_assignments"]}
    required_roles = {"governance-context-owner", "governance-language-owner", "ontology-lifecycle-context-owner", "ontology-lifecycle-language-owner"}
    check("four-separate-owner-roles-active", required_roles <= set(assignments) and all(assignments[role]["principal_id"] == "person:<vrondelli>" and assignments[role]["decision_separation"] == "required" for role in required_roles), {role: assignments.get(role) for role in sorted(required_roles)})

    prerequisite_results = []
    for item in decision["prerequisite_admissions"]:
        path = LAB / item["path"]
        actual = sha(path)
        status = load(path).get("status")
        prerequisite_results.append({"path": item["path"], "expected": item["sha256"], "actual": actual, "status": status})
    check("prerequisite-admissions-current", all(item["expected"] == item["actual"] and item["status"] == "owner-admitted" for item in prerequisite_results), prerequisite_results)

    evidence = decision["candidate_evidence"]
    pack_path = LAB / evidence["pack_path"]
    pack_projection_path = LAB / evidence["pack_projection_path"]
    validation_path = LAB / evidence["validation_path"]
    conformance_path = LAB / evidence["conformance_path"]
    validation = load(validation_path)
    conformance = load(conformance_path)
    check("candidate-pack-evidence-current", sha(pack_path) == evidence["pack_sha256"] and sha(pack_projection_path) == evidence["pack_projection_sha256"] and sha(validation_path) == evidence["validation_sha256"] and validation.get("result") == evidence["validation_result"] == "PASS" and validation.get("summary", {}).get("total") == evidence["validation_checks"], {"pack": sha(pack_path), "projection": sha(pack_projection_path), "validation": sha(validation_path), "summary": validation.get("summary")})
    check("candidate-conformance-current", sha(conformance_path) == evidence["conformance_sha256"] and conformance.get("result") == evidence["conformance_result"] == "PASS" and conformance.get("projection_parity") is True, {"sha256": sha(conformance_path), "result": conformance.get("result"), "projection_parity": conformance.get("projection_parity")})

    artifacts = []
    artifact_bytes_current = True
    candidate_bytes_preserved = True
    for binding in decision["admitted_artifacts"]:
        path = LAB / binding["path"]
        projection = LAB / binding["human_projection_path"]
        data = load(path)
        current = sha(path) == binding["sha256"] and sha(projection) == binding["human_projection_sha256"]
        preserved = data.get("status") == binding["candidate_status"] == "candidate-unadmitted" and data.get("authority_effect") == "none"
        artifact_bytes_current = artifact_bytes_current and current
        candidate_bytes_preserved = candidate_bytes_preserved and preserved
        artifacts.append({"artifact_id": binding["artifact_id"], "machine": sha(path), "projection": sha(projection), "status": data.get("status"), "effect": data.get("authority_effect")})
    check("four-artifact-byte-bindings-current", artifact_bytes_current and len(artifacts) == 4, artifacts)
    check("immutable-candidate-bytes-preserved", candidate_bytes_preserved, artifacts)

    expected_bindings = {
        "cal.context.governance": ("cal.artifact-type.bounded-context/v1", "governance-context-owner"),
        "cal.language.governance": ("cal.artifact-type.ubiquitous-language/v1", "governance-language-owner"),
        "cal.context.ontology-lifecycle": ("cal.artifact-type.bounded-context/v1", "ontology-lifecycle-context-owner"),
        "cal.language.ontology-lifecycle": ("cal.artifact-type.ubiquitous-language/v1", "ontology-lifecycle-language-owner"),
    }
    actual_bindings = {item["artifact_id"]: (item["artifact_type_ref"], item["owner_role"]) for item in decision["admitted_artifacts"]}
    check("exact-artifact-type-owner-closure", actual_bindings == expected_bindings and all(item["decision_overlay_status"] == "admitted" for item in decision["admitted_artifacts"]), actual_bindings)

    governance_context = load(LAB / "contexts/governance/v1/context.json")
    governance_language = load(LAB / "contexts/governance/v1/language.json")
    lifecycle_context = load(LAB / "contexts/ontology-lifecycle/v1/context.json")
    lifecycle_language = load(LAB / "contexts/ontology-lifecycle/v1/language.json")
    check("reciprocal-context-language-pairs", governance_context["ubiquitous_language_ref"] == f"{governance_language['language_id']}/v1" and governance_language["bounded_context_ref"] == f"{governance_context['context_id']}/v1" and lifecycle_context["ubiquitous_language_ref"] == f"{lifecycle_language['language_id']}/v1" and lifecycle_language["bounded_context_ref"] == f"{lifecycle_context['context_id']}/v1", {"governance": [governance_context["ubiquitous_language_ref"], governance_language["bounded_context_ref"]], "ontology_lifecycle": [lifecycle_context["ubiquitous_language_ref"], lifecycle_language["bounded_context_ref"]]})
    check("context-map-non-inference-preserved", governance_context["context_map_refs"] == [] and lifecycle_context["context_map_refs"] == [] and decision["admission_result"]["context_maps_admitted"] == 0, {"governance": governance_context["context_map_refs"], "ontology_lifecycle": lifecycle_context["context_map_refs"], "admitted": decision["admission_result"]["context_maps_admitted"]})

    result_data = decision["admission_result"]
    check("admission-cardinality", result_data == {"result": "complete-governance-and-ontology-lifecycle-context-language-admission", "bounded_contexts_admitted": 2, "ubiquitous_languages_admitted": 2, "context_maps_admitted": 0, "migration_manifests_admitted": 0}, result_data)
    check("projection-determinism-and-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(decision), str(OUTPUT))
    check("successor-effects-excluded", all(term in decision.get("claim_ceiling", "") for term in ("only the two exact Bounded Context", "does not select or admit a Context Map", "migration", "stable release")) and any("No source governance ontology" in item for item in decision["excluded_effects"]) and any("No runtime enforcement" in item for item in decision["excluded_effects"]), {"claim_ceiling": decision.get("claim_ceiling"), "excluded_effects": decision["excluded_effects"]})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-context-language-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": result,
        "authority_effect": "evidence-for-exact-context-language-decision-overlay",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "admission_state": "complete-governance-and-ontology-lifecycle-context-language-admission" if result == "PASS" else "not_evaluable",
        "next_gate": "context-map-candidate-authorship-requires-route-reentry",
        "claim_ceiling": decision["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX03_CONTEXT_LANGUAGE_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"NEXT_GATE={receipt['next_gate']}")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
