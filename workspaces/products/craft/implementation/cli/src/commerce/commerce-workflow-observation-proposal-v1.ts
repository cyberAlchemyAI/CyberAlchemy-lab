/** Source-bound, inert proposal for one original worker observation.
 * A completed protected step and current snapshot are required to mint its
 * handle. Fresh Auth, the worker Entry invocation and the atomic commit remain
 * separate original owners.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from './commerce-core-semantic-owner.js';
import {assertCommerceWorkflowRemoteResultOwnerV1,type CommerceWorkflowRemoteResultOwnerV1,
 type CommerceWorkflowRemoteResultHandleV1} from './commerce-workflow-remote-result-v1.js';
import {assertCommerceWorkflowQueryResultOwnerV1,type CommerceWorkflowQueryResultOwnerV1,
 type CommerceWorkflowQueryResultHandleV1} from './commerce-workflow-query-result-v1.js';
import {assertCommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotOwnerV1,
 type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,type CommerceWorkerContextV1}
 from './commerce-worker-context-v1.js';
import type {CoreExpression} from './commerce-core-expression.js';
import type {CoreWorkflowSource} from './commerce-core-flow-workflow.js';
import type {EntryContractV1} from './commerce-data-v1.js';

export class CommerceWorkflowObservationProposalErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowObservationProposalErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowObservationProposalErrorV1(code);};
const codePin=pinCoreImplementation(import.meta.url,[]);
const plain=(value:unknown):value is Record<string,unknown>=>!!value&&typeof value==='object'&&
 !Array.isArray(value)&&!host.isProxy(value)&&[Object.prototype,null].includes(Object.getPrototypeOf(value));
const field=(value:unknown,name:string):unknown=>{
 if(!plain(value))bad('InvalidSnapshot');
 const descriptor=Object.getOwnPropertyDescriptor(value,name);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidSnapshot');
 return descriptor!.value;
};
const pathOf=(expression:CoreExpression):readonly string[]=>{
 if(expression.kind==='name')return expression.name.split('.');
 if(expression.kind==='field')return [...pathOf(expression.value),expression.field];
 return bad('UnsupportedObservationExpression');
};
const samePath=(actual:readonly string[],expected:readonly string[])=>isDeepStrictEqual(actual,expected);

/** Exact source ABI for the observation Entry. This derives only data; neither
 * the plan nor a copied proposal is accepted as an invocation authority. */
export function inspectCommerceWorkflowObservationPlanV1(workflow:CoreWorkflowSource,
 entry:EntryContractV1):Readonly<{entry_id:string;target:string;owner_service:string;
 snapshot_binding:string;parameters:readonly ['orderId','expectedOrderVersion','expectedProgressVersion','observation'];
 causal_binding:string;causal_fields:readonly ['progress'];authority_effect:'none'}> {
 codePin.assertCurrent();
 const snapshots=workflow.drivers.filter(driver=>driver.kind==='snapshot'),
  observations=workflow.drivers.filter(driver=>driver.kind==='observation');
 if(snapshots.length!==1||observations.length!==1||!snapshots[0]!.call.binding)
  bad('InvalidContract');
 const snapshotBinding=snapshots[0]!.call.binding!,driver=observations[0]!,call=driver.call,
  names=['orderId','expectedOrderVersion','expectedProgressVersion','observation'] as const,
  paths=[[snapshotBinding,'order','id'],[snapshotBinding,'order','version'],
   [snapshotBinding,'progress','version'],['step','observation']] as const;
 if(call.role!=='Operation'||call.entry!==entry.id||
  call.target!==entry.invokes.module+'.'+entry.invokes.name||
  entry.service!==workflow.owner||entry.interaction!=='request-response'||
  call.arguments.length!==names.length||entry.parameters.length!==names.length||
  call.arguments.some((argument,index)=>argument.parameter!==names[index]||
   !samePath(pathOf(argument.value.source),paths[index]!))||
  entry.parameters.some((parameter,index)=>parameter.name!==names[index])||
  entry.access.principal_kind!=='service'||entry.access.caller!==workflow.owner||
  entry.access.worker_lifetime!=='requires-original-local-worker-owner'||
  entry.access.resource_phase!=='causal-before-invocation'||
  entry.access.matching_replay_resource_check!=='same-causal-input'||
  !entry.access.resource_condition||entry.access.resource_bindings.length!==1)
  bad('InvalidContract');
 const causal=entry.access.resource_bindings[0]!;
 if(causal.origin.kind!=='worker-observation'||causal.origin.declaration!==workflow.durable_state||
  causal.abi!=='craft.commerce-causal-call/v1-candidate'||
  causal.selector.split('/').at(-1)!=='original-worker-observation'||
  causal.required_fields.length!==1||causal.required_fields[0]!=='progress')
  bad('UnsupportedObservationCausalBinding');
 return coreFreeze({entry_id:entry.id,target:call.target,owner_service:workflow.owner,
  snapshot_binding:snapshotBinding,parameters:names,causal_binding:causal.name,
  causal_fields:['progress'] as const,authority_effect:'none' as const});
}

export interface CommerceWorkflowObservationProposalHandleV1 {
 readonly kind:'original-workflow-observation-proposal/v1-candidate';
}
export interface CommerceWorkflowObservationProposalInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly step_name:string;
 readonly remote_entry_id:string;readonly entry_id:string;readonly target:string;
 readonly order_id:string;readonly worker_id:string;readonly worker_epoch:bigint;
 readonly command_id:string;readonly request_fingerprint:string;
 readonly progress_version:bigint;readonly order_version:bigint;
 readonly input:Readonly<{orderId:string;expectedOrderVersion:bigint;
  expectedProgressVersion:bigint;observation:unknown}>;
 readonly causal_projection:Readonly<{progress:unknown}>;
 readonly next_action:unknown;
 readonly qualification:'original-result-selected-observation-proposal;fresh-auth-and-atomic-commit-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowObservationProposalOwnerV1 {
 propose():CommerceWorkflowObservationProposalHandleV1;
 inspect(handle:CommerceWorkflowObservationProposalHandleV1):CommerceWorkflowObservationProposalInspectionV1;
 recheck(handle:CommerceWorkflowObservationProposalHandleV1):CommerceWorkflowObservationProposalInspectionV1;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowObservationProposalOwnerV1(owner:CommerceWorkflowObservationProposalOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();
}

/** The result owner executes the original protected call and selects its
 * branch. This owner never accepts a caller-provided branch or observation. */
export function createCommerceWorkflowObservationProposalOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 resultOwner:CommerceWorkflowRemoteResultOwnerV1,result:CommerceWorkflowRemoteResultHandleV1,
 snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
 workerOwner:CommerceWorkerContextOwnerV1,worker:CommerceWorkerContextV1,
):CommerceWorkflowObservationProposalOwnerV1;
export function createCommerceWorkflowObservationProposalOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 resultOwner:CommerceWorkflowQueryResultOwnerV1,result:CommerceWorkflowQueryResultHandleV1,
 snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
 workerOwner:CommerceWorkerContextOwnerV1,worker:CommerceWorkerContextV1,
):CommerceWorkflowObservationProposalOwnerV1;
export function createCommerceWorkflowObservationProposalOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 resultOwner:CommerceWorkflowRemoteResultOwnerV1|CommerceWorkflowQueryResultOwnerV1,
 result:CommerceWorkflowRemoteResultHandleV1|CommerceWorkflowQueryResultHandleV1,
 snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
 workerOwner:CommerceWorkerContextOwnerV1,worker:CommerceWorkerContextV1,
):CommerceWorkflowObservationProposalOwnerV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);
 const queryResult=result?.kind==='original-protected-workflow-query-result/v1-candidate';
 if(queryResult)assertCommerceWorkflowQueryResultOwnerV1(resultOwner as CommerceWorkflowQueryResultOwnerV1);
 else assertCommerceWorkflowRemoteResultOwnerV1(resultOwner as CommerceWorkflowRemoteResultOwnerV1);
 assertCommerceWorkflowSnapshotOwnerV1(snapshots);
 assertCommerceWorkerContextOwnerV1(workerOwner);workerOwner.assertContextCurrent(worker);
 const source=binding.inspect(),checked=semantics.inspect(semantic),
  observation=source.workflow.drivers.find(driver=>driver.kind==='observation');
 if(checked.source_capture_sha256!==source.source_capture_sha256||!observation)
  bad('ForeignOwner');
 const entry=checked.entries.find(row=>row.id===observation!.call.entry);
 if(!entry)bad('InvalidContract');
 const plan=inspectCommerceWorkflowObservationPlanV1(source.workflow,entry!);
 const handles=new WeakMap<object,CommerceWorkflowObservationProposalInspectionV1>();
 let disposed=false;
 const inspectedResult=()=>queryResult?
  (resultOwner as CommerceWorkflowQueryResultOwnerV1).inspect(result as CommerceWorkflowQueryResultHandleV1):
  (resultOwner as CommerceWorkflowRemoteResultOwnerV1).inspect(result as CommerceWorkflowRemoteResultHandleV1);
 const selectedBranch=()=>queryResult?
  (resultOwner as CommerceWorkflowQueryResultOwnerV1).select(result as CommerceWorkflowQueryResultHandleV1):
  (resultOwner as CommerceWorkflowRemoteResultOwnerV1).select(result as CommerceWorkflowRemoteResultHandleV1);
 const derive=():CommerceWorkflowObservationProposalInspectionV1=>{
  if(disposed)bad('DisposedOwner');
  codePin.assertCurrent();
  binding.assertCurrent();semantics.assertCurrent(semantic);
  const remote=inspectedResult(),witness=snapshots.recheck(snapshot),
   currentWorker=workerOwner.inspectContext(worker),branch=selectedBranch();
  if(remote.workflow!==source.workflow.name||witness.workflow!==source.workflow.name||
   currentWorker.workflow!==source.workflow.name||
   remote.source_capture_sha256!==source.source_capture_sha256||
   witness.source_capture_sha256!==source.source_capture_sha256||
   currentWorker.source_capture_sha256!==source.source_capture_sha256||
   remote.store_id!==witness.store_id||remote.store_id!==currentWorker.store_id||
   remote.consumer_entry_id!==currentWorker.consumer_entry_id||
   remote.occurrence_id!==currentWorker.occurrence_id||
   remote.order_id!==witness.order_id||remote.order_id!==currentWorker.order_id||
   remote.worker_id!==witness.worker_id||remote.worker_id!==currentWorker.worker_id||
   remote.worker_epoch!==witness.worker_epoch||remote.worker_epoch!==currentWorker.worker_epoch||
   remote.progress_version!==witness.progress_version||
   !currentWorker.progress_claim_qualified||remote.result_kind!=='returned'||
   branch.outcome!=='selected'||branch.step_name!==remote.step_name||
   branch.workflow!==remote.workflow||branch.source_capture_sha256!==remote.source_capture_sha256||
   branch.observation===null||branch.observation===undefined)
   bad('ForeignOwner');
  const order=field(witness.value,'order'),progress=field(witness.value,'progress');
  const orderId=field(order,'id'),orderVersion=field(order,'version'),
   progressId=field(progress,'orderId'),progressVersion=field(progress,'version'),
   progressEpoch=field(progress,'workerEpoch');
  const exactOrderId=typeof orderId==='string'?orderId:bad('InvalidSnapshot'),
   exactOrderVersion=typeof orderVersion==='bigint'?orderVersion:bad('InvalidSnapshot');
  if(exactOrderId!==remote.order_id||progressId!==remote.order_id||
   exactOrderVersion<1n||
   progressVersion!==remote.progress_version||progressEpoch!==remote.worker_epoch)
   bad('StaleSnapshot');
  workerOwner.assertOrder(worker,exactOrderId);
  const input=coreFreeze({orderId:exactOrderId,expectedOrderVersion:exactOrderVersion,
   expectedProgressVersion:remote.progress_version,observation:branch.observation});
  const causal=coreFreeze({progress});
  inspectedResult();snapshots.recheck(snapshot);workerOwner.assertContextCurrent(worker);
  return coreFreeze({workflow:source.workflow.name,source_capture_sha256:source.source_capture_sha256,
   store_id:remote.store_id,consumer_entry_id:remote.consumer_entry_id,
   occurrence_id:remote.occurrence_id,step_name:remote.step_name,remote_entry_id:remote.target_entry_id,
   entry_id:plan.entry_id,target:plan.target,order_id:exactOrderId,
   worker_id:remote.worker_id,worker_epoch:remote.worker_epoch,
   command_id:remote.command_id,request_fingerprint:remote.request_fingerprint,
   progress_version:remote.progress_version,order_version:exactOrderVersion,input,
   causal_projection:causal,next_action:branch.action,
   qualification:'original-result-selected-observation-proposal;fresh-auth-and-atomic-commit-required' as const,
   authority_effect:'none' as const});
 };
 const initial=derive();
 // The protected result, checked branch and original snapshot are immutable.
 // Keep their derived proposal data, but recheck every mutable owner/claim and
 // the actual persisted snapshot each time. No freshness result is retained.
 const refresh=()=>{
  if(disposed)bad('DisposedOwner');
  codePin.assertCurrent();binding.assertCurrent();semantics.assertCurrent(semantic);
  const witness=queryResult?
   (resultOwner.assertCurrent(),snapshots.recheck(snapshot)):
   (resultOwner as CommerceWorkflowRemoteResultOwnerV1).recheckSnapshot(snapshots,snapshot),
   currentWorker=workerOwner.inspectContext(worker);
  if(witness.workflow!==initial.workflow||witness.source_capture_sha256!==initial.source_capture_sha256||
   witness.store_id!==initial.store_id||witness.order_id!==initial.order_id||
   witness.worker_id!==initial.worker_id||witness.worker_epoch!==initial.worker_epoch||
   witness.progress_version!==initial.progress_version||
   currentWorker.workflow!==initial.workflow||currentWorker.source_capture_sha256!==initial.source_capture_sha256||
   currentWorker.store_id!==initial.store_id||currentWorker.consumer_entry_id!==initial.consumer_entry_id||
   currentWorker.occurrence_id!==initial.occurrence_id||currentWorker.order_id!==initial.order_id||
   currentWorker.worker_id!==initial.worker_id||currentWorker.worker_epoch!==initial.worker_epoch||
   !currentWorker.progress_claim_qualified)bad('StaleOwner');
  resultOwner.assertCurrent();workerOwner.assertContextCurrent(worker);
  codePin.assertCurrent();binding.assertCurrent();semantics.assertCurrent(semantic);
 };
 const currentProposal=(handle:CommerceWorkflowObservationProposalHandleV1)=>{
  if(disposed)bad('DisposedOwner');
  const prior=handle&&typeof handle==='object'?handles.get(handle):undefined;
  if(!prior)bad('ForeignOwner');
  refresh();
  return prior!;
 };
 const owner:CommerceWorkflowObservationProposalOwnerV1=Object.freeze({
  propose(){refresh();const inspection=initial,handle:CommerceWorkflowObservationProposalHandleV1=
   Object.freeze({kind:'original-workflow-observation-proposal/v1-candidate'});
   handles.set(handle,inspection);return handle;},
  inspect:currentProposal,recheck:currentProposal,
  assertCurrent:refresh,dispose(){disposed=true;},
 });
 owners.add(owner);return owner;
}
