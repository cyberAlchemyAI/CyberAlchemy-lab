import test from 'node:test';
import assert from 'node:assert/strict';
import {createCommerceValueKernel} from '../../src/commerce/commerce-computation-kernel.js';
import {evaluateCoreCommerceFormalJsonInputV1}
 from '../../src/commerce/commerce-core-formal-json-input-v1.js';
import {evaluateCoreCommerceFormalPureWireV1,CoreCommerceFormalPureWireErrorV1}
 from '../../src/commerce/commerce-core-formal-pure-wire-v1.js';
import type {ExprV1} from '../../src/commerce/commerce-data-v1.js';
import type {CoreCommerceFormalInputFieldsV1} from '../../src/commerce/commerce-core-formal-input-fields-v1.js';
import type {CoreCommerceFormalPureOutcomeV1} from '../../src/commerce/commerce-core-formal-pure-outcome-v1.js';

const names=['subtotal','discountMinor','taxMinor','shippingMinor'];
const type={kind:'scalar',name:'UInt64'} as const;
const v=(name:string):ExprV1=>({op:'var',name});
const binary=(operator:'add'|'subtract',left:ExprV1,right:ExprV1):ExprV1=>
 ({op:'binary',operator,left,right});
const body=binary('add',binary('add',binary('subtract',v('subtotal'),v('discountMinor')),
 v('taxMinor')),v('shippingMinor'));
const fields={max_input_bytes:4096,max_value_bytes:524288,fuel:100000,input_fields:names} as CoreCommerceFormalInputFieldsV1;
const pure={inputs:names,max_output_bytes:524288,max_value_bytes:524288,fuel:100000,
 max_fuel_used_after_successful_input_at_max_wire_size:1000,
 declared_error_annotation:{kind:'fail',code:'calculation-failed'}} as CoreCommerceFormalPureOutcomeV1;
const encoder=new TextEncoder();
const wire=(values:readonly string[])=>encoder.encode('{'+names.map((name,i)=>
 JSON.stringify(name)+':'+JSON.stringify(values[i])).join(',')+'}');
const valueKernel=()=>createCommerceValueKernel({
 schema_version:'craft.core-computation/v1-candidate',
 limits:{max_input_bytes:fields.max_input_bytes,max_value_bytes:fields.max_value_bytes,
  max_output_bytes:pure.max_output_bytes,fuel:fields.fuel,max_items:4096,max_call_depth:16},
 values:{records:[],enums:[],refinements:[],collection_predicates:[]},
 inputs:names.map(name=>({name,type})),result:type,
},{isProxy:()=>false,isUint8Array:(value:unknown)=>value instanceof Uint8Array,
 isSharedArrayBuffer:()=>false},{record:()=>true,predicate:()=>true});

/** Exercise the checked kernel primitives in the same call/AST order as the
 * selected reference evaluator, without loading the Commerce workflow. */
const reference=(bytes:Uint8Array)=>{
 const kernel=valueKernel(),account=kernel.fresh(),scalar=type;
 const site=(path:string)=>kernel.site(path,[],['PayableTotal']);
 let phase:'input-validation'|'expression'|'complete'='input-validation';
 try{
  const env=kernel.input(bytes,account) as Record<string,bigint>;
  phase='expression';
  kernel.charge(account,kernel.site('$.expression'));
  const args=names.map((name,i)=>{
   const s=kernel.site(`$.expression.arguments[${i}]`);
   kernel.charge(account,s);
   return kernel.checkpoint(env[name],scalar,account,s) as bigint;
  });
  const callSite=site('$.expression');
  kernel.enter(account,callSite);
  const params=Object.fromEntries(names.map((name,i)=>[
   name,kernel.checkpoint(args[i],scalar,account,callSite),
  ])) as Record<string,bigint>;
  const run=(expr:ExprV1,path:string):bigint=>{
   const s=site(path);kernel.charge(account,s);
   let value:bigint;
   if(expr.op==='var')value=params[expr.name]!;
   else if(expr.op==='binary'&&(expr.operator==='add'||expr.operator==='subtract')){
    const left=run(expr.left,path+'.left'),right=run(expr.right,path+'.right');
    value=expr.operator==='add'?left+right:left-right;
    if(value<0n)kernel.fail('ArithmeticUnderflow',s);
    if(value>18446744073709551615n)kernel.fail('ArithmeticOverflow',s);
   }else throw new Error('unsupported test AST');
   return kernel.checkpoint(value,scalar,account,s) as bigint;
  };
  let result:bigint;
  try{result=kernel.checkpoint(run(body,'$.functions[0].body'),scalar,account,callSite) as bigint;}
  catch(error){throw kernel.annotate(error,'PayableTotal',pure.declared_error_annotation);}
  const value=kernel.checkpoint(result,scalar,account,kernel.site('$.expression')) as bigint;
  const output=kernel.output(value,account) as Uint8Array;
  phase='complete';
  return {status:'success',phase,error_path:'',fuel_used:account.used,
   value,wire_hex:Buffer.from(output).toString('hex'),pure_error_annotation_attached:false};
 }catch(error){
  const failed=kernel.failure(error,account);
  return {status:failed.error.code,phase,error_path:failed.error.expression_path,
   fuel_used:failed.fuel_used,value:null,wire_hex:null,
   pure_error_annotation_attached:(error as {actions?:unknown[]}).actions?.length===1};
 }
};

test('bounded concrete wire to PayableTotal output/fault/fuel agrees with kernel primitives',()=>{
 const cases=[['10','1','2','3'],['0','0','0','0'],['1','2','0','0'],
  ['18446744073709551615','0','0','0'],['18446744073709551615','0','1','0'],
  ['18446744073709551614','1','1','2'],['10','1','18446744073709551615','0'],
  ['10','1','2','18446744073709551615'],['10','-1','2','3'],['10','01','2','3']];
 for(const values of cases){
  const bytes=wire(values),input=evaluateCoreCommerceFormalJsonInputV1(fields,bytes);
  const projected=evaluateCoreCommerceFormalPureWireV1(input,pure,body,0);
  const actual=reference(bytes);
  for(const key of ['status','phase','error_path','fuel_used','value','wire_hex',
   'pure_error_annotation_attached'] as const)
   assert.deepEqual(projected[key],actual[key],`${values.join(',')} ${key}`);
 }
});

test('unmodeled expression and insufficient proven output budget reject translation',()=>{
 const input=evaluateCoreCommerceFormalJsonInputV1(fields,wire(['10','1','2','3']));
 assert.throws(()=>evaluateCoreCommerceFormalPureWireV1(input,pure,
  {op:'binary',operator:'multiply',left:v('subtotal'),right:v('taxMinor')},0),
 (error:unknown)=>error instanceof CoreCommerceFormalPureWireErrorV1&&error.code==='UnsupportedTranslation');
 assert.throws(()=>evaluateCoreCommerceFormalPureWireV1(input,{...pure,max_output_bytes:2},body,0),
 (error:unknown)=>error instanceof CoreCommerceFormalPureWireErrorV1&&error.code==='UnsupportedTranslation');
});
