/** A protected Workflow step targeting its own worker service must retain the
 * original local worker and committed progress claim. This is data-only.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {assertCommerceWorkflowProtectedCallBindingV1,
 type CommerceWorkflowProtectedCallBindingV1,type CommerceWorkflowProtectedCallInspectionV1}
 from './commerce-workflow-protected-call-binding-v1.js';
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,type CommerceWorkerContextV1}
 from './commerce-worker-context-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from './commerce-service-storage-v1.js';
import type {EntryContractV1} from './commerce-data-v1.js';

export class CommerceWorkflowWorkerStepAdmissionErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowWorkerStepAdmissionErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowWorkerStepAdmissionErrorV1(code);};

export function assertCommerceWorkflowWorkerStepAdmissionV1(
 entry:EntryContractV1,sourceSha:string,protectedCall:CommerceWorkflowProtectedCallBindingV1,
 storage:CommerceServiceStorageOwnerV1,workerOwner:CommerceWorkerContextOwnerV1,
 workerContext:CommerceWorkerContextV1,
):CommerceWorkflowProtectedCallInspectionV1 {
 const call=assertCommerceWorkflowProtectedCallBindingV1(protectedCall);
 assertCommerceServiceStorageOwnerV1(storage);
 assertCommerceWorkerContextOwnerV1(workerOwner);workerOwner.assertContextCurrent(workerContext);
 const store=storage.inspect(),worker=workerOwner.inspectContext(workerContext),
  access=entry.access,causal=access.resource_bindings.length===1?access.resource_bindings[0]:null;
 if(call.source_capture_sha256!==sourceSha||call.source_capture_sha256!==store.source_capture_sha256||
  call.entry_id!==entry.id||call.target!==entry.invokes.module+'.'+entry.invokes.name||
  call.role!==entry.invokes.role||call.caller_service!==access.caller||call.caller_service!==store.service||
  entry.service!==store.service||call.phase!=='Dispatched'||
  access.principal_kind!=='service'||access.worker_lifetime!=='requires-original-local-worker-owner'||
  access.resource_phase!=='causal-before-invocation'||!access.resource_condition||
  access.matching_replay_resource_check!=='same-causal-input'||
  access.context.abi!=='craft.commerce-worker-context/v1-candidate'||
  access.current_action!=='before-replay-and-effects'||
  !causal||causal.origin.kind!=='workflow-journal'||causal.origin.declaration!==call.workflow||
  causal.abi!=='craft.commerce-causal-call/v1-candidate'||
  causal.selector.split('/').at(-1)!=='original-step-journal'||
  entry.parameters.length!==Object.keys(call.arguments).length||
  entry.parameters.some(parameter=>!Object.hasOwn(call.arguments,parameter.name))||
  causal.required_fields.length!==Object.keys(call.causal_projection).length||
  causal.required_fields.some(field=>!Object.hasOwn(call.causal_projection,field))||
  !worker.progress_claim_qualified||worker.workflow!==call.workflow||
  worker.source_capture_sha256!==sourceSha||worker.store_id!==store.store_id||
  worker.store_id!==call.store_id||worker.consumer_entry_id!==call.consumer_entry_id||
  worker.occurrence_id!==call.occurrence_id||worker.order_id!==call.order_id||
  worker.worker_id!==call.worker_id||worker.worker_epoch!==call.worker_epoch)
  bad('ForeignWorkflowWorkerCall');
 return call;
}
