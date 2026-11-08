import {assertGenericInternalExecutionToken,type GenericInternalExecutionToken} from '../generic/execution-session.js';
/** Source-bound reference execution for the existing finite v2 expression language.
 * Open Questions: docs/COMMERCE-COMPUTATION-RUNTIME-V2.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {types as host} from 'node:util';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertGenericComputationDomainOwner,type GenericComputationDomainOwner,type GenericComputationDomainHandle} from '../generic/computation-domain.js';
import {createGenericPureCallOwner,createGenericKeyedPureCallOwner} from '../generic/pure-call-owner.js';
import type {GenericExprV1} from '../generic/computation-data-v1.js';
import {createCommerceValueKernel} from './commerce-computation-kernel.js';
import type {ExprV1,EvaluationErrorActionV1,ExpressionFailureV1} from './commerce-data-v1.js';
import type {CommerceEvaluationResult} from './commerce-stages-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-computation-kernel'+ext,'commerce-computation-domain'+ext,'commerce-computation-environment'+ext,'../generic/computation-domain'+ext,'../generic/pure-call-owner'+ext,'../generic/execution-session'+ext]);
export interface CommerceComputationObservation {
 readonly result:CommerceEvaluationResult;readonly evaluation_phase:'input-validation'|'expression'|'output-validation'|'complete';readonly declared_actions:readonly {readonly declaration:string;readonly action:EvaluationErrorActionV1}[];
 readonly policy_decisions:readonly {readonly policy:string;readonly branch:string;readonly calculation:string;readonly expression_path:string;readonly index_path:readonly number[];readonly call_path:readonly string[];readonly invocation_entered:boolean}[];
 readonly observation_status:'complete'|'truncated';
}
export function evaluateCommerceComputation(owner:CommerceComputationDomainOwner,handle:CommerceComputationDomainHandle,input:Uint8Array):CommerceEvaluationResult {return evaluateCommerceComputationObserved(owner,handle,input,false).result;}
export function evaluateCommerceComputationObserved(owner:CommerceComputationDomainOwner,handle:CommerceComputationDomainHandle,input:Uint8Array,observe=true):CommerceComputationObservation {
 return evaluateChecked({kind:'commerce',owner,handle},input,observe);
}
export function evaluateGenericComputation(owner:GenericComputationDomainOwner,handle:GenericComputationDomainHandle,input:Uint8Array):CommerceEvaluationResult{return evaluateGenericComputationObserved(owner,handle,input,false).result;}
export function evaluateGenericComputationObserved(owner:GenericComputationDomainOwner,handle:GenericComputationDomainHandle,input:Uint8Array,observe=true):CommerceComputationObservation{return evaluateChecked({kind:'generic',owner,handle},input,observe);}
type Subject={kind:'keyed';token:GenericInternalExecutionToken}|{kind:'commerce';owner:CommerceComputationDomainOwner;handle:CommerceComputationDomainHandle}|{kind:'generic';owner:GenericComputationDomainOwner;handle:GenericComputationDomainHandle};
function evaluateChecked(subject:Subject,input:Uint8Array,observe:boolean):CommerceComputationObservation{return createCheckedMachine(subject).evaluate(input,observe);}
export function createInternalGenericExecutionMachine(token:GenericInternalExecutionToken){assertGenericInternalExecutionToken(token);return createCheckedMachine({kind:'keyed',token});}
function createCheckedMachine(subject:Subject){
 const current=()=>{pin.assertCurrent();if(subject.kind==='keyed'){assertGenericInternalExecutionToken(subject.token);}else if(subject.kind==='generic'){assertGenericComputationDomainOwner(subject.owner);subject.owner.assertCurrent(subject.handle);}else{assertCommerceComputationDomainOwner(subject.owner);subject.owner.assertCurrent(subject.handle);}};current();
 const inspection=subject.kind==='keyed'?assertGenericInternalExecutionToken(subject.token).inspection:subject.owner.inspect(subject.handle as never),generic=subject.kind!=='commerce',callOwner=subject.kind==='keyed'?createGenericKeyedPureCallOwner(subject.token):subject.kind==='generic'?createGenericPureCallOwner(subject.owner,subject.handle):null,c=inspection.contract,types=new Map(inspection.environment.expressions.map(s=>[s.path,s.type])),functions=new Map(c.functions.map((f,i)=>[f.name,{f,i}])),policies=new Map(inspection.environment.policy_actions.map(s=>[s.path,s]));
 const privateResolvers=new WeakMap<object,(name:string,account:any,site:any)=>{found:boolean;value:any}>();
 const kernel=createCommerceValueKernel(c,host,{
  record(name:string,value:any,a:any,s:any){const index=c.values.records.findIndex(r=>r.name===name),r=c.values.records[index]!;for(let j=0;j<r.invariants.length;j++)if(run(r.invariants[j]!,'$.values.records['+index+'].invariants['+j+']',value,s.i,s.c,generic?'reject':c.rounding,a)!==true)return false;return true;},
  predicate(name:string,value:any,a:any,s:any,type:any){if(callOwner){const h=callOwner.bindPredicate(type);callOwner.assertPredicate(h,type,name);}return invoke(name,[value],s.p,s.i,s.c,a)===true;},
 });
 const invoke=(name:string,args:any[],p:string,ix:number[],calls:string[],a:any):any=>{
  const row=functions.get(name);if(!row)return kernel.fail('UnknownReference',kernel.site(p,ix,calls));const {f,i}=row,next=[...calls,name],s=kernel.site(p,ix,next);kernel.enter(a,s);
  const locals=Object.create(null);f.parameters.forEach((b,j)=>locals[b.name]=kernel.checkpoint(args[j],b.type,a,s));
  try{return kernel.checkpoint(run(f.body,'$.functions['+i+'].body',locals,ix,next,f.rounding,a),f.result,a,s);}catch(error){throw kernel.annotate(error,name,f.on_evaluation_error);}
 };
 const run=(e:GenericExprV1,p:string,env:any,ix:number[],calls:string[],rounding:string,a:any):any=>{
  const k=kernel,s=k.site(p,ix,calls),t=types.get(p)!;k.charge(a,s);
  const sub=(x:GenericExprV1,key:string,en=env,ind=ix)=>run(x,p+'.'+key,en,ind,calls,rounding,a),scope=(bindings:any)=>{const next=Object.assign(Object.create(null),env,bindings),resolver=privateResolvers.get(env);if(resolver)privateResolvers.set(next,resolver);return next;},check=(v:any,ind=ix)=>k.checkpoint(v,t,a,k.site(p,ind,calls)),partial=(v:any,ind=ix)=>k.partial(v,t,a,k.site(p,ind,calls));let v:any;
  switch(e.op){
   case'literal':v=e.type.kind==='scalar'&&e.type.name==='UInt64'?BigInt(e.value as string):e.value;break;
   case'validate_refinement':v=sub(e.value,'value');k.checkpoint(v,{kind:'refinement',name:e.refinement},a,s);break;
   case'var':{const selected=privateResolvers.get(env)?.(e.name,a,s);v=selected?.found?selected.value:env[e.name];}break;
   case'field':{const value=sub(e.value,'value'),vt=types.get(p+'.value')!;v=vt.kind==='variant'?value.fields[e.field]:value[e.field];}break;
   case'record':{v=Object.create(null);for(const [name,value]of Object.entries(e.fields))v[name]=sub(value,'fields.'+name);}break;
   case'record_update':{v=Object.assign(Object.create(null),sub(e.value,'value'));for(const [name,value]of Object.entries(e.fields))v[name]=sub(value,'fields.'+name);}break;
   case'enum_value':{const def=k.enums.get(e.type_name),simple=def.variants.every((x:any)=>!Object.keys(x.fields).length);if(simple)v=e.variant;else{const fields=Object.create(null);for(const [name,value]of Object.entries(e.fields))fields[name]=sub(value,'fields.'+name);v={kind:e.variant,fields};}}break;
   case'list':v=e.items.map((item,i)=>sub(item,'items['+i+']'));break;
   case'append':{const source=sub(e.source,'source'),item=sub(e.item,'item');k.checkpoint(item,e.list_type.element,a,s);if(source.length>=Math.min(e.list_type.max_items,c.limits.max_items))k.fail('OutputBound',s);k.charge(a,s,source.length+1);v=[...source,item];partial(v);}break;
   case'none':v={kind:'none'};break;
   case'some':v={kind:'some',value:sub(e.value,'value')};break;
   case'present':case'absent':{const value=sub(e.value,'value');v=e.op==='present'?value.kind==='some':value.kind==='none';}break;
   case'require_some':{const value=sub(e.value,'value');if(value.kind!=='some')k.fail('InputType',s);v=value.value;}break;
   case'require_variant':v=sub(e.value,'value');k.variant(v,{kind:'variant',enum_name:e.enum_name,variant:e.variant},s);break;
   case'tag':{const value=sub(e.value,'value');v=typeof value==='string'?value:(value.kind??value.tag);}break;
   case'all_unique_exact':{const values=sub(e.value,'value');v=true;if(generic){outer:for(let j=0;j<values.length;j++)for(let i=0;i<j;i++)if(k.equal(values[j],values[i],a,k.site(p,[...ix,j,i],calls))){v=false;break outer;}}else{const seen=new Set();for(let i=0;i<values.length;i++){const item=values[i],is=k.site(p,[...ix,i],calls);k.charge(a,is);if(typeof item==='string')k.byteWork(a,is,new TextEncoder().encode(item).length);if(seen.has(item)){v=false;break;}seen.add(item);}}}break;
   case'length':{const value=sub(e.value,'value');if(e.unit==='items')v=BigInt(value.length);else{k.byteWork(a,s,new TextEncoder().encode(value).length);v=BigInt(e.unit==='unicode-scalars'?[...value].length:new TextEncoder().encode(value).length);}}break;
   case'let':{let value=sub(e.value,'value');if(generic)value=k.checkpoint(value,e.binding.type,a,k.site(p+'.value',ix,calls));v=sub(e.body,'body',scope({[e.binding.name]:value}));}break;
   case'if':v=sub(e.condition,'condition')===true?sub(e.then,'then'):sub(e.else,'else');break;
   case'unary':v=!sub(e.value,'value');break;
   case'concat':{const left=sub(e.left,'left'),right=sub(e.right,'right');if(typeof left!=='string'||typeof right!=='string')k.fail('InputType',s);v=k.checkpoint(left+right,e.result_type,a,s);}break;
   case'binary':{
    const left=sub(e.left,'left');if(e.operator==='and'&&left===false){v=false;break;}if(e.operator==='or'&&left===true){v=true;break;}const right=sub(e.right,'right');
    switch(e.operator){case'and':case'or':v=right;break;case'eq':v=k.equal(left,right,a,s);break;case'lt':v=left<right;break;case'lte':v=left<=right;break;case'gt':v=left>right;break;case'gte':v=left>=right;break;
     case'add':v=left+right;if(v>k.max)k.fail('ArithmeticOverflow',s);break;case'subtract':v=left-right;if(v<0n)k.fail('ArithmeticUnderflow',s);break;case'multiply':v=left*right;if(v>k.max)k.fail('ArithmeticOverflow',s);break;
     case'divide':if(right===0n)k.fail('DivideByZero',s);{const aa=left as bigint,bb=right as bigint,r=aa%bb;if(r!==0n&&rounding==='reject')k.fail('InexactDivision',s);v=aa/bb+(r!==0n&&rounding==='ceil'?1n:0n);}break;
    }
   }break;
   case'call':{if(callOwner){const h=callOwner.bind(p);callOwner.assertCall(h,p,e.declaration);}v=invoke(e.declaration,e.arguments.map((arg,i)=>sub(arg,'arguments['+i+']')),p,ix,calls,a);}break;
   case'map':case'filter':{const source=sub(e.source,'source'),out:any[]=[];partial(out);for(let i=0;i<source.length;i++){const ind=[...ix,i];k.charge(a,k.site(p,ind,calls));const en=scope({[e.item.name]:source[i]}),item=e.op==='map'?sub(e.body,'body',en,ind):sub(e.predicate,'predicate',en,ind);if(e.op==='map')out.push(item);else if(item===true)out.push(source[i]);partial(out,ind);}v=out;}break;
   case'fold':case'indexed_fold':{const source=sub(e.source,'source');let state=sub(e.initial,'initial');check(state);for(let i=0;i<source.length;i++){const ind=[...ix,i];k.charge(a,k.site(p,ind,calls));const bindings:any={[e.state.name]:state,[e.item.name]:source[i]};if(e.op==='indexed_fold')bindings[e.index.name]=BigInt(i);state=sub(e.body,'body',scope(bindings),ind);check(state,ind);}v=state;}break;
   case'repeat':{const count=sub(e.count,'count');if(count>BigInt(e.max_iterations))k.fail('IterationBound',k.site(p+'.count',ix,calls));let state=sub(e.initial,'initial');check(state);for(let i=0;i<Number(count);i++){const ind=[...ix,i];k.charge(a,k.site(p,ind,calls));state=sub(e.body,'body',scope({[e.state.name]:state,[e.index.name]:BigInt(i)}),ind);check(state,ind);}v=state;}break;
   case'while_bounded':case'until_bounded':{let state=sub(e.initial,'initial');check(state);let i=0;for(;;){const ind=[...ix,i],en=scope({[e.state.name]:state}),guard=sub(e.guard,'guard',en,ind),more=e.op==='until_bounded'?!guard:guard;if(!more)break;if(i>=e.max_iterations)k.fail('IterationLimit',k.site(p,ind,calls));k.charge(a,k.site(p,ind,calls));state=sub(e.body,'body',en,ind);check(state,ind);i++;}v=state;}break;
   case'range':{const start=sub(e.start,'start'),end=sub(e.end,'end'),step=sub(e.step,'step');if(step===0n)k.fail('IterationBound',s);const count=start>=end?0n:(end-start+step-1n)/step;if(count>BigInt(e.max_iterations))k.fail('IterationBound',s);const out:any[]=[];partial(out);for(let i=0;i<Number(count);i++){const ind=[...ix,i];k.charge(a,k.site(p,ind,calls));out.push(start+BigInt(i)*step);partial(out,ind);}v=out;}break;
   case'sort':{const source=sub(e.source,'source'),decorated:any[]=[];for(let i=0;i<source.length;i++){const ind=[...ix,i];k.charge(a,k.site(p,ind,calls));const en=scope({[e.item.name]:source[i]});decorated.push({value:source[i],ordinal:i,keys:e.keys.map((key,j)=>sub(key.value,'keys['+j+'].value',en,ind))});}const sorted:any[]=[],sized:any[]=[];partial(sized);const compare=(left:any,right:any)=>{for(let j=0;j<e.keys.length;j++){const key=e.keys[j]!,n=k.compare(left.keys[j],right.keys[j],key.mode,a,k.site(p,[...ix,left.ordinal,right.ordinal,j],calls));if(n)return key.direction==='desc'?-n:n;}return 0;};for(const item of decorated){let j=sorted.length;while(j>0&&compare(item,sorted[j-1])<0)j--;sorted.splice(j,0,item);sized.push(item.value);partial(sized,[...ix,item.ordinal]);}v=sorted.map(x=>x.value);}break;
   case'policy':{let action=e.otherwise,key='otherwise';for(let j=0;j<e.cases.length;j++)if(sub(e.cases[j]!.condition,'cases['+j+'].condition')===true){action=e.cases[j]!.action;key='cases['+j+'].action';break;}const binding=policies.get(p+'.'+key)!,pending=k.select(a,s,e.declaration,binding.branch,action.calculation,binding.invocation_path);try{v=sub(action.expression,key+'.expression');}finally{a.pending.splice(a.pending.indexOf(pending),1);}}break;
   case'match':{const value=sub(e.value,'value'),en=scope({[e.binding.name]:value});let selected=e.otherwise,key='otherwise';for(let j=0;j<e.cases.length;j++)if(sub(e.cases[j]!.when,'cases['+j+'].when',en)===true){selected=e.cases[j]!.then;key='cases['+j+'].then';break;}v=sub(selected,key,en);}break;
   case'match_variant':{const value=sub(e.value,'value'),vt=types.get(p+'.value')!,variant=k.variant(value,vt,s);const index=e.cases.findIndex(cs=>cs.variant===variant.x.name);if(index<0){if(!e.otherwise)k.fail('InvalidContract',s);v=sub(e.otherwise!,'otherwise');}else{const cs=e.cases[index]!,names=Object.keys(variant.x.fields),en=cs.binding?scope({[cs.binding]:names.length===1?variant.fields[names[0]!]:value}):env;v=sub(cs.then,'cases['+index+'].then',en);}}break;
   case'state_machine':{const state=sub(e.state,'state'),event=sub(e.event,'event'),en=scope({[e.state_binding.name]:state,[e.event_binding.name]:event});v={tag:e.otherwise==='stay'?'stayed':'rejected',state,intents:[],machine:e.declaration,branch:'otherwise',reason:e.otherwise_reason??'no-match-stay'};for(let j=0;j<e.transitions.length;j++){const tr=e.transitions[j]!;if(sub(tr.guard,'transitions['+j+'].guard',en)===true){const next=sub(tr.next,'transitions['+j+'].next',en),intents:any[]=[];for(let z=0;z<tr.intents.length;z++){intents.push(sub(tr.intents[z]!,'transitions['+j+'].intents['+z+']',en));k.checkpoint(intents,{kind:'list',element:e.intent_type,min_items:0,max_items:e.max_intents},a,s);}v={tag:'transition',state:next,intents,machine:e.declaration,branch:'transition:'+j,reason:'matched'};break;}}}break;
  }
  return check(v);
 };
 const evaluate=(input:Uint8Array,observe:boolean):CommerceComputationObservation=>{
 const a=kernel.fresh(observe);let result:CommerceEvaluationResult;
 try{const env=kernel.input(input,a);a.phase='expression';const value=run(c.expression,'$.expression',env,[],[],c.rounding,a);a.phase='output-validation';const wire=kernel.output(value,a);a.phase='complete';result={ok:true,wire,fuel_used:a.used};}catch(error){result=kernel.failure(error,a) as {ok:false;error:ExpressionFailureV1;fuel_used:number};}
 current();return kernel.observation(a,result);
 };
 return {evaluate,current,kernel,contract:c,runRole(name:string,env:any,a:any,resolvePrivate:(name:string,account:any,site:any)=>{found:boolean;value:any},calls:string[]){current();if(subject.kind!=='keyed')throw new Error('private keyed execution only');const row=functions.get(name);if(!row)kernel.fail('UnknownReference',kernel.site('$.role'));privateResolvers.set(env,resolvePrivate);return run(row!.f.body,'$.functions['+row!.i+'].body',env,[],calls,row!.f.rounding,a);}};
}
