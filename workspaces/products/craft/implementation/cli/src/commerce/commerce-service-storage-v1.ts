import type {CommerceSqliteTableV1} from './commerce-sqlite-generation-v1.js';
/** Source-selected service storage with real local SQLite effects.
 * The outer Operation frame and command-principal custody are still inputs.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {mkdirSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {isDeepStrictEqual,types as host} from 'node:util';
import {dataDigest} from '../profile-engine/contracts.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {assertCommerceBindingAssemblyOwnerV1,type CommerceBindingAssemblyOwnerV1} from './commerce-binding-assembly-v1.js';
import {createCommerceSqliteFamilyOwnerV1} from './commerce-sqlite-family-v1.js';
import {createCommerceSqliteTransactionOwnerV1} from './commerce-sqlite-transaction-owner-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,isCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import {createCommerceCommandIdentityBindingOwnerV1,deriveCommerceCommandTransactionNamespaceV1,type CommerceCommandIdentityBindingOwnerV1} from './commerce-command-identity-binding-v1.js';
import {createCommerceIdentityCallOwner,type CommerceIdentityCallHandle} from './commerce-identity-call-owner.js';
import {createCommerceIdentityComponentOwner} from './commerce-identity-component.js';
import {projectCommerceCommandIdentityDataV1} from './commerce-command-identity-projection-v1.js';
import {assertCommerceGeneratedOperationRuntimeV1,type CommerceGeneratedOperationRuntimeV1,type CommerceGeneratedTransactionScopeV1} from './commerce-generated-operation-runtime-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {createCommerceWorkflowPreparedJournalProjectionV1,CommerceWorkflowPreparedJournalProjectionErrorV1,
 inspectCommerceWorkflowJournalRowDataV1,type CommerceWorkflowPreparedJournalProjectionV1}
 from './commerce-workflow-prepared-journal-projection-v1.js';
import {createCommerceWorkflowDispatchTransitionV1} from './commerce-workflow-dispatch-transition-v1.js';
import type {CommerceWorkflowObservationCommitBindingV1} from './commerce-workflow-observation-commit-binding-v1.js';
import {acquireCommerceWorkerQuiescenceV1} from './commerce-worker-quiescence-v1.js';
import type {CommerceWorkflowStepIdentityOwnerV1,CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CommerceLocalPlanOwnerV1} from './commerce-local-plan-owner-v1.js';
import type {CommerceFamilyOwnerV5} from '../profile-engine/family-v5.js';
import type {CommerceBindingAssemblyHandle,CommerceSourceHandle,CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';
import type {CommerceSqliteFamilyOwnerV1,CommerceRepositoryBundleHandleV1} from './commerce-sqlite-family-v1.js';
import type {CommerceSqliteTransactionOwnerV1,CommerceSqliteSourceProgramHandleV1} from './commerce-sqlite-transaction-owner-v1.js';
import type {CoreCommerceEventPublication,CoreCommerceEventPublicationCandidate}
 from '../generic/core-commerce-event-publication.js';
import type {CoreCommerceEventProducerProvenance,CoreCommerceEventProducerProof}
 from '../generic/core-commerce-event-producer-provenance.js';
import type {CoreCommerceEventDelivery,CoreCommerceEventReceiverAcknowledgement}
 from '../generic/core-commerce-event-delivery.js';
import type {CoreCommerceEventProducerSource} from '../generic/core-commerce-event-producer-source.js';
import {createCoreValueTypes,sameCoreValueType} from './commerce-core-types.js';
import type {OperationControlStepV1,TransactionPlanV1} from './commerce-data-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-binding-assembly-v1'+ext,'commerce-selected-entry-auth-v1'+ext,'commerce-command-identity-binding-v1'+ext,'commerce-command-identity-projection-v1'+ext,'commerce-identity-call-owner'+ext,'commerce-identity-component'+ext,'commerce-generated-operation-runtime-v1'+ext,'commerce-workflow-coordination-binding-v1'+ext,'commerce-sqlite-family-v1'+ext,'commerce-sqlite-transaction-owner-v1'+ext,'../../profiles/commerce-local-v1-candidate/runtime/sqlite-unit-of-work'+ext]);
const where={path:'service-storage',start:0,end:0};
const MAX_U64=18446744073709551615n;
// The fixed profile runtime lives outside the CLI's src root. This narrow
// structural boundary keeps typechecking inside src while runtime custody
// remains with its original owner and its source is covered by the pin.
export interface CommerceSqliteCommandKeyV1 {readonly logicalEntryId:string;readonly principalId:string;readonly commandId:string;readonly fingerprint:string;readonly transactionNamespace:string}
type CommerceSqliteClaimV1={readonly kind:'claimed';readonly command:object}|{readonly kind:'recorded';readonly result:CommerceNativeValue}|{readonly kind:'pending'|'unknown'|'conflict'|'capacity-unavailable'|'unavailable-before-start'};
type CommerceSqliteFreshClaimV1={readonly kind:'claimed';readonly command:object}|{readonly kind:'not-fresh'|'capacity-unavailable'|'unavailable-before-start'};
type CommerceSqliteOutcomeV1={readonly kind:'committed';readonly receipt:object;readonly result:CommerceNativeValue}|{readonly kind:'rolled-back'|'version-conflict'|'unique-conflict'|'capacity-unavailable';readonly rollback:object}|{readonly kind:'indeterminate';readonly ticket:object}|{readonly kind:'unavailable-before-start'};
/** The native receipt is returned only after the storage owner has consumed
 * the exact fresh generated execution. Its shape alone grants no authority. */
export interface CommerceServiceStorageFreshCommitReceiptV1 {readonly kind:'observed-native-sqlite-commit/v1-candidate'}
export interface CommerceEventPublicationAttemptV1 {readonly kind:'original-native-event-publication-attempt/v1-candidate'}
export type CommerceEventPublicationResultV1=
 {readonly kind:'published'|'recorded';readonly occurrence_id:string;readonly version:bigint;
  readonly receipt:object|null;readonly authority_effect:'committed'}|
 {readonly kind:'indeterminate';readonly attempt:CommerceEventPublicationAttemptV1;
  readonly authority_effect:'indeterminate'}|
 {readonly kind:'conflict'|'unavailable';readonly authority_effect:'none'};
export interface CommerceWorkScheduleClaimV1 {readonly kind:'original-committed-work-schedule-claim/v1-candidate'}
export interface CommerceClaimJournalV1 {readonly kind:'original-committed-claim-journal/v1-candidate'}
export interface CommerceWorkerProgressClaimV1 {readonly kind:'original-committed-worker-progress-claim/v1-candidate'}
export interface CommerceWorkflowStepJournalV1 {readonly kind:'original-committed-workflow-step-journal/v1-candidate'}
export interface CommerceWorkflowDispatchedStepJournalV1 {readonly kind:'original-committed-dispatched-workflow-step-journal/v1-candidate'}
export interface CommerceWorkScheduleClaimInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly order_id:string;
 readonly worker_id:string;readonly worker_epoch:bigint;readonly schedule_version:bigint;
 readonly prior_worker_owner:Readonly<{kind:'none'}|{kind:'some';value:string}>;readonly prior_worker_epoch:bigint;
 readonly predecessor_proof:'vacant'|'quiescent';readonly commit_receipt:object;
}
export type CommerceWorkScheduleClaimResultV1=
 {readonly kind:'claimed';readonly claim:CommerceWorkScheduleClaimV1}|
 {readonly kind:'not-ready'|'unavailable'|'indeterminate'};
export interface CommerceClaimJournalInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly order_id:string;
 readonly step_name:'claim';readonly command_id:string;readonly target_entry_id:string;
 readonly request_fingerprint:string;readonly worker_id:string;readonly worker_epoch:bigint;
 readonly phase:'Prepared';readonly commit_receipt:object;readonly authority_effect:'none';
}
export type CommerceClaimJournalResultV1=
 {readonly kind:'prepared';readonly journal:CommerceClaimJournalV1}|
 {readonly kind:'recorded'|'not-ready'|'conflict'|'unavailable'|'indeterminate'};
export interface CommerceWorkflowStepJournalInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly order_id:string;
 readonly step_name:string;readonly target_entry_id:string;readonly command_id:string;readonly request_fingerprint:string;
 readonly worker_id:string;readonly worker_epoch:bigint;readonly progress_version:bigint;
 readonly phase:'Prepared';readonly commit_receipt:object;readonly authority_effect:'none';
}
export type CommerceWorkflowStepJournalResultV1=
 {readonly kind:'prepared';readonly journal:CommerceWorkflowStepJournalV1}|
 {readonly kind:'recorded';readonly phase:'Prepared'|'Dispatched'|'Observed'|'Indeterminate'}|
 {readonly kind:'not-ready'|'conflict'|'unavailable'|'indeterminate'};
export interface CommerceWorkflowDispatchedStepJournalInspectionV1 extends Omit<CommerceWorkflowStepJournalInspectionV1,'phase'|'commit_receipt'> {
 readonly phase:'Dispatched';readonly prepare_commit_receipt:object;readonly dispatch_commit_receipt:object;
}
export type CommerceWorkflowDispatchedStepJournalResultV1=
 {readonly kind:'dispatched';readonly journal:CommerceWorkflowDispatchedStepJournalV1}|
 {readonly kind:'not-ready'|'conflict'|'unavailable'|'indeterminate'};
export interface CommerceWorkerProgressClaimInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly order_id:string;readonly worker_id:string;readonly worker_epoch:bigint;readonly progress_version:bigint;
 readonly transaction_path:string;readonly commit_receipt:object;readonly authority_effect:'none';
}
export type CommerceWorkflowEnqueueResultV1=
 {readonly kind:'enqueued'|'recorded';readonly receipt:CommerceNativeValue}|
 {readonly kind:'not-ready'|'conflict'|'unavailable'|'indeterminate'};
interface ServiceStore {
 inspect():Readonly<{service:string;store_id:string;schema_sha256:string}>;
 assertRepository(family:CommerceSqliteFamilyOwnerV1,bundle:CommerceRepositoryBundleHandleV1):void;
 claimCommand(key:CommerceSqliteCommandKeyV1):CommerceSqliteClaimV1;
 claimFreshCommand(key:CommerceSqliteCommandKeyV1):CommerceSqliteFreshClaimV1;
 inspectCommand(key:CommerceSqliteCommandKeyV1):Readonly<{kind:'recorded'|'pending'|'unknown'|'missing'|'conflict'|'rolled-back';result?:CommerceNativeValue}>;
 applySourceTransaction(owner:CommerceSqliteTransactionOwnerV1,program:CommerceSqliteSourceProgramHandleV1,command:object,frame:Readonly<Record<string,CommerceNativeValue>>,authorization?:Readonly<{owner:CommerceSelectedEntryAuthOwnerV1;invocation:CommerceOperationInvocationHandle}>,companion?:Readonly<{kind:'observed-step-journal';entity:string;row:object;expected_version:2n;changes:Readonly<{phase:'Observed';observation:CommerceNativeValue;version:3n}>}>):CommerceSqliteOutcomeV1;
 inspectDisposition(receipt:object):Readonly<{kind:'committed'|'rolled-back'|'indeterminate';attempt:number;scope_sha256:string;source_failure:Readonly<{code:string;source_path:string;source_action:unknown}>|null}>;
 readRow(entity:string,keyIndex:number,key:CommerceNativeValue):object|null;
 scanRows(entity:string,cursor:string|null,limit:number):Readonly<{rows:readonly CommerceNativeValue[];next_cursor:string|null}>;
 apply(command:object,steps:readonly (
  {readonly kind:'update';readonly row:object;readonly expected_version:bigint;readonly changes:Readonly<Record<string,CommerceNativeValue>>}|
  {readonly kind:'require-row';readonly row:object}|
  {readonly kind:'require-absent';readonly entity:string;readonly key_index:number;readonly key:CommerceNativeValue}|
  {readonly kind:'create';readonly entity:string;readonly value:CommerceNativeValue})[],result:CommerceNativeValue):CommerceSqliteOutcomeV1;
 executeBoundQuery(family:CommerceSqliteFamilyOwnerV1,bundle:CommerceRepositoryBundleHandleV1,query:import('./commerce-sqlite-family-v1.js').CommerceSqliteQueryHandleV1,slots:Readonly<Record<string,CommerceNativeValue>>):Readonly<{query:string;rows:readonly Readonly<Record<string,CommerceNativeValue>>[];residual_required:boolean;requires_original_context_owner:boolean;qualification:'original-bound-sqlite-row-data-only'}>;
 inspectRow(row:object):Readonly<{entity:string;value:CommerceNativeValue}>;
 countRows(entity:string):number;
 close():void;
}
interface SqliteRuntime {
 openCommerceSqliteUnitOfWorkV1(family:CommerceSqliteFamilyOwnerV1,bundle:CommerceRepositoryBundleHandleV1,absolutePath:string,mode:'create'|'reopen'):Promise<ServiceStore>;
 assertCommerceSqliteUnitOfWorkV1(store:ServiceStore):void;
}
async function fixedSqliteRuntime():Promise<SqliteRuntime> {
 pin.assertCurrent();
 const moduleUrl=new URL('../../profiles/commerce-local-v1-candidate/runtime/sqlite-unit-of-work.js',import.meta.url).href;
 const loaded:unknown=await import(moduleUrl);
 if(!loaded||typeof loaded!=='object'||typeof (loaded as Partial<SqliteRuntime>).openCommerceSqliteUnitOfWorkV1!=='function'||typeof (loaded as Partial<SqliteRuntime>).assertCommerceSqliteUnitOfWorkV1!=='function')
  fail('ForeignOwner',where,'fixed original SQLite runtime required');
 pin.assertCurrent();return loaded as SqliteRuntime;
}
export interface CommerceServiceStorageTransactionV1 {readonly kind:'original-source-service-storage-transaction/v1-candidate'}
/** A checked source transaction under an authorized local child. This handle
 * cannot enter apply: command ownership and quiescence remain unqualified. */
export interface CommerceServiceStorageLocalTransactionV1 {readonly kind:'original-source-service-storage-local-transaction/v1-candidate'}
export interface CommerceServiceStorageLocalTransactionInspectionV1 {
 readonly service:string;readonly operation:string;readonly transaction:string;readonly transaction_path:string;
 readonly root_entry:string;readonly local_call_path:string;readonly local_depth:number;
 readonly source_capture_sha256:string;readonly family_sha256:string;readonly schema_sha256:string;
 readonly qualification:'original-selected-local-source-transaction-only;command-and-quiescence-required';readonly authority_effect:'none';
}
export type CommerceServiceStorageExecutionV1=
 {readonly kind:'applied';readonly outcome:CommerceSqliteOutcomeV1}|
 {readonly kind:'not-claimed';readonly claim:Exclude<CommerceSqliteClaimV1,{readonly kind:'claimed'}>};
/** A fresh source transaction outcome only. Even a committed result is not a
 * provider dispatch permit; a protected command owner must inspect it. */
export type CommerceServiceStorageFreshExecutionV1=
 {readonly kind:'applied';readonly outcome:CommerceSqliteOutcomeV1;readonly authority_effect:'local-source-transaction-only'}|
 {readonly kind:'not-claimed';readonly claim:Exclude<CommerceSqliteFreshClaimV1,{readonly kind:'claimed'}>;readonly authority_effect:'none'};
export interface CommerceServiceStorageInspectionV1 {
 readonly kind:'original-source-service-storage/v1-candidate';readonly service:string;
 readonly source_capture_sha256:string;readonly family_sha256:string;readonly schema_sha256:string;
 readonly store_id:string;readonly native_basis_qualified:false;readonly imported_output_qualified:false;
 readonly bound_application_qualified:false;
 readonly qualification:'actual-source-selected-sqlite-component;outer-frame-and-command-principal-custody-required';
 readonly authority_effect:'none';
}
export interface CommerceFreshLocalObservationCommitV1 {
 readonly binding:Extract<CommerceWorkflowObservationCommitBindingV1,{kind:'local'}>;
 readonly operation:string;readonly transaction_path:string;
 readonly rows:readonly Readonly<{entity:string;key_index:number;key:CommerceNativeValue;value:CommerceNativeValue}>[];
}
export interface CommerceServiceStorageOwnerV1 {
 bindTransaction(operation:string,transaction:string,entry:string):Promise<CommerceServiceStorageTransactionV1>;
 bindLocalTransaction(selectedAuth:CommerceSelectedEntryAuthOwnerV1,child:CommerceOperationInvocationHandle,transaction:string):Promise<CommerceServiceStorageLocalTransactionV1>;
 inspectLocalTransaction(handle:CommerceServiceStorageLocalTransactionV1):CommerceServiceStorageLocalTransactionInspectionV1;
 apply(transaction:CommerceServiceStorageTransactionV1,key:CommerceSqliteCommandKeyV1,frame:Readonly<Record<string,CommerceNativeValue>>):CommerceServiceStorageExecutionV1;
 applyFreshGeneratedTransaction(runtime:CommerceGeneratedOperationRuntimeV1,token:CommerceGeneratedTransactionScopeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,transactionPath:string):Promise<CommerceServiceStorageFreshExecutionV1>;
 consumeFreshCommit(execution:CommerceServiceStorageFreshExecutionV1,runtime:CommerceGeneratedOperationRuntimeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,transactionPath:string):CommerceServiceStorageFreshCommitReceiptV1;
 inspectFreshLocalObservationCommit(receipt:object):CommerceFreshLocalObservationCommitV1;
 inspectFreshGeneratedCommit(receipt:object):Readonly<{kind:'committed';service:string;store_id:string;
  source_capture_sha256:string;operation:string;transaction_path:string;
  command_identity:CommerceSqliteCommandKeyV1;attempt:number;scope_sha256:string}>;
 inspectRecordedCommand(identity:CommerceSqliteCommandKeyV1):Readonly<{
  kind:'recorded'|'pending'|'unknown'|'missing'|'conflict'|'rolled-back';
  result?:CommerceNativeValue;service:string;store_id:string;source_capture_sha256:string}>;
 publishSelectedEvent(input:Readonly<{
  publication:CoreCommerceEventPublication;candidate:CoreCommerceEventPublicationCandidate;
  provenance:CoreCommerceEventProducerProvenance;proof:CoreCommerceEventProducerProof;
  delivery:CoreCommerceEventDelivery;acknowledgement:CoreCommerceEventReceiverAcknowledgement;
 }>):Promise<CommerceEventPublicationResultV1>;
 reconcileEventPublication(attempt:CommerceEventPublicationAttemptV1):CommerceEventPublicationResultV1;
 reconcilePublishedEvent(input:Readonly<{
  publication:CoreCommerceEventPublication;producerSource:CoreCommerceEventProducerSource;
  receiver:CommerceServiceStorageOwnerV1;occurrence_id:string;
 }>):Promise<CommerceEventPublicationResultV1>;
 inspect():CommerceServiceStorageInspectionV1;
  assertSelectedAssembly(selectedAuth:CommerceSelectedEntryAuthOwnerV1):void;
 inspectStoredRecord(entity:string,keyIndex:number,key:CommerceNativeValue):CommerceNativeValue|null;
 executeSourceQuery(read:import('./commerce-local-plan-owner-v1.js').CommerceLocalReadHandleV1,slots:Readonly<Record<string,CommerceNativeValue>>):Readonly<{query:string;rows:readonly Readonly<Record<string,CommerceNativeValue>>[];residual_required:boolean;requires_original_context_owner:boolean;qualification:'original-bound-sqlite-row-data-only'}>;
 querySlots(read:import('./commerce-local-plan-owner-v1.js').CommerceLocalReadHandleV1):readonly import('./commerce-sqlite-generation-v1.js').CommerceSqliteQuerySlotV1[];
 inspectSourceFailure(rollback:object):Readonly<{code:string;source_path:string;source_action:unknown}>|null;
 enqueueCommittedWorkflowEvent(binding:CommerceWorkflowCoordinationBindingV1,occurrenceId:string):Promise<CommerceWorkflowEnqueueResultV1>;
 scanReadyOutbox(binding:CommerceWorkflowCoordinationBindingV1,cursor:string|null,limit:number):Readonly<{occurrence_ids:readonly string[];next_cursor:string|null}>;
 scanReadySelectedEventOutbox(selection:Readonly<{entry:string;event_type:string;producer_service:string;
  producer_operation:string;outbox_entity:string;source_capture_sha256:string;
  native_family:'EventInboxOutbox'}>,cursor:string|null,limit:number):Readonly<{occurrence_ids:readonly string[];next_cursor:string|null}>;
 claimVacantWorkSchedule(binding:CommerceWorkflowCoordinationBindingV1,occurrenceId:string):CommerceWorkScheduleClaimResultV1;
 reclaimQuiescentWorkSchedule(binding:CommerceWorkflowCoordinationBindingV1,occurrenceId:string):CommerceWorkScheduleClaimResultV1;
 inspectWorkScheduleClaim(claim:CommerceWorkScheduleClaimV1):CommerceWorkScheduleClaimInspectionV1;
 assertWorkScheduleClaimCurrent(claim:CommerceWorkScheduleClaimV1):void;
 prepareClaimJournal(binding:CommerceWorkflowCoordinationBindingV1,claim:CommerceWorkScheduleClaimV1):CommerceClaimJournalResultV1;
 inspectClaimJournal(journal:CommerceClaimJournalV1):CommerceClaimJournalInspectionV1;
 assertClaimJournalCurrent(journal:CommerceClaimJournalV1):void;
 prepareWorkflowStepJournal(binding:CommerceWorkflowCoordinationBindingV1,schedule:CommerceWorkScheduleClaimV1,
  progress:CommerceWorkerProgressClaimV1,identities:CommerceWorkflowStepIdentityOwnerV1,
  identity:CommerceWorkflowStepIdentityHandleV1):CommerceWorkflowStepJournalResultV1;
 inspectWorkflowStepJournal(journal:CommerceWorkflowStepJournalV1):CommerceWorkflowStepJournalInspectionV1;
 assertWorkflowStepJournalCurrent(journal:CommerceWorkflowStepJournalV1):void;
 markWorkflowStepDispatched(binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceWorkflowStepJournalV1,
  identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1):CommerceWorkflowDispatchedStepJournalResultV1;
 inspectDispatchedWorkflowStepJournal(journal:CommerceWorkflowDispatchedStepJournalV1):CommerceWorkflowDispatchedStepJournalInspectionV1;
 assertDispatchedWorkflowStepJournalCurrent(journal:CommerceWorkflowDispatchedStepJournalV1):void;
 registerCommittedWorkerProgressClaim(binding:CommerceWorkflowCoordinationBindingV1,claim:CommerceWorkScheduleClaimV1,runtime:CommerceGeneratedOperationRuntimeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,receipt:object):CommerceWorkerProgressClaimV1;
 inspectWorkerProgressClaim(claim:CommerceWorkerProgressClaimV1):CommerceWorkerProgressClaimInspectionV1;
 assertWorkerProgressClaimCurrent(claim:CommerceWorkerProgressClaimV1):void;
 countStoredRecords(entity:string):bigint;
 reopen():Promise<void>;assertCurrent():void;close():void;
}
const owners=new WeakSet<object>();
export function assertCommerceServiceStorageOwnerV1(owner:CommerceServiceStorageOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original service-storage owner required');owner.assertCurrent();
}

/** Owns the exact generated repository and physical store for one selected
 * service. No caller-supplied SQL, native implementation, or evaluator. */
export async function createCommerceServiceStorageOwnerV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 plans:CommerceLocalPlanOwnerV1,families:CommerceFamilyOwnerV5,
 assemblyOwner:CommerceBindingAssemblyOwnerV1,assembly:CommerceBindingAssemblyHandle,
 serviceId:string,directory:string,mode:'create'|'reopen'='create',
):Promise<CommerceServiceStorageOwnerV1> {
 assertCommerceBindingAssemblyOwnerV1(assemblyOwner);assemblyOwner.assertCurrent(assembly);pin.assertCurrent();
 if(mode!=='create'&&mode!=='reopen')fail('InvalidContract',where,'supported service-storage open mode required');
 const selected=assemblyOwner.inspect(assembly),family=assemblyOwner.family(assembly);
 if(!selected.selection.services.some(s=>s.id===serviceId))fail('ForeignOwner',where,'service must belong to the original selected application');
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)fail('InvalidContract',where,'fresh absolute service-storage root required');
 const sqlite=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,family);
 const service=sqlite.bindService(serviceId);
 if(mode==='create')mkdirSync(directory,{mode:0o700});
 const bundle=mode==='create'
  ?sqlite.materialize(service,path.join(directory,'repository'))
  :sqlite.adoptExisting(service,path.join(directory,'repository'));
 const description=sqlite.inspectBundle(bundle);
 const repositoryModel=(await sqlite.loadDataComponent(bundle)).inspect();
 if(description.service!==serviceId||description.source_capture_sha256!==selected.selection.source_capture_sha256||description.family_sha256!==selected.selected_family_sha256)
  fail('ForeignOwner',where,'generated repository must match the exact selected application family');
 const storePath=path.join(directory,'store.sqlite');
 const runtime=await fixedSqliteRuntime();
 let store=await runtime.openCommerceSqliteUnitOfWorkV1(sqlite,bundle,storePath,mode);runtime.assertCommerceSqliteUnitOfWorkV1(store);
 const storeIdentity=store.inspect();
 let quiescence:ReturnType<typeof acquireCommerceWorkerQuiescenceV1>;
 try{quiescence=acquireCommerceWorkerQuiescenceV1({storePath,storeId:storeIdentity.store_id,
  schemaSha256:storeIdentity.schema_sha256},mode);}
 catch(error){store.close();throw error;}
 try {
 const identityDirectory=path.join(directory,mode==='create'?'identity':`identity-reopen-${randomUUID()}`);
 mkdirSync(identityDirectory,{mode:0o700});
 const programs=await createCommerceSqliteTransactionOwnerV1(sources,capture,stage,source,domain,baseline,plans,sqlite,bundle,identityDirectory);
 const entries=stage.moduleContracts(source).flatMap(m=>m.entries);
 const active=new WeakMap<object,{program:Awaited<ReturnType<typeof programs.bind>>;operation:string;entry:string}>();
 const local=new WeakMap<object,{selectedAuth:CommerceSelectedEntryAuthOwnerV1;child:CommerceOperationInvocationHandle;program:Awaited<ReturnType<typeof programs.bind>>;inspection:CommerceServiceStorageLocalTransactionInspectionV1}>();
 const freshCommits=new WeakMap<object,{runtime:CommerceGeneratedOperationRuntimeV1;selectedAuth:CommerceSelectedEntryAuthOwnerV1;invocation:CommerceOperationInvocationHandle;transactionPath:string;store:ServiceStore;epoch:number;receipt:CommerceServiceStorageFreshCommitReceiptV1}>();
 const generatedFreshCommitReceipts=new WeakMap<object,{store:ServiceStore;epoch:number;operation:string;
  transactionPath:string;sourceSha:string;identity:CommerceSqliteCommandKeyV1;local?:CommerceFreshLocalObservationCommitV1}>();
 const workerProgressReceipts=new WeakMap<object,{runtime:CommerceGeneratedOperationRuntimeV1;selectedAuth:CommerceSelectedEntryAuthOwnerV1;invocation:CommerceOperationInvocationHandle;transactionPath:string;store:ServiceStore;epoch:number;identity:Readonly<{journal_entry:string;command_id:string;request_fingerprint:string}>}>();
 const workerProgressClaims=new WeakMap<object,{binding:CommerceWorkflowCoordinationBindingV1;schedule:CommerceWorkScheduleClaimV1;store:ServiceStore;epoch:number;inspection:CommerceWorkerProgressClaimInspectionV1}>();
 const scheduleClaims=new WeakMap<object,{binding:CommerceWorkflowCoordinationBindingV1;store:ServiceStore;epoch:number;key:Readonly<Record<string,string>>;inspection:CommerceWorkScheduleClaimInspectionV1}>();
 const claimJournals=new WeakMap<object,{claim:CommerceWorkScheduleClaimV1;store:ServiceStore;epoch:number;key:Readonly<Record<string,string>>;inspection:CommerceClaimJournalInspectionV1}>();
 const stepJournals=new WeakMap<object,{binding:CommerceWorkflowCoordinationBindingV1;
  projection:CommerceWorkflowPreparedJournalProjectionV1;store:ServiceStore;epoch:number;
  inspection:CommerceWorkflowStepJournalInspectionV1}>();
 const dispatchedStepJournals=new WeakMap<object,{binding:CommerceWorkflowCoordinationBindingV1;
  store:ServiceStore;epoch:number;key:Readonly<{consumerEntryId:string;occurrenceId:string;stepName:string;commandId:string}>;
  inspection:CommerceWorkflowDispatchedStepJournalInspectionV1}>();
 type IngressIdentity={fingerprint:(event:CommerceNativeValue)=>string;dispose:()=>void};
 const ingressIdentities=new Map<string,Promise<IngressIdentity>>();
 const readyIngressIdentities=new Map<string,IngressIdentity>();
 let commandBindings:CommerceCommandIdentityBindingOwnerV1|undefined;
 let closed=false,storeEpoch=0;
 const current=()=>{
  if(closed)fail('DisposedOwner',where,'service storage closed');pin.assertCurrent();assemblyOwner.assertCurrent(assembly);
  // The original store reference is private and checked at open/reopen. This
  // one call checks its exact family/bundle relation, physical store/schema,
  // generated files and original source on every public boundary.
  store.assertRepository(sqlite,bundle);
  quiescence.assertCurrent();
 };
 const inspection:CommerceServiceStorageInspectionV1=coreFreeze({kind:'original-source-service-storage/v1-candidate',service:serviceId,
  source_capture_sha256:description.source_capture_sha256,family_sha256:description.family_sha256,schema_sha256:description.schema_sha256,
  store_id:store.inspect().store_id,native_basis_qualified:false,imported_output_qualified:false,bound_application_qualified:false,
  qualification:'actual-source-selected-sqlite-component;outer-frame-and-command-principal-custody-required',authority_effect:'none'});
 const technicalRecord=(row:object,entity:string):Readonly<Record<string,CommerceNativeValue>>=>{
  const actual=store.inspectRow(row);
  if(actual.entity!==entity||!actual.value||typeof actual.value!=='object'||Array.isArray(actual.value))
   fail('InvalidContract',where,'selected technical row has the wrong entity or shape');
  return actual.value as Readonly<Record<string,CommerceNativeValue>>;
 };
 const fieldPath=(expression:unknown):readonly string[]=>{
  const walk=(node:unknown,depth:number):string[]=>{
   if(depth>16||!node||typeof node!=='object'||Array.isArray(node))fail('UnsupportedCapability',where,'bounded original Workflow field path required');
   const part=node as Record<string,unknown>;
   if(part.kind==='name'&&typeof part.name==='string'){
    const fields=part.name.split('.');
    if(fields.length>16||fields.some(field=>!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(field)))
     fail('InvalidContract',where,'bounded original Workflow field path required');
    return fields;
   }
   if(part.kind==='field'&&typeof part.field==='string')return [...walk(part.value,depth+1),part.field];
   return fail('UnsupportedCapability',where,'original Workflow ingress identity needs a field path');
  };
  return walk(expression,0);
 };
 const originalEventField=(event:CommerceNativeValue,parameter:string,expression:unknown):CommerceNativeValue=>{
  const fields=fieldPath(expression);if(fields[0]!==parameter||fields.length<2)fail('InvalidContract',where,'Workflow ingress identity must project the original Event');
  let value:unknown=event;
  for(const field of fields.slice(1)){
   if(!value||typeof value!=='object'||Array.isArray(value)||!Object.hasOwn(value,field))fail('InvalidContract',where,'original Event ingress field is absent');
   value=(value as Record<string,unknown>)[field];
  }
  return value as CommerceNativeValue;
 };
 const ingressIdentity=async (binding:CommerceWorkflowCoordinationBindingV1):Promise<IngressIdentity>=>{
  const workflow=binding.inspect().workflow.name;
  let pending=ingressIdentities.get(workflow);
  if(!pending){
   pending=(async()=>{
    const sourceView=binding.inspect(),plan=semantics.inspect(semantic).workflows.find(w=>w.workflow.module+'.'+w.workflow.name===workflow);
    if(!plan||plan.service!==serviceId||plan.input_entry!==sourceView.workflow.input_entry)
     fail('ForeignOwner',where,'original selected Workflow semantic contract required');
    const eventType=sourceView.workflow.parameters[0]?.type;
    if(eventType?.kind!=='record')fail('InvalidContract',where,'original Workflow Event type required');
    const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
    const call=calls.bind(plan,'$.inbox_fingerprint.expression'),callView=calls.inspect(call);
    if(callView.observation.method!=='eventFingerprint'||callView.caller!==workflow||
     callView.event_schema?.name!==eventType.name)
     fail('InvalidContract',where,'original Workflow inbox must use its declared Event fingerprint call');
    const componentOwner=createCommerceIdentityComponentOwner(calls,stage,source,domain,baseline);
    const nativeDirectory=path.join(identityDirectory,'workflow-'+dataDigest({workflow}));mkdirSync(nativeDirectory,{mode:0o700});
    const component=await componentOwner.materialize([call],nativeDirectory);
    current();binding.assertCurrent();
    const identity=Object.freeze({fingerprint(event:CommerceNativeValue){
     current();binding.assertCurrent();const result=componentOwner.evaluateBoundParameters(component,call,[event]);
     if(!result.ok||typeof result.value!=='string')fail('InvalidContract',where,'original selected Event fingerprint rejected');
     return result.value;
    },dispose(){componentOwner.dispose(component);calls.dispose(call);}});
    readyIngressIdentities.set(workflow,identity);
    return identity;
   })();
   ingressIdentities.set(workflow,pending);
   void pending.catch(()=>{if(ingressIdentities.get(workflow)===pending)ingressIdentities.delete(workflow);});
  }
  return pending;
 };
 const scheduleClaimRow=(claim:CommerceWorkScheduleClaimV1)=>{
  current();const record=claim&&typeof claim==='object'?scheduleClaims.get(claim):undefined;
  if(!record)fail('ForeignOwner',where,'exact original WorkSchedule claim required');
  if(record.store!==store||record.epoch!==storeEpoch)fail('StaleOwner',where,'WorkSchedule claim predates store reopen');
  assertCommerceWorkflowCoordinationBindingV1(record.binding);
  const source=record.binding.inspect(),view=record.inspection;
  if(source.workflow.name!==view.workflow||source.owner_service!==serviceId||source.source_capture_sha256!==view.source_capture_sha256||
   source.workflow.input_entry!==view.consumer_entry_id||view.source_capture_sha256!==inspection.source_capture_sha256||
   view.store_id!==inspection.store_id||store.inspectDisposition(view.commit_receipt).kind!=='committed')
   fail('StaleOwner',where,'original selected WorkSchedule claim changed');
  const row=store.readRow(source.schedule_entity,0,record.key);
  if(!row)fail('StaleOwner',where,'committed WorkSchedule row is missing');
  const value=technicalRecord(row,source.schedule_entity),worker=value.workerOwner;
  if(value.consumerEntryId!==view.consumer_entry_id||value.occurrenceId!==view.occurrence_id||value.orderId!==view.order_id||
   value.state!=='Claimed'||!worker||typeof worker!=='object'||Array.isArray(worker)||
   (worker as Record<string,unknown>).kind!=='some'||(worker as Record<string,unknown>).value!==view.worker_id||
   value.workerEpoch!==view.worker_epoch||value.version!==view.schedule_version)
   fail('StaleOwner',where,'committed WorkSchedule ownership or version changed');
  current();return record;
 };
 const claimJournalRow=(journal:CommerceClaimJournalV1)=>{
  current();const record=journal&&typeof journal==='object'?claimJournals.get(journal):undefined;
  if(!record)fail('ForeignOwner',where,'exact original committed claim journal required');
  if(record.store!==store||record.epoch!==storeEpoch)fail('StaleOwner',where,'claim journal predates store reopen');
  scheduleClaimRow(record.claim);
  const view=record.inspection;
  if(view.store_id!==inspection.store_id||view.source_capture_sha256!==inspection.source_capture_sha256||
   store.inspectDisposition(view.commit_receipt).kind!=='committed')
   fail('StaleOwner',where,'original claim journal commit changed');
  const row=store.readRow(scheduleClaimRow(record.claim).binding.inspect().journal_entity,0,record.key);
  if(!row)fail('StaleOwner',where,'committed claim journal row missing');
  const actual=technicalRecord(row,scheduleClaimRow(record.claim).binding.inspect().journal_entity);
  if(actual.consumerEntryId!==view.consumer_entry_id||actual.occurrenceId!==view.occurrence_id||actual.orderId!==view.order_id||
   actual.stepName!==view.step_name||actual.commandId!==view.command_id||actual.targetEntryId!==view.target_entry_id||
   actual.requestFingerprint!==view.request_fingerprint||actual.phase!==view.phase||actual.workerOwner!==view.worker_id||
   actual.workerEpoch!==view.worker_epoch||actual.version!==1n||
   !actual.observation||typeof actual.observation!=='object'||Array.isArray(actual.observation)||
   (actual.observation as Record<string,unknown>).kind!=='none')
   fail('StaleOwner',where,'committed claim journal identity or phase changed');
  current();return record;
 };
 const workerProgressClaimRow=(claim:CommerceWorkerProgressClaimV1)=>{
  current();const record=claim&&typeof claim==='object'?workerProgressClaims.get(claim):undefined;
  if(!record)fail('ForeignOwner',where,'exact committed worker progress claim required');
  if(record.store!==store||record.epoch!==storeEpoch)fail('StaleOwner',where,'worker progress claim predates store reopen');
  const schedule=scheduleClaimRow(record.schedule),source=record.binding.inspect(),view=record.inspection;
  if(schedule.binding!==record.binding||source.workflow.name!==view.workflow||source.owner_service!==serviceId||
   source.source_capture_sha256!==view.source_capture_sha256||view.source_capture_sha256!==inspection.source_capture_sha256||
   view.store_id!==inspection.store_id||schedule.inspection.order_id!==view.order_id||
   schedule.inspection.worker_id!==view.worker_id||schedule.inspection.worker_epoch!==view.worker_epoch||
   store.inspectDisposition(view.commit_receipt).kind!=='committed')
   fail('StaleOwner',where,'original worker progress commit or schedule changed');
  const row=store.readRow(source.workflow.durable_state,0,{orderId:view.order_id});
  if(!row)fail('StaleOwner',where,'committed worker progress row missing');
  const progress=technicalRecord(row,source.workflow.durable_state),worker=progress.workerOwner;
  if(progress.orderId!==view.order_id||progress.workerEpoch!==view.worker_epoch||
   typeof progress.version!=='bigint'||progress.version<view.progress_version||
   !worker||typeof worker!=='object'||Array.isArray(worker)||
   (worker as Record<string,unknown>).kind!=='some'||(worker as Record<string,unknown>).value!==view.worker_id)
   fail('StaleOwner',where,'committed progress no longer belongs to the exact worker');
  return record;
 };
 const stepJournalRow=(journal:CommerceWorkflowStepJournalV1)=>{
  current();const record=journal&&typeof journal==='object'?stepJournals.get(journal):undefined;
  if(!record)fail('ForeignOwner',where,'exact committed Workflow StepJournal handle required');
  if(record.store!==store||record.epoch!==storeEpoch)fail('StaleOwner',where,'Workflow StepJournal predates store reopen');
  const projected=record.projection.recheck(),view=record.inspection;
  if(projected.workflow!==view.workflow||projected.source_capture_sha256!==view.source_capture_sha256||
   projected.store_id!==view.store_id||projected.consumer_entry_id!==view.consumer_entry_id||
   projected.occurrence_id!==view.occurrence_id||projected.order_id!==view.order_id||
   projected.step_name!==view.step_name||projected.target_entry_id!==view.target_entry_id||
   projected.command_id!==view.command_id||projected.request_fingerprint!==view.request_fingerprint||
   projected.worker_id!==view.worker_id||projected.worker_epoch!==view.worker_epoch||
   projected.progress_version!==view.progress_version||store.inspectDisposition(view.commit_receipt).kind!=='committed')
   fail('StaleOwner',where,'committed source StepJournal identity changed');
  const row=store.readRow(projected.journal_entity,0,projected.key);
  if(!row)fail('StaleOwner',where,'committed StepJournal row missing');
  // The projection was fully rechecked above. Validate the native row's exact
  // immutable request and worker as data, then close on current storage.
  const observed=inspectCommerceWorkflowJournalRowDataV1(projected.prepared,
   {id:projected.worker_id,epoch:projected.worker_epoch},technicalRecord(row,projected.journal_entity));
  if(observed.phase!=='Prepared'||!observed.same_current_worker||observed.version!==1n)
   fail('StaleOwner',where,'Prepared StepJournal phase or worker changed');
  current();return record;
 };
 const dispatchedStepJournalRow=(journal:CommerceWorkflowDispatchedStepJournalV1)=>{
  current();const record=journal&&typeof journal==='object'?dispatchedStepJournals.get(journal):undefined;
  if(!record)fail('ForeignOwner',where,'exact committed Dispatched StepJournal handle required');
  if(record.store!==store||record.epoch!==storeEpoch)fail('StaleOwner',where,'Dispatched StepJournal predates store reopen');
  record.binding.assertCurrent();const source=record.binding.inspect(),view=record.inspection;
  if(source.workflow.name!==view.workflow||source.journal_entity.length===0||
   source.source_capture_sha256!==view.source_capture_sha256||source.owner_service!==serviceId||
   view.store_id!==inspection.store_id||store.inspectDisposition(view.prepare_commit_receipt).kind!=='committed'||
   store.inspectDisposition(view.dispatch_commit_receipt).kind!=='committed')
   fail('StaleOwner',where,'committed Dispatched StepJournal source or receipts changed');
  const row=store.readRow(source.journal_entity,0,record.key);
  if(!row)fail('StaleOwner',where,'committed Dispatched StepJournal row missing');
  const observed=inspectCommerceWorkflowJournalRowDataV1({consumerEntryId:view.consumer_entry_id,
   occurrenceId:view.occurrence_id,orderId:view.order_id,stepName:view.step_name,commandId:view.command_id,
   targetEntryId:view.target_entry_id,requestFingerprint:view.request_fingerprint},
   {id:view.worker_id,epoch:view.worker_epoch},technicalRecord(row,source.journal_entity));
  if(observed.phase!=='Dispatched'||observed.version!==2n||!observed.same_current_worker||
   observed.observation_kind!=='none')fail('StaleOwner',where,'Dispatched StepJournal phase or worker changed');
  current();return record;
 };
 // Native SQLite decodes records with a null prototype. Compare their typed
 // values rather than object prototypes, while still distinguishing UInt64
 // 1 from string "1" in both command identities and recorded results.
 const typedDigest=(input:unknown):string=>{
   let nodes=0,bytes=0;const seen=new Set<object>();
   const visit=(value:unknown,depth:number):unknown=>{
    if(++nodes>65536||depth>32)fail('ResourceLimit',where,'bounded Event publication value required');
    if(value===null)return ['null'];
    if(typeof value==='boolean')return ['boolean',value];
    if(typeof value==='string'){
     bytes+=Buffer.byteLength(value);if(bytes>16777216)fail('ResourceLimit',where,'bounded Event publication value required');
     return ['string',value];
    }
    if(typeof value==='bigint'){
     if(value<0n||value>MAX_U64)fail('InvalidContract',where,'Event publication UInt64 required');
     return ['uint64',String(value)];
    }
    if(!value||typeof value!=='object'||host.isProxy(value)||seen.has(value))
     fail('InvalidContract',where,'plain acyclic Event publication value required');
    seen.add(value);
    try{
     if(Array.isArray(value)){
      if(Object.getPrototypeOf(value)!==Array.prototype||
       Reflect.ownKeys(value).length!==value.length+1)
       fail('InvalidContract',where,'dense Event publication list required');
      const items=[];
      for(let index=0;index<value.length;index++){
       const descriptor=Object.getOwnPropertyDescriptor(value,String(index));
       if(!descriptor||!Object.hasOwn(descriptor,'value')||!descriptor.enumerable)
        fail('InvalidContract',where,'plain Event publication list required');
       items.push(visit(descriptor.value,depth+1));
      }
      return ['list',items];
     }
     if(![Object.prototype,null].includes(Object.getPrototypeOf(value)))
      fail('InvalidContract',where,'plain Event publication record required');
     const keys=Reflect.ownKeys(value);
     if(keys.some(key=>typeof key!=='string'))
      fail('InvalidContract',where,'string Event publication fields required');
     const fields=[];
     for(const key of (keys as string[]).sort()){
      const descriptor=Object.getOwnPropertyDescriptor(value,key);
      if(!descriptor||!Object.hasOwn(descriptor,'value')||!descriptor.enumerable)
       fail('InvalidContract',where,'plain Event publication record required');
      bytes+=Buffer.byteLength(key);if(bytes>16777216)
       fail('ResourceLimit',where,'bounded Event publication value required');
      fields.push([key,visit(descriptor.value,depth+1)]);
     }
     return ['record',fields];
    }finally{seen.delete(value);}
   };
   return dataDigest({kind:'typed-Event-publication-value/v1-candidate',value:visit(input,0)});
  };
 const samePublicationValue=(observed:unknown,expected:unknown):boolean=>
  typedDigest(observed)===typedDigest(expected);
 const eventPublicationCommand=(selected:ReturnType<CoreCommerceEventPublication['inspect']>,
  id:string,expectedVersion:bigint,event:CommerceNativeValue,
  eventFingerprint:string,receipt:unknown)=>{
  const eventDigest=typedDigest(event),receiptDigest=typedDigest(receipt);
  const identity:CommerceSqliteCommandKeyV1=coreFreeze({
   logicalEntryId:selected.entry,principalId:selected.producer_service,
   commandId:'publish:'+id,
   transactionNamespace:dataDigest({kind:'EventInboxOutbox-publication/v1-candidate',
    source:selected.source_capture_sha256,family:selected.family_sha256,
    machine:selected.publication_machine,signal:selected.publication_signal,
    entry:selected.entry,entity:selected.outbox_entity}),
   fingerprint:dataDigest({kind:'original-Event-publication/v1-candidate',
    occurrence:id,event_digest:eventDigest,expected_version:String(expectedVersion),
    receiver_store:selected.receiver_store_id,
    event_fingerprint:eventFingerprint,receipt_digest:receiptDigest})});
  const result:CommerceNativeValue=coreFreeze({kind:'EventPublished',
   occurrenceId:id,entry:selected.entry,eventFingerprint,
   receiverStoreId:selected.receiver_store_id,
   receiptDigest,version:expectedVersion+1n});
  return {identity,result};
 };
 const eventPublications=new WeakMap<object,{store:ServiceStore;epoch:number;
  entity:string;id:string;nextVersion:bigint;identity:CommerceSqliteCommandKeyV1;
  expectedResult:CommerceNativeValue;ready:Readonly<Record<string,CommerceNativeValue>>}>();
 const reconcilePublication=(attempt:CommerceEventPublicationAttemptV1):CommerceEventPublicationResultV1=>{
  current();const issued=attempt&&typeof attempt==='object'?eventPublications.get(attempt):undefined;
  if(!issued||issued.store!==store||issued.epoch!==storeEpoch)
   fail('ForeignOwner',where,'original native Event publication attempt required');
  const journal=store.inspectCommand(issued.identity),row=store.readRow(issued.entity,0,{eventId:issued.id});
  if(journal.kind==='recorded'){
   if(!samePublicationValue(journal.result,issued.expectedResult)||!row)
    fail('StaleOwner',where,'recorded Event publication journal or row differs');
   const observed=technicalRecord(row,issued.entity);
   if(observed.state!=='Published'||observed.version!==issued.nextVersion||
    !isDeepStrictEqual({...observed,state:'Ready',version:issued.ready.version},
     {...issued.ready}))
    fail('StaleOwner',where,'recorded Event publication lacks exact Published row');
   current();return coreFreeze({kind:'recorded' as const,occurrence_id:issued.id,
    version:issued.nextVersion,receipt:null,authority_effect:'committed' as const});
  }
  if(journal.kind==='pending'||journal.kind==='unknown')
   return coreFreeze({kind:'indeterminate' as const,attempt,
    authority_effect:'indeterminate' as const});
  if(row){const observed=technicalRecord(row,issued.entity);
   if(observed.state==='Published'&&observed.version===issued.nextVersion)
    fail('StaleOwner',where,'Published Event row lacks exact recorded command journal');
  }
  return coreFreeze({kind:'conflict' as const,authority_effect:'none' as const});
 };
 const owner:CommerceServiceStorageOwnerV1=Object.freeze({
  async bindTransaction(operation:string,transaction:string,entry:string){
   current();const op=plans.bindOperation(operation),view=plans.inspectOperation(op);
   if(view.plan.service!==serviceId)fail('ForeignOwner',where,'Operation must belong to selected service');
   const declared=entries.find(e=>e.id===entry);
   if(!declared||declared.service!==serviceId||declared.invokes.role!=='Operation'||declared.invokes.module+'.'+declared.invokes.name!==operation)
    fail('ForeignOwner',where,'Entry must target the exact original Operation and service');
   const tx=view.transactions.find(t=>t.plan.name===transaction);
   if(!tx)fail('UnknownReference',where,'named original transaction absent');
   const plan=plans.bindTransaction(op,tx.path),program=await programs.bind(op,plan),record=programs.inspect(program);
   if(record.operation!==operation||record.service!==serviceId||record.source_capture_sha256!==inspection.source_capture_sha256||record.family_sha256!==inspection.family_sha256||record.schema_sha256!==inspection.schema_sha256)
    fail('ForeignOwner',where,'source transaction must match selected repository and service');
   const h=Object.freeze({kind:'original-source-service-storage-transaction/v1-candidate' as const});
   active.set(h,{program,operation,entry});current();return h;
  },
  async bindLocalTransaction(selectedAuth:CommerceSelectedEntryAuthOwnerV1,child:CommerceOperationInvocationHandle,transaction:string){
   current();assertCommerceSelectedEntryAuthOwnerV1(selectedAuth);selectedAuth.assertAssembly(assemblyOwner,assembly);
   const selectedView=selectedAuth.inspect(),view=selectedAuth.inspectInvocation(child);
   if(selectedView.source_capture_sha256!==inspection.source_capture_sha256||selectedView.family_sha256!==inspection.family_sha256||view.source_sha256!==inspection.source_capture_sha256||view.service!==serviceId||view.role!=='Operation'||view.depth<1||view.parent_call_path===null)
    fail('ForeignOwner',where,'local invocation must belong to exact selected source and service');
   selectedAuth.assertSelectedLocalChild(child,view.entry,view.operation);
   const root=entries.find(e=>e.id===view.entry);
   if(!root||root.service!==serviceId||root.invokes.role!=='Operation')
    fail('ForeignOwner',where,'local invocation must descend from an original same-service Operation Entry');
   const op=selectedAuth.operation(child),operation=plans.inspectOperation(op);
   if(operation.operation!==view.operation||operation.plan.service!==serviceId||operation.source_capture_sha256!==inspection.source_capture_sha256)
    fail('ForeignOwner',where,'selected child must carry the exact original Operation plan');
   const named=operation.transactions.find(t=>t.plan.name===transaction);
   if(!named)fail('UnknownReference',where,'named original local transaction absent');
   const plan=plans.bindTransaction(op,named.path),program=await programs.bind(op,plan),record=programs.inspect(program);
   selectedAuth.assertAssembly(assemblyOwner,assembly);selectedAuth.assertSelectedLocalChild(child,view.entry,view.operation);current();
   if(record.operation!==view.operation||record.transaction_path!==named.path||record.service!==serviceId||record.source_capture_sha256!==inspection.source_capture_sha256||record.family_sha256!==inspection.family_sha256||record.schema_sha256!==inspection.schema_sha256)
    fail('ForeignOwner',where,'local source transaction must match selected repository and service');
   const info:CommerceServiceStorageLocalTransactionInspectionV1=coreFreeze({service:serviceId,operation:view.operation,transaction,transaction_path:named.path,
    root_entry:view.entry,local_call_path:view.parent_call_path,local_depth:view.depth,source_capture_sha256:inspection.source_capture_sha256,
    family_sha256:inspection.family_sha256,schema_sha256:inspection.schema_sha256,
    qualification:'original-selected-local-source-transaction-only;command-and-quiescence-required',authority_effect:'none'});
   const h=Object.freeze({kind:'original-source-service-storage-local-transaction/v1-candidate' as const});
   local.set(h,{selectedAuth,child,program,inspection:info});return h;
  },
  inspectLocalTransaction(h:CommerceServiceStorageLocalTransactionV1){
   current();const row=h&&typeof h==='object'?local.get(h):undefined;
   if(!row)fail('ForeignOwner',where,'exact local transaction handle required');
   row.selectedAuth.assertAssembly(assemblyOwner,assembly);
   row.selectedAuth.assertSelectedLocalChild(row.child,row.inspection.root_entry,row.inspection.operation);
   const view=row.selectedAuth.inspectInvocation(row.child),program=programs.inspect(row.program);
   if(view.parent_call_path!==row.inspection.local_call_path||view.depth!==row.inspection.local_depth||view.service!==serviceId||
    program.operation!==row.inspection.operation||program.transaction_path!==row.inspection.transaction_path||program.service!==serviceId||program.source_capture_sha256!==inspection.source_capture_sha256||program.family_sha256!==inspection.family_sha256||program.schema_sha256!==inspection.schema_sha256)
    fail('StaleOwner',where,'selected local transaction or child invocation changed');
   return row.inspection;
  },
  apply(h:CommerceServiceStorageTransactionV1,key:CommerceSqliteCommandKeyV1,frame:Readonly<Record<string,CommerceNativeValue>>){
   current();const row=h&&typeof h==='object'?active.get(h):undefined;if(!row)fail('ForeignOwner',where,'exact selected transaction handle required');
   const program=programs.inspect(row.program);
   if(program.operation!==row.operation||program.service!==serviceId||program.source_capture_sha256!==inspection.source_capture_sha256)fail('StaleOwner',where,'selected transaction changed');
   const names=['logicalEntryId','principalId','commandId','fingerprint','transactionNamespace'];
   if(!key||typeof key!=='object'||host.isProxy(key)||![Object.prototype,null].includes(Object.getPrototypeOf(key))||Reflect.ownKeys(key).length!==names.length)
    fail('InvalidContract',where,'closed component command key required');
   const descriptors=Object.getOwnPropertyDescriptors(key);
   if(names.some(name=>!Object.hasOwn(descriptors,name)||!descriptors[name]!.enumerable||!Object.hasOwn(descriptors[name]!,'value')))
    fail('InvalidContract',where,'inert component command key required');
   if(key.logicalEntryId!==row.entry)fail('ForeignOwner',where,'command must identify the original Entry');
   if(key.transactionNamespace!==deriveCommerceCommandTransactionNamespaceV1(program.operation,program.plan.name))
    fail('ForeignOwner',where,'command must identify the exact source-declared transaction');
   const claim=store.claimCommand(key);
   if(claim.kind!=='claimed')return coreFreeze({kind:'not-claimed' as const,claim});
   const outcome=store.applySourceTransaction(programs,row.program,claim.command,frame);
   current();return coreFreeze({kind:'applied' as const,outcome});
  },
  async applyFreshGeneratedTransaction(generated:CommerceGeneratedOperationRuntimeV1,token:CommerceGeneratedTransactionScopeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,transactionPath:string){
   current();assertCommerceGeneratedOperationRuntimeV1(generated);assertCommerceSelectedEntryAuthOwnerV1(selectedAuth);
   generated.assertStorage(owner);selectedAuth.assertAssembly(assemblyOwner,assembly);
   // The generated runtime owns this token. Consume it before any await or
   // native journal claim, so failed validation cannot turn it into a retry.
   const scope=generated.consumeTransactionScope(token,selectedAuth,invocation,transactionPath);
   const selectedView=selectedAuth.inspect(),invocationView=selectedAuth.inspectInvocation(invocation),op=selectedAuth.operation(invocation),operation=plans.inspectOperation(op);
   if(invocationView.role!=='Operation'||invocationView.service!==serviceId||invocationView.source_sha256!==inspection.source_capture_sha256||
    selectedView.source_capture_sha256!==inspection.source_capture_sha256||selectedView.family_sha256!==inspection.family_sha256||
    operation.operation!==invocationView.operation||operation.plan.service!==serviceId||operation.source_capture_sha256!==inspection.source_capture_sha256)
    fail('ForeignOwner',where,'generated transaction must retain selected source, service and Operation');
   const generatedView=generated.inspect();
   if(generatedView.operation!==operation.operation||generatedView.service!==serviceId||
    generatedView.source_capture_sha256!==inspection.source_capture_sha256)
    fail('ForeignOwner',where,'generated transaction differs from selected Operation');
   const transaction=operation.transactions.find(t=>t.path===transactionPath);
   if(!transaction)fail('UnknownReference',where,'exact original transaction path required');
   const openStore=store;
   const plan=plans.bindTransaction(op,transactionPath),program=await programs.bind(op,plan);
   current();if(store!==openStore)fail('StaleOwner',where,'store reopened while binding fresh source transaction');
   const programView=programs.inspect(program);
   if(programView.operation!==operation.operation||programView.transaction_path!==transactionPath||programView.service!==serviceId||
    programView.source_capture_sha256!==inspection.source_capture_sha256||programView.family_sha256!==inspection.family_sha256||programView.schema_sha256!==inspection.schema_sha256)
    fail('ForeignOwner',where,'generated source transaction must match original selected repository');
   const workerIdentity=selectedAuth.workerCommandIdentity(invocation,transactionPath);
   let identity:Readonly<{logicalEntryId:string;principalId:string;commandId:string;fingerprint:string;transactionNamespace:string}>;
   if(workerIdentity){
    const principal=selectedAuth.principalIdentity(invocation);
    if(principal.kind!=='service'||principal.id!==serviceId||workerIdentity.journal_entry!==invocationView.entry||
     typeof workerIdentity.command_id!=='string'||!workerIdentity.command_id||Buffer.byteLength(workerIdentity.command_id)>256||
     typeof workerIdentity.request_fingerprint!=='string'||! /^[a-f0-9]{64}$/.test(workerIdentity.request_fingerprint))
     fail('ForeignOwner',where,'committed Workflow claim must identify the selected service command');
    identity=coreFreeze({logicalEntryId:workerIdentity.journal_entry,principalId:principal.id,
     commandId:workerIdentity.command_id,fingerprint:workerIdentity.request_fingerprint,
     transactionNamespace:deriveCommerceCommandTransactionNamespaceV1(operation.operation,transaction.plan.name)});
   }else{
    commandBindings??=createCommerceCommandIdentityBindingOwnerV1(sources,capture,semantics,semantic,domain,baseline,plans,assemblyOwner,assembly);
    const binding=commandBindings.bind(invocationView.entry,op,transactionPath);
    const projected=projectCommerceCommandIdentityDataV1(commandBindings,binding,selectedAuth,invocation,plans,programs,program,scope);
     // Projection provenance is not part of the native journal key. Retain the
     // exact same closed tuple used for the claim and later receipt inspection.
     identity=coreFreeze({logicalEntryId:projected.logicalEntryId,principalId:projected.principalId,
      commandId:projected.commandId,fingerprint:projected.fingerprint,
      transactionNamespace:projected.transactionNamespace});
   }
   // The generated transaction port holds the complete lexical environment.
   // The original native program accepts only its declared free-variable frame.
   const checkedScope=programs.copySourceScope(program,scope),frame:Record<string,CommerceNativeValue>=Object.create(null);
   for(const field of programView.frame)frame[field.name]=checkedScope[field.name]!;
   Object.freeze(frame);
   current();selectedAuth.inspectInvocation(invocation);if(store!==openStore)fail('StaleOwner',where,'store changed before fresh claim');
   const claim=store.claimFreshCommand({logicalEntryId:identity.logicalEntryId,principalId:identity.principalId,commandId:identity.commandId,fingerprint:identity.fingerprint,transactionNamespace:identity.transactionNamespace});
   if(claim.kind!=='claimed')return coreFreeze({kind:'not-claimed' as const,claim,authority_effect:'none' as const});
   const observationInvocation=selectedAuth.isWorkflowObservationInvocation(invocation);
   let localCommitBinding:Extract<CommerceWorkflowObservationCommitBindingV1,{kind:'local'}>|undefined;
   const apply=()=>{
    let companion:Parameters<ServiceStore['applySourceTransaction']>[5];
    if(observationInvocation){
     // The selected invocation, not an input field or a shaped data record,
     // supplies the source-bound original journal identity at the effect edge.
     const checked:CommerceWorkflowObservationCommitBindingV1=
      selectedAuth.inspectWorkflowObservationCommitBinding(invocation,transactionPath);
     if(checked.kind==='local')localCommitBinding=checked;
     if(checked.kind==='dispatched-step'){
      if(checked.source_capture_sha256!==inspection.source_capture_sha256||
       checked.store_id!==inspection.store_id||checked.observation_entry_id!==invocationView.entry||
       checked.order_id.length===0||!programView.plan.participants.includes(checked.journal_entity))
       fail('ForeignOwner',where,'checked observation must match declared source StepJournal participant');
      const row=store.readRow(checked.journal_entity,0,checked.journal_key);
      if(!row)fail('StaleOwner',where,'original Dispatched StepJournal missing before observation');
      const original={consumerEntryId:checked.consumer_entry_id,occurrenceId:checked.occurrence_id,
       orderId:checked.order_id,stepName:checked.step_name,commandId:checked.command_id,
       targetEntryId:checked.target_entry_id,requestFingerprint:checked.request_fingerprint};
      const observed=inspectCommerceWorkflowJournalRowDataV1(original,
       {id:checked.journal_worker_id,epoch:checked.journal_worker_epoch},
       technicalRecord(row,checked.journal_entity));
      if(observed.phase!=='Dispatched'||observed.version!==2n||
       observed.observation_kind!=='none'||!observed.same_current_worker)
       fail('StaleOwner',where,'original StepJournal must still be Dispatched at version 2');
      companion=coreFreeze({kind:'observed-step-journal' as const,entity:checked.journal_entity,row,
       expected_version:2n as const,changes:coreFreeze({phase:'Observed' as const,
        observation:coreFreeze({kind:'some' as const,value:checked.observation as CommerceNativeValue}),
        version:3n as const})});
     }
    }
    return store.applySourceTransaction(programs,program,claim.command,frame,
     {owner:selectedAuth,invocation},companion);
   };
   const outcome=workerIdentity||observationInvocation?
    selectedAuth.withWorkerTransaction(invocation,owner,transactionPath,apply):apply();
   current();const execution=coreFreeze({kind:'applied' as const,outcome,authority_effect:'local-source-transaction-only' as const});
   if(outcome.kind==='committed'){
    freshCommits.set(execution,{runtime:generated,selectedAuth,invocation,transactionPath,store:openStore,epoch:storeEpoch,receipt:outcome.receipt as CommerceServiceStorageFreshCommitReceiptV1});
    let localCommit:CommerceFreshLocalObservationCommitV1|undefined;
    if(localCommitBinding){
     const result=outcome.result;
     if(!result||typeof result!=='object'||Array.isArray(result))fail('InvalidContract',where,'native local commit row aliases required');
     const rows:CommerceFreshLocalObservationCommitV1['rows'][number][]=[];
     for(const step of programView.plan.body){
      if(step.kind!=='mutation'||step.operation!=='update')continue;
      const table=(repositoryModel.tables as readonly CommerceSqliteTableV1[]).find(table=>table.entity===step.target),value=(result as Readonly<Record<string,CommerceNativeValue>>)[step.binding];
      if(!table||!value||typeof value!=='object'||Array.isArray(value))fail('InvalidContract',where,'original native local mutation alias required');
      const record=value as Readonly<Record<string,CommerceNativeValue>>;
      const key=Object.fromEntries(table!.keys[0]!.map(field=>[field,record[field]!]));
      rows.push(coreFreeze({entity:step.target,key_index:0,key:coreFreeze(key),value:value!}));
     }
     if(rows.length<2)fail('InvalidContract',where,'local observation requires original committed row aliases');
     localCommit=coreFreeze({binding:localCommitBinding,operation:generatedView.operation,transaction_path:transactionPath,rows});
    }
    generatedFreshCommitReceipts.set(outcome.receipt,{store:openStore,epoch:storeEpoch,
     operation:generatedView.operation,transactionPath,sourceSha:generatedView.source_capture_sha256,
     identity,...localCommit?{local:localCommit}:{}});
   }
   if(workerIdentity&&outcome.kind==='committed')workerProgressReceipts.set(outcome.receipt,{runtime:generated,selectedAuth,invocation,transactionPath,store:openStore,epoch:storeEpoch,identity:workerIdentity});
   return execution;
  },
  consumeFreshCommit(execution:CommerceServiceStorageFreshExecutionV1,generated:CommerceGeneratedOperationRuntimeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,transactionPath:string){
   current();assertCommerceGeneratedOperationRuntimeV1(generated);assertCommerceSelectedEntryAuthOwnerV1(selectedAuth);
   generated.assertStorage(owner);selectedAuth.assertAssembly(assemblyOwner,assembly);
   const row=execution&&typeof execution==='object'?freshCommits.get(execution):undefined;
   if(!row||row.runtime!==generated||row.selectedAuth!==selectedAuth||row.invocation!==invocation||row.transactionPath!==transactionPath)
    fail('ForeignOwner',where,'exact fresh generated commit and invocation required');
   if(row.store!==store||row.epoch!==storeEpoch)fail('StaleOwner',where,'fresh commit was issued before store reopen or close');
   selectedAuth.inspectInvocation(invocation);
   if(store.inspectDisposition(row.receipt).kind!=='committed')fail('ForeignOwner',where,'original native commit receipt required');
   freshCommits.delete(execution);
   return row.receipt;
  },
  inspectFreshGeneratedCommit(receipt:object){
   current();const row=receipt&&typeof receipt==='object'?generatedFreshCommitReceipts.get(receipt):undefined;
   if(!row||row.store!==store||row.epoch!==storeEpoch||row.sourceSha!==inspection.source_capture_sha256)
    fail('ForeignOwner',where,'original fresh generated commit receipt required');
   const disposition=store.inspectDisposition(receipt);
   if(disposition.kind!=='committed')fail('ForeignOwner',where,'original native commit is not committed');
   if(store.inspectCommand(row.identity).kind!=='recorded')
    fail('ForeignOwner',where,'original generated command journal is not committed');
   current();return coreFreeze({kind:'committed' as const,service:serviceId,store_id:inspection.store_id,
    source_capture_sha256:row.sourceSha,operation:row.operation,transaction_path:row.transactionPath,
    command_identity:row.identity,
    attempt:disposition.attempt,scope_sha256:disposition.scope_sha256});
  },
  inspectFreshLocalObservationCommit(receipt:object){
   owner.inspectFreshGeneratedCommit(receipt);
   const row=generatedFreshCommitReceipts.get(receipt);
   if(!row?.local)fail('ForeignOwner',where,'original fresh local observation receipt required');
   return row!.local!;
  },
  inspectRecordedCommand(identity:CommerceSqliteCommandKeyV1){
   current();const observation=store.inspectCommand(identity);current();
   return coreFreeze({...observation,service:serviceId,store_id:inspection.store_id,
    source_capture_sha256:inspection.source_capture_sha256});
  },
  async publishSelectedEvent({publication,candidate,provenance,proof,delivery,acknowledgement}:
   Parameters<CommerceServiceStorageOwnerV1['publishSelectedEvent']>[0]){
   current();const [{assertCoreCommerceEventPublication},
    {assertCoreCommerceEventProducerProvenance},{assertCoreCommerceEventDelivery}]=await Promise.all([
     import('../generic/core-commerce-event-publication.js'),
     import('../generic/core-commerce-event-producer-provenance.js'),
     import('../generic/core-commerce-event-delivery.js')]);
   assertCoreCommerceEventPublication(publication);
   assertCoreCommerceEventProducerProvenance(provenance);
   assertCoreCommerceEventDelivery(delivery);
   const selected=publication.inspect(),proposal=publication.inspectCandidate(candidate),
    emitted=provenance.inspectProof(proof),received=delivery.inspectAcknowledgement(acknowledgement);
   if(selected.producer_service!==serviceId||selected.producer_store_id!==inspection.store_id||
    selected.source_capture_sha256!==inspection.source_capture_sha256||
    selected.family_sha256!==inspection.family_sha256||
    proposal.entry!==selected.entry||proposal.outbox_entity!==selected.outbox_entity||
    proposal.expected_state!==selected.ready_state||proposal.next_state!==selected.published_state||
    proposal.next_version!==proposal.expected_version+1n||
    // The producer Operation and receiver Event have distinct Entries. Match
    // the provenance to the source-selected producer Operation, not the Event Entry.
    emitted.operation!==selected.producer_operation||
    emitted.occurrence_id!==proposal.occurrence_id||
    emitted.outbox_entity!==selected.outbox_entity||
    emitted.producer_store_id!==inspection.store_id||
    emitted.source_capture_sha256!==inspection.source_capture_sha256||
    received.entry!==selected.entry||received.occurrence_id!==proposal.occurrence_id||
    received.producer_store_id!==inspection.store_id||
    received.receiver_store_id!==selected.receiver_store_id||
    received.source_capture_sha256!==inspection.source_capture_sha256||
    typeof received.event_fingerprint!=='string'||
    !/^[a-f0-9]{64}$/.test(received.event_fingerprint))
    fail('ForeignOwner',where,'selected producer, receiver ACK and publication transition differ');
   const row=store.readRow(selected.outbox_entity,0,{eventId:proposal.occurrence_id});
   if(!row)fail('StaleOwner',where,'original Ready producer outbox missing');
   const ready=technicalRecord(row,selected.outbox_entity);
   if(ready.eventId!==proposal.occurrence_id||ready.state!==proposal.expected_state||
    ready.version!==proposal.expected_version||ready.event===undefined)
    fail('StaleOwner',where,'original producer outbox changed before publication');
   const {identity,result:expectedResult}=eventPublicationCommand(selected,
    proposal.occurrence_id,proposal.expected_version,ready.event as CommerceNativeValue,
    received.event_fingerprint,received.receipt);
   const attempt:CommerceEventPublicationAttemptV1=Object.freeze({
    kind:'original-native-event-publication-attempt/v1-candidate'});
   eventPublications.set(attempt,{store,epoch:storeEpoch,entity:selected.outbox_entity,
    id:proposal.occurrence_id,nextVersion:proposal.next_version,identity,
    expectedResult,ready});
   const claimed=store.claimCommand(identity);
   if(claimed.kind==='recorded')return reconcilePublication(attempt);
   if(claimed.kind==='pending'||claimed.kind==='unknown')
    return coreFreeze({kind:'indeterminate' as const,attempt,
     authority_effect:'indeterminate' as const});
   if(claimed.kind==='conflict')
    return coreFreeze({kind:'conflict' as const,authority_effect:'none' as const});
   if(claimed.kind!=='claimed')
    return coreFreeze({kind:'unavailable' as const,authority_effect:'none' as const});
   const result=store.apply(claimed.command,[{kind:'update',row,
    expected_version:proposal.expected_version,
    changes:coreFreeze({state:proposal.next_state,version:proposal.next_version})}],
    expectedResult);
   if(result.kind==='committed'){
    if(store.inspectDisposition(result.receipt).kind!=='committed'||
     !samePublicationValue(result.result,expectedResult))
     fail('StaleOwner',where,'native Event publication receipt or result changed');
    const reconciled=reconcilePublication(attempt);
    if(reconciled.kind!=='recorded')
     fail('StaleOwner',where,'committed Event publication lacks recorded row and journal');
    return coreFreeze({kind:'published' as const,occurrence_id:proposal.occurrence_id,
     version:proposal.next_version,receipt:result.receipt,authority_effect:'committed' as const});
   }
   if(result.kind==='indeterminate')return reconcilePublication(attempt);
   if(result.kind==='version-conflict'||result.kind==='unique-conflict')
    return coreFreeze({kind:'conflict' as const,authority_effect:'none' as const});
   return coreFreeze({kind:'unavailable' as const,authority_effect:'none' as const});
  },
  reconcileEventPublication:reconcilePublication,
  async reconcilePublishedEvent({publication,producerSource,receiver,occurrence_id}:
   Parameters<CommerceServiceStorageOwnerV1['reconcilePublishedEvent']>[0]){
   current();const [{assertCoreCommerceEventPublication},
    {assertCoreCommerceEventProducerSource}]=await Promise.all([
     import('../generic/core-commerce-event-publication.js'),
     import('../generic/core-commerce-event-producer-source.js')]);
   assertCoreCommerceEventPublication(publication);
   assertCoreCommerceEventProducerSource(producerSource);
   assertCommerceServiceStorageOwnerV1(receiver);
   const selected=publication.inspect(),sourcePlan=producerSource.inspect(),receiverStore=receiver.inspect();
   if(selected.producer_service!==serviceId||selected.producer_store_id!==inspection.store_id||
    selected.family_sha256!==inspection.family_sha256||
    selected.source_capture_sha256!==inspection.source_capture_sha256||
    sourcePlan.service!==serviceId||sourcePlan.operation!==selected.producer_operation||
    sourcePlan.outbox_entity!==selected.outbox_entity||
    sourcePlan.event_type!==selected.event_type||
    sourcePlan.source_capture_sha256!==inspection.source_capture_sha256||
    receiverStore.service!==selected.receiver_service||
    receiverStore.store_id!==selected.receiver_store_id||
    receiverStore.source_capture_sha256!==inspection.source_capture_sha256||
    receiverStore.family_sha256!==inspection.family_sha256||
    typeof occurrence_id!=='string'||!occurrence_id||Buffer.byteLength(occurrence_id)>128)
    fail('ForeignOwner',where,'reopened source-selected Event publication and stores required');
   const publishedRow=store.readRow(selected.outbox_entity,0,{eventId:occurrence_id});
   if(!publishedRow)return coreFreeze({kind:'conflict' as const,authority_effect:'none' as const});
   const published=technicalRecord(publishedRow,selected.outbox_entity),
    version=published.version;
   if(published.eventId!==occurrence_id||published.state!=='Published'||
    typeof version!=='bigint'||version<2n||version>MAX_U64||
    !published.event||typeof published.event!=='object'||Array.isArray(published.event))
    return coreFreeze({kind:'conflict' as const,authority_effect:'none' as const});
   const event=published.event as Readonly<Record<string,CommerceNativeValue>>,
    metadata=event.metadata;
   if(!metadata||typeof metadata!=='object'||Array.isArray(metadata)||
    (metadata as Record<string,unknown>).eventId!==occurrence_id||
    (metadata as Record<string,unknown>).producer!==serviceId||
    typeof (metadata as Record<string,unknown>).commandId!=='string')
    fail('StaleOwner',where,'Published outbox lacks original Event metadata');
   const commandId=(metadata as Record<string,unknown>).commandId;
   if(typeof commandId!=='string'||!commandId)
    fail('StaleOwner',where,'Published Event command identity missing');
   const actionValue=store.readRow(sourcePlan.action_entity,0,{commandId});
   if(!actionValue)fail('StaleOwner',where,'Published Event lacks original action result');
   const action=technicalRecord(actionValue,sourcePlan.action_entity),
    ready={...published,state:'Ready',version:version-1n};
   if(action.commandId!==commandId||action.orderId!==event.orderId||
    typeof action.requestFingerprint!=='string'||
    !/^[a-f0-9]{64}$/.test(action.requestFingerprint))
    fail('StaleOwner',where,'Published Event action identity changed');
   const producerIdentity:CommerceSqliteCommandKeyV1=coreFreeze({
    logicalEntryId:sourcePlan.entry,principalId:sourcePlan.service,
    commandId,fingerprint:action.requestFingerprint,
    transactionNamespace:deriveCommerceCommandTransactionNamespaceV1(
     sourcePlan.operation,sourcePlan.transaction)}),
    producerJournal=store.inspectCommand(producerIdentity);
   if(producerJournal.kind!=='recorded'||
    !producerJournal.result||typeof producerJournal.result!=='object'||
    Array.isArray(producerJournal.result))
    fail('StaleOwner',where,'Published Event lacks original recorded producer command');
   const aliases=producerJournal.result as Record<string,unknown>;
   if(!samePublicationValue(aliases[sourcePlan.event_binding],event)||
    !samePublicationValue(aliases[sourcePlan.outbox_binding],ready)||
    !samePublicationValue(aliases[sourcePlan.action_binding],action))
    fail('StaleOwner',where,'Published Event differs from original producer command aliases');
   const inbox=receiver.inspectStoredRecord(selected.consumer_inbox_entity,0,
    {consumerEntryId:selected.entry,occurrenceId:occurrence_id});
   if(!inbox||typeof inbox!=='object'||Array.isArray(inbox))
    fail('StaleOwner',where,'Published Event lacks original receiver inbox');
   const received=inbox as Record<string,unknown>;
   if(received.consumerEntryId!==selected.entry||received.occurrenceId!==occurrence_id||
    typeof received.eventFingerprint!=='string'||
    !/^[a-f0-9]{64}$/.test(received.eventFingerprint)||
    !Object.hasOwn(received,'receipt'))
    fail('StaleOwner',where,'Published Event receiver inbox identity changed');
   const {identity,result}=eventPublicationCommand(selected,occurrence_id,version-1n,
    published.event,received.eventFingerprint,received.receipt),
    journal=store.inspectCommand(identity);
   if(journal.kind!=='recorded'||!samePublicationValue(journal.result,result))
    fail('StaleOwner',where,'Published Event lacks exact native publication command');
   current();receiver.assertCurrent();return coreFreeze({kind:'recorded' as const,
    occurrence_id,version,receipt:null,authority_effect:'committed' as const});
  },
  inspect(){current();return inspection;},
  assertSelectedAssembly(selectedAuth:CommerceSelectedEntryAuthOwnerV1){current();if(!isCommerceSelectedEntryAuthOwnerV1(selectedAuth))fail('ForeignOwner',where,'original selected Entry/Auth owner required');selectedAuth.assertAssembly(assemblyOwner,assembly);},
  inspectStoredRecord(entity:string,keyIndex:number,key:CommerceNativeValue){current();const row=store.readRow(entity,keyIndex,key);const result=row?store.inspectRow(row).value:null;current();return result;},
  executeSourceQuery(read:import('./commerce-local-plan-owner-v1.js').CommerceLocalReadHandleV1,slots:Readonly<Record<string,CommerceNativeValue>>){current();const view=plans.inspectRead(read);if(view.plan.kind!=='local'||view.plan.service!==serviceId||view.source_capture_sha256!==inspection.source_capture_sha256)fail('ForeignOwner',where,'exact local source Query and selected service required');const query=sqlite.bindQuery(service,read),result=store.executeBoundQuery(sqlite,bundle,query,slots);if(result.query!==view.query)fail('InvalidContract',where,'native query result must retain original source identity');current();return result;},
  querySlots(read:import('./commerce-local-plan-owner-v1.js').CommerceLocalReadHandleV1){current();const view=plans.inspectRead(read);if(view.plan.kind!=='local'||view.plan.service!==serviceId||view.source_capture_sha256!==inspection.source_capture_sha256)fail('ForeignOwner',where,'exact local Query required');return sqlite.inspectQuery(sqlite.bindQuery(service,read)).slots;},
  inspectSourceFailure(rollback:object){current();const disposition=store.inspectDisposition(rollback);if(disposition.kind!=='rolled-back')fail('ForeignOwner',where,'original native rollback required');current();return disposition.source_failure;},
  scanReadyOutbox(binding:CommerceWorkflowCoordinationBindingV1,cursor:string|null,limit:number){
   current();assertCommerceWorkflowCoordinationBindingV1(binding);const source=binding.inspect();
   if(source.owner_service!==serviceId||source.workflow.input_producer!==serviceId||
     source.source_capture_sha256!==inspection.source_capture_sha256)
    fail('ForeignOwner',where,'selected producer Workflow and service storage required for outbox scan');
   const page=store.scanRows(source.input_outbox_entity,cursor,limit),ids:string[]=[];
   for(const value of page.rows){
    if(!value||typeof value!=='object'||Array.isArray(value))fail('InvalidContract',where,'original outbox record required');
    const record=value as Record<string,CommerceNativeValue>;
    if(record.state!=='Ready')continue;
    if(typeof record.eventId!=='string'||!record.eventId.length||Buffer.byteLength(record.eventId)>128)
     fail('InvalidContract',where,'bounded original outbox occurrence required');
    ids.push(record.eventId);
   }
   current();binding.assertCurrent();return coreFreeze({occurrence_ids:ids,next_cursor:page.next_cursor});
  },
  scanReadySelectedEventOutbox(selection:Readonly<{entry:string;event_type:string;producer_service:string;
   producer_operation:string;outbox_entity:string;source_capture_sha256:string;
   native_family:'EventInboxOutbox'}>,cursor:string|null,limit:number){
   current();
   if(!selection||typeof selection!=='object'||Array.isArray(selection)||
    selection.producer_service!==serviceId||selection.source_capture_sha256!==inspection.source_capture_sha256||
    selection.native_family!=='EventInboxOutbox')
    fail('ForeignOwner',where,'original source-selected producer Event outbox required');
   const checked=semantics.inspect(semantic),model=sources.inspect(capture).reconstruction,
    entry=checked.entries.find(row=>row.id===selection.entry),
    event=checked.pure.value_declarations.find(row=>row.name===selection.event_type&&row.role==='Event'),
    outbox=model.modules.flatMap(module=>module.declarations).find(row=>row.id===selection.outbox_entity);
   if(!entry||entry.interaction!=='event'||entry.access.principal_kind!=='service'||
    entry.access.producer!==serviceId||entry.access.caller!==serviceId||entry.service===serviceId||
    entry.parameters.length!==1||entry.parameters[0]!.type.kind!=='record'||
    entry.parameters[0]!.type.name!==selection.event_type||!event||event.event_version!==1||
    !outbox||outbox.surface!=='Entity'||!isDeepStrictEqual(outbox.identity,['eventId'])||
    model.ownership.find(row=>row.declaration===outbox.id)?.service!==serviceId)
    fail('ForeignOwner',where,'selected Entry, Event, and producer outbox must come from original source');
   const types=createCoreValueTypes(model),eventField=outbox.fields.find(row=>row.name==='event'),
    stateField=outbox.fields.find(row=>row.name==='state'),versionField=outbox.fields.find(row=>row.name==='version');
   if(!eventField||!stateField||!versionField||
    !sameCoreValueType(types.type(outbox.module,eventField.type,eventField.span),{kind:'record',name:event.name})||
    types.type(outbox.module,stateField.type,stateField.span).kind!=='enum'||
    !sameCoreValueType(types.type(outbox.module,versionField.type,versionField.span),{kind:'UInt64'}))
    fail('ForeignOwner',where,'selected Event outbox schema must come from original source');
   const transactions=(steps:readonly OperationControlStepV1[]):readonly TransactionPlanV1[]=>{
    const found:TransactionPlanV1[]=[];
    const visit=(rows:readonly OperationControlStepV1[]):void=>{
     for(const row of rows){
      if(row.kind==='transaction')found.push(row.transaction);
      else if(row.kind==='present'&&row.transaction)found.push(row.transaction);
      else if(row.kind==='conditional'){visit(row.then);visit(row.otherwise);}
      else if(row.kind==='read-set')visit(row.body);
     }
    };visit(steps);return found;
   };
   const emissions=checked.effects.filter(operation=>operation.service===serviceId)
    .flatMap(operation=>transactions(operation.body).filter(transaction=>
     transaction.participants.includes(outbox.id)&&
     transaction.body.some(step=>step.kind==='mutation'&&step.operation==='record-event'&&step.target===event.name)&&
     transaction.body.some(step=>step.kind==='mutation'&&step.operation==='create'&&step.target===outbox.id))
     .map(()=>operation.operation.module+'.'+operation.operation.name));
   if(emissions.length!==1||emissions[0]!==selection.producer_operation)
    fail('ForeignOwner',where,'one original atomic Event and outbox producer required');
   const page=store.scanRows(outbox.id,cursor,limit),ids:string[]=[];
   for(const value of page.rows){
    if(!value||typeof value!=='object'||Array.isArray(value))
     fail('InvalidContract',where,'original selected Event outbox record required');
    const row=value as Record<string,CommerceNativeValue>;
    if(row.state!=='Ready')continue;
    if(typeof row.eventId!=='string'||!row.eventId.length||
     Buffer.byteLength(row.eventId)>128||Buffer.from(row.eventId).toString('utf8')!==row.eventId)
     fail('InvalidContract',where,'bounded original Event outbox occurrence required');
    ids.push(row.eventId);
   }
   current();return coreFreeze({occurrence_ids:ids,next_cursor:page.next_cursor});
  },
  async enqueueCommittedWorkflowEvent(binding:CommerceWorkflowCoordinationBindingV1,occurrenceId:string):Promise<CommerceWorkflowEnqueueResultV1> {
   current();assertCommerceWorkflowCoordinationBindingV1(binding);const source=binding.inspect(),workflow=source.workflow;
   if(source.owner_service!==serviceId||source.source_capture_sha256!==inspection.source_capture_sha256||workflow.input_producer!==serviceId)
    fail('ForeignOwner',where,'original producer and Workflow coordination must use the selected service store');
   if(typeof occurrenceId!=='string'||!occurrenceId.length||Buffer.byteLength(occurrenceId)>128||Buffer.from(occurrenceId).toString('utf8')!==occurrenceId)
    fail('InvalidContract',where,'bounded original Event occurrence required');
   const originalStore=store,outbox=store.readRow(source.input_outbox_entity,0,{eventId:occurrenceId});
   if(!outbox)return coreFreeze({kind:'not-ready' as const});
   const produced=technicalRecord(outbox,source.input_outbox_entity),event=produced.event;
   if(!event||typeof event!=='object'||Array.isArray(event)||produced.eventId!==occurrenceId||
    typeof produced.version!=='bigint'||produced.version<1n||!workflow.parameters.length)
    fail('InvalidContract',where,'original persisted producer Event outbox required');
   const eventId=originalEventField(event,workflow.parameters[0]!.name,workflow.inbox_identity.find(i=>i.kind==='value')?.value.source);
   const orderId=originalEventField(event,workflow.parameters[0]!.name,workflow.correlation.source);
   const metadata=(event as Record<string,CommerceNativeValue>).metadata;
   if(eventId!==occurrenceId||typeof orderId!=='string'||!orderId||!metadata||typeof metadata!=='object'||Array.isArray(metadata)||
    (metadata as Record<string,unknown>).producer!==workflow.input_producer||
    (metadata as Record<string,unknown>).eventId!==occurrenceId)
    fail('InvalidContract',where,'persisted Event must match source Workflow occurrence and producer');
   const identity=await ingressIdentity(binding);current();binding.assertCurrent();
   if(store!==originalStore)fail('StaleOwner',where,'producer store changed while binding Event identity');
   const eventFingerprint=identity.fingerprint(event),key=Object.freeze({consumerEntryId:workflow.input_entry,occurrenceId});
   const receipt=Object.freeze({consumerEntryId:key.consumerEntryId,occurrenceId,orderId});
   const existing=()=>{
    const priorInbox=store.readRow(source.inbox_entity,0,key),priorSchedule=store.readRow(source.schedule_entity,0,key);
    if(!priorInbox&&!priorSchedule)return null;
    if(!priorInbox||!priorSchedule)return coreFreeze({kind:'conflict' as const});
    const inbox=technicalRecord(priorInbox,source.inbox_entity),schedule=technicalRecord(priorSchedule,source.schedule_entity);
    const saved=inbox.receipt;
    if(inbox.consumerEntryId!==key.consumerEntryId||inbox.occurrenceId!==occurrenceId||inbox.orderId!==orderId||
     inbox.eventFingerprint!==eventFingerprint||!saved||typeof saved!=='object'||Array.isArray(saved)||
     (saved as Record<string,unknown>).consumerEntryId!==key.consumerEntryId||
     (saved as Record<string,unknown>).occurrenceId!==occurrenceId||
     (saved as Record<string,unknown>).orderId!==orderId||
     schedule.consumerEntryId!==key.consumerEntryId||schedule.occurrenceId!==occurrenceId||schedule.orderId!==orderId)
     return coreFreeze({kind:'conflict' as const});
    return coreFreeze({kind:'recorded' as const,receipt:saved});
   };
   const prior=existing();if(prior)return prior;
   if(produced.state!=='Ready')return coreFreeze({kind:'not-ready' as const});
   const commandKey={logicalEntryId:key.consumerEntryId,principalId:'workflow-ingress',
    commandId:'ingress:'+occurrenceId,
    transactionNamespace:dataDigest({kind:'workflow-ingress',workflow:workflow.name,source_sha256:source.source_capture_sha256}),
    fingerprint:eventFingerprint};
   const claim=store.claimFreshCommand(commandKey);
   if(claim.kind!=='claimed'){
    const status=store.inspectCommand(commandKey);
    if(status.kind==='conflict')return coreFreeze({kind:'conflict' as const});
    return existing()??coreFreeze({kind:'unavailable' as const});
   }
   const outcome=store.apply(claim.command,[
    {kind:'require-row',row:outbox},
    {kind:'require-absent',entity:source.inbox_entity,key_index:0,key},
    {kind:'require-absent',entity:source.schedule_entity,key_index:0,key},
    {kind:'create',entity:source.inbox_entity,value:Object.freeze({consumerEntryId:key.consumerEntryId,occurrenceId,eventFingerprint,orderId,receipt,version:1n})},
    {kind:'create',entity:source.schedule_entity,value:Object.freeze({consumerEntryId:key.consumerEntryId,occurrenceId,orderId,state:'Ready',workerOwner:Object.freeze({kind:'none'}),workerEpoch:0n,version:1n})},
   ],receipt);
   if(outcome.kind==='indeterminate')return coreFreeze({kind:'indeterminate' as const});
   if(outcome.kind==='unique-conflict')return existing()??coreFreeze({kind:'conflict' as const});
   if(outcome.kind==='version-conflict')return coreFreeze({kind:'not-ready' as const});
   if(outcome.kind!=='committed')return coreFreeze({kind:'unavailable' as const});
   current();if(store.inspectDisposition(outcome.receipt).kind!=='committed')fail('InvalidContract',where,'original native inbox and schedule commit required');
   const committed=existing();if(!committed||committed.kind!=='recorded')fail('InvalidContract',where,'committed inbox and WorkSchedule must be readable together');
   return coreFreeze({kind:'enqueued' as const,receipt:committed.receipt});
  },
  claimVacantWorkSchedule(binding:CommerceWorkflowCoordinationBindingV1,occurrenceId:string):CommerceWorkScheduleClaimResultV1 {
   current();assertCommerceWorkflowCoordinationBindingV1(binding);const source=binding.inspect();
   if(source.owner_service!==serviceId||source.source_capture_sha256!==inspection.source_capture_sha256)
    fail('ForeignOwner',where,'Workflow coordination must belong to the selected source and Orders store');
   if(typeof occurrenceId!=='string'||!occurrenceId.length||Buffer.byteLength(occurrenceId)>128||Buffer.from(occurrenceId).toString('utf8')!==occurrenceId)
    fail('InvalidContract',where,'bounded original event occurrence required');
   const key=Object.freeze({consumerEntryId:source.workflow.input_entry,occurrenceId});
   const inbox=store.readRow(source.inbox_entity,0,key),schedule=store.readRow(source.schedule_entity,0,key);
   if(!inbox||!schedule)return coreFreeze({kind:'not-ready' as const});
   const received=technicalRecord(inbox,source.inbox_entity),ready=technicalRecord(schedule,source.schedule_entity);
   const receipt=received.receipt;
   if(received.consumerEntryId!==key.consumerEntryId||received.occurrenceId!==occurrenceId||
    typeof received.orderId!=='string'||!received.orderId||typeof received.eventFingerprint!=='string'||!received.eventFingerprint||
    typeof received.version!=='bigint'||received.version<1n||!receipt||typeof receipt!=='object'||Array.isArray(receipt)||
    (receipt as Record<string,unknown>).consumerEntryId!==key.consumerEntryId||
    (receipt as Record<string,unknown>).occurrenceId!==occurrenceId||
    (receipt as Record<string,unknown>).orderId!==received.orderId||
    ready.consumerEntryId!==key.consumerEntryId||ready.occurrenceId!==occurrenceId||ready.orderId!==received.orderId)
    fail('InvalidContract',where,'original inbox and schedule identity must agree');
   const vacant=ready.workerOwner;
   if(ready.state!=='Ready'||!vacant||typeof vacant!=='object'||Array.isArray(vacant)||
    (vacant as Record<string,unknown>).kind!=='none')return coreFreeze({kind:'not-ready' as const});
   if(typeof ready.workerEpoch!=='bigint'||typeof ready.version!=='bigint'||ready.workerEpoch<0n||ready.workerEpoch>=MAX_U64||ready.version<1n||ready.version>=MAX_U64)
    fail('InvalidContract',where,'bounded original vacant schedule epoch and version required');
   const workerId=randomUUID(),workerEpoch=ready.workerEpoch+1n,scheduleVersion=ready.version+1n;
   const claim=store.claimFreshCommand({logicalEntryId:key.consumerEntryId,principalId:'workflow-worker',
    commandId:'schedule:'+occurrenceId,
    transactionNamespace:dataDigest({kind:'work-schedule-vacant-claim',workflow:source.workflow.name,source_sha256:source.source_capture_sha256}),
    fingerprint:dataDigest({workflow:source.workflow.name,source_sha256:source.source_capture_sha256,occurrenceId,orderId:received.orderId,
     priorEpoch:String(ready.workerEpoch),priorVersion:String(ready.version)})});
   if(claim.kind!=='claimed')return coreFreeze({kind:'unavailable' as const});
   const outcome=store.apply(claim.command,[{kind:'update',row:schedule,expected_version:ready.version,
    changes:Object.freeze({state:'Claimed',workerOwner:Object.freeze({kind:'some',value:workerId}),workerEpoch,version:scheduleVersion})}],false);
   if(outcome.kind==='indeterminate')return coreFreeze({kind:'indeterminate' as const});
   if(outcome.kind==='version-conflict')return coreFreeze({kind:'not-ready' as const});
   if(outcome.kind!=='committed')return coreFreeze({kind:'unavailable' as const});
   current();
   if(store.inspectDisposition(outcome.receipt).kind!=='committed')fail('InvalidContract',where,'original native WorkSchedule commit required');
   const view:CommerceWorkScheduleClaimInspectionV1=coreFreeze({workflow:source.workflow.name,source_capture_sha256:source.source_capture_sha256,
    store_id:inspection.store_id,consumer_entry_id:key.consumerEntryId,occurrence_id:occurrenceId,order_id:received.orderId,
    worker_id:workerId,worker_epoch:workerEpoch,schedule_version:scheduleVersion,
    prior_worker_owner:Object.freeze({kind:'none' as const}),prior_worker_epoch:ready.workerEpoch,
    predecessor_proof:'vacant',commit_receipt:outcome.receipt});
   const handle:CommerceWorkScheduleClaimV1=Object.freeze({kind:'original-committed-work-schedule-claim/v1-candidate'});
   scheduleClaims.set(handle,{binding,store,epoch:storeEpoch,key,inspection:view});scheduleClaimRow(handle);
   return coreFreeze({kind:'claimed' as const,claim:handle});
  },
  reclaimQuiescentWorkSchedule(binding:CommerceWorkflowCoordinationBindingV1,occurrenceId:string):CommerceWorkScheduleClaimResultV1 {
   current();if(mode!=='reopen')fail('InvalidContract',where,'whole-process reopen required for predecessor quiescence');
   quiescence.assertCurrent();assertCommerceWorkflowCoordinationBindingV1(binding);const source=binding.inspect();
   if(source.owner_service!==serviceId||source.source_capture_sha256!==inspection.source_capture_sha256)
    fail('ForeignOwner',where,'recovery Workflow must belong to the exact source and service store');
   if(typeof occurrenceId!=='string'||!occurrenceId.length||Buffer.byteLength(occurrenceId)>128||
    Buffer.from(occurrenceId).toString('utf8')!==occurrenceId)
    fail('InvalidContract',where,'bounded original Event occurrence required');
   const key=Object.freeze({consumerEntryId:source.workflow.input_entry,occurrenceId}),
    inbox=store.readRow(source.inbox_entity,0,key),schedule=store.readRow(source.schedule_entity,0,key);
   if(!inbox||!schedule)return coreFreeze({kind:'not-ready' as const});
   const received=technicalRecord(inbox,source.inbox_entity),old=technicalRecord(schedule,source.schedule_entity),
    receipt=received.receipt,oldOwner=old.workerOwner;
   if(received.consumerEntryId!==key.consumerEntryId||received.occurrenceId!==occurrenceId||
    typeof received.orderId!=='string'||!received.orderId||typeof received.eventFingerprint!=='string'||
    !received.eventFingerprint||typeof received.version!=='bigint'||received.version<1n||
    !receipt||typeof receipt!=='object'||Array.isArray(receipt)||
    (receipt as Record<string,unknown>).consumerEntryId!==key.consumerEntryId||
    (receipt as Record<string,unknown>).occurrenceId!==occurrenceId||
    (receipt as Record<string,unknown>).orderId!==received.orderId||
    old.consumerEntryId!==key.consumerEntryId||old.occurrenceId!==occurrenceId||old.orderId!==received.orderId)
    fail('InvalidContract',where,'original inbox and claimed schedule identity must agree');
   if(old.state!=='Claimed'||!oldOwner||typeof oldOwner!=='object'||Array.isArray(oldOwner)||
    (oldOwner as Record<string,unknown>).kind!=='some'||
    typeof (oldOwner as Record<string,unknown>).value!=='string'||
    !(oldOwner as Record<string,string>).value)return coreFreeze({kind:'not-ready' as const});
   const priorWorker=(oldOwner as {kind:'some';value:string}).value,
    priorEpoch=old.workerEpoch,priorVersion=old.version;
   if(typeof priorEpoch!=='bigint'||typeof priorVersion!=='bigint'||priorEpoch<1n||priorEpoch>=MAX_U64||
    priorVersion<2n||priorVersion>=MAX_U64)
    fail('InvalidContract',where,'bounded predecessor schedule epoch and version required');
   const progressRow=store.readRow(source.workflow.durable_state,0,{orderId:received.orderId});
   if(!progressRow)return coreFreeze({kind:'not-ready' as const});
   const progress=technicalRecord(progressRow,source.workflow.durable_state),progressOwner=progress.workerOwner;
   if(progress.orderId!==received.orderId||progress.workerEpoch!==priorEpoch||
    typeof progress.version!=='bigint'||progress.version<2n||
    !progressOwner||typeof progressOwner!=='object'||Array.isArray(progressOwner)||
    (progressOwner as Record<string,unknown>).kind!=='some'||
    (progressOwner as Record<string,unknown>).value!==priorWorker)
    return coreFreeze({kind:'not-ready' as const});
   const workerId=randomUUID(),workerEpoch=priorEpoch+1n,scheduleVersion=priorVersion+1n;
   const command=store.claimFreshCommand({logicalEntryId:key.consumerEntryId,principalId:'workflow-worker-reclaim',
    commandId:dataDigest({kind:'work-schedule-quiescent-reclaim',occurrenceId,priorVersion:String(priorVersion)}),
    transactionNamespace:dataDigest({kind:'work-schedule-quiescent-reclaim',workflow:source.workflow.name,
     source_sha256:source.source_capture_sha256}),
    fingerprint:dataDigest({workflow:source.workflow.name,occurrenceId,orderId:received.orderId,
     priorWorker,priorEpoch:String(priorEpoch),priorVersion:String(priorVersion),progressVersion:String(progress.version)})});
   if(command.kind!=='claimed')return coreFreeze({kind:'unavailable' as const});
   const outcome=store.apply(command.command,[{kind:'require-row',row:inbox},{kind:'require-row',row:progressRow},
    {kind:'update',row:schedule,expected_version:priorVersion,
     changes:Object.freeze({state:'Claimed',workerOwner:Object.freeze({kind:'some',value:workerId}),
      workerEpoch,version:scheduleVersion})}],false);
   if(outcome.kind==='indeterminate')return coreFreeze({kind:'indeterminate' as const});
   if(outcome.kind==='version-conflict')return coreFreeze({kind:'not-ready' as const});
   if(outcome.kind!=='committed')return coreFreeze({kind:'unavailable' as const});
   current();quiescence.assertCurrent();
   if(store.inspectDisposition(outcome.receipt).kind!=='committed')
    fail('InvalidContract',where,'native quiescent WorkSchedule reclaim commit required');
   const view:CommerceWorkScheduleClaimInspectionV1=coreFreeze({workflow:source.workflow.name,
    source_capture_sha256:source.source_capture_sha256,store_id:inspection.store_id,
    consumer_entry_id:key.consumerEntryId,occurrence_id:occurrenceId,order_id:received.orderId,
    worker_id:workerId,worker_epoch:workerEpoch,schedule_version:scheduleVersion,
    prior_worker_owner:Object.freeze({kind:'some' as const,value:priorWorker}),prior_worker_epoch:priorEpoch,
    predecessor_proof:'quiescent',commit_receipt:outcome.receipt});
   const handle:CommerceWorkScheduleClaimV1=Object.freeze({kind:'original-committed-work-schedule-claim/v1-candidate'});
   scheduleClaims.set(handle,{binding,store,epoch:storeEpoch,key,inspection:view});scheduleClaimRow(handle);
   return coreFreeze({kind:'claimed' as const,claim:handle});
  },
  inspectWorkScheduleClaim(claim:CommerceWorkScheduleClaimV1){return scheduleClaimRow(claim).inspection;},
  assertWorkScheduleClaimCurrent(claim:CommerceWorkScheduleClaimV1){scheduleClaimRow(claim);},
  prepareClaimJournal(binding:CommerceWorkflowCoordinationBindingV1,claim:CommerceWorkScheduleClaimV1):CommerceClaimJournalResultV1 {
   current();assertCommerceWorkflowCoordinationBindingV1(binding);const selected=binding.inspect(),schedule=scheduleClaimRow(claim),view=schedule.inspection;
   if(schedule.binding!==binding||selected.workflow.name!==view.workflow||selected.source_capture_sha256!==view.source_capture_sha256||
    selected.owner_service!==serviceId||selected.workflow.input_entry!==view.consumer_entry_id)
    fail('ForeignOwner',where,'exact source Workflow and committed WorkSchedule claim required');
   const drivers=selected.workflow.drivers.filter(driver=>driver.kind==='claim');
   if(drivers.length!==1||drivers[0]!.call.role!=='Operation'||drivers[0]!.call.arguments.length!==2||
    fieldPath(drivers[0]!.call.arguments.find(argument=>argument.parameter==='orderId')?.value.source).join('.')!=='snapshot.order.id'||
    fieldPath(drivers[0]!.call.arguments.find(argument=>argument.parameter==='expectedProgressVersion')?.value.source).join('.')!=='snapshot.progress.version')
    fail('InvalidContract',where,'checked claim driver must bind current source snapshot and version');
   const driver=drivers[0]!,progress=store.readRow(selected.workflow.durable_state,0,{orderId:view.order_id});
   if(!progress)return coreFreeze({kind:'not-ready' as const});
   const value=technicalRecord(progress,selected.workflow.durable_state),prior=value.workerOwner;
   const predecessorMatches=view.predecessor_proof==='vacant'
    ?view.prior_worker_owner.kind==='none'&&!!prior&&typeof prior==='object'&&!Array.isArray(prior)&&
      (prior as Record<string,unknown>).kind==='none'
    :view.prior_worker_owner.kind==='some'&&!!prior&&typeof prior==='object'&&!Array.isArray(prior)&&
      (prior as Record<string,unknown>).kind==='some'&&
      (prior as Record<string,unknown>).value===view.prior_worker_owner.value;
   if(value.orderId!==view.order_id||typeof value.version!=='bigint'||value.version<1n||
    value.workerEpoch!==view.prior_worker_epoch||!predecessorMatches)
    return coreFreeze({kind:'not-ready' as const});
   const scheduleRow=store.readRow(selected.schedule_entity,0,schedule.key);
   if(!scheduleRow)fail('StaleOwner',where,'committed WorkSchedule row missing');
   const stepName='claim' as const,commandId=view.worker_id,targetEntryId=driver.call.entry;
   const requestFingerprint=dataDigest({workflow:view.workflow,source_sha256:view.source_capture_sha256,stepName,
    targetEntryId,orderId:view.order_id,workerId:view.worker_id,workerEpoch:String(view.worker_epoch)});
   const key=Object.freeze({consumerEntryId:view.consumer_entry_id,occurrenceId:view.occurrence_id,stepName,commandId});
   const existing=store.readRow(selected.journal_entity,0,key);
   if(existing){const saved=technicalRecord(existing,selected.journal_entity);
    return coreFreeze({kind:saved.orderId===view.order_id&&saved.targetEntryId===targetEntryId&&
     saved.requestFingerprint===requestFingerprint&&saved.workerOwner===view.worker_id&&saved.workerEpoch===view.worker_epoch&&
     saved.phase==='Prepared'?'recorded' as const:'conflict' as const});}
   const command=store.claimFreshCommand({logicalEntryId:targetEntryId,principalId:'workflow-claim-journal',commandId,
    transactionNamespace:dataDigest({kind:'workflow-claim-journal',workflow:view.workflow,source_sha256:view.source_capture_sha256}),
    fingerprint:requestFingerprint});
   if(command.kind!=='claimed')return coreFreeze({kind:'unavailable' as const});
   const outcome=store.apply(command.command,[{kind:'require-row',row:progress},{kind:'require-row',row:scheduleRow},
    {kind:'require-absent',entity:selected.journal_entity,key_index:0,key},
    {kind:'create',entity:selected.journal_entity,value:Object.freeze({consumerEntryId:view.consumer_entry_id,
     occurrenceId:view.occurrence_id,orderId:view.order_id,stepName,commandId,targetEntryId,requestFingerprint,
     phase:'Prepared',workerOwner:view.worker_id,workerEpoch:view.worker_epoch,
     observation:Object.freeze({kind:'none'}),version:1n})}],false);
   if(outcome.kind==='indeterminate')return coreFreeze({kind:'indeterminate' as const});
   if(outcome.kind==='unique-conflict')return coreFreeze({kind:'conflict' as const});
   if(outcome.kind==='version-conflict')return coreFreeze({kind:'not-ready' as const});
   if(outcome.kind!=='committed')return coreFreeze({kind:'unavailable' as const});
   current();if(store.inspectDisposition(outcome.receipt).kind!=='committed')fail('InvalidContract',where,'original native StepJournal commit required');
   const journal:CommerceClaimJournalV1=Object.freeze({kind:'original-committed-claim-journal/v1-candidate'});
   const bound:CommerceClaimJournalInspectionV1=coreFreeze({workflow:view.workflow,source_capture_sha256:view.source_capture_sha256,
    store_id:view.store_id,consumer_entry_id:view.consumer_entry_id,occurrence_id:view.occurrence_id,order_id:view.order_id,
    step_name:stepName,command_id:commandId,target_entry_id:targetEntryId,request_fingerprint:requestFingerprint,
    worker_id:view.worker_id,worker_epoch:view.worker_epoch,phase:'Prepared',commit_receipt:outcome.receipt,authority_effect:'none'});
   claimJournals.set(journal,{claim,store,epoch:storeEpoch,key,inspection:bound});claimJournalRow(journal);
   return coreFreeze({kind:'prepared' as const,journal});
  },
  inspectClaimJournal(journal:CommerceClaimJournalV1){return claimJournalRow(journal).inspection;},
  assertClaimJournalCurrent(journal:CommerceClaimJournalV1){claimJournalRow(journal);},
  prepareWorkflowStepJournal(binding:CommerceWorkflowCoordinationBindingV1,schedule:CommerceWorkScheduleClaimV1,
   progress:CommerceWorkerProgressClaimV1,identities:CommerceWorkflowStepIdentityOwnerV1,
   identity:CommerceWorkflowStepIdentityHandleV1):CommerceWorkflowStepJournalResultV1 {
   current();const projection=createCommerceWorkflowPreparedJournalProjectionV1(binding,owner,schedule,progress,identities,identity),
    view=projection.recheck(),source=binding.inspect();
   if(source.owner_service!==serviceId||source.source_capture_sha256!==inspection.source_capture_sha256||
    view.journal_entity!==source.journal_entity||view.store_id!==inspection.store_id)
    fail('ForeignOwner',where,'exact selected source Workflow and store required for StepJournal');
   const scheduleRow=store.readRow(source.schedule_entity,0,{consumerEntryId:view.consumer_entry_id,occurrenceId:view.occurrence_id}),
    progressRow=store.readRow(source.workflow.durable_state,0,{orderId:view.order_id});
   if(!scheduleRow||!progressRow)return coreFreeze({kind:'not-ready' as const});
   const claimed=technicalRecord(scheduleRow,source.schedule_entity),currentProgress=technicalRecord(progressRow,source.workflow.durable_state),
    scheduleWorker=claimed.workerOwner,progressWorker=currentProgress.workerOwner;
   if(claimed.state!=='Claimed'||claimed.orderId!==view.order_id||claimed.version!==view.schedule_version||
    claimed.workerEpoch!==view.worker_epoch||!scheduleWorker||typeof scheduleWorker!=='object'||Array.isArray(scheduleWorker)||
    (scheduleWorker as Record<string,unknown>).kind!=='some'||(scheduleWorker as Record<string,unknown>).value!==view.worker_id||
    currentProgress.orderId!==view.order_id||currentProgress.version!==view.progress_version||
    currentProgress.workerEpoch!==view.worker_epoch||!progressWorker||typeof progressWorker!=='object'||Array.isArray(progressWorker)||
    (progressWorker as Record<string,unknown>).kind!=='some'||(progressWorker as Record<string,unknown>).value!==view.worker_id)
    return coreFreeze({kind:'not-ready' as const});
   const existing=()=>{
    const row=store.readRow(source.journal_entity,0,view.key);
    if(!row)return null;
    try{const observed=projection.inspectRecordedRow(technicalRecord(row,source.journal_entity));
     return coreFreeze({kind:'recorded' as const,phase:observed.phase});}
    catch(error){if(error instanceof CommerceWorkflowPreparedJournalProjectionErrorV1&&error.code==='JournalConflict')
      return coreFreeze({kind:'conflict' as const});throw error;}
   };
   const prior=existing();if(prior)return prior;
   const command=store.claimFreshCommand({logicalEntryId:view.target_entry_id,principalId:'workflow-step-journal',
    commandId:dataDigest({kind:'workflow-step-journal',consumerEntryId:view.consumer_entry_id,
     occurrenceId:view.occurrence_id,stepName:view.step_name,commandId:view.command_id}),
    transactionNamespace:dataDigest({kind:'workflow-step-journal',workflow:view.workflow,source_sha256:view.source_capture_sha256}),
    fingerprint:view.request_fingerprint});
   if(command.kind!=='claimed')return existing()??coreFreeze({kind:'indeterminate' as const});
   const outcome=store.apply(command.command,[{kind:'require-row',row:scheduleRow},{kind:'require-row',row:progressRow},
    {kind:'require-absent',entity:source.journal_entity,key_index:0,key:view.key},
    {kind:'create',entity:source.journal_entity,value:view.prepared}],false);
   if(outcome.kind==='indeterminate')return coreFreeze({kind:'indeterminate' as const});
   if(outcome.kind==='unique-conflict')return existing()??coreFreeze({kind:'conflict' as const});
   if(outcome.kind==='version-conflict')return coreFreeze({kind:'not-ready' as const});
   if(outcome.kind!=='committed')return coreFreeze({kind:'unavailable' as const});
   current();if(store.inspectDisposition(outcome.receipt).kind!=='committed')
    fail('InvalidContract',where,'native Prepared StepJournal commit required');
   const row=store.readRow(source.journal_entity,0,view.key);
   if(!row)fail('InvalidContract',where,'committed Prepared StepJournal must be readable');
   // The precommit projection, exact native CAS, and committed receipt were
   // checked above. Inspect the committed bytes without repeating the full
   // source/worker projection; later handle use still rechecks it.
   const committed=inspectCommerceWorkflowJournalRowDataV1(view.prepared,
    {id:view.worker_id,epoch:view.worker_epoch},technicalRecord(row,source.journal_entity));
   if(committed.phase!=='Prepared'||!committed.same_current_worker||committed.version!==1n)
    fail('InvalidContract',where,'committed Prepared StepJournal must retain original worker and phase');
   const journal:CommerceWorkflowStepJournalV1=Object.freeze({kind:'original-committed-workflow-step-journal/v1-candidate'}),
    bound:CommerceWorkflowStepJournalInspectionV1=coreFreeze({workflow:view.workflow,
     source_capture_sha256:view.source_capture_sha256,store_id:view.store_id,
     consumer_entry_id:view.consumer_entry_id,occurrence_id:view.occurrence_id,order_id:view.order_id,
     step_name:view.step_name,target_entry_id:view.target_entry_id,command_id:view.command_id,
     request_fingerprint:view.request_fingerprint,worker_id:view.worker_id,worker_epoch:view.worker_epoch,
     progress_version:view.progress_version,phase:'Prepared',commit_receipt:outcome.receipt,authority_effect:'none'});
   // The committed receipt and exact Prepared row were checked above. This
   // inert handle is fully rechecked on every later use; repeating that full
   // projection walk here adds no creation-time authority.
   current();stepJournals.set(journal,{binding,projection,store,epoch:storeEpoch,inspection:bound});
   return coreFreeze({kind:'prepared' as const,journal});
  },
  inspectWorkflowStepJournal(journal:CommerceWorkflowStepJournalV1){return stepJournalRow(journal).inspection;},
  assertWorkflowStepJournalCurrent(journal:CommerceWorkflowStepJournalV1){stepJournalRow(journal);},
  markWorkflowStepDispatched(binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceWorkflowStepJournalV1,
   identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1):CommerceWorkflowDispatchedStepJournalResultV1 {
   current();const transition=createCommerceWorkflowDispatchTransitionV1(binding,owner,journal,identities,identity),
    view=transition.initial(),source=binding.inspect();
   if(source.owner_service!==serviceId||source.source_capture_sha256!==inspection.source_capture_sha256||
    view.store_id!==inspection.store_id||view.journal_entity!==source.journal_entity)
    fail('ForeignOwner',where,'exact original StepJournal and service store required');
   const scheduleRow=store.readRow(source.schedule_entity,0,{consumerEntryId:view.consumer_entry_id,occurrenceId:view.occurrence_id}),
    progressRow=store.readRow(source.workflow.durable_state,0,{orderId:view.order_id}),
    journalRow=store.readRow(source.journal_entity,0,view.key);
   if(!scheduleRow||!progressRow||!journalRow)return coreFreeze({kind:'not-ready' as const});
   const schedule=technicalRecord(scheduleRow,source.schedule_entity),progress=technicalRecord(progressRow,source.workflow.durable_state),
    worker=schedule.workerOwner,progressWorker=progress.workerOwner;
   if(schedule.state!=='Claimed'||schedule.orderId!==view.order_id||schedule.workerEpoch!==view.worker_epoch||
    !worker||typeof worker!=='object'||Array.isArray(worker)||(worker as Record<string,unknown>).kind!=='some'||
    (worker as Record<string,unknown>).value!==view.worker_id||progress.orderId!==view.order_id||
    progress.version!==view.progress_version||progress.workerEpoch!==view.worker_epoch||
    !progressWorker||typeof progressWorker!=='object'||Array.isArray(progressWorker)||
    (progressWorker as Record<string,unknown>).kind!=='some'||(progressWorker as Record<string,unknown>).value!==view.worker_id)
    return coreFreeze({kind:'not-ready' as const});
   const observed=inspectCommerceWorkflowJournalRowDataV1(view.old,{id:view.worker_id,epoch:view.worker_epoch},
    technicalRecord(journalRow,source.journal_entity));
   if(observed.phase!=='Prepared'||observed.version!==view.expected_version||!observed.same_current_worker)
    return coreFreeze({kind:'conflict' as const});
   transition.recheck();
   const command=store.claimFreshCommand({logicalEntryId:view.target_entry_id,principalId:'workflow-step-dispatch',
    commandId:dataDigest({kind:'workflow-step-dispatch',consumerEntryId:view.consumer_entry_id,
     occurrenceId:view.occurrence_id,stepName:view.step_name,commandId:view.command_id}),
    transactionNamespace:dataDigest({kind:'workflow-step-dispatch',workflow:view.workflow,source_sha256:view.source_capture_sha256}),
    fingerprint:view.request_fingerprint});
   if(command.kind!=='claimed')return coreFreeze({kind:'indeterminate' as const});
   const outcome=store.apply(command.command,[{kind:'require-row',row:scheduleRow},{kind:'require-row',row:progressRow},
    {kind:'update',row:journalRow,expected_version:view.expected_version,changes:view.changes}],false);
   if(outcome.kind==='indeterminate')return coreFreeze({kind:'indeterminate' as const});
   if(outcome.kind==='version-conflict')return coreFreeze({kind:'not-ready' as const});
   if(outcome.kind==='unique-conflict')return coreFreeze({kind:'conflict' as const});
   if(outcome.kind!=='committed')return coreFreeze({kind:'unavailable' as const});
   current();if(store.inspectDisposition(outcome.receipt).kind!=='committed')
    fail('InvalidContract',where,'native Dispatched StepJournal commit required');
   const committed=store.readRow(source.journal_entity,0,view.key);
   if(!committed)fail('InvalidContract',where,'committed Dispatched StepJournal must be readable');
   const next=inspectCommerceWorkflowJournalRowDataV1(view.next,{id:view.worker_id,epoch:view.worker_epoch},
    technicalRecord(committed,source.journal_entity));
   if(next.phase!=='Dispatched'||next.version!==2n||!next.same_current_worker||next.observation_kind!=='none')
    fail('InvalidContract',where,'committed StepJournal must be Dispatched with original worker and request');
   const {prepare_commit_receipt:prepareReceipt,...originalIdentity}=view;
   const dispatched:CommerceWorkflowDispatchedStepJournalV1=Object.freeze({kind:'original-committed-dispatched-workflow-step-journal/v1-candidate'}),
    bound:CommerceWorkflowDispatchedStepJournalInspectionV1=coreFreeze({workflow:originalIdentity.workflow,
     source_capture_sha256:originalIdentity.source_capture_sha256,store_id:originalIdentity.store_id,
     consumer_entry_id:originalIdentity.consumer_entry_id,occurrence_id:originalIdentity.occurrence_id,
     order_id:originalIdentity.order_id,step_name:originalIdentity.step_name,
     target_entry_id:originalIdentity.target_entry_id,command_id:originalIdentity.command_id,
     request_fingerprint:originalIdentity.request_fingerprint,worker_id:originalIdentity.worker_id,
     worker_epoch:originalIdentity.worker_epoch,progress_version:originalIdentity.progress_version,
     phase:'Dispatched' as const,prepare_commit_receipt:prepareReceipt,
     dispatch_commit_receipt:outcome.receipt,authority_effect:'none' as const});
   // The committed receipt and exact Dispatched row were checked above.
   // Consumers still enter through dispatchedStepJournalRow for full custody.
   current();dispatchedStepJournals.set(dispatched,{binding,store,epoch:storeEpoch,key:view.key,inspection:bound});
   return coreFreeze({kind:'dispatched' as const,journal:dispatched});
  },
  inspectDispatchedWorkflowStepJournal(journal:CommerceWorkflowDispatchedStepJournalV1){return dispatchedStepJournalRow(journal).inspection;},
  assertDispatchedWorkflowStepJournalCurrent(journal:CommerceWorkflowDispatchedStepJournalV1){dispatchedStepJournalRow(journal);},
  registerCommittedWorkerProgressClaim(binding:CommerceWorkflowCoordinationBindingV1,schedule:CommerceWorkScheduleClaimV1,
   generated:CommerceGeneratedOperationRuntimeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,receipt:object){
   current();assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceGeneratedOperationRuntimeV1(generated);
   assertCommerceSelectedEntryAuthOwnerV1(selectedAuth);generated.assertStorage(owner);selectedAuth.assertAssembly(assemblyOwner,assembly);
   const committed=receipt&&typeof receipt==='object'?workerProgressReceipts.get(receipt):undefined,
    claimed=scheduleClaimRow(schedule),workflow=binding.inspect(),view=claimed.inspection;
   if(!committed||committed.runtime!==generated||committed.selectedAuth!==selectedAuth||committed.invocation!==invocation||
    committed.store!==store||committed.epoch!==storeEpoch||claimed.binding!==binding||
    workflow.owner_service!==serviceId||workflow.workflow.name!==view.workflow||
    workflow.source_capture_sha256!==inspection.source_capture_sha256||view.store_id!==inspection.store_id||
    committed.identity.journal_entry!==workflow.workflow.drivers.find(driver=>driver.kind==='claim')?.call.entry||
    committed.identity.command_id!==view.worker_id||store.inspectDisposition(receipt).kind!=='committed')
    fail('ForeignOwner',where,'exact generated Workflow progress commit required');
   const identity=selectedAuth.workerCommandIdentity(invocation,committed.transactionPath),
    selected=selectedAuth.inspectInvocation(invocation),parameters=selectedAuth.parameters(invocation);
   if(!identity||identity.journal_entry!==committed.identity.journal_entry||
    identity.command_id!==committed.identity.command_id||identity.request_fingerprint!==committed.identity.request_fingerprint||
    selected.entry!==identity.journal_entry||selected.operation!==workflow.workflow.drivers.find(driver=>driver.kind==='claim')?.call.target||
    parameters.orderId!==view.order_id||typeof parameters.expectedProgressVersion!=='bigint'||
    parameters.expectedProgressVersion<1n||parameters.expectedProgressVersion>=MAX_U64)
    fail('ForeignOwner',where,'original worker invocation must retain the committed claim identity');
   const row=store.readRow(workflow.workflow.durable_state,0,{orderId:view.order_id});
   if(!row)fail('StaleOwner',where,'generated worker progress commit has no row');
   const progress=technicalRecord(row,workflow.workflow.durable_state),worker=progress.workerOwner;
   if(progress.orderId!==view.order_id||progress.version!==parameters.expectedProgressVersion+1n||
    progress.workerEpoch!==view.worker_epoch||!worker||typeof worker!=='object'||Array.isArray(worker)||
    (worker as Record<string,unknown>).kind!=='some'||(worker as Record<string,unknown>).value!==view.worker_id)
    fail('StaleOwner',where,'generated claim must commit the exact source progress transition');
   const claimInspection:CommerceWorkerProgressClaimInspectionV1=coreFreeze({workflow:view.workflow,source_capture_sha256:view.source_capture_sha256,
    store_id:view.store_id,order_id:view.order_id,worker_id:view.worker_id,worker_epoch:view.worker_epoch,
    progress_version:progress.version as bigint,transaction_path:committed.transactionPath,commit_receipt:receipt,authority_effect:'none'});
   const claim:CommerceWorkerProgressClaimV1=Object.freeze({kind:'original-committed-worker-progress-claim/v1-candidate'});
   workerProgressClaims.set(claim,{binding,schedule,store,epoch:storeEpoch,inspection:claimInspection});workerProgressClaimRow(claim);
   return claim;
  },
  inspectWorkerProgressClaim(claim:CommerceWorkerProgressClaimV1){return workerProgressClaimRow(claim).inspection;},
  assertWorkerProgressClaimCurrent(claim:CommerceWorkerProgressClaimV1){workerProgressClaimRow(claim);},
  countStoredRecords(entity:string){current();const count=store.countRows(entity);if(!Number.isSafeInteger(count)||count<0)fail('InvalidContract',where,'bounded native row count required');current();return BigInt(count);},
  async reopen(){current();storeEpoch++;store.close();try{store=await runtime.openCommerceSqliteUnitOfWorkV1(sqlite,bundle,storePath,'reopen');runtime.assertCommerceSqliteUnitOfWorkV1(store);
   const actual=store.inspect();
   if(actual.store_id!==inspection.store_id||actual.service!==serviceId||actual.schema_sha256!==inspection.schema_sha256)
    fail('StaleOwner',where,'reopened original store identity must match the selected service');
   current();}catch(error){try{store.close();}catch{}quiescence.close();closed=true;throw error;}},
  assertCurrent:current,
  close(){if(closed)return;closed=true;storeEpoch++;
   for(const [workflow,pending] of ingressIdentities){
    const identity=readyIngressIdentities.get(workflow);
    if(identity){try{identity.dispose();}catch{}}
    else void pending.then(value=>{try{value.dispose();}catch{}},()=>{});
   }
   readyIngressIdentities.clear();
   try{store.close();}finally{quiescence.close();commandBindings?.dispose();sqlite.dispose();}},
 });
 owners.add(owner);current();return owner;
 }catch(error){quiescence.close();try{store.close();}catch{}throw error;}
}
