import type {TypedRulePolicyContract} from '../typed-backend/policy-rules.js';
import type {CompiledProjectGraph} from '../input/project-model.js';
import {decodeTypedRecordContract,decodeTypedSumContract,decodeTypedRuleContract,type TypedType,type TypedRecordContract,type TypedSumContract,type TypedRuleContract,type RuleExpression,type ValueExpression} from '../typed-operation/contracts.js';
import type {SumRecipe} from './reconciled-sum-controls.js';
export type WitnessDeclaration=Readonly<{kind:'Entity'|'Value Object';contract:TypedRecordContract}>|Readonly<{kind:'Enum';contract:TypedSumContract}>;
type Bound=Readonly<{type:TypedType;value:any}>;
const part=(s:string)=>s.length+':'+s;
const fail=(message:string):never=>{throw new TypeError('DS_RECORD_RULE_REFERENCE:'+message);};
export class RuleWitnessCapacity extends Error {}
/** Source interpreter for verification only. Never imports a generated renderer/runtime. */
export function createRecordRuleReference(graph:CompiledProjectGraph){
 const declarations=new Map<string,WitnessDeclaration>(),rules=new Map<string,TypedRuleContract>();
 for(const n of graph.nodes){
  if(n.kind==='Entity'||n.kind==='Value Object')declarations.set(n.selector,{kind:n.kind,contract:decodeTypedRecordContract(n.body.typed_contract)});
  else if(n.kind==='Enum')declarations.set(n.selector,{kind:'Enum',contract:decodeTypedSumContract(n.body.typed_contract)});
  else if(n.kind==='Rule')rules.set(n.selector,decodeTypedRuleContract(n.body.typed_contract));
 }
 const get=(s:string)=>declarations.get(s)??fail('missing declaration:'+s);
 const shape=(d:WitnessDeclaration):TypedType=>d.kind==='Enum'?{kind:'sum',variants:d.contract.variants}:fail('sum required');
 const key=(t:TypedType,v:any):string=>{
  if(t.kind==='scalar')return part(t.name)+part(t.name==='Bool'?(v?'1':'0'):String(v));
  if(t.kind==='optional')return v===null?part('absent'):part('present')+part(key(t.element,v));
  if(t.kind==='list'||t.kind==='set')return part(t.kind)+part(String(v.length))+v.map((x:any)=>part(key(t.element,x))).join('');
  if(t.kind==='sum'){const variant=t.variants.find(x=>x.name===v.variant)??fail('unknown variant');return part('sum')+part(v.variant)+(variant.payload?part(key(variant.payload,v.payload)):part('no-payload'));}
  const d=get(t.selector);if(d.kind==='Enum')return part(t.selector)+part(key(shape(d),v));
  const fields=[...d.contract.properties].filter(f=>d.kind!=='Entity'||f.identity).sort((a,b)=>a.name<b.name?-1:1);
  return part(d.kind)+part(t.selector)+fields.map(f=>part(f.name)+part(key(f.type,v[f.name]))).join('');
 };
 // Back-to-front insertion preserves the first source representative on overwrite.
 const toSet=(t:TypedType,values:any[])=>[...new Map([...values].reverse().map(v=>[key(t,v),v])).entries()].sort(([a],[b])=>a<b?-1:a>b?1:0).map(([,v])=>v);
 const fact=(t:TypedType,r:SumRecipe):any=>{
  if(t.kind==='scalar')return t.name==='UInt64'?BigInt(r.value as string):r.value;
  if(t.kind==='optional')return r.tag==='null'?null:fact(t.element,r);
  if(t.kind==='list'||t.kind==='set'){const values=r.items!.map(v=>fact(t.element,v));return t.kind==='set'?toSet(t.element,values):values;}
  if(t.kind==='sum'){const v=t.variants.find(v=>v.name===r.variant)??fail('unknown recipe variant');return {variant:v.name,...(v.payload?{payload:fact(v.payload,r.payload!)}:{})};}
  const d=get(t.selector);
  if(d.kind==='Enum')return fact(shape(d),r.tag==='enum'?{tag:'sum',variant:r.variant!}:r.input!);
  return Object.fromEntries(d.contract.properties.map(p=>[p.name,fact(p.type,r.fields![p.name]!)]));
 };
 const value=(e:ValueExpression,scope:ReadonlyMap<string,Bound>):Bound=>{
  if(e.op==='literal')return {type:{kind:'scalar',name:e.type},value:e.type==='UInt64'?BigInt(e.value as string|number):e.value};
  if(e.op==='variant'){for(const [selector,d] of declarations)if(d.kind==='Enum'){const v=d.contract.variants.find(v=>v.ontology_variant===e.selector);if(v&&v.payload===null)return {type:{kind:'named',selector},value:{variant:v.name}};}return fail('unknown literal variant');}
  if(e.op==='to_set'){const v=value(e.value,scope);if(v.type.kind!=='list')return fail('to_set requires list');return {type:{kind:'set',element:v.type.element},value:toSet(v.type.element,v.value)};}
  let current=scope.get(e.root)??fail('unknown parameter:'+e.root);
  for(const property of e.properties){
   const type=current.type,collection=type.kind==='list'||type.kind==='set',owner=collection?type.element:type;
   if(owner.kind!=='named')return fail('projection requires named value');
   const d=get(owner.selector);if(d.kind==='Enum')return fail('record projection required');
   const p=d.contract.properties.find(p=>p.ontology_property===property)??fail('unknown ontology property');
   if(collection){const mapped=current.value.map((v:any)=>v[p.name]);current={type:{kind:type.kind,element:p.type},value:type.kind==='set'?toSet(p.type,mapped):mapped};}
   else current={type:p.type,value:current.value[p.name]};
  }return current;
 };
 let visits=0;
 type Call={selector:string;parent:number|null;input:Record<string,unknown>;result:boolean};
 let tracing:Call[]|null=null;
 const callStack:number[]=[];
 const expression=(e:RuleExpression,scope:ReadonlyMap<string,Bound>,depth:number):boolean=>{
  if(++visits>65536||depth>64)throw new RuleWitnessCapacity('bounded record witness Rule evaluation exceeded');
  if(e.op==='all'||e.op==='any')return e.op==='all'?e.terms.every(t=>expression(t,scope,depth+1)):e.terms.some(t=>expression(t,scope,depth+1));
  if(e.op==='not')return !expression(e.term,scope,depth+1);
  if(e.op==='rule_ref'){const args=new Map(e.arguments.map(a=>[a.parameter,value(a.value,scope)]));return evaluate(e.selector,args,depth+1);}
  if(e.op==='eq'||e.op==='lt'||e.op==='set_equal'||e.op==='contains'){
   const a=value(e.left,scope),b=value(e.right,scope);
   if(e.op==='lt')return a.value<b.value;
   if(e.op==='contains'){if(a.type.kind!=='list'&&a.type.kind!=='set')return fail('collection required');const element=a.type.element;return a.value.some((x:any)=>key(element,x)===key(b.type,b.value));}
   return key(a.type,a.value)===key(b.type,b.value);
  }
  if(e.op!=='unique'&&e.op!=='exists'&&e.op!=='exactly_one')return fail('unsupported checked expression');
  const source=value(e.collection,scope);if(source.type.kind!=='list'&&source.type.kind!=='set')return fail('quantifier collection required');
  const element=source.type.element,nested=(v:any)=>new Map([...scope,[e.binding,{type:element,value:v}] as const]);
  if(e.op==='unique'){
   if(e.where.op!=='eq')return fail('checked unique equality required');
   const field=e.where.left;return new Set(source.value.map((v:any)=>{const b=value(field,nested(v));return key(b.type,b.value);})).size===source.value.length;
  }
  if(e.op==='exists')return source.value.some((v:any)=>expression(e.where,nested(v),depth+1));
  return source.value.filter((v:any)=>expression(e.where,nested(v),depth+1)).length===1;
 };
 const evaluate=(selector:string,args:ReadonlyMap<string,Bound>,depth:number):boolean=>{
  const rule=rules.get(selector)??fail('missing bound Rule:'+selector);
  if(args.size!==rule.parameters.length||rule.parameters.some(p=>!args.has(p.name)))return fail('Rule argument coverage');
  if(!tracing)return expression(rule.expression,args,depth);
  const index=tracing.length;
  if(index>=65536)throw new RuleWitnessCapacity('bounded Rule trace capacity exceeded');
  const call:Call={selector,parent:callStack.at(-1)??null,input:Object.fromEntries([...args].map(([name,b])=>[name,b.value])),result:false};
  tracing.push(call);callStack.push(index);
  try{call.result=expression(rule.expression,args,depth);return call.result;}finally{callStack.pop();}
 };
 const seeds=(roots:readonly string[],extra:readonly ValueExpression[]=[])=>{
  const literals:{type:string;value:string|boolean}[]=[],seen=new Set<string>();
  const visit=(selector:string)=>{if(seen.has(selector))return;seen.add(selector);walk((rules.get(selector)??fail('missing seed Rule')).expression);};
  const walk=(v:any)=>{if(!v||typeof v!=='object')return;if(v.op==='literal')literals.push({type:v.type,value:v.type==='UInt64'?String(v.value):v.value});if(v.op==='rule_ref')visit(v.selector);for(const x of Object.values(v))if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object')walk(x);};
  roots.forEach(visit);extra.forEach(walk);return literals;
 };
 const select=(contract:TypedRulePolicyContract,args:ReadonlyMap<string,Bound>)=>{
  visits=0;
  for(const [index,c] of contract.cases.entries())if(evaluate(c.rule.selector,new Map(c.rule.arguments.map(a=>[a.parameter,value(a.value,args)])),0))return {target:c.target,index};
  return {target:contract.default_target,index:-1};
 };
 return {declarations,rules,get,key,fact,seeds,select,tracePolicy:(contract:TypedRulePolicyContract,args:ReadonlyMap<string,Bound>)=>{
  const calls:Call[]=[];tracing=calls;callStack.length=0;
  try{return {...select(contract,args),calls};}finally{tracing=null;callStack.length=0;}
 },traceGuard:(guard:Readonly<{selector:string;arguments:readonly Readonly<{parameter:string;value:ValueExpression}>[]}>,args:ReadonlyMap<string,Bound>)=>{
  const calls:Call[]=[];tracing=calls;callStack.length=0;visits=0;
  try{return {result:evaluate(guard.selector,new Map(guard.arguments.map(a=>[a.parameter,value(a.value,args)])),0),calls};}finally{tracing=null;callStack.length=0;}
 },traceEvaluation:(selector:string,args:ReadonlyMap<string,Bound>)=>{
  const calls:Call[]=[];tracing=calls;callStack.length=0;visits=0;
  try{return {result:evaluate(selector,args,0),calls};}finally{tracing=null;callStack.length=0;}
 },guard:(guard:Readonly<{selector:string;arguments:readonly Readonly<{parameter:string;value:ValueExpression}>[]}>,args:ReadonlyMap<string,Bound>)=>{
  visits=0;return evaluate(guard.selector,new Map(guard.arguments.map(a=>[a.parameter,value(a.value,args)])),0);
 },evaluate:(selector:string,args:ReadonlyMap<string,Bound>)=>{visits=0;return evaluate(selector,args,0);}};
}
