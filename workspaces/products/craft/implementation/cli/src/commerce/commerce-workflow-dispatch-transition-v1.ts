/** Data-only Prepared -> Dispatched StepJournal transition. A caller must
 * recheck the original owners and commit the returned change atomically in
 * native storage; this projection itself never authorizes a provider call.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceWorkflowStepJournalV1,type CommerceWorkflowStepJournalInspectionV1}
 from './commerce-service-storage-v1.js';
import {assertCommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityOwnerV1,
 type CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';
import {inspectCommerceWorkflowJournalRowDataV1,type CommerceWorkflowJournalImmutableV1}
 from './commerce-workflow-prepared-journal-projection-v1.js';

export class CommerceWorkflowDispatchTransitionErrorV1 extends Error {
 readonly code:string;
 constructor(code:string,detail:string){super(detail);this.name='CommerceWorkflowDispatchTransitionErrorV1';this.code=code;}
}
const bad=(code:string,detail:string):never=>{throw new CommerceWorkflowDispatchTransitionErrorV1(code,detail);};

export type CommerceWorkflowPreparedRowV1=Readonly<CommerceWorkflowJournalImmutableV1&{
 phase:'Prepared';workerOwner:string;workerEpoch:bigint;observation:Readonly<{kind:'none'}>;version:1n;
}>;
export type CommerceWorkflowDispatchedRowV1=Readonly<CommerceWorkflowJournalImmutableV1&{
 phase:'Dispatched';workerOwner:string;workerEpoch:bigint;observation:Readonly<{kind:'none'}>;version:2n;
}>;
export interface CommerceWorkflowDispatchedRowProjectionV1 {
 readonly old:CommerceWorkflowPreparedRowV1;
 readonly next:CommerceWorkflowDispatchedRowV1;
 readonly changes:Readonly<{phase:'Dispatched';version:2n}>;
 readonly expected_version:1n;
 readonly authority_effect:'none';
}

/** Exact source StepJournal ABI and original request are checked by the
 * shared row inspector. This is a pure data projection, not a storage CAS. */
export function projectCommerceWorkflowDispatchedRowV1(
 immutable:CommerceWorkflowJournalImmutableV1,currentWorker:Readonly<{id:string;epoch:bigint}>,row:unknown,
):CommerceWorkflowDispatchedRowProjectionV1 {
 const observed=inspectCommerceWorkflowJournalRowDataV1(immutable,currentWorker,row);
 if(observed.phase!=='Prepared'||observed.version!==1n||observed.observation_kind!=='none')
  bad('StaleJournal','original StepJournal must still be Prepared at version 1');
 if(!observed.same_current_worker)
  bad('StaleOwner','original StepJournal worker fencing no longer matches');
 const originalRequest=coreFreeze({consumerEntryId:immutable.consumerEntryId,occurrenceId:immutable.occurrenceId,
  orderId:immutable.orderId,stepName:immutable.stepName,commandId:immutable.commandId,
  targetEntryId:immutable.targetEntryId,requestFingerprint:immutable.requestFingerprint});
 const original=coreFreeze({...originalRequest,phase:'Prepared' as const,workerOwner:currentWorker.id,
  workerEpoch:currentWorker.epoch,observation:coreFreeze({kind:'none' as const}),version:1n as const});
 const next=coreFreeze({...originalRequest,phase:'Dispatched' as const,workerOwner:currentWorker.id,
  workerEpoch:currentWorker.epoch,observation:coreFreeze({kind:'none' as const}),version:2n as const});
 return coreFreeze({old:original,next,changes:coreFreeze({phase:'Dispatched' as const,version:2n as const}),
  expected_version:1n as const,authority_effect:'none' as const});
}

export interface CommerceWorkflowDispatchTransitionInspectionV1 extends CommerceWorkflowDispatchedRowProjectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;readonly journal_entity:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly order_id:string;
 readonly step_name:string;readonly target_entry_id:string;readonly command_id:string;readonly request_fingerprint:string;
 readonly worker_id:string;readonly worker_epoch:bigint;readonly progress_version:bigint;
 readonly prepare_commit_receipt:object;
 readonly key:Readonly<{consumerEntryId:string;occurrenceId:string;stepName:string;commandId:string}>;
 readonly qualification:'checked-original-prepared-step-journal-transition-data-only;atomic-native-update-required';
}
export interface CommerceWorkflowDispatchTransitionV1 {
 /** The already checked construction-time view. Use only in one synchronous
  * transition before the mandatory pre-commit recheck. */
 initial():CommerceWorkflowDispatchTransitionInspectionV1;
 inspect():CommerceWorkflowDispatchTransitionInspectionV1;
 recheck():CommerceWorkflowDispatchTransitionInspectionV1;
}

/** The opaque journal handle, source binding, store and snapshot identity
 * must all be genuine. Their inspections alone are insufficient authority. */
export function createCommerceWorkflowDispatchTransitionV1(
 binding:CommerceWorkflowCoordinationBindingV1,storage:CommerceServiceStorageOwnerV1,
 journal:CommerceWorkflowStepJournalV1,identities:CommerceWorkflowStepIdentityOwnerV1,
 identity:CommerceWorkflowStepIdentityHandleV1,
):CommerceWorkflowDispatchTransitionV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceServiceStorageOwnerV1(storage);
 assertCommerceWorkflowStepIdentityOwnerV1(identities);
 const inspectCurrent=():CommerceWorkflowDispatchTransitionInspectionV1=>{
  const source=binding.inspect(),store=storage.inspect(),committed:CommerceWorkflowStepJournalInspectionV1=
   storage.inspectWorkflowStepJournal(journal),step=identities.recheck(identity);
  if(store.service!==source.owner_service||store.source_capture_sha256!==source.source_capture_sha256||
   store.store_id!==committed.store_id||source.workflow.name!==committed.workflow||
   source.source_capture_sha256!==committed.source_capture_sha256||
   source.workflow.input_entry!==committed.consumer_entry_id||
   step.workflow!==committed.workflow||step.source_capture_sha256!==committed.source_capture_sha256||
   step.store_id!==committed.store_id||step.order_id!==committed.order_id||
   step.step_name!==committed.step_name||step.target_entry_id!==committed.target_entry_id||
   step.command_id!==committed.command_id||step.request_fingerprint!==committed.request_fingerprint||
   step.worker_id!==committed.worker_id||step.worker_epoch!==committed.worker_epoch||
   step.progress_version!==committed.progress_version||committed.phase!=='Prepared'||
   committed.authority_effect!=='none')
   bad('ForeignOwner','checked Workflow, committed StepJournal and current source step must agree');
  const remote=source.workflow.steps.find(row=>row.name===step.step_name);
  if(!remote||remote.kind!=='remote'||remote.call.entry!==step.target_entry_id)
   bad('ForeignOwner','source Workflow remote Entry changed');
  const key=coreFreeze({consumerEntryId:committed.consumer_entry_id,occurrenceId:committed.occurrence_id,
   stepName:committed.step_name,commandId:committed.command_id});
  const immutable:CommerceWorkflowJournalImmutableV1=coreFreeze({consumerEntryId:committed.consumer_entry_id,
   occurrenceId:committed.occurrence_id,orderId:committed.order_id,stepName:committed.step_name,
   commandId:committed.command_id,targetEntryId:committed.target_entry_id,
   requestFingerprint:committed.request_fingerprint});
  const row=storage.inspectStoredRecord(source.journal_entity,0,key);
  if(!row)bad('StaleJournal','committed source StepJournal row is missing');
  const projected=projectCommerceWorkflowDispatchedRowV1(immutable,
   {id:committed.worker_id,epoch:committed.worker_epoch},row);
  // inspectWorkflowStepJournal fully checks the original opaque journal above;
  // the exact native row is checked below it. Close the synchronous projection
  // with current storage rather than walking that same journal two more times.
  storage.assertCurrent();
  return coreFreeze({...projected,workflow:committed.workflow,source_capture_sha256:committed.source_capture_sha256,
   store_id:committed.store_id,journal_entity:source.journal_entity,consumer_entry_id:committed.consumer_entry_id,
   occurrence_id:committed.occurrence_id,order_id:committed.order_id,step_name:committed.step_name,
   target_entry_id:committed.target_entry_id,command_id:committed.command_id,
   request_fingerprint:committed.request_fingerprint,worker_id:committed.worker_id,
   worker_epoch:committed.worker_epoch,progress_version:committed.progress_version,
   prepare_commit_receipt:committed.commit_receipt,key,
   qualification:'checked-original-prepared-step-journal-transition-data-only;atomic-native-update-required' as const});
 };
 const initial=inspectCurrent();
 const recheck=()=>{
  const current=inspectCurrent();
  for(const key of ['workflow','source_capture_sha256','store_id','journal_entity','consumer_entry_id',
   'occurrence_id','order_id','step_name','target_entry_id','command_id','request_fingerprint',
   'worker_id','worker_epoch','progress_version'] as const)
   if(current[key]!==initial[key])bad('StaleOwner','original StepJournal transition source changed');
  return initial;
 };
 return Object.freeze({initial:()=>initial,inspect:recheck,recheck});
}
