/** Execute the checked Workflow snapshot through its original Query Entry,
 * fresh service Auth, committed claim journal and qualified WorkerContext.
 * The assembly supplies its captured Read owners; callers supply no SQL,
 * context value or domain callback.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from '../commerce/commerce-application-assembly-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1} from '../commerce/commerce-service-storage-v1.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceAuthActorV1} from '../commerce/commerce-entry-context-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from '../commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceSourceQueryOutputCodecV1,type CommerceSourceQueryOutputCodecV1} from '../commerce/commerce-source-query-output-codec-v1.js';
import {createCommerceSourceQueryRuntimeV1,type CommerceSourceQueryRuntimeV1} from '../commerce/commerce-source-query-runtime-v1.js';
import {createCommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotOwnerV1,
 type CommerceWorkflowSnapshotHandleV1,type CommerceWorkflowSnapshotInspectionV1}
 from '../commerce/commerce-workflow-snapshot-v1.js';
import type {CoreCommerceStageSourceOwner} from '../commerce/commerce-core-stage-owner.js';
import type {CommerceSourceHandle} from '../commerce/commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from '../commerce/commerce-computation-domain.js';
import type {CommerceLocalPlanOwnerV1,CommerceLocalReadHandleV1} from '../commerce/commerce-local-plan-owner-v1.js';
import {assertCoreCommerceClaimedWorkerSession,type CoreCommerceClaimedWorkerSession} from './core-commerce-worker-claim-executor.js';
import {createCoreCommerceWorkerActorRegistry} from './core-commerce-worker-actor-registry.js';
import {selectCoreCommerceWorkerSnapshotInput} from './core-commerce-worker-snapshot-input.js';

export interface CoreCommerceWorkerSnapshotWitness {
 readonly kind:'snapshot';
 readonly snapshots:CommerceWorkflowSnapshotOwnerV1;
 readonly handle:CommerceWorkflowSnapshotHandleV1;
 readonly inspection:CommerceWorkflowSnapshotInspectionV1;
 dispose():void;
}
const originalWitnesses=new WeakSet<object>();
export function assertCoreCommerceWorkerSnapshotWitness(witness:CoreCommerceWorkerSnapshotWitness):void {
 if(!witness||typeof witness!=='object'||!originalWitnesses.has(witness))
  throw new Error('original source-owned worker snapshot witness required');
 witness.snapshots.inspect(witness.handle);
}
export type CoreCommerceWorkerSnapshotResult=CoreCommerceWorkerSnapshotWitness|
 Readonly<{kind:'rejected'|'failed';code:string;authority_effect:'none'}>|
 Readonly<{kind:'entry-denied';status:401|403;code:'unauthorized'|'forbidden'}>;
export interface CoreCommerceWorkerSnapshotQuery {
 inspect():Readonly<{workflow:string;query:string;entry:string;source_capture_sha256:string;
  qualification:'source-selected-worker-snapshot-query;fresh-auth-and-native-context-required'}>;
 bindActor(actor:CommerceAuthActorV1):readonly string[];
 run(session:CoreCommerceClaimedWorkerSession):Promise<CoreCommerceWorkerSnapshotResult>;
 assertCurrent():void;
 close():void;
}

export function createCoreCommerceWorkerSnapshotQuery(input:Readonly<{
 assembly:CommerceApplicationAssemblyV1;
 binding:CommerceWorkflowCoordinationBindingV1;
 storage:CommerceServiceStorageOwnerV1;
 auth:CommerceEntryContextOwnerV1;
 selected:CommerceSelectedEntryAuthOwnerV1;
 stage:CoreCommerceStageSourceOwner;
 source:CommerceSourceHandle;
 domain:CommerceComputationDomainOwner;
 baseline:CommerceComputationDomainHandle;
 plans:CommerceLocalPlanOwnerV1;
}>):CoreCommerceWorkerSnapshotQuery {
 const {assembly,binding,storage,auth,selected,stage,source,domain,baseline,plans}=input;
 assertCommerceApplicationAssemblyV1(assembly);assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(storage);assertCommerceEntryContextOwnerV1(auth);
 assertCommerceSelectedEntryAuthOwnerV1(selected);
 const workflow=binding.inspect(),store=storage.inspect(),snapshots=workflow.workflow.drivers.filter(row=>row.kind==='snapshot');
 if(snapshots.length!==1||snapshots[0]!.call.role!=='Query'||
  workflow.owner_service!==store.service||store.source_capture_sha256!==workflow.source_capture_sha256||
  assembly.inspect().source_capture_sha256!==workflow.source_capture_sha256)
  throw new Error('one original selected Workflow snapshot Query and service store required');
 const snapshot=snapshots[0]!.call,actors=createCoreCommerceWorkerActorRegistry(assembly,auth,workflow.workflow.name);
 const leases=new Set<()=>void>();
 let closed=false;
 const current=()=>{
  if(closed)throw new Error('worker snapshot Query closed');
  assembly.assertCurrent();binding.assertCurrent();storage.assertCurrent();auth.assertCurrent();selected.assertCurrent();
  if(storage.inspect().store_id!==store.store_id||binding.inspect().source_capture_sha256!==workflow.source_capture_sha256)
   throw new Error('selected worker snapshot source or store changed');
 };
 const owner:CoreCommerceWorkerSnapshotQuery=Object.freeze({
  inspect(){current();return Object.freeze({workflow:workflow.workflow.name,query:snapshot.target,entry:snapshot.entry,
   source_capture_sha256:workflow.source_capture_sha256,
   qualification:'source-selected-worker-snapshot-query;fresh-auth-and-native-context-required' as const});},
  bindActor(actor:CommerceAuthActorV1){current();return actors.bind(actor);},
  async run(session:CoreCommerceClaimedWorkerSession):Promise<CoreCommerceWorkerSnapshotResult>{
   current();assertCoreCommerceClaimedWorkerSession(session);
   storage.assertWorkScheduleClaimCurrent(session.claim);storage.assertClaimJournalCurrent(session.journal);
   storage.assertWorkerProgressClaimCurrent(session.progress_claim);
   const claim=storage.inspectWorkScheduleClaim(session.claim),journal=storage.inspectClaimJournal(session.journal),
    progress=storage.inspectWorkerProgressClaim(session.progress_claim),context=session.worker.inspectContext(session.context);
   if(!context.progress_claim_qualified||claim.store_id!==store.store_id||claim.workflow!==workflow.workflow.name||
    claim.worker_id!==context.worker_id||claim.order_id!==context.order_id||
    journal.order_id!==claim.order_id||journal.worker_id!==claim.worker_id||
    progress.order_id!==claim.order_id||progress.worker_id!==claim.worker_id||
    journal.source_capture_sha256!==workflow.source_capture_sha256)
    throw new Error('original qualified worker snapshot claim required');
   const selectedInput=selectCoreCommerceWorkerSnapshotInput(binding,storage,session.claim);
   if(selectedInput.entry!==snapshot.entry||selectedInput.query!==snapshot.target||
    selectedInput.service!==store.service||selectedInput.source_capture_sha256!==workflow.source_capture_sha256)
    throw new Error('snapshot input differs from checked Workflow source');
   const actor=actors.actorFor('snapshot');
   const entry=auth.bindEntry(selectedInput.entry);
   let wire:Uint8Array;
   try{
    const checked=auth.inspectEntry(entry);
    if(checked.service!==selectedInput.service||checked.invokes.role!=='Query'||
     checked.invokes.module+'.'+checked.invokes.name!==selectedInput.query)
     throw new Error('selected worker snapshot Entry differs from original Query');
    wire=auth.encodeEntryArguments(entry,selectedInput.parameters);
   }finally{auth.disposeEntry(entry);}
   const started=await selected.beginWorkerRead(actor,selectedInput.entry,wire!,selectedInput.parameters,
    storage,binding,session.journal,session.worker,session.context);
   if(!started.ok)return Object.freeze({kind:'entry-denied' as const,status:started.status,code:started.code});
   let read:CommerceLocalReadHandleV1|undefined,codec:CommerceSourceQueryOutputCodecV1|undefined,
    query:CommerceSourceQueryRuntimeV1|undefined,snapshotOwner:CommerceWorkflowSnapshotOwnerV1|undefined;
   let released=false,retained=false;
   const release=()=>{
    if(released)return;released=true;leases.delete(release);
    try{snapshotOwner?.dispose();}finally{
     try{query?.dispose();}finally{
      try{codec?.dispose();}finally{
       try{if(read)plans.disposeRead(read);}finally{selected.retire(started.invocation);}
      }
     }
    }
   };
   try{
    read=plans.bindRead(selectedInput.query);
    const plan=plans.inspectRead(read);
    if(plan.plan.kind!=='local'||plan.plan.service!==store.service||
     plan.source_capture_sha256!==workflow.source_capture_sha256)
     throw new Error('selected worker snapshot requires original local Read');
    codec=await createCommerceSourceQueryOutputCodecV1(stage,source,domain,baseline,plans,read);
    query=createCommerceSourceQueryRuntimeV1(stage,source,plans,read,domain,baseline,storage,codec);
    if(query.query!==selectedInput.query)throw new Error('selected worker snapshot Query changed');
    snapshotOwner=createCommerceWorkflowSnapshotOwnerV1(binding,storage,session.worker,session.context,
     query,selected,started.invocation);
    const witnessed=snapshotOwner.read();
    if(witnessed.kind!=='snapshot')return witnessed;
    const inspection=snapshotOwner.inspect(witnessed.handle);
    leases.add(release);retained=true;
    const original=Object.freeze({kind:'snapshot' as const,snapshots:snapshotOwner,handle:witnessed.handle,
     inspection,dispose:release});
    originalWitnesses.add(original);
    return original;
   }finally{if(!retained)release();}
  },
  assertCurrent:current,
  close(){if(closed)return;closed=true;for(const release of [...leases])release();},
 });
 current();return owner;
}
