#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
SOURCE = HERE / "business-ontology.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipts/validation.json"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def evaluate(model, currentness=True):
    checks = []
    def add(i, ok, detail): checks.append({"check_id": i, "result": "PASS" if ok else "FAIL", "detail": detail})
    errors = sorted(e.message for e in Draft202012Validator(load(SCHEMA)).iter_errors(model))
    add("schema-valid", not errors, errors)
    failures = []
    if currentness:
        for ref in model.get("predecessors", []):
            path = LAB / ref["path"]
            actual = digest(path) if path.is_file() else None
            if actual != ref["sha256"]: failures.append({"path": ref["path"], "actual": actual})
    add("selected-predecessors-current", not failures, failures)
    ctx = model.get("context_contract", {})
    add("exact-v2-context-topology", ctx == {"governance_context_ref":"cal.context.governance/v2","ontology_lifecycle_context_ref":"cal.context.ontology-lifecycle/v2","context_map_ref":"cal.context-map.governance-ontology-lifecycle/v2","direction":"source-to-target","source_language_ref":"cal.language.governance/v2","target_language_ref":"cal.language.ontology-lifecycle/v2"}, ctx)
    bridge = model.get("bridge_contract", {})
    required = set(bridge.get("payload_required", []))
    add("payload-and-acl-complete", {"decision_id","decision_version","subject_ref","source_digest","authority_scope","outcome","effective_boundary","challenge_route","evidence_refs"} == required and "ExactSemanticEventReference" in bridge.get("acl_translation", ""), bridge)
    add("challenge-contract-present", set(bridge.get("challenge_contract", {})) == {"owner_route","resolution_gate","blocking_rule"}, bridge.get("challenge_contract"))
    joined = json.dumps(model, sort_keys=True).lower()
    add("canonical-event-source-only", "only replay source" in joined and "can never become a canonical event source" in joined, model.get("rules"))
    add("authority-boundary", "authority transfer" in joined and model.get("product_approval") == "not-requested" and model.get("authority_effect") == "none", {"approval": model.get("product_approval"), "authority": model.get("authority_effect")})
    node_ids = {n.get("id") for n in model.get("nodes", [])}
    add("relation-endpoints-closed", all(r.get("source") in node_ids and r.get("target") in node_ids for r in model.get("relations", [])), sorted(node_ids))
    return checks

def main():
    model = load(SOURCE)
    checks = evaluate(model)
    probes = []
    for probe_id, mutate, expected in [
        ("predecessor-drift", lambda x: x["predecessors"][0].update(sha256="0"*64), "selected-predecessors-current"),
        ("v1-map-substitution", lambda x: x["context_contract"].update(context_map_ref="cal.context-map.governance-ontology-lifecycle/v1"), "exact-v2-context-topology"),
        ("reverse-direction", lambda x: x["context_contract"].update(direction="target-to-source"), "exact-v2-context-topology"),
        ("missing-challenge-route", lambda x: x["bridge_contract"]["challenge_contract"].pop("owner_route"), "challenge-contract-present")]:
        hostile = copy.deepcopy(model); mutate(hostile)
        failed = {c["check_id"] for c in evaluate(hostile, probe_id == "predecessor-drift") if c["result"] == "FAIL"}
        probes.append({"probe_id": probe_id, "result": "PASS" if expected in failed else "FAIL", "detector": expected})
    passed = all(x["result"] == "PASS" for x in checks + probes)
    receipt = {"schema_version":"cal.d65-s3-business-ontology-validation/v2","stage_id":"D65-S3","result":"PASS" if passed else "FAIL","checks":checks,"hostile_probes":probes,"checks_passed":sum(x["result"]=="PASS" for x in checks),"checks_total":len(checks),"hostile_probes_passed":sum(x["result"]=="PASS" for x in probes),"hostile_probes_total":len(probes),"artifacts":{"candidate_path":str(SOURCE.relative_to(LAB)),"candidate_sha256":digest(SOURCE)},"stage_state":"TESTED_PROTOTYPE" if passed else "PROTOTYPE_TEST_FAILED","next_product_frontier":"D65-S4" if passed else "D65-S3","product_approval":"not-requested","authority_effect":"none","claim_ceiling":model["claim_ceiling"]}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("stage_id","result","checks_passed","checks_total","hostile_probes_passed","hostile_probes_total","next_product_frontier","product_approval","authority_effect")}, indent=2))
    return 0 if passed else 1

if __name__ == "__main__": raise SystemExit(main())
