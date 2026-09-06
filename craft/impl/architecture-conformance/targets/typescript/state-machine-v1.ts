import type {StateMachineDescriptor,StateMachineObservation} from "../../families/orchestration-lifecycle/contracts/w4-contracts.js";
import {evaluateW4} from "../../families/orchestration-lifecycle/evaluator/evaluate-w4.js";
import type {LifecycleStateMachineDescriptor,LifecycleStateMachineObservation,TransitionEffectIntentHandle} from "../../families/lifecycle-state-machine/contracts/state-machine-contracts.js";
import {decodeReturnedEffectIntent,evaluateLifecycleStateMachine} from "../../families/lifecycle-state-machine/evaluator/evaluate-state-machine.js";
import {settlementStateMachineDescriptor,settlementStateMachineObservation} from "../../families/lifecycle-state-machine/fixtures/settlement-state-machine.js";

const EXPECTED_DEPENDENCIES=Object.freeze({
  mapping:Object.freeze({swu_id:"RMT-MAP-010",sha256:"0f510344fe868b24e84b11e85397db3ca459dc6f9f7df3fbdfabdbf38ff2d544"}),
  event:Object.freeze({swu_id:"RMT-EVENT-010",sha256:"662c95eced8e9fc9b5c8b52e8d8145f95e77e3864a9d0e28b05ffe9e4ed8de55"}),
  rule:Object.freeze({swu_id:"RMT-RULE-010",sha256:"e39d3df7ec6e4d2f4b33b3b3a30f85c2896f8f668d0f8148e3911393aaa9116b"})
});
const settlementTransitions=Object.freeze([
  Object.freeze({from:"pending",trigger:"confirm",to:"settled",guard_ids:Object.freeze(["can-settle"]),effect_intents:Object.freeze(["persist-settlement","append-settlement-created"])}),
  Object.freeze({from:"pending",trigger:"reject",to:"failed",guard_ids:Object.freeze(["can-settle"]),effect_intents:Object.freeze(["record-rejection"])})
] as const);
const transitionSettlementLifecycle=(state:"pending"|"settled"|"failed",trigger:"confirm"|"reject")=>state==="pending"&&trigger==="confirm"?Object.freeze({accepted:true,nextState:"settled" as const,guardIds:Object.freeze(["can-settle"]),effectIntents:Object.freeze(["persist-settlement","append-settlement-created"])}):state==="pending"&&trigger==="reject"?Object.freeze({accepted:true,nextState:"failed" as const,guardIds:Object.freeze(["can-settle"]),effectIntents:Object.freeze(["record-rejection"])}):Object.freeze({accepted:false,nextState:null,guardIds:Object.freeze([] as string[]),effectIntents:Object.freeze([] as string[])});
type DependencyHandles=typeof EXPECTED_DEPENDENCIES;
export type StateMachineRequest=Readonly<{current_state:"pending"|"settled"|"failed";trigger:"confirm"|"reject";guard_passed:boolean}>;
export type StateMachineCase=Readonly<{dependency_handles:DependencyHandles;descriptor:LifecycleStateMachineDescriptor;observation:LifecycleStateMachineObservation;requests:readonly StateMachineRequest[]}>;
export type StateMachinePortableResult=Readonly<{schema_version:"domainspec.state-machine-portable-result/v1";result:"pass";meta_type:"State Machine";state_ids:readonly string[];initial_state:string;terminal_states:readonly string[];cycle_policy:"declared-only";invalid_transition_policy:"reject";transition_results:readonly Readonly<{current_state:string;trigger:string;accepted:boolean;next_state:string|null;guard_ids:readonly string[];effect_intents:readonly string[];returned_handle:TransitionEffectIntentHandle|null}>[];effect_execution:"returned-effect-intents";effects_performed_inline:false;semantic_plan_epoch_id:string;semantic_contract_digest:string;authority_effect:"none"}>;
const exactKeys=(value:unknown,keys:readonly string[],code:string):Record<string,unknown>=>{if(!value||typeof value!=="object"||Array.isArray(value)||JSON.stringify(Object.keys(value).sort())!==JSON.stringify([...keys].sort()))throw new Error(code);return value as Record<string,unknown>;};
const ref=(id:string)=>({id,sha256:"a".repeat(64)});
const w4Descriptor:StateMachineDescriptor={schema_version:"domainspec.w4-descriptor/v1",descriptor_id:"state-machine.settlement-lifecycle",language:"typescript",binding:{protocol_id:"domainspec.w4-descriptor-binding/v1",concept_ref:ref("DS-D1.14"),decision_ref:ref("W4-A-PURE-GRAPH-BOUND-ORCHESTRATION-LIFECYCLE"),profile_ref:ref("architecture.typescript-strict"),provider_ref:ref("typescript.settlement-state-machine"),source_ref:ref("settlement-state-machine.ts"),fixture_ref:ref("financial-settlement.w4.observations")},admission_status:"candidate",claim_ceiling:"candidate-local-exact-fixture",authority_effect:"none",kind:"StateMachine",expected_states:["pending","settled","failed"],initial_state:"pending",terminal_states:["settled","failed"],transitions:settlementTransitions,invalid_transition_policy:"reject",effect_execution:"returned-effect-intents"};
const toExecution=(from:"pending"|"settled",trigger:"confirm"|"reject")=>{const decision=transitionSettlementLifecycle(from,trigger);return{from,trigger,accepted:decision.accepted,to:decision.nextState,guard_ids:decision.guardIds,effect_intents:decision.effectIntents};};
const w4Observation:StateMachineObservation={kind:"StateMachine",observed_states:["pending","settled","failed"],observed_initial_state:"pending",observed_terminal_states:["settled","failed"],observed_transitions:settlementTransitions,executions:[toExecution("pending","confirm"),toExecution("pending","reject"),toExecution("settled","confirm")],effects_performed_inline:[]};
export const makeSettlementStateMachineCase=():StateMachineCase=>Object.freeze({dependency_handles:EXPECTED_DEPENDENCIES,descriptor:settlementStateMachineDescriptor,observation:settlementStateMachineObservation(),requests:Object.freeze([{current_state:"pending",trigger:"confirm",guard_passed:true},{current_state:"pending",trigger:"reject",guard_passed:true},{current_state:"settled",trigger:"confirm",guard_passed:true}] as const)});
export const decodeStateMachineCase=(text:string):StateMachineCase=>{
  let parsed:unknown;try{parsed=JSON.parse(text);}catch{throw new Error("RMT_SM_CLOSED_DECODE_INVALID_JSON");}
  const top=exactKeys(parsed,["dependency_handles","descriptor","observation","requests"],"RMT_SM_CLOSED_DECODE_UNKNOWN_MEMBER");
  const dependencies=exactKeys(top.dependency_handles,["mapping","event","rule"],"RMT_SM_DEPENDENCY_HANDLE_INVALID");
  for(const key of ["mapping","event","rule"] as const){const handle=exactKeys(dependencies[key],["sha256","swu_id"],"RMT_SM_DEPENDENCY_HANDLE_INVALID");if(JSON.stringify(handle)!==JSON.stringify(EXPECTED_DEPENDENCIES[key]))throw new Error("RMT_SM_DEPENDENCY_HANDLE_STALE:"+key);}
  if(!Array.isArray(top.requests)||top.requests.length!==3)throw new Error("RMT_SM_REQUEST_SET_INVALID");
  for(const request of top.requests)exactKeys(request,["current_state","guard_passed","trigger"],"RMT_SM_CLOSED_DECODE_UNKNOWN_MEMBER");
  return parsed as StateMachineCase;
};
export const evaluateStateMachineCase=(input:StateMachineCase):Readonly<{portable:StateMachinePortableResult;native_evidence:Readonly<{language:"typescript";mechanism:"unchanged-w4-pure-transition-plus-closed-returned-intent-handle"}>}>=>{
  const family=evaluateLifecycleStateMachine(input.descriptor,input.observation),w4=evaluateW4(w4Descriptor,w4Observation);
  if(family.verdict!=="pass"||w4.verdict!=="pass")throw new Error("RMT_SM_TYPESCRIPT_REJECTED:"+JSON.stringify({family:family.findings,w4:w4.findings}));
  if(JSON.stringify(input.dependency_handles)!==JSON.stringify(EXPECTED_DEPENDENCIES))throw new Error("RMT_SM_DEPENDENCY_HANDLE_STALE");
  const transitionResults=input.requests.map(request=>{
    const decision=transitionSettlementLifecycle(request.current_state,request.trigger);
    const accepted=decision.accepted&&request.guard_passed;
    const transition=input.descriptor.transitions.find(item=>item.from_state===request.current_state&&item.trigger===request.trigger);
    const effectIntents=accepted?decision.effectIntents:[];
    const handle=accepted&&transition?Object.freeze({handle:"state-machine-transition-effect-intent/v1" as const,transition_id:transition.transition_id,from_state:request.current_state,to_state:decision.nextState!,effect_intents:Object.freeze(effectIntents.map(effect_intent_id=>decodeReturnedEffectIntent({effect_intent_id,payload:{}})))}):null;
    return Object.freeze({current_state:request.current_state,trigger:request.trigger,accepted,next_state:accepted?decision.nextState:null,guard_ids:accepted?decision.guardIds:Object.freeze([]),effect_intents:Object.freeze([...effectIntents]),returned_handle:handle});
  });
  return Object.freeze({portable:Object.freeze({schema_version:"domainspec.state-machine-portable-result/v1",result:"pass",meta_type:"State Machine",state_ids:Object.freeze([...input.descriptor.state_ids]),initial_state:input.descriptor.initial_state,terminal_states:Object.freeze([...input.descriptor.terminal_states]),cycle_policy:input.descriptor.cycle_policy,invalid_transition_policy:"reject",transition_results:Object.freeze(transitionResults),effect_execution:"returned-effect-intents",effects_performed_inline:false,semantic_plan_epoch_id:input.descriptor.semantic_plan_epoch_id,semantic_contract_digest:input.descriptor.semantic_contract_digest,authority_effect:"none"}),native_evidence:Object.freeze({language:"typescript",mechanism:"unchanged-w4-pure-transition-plus-closed-returned-intent-handle"})});
};
