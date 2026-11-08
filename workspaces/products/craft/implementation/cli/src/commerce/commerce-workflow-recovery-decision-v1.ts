/** Checked recovery decision for a quiescent predecessor's remote step.
 * Its data carries no authority, but the original owner can recheck the
 * issued object against the live claim, journal, snapshot and source branch.
 * Fresh Auth and a native observation commit remain separate requirements.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {isDeepStrictEqual} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,type CommerceWorkScheduleClaimV1}
 from './commerce-service-storage-v1.js';
import {assertCommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityOwnerV1,
 type CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';
import {assertCommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotOwnerV1,
 type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import {assertCommerceWorkflowBranchSelectionOwnerV1,type CommerceWorkflowBranchSelectionOwnerV1}
 from './commerce-workflow-branch-selection-v1.js';
import {inspectCommerceWorkflowJournalRowDataV1,CommerceWorkflowPreparedJournalProjectionErrorV1}
 from './commerce-workflow-prepared-journal-projection-v1.js';
import type {WorkflowActionV1} from './commerce-data-v1.js';

export class CommerceWorkflowRecoveryDecisionErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowRecoveryDecisionErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowRecoveryDecisionErrorV1(code);};
const issued=new WeakMap<object,()=>CommerceWorkflowRecoveryDecisionV1>();

export interface CommerceWorkflowRecoveryDecisionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;
 readonly step_name:string;readonly target_entry_id:string;readonly command_id:string;
 readonly request_fingerprint:string;readonly order_id:string;readonly progress_version:bigint;
 readonly predecessor_worker_id:string;readonly predecessor_worker_epoch:bigint;
 readonly current_worker_id:string;readonly current_worker_epoch:bigint;
 readonly kind:'new-step'|'prepared-predecessor'|'dispatched-reconcile'|'observed-reread'|'suspend';
 readonly reason:'no-journal'|'prepared-never-dispatched'|'dispatched-unknown-result'|
  'observed-reload'|'indeterminate'|'identity-conflict'|'no-declared-reconciliation';
 readonly journal_phase:'Prepared'|'Dispatched'|'Observed'|'Indeterminate'|null;
 readonly action:WorkflowActionV1|null;readonly observation:unknown|null;
 readonly original_journal:'retain';
 readonly qualification:'quiescent-original-journal-recovery-data-only;fresh-auth-and-native-observation-required';
 readonly authority_effect:'none';
}

/** A copied or shaped decision has no provenance. Rechecking an issued one
 * repeats the original quiescent-claim, journal, identity, snapshot and
 * source-branch selection, and refuses any changed observation or action. */
export function recheckCommerceWorkflowRecoveryDecisionV1(
 decision:CommerceWorkflowRecoveryDecisionV1,
):CommerceWorkflowRecoveryDecisionV1 {
 const derive=decision&&typeof decision==='object'?issued.get(decision):undefined;
 if(!derive)return bad('ForeignOwner');
 const current=derive();
 if(!isDeepStrictEqual(current,decision))bad('StaleOwner');
 return decision;
}

/** The same original command key/fingerprint is required across worker epochs.
 * A Dispatched predecessor is mapped only to its source-declared inspection
 * companion. A missing or conflicting journal cannot create call authority. */
export function selectCommerceWorkflowRecoveryDecisionV1(
 binding:CommerceWorkflowCoordinationBindingV1,storage:CommerceServiceStorageOwnerV1,
 schedule:CommerceWorkScheduleClaimV1,identities:CommerceWorkflowStepIdentityOwnerV1,
 identity:CommerceWorkflowStepIdentityHandleV1,snapshots:CommerceWorkflowSnapshotOwnerV1,
 snapshot:CommerceWorkflowSnapshotHandleV1,branches:CommerceWorkflowBranchSelectionOwnerV1,
):CommerceWorkflowRecoveryDecisionV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceServiceStorageOwnerV1(storage);
 assertCommerceWorkflowStepIdentityOwnerV1(identities);assertCommerceWorkflowSnapshotOwnerV1(snapshots);
 assertCommerceWorkflowBranchSelectionOwnerV1(branches);
 storage.assertWorkScheduleClaimCurrent(schedule);
 const source=binding.inspect(),store=storage.inspect(),claim=storage.inspectWorkScheduleClaim(schedule),
  step=identities.recheck(identity),witness=snapshots.recheck(snapshot),
  remote=source.workflow.steps.find(row=>row.name===step.step_name);
 const predecessor=claim.prior_worker_owner;
 const predecessorId=predecessor.kind==='some'?predecessor.value:bad('ForeignOwner');
 if(claim.predecessor_proof!=='quiescent'||
  source.owner_service!==store.service||source.source_capture_sha256!==store.source_capture_sha256||
  source.source_capture_sha256!==step.source_capture_sha256||
  source.source_capture_sha256!==witness.source_capture_sha256||
  source.workflow.name!==claim.workflow||source.workflow.name!==step.workflow||
  source.workflow.name!==witness.workflow||source.workflow.input_entry!==claim.consumer_entry_id||
  store.store_id!==claim.store_id||store.store_id!==step.store_id||store.store_id!==witness.store_id||
  step.order_id!==claim.order_id||step.order_id!==witness.order_id||
  step.worker_id!==claim.worker_id||step.worker_id!==witness.worker_id||
  step.worker_epoch!==claim.worker_epoch||step.worker_epoch!==witness.worker_epoch||
  step.progress_version!==witness.progress_version||!remote||remote.kind!=='remote'||
  remote.call.entry!==step.target_entry_id)
  bad('ForeignOwner');
 const original={consumerEntryId:claim.consumer_entry_id,occurrenceId:claim.occurrence_id,
  orderId:step.order_id,stepName:step.step_name,commandId:step.command_id,
  targetEntryId:step.target_entry_id,requestFingerprint:step.request_fingerprint};
 const key={consumerEntryId:claim.consumer_entry_id,occurrenceId:claim.occurrence_id,
  stepName:step.step_name,commandId:step.command_id};
 const make=(kind:CommerceWorkflowRecoveryDecisionV1['kind'],reason:CommerceWorkflowRecoveryDecisionV1['reason'],
  journal_phase:CommerceWorkflowRecoveryDecisionV1['journal_phase'],action:WorkflowActionV1|null=null,
  observation:unknown=null):CommerceWorkflowRecoveryDecisionV1=>{
  const decision=coreFreeze({workflow:source.workflow.name,
   source_capture_sha256:source.source_capture_sha256,store_id:store.store_id,
   consumer_entry_id:claim.consumer_entry_id,occurrence_id:claim.occurrence_id,
   step_name:step.step_name,target_entry_id:step.target_entry_id,command_id:step.command_id,
   request_fingerprint:step.request_fingerprint,order_id:step.order_id,
   progress_version:step.progress_version,
   predecessor_worker_id:predecessorId,
   predecessor_worker_epoch:claim.prior_worker_epoch,current_worker_id:step.worker_id,
   current_worker_epoch:step.worker_epoch,kind,reason,journal_phase,action,observation,
   original_journal:'retain' as const,
   qualification:'quiescent-original-journal-recovery-data-only;fresh-auth-and-native-observation-required' as const,
   authority_effect:'none' as const});
  issued.set(decision,()=>selectCommerceWorkflowRecoveryDecisionV1(
   binding,storage,schedule,identities,identity,snapshots,snapshot,branches));
  return decision;
 };
 const recorded=storage.inspectStoredRecord(source.journal_entity,0,key);
 if(!recorded){storage.assertWorkScheduleClaimCurrent(schedule);identities.recheck(identity);
  return make('new-step','no-journal',null);}
 let journal:ReturnType<typeof inspectCommerceWorkflowJournalRowDataV1>;
 try{journal=inspectCommerceWorkflowJournalRowDataV1(original,
  {id:predecessorId,epoch:claim.prior_worker_epoch},recorded);}
 catch(error){if(error instanceof CommerceWorkflowPreparedJournalProjectionErrorV1&&
  (error.code==='JournalConflict'||error.code==='InvalidJournalRow'))return make('suspend','identity-conflict',null);
  throw error;}
 if(!journal.same_current_worker)return make('suspend','identity-conflict',journal.phase);
 if(journal.phase==='Prepared')return make('prepared-predecessor','prepared-never-dispatched','Prepared');
 if(journal.phase==='Observed')return make('observed-reread','observed-reload','Observed');
 if(journal.phase==='Indeterminate')return make('suspend','indeterminate','Indeterminate');
 const companion=identities.plans().find(row=>row.step_name===step.step_name)?.identity_source_step;
 const declared=branches.plans().find(row=>row.step_name===step.step_name);
 const channel=declared?.branches.some(row=>row.channel==='call-failure')?'call-failure':
  declared?.branches.some(row=>row.channel==='unknown')?'unknown':null;
 if(!companion||!channel)return make('suspend','no-declared-reconciliation','Dispatched');
 // A killed worker has no trustworthy response. The declared failure/unknown
 // branch is conservative data for recording uncertainty, not a result claim.
 let decision:ReturnType<CommerceWorkflowBranchSelectionOwnerV1['selectCurrent']>;
 try{decision=branches.selectCurrent(identities,identity,snapshots,snapshot,{channel});}
 catch{return make('suspend','no-declared-reconciliation','Dispatched');}
 storage.assertWorkScheduleClaimCurrent(schedule);identities.recheck(identity);
 if(decision.outcome!=='selected'||decision.action?.kind!=='step'||decision.action.target!==companion)
  return make('suspend','no-declared-reconciliation','Dispatched');
 return make('dispatched-reconcile','dispatched-unknown-result','Dispatched',decision.action,decision.observation);
}
