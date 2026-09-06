#!/usr/bin/env python3
"""Render the human view for CAL-PROP-0004 from its canonical JSON."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "proposal.json"
TARGET = ROOT / "PROPOSAL.md"


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def render() -> str:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    proposal = data["proposal"]
    lines: list[str] = [
        "<!-- Generated from proposal.json by render.py. Do not edit this projection directly. -->",
        "",
        f"# {data['title']}",
        "",
        f"- Proposal: `{data['proposal_id']}`",
        f"- Schema: `{data['schema_version']}`",
        f"- Status: `{data['status']}`",
        f"- Decision posture: `{data['decision_posture']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "> This is an unselected successor architecture candidate. It does not rewrite the immutable selected baseline or authorize schema, runtime, migration, publication, release, or deployment effects.",
        "",
        "## Immutable predecessor",
        "",
        f"- Proposal: `{data['predecessor']['proposal_id']}`",
        f"- Path: `{data['predecessor']['path']}`",
        f"- SHA-256: `{data['predecessor']['sha256']}`",
        f"- Posture: `{data['predecessor']['posture']}`",
        f"- Rule: {data['predecessor']['mutation_rule']}",
        "",
        "## Decision question",
        "",
        proposal["decision_question"],
        "",
        "## Recommendation",
        "",
        proposal["recommendation"],
        "",
        "## Convention change",
        "",
        f"- Current rule: {proposal['current_rule']}",
        f"- Proposed rule: {proposal['proposed_rule']}",
        "",
        "## Governed ontology node view",
        "",
        "```text",
        "canonical semantic events ──> SemanticNodeState",
        "                                    │",
        "separate governance events ──> GovernanceState",
        "                                    │ exact semantic event ID + digest + cursor",
        "                                    ▼",
        "                         GovernedOntologyNodeView",
        "                                    │ exact Context selector",
        "                                    ▼",
        "                           bounded Context projection",
        "```",
        "",
    ]

    for title, key in (
        ("Identity", "identity"),
        ("Semantic state", "semantic_state"),
        ("Governance state", "governance_state"),
        ("Projection metadata", "projection_metadata"),
    ):
        lines.extend([f"### {title}", "", bullets(proposal["governed_node_view"][key]), ""])

    challenge = proposal["challenge_contract"]
    lines.extend([
        "## Challenge contract",
        "",
        f"- Definition reference: `{challenge['definition_ref']}`",
        f"- Required when: {challenge['required_when']}",
        f"- Boundary: {challenge['boundary']}",
        "",
        "Required fields:",
        "",
        bullets(challenge["fields"]),
        "",
        "Valid challenge modes:",
        "",
        bullets(challenge["valid_challenge_modes"]),
        "",
        "## Typed ontology profiles",
        "",
    ])
    for profile in proposal["typed_profiles"]:
        fields = profile.get("additional_semantic_requirements", []) + profile.get("additional_governance_requirements", []) + profile.get("additional_projection_requirements", [])
        lines.append(f"- `{profile['profile']}`: {', '.join(fields)}")

    relation = proposal["relation_rule"]
    event_topology = proposal["event_topology"]
    lines.extend([
        "",
        "## Relation architecture",
        "",
        f"- Canonicality: {relation['canonicality']}",
        f"- Integrity: {relation['integrity']}",
        f"- Challenge edges: {relation['challenge_edge_rule']}",
        f"- Cycle rule: {relation['cycle_rule']}",
        "",
        "Minimum relation state:",
        "",
        bullets(relation["minimum_state"]),
        "",
        "## Event topology",
        "",
        f"- Semantic stream: {event_topology['semantic_stream']}",
        f"- Governance stream: {event_topology['governance_stream']}",
        f"- Challenge revision: {event_topology['semantic_change_after_challenge']}",
        f"- Calculated view: {event_topology['calculated_view']}",
        f"- Failure policy: {event_topology['failure_policy']}",
        "",
        "## Context interaction",
        "",
        bullets(proposal["context_interaction"]),
        "",
        "## Invariants",
        "",
        bullets(proposal["invariants"]),
        "",
        "## Migration impact",
        "",
        bullets(proposal["migration_impact"]),
        "",
        "## Required successors",
        "",
        bullets(proposal["required_successors"]),
        "",
        "## Rollback",
        "",
        proposal["rollback"],
        "",
        "## Typed residue",
        "",
    ])
    for residue in data["typed_residue"]:
        lines.extend([
            f"### {residue['residue']}",
            "",
            f"- Owner needed: {residue['owner_needed']}",
            f"- Effect: {residue['effect']}",
            "",
        ])

    lines.extend(["## Claim ceiling", "", data["claim_ceiling"], ""])
    return "\n".join(lines)


if __name__ == "__main__":
    TARGET.write_text(render(), encoding="utf-8")
