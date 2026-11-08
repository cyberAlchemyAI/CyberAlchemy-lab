import test from 'node:test';
import assert from 'node:assert/strict';
import {createCommerceValueKernel} from '../../src/commerce/commerce-computation-kernel.js';
import {evaluateCoreCommerceFormalPrimitiveRuleBodyV1,CoreCommerceFormalPrimitiveRuleErrorV1}
 from '../../src/commerce/commerce-core-formal-primitive-rule-v1.js';
import type {ExprV1} from '../../src/commerce/commerce-data-v1.js';

const v=(name:string):ExprV1=>({op:'var',name});
const zero:ExprV1={op:'literal',type:{kind:'scalar',name:'UInt64'},value:'0'};
const body:ExprV1={op:'binary',operator:'and',
 left:{op:'binary',operator:'gt',left:v('quantity'),right:zero},
 right:{op:'binary',operator:'lte',left:v('quantity'),right:v('available')},
};
const types={quantity:'UInt64',available:'UInt64'} as const;
const uint64={kind:'scalar',name:'UInt64'} as const;
const bool={kind:'scalar',name:'Bool'} as const;
const kernel=createCommerceValueKernel({
 schema_version:'craft.core-computation/v1-candidate',
 limits:{fuel:100000,max_input_bytes:4096,max_output_bytes:4096,max_value_bytes:4096,
  max_items:100,max_call_depth:16},
 values:{records:[],enums:[],refinements:[],collection_predicates:[]},
 inputs:[],result:bool,
},{isProxy:()=>false,isUint8Array:(value:unknown)=>value instanceof Uint8Array,
 isSharedArrayBuffer:()=>false},{record:()=>true,predicate:()=>true});

const reference=(bindings:Readonly<Record<string,bigint>>)=>{
 const account=kernel.fresh();
 const run=(expr:ExprV1,path:string):boolean|bigint=>{
  const site=kernel.site(path);kernel.charge(account,site);
  let value:boolean|bigint;
  if(expr.op==='var')value=bindings[expr.name]!;
  else if(expr.op==='literal'&&expr.type.kind==='scalar'&&expr.type.name==='UInt64')
   value=BigInt(expr.value as string);
  else if(expr.op==='binary'){
   const left=run(expr.left,path+'.left');
   if(expr.operator==='and'&&left===false)value=false;
   else{
    const right=run(expr.right,path+'.right');
    if(expr.operator==='and')value=right as boolean;
    else if(expr.operator==='gt')value=(left as bigint)>(right as bigint);
    else if(expr.operator==='lte')value=(left as bigint)<=(right as bigint);
    else throw Error('unsupported test AST');
   }
  }else throw Error('unsupported test AST');
  return kernel.checkpoint(value,typeof value==='boolean'?bool:uint64,account,site) as boolean|bigint;
 };
 const value=run(body,'$.functions[0].body') as boolean;
 const bodyFuel=account.used;
 kernel.checkpoint(value,bool,account,kernel.site('$.expression'));
 kernel.checkpoint(value,bool,account,kernel.site('$.expression'));
 const wire=kernel.output(value,account) as Uint8Array;
 return {value,body_fuel:bodyFuel,body_and_output_fuel:account.used,
  output_wire_hex:Buffer.from(wire).toString('hex')};
};

test('primitive Rule short-circuit result and body/output fuel match checked kernel',()=>{
 for(const [quantity,available] of [[0n,0n],[0n,100n],[1n,0n],[1n,1n],
  [10n,9n],[10n,10n],[18446744073709551615n,18446744073709551615n]]){
  const bindings={quantity,available};
  const projected=evaluateCoreCommerceFormalPrimitiveRuleBodyV1(body,bindings,types);
  assert.deepEqual(projected,reference(bindings));
 }
});

test('Rule translator rejects unsupported expression and invalid typed premises',()=>{
 assert.throws(()=>evaluateCoreCommerceFormalPrimitiveRuleBodyV1(
  {op:'field',value:v('quantity'),field:'x'},
  {quantity:1n,available:1n},types),
  (error:unknown)=>error instanceof CoreCommerceFormalPrimitiveRuleErrorV1&&error.code==='UnsupportedTranslation');
 assert.throws(()=>evaluateCoreCommerceFormalPrimitiveRuleBodyV1(body,
  {quantity:-1n,available:1n},types),
  (error:unknown)=>error instanceof CoreCommerceFormalPrimitiveRuleErrorV1&&error.code==='UnsupportedTranslation');
});
