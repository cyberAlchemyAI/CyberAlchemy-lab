#!/usr/bin/env python3
"""Validate the Decision 0073 proposal and immutable postimage."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HERE = ROOT.parent
LAB = HERE.parents[2]
CANDIDATE = LAB / "authority/agent-work-episodes/candidates/0001-first-governed-agent-context"
POST = ROOT / "bundle-postimage"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    run = subprocess.run([sys.executable, str(CANDIDATE / "validate.py")], cwd=LAB, check=False)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    required = [ROOT / "proposal.json", POST / "bundle.json", POST / "artifact-instance-admission.json", POST / "typed-relation-admission.json"]
    missing = [str(path.relative_to(LAB)) for path in required if not path.is_file()]
    if missing:
        print(json.dumps({"result": "FAIL", "missing": missing}, sort_keys=True))
        return 1
    proposal = load(ROOT / "proposal.json")
    bundle = load(POST / "bundle.json")
    candidate = load(CANDIDATE / "candidate.json")
    artifacts = load(POST / "artifact-instance-admission.json")
    relations = load(POST / "typed-relation-admission.json")
    check("candidate-validation-current", run.returncode == 0 and proposal["inputs"]["candidate"]["sha256"] == sha(CANDIDATE / "candidate.json"), proposal["inputs"])
    check("proposal-bundle-binding", proposal["postimage"]["sha256"] == sha(POST / "bundle.json"), proposal["postimage"])
    closure = [{"path": item["path"], "current": sha(POST / item["path"]) == item["sha256"]} for item in bundle["files"]]
    check("immutable-bundle-closure", len(closure) == len(bundle["files"]) and all(item["current"] for item in closure), closure)
    copied_artifacts = [sha(POST / "instances/artifacts" / Path(item["path"]).name) == item["sha256"] for item in candidate["artifact_instances"]]
    copied_relations = [sha(POST / "instances/typed-relations" / Path(item["path"]).name) == item["sha256"] for item in candidate["typed_relations"]]
    check("exact-candidate-bytes", all(copied_artifacts) and all(copied_relations), {"artifacts": sum(copied_artifacts), "relations": sum(copied_relations)})
    expected = {"artifact_instances_admitted": 22, "typed_relation_instances_admitted": 23, "semantic_events_admitted": 1, "governance_events_admitted": 1, "predecessor_project_states_historical": 1, "predecessor_history_versions_historical": 2, "agent_instances_closed": 1, "agent_sessions_closed": 1, "runtime_activations": 0}
    check("exact-effects", bundle["counts"] == proposal["proposed_effects"] == expected and artifacts["count"] == 22 and relations["count"] == 23, bundle["counts"])
    transitions_ok = len(artifacts["predecessor_transitions"]) == 3 and all(item["bytes_preserved"] and sha(LAB / item["path"]) == item["sha256"] for item in artifacts["predecessor_transitions"])
    check("predecessor-preservation", transitions_ok, artifacts["predecessor_transitions"])
    closure_record = artifacts["operational_closure"]
    check("ephemeral-agent-closure", closure_record["runtime_active"] is False and closure_record["session_memory_retained"] is False and closure_record["agent_session_disposition"] == "closed-at-owner-review-boundary", closure_record)
    correction = proposal["admission_correction"]
    check("reviewed-model-consistency-repair", correction["semantic_scope_changed"] is False and correction["admission_candidate_sha256"] == sha(CANDIDATE / "candidate.json"), correction)
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    output = {"schema_version": "cyberalchemy-lab-first-governed-agent-work-episode-proposal-validation/v1", "result": result, "checks": checks, "materials": {"proposal_sha256": sha(ROOT / "proposal.json"), "bundle_sha256": sha(POST / "bundle.json"), "candidate_sha256": sha(CANDIDATE / "candidate.json")}, "claim_ceiling": "PASS proves the proposal is an exact closed admission postimage of the corrected reviewed candidate. It applies no authority effect."}
    (ROOT / "validation.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": result, "checks": len(checks), **output["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
