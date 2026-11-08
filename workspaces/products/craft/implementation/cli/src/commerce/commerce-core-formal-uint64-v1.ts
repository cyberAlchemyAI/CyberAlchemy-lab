/** Source-bound SMT-LIB projection of a checked pure UInt64 Calculation.
 * It models the exact left-to-right add/subtract/multiply arithmetic and the
 * first arithmetic error and its declared pure-function annotation for valid
 * UInt64 arguments. Metering, wire validation, action execution and generated-
 * code parity are unsupported here.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import type {ExprV1} from './commerce-data-v1.js';

export class CoreCommercePureFormalErrorV1 extends Error {
 constructor(readonly code:'InvalidSource'|'UnsupportedExpression'|'InvalidModel') {super(code);this.name='CoreCommercePureFormalErrorV1';}
}
const reject=(code:CoreCommercePureFormalErrorV1['code']):never=>{throw new CoreCommercePureFormalErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const pin=pinCoreImplementation(import.meta.url,[]);
const MAX=(1n<<64n)-1n;

export interface CoreCommercePureUint64SmtV1 {
 readonly schema_version:'craft.core-commerce-pure-uint64-smt/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'one-checked-pure-uint64-calculation-arithmetic-and-error-annotation-on-valid-inputs';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly inputs:readonly Readonly<{name:string;symbol:string}>[];
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly pure_subject_sha256:string;readonly calculation_sha256:string;readonly exporter_code_sha256:string;
 readonly arithmetic_ops:readonly ('add'|'subtract'|'multiply')[];
 readonly declared_error_annotation:Readonly<{kind:'reject'|'fail';code:string}>|null;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['fuel-and-byte-budgets','input-output-wire-validation','non-arithmetic-error-annotation','declared-failure-action-execution','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'checked-uint64-arithmetic-first-arithmetic-error-and-declared-annotation-for-valid-inputs-only';
}

/** A rejected AST shape never gets an approximate translation. */
export function exportCoreCommercePureUint64SmtV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommercePureUint64SmtV1 {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);
 assertCommerceApplicationAssemblyV1(assembly);pin.assertCurrent();semantics.assertSource(semantic,capture);
 const source=sources.inspect(capture),checked=semantics.inspect(semantic),application=assembly.inspect();
 if(source.capture_sha256!==checked.source_capture_sha256||checked.source_capture_sha256!==application.source_capture_sha256||
  checked.application!==application.application)reject('InvalidSource');
 const candidates=checked.pure.declarations.filter(row=>row.name===selector&&row.kind==='Calculation');
 if(candidates.length!==1)reject('InvalidSource');
 const calculation=candidates[0]!,owned=checked.ownership.filter(row=>row.declaration===selector),service=owned[0]?.service;
 if(owned.length!==1||!service)throw new CoreCommercePureFormalErrorV1('InvalidSource');
 if(!application.services.includes(service)||calculation.result.kind!=='UInt64'||
  calculation.parameters.length<1||calculation.parameters.length>8||
  calculation.parameters.some(row=>row.type.kind!=='UInt64')||calculation.preconditions.length!==0)
  reject('UnsupportedExpression');
 const inputNames=calculation.parameters.map(row=>row.name);
 if(new Set(inputNames).size!==inputNames.length)reject('InvalidSource');
 const inputs=inputNames.map((name,i)=>({name,symbol:`Input${i}`})),symbols=new Map(inputs.map(row=>[row.name,row.symbol]));
 const lines=[
  '(set-logic QF_BV)',
  `; source_capture_sha256: ${source.capture_sha256}`,
  `; executable_sha256: ${checked.executable_sha256}`,
  `; family_sha256: ${application.family_sha256}`,
  `; pure_subject_sha256: ${checked.pure.pure_subject_sha256}`,
  `; calculation_sha256: ${dataDigest(calculation)}`,
  `; declared_error_annotation_sha256: ${dataDigest(calculation.on_evaluation_error)}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  '; Status: #b00 success, #b01 ArithmeticUnderflow, #b10 ArithmeticOverflow.',
  '; Value is meaningful only when Status is #b00. All inputs are valid UInt64.',
  '; ActionAttached records the checked pure declaration annotation on arithmetic fault.',
  '; It does not execute or prove the enclosing Operation failure action.',
  '; check-sat below checks that the declarations are satisfiable, not implementation equivalence.',
  ...inputs.map(row=>`(declare-fun ${row.symbol} () (_ BitVec 64))`),
 ];
 const ops:('add'|'subtract'|'multiply')[]=[];
 let counter=0;
 const compile=(expr:ExprV1,depth:number):{value:string;status:string}=>{
  if(depth>16||counter>32)reject('UnsupportedExpression');
  if(expr.op==='var'){
   const symbol=symbols.get(expr.name);if(!symbol)throw new CoreCommercePureFormalErrorV1('UnsupportedExpression');
   return {value:symbol,status:'#b00'};
  }
  if(expr.op==='literal'&&expr.type.kind==='scalar'&&expr.type.name==='UInt64'&&typeof expr.value==='string'&&/^\d+$/.test(expr.value)){
   const value=BigInt(expr.value);if(value>MAX)reject('UnsupportedExpression');
   return {value:`(_ bv${value} 64)`,status:'#b00'};
  }
  if(expr.op!=='binary')throw new CoreCommercePureFormalErrorV1('UnsupportedExpression');
  if(expr.operator!=='add'&&expr.operator!=='subtract'&&expr.operator!=='multiply')throw new CoreCommercePureFormalErrorV1('UnsupportedExpression');
  const left=compile(expr.left,depth+1),right=compile(expr.right,depth+1),name=`N${counter++}`;
  ops.push(expr.operator as 'add'|'subtract'|'multiply');
  const operation=expr.operator==='add'?'bvadd':expr.operator==='subtract'?'bvsub':'bvmul';
  lines.push(`(define-fun ${name}Value () (_ BitVec 64) (${operation} ${left.value} ${right.value}))`);
  const failure=expr.operator==='add'?`(bvult ${name}Value ${left.value})`:
   expr.operator==='subtract'?`(bvult ${left.value} ${right.value})`:
   `(and (not (= ${right.value} (_ bv0 64))) (not (= (bvudiv ${name}Value ${right.value}) ${left.value})))`;
  const failureCode=expr.operator==='subtract'?'#b01':'#b10';
  lines.push(`(define-fun ${name}Status () (_ BitVec 2) (ite (not (= ${left.status} #b00)) ${left.status} (ite (not (= ${right.status} #b00)) ${right.status} (ite ${failure} ${failureCode} #b00))))`);
  return {value:`${name}Value`,status:`${name}Status`};
 };
 const root=compile(calculation.body,0);
 if(ops.length<1)reject('UnsupportedExpression');
 lines.push(`(define-fun Value () (_ BitVec 64) ${root.value})`,
  `(define-fun Status () (_ BitVec 2) ${root.status})`,
  `(define-fun ActionAttached () Bool ${calculation.on_evaluation_error?'(not (= Status #b00))':'false'})`,
  '(check-sat)','');
 const smtlib2=lines.join('\n');
 const result:CoreCommercePureUint64SmtV1=coreFreeze({
  schema_version:'craft.core-commerce-pure-uint64-smt/v1-candidate' as const,language:'smtlib2' as const,
  scope:'one-checked-pure-uint64-calculation-arithmetic-and-error-annotation-on-valid-inputs' as const,
  application:application.application,selector,service,inputs,source_capture_sha256:source.capture_sha256,
  executable_sha256:checked.executable_sha256,family_sha256:application.family_sha256,
  pure_subject_sha256:checked.pure.pure_subject_sha256,calculation_sha256:dataDigest(calculation),
  exporter_code_sha256:pin.sha256,arithmetic_ops:ops,declared_error_annotation:calculation.on_evaluation_error,
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['fuel-and-byte-budgets','input-output-wire-validation','non-arithmetic-error-annotation',
   'declared-failure-action-execution','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'checked-uint64-arithmetic-first-arithmetic-error-and-declared-annotation-for-valid-inputs-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommercePureUint64SmtCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommercePureUint64SmtV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(exportCoreCommercePureUint64SmtV1(sources,capture,semantics,semantic,assembly,selector))!==dataDigest(model))
  reject('InvalidModel');
}
