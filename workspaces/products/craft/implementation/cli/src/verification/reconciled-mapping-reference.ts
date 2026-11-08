import type {CompiledProjectGraph} from '../input/project-model.js';
import {decodeTypedRecordContract,decodeTypedSumContract,type ValueExpression} from '../typed-operation/contracts.js';
import {decodeNamedInterface} from '../typed-backend/interface.js';
import {qualifyPublicType,type MappingValueType as Type} from '../typed-backend/mapping-public.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
export type {MappingValueType as MappingType} from '../typed-backend/mapping-public.js';
type Bound=Readonly<{type:Type;value:any}>;
type Field=Readonly<{name:string;ontology_property:string;type:Type;identity?:boolean}>;
const part=(s:string)=>s.length+':'+s;
export class MappingCapacity extends Error {}
/** Independent source interpretation. Public declarations keep their actual qualified identity. */
export function createMappingReference(graph:CompiledProjectGraph){
 const domain=new Map(graph.nodes.filter(n=>['Entity','Value Object','Enum'].includes(n.kind)).map(n=>[n.selector,{kind:n.kind,contract:n.kind==='Enum'?decodeTypedSumContract(n.body.typed_contract):decodeTypedRecordContract(n.body.typed_contract)}] as const));
 const apis=new Map(graph.nodes.filter(n=>n.kind==='Interface').map(n=>[n.selector,decodeNamedInterface(n.body.typed_contract)]));
 const get=(t:Type):{kind:string;properties:readonly Field[];variants?:any}=>{
  if(t.kind==='contract'){
   const c=apis.get(t.interface_selector)?.contracts.find(c=>c.contract_id===t.contract_id);if(!c)throw new TypeError('MAPPING_REFERENCE:public declaration');
   return {kind:'Public Contract',properties:c.fields.map(f=>({name:f.name,ontology_property:f.ontology_field,type:qualifyPublicType(f.type,t.interface_selector)}))};
  }
  if(t.kind!=='named')throw new TypeError('MAPPING_REFERENCE:declared value required');
  const d=domain.get(t.selector);if(!d)throw new TypeError('MAPPING_REFERENCE:domain declaration');
  return d.kind==='Enum'?{kind:d.kind,properties:[],variants:(d.contract as any).variants}:{kind:d.kind,properties:(d.contract as any).properties};
 };
 const key=(t:Type,v:any):string=>{
  if(t.kind==='scalar')return part(t.name)+part(t.name==='Bool'?(v?'1':'0'):String(v));
  if(t.kind==='optional')return v===null?part('absent'):part('present')+part(key(t.element,v));
  if(t.kind==='list'||t.kind==='set')return part(t.kind)+part(String(v.length))+v.map((x:any)=>part(key(t.element,x))).join('');
  if(t.kind==='sum'){const variant=t.variants.find(x=>x.name===v.variant)!;return part('sum')+part(v.variant)+(variant.payload?part(key(variant.payload,v.payload)):part('no-payload'));}
  const d=get(t);if(d.kind==='Enum')return part((t as any).selector)+part(key({kind:'sum',variants:d.variants},v));
  const fields=[...d.properties].filter(f=>d.kind!=='Entity'||f.identity).sort((a,b)=>a.name<b.name?-1:1);
  const prefix=t.kind==='contract'?part(t.interface_selector)+part(t.contract_id):part(d.kind)+part((t as Extract<Type,{kind:'named'}>).selector);
  return prefix+fields.map(f=>part(f.name)+part(key(f.type,v[f.name]))).join('');
 };
 const toSet=(t:Type,values:any[])=>[...new Map([...values].reverse().map(v=>[key(t,v),v])).entries()].sort(([a],[b])=>a<b?-1:a>b?1:0).map(([,v])=>v);
 const fact=(t:Type,r:FactRecipe):any=>{
  if(t.kind==='scalar')return t.name==='UInt64'?BigInt(r.value as string):r.value;
  if(t.kind==='optional')return r.tag==='null'?null:fact(t.element,r);
  if(t.kind==='list'||t.kind==='set'){const v=r.items!.map(x=>fact(t.element,x));return t.kind==='set'?toSet(t.element,v):v;}
  if(t.kind==='sum'){const v=t.variants.find(v=>v.name===r.variant)!;return {variant:v.name,...(v.payload?{payload:fact(v.payload,r.payload!)}:{})};}
  const d=get(t);if(d.kind==='Enum')return fact({kind:'sum',variants:d.variants},r.input!);
  return Object.fromEntries(d.properties.map(p=>[p.name,fact(p.type,r.fields![p.name]!)]));
 };
 const value=(e:ValueExpression,scope:ReadonlyMap<string,Bound>):Bound=>{
  if(e.op==='literal')return {type:{kind:'scalar',name:e.type},value:e.type==='UInt64'?BigInt(e.value as string|number):e.value};
  if(e.op==='variant'){for(const [selector,d]of domain)if(d.kind==='Enum'){const v=(d.contract as any).variants.find((v:any)=>v.ontology_variant===e.selector);if(v)return {type:{kind:'named',selector},value:{variant:v.name}};}throw new TypeError('MAPPING_REFERENCE:variant');}
  if(e.op==='to_set'){const v=value(e.value,scope);if(v.type.kind!=='list')throw new TypeError('MAPPING_REFERENCE:list');return {type:{kind:'set',element:v.type.element},value:toSet(v.type.element,v.value)};}
  let current=scope.get(e.root)!;
  for(const property of e.properties){
   const t=current.type,collection=t.kind==='list'||t.kind==='set',owner=collection?t.element:t;
   const p=get(owner).properties.find(p=>p.ontology_property===property)!;
   if(collection){const mapped=current.value.map((v:any)=>v[p.name]);current={type:{kind:t.kind,element:p.type},value:t.kind==='set'?toSet(p.type,mapped):mapped};}
   else current={type:p.type,value:current.value[p.name]};
  }return current;
 };
 const seeds=(extra:readonly unknown[])=>{const literals:{type:string;value:string|boolean}[]=[];
  const walk=(v:any)=>{if(!v||typeof v!=='object')return;if(v.op==='literal')literals.push({type:v.type,value:v.type==='UInt64'?String(v.value):v.value});for(const x of Object.values(v))if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object')walk(x);};extra.forEach(walk);return literals;};
 const fail=(message:string):never=>{throw new TypeError(message);};
 const unwrap=(r:FactRecipe):FactRecipe=>r.tag==='bad'&&['frozen','null-prototype'].includes(r.mode!)?unwrap(r.base!):r;
 const members=(r:FactRecipe,error:string):Record<string,FactRecipe>=>{
  r=unwrap(r);if(r.tag==='bad'&&r.mode==='missing-field'){const fields={...members(r.base!,error)};delete fields[r.field!];return fields;}
  if(!['record','fields'].includes(r.tag))return fail(error);return {...r.fields};
 };
 const normalize=(t:Type,r:FactRecipe,error:string,depth=0):any=>{
  if(depth>64)throw new MappingCapacity('bounded Mapping normalization depth exceeded');
  if(t.kind==='contract')error='INTERFACE_VALUE';
  if(t.kind==='optional'&&(r.tag==='null'||r.tag==='bad'&&r.mode==='null'))return null;
  if(t.kind==='scalar'){
   if(r.tag!=='scalar')return fail(error);
   if(t.name==='String')return typeof r.value==='string'?r.value:fail(error);
   if(t.name==='Bool')return typeof r.value==='boolean'?r.value:fail(error);
   if(typeof r.value!=='string'||!/^(?:0|[1-9][0-9]*)$/.test(r.value))return fail(error);
   const n=BigInt(r.value);if(n>18446744073709551615n||r.format==='number'&&n>9007199254740991n)return fail(error);return n;
  }
  if(t.kind==='optional')return normalize(t.element,r,error,depth+1);
  if(t.kind==='list'||t.kind==='set'){
   if(r.tag!==t.kind)return fail(error);const values=r.items!.map(v=>normalize(t.element,v,error,depth+1));
   if(t.kind==='set'){if(new Set(values.map(v=>key(t.element,v))).size!==values.length)return fail(error);return toSet(t.element,values);}return values;
  }
  if(t.kind==='sum'){
   if(r.tag!=='sum')return fail(error);const v=t.variants.find(v=>v.name===r.variant);if(!v||!!v.payload!==!!r.payload)return fail(error);
   return {variant:v.name,...(v.payload?{payload:normalize(v.payload,r.payload!,error,depth+1)}:{})};
  }
  const d=get(t);if(d.kind==='Enum')return r.tag==='named'?normalize({kind:'sum',variants:d.variants},r.input!,error,depth+1):fail(error);
  const fields=members(r,error);if(Object.keys(fields).some(k=>!d.properties.some(p=>p.name===k)))return fail(error);
  return Object.fromEntries([...d.properties].sort((a,b)=>a.name<b.name?-1:1).map(p=>[p.name,Object.hasOwn(fields,p.name)?normalize(p.type,fields[p.name]!,error,depth+1):p.type.kind==='optional'?null:fail(error)]));
 };
 return {get,key,fact,value,seeds,normalize,members};
}
