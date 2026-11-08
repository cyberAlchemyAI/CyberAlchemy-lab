/** Conditional data-flow projection of one checked Operation let into one
 * checked transaction field. It describes source value provenance, not a row
 * write, native commit, or end-to-end operation outcome.
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
import {exportCoreCommerceFormalOperationFailureV1} from './commerce-core-formal-operation-failure-v1.js';
import {commerceTransactionOutcomeMappingV1} from '../generation/commerce-effectful-operation-source-v1.js';

export class CoreCommerceFormalOrderValueFlowErrorV1 extends Error {
 constructor(readonly code:'UnsupportedValueFlow'|'InvalidModel'){
  super(code);this.name='CoreCommerceFormalOrderValueFlowErrorV1';
 }
}
const fail=(code:CoreCommerceFormalOrderValueFlowErrorV1['code']):never=>{
 throw new CoreCommerceFormalOrderValueFlowErrorV1(code);
};
const sha=(text:string)=>createHash('sha256').update(text).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-core-formal-operation-failure-v1'+ext,
 'commerce-sqlite-transaction-owner-v1'+ext,
 '../generation/commerce-effectful-operation-source-v1'+ext,
]);

export interface CoreCommerceFormalOrderValueFlowV1 {
 readonly schema_version:'craft.core-commerce-formal-order-value-flow/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'conditional-checked-let-to-order-create-field-data-flow';
 readonly application:string;readonly operation:string;readonly calculation:string;
 readonly let_binding:'payableMinor';readonly transaction:string;
 readonly guard_step_index:number;readonly guard_source_path:string;
 readonly guard_action:Readonly<{kind:'reject';code:'quote-expired'}>;
 readonly transaction_step_index:number;readonly mutation_index:number;readonly field_index:number;
 readonly precondition_steps:readonly [
  Readonly<{kind:'require-absent';entity:'Orders.ReplayRecord';source_path:string}>,
  Readonly<{kind:'capacity';entity:'Orders.ReplayRecord';maximum:4096;source_path:string}>];
 readonly direct_dispositions:Readonly<{
  committed:Readonly<{requires:'original-commit-receipt';aliases:'escape-only-after-original-commit'}>;
  rolled_back:Readonly<{requires:'original-proven-rollback';action:Readonly<{kind:'reject';code:'acceptance-contention'}>}>;
  indeterminate:Readonly<{requires:'original-unresolved-commit';action:Readonly<{kind:'fail';code:'outcome-unknown'}>;retain_original:true}>;
 }>;
 readonly target_entity:'Orders.Order';readonly target_field:'payableMinor';
 readonly assumed_control_path:'fresh-normal-operation-path';
 readonly field_source_path:string;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly operation_model_sha256:string;readonly operation_plan_sha256:string;
 readonly transaction_plan_sha256:string;readonly field_expression_sha256:string;
 readonly guard_expression_sha256:string;readonly disposition_mapping_sha256:string;
 readonly exporter_code_sha256:string;readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly [
  'source-and-custody-of-quote-and-clock','earlier-auth-read-and-fuel',
  'intervening-operation-steps-and-fuel','native-precondition-outcomes-and-other-fields',
  'native-row-write-and-commit','rollback-and-recovery','event-and-outbox-effects',
  'other-transaction-disposition-channels','native-disposition-proof-production',
  'generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'source-value-provenance-only-if-original-field-evaluation-is-reached';
}

export function exportCoreCommerceFormalOrderValueFlowV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalOrderValueFlowV1 {
 pin.assertCurrent();
 const operation=exportCoreCommerceFormalOperationFailureV1(
  sources,capture,semantics,semantic,assembly,selector);
 const plans=semantics.inspect(semantic).effects.filter(plan=>
  `${plan.operation.module}.${plan.operation.name}`===operation.operation);
 if(plans.length!==1)fail('UnsupportedValueFlow');
 const plan=plans[0]!;
 const letStep=plan.body[operation.step_index];
 if(letStep?.kind!=='let'||letStep.name!=='payableMinor'||
  plan.body.slice(0,operation.step_index).some(step=>step.kind==='transaction'))
  fail('UnsupportedValueFlow');
 const guards=plan.body.flatMap((step,index)=>
  index<operation.step_index&&step.kind==='guard'&&step.on_false.kind==='reject'&&
  step.on_false.code==='quote-expired'?[{step,index}]:[]);
 if(guards.length!==1)fail('UnsupportedValueFlow');
 const {step:guard, index:guardStepIndex}=guards[0]!;
 if(guard.kind!=='guard'||guard.condition.result.kind!=='scalar'||
  guard.condition.result.name!=='Bool'||guard.condition.local_records.length!==0)
  fail('UnsupportedValueFlow');
 const guardExpr=guard.condition.expression;
 if(guardExpr.op!=='binary'||guardExpr.operator!=='gt'||
  guardExpr.left.op!=='field'||guardExpr.left.field!=='expiresAtEpochMs'||
  guardExpr.left.value.op!=='var'||guardExpr.left.value.name!=='quote'||
  guardExpr.right.op!=='var'||guardExpr.right.name!=='nowEpochMs')
  fail('UnsupportedValueFlow');
 const guardSourcePath=`$.body[${guardStepIndex}].condition.expression`;
 const matches=plan.body.flatMap((step,transactionStepIndex)=>{
  if(step.kind!=='transaction'||transactionStepIndex<=operation.step_index)return [];
  return step.transaction.body.flatMap((mutation,mutationIndex)=>{
   if(mutation.kind!=='mutation'||mutation.operation!=='create'||
    mutation.target!=='Orders.Order'||mutation.binding!=='order')return [];
   return mutation.fields.flatMap((field,fieldIndex)=>
    field.name==='payableMinor'&&field.value.result.kind==='scalar'&&
    field.value.result.name==='UInt64'&&field.value.local_records.length===0&&
    field.value.expression.op==='var'&&field.value.expression.name==='payableMinor'?
     [{step,mutation,field,transactionStepIndex,mutationIndex,fieldIndex}]:[]);
  });
 });
 if(matches.length!==1)fail('UnsupportedValueFlow');
 const {step,mutation,field,transactionStepIndex,mutationIndex,fieldIndex}=matches[0]!;
 if(step.kind!=='transaction'||step.transaction.name!=='AcceptCheckout'||
  mutation.kind!=='mutation'||mutation.key!==null||mutation.expected_version!==null)
  fail('UnsupportedValueFlow');
 const [absence,capacity]=step.transaction.body;
 if(mutationIndex!==2||absence?.kind!=='require-absent'||
  absence.entity!=='Orders.ReplayRecord'||capacity?.kind!=='capacity'||
  capacity.entity!=='Orders.ReplayRecord'||capacity.maximum!==4096)
  fail('UnsupportedValueFlow');
 const preconditionBase=`$.body[${transactionStepIndex}].transaction.body`;
 const preconditionSteps=[
  {kind:'require-absent' as const,entity:'Orders.ReplayRecord' as const,
   source_path:`${preconditionBase}[0]`},
  {kind:'capacity' as const,entity:'Orders.ReplayRecord' as const,maximum:4096 as const,
   source_path:`${preconditionBase}[1]`},
 ] as const;
 const mapping=commerceTransactionOutcomeMappingV1(step.transaction);
 if(mapping.committed.requires!=='original-commit-receipt'||
  mapping.committed.aliases!=='escape-only-after-original-commit'||
  mapping['rolled-back'].requires!=='original-proven-rollback'||
  mapping['rolled-back'].action?.kind!=='reject'||
  mapping['rolled-back'].action.code!=='acceptance-contention'||
  mapping.indeterminate.requires!=='original-unresolved-commit'||
  mapping.indeterminate.action?.kind!=='fail'||
  mapping.indeterminate.action.code!=='outcome-unknown'||
  mapping.indeterminate.retain_original!==true)
  fail('UnsupportedValueFlow');
 const directDispositions={
  committed:{requires:'original-commit-receipt' as const,aliases:'escape-only-after-original-commit' as const},
  rolled_back:{requires:'original-proven-rollback' as const,
   action:{kind:'reject' as const,code:'acceptance-contention' as const}},
  indeterminate:{requires:'original-unresolved-commit' as const,
   action:{kind:'fail' as const,code:'outcome-unknown' as const},retain_original:true as const},
 };
 const fieldSourcePath=`$.body[${transactionStepIndex}].transaction.body[${mutationIndex}].fields[${fieldIndex}].value.expression`;
 const tail=[
  `; transaction_plan_sha256: ${dataDigest(step.transaction)}`,
  `; field_expression_sha256: ${dataDigest(field.value.expression)}`,
  `; guard_expression_sha256: ${dataDigest(guardExpr)}`,
  `; disposition_mapping_sha256: ${dataDigest(mapping)}`,
  `; guard_source_path: ${guardSourcePath}`,
  `; field_source_path: ${fieldSourcePath}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  '; Guard truth is conditional on the original typed quote and clock values at this checked step.',
  '; A false guard selects the checked reject quote-expired action; its execution is not modeled.',
  '; Conditional on a fresh normal Operation path reaching this create-field evaluation.',
  '; Retained-binding recovery and replay paths are outside this premise.',
  '; The source field is a direct read of the preceding payableMinor let binding.',
  '; Native precondition outcomes, other fields, write/commit and rollback are not translated.',
  '; The two source precondition instructions precede the Order create field evaluation.',
  '; Resumed means the original source instruction generator continued after native handling; acceptance is not inferred.',
  '; Disposition tags below are assumed already proven by the original native owner.',
  '; Other channels and production of commit, rollback or unresolved evidence are not translated.',
  '(declare-fun QuoteExpiresAtEpochMs () Int)',
  '(declare-fun NowEpochMs () Int)',
  '(assert (and (<= 0 QuoteExpiresAtEpochMs) (<= QuoteExpiresAtEpochMs 18446744073709551615)))',
  '(assert (and (<= 0 NowEpochMs) (<= NowEpochMs 18446744073709551615)))',
  '(define-fun QuoteNotExpired () Bool (> QuoteExpiresAtEpochMs NowEpochMs))',
  '(define-fun QuoteExpiredRejectionProposed () Bool (not QuoteNotExpired))',
  '(define-fun QuoteExpiredRejectionCode () String (ite QuoteExpiredRejectionProposed "quote-expired" ""))',
  '(declare-fun RequireAbsentInstructionResumed () Bool)',
  '(declare-fun CapacityInstructionResumed () Bool)',
  '(assert (=> CapacityInstructionResumed RequireAbsentInstructionResumed))',
  '(declare-fun NormalPathOrderCreateFieldEvaluationReached () Bool)',
  '(assert (=> NormalPathOrderCreateFieldEvaluationReached (and QuoteNotExpired (= ArgumentStatus 0) (= Status 0) CapacityInstructionResumed)))',
  '(define-fun PayableMinorLetAssigned () Bool (and (= ArgumentStatus 0) (= Status 0)))',
  '(define-fun PayableMinorLetValue () Int Value)',
  '(define-fun OrderCreatePayableMinorFieldValue () Int PayableMinorLetValue)',
  '; OriginalDisposition: 0 committed, 1 rolled-back, 2 indeterminate, 3 unsupported other channel.',
  '(declare-fun OriginalDisposition () Int)',
  '(assert (and (<= 0 OriginalDisposition) (<= OriginalDisposition 3)))',
  '(define-fun CommitReceiptRequired () Bool (= OriginalDisposition 0))',
  '(define-fun ProvenRollbackRejectionProposed () Bool (= OriginalDisposition 1))',
  '(define-fun UnresolvedCommitFailureProposed () Bool (= OriginalDisposition 2))',
  '(define-fun DirectDispositionActionCode () String (ite ProvenRollbackRejectionProposed "acceptance-contention" (ite UnresolvedCommitFailureProposed "outcome-unknown" "")))',
  '',
 ];
 const smtlib2=operation.smtlib2+tail.join('\n');
 const result:CoreCommerceFormalOrderValueFlowV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-order-value-flow/v1-candidate' as const,
  language:'smtlib2' as const,
  scope:'conditional-checked-let-to-order-create-field-data-flow' as const,
  application:operation.application,operation:operation.operation,calculation:selector,
  let_binding:'payableMinor' as const,transaction:step.transaction.name,
  guard_step_index:guardStepIndex,guard_source_path:guardSourcePath,
  guard_action:{kind:'reject' as const,code:'quote-expired' as const},
  transaction_step_index:transactionStepIndex,mutation_index:mutationIndex,field_index:fieldIndex,
  precondition_steps:preconditionSteps,
  direct_dispositions:directDispositions,
  target_entity:'Orders.Order' as const,target_field:'payableMinor' as const,field_source_path:fieldSourcePath,
  assumed_control_path:'fresh-normal-operation-path' as const,
  source_capture_sha256:operation.source_capture_sha256,executable_sha256:operation.executable_sha256,
  family_sha256:operation.family_sha256,operation_model_sha256:operation.smtlib2_sha256,
  operation_plan_sha256:operation.operation_plan_sha256,
  transaction_plan_sha256:dataDigest(step.transaction),field_expression_sha256:dataDigest(field.value.expression),
  guard_expression_sha256:dataDigest(guardExpr),disposition_mapping_sha256:dataDigest(mapping),
  exporter_code_sha256:pin.sha256,smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['source-and-custody-of-quote-and-clock','earlier-auth-read-and-fuel',
   'intervening-operation-steps-and-fuel','native-precondition-outcomes-and-other-fields',
   'native-row-write-and-commit','rollback-and-recovery','event-and-outbox-effects',
   'other-transaction-disposition-channels','native-disposition-proof-production',
   'generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'source-value-provenance-only-if-original-field-evaluation-is-reached' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalOrderValueFlowCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalOrderValueFlowV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||
  model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalOrderValueFlowV1(
   sources,capture,semantics,semantic,assembly,selector)))fail('InvalidModel');
}
