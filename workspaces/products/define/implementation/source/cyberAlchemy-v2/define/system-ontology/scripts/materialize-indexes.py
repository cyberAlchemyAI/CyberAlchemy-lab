#!/usr/bin/env python3
"""Deterministically project the per-node DomainSpec source into checked indexes."""

from __future__ import annotations

import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent
FEATURE_ROOT = PACKAGE / "domainspec-project/specs/define-session-runtime"

NEW_DESIGN_NODES = {
    "define-session-runtime.AdditionalContextRequested",
    "define-session-runtime.ActorAccessContext",
    "define-session-runtime.DefineRuntimeInterface",
    "define-session-runtime.ExpectedRevisionRule",
    "define-session-runtime.IdempotentCommandRule",
    "define-session-runtime.InteractionAccessibilityPolicy",
    "define-session-runtime.ProportionateGovernancePolicy",
    "define-session-runtime.RuntimeHealth",
    "define-session-runtime.RuntimeSloPolicy",
    "define-session-runtime.RuntimeTelemetryPolicy",
    "define-session-runtime.SaveSession",
    "define-session-runtime.SessionAccessPolicy",
    "define-session-runtime.SessionPersistenceMapping",
    "define-session-runtime.SessionRepositoryInterface",
    "define-session-runtime.SessionRetentionPolicy",
    "define-session-runtime.SessionRevision",
    "define-session-runtime.SessionSaved",
    "define-session-runtime.SessionSchemaVersion",
    "define-session-runtime.SessionTransportInterface",
    "define-session-runtime.SessionWriteRejected",
    "define-session-runtime.ContextCandidate",
    "define-session-runtime.ContextResolutionPolicy",
    "define-session-runtime.ContextSourceKind",
    "define-session-runtime.ContextSufficiencyEvaluation",
    "define-session-runtime.ContextSufficiencyStatus",
    "define-session-runtime.EvaluateContextSufficiency",
    "define-session-runtime.RequestAdditionalContext",
    "define-session-runtime.ResolveIntentContext",
    "define-session-runtime.SemanticEvaluatorInterface",
}

CONTEXT_DESIGN_NODES = {
    "define-session-runtime.AdditionalContextRequested",
    "define-session-runtime.ContextCandidate",
    "define-session-runtime.ContextResolutionPolicy",
    "define-session-runtime.ContextSourceKind",
    "define-session-runtime.ContextSufficiencyEvaluation",
    "define-session-runtime.ContextSufficiencyStatus",
    "define-session-runtime.EvaluateContextSufficiency",
    "define-session-runtime.RequestAdditionalContext",
    "define-session-runtime.ResolveIntentContext",
    "define-session-runtime.SemanticEvaluatorInterface",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


feature = load(FEATURE_ROOT / "feature.json")
nodes = [load(FEATURE_ROOT / relative) for relative in feature["node_sources"]]
node_paths = {
    node["node_id"]: f"domainspec-project/specs/define-session-runtime/{relative}"
    for node, relative in zip(nodes, feature["node_sources"])
}

node_rows = []
relation_rows = []
for node in nodes:
    source_refs = [
        "define.interaction",
        "define.lifecycle",
        "domainspec.current-implementation",
        "domainspec.formation-projection",
    ]
    if node["node_id"] in NEW_DESIGN_NODES:
        source_refs = [
            "define.interaction",
            "define.lifecycle",
            "define.authority",
            "domainspec.architecture-ontology",
            "domainspec.bte-design",
            "domainspec.current-implementation",
            "domainspec.formation-projection",
        ]
    if node["node_id"] in CONTEXT_DESIGN_NODES:
        source_refs = [
            "define.capability",
            "define.interaction",
            "define.definition-pack",
            "reasoning.semantic-evaluator-witness",
            "domainspec.architecture-ontology",
            "domainspec.current-implementation",
            "domainspec.formation-projection",
        ]
    node_rows.append(
        {
            "node_id": node["node_id"],
            "source_path": node_paths[node["node_id"]],
            "kind": node["kind"],
            "intent": node["intent"],
            "status": "candidate",
            "implementation_status": "not-implemented",
            "source_refs": source_refs,
            "evidence_confidence": "high",
            "commitment_confidence": "candidate",
            "authority_effect": "none",
        }
    )
    for edge in node["connections"]:
        relation_rows.append(
            {
                "relation_id": edge["edge_id"],
                "type": edge["type"],
                "from_node_id": node["node_id"],
                "to_node_id": edge["to"],
                "source_node_path": node_paths[node["node_id"]],
                "status": "candidate",
                "source_refs": ["define.interaction", "domainspec.relationships"],
                "authority_effect": "none",
            }
        )

dump(
    PACKAGE / "NODES.json",
    {
        "$schema": "schemas/ontology-package.schema.json#/$defs/nodes",
        "schema_version": "cav2.define.system-ontology.nodes/v1",
        "nodes": node_rows,
    },
)
dump(
    PACKAGE / "RELATIONS.json",
    {
        "$schema": "schemas/ontology-package.schema.json#/$defs/relations",
        "schema_version": "cav2.define.system-ontology.relations/v1",
        "relations": relation_rows,
    },
)
