#!/usr/bin/env python3
"""Validate the first governed Agent work episode candidate."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
RECEIPT = ROOT / "receipts" / "validation.json"
MODEL = LAB / "authority/admissions/project-state-bootstrap/v1"
FOUNDATION = LAB / "authority/admissions/cyberalchemy-lab-operational-foundation/v1"
RELATION_REGISTRY = LAB / "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def schema_errors(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    return [f"{'/'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in sorted(jsonschema.Draft202012Validator(schema).iter_errors(record), key=lambda x: list(x.absolute_path))]


def snapshot() -> dict[str, str]:
    paths = [ROOT / "candidate.json", ROOT / "EPISODE.md", ROOT / "REVIEW.md"]
    paths += sorted(path for path in (ROOT / "instances").rglob("*.json"))
    return {str(path.relative_to(ROOT)): sha(path) for path in paths}


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    before = snapshot()
    run = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=LAB, text=True, capture_output=True, check=False)
    after = snapshot()
    check("deterministic-build", run.returncode == 0 and before == after, {"returncode": run.returncode, "stdout": run.stdout.strip(), "stderr": run.stderr.strip(), "changed": sorted(set(before) | set(after)) if before != after else []})

    candidate = load(ROOT / "candidate.json")
    input_results = [{"name": name, "current": sha(LAB / binding["path"]) == binding["sha256"]} for name, binding in candidate["inputs"].items()]
    check("inputs-current", all(x["current"] for x in input_results), input_results)

    registry = load(MODEL / "registries/artifact-type-registry.json")
    contracts = {x["artifact_type_ref"]: x for x in registry["admitted_contracts"] if x["lifecycle_state"] == "admitted-current"}
    artifacts: dict[str, dict[str, Any]] = {}
    artifact_results = []
    for entry in candidate["artifact_instances"]:
        path = LAB / entry["path"]
        record = load(path)
        contract = contracts.get(entry["carrier_type_ref"])
        errors = ["carrier is not admitted-current"] if contract is None else schema_errors(record, load(LAB / contract["schema_path"]))
        identity = record.get("node_id")
        if identity != entry["identity_ref"]:
            errors.append("identity mismatch")
        if sha(path) != entry["sha256"]:
            errors.append("digest mismatch")
        if record.get("authority_effect") != "none":
            errors.append("authority effect is not none")
        artifacts[identity] = record
        artifact_results.append({"identity": identity, "kind": entry["semantic_kind"], "errors": errors})
    check("artifact-schemas-and-digests", len(artifacts) == len(candidate["artifact_instances"]) and all(not x["errors"] for x in artifact_results), artifact_results)

    external: dict[str, str] = {}
    for base in [FOUNDATION / "instances/artifacts", MODEL / "instances/artifacts"]:
        for path in base.glob("*.json"):
            value = load(path)
            identity = value.get("node_id") or value.get("project_id") or value.get("product_id") or value.get("goal_id")
            inferred_kind = value.get("kind") or ("project" if value.get("project_id") else "product" if value.get("product_id") else "goal" if value.get("goal_id") else "")
            if identity:
                external[identity] = inferred_kind
    endpoints = {**external, **{ref: record.get("kind", "") for ref, record in artifacts.items()}}
    typed_schema = load(LAB / contracts["cal.artifact-type.typed-relation/v2"]["schema_path"])
    relation_registry = load(RELATION_REGISTRY)
    relation_results = []
    relation_ids = set()
    for entry in candidate["typed_relations"]:
        path = LAB / entry["path"]
        record = load(path)
        payload = record["payload"]
        kind_entry = next((x for x in relation_registry["entries"] if x["relation_kind_id"] == payload["relation_kind_ref"] and x["lifecycle_state"] == "admitted-current"), None)
        errors = schema_errors(record, typed_schema)
        if sha(path) != entry["sha256"]:
            errors.append("digest mismatch")
        if kind_entry is None:
            errors.append("relation kind is not admitted-current")
        else:
            kind = load(LAB / kind_entry["instance_path"])
            pair = {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]}
            if pair not in kind["payload"]["allowed_endpoint_pairs"]:
                errors.append(f"endpoint pair is not admitted: {pair}")
            if set(payload["qualifiers"]) != set(kind["payload"]["qualifier_contract"]["required_axes"]):
                errors.append("qualifier axes are not exact")
        for side in ("source", "target"):
            endpoint = payload[side]
            if endpoints.get(endpoint["ref"]) != endpoint["kind"]:
                errors.append(f"{side} endpoint does not close with exact kind")
        relation_ids.add(record["node_id"])
        relation_results.append({"relation": record["node_id"], "errors": errors})
    check("typed-relations-close-exactly", len(relation_ids) == len(candidate["typed_relations"]) and all(not x["errors"] for x in relation_results), relation_results)

    state = artifacts["project-state:cyberalchemy-v2-to-lab-migration:decision-0072"]
    old_state = load(MODEL / "instances/artifacts/project-state.json")
    semantic = artifacts["project-semantic-event-history:cyberalchemy-v2-to-lab-migration"]
    governance = artifacts["project-governance-event-history:cyberalchemy-v2-to-lab-migration"]
    sem_events = semantic["payload"]["events"]
    gov_events = governance["payload"]["events"]
    sem2 = sem_events[-1]
    gov2 = gov_events[-1]
    materials = [{"path": path, "sha256": sha(LAB / path)} for path in state["payload"]["artifact_refs"]]
    state_ok = (
        state["payload"]["state_digest"] == "sha256:" + digest(materials)
        and sem2["predecessor_state_digest"] == old_state["payload"]["state_digest"]
        and sem2["resulting_state_digest"] == state["payload"]["state_digest"]
        and sem2["event_digest"] == digest({k: v for k, v in sem2.items() if k != "event_digest"})
        and semantic["payload"]["chain_digest"] == digest([x["event_digest"] for x in sem_events])
        and gov2["event_digest"] == digest({k: v for k, v in gov2.items() if k != "event_digest"})
        and governance["payload"]["chain_digest"] == digest([x["event_digest"] for x in gov_events])
        and gov2["semantic_event_ref"] == {"semantic_event_id": sem2["event_id"], "semantic_event_digest": sem2["event_digest"], "semantic_cursor": 2}
    )
    check("project-state-and-event-chain", state_ok, {"state": state["node_id"], "state_digest": state["payload"]["state_digest"], "semantic_cursor": semantic["payload"]["latest_cursor"], "governance_cursor": governance["payload"]["latest_governance_cursor"]})

    context_view = artifacts["context-view:first-governed-agent-episode:2026-10-06"]
    included_ok = all((LAB / item["source_ref"]).is_file() and sha(LAB / item["source_ref"]) == item["sha256"] for item in context_view["included_material"])
    session = artifacts["agent-session:first-governed-agent-episode:2026-10-06"]
    agent = artifacts["agent-instance:first-governed-agent-episode:2026-10-06"]
    memory_ok = (
        candidate["memory_contract"]["machine_agent_ephemeral"] is True
        and candidate["memory_contract"]["session_memory_expires"] is True
        and candidate["memory_contract"]["standalone_agent_memory_artifact"] is False
        and session["payload"]["session_memory"]["expires_with_session"] is True
        and agent["payload"]["terminated_at"] == "when-owner-review-boundary-closes"
        and state["node_id"] in candidate["memory_contract"]["durable_memory_refs"]
        and context_view["node_id"] in candidate["memory_contract"]["durable_memory_refs"]
        and included_ok
        and not any(x["semantic_kind"] == "session-memory" for x in candidate["artifact_instances"])
    )
    check("agent-memory-boundary-and-context-digests", memory_ok, {"durable_refs": candidate["memory_contract"]["durable_memory_refs"], "context_digests_current": included_ok, "termination": agent["payload"]["terminated_at"]})

    ontology = artifacts["ontology:cyberalchemy-lab-operational-context"]
    cut = artifacts["ontology-cut:cyberalchemy-lab-operational-context:decision-0072"]
    view = artifacts["ontology-view:first-governed-agent-episode:2026-10-06"]
    state_node = artifacts["ontology-node:first-agent-episode:project-state-decision-0072"]
    project_node = artifacts["ontology-node:first-agent-episode:project"]
    edge = artifacts["ontology-edge:first-agent-episode:state-member-of-project"]
    state_relation_entry = next(x for x in candidate["typed_relations"] if x["relation_id"] == "typed-relation:first-agent-episode:state-project")
    projection_ok = (
        ontology["node_refs"] == [state_node["node_id"], project_node["node_id"]]
        and ontology["relation_refs"] == [edge["node_id"]]
        and cut["payload"]["node_refs"] == view["payload"]["selected_node_refs"] == [state_node["node_id"], project_node["node_id"]]
        and cut["payload"]["edge_refs"] == view["payload"]["selected_edge_refs"] == [edge["node_id"]]
        and view["payload"]["cut_digest"] == cut["payload"]["calculated_digest"]
        and cut["payload"]["replay_source"] is False
        and view["payload"]["replay_source"] is False
        and state_node["payload"]["represented_subject"]["digest"] == sha(ROOT / "instances/artifacts/project-state.json")
        and project_node["payload"]["represented_subject"]["digest"] == sha(FOUNDATION / "instances/artifacts/project.json")
        and edge["payload"]["global_typed_relation_binding"]["typed_relation_digest"] == state_relation_entry["sha256"]
        and edge["payload"]["local_interpretation"] is None
    )
    check("minimal-ontology-projection-boundary", projection_ok, {"ontology": ontology["node_id"], "nodes": len(view["payload"]["selected_node_refs"]), "edges": len(view["payload"]["selected_edge_refs"]), "replay_source": view["payload"]["replay_source"]})

    critical_refs = {
        "assignment.work": artifacts["agent-assignment:first-governed-agent-episode"]["payload"]["work_ref"],
        "assignment.agent": artifacts["agent-assignment:first-governed-agent-episode"]["payload"]["eligible_agent_ref"],
        "agent.profile": agent["payload"]["profile_ref"],
        "agent.capability": agent["payload"]["capability_refs"][0],
        "agent.classification": agent["payload"]["agent_classification_assignment_ref"],
        "agent.principal": agent["payload"]["accountable_principal_ref"],
        "agent.session": agent["payload"]["session_ref"],
        "session.context": session["payload"]["context_view_ref"],
        "session.ontology": session["payload"]["ontology_view_ref"],
    }
    check("critical-payload-reference-closure", all(ref in artifacts for ref in critical_refs.values()), critical_refs)

    expected_counts = {"artifact_instances": 22, "typed_relation_instances": 23, "semantic_events_appended": 1, "governance_events_appended": 1, "runtime_activations": 0}
    boundary_ok = candidate["counts"] == expected_counts and candidate["status"] == "candidate-awaiting-owner-review" and candidate["authority_effect"] == "none" and candidate["optimization"]["context_lineage_record_excluded"].startswith("The admitted Context Lineage Record/v2")
    check("scope-authority-and-optimization-boundary", boundary_ok, {"counts": candidate["counts"], "status": candidate["status"], "authority_effect": candidate["authority_effect"], "context_lineage": candidate["optimization"]["context_lineage_record_excluded"]})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-agent-work-episode-validation/v1", "result": result, "authority_effect": "none", "checks": checks, "materials": {"candidate_sha256": sha(ROOT / "candidate.json")}, "claim_ceiling": "PASS proves the deterministic candidate, admitted schema use, exact Typed Relation closure, Project State transition, ephemeral Agent memory boundary, and minimal exact ontology projection. It admits nothing and activates no runtime."}
    dump(RECEIPT, receipt)
    print(json.dumps({"result": result, "checks": len(checks), "candidate_sha256": receipt["materials"]["candidate_sha256"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
