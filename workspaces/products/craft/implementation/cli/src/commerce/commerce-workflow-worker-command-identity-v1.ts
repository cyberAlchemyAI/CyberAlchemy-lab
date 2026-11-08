/** Source-bound command identity for a Workflow step whose target is the
 * worker's own Operation. A journal key is data until Auth and the generated
 * transaction owner consume it. Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalOperationHandleV1}
 from './commerce-local-plan-owner-v1.js';
import {assertCommerceWorkflowProtectedCallBindingV1,type CommerceWorkflowProtectedCallBindingV1}
 from './commerce-workflow-protected-call-binding-v1.js';

export class CommerceWorkflowWorkerCommandIdentityErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowWorkerCommandIdentityErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowWorkerCommandIdentityErrorV1(code);};

export function deriveCommerceWorkflowWorkerCommandIdentityV1(
 plans:CommerceLocalPlanOwnerV1,operation:CommerceLocalOperationHandleV1,
 protectedCall:CommerceWorkflowProtectedCallBindingV1,transactionPath:string,
):Readonly<{journal_entry:string;command_id:string;request_fingerprint:string}> {
 assertCommerceLocalPlanOwnerV1(plans);assertCommerceWorkflowProtectedCallBindingV1(protectedCall);
 const original=plans.inspectOperation(operation),call=protectedCall.recheck();
 if(call.role!=='Operation'||original.operation!==call.target||
  original.plan.service!==call.caller_service||
  original.source_capture_sha256!==call.source_capture_sha256||
  original.transactions.length!==1||original.transactions[0]!.path!==transactionPath)
  bad('ForeignWorkflowCommand');
 return Object.freeze({journal_entry:call.entry_id,command_id:call.command_id,
  request_fingerprint:call.request_fingerprint});
}
