/** Conditional pure Bool Rule model for a checked primitive expression subset.
 * A nonprimitive typed parameter may be present but must be unused by the
 * body; its caller checkpoint and full wire validation remain unmodeled.
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

export class CoreCommerceFormalPrimitiveRuleErrorV1 extends Error {
 constructor(readonly code:'UnsupportedTranslation'|'InvalidSource'){
  super(code);this.name='CoreCommerceFormalPrimitiveRuleErrorV1';
 }
}
const fail=(code:CoreCommerceFormalPrimitiveRuleErrorV1['code']):never=>
 {throw new CoreCommerceFormalPrimitiveRuleErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-computation-kernel'+ext,'commerce-computation-evaluate'+ext,
 'commerce-core-pure-contract'+ext,
]);
type Primitive='Bool'|'UInt64';
type Value=boolean|bigint;
type Node=Readonly<{type:Primitive;value:string;fuel:string;maxFuel:number}>;
const MAX=18446744073709551615n;
const smtString=(value:string)=>`"${value.replaceAll('"','""')}"`;

export interface CoreCommerceFormalPrimitiveRuleV1 {
 readonly schema_version:'craft.core-commerce-formal-primitive-rule/v1-candidate';
 readonly language:'smtlib2';
 readonly scope:'checked-bool-rule-body-and-output-after-valid-typed-parameters-and-sufficient-fuel';
 readonly application:string;readonly selector:string;readonly service:string;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly rule_sha256:string;readonly contract_sha256:string;readonly exporter_code_sha256:string;
 readonly function_index:number;readonly body:ExprV1;
 readonly used_primitive_inputs:readonly Readonly<{name:string;type:Primitive;symbol:string}>[];
 readonly body_max_fuel:number;readonly successful_continuation_fuel:7;
 readonly maximum_required_fuel_at_body_entry:number;
 readonly max_output_bytes:number;readonly max_value_bytes:number;
 readonly smtlib2:string;readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly ['wire-and-typed-parameter-validation','nonprimitive-parameter-checkpoint-fuel',
  'insufficient-fuel-error-order','field-record-list-policy-collection-and-call-expressions',
  'enclosing-operation-action-and-native-effect','solver-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'checked-primitive-bool-rule-short-circuit-result-and-body-output-fuel-under-sufficient-fuel-premise';
}

/** Independent concrete evaluator for the same restricted body, starting at
 * the function-body entrance with validated primitive parameters. */
export function evaluateCoreCommerceFormalPrimitiveRuleBodyV1(
 body:ExprV1,bindings:Readonly<Record<string,Value>>,
 types:Readonly<Record<string,Primitive>>,
):Readonly<{value:boolean;body_fuel:number;body_and_output_fuel:number;output_wire_hex:string}> {
 let fuel=0;
 const run=(expr:ExprV1,depth:number):{type:Primitive;value:Value}=>{
  if(depth>16)fail('UnsupportedTranslation');
  fuel++;let result:{type:Primitive;value:Value};
  if(expr.op==='var'){
   const type=types[expr.name],value=bindings[expr.name];
   if(!type||value===undefined||type==='Bool'&&typeof value!=='boolean'||
    type==='UInt64'&&(typeof value!=='bigint'||value<0n||value>MAX))fail('UnsupportedTranslation');
   result={type:type as Primitive,value:value as Value};
  }else if(expr.op==='literal'&&expr.type.kind==='scalar'&&expr.type.name==='UInt64'&&
   typeof expr.value==='string'&&/^(0|[1-9][0-9]*)$/.test(expr.value)&&BigInt(expr.value)<=MAX){
   result={type:'UInt64',value:BigInt(expr.value)};
  }else if(expr.op==='literal'&&expr.type.kind==='scalar'&&expr.type.name==='Bool'&&
   typeof expr.value==='boolean')result={type:'Bool',value:expr.value};
  else if(expr.op==='unary'&&expr.operator==='not'){
   const child=run(expr.value,depth+1);if(child.type!=='Bool')fail('UnsupportedTranslation');
   result={type:'Bool',value:!child.value};
  }else if(expr.op==='binary'){
   const left=run(expr.left,depth+1),op=expr.operator;
   if((op==='and'&&left.value===false)||(op==='or'&&left.value===true)){
    if(left.type!=='Bool')fail('UnsupportedTranslation');
    result={type:'Bool',value:left.value};
   }else{
    const right=run(expr.right,depth+1);
    if(op==='and'||op==='or'){
     if(left.type!=='Bool'||right.type!=='Bool')fail('UnsupportedTranslation');
     result={type:'Bool',value:right.value};
    }else if(op==='eq'){
     if(left.type!==right.type)fail('UnsupportedTranslation');
     result={type:'Bool',value:left.value===right.value};
    }else if(op==='lt'||op==='lte'||op==='gt'||op==='gte'){
     if(left.type!=='UInt64'||right.type!=='UInt64')fail('UnsupportedTranslation');
     const a=left.value as bigint,b=right.value as bigint;
     result={type:'Bool',value:op==='lt'?a<b:op==='lte'?a<=b:op==='gt'?a>b:a>=b};
    }else fail('UnsupportedTranslation');
   }
  }else if(expr.op==='if'){
   const condition=run(expr.condition,depth+1);
   if(condition.type!=='Bool')fail('UnsupportedTranslation');
   result=run(condition.value===true?expr.then:expr.else,depth+1);
  }else fail('UnsupportedTranslation');
  fuel+=2; // successful node checkpoint: validate + one byte-work unit
  return result!;
 };
 const root=run(body,0);
 if(root.type!=='Bool')fail('UnsupportedTranslation');
 const value=root.value as boolean;
 return coreFreeze({value,body_fuel:fuel,body_and_output_fuel:fuel+7,
  output_wire_hex:Buffer.from(value?'true':'false').toString('hex')});
}

export function exportCoreCommerceFormalPrimitiveRuleV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):CoreCommerceFormalPrimitiveRuleV1 {
 pin.assertCurrent();
 const checked=semantics.inspect(semantic),source=sources.inspect(capture),selected=assembly.inspect();
 if(checked.source_capture_sha256!==source.capture_sha256||
  selected.source_capture_sha256!==source.capture_sha256||
  checked.application!==selected.application)fail('InvalidSource');
 const matches=checked.pure.declarations.filter(row=>row.kind==='Rule'&&row.name===selector);
 if(matches.length!==1)fail('UnsupportedTranslation');
 const rule=matches[0]!;
 if(rule.result.kind!=='Bool'||rule.preconditions.length||rule.on_evaluation_error!==null)
  fail('UnsupportedTranslation');
 const ownership=checked.ownership.filter(row=>row.declaration===selector),service=ownership[0]?.service;
 if(ownership.length!==1||!service||!selected.services.includes(service))
  throw new CoreCommerceFormalPrimitiveRuleErrorV1('InvalidSource');
 const asset=source.files.find(row=>row.path==='contracts/compute-bounds.json');
 if(!asset)fail('InvalidSource');
 const limits=(parseCoreCommerceJson(asset!.text,asset!.path) as
  {computation?:{limits?:ComputationLimitsV1}}).computation?.limits;
 if(!limits)fail('InvalidSource');
 const paths=new Set(source.reconstruction.modules.map(row=>row.path));
 const contract=createCoreCommerceComputationContract(source.files.filter(row=>paths.has(row.path)),selector,
  limits as ComputationLimitsV1);
 const functionIndex=contract.functions.findIndex(row=>row.name===selector);
 if(functionIndex<0||dataDigest(contract.functions[functionIndex]?.body)!==dataDigest(rule.body))
  fail('InvalidSource');
 if(limits!.max_output_bytes<5||limits!.max_value_bytes<22)fail('UnsupportedTranslation');
 const parameters=new Map(rule.parameters.map(row=>[row.name,row.type.kind]));
 const used:Readonly<{name:string;type:Primitive;symbol:string}>[]=[];
 const usedMap=new Map<string,Node>(),lines=[
  '(set-logic ALL)',
  `; source_capture_sha256: ${source.capture_sha256}`,
  `; executable_sha256: ${checked.executable_sha256}`,
  `; family_sha256: ${selected.family_sha256}`,
  `; rule_sha256: ${dataDigest(rule)}`,
  `; contract_sha256: ${dataDigest(contract)}`,
  `; exporter_code_sha256: ${pin.sha256}`,
  '; Assumes validated typed parameters and enough fuel at function-body entry.',
  '; Record/list parameter checkpoints and wire decoding are outside this model.',
  '; Body node checkpoint costs one validate and one byte-work unit for Bool/UInt64.',
 ];
 let nodeId=0;
 const compile=(expr:ExprV1,depth:number):Node=>{
  if(depth>16||nodeId>32)fail('UnsupportedTranslation');
  const name=`N${nodeId++}`;
  let type:Primitive='Bool',value='false',fuel='0',maxFuel=0;
  if(expr.op==='var'){
   const kind=parameters.get(expr.name);
   if(kind!=='Bool'&&kind!=='UInt64')fail('UnsupportedTranslation');
   let prior=usedMap.get(expr.name);
   if(!prior){
    const symbol=`Input${used.length}`;
    used.push({name:expr.name,type:kind as Primitive,symbol});
    lines.push(`(declare-fun ${symbol} () ${kind==='Bool'?'Bool':'Int'})`);
    if(kind==='UInt64')lines.push(`(assert (and (>= ${symbol} 0) (<= ${symbol} ${MAX})))`);
    prior={type:kind as Primitive,value:symbol,fuel:'3',maxFuel:3};
    usedMap.set(expr.name,prior);
   }
   type=prior.type;value=prior.value;fuel='3';maxFuel=3;
  }else if(expr.op==='literal'&&expr.type.kind==='scalar'&&expr.type.name==='UInt64'&&
   typeof expr.value==='string'&&/^(0|[1-9][0-9]*)$/.test(expr.value)&&BigInt(expr.value)<=MAX){
   type='UInt64';value=expr.value;fuel='3';maxFuel=3;
  }else if(expr.op==='literal'&&expr.type.kind==='scalar'&&expr.type.name==='Bool'&&
   typeof expr.value==='boolean'){
   type='Bool';value=String(expr.value);fuel='3';maxFuel=3;
  }else if(expr.op==='unary'&&expr.operator==='not'){
   const child=compile(expr.value,depth+1);if(child.type!=='Bool')fail('UnsupportedTranslation');
   type='Bool';value=`(not ${child.value})`;fuel=`(+ 3 ${child.fuel})`;maxFuel=3+child.maxFuel;
  }else if(expr.op==='binary'){
   const left=compile(expr.left,depth+1),right=compile(expr.right,depth+1),op=expr.operator;
   if(op==='and'||op==='or'){
    if(left.type!=='Bool'||right.type!=='Bool')fail('UnsupportedTranslation');
    type='Bool';value=`(${op} ${left.value} ${right.value})`;
    fuel=`(ite ${op==='and'?left.value:`(not ${left.value})`} (+ 3 ${left.fuel} ${right.fuel}) (+ 3 ${left.fuel}))`;
    maxFuel=3+left.maxFuel+right.maxFuel;
   }else if(op==='eq'){
    if(left.type!==right.type)fail('UnsupportedTranslation');
    type='Bool';value=`(= ${left.value} ${right.value})`;
    fuel=`(+ 3 ${left.fuel} ${right.fuel})`;maxFuel=3+left.maxFuel+right.maxFuel;
   }else if(op==='lt'||op==='lte'||op==='gt'||op==='gte'){
    if(left.type!=='UInt64'||right.type!=='UInt64')fail('UnsupportedTranslation');
    type='Bool';value=`(${op==='lt'?'<':op==='lte'?'<=':op==='gt'?'>':'>='} ${left.value} ${right.value})`;
    fuel=`(+ 3 ${left.fuel} ${right.fuel})`;maxFuel=3+left.maxFuel+right.maxFuel;
   }else fail('UnsupportedTranslation');
  }else if(expr.op==='if'){
   const condition=compile(expr.condition,depth+1),then=compile(expr.then,depth+1),otherwise=compile(expr.else,depth+1);
   if(condition.type!=='Bool'||then.type!==otherwise.type)fail('UnsupportedTranslation');
   type=then.type;value=`(ite ${condition.value} ${then.value} ${otherwise.value})`;
   fuel=`(ite ${condition.value} (+ 3 ${condition.fuel} ${then.fuel}) (+ 3 ${condition.fuel} ${otherwise.fuel}))`;
   maxFuel=3+condition.maxFuel+Math.max(then.maxFuel,otherwise.maxFuel);
  }else fail('UnsupportedTranslation');
  lines.push(`(define-fun ${name}Value () ${type==='Bool'?'Bool':'Int'} ${value})`,
   `(define-fun ${name}Fuel () Int ${fuel})`);
  return {type:type!,value:`${name}Value`,fuel:`${name}Fuel`,maxFuel:maxFuel!};
 };
 const root=compile(rule.body,0);
 if(root.type!=='Bool')fail('UnsupportedTranslation');
 lines.push(
  `(declare-fun RemainingFuelAtBodyEntry () Int)`,
  `(assert (>= RemainingFuelAtBodyEntry ${root.maxFuel+7}))`,
  `(define-fun RuleValue () Bool ${root.value})`,
  `(define-fun BodyFuel () Int ${root.fuel})`,
  `(define-fun BodyAndOutputFuel () Int (+ BodyFuel 7))`,
  `(define-fun OutputWire () String (ite RuleValue ${smtString('true')} ${smtString('false')}))`,
  '',
 );
 const smtlib2=lines.join('\n');
 const model=coreFreeze({
  schema_version:'craft.core-commerce-formal-primitive-rule/v1-candidate' as const,
  language:'smtlib2' as const,
  scope:'checked-bool-rule-body-and-output-after-valid-typed-parameters-and-sufficient-fuel' as const,
  application:selected.application,selector,service,
  source_capture_sha256:source.capture_sha256,executable_sha256:checked.executable_sha256,
  family_sha256:selected.family_sha256,rule_sha256:dataDigest(rule),contract_sha256:dataDigest(contract),
  exporter_code_sha256:pin.sha256,function_index:functionIndex,body:rule.body,
  used_primitive_inputs:used,body_max_fuel:root.maxFuel,successful_continuation_fuel:7 as const,
  maximum_required_fuel_at_body_entry:root.maxFuel+7,
  max_output_bytes:limits!.max_output_bytes,max_value_bytes:limits!.max_value_bytes,
  smtlib2,smtlib2_sha256:sha(smtlib2),
  unsupported_semantics:['wire-and-typed-parameter-validation','nonprimitive-parameter-checkpoint-fuel',
   'insufficient-fuel-error-order','field-record-list-policy-collection-and-call-expressions',
   'enclosing-operation-action-and-native-effect','solver-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'checked-primitive-bool-rule-short-circuit-result-and-body-output-fuel-under-sufficient-fuel-premise' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);assembly.assertCurrent();pin.assertCurrent();
 return model;
}
