import test from 'node:test';
import assert from 'node:assert/strict';
import {createCommerceValueKernel} from '../../src/commerce/commerce-computation-kernel.js';
import {evaluateCoreCommerceFormalJsonInputV1,CoreCommerceFormalJsonInputErrorV1}
 from '../../src/commerce/commerce-core-formal-json-input-v1.js';
import type {CoreCommerceFormalInputFieldsV1} from '../../src/commerce/commerce-core-formal-input-fields-v1.js';

const names=['subtotal','discountMinor','taxMinor','shippingMinor'];
const makeModel=(maxInput=4096,fuel=100000)=>({
 max_input_bytes:maxInput,max_value_bytes:524288,fuel,input_fields:names,
}) as CoreCommerceFormalInputFieldsV1;
const bytes=(wire:string)=>new TextEncoder().encode(wire);
const kernel=(model:CoreCommerceFormalInputFieldsV1)=>createCommerceValueKernel({
 schema_version:'craft.core-computation/v1-candidate',
 limits:{max_input_bytes:model.max_input_bytes,max_value_bytes:model.max_value_bytes,
  fuel:model.fuel,max_items:4096},
 values:{records:[],enums:[],refinements:[],collection_predicates:[]},
 inputs:names.map(name=>({name,type:{kind:'scalar',name:'UInt64'}})),
 result:{kind:'scalar',name:'UInt64'},
},{isProxy:()=>false,isUint8Array:(value:unknown)=>value instanceof Uint8Array,
 isSharedArrayBuffer:()=>false},{record:()=>true,predicate:()=>true});

const compare=(model:CoreCommerceFormalInputFieldsV1,wire:Uint8Array)=>{
 const projected=evaluateCoreCommerceFormalJsonInputV1(model,wire);
 const runtime=kernel(model),account=runtime.fresh();
 let actual:Record<string,bigint>|undefined,error:{error:{code:string;expression_path:string}}|undefined;
 try{actual=runtime.input(wire,account) as Record<string,bigint>;}catch(caught){
  error=caught as {error:{code:string;expression_path:string}};
 }
 if(error){
  assert.equal(projected.status,error.error.code,Buffer.from(wire).toString('hex'));
  assert.equal(projected.fault_path,error.error.expression_path);
  assert.equal(projected.values,null);
 }else{
  assert.equal(projected.status,'ready_for_expression');
  assert.deepEqual(projected.values,names.map(name=>actual![name]));
 }
 assert.equal(projected.fuel_used,account.used);
};

test('bounded parser and UInt64 input fault priority matches checked kernel directly',()=>{
 const model=makeModel();
 const base='{ "subtotal":"10", "discountMinor":"1", "taxMinor":"2", "shippingMinor":"3" }';
 const cases=[base,
  '{"shippingMinor":"3","taxMinor":"2","discountMinor":"1","subtotal":"10"}',
  '{"subtotal":"10","discountMinor":"1","taxMinor":"2","shippingMinor":"3","extra":0}',
  '{"subtotal":"10","discountMinor":"1","taxMinor":"2"}',
  '{"subtotal":"10","subtotal":"11","discountMinor":"1","taxMinor":"2","shippingMinor":"3"}',
  '{"subtotal":"10","su\\u0062total":"11","discountMinor":"1","taxMinor":"2","shippingMinor":"3"}',
  '{"subtotal":"10","discountMinor":"1","taxMinor":"2","shippingMinor":"3"}!',
  '{"subtotal":"10","discountMinor":"1","taxMinor":"2","shippingMinor":"3",}',
  '{"subtotal":"10","discountMinor":"1","taxMinor":"2","shippingMinor":"3"',
  '{"subtotal":"10","discountMinor":"1","taxMinor":"2","shippingMinor":"\\u0033"}',
  '{"subtotal":"\\uD800","discountMinor":"1","taxMinor":"2","shippingMinor":"3"}',
  '{"subtotal":"18446744073709551616","discountMinor":"1","taxMinor":"2","shippingMinor":"3"}',
  '{"subtotal":"01","discountMinor":"1","taxMinor":"2","shippingMinor":"3"}',
  '{"subtotal":10,"discountMinor":"1","taxMinor":"2","shippingMinor":"3"}',
  '{"subtotal":"10","discountMinor":"1","taxMinor":[],"shippingMinor":"3"}',
  '{"subtotal":"10","discountMinor":"1","taxMinor":"2","shippingMinor":"3\\x"}',
  '[]','null','1e999','"x"','{}','',
  '['.repeat(33)+'0'+']'.repeat(33),
  '{"x":'+ '['.repeat(32)+'0'+']'.repeat(32)+'}',
 ];
 for(const wire of cases)compare(model,bytes(wire));
 for(const wire of [Uint8Array.from([255]),Uint8Array.from([239,187,191,123,125]),
  Uint8Array.from([239,187,191,255]),Uint8Array.from([0x7b,0x22,0xff,0x22,0x3a,0x30,0x7d])])compare(model,wire);
 for(const fuel of [0,1,2,3,4,5,6,7,8,9,10,11,12,13])compare(makeModel(4096,fuel),bytes(base));
 for(const maxInput of [0,1,32,33,64])compare(makeModel(maxInput),bytes(base));
 let seed=0xa5c31d2e;
 for(let sample=0;sample<192;sample++){
  const mutated=bytes(base),changes=1+sample%4;
  for(let change=0;change<changes;change++){
   seed=(Math.imul(seed,1664525)+1013904223)>>>0;
   mutated[seed%mutated.length]=seed>>>24;
  }
  compare(model,mutated);
 }
});

test('unmodeled large JSON that passed admission is explicit UnsupportedTranslation',()=>{
 const model=makeModel(8192);
 assert.throws(()=>evaluateCoreCommerceFormalJsonInputV1(model,bytes(' '.repeat(4097))),
  (error:unknown)=>error instanceof CoreCommerceFormalJsonInputErrorV1&&error.code==='UnsupportedTranslation');
 compare(makeModel(32),bytes(' '.repeat(4097)));
});
