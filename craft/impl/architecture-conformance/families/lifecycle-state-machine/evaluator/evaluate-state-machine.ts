import type {LifecycleStateMachineDescriptor,LifecycleStateMachineObservation,ReturnedEffectIntent,StateMachineEvaluation,StateMachineFindingCode,StateMachineRelationAssertion} from "../contracts/state-machine-contracts.js";
type Finding=StateMachineEvaluation["findings"][number];
const finding=(code:StateMachineFindingCode,expected:unknown,observed:unknown):Finding=>({code,expected,observed});
const sameSet=(a:readonly string[],b:readonly string[])=>a.length===new Set(a).size&&b.length===new Set(b).size&&JSON.stringify([...a].sort())===JSON.stringify([...b].sort());
const finish=(descriptor_id:string,findings:Finding[]):StateMachineEvaluation=>Object.freeze({schema_version:"domainspec.lifecycle-state-machine-evaluation/v1",descriptor_id,verdict:findings.length?"reject":"pass",findings:Object.freeze(findings),authority_effect:"none"});
export const evaluateLifecycleStateMachine=(descriptor:LifecycleStateMachineDescriptor,observed:LifecycleStateMachineObservation):StateMachineEvaluation=>{
  const findings:Finding[]=[];
  if(observed.illegal_transition_observed||!sameSet(descriptor.transitions.map(({transition_id})=>transition_id),observed.observed_transition_ids))findings.push(finding("RMT_SM_ILLEGAL_TRANSITION",descriptor.transitions.map(({transition_id})=>transition_id),observed.observed_transition_ids));
  if(observed.observed_initial_state!==descriptor.initial_state)findings.push(finding("RMT_SM_INITIAL_STATE_DRIFT",descriptor.initial_state,observed.observed_initial_state));
  if(!sameSet(descriptor.terminal_states,observed.observed_terminal_states))findings.push(finding("RMT_SM_TERMINAL_STATE_DRIFT",descriptor.terminal_states,observed.observed_terminal_states));
  if(observed.guard_bypass_observed)findings.push(finding("RMT_SM_GUARD_BYPASS",false,true));
  if(observed.nondeterministic_outcome_observed)findings.push(finding("RMT_SM_NONDETERMINISTIC_TRANSITION",false,true));
  if(observed.effects_performed_inline.length>0)findings.push(finding("RMT_SM_EXECUTES_EFFECT",[],observed.effects_performed_inline));
  if(observed.observed_cycle_policy!==descriptor.cycle_policy||observed.undeclared_cycle_observed)findings.push(finding("RMT_SM_CYCLE_POLICY_MISMATCH",descriptor.cycle_policy,{policy:observed.observed_cycle_policy,undeclared:observed.undeclared_cycle_observed}));
  if(observed.invalid_transition_accepted)findings.push(finding("RMT_SM_INVALID_TRANSITION_SUCCESS",false,true));
  if(observed.hidden_mutation_observed)findings.push(finding("RMT_SM_HIDDEN_MUTATION",false,true));
  if(!observed.stable_transition_ids)findings.push(finding("RMT_SM_UNSTABLE_TRANSITION_IDENTITY",true,false));
  return finish(descriptor.descriptor_id,findings);
};
export const decodeReturnedEffectIntent=(value:unknown):ReturnedEffectIntent=>{
  if(!value||typeof value!=="object"||Array.isArray(value))throw new Error("RMT_S1_CLOSED_DECODE_INVALID_SHAPE");
  const record=value as Record<string,unknown>,keys=Object.keys(record).sort();
  if(JSON.stringify(keys)!==JSON.stringify(["effect_intent_id","payload"]))throw new Error("RMT_S1_CLOSED_DECODE_UNKNOWN_MEMBER");
  if(typeof record.effect_intent_id!=="string"||record.effect_intent_id.length===0||!record.payload||typeof record.payload!=="object"||Array.isArray(record.payload))throw new Error("RMT_S1_CLOSED_DECODE_INVALID_SHAPE");
  return Object.freeze({effect_intent_id:record.effect_intent_id,payload:Object.freeze({...record.payload as Record<string,unknown>})});
};
const endpoints=(id:StateMachineRelationAssertion["contract_id"])=>id==="state-machine/guarded-by-rule"?{source:["architecture.RuleImplementation"],target:["architecture.StateMachineImplementation"]}:id==="state-machine/has-state"?{source:["architecture.StateMachineImplementation"],target:["architecture.StateContract"]}:{source:["architecture.StateContract"],target:["architecture.StateContract"]};
export const evaluateStateMachineRelation=(assertion:StateMachineRelationAssertion):StateMachineEvaluation=>{
  const findings:Finding[]=[],allowed=endpoints(assertion.contract_id);
  if(assertion.owner_evidence_sha256!==assertion.current_owner_evidence_sha256)findings.push(finding("RMT_RELATION_OWNER_EVIDENCE_STALE",assertion.current_owner_evidence_sha256,assertion.owner_evidence_sha256));
  if(!allowed.source.includes(assertion.source_type))findings.push(finding("RMT_RELATION_SOURCE_ENDPOINT_MISMATCH",allowed.source,assertion.source_type));
  if(!allowed.target.includes(assertion.target_type))findings.push(finding("RMT_RELATION_TARGET_ENDPOINT_MISMATCH",allowed.target,assertion.target_type));
  if(assertion.mode==="materialized"&&!assertion.exact_assertion_id)findings.push(finding("RMT_RELATION_ASSERTION_REQUIRED","non-empty exact assertion id",assertion.exact_assertion_id));
  return finish(assertion.contract_id,findings);
};
