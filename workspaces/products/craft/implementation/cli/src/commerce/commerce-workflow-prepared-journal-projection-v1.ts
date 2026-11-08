/** Inert projection of one checked Workflow step into its source-declared
 * StepJournal ABI. Storage must obtain this projection from original owners,
 * recheck it, and make its own atomic native commit before any dispatch.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceWorkScheduleClaimV1,type CommerceWorkerProgressClaimV1} from './commerce-service-storage-v1.js';
import {assertCommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityOwnerV1,
 type CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';

export class CommerceWorkflowPreparedJournalProjectionErrorV1 extends Error {
 readonly code:string;
 constructor(code:string,detail:string){super(detail);this.name='CommerceWorkflowPreparedJournalProjectionErrorV1';this.code=code;}
}
const bad=(code:string,detail:string):never=>{throw new CommerceWorkflowPreparedJournalProjectionErrorV1(code,detail);};
const MAX_U64=18446744073709551615n;
const id=(value:unknown,max=256):value is string=>typeof value==='string'&&value.length>0&&
 Buffer.byteLength(value,'utf8')<=max&&Buffer.from(value).toString('utf8')===value;
const fingerprint=(value:unknown):value is string=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
const uint=(value:unknown,min:bigint):value is bigint=>typeof value==='bigint'&&value>=min&&value<=MAX_U64;
const plain=(value:unknown):value is Record<string,unknown>=>!!value&&typeof value==='object'&&!Array.isArray(value)&&
 !host.isProxy(value)&&(Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
const own=(value:Record<string,unknown>,name:string):unknown=>{
 const descriptor=Object.getOwnPropertyDescriptor(value,name);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidJournalRow','plain own StepJournal fields required');
 return descriptor!.value;
};

/** The committed worker claim is the lower bound. Later observed business
 * steps legitimately advance the durable progress version. */
export function assertCommerceWorkflowJournalProgressVersionV1(
 committedClaimVersion:unknown,currentStepVersion:unknown,
):void {
 if(!uint(committedClaimVersion,1n)||!uint(currentStepVersion,1n))
  return bad('InvalidContract','bounded committed and current progress versions required');
 if(currentStepVersion<committedClaimVersion)
  return bad('StaleOwner','current source snapshot predates committed worker progress claim');
}

export interface CommerceWorkflowJournalImmutableV1 {
 readonly consumerEntryId:string;readonly occurrenceId:string;readonly orderId:string;
 readonly stepName:string;readonly commandId:string;readonly targetEntryId:string;
 readonly requestFingerprint:string;
}
export interface CommerceWorkflowJournalRowInspectionV1 {
 readonly phase:'Prepared'|'Dispatched'|'Observed'|'Indeterminate';
 readonly worker_id:string;readonly worker_epoch:bigint;readonly version:bigint;
 readonly observation_kind:'none'|'some';readonly same_current_worker:boolean;
 readonly authority_effect:'none';
}
/** Validates a native-decoded row's exact immutable request and mutable phase.
 * This function is data-only. A matching row is never a dispatch permit. */
export function inspectCommerceWorkflowJournalRowDataV1(
 immutable:CommerceWorkflowJournalImmutableV1,currentWorker:Readonly<{id:string;epoch:bigint}>,row:unknown,
):CommerceWorkflowJournalRowInspectionV1 {
 if(!plain(row))return bad('InvalidJournalRow','plain StepJournal row required');
 const expected=['consumerEntryId','occurrenceId','orderId','stepName','commandId','targetEntryId',
  'requestFingerprint','phase','workerOwner','workerEpoch','observation','version'];
 if(Reflect.ownKeys(row).length!==expected.length||expected.some(name=>!Object.hasOwn(row,name)))
  return bad('InvalidJournalRow','exact StepJournal ABI fields required');
 for(const name of ['consumerEntryId','occurrenceId','orderId','stepName','commandId','targetEntryId','requestFingerprint'] as const)
  if(own(row,name)!==immutable[name])return bad('JournalConflict','immutable original command and request differ');
 const phase=own(row,'phase'),worker=own(row,'workerOwner'),epoch=own(row,'workerEpoch'),
  version=own(row,'version'),observation=own(row,'observation');
 if(phase!=='Prepared'&&phase!=='Dispatched'&&phase!=='Observed'&&phase!=='Indeterminate')
  return bad('InvalidJournalRow','declared StepJournal phase required');
 if(!id(worker)||!uint(epoch,0n)||!uint(version,1n)||!plain(observation))
  return bad('InvalidJournalRow','bounded worker, epoch, version and observation required');
 const observationKind=own(observation,'kind');
 if(observationKind!=='none'&&observationKind!=='some')return bad('InvalidJournalRow','declared optional observation required');
 if(Reflect.ownKeys(observation).length!==(observationKind==='none'?1:2)||
  observationKind==='some'&&!Object.hasOwn(observation,'value'))
  return bad('InvalidJournalRow','exact optional observation shape required');
 if(phase==='Prepared'&&observationKind!=='none')return bad('InvalidJournalRow','Prepared cannot already contain an observation');
 return coreFreeze({phase,worker_id:worker,worker_epoch:epoch,version,
  observation_kind:observationKind,same_current_worker:worker===currentWorker.id&&epoch===currentWorker.epoch,
  authority_effect:'none' as const});
}

export interface CommerceWorkflowPreparedJournalProjectionInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;readonly journal_entity:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly order_id:string;
 readonly step_name:string;readonly target_entry_id:string;readonly command_id:string;readonly request_fingerprint:string;
 readonly worker_id:string;readonly worker_epoch:bigint;readonly schedule_version:bigint;readonly progress_version:bigint;
 readonly key:Readonly<{consumerEntryId:string;occurrenceId:string;stepName:string;commandId:string}>;
 readonly prepared:Readonly<CommerceWorkflowJournalImmutableV1&{
  phase:'Prepared';workerOwner:string;workerEpoch:bigint;observation:Readonly<{kind:'none'}>;version:1n}>;
 readonly qualification:'checked-original-step-journal-record-data-only;native-commit-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowPreparedJournalProjectionV1 {
 inspect():CommerceWorkflowPreparedJournalProjectionInspectionV1;
 recheck():CommerceWorkflowPreparedJournalProjectionInspectionV1;
 inspectRecordedRow(row:unknown):CommerceWorkflowJournalRowInspectionV1;
}

/** Source ABI is already checked by the binding; the other owners provide
 * genuine current claim and snapshot handles, never caller-supplied IDs. */
export function createCommerceWorkflowPreparedJournalProjectionV1(
 binding:CommerceWorkflowCoordinationBindingV1,storage:CommerceServiceStorageOwnerV1,
 scheduleClaim:CommerceWorkScheduleClaimV1,progressClaim:CommerceWorkerProgressClaimV1,
 identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
):CommerceWorkflowPreparedJournalProjectionV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceServiceStorageOwnerV1(storage);
 assertCommerceWorkflowStepIdentityOwnerV1(identities);
 const inspectCurrent=():CommerceWorkflowPreparedJournalProjectionInspectionV1=>{
  binding.assertCurrent();storage.assertCurrent();identities.assertCurrent();
  storage.assertWorkScheduleClaimCurrent(scheduleClaim);
  storage.assertWorkerProgressClaimCurrent(progressClaim);
  const source=binding.inspect(),store=storage.inspect(),schedule=storage.inspectWorkScheduleClaim(scheduleClaim),
   progress=storage.inspectWorkerProgressClaim(progressClaim),step=identities.recheck(identity),
   remote=source.workflow.steps.find(row=>row.name===step.step_name);
  if(store.service!==source.owner_service||store.source_capture_sha256!==source.source_capture_sha256||
   store.store_id!==schedule.store_id||store.store_id!==progress.store_id||store.store_id!==step.store_id||
   schedule.workflow!==source.workflow.name||progress.workflow!==source.workflow.name||step.workflow!==source.workflow.name||
   schedule.source_capture_sha256!==source.source_capture_sha256||progress.source_capture_sha256!==source.source_capture_sha256||
   step.source_capture_sha256!==source.source_capture_sha256||schedule.consumer_entry_id!==source.workflow.input_entry||
   schedule.order_id!==progress.order_id||progress.order_id!==step.order_id||
   schedule.worker_id!==progress.worker_id||progress.worker_id!==step.worker_id||
   schedule.worker_epoch!==progress.worker_epoch||progress.worker_epoch!==step.worker_epoch||
   !remote||remote.kind!=='remote'||remote.call.entry!==step.target_entry_id)
   bad('ForeignOwner','selected Workflow, committed worker, snapshot and target Entry must agree');
  if(!id(schedule.occurrence_id,128)||!id(step.step_name)||!id(step.target_entry_id)||
   !id(step.command_id)||!fingerprint(step.request_fingerprint)||
   !uint(schedule.worker_epoch,1n)||!uint(schedule.schedule_version,1n)||
   !uint(progress.progress_version,1n)||!uint(step.progress_version,1n))
   bad('InvalidContract','bounded source command and current worker versions required');
  assertCommerceWorkflowJournalProgressVersionV1(progress.progress_version,step.progress_version);
  const key=coreFreeze({consumerEntryId:schedule.consumer_entry_id,occurrenceId:schedule.occurrence_id,
   stepName:step.step_name,commandId:step.command_id});
  const prepared=coreFreeze({consumerEntryId:schedule.consumer_entry_id,occurrenceId:schedule.occurrence_id,
   orderId:step.order_id,stepName:step.step_name,commandId:step.command_id,targetEntryId:step.target_entry_id,
   requestFingerprint:step.request_fingerprint,phase:'Prepared' as const,workerOwner:step.worker_id,
   workerEpoch:step.worker_epoch,observation:{kind:'none' as const},version:1n as const});
  return coreFreeze({workflow:source.workflow.name,source_capture_sha256:source.source_capture_sha256,
   store_id:store.store_id,journal_entity:source.journal_entity,
   consumer_entry_id:schedule.consumer_entry_id,occurrence_id:schedule.occurrence_id,order_id:step.order_id,
   step_name:step.step_name,target_entry_id:step.target_entry_id,command_id:step.command_id,
   request_fingerprint:step.request_fingerprint,worker_id:step.worker_id,worker_epoch:step.worker_epoch,
   schedule_version:schedule.schedule_version,progress_version:step.progress_version,key,prepared,
   qualification:'checked-original-step-journal-record-data-only;native-commit-required' as const,
   authority_effect:'none' as const});
 };
 const initial=inspectCurrent();
 const recheck=()=>{
  const current=inspectCurrent();
  for(const key of ['workflow','source_capture_sha256','store_id','journal_entity','consumer_entry_id','occurrence_id',
   'order_id','step_name','target_entry_id','command_id','request_fingerprint','worker_id','worker_epoch',
   'schedule_version','progress_version'] as const)
   if(current[key]!==initial[key])bad('StaleOwner','original Workflow step projection changed');
  return initial;
 };
 return Object.freeze({inspect:recheck,recheck,
  inspectRecordedRow(row:unknown){recheck();return inspectCommerceWorkflowJournalRowDataV1(initial.prepared,
   {id:initial.worker_id,epoch:initial.worker_epoch},row);}});
}
