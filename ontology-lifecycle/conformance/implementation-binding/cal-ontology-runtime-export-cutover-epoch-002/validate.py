#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent; LAB=HERE.parents[3]; SOURCE=HERE/"binding.json"; SCHEMA=HERE/"schema.json"; RECEIPT=HERE/"receipts/validation.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def evaluate(b,current=True):
    checks=[]
    def add(i,ok,d): checks.append({"check_id":i,"result":"PASS" if ok else "FAIL","detail":d})
    errors=sorted(e.message for e in Draft202012Validator(load(SCHEMA)).iter_errors(b)); add("schema-valid",not errors,errors)
    drift=[]
    if current:
        for ref in b.get("compiled_predecessors",[])+b.get("protected_admitted_runtime",[]):
            p=LAB/ref["path"]; actual=digest(p) if p.is_file() else None
            if actual!=ref["sha256"]: drift.append({"path":ref["path"],"actual":actual})
    add("selected-byte-currentness",not drift,drift)
    crate=b.get("candidate_crate",{}); add("isolated-versioned-target",crate.get("root")=="ontology-lifecycle/runtime-candidates/cal-ontology-context-adapters-v2/v1" and crate.get("files")==["Cargo.toml","Cargo.lock","src/lib.rs","tests/public_contract.rs"] and crate.get("dependency",{}).get("path")=="../../../runtime",crate)
    symbols={(x.get("module"),x.get("symbol"),x.get("kind")) for x in b.get("symbol_bindings",[])}; required={("crate","V2_CONTEXT_MAP","public-constant"),("governance_v2","GovernanceContextAdapterV2","public-struct"),("governance_v2","project_governance_context_v2","public-function"),("ontology_lifecycle_v2","OntologyLifecycleContextAdapterV2","public-struct"),("ontology_lifecycle_v2","project_ontology_lifecycle_context_v2","public-function")}; add("public-symbol-closure",symbols==required,sorted(symbols))
    tests={x.get("test") for x in b.get("behavior_bindings",[])}; add("behavior-test-closure",tests=={"exact_v2_topology_is_public_and_enforced","both_contexts_share_the_exact_event_cut","projection_is_not_a_replay_source","projection_has_no_authority_effect"},sorted(tests))
    joined=json.dumps(b.get("implementation_constraints",[])).lower(); add("source-and-authority-boundaries","do not edit ontology-lifecycle/runtime" in joined and "admitted runtime public api" in joined and b.get("implementation_authorized") is False and b.get("product_approval")=="not-requested" and b.get("authority_effect")=="none",b.get("implementation_constraints"))
    return checks
def main():
    b=load(SOURCE); checks=evaluate(b); probes=[]
    cases=[("compiled-drift",lambda x:x["compiled_predecessors"][0].update(sha256="0"*64),"selected-byte-currentness",True),("target-inside-admitted-runtime",lambda x:x["candidate_crate"].update(root="ontology-lifecycle/runtime"),"isolated-versioned-target",False),("private-module",lambda x:x["symbol_bindings"].pop(),"public-symbol-closure",False)]
    for pid,mut,det,current in cases:
        h=copy.deepcopy(b); mut(h); failed={x["check_id"] for x in evaluate(h,current) if x["result"]=="FAIL"}; probes.append({"probe_id":pid,"result":"PASS" if det in failed else "FAIL","detector":det})
    passed=all(x["result"]=="PASS" for x in checks+probes)
    receipt={"schema_version":"cal.d65-s6-binding-validation/v2","stage_id":"D65-S6","result":"PASS" if passed else "FAIL","checks":checks,"hostile_probes":probes,"checks_passed":sum(x["result"]=="PASS" for x in checks),"checks_total":len(checks),"hostile_probes_passed":sum(x["result"]=="PASS" for x in probes),"hostile_probes_total":len(probes),"artifacts":{"binding_path":str(SOURCE.relative_to(LAB)),"binding_sha256":digest(SOURCE)},"stage_state":"TESTED_PROTOTYPE" if passed else "PROTOTYPE_TEST_FAILED","next_product_frontier":"D65-S7" if passed else "D65-S6","product_approval":"not-requested","implementation_authorized":False,"authority_effect":"none","claim_ceiling":b["claim_ceiling"]}
    RECEIPT.parent.mkdir(parents=True,exist_ok=True); RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("stage_id","result","checks_passed","checks_total","hostile_probes_passed","hostile_probes_total","next_product_frontier","product_approval","implementation_authorized","authority_effect")},indent=2)); return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main())
