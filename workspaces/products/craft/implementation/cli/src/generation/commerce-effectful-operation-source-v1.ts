/** Additive native transaction/outcome source construction. Original runtime
 * handles and proof owners arise at the later SDK/native join, never here.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC18/CONTEXT.md. */
import {dataDigest} from '../profile-engine/contracts.js';
import type {EffectPlanV1,TransactionPlanV1,OperationActionV1} from '../commerce/commerce-data-v1.js';
export interface CommerceEffectTransactionSourceV1 {readonly path:string;readonly plan:TransactionPlanV1}
export interface CommerceEffectSourceInputV1 {readonly operation:string;readonly source_capture_sha256:string;readonly effect_plan:EffectPlanV1;readonly transactions:readonly CommerceEffectTransactionSourceV1[]}
export interface CommerceEffectSourceBundleV1 {readonly files:readonly {readonly path:string;readonly text:string}[];readonly manifest:Readonly<Record<string,unknown>>}
const json=(v:unknown)=>JSON.stringify(v),freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;};
/** Data-only source mapping. It never treats an outcome tag as original proof. */
export function commerceTransactionOutcomeMappingV1(plan:TransactionPlanV1){
 const channel=(name:string,proof:'rollback'|'uncertain')=>{const handler=plan.handlers.find(h=>h.channel===name),fallback=plan.defaults.find(d=>d.channel===name),rollback=plan.handlers.find(h=>h.channel==='on-proven-rollback'),action:OperationActionV1|null=handler?.action??(fallback?.fallback==='explicit-proven-rollback-handler-then-fixed-default'?rollback?.action??fallback.action:fallback?.action)??null;
  if(handler&&handler.requires!==(proof==='rollback'?'original-proven-rollback':'original-unresolved-commit'))throw Error('OriginalDispositionMismatch');
  return {channel:name,requires:proof==='rollback'?'original-proven-rollback':'original-unresolved-commit',action,recovery:handler?.recovery??null,do_not_ack:handler?.do_not_ack??false,retain_original:handler?.retain_original??false};};
 return freeze({committed:{requires:'original-commit-receipt',aliases:'escape-only-after-original-commit'},'version-conflict':channel('on-version-conflict','rollback'),'unique-conflict':channel('on-unique-conflict','rollback'),'rolled-back':channel('on-proven-rollback','rollback'),indeterminate:channel('on-unknown-commit','uncertain'),'unavailable-before-start':{requires:'original-no-start-observation',action:{kind:'fail',code:'transaction-unavailable'},recovery:null,retain_original:true,do_not_ack:true}});
}
/** Emits explicit native calls and source outcome handlers. Recovery is an
 * unresolved typed requirement until generated recovery source is joined;
 * no user business/recovery callback is accepted to fill that missing stage. */
export function renderCommerceEffectfulTransactionSourcesV1(input:CommerceEffectSourceInputV1):CommerceEffectSourceBundleV1 {
 const mappings=input.transactions.map(t=>({path:t.path,name:t.plan.name,plan:t.plan,mapping:commerceTransactionOutcomeMappingV1(t.plan)}));
 const contract=`// Generated source construction contracts, not runtime handle producers.
export type NativeValue=boolean|string|bigint|readonly NativeValue[]|Readonly<{[key:string]:NativeValue}>;
declare const original:unique symbol;
export interface Invocation {readonly [original]:'private-generated-operation-invocation'}
export interface Store {readonly [original]:'service-owned-store'}
export interface Transaction {readonly [original]:'original-generated-transaction'}
export interface Commit {readonly [original]:'actual-local-commit-receipt'}
export interface Rollback {readonly [original]:'actual-proven-local-rollback'}
export interface Unknown {readonly [original]:'indeterminate-local-transaction'}
export type NativeOutcome={readonly kind:'committed';readonly receipt:Commit;readonly result:NativeValue}|{readonly kind:'version-conflict'|'unique-conflict'|'rolled-back';readonly rollback:Rollback}|{readonly kind:'indeterminate';readonly ticket:Unknown}|{readonly kind:'unavailable-before-start'};
export interface NativeStore {applyCommerceTransaction(invocation:Invocation,store:Store,plan:Transaction,bindings:Readonly<Record<string,NativeValue>>):Promise<NativeOutcome>}
// These are prospective SDK assembly obligations. There is no constructor or
// registration API in this generated component. EC19 must supply actual owners.
export interface OriginalDispositionOwner {
 assertInvocation(invocation:Invocation,source:string,operation:string):void;
 assertOutcome(invocation:Invocation,sourcePath:string,outcome:NativeOutcome):void;
}
export type SourceAction={readonly kind:'reject'|'fail';readonly code:string}|Readonly<{kind:'return'|'invoke-return';[key:string]:unknown}>;
export type SourceSettlement={readonly kind:'committed';readonly receipt:Commit;readonly aliases:NativeValue}|{readonly kind:'rejected'|'failed';readonly code:string;readonly rollback:Rollback|null}|{readonly kind:'indeterminate';readonly ticket:Unknown;readonly source_action:SourceAction|null;readonly retain_original:boolean;readonly do_not_ack:boolean}|{readonly kind:'source-return-required';readonly source_action:SourceAction;readonly source_action_path:string|null;readonly rollback:Rollback}|{readonly kind:'generated-recovery-required';readonly recovery:string;readonly rollback:Rollback;readonly source_path:string};
`;
 const text=`// Generated native transaction and typed source outcome adapter.
// Qualification: source construction only; no original runtime/native admission.
import type {NativeValue,Invocation,Store,Transaction,NativeStore,NativeOutcome,OriginalDispositionOwner,SourceSettlement,SourceAction} from './native-effect-contract.js';
const source=${json(input.source_capture_sha256)},operation=${json(input.operation)};
const seal=(value:any):any=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){for(const child of Object.values(value))seal(child);Object.freeze(value);}return value;};
export const transactions=seal(JSON.parse(${json(json(mappings))})) as readonly {path:string;name:string;plan:any;mapping:any}[];
export const effectPlan=seal(JSON.parse(${json(json(input.effect_plan))}));
export const qualification='generated-native-transaction-outcome-component-only;outer-operation-and-recovery-source-not-established' as const;
export async function executeTransaction(path:string,invocation:Invocation,store:Store,transaction:Transaction,bindings:Readonly<Record<string,NativeValue>>,native:NativeStore,proof:OriginalDispositionOwner):Promise<SourceSettlement>{
 const row=transactions.find(t=>t.path===path);if(!row)throw new TypeError('UnknownOriginalTransaction');
 proof.assertInvocation(invocation,source,operation);
 const outcome=await native.applyCommerceTransaction(invocation,store,transaction,bindings);
 proof.assertInvocation(invocation,source,operation);
 proof.assertOutcome(invocation,path,outcome);
 if(outcome.kind==='committed')return Object.freeze({kind:'committed',receipt:outcome.receipt,aliases:outcome.result});
 if(outcome.kind==='unavailable-before-start')return Object.freeze({kind:'failed',code:'transaction-unavailable',rollback:null});
 if(outcome.kind==='indeterminate'){const mapping=row.mapping.indeterminate;return Object.freeze({kind:'indeterminate',ticket:outcome.ticket,source_action:mapping.action as SourceAction|null,retain_original:mapping.retain_original,do_not_ack:mapping.do_not_ack});}
 const mapping=row.mapping[outcome.kind];
 if(mapping.recovery)return Object.freeze({kind:'generated-recovery-required',recovery:mapping.recovery,rollback:outcome.rollback,source_path:path});
 if(!mapping.action)throw new TypeError('MissingSourceOutcomeMapping');
 const action=mapping.action as SourceAction;
 if(action.kind==='return'||action.kind==='invoke-return')return Object.freeze({kind:'source-return-required',source_action:action,source_action_path:null,rollback:outcome.rollback});
 return Object.freeze({kind:action.kind==='reject'?'rejected':'failed',code:action.code as string,rollback:outcome.rollback});
}
export function assertWholeOperationGenerationAvailable():never {throw new TypeError('OuterOperationAndRecoveryGenerationNotYetJoined');}
`;
 const files=freeze([{path:'native-effect-contract.ts',text:contract},{path:'effectful-transactions.ts',text}]);
 return freeze({files,manifest:{schema_version:'craft.commerce-effect-source/v1-candidate',operation:input.operation,source_capture_sha256:input.source_capture_sha256,effect_plan_sha256:dataDigest(input.effect_plan),transactions:mappings.map(t=>({path:t.path,name:t.name,plan_sha256:dataDigest(t.plan),mapping_sha256:dataDigest(t.mapping),generated_recovery_required:Object.values(t.mapping).some(m=>'recovery'in m&&m.recovery!==null)})),native_signature:'ServiceSqliteNativeV1.applyCommerceTransaction;source-shape-only;actual-owner-and-ABI-join-required',runtime_handles_created:false,whole_operation_generation:false,qualification:'actual-native-transaction-adapter-source-only;not-complete-async-operation-or-native-basis',authority_effect:'none'}});
}
