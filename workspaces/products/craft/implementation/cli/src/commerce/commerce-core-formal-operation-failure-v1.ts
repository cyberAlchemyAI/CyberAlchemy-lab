/** Conditional source-bound binding from checked argument-acquisition or
 * pure-call arithmetic faults to the enclosing Operation let-step's proposed action. Earlier
 * guards/reads, effect execution, rollback and native parity are not modeled.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import type {FlowExprV1,OperationControlStepV1} from './commerce-data-v1.js';
import {exportCoreCommerceFormalPureOutcomeV1} from './commerce-core-formal-pure-outcome-v1.js';
import {adaptCommercePureCallResult} from './commerce-computation-call-runtime.js';

export class CoreCommerceFormalOperationFailureErrorV1 extends Error {
 constructor(readonly code:'UnsupportedOperationBinding'|'InvalidModel'){
  super(code);this.name='CoreCommerceFormalOperationFailureErrorV1';
 }
}
const fail=(code:CoreCommerceFormalOperationFailureErrorV1['code']):never=>{throw new CoreCommerceFormalOperationFailureErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-call-runtime'+ext,'commerce-flow-expression-data-v1'+ext,
 '../generation/commerce-operation-control-source-v1'+ext,
]);
const smtString=(value:string)=>`"${value.replaceAll('"','""')}"`;
const containsTransaction=(step:OperationControlStepV1):boolean=>{
 if(step.kind==='transaction')return true;
 if(step.kind==='conditional')return [...step.then,...step.otherwise].some(containsTransaction);
 if(step.kind==='present')return step.transaction!==null;
 if(step.kind==='read-set')return step.body.some(containsTransaction);
 return false;
};
const quoteField=(value:FlowExprV1,field:string):boolean=>
 value.op==='field'&&value.field===field&&value.value.op==='var'&&value.value.name==='quote';

export interface CoreCommerceFormalOperationFailureV1 {
 readonly schema_version:'craft.core-commerce-formal-operation-failure/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'checked-direct-operation-let-argument-or-pure-call-expression-fault-if-reached';
 readonly application:string;readonly service:string;readonly calculation:string;
 readonly operation:string;readonly let_binding:string;readonly step_index:number;
 readonly before_first_declared_transaction:boolean;
 readonly argument_bindings:readonly string[];
 readonly argument_charge_count_when_ready:9;
 readonly action:Readonly<{kind:'reject'|'fail';code:string}>;
 readonly action_subject_sha256:string;
 readonly adapter_decision:'evaluation-error';
 readonly action_requirement:'requires-original-caller-to-apply-source-action';
 readonly parameter_validation_decision:'parameter-validation-error';
 readonly parameter_validation_action:'none';
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly operation_plan_sha256:string;readonly pure_outcome_sha256:string;readonly exporter_code_sha256:string;
 readonly assumed_invocation:'checked-operation-reaches-direct-let-with-ordinary-typed-own-data-scope-and-nine-operation-charges-available';
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['earlier-guards-reads-and-auth','source-and-custody-of-subtotal-and-quote','earlier-operation-charge-account','transaction-effects-and-rollback','actual-failure-action-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'checked-direct-operation-handler-proposal-conditional-on-reaching-the-let-and-expression-fault';
}

export function exportCoreCommerceFormalOperationFailureV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalOperationFailureV1 {
 pin.assertCurrent();
 const pure=exportCoreCommerceFormalPureOutcomeV1(sources,capture,semantics,semantic,assembly,selector);
 const checked=semantics.inspect(semantic);
 const matches=checked.effects.flatMap(plan=>plan.body.flatMap((step,index)=>
  step.kind==='let'&&step.value.expression.op==='call'&&step.value.expression.declaration===selector&&
  (step.on_error.kind==='reject'||step.on_error.kind==='fail')?
   [{plan,step,index}]:[]));
 if(matches.length!==1)fail('UnsupportedOperationBinding');
 const {plan,step,index}=matches[0]!;
 if(step.kind!=='let'||step.on_error.kind==='return'||step.on_error.kind==='invoke-return'||
  step.value.expression.op!=='call'||step.value.result.kind!=='scalar'||step.value.result.name!=='UInt64'||
  plan.service!==pure.service||plan.operation.role!=='Operation'||
  plan.body.slice(0,index).some(containsTransaction))fail('UnsupportedOperationBinding');
 const call=step.value.expression;
 if(call.op!=='call'||step.value.local_records.length!==0||pure.inputs.length!==4||
  pure.inputs[0]!=='subtotal'||call.arguments.length!==4||
  call.arguments[0]?.op!=='var'||call.arguments[0].name!=='subtotal'||
  !quoteField(call.arguments[1]!,pure.inputs[1]!)||
  !quoteField(call.arguments[2]!,pure.inputs[2]!)||
  !quoteField(call.arguments[3]!,pure.inputs[3]!))fail('UnsupportedOperationBinding');
 const actionKind=step.on_error.kind==='reject'?'reject':step.on_error.kind==='fail'?'fail':fail('UnsupportedOperationBinding');
 const actionCode='code' in step.on_error?step.on_error.code:fail('UnsupportedOperationBinding');
 const actionSubjectSha256=dataDigest(step.on_error);
 const adapterSpec={on_error:{kind:actionKind,code:actionCode,subject_sha256:actionSubjectSha256},
  requires_rollback:false,direct_guard:false,on_false:null};
 const adapter=adaptCommercePureCallResult({result:{ok:false},evaluation_phase:'expression'},adapterSpec);
 const inputAdapter=adaptCommercePureCallResult({result:{ok:false},evaluation_phase:'input-validation'},adapterSpec);
 if(adapter.decision!=='evaluation-error'||adapter.source_action?.kind!==actionKind||
  adapter.source_action?.code!==actionCode||
  adapter.source_action?.subject_sha256!==actionSubjectSha256||
  adapter.action_requirement!=='requires-original-caller-to-apply-source-action'||
  inputAdapter.decision!=='parameter-validation-error'||inputAdapter.source_action!==null||
  inputAdapter.action_requirement!=='none')fail('UnsupportedOperationBinding');
 const operation=`${plan.operation.module}.${plan.operation.name}`;
 const tail=[
  `; operation_plan_sha256: ${dataDigest(plan)}`,
  `; pure_outcome_sha256: ${pure.smtlib2_sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  `; Conditional on checked ${operation} reaching let ${step.name} with adequate fuel.`,
  '; Generated control charges one let step and eight direct call/argument nodes.',
  '; Its own-data field lookup fails with ExpressionFault(InputType); the let catches that fault.',
  '; Scope flags and values are observations of an ordinary typed original scope, not constructed here.',
  '; The generated let handler selects the checked source action after an ExpressionFault.',
  '; The separate pure-call adapter proposes that action after an evaluation fault.',
  '; That adapter proposes no source action for its own parameter-validation faults.',
  '; Earlier guards, Query/Auth custody, previous fuel, action execution and rollback are absent.',
  '(declare-fun ScopeHasSubtotal () Bool)',
  '(declare-fun ScopeHasQuote () Bool)',
  '(declare-fun QuoteHasField1 () Bool)',
  '(declare-fun QuoteHasField2 () Bool)',
  '(declare-fun QuoteHasField3 () Bool)',
  '(declare-fun ScopeSubtotal () Int)',
  '(declare-fun QuoteField1 () Int)',
  '(declare-fun QuoteField2 () Int)',
  '(declare-fun QuoteField3 () Int)',
  '(define-fun ArgumentStatus () Int (ite (and ScopeHasSubtotal ScopeHasQuote QuoteHasField1 QuoteHasField2 QuoteHasField3) 0 1))',
  '(define-fun ArgumentFaultOrdinal () Int (ite (not ScopeHasSubtotal) 0 (ite (or (not ScopeHasQuote) (not QuoteHasField1)) 1 (ite (not QuoteHasField2) 2 (ite (not QuoteHasField3) 3 (- 1))))))',
  '(define-fun OperationArgumentChargeCount () Int (ite (not ScopeHasSubtotal) 3 (ite (or (not ScopeHasQuote) (not QuoteHasField1)) 5 (ite (not QuoteHasField2) 7 9))))',
  '(assert (=> (= ArgumentStatus 0) (and (= Input0 ScopeSubtotal) (= Input1 QuoteField1) (= Input2 QuoteField2) (= Input3 QuoteField3))))',
  '(define-fun OperationFailureCause () Int (ite (= ArgumentStatus 1) 1 (ite (= Status 1) 2 (ite (= Status 2) 3 0))))',
  '(define-fun OperationActionProposed () Bool (not (= OperationFailureCause 0)))',
  `(define-fun OperationActionKind () String (ite OperationActionProposed ${smtString(actionKind)} "none"))`,
  `(define-fun OperationActionCode () String (ite OperationActionProposed ${smtString(actionCode)} ""))`,
  '(define-fun OperationFailureCode () String (ite (= ArgumentStatus 1) "InputType" (ite (= Status 1) "ArithmeticUnderflow" (ite (= Status 2) "ArithmeticOverflow" ""))))',
  '(define-fun ParameterValidationActionSelected () Bool false)',
  '',
 ];
 const smtlib2=pure.smtlib2+tail.join('\n');
 const result:CoreCommerceFormalOperationFailureV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-operation-failure/v1-candidate' as const,
  language:'smtlib2' as const,
  scope:'checked-direct-operation-let-argument-or-pure-call-expression-fault-if-reached' as const,
  application:pure.application,service:pure.service,calculation:selector,operation,
  let_binding:step.name,step_index:index,before_first_declared_transaction:true as const,
  argument_bindings:['subtotal',...pure.inputs.slice(1).map(field=>'quote.'+field)],
  argument_charge_count_when_ready:9 as const,
  action:{kind:actionKind,code:actionCode},
  action_subject_sha256:actionSubjectSha256,
  adapter_decision:'evaluation-error' as const,
  action_requirement:'requires-original-caller-to-apply-source-action' as const,
  parameter_validation_decision:'parameter-validation-error' as const,
  parameter_validation_action:'none' as const,
  source_capture_sha256:pure.source_capture_sha256,executable_sha256:pure.executable_sha256,
  family_sha256:pure.family_sha256,operation_plan_sha256:dataDigest(plan),
  pure_outcome_sha256:pure.smtlib2_sha256,exporter_code_sha256:pin.sha256,
  assumed_invocation:'checked-operation-reaches-direct-let-with-ordinary-typed-own-data-scope-and-nine-operation-charges-available' as const,
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['earlier-guards-reads-and-auth','source-and-custody-of-subtotal-and-quote','earlier-operation-charge-account',
   'transaction-effects-and-rollback','actual-failure-action-execution','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'checked-direct-operation-handler-proposal-conditional-on-reaching-the-let-and-expression-fault' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalOperationFailureCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalOperationFailureV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||
  model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalOperationFailureV1(
   sources,capture,semantics,semantic,assembly,selector)))fail('InvalidModel');
}
