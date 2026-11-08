/** Derive the finite source recovery templates from checked Operation structure.
 * No Entity/binder naming convention, query implementation or recovery callback.
 * Data only: genuine source/disposition ownership stays with its actual owners.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC18/CONTEXT.md. */
import type {OperationControlStepV1,OperationActionV1,ValueTypeV1,TransactionPlanV1} from '../commerce/commerce-data-v1.js';
import type {CommerceEffectSourceInputV1} from './commerce-effectful-operation-source-v1.js';
import {dataDigest} from '../profile-engine/contracts.js';

type Read=Extract<OperationControlStepV1,{kind:'read'}>;
export type CommerceRecoveryKindV1='resolve-original-replay'|'reread-original-inbox'|'proven-rollback-reread-original-inbox-or-shipment';
export interface CommerceSourceRecoveryPlanV1 {
 readonly kind:CommerceRecoveryKindV1;
 readonly transaction_path:string;
 readonly handler_index:number;
 readonly handler_path:string;
 readonly requires:'original-proven-rollback';
 readonly guard_indices:readonly number[];
 readonly prefix_indices:readonly number[];
 readonly original_read_paths:readonly string[];
 readonly retained_bindings:readonly string[];
 readonly fallback:{readonly source_path:string;readonly action:OperationActionV1};
 readonly nested_transaction_paths:readonly string[];
 readonly source_sha256:string;
 readonly qualification:'source-recovery-construction-only;original-disposition-and-runtime-required';
}
const fail=(code:string,p:string):never=>{throw new TypeError(code+':'+p);};
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;};
function has(v:unknown,predicate:(v:Record<string,unknown>)=>boolean):boolean {
 let nodes=0;const visit=(v:unknown,depth=0):boolean=>{if(!v||typeof v!=='object')return false;if(++nodes>65536||depth>128)throw new TypeError('RecoverySourceBound');if(!Array.isArray(v)&&predicate(v as Record<string,unknown>))return true;return Object.values(v).some(x=>visit(x,depth+1));};return visit(v);
}
const native=(v:unknown)=>has(v,v=>v.op==='native_observation');
const underlying=(t:ValueTypeV1):ValueTypeV1=>t.kind==='optional'?t.element:t;
const sameType=(a:ValueTypeV1,b:ValueTypeV1)=>dataDigest(underlying(a))===dataDigest(underlying(b));
const sourceReturn=(a:OperationActionV1)=>a.kind!=='invoke-return'&&!native(a);

/** Closed selected-cell recovery. Unsupported/ambiguous structure rejects during
 * generation; it never acquires a caller-supplied implementation. */
export function deriveCommerceSourceRecoveryPlansV1(input:CommerceEffectSourceInputV1):readonly CommerceSourceRecoveryPlanV1[] {
 const result:CommerceSourceRecoveryPlanV1[]=[],body=input.effect_plan.body;
 for(const original of input.transactions){
  const handlers=original.plan.handlers.map((h,i)=>({h,i})).filter(x=>x.h.recovery!==null);if(!handlers.length)continue;
  const location=/^\$\.body\[(\d+)\]\.transaction$/.exec(original.path)??fail('UnsupportedRecoveryScope',original.path);
  const index=Number(location[1]),step=body[index];if(!step||!('transaction'in step)||step.transaction===null||dataDigest(step.transaction)!==dataDigest(original.plan))fail('ForeignRecoveryTransaction',original.path);
  const prior=body.slice(0,index).map((step,i)=>({step,i})),reads=prior.filter((r):r is {step:Read;i:number}=>r.step.kind==='read'&&r.step.entity!==null&&r.step.key!==null);
  const receiptCreates=original.plan.body.filter(s=>s.kind==='mutation'&&s.operation==='create'&&s.fields.some(f=>sameType(f.value.result,input.effect_plan.result)));
  for(const {h,i:handlerIndex}of handlers){
   if(h.requires!=='original-proven-rollback')fail('UnresolvedRecoveryRequiresDistinctNativeProtocol',original.path);
   const kind=h.recovery!;
   if(!['resolve-original-replay','reread-original-inbox','proven-rollback-reread-original-inbox-or-shipment'].includes(kind))fail('UnknownRecoveryTemplate',original.path);
   const absence=original.plan.body.filter(s=>s.kind==='require-absent');
   const anchors=reads.filter(r=>receiptCreates.some(s=>s.kind==='mutation'&&s.target===r.step.entity)&&(kind!=='resolve-original-replay'||absence.some(s=>s.kind==='require-absent'&&s.entity===r.step.entity&&dataDigest(s.key)===dataDigest(r.step.key))));
   if(anchors.length!==1)fail('AmbiguousRecoveryReceiptRead',original.path);const anchor=anchors[0]!,guardIndices:number[]=[],prefix:number[]=[anchor.i],retained:string[]=[],readPaths=['$.body['+anchor.i+']'],nested:string[]=[];
   if(kind==='resolve-original-replay'&&!prior.some(r=>r.step.kind==='preflight'))fail('MissingOriginalReplayContract',original.path);
   for(const p of prior.filter(p=>p.i<anchor.i&&(p.step.kind==='guard'||p.step.kind==='preflight'))){if(native(p.step))fail('RecoveryGuardWouldAcquireNewObservation',original.path);guardIndices.push(p.i);}
   const candidates=reads.filter(r=>r.i>anchor.i&&original.plan.body.some(s=>s.kind==='mutation'&&s.operation==='create'&&s.target===r.step.entity));
   const secondary=kind==='proven-rollback-reread-original-inbox-or-shipment'?(candidates.length===1?candidates[0]:fail('AmbiguousRecoveryOriginalRow',original.path)):null;
   const referenceNames=new Set([anchor.step.name,...(secondary?[secondary.step.name]:[])]);
   const safeAction=(a:OperationActionV1)=>sourceReturn(a)&&(a.kind!=='return'||has(a.value,v=>v.op==='var'&&referenceNames.has(String(v.name))));
   const safeInboxTransaction=(t:TransactionPlanV1,p:string)=>{
    if(t.participants.length!==1||t.participants[0]!==anchor.step.entity||t.body.some(s=>s.kind!=='mutation'||s.operation!=='create'||s.target!==anchor.step.entity)||native(t.body)||!t.handlers.some(h=>h.recovery==='reread-original-inbox'&&h.requires==='original-proven-rollback'))return false;
    nested.push(p);return true;
   };
   let terminal=false;
   for(let j=anchor.i+1;j<index;j++){
    const s=body[j]!,p='$.body['+j+']';
    if(s.kind==='read'){
     if(secondary&&j===secondary.i){prefix.push(j);readPaths.push(p);continue;}break;
    }
    if(s.kind==='let'&&kind==='resolve-original-replay'&&native(s.value)||s.kind==='count'&&kind==='resolve-original-replay'){
     retained.push(s.name);continue;
    }
    if(native(s))break;
    if(s.kind==='let'){prefix.push(j);continue;}
    if(s.kind==='guard'&&sourceReturn(s.on_false)){prefix.push(j);continue;}
    if(s.kind==='case'&&s.branches.every(b=>safeAction(b.action))){prefix.push(j);terminal||=s.branches.some(b=>b.action.kind==='return');continue;}
    if(s.kind==='present'&&(!s.on_false||sourceReturn(s.on_false))&&(!s.action||safeAction(s.action))&&(!s.transaction||secondary&&safeInboxTransaction(s.transaction,p+'.transaction'))){prefix.push(j);terminal||=s.action?.kind==='return';continue;}
    break;
   }
   if(!terminal||secondary&&!prefix.includes(secondary.i))fail('IncompleteOriginalRecoveryPrefix',original.path);
   const fallback=anchor.step.on_unavailable;if(fallback.kind!=='fail'&&fallback.kind!=='reject')fail('RecoveryFallbackWouldDispatchWork',original.path);
   const plan={kind,transaction_path:original.path,handler_index:handlerIndex,handler_path:original.path+'.handlers['+handlerIndex+']',requires:'original-proven-rollback' as const,guard_indices:guardIndices,prefix_indices:prefix,original_read_paths:readPaths,retained_bindings:retained,fallback:{source_path:'$.body['+anchor.i+'].on_unavailable',action:fallback},nested_transaction_paths:nested,source_sha256:input.source_capture_sha256,qualification:'source-recovery-construction-only;original-disposition-and-runtime-required' as const};
   result.push(freeze(plan));
  }
 }
 // Every nested write is an actual original source transaction, and every
 // recovery recursion must terminate before fresh work rather than retry it.
 const visit=(p:string,active:Set<string>)=>{if(active.has(p))fail('RecursiveSourceRecovery',p);const next=new Set(active);next.add(p);for(const row of result.filter(r=>r.transaction_path===p))for(const child of row.nested_transaction_paths){if(!input.transactions.some(t=>t.path===child))fail('ForeignNestedRecoveryTransaction',child);visit(child,next);}};
 for(const row of result)visit(row.transaction_path,new Set());return freeze(result);
}
