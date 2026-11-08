/** Source Entry and committed Workflow call must describe the same protected
 * service invocation. This check is data-only; Auth and runtime claim the call.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {assertCommerceWorkflowProtectedCallBindingV1,
 type CommerceWorkflowProtectedCallBindingV1,type CommerceWorkflowProtectedCallInspectionV1}
 from './commerce-workflow-protected-call-binding-v1.js';
import type {EntryContractV1} from './commerce-data-v1.js';

export class CommerceWorkflowServiceStepAdmissionErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowServiceStepAdmissionErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowServiceStepAdmissionErrorV1(code);};

export function assertCommerceWorkflowServiceStepAdmissionV1(
 entry:EntryContractV1,sourceSha:string,protectedCall:CommerceWorkflowProtectedCallBindingV1,
):CommerceWorkflowProtectedCallInspectionV1 {
 const call=assertCommerceWorkflowProtectedCallBindingV1(protectedCall),access=entry.access,
  causal=access.resource_bindings.length===1?access.resource_bindings[0]:null;
 if(call.source_capture_sha256!==sourceSha||call.entry_id!==entry.id||
  call.target!==entry.invokes.module+'.'+entry.invokes.name||call.role!==entry.invokes.role||
  call.caller_service!==access.caller||call.phase!=='Dispatched'||
  access.principal_kind!=='service'||access.worker_lifetime!=='not-applicable'||
  access.resource_phase!=='causal-before-invocation'||!access.resource_condition||
  access.matching_replay_resource_check!=='same-causal-input'||
  access.current_action!=='before-replay-and-effects'||
  !causal||causal.origin.kind!=='workflow-journal'||causal.origin.declaration!==call.workflow||
  causal.abi!=='craft.commerce-causal-call/v1-candidate'||
  causal.selector.split('/').at(-1)!=='original-step-journal'||
  entry.parameters.length!==Object.keys(call.arguments).length||
  entry.parameters.some(parameter=>!Object.hasOwn(call.arguments,parameter.name))||
  causal.required_fields.length!==Object.keys(call.causal_projection).length||
  causal.required_fields.some(field=>!Object.hasOwn(call.causal_projection,field)))
  bad('ForeignWorkflowCall');
 return call;
}
