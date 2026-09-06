"""Candidate-local native Python witness for WP-RMT-002 State Machine."""
from __future__ import annotations
import json,sys
from dataclasses import dataclass
EXPECTED_DEPENDENCIES={"mapping":{"swu_id":"RMT-MAP-010","sha256":"0f510344fe868b24e84b11e85397db3ca459dc6f9f7df3fbdfabdbf38ff2d544"},"event":{"swu_id":"RMT-EVENT-010","sha256":"662c95eced8e9fc9b5c8b52e8d8145f95e77e3864a9d0e28b05ffe9e4ed8de55"},"rule":{"swu_id":"RMT-RULE-010","sha256":"e39d3df7ec6e4d2f4b33b3b3a30f85c2896f8f668d0f8148e3911393aaa9116b"}}
@dataclass(frozen=True)
class TransitionDecision:
    accepted:bool
    next_state:str|None
    guard_ids:tuple[str,...]
    effect_intents:tuple[str,...]
def transition(state:str,trigger:str,guard_passed:bool)->TransitionDecision:
    if not guard_passed:return TransitionDecision(False,None,(),())
    if state=="pending" and trigger=="confirm":return TransitionDecision(True,"settled",("can-settle",),("persist-settlement","append-settlement-created"))
    if state=="pending" and trigger=="reject":return TransitionDecision(True,"failed",("can-settle",),("record-rejection",))
    return TransitionDecision(False,None,(),())
def decode_effect_intent(value:object)->dict[str,object]:
    if not isinstance(value,dict) or sorted(value)!=["effect_intent_id","payload"]:raise ValueError("RMT_S1_CLOSED_DECODE_UNKNOWN_MEMBER")
    if not isinstance(value["effect_intent_id"],str) or not value["effect_intent_id"] or not isinstance(value["payload"],dict):raise ValueError("RMT_S1_CLOSED_DECODE_INVALID_SHAPE")
    return value
def evaluate_state_machine(descriptor:dict[str,object],observed:dict[str,object])->tuple[str,...]:
    findings:list[str]=[]
    if observed["illegal_transition_observed"] or sorted(observed["observed_transition_ids"])!=sorted(item["transition_id"] for item in descriptor["transitions"]):findings.append("RMT_SM_ILLEGAL_TRANSITION")
    if observed["observed_initial_state"]!=descriptor["initial_state"]:findings.append("RMT_SM_INITIAL_STATE_DRIFT")
    if sorted(observed["observed_terminal_states"])!=sorted(descriptor["terminal_states"]):findings.append("RMT_SM_TERMINAL_STATE_DRIFT")
    if observed["guard_bypass_observed"]:findings.append("RMT_SM_GUARD_BYPASS")
    if observed["nondeterministic_outcome_observed"]:findings.append("RMT_SM_NONDETERMINISTIC_TRANSITION")
    if observed["effects_performed_inline"]:findings.append("RMT_SM_EXECUTES_EFFECT")
    if observed["observed_cycle_policy"]!=descriptor["cycle_policy"] or observed["undeclared_cycle_observed"]:findings.append("RMT_SM_CYCLE_POLICY_MISMATCH")
    if observed["invalid_transition_accepted"]:findings.append("RMT_SM_INVALID_TRANSITION_SUCCESS")
    if observed["hidden_mutation_observed"]:findings.append("RMT_SM_HIDDEN_MUTATION")
    if not observed["stable_transition_ids"]:findings.append("RMT_SM_UNSTABLE_TRANSITION_IDENTITY")
    return tuple(findings)
def decode_case(value:object)->dict[str,object]:
    if not isinstance(value,dict) or sorted(value)!=["dependency_handles","descriptor","observation","requests"]:raise ValueError("RMT_SM_CLOSED_DECODE_UNKNOWN_MEMBER")
    if value["dependency_handles"]!=EXPECTED_DEPENDENCIES:raise ValueError("RMT_SM_DEPENDENCY_HANDLE_STALE")
    if not isinstance(value["requests"],list) or len(value["requests"])!=3:raise ValueError("RMT_SM_REQUEST_SET_INVALID")
    for request in value["requests"]:
        if not isinstance(request,dict) or sorted(request)!=["current_state","guard_passed","trigger"]:raise ValueError("RMT_SM_CLOSED_DECODE_UNKNOWN_MEMBER")
    return value
def evaluate_case(case:dict[str,object])->dict[str,object]:
    case=decode_case(case)
    descriptor=case["descriptor"];observed=case["observation"]
    findings=evaluate_state_machine(descriptor,observed)
    if findings:raise ValueError("RMT_SM_PYTHON_REJECTED:"+",".join(findings))
    results=[]
    by_pair={(item["from_state"],item["trigger"]):item for item in descriptor["transitions"]}
    for request in case["requests"]:
        decision=transition(request["current_state"],request["trigger"],request["guard_passed"])
        definition=by_pair.get((request["current_state"],request["trigger"]))
        handle=None
        if decision.accepted and definition:
            intents=[decode_effect_intent({"effect_intent_id":item,"payload":{}}) for item in decision.effect_intents]
            handle={"handle":"state-machine-transition-effect-intent/v1","transition_id":definition["transition_id"],"from_state":request["current_state"],"to_state":decision.next_state,"effect_intents":intents}
        results.append({"current_state":request["current_state"],"trigger":request["trigger"],"accepted":decision.accepted,"next_state":decision.next_state,"guard_ids":list(decision.guard_ids),"effect_intents":list(decision.effect_intents),"returned_handle":handle})
    portable={"schema_version":"domainspec.state-machine-portable-result/v1","result":"pass","meta_type":"State Machine","state_ids":descriptor["state_ids"],"initial_state":descriptor["initial_state"],"terminal_states":descriptor["terminal_states"],"cycle_policy":descriptor["cycle_policy"],"invalid_transition_policy":"reject","transition_results":results,"effect_execution":"returned-effect-intents","effects_performed_inline":False,"semantic_plan_epoch_id":descriptor["semantic_plan_epoch_id"],"semantic_contract_digest":descriptor["semantic_contract_digest"],"authority_effect":"none"}
    return {"portable":portable,"native_evidence":{"language":"python","mechanism":"frozen-dataclass-pure-transition-and-closed-returned-intent-handle"}}
if __name__=="__main__" and sys.argv[1:]==["--evaluate"]:
    try:print(json.dumps(evaluate_case(json.load(sys.stdin)),sort_keys=True,separators=(",",":")))
    except Exception as error:print(str(error),file=sys.stderr);raise SystemExit(1) from error
