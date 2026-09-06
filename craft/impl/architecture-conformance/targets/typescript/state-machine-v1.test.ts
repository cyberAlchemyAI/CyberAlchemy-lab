import {describe,expect,it} from "vitest";
import {decodeStateMachineCase,evaluateStateMachineCase,makeSettlementStateMachineCase} from "./state-machine-v1.js";
describe("TypeScript State Machine v1 target",()=>{
  it("returns deterministic effect-intent handles for both W4 transitions and rejects an invalid transition",()=>{
    const first=evaluateStateMachineCase(makeSettlementStateMachineCase()),second=evaluateStateMachineCase(makeSettlementStateMachineCase());
    expect(second.portable).toEqual(first.portable);
    expect(first.portable.transition_results.map(({accepted,next_state})=>[accepted,next_state])).toEqual([[true,"settled"],[true,"failed"],[false,null]]);
    expect(first.portable.transition_results.filter(({accepted})=>accepted).map(({returned_handle})=>returned_handle?.transition_id)).toEqual(["sm.pending.confirm.settled/v1","sm.pending.reject.failed/v1"]);
    expect(first.portable.effects_performed_inline).toBe(false);
  });
  it("rejects stale dependency handles, unknown members, and unknown returned-intent members",()=>{
    const baseline=makeSettlementStateMachineCase();
    const stale={...baseline,dependency_handles:{...baseline.dependency_handles,event:{...baseline.dependency_handles.event,sha256:"b".repeat(64)}}};
    expect(()=>decodeStateMachineCase(JSON.stringify(stale))).toThrowError("RMT_SM_DEPENDENCY_HANDLE_STALE:event");
    expect(()=>decodeStateMachineCase(JSON.stringify({...baseline,raw_effect_escape:true}))).toThrowError("RMT_SM_CLOSED_DECODE_UNKNOWN_MEMBER");
    const extraRequest={...baseline,requests:[...baseline.requests.slice(0,2),{...baseline.requests[2],execute_effects:true}]};
    expect(()=>decodeStateMachineCase(JSON.stringify(extraRequest))).toThrowError("RMT_SM_CLOSED_DECODE_UNKNOWN_MEMBER");
  });
});
