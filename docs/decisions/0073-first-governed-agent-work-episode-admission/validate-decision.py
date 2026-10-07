#!/usr/bin/env python3
"""Validate applied Decision 0073 and its immutable admission bundle."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
FINAL = LAB / "authority/admissions/first-governed-agent-work-episode/v1"
CANDIDATE = LAB / "authority/agent-work-episodes/candidates/0001-first-governed-agent-context"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    required = [HERE / "authorization.json", HERE / "decision.json", HERE / "receipts/application.json", FINAL / "bundle.json"]
    missing = [str(path.relative_to(LAB)) for path in required if not path.is_file()]
    if missing:
        print(json.dumps({"result": "FAIL", "missing": missing}, sort_keys=True))
        return 1
    authorization = load(HERE / "authorization.json")
    decision = load(HERE / "decision.json")
    receipt = load(HERE / "receipts/application.json")
    proposal = load(HERE / "proposal/proposal.json")
    bundle = load(FINAL / "bundle.json")
    artifacts = load(FINAL / "artifact-instance-admission.json")
    relations = load(FINAL / "typed-relation-admission.json")
    candidate = load(CANDIDATE / "candidate.json")
    check("authorization-exact", authorization["authorized"] is True and authorization["decision_id"] == decision["decision_id"] and authorization["proposal_sha256"] == sha(HERE / "proposal/proposal.json") and authorization["admission_candidate_sha256"] == sha(CANDIDATE / "candidate.json"), authorization)
    check("decision-bundle-binding", decision["admission_bundle"]["sha256"] == sha(FINAL / "bundle.json") == proposal["postimage"]["sha256"] and bundle["decision_id"] == decision["decision_id"], decision["admission_bundle"])
    files = [{"path": item["path"], "current": sha(FINAL / item["path"]) == item["sha256"]} for item in bundle["files"]]
    check("immutable-bundle-closure", all(item["current"] for item in files), files)
    artifact_bytes = [sha(FINAL / "instances/artifacts" / Path(item["path"]).name) == item["sha256"] for item in candidate["artifact_instances"]]
    relation_bytes = [sha(FINAL / "instances/typed-relations" / Path(item["path"]).name) == item["sha256"] for item in candidate["typed_relations"]]
    check("admitted-instance-bytes", all(artifact_bytes) and all(relation_bytes), {"artifacts": sum(artifact_bytes), "relations": sum(relation_bytes)})
    expected = {"artifact_instances_admitted": 22, "typed_relation_instances_admitted": 23, "semantic_events_admitted": 1, "governance_events_admitted": 1, "predecessor_project_states_historical": 1, "predecessor_history_versions_historical": 2, "agent_instances_closed": 1, "agent_sessions_closed": 1, "runtime_activations": 0}
    check("exact-effects", bundle["counts"] == decision["effects"] == receipt["effects"] == expected and artifacts["count"] == 22 and relations["count"] == 23, bundle["counts"])
    predecessors_ok = len(artifacts["predecessor_transitions"]) == 3 and all(item["bytes_preserved"] and sha(LAB / item["path"]) == item["sha256"] for item in artifacts["predecessor_transitions"])
    check("predecessor-preservation", predecessors_ok, artifacts["predecessor_transitions"])
    state = load(FINAL / "instances/artifacts/project-state.json")
    semantic = load(FINAL / "instances/artifacts/project-semantic-event-history.json")
    governance = load(FINAL / "instances/artifacts/project-governance-event-history.json")
    state_ok = state["node_id"] == decision["current_project_state_ref"] and state["payload"]["cursor"] == "decision:0072" and decision["decision_id"] not in state["payload"]["decision_refs"] and len(semantic["payload"]["events"]) == 2 and len(governance["payload"]["events"]) == 2
    check("project-state-successor-boundary", state_ok, {"state_ref": state["node_id"], "cursor": state["payload"]["cursor"], "semantic_events": len(semantic["payload"]["events"]), "governance_events": len(governance["payload"]["events"])})
    closure = load(FINAL / "operational-closure.json")
    check("ephemeral-agent-memory-boundary", closure["runtime_active"] is False and closure["session_memory_retained"] is False and closure["agent_instance_disposition"] == "terminated-at-owner-review-boundary" and closure["agent_session_disposition"] == "closed-at-owner-review-boundary", closure)
    correction = load(FINAL / "admission-correction.json")
    check("admission-correction-bounded", correction["semantic_scope_changed"] is False and correction["admission_candidate_sha256"] == sha(CANDIDATE / "candidate.json") and "minimal exact" in correction["reviewed_model"], correction)
    check("application-receipt-current", receipt["result"] == "PASS" and receipt["materials"]["decision_sha256"] == sha(HERE / "decision.json") and receipt["materials"]["bundle_sha256"] == sha(FINAL / "bundle.json") and receipt["materials"]["candidate_sha256"] == sha(CANDIDATE / "candidate.json"), receipt["materials"])
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    output = {"schema_version": "cyberalchemy-lab-first-governed-agent-work-episode-decision-validation/v1", "result": result, "checks": checks, "materials": {"decision_sha256": sha(HERE / "decision.json"), "bundle_sha256": sha(FINAL / "bundle.json"), "candidate_sha256": sha(CANDIDATE / "candidate.json")}, "claim_ceiling": "PASS proves Decision 0073, its immutable bundle, exact admitted records and connections, Project State boundary, and closed ephemeral Agent memory boundary remain exact. It proves no runtime activation or later successor state."}
    receipt_path = HERE / "receipts/decision-validation.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": result, "checks": len(checks), **output["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
