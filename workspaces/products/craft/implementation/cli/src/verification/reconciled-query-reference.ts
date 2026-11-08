import type {TypedType} from '../typed-operation/contracts.js';
import type {TypedQueryContract,BackendPredicate,BackendValue} from '../typed-backend/contracts.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
import {RuleFactsCapacity} from './reconciled-rule-facts.js';
import type {createRecordRuleReference} from './reconciled-rule-reference.js';
/** Query-only interpretation of checked source meaning; never imports generated code. */
export function createQueryReference(contract:TypedQueryContract,reference:ReturnType<typeof createRecordRuleReference>){
 const source=reference.get(contract.source);if(source.kind!=='Entity')throw new TypeError('QUERY_REFERENCE:source Entity');
 const fields=source.contract.properties,fail=():never=>{throw new TypeError('QUERY_INPUT');};
 const members=(r:FactRecipe):Record<string,FactRecipe>=>{
  if(r.tag==='bad'&&['frozen','null-prototype'].includes(r.mode!))return members(r.base!);
  if(r.tag==='bad'&&r.mode==='missing-field'){const d={...members(r.base!)};delete d[r.field!];return d;}
  if(!['record','fields'].includes(r.tag))return fail();return {...r.fields};
 };
 const normalize=(t:TypedType,r:FactRecipe,depth=0):any=>{
  if(depth>64)throw new RuleFactsCapacity('bounded Query normalization depth exceeded');
  if(t.kind==='optional'&&(r.tag==='null'||r.tag==='bad'&&r.mode==='null'))return null;
  if(t.kind==='scalar'){
   if(r.tag!=='scalar')return fail();
   if(t.name==='String')return typeof r.value==='string'?r.value:fail();
   if(t.name==='Bool')return typeof r.value==='boolean'?r.value:fail();
   if(typeof r.value!=='string'||!/^(?:0|[1-9][0-9]*)$/.test(r.value))return fail();
   const n=BigInt(r.value);return n>18446744073709551615n||r.format==='number'&&n>9007199254740991n?fail():n;
  }
  if(t.kind==='optional')return normalize(t.element,r,depth+1);
  if(t.kind==='list'||t.kind==='set'){
   if(r.tag!==t.kind)return fail();const rows=r.items!.map(x=>normalize(t.element,x,depth+1));
   if(t.kind==='set'){
    const keyed=rows.map(x=>[reference.key(t.element,x),x] as const);if(new Set(keyed.map(([k])=>k)).size!==rows.length)return fail();
    return keyed.sort(([a],[b])=>a<b?-1:a>b?1:0).map(([,x])=>x);
   }return rows;
  }
  if(t.kind==='sum'){
   if(r.tag!=='sum')return fail();const v=t.variants.find(v=>v.name===r.variant);if(!v||!!v.payload!==!!r.payload)return fail();
   return {variant:v.name,...(v.payload?{payload:normalize(v.payload,r.payload!,depth+1)}:{})};
  }
  const d=reference.get(t.selector);if(d.kind==='Enum')return r.tag==='named'?normalize({kind:'sum',variants:d.contract.variants},r.input!,depth+1):fail();
  const raw=members(r);if(Object.keys(raw).some(k=>!d.contract.properties.some(p=>p.name===k)))return fail();
  return Object.fromEntries([...d.contract.properties].sort((a,b)=>a.name<b.name?-1:1).map(p=>[p.name,Object.hasOwn(raw,p.name)?normalize(p.type,raw[p.name]!,depth+1):p.type.kind==='optional'?null:fail()]));
 };
 const value=(v:BackendValue,row:any,params:any):{type:TypedType;value:any}=>{
  if(v.kind==='literal')return {type:{kind:'scalar',name:v.type},value:v.type==='UInt64'?BigInt(v.value as number):v.value};
  return v.kind==='field'?{type:fields.find(f=>f.name===v.name)!.type,value:row[v.name]}:{type:contract.inputs.find(p=>p.name===v.name)!.type,value:params[v.name]};
 };
 const predicate=(p:BackendPredicate,row:any,params:any):boolean=>{
  if(p.op==='all'||p.op==='any')return p.op==='all'?p.terms.every(t=>predicate(t,row,params)):p.terms.some(t=>predicate(t,row,params));
  if(p.op==='not')return !predicate(p.term,row,params);
  if(!('left'in p))throw new TypeError('QUERY_REFERENCE:predicate');
  const a=value(p.left,row,params),b=value(p.right,row,params);
  return p.op==='eq'?reference.key(a.type,a.value)===reference.key(b.type,b.value):p.op==='lt'?a.value<b.value:p.op==='lte'?a.value<=b.value:p.op==='gt'?a.value>b.value:a.value>=b.value;
 };
 const evaluate=(rowRecipe:FactRecipe,paramRecipe:FactRecipe)=>{
  const raw=members(paramRecipe);if(Object.keys(raw).length!==contract.inputs.length||Object.keys(raw).some(k=>!contract.inputs.some(p=>p.name===k)))return fail();
  const params=Object.fromEntries(contract.inputs.map(p=>[p.name,normalize(p.type,raw[p.name]!) ]));
  const rows:any[]=normalize({kind:'list',element:{kind:'named',selector:contract.source}},rowRecipe);
  let selected=rows.filter(row=>contract.filter===null||predicate(contract.filter,row,params));
  if(contract.order_by){const {field,direction}=contract.order_by;selected=selected.map((row,index)=>({row,index})).sort((a,b)=>{
   const x=a.row[field],y=b.row[field],order=x<y?-1:x>y?1:0;return (direction==='asc'?order:-order)||a.index-b.index;
  }).map(x=>x.row);}
  if(contract.limit!==null)selected=selected.slice(0,contract.limit);
  if(contract.schema_version==='domainspec.typed-query/v2'&&contract.result_cardinality==='optional'){
   if(selected.length>1)throw new TypeError('QUERY_CARDINALITY');
   if(selected.length===0)return null;
   return contract.projection.map(name=>[name,view(selected[0][name])]);
  }
  return selected.map(row=>contract.projection.map(name=>[name,view(row[name])]));
 };
 return {fields,normalize,evaluate};
}
function view(v:any):unknown{return v===null?['null']:typeof v!=='object'?[typeof v,String(v)]:Array.isArray(v)?['array',v.map(view)]:['record',Object.keys(v).sort().map(k=>[k,view(v[k])])];}
