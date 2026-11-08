import {assertCheckedComposedOperationAction, type CheckedComposedOperationAction} from './action-bindings.js';
import {assertInterfaceData} from '../typed-backend/interface.js';

export interface ComposedWorkflowAction {
 readonly action:CheckedComposedOperationAction;
 readonly absence_failures:readonly Readonly<{binding:string;code:string}>[];
}
export interface ComposedPrecommitStage {readonly stage:string;readonly codes:readonly string[];}

/** Exact precommit metadata vocabulary, not evidence that a provider is truthful. */
export function composedPrecommitStages(action:CheckedComposedOperationAction,absence:ComposedWorkflowAction['absence_failures']):readonly ComposedPrecommitStage[]{
 assertCheckedComposedOperationAction(action);assertInterfaceData(absence);
 const fail=():never=>{throw new TypeError('COMPOSED_SETTLEMENT:explicit absence coverage required');};
 const bindings=action.value_composition.references.composition.bindings;
 const required=bindings.filter(b=>b.kind==='query'&&b.absence==='require-present').map(b=>b.name);
 if(!Array.isArray(absence)||absence.length!==required.length||new Set(absence.map(a=>a.binding)).size!==absence.length)fail();
 for(const row of absence)if(!row||typeof row!=='object'||Object.keys(row).sort().join('|')!=='binding|code'||!required.includes(row.binding)||typeof row.code!=='string'||/^[A-Z][A-Z0-9_]{0,127}$/.exec(row.code)?.[0]!==row.code)fail();
 const stages=new Map<string,Set<string>>();
 const add=(stage:string,codes:string[])=>{const set=stages.get(stage)??new Set<string>();for(const code of codes)set.add(code);stages.set(stage,set);};
 for(const binding of bindings){
  if(binding.kind==='query'){
   add('query-source:'+binding.name,['OPERATION_FAILED']);
   add('query:'+binding.selector,['OPERATION_FAILED','QUERY_CARDINALITY',...(binding.absence==='require-present'?[absence.find(a=>a.binding===binding.name)!.code]:[])]);
  }else add('mapping:'+binding.selector,['OPERATION_FAILED']);
 }
 return Object.freeze([...stages].sort(([a],[b])=>a<b?-1:a>b?1:0).map(([stage,codes])=>Object.freeze({stage,codes:Object.freeze([...codes].sort())})));
}
