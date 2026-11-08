/** Concrete SMT witness for a checked pure-expression subset.
 * The checked value kernel supplies the exact
 * validation, size, fuel and diagnostic primitives; this module independently
 * follows the expression, call, policy and collection evaluation order.
 * It does not claim a universal formula or native/generated-code equivalence.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import {createHash} from 'node:crypto';
import {types as host} from 'node:util';
import {dataDigest} from '../profile-engine/contracts.js';
import {createCommerceValueKernel} from '../commerce/commerce-computation-kernel.js';
import {assertGenericComputationDomainOwner,type GenericComputationDomainOwner,
 type GenericComputationDomainHandle} from './computation-domain.js';
import type {GenericComputationContractV1,GenericExprV1} from './computation-data-v1.js';
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';

export class GenericPureExpressionFormalErrorV1 extends Error {
 constructor(readonly code:'UnsupportedTranslation'|'InvalidSource'){
  super(code);this.name='GenericPureExpressionFormalErrorV1';
 }
}
const unsupported=():never=>{throw new GenericPureExpressionFormalErrorV1('UnsupportedTranslation');};
const digest=(text:string|Uint8Array)=>createHash('sha256').update(text).digest('hex');
const originalBinding=Symbol('original-checked-generic-owner');
const smtString=(value:string):string=>{
 if(/[^\x20-\x7e]/.test(value))return unsupported();
 return '"'+value.replaceAll('"','""')+'"';
};
type PolicyBinding=Readonly<{path:string;branch:string;invocation_path:string}>;
export interface GenericPureExpressionFormalContextV1 {
 readonly contract:GenericComputationContractV1;
 readonly expression_types:readonly Readonly<{path:string;type:ValueTypeV1}>[];
 readonly policy_actions:readonly PolicyBinding[];
 readonly decoded_inputs?:Readonly<Record<string,unknown>>;
 readonly source_capture_sha256:string;
 readonly contract_sha256:string;
 readonly executable_semantics_sha256:string;
 readonly code_epoch_sha256:string;
}
export interface GenericPureExpressionFormalWitnessV1 {
 readonly schema_version:'craft.generic-pure-expression-formal-witness/v1-candidate';
 readonly language:'smtlib2';
 readonly source_node:string;
 readonly source_capture_sha256:string;
 readonly contract_sha256:string;
 readonly executable_semantics_sha256:string;
 readonly code_epoch_sha256:string;
 readonly input_sha256:string;
 readonly input_mode:'same-account-wire-input'|'fresh-account-validated-decoded-input';
 readonly source_binding:'original-owner-checked'|'caller-context-unverified';
 readonly result:Readonly<{ok:true;wire_hex:string;fuel_used:number}|{ok:false;code:string;expression_path:string;index_path:readonly number[];call_path:readonly string[];fuel_used:number}>;
 readonly smtlib2:string;
 readonly smtlib2_sha256:string;
 readonly unsupported_semantics:readonly string[];
 readonly claim_ceiling:'one-concrete-wire-and-checked-pure-expression-observation-only'|
  'one-fresh-account-checked-pure-expression-observation-only';
}

/** A narrow executable formal transition projection. A missing expression type,
 * unmodeled AST operator or non-current source is an unsupported translation.
 * The optional wire path uses one kernel account through input and expression,
 * preserving decode cache state and fuel; it remains one ground observation. */
export function evaluateGenericPureExpressionFormalSliceV1(context:GenericPureExpressionFormalContextV1,
 binding?:symbol,inputWire?:Uint8Array):GenericPureExpressionFormalWitnessV1 {
 const c=context.contract;
 if(c.schema_version!=='craft.generic-computation/v1-candidate'||
  c.semantics_revision!=='ordered-metered-generic-v1-candidate'||
  !/^[a-f0-9]{64}$/.test(context.source_capture_sha256)||
  dataDigest(c)!==context.contract_sha256||
  !/^[a-f0-9]{64}$/.test(context.executable_semantics_sha256)||
  !/^[a-f0-9]{64}$/.test(context.code_epoch_sha256))
  throw new GenericPureExpressionFormalErrorV1('InvalidSource');
 const types=new Map(context.expression_types.map(row=>[row.path,row.type]));
 const policies=new Map(context.policy_actions.map(row=>[row.path,row]));
 const functions=new Map(c.functions.map((f,index)=>[f.name,{f,index}]));
 const internalInputs:Record<string,unknown>=Object.create(null);
 if(inputWire===undefined){
  const decoded=context.decoded_inputs??unsupported();
  for(const item of c.inputs){
   if(!Object.hasOwn(decoded,item.name))unsupported();
   internalInputs[item.name]=decoded[item.name];
  }
  if(Object.keys(decoded).length!==c.inputs.length)unsupported();
 }
 let k:ReturnType<typeof createCommerceValueKernel>;
 const run=(expr:GenericExprV1,p:string,env:Record<string,any>,ix:number[],calls:string[],rounding:string,a:any):any=>{
  const t=types.get(p);if(!t)unsupported();
  const s=k.site(p,ix,calls);k.charge(a,s);
  const sub=(child:GenericExprV1,key:string,next=env,index=ix)=>run(child,p+'.'+key,next,index,calls,rounding,a);
  const scope=(values:Record<string,unknown>)=>Object.assign(Object.create(null),env,values);
  const check=(value:any,index=ix)=>k.checkpoint(value,t,a,k.site(p,index,calls));
  const partial=(value:any,index=ix)=>k.partial(value,t,a,k.site(p,index,calls));
  let value:any;
  switch(expr.op){
   case 'literal':value=expr.type.kind==='scalar'&&expr.type.name==='UInt64'?BigInt(expr.value as string):expr.value;break;
   case 'var':if(!Object.hasOwn(env,expr.name))unsupported();value=env[expr.name];break;
   case 'field':{
    const parent=sub(expr.value,'value'),parentType=types.get(p+'.value')??unsupported();
    value=parentType.kind==='variant'?parent?.fields?.[expr.field]:parent?.[expr.field];
   }break;
   case 'record':{
    value=Object.create(null);
    for(const [name,field] of Object.entries(expr.fields))value[name]=sub(field,'fields.'+name);
   }break;
   case 'enum_value':{
    const def=k.enums.get(expr.type_name);if(!def)unsupported();
    if(def.variants.every((variant:any)=>Object.keys(variant.fields).length===0))value=expr.variant;
    else{
     const fields=Object.create(null);
     for(const [name,field] of Object.entries(expr.fields))fields[name]=sub(field,'fields.'+name);
     value={kind:expr.variant,fields};
    }
   }break;
   case 'all_unique_exact':{
    const items=sub(expr.value,'value');if(!Array.isArray(items))unsupported();
    value=true;
    outer:for(let j=0;j<items.length;j++)for(let i=0;i<j;i++)
     if(k.equal(items[j],items[i],a,k.site(p,[...ix,j,i],calls))){value=false;break outer;}
   }break;
   case 'length':{
    const selected=sub(expr.value,'value');
    if(expr.unit==='items'){
     if(!Array.isArray(selected))unsupported();
     value=BigInt(selected.length);
    }else{
     if(typeof selected!=='string')unsupported();
     const size=new TextEncoder().encode(selected).length;
     k.byteWork(a,s,size);
     value=BigInt(expr.unit==='unicode-scalars'?[...selected].length:size);
    }
   }break;
   case 'let':{
    let selected=sub(expr.value,'value');
    selected=k.checkpoint(selected,expr.binding.type,a,k.site(p+'.value',ix,calls));
    value=sub(expr.body,'body',scope({[expr.binding.name]:selected}));
   }break;
   case 'binary':{
    const left=sub(expr.left,'left');
    if(expr.operator==='and'&&left===false){value=false;break;}
    if(expr.operator==='or'&&left===true){value=true;break;}
    const right=sub(expr.right,'right');
    switch(expr.operator){
     case 'and':case 'or':value=right;break;
     case 'eq':value=k.equal(left,right,a,s);break;
     case 'lt':value=left<right;break;
     case 'lte':value=left<=right;break;
     case 'gt':value=left>right;break;
     case 'gte':value=left>=right;break;
     case 'add':value=left+right;if(value>k.max)k.fail('ArithmeticOverflow',s);break;
     case 'subtract':value=left-right;if(value<0n)k.fail('ArithmeticUnderflow',s);break;
     case 'multiply':value=left*right;if(value>k.max)k.fail('ArithmeticOverflow',s);break;
     case 'divide':{
      if(right===0n)k.fail('DivideByZero',s);
      const aa=left as bigint,bb=right as bigint,rem=aa%bb;
      if(rem!==0n&&rounding==='reject')k.fail('InexactDivision',s);
      value=aa/bb+(rem!==0n&&rounding==='ceil'?1n:0n);
     }break;
    }
   }break;
   case 'unary':if(expr.operator!=='not')unsupported();value=!sub(expr.value,'value');break;
   case 'if':value=sub(expr.condition,'condition')===true?sub(expr.then,'then'):sub(expr.else,'else');break;
   case 'call':{
    const args=expr.arguments.map((argument,index)=>sub(argument,'arguments['+index+']'));
    value=invoke(expr.declaration,args,p,ix,calls,a);
   }break;
   case 'map':case 'filter':{
    const source=sub(expr.source,'source');if(!Array.isArray(source))unsupported();
    const out:any[]=[];partial(out);
    for(let i=0;i<source.length;i++){
     const index=[...ix,i];k.charge(a,k.site(p,index,calls));
     const inner=scope({[expr.item.name]:source[i]});
     const item=expr.op==='map'?sub(expr.body,'body',inner,index):sub(expr.predicate,'predicate',inner,index);
     if(expr.op==='map')out.push(item);else if(item===true)out.push(source[i]);
     partial(out,index);
    }
    value=out;
   }break;
   case 'fold':{
    const source=sub(expr.source,'source');if(!Array.isArray(source))unsupported();
    let state=sub(expr.initial,'initial');check(state);
    for(let i=0;i<source.length;i++){
     const index=[...ix,i];k.charge(a,k.site(p,index,calls));
     state=sub(expr.body,'body',scope({[expr.state.name]:state,[expr.item.name]:source[i]}),index);
     check(state,index);
    }
    value=state;
   }break;
   case 'sort':{
    const source=sub(expr.source,'source');if(!Array.isArray(source))unsupported();
    const decorated:{value:any;ordinal:number;keys:any[]}[]=[];
    for(let i=0;i<source.length;i++){
     const index=[...ix,i];k.charge(a,k.site(p,index,calls));
     const inner=scope({[expr.item.name]:source[i]});
     decorated.push({value:source[i],ordinal:i,keys:expr.keys.map((key,j)=>sub(key.value,'keys['+j+'].value',inner,index))});
    }
    const sorted:typeof decorated=[],sized:any[]=[];partial(sized);
    const compare=(left:typeof decorated[number],right:typeof decorated[number])=>{
     for(let j=0;j<expr.keys.length;j++){
      const key=expr.keys[j]!;
      const comparison=k.compare(left.keys[j],right.keys[j],key.mode,a,k.site(p,[...ix,left.ordinal,right.ordinal,j],calls));
      if(comparison)return key.direction==='desc'?-comparison:comparison;
     }
     return 0;
    };
    for(const item of decorated){
     let j=sorted.length;while(j>0&&compare(item,sorted[j-1]!)<0)j--;
     sorted.splice(j,0,item);sized.push(item.value);partial(sized,[...ix,item.ordinal]);
    }
    value=sorted.map(item=>item.value);
   }break;
   case 'policy':{
    let action=expr.otherwise,key='otherwise';
    for(let j=0;j<expr.cases.length;j++)if(sub(expr.cases[j]!.condition,'cases['+j+'].condition')===true){
     action=expr.cases[j]!.action;key='cases['+j+'].action';break;
    }
    const selected=policies.get(p+'.'+key)??unsupported();
    const pending=k.select(a,s,expr.declaration,selected.branch,action.calculation,selected.invocation_path);
    try{value=sub(action.expression,key+'.expression');}
    finally{a.pending.splice(a.pending.indexOf(pending),1);}
   }break;
   default:unsupported();
  }
  return check(value);
 };
 const invoke=(name:string,args:any[],p:string,ix:number[],calls:string[],a:any):any=>{
  const row=functions.get(name)??unsupported();if(args.length!==row.f.parameters.length)unsupported();
  const {f,index}=row,next=[...calls,name],site=k.site(p,ix,next);k.enter(a,site);
  const env=Object.create(null);
  f.parameters.forEach((parameter,j)=>{env[parameter.name]=k.checkpoint(args[j],parameter.type,a,site);});
  try{
   return k.checkpoint(run(f.body,'$.functions['+index+'].body',env,ix,next,f.rounding,a),f.result,a,site);
  }catch(error){throw k.annotate(error,name,f.on_evaluation_error);}
 };
 const hooks={
  record(name:string,value:any,a:any,s:any){
   const index=c.values.records.findIndex(record=>record.name===name),record=c.values.records[index]??unsupported();
   for(let j=0;j<record.invariants.length;j++)
    if(run(record.invariants[j]!,'$.values.records['+index+'].invariants['+j+']',value,s.i,s.c,'reject',a)!==true)return false;
   return true;
  },
  predicate(){unsupported();},
 };
 const runtimeKernel=createCommerceValueKernel(c,host,hooks);
 if(inputWire===undefined){
  k=createCommerceValueKernel({...c,limits:{...c.limits,fuel:1000000000}},host,hooks);
  // The typed-premise audit is separate and never charged to expression fuel.
  const premise=k.fresh();
  try{for(const item of c.inputs)
   k.checkpoint(internalInputs[item.name],item.type,premise,k.site('$.inputs.'+item.name));
  }catch{unsupported();}
 }
 k=runtimeKernel;
 const account=k.fresh();
 let result:GenericPureExpressionFormalWitnessV1['result'];
 try{
  const env=inputWire===undefined?internalInputs:k.input(inputWire,account);
  const value=run(c.expression,'$.expression',env,[],[],c.rounding,account);
  const wire=k.output(value,account) as Uint8Array;
  result={ok:true,wire_hex:Buffer.from(wire).toString('hex'),fuel_used:account.used};
 }catch(error){
  if(error instanceof GenericPureExpressionFormalErrorV1)throw error;
  const failure=k.failure(error,account);
  result={ok:false,code:failure.error.code,expression_path:failure.error.expression_path,
   index_path:failure.error.index_path,call_path:failure.error.call_path,fuel_used:failure.fuel_used};
 }
 const payload=result.ok?result.wire_hex:Buffer.from(JSON.stringify({code:result.code,
  expression_path:result.expression_path,index_path:result.index_path,call_path:result.call_path})).toString('hex');
 const smtlib2=[
  '(set-logic ALL)',
  `; source_capture_sha256 ${context.source_capture_sha256}`,
  `; contract_sha256 ${context.contract_sha256}`,
  `; executable_semantics_sha256 ${context.executable_semantics_sha256}`,
  '; One concrete input observation; payload is UTF8 hex; no general quantification.',
  '(declare-datatypes () ((EvalResult (observed (ok Bool) (payload String) (fuel Int)))))',
  `(define-fun Evaluate () EvalResult (observed ${result.ok} ${smtString(payload)} ${result.fuel_used}))`,
 ].join('\n')+'\n';
 return Object.freeze({schema_version:'craft.generic-pure-expression-formal-witness/v1-candidate' as const,
  language:'smtlib2' as const,source_node:c.source_node,
  source_binding:binding===originalBinding?'original-owner-checked' as const:'caller-context-unverified' as const,
  input_mode:inputWire===undefined?'fresh-account-validated-decoded-input' as const:'same-account-wire-input' as const,
  source_capture_sha256:context.source_capture_sha256,contract_sha256:context.contract_sha256,
  executable_semantics_sha256:context.executable_semantics_sha256,code_epoch_sha256:context.code_epoch_sha256,
  input_sha256:inputWire===undefined?dataDigest(JSON.parse(JSON.stringify(context.decoded_inputs,
   (_key,value)=>typeof value==='bigint'?String(value):value))):digest(inputWire),
  result:Object.freeze(result),smtlib2,
  smtlib2_sha256:digest(smtlib2),unsupported_semantics:Object.freeze([
   ...(inputWire===undefined?['real-decode-cache-state-and-continuation-fuel']:[]),
   'symbolic-all-inputs-proof','generated-native-parity',
   'entry-auth-operation-effects-and-temporal-recovery']),
  claim_ceiling:inputWire===undefined?'one-fresh-account-checked-pure-expression-observation-only' as const:
   'one-concrete-wire-and-checked-pure-expression-observation-only' as const});
}

/** Binds the slice to the original checked generic owner. This still takes
 * already-decoded internal values and therefore excludes wire-input costs. */
export function exportCheckedGenericPureExpressionFormalSliceV1(
 owner:GenericComputationDomainOwner,handle:GenericComputationDomainHandle,
 decodedInputs:Readonly<Record<string,unknown>>,
):GenericPureExpressionFormalWitnessV1 {
 assertGenericComputationDomainOwner(owner);owner.assertCurrent(handle);
 const inspection=owner.inspect(handle);
 const executable=inspection.derivation.executable_semantics_sha256;
 if(typeof executable!=='string')throw new GenericPureExpressionFormalErrorV1('InvalidSource');
 const witness=evaluateGenericPureExpressionFormalSliceV1({contract:inspection.contract,
  expression_types:inspection.environment.expressions,
  policy_actions:inspection.environment.policy_actions,
  decoded_inputs:decodedInputs,source_capture_sha256:inspection.source_capture_sha256,
  contract_sha256:inspection.contract_sha256,
  executable_semantics_sha256:executable,
  code_epoch_sha256:inspection.code_epoch_sha256},originalBinding);
 owner.assertCurrent(handle);return witness;
}

/** Same-account wire-to-output witness on the original checked domain. It
 * models one input only and is not a universal parser or expression theorem. */
export function exportCheckedGenericPureExpressionFormalFromWireV1(
 owner:GenericComputationDomainOwner,handle:GenericComputationDomainHandle,inputWire:Uint8Array,
):GenericPureExpressionFormalWitnessV1 {
 assertGenericComputationDomainOwner(owner);owner.assertCurrent(handle);
 const inspection=owner.inspect(handle),executable=inspection.derivation.executable_semantics_sha256;
 if(typeof executable!=='string')throw new GenericPureExpressionFormalErrorV1('InvalidSource');
 const witness=evaluateGenericPureExpressionFormalSliceV1({contract:inspection.contract,
  expression_types:inspection.environment.expressions,
  policy_actions:inspection.environment.policy_actions,
  source_capture_sha256:inspection.source_capture_sha256,
  contract_sha256:inspection.contract_sha256,
  executable_semantics_sha256:executable,
  code_epoch_sha256:inspection.code_epoch_sha256},originalBinding,inputWire);
 owner.assertCurrent(handle);return witness;
}
