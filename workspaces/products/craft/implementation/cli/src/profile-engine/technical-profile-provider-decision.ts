/** Closed source Policy -> genuine original provider Attempt frame admission.
 * Original Core checks the Policy/Decision contract; this finite family joins
 * its five declared actions to the same original provider owner.
 * Open Questions: docs/TECHNICAL-PROFILE-SOURCE.md#open-questions. */
import {captureJson,reject} from './contracts.js';
export const TECHNICAL_PROVIDER_DECISION_ACTIONS=Object.freeze({Dispatch:'dispatch',Backoff:'backoff',InspectOriginal:'inspect',Finish:'replay',Halt:'halt'} as const);
export function validateTechnicalProviderDecisionBindings(runtimeBindings:readonly any[],providerStages:readonly any[]){
 const fail=(message:string):never=>reject('TECHNICAL_PROFILE_PROVIDER_DECISION','provider-decision',message),out:any[]=[];
 for(const binding of runtimeBindings){
  const stage=providerStages.find(s=>s.binding===binding.binding&&s.selection.operation===binding.operation);
  if(stage?.selection.readCurrent===true)fail('readCurrent cannot establish authoritative effect classification for this provider Decision family');
  if(!stage||binding.kind!=='decision'||out.some(v=>v.binding===binding.binding)||JSON.stringify(binding.arguments)!==JSON.stringify({attempt:{from:'owner.observation.attempt'}}))fail('only one exact original-provider Decision/Attempt binding per selected operation is supported');
  if(Object.keys(binding.handlers??{}).sort().join(',')!==Object.keys(TECHNICAL_PROVIDER_DECISION_ACTIONS).sort().join(','))fail('provider Decision must declare exactly Dispatch/Backoff/InspectOriginal/Finish/Halt; credential actions need their original credential owner');
  for(const [action,operation]of Object.entries(TECHNICAL_PROVIDER_DECISION_ACTIONS)){const h=binding.handlers[action];if(h?.owner!==binding.binding||h.operation!==operation)fail('provider Decision handlers must select the same exact original provider owner and action');}
  out.push(captureJson(binding));
 }
 return Object.freeze(out);
}
