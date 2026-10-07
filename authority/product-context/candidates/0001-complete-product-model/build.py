#!/usr/bin/env python3
"""Build the complete governed Product context candidate and example."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
IDENTITY_V1 = LAB / "authority/artifact-types/product-identity/v1"
IDENTITY_V2 = LAB / "authority/artifact-types/product-identity/v2"
THESIS = LAB / "authority/artifact-types/product-thesis/v1"
CAPABILITY = LAB / "authority/artifact-types/product-capability/v1"
BINDING = LAB / "authority/artifact-types/capability-realization-binding/v1"
CAPABILITY_INSTANCE = LAB / "authority/artifact-types/capability-instance/v1"
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
MIGRATION_REGISTRY = LAB / "authority/decisions/migration-contracts/v1/registry.json"
ARTIFACT_REGISTRY = LAB / "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"
GENERATOR = LAB / "tooling/generators/cml07_identity_artifact.py"
VALIDATOR = LAB / "tooling/validators/cml07_identity_artifact_type.py"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


def binding(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha(path)}


PACKAGE_GENERATOR = '''#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parents[3] / "tooling/generators/cml07_identity_artifact.py"
spec = importlib.util.spec_from_file_location("product_identity_generator", SHARED)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

if __name__ == "__main__":
    artifact = json.loads((ROOT / "artifact.json").read_text(encoding="utf-8"))
    (ROOT / "ARTIFACT.md").write_text(module.render_artifact(artifact), encoding="utf-8")
    data = json.loads((ROOT / artifact["validation_contract"]["positive_witness"]).read_text(encoding="utf-8"))
    (ROOT / artifact["validation_contract"]["positive_projection"]).write_text(module.render_instance(artifact, data), encoding="utf-8")
'''


PACKAGE_VALIDATOR = '''#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parents[3] / "tooling/validators/cml07_identity_artifact_type.py"
spec = importlib.util.spec_from_file_location("product_identity_validator", SHARED)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

if __name__ == "__main__":
    raise SystemExit(module.run(ROOT, "product-identity"))
'''


def build_product_identity_v2() -> None:
    IDENTITY_V2.mkdir(parents=True, exist_ok=True)
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://cyberalchemy.local/schemas/product-identity/v2",
        "title": "CyberAlchemy Lab Product Identity v2 candidate instance",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version", "product_id", "version", "name", "status", "authority_effect",
            "semantic_definition_refs", "purpose", "value_promise", "scope", "semantic_owner_ref",
            "owner_route", "lineage_ref", "current_thesis_ref", "evidence_refs", "challenge_route", "claim_ceiling",
        ],
        "properties": {
            "schema_version": {"const": "cyberalchemy-lab-product-identity/v2"},
            "product_id": {"type": "string", "minLength": 1},
            "version": {"type": "string", "minLength": 1},
            "name": {"type": "string", "minLength": 1},
            "status": {"const": "candidate-unadmitted"},
            "authority_effect": {"const": "none"},
            "semantic_definition_refs": {"const": ["cal.definition.product@1.0.0-candidate.1", "cal.definition.identity-carrier@1.0.0-candidate.1"]},
            "purpose": {"type": "string", "minLength": 1},
            "value_promise": {"type": "string", "minLength": 1},
            "scope": {"$ref": "#/$defs/scope"},
            "semantic_owner_ref": {"type": "string", "minLength": 1},
            "owner_route": {"type": "string", "minLength": 1},
            "lineage_ref": {"type": "string", "minLength": 1},
            "current_thesis_ref": {"type": "string", "minLength": 1},
            "evidence_refs": {"$ref": "#/$defs/nonEmptyUniqueStrings"},
            "challenge_route": {"type": "string", "minLength": 1},
            "claim_ceiling": {"type": "string", "minLength": 1},
        },
        "$defs": {
            "nonEmptyUniqueStrings": {
                "type": "array", "minItems": 1, "uniqueItems": True,
                "items": {"type": "string", "minLength": 1},
            },
            "scope": {
                "type": "object", "additionalProperties": False,
                "required": ["includes", "excludes"],
                "properties": {
                    "includes": {"$ref": "#/$defs/nonEmptyUniqueStrings"},
                    "excludes": {"$ref": "#/$defs/nonEmptyUniqueStrings"},
                },
            },
        },
    }
    dump(IDENTITY_V2 / "schema.json", schema)

    definitions = {
        f"{entry['definition_id']}@{entry['version']}": entry
        for entry in load(DEFINITION_REGISTRY)["entries"]
        if entry["lifecycle_state"] == "admitted"
    }
    refs = ["cal.definition.product@1.0.0-candidate.1", "cal.definition.identity-carrier@1.0.0-candidate.1"]
    semantic_bindings = [
        {
            "definition_ref": ref,
            "path": definitions[ref]["path"],
            "sha256": definitions[ref]["sha256"],
            "admission_posture": "admitted",
            "admission_decision_ref": definitions[ref]["admission_decision_ref"],
        }
        for ref in refs
    ]
    root_type = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
    artifact = {
        "schema_version": "cyberalchemy-lab-artifact-type-candidate/v2",
        "artifact_type_id": "cal.artifact-type.product-identity",
        "artifact_type_ref": "cal.artifact-type.product-identity/v2",
        "version": "2.0.0-candidate.1",
        "name": "Product Identity",
        "status": "candidate-unadmitted",
        "authority_effect": "none",
        "classification": {
            "artifact_type_ref": "cal.artifact-type.artifact-type/v2",
            "semantic_kind": "product-identity",
            "authority_kind": "none",
            "lifecycle_posture_ref": "candidate:complete-product-context/v1",
        },
        "artifact_type_root_binding": {
            "path": rel(root_type),
            "sha256": sha(root_type),
            "admission_decision_ref": "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1",
        },
        "semantic_owner_ref": "role:artifact-type-owner",
        "semantic_definition_refs": refs,
        "semantic_definition_bindings": semantic_bindings,
        "schema_ref": "cal.schema.product-identity/v2",
        "schema_digest": sha(IDENTITY_V2 / "schema.json"),
        "instance_contract": {
            "canonical_filename": "product.json",
            "human_filename": "PRODUCT.md",
            "identity_field": "product_id",
            "closed_representation": True,
            "required_semantic_fields": [
                "purpose", "value_promise", "scope", "semantic_owner_ref", "owner_route", "lineage_ref",
                "current_thesis_ref", "evidence_refs", "challenge_route",
            ],
            "forbidden_canonical_fields": [
                "project_id", "method_ref", "goal_id", "bounded_context_ref", "capability_refs",
                "implementation_refs", "directory_identity",
            ],
        },
        "distinct_validation_purpose": "Preserves durable Product identity, purpose, value promise, scope, owner route, lineage, and current thesis without embedding Projects, Capabilities, contexts, or implementations.",
        "orthogonality_rules": [
            {"rule_id": "PRODUCT-V2-IDENTITY", "statement": "Product identity is supplied only by product_id; names, directories, Projects, theses, and realizations cannot create or replace it.", "validation_mode": "deterministic"},
            {"rule_id": "PRODUCT-V2-CAPABILITY-BOUNDARY", "statement": "Product Capability membership is owned by each capability's product_ref and appears on Product only as a derived inverse projection.", "validation_mode": "deterministic"},
            {"rule_id": "PRODUCT-V2-THESIS", "statement": "current_thesis_ref selects the present proposition without merging Product identity with Product Thesis lifecycle or claims.", "validation_mode": "deterministic"},
        ],
        "source_direction": {
            "canonical": "artifact.json", "human_projection": "ARTIFACT.md", "projection_policy": "generated-only",
            "generator": "generator.py", "shared_generator_path": rel(GENERATOR), "shared_generator_sha256": sha(GENERATOR),
        },
        "four_facets": {
            "classification": "Product Identity/v2 is a candidate successor to admitted v1 and remains separately governed until admission.",
            "schema": "The closed schema carries Product identity, value promise, lineage, owner route, and current thesis while rejecting embedded capability or implementation lists.",
            "human_continuation": "PRODUCT.md is generated from the exact canonical example.",
            "machine_checkable": "Schema closure, admitted Definition bindings, predecessor binding, hostile fixtures, and projections are validated.",
        },
        "validation_contract": {
            "validator_path": "validate.py", "shared_validator_path": rel(VALIDATOR), "shared_validator_sha256": sha(VALIDATOR),
            "positive_witness": "fixtures/valid/product.json", "positive_projection": "fixtures/valid/PRODUCT.md",
            "negative_witnesses": [
                "fixtures/invalid/authority-effect.json", "fixtures/invalid/missing-value-promise.json", "fixtures/invalid/embedded-capabilities.json",
            ],
            "assessment_scope": "schema-and-artifact-type-contract", "admission_effect": "none",
            "required_checks": ["closed schema", "stable Product identity", "explicit value promise", "admitted Definition bindings", "no embedded capabilities", "deterministic projections"],
        },
        "typed_residue": [
            {"residue_id": "PRODUCT-V2-R1", "missing": "No artifact-type-owner decision admits Product Identity/v2 as successor.", "owner_ref": "role:artifact-type-owner", "consequence": "Product Identity/v1 remains admitted-current."},
            {"residue_id": "PRODUCT-V2-R2", "missing": "No instance migration decision adopts the v2 record.", "owner_ref": "role:craft-product-owner", "consequence": "The Craft fixture remains illustrative and candidate-only."},
        ],
        "claim_ceiling": "This is a Product Identity/v2 successor candidate. It does not supersede v1, admit a Product or Product Thesis, infer capability membership, establish Product value, or activate any realization.",
    }
    dump(IDENTITY_V2 / "artifact.json", artifact)
    dump(
        IDENTITY_V2 / "successor.json",
        {
            "schema_version": "cyberalchemy-lab-artifact-type-successor-candidate/v1",
            "predecessor_ref": "cal.artifact-type.product-identity/v1",
            "predecessor_artifact": binding(IDENTITY_V1 / "artifact.json"),
            "predecessor_schema": binding(IDENTITY_V1 / "schema.json"),
            "predecessor_admission_decision_ref": "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1",
            "successor_ref": artifact["artifact_type_ref"],
            "status": "candidate-unadmitted",
            "changes": ["Add explicit value_promise", "Add explicit owner_route", "Add current_thesis_ref", "Forbid embedded capability and implementation lists"],
            "authority_effect": "none",
        },
    )
    product = {
        "schema_version": "cyberalchemy-lab-product-identity/v2",
        "product_id": "CA2-PRODUCT-CRAFT",
        "version": "2.0.0-candidate.1",
        "name": "Craft",
        "status": "candidate-unadmitted",
        "authority_effect": "none",
        "semantic_definition_refs": refs,
        "purpose": "Provide a governed recursive system-building Product while preserving its identity separately from Projects, methods, theses, Capabilities, contexts, repositories, and implementations.",
        "value_promise": "Help people and machine collaborators understand, change, and validate complex systems while keeping meaning, evidence, ownership, authority, and unresolved residue explicit.",
        "scope": {
            "includes": ["Craft Product meaning and value boundary", "Same-Product lineage continuity from DomainSpec v2", "Governed recursive system-building workflows"],
            "excludes": ["Project coordination authority", "Method meaning", "Goal achievement", "Product Capability identity", "Bounded Context inference", "Implementation or runtime conformance"],
        },
        "semantic_owner_ref": "role:craft-product-owner",
        "owner_route": "role:craft-product-owner",
        "lineage_ref": "CAL-LINEAGE-CRAFT-PRODUCT-V1",
        "current_thesis_ref": "product-thesis:craft",
        "evidence_refs": ["CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-PRODUCT", "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1", "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1"],
        "challenge_route": "role:craft-product-owner",
        "claim_ceiling": "Candidate Product Identity/v2 fixture only. It does not admit Craft, commit its thesis, adopt a Capability, prove value, or authorize implementation or runtime effects.",
    }
    dump(IDENTITY_V2 / "fixtures/valid/product.json", product)
    authority = dict(product); authority["authority_effect"] = "runtime"
    dump(IDENTITY_V2 / "fixtures/invalid/authority-effect.json", authority)
    missing = dict(product); del missing["value_promise"]
    dump(IDENTITY_V2 / "fixtures/invalid/missing-value-promise.json", missing)
    embedded = dict(product); embedded["capability_refs"] = ["capability:craft:governed-definition-admission"]
    dump(IDENTITY_V2 / "fixtures/invalid/embedded-capabilities.json", embedded)
    (IDENTITY_V2 / "generator.py").write_text(PACKAGE_GENERATOR, encoding="utf-8")
    (IDENTITY_V2 / "validate.py").write_text(PACKAGE_VALIDATOR, encoding="utf-8")
    projection = subprocess.run([sys.executable, str(IDENTITY_V2 / "generator.py")], cwd=LAB, check=False)
    if projection.returncode:
        raise RuntimeError("Product Identity/v2 projection generation failed")
    result = subprocess.run([sys.executable, str(IDENTITY_V2 / "validate.py")], cwd=LAB, check=False)
    if result.returncode:
        raise RuntimeError("Product Identity/v2 validation failed")


def render_model(model: dict[str, Any]) -> str:
    return f'''<!-- GENERATED FILE: canonical data is model.json. -->

# Complete Product Context candidate

- Model: `{model["model_id"]}`
- Status: `{model["status"]}`
- Authority effect: `{model["authority_effect"]}`

```mermaid
flowchart LR
    P[Product Identity]
    T[Product Thesis]
    O[Stable Thesis Outcome]
    C[Product Capability]
    I[Capability Instance]
    B[Realization Binding]
    R[Implementation / Agent / Workflow]
    E[Evaluation and Evidence]
    D[Adoption Decision]

    T -->|belongs-to-product| P
    T -->|declares| O
    C -->|belongs-to-product| P
    C -->|derives-from outcome| O
    I -->|instance-of| C
    B -->|binds exact capability version| C
    B -->|names typed realizations| R
    E -->|evaluates / supports / contradicts| T
    E -->|evaluates / observes| C
    D -->|adopts| C
    D -->|adopts| B
```

## Canonical ownership

| Concern | Canonical owner | Reverse view |
| --- | --- | --- |
| Product purpose, value promise, lineage | Product Identity | Direct |
| Product proposition and identified outcomes | Product Thesis | Product selects current thesis |
| Stable repeatable outcome contract | Product Capability | Product capability list is derived |
| Owner-local adoption | Capability Instance | Capability instance list is derived |
| Implementation endpoints and contract mapping | Capability Realization Binding | Capability realizations are derived |
| Runtime, conformance, observations, and value | Separate evidence and evaluation artifacts | Never inferred from binding existence |

## Core rule

Product Capabilities are not embedded in Product identity. Each capability owns `product_ref`, `product_thesis_ref`, and `thesis_outcome_refs`. Product-facing capability lists are read-only inverse projections.

## Claim ceiling

{model["claim_ceiling"]}
'''


def main() -> int:
    build_product_identity_v2()
    migration_entries = {entry["target_id"]: entry for entry in load(MIGRATION_REGISTRY)["entries"]}
    artifact_entries = {entry["artifact_type_ref"]: entry for entry in load(ARTIFACT_REGISTRY)["entries"]}
    components = []
    for role, root in [
        ("product-identity", IDENTITY_V2),
        ("product-thesis", THESIS),
        ("product-capability", CAPABILITY),
        ("capability-realization-binding", BINDING),
        ("capability-instance", CAPABILITY_INSTANCE),
    ]:
        artifact = load(root / "artifact.json")
        existing = artifact_entries.get(artifact["artifact_type_ref"])
        components.append(
            {
                "role": role,
                "artifact_type_ref": artifact["artifact_type_ref"],
                "artifact": binding(root / "artifact.json"),
                "schema": binding(root / "schema.json"),
                "lifecycle_state": existing["lifecycle_state"] if existing else "candidate-unadmitted",
                "admission_decision_ref": existing["admission_decision_ref"] if existing else None,
            }
        )
    contract_ids = [
        "profile.product-thesis-lifecycle", "profile.product-thesis-evaluation", "profile.capability-lifecycle",
        "relation.belongs-to-product", "relation.derives-from", "relation.realizes", "relation.instance-of",
        "relation.adopts", "relation.evaluates", "relation.supports", "relation.contradicts", "derived.capability-ontology",
    ]
    supporting_contracts = [
        {
            "target_id": target_id,
            "family": migration_entries[target_id]["family"],
            "status": migration_entries[target_id]["status"],
            "consumer_activation": migration_entries[target_id]["consumer_activation"],
            "contract": migration_entries[target_id]["contract"],
        }
        for target_id in contract_ids
    ]
    model = {
        "schema_version": "cyberalchemy-lab-complete-product-context/v1",
        "model_id": "CAL-PRODUCT-CONTEXT-COMPLETE-0001",
        "status": "candidate-unadmitted",
        "authority_effect": "none",
        "branches": {
            "business": ["product-identity", "product-thesis", "thesis-outcome", "product-capability", "project", "goal"],
            "system": ["capability-instance", "implementation", "agent-capability", "service", "workflow"],
            "bridge": ["capability-realization-binding", "evaluation", "evidence", "observation", "measurement", "adoption-decision"],
        },
        "components": components,
        "supporting_migration_contracts": supporting_contracts,
        "edge_rules": [
            {"relation_kind": "relation.belongs-to-product", "source_roles": ["product-thesis", "product-capability"], "target_role": "product-identity", "canonical_owner": "source record", "inverse_projection": "Product theses and capabilities"},
            {"relation_kind": "relation.derives-from", "source_roles": ["product-capability"], "target_role": "thesis-outcome", "canonical_owner": "Product Capability", "inverse_projection": "Capabilities derived from outcome"},
            {"relation_kind": "relation.instance-of", "source_roles": ["capability-instance"], "target_role": "product-capability", "canonical_owner": "Capability Instance", "inverse_projection": "Capability instances"},
            {"relation_kind": "relation.realizes", "source_roles": ["implementation", "agent-capability", "service", "workflow"], "target_role": "product-capability", "canonical_owner": "Capability Realization Binding", "inverse_projection": "Capability realizations"},
            {"relation_kind": "relation.adopts", "source_roles": ["adoption-decision"], "target_role": "product-capability-or-binding", "canonical_owner": "Decision", "inverse_projection": "Adoption decisions"},
            {"relation_kind": "relation.evaluates", "source_roles": ["evaluation"], "target_role": "product-thesis-or-capability", "canonical_owner": "Evaluation", "inverse_projection": "Evaluations"},
            {"relation_kind": "relation.supports-or-contradicts", "source_roles": ["evidence", "observation", "measurement"], "target_role": "hypothesis-or-finding", "canonical_owner": "Evidence relation", "inverse_projection": "Evidence and counterevidence"},
        ],
        "invariants": [
            "Product identity never embeds canonical capability or implementation lists.",
            "Every Product Thesis and Product Capability belongs to exactly one Product.",
            "Every Product Capability references at least one stable identified thesis outcome.",
            "Capability identity is stable across Capability Instances and realization bindings.",
            "A realization binding does not imply adoption, conformance, operation, or value.",
            "Business meaning cannot be silently redefined by a system realization.",
            "Product capability reverse lists and the Capability Ontology are derived read-only surfaces.",
        ],
        "current_authority_boundary": {
            "product_identity_v1": "admitted-current",
            "product_identity_v2": "candidate-successor",
            "product_thesis": "candidate-refined",
            "product_capability": "candidate-refined",
            "capability_realization_binding": "candidate-refined",
            "capability_instance_v1": artifact_entries["cal.artifact-type.capability-instance/v1"]["lifecycle_state"],
            "profiles_relations_and_projection": "admitted-migration-contracts; consumers inactive",
        },
        "claim_ceiling": "This candidate defines and validates the complete Product context contract and one cross-linked example. It does not admit Product Identity/v2, Product Thesis, Product Capability, or Capability Realization Binding; it does not adopt a Capability Instance or realization, activate a consumer, prove runtime conformance, or prove Product value.",
    }
    dump(ROOT / "model.json", model)
    (ROOT / "MODEL.md").write_text(render_model(model), encoding="utf-8")
    example = {
        "schema_version": "cyberalchemy-lab-product-context-example/v1",
        "example_id": "CAL-PRODUCT-CONTEXT-CRAFT-EXAMPLE-0001",
        "status": "candidate-fixture",
        "authority_effect": "none",
        "product": load(IDENTITY_V2 / "fixtures/valid/product.json"),
        "product_thesis": load(THESIS / "fixtures/valid/record.json"),
        "product_capability": load(CAPABILITY / "fixtures/valid/record.json"),
        "capability_realization_binding": load(BINDING / "fixtures/valid/record.json"),
        "derived_product_capability_refs": [load(CAPABILITY / "fixtures/valid/record.json")["node_id"]],
        "relations": [
            {"relation_kind": "relation.belongs-to-product", "source_ref": "product-thesis:craft", "target_ref": "CA2-PRODUCT-CRAFT"},
            {"relation_kind": "relation.belongs-to-product", "source_ref": "capability:craft:governed-definition-admission", "target_ref": "CA2-PRODUCT-CRAFT"},
            {"relation_kind": "relation.derives-from", "source_ref": "capability:craft:governed-definition-admission", "target_ref": "product-thesis:craft#outcome-authoritative-state"},
            {"relation_kind": "relation.realizes", "source_ref": "workflow:definition-admission:v1", "target_ref": "capability:craft:governed-definition-admission", "binding_ref": "binding:craft:governed-definition-admission:workflow-v1"},
        ],
        "claim_ceiling": "Illustrative cross-linked candidate records only; no record is admitted or adopted and no realization or value claim is established.",
    }
    dump(ROOT / "example.json", example)
    manifest_paths = [ROOT / "build.py", ROOT / "validate.py", ROOT / "model.json", ROOT / "MODEL.md", ROOT / "example.json"]
    manifest_paths.extend(path for path in IDENTITY_V2.rglob("*") if path.is_file())
    dump(
        ROOT / "manifest.json",
        {
            "schema_version": "cyberalchemy-lab-exact-file-manifest/v1",
            "subject": model["model_id"],
            "files": [{"path": rel(path), "sha256": sha(path)} for path in sorted(set(manifest_paths), key=rel)],
            "excluded_from_self_hash": [rel(ROOT / "manifest.json"), rel(ROOT / "receipts/validation.json")],
        },
    )
    return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
