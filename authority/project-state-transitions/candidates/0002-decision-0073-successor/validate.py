#!/usr/bin/env python3
"""Validate the Decision 0073 Project State successor candidate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
CURRENT = LAB / "authority/admissions/first-governed-agent-work-episode/v1"
DECISION_DIR = LAB / "docs/decisions/0073-first-governed-agent-work-episode-admission"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    transition_path = ROOT / "transition.json"
    tracked = [transition_path, *sorted((ROOT / "instances").rglob("*.json")), ROOT / "TRANSITION.md", ROOT / "REVIEW.md"]
    before = {str(path.relative_to(ROOT)): sha(path) for path in tracked}
    run = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=LAB, capture_output=True, text=True, check=False)
    after = {str(path.relative_to(ROOT)): sha(path) for path in tracked}
    transition = load(transition_path)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("deterministic-build", run.returncode == 0 and before == after, {"returncode": run.returncode, "stable": before == after})
    inputs = transition["inputs"]
    inputs_ok = all(sha(LAB / value["path"]) == value["sha256"] for value in inputs.values())
    check("inputs-current", inputs_ok, inputs)

    schemas = {
        "project-state": load(LAB / "authority/artifact-types/project-state/v1/schema.json"),
        "project-semantic-event-history": load(LAB / "authority/artifact-types/project-semantic-event-history/v1/schema.json"),
        "project-governance-event-history": load(LAB / "authority/artifact-types/project-governance-event-history/v1/schema.json"),
    }
    artifact_results = []
    for item in transition["artifact_instances"]:
        record = load(LAB / item["path"])
        errors = list(jsonschema.Draft202012Validator(schemas[item["semantic_kind"]]).iter_errors(record))
        artifact_results.append({"identity_ref": item["identity_ref"], "digest_current": sha(LAB / item["path"]) == item["sha256"], "schema_errors": [error.message for error in errors]})
    check("artifact-schemas-and-digests", all(item["digest_current"] and not item["schema_errors"] for item in artifact_results), artifact_results)

    relation_schema = load(LAB / "authority/artifact-types/typed-relation/v2/schema.json")
    relation_results = []
    for item in transition["typed_relations"]:
        record = load(LAB / item["path"])
        errors = list(jsonschema.Draft202012Validator(relation_schema).iter_errors(record))
        relation_results.append({"relation_id": item["relation_id"], "digest_current": sha(LAB / item["path"]) == item["sha256"], "manifest_exact": item["relation_id"] == record["node_id"] and item["relation_kind_ref"] == record["payload"]["relation_kind_ref"] and item["source_ref"] == record["payload"]["source"]["ref"] and item["target_ref"] == record["payload"]["target"]["ref"], "schema_errors": [error.message for error in errors]})
    check("typed-relations-exact-closure", all(item["digest_current"] and item["manifest_exact"] and not item["schema_errors"] for item in relation_results), relation_results)

    old_state = load(CURRENT / "instances/artifacts/project-state.json")
    state = load(ROOT / "instances/artifacts/project-state.json")
    materials = [{"path": path, "sha256": sha(LAB / path)} for path in state["payload"]["artifact_refs"]]
    state_ok = state["node_id"] == transition["successor_state_ref"] and state["payload"]["cursor"] == "decision:0073" and state["payload"]["artifact_refs"][: len(old_state["payload"]["artifact_refs"])] == old_state["payload"]["artifact_refs"] and state["payload"]["state_digest"] == "sha256:" + digest(materials)
    check("project-state-successor", state_ok, {"node_id": state["node_id"], "cursor": state["payload"]["cursor"], "state_digest": state["payload"]["state_digest"]})

    old_semantic = load(CURRENT / "instances/artifacts/project-semantic-event-history.json")
    semantic = load(ROOT / "instances/artifacts/project-semantic-event-history.json")
    se = semantic["payload"]["events"][-1]
    semantic_ok = semantic["payload"]["events"][:-1] == old_semantic["payload"]["events"] and se["cursor"] == 3 and se["previous_event_digest"] == old_semantic["payload"]["events"][-1]["event_digest"] and se["event_digest"] == digest({key: value for key, value in se.items() if key != "event_digest"}) and semantic["payload"]["chain_digest"] == digest([event["event_digest"] for event in semantic["payload"]["events"]]) and se["resulting_state_digest"] == state["payload"]["state_digest"]
    check("semantic-event-chain", semantic_ok, {"event_id": se["event_id"], "event_digest": se["event_digest"], "chain_digest": semantic["payload"]["chain_digest"]})

    old_governance = load(CURRENT / "instances/artifacts/project-governance-event-history.json")
    governance = load(ROOT / "instances/artifacts/project-governance-event-history.json")
    ge = governance["payload"]["events"][-1]
    governance_ok = governance["payload"]["events"][:-1] == old_governance["payload"]["events"] and ge["governance_cursor"] == 3 and ge["previous_event_digest"] == old_governance["payload"]["events"][-1]["event_digest"] and ge["event_digest"] == digest({key: value for key, value in ge.items() if key != "event_digest"}) and governance["payload"]["chain_digest"] == digest([event["event_digest"] for event in governance["payload"]["events"]]) and ge["semantic_event_ref"]["semantic_event_digest"] == se["event_digest"] and ge["authorization_sha256"] == sha(DECISION_DIR / "authorization.json")
    check("governance-event-chain", governance_ok, {"event_id": ge["event_id"], "event_digest": ge["event_digest"], "chain_digest": governance["payload"]["chain_digest"]})

    scope_ok = transition["counts"] == {"artifact_instances": 3, "typed_relation_instances": 2, "runtime_activations": 0} and transition["events_appended"]["semantic"] == 1 and transition["events_appended"]["governance"] == 1 and "CAL-DECISION-0074" not in state["payload"]["decision_refs"] and transition["authority_effect"] == "none"
    check("scope-authority-and-self-exclusion", scope_ok, {"counts": transition["counts"], "events_appended": transition["events_appended"], "decision_refs": state["payload"]["decision_refs"]})
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-project-state-successor-validation/v1", "result": result, "authority_effect": "none", "checks": checks, "materials": {"transition_sha256": sha(transition_path)}, "claim_ceiling": transition["claim_ceiling"]}
    receipt_path = ROOT / "receipts/validation.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": result, "checks": len(checks), **receipt["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
