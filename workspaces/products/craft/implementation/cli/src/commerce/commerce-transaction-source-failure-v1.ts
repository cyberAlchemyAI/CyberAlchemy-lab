/** Source paths for actions declared inside an atomic transaction. The native
 * rollback owner supplies the failure path; this module only resolves it back
 * to the checked transaction plan. Open Questions:
 * docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import type {OperationActionV1,TransactionPlanV1,TransactionStepV1} from './commerce-data-v1.js';
import {dataDigest} from '../profile-engine/contracts.js';

export interface CommerceTransactionFailureActionV1 {
 readonly action:OperationActionV1;
 readonly action_path:string;
 readonly failure_path:string;
 readonly failure_kind:'guard'|'let';
}

export function commerceTransactionFailureActionsV1(path:string,plan:TransactionPlanV1):readonly CommerceTransactionFailureActionV1[] {
 const found:CommerceTransactionFailureActionV1[]=[];
 const walk=(steps:readonly TransactionStepV1[],base:string):void=>{
  steps.forEach((step,index)=>{
   const at=base+'['+index+']';
   if(step.kind==='guard')found.push({action:step.on_false,action_path:at+'.on_false',failure_path:at,failure_kind:'guard'});
   else if(step.kind==='let'&&step.on_error)found.push({action:step.on_error,action_path:at+'.on_error',failure_path:at+'.value',failure_kind:'let'});
   else if(step.kind==='for')walk(step.body,at+'.body');
   else if(step.kind==='conditional'){
    walk(step.then,at+'.then');walk(step.otherwise,at+'.otherwise');
   }
  });
 };
 walk(plan.body,path+'.body');
 return Object.freeze(found.map(row=>Object.freeze(row)));
}

export function commerceTransactionFailureAtV1(path:string,plan:TransactionPlanV1,sourcePath:string,action:unknown):CommerceTransactionFailureActionV1|null {
 if(typeof sourcePath!=='string')return null;
 try{
  const matching=commerceTransactionFailureActionsV1(path,plan).filter(row=>
   (row.failure_kind==='guard'?sourcePath===row.failure_path:sourcePath===row.failure_path||sourcePath.startsWith(row.failure_path+'.'))&&
   dataDigest(row.action)===dataDigest(action));
  return matching.length===1?matching[0]!:null;
 }catch{return null;}
}
