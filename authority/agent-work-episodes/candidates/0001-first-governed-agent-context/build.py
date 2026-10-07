#!/usr/bin/env python3
"""Build the first closed, governed Agent work episode candidate."""

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
MODEL = LAB / "authority/admissions/project-state-bootstrap/v1"
FOUNDATION = LAB / "authority/admissions/cyberalchemy-lab-operational-foundation/v1"
OWNER = "role:repository-owner"
SCOPE = "scope:cyberalchemy-lab-first-agent-episode"
CHALLENGE = "challenge-contract:cyberalchemy-lab-operational-foundation"
POLICY = "policy:cyberalchemy-lab-operational-foundation"
PROJECT = "project:cyberalchemy-v2-to-lab-migration"
INTENT = "intent:establish-cyberalchemy-lab-operational-foundation"
CONTEXT = "context:cyberalchemy-v2-to-lab-migration"
CAPABILITY = "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"
OLD_STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0071"
NEW_STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0072"
SEM_HISTORY = "project-semantic-event-history:cyberalchemy-v2-to-lab-migration"
GOV_HISTORY = "project-governance-event-history:cyberalchemy-v2-to-lab-migration"
REQUEST = "context-request:first-governed-agent-episode"
VIEW = "context-view:first-governed-agent-episode:2026-10-06"
WORK = "work:materialize-first-governed-agent-episode"
ASSIGNMENT = "agent-assignment:first-governed-agent-episode"
PRINCIPAL = "principal:repository-owner"
PROFILE = "agent-profile:governed-repository-candidate-authoring"
AGENT_CAPABILITY = "agent-capability:governed-repository-candidate-authoring"
IMPLEMENTATION = "implementation:codex-local-repository-agent"
SCHEME = "classification-scheme:agent-runtime-posture"
VALUE = "classification-value:ephemeral-machine-agent"
CLASSIFICATION = "classification-assignment:first-governed-agent-episode"
AGENT = "agent-instance:first-governed-agent-episode:2026-10-06"
SESSION = "agent-session:first-governed-agent-episode:2026-10-06"
ONTOLOGY = "ontology:cyberalchemy-lab-operational-context"
CUT = "ontology-cut:cyberalchemy-lab-operational-context:decision-0072"
ONTOLOGY_VIEW = "ontology-view:first-governed-agent-episode:2026-10-06"
STATE_NODE = "ontology-node:first-agent-episode:project-state-decision-0072"
PROJECT_NODE = "ontology-node:first-agent-episode:project"
STATE_PROJECT_EDGE = "ontology-edge:first-agent-episode:state-member-of-project"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def fixture(kind: str) -> dict[str, Any]:
    version = "v2" if kind == "ontology-node" else "v1"
    return copy.deepcopy(load(LAB / f"authority/artifact-types/{kind}/{version}/fixtures/valid/record.json"))


def relation_ref(kind: str, direction: str, counterpart_kind: str, counterpart_ref: str) -> dict[str, str]:
    return {"relation_kind_ref": kind, "direction": direction, "counterpart_kind": counterpart_kind, "counterpart_ref": counterpart_ref}


def standard(kind: str, node_id: str, name: str, relations: list[dict[str, str]], claim: str) -> dict[str, Any]:
    record = fixture(kind)
    record.update({"node_id": node_id, "name": name, "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "authority_effect": "none", "successor_refs": [], "claim_ceiling": claim})
    if "lifecycle_state" in record:
        record["lifecycle_state"] = "candidate"
    if "record_state" in record:
        record["record_state"] = "candidate"
    if "status" in record:
        record["status"] = "candidate-unadmitted"
    if "evidence_refs" in record:
        record["evidence_refs"] = ["docs/decisions/0072-project-state-bootstrap-admission/decision.json"]
    if "relation_refs" in record and isinstance(record["relation_refs"], list):
        record["relation_refs"] = relations
    return record


def build_state_records() -> dict[str, dict[str, Any]]:
    old_state = load(MODEL / "instances/artifacts/project-state.json")
    semantic = load(MODEL / "instances/artifacts/project-semantic-event-history.json")
    governance = load(MODEL / "instances/artifacts/project-governance-event-history.json")
    decision_path = "docs/decisions/0072-project-state-bootstrap-admission/decision.json"
    bundle_path = "authority/admissions/project-state-bootstrap/v1/bundle.json"
    authorization_path = "docs/decisions/0072-project-state-bootstrap-admission/authorization.json"
    material_refs = [
        {"path": decision_path, "sha256": sha(LAB / decision_path)},
        {"path": bundle_path, "sha256": sha(LAB / bundle_path)},
    ]
    artifact_refs = list(old_state["payload"]["artifact_refs"]) + [decision_path, bundle_path]
    state_materials = [{"path": path, "sha256": sha(LAB / path)} for path in artifact_refs]
    state_digest = "sha256:" + digest(state_materials)
    state = copy.deepcopy(old_state)
    state.update({
        "node_id": NEW_STATE,
        "name": "CyberAlchemy v2 migration operational state after Decision 0072",
        "scope_ref": SCOPE,
        "claim_ceiling": "Immutable candidate successor Project State through Decision 0072. Decision 0073 and the Agent episode candidate require a later owner admission and successor.",
        "evidence_refs": artifact_refs,
        "relation_refs": [
            relation_ref("relation.member-of", "source", "project", PROJECT),
            relation_ref("relation.successor-of", "source", "project-state", OLD_STATE),
        ],
    })
    state["payload"].update({
        "artifact_refs": artifact_refs,
        "cursor": "decision:0072",
        "decision_refs": list(old_state["payload"]["decision_refs"]) + ["CAL-DECISION-0072-PROJECT-STATE-BOOTSTRAP-ADMISSION"],
        "state_digest": state_digest,
    })
    sem_core = {
        "event_id": "project-semantic-event:cyberalchemy-v2-to-lab-migration:2",
        "cursor": 2,
        "previous_event_digest": semantic["payload"]["events"][-1]["event_digest"],
        "change_kind": "project-state-bootstrap-admitted",
        "predecessor_state_ref": OLD_STATE,
        "predecessor_state_digest": old_state["payload"]["state_digest"],
        "resulting_state_ref": NEW_STATE,
        "resulting_state_digest": state_digest,
        "material_refs": material_refs,
        "record_ref": bundle_path,
        "semantic_summary": "Decision 0072 admitted the Project event-history contracts and closed the first Project State bootstrap.",
    }
    sem_event = {**sem_core, "event_digest": digest(sem_core)}
    semantic["payload"]["events"].append(sem_event)
    semantic["payload"]["latest_cursor"] = 2
    semantic["payload"]["chain_digest"] = digest([x["event_digest"] for x in semantic["payload"]["events"]])
    semantic.update({"scope_ref": SCOPE, "evidence_refs": [decision_path, bundle_path], "claim_ceiling": "Candidate Project semantic history through Decision 0072; it records durable change and no governance authority."})
    gov_core = {
        "event_id": "project-governance-event:cyberalchemy-v2-to-lab-migration:2",
        "governance_cursor": 2,
        "previous_event_digest": governance["payload"]["events"][-1]["event_digest"],
        "semantic_event_ref": {"semantic_event_id": sem_event["event_id"], "semantic_event_digest": sem_event["event_digest"], "semantic_cursor": 2},
        "decision_ref": "CAL-DECISION-0072-PROJECT-STATE-BOOTSTRAP-ADMISSION",
        "authorization_ref": authorization_path,
        "authorization_sha256": sha(LAB / authorization_path),
        "policy_ref": POLICY,
        "challenge_contract_ref": CHALLENGE,
        "upstream_governance_evidence_refs": [authorization_path, decision_path, bundle_path],
        "record_ref": decision_path,
        "governance_summary": "Repository owner authorization admitted Decision 0072 under the operational foundation Policy and Challenge Contract.",
    }
    gov_event = {**gov_core, "event_digest": digest(gov_core)}
    governance["payload"]["events"].append(gov_event)
    governance["payload"]["latest_governance_cursor"] = 2
    governance["payload"]["chain_digest"] = digest([x["event_digest"] for x in governance["payload"]["events"]])
    governance.update({"scope_ref": SCOPE, "evidence_refs": [authorization_path, decision_path, bundle_path], "claim_ceiling": "Candidate Project governance history through Decision 0072; it observes exact authority evidence and cannot patch semantic state."})
    return {"project-state": state, "project-semantic-event-history": semantic, "project-governance-event-history": governance}


def build_episode_records(state_records: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    context_version = f"{CONTEXT}@decision-0071"
    request = fixture("context-request")
    request.update({
        "node_id": REQUEST, "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE,
        "context_ref": CONTEXT, "context_version_ref": context_version, "consumer_refs": [SESSION],
        "intended_uses": ["Provide bounded admitted inputs to the first ephemeral Agent work episode"],
        "selectors": ["Current Project State at Decision 0071", "Decision 0072 and its admitted bundle", "Operational foundation Policy and Challenge Contract", "Admitted-current contracts required by this episode"],
        "freshness_requirement": "Every selected repository file must match its declared SHA-256 when the Context View is built.",
        "exclusions": ["Secrets", "Live external services", "Unrelated dirty work", "Hidden cross-session memory", "Unadmitted ontology claims"],
        "output_constraints": ["Immutable digest-bound Context View", "Ephemeral Agent and Session", "No authority beyond candidate authoring", "Owner review before admission"],
        "budget": {"max_items": 32, "max_bytes": 1000000}, "requested_at": "2026-10-06T19:00:00Z",
        "owner_route": "route:repository-owner-review", "status": "candidate-unadmitted", "authority_effect": "none",
        "claim_ceiling": "Candidate Context Request for one bounded Agent work episode; it resolves no view and grants no authority by itself.",
    })
    included_paths = [
        "authority/admissions/project-state-bootstrap/v1/instances/artifacts/project-state.json",
        "docs/decisions/0072-project-state-bootstrap-admission/decision.json",
        "authority/admissions/project-state-bootstrap/v1/bundle.json",
        "authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/context.json",
        "authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/policy.json",
        "authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/challenge-contract.json",
    ]
    view = fixture("context-view")
    view.update({
        "node_id": VIEW, "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE,
        "request_ref": REQUEST, "context_ref": CONTEXT, "context_version_ref": context_version,
        "source_epoch": "project-state:decision-0071", "generated_at": "2026-10-06T19:05:00Z", "expires_at": "2026-10-07T19:05:00Z",
        "included_material": [{"source_ref": path, "selector": "whole-file", "sha256": sha(LAB / path)} for path in included_paths],
        "excluded_material": [{"source_ref": "runtime:live-services", "reason": "No runtime activation belongs to this candidate"}, {"source_ref": "memory:hidden-cross-session", "reason": "Machine Agent durable memory is forbidden"}],
        "lineage_refs": [REQUEST, OLD_STATE, "CAL-DECISION-0072-PROJECT-STATE-BOOTSTRAP-ADMISSION"],
        "limitations": ["The view covers the repository at one bounded source epoch", "The ontology view is a minimal exact projection of the Decision 0072 Project State, its Project, and their global member-of connection"],
        "selection_basis": "Exact request selectors, admitted-authority-first lookup, and digest-bound source bytes.",
        "owner_route": "route:repository-owner-review", "status": "candidate-unadmitted", "authority_effect": "none",
        "claim_ceiling": "Immutable candidate projection for one Agent Session; it owns no source authority and is not durable Agent memory.",
    })
    work = standard("work", WORK, "Materialize the first governed Agent work episode", [relation_ref("relation.member-of", "source", "project", PROJECT)], "Candidate Work record for building and validating the review package; completion establishes no admission or runtime activation.")
    work["payload"] = {"project_ref": PROJECT, "goal_refs": ["goal:first-governed-agent-context"], "work_statement": "Build the smallest closed candidate Agent context and Decision 0072 Project State successor for owner review.", "input_refs": [OLD_STATE, REQUEST], "output_refs": ["candidate:first-governed-agent-context/v1", "receipt:first-governed-agent-context-validation"], "completion_state": "candidate-complete"}
    assignment = standard("agent-assignment", ASSIGNMENT, "Build the first governed Agent work episode", [relation_ref("relation.member-of", "source", "project", PROJECT), relation_ref("relation.addresses-intent", "source", "intent", INTENT)], "Candidate assignment of one bounded task; it is not a Delegation and grants no authority beyond candidate authoring.")
    assignment["payload"] = {"eligible_agent_ref": AGENT, "intent_ref": INTENT, "project_ref": PROJECT, "work_ref": WORK, "owner_ref": PRINCIPAL, "period": SESSION, "expected_output_refs": ["candidate:first-governed-agent-context/v1"], "stop_conditions": ["candidate-validation-pass", "owner-review-boundary", "authority-boundary-reached"]}
    principal = standard("principal", PRINCIPAL, "Repository owner principal", [relation_ref("relation.acts-for", "target", "agent-instance", AGENT)], "Candidate repository-local Principal identity; it does not authenticate a person or grant authority beyond explicit owner decisions.")
    principal["payload"] = {"principal_kind": "human", "stable_subject_ref": "person-reference:repository-owner", "recognition_boundary_refs": ["boundary:cyberalchemy-lab-repository"], "registry_ref": "registry:lab-principals", "status": "active"}
    profile = standard("agent-profile", PROFILE, "Governed repository candidate authoring profile", [relation_ref("relation.has-capability", "source", "agent-capability", AGENT_CAPABILITY), relation_ref("relation.profiled-by", "target", "agent-instance", AGENT), relation_ref("relation.governed-by", "source", "policy", POLICY)], "Candidate Agent Profile for repository-local artifact authoring under owner review.")
    profile["payload"] = {"profile_purpose": "Build and validate bounded candidate governance artifacts", "allowed_input_kinds": ["context-view", "ontology-view", "project-state"], "allowed_output_kinds": ["project-state", "agent-instance", "agent-session", "typed-relation"], "policy_refs": [POLICY], "tool_class_refs": ["tool-class:repository-read", "tool-class:repository-write"], "stop_conditions": ["assignment-complete", "owner-review-boundary", "authority-boundary-reached"]}
    capability = standard("agent-capability", AGENT_CAPABILITY, "Governed repository candidate authoring", [relation_ref("relation.has-capability", "target", "agent-profile", PROFILE), relation_ref("relation.has-capability", "target", "agent-instance", AGENT)], "Candidate Agent Capability for repository-local construction and validation; it does not authorize admission.")
    capability["payload"] = {"capability_statement": "Author and validate exact candidate repository artifacts", "input_contract_refs": ["contract:exact-source-input"], "output_contract_refs": ["contract:candidate-artifact-output"], "evidence_contract_refs": ["contract:validation-receipt"], "failure_mode_refs": ["failure-mode:unsupported-authority-claim", "failure-mode:hidden-agent-memory"], "implementation_refs": [IMPLEMENTATION]}
    implementation = standard("implementation", IMPLEMENTATION, "Codex local repository Agent", [relation_ref("relation.realizes", "source", "product-capability", CAPABILITY)], "Candidate implementation identity for this local authoring episode; it proves no adoption, activation, or general runtime conformance.")
    implementation["payload"] = {"implementation_kind": "repository-agent", "realizes_capability_refs": [CAPABILITY], "conforms_to_schema_refs": ["cal.artifact-type.typed-relation/v2", "cal.artifact-type.agent-session/v1"], "environment_contract_ref": "contract:codex-local-repository", "execution_entrypoint_ref": "authority/agent-work-episodes/candidates/0001-first-governed-agent-context/validate.py"}
    scheme = standard("classification-scheme", SCHEME, "Agent runtime posture", [relation_ref("relation.member-of", "target", "classification-value", VALUE), relation_ref("relation.governed-by", "target", "classification-assignment", CLASSIFICATION)], "Candidate classification scheme distinguishing ephemeral machine execution from durable project state.")
    scheme["payload"] = {"scheme_name": "Agent runtime posture", "axis_refs": ["axis:actor-kind", "axis:memory-lifetime"], "value_refs": [VALUE], "cardinality_rules": ["one-runtime-posture-per-agent-instance"], "compatibility_rules": ["machine-agent-requires-ephemeral-instance", "session-memory-expires-with-session"], "mapping_refs": []}
    value = standard("classification-value", VALUE, "Ephemeral machine Agent", [relation_ref("relation.member-of", "source", "classification-scheme", SCHEME), relation_ref("relation.instance-of", "target", "agent-instance", AGENT)], "Candidate classification value stating that the machine Agent exists only for one bounded session.")
    value["payload"] = {"scheme_ref": SCHEME, "axis_ref": "axis:actor-kind", "value_code": "ephemeral-machine-agent", "definition_ref": "cal.definition.agent@1.0.0-candidate.1", "parent_value_refs": [], "compatibility_refs": ["rule:ephemeral-machine-agent", "rule:session-memory-expires"]}
    classification = standard("classification-assignment", CLASSIFICATION, "Classify first Agent as ephemeral", [relation_ref("relation.governed-by", "source", "classification-scheme", SCHEME)], "Candidate classification assignment for this exact Agent Instance and session period.")
    classification["payload"] = {"subject_ref": AGENT, "subject_version_ref": f"{AGENT}@candidate.1", "scheme_version_ref": f"{SCHEME}@candidate.1", "axis_ref": "axis:actor-kind", "value_ref": VALUE, "basis": "owner-declared-machine-agent-boundary", "action_ref": "action:materialize-first-governed-agent-episode", "method_ref": "method:concept-layer-optimization", "implementation_ref": IMPLEMENTATION, "evidence_refs": ["docs/decisions/0072-project-state-bootstrap-admission/decision.json"], "effective_period": SESSION, "status": "active"}
    agent_relations = [
        relation_ref("relation.acts-for", "source", "principal", PRINCIPAL), relation_ref("relation.has-capability", "source", "agent-capability", AGENT_CAPABILITY),
        relation_ref("relation.instance-of", "source", "classification-value", VALUE), relation_ref("relation.member-of", "source", "agent-session", SESSION),
        relation_ref("relation.performs", "source", "work", WORK), relation_ref("relation.profiled-by", "source", "agent-profile", PROFILE),
        relation_ref("relation.governed-by", "source", "policy", POLICY),
    ]
    agent = standard("agent-instance", AGENT, "Ephemeral first Agent context author", agent_relations, "Candidate representation of one ephemeral machine Agent execution; it owns no durable memory and expires with its session.")
    agent["payload"] = {"agent_classification_assignment_ref": CLASSIFICATION, "profile_ref": PROFILE, "implementation_ref": IMPLEMENTATION, "capability_refs": [AGENT_CAPABILITY], "accountable_principal_ref": PRINCIPAL, "session_ref": SESSION, "started_at": "2026-10-06T19:00:00Z", "terminated_at": "when-owner-review-boundary-closes"}

    ontology = fixture("ontology")
    ontology.update({"node_id": ONTOLOGY, "name": "CyberAlchemy Lab operational context ontology", "owner_ref": OWNER, "scope_ref": SCOPE, "challenge_route": CHALLENGE, "owner_route": "route:repository-owner-review", "ontology_version": "1.0.0-candidate.1", "promotion_state": "draft", "status": "candidate-unadmitted", "purpose": "Provide the smallest exact operational projection needed by the first Agent Session.", "boundaries": ["Projects only the current Project State, its Project, and their member-of connection", "Uses Project event histories as the replay source", "Creates no broader ontology truth or runtime activation"], "branch_refs": ["branch:operational-context"], "node_refs": [STATE_NODE, PROJECT_NODE], "relation_refs": [STATE_PROJECT_EDGE], "provenance_refs": [SEM_HISTORY, GOV_HISTORY, NEW_STATE], "role_assignment_refs": ["role:repository-owner"], "governance_rules": ["Project event histories remain replay sources", "Every projected edge binds one exact global Typed Relation", "Promotion requires an owner decision"], "confidence_policy_ref": POLICY, "authority_effect": "none", "claim_ceiling": "Candidate minimal ontology boundary for one Agent Session; it projects only exact repository subjects and one global Typed Relation."})
    event_set_digest = digest({"semantic_chain": state_records["project-semantic-event-history"]["payload"]["chain_digest"], "governance_chain": state_records["project-governance-event-history"]["payload"]["chain_digest"]})
    cut_digest = digest({"ontology_ref": ONTOLOGY, "semantic_cursor": 2, "source_event_set_digest": event_set_digest, "nodes": [], "edges": []})
    cut = standard("ontology-cut", CUT, "Minimal operational ontology cut at Decision 0072", [], "Candidate immutable minimal cut over the exact Project event cursor; it is derived and not a replay source.")
    cut["payload"] = {"ontology_ref": ONTOLOGY, "semantic_cursor": 2, "source_event_set_digest": event_set_digest, "node_refs": [], "edge_refs": [], "calculated_digest": cut_digest, "governance_join_policy_ref": "governance-join:exact-event-tuple/v1", "replay_source": False, "integrity_result": "pass"}
    ontology_view = standard("ontology-view", ONTOLOGY_VIEW, "First Agent episode minimal ontology view", [], "Candidate purpose-bounded minimal Ontology View; it contains exact projected subjects and has no replay or source authority.")
    ontology_view["payload"] = {"ontology_ref": ONTOLOGY, "cut_ref": CUT, "cut_digest": cut_digest, "selector_ref": "ontology-selector:first-agent-episode-empty", "consumer_ref": SESSION, "intended_use": "Make the absence of admitted operational ontology nodes and edges explicit to the first Agent Session.", "selected_node_refs": [], "selected_edge_refs": [], "exclusions": ["All unadmitted ontology projections", "Runtime activation", "Implicit authority", "Hidden Agent memory"], "freshness_at": "2026-10-06T19:10:00Z", "expires_at": "2026-10-07T19:10:00Z", "source_event_set_digest": event_set_digest, "semantic_cursor": 2, "governance_join_policy_ref": "governance-join:exact-event-tuple/v1", "replay_source": False}
    session_relations = [relation_ref("relation.consumes-view", "source", "context-view", VIEW), relation_ref("relation.consumes-view", "source", "ontology-view", ONTOLOGY_VIEW), relation_ref("relation.governed-by", "source", "policy", POLICY), relation_ref("relation.uses-tool", "source", "implementation", IMPLEMENTATION), relation_ref("relation.member-of", "target", "agent-instance", AGENT)]
    session = standard("agent-session", SESSION, "First governed Agent work episode", session_relations, "Candidate Agent Session; its short memory expires with the session and durable continuity remains Project State, Context View, and the bounded Ontology View.")
    session["payload"] = {"agent_instance_ref": AGENT, "assignment_ref": ASSIGNMENT, "context_view_ref": VIEW, "ontology_view_ref": ONTOLOGY_VIEW, "policy_refs": [POLICY], "authority_envelope_ref": "delegation:none-beyond-explicit-task", "input_refs": [INTENT, REQUEST, OLD_STATE], "budget_refs": ["budget:current-task"], "event_cursor": "project-semantic:2", "session_memory": {"selected_input_refs": [VIEW, ONTOLOGY_VIEW], "working_record_refs": [WORK, "candidate:first-governed-agent-context/v1"], "unresolved_questions": ["owner-admission-decision"], "expires_with_session": True}, "termination_state": "awaiting-owner-review"}
    return {"context-request": request, "context-view": view, "work": work, "agent-assignment": assignment, "principal": principal, "agent-profile": profile, "agent-capability": capability, "implementation": implementation, "classification-scheme": scheme, "classification-value": value, "classification-assignment": classification, "agent-instance": agent, "ontology": ontology, "ontology-cut": cut, "ontology-view": ontology_view, "agent-session": session}


def build_projection(records: dict[str, dict[str, Any]]) -> None:
    sem2 = records["project-semantic-event-history"]["payload"]["events"][-1]
    gov2 = records["project-governance-event-history"]["payload"]["events"][-1]
    state_path = ARTIFACTS / "project-state.json"
    project_path = FOUNDATION / "instances/artifacts/project.json"
    governance_binding = {
        "semantic_event_ref": {"semantic_event_id": sem2["event_id"], "semantic_event_digest": sem2["event_digest"], "semantic_cursor": 2},
        "governance_event_refs": [gov2["event_id"]],
        "evidence_confidence_ref": "confidence:exact-repository-bytes",
        "commitment_confidence_ref": "confidence:candidate-awaiting-owner-review",
        "challenge_contract_ref": CHALLENGE,
        "authority_effect": "none",
    }
    specs = [
        ("ontology-node-state", STATE_NODE, "Decision 0072 Project State", "project-state", NEW_STATE, f"{NEW_STATE}@candidate.1", sha(state_path), "system", "Current immutable candidate Project State through Decision 0072."),
        ("ontology-node-project", PROJECT_NODE, "CyberAlchemy v2 migration Project", "project", PROJECT, f"{PROJECT}@decision-0071", sha(project_path), "business", "Project coordinating CyberAlchemy v2 reconstruction and operational proving."),
    ]
    for kind, node_id, name, subject_kind, subject_ref, version_ref, subject_digest, branch, proposition in specs:
        node = standard("ontology-node", node_id, name, [], "Candidate derived Ontology Node binding one exact repository subject and event tuple; it is not a replay source.")
        node["payload"] = {
            "ontology_ref": ONTOLOGY, "ontology_manifest_ref": "candidate:first-governed-agent-context/v1",
            "represented_subject": {"kind": subject_kind, "ref": subject_ref, "version_ref": version_ref, "digest": subject_digest},
            "node_type_ref": f"ontology-node-type:{subject_kind}", "profile_ref": "ontology-profile:operational-context", "branch": branch,
            "semantic_state": {"lifecycle": "active", "label": name, "proposition": proposition, "semantic_components": [subject_kind, "identity", "lifecycle"], "semantic_definition_refs": [], "typed_properties": {"source_digest": subject_digest}, "use_obligations": ["Resolve the represented subject by exact digest"], "forbidden_collapse": ["Ontology Node is not the represented artifact", "Projection authority is not source authority"]},
            "governance_binding": copy.deepcopy(governance_binding), "provenance_refs": [SEM_HISTORY, GOV_HISTORY, subject_ref], "replay_source": False,
        }
        records[kind] = node
        dump(ARTIFACTS / f"{kind}.json", node)
    relation_path = RELATIONS / "state-project.json"
    relation = load(relation_path)
    edge = standard("ontology-edge", STATE_PROJECT_EDGE, "Project State belongs to migration Project", [], "Candidate derived Ontology Edge projecting one exact global Typed Relation; it is not a replay source.")
    edge["payload"] = {
        "ontology_ref": ONTOLOGY, "edge_mode": "global-projection", "relation_type_ref": "relation.member-of",
        "source_node_ref": STATE_NODE, "target_node_ref": PROJECT_NODE, "direction": "directed", "closed_qualifiers": relation["payload"]["qualifiers"],
        "global_typed_relation_binding": {"typed_relation_ref": relation["node_id"], "typed_relation_version_ref": f"{relation['node_id']}@candidate.1", "typed_relation_digest": sha(relation_path)},
        "local_interpretation": None, "lifecycle": "active", "forbidden_collapse": ["Ontology Edge is not the global Typed Relation", "Projection does not create new connection authority"],
        "semantic_event_ref": governance_binding["semantic_event_ref"], "replay_source": False,
    }
    records["ontology-edge"] = edge
    dump(ARTIFACTS / "ontology-edge.json", edge)
    source_event_set_digest = digest({"semantic_chain": records["project-semantic-event-history"]["payload"]["chain_digest"], "governance_chain": records["project-governance-event-history"]["payload"]["chain_digest"]})
    projection_set = {"ontology_ref": ONTOLOGY, "semantic_cursor": 2, "source_event_set_digest": source_event_set_digest, "nodes": [{"ref": STATE_NODE, "sha256": sha(ARTIFACTS / "ontology-node-state.json")}, {"ref": PROJECT_NODE, "sha256": sha(ARTIFACTS / "ontology-node-project.json")}], "edges": [{"ref": STATE_PROJECT_EDGE, "sha256": sha(ARTIFACTS / "ontology-edge.json")}]}
    cut_digest = digest(projection_set)
    records["ontology-cut"]["payload"].update({"source_event_set_digest": source_event_set_digest, "node_refs": [STATE_NODE, PROJECT_NODE], "edge_refs": [STATE_PROJECT_EDGE], "calculated_digest": cut_digest})
    records["ontology-view"]["payload"].update({"source_event_set_digest": source_event_set_digest, "selected_node_refs": [STATE_NODE, PROJECT_NODE], "selected_edge_refs": [STATE_PROJECT_EDGE], "cut_digest": cut_digest, "intended_use": "Provide the first Agent Session with the exact current Project State, Project, and membership connection."})
    dump(ARTIFACTS / "ontology-cut.json", records["ontology-cut"])
    dump(ARTIFACTS / "ontology-view.json", records["ontology-view"])


def make_relation(slug: str, kind: str, source_kind: str, source_ref: str, target_kind: str, target_ref: str, qualifiers: dict[str, str]) -> dict[str, Any]:
    return {
        "schema_version": "cyberalchemy-lab-typed-relation/v2", "node_id": f"typed-relation:first-agent-episode:{slug}", "kind": "typed-relation", "name": f"First Agent episode {kind}", "lifecycle_state": "candidate", "authority_effect": "none", "owner_ref": OWNER, "scope_ref": SCOPE,
        "evidence_refs": ["docs/decisions/0072-project-state-bootstrap-admission/decision.json"], "challenge_route": CHALLENGE, "successor_refs": [], "relation_refs": [],
        "payload": {"relation_kind_ref": kind, "source": {"kind": source_kind, "ref": source_ref, "version_ref": f"{source_ref}@candidate.1"}, "target": {"kind": target_kind, "ref": target_ref, "version_ref": f"{target_ref}@candidate.1"}, "qualifiers": qualifiers, "relation_lifecycle_state": "candidate", "relation_evidence_refs": ["candidate:first-governed-agent-context/v1"]},
        "claim_ceiling": "Candidate Typed Relation over exact endpoints; validation creates no connection authority or runtime effect.",
    }


def build_relations(view_digest: str, ontology_view_digest: str) -> list[dict[str, Any]]:
    specs = [
        ("state-successor", "relation.successor-of", "project-state", NEW_STATE, "project-state", OLD_STATE, {"succession_effect": "continues-and-supersedes-current-state"}),
        ("state-project", "relation.member-of", "project-state", NEW_STATE, "project", PROJECT, {"membership_role": "durable-project-state"}),
        ("request-context", "relation.requests-resolution-of", "context-request", REQUEST, "context", CONTEXT, {"context_version_ref": f"{CONTEXT}@decision-0071"}),
        ("view-context", "relation.derives-from", "context-view", VIEW, "context", CONTEXT, {"derivation_role": "bounded-context-resolution"}),
        ("view-request", "relation.fulfills-request", "context-view", VIEW, "context-request", REQUEST, {"fulfillment_role": "exact-bounded-resolution"}),
        ("value-scheme", "relation.member-of", "classification-value", VALUE, "classification-scheme", SCHEME, {"membership_role": "declared-runtime-posture"}),
        ("classification-scheme", "relation.governed-by", "classification-assignment", CLASSIFICATION, "classification-scheme", SCHEME, {"governance_role": "classification-contract"}),
        ("profile-capability", "relation.has-capability", "agent-profile", PROFILE, "agent-capability", AGENT_CAPABILITY, {"capability_version_ref": f"{AGENT_CAPABILITY}@candidate.1", "declaration_basis": "profile-contract"}),
        ("implementation-capability", "relation.realizes", "implementation", IMPLEMENTATION, "product-capability", CAPABILITY, {"realization_role": "candidate-authoring-tool", "exact_target_version_ref": f"{CAPABILITY}@decision-0071"}),
        ("work-project", "relation.member-of", "work", WORK, "project", PROJECT, {"membership_role": "bounded-project-work"}),
        ("assignment-project", "relation.member-of", "agent-assignment", ASSIGNMENT, "project", PROJECT, {"membership_role": "bounded-agent-assignment"}),
        ("assignment-intent", "relation.addresses-intent", "agent-assignment", ASSIGNMENT, "intent", INTENT, {"intent_resolution_ref": "intent-resolution:first-agent-episode", "addressing_role": "operationalize-agent-context"}),
        ("agent-principal", "relation.acts-for", "agent-instance", AGENT, "principal", PRINCIPAL, {"delegation_ref": "delegation:none-beyond-explicit-task", "scope_ref": SCOPE, "effective_period": SESSION, "revocation_state": "expires-with-session"}),
        ("agent-profile", "relation.profiled-by", "agent-instance", AGENT, "agent-profile", PROFILE, {"profile_version_ref": f"{PROFILE}@candidate.1", "binding_ref": ASSIGNMENT}),
        ("agent-capability", "relation.has-capability", "agent-instance", AGENT, "agent-capability", AGENT_CAPABILITY, {"capability_version_ref": f"{AGENT_CAPABILITY}@candidate.1", "declaration_basis": ASSIGNMENT}),
        ("agent-classification", "relation.instance-of", "agent-instance", AGENT, "classification-value", VALUE, {"parent_version_ref": f"{VALUE}@candidate.1", "binding_ref": CLASSIFICATION}),
        ("agent-session", "relation.member-of", "agent-instance", AGENT, "agent-session", SESSION, {"membership_role": "ephemeral-session-participant"}),
        ("agent-work", "relation.performs", "agent-instance", AGENT, "work", WORK, {"session_ref": SESSION, "participation_role": "candidate-author", "action_posture": "bounded-local-execution"}),
        ("agent-policy", "relation.governed-by", "agent-instance", AGENT, "policy", POLICY, {"governance_role": "ephemeral-agent-boundary"}),
        ("session-context-view", "relation.consumes-view", "agent-session", SESSION, "context-view", VIEW, {"view_digest": view_digest, "cursor": "project-state:decision-0071", "consumption_purpose": "bounded-task-context"}),
        ("session-ontology-view", "relation.consumes-view", "agent-session", SESSION, "ontology-view", ONTOLOGY_VIEW, {"view_digest": ontology_view_digest, "cursor": "project-semantic:2", "consumption_purpose": "explicit-empty-ontology-boundary"}),
        ("session-policy", "relation.governed-by", "agent-session", SESSION, "policy", POLICY, {"governance_role": "session-memory-and-authority-boundary"}),
        ("session-implementation", "relation.uses-tool", "agent-session", SESSION, "implementation", IMPLEMENTATION, {"tool_version_ref": f"{IMPLEMENTATION}@candidate.1", "invocation_contract_ref": "contract:codex-local-repository", "use_role": "candidate-construction-and-validation"}),
    ]
    return [make_relation(*spec) for spec in specs]


def main() -> None:
    if ROOT / "instances":
        shutil.rmtree(ROOT / "instances", ignore_errors=True)
    state_records = build_state_records()
    records = {**state_records, **build_episode_records(state_records)}
    filename = {kind: kind + ".json" for kind in records}
    for kind, record in records.items():
        dump(ARTIFACTS / filename[kind], record)
    relations = build_relations(sha(ARTIFACTS / "context-view.json"), sha(ARTIFACTS / "ontology-view.json"))
    for relation in relations:
        dump(RELATIONS / (relation["node_id"].split(":")[-1] + ".json"), relation)
    build_projection(records)
    relations = build_relations(sha(ARTIFACTS / "context-view.json"), sha(ARTIFACTS / "ontology-view.json"))
    for relation in relations:
        dump(RELATIONS / (relation["node_id"].split(":")[-1] + ".json"), relation)
    filename = {kind: kind + ".json" for kind in records}
    type_refs = {item["semantic_kind"]: item["artifact_type_ref"] for item in load(MODEL / "registries/artifact-type-registry.json")["admitted_contracts"] if item["lifecycle_state"] == "admitted-current"}
    artifact_entries = []
    for kind, record in sorted(records.items()):
        path = ARTIFACTS / filename[kind]
        semantic_kind = record["kind"]
        artifact_entries.append({"identity_ref": record["node_id"], "semantic_kind": semantic_kind, "carrier_type_ref": type_refs[semantic_kind], "version_ref": f"{record['node_id']}@candidate.1", "path": str(path.relative_to(LAB)), "sha256": sha(path)})
    relation_entries = []
    for relation in relations:
        path = RELATIONS / (relation["node_id"].split(":")[-1] + ".json")
        relation_entries.append({"relation_id": relation["node_id"], "relation_kind_ref": relation["payload"]["relation_kind_ref"], "path": str(path.relative_to(LAB)), "sha256": sha(path)})
    candidate = {
        "schema_version": "cyberalchemy-lab-agent-work-episode-candidate/v1", "candidate_id": "CAL-AGENT-WORK-EPISODE-0001", "status": "candidate-awaiting-owner-review", "authority_effect": "none",
        "title": "First governed Agent work episode and Decision 0072 Project State successor",
        "optimization": {"mode": "standard-assumed", "selected_unit": "closed-first-agent-work-episode", "rejected_smaller_unit": "six-record-agent-context-left-required-dependencies-dangling", "context_lineage_record_excluded": "The admitted Context Lineage Record/v2 models Context succession, not Context View source selection; the Context View lineage_refs carry this episode's exact selection lineage."},
        "inputs": {
            "decision_0072": {"path": "docs/decisions/0072-project-state-bootstrap-admission/decision.json", "sha256": sha(LAB / "docs/decisions/0072-project-state-bootstrap-admission/decision.json")},
            "project_state_bootstrap": {"path": "authority/admissions/project-state-bootstrap/v1/bundle.json", "sha256": sha(MODEL / "bundle.json")},
            "artifact_type_registry": {"path": "authority/admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json", "sha256": sha(MODEL / "registries/artifact-type-registry.json")},
            "relation_kind_registry": {"path": "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json", "sha256": sha(LAB / "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json")},
        },
        "counts": {"artifact_instances": len(artifact_entries), "typed_relation_instances": len(relation_entries), "semantic_events_appended": 1, "governance_events_appended": 1, "runtime_activations": 0},
        "artifact_instances": artifact_entries, "typed_relations": relation_entries,
        "memory_contract": {"machine_agent_ephemeral": True, "session_memory_expires": True, "standalone_agent_memory_artifact": False, "durable_memory_refs": [NEW_STATE, VIEW, ONTOLOGY_VIEW], "ontology_projection_state": "minimal-exact-project-state-view"},
        "excluded_effects": ["No admission or lifecycle transition is applied", "No runtime, consumer, service, deployment, or external system is activated", "No evidence claim, Finding, operational lesson, or local ontology interpretation is fabricated", "Decision 0073 is not self-included in the Decision 0072 successor state"],
        "claim_ceiling": "PASS proves a closed candidate Project State transition and first Agent work episode over admitted contracts. It does not admit any instance or relation and activates no runtime.",
    }
    dump(ROOT / "candidate.json", candidate)
    write(ROOT / "EPISODE.md", f"""# First governed Agent work episode

Status: **candidate awaiting owner review**

- Artifact instances: `{len(artifact_entries)}`
- Typed Relations: `{len(relation_entries)}`
- Semantic events appended: `1`
- Governance events appended: `1`
- Runtime activations: `0`

The candidate advances durable Project State from `{OLD_STATE}` to `{NEW_STATE}` and materializes one bounded Agent work episode. The machine Agent and its session are ephemeral. Durable continuity belongs to Project State, the immutable Context View, and the minimal exact Ontology View. Session memory expires at the review boundary.

## Context lineage decision

No Context Lineage Record is created. Its admitted v2 contract describes Context version succession, while this episode resolves one Context version into a Context View. Exact selection lineage is carried by `context-view.lineage_refs` and digest-bound included material.

## Review boundary

No admission has been applied. Owner review of the complete example is required before any Decision 0073 authorization.

## Claim ceiling

{candidate['claim_ceiling']}
""")
    write(ROOT / "REVIEW.md", """# Decision 0073 candidate review

Review these records in order:

1. `instances/artifacts/project-state.json` and the two Project histories.
2. `instances/artifacts/context-request.json` and `context-view.json`.
3. `classification-scheme.json`, `classification-value.json`, and `classification-assignment.json`.
4. `principal.json`, `agent-profile.json`, `agent-capability.json`, and `implementation.json`.
5. `work.json`, `agent-assignment.json`, `agent-instance.json`, and `agent-session.json`.
6. `ontology.json`, `ontology-cut.json`, and `ontology-view.json`.
7. The Typed Relations and validation receipt.

The ontology projection is intentionally minimal: it contains only the exact Decision 0072 Project State, its Project, and the candidate global `member-of` relation. It introduces no local interpretation and binds every projected subject and edge by digest.
""")
    print(json.dumps(candidate["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
