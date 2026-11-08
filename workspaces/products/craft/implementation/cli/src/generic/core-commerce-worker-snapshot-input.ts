/** Derive a worker Query input from the source correlation and a committed
 * WorkSchedule claim. The original progress claim remains a separate required
 * precondition before the protected snapshot may be read.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {assertCommerceWorkflowCoordinationBindingV1,
 type CommerceWorkflowCoordinationBindingV1} from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceWorkScheduleClaimV1} from '../commerce/commerce-service-storage-v1.js';

export type CoreCommerceWorkerSnapshotInput=Readonly<{
 entry:string;
 query:string;
 service:string;
 parameters:Readonly<Record<string,string>>;
 source_capture_sha256:string;
 qualification:'source-correlated-claim-to-worker-snapshot-input-only;fresh-entry-auth-required';
}>;

/** The current coordination ABI stores one original correlation identifier in
 * its claim. Refuse a snapshot that asks for any other input until an original
 * event-payload owner supplies that value; never guess it from a field name. */
export function selectCoreCommerceWorkerSnapshotInput(
 binding:CommerceWorkflowCoordinationBindingV1,
 storage:CommerceServiceStorageOwnerV1,
 claim:CommerceWorkScheduleClaimV1,
):CoreCommerceWorkerSnapshotInput {
 assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(storage);
 storage.assertWorkScheduleClaimCurrent(claim);
 const selected=binding.inspect(),store=storage.inspect(),committed=storage.inspectWorkScheduleClaim(claim);
 if(store.service!==selected.owner_service||store.source_capture_sha256!==selected.source_capture_sha256||
  committed.store_id!==store.store_id||committed.workflow!==selected.workflow.name||
  committed.source_capture_sha256!==selected.source_capture_sha256||
  committed.consumer_entry_id!==selected.workflow.input_entry||
  typeof committed.order_id!=='string'||!committed.order_id)
  throw new Error('snapshot input requires the exact original committed Workflow claim');
 const snapshots=selected.workflow.drivers.filter(driver=>driver.kind==='snapshot');
 if(snapshots.length!==1)throw new Error('one checked Workflow snapshot driver required');
 const call=snapshots[0]!.call;
 if(call.role!=='Query'||call.arguments.length!==1)
  throw new Error('worker snapshot input supports one source-correlated Query argument');
 const argument=call.arguments[0]!;
 if(dataDigest(argument.value.evaluation)!==dataDigest(selected.workflow.correlation.evaluation))
  throw new Error('worker snapshot input must be the exact checked Workflow correlation');
 return Object.freeze({entry:call.entry,query:call.target,service:selected.owner_service,
  parameters:Object.freeze({[argument.parameter]:committed.order_id}),
  source_capture_sha256:selected.source_capture_sha256,
  qualification:'source-correlated-claim-to-worker-snapshot-input-only;fresh-entry-auth-required' as const});
}
