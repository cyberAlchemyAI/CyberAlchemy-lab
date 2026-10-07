#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_generator():
    path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("coordination_context_v2_generator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_failures(instance: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    identity = instance.get("coordination_context_id")
    endpoints = {
        "product": instance.get("product_ref"),
        "project": instance.get("project_ref"),
        "goal": instance.get("goal_ref"),
    }
    for kind, endpoint in endpoints.items():
        if isinstance(endpoint, str) and identity == endpoint:
            failures.append(f"identity-collapses-with-{kind}")
    if identity in instance.get("bounded_context_refs", []):
        failures.append("identity-collapses-with-bounded-context")
    endpoint_values = {value for value in endpoints.values() if isinstance(value, str)}
    endpoint_values.update(instance.get("bounded_context_refs", []))
    if instance.get("owner_ref") in endpoint_values:
        failures.append("owner-collapses-with-framed-endpoint")
    return sorted(failures)


def relation_projections(instance: dict[str, Any]) -> list[dict[str, Any]]:
    source = instance["coordination_context_id"]
    relations = [
        {
            "relation_kind_id": "relation.frames",
            "source_ref": source,
            "target_ref": instance["product_ref"],
            "qualifiers": {"framing_role": "primary-product"},
        }
    ]
    if instance["project_ref"] is not None:
        relations.append(
            {
                "relation_kind_id": "relation.frames",
                "source_ref": source,
                "target_ref": instance["project_ref"],
                "qualifiers": {"framing_role": "project-anchor"},
            }
        )
    if instance["goal_ref"] is not None:
        relations.append(
            {
                "relation_kind_id": "relation.frames",
                "source_ref": source,
                "target_ref": instance["goal_ref"],
                "qualifiers": {"framing_role": "goal-anchor"},
            }
        )
    relations.extend(
        {
            "relation_kind_id": "relation.frames",
            "source_ref": source,
            "target_ref": target,
            "qualifiers": {"framing_role": "semantic-boundary"},
        }
        for target in instance["bounded_context_refs"]
    )
    if instance["predecessor_ref"] is not None:
        relations.append(
            {
                "relation_kind_id": "relation.successor-of",
                "source_ref": source,
                "target_ref": instance["predecessor_ref"],
                "qualifiers": {"succession_effect": "continues-coordination-frame"},
            }
        )
    return relations


def lifecycle_result(base: dict[str, Any], after: dict[str, Any]) -> str:
    anchors = ("product_ref", "project_ref", "goal_ref", "purpose")
    changed = [key for key in anchors if base.get(key) != after.get(key)]
    same_identity = base["coordination_context_id"] == after["coordination_context_id"]
    if changed and same_identity:
        return "successor-required"
    if changed:
        return (
            "successor-identity-present"
            if after.get("predecessor_ref") == base["coordination_context_id"]
            else "successor-link-missing"
        )
    if same_identity and after.get("revision_history"):
        return "same-identity-revision-permitted"
    return "revision-record-missing"


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "build_fixtures.py")], check=True)
    artifact = load(ROOT / "artifact.json")
    schema = load(ROOT / "schema.json")
    validator = Draft202012Validator(schema)
    generator = load_generator()
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append(
            {"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail}
        )

    check(
        "artifact-identity",
        artifact["artifact_type_ref"] == "cal.artifact-type.coordination-context/v2"
        and artifact["version"] == "2.0.0-candidate.1"
        and artifact["status"] == "candidate-unadmitted"
        and artifact["authority_effect"] == "none",
        {
            "ref": artifact["artifact_type_ref"],
            "version": artifact["version"],
            "status": artifact["status"],
        },
    )
    root_binding = artifact["artifact_type_root_binding"]
    root_path = LAB / root_binding["path"]
    check(
        "artifact-type-root-binding",
        root_path.exists() and sha256(root_path) == root_binding["sha256"],
        root_binding,
    )
    predecessor = artifact["predecessor_artifact_type"]
    predecessor_path = LAB / predecessor["path"]
    predecessor_decision = LAB / predecessor["admission_decision_path"]
    check(
        "admitted-v1-predecessor-preserved",
        sha256(predecessor_path) == predecessor["sha256"]
        and sha256(predecessor_decision) == predecessor["admission_decision_sha256"],
        predecessor,
    )
    definition_registry = load(LAB / "authority/definitions/registry.json")
    binding = artifact["semantic_definition_bindings"][0]
    definition_path = LAB / binding["path"]
    check(
        "admitted-current-definition-binding",
        sha256(definition_path) == binding["sha256"]
        and binding["admission_posture"] == "admitted"
        and definition_registry["current_lookup"].get("cal.definition.coordination-context")
        == binding["definition_ref"],
        binding,
    )
    check(
        "schema-and-generator-digests",
        artifact["schema_digest"] == sha256(ROOT / "schema.json")
        and artifact["source_direction"]["generator_sha256"]
        == sha256(ROOT / "generator.py"),
        {
            "schema": sha256(ROOT / "schema.json"),
            "generator": sha256(ROOT / "generator.py"),
        },
    )
    source_audit = artifact["validation_contract"]["source_audit"]
    source_audit_path = LAB / source_audit["path"]
    source_audit_data = load(source_audit_path)
    check(
        "expanded-audit-bound",
        sha256(source_audit_path) == source_audit["sha256"]
        and source_audit_data["result"] == source_audit["result"] == "PASS",
        source_audit,
    )
    required = set(schema["required"])
    semantic_required = set(artifact["instance_contract"]["required_semantic_fields"])
    check(
        "instance-contract-schema-alignment",
        semantic_required.issubset(required)
        and {"project_ref", "goal_ref", "predecessor_ref"}.issubset(required),
        {
            "missing": sorted(semantic_required - required),
            "optional_semantic_fields_canonical_presence": [
                "project_ref",
                "goal_ref",
                "predecessor_ref",
            ],
        },
    )

    positive_results = []
    for path in sorted((ROOT / "fixtures/valid").glob("*.json")):
        instance = load(path)
        schema_errors = sorted(error.message for error in validator.iter_errors(instance))
        semantic_errors = semantic_failures(instance)
        positive_results.append(
            {
                "fixture": path.name,
                "schema_errors": schema_errors,
                "semantic_errors": semantic_errors,
                "accepted": not schema_errors and not semantic_errors,
            }
        )
    check(
        "four-optional-axis-positive-cases",
        len(positive_results) == 4 and all(row["accepted"] for row in positive_results),
        positive_results,
    )

    hostile_results = []
    for path in sorted((ROOT / "fixtures/invalid").glob("*.json")):
        instance = load(path)
        schema_errors = sorted(error.message for error in validator.iter_errors(instance))
        semantic_errors = semantic_failures(instance)
        hostile_results.append(
            {
                "fixture": path.name,
                "schema_errors": schema_errors,
                "semantic_errors": semantic_errors,
                "rejected": bool(schema_errors or semantic_errors),
            }
        )
    check(
        "eighteen-hostile-non-collapse-cases",
        len(hostile_results) == 18 and all(row["rejected"] for row in hostile_results),
        hostile_results,
    )
    semantic_only = [
        row["fixture"]
        for row in hostile_results
        if not row["schema_errors"] and row["semantic_errors"]
    ]
    check(
        "five-v1-validator-blind-spots-closed",
        set(semantic_only)
        == {
            "identity-equals-product.json",
            "identity-equals-project.json",
            "identity-equals-goal.json",
            "identity-equals-bounded-context.json",
            "owner-equals-product.json",
        },
        semantic_only,
    )
    lifecycle = load(ROOT / "fixtures/lifecycle/cases.json")
    lifecycle_results = [
        {
            "case_id": case["case_id"],
            "expected": case["expected"],
            "result": lifecycle_result(lifecycle["base"], case["after"]),
        }
        for case in lifecycle["cases"]
    ]
    check(
        "six-lifecycle-cases",
        len(lifecycle_results) == 6
        and all(row["expected"] == row["result"] for row in lifecycle_results),
        lifecycle_results,
    )

    relation_model = load(
        LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
    )
    existing_pairs = [
        {"relation_kind_id": entry["relation_kind_id"], **pair}
        for entry in relation_model["entries"]
        for pair in entry["allowed_endpoint_pairs"]
        if "coordination-context" in pair.values()
    ]
    proposed = artifact["relation_projection_contract"]["projections"]
    check(
        "typed-connection-extension-residue",
        not existing_pairs
        and len(proposed) == 5
        and artifact["relation_projection_contract"]["admission_posture"]
        == "candidate-endpoint-extensions-required",
        {"existing_pairs": existing_pairs, "proposed": proposed},
    )
    fixture = load(ROOT / "fixtures/valid/product-project-goal.json")
    relations_a = relation_projections(fixture)
    relations_b = relation_projections(fixture)
    check(
        "deterministic-read-only-relation-projections",
        relations_a == relations_b
        and len(relations_a) == 5
        and all(row["relation_kind_id"] != "relation.member-of" for row in relations_a),
        relations_a,
    )
    instance_a = generator.render_instance(fixture)
    instance_b = generator.render_instance(fixture)
    instance_projection = ROOT / "fixtures/valid/COORDINATION-CONTEXT.md"
    artifact_a = generator.render_artifact(artifact)
    artifact_b = generator.render_artifact(artifact)
    artifact_projection = ROOT / "ARTIFACT.md"
    check(
        "deterministic-human-projections",
        instance_a == instance_b == instance_projection.read_text()
        and artifact_a == artifact_b == artifact_projection.read_text(),
        {
            "instance_sha256": sha256(instance_projection),
            "artifact_sha256": sha256(artifact_projection),
        },
    )

    failed = [row for row in checks if row["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-coordination-context-v2-validation/v1",
        "artifact_type_ref": artifact["artifact_type_ref"],
        "candidate_version": artifact["version"],
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "summary": {
            "passed": len(checks) - len(failed),
            "failed": len(failed),
            "total": len(checks),
            "positive_cases": len(positive_results),
            "hostile_cases": len(hostile_results),
            "lifecycle_cases": len(lifecycle_results),
        },
        "materials": {
            "artifact_sha256": sha256(ROOT / "artifact.json"),
            "schema_sha256": sha256(ROOT / "schema.json"),
            "generator_sha256": sha256(ROOT / "generator.py"),
            "validator_sha256": sha256(ROOT / "validate.py"),
            "artifact_projection_sha256": sha256(artifact_projection),
            "instance_projection_sha256": sha256(instance_projection),
            "source_audit_sha256": sha256(source_audit_path),
            "lifecycle_matrix_sha256": sha256(ROOT / "fixtures/lifecycle/cases.json"),
        },
        "claim_ceiling": artifact["claim_ceiling"],
    }
    (ROOT / "receipts").mkdir(exist_ok=True)
    (ROOT / "receipts/validation.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(f"COORDINATION_CONTEXT_V2_VALIDATION={result}")
    print(f"CHECKS={len(checks)-len(failed)}/{len(checks)}")
    print(f"POSITIVE={len(positive_results)}/4")
    print(f"HOSTILE={len(hostile_results)}/18")
    print(f"LIFECYCLE={len(lifecycle_results)}/6")
    for row in failed:
        print(f"FAIL {row['check_id']}: {row['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
