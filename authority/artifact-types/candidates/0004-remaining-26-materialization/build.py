#!/usr/bin/env python3
"""Materialize the 26 admitted migration contracts as Artifact Type candidates."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
MIGRATION_REGISTRY = LAB / "authority/decisions/migration-contracts/v1/registry.json"
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
MIGRATION_DECISION = LAB / "docs/decisions/0052-remaining-83-contract-admission/decision.json"
DEFINITION_DECISION = LAB / "docs/decisions/0053-full-definition-queue-admission/decision.json"
SHARED_GENERATOR = LAB / "tooling/generators/artifact_surface.py"
SHARED_VALIDATOR = LAB / "tooling/validators/artifact_surface.py"
REFINEMENTS = ROOT / "refinements"
REVIEW_MODEL_PATH = ROOT / "review_model.py"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(LAB))


def import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


PACKAGE_GENERATOR = '''#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parents[3] / "tooling/generators/artifact_surface.py"
spec = importlib.util.spec_from_file_location("artifact_surface_generator", SHARED)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

if __name__ == "__main__":
    artifact = json.loads((ROOT / "artifact.json").read_text(encoding="utf-8"))
    (ROOT / "ARTIFACT.md").write_text(module.render_artifact(artifact), encoding="utf-8")
    witness = ROOT / artifact["validation_contract"]["positive_witness"]
    data = json.loads(witness.read_text(encoding="utf-8"))
    projection = ROOT / artifact["validation_contract"]["positive_projection"]
    projection.write_text(module.render_instance(artifact, data), encoding="utf-8")
'''


PACKAGE_VALIDATOR = '''#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parents[3] / "tooling/validators/artifact_surface.py"
spec = importlib.util.spec_from_file_location("artifact_surface_validator", SHARED)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

if __name__ == "__main__":
    raise SystemExit(module.validate_package(ROOT))
'''


def render_materialization(data: dict[str, Any]) -> str:
    defs = "<br>".join(f"`{x['definition_ref']}`" for x in data["semantic_definition_bindings"])
    return "\n".join(
        [
            "<!-- GENERATED FILE: canonical data is materialization.json. -->",
            "",
            f"# {data['name']} materialization",
            "",
            f"- Target: `{data['target_id']}`",
            f"- Artifact Type: `{data['artifact_type_ref']}`",
            f"- Status: `{data['status']}`",
            f"- Authority effect: `{data['authority_effect']}`",
            f"- Definitions: {defs}",
            "",
            "## Source contract",
            "",
            f"- Migration decision: `{data['migration_contract_admission']['decision_ref']}`",
            f"- Original contract: `{data['source_contract']['path']}`",
            f"- Original artifact candidate: `{data['source_artifact']['path']}`",
            "",
            "## Claim ceiling",
            "",
            data["claim_ceiling"],
            "",
        ]
    )


def render_catalog(entries: list[dict[str, Any]]) -> str:
    lines = [
        "<!-- GENERATED FILE: run build.py to refresh. -->",
        "",
        "# Materialized Artifact Type candidates",
        "",
        "These 26 packages start from the Artifact Type contracts selected by migration decision `CAL-REMAINING-83-CONTRACT-ADMISSION-0052`. Their Definition dependencies are rebound to the admitted Definition registry, and authorized owner-review refinements are identified explicitly. The packages remain candidates and have no consumer activation.",
        "",
        "| # | Migration target | Artifact Type | Name | Domain family | Admitted Definition binding | Package | Status |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, item in enumerate(entries, 1):
        definitions = "<br>".join(f"`{ref}`" for ref in item["semantic_definition_refs"])
        lines.append(
            f"| {index} | `{item['target_id']}` | `{item['artifact_type_ref']}` | {item['name']} | `{item['domain_family']}` | {definitions} | `{item['package_path']}` | `{item['status']}` |"
        )
    lines += [
        "",
        "## Status boundary",
        "",
        "Materialization proves that each selected migration contract now has a stable candidate package with a closed schema, generated projections, fixtures, exact admitted Definition bindings, and a passing validation receipt. Artifact Type admission, real instances, consumer integration, and activation require separate decisions.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    migration_registry = load(MIGRATION_REGISTRY)
    migration_decision = load(MIGRATION_DECISION)
    definition_decision = load(DEFINITION_DECISION)
    definition_entries = {
        f"{entry['definition_id']}@{entry['version']}": entry
        for entry in load(DEFINITION_REGISTRY)["entries"]
        if entry["lifecycle_state"] == "admitted"
    }
    selected = [entry for entry in migration_registry["entries"] if entry["family"] == "artifact-type"]
    if len(selected) != 26:
        raise RuntimeError(f"expected 26 Artifact Type contracts, found {len(selected)}")

    generator = import_module("materialization_generator", SHARED_GENERATOR)
    validator = import_module("materialization_validator", SHARED_VALIDATOR)
    review_model = import_module("remaining_artifact_type_review_model", REVIEW_MODEL_PATH)
    catalog_entries: list[dict[str, Any]] = []

    for selected_entry in selected:
        target_id = selected_entry["target_id"]
        slug = target_id.removeprefix("type.")
        source_artifact_path = LAB / selected_entry["binding"]["path"]
        source_contract_path = LAB / selected_entry["contract"]["path"]
        if sha(source_artifact_path) != selected_entry["binding"]["sha256"]:
            raise RuntimeError(f"source artifact drift: {target_id}")
        if sha(source_contract_path) != selected_entry["contract"]["sha256"]:
            raise RuntimeError(f"source contract drift: {target_id}")

        source_root = source_artifact_path.parent
        source_artifact = load(source_artifact_path)
        source_contract = load(source_contract_path)
        destination = LAB / "authority/artifact-types" / slug / "v1"
        destination.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_root / "schema.json", destination / "schema.json")
        for fixture in [
            "fixtures/valid/record.json",
            "fixtures/invalid/authority.json",
            "fixtures/invalid/missing-field.json",
            "fixtures/invalid/extra-field.json",
        ]:
            target = destination / fixture
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_root / fixture, target)
        shutil.copy2(source_contract_path, destination / "migration-contract.json")

        refinement_path = REFINEMENTS / f"{target_id}.json"
        refinement = load(refinement_path) if refinement_path.is_file() else None
        if target_id == "type.intent":
            if refinement is None or refinement["review_state"] != "revision-authorized-before-admission":
                raise RuntimeError("Intent refinement authorization is missing")
            schema = load(destination / "schema.json")
            schema["properties"].update(
                {
                    "intent_state": {
                        "enum": ["proposed", "active", "satisfied", "superseded", "rejected"],
                        "type": "string",
                    },
                    "target_pressure": {"pattern": "\\S", "type": "string"},
                    "current_output_hypothesis": {
                        "additionalProperties": False,
                        "properties": {
                            "artifact_type_ref": {"pattern": "\\S", "type": "string"},
                            "description": {"pattern": "\\S", "type": "string"},
                        },
                        "required": ["artifact_type_ref", "description"],
                        "type": "object",
                    },
                    "satisfaction_refs": {
                        "items": {"pattern": "\\S", "type": "string"},
                        "maxItems": 100,
                        "type": "array",
                        "uniqueItems": True,
                    },
                    "successor_refs": {
                        "items": {"pattern": "\\S", "type": "string"},
                        "maxItems": 100,
                        "type": "array",
                        "uniqueItems": True,
                    },
                    "revision_route": {"pattern": "\\S", "type": "string"},
                    "revision_history": {
                        "items": {
                            "additionalProperties": False,
                            "properties": {
                                "revision_id": {"pattern": "\\S", "type": "string"},
                                "change_kind": {
                                    "enum": ["refined", "split", "renamed", "rejected", "reactivated"],
                                    "type": "string",
                                },
                                "rationale": {"pattern": "\\S", "type": "string"},
                                "decision_ref": {"pattern": "\\S", "type": "string"},
                                "resulting_intent_refs": {
                                    "items": {"pattern": "\\S", "type": "string"},
                                    "maxItems": 100,
                                    "type": "array",
                                    "uniqueItems": True,
                                },
                            },
                            "required": ["revision_id", "change_kind", "rationale", "decision_ref", "resulting_intent_refs"],
                            "type": "object",
                        },
                        "maxItems": 100,
                        "type": "array",
                    },
                }
            )
            schema["required"].extend(
                [
                    "intent_state",
                    "target_pressure",
                    "current_output_hypothesis",
                    "satisfaction_refs",
                    "successor_refs",
                    "revision_route",
                    "revision_history",
                ]
            )
            schema["allOf"] = [
                {
                    "if": {"properties": {"intent_state": {"const": "satisfied"}}, "required": ["intent_state"]},
                    "then": {"properties": {"satisfaction_refs": {"minItems": 1}}},
                },
                {
                    "if": {"properties": {"intent_state": {"const": "superseded"}}, "required": ["intent_state"]},
                    "then": {"properties": {"successor_refs": {"minItems": 1}}},
                },
            ]
            dump(destination / "schema.json", schema)
            witness = load(destination / "fixtures/valid/record.json")
            witness.update(
                {
                    "attributed_to": "person-reference:repository-owner",
                    "constraints": [
                        "Preserve exact source provenance from CyberAlchemy v2",
                        "Require owner review before admitting each Artifact Type",
                        "Do not activate consumers as a side effect of admission",
                        "Keep Definitions, Artifact Types, instances, and runtime activation as separate decisions",
                        "Do not silently discard unresolved migration residue",
                    ],
                    "direction": "Preserve useful CyberAlchemy v2 concepts and operating decisions as governed CyberAlchemy Lab artifacts.",
                    "intent_state": "active",
                    "motivation": "Reconstructed migration knowledge needs reviewed Artifact Types before repository tools and people can use it consistently.",
                    "node_id": "intent:complete-cyberalchemy-v2-migration",
                    "owner_ref": "role:artifact-type-owner",
                    "review_route": "authority/artifact-types/candidates/0004-remaining-26-materialization/CATALOG.md",
                    "scope_ref": "scope:cyberalchemy-v2-to-lab-migration",
                    "target_pressure": "Migration knowledge exists, but its Artifact Types are not yet available as admitted Lab authority.",
                    "current_output_hypothesis": {
                        "artifact_type_ref": "cal.artifact-type.artifact-type/v2",
                        "description": "A reviewed and admitted set of Artifact Types for the reconstructed CyberAlchemy v2 concepts.",
                    },
                    "satisfaction_refs": [],
                    "successor_refs": [],
                    "revision_route": "route:artifact-type-owner-review",
                    "revision_history": [],
                }
            )
            dump(destination / "fixtures/valid/record.json", witness)
            missing_traceability = dict(witness)
            del missing_traceability["current_output_hypothesis"]
            dump(destination / "fixtures/invalid/missing-traceability.json", missing_traceability)
        if target_id == "type.product-thesis":
            if refinement is None or refinement["review_state"] != "revision-authorized-before-admission":
                raise RuntimeError("Product Thesis refinement authorization is missing")
            schema = load(destination / "schema.json")
            nonempty_strings = {
                "items": {"pattern": "\\S", "type": "string"},
                "maxItems": 100,
                "minItems": 1,
                "type": "array",
                "uniqueItems": True,
            }
            optional_strings = {
                "items": {"pattern": "\\S", "type": "string"},
                "maxItems": 100,
                "type": "array",
                "uniqueItems": True,
            }
            schema["properties"].update(
                {
                    "participants": nonempty_strings,
                    "value_mechanism": {"pattern": "\\S", "type": "string"},
                    "first_order_principles": nonempty_strings,
                    "intended_outcomes": {
                        "items": {
                            "additionalProperties": False,
                            "properties": {
                                "outcome_id": {"pattern": "\\S", "type": "string"},
                                "statement": {"pattern": "\\S", "type": "string"},
                                "value_measure_refs": optional_strings,
                            },
                            "required": ["outcome_id", "statement", "value_measure_refs"],
                            "type": "object",
                        },
                        "maxItems": 100,
                        "minItems": 1,
                        "type": "array",
                    },
                    "boundaries": nonempty_strings,
                    "hypotheses": {
                        "items": {
                            "additionalProperties": False,
                            "properties": {
                                "hypothesis_id": {"pattern": "\\S", "type": "string"},
                                "statement": {"pattern": "\\S", "type": "string"},
                                "evidence_state": {
                                    "enum": ["untested", "supported", "challenged", "rejected"],
                                    "type": "string",
                                },
                            },
                            "required": ["hypothesis_id", "statement", "evidence_state"],
                            "type": "object",
                        },
                        "maxItems": 100,
                        "minItems": 1,
                        "type": "array",
                    },
                    "evidence_routes": optional_strings,
                    "counterevidence_routes": optional_strings,
                    "owner_route": {"pattern": "\\S", "type": "string"},
                    "commitment_state": {
                        "enum": ["draft", "committed", "revised", "retired", "superseded"],
                        "type": "string",
                    },
                    "successor_refs": optional_strings,
                    "revision_history": {
                        "items": {
                            "additionalProperties": False,
                            "properties": {
                                "revision_id": {"pattern": "\\S", "type": "string"},
                                "change_summary": {"pattern": "\\S", "type": "string"},
                                "rationale": {"pattern": "\\S", "type": "string"},
                                "decision_ref": {"pattern": "\\S", "type": "string"},
                                "evidence_refs": optional_strings,
                            },
                            "required": ["revision_id", "change_summary", "rationale", "decision_ref", "evidence_refs"],
                            "type": "object",
                        },
                        "maxItems": 100,
                        "type": "array",
                    },
                    "challenge_route": {"pattern": "\\S", "type": "string"},
                }
            )
            schema["required"].extend(
                [
                    "participants",
                    "value_mechanism",
                    "first_order_principles",
                    "intended_outcomes",
                    "boundaries",
                    "hypotheses",
                    "evidence_routes",
                    "counterevidence_routes",
                    "owner_route",
                    "commitment_state",
                    "successor_refs",
                    "revision_history",
                    "challenge_route",
                ]
            )
            schema["allOf"] = [
                {
                    "if": {"properties": {"commitment_state": {"enum": ["committed", "revised"]}}, "required": ["commitment_state"]},
                    "then": {
                        "properties": {
                            "evidence_routes": {"minItems": 1},
                            "counterevidence_routes": {"minItems": 1},
                        }
                    },
                },
                {
                    "if": {"properties": {"commitment_state": {"const": "revised"}}, "required": ["commitment_state"]},
                    "then": {"properties": {"revision_history": {"minItems": 1}}},
                },
                {
                    "if": {"properties": {"commitment_state": {"const": "superseded"}}, "required": ["commitment_state"]},
                    "then": {"properties": {"successor_refs": {"minItems": 1}}},
                },
            ]
            dump(destination / "schema.json", schema)
            witness = load(destination / "fixtures/valid/record.json")
            witness.update(
                {
                    "node_id": "product-thesis:craft",
                    "product_ref": "CA2-PRODUCT-CRAFT",
                    "audience": "Repository owners and human-machine engineering teams building governed software systems",
                    "participants": ["product owners", "project owners", "domain stewards", "human and machine collaborators"],
                    "problem": "Repository knowledge, decisions, evidence, and implementation work become fragmented across documents and tools, making authority and current state difficult to establish.",
                    "value_proposition": "Craft provides a governed human-machine work loop that preserves intent, shared meaning, evidence, ownership, bounded authority, and visible incompleteness.",
                    "value_mechanism": "Typed artifacts, exact provenance, explicit owner decisions, bounded evidence, and replaceable implementations keep meaning and authority inspectable while work evolves.",
                    "first_order_principles": [
                        "Source authority remains explicit",
                        "Human owners retain consequential decision authority",
                        "Incomplete or unsupported claims remain visible residue",
                        "Product identity remains separate from projects and implementations",
                        "Realizations remain replaceable behind governed contracts",
                    ],
                    "intended_outcomes": [
                        {
                            "outcome_id": "product-thesis:craft#outcome-authoritative-state",
                            "statement": "People can identify the current authoritative meaning and decision state.",
                            "value_measure_refs": ["measurement-method:decision-state-findability"],
                        },
                        {
                            "outcome_id": "product-thesis:craft#outcome-bounded-collaboration",
                            "statement": "Machine collaborators can operate within explicit evidence and authority boundaries.",
                            "value_measure_refs": ["measurement-method:authority-boundary-preservation"],
                        },
                        {
                            "outcome_id": "product-thesis:craft#outcome-product-continuity",
                            "statement": "Projects can evolve without silently redefining the Product.",
                            "value_measure_refs": ["measurement-method:product-identity-drift"],
                        },
                    ],
                    "boundaries": [
                        "The thesis does not prove that Craft is implemented or effective",
                        "One Project or experiment cannot prove the complete thesis",
                        "The thesis does not authorize deployment, publication, or external effects",
                    ],
                    "hypotheses": [
                        {
                            "hypothesis_id": "craft-thesis-h1",
                            "statement": "Explicit semantic and authority boundaries improve decision clarity enough to justify their maintenance cost.",
                            "evidence_state": "untested",
                        },
                        {
                            "hypothesis_id": "craft-thesis-h2",
                            "statement": "Evidence-bound machine collaboration preserves human agency better than unconstrained automation.",
                            "evidence_state": "untested",
                        },
                    ],
                    "assumptions": [
                        "Repository work benefits from explicit semantic and authority boundaries",
                        "Machine assistance is more useful when claims remain tied to evidence",
                        "Human owners must retain admission and effect authority",
                    ],
                    "evidence_routes": ["route:craft-product-thesis-evidence"],
                    "counterevidence_routes": ["route:craft-product-thesis-challenge"],
                    "revision_criteria": [
                        "Evidence shows the governed workflow adds more burden than decision clarity",
                        "Users cannot determine which artifacts or decisions are authoritative",
                        "A simpler model provides equivalent traceability and authority separation",
                    ],
                    "owner_ref": "role:craft-product-owner",
                    "owner_route": "role:craft-product-owner",
                    "commitment_state": "draft",
                    "successor_refs": [],
                    "revision_history": [],
                    "challenge_route": "route:craft-product-thesis-challenge",
                    "scope_ref": "scope:craft-product",
                }
            )
            dump(destination / "fixtures/valid/record.json", witness)
            missing_structure = dict(witness)
            del missing_structure["value_mechanism"]
            dump(destination / "fixtures/invalid/missing-thesis-structure.json", missing_structure)
        if target_id == "type.product-capability":
            if refinement is None or refinement["review_state"] != "revision-authorized-before-admission":
                raise RuntimeError("Product Capability refinement authorization is missing")
            schema = load(destination / "schema.json")
            optional_refs = {
                "items": {"pattern": "\\S", "type": "string"},
                "maxItems": 100,
                "type": "array",
                "uniqueItems": True,
            }
            required_refs = dict(optional_refs)
            required_refs["minItems"] = 1
            schema["properties"].update(
                {
                    "name": {"pattern": "\\S", "type": "string"},
                    "product_thesis_ref": {"pattern": "\\S", "type": "string"},
                    "thesis_outcome_refs": required_refs,
                    "participant_refs": required_refs,
                    "consumer_refs": required_refs,
                    "input_contract_refs": optional_refs,
                    "output_contract_refs": required_refs,
                    "context_policy_refs": optional_refs,
                    "owner_routes": required_refs,
                    "lifecycle_posture": {
                        "additionalProperties": False,
                        "properties": {
                            "kind": {"const": "product-capability"},
                            "status": {"pattern": "\\S", "type": "string"},
                            "status_vocabulary_ref": {"pattern": "\\S", "type": "string"},
                            "evidence_refs": optional_refs,
                            "commitment_ref": {
                                "anyOf": [
                                    {"pattern": "\\S", "type": "string"},
                                    {"type": "null"},
                                ]
                            },
                            "provenance_refs": required_refs,
                            "owner_ref": {"pattern": "\\S", "type": "string"},
                            "residue_refs": optional_refs,
                        },
                        "required": [
                            "kind",
                            "status",
                            "status_vocabulary_ref",
                            "evidence_refs",
                            "commitment_ref",
                            "provenance_refs",
                            "owner_ref",
                            "residue_refs",
                        ],
                        "type": "object",
                    },
                    "realization_binding_refs": optional_refs,
                    "evidence_refs": optional_refs,
                    "revision_history": {
                        "items": {
                            "additionalProperties": False,
                            "properties": {
                                "revision_id": {"pattern": "\\S", "type": "string"},
                                "changed_anchors": {
                                    "items": {
                                        "enum": ["product_ref", "outcome", "scope_ref", "owner_routes"]
                                    },
                                    "minItems": 1,
                                    "type": "array",
                                    "uniqueItems": True,
                                },
                                "rationale": {"pattern": "\\S", "type": "string"},
                                "decision_ref": {"pattern": "\\S", "type": "string"},
                            },
                            "required": ["revision_id", "changed_anchors", "rationale", "decision_ref"],
                            "type": "object",
                        },
                        "maxItems": 100,
                        "type": "array",
                    },
                    "successor_refs": optional_refs,
                    "challenge_route": {"pattern": "\\S", "type": "string"},
                }
            )
            schema["required"].extend(
                [
                    "name",
                    "product_thesis_ref",
                    "thesis_outcome_refs",
                    "participant_refs",
                    "consumer_refs",
                    "input_contract_refs",
                    "output_contract_refs",
                    "context_policy_refs",
                    "owner_routes",
                    "lifecycle_posture",
                    "realization_binding_refs",
                    "evidence_refs",
                    "revision_history",
                    "successor_refs",
                    "challenge_route",
                ]
            )
            dump(destination / "schema.json", schema)
            witness = load(destination / "fixtures/valid/record.json")
            witness.update(
                {
                    "node_id": "capability:craft:governed-definition-admission",
                    "name": "Governed Definition Admission",
                    "product_ref": "CA2-PRODUCT-CRAFT",
                    "product_thesis_ref": "product-thesis:craft",
                    "thesis_outcome_refs": ["product-thesis:craft#outcome-authoritative-state"],
                    "outcome": "Repository owners can admit exact semantic Definitions while preserving provenance, review authority, drift visibility, and separation from consumer activation.",
                    "scope_ref": "scope:craft-semantic-governance",
                    "participant_refs": ["role:definition-owner", "role:source-admission-owner"],
                    "consumer_refs": ["consumer:definition-registry", "consumer:repository-inventory"],
                    "input_contract_refs": ["contract:definition-candidate", "contract:source-admission-selection"],
                    "output_contract_refs": ["contract:definition-admission-decision", "contract:definition-registry-postimage"],
                    "context_policy_refs": ["policy:definition-authority-separation", "policy:no-consumer-activation-by-admission"],
                    "owner_ref": "role:definition-owner",
                    "owner_routes": ["role:definition-owner", "route:definition-governance-challenge"],
                    "acceptance_conditions": [
                        "Every admitted Definition version is bound by exact path and digest",
                        "The canonical registry and human index agree on admitted current versions",
                        "Admission does not activate downstream consumers",
                    ],
                    "exclusions": [
                        "Runtime activation",
                        "Artifact Type admission",
                        "Authentication of external identity claims",
                    ],
                    "lifecycle_posture": {
                        "kind": "product-capability",
                        "status": "draft",
                        "status_vocabulary_ref": "profile.capability-lifecycle",
                        "evidence_refs": [],
                        "commitment_ref": None,
                        "provenance_refs": ["migration-contract:type.product-capability"],
                        "owner_ref": "role:definition-owner",
                        "residue_refs": ["residue:capability-owner-adoption-required"],
                    },
                    "realization_binding_refs": ["binding:craft:governed-definition-admission:workflow-v1"],
                    "evidence_refs": [],
                    "revision_history": [],
                    "successor_refs": [],
                    "challenge_route": "route:definition-governance-challenge",
                }
            )
            dump(destination / "fixtures/valid/record.json", witness)
            missing_contract = dict(witness)
            del missing_contract["output_contract_refs"]
            dump(destination / "fixtures/invalid/missing-capability-contract.json", missing_contract)
        if target_id == "type.capability-realization-binding":
            if refinement is None or refinement["review_state"] != "revision-authorized-before-admission":
                raise RuntimeError("Capability Realization Binding refinement authorization is missing")
            schema = load(destination / "schema.json")
            optional_refs = {
                "items": {"pattern": "\\S", "type": "string"},
                "maxItems": 100,
                "type": "array",
                "uniqueItems": True,
            }
            required_refs = dict(optional_refs)
            required_refs["minItems"] = 1
            schema["properties"].update(
                {
                    "binding_version": {"pattern": "\\S", "type": "string"},
                    "capability_version_ref": {"pattern": "\\S", "type": "string"},
                    "binding_state": {
                        "enum": ["candidate", "adopted", "retired", "superseded"],
                        "type": "string",
                    },
                    "realization_refs": {
                        "items": {
                            "additionalProperties": False,
                            "properties": {
                                "realization_ref": {"pattern": "\\S", "type": "string"},
                                "realization_kind": {
                                    "enum": ["capability-instance", "agent-capability", "implementation", "service", "workflow"],
                                    "type": "string",
                                },
                                "owner_ref": {"pattern": "\\S", "type": "string"},
                                "contract_ref": {"pattern": "\\S", "type": "string"},
                            },
                            "required": ["realization_ref", "realization_kind", "owner_ref", "contract_ref"],
                            "type": "object",
                        },
                        "maxItems": 100,
                        "minItems": 1,
                        "type": "array",
                    },
                    "contract": {
                        "additionalProperties": False,
                        "properties": {
                            "input_contract_refs": optional_refs,
                            "output_contract_refs": required_refs,
                            "context_policy_refs": optional_refs,
                        },
                        "required": ["input_contract_refs", "output_contract_refs", "context_policy_refs"],
                        "type": "object",
                    },
                    "adoption_decision_ref": {
                        "anyOf": [
                            {"pattern": "\\S", "type": "string"},
                            {"type": "null"},
                        ]
                    },
                    "conformance_refs": optional_refs,
                    "observation_refs": optional_refs,
                    "successor_refs": optional_refs,
                    "owner_route": {"pattern": "\\S", "type": "string"},
                    "challenge_route": {"pattern": "\\S", "type": "string"},
                }
            )
            schema["required"].extend(
                [
                    "binding_version",
                    "capability_version_ref",
                    "binding_state",
                    "adoption_decision_ref",
                    "conformance_refs",
                    "observation_refs",
                    "successor_refs",
                    "owner_route",
                    "challenge_route",
                ]
            )
            schema["allOf"] = [
                {
                    "if": {"properties": {"binding_state": {"const": "adopted"}}, "required": ["binding_state"]},
                    "then": {
                        "properties": {
                            "adoption_decision_ref": {"pattern": "\\S", "type": "string"},
                            "conformance_refs": {"minItems": 1},
                        }
                    },
                },
                {
                    "if": {"properties": {"binding_state": {"const": "superseded"}}, "required": ["binding_state"]},
                    "then": {"properties": {"successor_refs": {"minItems": 1}}},
                },
            ]
            dump(destination / "schema.json", schema)
            witness = load(destination / "fixtures/valid/record.json")
            witness.update(
                {
                    "node_id": "binding:craft:governed-definition-admission:workflow-v1",
                    "binding_version": "1.0.0-candidate.1",
                    "capability_ref": "capability:craft:governed-definition-admission",
                    "capability_version_ref": "capability:craft:governed-definition-admission@1.0.0-candidate.1",
                    "binding_state": "candidate",
                    "realization_refs": [
                        {
                            "realization_ref": "workflow:definition-admission:v1",
                            "realization_kind": "workflow",
                            "owner_ref": "role:definition-owner",
                            "contract_ref": "contract:definition-admission-workflow/v1",
                        }
                    ],
                    "contract": {
                        "input_contract_refs": ["contract:definition-candidate", "contract:source-admission-selection"],
                        "output_contract_refs": ["contract:definition-admission-decision", "contract:definition-registry-postimage"],
                        "context_policy_refs": ["policy:definition-authority-separation", "policy:no-consumer-activation-by-admission"],
                    },
                    "limitations": [
                        "Candidate binding does not adopt or activate the workflow",
                        "Schema conformance does not prove runtime or Product outcome conformance",
                    ],
                    "adoption_decision_ref": None,
                    "conformance_refs": [],
                    "observation_refs": [],
                    "successor_refs": [],
                    "owner_ref": "role:definition-owner",
                    "owner_route": "role:definition-owner",
                    "challenge_route": "route:definition-governance-challenge",
                    "scope_ref": "scope:craft-semantic-governance",
                }
            )
            dump(destination / "fixtures/valid/record.json", witness)
            missing_endpoint = dict(witness)
            del missing_endpoint["capability_version_ref"]
            dump(destination / "fixtures/invalid/missing-capability-version.json", missing_endpoint)

        if target_id == "type.research-inquiry":
            if refinement is None or refinement["review_state"] != "revision-authorized-before-admission":
                raise RuntimeError("Research Inquiry refinement authorization is missing")
            schema = load(destination / "schema.json")
            string_array = {
                "items": {"pattern": "\\S", "type": "string"},
                "maxItems": 100,
                "type": "array",
                "uniqueItems": True,
            }
            nonempty_string_array = dict(string_array)
            nonempty_string_array["minItems"] = 1
            schema["properties"].update(
                {
                    "goal_refs": nonempty_string_array,
                    "source_policy": {
                        "additionalProperties": False,
                        "properties": {
                            "allowed_source_kinds": nonempty_string_array,
                            "selection_criteria": nonempty_string_array,
                            "freshness_rule": {"pattern": "\\S", "type": "string"},
                            "conflict_handling": {"pattern": "\\S", "type": "string"},
                        },
                        "required": [
                            "allowed_source_kinds",
                            "selection_criteria",
                            "freshness_rule",
                            "conflict_handling",
                        ],
                        "type": "object",
                    },
                    "source_refs": string_array,
                    "evidence_aggregate_refs": string_array,
                    "counterevidence_refs": string_array,
                    "finding_refs": string_array,
                    "limitations": nonempty_string_array,
                    "created_at": {
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$",
                        "type": "string",
                    },
                    "last_updated_at": {
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$",
                        "type": "string",
                    },
                    "owner_route": {"pattern": "\\S", "type": "string"},
                    "challenge_route": {"pattern": "\\S", "type": "string"},
                    "claim_ceiling": {"pattern": "\\S", "type": "string"},
                }
            )
            schema["required"].extend(
                [
                    "goal_refs",
                    "source_policy",
                    "source_refs",
                    "evidence_aggregate_refs",
                    "counterevidence_refs",
                    "finding_refs",
                    "limitations",
                    "created_at",
                    "last_updated_at",
                    "owner_route",
                    "challenge_route",
                    "claim_ceiling",
                ]
            )
            dump(destination / "schema.json", schema)
            witness = {
                "authority_effect": "none",
                "challenge_route": "route:artifact-type-migration-research-challenge",
                "claim_ceiling": "Candidate Research Inquiry fixture only. It records the bounded question and planned evidence boundary; it does not establish a Finding, decision, Definition, migration completion, admission, or runtime authority.",
                "counterevidence_refs": [],
                "created_at": "2026-10-05T12:00:00Z",
                "evidence_aggregate_refs": [],
                "exclusions": [
                    "Runtime behavior or consumer activation",
                    "Claims that all CyberAlchemy v2 material has been migrated",
                    "Automatic admission of reconstructed Artifact Types",
                ],
                "finding_refs": [],
                "goal_refs": ["goal:complete-governed-artifact-type-migration"],
                "inclusions": [
                    "Compare each migration Artifact Type candidate with its admitted Definition",
                    "Detect overlap with already admitted Artifact Type carriers",
                    "Preserve validation evidence and unresolved semantic residue",
                ],
                "kind": "research-inquiry",
                "last_updated_at": "2026-10-05T12:00:00Z",
                "limitations": [
                    "Repository evidence does not prove external system behavior",
                    "Unindexed or unavailable CyberAlchemy v2 sources may remain outside the evidence set",
                ],
                "method_ref": "method:definition-bound-artifact-type-review/v1",
                "node_id": "research-inquiry:artifact-type-migration-review",
                "owner_ref": "role:migration-research-owner",
                "owner_route": "role:migration-research-owner",
                "project_ref": "CA2-PROJECT-CYBERALCHEMY-V2-MIGRATION",
                "question": "Which reconstructed CyberAlchemy v2 Artifact Types should be admitted into CyberAlchemy Lab without duplicating or weakening already admitted carriers?",
                "scope_ref": "scope:artifact-type-migration-review",
                "source_policy": {
                    "allowed_source_kinds": [
                        "admitted-definition",
                        "digest-bound-migration-contract",
                        "repository-artifact",
                        "validation-receipt",
                    ],
                    "conflict_handling": "Preserve conflicting evidence explicitly and route unresolved semantic conflicts to the challenge route.",
                    "freshness_rule": "Recompute repository paths and digests before relying on mutable local materials.",
                    "selection_criteria": [
                        "Prefer admitted semantic authority over reconstructed labels",
                        "Prefer exact paths and digests over directory inference",
                        "Include counterevidence that could block admission",
                    ],
                },
                "source_refs": [
                    "authority:definitions-registry",
                    "migration:remaining-26-materialization",
                    "authority:artifact-type-decisions",
                ],
                "status": "candidate-unadmitted",
                "stop_conditions": [
                    "Every queue entry has an admission, duplicate resolution, revision request, or explicit block",
                    "Every recommendation is bound to the current candidate, Definition, and validation evidence",
                    "Unresolved conflicts are recorded with an owner and challenge route",
                ],
            }
            dump(destination / "fixtures/valid/record.json", witness)
            missing_boundary = dict(witness)
            del missing_boundary["source_policy"]
            dump(destination / "fixtures/invalid/missing-research-boundary.json", missing_boundary)

        if target_id == "type.research-run":
            if refinement is None or refinement["review_state"] != "revision-authorized-before-admission":
                raise RuntimeError("Research Run refinement authorization is missing")
            schema = load(destination / "schema.json")
            for obsolete in ["input_refs", "output_refs", "method_ref"]:
                schema["properties"].pop(obsolete, None)
                if obsolete in schema["required"]:
                    schema["required"].remove(obsolete)
            string_array = {
                "items": {"pattern": "\\S", "type": "string"},
                "maxItems": 100,
                "type": "array",
                "uniqueItems": True,
            }
            nonempty_string_array = dict(string_array)
            nonempty_string_array["minItems"] = 1
            nullable_string = {
                "anyOf": [
                    {"pattern": "\\S", "type": "string"},
                    {"type": "null"},
                ]
            }
            schema["properties"].update(
                {
                    "inquiry_version_ref": {"pattern": "\\S", "type": "string"},
                    "project_ref": {"pattern": "\\S", "type": "string"},
                    "goal_refs": nonempty_string_array,
                    "inspected_sources": {
                        "items": {
                            "additionalProperties": False,
                            "properties": {
                                "source_ref": {"pattern": "\\S", "type": "string"},
                                "selector": {"pattern": "\\S", "type": "string"},
                                "observed_sha256": {
                                    "pattern": "^[0-9a-f]{64}$",
                                    "type": "string",
                                },
                            },
                            "required": ["source_ref", "selector", "observed_sha256"],
                            "type": "object",
                        },
                        "maxItems": 100,
                        "minItems": 1,
                        "type": "array",
                    },
                    "method_performed": {
                        "additionalProperties": False,
                        "properties": {
                            "method_ref": {"pattern": "\\S", "type": "string"},
                            "procedure_summary": {"pattern": "\\S", "type": "string"},
                            "deviation_refs": string_array,
                        },
                        "required": ["method_ref", "procedure_summary", "deviation_refs"],
                        "type": "object",
                    },
                    "observation_refs": string_array,
                    "counterevidence_refs": string_array,
                    "evidence_set_ref": nullable_string,
                    "run_state": {
                        "enum": ["running", "completed", "stopped", "failed"],
                        "type": "string",
                    },
                    "stop_reason": nullable_string,
                    "owner_route": {"pattern": "\\S", "type": "string"},
                    "challenge_route": {"pattern": "\\S", "type": "string"},
                    "claim_ceiling": {"pattern": "\\S", "type": "string"},
                }
            )
            schema["required"].extend(
                [
                    "inquiry_version_ref",
                    "project_ref",
                    "goal_refs",
                    "inspected_sources",
                    "method_performed",
                    "observation_refs",
                    "counterevidence_refs",
                    "evidence_set_ref",
                    "run_state",
                    "stop_reason",
                    "owner_route",
                    "challenge_route",
                    "claim_ceiling",
                ]
            )
            schema["allOf"] = [
                {
                    "if": {
                        "properties": {"run_state": {"const": "completed"}},
                        "required": ["run_state"],
                    },
                    "then": {
                        "properties": {
                            "evidence_set_ref": {"pattern": "\\S", "type": "string"},
                            "observation_refs": {"minItems": 1},
                            "period": {
                                "properties": {
                                    "end": {"format": "date-time", "type": "string"}
                                }
                            },
                        }
                    },
                },
                {
                    "if": {
                        "properties": {
                            "run_state": {"enum": ["stopped", "failed"]}
                        },
                        "required": ["run_state"],
                    },
                    "then": {
                        "properties": {
                            "stop_reason": {"pattern": "\\S", "type": "string"},
                            "period": {
                                "properties": {
                                    "end": {"format": "date-time", "type": "string"}
                                }
                            },
                        }
                    },
                },
            ]
            dump(destination / "schema.json", schema)
            inquiry_artifact = LAB / "authority/artifact-types/research-inquiry/v1/artifact.json"
            inquiry_definition = LAB / "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/research-inquiry/v1/definition.json"
            witness = {
                "authority_effect": "none",
                "challenge_route": "route:artifact-type-migration-research-challenge",
                "claim_ceiling": "Candidate Research Run fixture only. It records one completed repository review execution and its evidence boundary; it does not establish a Finding, admission recommendation, migration completion, Definition, proof, or runtime authority.",
                "counterevidence_refs": [
                    "evidence:research-inquiry-original-minimal-contract"
                ],
                "evidence_set_ref": "evidence-set:research-inquiry-v1-review",
                "goal_refs": ["goal:complete-governed-artifact-type-migration"],
                "inquiry_ref": "research-inquiry:artifact-type-migration-review",
                "inquiry_version_ref": "research-inquiry:artifact-type-migration-review@1.0.0-candidate.1",
                "inspected_sources": [
                    {
                        "observed_sha256": sha(inquiry_definition),
                        "selector": "whole-json",
                        "source_ref": relative(inquiry_definition),
                    },
                    {
                        "observed_sha256": sha(inquiry_artifact),
                        "selector": "whole-json",
                        "source_ref": relative(inquiry_artifact),
                    },
                ],
                "kind": "research-run",
                "limitations": [
                    "The run inspected repository evidence only",
                    "The run did not validate external systems or execute a consumer runtime",
                ],
                "method_performed": {
                    "deviation_refs": [],
                    "method_ref": "method:definition-bound-artifact-type-review/v1",
                    "procedure_summary": "Compare the materialized Artifact Type with its admitted Definition, identify missing semantic fields, revise the closed schema and fixture, and rerun deterministic package and batch validation.",
                },
                "node_id": "research-run:research-inquiry-v1-review:2026-10-05",
                "observation_refs": [
                    "observation:research-inquiry-definition-gap-review",
                    "observation:research-inquiry-package-validation",
                ],
                "owner_ref": "role:migration-research-owner",
                "owner_route": "role:migration-research-owner",
                "period": {
                    "end": "2026-10-05T13:00:00Z",
                    "start": "2026-10-05T12:00:00Z",
                },
                "project_ref": "CA2-PROJECT-CYBERALCHEMY-V2-MIGRATION",
                "receipt_ref": "receipt:research-inquiry-v1-review",
                "run_state": "completed",
                "scope_ref": "scope:artifact-type-migration-review",
                "status": "candidate-unadmitted",
                "stop_reason": None,
            }
            dump(destination / "fixtures/valid/record.json", witness)
            missing_execution_evidence = dict(witness)
            del missing_execution_evidence["inspected_sources"]
            dump(destination / "fixtures/invalid/missing-execution-evidence.json", missing_execution_evidence)

        if target_id == "type.finding":
            if refinement is None or refinement["review_state"] != "revision-authorized-before-admission":
                raise RuntimeError("Finding refinement authorization is missing")
            schema = load(destination / "schema.json")
            schema["properties"].pop("evidence_ref", None)
            schema["properties"].pop("question_ref", None)
            for obsolete in ["evidence_ref", "question_ref"]:
                if obsolete in schema["required"]:
                    schema["required"].remove(obsolete)
            string_array = {
                "items": {"pattern": "\\S", "type": "string"},
                "maxItems": 100,
                "type": "array",
                "uniqueItems": True,
            }
            nonempty_string_array = dict(string_array)
            nonempty_string_array["minItems"] = 1
            schema["properties"].update(
                {
                    "inquiry_ref": {"pattern": "\\S", "type": "string"},
                    "question": {"pattern": "\\S", "type": "string"},
                    "research_run_refs": nonempty_string_array,
                    "evidence_set_refs": nonempty_string_array,
                    "evidence_refs": nonempty_string_array,
                    "support_assessment": {
                        "additionalProperties": False,
                        "properties": {
                            "support_state": {
                                "enum": [
                                    "supported",
                                    "partially-supported",
                                    "not-supported",
                                    "contradicted",
                                    "indeterminate",
                                ],
                                "type": "string",
                            },
                            "rationale": {"pattern": "\\S", "type": "string"},
                        },
                        "required": ["support_state", "rationale"],
                        "type": "object",
                    },
                    "finding_state": {
                        "enum": ["draft", "current", "contested", "superseded", "withdrawn"],
                        "type": "string",
                    },
                    "created_at": {
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$",
                        "type": "string",
                    },
                    "last_updated_at": {
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$",
                        "type": "string",
                    },
                    "owner_route": {"pattern": "\\S", "type": "string"},
                    "challenge_route": {"pattern": "\\S", "type": "string"},
                    "successor_refs": string_array,
                    "revision_history": {
                        "items": {
                            "additionalProperties": False,
                            "properties": {
                                "revision_id": {"pattern": "\\S", "type": "string"},
                                "rationale": {"pattern": "\\S", "type": "string"},
                                "decision_ref": {"pattern": "\\S", "type": "string"},
                                "supersedes_finding_ref": {
                                    "anyOf": [
                                        {"pattern": "\\S", "type": "string"},
                                        {"type": "null"},
                                    ]
                                },
                            },
                            "required": [
                                "revision_id",
                                "rationale",
                                "decision_ref",
                                "supersedes_finding_ref",
                            ],
                            "type": "object",
                        },
                        "maxItems": 100,
                        "type": "array",
                    },
                    "claim_ceiling": {"pattern": "\\S", "type": "string"},
                }
            )
            schema["required"].extend(
                [
                    "inquiry_ref",
                    "question",
                    "research_run_refs",
                    "evidence_set_refs",
                    "evidence_refs",
                    "support_assessment",
                    "finding_state",
                    "created_at",
                    "last_updated_at",
                    "owner_route",
                    "challenge_route",
                    "successor_refs",
                    "revision_history",
                    "claim_ceiling",
                ]
            )
            schema["allOf"] = [
                {
                    "if": {
                        "properties": {"finding_state": {"const": "superseded"}},
                        "required": ["finding_state"],
                    },
                    "then": {"properties": {"successor_refs": {"minItems": 1}}},
                }
            ]
            dump(destination / "schema.json", schema)
            witness = {
                "authority_effect": "none",
                "challenge_route": "route:artifact-type-migration-research-challenge",
                "claim_ceiling": "Candidate Finding fixture only. The cited repository evidence supports a bounded contract-gap conclusion; it does not admit an Artifact Type, prove migration completeness, create a Definition or decision, or authorize implementation or runtime effects.",
                "counterevidence_refs": [
                    "evidence:research-inquiry-original-scaffold-preserved-question-method-and-stop-conditions"
                ],
                "created_at": "2026-10-05T13:05:00Z",
                "evidence_refs": [
                    "observation:research-inquiry-definition-gap-review",
                    "observation:research-inquiry-package-validation",
                ],
                "evidence_set_refs": ["evidence-set:research-inquiry-v1-review"],
                "finding_state": "draft",
                "inquiry_ref": "research-inquiry:artifact-type-migration-review",
                "kind": "finding",
                "last_updated_at": "2026-10-05T13:05:00Z",
                "limitations": [
                    "The comparison covers the admitted Definition and current repository candidate only",
                    "It does not establish behavior of external or unavailable CyberAlchemy v2 systems",
                ],
                "node_id": "finding:research-inquiry-v1-contract-gap",
                "owner_ref": "role:migration-research-owner",
                "owner_route": "role:migration-research-owner",
                "question": "Which reconstructed CyberAlchemy v2 Artifact Types should be admitted into CyberAlchemy Lab without duplicating or weakening already admitted carriers?",
                "research_run_refs": [
                    "research-run:research-inquiry-v1-review:2026-10-05"
                ],
                "revision_history": [],
                "scope_ref": "scope:artifact-type-migration-review",
                "statement": "Research Inquiry/v1 candidate.1 preserved a bounded question, Project, method, scope, and stopping conditions but omitted Goal linkage, source policy, evidence and counterevidence separation, Finding references, limitations, timestamps, owner route, challenge route, and a claim ceiling required to carry the admitted Definition without semantic weakening.",
                "status": "candidate-unadmitted",
                "successor_refs": [],
                "support_assessment": {
                    "rationale": "The missing fields are directly observable by comparing the admitted Research Inquiry Definition with the candidate.1 schema; the original scaffold's preserved fields are recorded as counterevidence against claiming total absence of Research semantics.",
                    "support_state": "supported",
                },
            }
            dump(destination / "fixtures/valid/record.json", witness)
            missing_support = dict(witness)
            del missing_support["support_assessment"]
            dump(destination / "fixtures/invalid/missing-support-assessment.json", missing_support)

        review_model.apply_package(target_id, destination)

        rebound = []
        for binding in source_artifact["semantic_definition_bindings"]:
            definition_ref = binding["definition_ref"]
            if definition_ref not in definition_entries:
                raise RuntimeError(f"Definition is not admitted: {definition_ref}")
            live = definition_entries[definition_ref]
            if sha(LAB / live["path"]) != live["sha256"]:
                raise RuntimeError(f"live Definition drift: {definition_ref}")
            rebound.append(
                {
                    "admission_decision_ref": live["admission_decision_ref"],
                    "admission_posture": "admitted",
                    "definition_ref": definition_ref,
                    "path": live["path"],
                    "sha256": live["sha256"],
                }
            )

        artifact = dict(source_artifact)
        artifact["classification"] = dict(artifact["classification"])
        artifact["classification"]["lifecycle_posture_ref"] = "candidate:remaining-26-materialization/v1"
        artifact["semantic_definition_bindings"] = rebound
        artifact["source_direction"] = {
            "canonical": "artifact.json",
            "human_projection": "ARTIFACT.md",
            "projection_policy": "generated-only",
            "shared_generator_path": relative(SHARED_GENERATOR),
            "shared_generator_sha256": sha(SHARED_GENERATOR),
        }
        artifact["validation_contract"] = dict(artifact["validation_contract"])
        artifact["validation_contract"]["shared_validator_path"] = relative(SHARED_VALIDATOR)
        artifact["validation_contract"]["shared_validator_sha256"] = sha(SHARED_VALIDATOR)
        artifact["validation_contract"]["validator_path"] = relative(destination / "validate.py")
        if target_id == "type.intent":
            artifact["version"] = "1.0.0-candidate.2"
            artifact["schema_ref"] = "cal.schema.intent-review-candidate/v2"
            artifact["distinct_validation_purpose"] = "Records attributable desired direction together with its output hypothesis, lifecycle, revision route, and outcome traceability."
            artifact["four_facets"] = dict(artifact["four_facets"])
            artifact["four_facets"]["human_continuation"] = "Generated RECORD.md and the materialization review record explain the example, refinement, and limits."
            artifact["instance_contract"] = dict(artifact["instance_contract"])
            artifact["instance_contract"]["required_semantic_fields"] = sorted(
                set(artifact["instance_contract"]["required_semantic_fields"])
                | {
                    "intent_state",
                    "target_pressure",
                    "current_output_hypothesis",
                    "satisfaction_refs",
                    "successor_refs",
                    "revision_route",
                    "revision_history",
                }
            )
            artifact["orthogonality_rules"] = list(artifact["orthogonality_rules"]) + [
                {
                    "rule_id": "INTENT-TRACEABILITY",
                    "statement": "Lifecycle state, output hypothesis, revisions, successors, and satisfaction evidence remain explicit and independently reviewable.",
                }
            ]
            artifact["validation_contract"]["negative_witnesses"] = list(
                artifact["validation_contract"]["negative_witnesses"]
            ) + ["fixtures/invalid/missing-traceability.json"]
        if target_id == "type.product-thesis":
            artifact["version"] = "1.0.0-candidate.3"
            artifact["schema_ref"] = "cal.schema.product-thesis-review-candidate/v3"
            artifact["distinct_validation_purpose"] = "Defines an owner-held Product value proposition, mechanism, principles, hypotheses, evidence routes, commitment lifecycle, and revision criteria."
            artifact["four_facets"] = dict(artifact["four_facets"])
            artifact["four_facets"]["human_continuation"] = "Generated RECORD.md and the materialization review record explain the thesis, refinement, and limits."
            artifact["instance_contract"] = dict(artifact["instance_contract"])
            artifact["instance_contract"]["required_semantic_fields"] = sorted(
                set(artifact["instance_contract"]["required_semantic_fields"])
                | {
                    "participants",
                    "value_mechanism",
                    "first_order_principles",
                    "intended_outcomes",
                    "boundaries",
                    "hypotheses",
                    "evidence_routes",
                    "counterevidence_routes",
                    "owner_route",
                    "commitment_state",
                    "successor_refs",
                    "revision_history",
                    "challenge_route",
                }
            )
            artifact["orthogonality_rules"] = list(artifact["orthogonality_rules"]) + [
                {
                    "rule_id": "PRODUCT-THESIS-EVIDENCE-BOUNDARY",
                    "statement": "Commitment records an owner-held proposition; it does not prove Product realization, effectiveness, market value, or product-market fit.",
                },
                {
                    "rule_id": "PRODUCT-THESIS-REVISION",
                    "statement": "Evidence, counterevidence, revisions, successors, and challenges remain explicit and independently reviewable.",
                },
            ]
            artifact["validation_contract"]["negative_witnesses"] = list(
                artifact["validation_contract"]["negative_witnesses"]
            ) + ["fixtures/invalid/missing-thesis-structure.json"]
        if target_id == "type.product-capability":
            artifact["version"] = "1.0.0-candidate.2"
            artifact["schema_ref"] = "cal.schema.product-capability-review-candidate/v2"
            artifact["distinct_validation_purpose"] = "Defines one stable, owner-qualified Product outcome and its contracts, thesis trace, lifecycle posture, evidence routes, and realization-binding boundary."
            artifact["four_facets"] = dict(artifact["four_facets"])
            artifact["four_facets"]["human_continuation"] = "Generated RECORD.md and the materialization review record explain the capability contract, product and thesis trace, and limits."
            artifact["instance_contract"] = dict(artifact["instance_contract"])
            artifact["instance_contract"]["required_semantic_fields"] = sorted(
                set(artifact["instance_contract"]["required_semantic_fields"])
                | {
                    "name",
                    "product_thesis_ref",
                    "thesis_outcome_refs",
                    "participant_refs",
                    "consumer_refs",
                    "input_contract_refs",
                    "output_contract_refs",
                    "context_policy_refs",
                    "owner_routes",
                    "lifecycle_posture",
                    "realization_binding_refs",
                    "evidence_refs",
                    "revision_history",
                    "successor_refs",
                    "challenge_route",
                }
            )
            artifact["orthogonality_rules"] = list(artifact["orthogonality_rules"]) + [
                {
                    "rule_id": "PRODUCT-CAPABILITY-THESIS-TRACE",
                    "statement": "Every Product Capability points to exactly one Product and at least one stable outcome in a Product Thesis.",
                },
                {
                    "rule_id": "PRODUCT-CAPABILITY-REALIZATION-SEPARATION",
                    "statement": "Capability identity and outcome remain stable across realization bindings; implementation references do not define the capability.",
                },
            ]
            artifact["validation_contract"]["negative_witnesses"] = list(
                artifact["validation_contract"]["negative_witnesses"]
            ) + ["fixtures/invalid/missing-capability-contract.json"]
        if target_id == "type.capability-realization-binding":
            artifact["version"] = "1.0.0-candidate.2"
            artifact["schema_ref"] = "cal.schema.capability-realization-binding-review-candidate/v2"
            artifact["distinct_validation_purpose"] = "Binds one exact Product Capability version to typed owner-qualified realizations while keeping adoption, conformance, observations, operation, and value as separate claims."
            artifact["four_facets"] = dict(artifact["four_facets"])
            artifact["four_facets"]["human_continuation"] = "Generated RECORD.md and the materialization review record explain endpoints, contract mapping, evidence posture, and limits."
            artifact["instance_contract"] = dict(artifact["instance_contract"])
            artifact["instance_contract"]["required_semantic_fields"] = sorted(
                set(artifact["instance_contract"]["required_semantic_fields"])
                | {
                    "binding_version",
                    "capability_version_ref",
                    "binding_state",
                    "adoption_decision_ref",
                    "conformance_refs",
                    "observation_refs",
                    "successor_refs",
                    "owner_route",
                    "challenge_route",
                }
            )
            artifact["orthogonality_rules"] = list(artifact["orthogonality_rules"]) + [
                {
                    "rule_id": "CAPABILITY-BINDING-NON-COLLAPSE",
                    "statement": "A realization endpoint, binding, Capability Instance, and Product Capability remain distinct identities with separate owners and lifecycle posture.",
                },
                {
                    "rule_id": "CAPABILITY-BINDING-EVIDENCE-SEPARATION",
                    "statement": "Candidate, adopted, conformant, observed, operational, and valuable are separate claims and cannot be inferred from one another.",
                },
            ]
            artifact["validation_contract"]["negative_witnesses"] = list(
                artifact["validation_contract"]["negative_witnesses"]
            ) + ["fixtures/invalid/missing-capability-version.json"]
        if target_id == "type.research-inquiry":
            artifact["version"] = "1.0.0-candidate.2"
            artifact["schema_ref"] = "cal.schema.research-inquiry-review-candidate/v2"
            artifact["distinct_validation_purpose"] = "Defines one bounded attributable research question with Project and Goal linkage, source policy, method, evidence boundaries, stopping conditions, limitations, timestamps, ownership, and challengeability while keeping Findings separate."
            artifact["four_facets"] = dict(artifact["four_facets"])
            artifact["four_facets"]["human_continuation"] = "Generated RECORD.md and the materialization review record explain the inquiry boundary, source policy, evidence separation, refinement, and limits."
            artifact["instance_contract"] = dict(artifact["instance_contract"])
            artifact["instance_contract"]["required_semantic_fields"] = sorted(
                set(artifact["instance_contract"]["required_semantic_fields"])
                | {
                    "goal_refs",
                    "source_policy",
                    "source_refs",
                    "evidence_aggregate_refs",
                    "counterevidence_refs",
                    "finding_refs",
                    "limitations",
                    "created_at",
                    "last_updated_at",
                    "owner_route",
                    "challenge_route",
                    "claim_ceiling",
                }
            )
            artifact["orthogonality_rules"] = list(artifact["orthogonality_rules"]) + [
                {
                    "rule_id": "RESEARCH-INQUIRY-TRACEABILITY",
                    "statement": "Question, Project and Goal linkage, scope, sources, method, timestamps, ownership, stopping conditions, and limitations remain explicit and independently reviewable.",
                },
                {
                    "rule_id": "RESEARCH-INQUIRY-EVIDENCE-SEPARATION",
                    "statement": "Sources, evidence aggregates, counterevidence, and separate Findings do not become conclusions, decisions, Definitions, proof, or authority through the inquiry record.",
                },
                {
                    "rule_id": "RESEARCH-INQUIRY-NO-OUTCOME",
                    "statement": "Research Inquiry carries no outcome field; conclusions remain in separately governed Finding records.",
                },
            ]
            artifact["validation_contract"]["negative_witnesses"] = list(
                artifact["validation_contract"]["negative_witnesses"]
            ) + ["fixtures/invalid/missing-research-boundary.json"]
        if target_id == "type.research-run":
            artifact["version"] = "1.0.0-candidate.2"
            artifact["schema_ref"] = "cal.schema.research-run-review-candidate/v2"
            artifact["distinct_validation_purpose"] = "Records one immutable attributable execution of an exact Research Inquiry version, including digest-bearing inspected sources, performed method and deviations, observations, counterevidence, evidence-set result, limitations, timing, completion or stop state, ownership, and challenge route."
            artifact["four_facets"] = dict(artifact["four_facets"])
            artifact["four_facets"]["human_continuation"] = "Generated RECORD.md and the materialization review record explain the exact execution inputs, method, outputs, state, refinement, and limits."
            artifact["instance_contract"] = dict(artifact["instance_contract"])
            required = set(artifact["instance_contract"]["required_semantic_fields"])
            required -= {"input_refs", "output_refs", "method_ref"}
            required |= {
                "inquiry_version_ref",
                "project_ref",
                "goal_refs",
                "inspected_sources",
                "method_performed",
                "observation_refs",
                "counterevidence_refs",
                "evidence_set_ref",
                "run_state",
                "stop_reason",
                "owner_route",
                "challenge_route",
                "claim_ceiling",
            }
            artifact["instance_contract"]["required_semantic_fields"] = sorted(required)
            artifact["orthogonality_rules"] = list(artifact["orthogonality_rules"]) + [
                {
                    "rule_id": "RESEARCH-RUN-IMMUTABLE-INPUTS",
                    "statement": "The exact Inquiry version and every inspected source digest are explicit; planned inputs or directory placement cannot substitute for observed execution inputs.",
                },
                {
                    "rule_id": "RESEARCH-RUN-EXECUTION-SEPARATION",
                    "statement": "A completed or stopped execution and its evidence set do not become a Finding, decision, Definition, proof, admission, or Product claim.",
                },
                {
                    "rule_id": "RESEARCH-RUN-STATE-EVIDENCE",
                    "statement": "Completed runs require observations, an evidence set, and an end time; stopped or failed runs require a stop reason and end time.",
                },
            ]
            artifact["validation_contract"]["negative_witnesses"] = list(
                artifact["validation_contract"]["negative_witnesses"]
            ) + ["fixtures/invalid/missing-execution-evidence.json"]
        if target_id == "type.finding":
            artifact["version"] = "1.0.0-candidate.2"
            artifact["schema_ref"] = "cal.schema.finding-review-candidate/v2"
            artifact["distinct_validation_purpose"] = "Records one attributable evidence-bounded conclusion derived from exact Research Runs and Evidence Sets, with question fidelity, support assessment, counterevidence, limitations, lifecycle, ownership, challengeability, revisions, successors, and an explicit claim ceiling."
            artifact["four_facets"] = dict(artifact["four_facets"])
            artifact["four_facets"]["human_continuation"] = "Generated RECORD.md and the materialization review record explain the question, derivation, support and counterevidence, lifecycle, refinement, and limits."
            artifact["instance_contract"] = dict(artifact["instance_contract"])
            required = set(artifact["instance_contract"]["required_semantic_fields"])
            required -= {"evidence_ref", "question_ref"}
            required |= {
                "inquiry_ref",
                "question",
                "research_run_refs",
                "evidence_set_refs",
                "evidence_refs",
                "support_assessment",
                "finding_state",
                "created_at",
                "last_updated_at",
                "owner_route",
                "challenge_route",
                "successor_refs",
                "revision_history",
                "claim_ceiling",
            }
            artifact["instance_contract"]["required_semantic_fields"] = sorted(required)
            artifact["orthogonality_rules"] = list(artifact["orthogonality_rules"]) + [
                {
                    "rule_id": "FINDING-DERIVATION",
                    "statement": "Every Finding preserves the Inquiry question and cites one or more Research Runs, Evidence Sets, and supporting evidence; counterevidence and limitations remain explicit.",
                },
                {
                    "rule_id": "FINDING-CLAIM-CEILING",
                    "statement": "Finding wording cannot exceed its recorded support assessment, and a Finding does not become a decision, Definition, specification, proof, admission, policy, or Product claim.",
                },
                {
                    "rule_id": "FINDING-LIFECYCLE",
                    "statement": "Draft, current, contested, superseded, and withdrawn are explicit states; superseded Findings require at least one successor reference.",
                },
            ]
            artifact["validation_contract"]["negative_witnesses"] = list(
                artifact["validation_contract"]["negative_witnesses"]
            ) + ["fixtures/invalid/missing-support-assessment.json"]
        review_model.apply_artifact(target_id, artifact)
        artifact["schema_digest"] = sha(destination / "schema.json")
        artifact["typed_residue"] = [
            {
                "consequence": "The package remains candidate-only and is absent from admitted Artifact Type authority.",
                "missing": "Artifact Type owner admission for this exact materialized package.",
                "owner_ref": "role:artifact-type-owner",
                "residue_id": "MAT-R1",
            },
            {
                "consequence": "No operational or domain claim may be inferred from the candidate fixture.",
                "missing": "A real instance, bounded consumer integration, and an activation decision.",
                "owner_ref": "role:migration-consumer-owner",
                "residue_id": "MAT-R2",
            },
        ]
        artifact["claim_ceiling"] = (
            "This stable package starts from the migration-selected Artifact Type contract, applies any recorded owner-review refinement, and binds its semantic dependencies to admitted Definitions. "
            "It does not admit the Artifact Type, admit any instance, authenticate fixture claims, integrate a consumer, or activate behavior."
        )
        dump(destination / "artifact.json", artifact)
        (destination / "generator.py").write_text(PACKAGE_GENERATOR, encoding="utf-8")
        (destination / "validate.py").write_text(PACKAGE_VALIDATOR, encoding="utf-8")
        (destination / "ARTIFACT.md").write_text(generator.render_artifact(artifact), encoding="utf-8")
        valid_data = load(destination / artifact["validation_contract"]["positive_witness"])
        (destination / artifact["validation_contract"]["positive_projection"]).write_text(
            generator.render_instance(artifact, valid_data), encoding="utf-8"
        )

        materialization = {
            "schema_version": "cyberalchemy-lab-artifact-type-materialization/v1",
            "target_id": target_id,
            "artifact_type_ref": artifact["artifact_type_ref"],
            "name": artifact["name"],
            "status": "candidate-refined" if refinement else "candidate-materialized",
            "authority_effect": "none",
            "package_path": relative(destination),
            "source_artifact": selected_entry["binding"],
            "source_contract": selected_entry["contract"],
            "migration_contract_admission": {
                "decision_ref": migration_decision["decision_id"],
                "path": relative(MIGRATION_DECISION),
                "sha256": sha(MIGRATION_DECISION),
            },
            "definition_admission": {
                "decision_ref": definition_decision["decision_id"],
                "path": relative(DEFINITION_DECISION),
                "sha256": sha(DEFINITION_DECISION),
            },
            "semantic_definition_bindings": rebound,
            "consumer_activation": "not-applied",
            "claim_ceiling": artifact["claim_ceiling"],
        }
        if refinement:
            materialization["review_refinement"] = {
                "path": relative(refinement_path),
                "sha256": sha(refinement_path),
                "review_state": refinement["review_state"],
            }
        dump(destination / "materialization.json", materialization)
        (destination / "MATERIALIZATION.md").write_text(render_materialization(materialization), encoding="utf-8")

        if validator.validate_package(destination) != 0:
            raise RuntimeError(f"candidate package validation failed: {target_id}")
        receipt_path = destination / "receipts/validation.json"
        if load(receipt_path)["result"] != "PASS":
            raise RuntimeError(f"candidate package receipt blocked: {target_id}")

        catalog_entries.append(
            {
                "target_id": target_id,
                "artifact_type_ref": artifact["artifact_type_ref"],
                "name": artifact["name"],
                "domain_family": source_contract["normalization_contract"]["family"],
                "semantic_definition_refs": artifact["semantic_definition_refs"],
                "package_path": relative(destination),
                "canonical_instance": artifact["instance_contract"]["canonical_filename"],
                "status": "candidate-refined" if refinement else "candidate-materialized",
                "authority_effect": "none",
                "artifact_sha256": sha(destination / "artifact.json"),
                "schema_sha256": sha(destination / "schema.json"),
                "materialization_sha256": sha(destination / "materialization.json"),
                "validation_receipt": {
                    "path": relative(receipt_path),
                    "sha256": sha(receipt_path),
                    "result": "PASS",
                },
            }
        )

    candidate = {
        "schema_version": "cyberalchemy-lab-artifact-type-materialization-batch/v1",
        "batch_id": "CAL-ARTIFACT-TYPE-MATERIALIZATION-0004",
        "status": "candidate-materialized-awaiting-artifact-type-owner-admission",
        "authority_effect": "none",
        "migration_contract_admission": {
            "decision_ref": migration_decision["decision_id"],
            "path": relative(MIGRATION_DECISION),
            "sha256": sha(MIGRATION_DECISION),
        },
        "definition_admission": {
            "decision_ref": definition_decision["decision_id"],
            "path": relative(DEFINITION_DECISION),
            "sha256": sha(DEFINITION_DECISION),
        },
        "counts": {
            "materialized_artifact_types": len(catalog_entries),
            "package_validation_pass": len(catalog_entries),
            "owner_review_refinements": sum(1 for entry in catalog_entries if entry["status"] == "candidate-refined"),
            "artifact_types_admitted_by_this_batch": 0,
            "consumer_activations": 0,
        },
        "entries": catalog_entries,
        "claim_ceiling": "This batch materializes 26 migration-selected Artifact Type contracts as stable candidate packages with admitted Definition bindings and records owner-review refinements where authorized. It does not admit Artifact Types or instances and does not activate consumers or behavior.",
    }
    dump(ROOT / "candidate.json", candidate)
    (ROOT / "CATALOG.md").write_text(render_catalog(catalog_entries), encoding="utf-8")

    manifest_paths = [ROOT / "build.py", ROOT / "validate.py", ROOT / "review_model.py", ROOT / "candidate.json", ROOT / "CATALOG.md"]
    manifest_paths.extend(path for path in REFINEMENTS.rglob("*") if path.is_file())
    for item in catalog_entries:
        package = LAB / item["package_path"]
        manifest_paths.extend(path for path in package.rglob("*") if path.is_file())
    manifest = {
        "schema_version": "cyberalchemy-lab-exact-file-manifest/v1",
        "subject": candidate["batch_id"],
        "files": [
            {"path": relative(path), "sha256": sha(path)}
            for path in sorted(set(manifest_paths), key=lambda path: relative(path))
        ],
        "excluded_from_self_hash": [relative(ROOT / "manifest.json"), relative(ROOT / "receipts/validation.json")],
    }
    dump(ROOT / "manifest.json", manifest)
    result = subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False)
    if result.returncode:
        return result.returncode
    print(f"MATERIALIZED_ARTIFACT_TYPES={len(catalog_entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
