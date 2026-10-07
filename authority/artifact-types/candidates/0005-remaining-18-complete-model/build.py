#!/usr/bin/env python3
"""Build the single review surface for the remaining 18 Artifact Types."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
MATERIALIZATION = LAB / "authority/artifact-types/candidates/0004-remaining-26-materialization"
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
RELATION_CONTRACT_REGISTRY = LAB / "authority/decisions/migration-contracts/v1/registry.json"
AXIS_RELATION_MODEL = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
AXIS_RELATION_RECEIPT = LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/receipts/validation.json"

ORDER = [
    "finding",
    "measurement-method", "measurement-result", "observation", "experiment-design", "experiment-run",
    "ontology",
    "context-profile", "context", "context-request", "context-view",
    "model-instance-binding",
    "person-reference", "identity-claim", "role", "team", "team-membership", "role-assignment",
]

FAMILIES = {
    "finding": "research conclusion",
    "measurement-method": "empirical work", "measurement-result": "empirical work", "observation": "empirical work",
    "experiment-design": "empirical work", "experiment-run": "empirical work",
    "ontology": "knowledge model",
    "context-profile": "context resolution", "context": "context resolution", "context-request": "context resolution", "context-view": "context resolution",
    "model-instance-binding": "model authority",
    "person-reference": "people and teams", "identity-claim": "people and teams", "role": "people and teams",
    "team": "people and teams", "team-membership": "people and teams", "role-assignment": "people and teams",
}

DEPENDENCIES = {
    "finding": ["cal.artifact-type.research-inquiry/v1", "cal.artifact-type.research-run/v1"],
    "measurement-method": [],
    "measurement-result": ["cal.artifact-type.measurement-method/v1"],
    "observation": ["cal.artifact-type.research-run/v1 or cal.artifact-type.experiment-run/v1"],
    "experiment-design": ["cal.artifact-type.project-identity/v1", "cal.artifact-type.research-inquiry/v1 (optional research framing)", "Product Identity, Product Thesis, Product Capability, and Capability Realization Binding (optional product evaluation)", "cal.artifact-type.measurement-method/v1"],
    "experiment-run": ["cal.artifact-type.experiment-design/v1", "cal.artifact-type.observation/v1", "cal.artifact-type.measurement-result/v1"],
    "ontology": [],
    "context-profile": [],
    "context": ["cal.artifact-type.product-identity/v2", "cal.artifact-type.project-identity/v1", "cal.artifact-type.context-profile/v1"],
    "context-request": ["cal.artifact-type.context/v1"],
    "context-view": ["cal.artifact-type.context/v1", "cal.artifact-type.context-request/v1"],
    "model-instance-binding": [],
    "person-reference": [],
    "identity-claim": ["cal.artifact-type.person-reference/v1"],
    "role": [],
    "team": ["cal.artifact-type.team-membership/v1", "cal.artifact-type.role-assignment/v1"],
    "team-membership": ["cal.artifact-type.person-reference/v1", "cal.artifact-type.team/v1"],
    "role-assignment": ["cal.artifact-type.person-reference/v1 or cal.artifact-type.team/v1", "cal.artifact-type.role/v1"],
}

OVERLAPS = [
    {
        "candidate_ref": "cal.artifact-type.context-profile/v1",
        "adjacent_ref": "cal.artifact-type.context/v1",
        "disposition": "specialized-policy-carrier",
        "boundary": "Context Profile carries reusable construction and resolution policy derived from the admitted Context contract. It has no Product, Project, Goal, purpose-bound Context identity, or resolved source selection and cannot validate as a Context instance.",
    },
    {
        "candidate_ref": "cal.artifact-type.context/v1",
        "adjacent_ref": "cal.artifact-type.bounded-context/v2",
        "disposition": "distinct",
        "boundary": "Context defines a purpose-specific relevance and interpretation boundary anchored to Product and optionally Project or Goal. Bounded Context defines a semantic ownership boundary for a domain model.",
    },
    {
        "candidate_ref": "cal.artifact-type.experiment-run/v1",
        "adjacent_ref": "cal.artifact-type.research-run/v1",
        "disposition": "distinct",
        "boundary": "Experiment Run executes a predeclared controlled design with variables or interventions. Research Run executes a bounded inquiry method and may be observational or analytical without an Experiment Design.",
    },
    {
        "candidate_ref": "cal.artifact-type.model-instance-binding/v1",
        "adjacent_ref": "cal.artifact-type.capability-realization-binding/v1",
        "disposition": "distinct",
        "boundary": "Model Instance Binding is the generic parent-to-instance authority separation contract. Capability Realization Binding is the Product Capability-specific relation with adoption and realization evidence semantics.",
    },
    {
        "candidate_ref": "cal.artifact-type.ontology/v1",
        "adjacent_ref": "cal.artifact-type.ontology-package/v1",
        "disposition": "distinct",
        "boundary": "Ontology carries governed typed knowledge and relations. Ontology Package is a packaging carrier and does not replace the Ontology semantic identity.",
    },
]

EXPERIMENT_RELATIONS = [
    {"source": "Experiment Design", "relation": "belongs-to-project", "target": "Project Identity", "carrier": "project_ref", "relation_kind_state": "migration-contract-only"},
    {"source": "Experiment Design", "relation": "advances-goal", "target": "Goal", "carrier": "goal_refs", "relation_kind_state": "exact-kind-missing"},
    {"source": "Experiment Design", "relation": "tests-question-from", "target": "Research Inquiry", "carrier": "research_refs", "relation_kind_state": "exact-kind-missing"},
    {"source": "Experiment Design", "relation": "evaluates-product-context", "target": "Product, Product Thesis outcome, Product Capability, or realization binding", "carrier": "product_evaluation_context", "relation_kind_state": "exact-kind-missing"},
    {"source": "Experiment Design", "relation": "uses-method", "target": "Protocol and Measurement Method", "carrier": "protocol_ref and measure_refs", "relation_kind_state": "migration-contract-only"},
    {"source": "Experiment Run", "relation": "executes-design", "target": "Experiment Design", "carrier": "design_ref and design_version_ref", "relation_kind_state": "exact-kind-missing"},
    {"source": "Experiment Run", "relation": "preserves-research-trace", "target": "Research Inquiry", "carrier": "research_refs", "relation_kind_state": "exact-kind-missing"},
    {"source": "Experiment Run", "relation": "preserves-product-evaluation-context", "target": "Product, Product Thesis outcome, Product Capability, or realization binding", "carrier": "product_evaluation_context", "relation_kind_state": "exact-kind-missing"},
    {"source": "Experiment Run", "relation": "produces-observation", "target": "Observation", "carrier": "observation_refs and Observation.run_ref", "relation_kind_state": "exact-kind-missing"},
    {"source": "Experiment Run", "relation": "produces-measurement", "target": "Measurement Result", "carrier": "measurement_result_refs", "relation_kind_state": "exact-kind-missing"},
    {"source": "Experiment Run", "relation": "produces-evidence", "target": "Evidence Set", "carrier": "evidence_set_ref", "relation_kind_state": "exact-kind-missing"},
    {"source": "Observation", "relation": "derives-from", "target": "Experiment Run or Research Run", "carrier": "run_ref", "relation_kind_state": "migration-contract-only"},
    {"source": "Measurement Result", "relation": "uses-method", "target": "Measurement Method", "carrier": "method_ref", "relation_kind_state": "migration-contract-only"},
    {"source": "Finding", "relation": "derives-from", "target": "Research Run or Evidence Set", "carrier": "research_run_refs and evidence_set_refs", "relation_kind_state": "migration-contract-only"},
    {"source": "Evidence", "relation": "supports or contradicts", "target": "Finding", "carrier": "evidence_refs and counterevidence_refs", "relation_kind_state": "migration-contract-only"},
]

RELATION_ENDPOINT_GAPS = [
    {"relation": "belongs-to-product", "current_sources": ["product-capability", "product-thesis"], "missing_sources": ["context"], "reason": "Context is anchored to one Product. Experiments should use evaluates rather than claiming Product membership."},
    {"relation": "belongs-to-project", "current_sources": ["research-inquiry", "experiment-design", "goal", "work", "evidence-set", "capability-realization-binding"], "missing_sources": ["context", "experiment-run", "research-run"], "reason": "These carriers preserve Project scope, but the admitted migration contract does not accept their source kinds."},
    {"relation": "uses-method", "current_sources": ["research-run", "experiment-run"], "missing_sources": ["measurement-result", "observation", "project", "product"], "reason": "Empirical records and the existing Identity Graph fixture carry Method links, but the current endpoint contract only types run-to-method edges."},
    {"relation": "evaluates", "current_sources": ["evaluation"], "missing_sources": ["experiment-design", "experiment-run"], "reason": "An Experiment can evaluate declared Product anchors, but it is not an Evaluation artifact under the current contract."},
    {"relation": "instance-of", "current_sources": ["implementation", "product-capability"], "missing_sources": ["capability-instance"], "reason": "The instance is the source endpoint; Model Instance Binding remains the lifecycle-bearing relation record."},
]

MISSING_EXACT_RELATIONS = [
    {"family": "semantic-governance", "relation": "carries-definition", "source": "Artifact Type", "target": "Definition", "carrier": "semantic_definition_refs and semantic_definition_bindings", "priority": "required"},
    {"family": "semantic-governance", "relation": "admits", "source": "Decision", "target": "Definition, Artifact Type, Relation Kind, or other governed version", "carrier": "admission decision bindings", "priority": "required"},
    {"family": "product", "relation": "contributes-to-product", "source": "Project", "target": "Product", "carrier": "new Project-to-Product typed relation", "priority": "required-when-present"},
    {"family": "research", "relation": "executes-inquiry", "source": "Research Run", "target": "Research Inquiry", "carrier": "Research Run.inquiry_ref", "priority": "required"},
    {"family": "research", "relation": "tests-question-from", "source": "Experiment Design", "target": "Research Inquiry", "carrier": "research_refs", "priority": "required-when-present"},
    {"family": "research", "relation": "executes-design", "source": "Experiment Run", "target": "Experiment Design", "carrier": "design_ref and design_version_ref", "priority": "required"},
    {"family": "research", "relation": "advances-goal", "source": "Research or Experiment", "target": "Goal", "carrier": "goal_refs", "priority": "required"},
    {"family": "evidence", "relation": "produces-observation", "source": "Research Run or Experiment Run", "target": "Observation", "carrier": "observation_refs and Observation.run_ref", "priority": "required"},
    {"family": "evidence", "relation": "produces-measurement", "source": "Experiment Run", "target": "Measurement Result", "carrier": "measurement_result_refs", "priority": "required"},
    {"family": "evidence", "relation": "produces-evidence-set", "source": "Research Run or Experiment Run", "target": "Evidence Set", "carrier": "evidence_set_ref", "priority": "required"},
    {"family": "evidence", "relation": "answers-inquiry", "source": "Finding", "target": "Research Inquiry", "carrier": "inquiry_ref", "priority": "required"},
    {"family": "product", "relation": "tests-thesis-hypothesis", "source": "Experiment Design", "target": "Product Thesis hypothesis", "carrier": "product_evaluation_context.thesis_hypothesis_refs", "priority": "required-when-present"},
    {"family": "product", "relation": "tests-thesis-outcome", "source": "Experiment Design", "target": "Product Thesis outcome", "carrier": "product_evaluation_context.thesis_outcome_refs", "priority": "required-when-present"},
    {"family": "product", "relation": "evaluates-capability", "source": "Experiment Design", "target": "Product Capability", "carrier": "product_evaluation_context.product_capability_refs", "priority": "required-when-present"},
    {"family": "product", "relation": "tests-realization", "source": "Experiment Design", "target": "Capability Realization Binding", "carrier": "product_evaluation_context.realization_binding_refs", "priority": "required-when-present"},
    {"family": "context", "relation": "conforms-to-profile", "source": "Context", "target": "Context Profile", "carrier": "profile_ref", "priority": "required"},
    {"family": "context", "relation": "resolves-context", "source": "Context Request", "target": "Context", "carrier": "context_ref and context_version_ref", "priority": "required"},
    {"family": "context", "relation": "fulfills-request", "source": "Context View", "target": "Context Request", "carrier": "request_ref", "priority": "required"},
    {"family": "context", "relation": "projects-context", "source": "Context View", "target": "Context", "carrier": "context_ref and context_version_ref", "priority": "required"},
    {"family": "ontology", "relation": "contains-node", "source": "Ontology", "target": "Ontology node", "carrier": "node_refs", "priority": "required"},
    {"family": "ontology", "relation": "asserts-relation", "source": "Ontology", "target": "Typed relation", "carrier": "relation_refs", "priority": "required"},
    {"family": "model-authority", "relation": "binds-instance-to-parent", "source": "Model Instance Binding", "target": "exact parent model and local instance", "carrier": "parent_model_ref, parent_model_version_ref, and instance_ref", "priority": "required"},
    {"family": "model-authority", "relation": "inherits-contract", "source": "Model Instance Binding", "target": "Inherited contract", "carrier": "inherited_contract_refs", "priority": "required"},
    {"family": "model-authority", "relation": "conforms-to", "source": "Model Instance Binding", "target": "Conformance evidence", "carrier": "conformance_refs", "priority": "required-when-active"},
    {"family": "people-and-teams", "relation": "claims-identifier-for", "source": "Identity Claim", "target": "Person Reference", "carrier": "person_reference_ref", "priority": "required"},
    {"family": "people-and-teams", "relation": "defines-responsibility", "source": "Role", "target": "Responsibility", "carrier": "responsibility_refs", "priority": "required-when-present"},
    {"family": "people-and-teams", "relation": "bounded-by-authority-claim", "source": "Role Assignment", "target": "Authority Claim", "carrier": "authority_claim_refs", "priority": "required-when-present"},
]

RELATION_RECORD_REQUIREMENTS = [
    {"relation": "member-of", "endpoint_edge": "Person Reference -> Team", "relation_record": "Team Membership", "requirement": "The edge must retain membership_ref, state, period, basis, owner, and challenge route so the lifecycle record is not erased."},
    {"relation": "assigned-role", "endpoint_edge": "Person Reference or Team -> Role", "relation_record": "Role Assignment", "requirement": "The edge must retain role_assignment_ref, state, period, basis, scope, owner, and challenge route so the assignment record remains authoritative."},
]

RELATION_NORMALIZATION_PLAN = [
    {"relation": "carries-definition", "action": "add", "covers": ["artifact-type-carries-definition", "binds-definition"], "shape": "Artifact Type -> exact Definition version"},
    {"relation": "admits", "action": "add", "covers": ["decision-admits-artifact-type"], "shape": "Decision -> exact governed version admitted by that decision"},
    {"relation": "contributes-to-product", "action": "add", "covers": ["coordinated-by", "project-serves-product"], "shape": "Project -> Product"},
    {"relation": "addresses-inquiry", "action": "add", "covers": ["executes-inquiry", "tests-question-from", "preserves-research-trace"], "shape": "Research Run, Experiment Design, or Experiment Run -> Research Inquiry"},
    {"relation": "executes-design", "action": "add", "covers": ["executes-design"], "shape": "Experiment Run -> exact Experiment Design version"},
    {"relation": "advances-goal", "action": "add", "covers": ["advances-goal", "pursues-goal"], "shape": "Project, Research, or Experiment carrier -> Goal"},
    {"relation": "answers-inquiry", "action": "add", "covers": ["answers-inquiry"], "shape": "Finding -> Research Inquiry"},
    {"relation": "tests-thesis-proposition", "action": "add", "covers": ["tests-thesis-hypothesis", "tests-thesis-outcome"], "shape": "Experiment Design -> Product Thesis hypothesis or outcome"},
    {"relation": "conforms-to", "action": "add", "covers": ["conforms-to-profile", "conforms-to"], "shape": "Context -> Context Profile; capability instance -> exact parent contract"},
    {"relation": "requests-resolution-of", "action": "add", "covers": ["resolves-context"], "shape": "Context Request -> exact Context version"},
    {"relation": "fulfills-request", "action": "add", "covers": ["fulfills-request"], "shape": "Context View -> Context Request"},
    {"relation": "projects-context", "action": "add", "covers": ["projects-context"], "shape": "Context View -> exact Context version"},
    {"relation": "contains", "action": "add", "covers": ["contains-node", "asserts-relation"], "shape": "Ontology -> governed node or typed relation"},
    {"relation": "inherits-contract", "action": "add", "covers": ["inherits-contract"], "shape": "Capability instance -> inherited contract, qualified by Model Instance Binding"},
    {"relation": "claims-identifier-for", "action": "add", "covers": ["claims-identifier-for"], "shape": "Identity Claim -> Person Reference"},
    {"relation": "defines-responsibility", "action": "add", "covers": ["defines-responsibility"], "shape": "Role -> Responsibility"},
    {"relation": "bounded-by-authority-claim", "action": "add", "covers": ["bounded-by-authority-claim"], "shape": "Role Assignment -> Authority Claim"},
]

REUSED_EXISTING_RELATIONS = [
    {"relation": "derives-from", "use": "Observation, Measurement Result, and Evidence Set -> producing Research Run or Experiment Run", "replaces": ["produces-observation", "produces-measurement", "produces-evidence-set"]},
    {"relation": "evaluates", "use": "Experiment Design or Experiment Run -> Product, Product Capability, or Capability Realization Binding", "replaces": ["evaluates-capability", "tests-realization", "evaluates-product-context"]},
    {"relation": "belongs-to-product", "use": "Context -> Product", "replaces": []},
    {"relation": "belongs-to-project", "use": "Context, Research Run, or Experiment Run -> Project", "replaces": []},
    {"relation": "uses-method", "use": "Observation, Measurement Result, Project, or Product -> Method, with a usage-role qualifier when the Method is constitutive", "replaces": ["embodies-method"]},
    {"relation": "instance-of", "use": "Capability instance -> exact parent model", "replaces": ["binds-instance-to-parent"]},
    {"relation": "governed-by", "use": "Context or Ontology -> Policy", "replaces": []},
    {"relation": "successor-of and supersedes", "use": "All successor-bearing candidates", "replaces": []},
]

SCHEMA_RELATION_CORRECTIONS = [
    "Measurement Result.subject_ref now identifies the Experiment Run that produced the result in the coherent example.",
    "Experiment Run.design_version_ref now names a complete logical version instead of a truncated pseudo-digest.",
    "Model Instance Binding.parent_model_version_ref now names a complete parent version instead of the ambiguous @v1 shorthand.",
    "Identity Claim and Team Membership now use person_reference_ref, making the endpoint kind explicit rather than implying a direct Person record.",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


def render(model: dict[str, Any], examples: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is model.json and examples.json. -->",
        "",
        "# Remaining 18 Artifact Types: complete review model",
        "",
        "This is the one decision surface for the remaining migration queue. Every package is revised and validated, but none is admitted by this review candidate.",
        "",
        "## Decision effect",
        "",
        "A single approval will authorize one atomic admission decision covering the exact 18 Artifact Type contracts and schemas bound here. It will not admit example instances, activate consumers, grant identity or authority, run research or experiments, or establish findings as decisions.",
        "",
        "## Complete model",
        "",
        "| # | Family | Artifact Type | Definition | Depends on | Version | Validation |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for index, entry in enumerate(model["entries"], 1):
        deps = "<br>".join(f"`{x}`" for x in entry["dependencies"]) or "none"
        defs = "<br>".join(f"`{x}`" for x in entry["semantic_definition_refs"])
        lines.append(f"| {index} | {entry['family']} | `{entry['artifact_type_ref']}` | {defs} | {deps} | `{entry['artifact_version']}` | `{entry['validation_result']}` |")

    lines += [
        "",
        "## Dependency shape",
        "",
        "```mermaid",
        "flowchart LR",
        "  MM[Measurement Method] --> MR[Measurement Result]",
        "  MM --> ED[Experiment Design]",
        "  ED --> ER[Experiment Run]",
        "  ER --> O[Observation]",
        "  ER --> MR",
        "  RI[Admitted Research Inquiry] --> RR[Admitted Research Run] --> F[Finding]",
        "  CP[Context Profile] --> C[Context] --> CR[Context Request] --> CV[Context View]",
        "  PR[Person Reference] --> IC[Identity Claim]",
        "  PR --> TM[Team Membership]",
        "  T[Team] <--> TM",
        "  R[Role] --> RA[Role Assignment]",
        "  PR --> RA",
        "  T --> RA",
        "```",
        "",
        "The Experiment Run, Observation, and Measurement Result contracts form one mutually useful empirical cluster. Team and Team Membership form one lifecycle cluster. Atomic admission keeps those cross-references resolvable without pretending that any instance exists.",
        "",
        "## Overlap dispositions",
        "",
        "| Candidate | Adjacent carrier | Disposition | Boundary |",
        "| --- | --- | --- | --- |",
    ]
    for overlap in model["overlap_dispositions"]:
        lines.append(f"| `{overlap['candidate_ref']}` | `{overlap['adjacent_ref']}` | `{overlap['disposition']}` | {overlap['boundary']} |")

    lines += [
        "",
        "## Experiment and Research relations",
        "",
        "| Source | Relation | Target | Current carrier | Relation-kind state |",
        "| --- | --- | --- | --- | --- |",
    ]
    for relation in model["experiment_relations"]:
        lines.append(f"| {relation['source']} | `{relation['relation']}` | {relation['target']} | `{relation['carrier']}` | `{relation['relation_kind_state']}` |")

    audit = model["relation_audit"]
    lines += [
        "",
        "## Complete relation audit",
        "",
        f"The repository has **{audit['existing_contract_count']} admitted migration contracts** for relation kinds. They select migration semantics only; they do not provide admitted canonical relation carriers. The revised Artifact Types carry the references below, but the graph is incomplete until endpoint gaps and missing exact kinds are resolved.",
        "",
        "### Existing relation kinds with endpoint gaps",
        "",
        "| Relation | Current source kinds | Missing source kinds | Why it matters |",
        "| --- | --- | --- | --- |",
    ]
    for gap in audit["endpoint_gaps"]:
        lines.append(f"| `{gap['relation']}` | {', '.join(f'`{x}`' for x in gap['current_sources'])} | {', '.join(f'`{x}`' for x in gap['missing_sources'])} | {gap['reason']} |")

    lines += [
        "",
        "### Unmodeled exact relationship semantics",
        "",
        f"These {len(audit['missing_exact_relations'])} rows are semantic gaps found in the field model and repository examples. They are not a recommendation to create one relation kind per row; the normalization below reuses generic relations and combines repeated meanings.",
        "",
        "| Family | Relation | Source | Target | Current field carrier | Priority |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for gap in audit["missing_exact_relations"]:
        lines.append(f"| {gap['family']} | `{gap['relation']}` | {gap['source']} | {gap['target']} | `{gap['carrier']}` | `{gap['priority']}` |")

    lines += [
        "",
        "### Relation records that must retain identity",
        "",
    ]
    for requirement in audit["relation_record_requirements"]:
        lines.append(f"- `{requirement['relation']}` ({requirement['endpoint_edge']}) is represented by `{requirement['relation_record']}`. {requirement['requirement']}")

    lines += [
        "",
        "### Superseded verb-level relation proposal",
        "",
        f"The initial proposal added **{len(audit['normalization_plan'])}** relation kinds and expanded five contracts. The admitted Classification Axis, Classification Orthogonality, Typed Coupling, Root-Axis Independence, Governance-Axis Independence, and Identity Relation definitions showed that this still duplicated semantic axes. It is retained below as audit history and is superseded by the axis-orthogonal successor.",
        "",
        "| Relation | Action | Consolidates | Endpoint shape |",
        "| --- | --- | --- | --- |",
    ]
    for item in audit["normalization_plan"]:
        lines.append(f"| `{item['relation']}` | `{item['action']}` | {', '.join(f'`{x}`' for x in item['covers'])} | {item['shape']} |")
    lines += ["", "Existing kinds to reuse:", ""]
    for item in audit["reused_existing_relations"]:
        lines.append(f"- `{item['relation']}`: {item['use']}")

    axis_model = audit["axis_orthogonal_successor"]
    lines += [
        "",
        "### Current axis-orthogonal relation model",
        "",
        f"The current candidate compresses `{axis_model['predecessor_relation_kinds']}` verb-level kinds into `{axis_model['axis_relation_kinds']}` independently valued relation axes, preserves all prior meanings as qualifier values, and passes `{axis_model['hostile_no_collapse_cases']}` hostile no-collapse cases.",
        "",
        f"Canonical candidate: `{axis_model['path']}`",
        "",
        f"Validation receipt: `{axis_model['validation_receipt_path']}`",
    ]

    lines += [
        "",
        "### Corrections applied during this audit",
        "",
    ]
    for correction in audit["schema_relation_corrections"]:
        lines.append(f"- {correction}")

    lines += ["", "## Revised examples", ""]
    for index, entry in enumerate(model["entries"], 1):
        slug = entry["slug"]
        lines += [
            f"### {index}. {entry['name']}",
            "",
            entry["purpose"],
            "",
            f"Canonical example: `{entry['example_path']}`",
            "",
            "```json",
            json.dumps(examples[slug], indent=2, sort_keys=True),
            "```",
            "",
        ]

    lines += [
        "## Claim ceiling",
        "",
        model["claim_ceiling"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    live_defs = {
        f"{item['definition_id']}@{item['version']}": item
        for item in load(DEFINITION_REGISTRY)["entries"]
        if item["lifecycle_state"] == "admitted"
    }
    entries = []
    examples: dict[str, Any] = {}
    for slug in ORDER:
        root = LAB / "authority/artifact-types" / slug / "v1"
        artifact = load(root / "artifact.json")
        materialization = load(root / "materialization.json")
        receipt = load(root / "receipts/validation.json")
        example_path = root / artifact["validation_contract"]["positive_witness"]
        example = load(example_path)
        examples[slug] = example
        definitions = artifact["semantic_definition_refs"]
        if not definitions or any(ref not in live_defs for ref in definitions):
            raise RuntimeError(f"unadmitted Definition dependency for {slug}")
        entries.append({
            "slug": slug,
            "target_id": f"type.{slug}",
            "family": FAMILIES[slug],
            "artifact_type_ref": artifact["artifact_type_ref"],
            "artifact_version": artifact["version"],
            "name": artifact["name"],
            "purpose": artifact["distinct_validation_purpose"],
            "dependencies": DEPENDENCIES[slug],
            "semantic_definition_refs": definitions,
            "artifact_path": rel(root / "artifact.json"),
            "artifact_sha256": sha(root / "artifact.json"),
            "schema_path": rel(root / "schema.json"),
            "schema_sha256": sha(root / "schema.json"),
            "example_path": rel(example_path),
            "example_sha256": sha(example_path),
            "materialization_path": rel(root / "materialization.json"),
            "materialization_sha256": sha(root / "materialization.json"),
            "refinement": materialization["review_refinement"],
            "validation_receipt_path": rel(root / "receipts/validation.json"),
            "validation_receipt_sha256": sha(root / "receipts/validation.json"),
            "validation_result": receipt["result"],
            "admission_state": "awaiting-single-batch-decision",
        })

    model = {
        "schema_version": "cyberalchemy-lab-complete-artifact-type-review-model/v1",
        "model_id": "CAL-REMAINING-18-COMPLETE-MODEL-0005",
        "status": "candidate-complete-awaiting-one-admission-decision",
        "authority_effect": "none",
        "decision_shape": "one-atomic-admission-decision-for-18-artifact-types",
        "counts": {
            "artifact_types": 18,
            "revised": 18,
            "package_validation_pass": 18,
            "exact_duplicates": 0,
            "distinct_overlap_dispositions": len(OVERLAPS),
            "instances_admitted": 0,
            "consumer_activations": 0,
        },
        "entries": entries,
        "overlap_dispositions": OVERLAPS,
        "experiment_relations": EXPERIMENT_RELATIONS,
        "relation_audit": {
            "existing_contract_count": len([entry for entry in load(RELATION_CONTRACT_REGISTRY)["entries"] if entry["family"] == "relation-kind"]),
            "contract_state": "admitted-migration-contract-only",
            "canonical_relation_carrier_state": "not-admitted-by-this-artifact-type-batch",
            "endpoint_gaps": RELATION_ENDPOINT_GAPS,
            "missing_exact_relations": MISSING_EXACT_RELATIONS,
            "relation_record_requirements": RELATION_RECORD_REQUIREMENTS,
            "normalization_plan": RELATION_NORMALIZATION_PLAN,
            "reused_existing_relations": REUSED_EXISTING_RELATIONS,
            "schema_relation_corrections": SCHEMA_RELATION_CORRECTIONS,
            "recommendation_state": "superseded-by-axis-orthogonal-successor",
            "axis_orthogonal_successor": {
                "path": rel(AXIS_RELATION_MODEL), "sha256": sha(AXIS_RELATION_MODEL),
                "validation_receipt_path": rel(AXIS_RELATION_RECEIPT), "validation_receipt_sha256": sha(AXIS_RELATION_RECEIPT),
                "predecessor_relation_kinds": load(AXIS_RELATION_MODEL)["counts"]["predecessor_relation_kinds"],
                "axis_relation_kinds": load(AXIS_RELATION_MODEL)["counts"]["axis_relation_kinds"],
                "collapsed_duplicate_kinds": load(AXIS_RELATION_MODEL)["counts"]["collapsed_duplicate_kinds"],
                "hostile_no_collapse_cases": load(AXIS_RELATION_MODEL)["counts"]["hostile_no_collapse_cases"],
                "validation_result": load(AXIS_RELATION_RECEIPT)["result"],
            },
            "admission_recommendation": "Use the axis-orthogonal successor as the relation layer for the final review. Do not admit the superseded verb-level proposal as independent Relation Kinds.",
        },
        "admission_prerequisites": [
            "All 18 exact artifact, schema, example, materialization, refinement, and receipt digests remain current.",
            "All semantic Definition bindings remain admitted and digest-current.",
            "The owner approves this complete model as one atomic batch.",
            "The bound axis-orthogonal Relation Kind model and no-collapse receipt remain digest-current and passing.",
        ],
        "admission_exclusions": [
            "No example or real instance is admitted.",
            "No consumer, tool, runtime, research run, or experiment is activated.",
            "No identity, Team Membership, Role Assignment, permission, responsibility, or authority claim is established.",
            "No Observation, Measurement Result, or Finding is accepted as fact, decision, Definition, proof, Product value, or policy.",
        ],
        "claim_ceiling": "This complete model proves that the exact 18 candidate Artifact Type packages were revised as one coherent model, bound to admitted Definitions, checked for exact duplicates and close overlaps, and validated against their fixtures. It does not admit the Artifact Types or any instances and does not activate consumers or behavior.",
    }
    dump(ROOT / "examples.json", examples)
    dump(ROOT / "model.json", model)
    (ROOT / "MODEL.md").write_text(render(model, examples), encoding="utf-8")

    paths = [ROOT / "build.py", ROOT / "validate.py", ROOT / "model.json", ROOT / "examples.json", ROOT / "MODEL.md"]
    manifest = {
        "schema_version": "cyberalchemy-lab-exact-file-manifest/v1",
        "subject": model["model_id"],
        "files": [{"path": rel(path), "sha256": sha(path)} for path in paths],
        "bound_package_files": [
            {"path": entry[field], "sha256": entry[digest]}
            for entry in entries
            for field, digest in [
                ("artifact_path", "artifact_sha256"), ("schema_path", "schema_sha256"),
                ("example_path", "example_sha256"), ("materialization_path", "materialization_sha256"),
                ("validation_receipt_path", "validation_receipt_sha256"),
            ]
        ],
        "excluded_from_self_hash": [rel(ROOT / "manifest.json"), rel(ROOT / "receipts/validation.json")],
    }
    dump(ROOT / "manifest.json", manifest)
    result = subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
