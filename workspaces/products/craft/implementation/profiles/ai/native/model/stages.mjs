import {assert,freeze} from '../shared.mjs';
import {INFERENCE_ABI} from './index.mjs';
export const OBSERVATION_STAGE_ABI='typed-model-observation-stage/v1';

/** Typed model observations remain proposals. The original generated business
 * Entry/Operation owns Auth, Rules, Policies and commit. This wrapper calls that
 * existing owner, never mirrors an authored predicate or business branch.
 * Open Questions: README.md. */
export function createTypedObservationStage({inference,bindInvocation,applyObservation,assertCurrent}) {
 assert(inference?.abi===INFERENCE_ABI&&typeof bindInvocation==='function'&&typeof assertCurrent==='function','ForeignOwner','original generated stage owners');
 const proposals=new WeakMap();let closed=false;
 const current=()=>{assert(!closed,'StaleOwner','stage closed');assert(assertCurrent()===true,'StaleOwner','current original business owner');inference.assertCurrent();};
 return Object.freeze({abi:OBSERVATION_STAGE_ABI,
  async propose(request){current();const bound=await bindInvocation(request);current();const outcome=await inference.invoke({...request,...bound});current();
   if(outcome.kind!=='candidate')return outcome;
   const proposal=Object.freeze({kind:'typed-model-proposal',value:outcome.value,wire:new Uint8Array(outcome.wire),usage:outcome.usage,exposure:outcome.exposure,attemptId:outcome.attemptId,...(outcome.embeddingSpace?{embeddingSpace:outcome.embeddingSpace}:{})});
   proposals.set(proposal,{bound,outcome});return proposal;
  },
  async apply(proposal,authorization){current();const owned=proposals.get(proposal);assert(owned,'ForeignOwner','opaque original typed proposal');assert(typeof applyObservation==='function','UnsupportedCapability','original generated business apply owner required');
   // Authored Rules/Policies execute inside this original compiled operation.
   const result=await applyObservation({value:owned.outcome.value,wire:new Uint8Array(owned.outcome.wire),bindingId:owned.bound.bindingId,attemptId:owned.outcome.attemptId,authorization});current();return result;
  },
  inspect(proposal){current();const owned=proposals.get(proposal);assert(owned,'ForeignOwner','original proposal');return freeze({abi:OBSERVATION_STAGE_ABI,bindingId:owned.bound.bindingId,attemptId:owned.outcome.attemptId,authority:'proposal-only',...(owned.outcome.embeddingSpace?{embeddingSpace:owned.outcome.embeddingSpace}:{})});},
  close(){closed=true;},
 });
}
