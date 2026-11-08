/** Conditional formal outcome of one checked pure UInt64 Calculation.
 * Inputs are already successfully decoded; their wire/parser relation and any
 * enclosing Operation error action remain outside this model.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {parseCoreCommerceJson,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import {exportCoreCommerceFormalInputFieldsV1} from './commerce-core-formal-input-fields-v1.js';
import {createCoreCommerceComputationContract} from './commerce-core-pure-contract.js';
import type {ExprV1,ComputationLimitsV1} from './commerce-data-v1.js';

export class CoreCommerceFormalPureOutcomeErrorV1 extends Error {
 constructor(readonly code:'UnsupportedExpression'|'UnsupportedBudget'|'InvalidSource'|'InvalidModel'){
  super(code);this.name='CoreCommerceFormalPureOutcomeErrorV1';
 }
}
const reject=(code:CoreCommerceFormalPureOutcomeErrorV1['code']):never=>{throw new CoreCommerceFormalPureOutcomeErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-evaluate'+ext,'commerce-computation-kernel'+ext,
 'commerce-core-pure-contract'+ext,
 'commerce-core-formal-input-fields-v1'+ext,
]);
const MAX=18446744073709551615n;

export interface CoreCommerceFormalPureOutcomeV1 {
 readonly schema_version:'craft.core-commerce-formal-pure-outcome/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'checked-pure-uint64-call-first-arithmetic-fault-and-output-for-valid-decoded-inputs';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly inputs:readonly string[];readonly arithmetic_node_count:number;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly calculation_sha256:string;readonly contract_sha256:string;readonly input_fields_model_sha256:string;
 readonly bounds_asset_sha256:string;readonly exporter_code_sha256:string;
 readonly max_output_bytes:number;readonly max_value_bytes:number;readonly fuel:number;
 readonly max_fuel_used_after_successful_input_at_max_wire_size:number;
 readonly declared_error_annotation:Readonly<{kind:'reject'|'fail';code:string}>|null;
 readonly assumed_input:'ordinary-admitted-bytes-with-successful-parse-and-valid-decoded-uint64-fields';
 readonly status_codes:Readonly<{success:0;ArithmeticUnderflow:1;ArithmeticOverflow:2}>;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['utf8-and-json-parser-translation','parser-to-decoded-value-binding','invalid-input-priority','enclosing-operation-failure-action','generated-native-parity','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'conditional-first-arithmetic-fault-path-fuel-annotation-and-output-of-source-reconstructed-pure-call';
}

/** The evaluator charges one fuel per expression node, then a successful
 * UInt64 checkpoint charges one validation and one 3..22 byte size unit.
 * Its reconstructed top-level call also charges its node, argument nodes,
 * function entry, parameter checkpoints, and successful return checkpoints.
 * A failing arithmetic node has no checkpoint. Output repeats the checkpoint
 * and charges one 3..22 byte wire unit. Bounds below prove no resource/output
 * fault for this restricted call after valid input decoding. */
export function exportCoreCommerceFormalPureOutcomeV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalPureOutcomeV1 {
 pin.assertCurrent();
 const fields=exportCoreCommerceFormalInputFieldsV1(sources,capture,semantics,semantic,assembly,selector);
 const checked=semantics.inspect(semantic),source=sources.inspect(capture);
 const rows=checked.pure.declarations.filter(row=>row.kind==='Calculation'&&row.name===selector);
 if(rows.length!==1)reject('InvalidSource');
 const calculation=rows[0]!;
 if(calculation.preconditions.length||calculation.result.kind!=='UInt64'||
  calculation.parameters.length!==fields.input_fields.length||
  calculation.parameters.some((row,i)=>row.name!==fields.input_fields[i]||row.type.kind!=='UInt64'))
  reject('UnsupportedExpression');
 const asset=source.files.find(row=>row.path==='contracts/compute-bounds.json');
 if(!asset)throw new CoreCommerceFormalPureOutcomeErrorV1('InvalidSource');
 if(asset.sha256!==fields.bounds_asset_sha256||
  fields.calculation_sha256!==dataDigest(calculation))reject('InvalidSource');
 const bounds=parseCoreCommerceJson(asset.text,asset.path) as
  {computation?:{limits?:ComputationLimitsV1}};
 const limits=bounds.computation?.limits;
 if(!limits)throw new CoreCommerceFormalPureOutcomeErrorV1('InvalidSource');
 const maxOutput=limits.max_output_bytes;
 if(typeof maxOutput!=='number'||!Number.isSafeInteger(maxOutput)||maxOutput<22||
  limits.max_value_bytes!==fields.max_value_bytes)reject('UnsupportedBudget');
 const max_output_bytes=maxOutput as number;
 const paths=new Set(source.reconstruction.modules.map(row=>row.path));
 const texts=source.files.filter(row=>paths.has(row.path));
 const contract=createCoreCommerceComputationContract(texts,selector,limits);
 const call=contract.expression;
 if(call.op!=='call')throw new CoreCommerceFormalPureOutcomeErrorV1('UnsupportedExpression');
 const functionIndex=contract.functions.findIndex(row=>row.name===selector);
 if(contract.source_node!==selector||call.declaration!==selector||
  functionIndex<0||contract.functions[functionIndex]?.kind!=='Calculation'||
  dataDigest(contract.functions[functionIndex]!.body)!==dataDigest(calculation.body)||
  dataDigest(contract.functions[functionIndex]!.on_evaluation_error)!==dataDigest(calculation.on_evaluation_error)||
  contract.inputs.length!==fields.input_fields.length||
  contract.inputs.some((row,i)=>row.name!==fields.input_fields[i]||row.type.kind!=='scalar'||row.type.name!=='UInt64')||
  call.arguments.length!==fields.input_fields.length||
  call.arguments.some((row,i)=>row.op!=='var'||row.name!==fields.input_fields[i])||
  contract.result.kind!=='scalar'||contract.result.name!=='UInt64'||
  contract.limits.max_input_bytes!==fields.max_input_bytes||contract.limits.max_output_bytes!==max_output_bytes||
  contract.limits.max_value_bytes!==fields.max_value_bytes||contract.limits.fuel!==fields.fuel)reject('InvalidSource');
 if(contract.limits.max_call_depth<1)reject('UnsupportedBudget');
 const wrapperFuelBeforeBody=2+5*fields.input_fields.length;
 const wrapperFuelAfterSuccess=7;
 const symbols=new Map(fields.input_fields.map((name,i)=>[name,`Input${i}`]));
 const lines=[
  '(set-logic ALL)',
  `; source_capture_sha256: ${fields.source_capture_sha256}`,
  `; executable_sha256: ${fields.executable_sha256}`,
  `; family_sha256: ${fields.family_sha256}`,
  `; calculation_sha256: ${fields.calculation_sha256}`,
  `; reconstructed_contract_sha256: ${dataDigest(contract)}`,
  `; input_fields_model_sha256: ${fields.smtlib2_sha256}`,
  `; bounds_asset_sha256: ${asset.sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  '; Preconditions: valid decoded UInt64 fields from the same admitted ordinary wire.',
  '; InputByteCount and InputN are honest observations of that wire and its decoder.',
  '; Status: 0 success, 1 ArithmeticUnderflow, 2 ArithmeticOverflow.',
  '; ErrorPath and OutputWire are meaningful only on fault and success respectively.',
  '; This is the source-reconstructed top-level pure call, not its enclosing Operation.',
  `; Function-body paths start at $.functions[${functionIndex}].body.`,
  `; Wrapper fuel before body: ${wrapperFuelBeforeBody}; success after body: ${wrapperFuelAfterSuccess}.`,
  '(declare-fun InputByteCount () Int)',
  `(assert (and (>= InputByteCount 0) (<= InputByteCount ${fields.max_input_bytes})))`,
  ...fields.input_fields.flatMap((name,i)=>[
   `; ${name}`,
   `(declare-fun Input${i} () Int)`,
   `(assert (and (>= Input${i} 0) (<= Input${i} ${MAX})))`,
  ]),
  '(define-fun InputByteWork () Int (div (+ InputByteCount 31) 32))',
  `(define-fun InputFuel () Int (+ InputByteWork ${3*fields.input_fields.length}))`,
 ];
 type Node={value:string;status:string;fuel:string;errorPath:string;nodeCount:number;arithmeticCount:number};
 let index=0;
 const compile=(expr:ExprV1,expressionPath:string,depth:number):Node=>{
  if(depth>16||index>32)reject('UnsupportedExpression');
  if(expr.op==='var'){
   const input=symbols.get(expr.name);if(!input)reject('UnsupportedExpression');
   const name=`N${index++}`;
   lines.push(`(define-fun ${name}Value () Int ${input})`,
    `(define-fun ${name}Status () Int 0)`,
    `(define-fun ${name}Fuel () Int 3)`,
    `(define-fun ${name}ErrorPath () String "")`);
   return {value:`${name}Value`,status:`${name}Status`,fuel:`${name}Fuel`,
    errorPath:`${name}ErrorPath`,nodeCount:1,arithmeticCount:0};
  }
  if(expr.op==='literal'&&expr.type.kind==='scalar'&&expr.type.name==='UInt64'&&
   typeof expr.value==='string'&&/^(0|[1-9][0-9]*)$/.test(expr.value)&&BigInt(expr.value)<=MAX){
   const name=`N${index++}`;
   lines.push(`(define-fun ${name}Value () Int ${expr.value})`,
    `(define-fun ${name}Status () Int 0)`,
    `(define-fun ${name}Fuel () Int 3)`,
    `(define-fun ${name}ErrorPath () String "")`);
   return {value:`${name}Value`,status:`${name}Status`,fuel:`${name}Fuel`,
    errorPath:`${name}ErrorPath`,nodeCount:1,arithmeticCount:0};
  }
  if(expr.op!=='binary')throw new CoreCommerceFormalPureOutcomeErrorV1('UnsupportedExpression');
  if(expr.operator!=='add'&&expr.operator!=='subtract')throw new CoreCommerceFormalPureOutcomeErrorV1('UnsupportedExpression');
  const left=compile(expr.left,expressionPath+'.left',depth+1);
  const right=compile(expr.right,expressionPath+'.right',depth+1);
  const name=`N${index++}`,subtract=expr.operator==='subtract';
  const value=`(${subtract?'-':'+'} ${left.value} ${right.value})`;
  const selfFault=subtract?`(< ${name}Value 0)`:`(> ${name}Value ${MAX})`;
  const ownStatus=subtract?1:2;
  lines.push(
   `(define-fun ${name}Value () Int ${value})`,
   `(define-fun ${name}SelfFault () Bool ${selfFault})`,
   `(define-fun ${name}Status () Int (ite (not (= ${left.status} 0)) ${left.status} (ite (not (= ${right.status} 0)) ${right.status} (ite ${name}SelfFault ${ownStatus} 0))))`,
   `(define-fun ${name}Fuel () Int (ite (not (= ${left.status} 0)) (+ 1 ${left.fuel}) (ite (not (= ${right.status} 0)) (+ 1 ${left.fuel} ${right.fuel}) (ite ${name}SelfFault (+ 1 ${left.fuel} ${right.fuel}) (+ 3 ${left.fuel} ${right.fuel})))))`,
   `(define-fun ${name}ErrorPath () String (ite (not (= ${left.status} 0)) ${left.errorPath} (ite (not (= ${right.status} 0)) ${right.errorPath} (ite ${name}SelfFault ${JSON.stringify(expressionPath)} ""))))`,
  );
  return {value:`${name}Value`,status:`${name}Status`,fuel:`${name}Fuel`,
   errorPath:`${name}ErrorPath`,nodeCount:left.nodeCount+right.nodeCount+1,
   arithmeticCount:left.arithmeticCount+right.arithmeticCount+1};
 };
 const root=compile(calculation.body,`$.functions[${functionIndex}].body`,0);
 if(root.arithmeticCount<1||root.nodeCount!==index)reject('UnsupportedExpression');
 const maxFuel=fields.worst_admitted_input_byte_work+3*fields.input_fields.length+
  wrapperFuelBeforeBody+3*root.nodeCount+wrapperFuelAfterSuccess;
 if(maxFuel>fields.fuel)reject('UnsupportedBudget');
 lines.push(
  `(define-fun Status () Int ${root.status})`,
  `(define-fun ErrorPath () String ${root.errorPath})`,
  `(define-fun ActionAttached () Bool ${calculation.on_evaluation_error?'(not (= Status 0))':'false'})`,
  `(define-fun Value () Int ${root.value})`,
  '(define-fun OutputWire () String (ite (= Status 0) (str.++ (str.from_code 34) (str.from_int Value) (str.from_code 34)) ""))',
  `(define-fun FuelUsed () Int (+ InputFuel ${wrapperFuelBeforeBody} ${root.fuel} (ite (= Status 0) ${wrapperFuelAfterSuccess} 0)))`,
  `(assert (=> (= Status 0) (and (<= (str.len OutputWire) ${max_output_bytes}) (<= (str.len OutputWire) ${fields.max_value_bytes}))))`,
  `(assert (<= FuelUsed ${fields.fuel}))`,
  '',
 );
 const smtlib2=lines.join('\n');
 const result:CoreCommerceFormalPureOutcomeV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-pure-outcome/v1-candidate' as const,
  language:'smtlib2' as const,
  scope:'checked-pure-uint64-call-first-arithmetic-fault-and-output-for-valid-decoded-inputs' as const,
  application:fields.application,selector,service:fields.service,inputs:fields.input_fields,
  arithmetic_node_count:root.arithmeticCount,
  source_capture_sha256:fields.source_capture_sha256,executable_sha256:fields.executable_sha256,
  family_sha256:fields.family_sha256,calculation_sha256:fields.calculation_sha256,
  contract_sha256:dataDigest(contract),
  input_fields_model_sha256:fields.smtlib2_sha256,bounds_asset_sha256:asset.sha256,
  exporter_code_sha256:pin.sha256,max_output_bytes,max_value_bytes:fields.max_value_bytes,
  fuel:fields.fuel,max_fuel_used_after_successful_input_at_max_wire_size:maxFuel,
  declared_error_annotation:calculation.on_evaluation_error,
  assumed_input:'ordinary-admitted-bytes-with-successful-parse-and-valid-decoded-uint64-fields' as const,
  status_codes:{success:0 as const,ArithmeticUnderflow:1 as const,ArithmeticOverflow:2 as const},
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['utf8-and-json-parser-translation','parser-to-decoded-value-binding','invalid-input-priority',
   'enclosing-operation-failure-action','generated-native-parity','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'conditional-first-arithmetic-fault-path-fuel-annotation-and-output-of-source-reconstructed-pure-call' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalPureOutcomeCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,model:CoreCommerceFormalPureOutcomeV1,
):void {
 if(!model||typeof model!=='object'||typeof model.smtlib2!=='string'||
  model.smtlib2_sha256!==sha(model.smtlib2)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalPureOutcomeV1(
   sources,capture,semantics,semantic,assembly,selector)))reject('InvalidModel');
}
