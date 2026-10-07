#!/usr/bin/env python3
"""Validate the Decision 0071 Project State bootstrap candidate."""

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
RECEIPT = ROOT / "receipts/validation.json"
SEMANTIC_TYPE = LAB / "authority/artifact-types/project-semantic-event-history/v1"
GOVERNANCE_TYPE = LAB / "authority/artifact-types/project-governance-event-history/v1"
FOUNDATION = LAB / "authority/admissions/cyberalchemy-lab-operational-foundation/v1"
MODEL = LAB / "authority/admissions/definition-complete-lab-model/v1"


def load(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding="utf-8"))
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(value: Any) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def errors(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    return [f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}" for error in sorted(jsonschema.Draft202012Validator(schema).iter_errors(record), key=lambda item: list(item.absolute_path))]


def snapshot() -> dict[str, str]:
    paths = [ROOT / "transition.json", ROOT / "TRANSITION.md", ROOT / "definition-registry-postimage.json", ROOT / "DEFINITIONS-INDEX-postimage.md", ROOT / "artifact-type-registry-postimage.json"]
    for base in [ROOT / "instances", LAB / "authority/definitions/candidates/0015-project-state-event-histories", SEMANTIC_TYPE, GOVERNANCE_TYPE]:
        paths.extend(sorted(path for path in base.rglob("*") if path.is_file() and "receipts" not in path.parts))
    return {str(path.relative_to(LAB)): sha(path) for path in paths}


def main() -> int:
    checks: list[dict[str, Any]] = []
    def check(check_id: str, ok: bool, detail: Any) -> None: checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    before = snapshot()
    run = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=LAB, text=True, capture_output=True, check=False)
    after = snapshot()
    check("deterministic-build", run.returncode == 0 and before == after, {"returncode": run.returncode, "stdout": run.stdout.strip(), "stderr": run.stderr.strip(), "changed": sorted(set(before) | set(after)) if before != after else []})

    manifest = load(ROOT / "transition.json")
    input_results = [{"name": name, "match": sha(LAB / binding["path"]) == binding["sha256"]} for name, binding in manifest["inputs"].items()]
    check("inputs-current", all(item["match"] for item in input_results), input_results)

    definition_schema = load(LAB / "authority/artifact-types/definition/v1/schema.json")
    definition_results = []
    for item in manifest["definitions"]:
        record = load(LAB / item["path"])
        definition_results.append({"ref": item["ref"], "digest_current": sha(LAB / item["path"]) == item["sha256"], "errors": errors(record, definition_schema)})
    dpost = load(ROOT / "definition-registry-postimage.json")
    new_lookup = {item["definition_id"]: dpost["current_lookup"].get(item["definition_id"]) for item in manifest["definitions"]}
    check("definition-contracts-and-registry", all(item["digest_current"] and not item["errors"] for item in definition_results) and all(new_lookup[item["definition_id"]] == item["ref"] for item in manifest["definitions"]) and len(dpost["entries"]) == 188 and len(dpost["current_lookup"]) == 182, {"definitions": definition_results, "lookup": new_lookup, "entries": len(dpost["entries"]), "current": len(dpost["current_lookup"])})

    type_results = []
    apost = load(ROOT / "artifact-type-registry-postimage.json")
    for item in manifest["artifact_types"]:
        root = (LAB / item["artifact_path"]).parent
        descriptor = load(root / "artifact.json"); schema = load(root / "schema.json"); fixture = load(root / "fixtures/valid/record.json")
        invalid = [errors(load(root / relative), schema) for relative in descriptor["validation_contract"]["negative_witnesses"]]
        contract = next((entry for entry in apost["admitted_contracts"] if entry["artifact_type_ref"] == item["artifact_type_ref"] and entry["lifecycle_state"] == "admitted-current"), None)
        type_results.append({"type_ref": item["artifact_type_ref"], "descriptor_current": sha(root / "artifact.json") == item["artifact_sha256"], "schema_current": sha(root / "schema.json") == item["schema_sha256"] == descriptor["schema_digest"], "fixture_errors": errors(fixture, schema), "hostile_rejected": all(bool(value) for value in invalid), "definition_ref": descriptor["semantic_definition_refs"][0], "registry_contract": contract is not None, "no_relation_surface": descriptor["allowed_relation_kinds"] == descriptor["relation_roles"] == []})
    check("artifact-type-contracts-and-registry", all(all([item["descriptor_current"], item["schema_current"], not item["fixture_errors"], item["hostile_rejected"], item["registry_contract"], item["no_relation_surface"]]) for item in type_results) and apost["inventory"]["admitted_contract_count"] == 129 and apost["inventory"]["admitted_current_count"] == 115, type_results)

    artifacts = {item["semantic_kind"]: load(LAB / item["path"]) for item in manifest["artifact_instances"]}
    semantic = artifacts["project-semantic-event-history"]; governance = artifacts["project-governance-event-history"]; state = artifacts["project-state"]
    sem_event = semantic["payload"]["events"][0]; sem_core = {k: v for k, v in sem_event.items() if k != "event_digest"}
    gov_event = governance["payload"]["events"][0]; gov_core = {k: v for k, v in gov_event.items() if k != "event_digest"}
    event_ok = sem_event["event_digest"] == digest(sem_core) and semantic["payload"]["chain_digest"] == digest([sem_event["event_digest"]]) and gov_event["event_digest"] == digest(gov_core) and governance["payload"]["chain_digest"] == digest([gov_event["event_digest"]]) and gov_event["semantic_event_ref"] == {"semantic_event_id": sem_event["event_id"], "semantic_event_digest": sem_event["event_digest"], "semantic_cursor": sem_event["cursor"]}
    check("separate-event-chain-integrity", event_ok, manifest["integrity"])

    sem_errors = errors(semantic, load(SEMANTIC_TYPE / "schema.json")); gov_errors = errors(governance, load(GOVERNANCE_TYPE / "schema.json")); state_errors = errors(state, load(LAB / "authority/artifact-types/project-state/v1/schema.json"))
    check("instance-schemas", not sem_errors and not gov_errors and not state_errors, {"semantic": sem_errors, "governance": gov_errors, "state": state_errors})

    materials = [{"path": path, "sha256": sha(LAB / path)} for path in state["payload"]["artifact_refs"]]
    expected_state = f"sha256:{digest(materials)}"
    old = load(FOUNDATION / "instances/artifacts/project-state.json")
    state_ok = state["payload"]["cursor"] == "decision:0071" and state["payload"]["state_digest"] == expected_state == sem_event["resulting_state_digest"] and sem_event["predecessor_state_digest"] == old["payload"]["state_digest"] and state["payload"]["semantic_history_ref"] == semantic["node_id"] and state["payload"]["governance_history_ref"] == governance["node_id"] and "CAL-DECISION-0072-PROJECT-STATE-BOOTSTRAP-ADMISSION" not in state["payload"]["decision_refs"]
    check("successor-state-snapshot", state_ok, {"expected": expected_state, "declared": state["payload"]["state_digest"], "cursor": state["payload"]["cursor"], "decisions": state["payload"]["decision_refs"]})

    typed_schema = load(LAB / "authority/artifact-types/typed-relation/v2/schema.json")
    relation_registry = load(MODEL / "relation-kind-registry.json")
    relation_results = []
    for item in manifest["typed_relations"]:
        record = load(LAB / item["path"]); payload = record["payload"]; kind_entry = next(entry for entry in relation_registry["entries"] if entry["relation_kind_id"] == payload["relation_kind_ref"]); kind = load(LAB / kind_entry["instance_path"]); pair = {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]}
        relation_results.append({"id": record["node_id"], "schema_errors": errors(record, typed_schema), "pair_allowed": pair in kind["payload"]["allowed_endpoint_pairs"], "qualifiers_exact": set(payload["qualifiers"]) == set(kind["payload"]["qualifier_contract"]["required_axes"]), "digest_current": sha(LAB / item["path"]) == item["sha256"]})
    check("typed-relations", len(relation_results) == 2 and all(not item["schema_errors"] and item["pair_allowed"] and item["qualifiers_exact"] and item["digest_current"] for item in relation_results), relation_results)

    exact_counts = {"definitions": 2, "artifact_types": 2, "artifact_instances": 3, "typed_relation_instances": 2, "semantic_events": 1, "governance_events": 1, "runtime_activations": 0}
    boundary_ok = manifest["counts"] == exact_counts and manifest["authority_effect"] == "none" and manifest["status"] == "candidate-awaiting-admission" and not ({"agent-instance", "agent-session", "context-view", "evidence-set", "ontology-node", "ontology-edge", "ontology-cut", "ontology-view"} & {item["semantic_kind"] for item in manifest["artifact_instances"]})
    check("scope-and-authority-boundary", boundary_ok, {"counts": manifest["counts"], "authority_effect": manifest["authority_effect"], "kinds": [item["semantic_kind"] for item in manifest["artifact_instances"]]})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-project-state-bootstrap-validation/v1", "result": result, "authority_effect": "none", "checks": checks, "materials": {"transition_sha256": sha(ROOT / "transition.json"), "definition_registry_postimage_sha256": sha(ROOT / "definition-registry-postimage.json"), "artifact_type_registry_postimage_sha256": sha(ROOT / "artifact-type-registry-postimage.json")}, "claim_ceiling": "PASS proves the exact Definition, Artifact Type, event-chain, Project State, Typed Relation, and registry postimages. It does not apply Decision 0072."}
    dump(RECEIPT, receipt)
    print(json.dumps({"result": result, "checks": len(checks), **receipt["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__": raise SystemExit(main())
