#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text())


def mutate_registry(registry: dict, mutation: str) -> dict:
    value = copy.deepcopy(registry)
    if mutation == "replace-descriptors-with-empty-objects":
        value["descriptors"] = [{} for _ in registry["descriptors"]]
    elif mutation == "replace-admitted-contracts-with-string":
        value["admitted_contracts"] = ["not-a-contract"]
    elif mutation == "replace-current-map-value-with-number":
        value["current_by_identity"] = {"cal.artifact-type.invalid": 17}
    elif mutation == "replace-overlays-with-boolean":
        value["overlay_sources"] = [False]
    elif mutation == "replace-resolutions-with-number":
        value["duplicate_resolutions"] = [42]
    elif mutation == "remove-inventory-state-counts":
        value["inventory"].pop("state_counts")
    elif mutation == "add-lineage-authority-field":
        value["candidate_lineage"][0]["execution_authority"] = True
    else:
        raise ValueError(f"unknown hostile mutation: {mutation}")
    return value


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "audit_content.py")], check=True)
    registry = load(ROOT / "registry.json")
    candidate = load(ROOT / "candidate.json")
    schema = load(ROOT / "schema.json")
    artifact_type = load(ROOT / "artifact-type-candidate.json")
    definitions = load(LAB / "authority/definitions/registry.json")
    hostile_matrix = load(ROOT / "hostile-cases.json")
    checks = []

    def check(check_id, ok, detail):
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    validator = jsonschema.Draft202012Validator(schema)
    errors = [error.message for error in validator.iter_errors(registry)]
    check("registry-schema", not errors, errors)

    closed_defs = {
        "admittedContract",
        "candidateLineage",
        "descriptor",
        "duplicateResolution",
        "instanceDiscriminator",
        "inventory",
        "overlaySource",
        "sourceDirection",
    }
    check(
        "schema-entry-contracts-closed",
        schema.get("additionalProperties") is False
        and all(schema["$defs"][name].get("additionalProperties") is False for name in closed_defs)
        and schema["properties"]["descriptors"].get("minItems") == 1
        and schema["properties"]["descriptors"]["items"] == {"$ref": "#/$defs/descriptor"},
        {name: schema["$defs"][name].get("additionalProperties") for name in sorted(closed_defs)},
    )

    hostile_results = []
    for case in hostile_matrix["cases"]:
        hostile = mutate_registry(registry, case["mutation"])
        messages = [error.message for error in validator.iter_errors(hostile)]
        expected = case["expected_rejection_fragment"]
        hostile_results.append({
            "case_id": case["case_id"],
            "rejected": bool(messages),
            "expected_seen": any(expected in message for message in messages),
            "errors": messages[:4],
        })
    check(
        "hostile-structure-matrix",
        len(hostile_results) == 7
        and all(item["rejected"] and item["expected_seen"] for item in hostile_results)
        and artifact_type["validation_contract"]["hostile_matrix"]["sha256"] == sha(ROOT / "hostile-cases.json"),
        hostile_results,
    )

    check(
        "artifact-type-v2-contract",
        artifact_type["artifact_type_ref"] == "cal.artifact-type.artifact-type-registry/v2"
        and artifact_type["version"] == "2.0.0-candidate.2"
        and artifact_type["status"] == "candidate-unadmitted"
        and artifact_type["authority_effect"] == "none"
        and candidate["artifact_type_candidate"]["version"] == artifact_type["version"]
        and candidate["artifact_type_candidate"]["sha256"] == sha(ROOT / "artifact-type-candidate.json"),
        {"ref": artifact_type["artifact_type_ref"], "version": artifact_type["version"], "status": artifact_type["status"]},
    )
    root = LAB / artifact_type["artifact_type_root_binding"]["path"]
    check(
        "artifact-type-root-current",
        sha(root) == artifact_type["artifact_type_root_binding"]["sha256"] == "18641c47d5b50b20aa3050f9849518bd72156dbe31a4f67a43ff7dc8db57a0eb",
        artifact_type["artifact_type_root_binding"],
    )
    binding_results = []
    for binding in artifact_type["semantic_definition_bindings"]:
        path = LAB / binding["path"]
        current = definitions["current_lookup"].get(binding["definition_ref"].split("@")[0])
        binding_results.append({
            "ref": binding["definition_ref"],
            "digest": sha(path) == binding["sha256"],
            "current": current == binding["definition_ref"],
            "admitted": binding["admission_posture"] == "admitted",
        })
    check("semantic-definitions-current", all(item["digest"] and item["current"] and item["admitted"] for item in binding_results), binding_results)
    check(
        "predecessor-and-schema-bound",
        sha(LAB / artifact_type["predecessor_contract"]["path"]) == artifact_type["predecessor_contract"]["sha256"]
        and sha(ROOT / "schema.json") == artifact_type["schema_digest"],
        {"predecessor": artifact_type["predecessor_contract"], "schema_digest": artifact_type["schema_digest"]},
    )
    check(
        "inventory-cardinality",
        registry["inventory"]["descriptor_count"] == len(registry["descriptors"]) == 56
        and registry["inventory"]["descriptor_identity_count"] == 46
        and registry["inventory"]["descriptor_declared_ref_count"] == 49
        and registry["inventory"]["descriptor_resolved_ref_count"] == 51,
        registry["inventory"],
    )
    descriptors = [{"path": item["descriptor_path"], "expected": item["descriptor_sha256"], "actual": sha(LAB / item["descriptor_path"])} for item in registry["descriptors"]]
    check("descriptor-bytes-current", all(item["expected"] == item["actual"] for item in descriptors), descriptors)
    schemas = [{"path": item["schema_path"], "expected": item["schema_sha256"], "actual": sha(LAB / item["schema_path"])} for item in registry["descriptors"]]
    check("schema-bytes-current", all(item["expected"] == item["actual"] for item in schemas), schemas)
    overlays = [{"path": item["path"], "expected": item["sha256"], "actual": sha(LAB / item["path"])} for item in registry["overlay_sources"]]
    check("overlay-sources-current", all(item["expected"] == item["actual"] for item in overlays), overlays)
    contracts = [item for item in registry["admitted_contracts"] if (LAB / item["artifact_path"]).exists() and (LAB / item["schema_path"]).exists()]
    check(
        "admitted-contract-materials",
        len(contracts) == len(registry["admitted_contracts"]) == 33
        and all(sha(LAB / item["artifact_path"]) == item["artifact_sha256"] and sha(LAB / item["schema_path"]) == item["schema_sha256"] for item in contracts),
        {"count": len(contracts)},
    )
    current = [item for item in contracts if item["lifecycle_state"] == "admitted-current"]
    discriminators = [(item["instance_discriminator"]["path"], item["instance_discriminator"]["value"]) for item in current]
    check("unique-current-discriminators", len(discriminators) == len(set(discriminators)), discriminators)
    check(
        "embedded-status-not-effective",
        all(item["embedded_status"] == "candidate-unadmitted" for item in registry["descriptors"])
        and any(item["effective_state"] == "admitted-current" for item in registry["descriptors"]),
        registry["inventory"]["state_counts"],
    )
    exact = {(item["artifact_path"], item["artifact_sha256"], item["artifact_type_ref"]): item["lifecycle_state"] for item in contracts}
    derived = all(
        item["effective_state"] == exact[(item["descriptor_path"], item["descriptor_sha256"], item["artifact_type_ref"])]
        if (item["descriptor_path"], item["descriptor_sha256"], item["artifact_type_ref"]) in exact
        else item["effective_state"] in {"candidate-unadmitted", "resolved-duplicate"}
        for item in registry["descriptors"]
    )
    check("effective-state-derived", derived, registry["inventory"]["state_counts"])
    check(
        "shared-carrier-disambiguation",
        next(item for item in registry["descriptors"] if item["descriptor_path"] == "authority/artifact-types/artifact-type/v1/artifact.json")["effective_state"] == "admitted-historical",
        {"shared_path_contracts": [item["artifact_type_ref"] for item in contracts if item["artifact_path"] == "authority/artifact-types/artifact-type/v1/artifact.json"]},
    )
    check(
        "duplicate-resolution-closure",
        len(registry["duplicate_resolutions"]) == 2
        and {item["source_artifact_type_ref"] for item in registry["duplicate_resolutions"]} == {"cal.artifact-type.product/v1", "cal.artifact-type.project/v1"},
        {item["source_artifact_type_ref"]: item["effective_current_target_ref"] for item in registry["duplicate_resolutions"]},
    )
    rebinds = [item for item in registry["descriptors"] if item["semantic_binding_posture"] != "current-as-declared"]
    check(
        "step3-rebind-exposure",
        len(rebinds) == 5
        and sum(item["semantic_binding_posture"] == "admitted-successor-required" for item in rebinds) == 1
        and sum(item["semantic_binding_posture"] == "candidate-rebind-required" for item in rebinds) == 4,
        [{"ref": item["artifact_type_ref"], "posture": item["semantic_binding_posture"]} for item in rebinds],
    )
    check("no-activation-inference", all(item["activation_state"] == "not-activated" for item in registry["descriptors"]), None)
    audit = load(ROOT / "content-audit.json")
    audit_ref = candidate["content_audit"]
    check(
        "content-audit-bound",
        audit_ref["path"] == "authority/artifact-types/candidates/0006-effective-state-registry/content-audit.json"
        and audit_ref["sha256"] == sha(ROOT / "content-audit.json")
        and audit_ref["audit_id"] == audit["audit_id"],
        audit_ref,
    )
    check(
        "content-audit-coverage",
        audit["summary"]["descriptor_count"] == 56
        and len(audit["entries"]) == 56
        and audit["subject_registry"]["sha256"] == sha(ROOT / "registry.json")
        and audit["definition_registry"]["sha256"] == sha(LAB / "authority/definitions/registry.json"),
        audit["summary"],
    )
    check(
        "content-audit-decision-separation",
        audit["decision_conclusion"]["effective_state_registry_ready_for_owner_review"] is True
        and audit["decision_conclusion"]["all_artifact_type_contents_ready_for_collective_admission"] is False
        and audit["summary"]["actionable_descriptor_count"] == 14,
        audit["decision_conclusion"],
    )
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    registry_projection = (ROOT / "REGISTRY.md").read_text()
    artifact_projection = (ROOT / "ARTIFACT-TYPE.md").read_text()
    check(
        "projection-parity-surface",
        registry["registry_id"] in registry_projection
        and artifact_type["artifact_type_ref"] in artifact_projection
        and "## Descriptor effective state" in registry_projection,
        {"registry": sha(ROOT / "REGISTRY.md"), "artifact_type": sha(ROOT / "ARTIFACT-TYPE.md")},
    )
    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-effective-state-validation/v1",
        "subject": candidate["candidate_id"],
        "result": "PASS" if not failed else "FAIL",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "candidate_sha256": sha(ROOT / "candidate.json"),
            "artifact_type_candidate_sha256": sha(ROOT / "artifact-type-candidate.json"),
            "registry_sha256": sha(ROOT / "registry.json"),
            "schema_sha256": sha(ROOT / "schema.json"),
            "hostile_matrix_sha256": sha(ROOT / "hostile-cases.json"),
            "content_audit_sha256": sha(ROOT / "content-audit.json"),
            "content_audit_projection_sha256": sha(ROOT / "CONTENT-AUDIT.md"),
            "artifact_type_projection_sha256": sha(ROOT / "ARTIFACT-TYPE.md"),
            "registry_projection_sha256": sha(ROOT / "REGISTRY.md"),
        },
        "claim_ceiling": registry["claim_ceiling"],
    }
    (ROOT / "receipts").mkdir(exist_ok=True)
    (ROOT / "receipts/validation.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("ARTIFACT_TYPE_EFFECTIVE_STATE_VALIDATION=" + receipt["result"])
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"HOSTILE={sum(item['rejected'] and item['expected_seen'] for item in hostile_results)}/{len(hostile_results)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
