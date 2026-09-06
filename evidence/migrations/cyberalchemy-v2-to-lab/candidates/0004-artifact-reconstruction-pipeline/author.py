#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
SOURCE = LAB.parent / "domainspec-core" / "cyberAlchemy-v2"
PREDECESSOR = ROOT.parent / "0003-review-led-reconstruction"
DECISION = PREDECESSOR / "decisions/0001-planning-selection/decision.json"
D65 = PREDECESSOR / "d65-successor.json"
D65_REVIEW = PREDECESSOR / "reviews/0001-definition/review.json"
TARGET_INDEX = PREDECESSOR / "target-candidate-index.json"
DEFINITION_SCHEMA = LAB / "authority/artifact-types/definition/v1/schema.json"
DEFINITION_GENERATOR = LAB / "authority/artifact-types/definition/v1/generator.py"
ARTIFACT_TYPE_ROOT = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
ARTIFACT_TYPE_DECISION = LAB / "docs/decisions/0029-cml07-semantic-foundation-v1/decision.json"
ARTIFACT_GENERATOR = LAB / "tooling/generators/artifact_surface.py"
ARTIFACT_VALIDATOR = LAB / "tooling/validators/artifact_surface.py"
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
CAV2_DEFINITIONS = SOURCE / "authority/definitions/DEFINITIONS.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(LAB.resolve()).as_posix()


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(result)
    return result


def source_binding(path: Path, repository_id: str = "cyberalchemy-lab") -> dict:
    base = LAB if repository_id == "cyberalchemy-lab" else SOURCE
    return {
        "repository_id": repository_id,
        "path": path.resolve().relative_to(base.resolve()).as_posix(),
        "sha256": sha(path),
    }


def markdown_h2_section(path: Path, heading: str) -> bytes:
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"(?m)^## CAV2-D(\d+): (.+)$", text))
    starts = [index for index, match in enumerate(matches) if match.group(0) == heading]
    if len(starts) != 1:
        raise ValueError(f"expected one heading {heading!r} in {path}")
    index = starts[0]
    start = matches[index].start()
    end = matches[index + 1].start() if index + 1 < len(matches) else text.find(
        "\n## Withdrawn Definition IDs", matches[index].end()
    )
    if end < 0:
        end = len(text)
    return (text[start:end].rstrip() + "\n").encode("utf-8")


def base_instance_schema(
    title: str,
    schema_version: str,
    identity_field: str,
    artifact_type_ref: str,
    extra_properties: dict,
    required_extra: list[str],
) -> dict:
    properties = {
        "schema_version": {"const": schema_version},
        identity_field: {"type": "string", "minLength": 1},
        "artifact_type_ref": {"const": artifact_type_ref},
        "status": {"const": "candidate-unadmitted"},
        "authority_effect": {"const": "none"},
        "owner_ref": {"type": "string", "minLength": 1},
        "source_direction": {
            "type": "object",
            "additionalProperties": False,
            "required": ["canonical", "human_projection", "projection_policy"],
            "properties": {
                "canonical": {"type": "string", "minLength": 1},
                "human_projection": {"type": "string", "minLength": 1},
                "projection_policy": {"const": "generated-only"},
            },
        },
        "claim_ceiling": {"type": "string", "minLength": 1},
        **extra_properties,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://cyberalchemy.local/schemas/reconstruction/{schema_version}",
        "title": title,
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            identity_field,
            "artifact_type_ref",
            "status",
            "authority_effect",
            "owner_ref",
            *required_extra,
            "source_direction",
            "claim_ceiling",
        ],
        "properties": properties,
    }


def schemas() -> dict[str, dict]:
    string_array = {"type": "array", "items": {"type": "string", "minLength": 1}}
    return {
        "construction-profile": base_instance_schema(
            "Construction Profile v1",
            "cyberalchemy-lab-construction-profile/v1",
            "profile_id",
            "cal.artifact-type.construction-profile/v1",
            {
                "stages": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["stage_id", "predecessor_refs", "evidence_kind"],
                        "properties": {
                            "stage_id": {"type": "string", "minLength": 1},
                            "predecessor_refs": string_array,
                            "evidence_kind": {"type": "string", "minLength": 1},
                        },
                    },
                },
                "ordering_rule": {"type": "string", "minLength": 1},
                "approval_boundary": {"type": "string", "minLength": 1},
            },
            ["stages", "ordering_rule", "approval_boundary"],
        ),
        "construction-binding": base_instance_schema(
            "Construction Binding v1",
            "cyberalchemy-lab-construction-binding/v1",
            "binding_id",
            "cal.artifact-type.construction-binding/v1",
            {
                "subject_ref": {"type": "string", "minLength": 1},
                "profile_ref": {"type": "string", "minLength": 1},
                "profile_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "stage_bindings": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["stage_id", "artifact_ref", "artifact_sha256", "state"],
                        "properties": {
                            "stage_id": {"type": "string", "minLength": 1},
                            "artifact_ref": {"type": "string", "minLength": 1},
                            "artifact_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                            "state": {"enum": ["planned", "prototype", "tested-product"]},
                        },
                    },
                },
            },
            ["subject_ref", "profile_ref", "profile_sha256", "stage_bindings"],
        ),
        "implementation-binding": base_instance_schema(
            "Implementation Binding v1",
            "cyberalchemy-lab-implementation-binding/v1",
            "binding_id",
            "cal.artifact-type.implementation-binding/v1",
            {
                "system_model_ref": {"type": "string", "minLength": 1},
                "system_model_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "implementation_targets": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["path", "obligation_refs"],
                        "properties": {
                            "path": {"type": "string", "minLength": 1},
                            "obligation_refs": string_array,
                        },
                    },
                },
            },
            ["system_model_ref", "system_model_sha256", "implementation_targets"],
        ),
        "evaluation": base_instance_schema(
            "Evaluation v1",
            "cyberalchemy-lab-evaluation/v1",
            "evaluation_id",
            "cal.artifact-type.evaluation/v1",
            {
                "profile_ref": {"type": "string", "minLength": 1},
                "profile_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "subject_ref": {"type": "string", "minLength": 1},
                "subject_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "outcomes": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["check_id", "result", "evidence_refs", "blockers"],
                        "properties": {
                            "check_id": {"type": "string", "minLength": 1},
                            "result": {"enum": ["PASS", "FAIL", "NOT_EVALUABLE"]},
                            "evidence_refs": string_array,
                            "blockers": string_array,
                        },
                    },
                },
                "aggregate_result": {"enum": ["PASS", "FAIL", "NOT_EVALUABLE"]},
            },
            ["profile_ref", "profile_sha256", "subject_ref", "subject_sha256", "outcomes", "aggregate_result"],
        ),
        "evaluation-profile": base_instance_schema(
            "Evaluation Profile v2",
            "cyberalchemy-lab-evaluation-profile/v2",
            "profile_id",
            "cal.artifact-type.evaluation-profile/v2",
            {
                "evaluation_kind": {"type": "string", "minLength": 1},
                "subject_artifact_type_refs": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"type": "string", "minLength": 1},
                },
                "outcomes": {
                    "const": ["PASS", "FAIL", "NOT_EVALUABLE"]
                },
                "evaluation_mode": {"const": "collect-all"},
                "checks": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["check_id", "purpose", "depends_on"],
                        "properties": {
                            "check_id": {"type": "string", "minLength": 1},
                            "purpose": {"type": "string", "minLength": 1},
                            "depends_on": string_array,
                        },
                    },
                },
                "decision_rule": {"type": "string", "minLength": 1},
            },
            ["evaluation_kind", "subject_artifact_type_refs", "outcomes", "evaluation_mode", "checks", "decision_rule"],
        ),
    }


def profile_records() -> dict[str, dict]:
    common = {
        "schema_version": "cyberalchemy-lab-evaluation-profile/v2",
        "artifact_type_ref": "cal.artifact-type.evaluation-profile/v2",
        "status": "candidate-unadmitted",
        "authority_effect": "none",
        "owner_ref": "role:evidence-conformance-owner",
        "outcomes": ["PASS", "FAIL", "NOT_EVALUABLE"],
        "evaluation_mode": "collect-all",
        "source_direction": {
            "canonical": "profile.json",
            "human_projection": "PROFILE.md",
            "projection_policy": "generated-only",
        },
    }
    return {
        "prototype-construction-evaluation": {
            **common,
            "profile_id": "profile.prototype-construction-evaluation",
            "evaluation_kind": "prototype-construction",
            "subject_artifact_type_refs": [
                "cal.artifact-type.construction-profile/v1",
                "cal.artifact-type.construction-binding/v1",
                "cal.artifact-type.implementation-binding/v1",
            ],
            "checks": [
                {"check_id": "PCE-01-SOURCES", "purpose": "Resolve exact source and planning-decision bindings.", "depends_on": []},
                {"check_id": "PCE-02-GRAPH", "purpose": "Validate stage identity, typed predecessors, and complete bindings.", "depends_on": ["PCE-01-SOURCES"]},
                {"check_id": "PCE-03-PROJECTIONS", "purpose": "Prove every human view is generated from its canonical machine record.", "depends_on": ["PCE-02-GRAPH"]},
                {"check_id": "PCE-04-AUTHORITY", "purpose": "Reject prototype artifacts or receipts that claim admission or operational authority.", "depends_on": []},
            ],
            "decision_rule": "PASS requires all independent checks PASS; dependency-blocked checks are NOT_EVALUABLE and never omitted.",
            "claim_ceiling": "This candidate profile evaluates prototype construction only. PASS cannot admit artifacts, approve a product, or authorize operation.",
        },
        "product-candidate-evaluation": {
            **common,
            "profile_id": "profile.product-candidate-evaluation",
            "evaluation_kind": "product-candidate",
            "subject_artifact_type_refs": [
                "cal.artifact-type.construction-binding/v1",
                "cal.artifact-type.evaluation/v1",
            ],
            "checks": [
                {"check_id": "PDE-01-FREEZE", "purpose": "Bind one exact product candidate and acceptance-bound byte set.", "depends_on": []},
                {"check_id": "PDE-02-TESTS", "purpose": "Require current complete product-test evidence for the frozen candidate.", "depends_on": ["PDE-01-FREEZE"]},
                {"check_id": "PDE-03-ELIGIBILITY", "purpose": "Determine product-approval request eligibility without granting approval.", "depends_on": ["PDE-02-TESTS"]},
                {"check_id": "PDE-04-SEPARATION", "purpose": "Keep product approval separate from later authority, admission, activation, and release decisions.", "depends_on": []},
            ],
            "decision_rule": "PASS establishes eligibility for a separate product decision only; it grants no approval or post-approval authority.",
            "claim_ceiling": "This candidate profile evaluates a frozen product candidate. PASS does not approve the product or authorize admission, activation, release, or deployment.",
        },
    }


def witness_records(profiles: dict[str, dict]) -> dict[str, dict]:
    zero = "0" * 64
    return {
        "construction-profile": {
            "schema_version": "cyberalchemy-lab-construction-profile/v1",
            "profile_id": "profile.d65-prototype-first-construction",
            "artifact_type_ref": "cal.artifact-type.construction-profile/v1",
            "status": "candidate-unadmitted",
            "authority_effect": "none",
            "owner_ref": "role:construction-profile-owner",
            "stages": [
                {"stage_id": "prototype-definitions", "predecessor_refs": [], "evidence_kind": "prototype"},
                {"stage_id": "ontology-scaffolds", "predecessor_refs": ["prototype-definitions"], "evidence_kind": "prototype"},
                {"stage_id": "product-prototypes", "predecessor_refs": ["ontology-scaffolds"], "evidence_kind": "prototype"},
                {"stage_id": "frozen-product-candidate", "predecessor_refs": ["product-prototypes"], "evidence_kind": "tested-product"},
                {"stage_id": "product-approval-eligibility", "predecessor_refs": ["frozen-product-candidate"], "evidence_kind": "decision-eligibility"},
            ],
            "ordering_rule": "Prototype stages may iterate; only one exact frozen product candidate crosses into current product testing.",
            "approval_boundary": "Product approval is separate from every authority, admission, activation, release, or deployment decision.",
            "source_direction": {"canonical": "profile.json", "human_projection": "PROFILE.md", "projection_policy": "generated-only"},
            "claim_ceiling": "Fixture proving the Construction Profile schema only; it creates no active workflow or authority.",
        },
        "construction-binding": {
            "schema_version": "cyberalchemy-lab-construction-binding/v1",
            "binding_id": "binding.fixture.d65-construction",
            "artifact_type_ref": "cal.artifact-type.construction-binding/v1",
            "status": "candidate-unadmitted",
            "authority_effect": "none",
            "owner_ref": "role:construction-binding-owner",
            "subject_ref": "product.fixture",
            "profile_ref": "profile.d65-prototype-first-construction",
            "profile_sha256": zero,
            "stage_bindings": [{"stage_id": "prototype-definitions", "artifact_ref": "fixture.definition", "artifact_sha256": zero, "state": "prototype"}],
            "source_direction": {"canonical": "binding.json", "human_projection": "BINDING.md", "projection_policy": "generated-only"},
            "claim_ceiling": "Fixture proving the Construction Binding schema only; it binds no live product or execution.",
        },
        "implementation-binding": {
            "schema_version": "cyberalchemy-lab-implementation-binding/v1",
            "binding_id": "binding.fixture.implementation",
            "artifact_type_ref": "cal.artifact-type.implementation-binding/v1",
            "status": "candidate-unadmitted",
            "authority_effect": "none",
            "owner_ref": "role:implementation-binding-owner",
            "system_model_ref": "system-model.fixture",
            "system_model_sha256": zero,
            "implementation_targets": [{"path": "src/lib.rs", "obligation_refs": ["obligation.fixture"]}],
            "source_direction": {"canonical": "binding.json", "human_projection": "BINDING.md", "projection_policy": "generated-only"},
            "claim_ceiling": "Fixture proving the Implementation Binding schema only; it proves no implementation or conformance.",
        },
        "evaluation": {
            "schema_version": "cyberalchemy-lab-evaluation/v1",
            "evaluation_id": "evaluation.fixture",
            "artifact_type_ref": "cal.artifact-type.evaluation/v1",
            "status": "candidate-unadmitted",
            "authority_effect": "none",
            "owner_ref": "role:evidence-conformance-owner",
            "profile_ref": "profile.fixture",
            "profile_sha256": zero,
            "subject_ref": "subject.fixture",
            "subject_sha256": zero,
            "outcomes": [{"check_id": "FIXTURE-01", "result": "NOT_EVALUABLE", "evidence_refs": [], "blockers": ["fixture-only"]}],
            "aggregate_result": "NOT_EVALUABLE",
            "source_direction": {"canonical": "evaluation.json", "human_projection": "EVALUATION.md", "projection_policy": "generated-only"},
            "claim_ceiling": "Fixture proving the Evaluation schema only; it is not current product evidence.",
        },
        "evaluation-profile": profiles["prototype-construction-evaluation"],
    }


def definition_record() -> dict:
    review = load(D65_REVIEW)
    definition_schema_sha = sha(DEFINITION_SCHEMA)
    generator_sha = sha(DEFINITION_GENERATOR)
    return {
        "schema_version": "cyberalchemy-lab-definition/v1",
        "definition_id": "cal.definition.prototype-first-domainspec-construction-invariant",
        "version": "1.0.0-candidate.1",
        "term": "Prototype-First DomainSpec Construction Invariant",
        "aliases": ["D65 prototype-first construction invariant"],
        "classification": {
            "artifact_type_ref": "cal.artifact-type.definition/v1",
            "semantic_kind": "definition",
            "authority_kind": "semantic-authority",
            "lifecycle_posture_ref": "candidate:d65-reconstruction-pipeline/v1",
        },
        "semantic_owner_ref": "role:definition-owner",
        "scope": {
            "authority_scope_ref": "scope:construction",
            "applicability": "Construction of a new or materially revised implementation-bearing system or capability in CyberAlchemy-lab.",
            "exclusions": [
                "Purely narrative edits with no implementation-bearing system change.",
                "Admission, activation, publication, release, deployment, or external-effect decisions.",
            ],
        },
        "voices": {
            "scientific_formal": {
                "normative_statement": "An implementation-bearing construction must begin with prototype definitions, use ontology only as non-authoritative navigation scaffolding, iterate product and implementation prototypes, freeze one exact product candidate, obtain current product-test evidence, and become eligible for product approval before any separate authority request. Product approval grants no operational authority.",
                "formal_expression": "D -> O_s -> P* -> freeze(P_c@h) -> test(P_c@h) -> eligible(product_approval) -> decision(product_approval) -> eligible(separate_authority_request); O_s.authority=none; product_approval =/=> operational_authority",
                "notation": [
                    {"symbol": "D", "meaning": "Prototype definitions."},
                    {"symbol": "O_s", "meaning": "Agent-facing, non-authoritative ontology scaffolds."},
                    {"symbol": "P*", "meaning": "Iterative product, business, DomainSpec, compiled-system, and implementation prototypes."},
                    {"symbol": "P_c@h", "meaning": "One frozen product candidate bound to exact digest h."},
                ],
                "boundary_conditions": [
                    "Prototype epochs may iterate without admission requests.",
                    "Testing binds one exact frozen candidate.",
                    "Changed acceptance-bound bytes require a new test and approval epoch.",
                    "Authority decisions occur only after product approval and remain separate.",
                ],
                "testable_conditions": [
                    "Every construction stage has an explicit typed carrier.",
                    "Ontology scaffolds declare authority_effect none.",
                    "Product-test evidence binds the frozen candidate digest.",
                    "No authority request precedes exact product approval evidence.",
                ],
            },
            "plain_language": {
                "normative": False,
                "explanation": "First learn with explicit prototypes. Freeze and test one exact product only when the model is coherent. Product approval may then be considered, while every real-world authority decision remains separate.",
            },
            "domain_context": {
                "normative": False,
                "workspace_ref": str(LAB),
                "explanation": "The CyberAlchemy-v2 reconstruction uses this invariant to turn reviewed source meanings into candidate Lab artifacts without copying source structure or treating tests as admission.",
                "examples": [
                    "The 176 migration scaffolds remain prototypes until family schemas and tests exist.",
                    "The D65 vertical tests one Definition, Artifact Types, and profiles before wider reconstruction.",
                ],
            },
        },
        "boundaries": [
            "Construction Profile defines stages; it is not the invariant itself.",
            "Construction Binding binds an exact subject to a construction graph; it is not an implementation binding.",
            "Implementation Binding maps a system model to implementation targets; it does not prove implementation conformance.",
            "Evaluation Profile defines checks; Evaluation records results.",
        ],
        "source_refs": [
            {
                "source_ref": "cyberalchemy-v2:CAV2-D65",
                "selector": review["current_source_ref"]["heading"],
                "content_sha256": review["current_source_ref"]["raw_section_sha256"],
                "admission_posture": "candidate-unadmitted",
                "source_admission_ref": None,
            }
        ],
        "primary_consumer_refs": [
            "cal.artifact-type.construction-profile/v1",
            "cal.artifact-type.construction-binding/v1",
            "cal.artifact-type.implementation-binding/v1",
            "profile.prototype-construction-evaluation",
            "profile.product-candidate-evaluation",
        ],
        "index_entry": {
            "index_ref": rel(ROOT / "registry.json"),
            "entry_id": "cal.definition.prototype-first-domainspec-construction-invariant@1.0.0-candidate.1",
        },
        "drift_route": {
            "owner_ref": "role:definition-owner",
            "audit_ref": rel(ROOT / "drift-audit.json"),
            "challenge_ref": "CA2-ROUTE-DEFINITIONS",
        },
        "source_direction": {
            "canonical": "definition.json",
            "human_projection": "DEFINITION.md",
            "projection_policy": "generated-only",
            "generator_ref": "cal.generator.definition-markdown/v1",
            "generator_sha256": generator_sha,
        },
        "schema_ref": "cal.schema.definition/v1",
        "schema_digest": definition_schema_sha,
        "evidence_refs": [rel(DECISION), rel(ROOT / "receipts/validation.json")],
        "residue_refs": [rel(ROOT / "drift-audit.json")],
        "typed_relations": [],
        "claim_ceiling": "Candidate Definition reconstructed from the selected D65 planning successor. It does not alter CyberAlchemy-v2, enter the admitted Lab Definition registry, activate construction policy, or authorize implementation or migration.",
    }


def artifact_type_record(
    key: str,
    schema: dict,
    definition: dict,
    positive_path: str,
    positive_projection: str,
) -> dict:
    configs = {
        "construction-profile": ("Construction Profile", "construction-profile", "Defines stage vocabulary and predecessor rules without carrying execution state."),
        "construction-binding": ("Construction Binding", "construction-binding", "Binds one subject and epoch to an exact construction dependency graph without becoming an implementation binding."),
        "implementation-binding": ("Implementation Binding", "implementation-binding", "Maps one exact system model to implementation targets and obligations without claiming implementation conformance."),
        "evaluation": ("Evaluation", "evaluation", "Records complete bounded results under an exact evaluation profile without granting admission or authority."),
        "evaluation-profile": ("Evaluation Profile", "evaluation-profile", "Defines reusable collect-all check semantics for arbitrary declared subject Artifact Types without becoming an Evaluation result."),
    }
    name, semantic_kind, purpose = configs[key]
    version = "2.0.0-candidate.1" if key == "evaluation-profile" else "1.0.0-candidate.1"
    type_ref = f"cal.artifact-type.{key}/{'v2' if key == 'evaluation-profile' else 'v1'}"
    schema_ref = f"cal.schema.{key}/{'v2' if key == 'evaluation-profile' else 'v1'}"
    if key in {"evaluation", "evaluation-profile"}:
        entry = next(
            item for item in load(DEFINITION_REGISTRY)["entries"]
            if item["definition_id"] == "cal.definition.evaluation"
            and item["lifecycle_state"] == "admitted"
        )
        refs = [f'{entry["definition_id"]}@{entry["version"]}']
        bindings = [{
            "definition_ref": refs[0],
            "path": entry["path"],
            "sha256": entry["sha256"],
            "admission_posture": "admitted",
        }]
    else:
        refs = [f'{definition["definition_id"]}@{definition["version"]}']
        definition_path = ROOT / "definitions/prototype-first-domainspec-construction-invariant/v1/definition.json"
        bindings = [{
            "definition_ref": refs[0],
            "path": rel(definition_path),
            "sha256": sha(definition_path),
            "admission_posture": "candidate-unadmitted",
        }]
    root_decision = load(ARTIFACT_TYPE_DECISION)
    return {
        "schema_version": "cyberalchemy-lab-artifact-type-candidate/v2",
        "artifact_type_id": f"cal.artifact-type.{key}",
        "artifact_type_ref": type_ref,
        "version": version,
        "name": name,
        "status": "candidate-unadmitted",
        "authority_effect": "none",
        "classification": {
            "artifact_type_ref": "cal.artifact-type.artifact-type/v2",
            "semantic_kind": semantic_kind,
            "authority_kind": "none",
            "lifecycle_posture_ref": "candidate:d65-reconstruction-pipeline/v1",
        },
        "artifact_type_root_binding": {
            "path": rel(ARTIFACT_TYPE_ROOT),
            "sha256": sha(ARTIFACT_TYPE_ROOT),
            "admission_decision_ref": root_decision["decision_id"],
        },
        "semantic_owner_ref": "role:artifact-type-owner",
        "semantic_definition_refs": refs,
        "semantic_definition_bindings": bindings,
        "schema_ref": schema_ref,
        "schema_digest": hashlib.sha256(canonical_bytes(schema)).hexdigest(),
        "instance_contract": {
            "canonical_filename": Path(positive_path).name,
            "human_filename": Path(positive_projection).name,
            "identity_field": {
                "construction-profile": "profile_id",
                "construction-binding": "binding_id",
                "implementation-binding": "binding_id",
                "evaluation": "evaluation_id",
                "evaluation-profile": "profile_id",
            }[key],
            "closed_representation": True,
            "required_semantic_fields": sorted(
                set(schema["required"])
                - {"schema_version", "status", "authority_effect", "source_direction", "claim_ceiling"}
            ),
            "forbidden_canonical_fields": ["implicit_admission", "directory_inference", "derived_authority"],
        },
        "distinct_validation_purpose": purpose,
        "orthogonality_rules": [
            {"rule_id": f"D65-{key.upper()}-01", "statement": "Semantic identity, Artifact Type, lifecycle state, evaluation result, and authority remain separate axes."},
            {"rule_id": f"D65-{key.upper()}-02", "statement": purpose},
        ],
        "source_direction": {
            "canonical": "artifact.json",
            "human_projection": "ARTIFACT.md",
            "projection_policy": "generated-only",
            "shared_generator_path": rel(ARTIFACT_GENERATOR),
            "shared_generator_sha256": sha(ARTIFACT_GENERATOR),
        },
        "four_facets": {
            "classification": f"Candidate {semantic_kind} described by Artifact Type/v2.",
            "schema": "schema.json is a closed candidate instance contract.",
            "human_continuation": f"{Path(positive_projection).name} and ARTIFACT.md are generated from canonical JSON.",
            "machine_checkable": "Schema closure, semantic bindings, hostile fixtures, source digests, and projection parity are executable.",
        },
        "validation_contract": {
            "validator_path": rel(ROOT / "validate.py"),
            "shared_validator_path": rel(ARTIFACT_VALIDATOR),
            "shared_validator_sha256": sha(ARTIFACT_VALIDATOR),
            "positive_witness": positive_path,
            "positive_projection": positive_projection,
            "negative_witnesses": ["fixtures/invalid/additional-property.json", "fixtures/invalid/authority-effect.json"],
            "assessment_scope": "schema-and-artifact-type-contract",
            "admission_effect": "none",
        },
        "typed_residue": [
            {
                "residue_id": f"D65-{key.upper()}-R1",
                "missing": "No Artifact Type admission decision exists for this exact candidate.",
                "owner_ref": "role:artifact-type-owner",
                "consequence": "The type and its instances remain candidate-only.",
            }
        ],
        "claim_ceiling": f"Candidate {name} contract and fixtures only. PASS does not admit the type, register it as current, or authorize any instance or runtime.",
    }


def render_plan(plan: dict) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is implementation-layering.json. -->", "", "# Artifact Reconstruction Pipeline Implementation Layering", ""]
    for layer in plan["layers"]:
        lines += [f'## {layer["layer_id"]}: {layer["name"]}', "", f'**Decision:** {layer["decision_question"]}', "", f'**Minimum working unit:** {layer["minimum_working_unit"]}', "", f'**Exit evidence:** {", ".join(layer["exit_evidence"])}', ""]
    lines += ["## Boundary", "", plan["claim_ceiling"], ""]
    return "\n".join(lines)


def render_candidate(candidate: dict) -> str:
    return f'''<!-- GENERATED FILE: canonical data is candidate.json. -->

# Artifact Reconstruction Pipeline D65 Vertical

- Candidate: `{candidate["candidate_id"]}`
- Status: `{candidate["status"]}`
- Normalized targets: `{candidate["target_counts"]["normalized"]}`
- Supporting artifacts: `{candidate["target_counts"]["supporting"]}`
- Authority effect: `{candidate["authority_effect"]}`

## Product-construction frontier

{candidate["product_construction"]["frontier"]}

## Operational residue

{candidate["operational_support"][0]["task"]} This does not block the candidate test.

## Claim ceiling

{candidate["claim_ceiling"]}
'''


def render_registry(registry: dict) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is registry.json. -->", "", "# D65 Reconstruction Candidate Registry", "", f'- Entries: `{len(registry["entries"])}`', "", "| Target | Family | State | Proposed home |", "|---|---|---|---|"]
    for item in registry["entries"]:
        lines.append(f'| `{item["target_id"]}` | `{item["family"]}` | `{item["status"]}` | `{item["proposed_home"]}` |')
    lines += ["", "## Claim ceiling", "", registry["claim_ceiling"], ""]
    return "\n".join(lines)


def render_relations(relations: dict) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is relations.json. -->", "", "# Reused D65 Relations", "", "No relation kind is minted by this candidate.", ""]
    lines.extend(f'- `{item["relation_id"]}` — `{item["posture"]}`' for item in relations["relations"])
    lines += ["", relations["claim_ceiling"], ""]
    return "\n".join(lines)


def render_drift(audit: dict) -> str:
    return f'''<!-- GENERATED FILE: canonical data is drift-audit.json. -->

# D65 Definition Drift Audit

- Result: `{audit["result"]}`
- Selected section current: `{str(audit["selected_source_current"]).lower()}`
- Conflicting consumers: `{audit["conflicting_consumer_count"]}`
- Authority effect: `{audit["authority_effect"]}`

{audit["claim_ceiling"]}
'''


def render_manifest(manifest: dict) -> str:
    return f'''<!-- GENERATED FILE: canonical data is manifest.json. -->

# Artifact Reconstruction Pipeline Manifest

- Materials: `{len(manifest["materials"])}`
- Source bindings: `{len(manifest["source_bindings"])}`
- Authority effect: `{manifest["authority_effect"]}`

{manifest["claim_ceiling"]}
'''


def main() -> None:
    artifact_renderer = module(ARTIFACT_GENERATOR, "artifact_surface_generator")
    definition_renderer = module(DEFINITION_GENERATOR, "definition_generator")
    selected_decision = load(DECISION)
    d65 = load(D65)
    if selected_decision["status"] != "selected-planning-baseline":
        raise ValueError("reconstruction planning baseline is not selected")

    plan = {
        "schema_version": "cyberalchemy-lab-implementation-layering/v1",
        "target": "Artifact Reconstruction Pipeline",
        "mode": "created",
        "owner_ref": "role:repository-migration-owner",
        "boundary_heuristic": "Each layer ends at the smallest slice that unlocks a new responsible decision with current evidence.",
        "layers": [
            {"layer_id": "L0", "name": "D65 dependency-closed vertical", "decision_question": "After this layer, we know whether existing Lab artifact mechanics can reconstruct one cross-family normalized slice without identity or authority collapse.", "minimum_working_unit": "One D65 Definition, five Artifact Types, two evaluation profiles, reused relations, hostile fixtures, and exact source bindings.", "included_scope": ["seven normalized target identities", "one Evaluation Profile successor", "candidate registry", "deterministic projections", "collect-all validation"], "deferred_scope": ["remaining target families", "context reconstruction", "admission", "runtime activation"], "exit_evidence": ["receipts/validation.json", "manifest.json"], "promotion_decision": "Continue to L1 only on deterministic PASS with no source drift."},
            {"layer_id": "L1", "name": "Semantic-family repeatability", "decision_question": "After this layer, we know whether candidate Definition reconstruction is repeatable across the remaining semantic targets.", "minimum_working_unit": "Batch-independent Definition candidates with voice, source, index, and drift closure.", "included_scope": ["remaining semantic targets"], "deferred_scope": ["admission", "non-semantic families"], "exit_evidence": ["family conformance receipt", "drift audit"], "promotion_decision": "Continue when every semantic candidate is independently reproducible."},
            {"layer_id": "L2", "name": "Cross-family reconstruction", "decision_question": "After this layer, we know whether Artifact Types, profiles, relation kinds, and derived surfaces can be reconstructed without redundant canonical axes.", "minimum_working_unit": "Family-specific schemas and dependency-ordered target batches.", "included_scope": ["artifact-type", "profile", "relation-kind", "derived-surface"], "deferred_scope": ["context activation", "migration execution"], "exit_evidence": ["cross-family conformance receipt"], "promotion_decision": "Continue when all 195 target identities have explicit realization evidence or typed residue."},
            {"layer_id": "L3", "name": "Context reconstruction and recovery", "decision_question": "After this layer, we know whether approved ontology routes can form bounded contexts that evolve and recover without losing source lineage.", "minimum_working_unit": "One context vertical with map, bindings, evolution, rollback, and recovery tests.", "included_scope": ["bounded contexts", "context maps", "runtime bindings", "recovery evidence"], "deferred_scope": ["admission", "activation", "publication"], "exit_evidence": ["context product-test receipt"], "promotion_decision": "Prepare one product candidate for review; do not infer admission."},
        ],
        "non_regression": ["machine JSON remains canonical", "human Markdown remains generated", "directory placement never establishes type or authority", "validation never grants admission", "source and target identities remain distinct"],
        "claim_ceiling": "This implementation layering guides candidate construction only. It is not an execution registry, admission decision, activation plan, or migration authority.",
    }
    dump(ROOT / "implementation-layering.json", plan)
    (ROOT / "IMPLEMENTATION-LAYERING.md").write_text(render_plan(plan), encoding="utf-8")

    definition = definition_record()
    definition_path = ROOT / "definitions/prototype-first-domainspec-construction-invariant/v1/definition.json"
    dump(definition_path, definition)
    (definition_path.parent / "DEFINITION.md").write_text(definition_renderer.render(definition), encoding="utf-8")

    profile_data = profile_records()
    type_schemas = schemas()
    witnesses = witness_records(profile_data)
    types = {}
    for key, schema in type_schemas.items():
        type_root = ROOT / "artifact-types" / key / ("v2" if key == "evaluation-profile" else "v1")
        dump(type_root / "schema.json", schema)
        if key == "evaluation-profile":
            profile_root = ROOT / "profiles/prototype-construction-evaluation/v1"
            positive_path = "../../../profiles/prototype-construction-evaluation/v1/profile.json"
            positive_projection = "../../../profiles/prototype-construction-evaluation/v1/PROFILE.md"
        else:
            fixture_name = {
                "construction-profile": "profile.json",
                "construction-binding": "binding.json",
                "implementation-binding": "binding.json",
                "evaluation": "evaluation.json",
            }[key]
            positive_path = f"fixtures/valid/{fixture_name}"
            positive_projection = f"fixtures/valid/{Path(fixture_name).stem.upper()}.md"
        artifact = artifact_type_record(key, schema, definition, positive_path, positive_projection)
        dump(type_root / "artifact.json", artifact)
        artifact = load(type_root / "artifact.json")
        (type_root / "ARTIFACT.md").write_text(artifact_renderer.render_artifact(artifact), encoding="utf-8")
        if key != "evaluation-profile":
            witness_path = type_root / positive_path
            dump(witness_path, witnesses[key])
            witness = load(witness_path)
            (type_root / positive_projection).write_text(artifact_renderer.render_instance(artifact, witness), encoding="utf-8")
        invalid_extra = dict(witnesses[key]); invalid_extra["unexpected"] = True
        invalid_authority = dict(witnesses[key]); invalid_authority["authority_effect"] = "admission"
        dump(type_root / "fixtures/invalid/additional-property.json", invalid_extra)
        dump(type_root / "fixtures/invalid/authority-effect.json", invalid_authority)
        types[key] = {"root": type_root, "artifact": artifact, "schema": schema}

    evaluation_profile_artifact = types["evaluation-profile"]["artifact"]
    for key, profile in profile_data.items():
        profile_root = ROOT / "profiles" / key / "v1"
        dump(profile_root / "profile.json", profile)
        profile = load(profile_root / "profile.json")
        (profile_root / "PROFILE.md").write_text(artifact_renderer.render_instance(evaluation_profile_artifact, profile), encoding="utf-8")

    normalized_targets = [
        "semantic.prototype-first-domainspec-construction-invariant",
        "type.construction-profile",
        "type.construction-binding",
        "type.implementation-binding",
        "type.evaluation",
        "profile.prototype-construction-evaluation",
        "profile.product-candidate-evaluation",
    ]
    proposed = {
        "semantic.prototype-first-domainspec-construction-invariant": ("definition", definition_path, "authority/definitions/prototype-first-domainspec-construction-invariant/v1/definition.json"),
        "type.construction-profile": ("artifact-type", types["construction-profile"]["root"] / "artifact.json", "authority/artifact-types/construction-profile/v1/artifact.json"),
        "type.construction-binding": ("artifact-type", types["construction-binding"]["root"] / "artifact.json", "authority/artifact-types/construction-binding/v1/artifact.json"),
        "type.implementation-binding": ("artifact-type", types["implementation-binding"]["root"] / "artifact.json", "authority/artifact-types/implementation-binding/v1/artifact.json"),
        "type.evaluation": ("artifact-type", types["evaluation"]["root"] / "artifact.json", "authority/artifact-types/evaluation/v1/artifact.json"),
        "profile.prototype-construction-evaluation": ("profile", ROOT / "profiles/prototype-construction-evaluation/v1/profile.json", "authority/profiles/prototype-construction-evaluation/v1/profile.json"),
        "profile.product-candidate-evaluation": ("profile", ROOT / "profiles/product-candidate-evaluation/v1/profile.json", "authority/profiles/product-candidate-evaluation/v1/profile.json"),
        "support.evaluation-profile-v2": ("artifact-type-successor", types["evaluation-profile"]["root"] / "artifact.json", "authority/artifact-types/evaluation-profile/v2/artifact.json"),
    }
    registry_entries = []
    for target_id, (family, path, home) in proposed.items():
        registry_entries.append({"target_id": target_id, "normalized_target": target_id in normalized_targets, "family": family, "candidate_path": rel(path), "candidate_sha256": sha(path), "proposed_home": home, "predecessor_ref": "cal.artifact-type.evaluation-profile/v1" if target_id == "support.evaluation-profile-v2" else None, "status": "candidate-unadmitted", "authority_effect": "none"})
    registry = {
        "schema_version": "cyberalchemy-lab-reconstruction-candidate-registry/v1",
        "registry_id": "CAL-D65-RECONSTRUCTION-VERTICAL-REGISTRY-0001",
        "entries": registry_entries,
        "normalized_target_count": 7,
        "supporting_artifact_count": 1,
        "source_direction": {"canonical": "registry.json", "human_projection": "REGISTRY.md", "projection_policy": "generated-only"},
        "authority_effect": "none",
        "claim_ceiling": "Candidate registry for this reconstruction vertical only. It is not the live Artifact Type or Definition registry and cannot admit or resolve repository artifacts.",
    }
    dump(ROOT / "registry.json", registry)
    (ROOT / "REGISTRY.md").write_text(render_registry(registry), encoding="utf-8")

    relations = {
        "schema_version": "cyberalchemy-lab-reused-relation-set/v1",
        "set_id": "CAL-D65-REUSED-RELATIONS-0001",
        "relations": [{"relation_id": item, "posture": "reuse-normalized-identity-no-new-axis"} for item in d65["reused_normalized_relations"]],
        "source_ref": rel(D65),
        "authority_effect": "none",
        "claim_ceiling": "This set references selected normalized relation identities. It does not define, admit, or apply a relation instance.",
    }
    dump(ROOT / "relations.json", relations)
    (ROOT / "RELATIONS.md").write_text(render_relations(relations), encoding="utf-8")

    drift = {
        "schema_version": "cyberalchemy-lab-definition-drift-audit/v1-candidate",
        "audit_id": "CAL-D65-RECONSTRUCTION-DRIFT-0001",
        "result": "CANDIDATE",
        "definition_id": definition["definition_id"],
        "selected_source": definition["source_refs"][0],
        "selected_source_current": hashlib.sha256(
            markdown_h2_section(
                CAV2_DEFINITIONS, definition["source_refs"][0]["selector"]
            )
        ).hexdigest()
        == definition["source_refs"][0]["content_sha256"],
        "conflicting_consumer_count": 0,
        "findings": [],
        "authority_effect": "none",
        "claim_ceiling": "Candidate-local drift audit only. It does not update the admitted Definition registry or settle future source changes.",
    }
    dump(ROOT / "drift-audit.json", drift)
    (ROOT / "DRIFT-AUDIT.md").write_text(render_drift(drift), encoding="utf-8")

    candidate = {
        "schema_version": "cyberalchemy-lab-artifact-reconstruction-pipeline-candidate/v1",
        "candidate_id": "CAL-ARTIFACT-RECONSTRUCTION-PIPELINE-D65-0001",
        "status": "prototype-construction-candidate",
        "predecessor_decision": {"path": rel(DECISION), "sha256": sha(DECISION), "decision_id": selected_decision["decision_id"]},
        "target_counts": {"normalized": 7, "d65_selected": 6, "dependency_from_approved_backlog": 1, "supporting": 1, "total_artifacts": 8},
        "product_construction": {"frontier": "Test whether existing Lab artifact mechanics can reconstruct the dependency-closed D65 vertical without type, lifecycle, profile/result, or authority collapse.", "runnable_now": ["deterministic-authoring", "schema-validation", "hostile-fixture-validation", "projection-parity", "source-currentness"], "causal_blockers": []},
        "operational_support": [{"task": "Commit, push, admission, registry activation, migration execution, and source retirement require separate routes and decisions.", "owner": "role:repository-migration-owner", "affected_stage": None, "state": "deferred", "blocks_frontier": False}],
        "dependency_resolution": {"evaluation_target": "type.evaluation", "profile_carrier": "cal.artifact-type.evaluation-profile/v2", "reason": "Evaluation results and Evaluation Profiles have distinct schemas and validation purposes; the admitted v1 profile schema is Definition-specific."},
        "canonical_machine_artifacts": ["candidate.json", "implementation-layering.json", "registry.json", "relations.json", "drift-audit.json", "manifest.json", "receipts/validation.json"],
        "generated_human_projections": ["CANDIDATE.md", "IMPLEMENTATION-LAYERING.md", "REGISTRY.md", "RELATIONS.md", "DRIFT-AUDIT.md", "MANIFEST.md", "receipts/VALIDATION.md"],
        "authority_effect": "none",
        "claim_ceiling": "This exact candidate proves only a testable reconstruction vertical. It does not admit or install the Definition, Artifact Types, profiles, relations, registry, or pipeline; it does not execute migration, activate a runtime, commit, push, publish, release, or deploy.",
    }
    dump(ROOT / "candidate.json", candidate)
    (ROOT / "CANDIDATE.md").write_text(render_candidate(candidate), encoding="utf-8")

    material_paths = [path for path in ROOT.rglob("*") if path.is_file() and path.name not in {"manifest.json", "MANIFEST.md", "validation.json", "VALIDATION.md"} and "receipts" not in path.parts]
    source_paths = [DECISION, D65, D65_REVIEW, TARGET_INDEX, DEFINITION_SCHEMA, DEFINITION_GENERATOR, ARTIFACT_TYPE_ROOT, ARTIFACT_TYPE_DECISION, ARTIFACT_GENERATOR, ARTIFACT_VALIDATOR, DEFINITION_REGISTRY]
    manifest = {
        "schema_version": "cyberalchemy-lab-artifact-reconstruction-manifest/v1",
        "manifest_id": "CAL-ARTIFACT-RECONSTRUCTION-PIPELINE-MANIFEST-0001",
        "materials": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for path in sorted(material_paths)],
        "source_bindings": [source_binding(path) for path in source_paths]
        + [source_binding(CAV2_DEFINITIONS, "cyberalchemy-v2-source")],
        "authority_effect": "none",
        "claim_ceiling": "This manifest binds candidate and source bytes only. It grants no admission, activation, migration, publication, release, or deployment authority.",
    }
    dump(ROOT / "manifest.json", manifest)
    (ROOT / "MANIFEST.md").write_text(render_manifest(manifest), encoding="utf-8")


if __name__ == "__main__":
    main()
