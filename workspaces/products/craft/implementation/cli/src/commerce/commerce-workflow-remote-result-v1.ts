/** Executes one original protected Workflow service step and retains its result.
 * The result handle is process-local: a copied result or an arbitrary runtime
 * outcome cannot select a branch through this owner. Transport failures need
 * their own original transport receipt before they can enter this boundary.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import path from 'node:path';
import {types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowProtectedCallBindingV1,type CommerceWorkflowProtectedCallBindingV1,
 type CommerceWorkflowProtectedCallInspectionV1} from './commerce-workflow-protected-call-binding-v1.js';
import {assertCommerceWorkflowBranchSelectionOwnerV1,type CommerceWorkflowBranchSelectionOwnerV1,
 type CommerceWorkflowBranchDecisionV1} from './commerce-workflow-branch-selection-v1.js';
import {assertCommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityOwnerV1,
 type CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';
import {assertCommerceWorkflowSnapshotOwnerV1,assertCommerceWorkflowSnapshotOwnerBrandV1,type CommerceWorkflowSnapshotOwnerV1,
 type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1} from './commerce-service-storage-v1.js';
import {createCommerceGeneratedOperationRuntimeV1,type CommerceGeneratedOperationRuntimeV1}
 from './commerce-generated-operation-runtime-v1.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceSourceHandle,CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CommerceLocalPlanOwnerV1} from './commerce-local-plan-owner-v1.js';
import type {CommerceWorkflowExpressionProducersV1} from './commerce-workflow-expression-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';
import type {CommerceDemoPayDispatchOwnerV1} from './commerce-demopay-dispatch-v1.js';
import type {CommerceSourceQueryRuntimeV1} from './commerce-source-query-runtime-v1.js';

export class CommerceWorkflowRemoteResultErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowRemoteResultErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowRemoteResultErrorV1(code);};
const same=(left:CommerceWorkflowProtectedCallInspectionV1,right:CommerceWorkflowProtectedCallInspectionV1)=>
 left.workflow===right.workflow&&left.source_capture_sha256===right.source_capture_sha256&&
 left.store_id===right.store_id&&left.consumer_entry_id===right.consumer_entry_id&&
 left.occurrence_id===right.occurrence_id&&left.step_name===right.step_name&&
 left.entry_id===right.entry_id&&left.order_id===right.order_id&&
 left.worker_id===right.worker_id&&left.worker_epoch===right.worker_epoch&&
 left.progress_version===right.progress_version&&left.command_id===right.command_id&&
 left.request_fingerprint===right.request_fingerprint;

/** Copy only the native value ABI. This prevents a mutable result object from
 * being changed after the generated Operation returned but before branch use. */
function copyValue(value:unknown):CommerceNativeValue {
 let nodes=0;
 const copy=(input:unknown,depth:number):CommerceNativeValue=>{
  if(++nodes>65536||depth>64)bad('ResultBound');
  if(typeof input==='boolean'||typeof input==='string'||typeof input==='bigint')return input;
  if(!input||typeof input!=='object'||host.isProxy(input))bad('InvalidResult');
  if(Array.isArray(input)){
   if(Object.getPrototypeOf(input)!==Array.prototype||input.length>65536||Reflect.ownKeys(input).length!==input.length+1)
    bad('InvalidResult');
   const result:CommerceNativeValue[]=[];
   for(let i=0;i<input.length;i++){
    const descriptor=Object.getOwnPropertyDescriptor(input,String(i));
    if(!descriptor||!descriptor.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidResult');
    result.push(copy(descriptor!.value,depth+1));
   }
   return Object.freeze(result);
  }
  const object=input as object;
  if(![Object.prototype,null].includes(Object.getPrototypeOf(object)))bad('InvalidResult');
  const keys=Reflect.ownKeys(object),out:Record<string,CommerceNativeValue>=Object.create(null);
  if(keys.length>65536)bad('ResultBound');
  for(const key of keys){
   if(typeof key!=='string')bad('InvalidResult');
   const descriptor=Object.getOwnPropertyDescriptor(object,key);
   if(!descriptor||!descriptor.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidResult');
   out[key as string]=copy(descriptor!.value,depth+1);
  }
  return Object.freeze(out);
 };
 return copy(value,0);
}

export interface CommerceWorkflowRemoteResultHandleV1 {
 readonly kind:'original-protected-workflow-remote-result/v1-candidate';
}
export interface CommerceWorkflowRemoteResultInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly step_name:string;
 readonly target_entry_id:string;readonly order_id:string;readonly worker_id:string;
 readonly worker_epoch:bigint;readonly progress_version:bigint;readonly command_id:string;
 readonly request_fingerprint:string;readonly result_kind:'returned';
 readonly native_commits:number;readonly committed_same_service:boolean;
 readonly qualification:'original-protected-generated-operation-result;branch-data-only';
 readonly authority_effect:'none';
}
export type CommerceWorkflowRemoteExecutionV1=
 {readonly kind:'returned';readonly handle:CommerceWorkflowRemoteResultHandleV1}|
 {readonly kind:'not-completed';readonly runtime_outcome:'failed'|'rejected'|'indeterminate';
  readonly authority_effect:'none'|'committed'|'indeterminate'};
export interface CommerceWorkflowRemoteResultOwnerV1 {
 execute():Promise<CommerceWorkflowRemoteExecutionV1>;
 inspect(handle:CommerceWorkflowRemoteResultHandleV1):CommerceWorkflowRemoteResultInspectionV1;
 select(handle:CommerceWorkflowRemoteResultHandleV1,
  producers?:CommerceWorkflowExpressionProducersV1):CommerceWorkflowBranchDecisionV1;
 /** Recheck the result and the requested persisted snapshot. Exact retained
  * sources share the protected call's actual snapshot read in this call only;
  * distinct handles and same-service commits require an independent read. */
 recheckSnapshot(snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):
  ReturnType<CommerceWorkflowSnapshotOwnerV1['recheck']>;
 assertCurrent():void;dispose():void;
}
export type CommerceWorkflowRemoteExecutionPortsV1=Readonly<{
 demoPayDispatch?:CommerceDemoPayDispatchOwnerV1;
 externalQueries?:readonly CommerceSourceQueryRuntimeV1[];
}>;
const owners=new WeakSet<object>();
export function assertCommerceWorkflowRemoteResultOwnerV1(owner:CommerceWorkflowRemoteResultOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();
}

/** Own runtime construction so the protected call supplied to the generated
 * Operation is exactly the call whose completed result becomes a witness. */
export async function createCommerceWorkflowRemoteResultOwnerV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 plans:CommerceLocalPlanOwnerV1,selected:CommerceSelectedEntryAuthOwnerV1,
 targetStorage:CommerceServiceStorageOwnerV1,invocation:CommerceOperationInvocationHandle,
 directory:string,protectedCall:CommerceWorkflowProtectedCallBindingV1,
 branches:CommerceWorkflowBranchSelectionOwnerV1,
 identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
 snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
 ports?:CommerceWorkflowRemoteExecutionPortsV1,
):Promise<CommerceWorkflowRemoteResultOwnerV1> {
 const original=assertCommerceWorkflowProtectedCallBindingV1(protectedCall);
 // The branded protected call has just rechecked the exact retained causal
 // handles. Distinct matching handles still need independent owner checks.
 const exactCausalSources=protectedCall.hasExactCausalSources(identities,identity,snapshots,snapshot);
 assertCommerceWorkflowBranchSelectionOwnerV1(branches);
 if(!exactCausalSources){
  assertCommerceWorkflowStepIdentityOwnerV1(identities);
  assertCommerceWorkflowSnapshotOwnerV1(snapshots);
 }
 assertCommerceSelectedEntryAuthOwnerV1(selected);
 assertCommerceServiceStorageOwnerV1(targetStorage);
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)bad('InvalidDirectory');
 if(ports!==undefined){
  if(!ports||typeof ports!=='object'||host.isProxy(ports)||![Object.prototype,null].includes(Object.getPrototypeOf(ports)))
   bad('InvalidPorts');
  const keys=Reflect.ownKeys(ports),descriptors=Object.getOwnPropertyDescriptors(ports);
  if(keys.length>2||keys.some(key=>typeof key!=='string'||!['demoPayDispatch','externalQueries'].includes(key)||
    !descriptors[key as string]?.enumerable||!Object.hasOwn(descriptors[key as string]!,'value')))
   bad('InvalidPorts');
 }
 const target=targetStorage.inspect();
 // A protected call privately retains the exact identity and snapshot handles
 // used by its causal projection. Its recheck covers those same handles. Keep
 // independent checks when a caller supplies different, value-matching handles.
 const exactIdentity=exactCausalSources?identities.inspect(identity):null,
  exactSnapshot=exactCausalSources?snapshots.inspect(snapshot):null;
 const validate=(call:CommerceWorkflowProtectedCallInspectionV1,
  currentIdentity:ReturnType<CommerceWorkflowStepIdentityOwnerV1['recheck']>,
  currentSnapshot:ReturnType<CommerceWorkflowSnapshotOwnerV1['recheck']>,
  currentInvocation:ReturnType<CommerceSelectedEntryAuthOwnerV1['inspectInvocation']>,
  currentTarget:ReturnType<CommerceServiceStorageOwnerV1['inspect']>)=>{
  if(!same(call,original)||call.role!=='Operation'||
   call.source_capture_sha256!==currentIdentity.source_capture_sha256||
   call.source_capture_sha256!==currentSnapshot.source_capture_sha256||
   call.workflow!==currentIdentity.workflow||call.workflow!==currentSnapshot.workflow||
   call.store_id!==currentIdentity.store_id||call.store_id!==currentSnapshot.store_id||
   call.step_name!==currentIdentity.step_name||call.entry_id!==currentIdentity.target_entry_id||
   call.order_id!==currentIdentity.order_id||call.order_id!==currentSnapshot.order_id||
   call.worker_id!==currentIdentity.worker_id||call.worker_id!==currentSnapshot.worker_id||
   call.worker_epoch!==currentIdentity.worker_epoch||call.worker_epoch!==currentSnapshot.worker_epoch||
   call.progress_version!==currentIdentity.progress_version||call.progress_version!==currentSnapshot.progress_version||
   call.command_id!==currentIdentity.command_id||call.request_fingerprint!==currentIdentity.request_fingerprint||
   currentInvocation.entry!==call.entry_id||currentInvocation.operation!==call.target||
   currentInvocation.service!==currentTarget.service||currentInvocation.role!=='Operation'||
   currentInvocation.source_sha256!==call.source_capture_sha256||
   currentInvocation.actual_business_resource_owners_qualified!==true||
   currentTarget.source_capture_sha256!==call.source_capture_sha256||
   branches.plans().filter(row=>row.step_name===call.step_name).length!==1)bad('ForeignOwner');
 };
 const check=()=>{
  const call=protectedCall.recheck(),currentIdentity=exactCausalSources?exactIdentity!:identities.recheck(identity),
   currentSnapshot=exactCausalSources?exactSnapshot!:snapshots.recheck(snapshot),
   currentInvocation=selected.inspectInvocation(invocation),currentTarget=targetStorage.inspect();
  validate(call,currentIdentity,currentSnapshot,currentInvocation,currentTarget);
  return call;
 };
 const capturedSnapshot=(exactSnapshot??snapshots.inspect(snapshot)).value;
 let runtime:CommerceGeneratedOperationRuntimeV1;
 try{runtime=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,domain,baseline,
  plans,selected,targetStorage,invocation,directory,{workflowProtectedCall:protectedCall,
   ...(ports&&Object.hasOwn(ports,'demoPayDispatch')?{demoPayDispatch:ports.demoPayDispatch}:{}),
   ...(ports&&Object.hasOwn(ports,'externalQueries')?{externalQueries:ports.externalQueries}:{})});}
 catch(error){throw error;}
 try{
  const generated=runtime.inspect();
  if(generated.operation!==original.target||generated.service!==target.service||
   generated.source_capture_sha256!==original.source_capture_sha256)bad('ForeignOwner');
  check();
 }catch(error){runtime.dispose();throw error;}
 const handles=new WeakMap<object,{inspection:CommerceWorkflowRemoteResultInspectionV1;value:CommerceNativeValue;
  receipts:readonly object[]}>();
 const selectedBranches=new WeakMap<object,CommerceWorkflowBranchDecisionV1>();
 let disposed=false,executed=false,postCommitReceipts:readonly object[]=[];
 const current=():boolean=>{
  if(disposed)bad('DisposedOwner');
  if(postCommitReceipts.length){
   // The original Order/Progress snapshot is expected to change after the
   // same-service Operation commits. Retain its pre-effect value for branch
   // evaluation, but check the selected invocation, source and exact native
   // receipts without pretending the old snapshot is still current.
   const invocationView=selected.inspectInvocation(invocation),store=targetStorage.inspect(),generated=runtime.inspect();
   if(original.caller_service!==store.service||store.service!==target.service||
    store.store_id!==target.store_id||store.source_capture_sha256!==original.source_capture_sha256||
    invocationView.entry!==original.entry_id||invocationView.operation!==original.target||
    invocationView.service!==store.service||invocationView.role!=='Operation'||
    invocationView.source_sha256!==original.source_capture_sha256||
    generated.operation!==original.target||generated.service!==store.service||
    generated.source_capture_sha256!==original.source_capture_sha256||
    branches.plans().filter(row=>row.step_name===original.step_name).length!==1)
    bad('ForeignOwner');
   let originalOperationCommitted=false;
   for(const receipt of postCommitReceipts){
    const commit=targetStorage.inspectFreshGeneratedCommit(receipt);
    if(commit.service!==store.service||commit.store_id!==store.store_id||
     commit.source_capture_sha256!==original.source_capture_sha256)bad('ForeignOwner');
    if(commit.operation===original.target)originalOperationCommitted=true;
   }
   return originalOperationCommitted;
  }else{check();runtime.assertCurrent();return false;}
 };
 const owner:CommerceWorkflowRemoteResultOwnerV1=Object.freeze({
  async execute(){
   current();if(executed)bad('AlreadyExecuted');executed=true;
   const outcome=await runtime.run(invocation);
   const rawCommits=outcome.commits;
   if(!Array.isArray(rawCommits)||rawCommits.some(receipt=>!receipt||typeof receipt!=='object'))
    bad('InvalidResult');
   const receipts=Object.freeze([...(rawCommits as object[])]) as readonly object[];
   let committedSameService=false;
   if(original.caller_service===target.service&&receipts.length){
    postCommitReceipts=receipts;committedSameService=current();
   }else current();
   const kind=outcome.kind;
   if(kind!=='returned'){
    if(kind==='failed'||kind==='rejected'||kind==='indeterminate')
     return coreFreeze({kind:'not-completed' as const,
      runtime_outcome:(receipts.length||kind==='indeterminate'?'indeterminate':kind) as 'failed'|'rejected'|'indeterminate',
      authority_effect:receipts.length?'committed' as const:kind==='indeterminate'?'indeterminate' as const:'none' as const});
    bad('InvalidResult');
   }
   if(!Object.hasOwn(outcome,'value'))bad('InvalidResult');
   const value=copyValue(outcome.value),call=original;
   const handle:CommerceWorkflowRemoteResultHandleV1=Object.freeze({kind:'original-protected-workflow-remote-result/v1-candidate'});
   const inspection=coreFreeze({workflow:call.workflow,source_capture_sha256:call.source_capture_sha256,
    store_id:call.store_id,consumer_entry_id:call.consumer_entry_id,occurrence_id:call.occurrence_id,
    step_name:call.step_name,target_entry_id:call.entry_id,order_id:call.order_id,
    worker_id:call.worker_id,worker_epoch:call.worker_epoch,progress_version:call.progress_version,
    command_id:call.command_id,request_fingerprint:call.request_fingerprint,result_kind:'returned' as const,
    native_commits:receipts.length,committed_same_service:committedSameService,
    qualification:'original-protected-generated-operation-result;branch-data-only' as const,
    authority_effect:'none' as const});
   handles.set(handle,{inspection,value,receipts});return coreFreeze({kind:'returned' as const,handle});
  },
  inspect(handle:CommerceWorkflowRemoteResultHandleV1){current();const row=handle&&typeof handle==='object'?handles.get(handle):undefined;
   if(!row)bad('ForeignOwner');return row!.inspection;},
  select(handle:CommerceWorkflowRemoteResultHandleV1,producers?:CommerceWorkflowExpressionProducersV1){current();const row=handle&&typeof handle==='object'?handles.get(handle):undefined;
   if(!row)bad('ForeignOwner');
   // A result and the source branch table are immutable. Reuse a previously
   // selected data-only decision only after the original call and branch owner
   // have been rechecked. Caller-supplied expression producers are not cached.
   const cached=producers===undefined?selectedBranches.get(handle):undefined;
   if(cached)return cached;
   const remember=(decision:CommerceWorkflowBranchDecisionV1)=>{
    if(producers===undefined&&decision.outcome==='selected')selectedBranches.set(handle,decision);
    return decision;
   };
   if(row!.inspection.committed_same_service)return remember(branches.selectCaptured(original.step_name,
    {channel:'result',value:row!.value},capturedSnapshot,producers));
   if(exactCausalSources){
    // current() has just rechecked this protected call, including the exact
    // identity and snapshot handles retained by its causal projection. The
    // branch is data-only. Recheck after evaluation as selectCurrent() does;
    // if anything changed, use its stale-context path rather than the result.
    const decision=branches.selectCaptured(original.step_name,
     {channel:'result',value:row!.value},capturedSnapshot,producers);
    try{
     protectedCall.recheck();
     if(decision.workflow===original.workflow&&
      decision.source_capture_sha256===original.source_capture_sha256)return remember(decision);
    }catch{}
   }
   return remember(branches.selectCurrent(identities,identity,snapshots,snapshot,
    {channel:'result',value:row!.value},producers));},
  recheckSnapshot(requestedSnapshots:CommerceWorkflowSnapshotOwnerV1,requestedSnapshot:CommerceWorkflowSnapshotHandleV1){
   assertCommerceWorkflowSnapshotOwnerBrandV1(requestedSnapshots);
   current();
   // current() always rechecks the original protected call outside the
   // post-commit path. That call retains and rereads these exact sources.
   // This returns immutable data, never a cached freshness verdict.
   if(exactCausalSources&&postCommitReceipts.length===0&&
    requestedSnapshots===snapshots&&requestedSnapshot===snapshot)return exactSnapshot!;
   return requestedSnapshots.recheck(requestedSnapshot);
  },
  assertCurrent:current,
  dispose(){if(disposed)return;disposed=true;runtime.dispose();},
 });
 owners.add(owner);return owner;
}
