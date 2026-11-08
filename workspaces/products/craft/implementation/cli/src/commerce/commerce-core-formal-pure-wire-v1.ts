/** Bounded concrete-wire composition of checked input and pure UInt64 output.
 * This reaches the same Calculation, but no enclosing Operation or native
 * effect. It is a per-input witness, not universal JSON SMT translation.
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
import type {ExprV1,ComputationLimitsV1} from './commerce-data-v1.js';
import {createCoreCommerceComputationContract} from './commerce-core-pure-contract.js';
import {exportCoreCommerceFormalPureOutcomeV1,type CoreCommerceFormalPureOutcomeV1}
 from './commerce-core-formal-pure-outcome-v1.js';
import {exportCoreCommerceFormalJsonInputWitnessV1,
 type CoreCommerceFormalJsonInputResultV1,type CoreCommerceFormalJsonInputWitnessV1}
 from './commerce-core-formal-json-input-v1.js';

export class CoreCommerceFormalPureWireErrorV1 extends Error {
 constructor(readonly code:'UnsupportedTranslation'|'InvalidSource'){
  super(code);this.name='CoreCommerceFormalPureWireErrorV1';
 }
}
const reject=(code:CoreCommerceFormalPureWireErrorV1['code']):never=>{throw new CoreCommerceFormalPureWireErrorV1(code);};
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-kernel'+ext,'commerce-computation-evaluate'+ext,
 'commerce-core-formal-json-input-v1'+ext,'commerce-core-formal-pure-outcome-v1'+ext,
 'commerce-core-pure-contract'+ext,
]);
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const MAX=18446744073709551615n;

export type CoreCommerceFormalPureWireResultV1=Readonly<{
 scope:'one-bounded-concrete-wire-checked-uint64-calculation';
 status:'success'|'InputType'|'InputBound'|'InvalidUnicode'|'ResourceLimit'|
  'ArithmeticUnderflow'|'ArithmeticOverflow';
 phase:'input-validation'|'expression'|'complete';
 error_path:string;fuel_used:number;value:bigint|null;wire_hex:string|null;
 pure_error_annotation_attached:boolean;
 claim_ceiling:'bounded-concrete-input-plus-checked-arithmetic-and-output-budget-only';
}>;

/** Restricted evaluator for the exact AST shapes accepted by the existing
 * source-bound pure exporter: UInt64 var/literal/add/subtract. Source bounds
 * prove this call has adequate fuel and 22-byte scalar output capacity. */
export function evaluateCoreCommerceFormalPureWireV1(
 input:CoreCommerceFormalJsonInputResultV1,
 pure:Pick<CoreCommerceFormalPureOutcomeV1,'inputs'|'fuel'|'max_output_bytes'|
  'max_value_bytes'|'max_fuel_used_after_successful_input_at_max_wire_size'|'declared_error_annotation'>,
 body:ExprV1,functionIndex:number,
):CoreCommerceFormalPureWireResultV1 {
 const scope='one-bounded-concrete-wire-checked-uint64-calculation' as const;
 const claim_ceiling='bounded-concrete-input-plus-checked-arithmetic-and-output-budget-only' as const;
 if(input.status!=='ready_for_expression')return coreFreeze({scope,status:input.status,
  phase:'input-validation' as const,error_path:input.fault_path,fuel_used:input.fuel_used,
  value:null,wire_hex:null,pure_error_annotation_attached:false,claim_ceiling});
 if(!input.values||pure.inputs.length!==input.values.length||pure.inputs.length<1||
  !Number.isSafeInteger(functionIndex)||functionIndex<0||pure.max_output_bytes<22||
  pure.max_value_bytes<22||
  pure.max_fuel_used_after_successful_input_at_max_wire_size>pure.fuel)
  reject('UnsupportedTranslation');
 const symbols=new Map(pure.inputs.map((name,i)=>[name,input.values![i]!]));
 let used=input.fuel_used+2+5*pure.inputs.length;
 if(used>pure.fuel)reject('UnsupportedTranslation');
 class ArithmeticFault extends Error {
  constructor(readonly code:'ArithmeticUnderflow'|'ArithmeticOverflow',readonly expressionPath:string){super(code);}
 }
 const checkpoint=(value:bigint)=>{
  if(value<0n||value>MAX)reject('UnsupportedTranslation');
  used+=2;
 };
 const evalExpr=(expr:ExprV1,expressionPath:string,depth:number):bigint=>{
  if(depth>16)reject('UnsupportedTranslation');
  used++;
  let value=0n;
  if(expr.op==='var'){
   const selected=symbols.get(expr.name);if(selected===undefined)reject('UnsupportedTranslation');
   value=selected as bigint;
  }else if(expr.op==='literal'&&expr.type.kind==='scalar'&&expr.type.name==='UInt64'&&
   typeof expr.value==='string'&&/^(0|[1-9][0-9]*)$/.test(expr.value)){
   value=BigInt(expr.value);
   if(value>MAX)reject('UnsupportedTranslation');
  }else if(expr.op==='binary'&&(expr.operator==='add'||expr.operator==='subtract')){
   const left=evalExpr(expr.left,expressionPath+'.left',depth+1);
   const right=evalExpr(expr.right,expressionPath+'.right',depth+1);
   value=expr.operator==='add'?left+right:left-right;
   if(value<0n)throw new ArithmeticFault('ArithmeticUnderflow',expressionPath);
   if(value>MAX)throw new ArithmeticFault('ArithmeticOverflow',expressionPath);
  }else reject('UnsupportedTranslation');
  checkpoint(value);
  return value;
 };
 try{
  const value=evalExpr(body,`$.functions[${functionIndex}].body`,0);
  used+=7; // function return, call result, output checkpoint and output byte work
  if(used>pure.fuel)reject('UnsupportedTranslation');
  const wire='"'+value.toString()+'"';
  if(Buffer.byteLength(wire)>pure.max_output_bytes||Buffer.byteLength(wire)>pure.max_value_bytes)
   reject('UnsupportedTranslation');
  return coreFreeze({scope,status:'success' as const,phase:'complete' as const,
   error_path:'',fuel_used:used,value,wire_hex:Buffer.from(wire).toString('hex'),
   pure_error_annotation_attached:false,claim_ceiling});
 }catch(error){
  if(!(error instanceof ArithmeticFault))throw error;
  if(used>pure.fuel)reject('UnsupportedTranslation');
  return coreFreeze({scope,status:error.code,phase:'expression' as const,
   error_path:error.expressionPath,fuel_used:used,value:null,wire_hex:null,
   pure_error_annotation_attached:pure.declared_error_annotation!==null,claim_ceiling});
 }
}

export interface CoreCommerceFormalPureWireWitnessV1 {
 readonly schema_version:'craft.core-commerce-formal-pure-wire-witness/v1-candidate';
 readonly language:'smtlib2';readonly scope:'one-bounded-concrete-input-checked-pure-calculation';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly input_witness_sha256:string;readonly pure_model_sha256:string;
 readonly exporter_code_sha256:string;readonly result:CoreCommerceFormalPureWireResultV1;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['universal-json-parser-relation','input-object-and-shared-buffer-validation',
  'admitted-buffers-above-4096-bytes','enclosing-operation-error-action-execution',
  'native-transaction-effect-and-temporal-equivalence','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'grounded-bounded-input-arithmetic-output-witness-only';
}

export function exportCoreCommerceFormalPureWireWitnessV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,bytes:Uint8Array,
):CoreCommerceFormalPureWireWitnessV1 {
 pin.assertCurrent();
 const input=exportCoreCommerceFormalJsonInputWitnessV1(
  sources,capture,semantics,semantic,assembly,selector,bytes);
 const pure=exportCoreCommerceFormalPureOutcomeV1(sources,capture,semantics,semantic,assembly,selector);
 if(input.source_capture_sha256!==pure.source_capture_sha256||
  input.executable_sha256!==pure.executable_sha256||
  input.fields_model_sha256!==pure.input_fields_model_sha256)reject('InvalidSource');
 const source=sources.inspect(capture),checked=semantics.inspect(semantic);
 const asset=source.files.find(row=>row.path==='contracts/compute-bounds.json');
 if(!asset)throw new CoreCommerceFormalPureWireErrorV1('InvalidSource');
 const limits=(parseCoreCommerceJson(asset.text,asset.path) as
  {computation?:{limits?:ComputationLimitsV1}}).computation?.limits;
 if(!limits)throw new CoreCommerceFormalPureWireErrorV1('InvalidSource');
 const paths=new Set(source.reconstruction.modules.map(row=>row.path));
 const contract=createCoreCommerceComputationContract(
  source.files.filter(row=>paths.has(row.path)),selector,limits);
 if(dataDigest(contract)!==pure.contract_sha256)reject('InvalidSource');
 const functionIndex=contract.functions.findIndex(row=>row.name===selector);
 const functionRow=contract.functions[functionIndex];
 const declaration=checked.pure.declarations.find(row=>row.kind==='Calculation'&&row.name===selector);
 if(functionIndex<0||!functionRow||!declaration||
  dataDigest(functionRow.body)!==dataDigest(declaration.body))
  throw new CoreCommerceFormalPureWireErrorV1('InvalidSource');
 const result=evaluateCoreCommerceFormalPureWireV1(input.result,pure,declaration.body,functionIndex);
 const status={success:0,InputType:1,InputBound:2,InvalidUnicode:3,ResourceLimit:4,
  ArithmeticUnderflow:5,ArithmeticOverflow:6}[result.status];
 const smtlib2=[
  input.smtlib2,
  `; checked_pure_model_sha256: ${pure.smtlib2_sha256}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  '; Grounded concrete-input result; this does not encode universal parser or native effects.',
  `(define-fun PureWireStatus () Int ${status})`,
  `(define-fun PureWireFuelUsed () Int ${result.fuel_used})`,
  `(define-fun PureWireFaultPath () String ${JSON.stringify(result.error_path)})`,
  `(define-fun PureWireActionAttached () Bool ${result.pure_error_annotation_attached})`,
  ...(result.value===null?[]:[`(define-fun PureWireValue () Int ${result.value})`]),
  ...(result.wire_hex===null?[]:[`; output_wire_hex: ${result.wire_hex}`]),
  '',
 ].join('\n');
 const witness=coreFreeze({
  schema_version:'craft.core-commerce-formal-pure-wire-witness/v1-candidate' as const,
  language:'smtlib2' as const,scope:'one-bounded-concrete-input-checked-pure-calculation' as const,
  application:pure.application,selector,service:pure.service,
  source_capture_sha256:pure.source_capture_sha256,executable_sha256:pure.executable_sha256,
  family_sha256:pure.family_sha256,input_witness_sha256:input.smtlib2_sha256,
  pure_model_sha256:pure.smtlib2_sha256,exporter_code_sha256:pin.sha256,result,
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['universal-json-parser-relation','input-object-and-shared-buffer-validation',
   'admitted-buffers-above-4096-bytes','enclosing-operation-error-action-execution',
   'native-transaction-effect-and-temporal-equivalence','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'grounded-bounded-input-arithmetic-output-witness-only' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return witness;
}
