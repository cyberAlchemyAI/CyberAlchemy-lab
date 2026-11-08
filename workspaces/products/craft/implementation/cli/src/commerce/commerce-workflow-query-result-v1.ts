/** An original protected Workflow Query result and its source-selected branch.
 * The result handle is process-local. A caller cannot substitute a result for
 * the selected service Query or use its data as effect authority.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {pinCoreImplementation} from './commerce-core-physical.js';
import {isDeepStrictEqual} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {evaluateCommerceFlowDataV1} from './commerce-flow-expression-data-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from './commerce-core-semantic-owner.js';
import {assertCommerceWorkflowProtectedCallBindingV1,type CommerceWorkflowProtectedCallBindingV1}
 from './commerce-workflow-protected-call-binding-v1.js';
import {assertCommerceWorkflowBranchSelectionOwnerV1,type CommerceWorkflowBranchSelectionOwnerV1,
 type CommerceWorkflowBranchDecisionV1} from './commerce-workflow-branch-selection-v1.js';
import {assertCommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityOwnerV1,
 type CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';
import {assertCommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotOwnerV1,
 type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1}
 from './commerce-selected-entry-auth-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from './commerce-service-storage-v1.js';
import {createCommerceSourceQueryOutputCodecV1} from './commerce-source-query-output-codec-v1.js';
import {createCommerceSourceQueryRuntimeV1} from './commerce-source-query-runtime-v1.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceSourceHandle,CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle}
 from './commerce-computation-domain.js';
import type {CommerceLocalPlanOwnerV1} from './commerce-local-plan-owner-v1.js';
import type {CommerceWorkflowExpressionProducersV1} from './commerce-workflow-expression-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';
import type {ReadPlanV1} from './commerce-data-v1.js';

export class CommerceWorkflowQueryResultErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowQueryResultErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowQueryResultErrorV1(code);};
const pin=pinCoreImplementation(import.meta.url,[]);
export interface CommerceWorkflowQueryResultHandleV1 {
 readonly kind:'original-protected-workflow-query-result/v1-candidate';
}
export interface CommerceWorkflowQueryResultInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;
 readonly step_name:string;readonly target_entry_id:string;readonly target_query:string;
 readonly order_id:string;readonly worker_id:string;readonly worker_epoch:bigint;
 readonly progress_version:bigint;readonly command_id:string;readonly request_fingerprint:string;
 readonly result_kind:'returned';readonly qualification:'original-protected-source-query-result;branch-data-only';
 readonly authority_effect:'none';
}
export type CommerceWorkflowQueryExecutionV1=
 Readonly<{kind:'returned';handle:CommerceWorkflowQueryResultHandleV1}>|
 Readonly<{kind:'not-completed';query_outcome:'failed'|'rejected';authority_effect:'none'}>;
export interface CommerceWorkflowQueryResultOwnerV1 {
 execute():CommerceWorkflowQueryExecutionV1;
 inspect(handle:CommerceWorkflowQueryResultHandleV1):CommerceWorkflowQueryResultInspectionV1;
 select(handle:CommerceWorkflowQueryResultHandleV1,
  producers?:CommerceWorkflowExpressionProducersV1):CommerceWorkflowBranchDecisionV1;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowQueryResultOwnerV1(owner:CommerceWorkflowQueryResultOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();
}

export async function createCommerceWorkflowQueryResultOwnerV1(
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 plans:CommerceLocalPlanOwnerV1,selected:CommerceSelectedEntryAuthOwnerV1,
 targetStorage:CommerceServiceStorageOwnerV1,invocation:CommerceOperationInvocationHandle,
 protectedCall:CommerceWorkflowProtectedCallBindingV1,
 branches:CommerceWorkflowBranchSelectionOwnerV1,
 identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
 snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
):Promise<CommerceWorkflowQueryResultOwnerV1> {
 pin.assertCurrent();assertCoreCommerceSemanticOwner(semantics);
 assertCommerceWorkflowProtectedCallBindingV1(protectedCall);
 assertCommerceWorkflowBranchSelectionOwnerV1(branches);
 assertCommerceWorkflowStepIdentityOwnerV1(identities);
 assertCommerceWorkflowSnapshotOwnerV1(snapshots);
 assertCommerceSelectedEntryAuthOwnerV1(selected);
 assertCommerceServiceStorageOwnerV1(targetStorage);
 const original=protectedCall.recheck(),target=targetStorage.inspect(),
  model=semantics.inspect(semantic),schema=domain.inspect(baseline).contract.values,
  wrapper=model.reads.find(row=>row.query.module+'.'+row.query.name===original.target),
  selectedTarget=wrapper?.kind==='delegated'?wrapper.target:original.target,
  targetRead=model.reads.find(row=>row.query.module+'.'+row.query.name===selectedTarget);
 if(!wrapper||!targetRead)throw new CommerceWorkflowQueryResultErrorV1('ForeignOwner');
 if(original.role!=='Query'||target.source_capture_sha256!==original.source_capture_sha256||
  model.source_capture_sha256!==original.source_capture_sha256||
  targetRead.kind!=='local'||targetRead.service!==target.service||
  wrapper.service!==target.service||wrapper.contexts.length!==0||
  !isDeepStrictEqual(wrapper.output,targetRead.output)||
  wrapper.kind==='delegated'&&(wrapper.forwarded_contexts.length!==0||
   wrapper.arguments.length!==targetRead.parameters.length||
   new Set(wrapper.arguments.map(row=>row.parameter)).size!==targetRead.parameters.length||
   targetRead.parameters.some(parameter=>!wrapper.arguments.some(row=>row.parameter===parameter.name))))
  bad('ForeignOwner');
 const delegated:Extract<ReadPlanV1,{kind:'delegated'}>|null=wrapper.kind==='delegated'?wrapper:null;
 const evaluateDelegation=()=>{
  if(!delegated)return null;
  const authorization=selected.inspectInvocation(invocation),input=selected.parameters(invocation),
   expected=delegated.parameters.map(parameter=>parameter.name);
  if(authorization.entry!==original.entry_id||authorization.operation!==original.target||
   Object.keys(input).length!==expected.length||expected.some(name=>!Object.hasOwn(input,name)))bad('ForeignOwner');
  const forwarded:Record<string,CommerceNativeValue>=Object.create(null);let fuel=0;
  for(const [index,arg] of delegated.arguments.entries())forwarded[arg.parameter]=
   evaluateCommerceFlowDataV1(arg.value.expression,'$.arguments['+index+'].value.expression',input,{
    charge(){if(++fuel>domain.inspect(baseline).contract.limits.fuel)bad('ResourceLimit');},
    pure(){return bad('UnsupportedDelegation');},native(){return bad('UnsupportedDelegation');},
    context(){return bad('UnsupportedDelegation');},
    isNullaryEnum(name){const declaration=schema.enums.find(row=>row.name===name);
     if(!declaration)bad('UnknownReference');return declaration!.variants.every(row=>Object.keys(row.fields).length===0);},
   });
  semantics.assertCurrent(semantic);protectedCall.recheck();selected.inspectInvocation(invocation);
  return coreFreeze(forwarded);
 };
 const check=()=>{
  pin.assertCurrent();semantics.assertCurrent(semantic);const call=protectedCall.recheck(),step=identities.recheck(identity),
   witness=snapshots.recheck(snapshot),authorized=selected.inspectInvocation(invocation),store=targetStorage.inspect();
  if(call.role!=='Query'||call.workflow!==original.workflow||
   call.source_capture_sha256!==original.source_capture_sha256||call.store_id!==original.store_id||
   call.consumer_entry_id!==original.consumer_entry_id||call.occurrence_id!==original.occurrence_id||
   call.step_name!==original.step_name||call.entry_id!==original.entry_id||
   call.order_id!==original.order_id||call.worker_id!==original.worker_id||
   call.worker_epoch!==original.worker_epoch||call.progress_version!==original.progress_version||
   call.command_id!==original.command_id||call.request_fingerprint!==original.request_fingerprint||
   call.source_capture_sha256!==step.source_capture_sha256||call.source_capture_sha256!==witness.source_capture_sha256||
   call.workflow!==step.workflow||call.workflow!==witness.workflow||
   call.store_id!==step.store_id||call.store_id!==witness.store_id||
   call.step_name!==step.step_name||call.entry_id!==step.target_entry_id||
   call.order_id!==step.order_id||call.order_id!==witness.order_id||
   call.worker_id!==step.worker_id||call.worker_id!==witness.worker_id||
   call.worker_epoch!==step.worker_epoch||call.worker_epoch!==witness.worker_epoch||
   call.progress_version!==step.progress_version||call.progress_version!==witness.progress_version||
   call.command_id!==step.command_id||call.request_fingerprint!==step.request_fingerprint||
   authorized.entry!==call.entry_id||authorized.operation!==call.target||authorized.role!=='Query'||
   authorized.service!==store.service||authorized.source_sha256!==call.source_capture_sha256||
   authorized.actual_business_resource_owners_qualified!==true||
   store.source_capture_sha256!==call.source_capture_sha256||store.service!==target.service||
   branches.plans().filter(row=>row.step_name===call.step_name).length!==1)bad('ForeignOwner');
  return call;
 };
 check();
 const read=plans.bindRead(selectedTarget);
 let codec:Awaited<ReturnType<typeof createCommerceSourceQueryOutputCodecV1>>|undefined;
 let query:ReturnType<typeof createCommerceSourceQueryRuntimeV1>;
 try{
  codec=await createCommerceSourceQueryOutputCodecV1(stage,source,domain,baseline,plans,read);
  query=createCommerceSourceQueryRuntimeV1(stage,source,plans,read,domain,baseline,targetStorage,codec);
  if(query.query!==selectedTarget)bad('ForeignOwner');check();
 }catch(error){try{codec?.dispose();}finally{plans.disposeRead(read);}throw error;}
 if(!codec)bad('InvalidContract');
 const outputCodec=codec;
 const results=new WeakMap<object,{inspection:CommerceWorkflowQueryResultInspectionV1;value:unknown}>();
 let disposed=false,executed=false;
 const current=()=>{if(disposed)bad('DisposedOwner');check();query.assertCurrent();};
 const owner:CommerceWorkflowQueryResultOwnerV1=Object.freeze({
  execute(){current();if(executed)bad('AlreadyExecuted');executed=true;
   const arguments_=evaluateDelegation();
   const outcome=arguments_?query.execute(arguments_):query.executeSelectedService(selected,invocation);
   current();if(outcome.kind!=='returned')return coreFreeze({kind:'not-completed' as const,
    query_outcome:outcome.kind,authority_effect:'none' as const});
   const call=check(),handle:CommerceWorkflowQueryResultHandleV1=
    Object.freeze({kind:'original-protected-workflow-query-result/v1-candidate'});
   results.set(handle,{inspection:coreFreeze({workflow:call.workflow,
    source_capture_sha256:call.source_capture_sha256,store_id:call.store_id,
    consumer_entry_id:call.consumer_entry_id,occurrence_id:call.occurrence_id,
    step_name:call.step_name,target_entry_id:call.entry_id,target_query:call.target,
    order_id:call.order_id,worker_id:call.worker_id,worker_epoch:call.worker_epoch,
    progress_version:call.progress_version,command_id:call.command_id,
    request_fingerprint:call.request_fingerprint,
    result_kind:'returned' as const,
    qualification:'original-protected-source-query-result;branch-data-only' as const,
    authority_effect:'none' as const}),value:outputCodec.copy(outcome.value)});
   return coreFreeze({kind:'returned' as const,handle});
  },
  inspect(handle:CommerceWorkflowQueryResultHandleV1){current();const row=handle&&typeof handle==='object'?results.get(handle):undefined;
   if(!row)bad('ForeignOwner');return row!.inspection;},
  select(handle:CommerceWorkflowQueryResultHandleV1,producers?:CommerceWorkflowExpressionProducersV1){current();const row=handle&&typeof handle==='object'?results.get(handle):undefined;
   if(!row)bad('ForeignOwner');return branches.selectCurrent(identities,identity,snapshots,snapshot,
    {channel:'result',value:row!.value},producers);},
  assertCurrent:current,
  dispose(){if(disposed)return;disposed=true;try{query.dispose();}finally{try{outputCodec.dispose();}finally{plans.disposeRead(read);}}},
 });
 owners.add(owner);return owner;
}
