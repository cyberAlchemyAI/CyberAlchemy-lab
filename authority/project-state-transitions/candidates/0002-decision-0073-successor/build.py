#!/usr/bin/env python3
"""Build the Decision 0073 Project State successor candidate."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
CURRENT = LAB / "authority/admissions/first-governed-agent-work-episode/v1"
DECISION_DIR = LAB / "docs/decisions/0073-first-governed-agent-work-episode-admission"
ARTIFACTS = ROOT / "instances/artifacts"
RELATIONS = ROOT / "instances/typed-relations"
PROJECT = "project:cyberalchemy-v2-to-lab-migration"
OLD_STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0072"
NEW_STATE = "project-state:cyberalchemy-v2-to-lab-migration:decision-0073"
SEMANTIC_HISTORY = "project-semantic-event-history:cyberalchemy-v2-to-lab-migration"
GOVERNANCE_HISTORY = "project-governance-event-history:cyberalchemy-v2-to-lab-migration"
DECISION = "CAL-DECISION-0073-FIRST-GOVERNED-AGENT-WORK-EPISODE-ADMISSION"
OWNER = "role:repository-owner"
SCOPE = "scope:cyberalchemy-lab-decision-0073-successor"
CHALLENGE = "challenge-contract:cyberalchemy-lab-operational-foundation"
POLICY = "policy:cyberalchemy-lab-operational-foundation"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def material(path: Path) -> dict:
    return {"path": str(path.relative_to(LAB)), "sha256": sha(path)}


def with_event_digest(event: dict) -> dict:
    result = copy.deepcopy(event)
    result["event_digest"] = digest(event)
    return result


def build_relation(template_name: str, output_name: str, relation_id: str, source: dict, target: dict, evidence_ref: str) -> dict:
    template = load(CURRENT / "instances/typed-relations" / template_name)
    template.update(
        {
            "node_id": relation_id,
            "name": f"Decision 0073 successor {template['payload']['relation_kind_ref']}",
            "lifecycle_state": "candidate",
            "authority_effect": "none",
            "owner_ref": OWNER,
            "scope_ref": SCOPE,
            "evidence_refs": [evidence_ref],
            "challenge_route": CHALLENGE,
            "successor_refs": [],
            "relation_refs": [],
            "claim_ceiling": "Candidate exact Typed Relation for the Decision 0073 Project State successor; it has no authority effect before admission.",
        }
    )
    template["payload"]["source"] = source
    template["payload"]["target"] = target
    template["payload"]["relation_lifecycle_state"] = "candidate"
    template["payload"]["relation_evidence_refs"] = [evidence_ref]
    dump(RELATIONS / output_name, template)
    return {
        "relation_id": relation_id,
        "relation_kind_ref": template["payload"]["relation_kind_ref"],
        "source_ref": source["ref"],
        "target_ref": target["ref"],
        "path": str((RELATIONS / output_name).relative_to(LAB)),
        "sha256": sha(RELATIONS / output_name),
    }


def main() -> None:
    decision_path = DECISION_DIR / "decision.json"
    authorization_path = DECISION_DIR / "authorization.json"
    bundle_path = CURRENT / "bundle.json"
    old_state_path = CURRENT / "instances/artifacts/project-state.json"
    old_semantic_path = CURRENT / "instances/artifacts/project-semantic-event-history.json"
    old_governance_path = CURRENT / "instances/artifacts/project-governance-event-history.json"
    decision = load(decision_path)
    old_state = load(old_state_path)
    old_semantic = load(old_semantic_path)
    old_governance = load(old_governance_path)
    if decision["status"] != "owner-admitted" or decision["current_project_state_ref"] != OLD_STATE:
        raise RuntimeError("Decision 0073 is not the admitted authority input expected by this successor")

    decision_material = material(decision_path)
    bundle_material = material(bundle_path)
    artifact_refs = old_state["payload"]["artifact_refs"] + [decision_material["path"], bundle_material["path"]]
    state_materials = [material(LAB / path) for path in artifact_refs]
    state_digest = "sha256:" + digest(state_materials)
    old_state_digest = old_state["payload"]["state_digest"]

    state = copy.deepcopy(old_state)
    state.update(
        {
            "node_id": NEW_STATE,
            "name": "CyberAlchemy v2 migration operational state after Decision 0073",
            "lifecycle_state": "candidate",
            "scope_ref": SCOPE,
            "evidence_refs": artifact_refs,
            "claim_ceiling": "Immutable candidate successor Project State through Decision 0073. It records the admitted first governed Agent work episode and creates no later decision, Agent runtime, evidence claim, or external effect.",
            "relation_refs": [
                {"relation_kind_ref": "relation.member-of", "direction": "source", "counterpart_kind": "project", "counterpart_ref": PROJECT},
                {"relation_kind_ref": "relation.successor-of", "direction": "source", "counterpart_kind": "project-state", "counterpart_ref": OLD_STATE},
            ],
        }
    )
    state["payload"].update(
        {
            "cursor": "decision:0073",
            "artifact_refs": artifact_refs,
            "decision_refs": old_state["payload"]["decision_refs"] + [DECISION],
            "state_digest": state_digest,
        }
    )
    dump(ARTIFACTS / "project-state.json", state)

    semantic_core = {
        "event_id": "project-semantic-event:cyberalchemy-v2-to-lab-migration:3",
        "cursor": 3,
        "previous_event_digest": old_semantic["payload"]["events"][-1]["event_digest"],
        "change_kind": "first-governed-agent-work-episode-admitted",
        "predecessor_state_ref": OLD_STATE,
        "predecessor_state_digest": old_state_digest,
        "resulting_state_ref": NEW_STATE,
        "resulting_state_digest": state_digest,
        "material_refs": [decision_material, bundle_material],
        "record_ref": bundle_material["path"],
        "semantic_summary": "Decision 0073 admitted the first governed Agent work episode, its exact Context and Ontology projections, and the closed ephemeral Agent boundary.",
    }
    semantic_event = with_event_digest(semantic_core)
    semantic = copy.deepcopy(old_semantic)
    semantic.update(
        {
            "lifecycle_state": "candidate",
            "scope_ref": SCOPE,
            "evidence_refs": [decision_material["path"], bundle_material["path"]],
            "claim_ceiling": "Candidate Project semantic history through Decision 0073; it appends one exact durable transition and supplies no governance authority.",
        }
    )
    semantic["payload"]["events"] = old_semantic["payload"]["events"] + [semantic_event]
    semantic["payload"]["latest_cursor"] = 3
    semantic["payload"]["chain_digest"] = digest([event["event_digest"] for event in semantic["payload"]["events"]])
    dump(ARTIFACTS / "project-semantic-event-history.json", semantic)

    governance_core = {
        "event_id": "project-governance-event:cyberalchemy-v2-to-lab-migration:3",
        "governance_cursor": 3,
        "previous_event_digest": old_governance["payload"]["events"][-1]["event_digest"],
        "semantic_event_ref": {"semantic_event_id": semantic_event["event_id"], "semantic_event_digest": semantic_event["event_digest"], "semantic_cursor": 3},
        "decision_ref": DECISION,
        "authorization_ref": str(authorization_path.relative_to(LAB)),
        "authorization_sha256": sha(authorization_path),
        "policy_ref": POLICY,
        "challenge_contract_ref": CHALLENGE,
        "upstream_governance_evidence_refs": [str(authorization_path.relative_to(LAB)), decision_material["path"], bundle_material["path"]],
        "record_ref": decision_material["path"],
        "governance_summary": "Repository owner authorization admitted Decision 0073 under the operational foundation Policy and Challenge Contract and closed the ephemeral Agent review boundary.",
    }
    governance_event = with_event_digest(governance_core)
    governance = copy.deepcopy(old_governance)
    governance.update(
        {
            "lifecycle_state": "candidate",
            "scope_ref": SCOPE,
            "evidence_refs": governance_core["upstream_governance_evidence_refs"],
            "claim_ceiling": "Candidate Project governance history through Decision 0073; it binds exact owner authority to semantic event 3 and cannot patch semantic state.",
        }
    )
    governance["payload"]["events"] = old_governance["payload"]["events"] + [governance_event]
    governance["payload"]["latest_governance_cursor"] = 3
    governance["payload"]["chain_digest"] = digest([event["event_digest"] for event in governance["payload"]["events"]])
    dump(ARTIFACTS / "project-governance-event-history.json", governance)

    evidence_ref = "candidate:decision-0073-project-state-successor/v1"
    relations = [
        build_relation(
            "state-successor.json",
            "successor-state-successor-of-decision-0072.json",
            "typed-relation:decision-0073-successor:state-successor",
            {"kind": "project-state", "ref": NEW_STATE, "version_ref": NEW_STATE + "@candidate.1"},
            {"kind": "project-state", "ref": OLD_STATE, "version_ref": OLD_STATE + "@candidate.1"},
            evidence_ref,
        ),
        build_relation(
            "state-project.json",
            "successor-state-member-of-project.json",
            "typed-relation:decision-0073-successor:state-project",
            {"kind": "project-state", "ref": NEW_STATE, "version_ref": NEW_STATE + "@candidate.1"},
            {"kind": "project", "ref": PROJECT, "version_ref": PROJECT + "@foundation.1"},
            evidence_ref,
        ),
    ]
    artifacts = []
    for name, carrier, kind, identity, version in [
        ("project-semantic-event-history.json", "cal.artifact-type.project-semantic-event-history/v1", "project-semantic-event-history", SEMANTIC_HISTORY, SEMANTIC_HISTORY + "@candidate.3"),
        ("project-governance-event-history.json", "cal.artifact-type.project-governance-event-history/v1", "project-governance-event-history", GOVERNANCE_HISTORY, GOVERNANCE_HISTORY + "@candidate.3"),
        ("project-state.json", "cal.artifact-type.project-state/v1", "project-state", NEW_STATE, NEW_STATE + "@candidate.1"),
    ]:
        path = ARTIFACTS / name
        artifacts.append({"identity_ref": identity, "version_ref": version, "semantic_kind": kind, "carrier_type_ref": carrier, "path": str(path.relative_to(LAB)), "sha256": sha(path)})

    inputs = {
        "decision_0073": {**decision_material, "decision_id": DECISION},
        "decision_0073_authorization": material(authorization_path),
        "decision_0073_bundle": bundle_material,
        "predecessor_project_state": material(old_state_path),
        "predecessor_semantic_history": material(old_semantic_path),
        "predecessor_governance_history": material(old_governance_path),
        "project_state_schema": material(LAB / "authority/artifact-types/project-state/v1/schema.json"),
        "semantic_history_schema": material(LAB / "authority/artifact-types/project-semantic-event-history/v1/schema.json"),
        "governance_history_schema": material(LAB / "authority/artifact-types/project-governance-event-history/v1/schema.json"),
        "typed_relation_schema": material(LAB / "authority/artifact-types/typed-relation/v2/schema.json"),
    }
    transition = {
        "schema_version": "cyberalchemy-lab-project-state-successor-candidate/v1",
        "transition_id": "CAL-PROJECT-STATE-SUCCESSOR-0002",
        "title": "Decision 0073 Project State successor",
        "status": "candidate-awaiting-owner-review",
        "authority_effect": "none",
        "project_ref": PROJECT,
        "predecessor_state_ref": OLD_STATE,
        "successor_state_ref": NEW_STATE,
        "inputs": inputs,
        "artifact_instances": artifacts,
        "typed_relations": relations,
        "events_appended": {"semantic": 1, "governance": 1, "resulting_semantic_cursor": 3, "resulting_governance_cursor": 3},
        "counts": {"artifact_instances": 3, "typed_relation_instances": 2, "runtime_activations": 0},
        "integrity": {"predecessor_state_digest": old_state_digest, "successor_state_digest": state_digest, "semantic_chain_digest": semantic["payload"]["chain_digest"], "governance_chain_digest": governance["payload"]["chain_digest"]},
        "excluded_effects": ["No admission or lifecycle transition is applied", "Decision 0074 is not self-included in the Decision 0073 successor state", "No Agent, Session, consumer, service, deployment, or external runtime is activated", "No evidence claim, Finding, operational lesson, or new ontology interpretation is created"],
        "claim_ceiling": "PASS proves a closed candidate successor from Project State D72 to D73 with exact semantic and governance event 3. It admits nothing and activates no runtime.",
    }
    dump(ROOT / "transition.json", transition)
    (ROOT / "TRANSITION.md").write_text(
        "# Decision 0073 Project State successor\n\n"
        "Status: **candidate awaiting owner review**\n\n"
        "- Artifact instances: `3`\n"
        "- Typed Relations: `2`\n"
        "- Semantic events appended: `1`\n"
        "- Governance events appended: `1`\n"
        "- Runtime activations: `0`\n\n"
        f"`{NEW_STATE}` succeeds `{OLD_STATE}` and binds the exact Decision 0073 decision, authorization, and immutable admission bundle.\n\n"
        "Decision 0074 is deliberately absent and must authorize admission later.\n",
        encoding="utf-8",
    )
    (ROOT / "REVIEW.md").write_text(
        "# Decision 0073 successor review\n\n"
        "Review in this order:\n\n"
        "1. `instances/artifacts/project-state.json` for the complete D73 material set.\n"
        "2. `instances/artifacts/project-semantic-event-history.json` for semantic event 3.\n"
        "3. `instances/artifacts/project-governance-event-history.json` for governance event 3.\n"
        "4. The two Typed Relations for `successor-of` and `member-of`.\n"
        "5. `receipts/validation.json` for exact closure and claim ceiling.\n",
        encoding="utf-8",
    )
    print(json.dumps({"artifact_instances": 3, "typed_relation_instances": 2, "semantic_cursor": 3, "governance_cursor": 3, "runtime_activations": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
