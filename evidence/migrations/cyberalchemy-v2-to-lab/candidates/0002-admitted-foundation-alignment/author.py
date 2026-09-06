#!/usr/bin/env python3
"""Author successor 0002 from admitted foundations without rewriting predecessor bytes."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
PREDECESSOR = ROOT.parent / "0001-full-migration-architecture"
DEFINITION_ROOT = LAB / "authority/definitions/candidates/0011-repository-migration-manifest"
TYPE_ROOT = LAB / "authority/artifact-types/repository-migration-manifest/v1/candidates/0001"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def definition_binding(definition_id: str) -> dict[str, Any]:
    registry_path = LAB / "authority/definitions/registry.json"
    registry = load(registry_path)
    current = registry["current_lookup"][definition_id]
    entry = next(item for item in registry["entries"] if f"{item['definition_id']}@{item['version']}" == current)
    return {
        "definition_ref": current,
        "path": entry["path"],
        "sha256": entry["sha256"],
        "lifecycle_state": entry["lifecycle_state"],
        "admission_decision_ref": entry["admission_decision_ref"],
    }


def artifact_type_binding(ref: str, decision_path: str, artifact_path: str, schema_path: str) -> dict[str, Any]:
    decision_file = LAB / decision_path
    decision = load(decision_file)
    return {
        "artifact_type_ref": ref,
        "artifact_path": artifact_path,
        "artifact_sha256": sha(LAB / artifact_path),
        "schema_path": schema_path,
        "schema_sha256": sha(LAB / schema_path),
        "lifecycle_state": "admitted-current",
        "admission_decision_ref": decision["decision_id"],
        "admission_decision_path": decision_path,
        "admission_decision_sha256": sha(decision_file),
    }


def decision_request_schema() -> dict[str, Any]:
    digest = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    nonempty = {"type": "string", "minLength": 1}
    target = {"type": "object", "additionalProperties": False, "properties": {"path": nonempty, "sha256": digest}, "required": ["path", "sha256"]}
    request = {
        "type": "object", "additionalProperties": False,
        "properties": {
            "request_id": nonempty, "sequence": {"type": "integer", "minimum": 1, "maximum": 4}, "decision_kind": {"enum": ["product-approval", "definition-admission", "artifact-type-admission", "migration-execution-authorization"]},
            "owner_ref": nonempty, "authority_scope_ref": nonempty, "targets": {"type": "array", "minItems": 1, "items": target}, "requested_outcome": {"const": "approve"}, "requested_effect": nonempty,
            "depends_on": {"type": "array", "items": nonempty, "uniqueItems": True}, "invalidation_conditions": {"type": "array", "minItems": 1, "items": nonempty, "uniqueItems": True},
        },
        "required": ["request_id", "sequence", "decision_kind", "owner_ref", "authority_scope_ref", "targets", "requested_outcome", "requested_effect", "depends_on", "invalidation_conditions"],
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://cyberalchemy.local/schemas/migration-decision-request-set/v1", "type": "object", "additionalProperties": False,
        "properties": {
            "schema_version": {"const": "cyberalchemy-lab-migration-decision-request-set/v1"}, "decision_request_set_id": nonempty, "status": {"const": "awaiting-owner-decision"}, "authority_effect": {"const": "none"},
            "candidate_manifest": target, "validation_receipt": target, "interaction_count": {"const": 1}, "decision_mode": {"const": "single-checkpoint-ordered-independent-decisions"},
            "semantic_definition_refs": {"type": "array", "minItems": 4, "items": nonempty, "uniqueItems": True}, "requests": {"type": "array", "minItems": 4, "maxItems": 4, "items": request},
            "claim_ceiling": nonempty,
        },
        "required": ["schema_version", "decision_request_set_id", "status", "authority_effect", "candidate_manifest", "validation_receipt", "interaction_count", "decision_mode", "semantic_definition_refs", "requests", "claim_ceiling"],
    }


def decision_record_schema() -> dict[str, Any]:
    digest = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    nonempty = {"type": "string", "minLength": 1}
    decision = {
        "type": "object", "additionalProperties": False,
        "properties": {"request_id": nonempty, "decision_kind": {"enum": ["product-approval", "definition-admission", "artifact-type-admission", "migration-execution-authorization"]}, "owner_ref": nonempty, "outcome": {"const": "approved"}, "authorized_effect": nonempty},
        "required": ["request_id", "decision_kind", "owner_ref", "outcome", "authorized_effect"],
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://cyberalchemy.local/schemas/migration-decision-record/v1", "type": "object", "additionalProperties": False,
        "properties": {
            "schema_version": {"const": "cyberalchemy-lab-migration-decision-record/v1"}, "decision_record_id": nonempty, "status": {"const": "owner-decided"}, "decision_request_set_path": nonempty, "decision_request_set_sha256": digest,
            "candidate_manifest_sha256": digest, "validation_receipt_sha256": digest, "principal_ref": {"const": "person:vrondelli"}, "decisions": {"type": "array", "minItems": 4, "maxItems": 4, "items": decision},
            "copy_boundary": {"type": "object", "additionalProperties": False, "properties": {"additive_only": {"const": True}, "overwrite": {"const": False}, "source_mutation": {"const": False}, "source_deletion": {"const": False}, "publication": {"const": False}}, "required": ["additive_only", "overwrite", "source_mutation", "source_deletion", "publication"]},
            "claim_ceiling": nonempty,
        },
        "required": ["schema_version", "decision_record_id", "status", "decision_request_set_path", "decision_request_set_sha256", "candidate_manifest_sha256", "validation_receipt_sha256", "principal_ref", "decisions", "copy_boundary", "claim_ceiling"],
    }


def main() -> None:
    for relative in ["mapping-rules.json", "exclusion-policy.json", "architecture/architecture.json", "architecture/concepts.json", "architecture/relations.json"]:
        dump(ROOT / relative, load(PREDECESSOR / relative))

    predecessor_author = import_path("migration_candidate_0001_author", PREDECESSOR / "author.py")
    predecessor_author.ROOT = ROOT
    predecessor_author.author_architecture_projections()

    foundation = {
        "schema_version": "cyberalchemy-lab-admitted-migration-foundation-bindings/v1",
        "binding_id": "CAL-CAV2-TO-LAB-ADMITTED-FOUNDATION-0002",
        "status": "admitted-dependencies-observed",
        "authority_effect": "none",
        "definition_registry": {"path": "authority/definitions/registry.json", "sha256": sha(LAB / "authority/definitions/registry.json"), "status": load(LAB / "authority/definitions/registry.json")["status"]},
        "definitions": [definition_binding(item) for item in [
            "cal.definition.definition", "cal.definition.artifact-type", "cal.definition.validation", "cal.definition.context-migration-manifest",
            "craft.definition.decision-checkpoint", "craft.definition.decision-request-set", "craft.definition.user-decision-preference", "craft.definition.workflow-decision-profile",
        ]],
        "artifact_types": [
            artifact_type_binding("cal.artifact-type.definition/v1", "docs/decisions/0015-definition-v1-admission/decision.json", "authority/artifact-types/definition/v1/candidates/0002-post-foundation-01/artifact.json", "authority/artifact-types/definition/v1/schema.json"),
            artifact_type_binding("cal.artifact-type.artifact-type/v2", "docs/decisions/0029-cml07-semantic-foundation-v1/decision.json", "authority/artifact-types/artifact-type/v2/artifact.json", "authority/artifact-types/artifact-type/v2/schema.json"),
            artifact_type_binding("cal.artifact-type.context-migration-manifest/v1", "docs/decisions/0021-ctx01-artifact-type-promotion/decision.json", "authority/artifact-types/context-migration-manifest/v1/artifact.json", "authority/artifact-types/context-migration-manifest/v1/schema.json"),
        ],
        "interpretation": "Candidate source status fields remain immutable provenance. Admission is established by exact decision overlays and the live Definition registry.",
        "claim_ceiling": "Dependency observation only; this binding grants no new admission, approval, migration, or execution authority.",
    }
    dump(ROOT / "admitted-foundation-bindings.json", foundation)
    dump(ROOT / "decision-request-set.schema.json", decision_request_schema())
    dump(ROOT / "decision-record.schema.json", decision_record_schema())

    predecessor_manifest = PREDECESSOR / "manifest.json"
    predecessor_receipt = PREDECESSOR / "receipts/validation.json"
    candidate = {
        "schema_version": "cyberalchemy-lab-repository-migration-product-candidate/v2",
        "candidate_id": "CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-0002",
        "version": "1.0.0-test-candidate.2",
        "status": "candidate-authored-tests-pending",
        "authority_effect": "none",
        "predecessor": {"candidate_ref": str(PREDECESSOR.relative_to(LAB) / "candidate.json"), "manifest_sha256": sha(predecessor_manifest), "receipt_sha256": sha(predecessor_receipt), "disposition": "preserved-as-tested-provenance"},
        "admitted_foundation_bindings_ref": "admitted-foundation-bindings.json",
        "definition_candidate_ref": str((DEFINITION_ROOT / "candidate.json").relative_to(LAB)),
        "artifact_type_candidate_ref": str((TYPE_ROOT / "artifact.json").relative_to(LAB)),
        "migration_candidate_ref": "migration.json",
        "source_inventory_ref": "source-inventory.json",
        "copy_allowlist_ref": "copy-allowlist.json",
        "expected_postimage_ref": "expected-postimage.json",
        "rollback_ref": "rollback.json",
        "decision_request_generator_ref": "prepare_decision_request.py",
        "decision_record_schema_ref": "decision-record.schema.json",
        "execution_ref": "execute.py",
        "construction": {
            "product_frontier": "One successor repository migration candidate using admitted foundations and a separate, digest-bound, single-checkpoint decision envelope.",
            "runnable_product_work": ["Refresh exact source and target observations.", "Revalidate collision-free additive copy and recovery.", "Generate one ordered independent Decision Request Set after PASS."],
            "operational_support": [
                {"task": "Record four explicit outcomes from the single decision checkpoint.", "owner_ref": "person:vrondelli acting in each declared scope", "affected_stage": "post-product-test decision boundary", "blocks_current_frontier": False},
                {"task": "Execute the exact additive copy after the admitted decision record exists.", "owner_ref": "role:repository-migration-owner", "affected_stage": "migration execution", "blocks_current_frontier": False},
                {"task": "Commit or push migrated bytes.", "owner_ref": "repository owner", "affected_stage": "separate publication workflow", "blocks_current_frontier": False},
            ],
            "causal_blockers": ["Repository Migration Manifest Definition remains candidate-unadmitted.", "Repository Migration Manifest Artifact Type remains candidate-unadmitted.", "No exact decision record binds product approval, both admissions, and execution authorization."],
            "deferred_operational_residue": ["Imported packages require later individual classification and admission.", "Runtime dependencies are reconstructed from profiles and locks.", "Source retirement, deletion, commit, push, publication, release, and deployment remain separate."],
        },
        "approval_boundary": {
            "interaction_count": 1,
            "decision_mode": "single-checkpoint-ordered-independent-decisions",
            "ordered_decisions": ["product-approval", "definition-admission", "artifact-type-admission", "migration-execution-authorization"],
            "meaning": "Present four exact, ordered, independently governed decisions once after the product candidate passes; record every outcome separately and execute only if all four are explicitly approved.",
            "invariant": "One interaction never merges authorities; each outcome retains its request identity, owner, exact target, digest, effect, dependency, and invalidation conditions.",
            "not_included": ["source deletion", "overwrite", "import activation", "commit", "push", "publication", "release", "deployment"],
        },
        "source_direction": {"canonical": "candidate.json", "human_projection": "CANDIDATE.md", "projection_policy": "generated-only", "generator": "build.py"},
        "claim_ceiling": "Successor product candidate only. It reuses admitted foundations but does not admit the two new candidates, approve or execute migration, activate imports, delete or overwrite bytes, commit, push, publish, release, or deploy.",
    }
    dump(ROOT / "candidate.json", candidate)
    print("MIGRATION_SUCCESSOR_AUTHORING=PASS")


if __name__ == "__main__":
    main()
