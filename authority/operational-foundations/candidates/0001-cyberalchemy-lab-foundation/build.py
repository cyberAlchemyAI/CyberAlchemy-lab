#!/usr/bin/env python3
"""Build the smallest real CyberAlchemy Lab operational foundation candidate."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
ARTIFACTS = ROOT / "instances" / "artifacts"
RELATIONS = ROOT / "instances" / "typed-relations"
REGISTRY = LAB / "authority/admissions/definition-complete-lab-model/v1/artifact-type-registry.json"
RELATION_REGISTRY = LAB / "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json"
MODEL_BUNDLE = LAB / "authority/admissions/definition-complete-lab-model/v1/bundle.json"
OWNER = "role:repository-owner"
SCOPE = "scope:cyberalchemy-lab-operational-foundation"
INTENT = "intent:establish-cyberalchemy-lab-operational-foundation"
PRODUCT = "product:cyberalchemy-lab"
THESIS = "product-thesis:cyberalchemy-lab-governed-work"
CAPABILITY = "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"
PROJECT = "project:cyberalchemy-v2-to-lab-migration"
POLICY = "policy:cyberalchemy-lab-operational-foundation"
CHALLENGE = "challenge-contract:cyberalchemy-lab-operational-foundation"
PROJECT_STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0070"
CONTEXT = "context:cyberalchemy-v2-to-lab-migration"
SEMANTIC_HISTORY = "semantic-history:cyberalchemy-v2-to-lab-migration"
GOVERNANCE_HISTORY = "governance-history:cyberalchemy-v2-to-lab-migration"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_value(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def merge(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge(target[key], value)
        else:
            target[key] = copy.deepcopy(value)
    return target


registry = load(REGISTRY)
contracts = {
    item["artifact_type_ref"]: item
    for item in registry["admitted_contracts"]
    if item["lifecycle_state"] == "admitted-current"
}


def fixture(type_ref: str) -> dict[str, Any]:
    contract = contracts[type_ref]
    descriptor_path = LAB / contract["artifact_path"]
    descriptor = load(descriptor_path)
    filename = descriptor["instance_contract"]["canonical_filename"]
    return load(descriptor_path.parent / "fixtures" / "valid" / filename)


artifact_entries: list[dict[str, Any]] = []
artifact_index: dict[str, dict[str, Any]] = {}
relation_entries: list[dict[str, Any]] = []


def add_artifact(slug: str, type_ref: str, kind: str, patch: dict[str, Any]) -> None:
    record = merge(fixture(type_ref), patch)
    if "relation_refs" in record:
        record["relation_refs"] = []
    identity = record.get("node_id") or record.get("product_id") or record.get("project_id")
    if not identity or identity in artifact_index:
        raise ValueError(f"invalid or duplicate identity for {slug}: {identity}")
    path = ARTIFACTS / f"{slug}.json"
    dump(path, record)
    entry = {
        "carrier_type_ref": type_ref,
        "identity_ref": identity,
        "path": str(path.relative_to(LAB)),
        "semantic_kind": kind,
        "sha256": sha(path),
        "version_ref": f"{identity}@foundation.1",
    }
    artifact_entries.append(entry)
    artifact_index[identity] = entry


def build_artifacts() -> None:
    add_artifact(
        "intent",
        "cal.artifact-type.intent/v1",
        "intent",
        {
            "node_id": INTENT,
            "direction": "Establish the minimum governed state from which CyberAlchemy Lab can perform real work and generate trustworthy successor state, Agent context, evidence, and ontology projections.",
            "motivation": "The admitted Lab model defines contracts, but future work needs a durable Product, Project, governance, state, and context root.",
            "target_pressure": "Without an admitted operational root, future instances have no single durable state boundary or explicit generation rules.",
            "scope_ref": SCOPE,
            "owner_ref": OWNER,
            "attributed_to": "person-reference:repository-owner",
            "review_route": "docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/DECISION.md",
            "revision_route": "route:repository-owner-review",
            "current_output_hypothesis": {
                "artifact_type_ref": "cal.artifact-type.project-state/v1",
                "description": "One admitted initial Project State, governed Context, and typed semantic root are sufficient to begin real work without fabricating runtime activity.",
            },
            "constraints": [
                "Use only admitted-current Artifact Type and Relation Kind contracts",
                "Make Project State the durable continuity owner",
                "Keep machine Agents ephemeral and session memory short lived",
                "Generate evidence and ontology projections only from real future events",
                "Keep derived Context and Ontology Views non-authoritative",
            ],
            "intent_state": "active",
            "satisfaction_refs": [],
            "successor_refs": [],
            "revision_history": [],
        },
    )
    add_artifact(
        "product",
        "cal.artifact-type.product-identity/v2",
        "product",
        {
            "product_id": PRODUCT,
            "version": "2.0.0-foundation.1",
            "name": "CyberAlchemy Lab",
            "purpose": "Provide a governed repository laboratory for reconstructing, testing, and evolving CyberAlchemy knowledge and work contracts.",
            "value_promise": "Repository owners and collaborators can understand current meaning, state, evidence, authority, and unresolved residue through inspectable governed artifacts.",
            "scope": {
                "includes": ["Governed knowledge and artifact lifecycle", "Typed semantic connections", "Evidence-bound human and machine collaboration"],
                "excludes": ["Any one migration Project", "Any one implementation", "Automatic authority", "Unverified external runtime behavior"],
            },
            "semantic_owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "lineage_ref": "lineage:cyberalchemy-v2-to-lab-product",
            "current_thesis_ref": THESIS,
            "evidence_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Admitted Product identity and boundary; it does not prove Product value or activate a runtime.",
        },
    )
    add_artifact(
        "product-thesis",
        "cal.artifact-type.product-thesis/v1",
        "product-thesis",
        {
            "node_id": THESIS,
            "product_ref": PRODUCT,
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "scope_ref": SCOPE,
            "problem": "Repository decisions, evidence, implementations, and machine work can drift apart, leaving current meaning and authority unclear.",
            "value_proposition": "CyberAlchemy Lab keeps meaning, evidence, authority, execution, and derived views inspectable while humans and ephemeral Agents collaborate.",
            "value_mechanism": "Admitted contracts, exact Typed Relations, event-bound ontology projections, bounded Context Views, and explicit owner decisions preserve distinctions and traceability.",
            "audience": "Repository owners and human-machine engineering teams",
            "participants": ["repository owners", "project owners", "researchers", "ephemeral machine Agents"],
            "assumptions": ["Explicit distinctions reduce semantic drift", "Evidence-bound views improve Agent continuity", "Human owners retain consequential authority"],
            "first_order_principles": ["Project State owns durable continuity", "Session memory expires with the Agent Session", "Derived views do not become authority", "Every connection uses an admitted Relation Kind"],
            "intended_outcomes": [
                {"outcome_id": f"{THESIS}#inspectable-state", "statement": "Current meaning, evidence, and decision state are inspectable.", "value_measure_refs": ["measurement-method:state-findability"]},
                {"outcome_id": f"{THESIS}#bounded-agent-work", "statement": "Ephemeral Agents work from bounded views without owning durable memory.", "value_measure_refs": ["measurement-method:agent-boundary-preservation"]},
            ],
            "hypotheses": [{"hypothesis_id": "lab-thesis-h1", "statement": "A typed, evidence-bound repository model reduces semantic ambiguity enough to justify its governance cost.", "evidence_state": "untested"}],
            "boundaries": ["This foundation does not prove Product value", "Schema validation does not prove runtime behavior", "The Product remains distinct from the migration Project"],
            "revision_criteria": ["Users cannot locate authoritative state", "Typed distinctions add burden without improving decisions", "A simpler model preserves equivalent traceability"],
            "evidence_routes": ["route:project-evidence"],
            "counterevidence_routes": ["route:foundation-challenge"],
            "challenge_route": CHALLENGE,
        },
    )
    add_artifact(
        "product-capability",
        "cal.artifact-type.product-capability/v1",
        "product-capability",
        {
            "node_id": CAPABILITY,
            "name": "Governed Knowledge Lifecycle",
            "product_ref": PRODUCT,
            "product_thesis_ref": THESIS,
            "thesis_outcome_refs": [f"{THESIS}#inspectable-state", f"{THESIS}#bounded-agent-work"],
            "outcome": "A repository participant can reconstruct current governed state, trace exact semantic connections, and provide bounded views to an ephemeral Agent.",
            "acceptance_conditions": ["Every persisted artifact validates against its admitted-current contract", "Every global connection is an admitted Typed Relation", "Every derived view binds exact source digests and cursors", "No Agent owns durable Project memory"],
            "exclusions": ["Migration completion", "Persistent machine Agent identity", "Automatic authority", "Live service activation"],
            "input_contract_refs": ["contract:admitted-artifact-type-registry", "contract:admitted-relation-kind-registry"],
            "output_contract_refs": ["contract:governed-project-state", "contract:bounded-agent-context", "contract:evidence-lineage", "contract:ontology-projection"],
            "context_policy_refs": [POLICY],
            "consumer_refs": ["consumer:repository-owner", "consumer:future-agent-sessions"],
            "participant_refs": [OWNER],
            "realization_binding_refs": [],
            "owner_ref": OWNER,
            "owner_routes": ["route:repository-owner-review", CHALLENGE],
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "lifecycle_posture": {
                "kind": "product-capability",
                "status": "draft",
                "status_vocabulary_ref": "profile.capability-lifecycle",
                "owner_ref": OWNER,
                "commitment_ref": None,
                "provenance_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
                "evidence_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
                "residue_refs": ["residue:no-capability-realization-binding-yet"],
            },
        },
    )
    add_artifact(
        "project",
        "cal.artifact-type.project-identity/v1",
        "project",
        {
            "project_id": PROJECT,
            "name": "CyberAlchemy v2 to Lab migration",
            "purpose": "Coordinate the bounded reconstruction, review, admission, and operational proving of CyberAlchemy v2 knowledge in CyberAlchemy Lab.",
            "coordination_scope": {
                "includes": ["Migration inventory", "Semantic reconstruction", "Candidate validation", "Owner admission", "Successor Project State"],
                "excludes": ["CyberAlchemy Lab Product identity", "Automatic migration completion", "Runtime cutover", "External publication"],
            },
            "accountable_owner_ref": OWNER,
            "evidence_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Admitted Project identity and coordination boundary; it does not claim the migration is complete.",
        },
    )
    add_artifact(
        "policy",
        "cal.artifact-type.policy/v1",
        "policy",
        {
            "node_id": POLICY,
            "name": "CyberAlchemy Lab operational foundation policy",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
            "claim_ceiling": "Admitted governance rules for future repository records; no runtime enforcement or consumer activation is implied.",
            "payload": {
                "issuer_ref": OWNER,
                "governed_scope_ref": SCOPE,
                "rule_refs": [
                    "rule:validate-against-admitted-current-contracts",
                    "rule:admit-only-by-exact-owner-decision",
                    "rule:project-state-owns-durable-continuity",
                    "rule:agent-session-memory-expires",
                    "rule:evidence-binds-exact-sources",
                    "rule:ontology-projections-bind-event-history",
                    "rule:derived-views-have-no-authority",
                ],
                "effective_period": "from-decision-0071-until-superseded",
                "exception_route": CHALLENGE,
            },
        },
    )
    add_artifact(
        "challenge-contract",
        "cal.artifact-type.challenge-contract/v1",
        "challenge-contract",
        {
            "node_id": CHALLENGE,
            "name": "CyberAlchemy Lab operational foundation challenge contract",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": "route:repository-owner-review",
            "evidence_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
            "claim_ceiling": "Admitted contestability route; it grants no authority and resolves no challenge by itself.",
            "payload": {
                "challengeable_subject_kinds": ["artifact-instance", "typed-relation", "project-state", "context-view", "evidence", "ontology-projection"],
                "eligible_challenger_kinds": ["principal", "person-reference", "project-owner"],
                "grounds": ["evidence-conflict", "scope-error", "semantic-collapse", "stale-projection", "authority-overreach"],
                "owner_route": "route:repository-owner-review",
                "policy_ref": POLICY,
                "required_evidence_kinds": ["source", "evidence-set", "validation-receipt", "decision"],
                "resolution_gate_ref": "gate:explicit-owner-decision",
                "response_modes": ["evidence", "contradiction", "revision", "owner-review"],
                "response_period": "before-dependent-admission-or-on-next-state-transition",
                "unresolved_residue_route": "route:foundation-residue",
            },
        },
    )

    materials = [
        LAB / "docs/decisions/0065-integrated-lab-definition-model-admission/decision.json",
        LAB / "docs/decisions/0066-definition-specialization-resolution-admission/decision.json",
        LAB / "docs/decisions/0070-definition-complete-lab-model-admission/decision.json",
        MODEL_BUNDLE,
        REGISTRY,
        RELATION_REGISTRY,
        LAB / "authority/admissions/definition-complete-lab-model/v1/endpoint-inventory.json",
    ]
    snapshot = [{"path": str(path.relative_to(LAB)), "sha256": sha(path)} for path in materials]
    state_digest = digest_value(snapshot)
    add_artifact(
        "project-state",
        "cal.artifact-type.project-state/v1",
        "project-state",
        {
            "node_id": PROJECT_STATE,
            "name": "CyberAlchemy v2 migration initial operational state at Decision 0070",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": [item["path"] for item in snapshot],
            "claim_ceiling": "Initial admitted durable Project State through Decision 0070. Decision 0071 and later work belong in successor state, never in-place mutation.",
            "payload": {
                "project_ref": PROJECT,
                "cursor": "decision:0070",
                "state_digest": f"sha256:{state_digest}",
                "artifact_refs": [item["path"] for item in snapshot],
                "decision_refs": [
                    "CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION",
                    "CAL-DECISION-0066-DEFINITION-SPECIALIZATION-RESOLUTION-ADMISSION",
                    "CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION",
                ],
                "semantic_history_ref": SEMANTIC_HISTORY,
                "governance_history_ref": GOVERNANCE_HISTORY,
            },
        },
    )
    add_artifact(
        "context",
        "cal.artifact-type.context/v1",
        "context",
        {
            "node_id": CONTEXT,
            "context_kind": "project",
            "purpose": "Select the admitted model, current Project State, evidence, and relevant ontology material needed for bounded future work on the migration Project.",
            "subject_scope": ["CyberAlchemy Lab Product direction", "CyberAlchemy v2 migration Project", "Current admitted Project State", "Task-specific evidence and ontology projections"],
            "bounded_context_refs": ["bounded-context:semantic-governance"],
            "goal_ref": None,
            "product_ref": PRODUCT,
            "project_ref": PROJECT,
            "consumer_refs": ["consumer:future-bounded-agent-sessions", "consumer:repository-owner-review"],
            "intended_uses": ["Build Context Requests", "Generate immutable Context Views", "Prepare Agent Sessions", "Review Project State successors"],
            "source_policy_refs": [POLICY],
            "profile_ref": "context-profile:project-operational-foundation",
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Admitted reusable Context boundary. It is not a resolved Context View, Project State, Agent memory, or source authority.",
            "lifecycle_state": "active",
            "revision_history": [],
            "successor_refs": [],
        },
    )

    declarations = {
        "schema_version": "cyberalchemy-lab-project-history-declarations/v1",
        "project_ref": PROJECT,
        "project_state_ref": PROJECT_STATE,
        "streams": [
            {"history_ref": SEMANTIC_HISTORY, "history_class": "semantic", "cursor": 0, "state": "initialized-empty", "runtime_active": False},
            {"history_ref": GOVERNANCE_HISTORY, "history_class": "governance", "cursor": 0, "state": "initialized-empty", "runtime_active": False},
        ],
        "first_successor_obligation": "Decision 0071 and its exact admission bundle must be appended through governed semantic and governance events before a successor Project State is admitted.",
        "claim_ceiling": "Declares empty logical history streams referenced by the initial Project State. It does not claim event instances or an active runtime.",
    }
    dump(ROOT / "history-declarations.json", declarations)


def relation_specs() -> list[tuple[str, str, str, str, str, str, dict[str, str]]]:
    return [
        ("product-addresses-intent", "relation.addresses-intent", "product", PRODUCT, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:foundation-admission", "addressing_role": "product-direction"}),
        ("thesis-member-of-product", "relation.member-of", "product-thesis", THESIS, "product", PRODUCT, {"membership_role": "current-product-thesis"}),
        ("capability-member-of-product", "relation.member-of", "product-capability", CAPABILITY, "product", PRODUCT, {"membership_role": "product-capability"}),
        ("capability-derives-from-thesis", "relation.derives-from", "product-capability", CAPABILITY, "product-thesis", THESIS, {"derivation_role": "thesis-outcome-realization"}),
        ("capability-addresses-intent", "relation.addresses-intent", "product-capability", CAPABILITY, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:foundation-admission", "addressing_role": "repeatable-product-outcome"}),
        ("project-contributes-to-product", "relation.contributes-to", "project", PROJECT, "product", PRODUCT, {"contribution_role": "migration-and-operational-model-development", "contribution_scope": SCOPE}),
        ("project-addresses-intent", "relation.addresses-intent", "project", PROJECT, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:foundation-admission", "addressing_role": "bounded-coordination"}),
        ("project-state-member-of-project", "relation.member-of", "project-state", PROJECT_STATE, "project", PROJECT, {"membership_role": "durable-project-state"}),
        ("context-member-of-project", "relation.member-of", "context", CONTEXT, "project", PROJECT, {"membership_role": "reusable-project-context"}),
        ("context-frames-product", "relation.frames", "context", CONTEXT, "product", PRODUCT, {"framing_role": "product-relevance-boundary"}),
        ("context-frames-project", "relation.frames", "context", CONTEXT, "project", PROJECT, {"framing_role": "project-relevance-boundary"}),
        ("context-governed-by-policy", "relation.governed-by", "context", CONTEXT, "policy", POLICY, {"governance_role": "context-and-view-generation-policy"}),
        ("challenge-governed-by-policy", "relation.governed-by", "challenge-contract", CHALLENGE, "policy", POLICY, {"governance_role": "foundation-contestability-policy"}),
    ]


def bind_relation_refs() -> None:
    bindings: dict[str, list[dict[str, str]]] = {}
    for _, kind, source_kind, source_ref, target_kind, target_ref, _ in relation_specs():
        bindings.setdefault(source_ref, []).append({"counterpart_kind": target_kind, "counterpart_ref": target_ref, "direction": "source", "relation_kind_ref": kind})
        bindings.setdefault(target_ref, []).append({"counterpart_kind": source_kind, "counterpart_ref": source_ref, "direction": "target", "relation_kind_ref": kind})
    for identity, entry in artifact_index.items():
        path = LAB / entry["path"]
        record = load(path)
        if "relation_refs" not in record:
            continue
        descriptor = load(LAB / contracts[entry["carrier_type_ref"]]["artifact_path"])
        roles = descriptor.get("relation_roles", [])
        record["relation_refs"] = [
            binding
            for binding in bindings.get(identity, [])
            if any(
                role["relation_kind_ref"] == binding["relation_kind_ref"]
                and role["direction"] == binding["direction"]
                and binding["counterpart_kind"] in role["counterpart_kinds"]
                for role in roles
            )
        ]
        dump(path, record)
        entry["sha256"] = sha(path)


def build_relations() -> None:
    for slug, kind, source_kind, source_ref, target_kind, target_ref, qualifiers in relation_specs():
        record = merge(
            fixture("cal.artifact-type.typed-relation/v2"),
            {
                "node_id": f"typed-relation:operational-foundation:{slug}",
                "name": f"Operational foundation {kind}",
                "owner_ref": OWNER,
                "scope_ref": SCOPE,
                "challenge_route": CHALLENGE,
                "evidence_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
                "claim_ceiling": "Exact global Typed Relation between two admitted foundation instances; it implies only its declared relation axis and qualifiers.",
                "payload": {
                    "relation_kind_ref": kind,
                    "relation_lifecycle_state": "candidate",
                    "source": {"kind": source_kind, "ref": source_ref, "version_ref": artifact_index[source_ref]["version_ref"]},
                    "target": {"kind": target_kind, "ref": target_ref, "version_ref": artifact_index[target_ref]["version_ref"]},
                    "qualifiers": qualifiers,
                    "relation_evidence_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
                },
                "relation_refs": [],
            },
        )
        record["payload"]["qualifiers"] = copy.deepcopy(qualifiers)
        path = RELATIONS / f"{slug}.json"
        dump(path, record)
        relation_entries.append(
            {
                "relation_id": record["node_id"],
                "relation_kind_ref": kind,
                "path": str(path.relative_to(LAB)),
                "sha256": sha(path),
                "source_kind": source_kind,
                "source_ref": source_ref,
                "target_kind": target_kind,
                "target_ref": target_ref,
                "version_ref": f"{record['node_id']}@foundation.1",
            }
        )


def build_manifest() -> None:
    history_path = ROOT / "history-declarations.json"
    manifest = {
        "schema_version": "cyberalchemy-lab-operational-foundation/v1",
        "foundation_id": "CAL-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-0001",
        "name": "CyberAlchemy Lab operational foundation",
        "status": "candidate-awaiting-admission",
        "authority_effect": "none",
        "owner_ref": OWNER,
        "scope_ref": SCOPE,
        "inputs": {
            "definition_complete_bundle": {"path": str(MODEL_BUNDLE.relative_to(LAB)), "sha256": sha(MODEL_BUNDLE)},
            "artifact_type_registry": {"path": str(REGISTRY.relative_to(LAB)), "sha256": sha(REGISTRY)},
            "relation_kind_registry": {"path": str(RELATION_REGISTRY.relative_to(LAB)), "sha256": sha(RELATION_REGISTRY)},
        },
        "counts": {"artifact_instances": len(artifact_entries), "typed_relation_instances": len(relation_entries), "history_stream_declarations": 2, "runtime_activations": 0},
        "artifacts": artifact_entries,
        "typed_relations": relation_entries,
        "history_declarations": {"path": str(history_path.relative_to(LAB)), "sha256": sha(history_path)},
        "generation_contracts": {
            "project_state": "Every governed write produces an immutable successor Project State and appends its semantic and governance events; admitted state is never mutated in place.",
            "agent_context": "A future task creates a Context Request, immutable Context View, Agent Instance, and Agent Session. Session memory expires; durable continuity remains Project State.",
            "evidence": "Real work creates exact Sources and observations or measurements, then an Evidence Set whose members and lineage are digest-bound before Findings are asserted.",
            "ontology": "Semantic and governance event histories are replay sources. Ontology Nodes and Edges bind exact subjects and Typed Relations; Cuts and Views are derived and non-authoritative.",
        },
        "excluded_instances": ["agent-instance", "agent-session", "context-request", "context-view", "source", "evidence-set", "finding", "ontology-node", "ontology-edge", "ontology-cut", "ontology-view", "implementation", "capability-realization-binding"],
        "excluded_effects": ["No Agent or session is activated", "No evidence or ontology projection is fabricated", "No implementation or capability realization is adopted", "No migration, cutover, deployment, publication, or external effect occurs"],
        "claim_ceiling": "This candidate establishes only the durable operational roots and closed generation rules. Until Decision 0071 is applied, it has no authority effect.",
    }
    dump(ROOT / "foundation.json", manifest)
    lines = [
        "<!-- GENERATED FILE: canonical data is foundation.json and bound instance records. -->",
        "",
        "# CyberAlchemy Lab operational foundation",
        "",
        "This is the minimum durable root for real Lab work.",
        "",
        f"- Artifact instances: `{len(artifact_entries)}`",
        f"- Typed Relations: `{len(relation_entries)}`",
        "- Declared empty history streams: `2`",
        "- Runtime activations: `0`",
        "",
        "## Durable roots",
        "",
        "| Kind | Identity |",
        "|---|---|",
    ]
    lines.extend(f"| `{item['semantic_kind']}` | `{item['identity_ref']}` |" for item in artifact_entries)
    lines.extend(["", "## What future work generates", ""])
    for key, value in manifest["generation_contracts"].items():
        lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
    lines.extend(["", "## Admission boundary", "", manifest["claim_ceiling"], ""])
    (ROOT / "FOUNDATION.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    for path in (ARTIFACTS, RELATIONS):
        if path.exists():
            shutil.rmtree(path)
    artifact_entries.clear()
    artifact_index.clear()
    relation_entries.clear()
    build_artifacts()
    bind_relation_refs()
    build_relations()
    build_manifest()
    print(json.dumps(load(ROOT / "foundation.json")["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
