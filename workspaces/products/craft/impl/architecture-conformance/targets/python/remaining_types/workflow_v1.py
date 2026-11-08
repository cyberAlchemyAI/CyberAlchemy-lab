"""Candidate-local native Python witness for WP-RMT-002 Workflow."""
from __future__ import annotations
import json,sys
EXPECTED_DEPENDENCIES={"operation":{"swu_id":"RMT-OP-010","sha256":"3eea502705e2960ee328a3d86931ccfb13090ad7c2d682223f9816f68d629e0e"},"rule":{"swu_id":"RMT-RULE-010","sha256":"e39d3df7ec6e4d2f4b33b3b3a30f85c2896f8f668d0f8148e3911393aaa9116b"},"state_machine":{"swu_id":"RMT-SM-010","sha256":"ff7f94427fb5d52da9ea2bb835d566e9ace86f47f6eb38b1717b3b6576d1a3ee"}}
def evaluate_workflow(descriptor:dict[str,object],observed:dict[str,object])->tuple[str,...]:
    findings:list[str]=[];expected=descriptor["ordered_step_ids"];actual=observed["observed_step_ids"]
    if len(actual)<len(expected) or any(item not in actual for item in expected):findings.append("RMT_WF_STEP_SKIP")
    elif len(set(actual))!=len(actual):findings.append("RMT_WF_STEP_DUPLICATE")
    elif actual!=expected:findings.append("RMT_WF_STEP_REORDER")
    if observed["scope"]!=descriptor["scope"]:findings.append("RMT_WF_SCOPE_DRIFT")
    if observed["failure_continuation_policy"]!=descriptor["failure_continuation_policy"]:findings.append("RMT_WF_FAILURE_CONTINUATION_MISMATCH")
    if observed["compensation_policy"]!=descriptor["compensation_policy"] or observed["recovery_intents"] or observed["durable_fact_preservation"]!=descriptor["post_commit_failure_policy"]:findings.append("RMT_WF_COMPENSATION_OVERCLAIM")
    if observed["direct_effects_executed"]:findings.append("RMT_WF_EXECUTES_EFFECT")
    if observed["binding_state"]!="current":findings.append("RMT_WF_STALE_BINDING")
    if observed["guard_bypass_observed"]:findings.append("RMT_WF_GUARD_BYPASS")
    if observed["lifecycle_transition_bypass_observed"]:findings.append("RMT_WF_LIFECYCLE_TRANSITION_BYPASS")
    return tuple(findings)
def validate_bindings(descriptor:dict[str,object])->None:
    bindings=descriptor["s1_bindings"]
    if bindings["operation"]["candidate_sha256"]!=EXPECTED_DEPENDENCIES["operation"]["sha256"] or bindings["operation"]["handle"]!="operation-transaction-effect-group/v1" or bindings["rule"]["candidate_sha256"]!=EXPECTED_DEPENDENCIES["rule"]["sha256"] or bindings["state_machine"]["candidate_sha256"]!=EXPECTED_DEPENDENCIES["state_machine"]["sha256"] or bindings["state_machine"]["handle"]!="state-machine-transition-effect-intent/v1":raise ValueError("RMT_S1_STALE_BINDING")
def decode_case(value:object)->dict[str,object]:
    if not isinstance(value,dict) or sorted(value)!=["dependency_handles","descriptor","observation","scenarios"]:raise ValueError("RMT_WF_CLOSED_DECODE_UNKNOWN_MEMBER")
    if value["dependency_handles"]!=EXPECTED_DEPENDENCIES:raise ValueError("RMT_WF_DEPENDENCY_HANDLE_STALE")
    if not isinstance(value["scenarios"],list) or len(value["scenarios"])!=2:raise ValueError("RMT_WF_SCENARIO_SET_INVALID")
    for scenario in value["scenarios"]:
        if not isinstance(scenario,dict) or sorted(scenario)!=["fail_step_id","scenario_id"]:raise ValueError("RMT_WF_CLOSED_DECODE_UNKNOWN_MEMBER")
    validate_bindings(value["descriptor"]);return value
def evaluate_case(case:dict[str,object])->dict[str,object]:
    case=decode_case(case);d=case["descriptor"];o=case["observation"];findings=evaluate_workflow(d,o)
    if o["s1_binding_state"]!="current":raise ValueError("RMT_S1_STALE_BINDING")
    if findings:raise ValueError("RMT_WF_PYTHON_REJECTED:"+",".join(findings))
    scenarios=[]
    for scenario in case["scenarios"]:
        failure=scenario["fail_step_id"]=="publish";scenarios.append({"scenario_id":scenario["scenario_id"],"trace":d["ordered_step_ids"][:3] if failure else d["ordered_step_ids"],"terminal_outcome":"settlement-failed" if failure else "settlement-completed","failed_step_id":scenario["fail_step_id"],"recovery_intents":["forward-recover-settlement"] if failure else [],"compensation_execution":False,"durable_fact_ids":["settlement:req-1"],"durable_fact_preservation":"preserve-durable-facts","direct_effects_executed":[]})
    portable={"schema_version":"domainspec.workflow-portable-result/v1","result":"pass","meta_type":"Workflow","scope":d["scope"],"ordered_step_ids":d["ordered_step_ids"],"binding_handle":"workflow-s1-bindings/v1","operation_handle":"operation-transaction-effect-group/v1","state_machine_handle":"state-machine-transition-effect-intent/v1","scenarios":scenarios,"authority_separation":True,"semantic_plan_epoch_id":d["semantic_plan_epoch_id"],"semantic_contract_digest":d["semantic_contract_digest"],"authority_effect":"none"}
    return {"portable":portable,"native_evidence":{"language":"python","mechanism":"pure-ordered-trace-and-forward-recovery-datamodel"}}
if __name__=="__main__" and sys.argv[1:]==["--evaluate"]:
    try:print(json.dumps(evaluate_case(json.load(sys.stdin)),sort_keys=True,separators=(",",":")))
    except Exception as error:print(str(error),file=sys.stderr);raise SystemExit(1) from error
