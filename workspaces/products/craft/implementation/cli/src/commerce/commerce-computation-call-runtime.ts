/** Pure outcome adaptation only; source actions are proposals, never effects.
 * Open Questions: docs/COMMERCE-COMPUTATION-CALLS.md#open-questions. */
export function adaptCommercePureCallResult(observation:any,spec:any):any {
 let decision:string,action:any=null;
 if(!observation.result.ok){
  decision=observation.evaluation_phase==='input-validation'?'parameter-validation-error':'evaluation-error';
  if(decision==='evaluation-error')action=spec.on_error;
 }else if(spec.direct_guard){
  const bool=new TextDecoder().decode(observation.result.wire);
  if(bool!=='true'&&bool!=='false')throw new Error('InvalidBooleanComputationResult');
  decision=bool==='true'?'guard-true':'guard-false';if(bool==='false')action=spec.on_false;
 }else decision='value';
 return {observation,decision,source_action:action,action_requirement:action?(spec.requires_rollback?'requires-original-proven-rollback-before-source-action':'requires-original-caller-to-apply-source-action'):'none',qualification:'bound-pure-parameter-evaluation-only;argument-acquisition-and-operation-execution-not-established',authority_effect:'none'};
}
