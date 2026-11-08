#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent; LAB=HERE.parents[2]; SOURCE=HERE/"authored-source.json"; SCHEMA=HERE/"schema.json"; RECEIPT=HERE/"receipts/validation.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def evaluate(m, current=True):
    out=[]
    def add(i,ok,d): out.append({"check_id":i,"result":"PASS" if ok else "FAIL","detail":d})
    errors=sorted(e.message for e in Draft202012Validator(load(SCHEMA)).iter_errors(m)); add("schema-valid",not errors,errors)
    drift=[]
    if current:
        for r in m.get("predecessors",[]):
            p=LAB/r["path"]; actual=digest(p) if p.is_file() else None
            if actual!=r["sha256"]: drift.append({"path":r["path"],"actual":actual})
    add("business-predecessor-current",not drift,drift)
    contexts={x.get("ref") for x in m.get("contexts",[])}; cmap=m.get("context_map",{})
    add("exact-v2-context-source",contexts=={"cal.context.governance/v2","cal.context.ontology-lifecycle/v2"} and cmap.get("ref")=="cal.context-map.governance-ontology-lifecycle/v2" and cmap.get("direction")=="source-to-target",{"contexts":sorted(contexts),"map":cmap})
    aggs=m.get("aggregates",[]); add("per-node-and-relation-event-streams",{x.get("aggregate_id") for x in aggs}=={"OntologyNode","OntologyRelation"} and all(x.get("semantic_stream") and x.get("governance_stream") for x in aggs),aggs)
    event_types={x.get("event_type") for x in m.get("events",[])}; add("canonical-event-model-complete",len(event_types)==5 and all(x.get("canonical") is True for x in m.get("events",[])),sorted(event_types))
    projections=m.get("projections",[]); add("latest-snapshot-and-context-projections",{x.get("projection_id") for x in projections}=={"LatestNodeSnapshot","LatestRelationSnapshot","GovernedContextProjectionV2"} and all(x.get("canonical_replay_source") is False for x in projections),projections)
    invariants={x.get("invariant_id") for x in m.get("invariants",[])}; add("invariant-closure",invariants=={"INV-CANONICAL-EVENTS-ONLY","INV-EXACT-GOVERNANCE-JOIN","INV-V2-TOPOLOGY","INV-NO-AUTHORITY-TRANSFER","INV-DERIVATIVES-NONCANONICAL"},sorted(invariants))
    required_failures={"CONTEXT_ID_MISMATCH","CONTEXT_VERSION_MISMATCH","CONTEXT_MAP_MISMATCH","CONTEXT_DIRECTION_MISMATCH","EVENT_CUT_GAP","EXACT_GOVERNANCE_STATE_MISSING","GOVERNANCE_REFERENCE_MISMATCH","NONCANONICAL_REPLAY_SOURCE"}; add("typed-failure-closure",set(m.get("typed_failures",[]))==required_failures,sorted(m.get("typed_failures",[])))
    adapter=m.get("public_adapter_contract",{}); add("isolated-public-adapter-contract",adapter.get("crate")=="cal-ontology-context-adapters-v2" and set(adapter.get("modules",[]))=={"governance_v2","ontology_lifecycle_v2"} and adapter.get("admitted_runtime_mutation") is False,adapter)
    add("no-premature-approval",m.get("product_approval")=="not-requested" and m.get("authority_effect")=="none",[m.get("product_approval"),m.get("authority_effect")])
    return out
def main():
    m=load(SOURCE); checks=evaluate(m); probes=[]
    cases=[("business-drift",lambda x:x["predecessors"][0].update(sha256="0"*64),"business-predecessor-current",True),("mixed-v1-context",lambda x:x["contexts"][0].update(ref="cal.context.governance/v1"),"exact-v2-context-source",False),("projection-as-source",lambda x:x["projections"][0].update(canonical_replay_source=True),"latest-snapshot-and-context-projections",False),("missing-exact-join",lambda x:x["invariants"].pop(1),"invariant-closure",False)]
    for pid,mut,det,current in cases:
        h=copy.deepcopy(m); mut(h); failed={c["check_id"] for c in evaluate(h,current) if c["result"]=="FAIL"}; probes.append({"probe_id":pid,"result":"PASS" if det in failed else "FAIL","detector":det})
    passed=all(x["result"]=="PASS" for x in checks+probes)
    receipt={"schema_version":"cal.d65-s4-domainspec-source-validation/v2","stage_id":"D65-S4","result":"PASS" if passed else "FAIL","checks":checks,"hostile_probes":probes,"checks_passed":sum(x["result"]=="PASS" for x in checks),"checks_total":len(checks),"hostile_probes_passed":sum(x["result"]=="PASS" for x in probes),"hostile_probes_total":len(probes),"artifacts":{"candidate_path":str(SOURCE.relative_to(LAB)),"candidate_sha256":digest(SOURCE)},"stage_state":"TESTED_PROTOTYPE" if passed else "PROTOTYPE_TEST_FAILED","next_product_frontier":"D65-S5" if passed else "D65-S4","product_approval":"not-requested","authority_effect":"none","claim_ceiling":m["claim_ceiling"]}
    RECEIPT.parent.mkdir(parents=True,exist_ok=True); RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("stage_id","result","checks_passed","checks_total","hostile_probes_passed","hostile_probes_total","next_product_frontier","product_approval","authority_effect")},indent=2)); return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main())
