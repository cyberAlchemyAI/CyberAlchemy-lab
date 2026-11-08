/** C14 selected Core Workflow ingress over the original producer store.
 * Occurrence discovery and worker execution are separate native owners.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceWorkflowEnqueueResultV1,type CommerceWorkScheduleClaimResultV1,
 type CommerceClaimJournalResultV1,type CommerceWorkScheduleClaimV1} from '../commerce/commerce-service-storage-v1.js';
import {selectCoreCommerceWorkerClaimInput,type CoreCommerceWorkerClaimInput} from './core-commerce-worker-claim-input.js';

export interface CoreCommerceWorkflowIngress {
 inspect():Readonly<{workflow:string;owner_service:string;input_producer:string;input_entry:string;
  input_outbox_entity:string;journal_entity:string;source_capture_sha256:string;
  qualification:'checked-committed-event-ingress-and-schedule-component;outbox-discovery-and-worker-pending'}>;
 enqueue(occurrenceId:string):Promise<CommerceWorkflowEnqueueResultV1>;
 scanReady(cursor:string|null,limit:number):Readonly<{occurrence_ids:readonly string[];next_cursor:string|null}>;
 claim(occurrenceId:string):CommerceWorkScheduleClaimResultV1;
 reclaimQuiescent(occurrenceId:string):CommerceWorkScheduleClaimResultV1;
 inspectClaimInput(claim:CommerceWorkScheduleClaimV1):CoreCommerceWorkerClaimInput;
 prepareClaimJournal(claim:CommerceWorkScheduleClaimV1):CommerceClaimJournalResultV1;
 assertCurrent():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceWorkflowIngress(owner:CoreCommerceWorkflowIngress):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))throw new Error('original checked Workflow ingress required');
 owner.assertCurrent();
}

export function createCoreCommerceWorkflowIngress(
 binding:CommerceWorkflowCoordinationBindingV1,
 storage:CommerceServiceStorageOwnerV1,
):CoreCommerceWorkflowIngress {
 assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(storage);
 const source=binding.inspect(),store=storage.inspect();
 if(source.owner_service!==store.service||source.workflow.input_producer!==store.service||
   source.source_capture_sha256!==store.source_capture_sha256)
  throw new Error('checked Workflow ingress requires its selected original producer store');
 const inspection=Object.freeze({workflow:source.workflow.name,owner_service:source.owner_service,
  input_producer:source.workflow.input_producer,input_entry:source.workflow.input_entry,
  input_outbox_entity:source.input_outbox_entity,journal_entity:source.journal_entity,
  source_capture_sha256:source.source_capture_sha256,
  qualification:'checked-committed-event-ingress-and-schedule-component;outbox-discovery-and-worker-pending' as const});
 const current=()=>{
  binding.assertCurrent();storage.assertCurrent();
  const latest=binding.inspect(),stored=storage.inspect();
  if(latest.workflow.name!==inspection.workflow||latest.source_capture_sha256!==inspection.source_capture_sha256||
    latest.owner_service!==stored.service||stored.source_capture_sha256!==inspection.source_capture_sha256)
   throw new Error('selected Workflow ingress source or producer store changed');
 };
 const owner:CoreCommerceWorkflowIngress=Object.freeze({
  inspect(){current();return inspection;},
  enqueue(occurrenceId:string){current();return storage.enqueueCommittedWorkflowEvent(binding,occurrenceId);},
  scanReady(cursor:string|null,limit:number){current();return storage.scanReadyOutbox(binding,cursor,limit);},
  claim(occurrenceId:string){current();return storage.claimVacantWorkSchedule(binding,occurrenceId);},
  reclaimQuiescent(occurrenceId:string){current();return storage.reclaimQuiescentWorkSchedule(binding,occurrenceId);},
  inspectClaimInput(claim:CommerceWorkScheduleClaimV1){current();return selectCoreCommerceWorkerClaimInput(binding,storage,claim);},
  prepareClaimJournal(claim:CommerceWorkScheduleClaimV1){current();return storage.prepareClaimJournal(binding,claim);},
  assertCurrent:current,
 });
 owners.add(owner);current();return owner;
}
