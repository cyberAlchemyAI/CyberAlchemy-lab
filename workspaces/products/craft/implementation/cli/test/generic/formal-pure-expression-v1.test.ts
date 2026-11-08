import test from 'node:test';
import assert from 'node:assert/strict';
import {types as host} from 'node:util';
import {dataDigest} from '../../src/profile-engine/contracts.js';
import {createCommerceValueKernel} from '../../src/commerce/commerce-computation-kernel.js';
import {deriveGenericComputationEnvironment} from '../../src/commerce/commerce-computation-environment.js';
import {evaluateGenericPureExpressionFormalSliceV1,GenericPureExpressionFormalErrorV1}
 from '../../src/generic/formal-pure-expression-v1.js';
import type {GenericComputationContractV1,GenericExprV1,GenericPureDeclarationV1}
 from '../../src/generic/computation-data-v1.js';
import type {ValueTypeV1} from '../../src/commerce/commerce-data-v1.js';

const bool:ValueTypeV1={kind:'scalar',name:'Bool'},uint:ValueTypeV1={kind:'scalar',name:'UInt64'};
const list:ValueTypeV1={kind:'list',element:uint,min_items:0,max_items:8};
const variable=(name:string):GenericExprV1=>({op:'var',name});
const number=(value:number):GenericExprV1=>({op:'literal',type:uint,value:String(value)});
const binary=(operator:'gt'|'multiply'|'add',left:GenericExprV1,right:GenericExprV1):GenericExprV1=>({op:'binary',operator,left,right});
const call=(declaration:string,args:GenericExprV1[]):GenericExprV1=>({op:'call',declaration,arguments:args});
const listBinder={name:'values',type:list} as const;
const source=variable('values');
const filter:GenericExprV1={op:'filter',source,item:{name:'item',type:uint},
 predicate:binary('gt',variable('item'),number(2))};
const map:GenericExprV1={op:'map',source,item:{name:'item',type:uint},
 body:binary('multiply',variable('item'),number(2))};
const fold:GenericExprV1={op:'fold',source,initial:number(0),state:{name:'total',type:uint},
 item:{name:'item',type:uint},body:binary('add',variable('total'),variable('item'))};
const sha='a'.repeat(64);
function contract(expression:GenericExprV1,result:ValueTypeV1,limitsFuel=100000,
 functions:readonly GenericPureDeclarationV1[]=[],inputs:GenericComputationContractV1['inputs']=[listBinder],
 records:GenericComputationContractV1['values']['records']=[]):GenericComputationContractV1{
 return {schema_version:'craft.generic-computation/v1-candidate',
  semantics_revision:'ordered-metered-generic-v1-candidate',source_node:'Demo.Selected',
  values:{schema_version:'craft.generic-values/v1-candidate',records,enums:[],refinements:[],
   collection_predicates:[],root:result},inputs,functions,result,rounding:'reject',
  limits:{fuel:limitsFuel,max_input_bytes:4096,max_output_bytes:4096,max_value_bytes:4096,
   max_items:8,max_call_depth:16},expression,invariant_policy:'reject-inexact/v1',
  record_layout:'canonical-fields/v1',equality_policy:'typed-structural-metered/v1',
  append_policy:'list-item-checkpoint-capacity/v1'};
}
function evaluate(c:GenericComputationContractV1,inputs:Readonly<Record<string,unknown>>,wire?:Uint8Array){
 const layout=deriveGenericComputationEnvironment(c);
 return evaluateGenericPureExpressionFormalSliceV1({contract:c,expression_types:layout.expressions,
  policy_actions:layout.policy_actions,decoded_inputs:inputs,source_capture_sha256:sha,
  contract_sha256:dataDigest(c),executable_semantics_sha256:sha,code_epoch_sha256:sha},undefined,wire);
}
function referenceFilter(values:bigint[],fuel=100000,wire?:Uint8Array){
 const c=contract(filter,list,fuel),k=createCommerceValueKernel(c,host,{record:()=>true,predicate:()=>true});
 const a=k.fresh(),s=(path:string,index:number[]=[])=>k.site(path,index);
 try{
  if(wire!==undefined)values=k.input(wire,a).values;
  k.charge(a,s('$.expression'));
  k.charge(a,s('$.expression.source'));
  k.checkpoint(values,list,a,s('$.expression.source'));
  const out:bigint[]=[];k.partial(out,list,a,s('$.expression'));
  for(let i=0;i<values.length;i++){
   const ix=[i],p='$.expression.predicate';k.charge(a,s('$.expression',ix));
   k.charge(a,s(p,ix));
   k.charge(a,s(p+'.left',ix));k.checkpoint(values[i],uint,a,s(p+'.left',ix));
   k.charge(a,s(p+'.right',ix));k.checkpoint(2n,uint,a,s(p+'.right',ix));
   const pass=values[i]!>2n;k.checkpoint(pass,bool,a,s(p,ix));
   if(pass)out.push(values[i]!);k.partial(out,list,a,s('$.expression',ix));
  }
  k.checkpoint(out,list,a,s('$.expression'));
  return {ok:true,wire_hex:Buffer.from(k.output(out,a)).toString('hex'),fuel_used:a.used};
 }catch(error){const failure=k.failure(error,a);return {ok:false,code:failure.error.code,
  expression_path:failure.error.expression_path,index_path:failure.error.index_path,
  call_path:failure.error.call_path,fuel_used:failure.fuel_used};}
}
function referenceMapOrFold(kind:'map'|'fold',values:bigint[],fuel=100000){
 const expression=kind==='map'?map:fold,output=kind==='map'?list:uint;
 const c=contract(expression,output,fuel),k=createCommerceValueKernel(c,host,{record:()=>true,predicate:()=>true});
 const a=k.fresh(),s=(path:string,index:number[]=[])=>k.site(path,index),root='$.expression';
 try{
  k.charge(a,s(root));k.charge(a,s(root+'.source'));
  k.checkpoint(values,list,a,s(root+'.source'));
  let result:any;
  if(kind==='map'){
   const out:bigint[]=[];k.partial(out,list,a,s(root));
   for(let i=0;i<values.length;i++){
    const ix=[i],p=root+'.body';k.charge(a,s(root,ix));k.charge(a,s(p,ix));
    k.charge(a,s(p+'.left',ix));k.checkpoint(values[i],uint,a,s(p+'.left',ix));
    k.charge(a,s(p+'.right',ix));k.checkpoint(2n,uint,a,s(p+'.right',ix));
    const product=values[i]!*2n;if(product>k.max)k.fail('ArithmeticOverflow',s(p,ix));
    out.push(k.checkpoint(product,uint,a,s(p,ix)));k.partial(out,list,a,s(root,ix));
   }
   result=out;
  }else{
   k.charge(a,s(root+'.initial'));let state=k.checkpoint(0n,uint,a,s(root+'.initial'));
   k.checkpoint(state,uint,a,s(root));
   for(let i=0;i<values.length;i++){
    const ix=[i],p=root+'.body';k.charge(a,s(root,ix));k.charge(a,s(p,ix));
    k.charge(a,s(p+'.left',ix));k.checkpoint(state,uint,a,s(p+'.left',ix));
    k.charge(a,s(p+'.right',ix));k.checkpoint(values[i],uint,a,s(p+'.right',ix));
    const next=state+values[i]!;if(next>k.max)k.fail('ArithmeticOverflow',s(p,ix));
    state=k.checkpoint(next,uint,a,s(p,ix));k.checkpoint(state,uint,a,s(root,ix));
   }
   result=state;
  }
  k.checkpoint(result,output,a,s(root));
  return {ok:true,wire_hex:Buffer.from(k.output(result,a)).toString('hex'),fuel_used:a.used};
 }catch(error){const failure=k.failure(error,a);return {ok:false,code:failure.error.code,
  expression_path:failure.error.expression_path,index_path:failure.error.index_path,
  call_path:failure.error.call_path,fuel_used:failure.fuel_used};}
}

test('filter formal witness matches independent checked-kernel traversal and fuel errors',()=>{
 for(const values of [[],[1n],[2n,3n,1n,4n],[8n,7n,6n,5n]]){
  for(const fuel of [3,10,25,100000]){
   const c=contract(filter,list,fuel);
   assert.deepEqual(evaluate(c,{values}).result,referenceFilter(values,fuel));
  }
 }
});

test('same-account wire entry preserves parser, decode cache, and expression fuel',()=>{
 for(const raw of [
  Buffer.from('{"values":[]}'),
  Buffer.from('{"values":["1","3","2","4"]}'),
  Buffer.from('{"values":["not-a-number"]}'),
  Buffer.from('{"values":["1",]}'),
  Buffer.from([0xff]),
 ])for(const fuel of [1,8,40,100000]){
  const wire=new Uint8Array(raw),values:bigint[]=[];
  const witness=evaluate(contract(filter,list,fuel),{values},wire);
  assert.equal(witness.input_mode,'same-account-wire-input');
  assert.equal(witness.source_binding,'caller-context-unverified');
  assert.deepEqual(witness.result,referenceFilter(values,fuel,wire));
 }
});

test('map and fold preserve item order, exact typed overflow and budget priority',()=>{
 for(const [expr,result,values,want] of [
  [map,list,[1n,2n,3n],['2','4','6']],
  [fold,uint,[1n,2n,3n],'6'],
 ] as const){
  const witness=evaluate(contract(expr,result),{values});
  assert.equal(witness.result.ok,true);
  if(witness.result.ok)assert.deepEqual(JSON.parse(Buffer.from(witness.result.wire_hex,'hex').toString()),want);
  assert.match(witness.smtlib2,/source_capture_sha256/);
 }
 const overflow=evaluate(contract(fold,uint),{values:[18446744073709551615n,1n]});
 assert.deepEqual(overflow.result.ok&&null,(false));
 if(!overflow.result.ok){assert.equal(overflow.result.code,'ArithmeticOverflow');
  assert.deepEqual(overflow.result.index_path,[1]);}
 const low=evaluate(contract(map,list,1),{values:[1n]});
 assert.equal(low.result.ok,false);
 if(!low.result.ok)assert.equal(low.result.code,'ResourceLimit');
 for(const values of [[],[1n],[2n,3n,4n],[18446744073709551615n,1n]])
  for(const fuel of [3,15,50,100000])
   for(const [kind,expression,output] of [['map',map,list],['fold',fold,uint]] as const)
    assert.deepEqual(evaluate(contract(expression,output,fuel),{values}).result,
     referenceMapOrFold(kind,values,fuel));
});

test('checked Mapping and Policy composition selects first branch and preserves authored record fields',()=>{
 const request:ValueTypeV1={kind:'record',name:'Demo.Request'},decision:ValueTypeV1={kind:'record',name:'Demo.Decision'};
 const records:GenericComputationContractV1['values']['records']=[
  {name:'Demo.Request',role:'ValueObject',fields:{flagged:bool,values:list},invariants:[],event_version:null,entity:null},
  {name:'Demo.Decision',role:'ValueObject',fields:{selected:list,total:uint},invariants:[],event_version:null,entity:null},
 ];
 const req=variable('request'),field=(name:string):GenericExprV1=>({op:'field',value:req,field:name});
 const values=field('values'),sum:GenericExprV1={...fold,source:values};
 const doubled:GenericExprV1=binary('add',sum,number(10));
 const params=[{name:'request',type:request}];
 const declaration=(name:string,kind:GenericPureDeclarationV1['kind'],body:GenericExprV1,result:ValueTypeV1):GenericPureDeclarationV1=>
  ({name,kind,pure:true,parameters:params,result,body,preconditions:[],
   precondition_mode:'embedded-once-in-body',rounding:'reject',on_evaluation_error:null});
 const total=declaration('Demo.Total','Calculation',sum,uint);
 const priority=declaration('Demo.Priority','Calculation',doubled,uint);
 const policy=declaration('Demo.Select','Policy',{op:'policy',declaration:'Demo.Select',cases:[{
  condition:field('flagged'),action:{calculation:'Demo.Priority',expression:call('Demo.Priority',[req])},
 }],otherwise:{calculation:'Demo.Total',expression:call('Demo.Total',[req])}},uint);
 const mapped=declaration('Demo.Map','Mapping',{op:'record',type_name:'Demo.Decision',fields:{
  selected:values,total:call('Demo.Select',[req]),
 }},decision);
 const c=contract(call('Demo.Map',[req]),decision,100000,[total,priority,policy,mapped],params,records);
 for(const flagged of [false,true]){
  const witness=evaluate(c,{request:{flagged,values:[1n,2n,3n]}});
  assert.equal(witness.result.ok,true);
  if(witness.result.ok)assert.deepEqual(JSON.parse(Buffer.from(witness.result.wire_hex,'hex').toString()),
   {selected:['1','2','3'],total:flagged?'16':'6'});
 }
});

test('unmodeled expressions and untrusted typed premises reject translation',()=>{
 const unknown:GenericExprV1={op:'repeat',count:number(1),max_iterations:1,initial:number(0),
  state:{name:'state',type:uint},index:{name:'index',type:uint},body:variable('state')};
 assert.throws(()=>evaluate(contract(unknown,uint),{values:[]}),
  (error:unknown)=>error instanceof GenericPureExpressionFormalErrorV1&&error.code==='UnsupportedTranslation');
 assert.throws(()=>evaluate(contract(filter,list),{values:['bad']}),
  (error:unknown)=>error instanceof GenericPureExpressionFormalErrorV1&&error.code==='UnsupportedTranslation');
});
