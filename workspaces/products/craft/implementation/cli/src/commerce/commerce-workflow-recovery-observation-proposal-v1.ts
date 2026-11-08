/** Inert observation proposal for a quiescent predecessor's Dispatched step.
 * The original recovery decision and successor snapshot are rechecked on every
 * inspection. Fresh Auth, admission, and an atomic native commit are separate.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from './commerce-core-semantic-owner.js';
import {recheckCommerceWorkflowRecoveryDecisionV1,type CommerceWorkflowRecoveryDecisionV1}
 from './commerce-workflow-recovery-decision-v1.js';
import {inspectCommerceWorkflowObservationPlanV1}
 from './commerce-workflow-observation-proposal-v1.js';
import {assertCommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotOwnerV1,
 type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,
 type CommerceWorkerContextV1} from './commerce-worker-context-v1.js';

export class CommerceWorkflowRecoveryObservationProposalErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowRecoveryObservationProposalErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowRecoveryObservationProposalErrorV1(code);};
const codePin=pinCoreImplementation(import.meta.url,[]);
const field=(value:unknown,name:string):unknown=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(value)))bad('InvalidSnapshot');
 const descriptor=Object.getOwnPropertyDescriptor(value,name);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidSnapshot');
 return descriptor!.value;
};

export interface CommerceWorkflowRecoveryObservationProposalHandleV1 {
 readonly kind:'original-recovery-observation-proposal/v1-candidate';
}
export interface CommerceWorkflowRecoveryObservationProposalInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly step_name:string;
 readonly remote_entry_id:string;readonly entry_id:string;readonly target:string;
 readonly order_id:string;readonly worker_id:string;readonly worker_epoch:bigint;
 readonly predecessor_worker_id:string;readonly predecessor_worker_epoch:bigint;
 readonly command_id:string;readonly request_fingerprint:string;
 readonly progress_version:bigint;readonly order_version:bigint;
 readonly input:Readonly<{orderId:string;expectedOrderVersion:bigint;
  expectedProgressVersion:bigint;observation:unknown}>;
 readonly causal_projection:Readonly<{progress:unknown}>;
 readonly next_action:unknown;readonly original_journal:'retain';
 readonly qualification:'quiescent-dispatched-source-branch-observation-data;fresh-auth-and-atomic-commit-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowRecoveryObservationProposalOwnerV1 {
 propose():CommerceWorkflowRecoveryObservationProposalHandleV1;
 inspect(handle:CommerceWorkflowRecoveryObservationProposalHandleV1):CommerceWorkflowRecoveryObservationProposalInspectionV1;
 recheck(handle:CommerceWorkflowRecoveryObservationProposalHandleV1):CommerceWorkflowRecoveryObservationProposalInspectionV1;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowRecoveryObservationProposalOwnerV1(
 owner:CommerceWorkflowRecoveryObservationProposalOwnerV1,
):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');
 owner.assertCurrent();
}

/** No caller-supplied branch, observation, or invocation can enter this path.
 * The decision must come from the original quiescent claim and be the source
 * branch selected for an unknown outcome of a durable Dispatched step. */
export function createCommerceWorkflowRecoveryObservationProposalOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 decision:CommerceWorkflowRecoveryDecisionV1,
 snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
 workerOwner:CommerceWorkerContextOwnerV1,worker:CommerceWorkerContextV1,
):CommerceWorkflowRecoveryObservationProposalOwnerV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);
 assertCommerceWorkflowSnapshotOwnerV1(snapshots);assertCommerceWorkerContextOwnerV1(workerOwner);
 const source=binding.inspect(),checked=semantics.inspect(semantic),
  observation=source.workflow.drivers.find(driver=>driver.kind==='observation');
 if(checked.source_capture_sha256!==source.source_capture_sha256||!observation)bad('ForeignOwner');
 const entry=checked.entries.find(row=>row.id===observation!.call.entry);
 if(!entry)bad('InvalidContract');
 const plan=inspectCommerceWorkflowObservationPlanV1(source.workflow,entry!);
 const handles=new WeakMap<object,CommerceWorkflowRecoveryObservationProposalInspectionV1>();
 let disposed=false;
 const derive=():CommerceWorkflowRecoveryObservationProposalInspectionV1=>{
  if(disposed)bad('DisposedOwner');
  codePin.assertCurrent();binding.assertCurrent();semantics.assertCurrent(semantic);
  // Rechecking the original decision already rechecks this exact snapshot.
  // Read its issued value here; the closing decision recheck covers changes
  // during proposal construction.
  const recovered=recheckCommerceWorkflowRecoveryDecisionV1(decision),
   witness=snapshots.inspect(snapshot),currentWorker=workerOwner.inspectContext(worker);
  if(recovered.kind!=='dispatched-reconcile'||recovered.reason!=='dispatched-unknown-result'||
   recovered.journal_phase!=='Dispatched'||recovered.action?.kind!=='step'||
   recovered.observation===null||recovered.observation===undefined||
   recovered.original_journal!=='retain'||recovered.authority_effect!=='none'||
   recovered.workflow!==source.workflow.name||witness.workflow!==source.workflow.name||
   currentWorker.workflow!==source.workflow.name||
   recovered.source_capture_sha256!==source.source_capture_sha256||
   witness.source_capture_sha256!==source.source_capture_sha256||
   currentWorker.source_capture_sha256!==source.source_capture_sha256||
   recovered.store_id!==witness.store_id||recovered.store_id!==currentWorker.store_id||
   recovered.consumer_entry_id!==currentWorker.consumer_entry_id||
   recovered.occurrence_id!==currentWorker.occurrence_id||
   recovered.order_id!==witness.order_id||recovered.order_id!==currentWorker.order_id||
   recovered.current_worker_id!==witness.worker_id||
   recovered.current_worker_id!==currentWorker.worker_id||
   recovered.current_worker_epoch!==witness.worker_epoch||
   recovered.current_worker_epoch!==currentWorker.worker_epoch||
   recovered.progress_version!==witness.progress_version||
   !currentWorker.progress_claim_qualified||currentWorker.predecessor_proof!=='quiescent'||
   currentWorker.prior_worker_owner.kind!=='some'||
   currentWorker.prior_worker_owner.value!==recovered.predecessor_worker_id||
   currentWorker.prior_worker_epoch!==recovered.predecessor_worker_epoch)
   bad('ForeignOwner');
  const order=field(witness.value,'order'),progress=field(witness.value,'progress');
  const orderId=field(order,'id'),orderVersion=field(order,'version'),
   progressId=field(progress,'orderId'),progressVersion=field(progress,'version'),
   progressEpoch=field(progress,'workerEpoch');
  const exactOrderId=typeof orderId==='string'?orderId:bad('InvalidSnapshot'),
   exactOrderVersion=typeof orderVersion==='bigint'?orderVersion:bad('InvalidSnapshot');
  if(exactOrderVersion<1n||exactOrderId!==recovered.order_id||progressId!==recovered.order_id||
   progressVersion!==recovered.progress_version||progressEpoch!==recovered.current_worker_epoch)
   bad('StaleSnapshot');
  const input=coreFreeze({orderId:exactOrderId,expectedOrderVersion:exactOrderVersion,
   expectedProgressVersion:recovered.progress_version,observation:recovered.observation});
  const causal=coreFreeze({progress});
  // The original decision's recheck also closes its successor snapshot;
  // later admission repeats this check before any effect.
  recheckCommerceWorkflowRecoveryDecisionV1(decision);
  workerOwner.assertContextCurrent(worker);
  return coreFreeze({workflow:recovered.workflow,source_capture_sha256:recovered.source_capture_sha256,
   store_id:recovered.store_id,consumer_entry_id:recovered.consumer_entry_id,
   occurrence_id:recovered.occurrence_id,step_name:recovered.step_name,
   remote_entry_id:recovered.target_entry_id,entry_id:plan.entry_id,target:plan.target,
   order_id:exactOrderId,worker_id:recovered.current_worker_id,
   worker_epoch:recovered.current_worker_epoch,
   predecessor_worker_id:recovered.predecessor_worker_id,
   predecessor_worker_epoch:recovered.predecessor_worker_epoch,
   command_id:recovered.command_id,request_fingerprint:recovered.request_fingerprint,
   progress_version:recovered.progress_version,order_version:exactOrderVersion,input,
   causal_projection:causal,next_action:recovered.action,original_journal:'retain' as const,
   qualification:'quiescent-dispatched-source-branch-observation-data;fresh-auth-and-atomic-commit-required' as const,
   authority_effect:'none' as const});
 };
 derive();
 const currentProposal=(handle:CommerceWorkflowRecoveryObservationProposalHandleV1)=>{
  if(disposed)bad('DisposedOwner');
  const prior=handle&&typeof handle==='object'?handles.get(handle):undefined;
  if(!prior)bad('ForeignOwner');
  const now=derive();if(!isDeepStrictEqual(now,prior))bad('StaleOwner');
  return prior!;
 };
 const owner:CommerceWorkflowRecoveryObservationProposalOwnerV1=Object.freeze({
  propose(){const inspection=derive(),handle:CommerceWorkflowRecoveryObservationProposalHandleV1=
   Object.freeze({kind:'original-recovery-observation-proposal/v1-candidate'});
   handles.set(handle,inspection);return handle;},
  inspect:currentProposal,recheck:currentProposal,
  assertCurrent(){derive();},dispose(){disposed=true;},
 });
 owners.add(owner);return owner;
}
