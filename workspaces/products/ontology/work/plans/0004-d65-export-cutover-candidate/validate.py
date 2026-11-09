#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent; LAB=HERE.parents[2]; PLAN=HERE/"plan.json"; SCHEMA=HERE/"schema.json"; RECEIPT=HERE/"receipts/validation.json"
EXPECTED_STAGES=["PLAN-S0","CTXMAP2-S1","D65-S1","D65-S2","D65-S3","D65-S4","D65-S5","D65-S6","D65-S7","D65-S8","CUTOVER-R1","CUTOVER-G1"]
def load(p):
    v=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v,dict): raise ValueError(f"object required: {p}")
    return v
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--write-receipt",action="store_true"); args=parser.parse_args(); plan=load(PLAN); checks=[]
    def add(i,ok,d): checks.append({"check_id":i,"result":"PASS" if ok else "BLOCK","detail":d})
    errors=sorted(e.message for e in Draft202012Validator(load(SCHEMA)).iter_errors(plan)); add("plan-schema",not errors,errors)
    drift=[]
    for ref in plan.get("selected_sources",[]):
        p=LAB/ref.get("path",""); actual=digest(p) if p.is_file() else None
        if actual!=ref.get("sha256"): drift.append({"path":ref.get("path"),"actual":actual})
    add("selected-source-currentness",not drift,drift)
    admission=load(LAB/plan["source_epoch"]["admission_decision_path"]); old_manifest=load(LAB/plan["source_epoch"]["manifest_path"]); old_verdict=load(LAB/plan["source_epoch"]["verdict_path"])
    add("admitted-epoch-001-predecessor",admission.get("status")=="selected" and admission.get("cutover",{}).get("authorized") is False and admission.get("cutover",{}).get("performed") is False and old_manifest.get("epoch_id")==plan["source_epoch"]["admitted_epoch_id"] and old_verdict.get("result")=="PASS",{"epoch":old_manifest.get("epoch_id"),"cutover":admission.get("cutover")})
    stages=plan.get("stages",[]); ids=[x.get("stage_id") for x in stages]; states={x.get("stage_id"):x.get("state") for x in stages}; expected_states={"PLAN-S0":"PASS","CTXMAP2-S1":"TESTED_PROTOTYPE",**{f"D65-S{i}":"TESTED_PROTOTYPE" for i in range(1,8)},"D65-S8":"TESTED_PRODUCT","CUTOVER-R1":"not_evaluable","CUTOVER-G1":"not_evaluable"}
    add("complete-prototype-first-chain",ids==EXPECTED_STAGES and states==expected_states and plan.get("first_executable_stage") is None and plan.get("first_owner_gate") is None,{"ids":ids,"states":states})
    stage_failures=[]
    for stage in stages:
        sid=stage.get("stage_id")
        if sid not in {f"D65-S{i}" for i in range(1,9)}: continue
        cp=LAB/str(stage.get("candidate_path","")); ep=LAB/str(stage.get("evidence_path",""))
        if not cp.is_file() or digest(cp)!=stage.get("candidate_sha256"): stage_failures.append(f"{sid}:candidate")
        if not ep.is_file() or digest(ep)!=stage.get("evidence_sha256"): stage_failures.append(f"{sid}:evidence"); continue
        receipt=load(ep); expected_state="TESTED_PRODUCT" if sid=="D65-S8" else "TESTED_PROTOTYPE"
        if receipt.get("result")!="PASS" or receipt.get("stage_state")!=expected_state or receipt.get("product_approval")!="not-requested" or receipt.get("authority_effect")!="none": stage_failures.append(f"{sid}:claim")
    add("stage-evidence-current",not stage_failures,stage_failures)
    candidate=plan.get("product_candidate",{}); candidate_failures=[]
    for pk,hk in (("manifest_path","manifest_sha256"),("product_test_evidence_path","product_test_evidence_sha256"),("approval_request_path","approval_request_sha256"),("approval_decision_path","approval_decision_sha256"),("approval_evidence_path","approval_evidence_sha256")):
        p=LAB/str(candidate.get(pk,""))
        if not p.is_file() or digest(p)!=candidate.get(hk): candidate_failures.append(pk)
    evidence=load(LAB/candidate["product_test_evidence_path"]); request=load(LAB/candidate["approval_request_path"]); decision=load(LAB/candidate["approval_decision_path"]); approval_evidence=load(LAB/candidate["approval_evidence_path"])
    add("approved-frozen-tested-product",not candidate_failures and evidence.get("result")=="PASS" and evidence.get("product_candidate_frozen") is True and evidence.get("product_approval_eligible") is True and evidence.get("product_approval")=="not-requested" and request.get("manifest_sha256")==candidate.get("manifest_sha256") and request.get("product_test_evidence_sha256")==candidate.get("product_test_evidence_sha256") and request.get("decision_state")=="not-decided" and request.get("authority_effect")=="none" and decision.get("selected_option",{}).get("option_id")=="D65PAPP-1" and decision.get("product_approval",{}).get("state")=="approved" and decision.get("authority_effect")=="product-approval-only" and approval_evidence.get("result")=="PASS" and approval_evidence.get("stage_state")=="PRODUCT_APPROVED" and approval_evidence.get("product_approval")=="approved" and approval_evidence.get("cutover_authorized") is False,{"failures":candidate_failures,"tests":evidence.get("result"),"decision":decision.get("selected_option"),"approval_validation":approval_evidence.get("result")})
    work=plan.get("work_plan",{}); tasks=work.get("operational_tasks",[]); approval_task=next((x for x in tasks if x.get("task_id")=="CAL-OP-D65-EPOCH-002-PRODUCT-APPROVAL-001"),{})
    add("two-lane-terminal-frontier",work.get("current_product_frontier") is None and work.get("continuation_status")=="complete" and approval_task.get("state")=="complete" and approval_task.get("applies_to_stage")=="product_approval" and approval_task.get("blocking_basis")=="authority-boundary" and all(x.get("authority_effect")=="none" for x in tasks),{"frontier":work.get("current_product_frontier"),"tasks":tasks})
    execution=plan.get("execution",{}); add("approval-and-authority-boundary",execution.get("authorized") is False and execution.get("prototype_construction_status")=="product-approved" and execution.get("implementation_ready") is True and execution.get("product_approval_eligible") is True and execution.get("product_approval")=="approved" and execution.get("cutover_authorized") is False and execution.get("cutover_performed") is False and candidate.get("authority_effect")=="product-approval-only" and plan.get("authority_effect")=="none",execution)
    failed=[x["check_id"] for x in checks if x["result"]!="PASS"]; result="PASS" if not failed else "BLOCK"
    validation={"schema_version":"cal.d65-export-cutover-plan-validation/v3","plan_id":plan.get("plan_id"),"revision":plan.get("revision"),"result":result,"checks":checks,"failed_checks":failed,"tested_product_current":result=="PASS","current_product_frontier":None,"next_owner_gate":None,"owner_gate_eligible":False,"product_approval":"approved" if result=="PASS" else "not_evaluable","implementation_admitted":False,"cutover_authorized":False,"cutover_performed":False,"authority_effect":"none","inputs":[{"path":str(PLAN.relative_to(LAB)),"sha256":digest(PLAN)},{"path":str(SCHEMA.relative_to(LAB)),"sha256":digest(SCHEMA)},{"path":str(Path(__file__).relative_to(LAB)),"sha256":digest(Path(__file__))},{"path":candidate.get("approval_decision_path"),"sha256":candidate.get("approval_decision_sha256")}],"claim_ceiling":"PASS proves CAL-PLAN-0004 revision 6 closes D65 product construction through exact product approval. It grants no admission, activation, migration, cutover, publication, release, deployment, or external effect."}
    if args.write_receipt: RECEIPT.parent.mkdir(parents=True,exist_ok=True); RECEIPT.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:validation[k] for k in ("plan_id","revision","result","failed_checks","tested_product_current","current_product_frontier","next_owner_gate","owner_gate_eligible","product_approval","cutover_authorized","authority_effect")},indent=2)); return 0 if result=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
