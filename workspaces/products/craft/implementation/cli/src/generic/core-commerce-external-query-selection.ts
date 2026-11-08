/** Source-derived service Query dependencies for a selected Core Operation.
 * Native service actors are provisioned separately; their Entry binding and
 * required permission come only from the checked source.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import type {EffectPlanV1,EntryContractV1,OperationCallV1} from '../commerce/commerce-data-v1.js';

export interface CoreCommerceExternalQueryBinding {
 readonly query:string;
 readonly entry:string;
 readonly target_service:string;
 readonly caller_service:string;
 readonly permission:EntryContractV1['access']['auth_permission'];
 readonly scope:string;
 readonly source_call_paths:readonly string[];
}

export function selectCoreCommerceExternalQueries(
 plan:EffectPlanV1,
 entries:readonly EntryContractV1[],
 selectedServices:readonly string[],
):readonly CoreCommerceExternalQueryBinding[]{
 if(!plan.service||!selectedServices.includes(plan.service))throw new Error('selected Operation service required');
 const sourceEntries=new Map(entries.map(entry=>[entry.id,entry]));
 if(sourceEntries.size!==entries.length)throw new Error('distinct checked source Entries required');
 const selected=new Set(selectedServices),calls=new Map<string,{call:OperationCallV1;paths:string[]}>();
 let visited=0;
 const walk=(value:unknown,at:string,depth:number):void=>{
  if(!value||typeof value!=='object')return;
  if(++visited>65536||depth>128||at.length>8192)throw new Error('bounded source Operation traversal required');
  if(!Array.isArray(value)&&'target'in value&&'role'in value&&'authorization'in value&&'entry'in value&&
    'arguments'in value&&'contexts'in value){
   const call=value as OperationCallV1;
   if(call.role==='Query'&&call.authorization==='fresh-original-entry-decision-required'){
    if(!call.entry||typeof call.target!=='string')throw new Error('external Query source Entry required');
    const original=sourceEntries.get(call.entry);
    if(!original||original.invokes.role!=='Query'||original.invokes.module+'.'+original.invokes.name!==call.target||
      original.access.principal_kind!=='service'||original.access.caller!==plan.service||!selected.has(original.service))
     throw new Error('external Query must retain checked source Entry and selected service caller');
    const existing=calls.get(call.target);
    if(existing&&existing.call.entry!==call.entry)throw new Error('ambiguous external Query Entry');
    if(existing)existing.paths.push(at);
    else calls.set(call.target,{call,paths:[at]});
   }
  }
  if(Array.isArray(value))value.forEach((child,index)=>walk(child,at+'['+index+']',depth+1));
  else for(const [key,child]of Object.entries(value))walk(child,at+'.'+key,depth+1);
 };
 walk(plan.body,'$.body',0);
 return Object.freeze([...calls].sort(([left],[right])=>left.localeCompare(right)).map(([query,row])=>{
  const entry=sourceEntries.get(row.call.entry!)!;
  return Object.freeze({query,entry:entry.id,target_service:entry.service,caller_service:plan.service!,
   permission:entry.access.auth_permission,scope:entry.access.auth_permission.scope,
   source_call_paths:Object.freeze(row.paths.sort())});
 }));
}
