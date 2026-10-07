#!/usr/bin/env python3
"""Build the complete candidate Relation Kind model for owner review."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
MIGRATION_REGISTRY = LAB / "authority/decisions/migration-contracts/v1/registry.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


REVISIONS = {
    "relation.belongs-to-product": {
        "source_kinds": ["product-capability", "product-thesis", "context"],
        "meaning": "Declares that a Product Thesis, Product Capability, or purpose-specific Context is anchored to one Product.",
    },
    "relation.belongs-to-project": {
        "source_kinds": ["research-inquiry", "research-run", "experiment-design", "experiment-run", "goal", "work", "evidence-set", "capability-realization-binding", "context"],
        "meaning": "Declares the Project scope that owns or bounds a research, experiment, goal, work, evidence, realization, or Context carrier.",
    },
    "relation.uses-method": {
        "source_kinds": ["research-run", "experiment-run", "measurement-result", "observation", "project", "product"],
        "meaning": "Declares the Method used by an execution, empirical record, Project, or Product; usage_role distinguishes ordinary use from a constitutive Method.",
        "required_qualifiers": ["usage_role"],
    },
    "relation.evaluates": {
        "source_kinds": ["evaluation", "experiment-design", "experiment-run"],
        "meaning": "Declares that an Evaluation or Experiment assesses a named subject without establishing adoption, realization, effectiveness, or Product value.",
        "required_qualifiers": ["evaluation_purpose"],
    },
    "relation.instance-of": {
        "source_kinds": ["implementation", "product-capability", "capability-instance"],
        "target_kinds": ["product-capability", "product", "governed-model"],
        "meaning": "Classifies an implementation or capability instance under an exact parent model while keeping ownership and lifecycle separate.",
        "required_qualifiers": ["parent_version_ref", "binding_ref"],
    },
}


MEANINGS = {
    "relation.originates-from": "Links an artifact to the source from which its content or identity originated.",
    "relation.successor-of": "Links a successor version or identity to its immediate predecessor.",
    "relation.supersedes": "Declares that a newer governed artifact replaces an older artifact within a stated scope.",
    "relation.derives-from": "Links a derived artifact, observation, result, or evidence set to the source or run from which it was produced.",
    "relation.supports": "Declares bounded evidence that supports a Finding, hypothesis, identity claim, or authority claim.",
    "relation.contradicts": "Declares bounded counterevidence against a Finding, hypothesis, identity claim, or authority claim.",
    "relation.governed-by": "Links a subject to the Policy or Constitution that governs it.",
    "relation.authorizes": "Links a Decision to the exact effect it authorizes; the edge does not execute the effect.",
    "relation.adopts": "Links a Decision to a version or model it adopts for use in scope.",
    "relation.realizes": "Links an implementation to the Product Capability it realizes.",
    "relation.compiles-to": "Links authored source to a generated output derived from it.",
    "relation.binds-implementation": "Links an implementation to the Ontology or Schema it implements.",
    "relation.frames": "Links a Context to the subject whose relevance and interpretation it frames.",
    "relation.references-bounded-context": "Links a purpose-specific Context to a DDD Bounded Context it references.",
    "relation.member-of": "Links a Person Reference to a Team through an independently governed Team Membership record.",
    "relation.assigned-role": "Links a Person Reference or Team to a Role through an independently governed Role Assignment record.",
    "relation.assigned-responsibility": "Links a Person Reference or Team to an explicitly assigned Responsibility.",
    "relation.represents-person": "Links a privacy-minimal Person Reference to the Person it denotes under bounded evidence.",
    "relation.identity-link": "Links two Person References asserted to refer to the same Person without merging their identities.",
    "relation.claims-authority-over": "Links an Authority Claim to the object and scope over which authority is asserted.",
}


GROUPS = {
    "relation.belongs-to-product": "product-and-project", "relation.belongs-to-project": "product-and-project",
    "relation.originates-from": "lineage-and-lifecycle", "relation.successor-of": "lineage-and-lifecycle", "relation.supersedes": "lineage-and-lifecycle",
    "relation.uses-method": "research-and-evidence", "relation.derives-from": "research-and-evidence", "relation.supports": "research-and-evidence", "relation.contradicts": "research-and-evidence", "relation.evaluates": "research-and-evidence",
    "relation.governed-by": "governance-and-authority", "relation.authorizes": "governance-and-authority", "relation.adopts": "governance-and-authority",
    "relation.realizes": "implementation-and-model", "relation.instance-of": "implementation-and-model", "relation.compiles-to": "implementation-and-model", "relation.binds-implementation": "implementation-and-model",
    "relation.frames": "context", "relation.references-bounded-context": "context",
    "relation.member-of": "people-and-teams", "relation.assigned-role": "people-and-teams", "relation.assigned-responsibility": "people-and-teams", "relation.represents-person": "people-and-teams", "relation.identity-link": "people-and-teams", "relation.claims-authority-over": "people-and-teams",
}


NEW = [
    {"id": "relation.carries-definition", "group": "semantic-governance", "meaning": "Links an Artifact Type to the exact admitted Definition version it carries.", "direction": "artifact-type-to-definition", "inverse": "carried-by-artifact-types", "sources": ["artifact-type"], "targets": ["definition"], "qualifiers": ["definition_version_ref", "definition_sha256"]},
    {"id": "relation.admits", "group": "semantic-governance", "meaning": "Links an admission Decision to the exact governed version admitted by that decision.", "direction": "decision-to-admitted-version", "inverse": "admitted-by", "sources": ["decision"], "targets": ["definition", "artifact-type", "relation-kind", "other-governed-version"], "qualifiers": ["admitted_version_ref", "admitted_sha256"]},
    {"id": "relation.contributes-to-product", "group": "product-and-project", "meaning": "Links a bounded Project to the Product whose outcomes it is intended to advance.", "direction": "project-to-product", "inverse": "supported-by-projects", "sources": ["project"], "targets": ["product"], "qualifiers": ["contribution_scope"]},
    {"id": "relation.addresses-inquiry", "group": "research-and-evidence", "meaning": "Links a Research Run, Experiment Design, or Experiment Run to the Research Inquiry whose question it addresses.", "direction": "research-activity-to-inquiry", "inverse": "addressed-by", "sources": ["research-run", "experiment-design", "experiment-run"], "targets": ["research-inquiry"], "qualifiers": []},
    {"id": "relation.executes-design", "group": "research-and-evidence", "meaning": "Links an Experiment Run to the exact Experiment Design version it executes.", "direction": "experiment-run-to-design", "inverse": "executed-by-runs", "sources": ["experiment-run"], "targets": ["experiment-design"], "qualifiers": ["design_version_ref"]},
    {"id": "relation.advances-goal", "group": "product-and-project", "meaning": "Links a Project, Research carrier, or Experiment carrier to the Goal it is intended to advance.", "direction": "activity-to-goal", "inverse": "advanced-by", "sources": ["project", "research-inquiry", "research-run", "experiment-design", "experiment-run"], "targets": ["goal"], "qualifiers": []},
    {"id": "relation.answers-inquiry", "group": "research-and-evidence", "meaning": "Links a Finding to the Research Inquiry whose question the Finding answers within its evidence boundary.", "direction": "finding-to-inquiry", "inverse": "answered-by-findings", "sources": ["finding"], "targets": ["research-inquiry"], "qualifiers": []},
    {"id": "relation.tests-thesis-proposition", "group": "product-and-project", "meaning": "Links an Experiment Design to a Product Thesis hypothesis or outcome proposition it is designed to test.", "direction": "experiment-design-to-thesis-proposition", "inverse": "tested-by-designs", "sources": ["experiment-design"], "targets": ["product-thesis-hypothesis", "product-thesis-outcome"], "qualifiers": ["proposition_kind"]},
    {"id": "relation.conforms-to", "group": "implementation-and-model", "meaning": "Declares evidence-bounded conformance of a Context or capability instance to an exact Profile, parent model, or contract.", "direction": "subject-to-governing-contract", "inverse": "conforming-subjects", "sources": ["context", "capability-instance"], "targets": ["context-profile", "governed-model", "contract"], "qualifiers": ["exact_version_ref", "conformance_evidence_refs"]},
    {"id": "relation.requests-resolution-of", "group": "context", "meaning": "Links a Context Request to the exact Context version it asks to resolve.", "direction": "context-request-to-context", "inverse": "resolution-requests", "sources": ["context-request"], "targets": ["context"], "qualifiers": ["context_version_ref"]},
    {"id": "relation.fulfills-request", "group": "context", "meaning": "Links an immutable Context View to the Context Request it fulfills.", "direction": "context-view-to-request", "inverse": "fulfilled-by-views", "sources": ["context-view"], "targets": ["context-request"], "qualifiers": []},
    {"id": "relation.projects-context", "group": "context", "meaning": "Links an immutable Context View to the exact Context version it projects.", "direction": "context-view-to-context", "inverse": "projected-by-views", "sources": ["context-view"], "targets": ["context"], "qualifiers": ["context_version_ref", "source_epoch"]},
    {"id": "relation.contains", "group": "semantic-governance", "meaning": "Declares governed composition, including Ontology membership and Product containment, without transferring authority between container and member.", "direction": "container-to-member", "inverse": "contained-by", "sources": ["ontology", "product"], "targets": ["ontology-node", "typed-relation", "product"], "qualifiers": ["membership_role"]},
    {"id": "relation.inherits-contract", "group": "implementation-and-model", "meaning": "Links a capability instance to an exact inherited contract, qualified by its Model Instance Binding.", "direction": "capability-instance-to-contract", "inverse": "inherited-by-instances", "sources": ["capability-instance"], "targets": ["contract"], "qualifiers": ["binding_ref", "contract_version_ref"]},
    {"id": "relation.claims-identifier-for", "group": "people-and-teams", "meaning": "Links an Identity Claim to the Person Reference for which it asserts a bounded identifier.", "direction": "identity-claim-to-person-reference", "inverse": "identifier-claims", "sources": ["identity-claim"], "targets": ["person-reference"], "qualifiers": ["assurance_level", "claim_scope"]},
    {"id": "relation.defines-responsibility", "group": "people-and-teams", "meaning": "Links a reusable Role to a Responsibility defined as part of that Role contract.", "direction": "role-to-responsibility", "inverse": "defined-by-roles", "sources": ["role"], "targets": ["responsibility"], "qualifiers": []},
    {"id": "relation.bounded-by-authority-claim", "group": "people-and-teams", "meaning": "Links a Role Assignment to the separate Authority Claim that bounds any authority exercised through the assignment.", "direction": "role-assignment-to-authority-claim", "inverse": "bounds-role-assignments", "sources": ["role-assignment"], "targets": ["authority-claim"], "qualifiers": []},
]


EXAMPLES = {
    "relation.belongs-to-product": ("context:lab-artifact-type-admission", "CA2-PRODUCT-CRAFT", {}),
    "relation.belongs-to-project": ("experiment-run:definition-normalization-residue:2026-10-05", "project:lab-semantic-governance", {}),
    "relation.originates-from": ("finding:research-inquiry-v1-contract-gap", "source:cyberalchemy-v2-definitions", {}),
    "relation.successor-of": ("definition:product-identity@2", "definition:product-identity@1", {}),
    "relation.supersedes": ("artifact-type:product-identity@2", "artifact-type:product-identity@1", {}),
    "relation.uses-method": ("measurement-result:definition-normalization-residue-entropy:2026-10-05", "measurement-method:definition-normalization-residue-entropy", {"usage_role": "measurement"}),
    "relation.derives-from": ("observation:definition-normalization-residue-classes", "experiment-run:definition-normalization-residue:2026-10-05", {}),
    "relation.supports": ("evidence-set:definition-normalization-residue-run-2026-10-05", "finding:normalization-residue-lowered", {}),
    "relation.contradicts": ("observation:normalization-regression", "finding:normalization-residue-lowered", {}),
    "relation.evaluates": ("experiment-run:definition-normalization-residue:2026-10-05", "capability:craft:governed-definition-admission", {"evaluation_purpose": "Measure one bounded residue signal"}),
    "relation.governed-by": ("context:lab-artifact-type-admission", "policy:admitted-authority-first", {}),
    "relation.authorizes": ("decision:admit-definition-v1", "effect:add-definition-to-authority-registry", {}),
    "relation.adopts": ("decision:adopt-definition-workflow", "binding:craft:governed-definition-admission:workflow-v1", {}),
    "relation.realizes": ("workflow:governed-definition-admission/v1", "capability:craft:governed-definition-admission", {}),
    "relation.instance-of": ("capability-instance:lab-artifact-type-reviewer", "product-capability:governed-definition-admission", {"parent_version_ref": "product-capability:governed-definition-admission@1.0.0-candidate.1", "binding_ref": "model-instance-binding:artifact-type-reviewer"}),
    "relation.compiles-to": ("authority/definitions/registry.json", "authority/definitions/DEFINITIONS-INDEX.md", {}),
    "relation.binds-implementation": ("tool:definition-validator", "ontology:artifact-governance", {}),
    "relation.frames": ("context:lab-artifact-type-admission", "review:remaining-18-artifact-types", {}),
    "relation.references-bounded-context": ("context:lab-artifact-type-admission", "bounded-context:semantic-governance", {}),
    "relation.member-of": ("person-reference:repository-reviewer", "team:semantic-governance", {"membership_ref": "team-membership:reviewer:semantic-governance", "state": "active", "period": "2026-10-05/open", "basis_ref": "decision:semantic-governance-team-membership"}),
    "relation.assigned-role": ("person-reference:repository-reviewer", "role:artifact-type-reviewer", {"role_assignment_ref": "role-assignment:reviewer:artifact-type-reviewer", "state": "active", "period": "2026-10-05/open", "basis_ref": "decision:assign-artifact-type-reviewer"}),
    "relation.assigned-responsibility": ("team:semantic-governance", "responsibility:maintain-definition-authority", {}),
    "relation.represents-person": ("person-reference:repository-reviewer", "person:repository-reviewer", {}),
    "relation.identity-link": ("person-reference:repository-reviewer", "person-reference:workspace-reviewer-001", {}),
    "relation.claims-authority-over": ("authority-claim:may-recommend-artifact-type-admission", "decision-scope:artifact-type-admission", {}),
    "relation.carries-definition": ("cal.artifact-type.experiment-run/v1", "cal.definition.experiment@1.0.0-candidate.1", {"definition_version_ref": "cal.definition.experiment@1.0.0-candidate.1", "definition_sha256": "digest-bound-at-instance-time"}),
    "relation.admits": ("decision:artifact-type-batch-admission", "cal.artifact-type.experiment-run/v1", {"admitted_version_ref": "cal.artifact-type.experiment-run/v1@1.0.0-candidate.2", "admitted_sha256": "digest-bound-at-decision-time"}),
    "relation.contributes-to-product": ("project:lab-semantic-governance", "CA2-PRODUCT-CRAFT", {"contribution_scope": "Governed semantic foundations"}),
    "relation.addresses-inquiry": ("experiment-design:definition-normalization-residue", "research-inquiry:definition-normalization-residue", {}),
    "relation.executes-design": ("experiment-run:definition-normalization-residue:2026-10-05", "experiment-design:definition-normalization-residue", {"design_version_ref": "experiment-design:definition-normalization-residue@1.0.0-candidate.1"}),
    "relation.advances-goal": ("project:lab-semantic-governance", "goal:reduce-unresolved-definition-residue", {}),
    "relation.answers-inquiry": ("finding:normalization-residue-lowered", "research-inquiry:definition-normalization-residue", {}),
    "relation.tests-thesis-proposition": ("experiment-design:definition-normalization-residue", "product-thesis:craft#outcome-authoritative-state", {"proposition_kind": "outcome"}),
    "relation.conforms-to": ("context:lab-artifact-type-admission", "context-profile:governed-review", {"exact_version_ref": "context-profile:governed-review@1.0.0-candidate.2", "conformance_evidence_refs": ["receipt:remaining-18-model-validation"]}),
    "relation.requests-resolution-of": ("context-request:remaining-18-review", "context:lab-artifact-type-admission", {"context_version_ref": "context:lab-artifact-type-admission@1.0.0-candidate.2"}),
    "relation.fulfills-request": ("context-view:remaining-18-review:2026-10-05", "context-request:remaining-18-review", {}),
    "relation.projects-context": ("context-view:remaining-18-review:2026-10-05", "context:lab-artifact-type-admission", {"context_version_ref": "context:lab-artifact-type-admission@1.0.0-candidate.2", "source_epoch": "git-worktree:2026-10-05T15:05:00Z"}),
    "relation.contains": ("ontology:artifact-governance", "cal.definition.artifact-type", {"membership_role": "governed-node"}),
    "relation.inherits-contract": ("capability-instance:lab-artifact-type-reviewer", "contract:definition-admission-boundaries/v1", {"binding_ref": "model-instance-binding:artifact-type-reviewer", "contract_version_ref": "contract:definition-admission-boundaries/v1"}),
    "relation.claims-identifier-for": ("identity-claim:repository-reviewer:workspace-handle", "person-reference:repository-reviewer", {"assurance_level": "self-asserted", "claim_scope": "CyberAlchemy Lab review attribution"}),
    "relation.defines-responsibility": ("role:artifact-type-reviewer", "responsibility:artifact-type-review-quality", {}),
    "relation.bounded-by-authority-claim": ("role-assignment:reviewer:artifact-type-reviewer", "authority-claim:may-recommend-artifact-type-admission", {}),
}


RESIDUE = [
    {"observed": "artifact-type-carries-definition or binds-definition", "disposition": "normalized", "canonical": ["relation.carries-definition"]},
    {"observed": "decision-admits-artifact-type", "disposition": "normalized", "canonical": ["relation.admits"]},
    {"observed": "supports-or-contradicts", "disposition": "split", "canonical": ["relation.supports", "relation.contradicts"]},
    {"observed": "contains_product", "disposition": "normalized-with-qualifier", "canonical": ["relation.contains"]},
    {"observed": "coordinated_by", "disposition": "inverse-normalized", "canonical": ["relation.contributes-to-product"]},
    {"observed": "embodies_method", "disposition": "normalized-with-usage-role", "canonical": ["relation.uses-method"]},
    {"observed": "uses_method", "disposition": "spelling-normalized", "canonical": ["relation.uses-method"]},
    {"observed": "pursues_goal", "disposition": "normalized", "canonical": ["relation.advances-goal"]},
    {"observed": "may-recommend-admission", "disposition": "modeled-as-authority-scope", "canonical": ["relation.claims-authority-over"]},
]


def build() -> dict[str, Any]:
    migration = load(MIGRATION_REGISTRY)
    entries = []
    for row in migration["entries"]:
        if row["family"] != "relation-kind":
            continue
        contract_path = LAB / row["contract"]["path"]
        contract = load(contract_path)
        relation_id = contract["relation_kind_id"]
        revision = REVISIONS.get(relation_id, {})
        entries.append({
            "relation_kind_id": relation_id,
            "name": relation_id.removeprefix("relation.").replace("-", " ").title(),
            "group": GROUPS[relation_id],
            "revision_state": "candidate-revised" if revision else "migration-contract-preserved",
            "meaning": revision["meaning"] if "meaning" in revision else MEANINGS[relation_id],
            "direction": contract["direction"],
            "inverse_projection": contract["inverse_projection"],
            "source_kinds": revision.get("source_kinds", contract["source_kinds"]),
            "target_kinds": revision.get("target_kinds", contract["target_kinds"]),
            "evidence_required": contract["evidence_required"],
            "self_relations": contract["self_relations"],
            "required_qualifiers": revision.get("required_qualifiers", []),
            "relation_record_requirement": "team-membership" if relation_id == "relation.member-of" else "role-assignment" if relation_id == "relation.assigned-role" else None,
            "source_contract": {"path": rel(contract_path), "sha256": sha(contract_path), "status": row["status"]},
            "claim_ceiling": contract["claim_ceiling"],
        })
    for item in NEW:
        entries.append({
            "relation_kind_id": item["id"], "name": item["id"].removeprefix("relation.").replace("-", " ").title(),
            "group": item["group"], "revision_state": "candidate-new", "meaning": item["meaning"],
            "direction": item["direction"], "inverse_projection": item["inverse"],
            "source_kinds": item["sources"], "target_kinds": item["targets"], "evidence_required": True,
            "self_relations": "rejected", "required_qualifiers": item["qualifiers"], "relation_record_requirement": None,
            "source_contract": None,
            "claim_ceiling": "Directed relationship typing and graph closure only. The relation does not admit endpoints, prove evidence truth, grant authority, or execute an effect.",
        })
    entries.sort(key=lambda x: (x["group"], x["relation_kind_id"]))
    examples = {
        relation_id: {
            "relation_id": f"example:{relation_id}", "relation_kind_ref": relation_id,
            "source_ref": source, "target_ref": target, "qualifiers": qualifiers,
            "evidence_refs": [f"evidence:{relation_id.removeprefix('relation.')}"],
            "status": "candidate-example", "authority_effect": "none",
        }
        for relation_id, (source, target, qualifiers) in EXAMPLES.items()
    }
    model = {
        "schema_version": "cyberalchemy-lab-complete-relation-model/v1",
        "model_id": "CAL-COMPLETE-RELATION-MODEL-0001",
        "status": "candidate-complete-awaiting-owner-review",
        "authority_effect": "none",
        "counts": {"relation_kinds": len(entries), "preserved": 20, "revised": 5, "new": len(NEW), "unresolved_aliases": 0},
        "entries": entries,
        "repository_relation_residue": RESIDUE,
        "admission_shape": "one atomic relation-kind decision after owner approval; relation examples and endpoint artifacts remain unadmitted",
        "claim_ceiling": "This candidate defines a complete normalized Relation Kind review surface for the current Artifact Type model and repository relation residue. It does not admit Relation Kinds, endpoint artifacts, examples, identities, authority, evidence claims, or effects.",
    }
    dump(ROOT / "model.json", model)
    dump(ROOT / "examples.json", examples)
    (ROOT / "RELATIONS.md").write_text(render(model, examples), encoding="utf-8")
    paths = [ROOT / "build.py", ROOT / "validate.py", ROOT / "model.json", ROOT / "examples.json", ROOT / "RELATIONS.md"]
    dump(ROOT / "manifest.json", {
        "schema_version": "cyberalchemy-lab-exact-file-manifest/v1", "subject": model["model_id"],
        "files": [{"path": rel(path), "sha256": sha(path)} for path in paths],
        "inputs": [{"path": rel(MIGRATION_REGISTRY), "sha256": sha(MIGRATION_REGISTRY)}],
        "excluded_from_self_hash": [rel(ROOT / "manifest.json"), rel(ROOT / "receipts/validation.json")],
    })
    return model


def render(model: dict[str, Any], examples: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is model.json and examples.json. -->", "",
        "# Complete revised Relation Kind model", "",
        "This candidate presents every normalized Relation Kind needed by the current repository model. Nothing in this candidate is admitted.", "",
        f"**Total:** {model['counts']['relation_kinds']} = {model['counts']['preserved']} preserved + {model['counts']['revised']} revised + {model['counts']['new']} new.", "",
        "## All relations", "",
        "| # | Group | Relation | State | Source kinds | Target kinds | Meaning | Required qualifiers |", "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, item in enumerate(model["entries"], 1):
        qualifiers = ", ".join(f"`{x}`" for x in item["required_qualifiers"]) or "none"
        lines.append(f"| {index} | {item['group']} | `{item['relation_kind_id']}` | `{item['revision_state']}` | {', '.join(f'`{x}`' for x in item['source_kinds'])} | {', '.join(f'`{x}`' for x in item['target_kinds'])} | {item['meaning']} | {qualifiers} |")
    lines += ["", "## Repository alias and residue reconciliation", "", "| Observed term | Disposition | Canonical relation |", "| --- | --- | --- |"]
    for item in model["repository_relation_residue"]:
        lines.append(f"| `{item['observed']}` | `{item['disposition']}` | {', '.join(f'`{x}`' for x in item['canonical'])} |")
    lines += ["", "## Examples", ""]
    for index, item in enumerate(model["entries"], 1):
        example = examples[item["relation_kind_id"]]
        lines += [f"### {index}. `{item['relation_kind_id']}`", "", item["meaning"], "", "```json", json.dumps(example, indent=2, sort_keys=True), "```", ""]
    lines += ["## Claim ceiling", "", model["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> int:
    build()
    result = subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
