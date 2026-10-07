#!/usr/bin/env python3
"""Build the first definition-complete CyberAlchemy Lab reference instance slice."""

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
ONTOLOGY = ROOT / "ontology"
REGISTRY_PATH = LAB / "authority/admissions/definition-complete-lab-model/v1/artifact-type-registry.json"
RELATION_REGISTRY_PATH = LAB / "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json"
BUNDLE_PATH = LAB / "authority/admissions/definition-complete-lab-model/v1/bundle.json"
SCOPE = "scope:cyberalchemy-lab-reference-slice"
OWNER = "role:repository-owner"
CHALLENGE = "challenge-contract:cyberalchemy-lab-reference-slice"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def merge(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge(target[key], value)
        else:
            target[key] = copy.deepcopy(value)
    return target


registry = load(REGISTRY_PATH)
contracts = {x["artifact_type_ref"]: x for x in registry["admitted_contracts"] if x["lifecycle_state"] == "admitted-current"}


def fixture(type_ref: str) -> dict[str, Any]:
    contract = contracts[type_ref]
    artifact_path = LAB / contract["artifact_path"]
    descriptor = load(artifact_path)
    canonical_name = descriptor["instance_contract"]["canonical_filename"]
    return load(artifact_path.parent / "fixtures" / "valid" / canonical_name)


artifact_entries: list[dict[str, Any]] = []
artifact_index: dict[str, dict[str, Any]] = {}


def add_artifact(
    slug: str,
    type_ref: str,
    semantic_kind: str,
    patch: dict[str, Any],
) -> dict[str, Any]:
    record = merge(fixture(type_ref), patch)
    if "relation_refs" in record:
        record["relation_refs"] = []
    path = ARTIFACTS / f"{slug}.json"
    dump(path, record)
    identity = record.get("node_id") or record.get("product_id") or record.get("project_id") or record.get("goal_id")
    if not identity:
        raise ValueError(f"No identity field found for {slug}")
    if identity in artifact_index:
        raise ValueError(f"Duplicate identity {identity}")
    entry = {
        "carrier_type_ref": type_ref,
        "identity_ref": identity,
        "path": str(path.relative_to(LAB)),
        "semantic_kind": semantic_kind,
        "sha256": sha(path),
        "version_ref": f"{identity}@candidate.1",
    }
    artifact_entries.append(entry)
    artifact_index[identity] = entry
    return record


PRODUCT = "product:cyberalchemy-lab"
THESIS = "product-thesis:cyberalchemy-lab-governed-work"
CAPABILITY = "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"
PROJECT = "project:cyberalchemy-v2-to-lab-migration"
GOAL = "goal:materialize-definition-complete-reference-slice"
INTENT = "intent:operationalize-cyberalchemy-lab-model"
BINDING = "capability-realization-binding:governed-repository-toolchain"
RESEARCH = "research-inquiry:v2-to-lab-semantic-preservation"
HYPOTHESIS = "hypothesis:reference-slice-preserves-orthogonality"
DESIGN = "experiment-design:reference-slice-contract-validation"
RUN = "experiment-run:reference-slice-contract-validation:2026-10-06"
IMPLEMENTATION = "implementation:cyberalchemy-lab-governed-repository-toolchain"
WORK = "work:materialize-reference-slice-v1"
EVIDENCE = "evidence-set:reference-slice-validation"
FINDING = "finding:reference-slice-schema-and-relation-closure"
PRINCIPAL = "principal:repository-owner"
AGENT = "agent-instance:reference-slice-authoring:2026-10-06"
ASSIGNMENT = "agent-assignment:materialize-reference-slice-v1"
SESSION = "agent-session:reference-slice-authoring:2026-10-06"
PROJECT_STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0070"
CONTEXT = "context:reference-slice-authoring"
CONTEXT_REQUEST = "context-request:reference-slice-authoring"
CONTEXT_VIEW = "context-view:reference-slice-authoring:2026-10-06"
ONTOLOGY_REF = "ontology:cyberalchemy-lab-reference-slice"
POLICY = "policy:reference-slice-governance"


def build_base_artifacts() -> None:
    add_artifact(
        "intent",
        "cal.artifact-type.intent/v1",
        "intent",
        {
            "node_id": INTENT,
            "direction": "Turn the admitted definition-complete CyberAlchemy Lab model into inspectable artifact instances, exact Typed Relations, and derived Agent views.",
            "motivation": "The admitted model defines contracts, while repository users and Agents still need a concrete, reviewable operational example.",
            "target_pressure": "No admitted ordinary reference slice or Typed Relation instance currently demonstrates the integrated model.",
            "scope_ref": SCOPE,
            "owner_ref": OWNER,
            "attributed_to": "person-reference:repository-owner",
            "review_route": str(ROOT.relative_to(LAB) / "REFERENCE-SLICE.md"),
            "revision_route": "route:repository-owner-review",
            "current_output_hypothesis": {
                "artifact_type_ref": "cal.artifact-type.typed-relation/v2",
                "description": "One coherent candidate slice can demonstrate contract closure without activating a runtime or claiming migration completion.",
            },
            "constraints": [
                "Use only admitted-current Artifact Type and Relation Kind contracts",
                "Keep Product, Project, Capability, research, experiment, implementation, Agent, Project State, Context View, and Ontology View distinct",
                "Persist no machine Agent memory outside the Agent Session",
                "Create no authority, runtime activation, migration, deployment, or cutover effect",
                "Require a later exact owner decision before any instance admission",
            ],
            "satisfaction_refs": [GOAL],
        },
    )
    add_artifact(
        "product",
        "cal.artifact-type.product-identity/v2",
        "product",
        {
            "product_id": PRODUCT,
            "version": "2.0.0-candidate.1",
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
            "claim_ceiling": "Candidate Product identity for this reference slice; it does not activate or publish CyberAlchemy Lab.",
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
            "boundaries": ["One reference slice cannot prove Product value", "Schema validation does not prove runtime behavior", "The Product remains distinct from the migration Project"],
            "revision_criteria": ["Users cannot locate authoritative state", "Typed distinctions add burden without improving decisions", "A simpler model preserves equivalent traceability"],
            "evidence_routes": ["route:reference-slice-evidence"],
            "counterevidence_routes": ["route:reference-slice-challenge"],
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
            "acceptance_conditions": ["All selected artifacts validate against admitted-current contracts", "Every connection resolves an exact admitted endpoint pair", "Ontology and Context Views preserve source digests and remain derived", "No Agent durable memory or runtime effect is created"],
            "exclusions": ["Migration completion", "Persistent Agent identity", "Automatic admission", "Live service activation"],
            "input_contract_refs": ["contract:admitted-artifact-type-registry", "contract:admitted-relation-kind-registry"],
            "output_contract_refs": ["contract:reference-instance-pack", "contract:derived-agent-view"],
            "context_policy_refs": ["policy:project-state-owns-continuity", "policy:derived-views-have-no-authority"],
            "consumer_refs": ["consumer:repository-owner-review", "consumer:ephemeral-agent-session"],
            "participant_refs": [OWNER, PRINCIPAL],
            "realization_binding_refs": [BINDING],
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
                "evidence_refs": [EVIDENCE],
                "residue_refs": ["residue:instance-admission-owner-decision"],
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
                "includes": ["Migration inventory", "Semantic reconstruction", "Candidate validation", "Owner admission preparation"],
                "excludes": ["CyberAlchemy Lab Product identity", "Automatic migration completion", "Runtime cutover", "External publication"],
            },
            "accountable_owner_ref": OWNER,
            "evidence_refs": ["evidence/migrations/cyberalchemy-v2-to-lab", "CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Candidate Project identity for coordination only; it does not imply the migration is complete.",
        },
    )
    add_artifact(
        "goal",
        "cal.artifact-type.goal/v1",
        "goal",
        {
            "goal_id": GOAL,
            "name": "Materialize the definition-complete reference slice",
            "outcome": "One candidate slice demonstrates the admitted model across Product, Project, research, experiment, implementation, Agent, durable state, relations, and derived views.",
            "rationale": "A concrete vertical slice is needed before broad instance admission or runtime activation.",
            "success_conditions": ["Every artifact validates", "Every relation resolves", "Projection digests bind exact sources", "Memory boundaries remain explicit", "Owner review receives one complete example"],
            "evidence_requirements": ["Candidate validation receipt", "Exact pack digest", "Non-collapse findings"],
            "accountable_owner_ref": OWNER,
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Candidate Goal only; validation does not establish owner acceptance or production readiness.",
        },
    )
    add_artifact(
        "capability-realization-binding",
        "cal.artifact-type.capability-realization-binding/v2",
        "capability-realization-binding",
        {
            "node_id": BINDING,
            "capability_ref": CAPABILITY,
            "capability_version_ref": f"{CAPABILITY}@candidate.1",
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "contract": {"input_contract_refs": ["contract:admitted-model-bundle"], "output_contract_refs": ["contract:validated-reference-slice"], "context_policy_refs": ["policy:bounded-agent-context"]},
            "realization_refs": [{"realization_kind": "implementation", "realization_ref": IMPLEMENTATION, "contract_ref": "contract:reference-slice-builder/v1", "owner_ref": OWNER}],
            "limitations": ["Candidate binding is not adoption or activation", "Validation does not prove Product value"],
        },
    )
    add_artifact(
        "policy",
        "cal.artifact-type.policy/v1",
        "policy",
        {
            "node_id": POLICY,
            "name": "Reference slice governance policy",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": ["CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
            "claim_ceiling": "Candidate policy instance for this reference slice; it grants no authority and activates no enforcement runtime.",
            "payload": {"issuer_ref": OWNER, "governed_scope_ref": SCOPE, "rule_refs": ["rule:exact-admitted-contracts-only", "rule:explicit-owner-admission", "rule:no-hidden-agent-memory", "rule:derived-views-have-no-authority"], "effective_period": "candidate-review-only", "exception_route": CHALLENGE},
        },
    )
    add_artifact(
        "challenge-contract",
        "cal.artifact-type.challenge-contract/v1",
        "challenge-contract",
        {
            "node_id": CHALLENGE,
            "name": "CyberAlchemy Lab reference slice challenge contract",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": "route:repository-owner-review",
            "evidence_refs": [EVIDENCE],
            "claim_ceiling": "Candidate contestability contract; it grants no authority and resolves no challenge by itself.",
            "payload": {
                "challengeable_subject_kinds": ["artifact-instance", "typed-relation", "ontology-node", "ontology-edge", "context-view"],
                "eligible_challenger_kinds": ["principal", "person-reference"],
                "grounds": ["evidence-conflict", "scope-error", "semantic-collapse", "stale-projection"],
                "owner_route": "route:repository-owner-review",
                "policy_ref": "policy:reference-slice-contestability/v1",
                "required_evidence_kinds": ["source", "evidence-set", "validation-receipt"],
                "resolution_gate_ref": "gate:explicit-owner-decision",
                "response_modes": ["evidence", "contradiction", "revision", "owner-review"],
                "response_period": "before-instance-admission",
                "unresolved_residue_route": "route:reference-slice-residue",
            },
        },
    )
    add_artifact(
        "research-inquiry",
        "cal.artifact-type.research-inquiry/v1",
        "research-inquiry",
        {
            "node_id": RESEARCH,
            "question": "Can the admitted Lab model represent the CyberAlchemy v2 migration as one coherent slice without collapsing Product, Project, research, execution, durable state, Agent memory, relations, or ontology projections?",
            "project_ref": PROJECT,
            "goal_refs": [GOAL],
            "scope_ref": SCOPE,
            "method_ref": "method:closed-schema-and-typed-endpoint-validation/v1",
            "inclusions": ["Admitted-current carrier schemas", "Admitted Relation Kind endpoint and qualifier contracts", "Agent memory boundary", "Ontology and Context projection lineage"],
            "exclusions": ["Live runtime behavior", "Migration completion", "Product value proof", "External systems"],
            "source_policy": {"allowed_source_kinds": ["owner-admitted-contract", "repository-artifact", "validation-receipt"], "selection_criteria": ["Prefer admitted-current registries", "Bind mutable sources by digest", "Keep counterevidence visible"], "freshness_rule": "Recompute digests for every candidate build.", "conflict_handling": "Preserve conflict as residue and route it through the Challenge Contract."},
            "source_refs": [str(BUNDLE_PATH.relative_to(LAB)), str(REGISTRY_PATH.relative_to(LAB)), str(RELATION_REGISTRY_PATH.relative_to(LAB))],
            "evidence_aggregate_refs": [EVIDENCE],
            "counterevidence_refs": [],
            "finding_refs": [FINDING],
            "limitations": ["One slice cannot establish global completeness", "Candidate data is not admitted authority", "Validation does not establish runtime behavior"],
            "stop_conditions": ["All local references and endpoint pairs close", "Projection digests match exact sources", "Every non-collapse check passes", "Remaining limits are explicit"],
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Candidate inquiry; it can support a bounded model finding but cannot prove migration completion or Product value.",
            "created_at": "2026-10-06T12:00:00Z",
            "last_updated_at": "2026-10-06T12:00:00Z",
        },
    )
    add_artifact(
        "hypothesis",
        "cal.artifact-type.hypothesis/v1",
        "hypothesis",
        {
            "node_id": HYPOTHESIS,
            "name": "Reference slice preserves admitted orthogonality",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": [EVIDENCE],
            "claim_ceiling": "Candidate test proposition; a passing validation run does not prove general model adequacy.",
            "payload": {"proposition": "A concrete Lab slice can close all selected schemas, exact relation endpoints, qualifiers, references, and projection digests while preserving the admitted non-collapse laws.", "falsification_conditions": ["Any selected artifact fails its admitted-current schema", "Any relation uses an undeclared endpoint pair or qualifier", "Any derived view lacks an exact source digest", "Session memory persists outside the Agent Session"], "observation_targets": ["receipt:reference-slice-validation", "finding:reference-slice-schema-and-relation-closure"], "disposition": "open"},
        },
    )

    add_artifact(
        "experiment-design",
        "cal.artifact-type.experiment-design/v1",
        "experiment-design",
        {
            "node_id": DESIGN,
            "project_ref": PROJECT,
            "goal_refs": [GOAL],
            "research_refs": [RESEARCH],
            "question_or_hypothesis": "The reference slice preserves schema, relation, projection, and memory-boundary invariants for its selected subjects.",
            "subject_ref": "instance-pack:cyberalchemy-lab-reference-slice/v1",
            "protocol_ref": "protocol:reference-slice-validation/v1",
            "conditions": ["Decision 0070 bundle is current", "Artifact and Relation Kind registries are owner-admitted", "Candidate generation is deterministic"],
            "variables_or_interventions": [{"kind": "intervention", "name": "materialize coherent candidate instances", "planned_value": "one definition-complete vertical slice"}],
            "measure_refs": ["measurement-method:schema-relation-projection-closure"],
            "prerequisites": ["Exact admitted registry digests resolve", "No instance admission is implied"],
            "stop_rules": ["Stop on the first unresolved carrier or relation kind", "Stop if any authority or runtime effect is detected"],
            "environment": "CyberAlchemy Lab repository checkout on 2026-10-06",
            "design_state": "ready",
            "run_refs": [RUN],
            "evidence_refs": [EVIDENCE],
            "finding_refs": [FINDING],
            "limitations": ["The design exercises a representative slice rather than all 93 Artifact Types and 538 endpoint pairs"],
            "product_evaluation_context": {"product_ref": PRODUCT, "product_thesis_ref": THESIS, "product_capability_refs": [CAPABILITY], "realization_binding_refs": [BINDING], "thesis_outcome_refs": [f"{THESIS}#inspectable-state"], "thesis_hypothesis_refs": [], "evaluation_purpose": "Evaluate contract coherence without treating it as Product value proof."},
            "scope_ref": SCOPE,
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Candidate design only; the linked run and receipt carry execution evidence separately.",
            "created_at": "2026-10-06T12:10:00Z",
            "last_updated_at": "2026-10-06T12:10:00Z",
        },
    )
    add_artifact(
        "experiment-run",
        "cal.artifact-type.experiment-run/v1",
        "experiment-run",
        {
            "node_id": RUN,
            "design_ref": DESIGN,
            "design_version_ref": f"{DESIGN}@candidate.1",
            "project_ref": PROJECT,
            "goal_refs": [GOAL],
            "research_refs": [RESEARCH],
            "input_refs": [str(REGISTRY_PATH.relative_to(LAB)), str(RELATION_REGISTRY_PATH.relative_to(LAB)), "instance-pack:cyberalchemy-lab-reference-slice/v1"],
            "environment": "CyberAlchemy Lab local repository; deterministic Python validator",
            "interventions": ["Generate candidate artifacts and Typed Relations", "Validate schemas, endpoint pairs, reference closure, projection lineage, and memory boundaries"],
            "deviations": [],
            "observation_refs": ["observation:reference-slice-validation-output"],
            "measurement_result_refs": ["measurement-result:reference-slice-check-counts"],
            "evidence_set_ref": EVIDENCE,
            "period": {"start": "2026-10-06T12:15:00Z", "end": "2026-10-06T12:20:00Z"},
            "run_state": "completed",
            "stop_reason": None,
            "product_evaluation_context": {"product_ref": PRODUCT, "product_thesis_ref": THESIS, "product_capability_refs": [CAPABILITY], "realization_binding_refs": [BINDING], "thesis_outcome_refs": [f"{THESIS}#inspectable-state"], "thesis_hypothesis_refs": [], "evaluation_purpose": "Record one bounded contract validation without deciding Product value."},
            "scope_ref": SCOPE,
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Records the candidate validator execution; completion does not establish instance admission, migration completion, runtime behavior, or Product value.",
        },
    )
    add_artifact(
        "implementation",
        "cal.artifact-type.implementation/v1",
        "implementation",
        {
            "node_id": IMPLEMENTATION,
            "name": "CyberAlchemy Lab governed repository toolchain",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": [EVIDENCE],
            "claim_ceiling": "Candidate implementation identity; validation does not establish adoption, activation, conformance, or live service behavior.",
            "payload": {"implementation_kind": "repository-toolchain", "environment_contract_ref": "contract:python3-local-repository", "execution_entrypoint_ref": str((ROOT / "validate.py").relative_to(LAB)), "conforms_to_schema_refs": ["cal.artifact-type.typed-relation/v2", "cal.artifact-type.ontology-node/v2"], "realizes_capability_refs": [CAPABILITY]},
        },
    )
    add_artifact(
        "work",
        "cal.artifact-type.work/v1",
        "work",
        {
            "node_id": WORK,
            "name": "Materialize CyberAlchemy Lab reference slice v1",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": [EVIDENCE],
            "claim_ceiling": "Candidate Work record; candidate completion does not establish owner admission or runtime activation.",
            "payload": {"work_statement": "Build and validate one coherent candidate instance and relation slice from the owner-admitted model.", "project_ref": PROJECT, "goal_refs": [GOAL], "input_refs": [str(BUNDLE_PATH.relative_to(LAB))], "output_refs": ["instance-pack:cyberalchemy-lab-reference-slice/v1", "receipt:reference-slice-validation"], "completion_state": "candidate-complete"},
        },
    )
    add_artifact(
        "principal",
        "cal.artifact-type.principal/v1",
        "principal",
        {
            "node_id": PRINCIPAL,
            "name": "Repository owner principal",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": ["evidence:explicit-owner-instructions"],
            "claim_ceiling": "Candidate repository-local Principal reference; it does not authenticate a person or grant authority beyond explicit owner decisions.",
            "payload": {"principal_kind": "human", "stable_subject_ref": "person-reference:repository-owner", "registry_ref": "registry:lab-principals", "recognition_boundary_refs": ["boundary:cyberalchemy-lab-repository"], "status": "active"},
        },
    )
    add_artifact(
        "agent-instance",
        "cal.artifact-type.agent-instance/v1",
        "agent-instance",
        {
            "node_id": AGENT,
            "name": "Ephemeral reference slice authoring Agent",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": ["evidence:current-codex-session"],
            "claim_ceiling": "Candidate representation of one ephemeral machine Agent execution; it owns no durable memory and expires with its session.",
            "payload": {"accountable_principal_ref": PRINCIPAL, "agent_classification_assignment_ref": "classification-assignment:machine-agent", "capability_refs": ["agent-capability:repository-candidate-authoring"], "implementation_ref": "implementation:codex-agent", "profile_ref": "agent-profile:repository-model-review", "session_ref": SESSION, "started_at": "2026-10-06T12:00:00Z", "terminated_at": "when-session-terminates"},
        },
    )
    add_artifact(
        "agent-assignment",
        "cal.artifact-type.agent-assignment/v1",
        "agent-assignment",
        {
            "node_id": ASSIGNMENT,
            "name": "Materialize the first reference slice",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": ["evidence:user-request-do-next"],
            "claim_ceiling": "Candidate assignment of expected work; it is not a Delegation and grants no authority beyond the explicit task.",
            "payload": {"eligible_agent_ref": AGENT, "owner_ref": PRINCIPAL, "intent_ref": INTENT, "project_ref": PROJECT, "work_ref": WORK, "period": SESSION, "expected_output_refs": ["instance-pack:cyberalchemy-lab-reference-slice/v1"], "stop_conditions": ["candidate-validation-pass", "owner-review-boundary"]},
        },
    )
    add_artifact(
        "context",
        "cal.artifact-type.context/v1",
        "context",
        {
            "node_id": CONTEXT,
            "purpose": "Resolve the admitted model, current project state, and exact candidate inputs needed to author and review the reference slice.",
            "context_kind": "project",
            "project_ref": PROJECT,
            "product_ref": PRODUCT,
            "goal_ref": None,
            "scope_ref": SCOPE,
            "subject_scope": ["Decision 0070 admitted contracts", "CyberAlchemy v2 migration Project State", "Reference slice candidate", "Validation evidence"],
            "intended_uses": ["Reference slice authoring", "Owner review", "Agent context selection"],
            "bounded_context_refs": ["bounded-context:semantic-governance"],
            "consumer_refs": [SESSION],
            "source_policy_refs": ["policy:admitted-authority-first", "policy:exact-digest-provenance"],
            "profile_ref": "context-profile:reference-slice-review",
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Candidate Context boundary; it is not Project State or an immutable resolved view.",
        },
    )
    add_artifact(
        "context-request",
        "cal.artifact-type.context-request/v1",
        "context-request",
        {
            "node_id": CONTEXT_REQUEST,
            "context_ref": CONTEXT,
            "context_version_ref": f"{CONTEXT}@candidate.1",
            "requested_at": "2026-10-06T12:00:00Z",
            "selectors": ["Decision 0070 exact admitted bundle", "Current Project State", "Reference slice source and validation contract"],
            "exclusions": ["Secrets", "Unrelated dirty work", "Live external services", "Hidden cross-session memory"],
            "intended_uses": ["Provide bounded inputs to the ephemeral Agent Session"],
            "consumer_refs": [SESSION],
            "budget": {"max_items": 128, "max_bytes": 2000000},
            "freshness_requirement": "Every selected repository source must match its declared SHA-256.",
            "output_constraints": ["Immutable digest-bound view", "Explicit exclusions", "No authority transfer"],
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Candidate request only; it does not resolve or mutate Context.",
        },
    )

    state_materials = [
        LAB / "docs/decisions/0065-integrated-lab-definition-model-admission/decision.json",
        LAB / "docs/decisions/0066-definition-specialization-resolution-admission/decision.json",
        LAB / "docs/decisions/0070-definition-complete-lab-model-admission/decision.json",
        BUNDLE_PATH,
    ]
    state_digest = digest_value([{"path": str(p.relative_to(LAB)), "sha256": sha(p)} for p in state_materials])
    add_artifact(
        "project-state",
        "cal.artifact-type.project-state/v1",
        "project-state",
        {
            "node_id": PROJECT_STATE,
            "name": "CyberAlchemy v2 migration state after Decision 0070",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": [str(p.relative_to(LAB)) for p in state_materials],
            "claim_ceiling": "Candidate durable Project State selection; it records repository state and does not belong to the Agent or its session.",
            "payload": {"project_ref": PROJECT, "cursor": "decision:0070", "state_digest": f"sha256:{state_digest}", "artifact_refs": [str(BUNDLE_PATH.relative_to(LAB)), str(REGISTRY_PATH.relative_to(LAB)), str(RELATION_REGISTRY_PATH.relative_to(LAB))], "decision_refs": ["CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION", "CAL-DECISION-0066-DEFINITION-SPECIALIZATION-RESOLUTION-ADMISSION", "CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"], "semantic_history_ref": "semantic-event-history:reference-slice:project-state-cyberalchemy-v2-to-lab-migration-decision-0070", "governance_history_ref": "governance-event-history:reference-slice:project-state-cyberalchemy-v2-to-lab-migration-decision-0070"},
        },
    )

    project_state_digest = artifact_index[PROJECT_STATE]["sha256"]
    add_artifact(
        "context-view",
        "cal.artifact-type.context-view/v1",
        "context-view",
        {
            "node_id": CONTEXT_VIEW,
            "context_ref": CONTEXT,
            "context_version_ref": f"{CONTEXT}@candidate.1",
            "request_ref": CONTEXT_REQUEST,
            "included_material": [
                {"source_ref": str(BUNDLE_PATH.relative_to(LAB)), "sha256": sha(BUNDLE_PATH), "selector": "owner-admitted definition-complete model"},
                {"source_ref": artifact_index[PROJECT_STATE]["path"], "sha256": project_state_digest, "selector": "durable Project State"},
            ],
            "excluded_material": [{"source_ref": "runtime:live-services", "reason": "No runtime activation belongs to this candidate"}, {"source_ref": "memory:hidden-cross-session", "reason": "Machine Agent durable memory is forbidden"}],
            "selection_basis": "Exact Context Request selectors with admitted-authority-first and digest-bound Project State.",
            "lineage_refs": [CONTEXT_REQUEST, PROJECT_STATE, "CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"],
            "source_epoch": f"sha256:{state_digest}",
            "generated_at": "2026-10-06T12:05:00Z",
            "expires_at": "2026-10-07T12:05:00Z",
            "limitations": ["The view covers one candidate build epoch", "Included authority remains owned by its source artifacts"],
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Immutable candidate projection for one Agent Session; it owns no source authority and is not durable Agent memory.",
        },
    )
    add_artifact(
        "agent-session",
        "cal.artifact-type.agent-session/v1",
        "agent-session",
        {
            "node_id": SESSION,
            "name": "Reference slice authoring session",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": [CONTEXT_VIEW],
            "claim_ceiling": "Candidate Agent Session; its short memory expires with the session and durable continuity remains Project State.",
            "payload": {"agent_instance_ref": AGENT, "assignment_ref": ASSIGNMENT, "authority_envelope_ref": "delegation:none-beyond-explicit-task", "budget_refs": ["budget:current-task"], "context_view_ref": CONTEXT_VIEW, "ontology_view_ref": "ontology-view:cyberalchemy-lab-reference-slice:2026-10-06", "event_cursor": "candidate-cursor:reference-slice", "input_refs": [INTENT, CONTEXT_REQUEST], "policy_refs": ["policy:owner-review-required", "policy:no-hidden-cross-session-memory"], "session_memory": {"expires_with_session": True, "selected_input_refs": [CONTEXT_VIEW, "ontology-view:cyberalchemy-lab-reference-slice:2026-10-06"], "working_record_refs": [WORK, RUN], "unresolved_questions": ["owner-instance-admission-decision"]}, "termination_state": "active"},
        },
    )
    add_artifact(
        "evidence-set",
        "cal.artifact-type.evidence-set/v1",
        "evidence-set",
        {
            "node_id": EVIDENCE,
            "name": "Reference slice validation evidence",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": ["receipt:reference-slice-validation"],
            "claim_ceiling": "Candidate evidence aggregation; it supports only the validator checks explicitly recorded in its receipt.",
            "payload": {"coverage_statement": "Selected admitted carrier schemas, exact Relation Kind endpoint pairs and qualifiers, local reference closure, projection digests, and Agent memory boundaries.", "item_refs": ["receipt:reference-slice-validation", str(BUNDLE_PATH.relative_to(LAB))], "source_refs": ["source:deterministic-reference-slice-validator", str(REGISTRY_PATH.relative_to(LAB)), str(RELATION_REGISTRY_PATH.relative_to(LAB))], "limitations": ["No live runtime behavior", "No general completeness proof", "No owner admission effect"]},
        },
    )
    add_artifact(
        "finding",
        "cal.artifact-type.finding/v1",
        "finding",
        {
            "node_id": FINDING,
            "question": "Can the admitted Lab model represent the CyberAlchemy v2 migration as one coherent slice without semantic collapse?",
            "statement": "The selected reference slice closes its admitted-current schemas, exact relation endpoints, qualifiers, references, and derived projection bindings while keeping Product, Project, research, execution, implementation, Agent Session, Project State, Context View, and Ontology View distinct.",
            "inquiry_ref": RESEARCH,
            "research_run_refs": [RUN],
            "evidence_set_refs": [EVIDENCE],
            "evidence_refs": ["receipt:reference-slice-validation"],
            "counterevidence_refs": ["limitation:representative-slice-not-all-93-types"],
            "support_assessment": {"support_state": "supported", "rationale": "The deterministic validator checks exact admitted schemas, relation contracts, closure, digests, and memory boundaries for this bounded slice."},
            "finding_state": "draft",
            "limitations": ["The slice does not exercise all Artifact Types or endpoint pairs", "It does not establish migration completion, Product value, or runtime behavior"],
            "created_at": "2026-10-06T12:20:00Z",
            "last_updated_at": "2026-10-06T12:20:00Z",
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Bounded candidate finding about this exact generated slice; it creates no admission or runtime effect.",
        },
    )
    add_artifact(
        "ontology",
        "cal.artifact-type.ontology/v1",
        "ontology",
        {
            "node_id": ONTOLOGY_REF,
            "name": "CyberAlchemy Lab reference slice ontology",
            "purpose": "Project exact candidate subjects and global Typed Relations into a bounded business-system bridge view for owner and Agent review.",
            "boundaries": ["Covers only subjects selected by this reference slice", "Global connections remain owned by Typed Relations", "Derived nodes, edges, cuts, and views are not replay authority"],
            "branch_refs": ["branch:business", "branch:system", "branch:bridge"],
            "node_refs": [],
            "relation_refs": [],
            "governance_rules": ["Every projected edge binds one exact global Typed Relation digest", "Every represented subject is digest-bound", "Semantic and governance event tuples remain distinct", "Contradictions remain contestable"],
            "provenance_refs": [str(BUNDLE_PATH.relative_to(LAB)), "semantic-event-history:reference-slice", "governance-event-history:reference-slice"],
            "confidence_policy_ref": "policy:reference-slice-confidence/v1",
            "role_assignment_refs": ["role-assignment:repository-owner"],
            "ontology_version": "1.0.0-candidate.1",
            "promotion_state": "draft",
            "owner_ref": OWNER,
            "owner_route": "route:repository-owner-review",
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "claim_ceiling": "Candidate derived ontology boundary; it neither replaces source artifacts nor creates global semantic connections.",
        },
    )


relation_entries: list[dict[str, Any]] = []
relation_index: dict[str, dict[str, Any]] = {}
relation_kind_records = {
    x["relation_kind_id"]: load(LAB / x["instance_path"])
    for x in load(RELATION_REGISTRY_PATH)["entries"]
}


def add_relation(slug: str, kind: str, source_kind: str, source_ref: str, target_kind: str, target_ref: str, qualifiers: dict[str, str]) -> None:
    template = fixture("cal.artifact-type.typed-relation/v2")
    relation_id = f"typed-relation:reference-slice:{slug}"
    record = merge(
        template,
        {
            "node_id": relation_id,
            "name": f"Reference slice {kind}",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "challenge_route": CHALLENGE,
            "evidence_refs": [EVIDENCE],
            "claim_ceiling": "Candidate global Typed Relation for the exact reference slice endpoints; validation creates no connection authority or runtime effect.",
            "payload": {
                "relation_kind_ref": kind,
                "relation_lifecycle_state": "candidate",
                "source": {"kind": source_kind, "ref": source_ref, "version_ref": artifact_index[source_ref]["version_ref"]},
                "target": {"kind": target_kind, "ref": target_ref, "version_ref": artifact_index[target_ref]["version_ref"]},
                "qualifiers": qualifiers,
                "relation_evidence_refs": [EVIDENCE],
            },
            "relation_refs": [],
        },
    )
    record["payload"]["qualifiers"] = copy.deepcopy(qualifiers)
    path = RELATIONS / f"{slug}.json"
    dump(path, record)
    entry = {"relation_id": relation_id, "relation_kind_ref": kind, "path": str(path.relative_to(LAB)), "sha256": sha(path), "source_kind": source_kind, "source_ref": source_ref, "target_kind": target_kind, "target_ref": target_ref, "version_ref": f"{relation_id}@candidate.1"}
    relation_entries.append(entry)
    relation_index[relation_id] = entry


def relation_specs() -> list[tuple[str, str, str, str, str, str, dict[str, str]]]:
    specs = [
        ("product-addresses-intent", "relation.addresses-intent", "product", PRODUCT, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:reference-slice-candidate", "addressing_role": "product-direction"}),
        ("capability-member-of-product", "relation.member-of", "product-capability", CAPABILITY, "product", PRODUCT, {"membership_role": "product-capability"}),
        ("capability-derives-from-thesis", "relation.derives-from", "product-capability", CAPABILITY, "product-thesis", THESIS, {"derivation_role": "thesis-outcome-realization"}),
        ("project-addresses-intent", "relation.addresses-intent", "project", PROJECT, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:reference-slice-candidate", "addressing_role": "bounded-coordination"}),
        ("project-contributes-to-product", "relation.contributes-to", "project", PROJECT, "product", PRODUCT, {"contribution_role": "migration-and-model-development", "contribution_scope": SCOPE}),
        ("goal-member-of-project", "relation.member-of", "goal", GOAL, "project", PROJECT, {"membership_role": "project-goal"}),
        ("goal-addresses-intent", "relation.addresses-intent", "goal", GOAL, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:reference-slice-candidate", "addressing_role": "measurable-outcome"}),
        ("binding-member-of-project", "relation.member-of", "capability-realization-binding", BINDING, "project", PROJECT, {"membership_role": "project-realization-binding"}),
        ("challenge-contract-governed-by-policy", "relation.governed-by", "challenge-contract", CHALLENGE, "policy", POLICY, {"governance_role": "contestability-policy"}),
        ("research-member-of-project", "relation.member-of", "research-inquiry", RESEARCH, "project", PROJECT, {"membership_role": "project-research"}),
        ("research-addresses-intent", "relation.addresses-intent", "research-inquiry", RESEARCH, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:reference-slice-candidate", "addressing_role": "evidence-question"}),
        ("design-member-of-project", "relation.member-of", "experiment-design", DESIGN, "project", PROJECT, {"membership_role": "project-experiment-design"}),
        ("design-engages-inquiry", "relation.engages-inquiry", "experiment-design", DESIGN, "research-inquiry", RESEARCH, {"inquiry_role": "tests-model-coherence"}),
        ("design-tests-hypothesis", "relation.tests-hypothesis", "experiment-design", DESIGN, "hypothesis", HYPOTHESIS, {"hypothesis_version_ref": f"{HYPOTHESIS}@candidate.1", "test_role": "contract-closure-test"}),
        ("design-evaluates-capability", "relation.evaluates", "experiment-design", DESIGN, "product-capability", CAPABILITY, {"evaluation_role": "contract-coherence", "evaluation_purpose": "bounded-reference-slice-validation"}),
        ("run-member-of-project", "relation.member-of", "experiment-run", RUN, "project", PROJECT, {"membership_role": "project-experiment-run"}),
        ("run-realizes-design", "relation.realizes", "experiment-run", RUN, "experiment-design", DESIGN, {"realization_role": "protocol-execution", "exact_target_version_ref": f"{DESIGN}@candidate.1"}),
        ("run-engages-inquiry", "relation.engages-inquiry", "experiment-run", RUN, "research-inquiry", RESEARCH, {"inquiry_role": "produces-validation-evidence"}),
        ("run-evaluates-capability", "relation.evaluates", "experiment-run", RUN, "product-capability", CAPABILITY, {"evaluation_role": "bounded-contract-run", "evaluation_purpose": "measure-selected-model-closure"}),
        ("evidence-member-of-project", "relation.member-of", "evidence-set", EVIDENCE, "project", PROJECT, {"membership_role": "project-validation-evidence"}),
        ("evidence-derives-from-run", "relation.derives-from", "evidence-set", EVIDENCE, "experiment-run", RUN, {"derivation_role": "validation-output"}),
        ("finding-derives-from-evidence", "relation.derives-from", "finding", FINDING, "evidence-set", EVIDENCE, {"derivation_role": "bounded-synthesis"}),
        ("finding-engages-inquiry", "relation.engages-inquiry", "finding", FINDING, "research-inquiry", RESEARCH, {"inquiry_role": "bounded-answer"}),
        ("evidence-bears-on-finding", "relation.evidence-bears-on", "evidence-set", EVIDENCE, "finding", FINDING, {"polarity": "supports"}),
        ("evidence-bears-on-hypothesis", "relation.evidence-bears-on", "evidence-set", EVIDENCE, "hypothesis", HYPOTHESIS, {"polarity": "supports"}),
        ("implementation-realizes-capability", "relation.realizes", "implementation", IMPLEMENTATION, "product-capability", CAPABILITY, {"realization_role": "repository-toolchain", "exact_target_version_ref": f"{CAPABILITY}@candidate.1"}),
        ("work-member-of-project", "relation.member-of", "work", WORK, "project", PROJECT, {"membership_role": "project-work"}),
        ("agent-acts-for-principal", "relation.acts-for", "agent-instance", AGENT, "principal", PRINCIPAL, {"delegation_ref": "delegation:none-beyond-explicit-task", "scope_ref": SCOPE, "effective_period": SESSION, "revocation_state": "expires-with-session"}),
        ("agent-member-of-session", "relation.member-of", "agent-instance", AGENT, "agent-session", SESSION, {"membership_role": "ephemeral-session-agent"}),
        ("assignment-member-of-project", "relation.member-of", "agent-assignment", ASSIGNMENT, "project", PROJECT, {"membership_role": "project-assignment"}),
        ("assignment-addresses-intent", "relation.addresses-intent", "agent-assignment", ASSIGNMENT, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:reference-slice-candidate", "addressing_role": "authorized-task"}),
        ("agent-performs-work", "relation.performs", "agent-instance", AGENT, "work", WORK, {"session_ref": SESSION, "participation_role": "candidate-author", "action_posture": "bounded-task"}),
        ("agent-performs-run", "relation.performs", "agent-instance", AGENT, "experiment-run", RUN, {"session_ref": SESSION, "participation_role": "validator-operator", "action_posture": "bounded-task"}),
        ("project-state-member-of-project", "relation.member-of", "project-state", PROJECT_STATE, "project", PROJECT, {"membership_role": "durable-project-state"}),
        ("context-member-of-project", "relation.member-of", "context", CONTEXT, "project", PROJECT, {"membership_role": "project-context"}),
        ("context-governed-by-policy", "relation.governed-by", "context", CONTEXT, "policy", POLICY, {"governance_role": "context-selection-policy"}),
        ("context-frames-product", "relation.frames", "context", CONTEXT, "product", PRODUCT, {"framing_role": "product-relevance-boundary"}),
        ("context-frames-project", "relation.frames", "context", CONTEXT, "project", PROJECT, {"framing_role": "project-relevance-boundary"}),
        ("request-requests-context", "relation.requests-resolution-of", "context-request", CONTEXT_REQUEST, "context", CONTEXT, {"context_version_ref": f"{CONTEXT}@candidate.1"}),
        ("view-fulfills-request", "relation.fulfills-request", "context-view", CONTEXT_VIEW, "context-request", CONTEXT_REQUEST, {"fulfillment_role": "bounded-agent-input"}),
        ("view-derives-from-context", "relation.derives-from", "context-view", CONTEXT_VIEW, "context", CONTEXT, {"derivation_role": "immutable-projection"}),
        ("session-consumes-context-view", "relation.consumes-view", "agent-session", SESSION, "context-view", CONTEXT_VIEW, {"view_digest": artifact_index[CONTEXT_VIEW]["sha256"], "cursor": "candidate-cursor:reference-slice", "consumption_purpose": "reference-slice-authoring"}),
        ("session-uses-implementation", "relation.uses-tool", "agent-session", SESSION, "implementation", IMPLEMENTATION, {"tool_version_ref": f"{IMPLEMENTATION}@candidate.1", "invocation_contract_ref": "contract:reference-slice-builder/v1", "use_role": "candidate-build-and-validation"}),
    ]
    return specs


def bind_artifact_relation_refs() -> None:
    bindings: dict[str, list[dict[str, str]]] = {}
    for _, kind, source_kind, source_ref, target_kind, target_ref, _ in relation_specs():
        bindings.setdefault(source_ref, []).append({"counterpart_kind": target_kind, "counterpart_ref": target_ref, "direction": "source", "relation_kind_ref": kind})
        bindings.setdefault(target_ref, []).append({"counterpart_kind": source_kind, "counterpart_ref": source_ref, "direction": "target", "relation_kind_ref": kind})
    for identity, entry in list(artifact_index.items()):
        path = LAB / entry["path"]
        record = load(path)
        if "relation_refs" not in record:
            continue
        descriptor = load(LAB / contracts[entry["carrier_type_ref"]]["artifact_path"])
        roles = descriptor.get("relation_roles", [])
        selected = []
        for binding in bindings.get(identity, []):
            if any(
                binding["relation_kind_ref"] == role["relation_kind_ref"]
                and binding["direction"] == role["direction"]
                and binding["counterpart_kind"] in role["counterpart_kinds"]
                for role in roles
            ):
                selected.append(binding)
        record["relation_refs"] = selected
        dump(path, record)
        entry["sha256"] = sha(path)
    context_view_path = LAB / artifact_index[CONTEXT_VIEW]["path"]
    context_view = load(context_view_path)
    for material in context_view["included_material"]:
        if material["source_ref"] == artifact_index[PROJECT_STATE]["path"]:
            material["sha256"] = artifact_index[PROJECT_STATE]["sha256"]
    dump(context_view_path, context_view)
    artifact_index[CONTEXT_VIEW]["sha256"] = sha(context_view_path)


def build_relations() -> None:
    for spec in relation_specs():
        add_relation(*spec)


def build_ontology_projection() -> None:
    projected = [
        "typed-relation:reference-slice:project-contributes-to-product",
        "typed-relation:reference-slice:capability-member-of-product",
        "typed-relation:reference-slice:implementation-realizes-capability",
        "typed-relation:reference-slice:research-member-of-project",
        "typed-relation:reference-slice:design-engages-inquiry",
        "typed-relation:reference-slice:run-realizes-design",
        "typed-relation:reference-slice:agent-performs-work",
        "typed-relation:reference-slice:session-consumes-context-view",
        "typed-relation:reference-slice:project-state-member-of-project",
    ]
    subject_refs = []
    for rel_id in projected:
        rel = load(LAB / relation_index[rel_id]["path"])
        subject_refs.extend([rel["payload"]["source"]["ref"], rel["payload"]["target"]["ref"]])
    subject_refs = list(dict.fromkeys(subject_refs))

    semantic_events: list[dict[str, Any]] = []
    governance_events: list[dict[str, Any]] = []
    semantic_history_refs: list[str] = []
    governance_history_refs: list[str] = []

    def add_event_histories(subject_key: str, subject_kind: str, projected_ref: str, source_entry: dict[str, Any], cursor: int) -> tuple[dict[str, Any], dict[str, Any]]:
        safe = subject_key.replace(":", "-").replace("/", "-")
        semantic_id = f"semantic-event:reference-slice:{cursor}"
        semantic_digest = digest_value({"event_id": semantic_id, "subject_ref": subject_key, "subject_digest": source_entry["sha256"], "operation": f"project-{subject_kind}"})
        semantic = {"cursor": cursor, "event_id": semantic_id, "event_digest": semantic_digest, "previous_event_digest": None, "record_ref": source_entry["path"]}
        semantic_history_ref = f"semantic-event-history:reference-slice:{safe}"
        semantic_history = fixture("cal.artifact-type.semantic-event-history/v1")
        semantic_history = merge(semantic_history, {"node_id": semantic_history_ref, "name": f"Semantic event history for {projected_ref}", "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "evidence_refs": [source_entry["path"]], "claim_ceiling": "Candidate one-subject semantic replay history for this projection only; it is not admitted runtime state.", "payload": {"history_id": semantic_history_ref, "stream_id": f"semantic:{projected_ref}", "subject_kind": subject_kind, "subject_ref": projected_ref, "ontology_ref": ONTOLOGY_REF, "append_only": True, "event_records_are_replay_source": True, "history_manifest_is_event_index": True, "events": [semantic], "latest_cursor": cursor, "chain_digest": digest_value([semantic_digest])}})
        add_generated_artifact(f"semantic-event-history-{cursor:02d}", "cal.artifact-type.semantic-event-history/v1", "semantic-event-history", semantic_history)
        semantic_history_refs.append(semantic_history_ref)
        semantic_events.append(semantic)

        governance_id = f"governance-event:reference-slice:{cursor}"
        governance_digest = digest_value({"event_id": governance_id, "semantic_event_digest": semantic_digest, "challenge_contract_ref": CHALLENGE, "authority_effect": "none"})
        governance = {"governance_cursor": cursor, "event_id": governance_id, "event_digest": governance_digest, "previous_event_digest": None, "record_ref": source_entry["path"], "semantic_event_ref": {"semantic_cursor": cursor, "semantic_event_id": semantic_id, "semantic_event_digest": semantic_digest}, "upstream_governance_evidence_refs": [CHALLENGE, "CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION"]}
        governance_history_ref = f"governance-event-history:reference-slice:{safe}"
        governance_history = fixture("cal.artifact-type.governance-event-history/v1")
        governance_history = merge(governance_history, {"node_id": governance_history_ref, "name": f"Governance event history for {projected_ref}", "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "evidence_refs": [source_entry["path"]], "claim_ceiling": "Candidate one-subject governance replay history; it cannot alter semantic events or grant authority.", "payload": {"history_id": governance_history_ref, "stream_id": f"governance:{projected_ref}", "subject_ref": projected_ref, "ontology_ref": ONTOLOGY_REF, "append_only": True, "event_records_are_replay_source": True, "history_manifest_is_event_index": True, "semantic_patch_forbidden": True, "events": [governance], "latest_governance_cursor": cursor, "chain_digest": digest_value([governance_digest])}})
        add_generated_artifact(f"governance-event-history-{cursor:02d}", "cal.artifact-type.governance-event-history/v1", "governance-event-history", governance_history)
        governance_history_refs.append(governance_history_ref)
        governance_events.append(governance)
        return semantic, governance

    node_ref_by_subject: dict[str, str] = {
        ref: f"ontology-node:reference-slice:{ref.replace(':', '-').replace('/', '-')}"
        for ref in subject_refs
    }
    node_entries = []
    for index, ref in enumerate(subject_refs, 1):
        entry = artifact_index[ref]
        safe = ref.replace(":", "-").replace("/", "-")
        node_ref = node_ref_by_subject[ref]
        semantic, governance = add_event_histories(ref, "ontology-node", node_ref, entry, index)
        template = fixture("cal.artifact-type.ontology-node/v2")
        record = merge(template, {"node_id": node_ref, "name": f"Reference slice node for {ref}", "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "evidence_refs": [entry["path"]], "claim_ceiling": "Candidate digest-bound Ontology Node projection; it is not the represented subject and has no authority effect.", "payload": {"ontology_ref": ONTOLOGY_REF, "ontology_manifest_ref": "ontology-manifest:reference-slice/v1", "node_type_ref": f"ontology-node-type:{entry['semantic_kind']}", "profile_ref": "ontology-profile:reference-slice", "branch": "bridge", "represented_subject": {"kind": entry["semantic_kind"], "ref": ref, "version_ref": entry["version_ref"], "digest": entry["sha256"]}, "provenance_refs": [entry["path"]], "replay_source": False, "semantic_state": {"label": ref, "proposition": f"Candidate representation of exact {entry['semantic_kind']} subject {ref}.", "lifecycle": "active", "semantic_definition_refs": [], "semantic_components": ["identity", "digest", "source-kind"], "typed_properties": {"carrier_type_ref": entry["carrier_type_ref"]}, "use_obligations": ["Resolve the exact represented-subject digest before use."], "forbidden_collapse": ["represented-subject", "governance-state", "projection"]}, "governance_binding": {"authority_effect": "none", "challenge_contract_ref": CHALLENGE, "commitment_confidence_ref": "confidence:commitment:candidate", "evidence_confidence_ref": "confidence:evidence:validated-candidate", "semantic_event_ref": {"semantic_cursor": semantic["cursor"], "semantic_event_id": semantic["event_id"], "semantic_event_digest": semantic["event_digest"]}, "governance_event_refs": [governance["event_id"]]}}})
        path = ONTOLOGY / "nodes" / f"{index:02d}-{safe}.json"
        dump(path, record)
        register_generated_path(path, "cal.artifact-type.ontology-node/v2", "ontology-node", node_ref)
        node_entries.append({"node_ref": node_ref, "path": str(path.relative_to(LAB)), "represented_subject_ref": ref, "sha256": sha(path)})

    edge_entries = []
    for index, rel_id in enumerate(projected, 1):
        entry = relation_index[rel_id]
        relation = load(LAB / entry["path"])
        edge_ref = f"ontology-edge:reference-slice:{index:02d}"
        semantic, _ = add_event_histories(rel_id, "ontology-edge", edge_ref, entry, len(subject_refs) + index)
        template = fixture("cal.artifact-type.ontology-edge/v1")
        record = merge(template, {"node_id": edge_ref, "name": f"Projection of {rel_id}", "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "evidence_refs": [entry["path"]], "claim_ceiling": "Candidate Ontology Edge projection of one exact global Typed Relation; it creates no new global connection and is not a replay source.", "payload": {"ontology_ref": ONTOLOGY_REF, "source_node_ref": node_ref_by_subject[relation["payload"]["source"]["ref"]], "target_node_ref": node_ref_by_subject[relation["payload"]["target"]["ref"]], "relation_type_ref": relation["payload"]["relation_kind_ref"], "direction": "directed", "edge_mode": "global-projection", "global_typed_relation_binding": {"typed_relation_ref": rel_id, "typed_relation_version_ref": entry["version_ref"], "typed_relation_digest": entry["sha256"]}, "local_interpretation": None, "closed_qualifiers": relation["payload"]["qualifiers"], "lifecycle": "active", "replay_source": False, "semantic_event_ref": {"semantic_cursor": semantic["cursor"], "semantic_event_id": semantic["event_id"], "semantic_event_digest": semantic["event_digest"]}, "forbidden_collapse": ["global-typed-relation", "source-node", "target-node"]}})
        record["payload"]["closed_qualifiers"] = copy.deepcopy(relation["payload"]["qualifiers"])
        path = ONTOLOGY / "edges" / f"{index:02d}.json"
        dump(path, record)
        register_generated_path(path, "cal.artifact-type.ontology-edge/v1", "ontology-edge", edge_ref)
        edge_entries.append({"edge_ref": edge_ref, "path": str(path.relative_to(LAB)), "projected_relation_ref": rel_id, "sha256": sha(path)})

    semantic_chain_digest = digest_value([x["event_digest"] for x in semantic_events])
    governance_chain_digest = digest_value([x["event_digest"] for x in governance_events])

    ontology_path = LAB / artifact_index[ONTOLOGY_REF]["path"]
    ontology_record = load(ontology_path)
    ontology_record["node_refs"] = [x["node_ref"] for x in node_entries]
    ontology_record["relation_refs"] = [x["edge_ref"] for x in edge_entries]
    ontology_record["provenance_refs"] = semantic_history_refs + governance_history_refs
    dump(ontology_path, ontology_record)
    artifact_index[ONTOLOGY_REF]["sha256"] = sha(ontology_path)

    cut_digest = digest_value({"semantic_chain_digest": semantic_chain_digest, "governance_chain_digest": governance_chain_digest, "nodes": [{"ref": x["node_ref"], "sha256": x["sha256"]} for x in node_entries], "edges": [{"ref": x["edge_ref"], "sha256": x["sha256"]} for x in edge_entries]})
    cut_ref = "ontology-cut:cyberalchemy-lab-reference-slice:2026-10-06"
    cut = fixture("cal.artifact-type.ontology-cut/v1")
    cut = merge(cut, {"node_id": cut_ref, "name": "CyberAlchemy Lab reference slice ontology cut", "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "evidence_refs": semantic_history_refs + governance_history_refs, "claim_ceiling": "Candidate immutable cut over exact projected nodes and edges; it is derived and not a replay source.", "payload": {"ontology_ref": ONTOLOGY_REF, "semantic_cursor": semantic_events[-1]["cursor"], "source_event_set_digest": semantic_chain_digest, "governance_join_policy_ref": "governance-join:exact-event-tuple/v1", "node_refs": [x["node_ref"] for x in node_entries], "edge_refs": [x["edge_ref"] for x in edge_entries], "calculated_digest": cut_digest, "integrity_result": "pass", "replay_source": False}})
    add_generated_artifact("ontology-cut", "cal.artifact-type.ontology-cut/v1", "ontology-cut", cut)

    view_ref = "ontology-view:cyberalchemy-lab-reference-slice:2026-10-06"
    view = fixture("cal.artifact-type.ontology-view/v1")
    view = merge(view, {"node_id": view_ref, "name": "CyberAlchemy Lab reference slice ontology view", "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "evidence_refs": [cut_ref], "claim_ceiling": "Candidate purpose-bounded Ontology View for one Agent Session; it is derived, expiring, and has no replay or source authority.", "payload": {"ontology_ref": ONTOLOGY_REF, "cut_ref": cut_ref, "cut_digest": cut_digest, "semantic_cursor": semantic_events[-1]["cursor"], "source_event_set_digest": semantic_chain_digest, "governance_join_policy_ref": "governance-join:exact-event-tuple/v1", "selector_ref": "ontology-selector:reference-slice-agent-context", "selected_node_refs": [x["node_ref"] for x in node_entries], "selected_edge_refs": [x["edge_ref"] for x in edge_entries], "consumer_ref": SESSION, "intended_use": "Explain Product, Project, research, realization, work, Agent context, and durable state connections during owner review.", "freshness_at": "2026-10-06T12:20:00Z", "expires_at": "2026-10-07T12:20:00Z", "exclusions": ["Unselected model subjects", "Runtime activation", "Implicit authority", "Hidden Agent memory"], "replay_source": False}})
    add_generated_artifact("ontology-view", "cal.artifact-type.ontology-view/v1", "ontology-view", view)
    add_relation(
        "session-consumes-ontology-view",
        "relation.consumes-view",
        "agent-session",
        SESSION,
        "ontology-view",
        view_ref,
        {"view_digest": artifact_index[view_ref]["sha256"], "cursor": "candidate-cursor:reference-slice", "consumption_purpose": "reference-slice-ontology-review"},
    )

    ontology_manifest = {"ontology_ref": ONTOLOGY_REF, "semantic_event_history_refs": semantic_history_refs, "governance_event_history_refs": governance_history_refs, "node_entries": node_entries, "edge_entries": edge_entries, "cut_ref": cut_ref, "cut_digest": cut_digest, "view_ref": view_ref, "semantic_chain_digest": semantic_chain_digest, "governance_chain_digest": governance_chain_digest, "replay_sources": semantic_history_refs + governance_history_refs, "derived_surfaces": [cut_ref, view_ref], "authority_effect": "none"}
    dump(ONTOLOGY / "projection-manifest.json", ontology_manifest)


def add_generated_artifact(slug: str, type_ref: str, semantic_kind: str, record: dict[str, Any]) -> None:
    path = ARTIFACTS / f"{slug}.json"
    dump(path, record)
    identity = record["node_id"]
    entry = {"carrier_type_ref": type_ref, "identity_ref": identity, "path": str(path.relative_to(LAB)), "semantic_kind": semantic_kind, "sha256": sha(path), "version_ref": f"{identity}@candidate.1"}
    artifact_entries.append(entry)
    artifact_index[identity] = entry


def register_generated_path(path: Path, type_ref: str, semantic_kind: str, identity: str) -> None:
    entry = {
        "carrier_type_ref": type_ref,
        "identity_ref": identity,
        "path": str(path.relative_to(LAB)),
        "semantic_kind": semantic_kind,
        "sha256": sha(path),
        "version_ref": f"{identity}@candidate.1",
    }
    artifact_entries.append(entry)
    artifact_index[identity] = entry


def build_pack() -> None:
    projection = load(ONTOLOGY / "projection-manifest.json")
    groups: dict[str, int] = {}
    for entry in artifact_entries:
        groups[entry["semantic_kind"]] = groups.get(entry["semantic_kind"], 0) + 1
    pack = {
        "schema_version": "cyberalchemy-lab-reference-instance-pack/v1",
        "pack_id": "CAL-REFERENCE-INSTANCE-PACK-0001",
        "name": "CyberAlchemy Lab definition-complete reference slice",
        "status": "candidate-owner-review-open",
        "authority_effect": "none",
        "scope_ref": SCOPE,
        "owner_ref": OWNER,
        "inputs": {
            "definition_complete_bundle": {"path": str(BUNDLE_PATH.relative_to(LAB)), "sha256": sha(BUNDLE_PATH)},
            "artifact_type_registry": {"path": str(REGISTRY_PATH.relative_to(LAB)), "sha256": sha(REGISTRY_PATH)},
            "relation_kind_registry": {"path": str(RELATION_REGISTRY_PATH.relative_to(LAB)), "sha256": sha(RELATION_REGISTRY_PATH)},
        },
        "counts": {"artifact_instances": len(artifact_entries), "typed_relation_instances": len(relation_entries), "ontology_nodes": len(projection["node_entries"]), "ontology_edges": len(projection["edge_entries"]), "artifact_kinds": len(groups)},
        "artifact_kind_counts": groups,
        "artifacts": artifact_entries,
        "typed_relations": relation_entries,
        "ontology_projection": {"manifest_path": str((ONTOLOGY / "projection-manifest.json").relative_to(LAB)), "manifest_sha256": sha(ONTOLOGY / "projection-manifest.json"), "cut_ref": projection["cut_ref"], "cut_digest": projection["cut_digest"], "view_ref": projection["view_ref"]},
        "memory_contract": {"machine_agent_ephemeral": True, "durable_continuity_ref": PROJECT_STATE, "durable_continuity_owner": "project", "long_term_selection_refs": [CONTEXT_VIEW, projection["view_ref"]], "short_term_owner": SESSION, "short_term_embedded_only": True, "short_term_expires_with_session": True, "standalone_session_memory_artifact_present": False, "hidden_cross_session_memory_forbidden": True},
        "non_collapse_assertions": ["Product is distinct from migration Project", "Product Capability is distinct from Implementation and its realization binding", "Research Inquiry is distinct from Hypothesis, Experiment Design, Experiment Run, Evidence Set, and Finding", "Agent Instance is distinct from Agent Session and Assignment", "Project State is durable and is not Agent memory", "Context View and Ontology View are derived selections and do not own source authority", "Typed Relation is the global connection; Ontology Edge is its digest-bound projection", "Semantic event history and governance event history remain separate replay sources", "Validation does not imply admission, activation, migration, cutover, conformance, effectiveness, or Product value"],
        "excluded_effects": ["No artifact instance or Typed Relation is admitted", "No Agent, consumer, implementation, service, or runtime is activated", "No migration, cutover, deployment, publication, or external effect occurs", "No hidden or durable machine Agent memory is created", "No source authority is transferred to a Context View, Ontology Node, Ontology Edge, Cut, or Ontology View"],
        "claim_ceiling": "This deterministic candidate demonstrates one coherent slice of the admitted model. It creates no authority or runtime effect and requires a later exact owner-reviewed admission proposal before any instance becomes authoritative.",
    }
    dump(ROOT / "pack.json", pack)

    lines = [
        "<!-- GENERATED FILE: canonical data is pack.json and the instance records. -->",
        "",
        "# CyberAlchemy Lab reference instance slice",
        "",
        "- Status: `candidate-owner-review-open`",
        "- Authority effect: `none`",
        f"- Artifact instances: `{pack['counts']['artifact_instances']}`",
        f"- Typed Relation instances: `{pack['counts']['typed_relation_instances']}`",
        f"- Ontology nodes: `{pack['counts']['ontology_nodes']}`",
        f"- Ontology edges: `{pack['counts']['ontology_edges']}`",
        "- Runtime activations: `0`",
        "",
        "## Concrete story",
        "",
        f"`{PRODUCT}` is the Product. `{PROJECT}` is the bounded migration Project that contributes to it. `{CAPABILITY}` is the Product outcome, while `{IMPLEMENTATION}` is one replaceable realization. `{RESEARCH}` asks a bounded question; `{DESIGN}` specifies a test; `{RUN}` records its execution; `{EVIDENCE}` aggregates the output; and `{FINDING}` states only the supported bounded conclusion.",
        "",
        f"`{AGENT}` is ephemeral and acts within `{SESSION}`. Its short memory is embedded in that session and expires with it. Durable continuity remains `{PROJECT_STATE}`, selected through `{CONTEXT_VIEW}` and the ontology view rather than owned by the Agent.",
        "",
        "## Artifact instances",
        "",
        "| Kind | Identity | Carrier |",
        "|---|---|---|",
    ]
    for entry in artifact_entries:
        lines.append(f"| `{entry['semantic_kind']}` | `{entry['identity_ref']}` | `{entry['carrier_type_ref']}` |")
    lines += ["", "## Typed Relations", "", "| Relation Kind | Source | Target |", "|---|---|---|"]
    for entry in relation_entries:
        lines.append(f"| `{entry['relation_kind_ref']}` | `{entry['source_ref']}` | `{entry['target_ref']}` |")
    lines += ["", "## Authority boundary", "", pack["claim_ceiling"], "", "This package is ready for owner review. It is not an admission proposal and contains no authorization file.", ""]
    (ROOT / "REFERENCE-SLICE.md").write_text("\n".join(lines), encoding="utf-8")

    primary_count = sum(1 for x in artifact_entries if x["semantic_kind"] not in {"semantic-event-history", "governance-event-history", "ontology-node", "ontology-edge"})
    review = [
        "# Reference slice review",
        "",
        "## Proposed model",
        "",
        f"The candidate contains `{primary_count}` primary artifact instances, `{len(projection['semantic_event_history_refs'])}` semantic histories, `{len(projection['governance_event_history_refs'])}` governance histories, `{len(projection['node_entries'])}` Ontology Nodes, `{len(projection['edge_entries'])}` Ontology Edges, and `{len(relation_entries)}` global Typed Relations.",
        "",
        "The primary path is:",
        "",
        f"1. Product `{PRODUCT}` defines the durable value boundary.",
        f"2. Project `{PROJECT}` coordinates the bounded v2 migration and contributes to the Product.",
        f"3. Product Capability `{CAPABILITY}` states the repeatable outcome.",
        f"4. Implementation `{IMPLEMENTATION}` realizes that Capability without becoming it.",
        f"5. Research Inquiry `{RESEARCH}` asks the bounded question.",
        f"6. Experiment Design `{DESIGN}` tests `{HYPOTHESIS}`; Experiment Run `{RUN}` realizes the Design.",
        f"7. Evidence Set `{EVIDENCE}` derives from the Run; Finding `{FINDING}` derives from the Evidence Set and answers the Inquiry only within its claim ceiling.",
        f"8. Agent Instance `{AGENT}` acts for `{PRINCIPAL}` within Agent Session `{SESSION}` and performs the Work and validation Run.",
        f"9. Durable continuity remains Project State `{PROJECT_STATE}`. The Agent consumes bounded Context and Ontology Views selected from that state.",
        "",
        "## Real Typed Relation example",
        "",
        "```json",
        json.dumps(load(RELATIONS / "implementation-realizes-capability.json"), indent=2, sort_keys=True),
        "```",
        "",
        "This relation says only that one implementation realizes one Product Capability at an exact target version. It does not establish conformance, effectiveness, adoption, activation, or Product value.",
        "",
        "## Agent memory rule demonstrated",
        "",
        f"The Agent Instance is ephemeral. Short memory is embedded inside `{SESSION}` with `expires_with_session: true`. Long-term continuity belongs to `{PROJECT_STATE}` and is selected through `{CONTEXT_VIEW}` plus `{projection['view_ref']}`.",
        "",
        "## Review boundary",
        "",
        "This is a validated candidate example. It admits no artifact or relation, activates no Agent or runtime, performs no migration or cutover, and requires a separate exact owner-reviewed admission proposal.",
        "",
    ]
    (ROOT / "REVIEW.md").write_text("\n".join(review), encoding="utf-8")


def main() -> None:
    for path in (ARTIFACTS, RELATIONS, ONTOLOGY):
        if path.exists():
            shutil.rmtree(path)
    build_base_artifacts()
    bind_artifact_relation_refs()
    build_relations()
    build_ontology_projection()
    build_pack()
    print(json.dumps(load(ROOT / "pack.json")["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
