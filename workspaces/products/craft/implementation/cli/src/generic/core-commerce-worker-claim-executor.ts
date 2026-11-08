/** Execute one original Workflow progress claim through the checked Entry,
 * private WorkerContext and generated Operation. The generated CAS remains the
 * only progress write; a durable journal and Auth decision are never inferred.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from '../commerce/commerce-application-assembly-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceWorkScheduleClaimV1,type CommerceClaimJournalV1,type CommerceWorkerProgressClaimV1}
 from '../commerce/commerce-service-storage-v1.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceAuthActorV1}
 from '../commerce/commerce-entry-context-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1}
 from '../commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,
 type CommerceWorkerContextV1} from '../commerce/commerce-worker-context-v1.js';
import {createCoreCommerceWorkerActorRegistry} from './core-commerce-worker-actor-registry.js';
import {selectCoreCommerceWorkerClaimInput,type CoreCommerceWorkerClaimInput} from './core-commerce-worker-claim-input.js';

export interface CoreCommerceClaimedWorkerSession {
 readonly claim:CommerceWorkScheduleClaimV1;
 readonly worker:CommerceWorkerContextOwnerV1;
 readonly context:CommerceWorkerContextV1;
 readonly journal:CommerceClaimJournalV1;
 readonly progress_claim:CommerceWorkerProgressClaimV1;
 inspect():ReturnType<CommerceWorkerContextOwnerV1['inspectContext']>;
 dispose():void;
}
const claimedSessions=new WeakSet<object>();
export function assertCoreCommerceClaimedWorkerSession(session:CoreCommerceClaimedWorkerSession):void {
 if(!session||typeof session!=='object'||!claimedSessions.has(session))
  throw new Error('original generated Workflow progress-claim session required');
 session.worker.assertContextCurrent(session.context);
}
export type CoreCommerceWorkerClaimExecution=
 CoreCommerceWorkerClaimInput & {readonly kind:'not-ready'}|
 Readonly<{kind:'journal-state';state:'recorded'|'not-ready'|'conflict'|'unavailable'|'indeterminate'}>|
 Readonly<{kind:'entry-denied';status:401|403;code:'unauthorized'|'forbidden'}>|
 Readonly<{kind:'operation-outcome';outcome:Readonly<Record<string,unknown>>}>|
 Readonly<{kind:'claimed-progress';session:CoreCommerceClaimedWorkerSession;
  source_capture_sha256:string;qualification:'committed-generated-progress-claim;worker-steps-pending'}>;

export interface CoreCommerceWorkerClaimExecutor {
 inspect():Readonly<{workflow:string;source_capture_sha256:string;store_id:string;
  required_entries:readonly string[];qualification:'source-selected-native-worker-claim-only;step-execution-pending'}>;
 bindActor(actor:CommerceAuthActorV1):readonly string[];
 run(claim:CommerceWorkScheduleClaimV1):Promise<CoreCommerceWorkerClaimExecution>;
 assertCurrent():void;
 close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceWorkerClaimExecutor(owner:CoreCommerceWorkerClaimExecutor):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))throw new Error('checked worker claim executor required');
 owner.assertCurrent();
}

export function createCoreCommerceWorkerClaimExecutor(
 assembly:CommerceApplicationAssemblyV1,binding:CommerceWorkflowCoordinationBindingV1,
 storage:CommerceServiceStorageOwnerV1,auth:CommerceEntryContextOwnerV1,
 selected:CommerceSelectedEntryAuthOwnerV1,
):CoreCommerceWorkerClaimExecutor {
 assertCommerceApplicationAssemblyV1(assembly);assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(storage);assertCommerceEntryContextOwnerV1(auth);
 assertCommerceSelectedEntryAuthOwnerV1(selected);
 const application=assembly.inspect(),source=binding.inspect(),store=storage.inspect();
 if(source.source_capture_sha256!==application.source_capture_sha256||
  source.owner_service!==store.service||store.source_capture_sha256!==source.source_capture_sha256||
  !application.services.includes(store.service))
  throw new Error('worker claim requires one selected original application service and Workflow');
 const actors=createCoreCommerceWorkerActorRegistry(assembly,auth,source.workflow.name),
  requirements=actors.inspect().requirements;
 if(requirements.filter(row=>row.usage==='claim'&&row.entry===source.workflow.drivers.find(driver=>driver.kind==='claim')?.call.entry).length!==1)
  throw new Error('one checked Workflow claim Entry actor requirement required');
 const sessions=new Set<CoreCommerceClaimedWorkerSession>();
 let closed=false;
 const current=()=>{
  if(closed)throw new Error('worker claim executor closed');
  assembly.assertCurrent();binding.assertCurrent();storage.assertCurrent();auth.assertCurrent();selected.assertCurrent();
  const now=binding.inspect(),stored=storage.inspect();
  if(now.workflow.name!==source.workflow.name||now.source_capture_sha256!==source.source_capture_sha256||
   stored.store_id!==store.store_id||stored.source_capture_sha256!==source.source_capture_sha256)
   throw new Error('selected Workflow claim source or store changed');
 };
 const owner:CoreCommerceWorkerClaimExecutor=Object.freeze({
  inspect(){current();return Object.freeze({workflow:source.workflow.name,
   source_capture_sha256:source.source_capture_sha256,store_id:store.store_id,
   required_entries:Object.freeze(requirements.map(row=>row.entry)),
   qualification:'source-selected-native-worker-claim-only;step-execution-pending' as const});},
  bindActor(actor:CommerceAuthActorV1){current();return actors.bind(actor);},
  async run(claim:CommerceWorkScheduleClaimV1):Promise<CoreCommerceWorkerClaimExecution>{
   current();const input=selectCoreCommerceWorkerClaimInput(binding,storage,claim);
   if(input.kind==='not-ready')return input;
   // A missing or disposed native actor must not leave a Prepared journal that
   // cannot be retried through this selected claim path.
   const actor=actors.actorFor('claim');
   const journal=storage.prepareClaimJournal(binding,claim);
   if(journal.kind!=='prepared')return Object.freeze({kind:'journal-state' as const,state:journal.kind});
   const worker=createCommerceWorkerContextOwnerV1(binding,storage);
   let invocation:Awaited<ReturnType<CommerceSelectedEntryAuthOwnerV1['beginWorker']>>|undefined;
   let opened=false,keepWorker=false;
   try{
    const context=worker.registerCommittedClaim(claim);
    const entry=auth.bindEntry(input.entry);
    let wire:Uint8Array;
    try{
     const checked=auth.inspectEntry(entry);
     if(checked.service!==input.service||checked.invokes.module+'.'+checked.invokes.name!==input.operation)
      throw new Error('original worker claim Entry differs from source-selected driver');
     wire=auth.encodeEntryArguments(entry,input.parameters);
    }finally{auth.disposeEntry(entry);}
    invocation=await selected.beginWorker(actor,input.entry,wire!,input.parameters,storage,binding,journal.journal,worker,context);
    if(!invocation.ok)return Object.freeze({kind:'entry-denied' as const,status:invocation.status,code:invocation.code});
    const runtime=await assembly.openGeneratedOperation(invocation.invocation);opened=true;
    const outcome=await runtime.run(invocation.invocation);
    if(outcome.kind!=='returned')return Object.freeze({kind:'operation-outcome' as const,outcome});
    const receipts=outcome.commits;
    if(!Array.isArray(receipts)||receipts.length!==1||!receipts[0]||typeof receipts[0]!=='object')
     throw new Error('generated Workflow claim must return one original committed CAS receipt');
    const progressClaim=worker.registerCommittedProgressClaim(context,runtime,selected,invocation.invocation,receipts[0]);
    const session:CoreCommerceClaimedWorkerSession=Object.freeze({
     claim,worker,context,journal:journal.journal,progress_claim:progressClaim,
     inspect(){return worker.inspectContext(context);},
     dispose(){if(!sessions.delete(session))return;worker.dispose();},
    });
    claimedSessions.add(session);
    sessions.add(session);keepWorker=true;
    return Object.freeze({kind:'claimed-progress' as const,session,
     source_capture_sha256:source.source_capture_sha256,
     qualification:'committed-generated-progress-claim;worker-steps-pending' as const});
   }finally{
    if(invocation?.ok){
     try{if(opened)assembly.releaseGeneratedOperation(invocation.invocation);}
     finally{selected.retire(invocation.invocation);}
    }
    if(!keepWorker)worker.dispose();
   }
  },
  assertCurrent:current,
  close(){if(closed)return;closed=true;for(const session of [...sessions])session.dispose();},
 });
 owners.add(owner);current();return owner;
}
