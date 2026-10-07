#!/usr/bin/env python3
"""Build the exact Decision 0073 Agent work episode admission postimage."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HERE = ROOT.parent
LAB = HERE.parents[2]
CANDIDATE = LAB / "authority/agent-work-episodes/candidates/0001-first-governed-agent-context"
POST = ROOT / "bundle-postimage"
DECISION = "CAL-DECISION-0073-FIRST-GOVERNED-AGENT-WORK-EPISODE-ADMISSION"
FINAL = "authority/admissions/first-governed-agent-work-episode/v1"
REVIEWED_SHA = "a54b0aacf9adbe322d1e9030ac8c61dd77bd743586726337f93a8d2a5b324710"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def main() -> None:
    check = subprocess.run([sys.executable, str(CANDIDATE / "validate.py")], cwd=LAB, check=False)
    if check.returncode:
        raise RuntimeError("candidate validation failed")
    candidate = load(CANDIDATE / "candidate.json")
    validation = load(CANDIDATE / "receipts/validation.json")
    candidate_sha = sha(CANDIDATE / "candidate.json")
    if validation["result"] != "PASS" or validation["materials"]["candidate_sha256"] != candidate_sha:
        raise RuntimeError("candidate validation is stale")
    if POST.exists():
        shutil.rmtree(POST)

    copy(CANDIDATE / "candidate.json", POST / "source-candidate.json")
    copy(CANDIDATE / "EPISODE.md", POST / "SOURCE-EPISODE.md")
    copy(CANDIDATE / "REVIEW.md", POST / "SOURCE-REVIEW.md")
    copy(CANDIDATE / "receipts/validation.json", POST / "receipts/candidate-validation.json")

    artifact_entries = []
    for item in candidate["artifact_instances"]:
        source = LAB / item["path"]
        destination = POST / "instances/artifacts" / source.name
        copy(source, destination)
        artifact_entries.append(
            {
                **item,
                "source_path": item["path"],
                "source_sha256": item["sha256"],
                "admitted_instance_path": f"{FINAL}/instances/artifacts/{source.name}",
                "admitted_instance_sha256": sha(destination),
                "lifecycle_state": "admitted-current",
                "admission_decision_ref": DECISION,
            }
        )

    relation_entries = []
    for item in candidate["typed_relations"]:
        source = LAB / item["path"]
        destination = POST / "instances/typed-relations" / source.name
        copy(source, destination)
        record = load(source)
        relation_entries.append(
            {
                **item,
                "source_path": item["path"],
                "source_sha256": item["sha256"],
                "admitted_instance_path": f"{FINAL}/instances/typed-relations/{source.name}",
                "admitted_instance_sha256": sha(destination),
                "source_ref": record["payload"]["source"]["ref"],
                "source_kind": record["payload"]["source"]["kind"],
                "target_ref": record["payload"]["target"]["ref"],
                "target_kind": record["payload"]["target"]["kind"],
                "lifecycle_state": "admitted-current",
                "admission_decision_ref": DECISION,
            }
        )

    predecessor_transitions = [
        {
            "identity_ref": "project-state:cyberalchemy-v2-to-lab-migration:decision-0071",
            "version_ref": "project-state:cyberalchemy-v2-to-lab-migration:decision-0071@bootstrap.1",
            "path": "authority/admissions/project-state-bootstrap/v1/instances/artifacts/project-state.json",
            "sha256": "5e4efe8bf1a802b01f795b524d240b99467ebcb6e5b8062fe793a45566d7e7cc",
            "from": "admitted-current",
            "to": "admitted-historical",
            "bytes_preserved": True,
        },
        {
            "identity_ref": "project-semantic-event-history:cyberalchemy-v2-to-lab-migration",
            "version_ref": "project-semantic-event-history:cyberalchemy-v2-to-lab-migration@bootstrap.1",
            "path": "authority/admissions/project-state-bootstrap/v1/instances/artifacts/project-semantic-event-history.json",
            "sha256": "6ddc2fb725c716759f5090f2f7272c40f6ffe8ed16b5965f2136f973c0c21896",
            "from": "admitted-current",
            "to": "admitted-historical",
            "bytes_preserved": True,
        },
        {
            "identity_ref": "project-governance-event-history:cyberalchemy-v2-to-lab-migration",
            "version_ref": "project-governance-event-history:cyberalchemy-v2-to-lab-migration@bootstrap.1",
            "path": "authority/admissions/project-state-bootstrap/v1/instances/artifacts/project-governance-event-history.json",
            "sha256": "f180713a223c85bd910a5630b7fe7d5fb3c5fb4c3f0e3b41dcbfc634cfe11dde",
            "from": "admitted-current",
            "to": "admitted-historical",
            "bytes_preserved": True,
        },
    ]
    operational_closure = {
        "agent_instance_ref": "agent-instance:first-governed-agent-episode:2026-10-06",
        "agent_instance_disposition": "terminated-at-owner-review-boundary",
        "agent_session_ref": "agent-session:first-governed-agent-episode:2026-10-06",
        "agent_session_disposition": "closed-at-owner-review-boundary",
        "assignment_ref": "agent-assignment:first-governed-agent-episode",
        "assignment_disposition": "reviewed-complete",
        "work_ref": "work:materialize-first-governed-agent-episode",
        "work_disposition": "admitted-complete",
        "session_memory_retained": False,
        "runtime_active": False,
        "durable_continuity_refs": candidate["memory_contract"]["durable_memory_refs"],
    }
    correction = {
        "kind": "editorial-consistency-repair",
        "reviewed_candidate_sha256": REVIEWED_SHA,
        "admission_candidate_sha256": candidate_sha,
        "path": "instances/artifacts/context-view.json#/limitations/1",
        "reviewed_model": "minimal exact ontology projection with two nodes and one edge",
        "repair": "Replaced a stale empty-projection sentence with the reviewed minimal exact projection description.",
        "semantic_scope_changed": False,
    }
    dump(
        POST / "artifact-instance-admission.json",
        {
            "schema_version": "cyberalchemy-lab-artifact-instance-admission/v1",
            "decision_id": DECISION,
            "status": "owner-admitted-postimage",
            "authority_effect": "first-governed-agent-work-episode-instance-admission-only",
            "count": len(artifact_entries),
            "predecessor_transitions": predecessor_transitions,
            "operational_closure": operational_closure,
            "entries": artifact_entries,
            "runtime_activations": 0,
            "claim_ceiling": "Admits the 22 exact reviewed episode records, advances Project State and both history identities, and records the ephemeral Agent boundary as closed.",
        },
    )
    dump(
        POST / "typed-relation-admission.json",
        {
            "schema_version": "cyberalchemy-lab-typed-relation-instance-admission/v1",
            "decision_id": DECISION,
            "status": "owner-admitted-postimage",
            "authority_effect": "first-governed-agent-work-episode-relation-admission-only",
            "count": len(relation_entries),
            "entries": relation_entries,
            "relation_kinds_admitted": 0,
            "runtime_activations": 0,
            "claim_ceiling": "Admits only the 23 exact Typed Relation instances in the reviewed episode.",
        },
    )
    dump(POST / "operational-closure.json", operational_closure)
    dump(POST / "admission-correction.json", correction)
    (POST / "ADMISSION.md").write_text(
        "# First governed Agent work episode admission\n\n"
        "This immutable postimage admits the Decision 0072 Project State successor, exact Context and Ontology Views, "
        "and the bounded Agent work episode. The machine Agent and Session close at the owner review boundary; session "
        "memory is not retained. Durable continuity remains in Project State, Context View, and Ontology View.\n\n"
        "Decision 0073 itself is intentionally absent from the Decision 0072 state and must enter the next governed successor.\n",
        encoding="utf-8",
    )

    counts = {
        "artifact_instances_admitted": 22,
        "typed_relation_instances_admitted": 23,
        "semantic_events_admitted": 1,
        "governance_events_admitted": 1,
        "predecessor_project_states_historical": 1,
        "predecessor_history_versions_historical": 2,
        "agent_instances_closed": 1,
        "agent_sessions_closed": 1,
        "runtime_activations": 0,
    }
    files = [
        {"path": str(path.relative_to(POST)), "sha256": sha(path)}
        for path in sorted(POST.rglob("*"))
        if path.is_file() and path.name != "bundle.json"
    ]
    bundle = {
        "schema_version": "cyberalchemy-lab-first-governed-agent-work-episode-admission-bundle/v1",
        "bundle_id": "CAL-FIRST-GOVERNED-AGENT-WORK-EPISODE-BUNDLE-0073",
        "decision_id": DECISION,
        "status": "owner-admitted-postimage",
        "authority_effect": "first-governed-agent-work-episode-admission-only",
        "source_candidate_sha256": candidate_sha,
        "counts": counts,
        "current_project_state_ref": "project-state:cyberalchemy-v2-to-lab-migration:decision-0072",
        "files": files,
        "admission_correction": correction,
        "excluded_effects": candidate["excluded_effects"],
        "claim_ceiling": "Immutable Decision 0073 postimage. It admits the exact bounded records and relations, closes the ephemeral session boundary, and activates no runtime.",
    }
    dump(POST / "bundle.json", bundle)
    proposal = {
        "schema_version": "cyberalchemy-lab-first-governed-agent-work-episode-admission-proposal/v1",
        "decision_id": DECISION,
        "title": "Admit the first governed Agent work episode and Decision 0072 Project State successor",
        "status": "candidate-awaiting-owner-authorization",
        "authority_effect": "none",
        "authorization_present": False,
        "inputs": {
            "candidate": {"path": str((CANDIDATE / "candidate.json").relative_to(LAB)), "sha256": candidate_sha},
            "validation": {"path": str((CANDIDATE / "receipts/validation.json").relative_to(LAB)), "sha256": sha(CANDIDATE / "receipts/validation.json"), "result": "PASS"},
        },
        "admission_correction": correction,
        "postimage": {"path": str((POST / "bundle.json").relative_to(LAB)), "sha256": sha(POST / "bundle.json"), "final_path": FINAL},
        "proposed_effects": counts,
        "atomic_transaction": ["Verify candidate and proposal", "Verify exact owner authorization", "Install immutable bundle", "Write Decision 0073 and receipts"],
        "excluded_effects": candidate["excluded_effects"],
        "claim_ceiling": "Proposal only; it has no authority effect before atomic application.",
    }
    dump(ROOT / "proposal.json", proposal)
    (ROOT / "PROPOSAL.md").write_text(
        "# Decision 0073 proposal\n\n"
        "- Artifact instances: `22`\n"
        "- Typed Relations: `23`\n"
        "- Semantic events: `1`\n"
        "- Governance events: `1`\n"
        "- Agent instances closed: `1`\n"
        "- Agent sessions closed: `1`\n"
        "- Runtime activations: `0`\n\n"
        f"Candidate: `{candidate_sha}`\n\nBundle: `{proposal['postimage']['sha256']}`\n\n{proposal['claim_ceiling']}\n",
        encoding="utf-8",
    )
    print(json.dumps({"candidate_sha256": candidate_sha, "bundle_sha256": proposal["postimage"]["sha256"], **counts}, sort_keys=True))


if __name__ == "__main__":
    main()
