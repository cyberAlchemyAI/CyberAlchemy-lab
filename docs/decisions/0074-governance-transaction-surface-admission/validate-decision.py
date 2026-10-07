#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
FINAL = LAB / "authority/admissions/governance-transaction-surface/v1"
CANDIDATE = LAB / "authority/artifact-types/candidates/0013-governance-transaction-surface"
D73 = LAB / "authority/project-state-transitions/candidates/0002-decision-0073-successor/instances/artifacts"
DECISIONS = [
    "CAL-DECISION-0074A-GOVERNANCE-CARRIER-ADMISSION",
    "CAL-DECISION-0074B-ADMISSION-TRANSACTION-DEFINITION-ADMISSION",
    "CAL-DECISION-0074C-GOVERNANCE-RELATION-SURFACE-ADMISSION",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


checks = []


def check(check_id: str, passed: bool, detail: object) -> None:
    checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})


bundle = load(FINAL / "bundle.json")
authorization = load(HERE / "authorization.json")
receipt = load(FINAL / "receipts/application.json")
transaction = load(FINAL / "instances/governance/admission-transaction.json")
state = load(FINAL / "instances/project-state.json")
semantic = load(FINAL / "instances/project-semantic-event-history.json")
governance = load(FINAL / "instances/project-governance-event-history.json")

check("exact-owner-authorization", authorization["authorized"] is True and authorization["verbatim_user_authorization"] == "amidted, and do next" and authorization["decision_refs"] == DECISIONS, authorization)
files = {item["path"]: item["sha256"] for item in bundle["files"]}
actual_files = {str(path.relative_to(FINAL)): sha(path) for path in FINAL.rglob("*") if path.is_file() and path.name != "bundle.json"}
check("bundle-file-closure", files == actual_files, {"declared": len(files), "actual": len(actual_files)})

output_results = []
for name, item in receipt["outputs"].items():
    path = LAB / item["path"]
    output_results.append({"name": name, "path": item["path"], "exists": path.is_file(), "digest_current": path.is_file() and sha(path) == item["sha256"]})
check("receipt-output-bindings", len(output_results) == 8 and all(item["exists"] and item["digest_current"] and not item["path"].startswith(".decision-") for item in output_results), output_results)

dreg = load(FINAL / "registries/definition-registry.json")
areg = load(FINAL / "registries/artifact-type-registry.json")
rreg = load(FINAL / "registries/relation-kind-registry.json")
endpoint = load(FINAL / "registries/endpoint-inventory.json")
check("registry-counts", (len(dreg["entries"]), len(dreg["current_lookup"]), areg["inventory"]["admitted_contract_count"], areg["inventory"]["admitted_current_count"], areg["inventory"]["admitted_historical_count"], rreg["count"], endpoint["counts"]["named_endpoint_kinds"], endpoint["counts"]["declared_endpoint_pairs"], endpoint["counts"]["wildcard_tokens"]) == (189, 183, 143, 121, 22, 41, 109, 550, 0), {"definitions": [len(dreg["entries"]), len(dreg["current_lookup"])], "artifact_types": areg["inventory"], "relation_kinds": rreg["count"], "endpoint_counts": endpoint["counts"]})
check("live-definition-projections", sha(LAB / "authority/definitions/registry.json") == sha(FINAL / "registries/definition-registry.json") and sha(LAB / "authority/definitions/DEFINITIONS-INDEX.md") == sha(FINAL / "registries/DEFINITIONS-INDEX.md"), {"registry": sha(LAB / "authority/definitions/registry.json"), "index": sha(LAB / "authority/definitions/DEFINITIONS-INDEX.md")})

target = load(CANDIDATE / "admission-target-set.json")
repair = load(CANDIDATE / "representation-closure-repair.json")
check("fourteen-target-closure", target["count"] == 14 and repair["reviewed_target_set_sha256"] == "9324030cacd0e1078129f8cbd3181a9af4b4046032bbd1d54413c97869c7f613" and repair["admission_target_set_sha256"] == sha(CANDIDATE / "admission-target-set.json") and repair["semantic_scope_changed"] is False, {"target_count": target["count"], "repair": repair})

decision_instances = list((FINAL / "instances/governance/decisions").glob("*.json"))
scope_instances = list((FINAL / "instances/governance/decision-scopes").glob("*.json"))
check("interaction-boundary", len(decision_instances) == len(scope_instances) == 3 and transaction["payload"]["application_state"] == "applied" and transaction["payload"]["atomicity"] == "all-or-nothing" and transaction["payload"]["runtime_activations"] == 0 and transaction["payload"]["external_effect_refs"] == [], {"decisions": len(decision_instances), "scopes": len(scope_instances), "transaction": transaction["payload"]["application_state"]})

consequences = {item["consequence_kind"]: item for item in transaction["payload"]["deterministic_consequences"]}
expected_consequence_paths = {"project-state": FINAL / "instances/project-state.json", "project-semantic-event-history": FINAL / "instances/project-semantic-event-history.json", "project-governance-event-history": FINAL / "instances/project-governance-event-history.json", "generated-output": FINAL / "instances/generated-output.json"}
check("transaction-output-bindings", set(consequences) == set(expected_consequence_paths) and all(consequences[kind]["output_sha256"] == sha(path) for kind, path in expected_consequence_paths.items()), consequences)

history_preservation = []
for name in ["project-state.json", "project-semantic-event-history.json", "project-governance-event-history.json"]:
    preserved = FINAL / "instances/project-history/decision-0073" / name
    history_preservation.append({"name": name, "exact": sha(D73 / name) == sha(preserved), "sha256": sha(preserved)})
check("D73-byte-exact-history", all(item["exact"] for item in history_preservation), history_preservation)

semantic_events = semantic["payload"]["events"]
governance_events = governance["payload"]["events"]
check("D74-project-state", state["payload"]["cursor"] == "decision:0074" and state["node_id"].endswith(":decision-0074") and all(item in state["payload"]["decision_refs"] for item in DECISIONS), {"cursor": state["payload"]["cursor"], "decision_refs": state["payload"]["decision_refs"][-3:]})
check("event-four-closure", semantic["payload"]["latest_cursor"] == governance["payload"]["latest_governance_cursor"] == 4 and semantic_events[-1]["cursor"] == governance_events[-1]["governance_cursor"] == 4 and semantic["payload"]["chain_digest"] == digest([item["event_digest"] for item in semantic_events]) and governance["payload"]["chain_digest"] == digest([item["event_digest"] for item in governance_events]), {"semantic": semantic["payload"]["chain_digest"], "governance": governance["payload"]["chain_digest"]})

typed_schema = load(CANDIDATE / "impacted-carrier-successors/typed-relation/v3/schema.json")
typed_results = []
for path in sorted((FINAL / "instances/typed-relations").glob("*.json")):
    errors = [error.message for error in jsonschema.Draft202012Validator(typed_schema).iter_errors(load(path))]
    typed_results.append({"path": str(path.relative_to(FINAL)), "result": "PASS" if not errors else "BLOCK", "errors": errors})
check("four-materializes-relations", len(typed_results) == 4 and all(item["result"] == "PASS" for item in typed_results), typed_results)

check("self-contained-no-D75", receipt["no_followup_bookkeeping_decision_required"] is True and load(HERE / "decision.json")["next_successor_obligation"] is None and bundle["current_project_state_ref"].endswith(":decision-0074"), {"receipt": receipt["no_followup_bookkeeping_decision_required"], "state": bundle["current_project_state_ref"]})
check("zero-runtime-external-effects", receipt["counts"]["runtime_activations"] == receipt["counts"]["external_effects"] == bundle["runtime_activations"] == 0 and bundle["external_effect_refs"] == [], receipt["counts"])

result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
validation = {"schema_version": "cyberalchemy-lab-decision-0074-validation/v1", "decision_checkpoint_ref": bundle["decision_checkpoint_ref"], "result": result, "checks": checks, "materials": {"bundle_sha256": sha(FINAL / "bundle.json"), "transaction_sha256": sha(FINAL / "instances/governance/admission-transaction.json"), "project_state_sha256": sha(FINAL / "instances/project-state.json"), "semantic_history_sha256": sha(FINAL / "instances/project-semantic-event-history.json"), "governance_history_sha256": sha(FINAL / "instances/project-governance-event-history.json")}, "claim_ceiling": "PASS proves the exact repository admission postimage, output bindings, state/event closure, and zero runtime or external effects."}
(HERE / "receipts").mkdir(exist_ok=True)
(HERE / "receipts/decision-validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"result": result, "checks": len(checks), **validation["materials"]}, sort_keys=True))
raise SystemExit(0 if result == "PASS" else 1)
