#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

import generator


ROOT = Path(__file__).resolve().parent


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def mutate(base: dict, **updates) -> dict:
    value = copy.deepcopy(base)
    value.update(updates)
    return value


def main() -> int:
    generator_sha = "b314fb28c2319ff0f1c2c79cba1f36968ea5c4ca5a7c71aeeb06ed2f1941591b"
    base = {
        "schema_version": "cyberalchemy-lab-coordination-context/v2",
        "coordination_context_id": "coordination:lab-integrated-model/v1",
        "version": "1.0.0-candidate.1",
        "status": "candidate-unadmitted",
        "authority_effect": "none",
        "classification": {
            "artifact_type_ref": "cal.artifact-type.coordination-context/v2",
            "semantic_kind": "coordination-context",
            "authority_kind": "none",
            "lifecycle_posture_ref": "cal.lifecycle.artifact/v1:candidate-authored",
        },
        "product_ref": "product:cyberalchemy-lab/v1",
        "project_ref": "project:integrated-lab-model/v1",
        "goal_ref": "goal:admit-complete-lab-model/v1",
        "purpose": "Coordinate completion and admission of the integrated CyberAlchemy Lab model.",
        "consumer_refs": ["person:vrondelli", "agent-role:repository-modeling-agent"],
        "intended_uses": ["Artifact Type review", "Admission decision preparation"],
        "subject_scope": {
            "statement": "Definitions, Artifact Types, Relation Kinds, ontology integration, and lifecycle behavior.",
            "exclusions": ["Runtime activation", "Deployment authority", "Transient Agent Session memory"],
        },
        "source_policy_refs": ["policy:admitted-authority-first", "policy:exact-digest-provenance"],
        "bounded_context_refs": ["bounded-context:semantic-governance/v2", "bounded-context:ontology-lifecycle/v2"],
        "owner_ref": "role:lab-architecture-owner",
        "owner_route": "route:lab-architecture-owner",
        "lifecycle_state": "active",
        "predecessor_ref": None,
        "revision_history": [],
        "challenge_route": "route:coordination-context-challenge",
        "evidence_refs": ["audit:cal-coordination-context-non-collapse-0001"],
        "residue_refs": ["residue:relation-endpoint-admission-required"],
        "source_direction": {
            "canonical": "coordination-context.json",
            "human_projection": "COORDINATION-CONTEXT.md",
            "projection_policy": "generated-only",
            "generator_ref": "cal.generator.coordination-context-v2/v1",
            "generator_sha256": generator_sha,
        },
        "claim_ceiling": "This Coordination Context frames work on the integrated Lab model. It does not own referenced endpoints, grant execution authority, admit artifacts, or retain an Agent Session.",
    }
    valid = {
        "product-only": mutate(base, project_ref=None, goal_ref=None),
        "product-project": mutate(base, goal_ref=None),
        "product-goal": mutate(base, project_ref=None),
        "product-project-goal": base,
    }
    for name, instance in valid.items():
        write(ROOT / f"fixtures/valid/{name}.json", instance)

    hostile = {
        "missing-product": {k: v for k, v in base.items() if k != "product_ref"},
        "multiple-products": mutate(base, product_ref=["product:a", "product:b"]),
        "multiple-projects": mutate(base, project_ref=["project:a", "project:b"]),
        "multiple-goals": mutate(base, goal_ref=["goal:a", "goal:b"]),
        "embedded-product": mutate(base, product={"product_id": "product:embedded"}),
        "embedded-project": mutate(base, project={"project_id": "project:embedded"}),
        "embedded-goal": mutate(base, goal={"goal_id": "goal:embedded"}),
        "bounded-context-ownership": mutate(base, domain_model_ref="model:collapsed", ubiquitous_language_ref="language:collapsed"),
        "generic-context-collapse": mutate(base, context_id="context:collapsed", profile_ref="profile:x"),
        "context-view-collapse": mutate(base, context_view_id="view:collapsed", included_material=[]),
        "agent-session-collapse": mutate(base, agent_session_ref="session:ephemeral", short_term_memory=["transient"]),
        "work-execution-collapse": mutate(base, work_ref="work:run", execution_authority="approved"),
        "source-selection-collapse": mutate(base, source_selection={"selected_sources": ["source:a"]}),
        "identity-equals-product": mutate(base, coordination_context_id=base["product_ref"]),
        "identity-equals-project": mutate(base, coordination_context_id=base["project_ref"]),
        "identity-equals-goal": mutate(base, coordination_context_id=base["goal_ref"]),
        "identity-equals-bounded-context": mutate(base, coordination_context_id=base["bounded_context_refs"][0]),
        "owner-equals-product": mutate(base, owner_ref=base["product_ref"]),
    }
    for name, instance in hostile.items():
        write(ROOT / f"fixtures/invalid/{name}.json", instance)

    lifecycle = {
        "schema_version": "cyberalchemy-lab-coordination-context-lifecycle-fixtures/v1",
        "base": base,
        "cases": [
            {"case_id": "same-id-product-change", "after": mutate(base, product_ref="product:changed/v1"), "expected": "successor-required"},
            {"case_id": "same-id-project-change", "after": mutate(base, project_ref="project:changed/v1"), "expected": "successor-required"},
            {"case_id": "same-id-goal-change", "after": mutate(base, goal_ref="goal:changed/v1"), "expected": "successor-required"},
            {"case_id": "same-id-purpose-change", "after": mutate(base, purpose="A materially different durable purpose."), "expected": "successor-required"},
            {"case_id": "new-id-anchor-change", "after": mutate(base, coordination_context_id="coordination:lab-integrated-model/v2", product_ref="product:changed/v1", predecessor_ref=base["coordination_context_id"]), "expected": "successor-identity-present"},
            {"case_id": "same-id-source-policy-revision", "after": mutate(base, source_policy_refs=["policy:admitted-authority-first/v2"], revision_history=[{"revision": "2", "decision_ref": "decision:source-policy-update", "changed_fields": ["source_policy_refs"]}]), "expected": "same-identity-revision-permitted"}
        ]
    }
    write(ROOT / "fixtures/lifecycle/cases.json", lifecycle)
    (ROOT / "fixtures/valid/COORDINATION-CONTEXT.md").write_text(generator.render_instance(base))
    artifact = json.loads((ROOT / "artifact.json").read_text())
    (ROOT / "ARTIFACT.md").write_text(generator.render_artifact(artifact))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
