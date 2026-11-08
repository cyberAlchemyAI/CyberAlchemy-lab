/** Finite provider schema projection over the existing checked business values.
 * This inert generator creates no application, execution or effect owner.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions.
 */
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {stripTypeScriptTypes} from 'node:module';
import {types as host} from 'node:util';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {checkCoreRefinementPattern} from '../commerce/commerce-core-types.js';
import {dataDigest} from '../profile-engine/contracts.js';
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';
import type {GenericValueSchemaV1} from './computation-data-v1.js';

type Json = null|boolean|number|string|readonly Json[]|{readonly [key:string]:Json};
export interface GenericCapabilityCodecOptions {readonly id:string;readonly max_bytes:number;readonly max_items:number}
export interface GenericCapabilityCodec {readonly schema:Readonly<Record<string,Json>>;readonly schema_sha256:string;readonly source:string;readonly codec_sha256:string;readonly type:ValueTypeV1}
export interface GenericNativeVectorCodec extends Omit<GenericCapabilityCodec,'type'> {readonly type:Readonly<{kind:'native-vector';dimensions:number}>}
export interface GenericNativeVectorCodecOptions {readonly id:string;readonly max_bytes:number;readonly max_items?:number}
const sha=(text:string)=>createHash('sha256').update(text).digest('hex');
const end='(?![\\s\\S])';
const unicode='^(?:[^\\uD800-\\uDFFF]|[\\uD800-\\uDBFF][\\uDC00-\\uDFFF])*'+end;
// Decimal language bounded by UInt64's exact maximum, without Number conversion.
const uint64Maximum='18446744073709551615';
const uint64Pattern='^(?:0|[1-9][0-9]{0,18}|'+[
 ...[...uint64Maximum].flatMap((digit,index)=>{
  const lower=index===0?'1':'0',upper=String(Number(digit)-1);
  return upper<lower?[]:[uint64Maximum.slice(0,index)+(lower===upper?lower:'['+lower+'-'+upper+']')+'[0-9]{'+(19-index)+'}'];
 }),uint64Maximum].join('|')+')'+end;

/** Copy data without invoking getters, proxy traps or user serialization hooks. */
function inert<T>(input:T,id:string):T {
 const active=new WeakSet<object>();let nodes=0,bytes=0;
 const bad=(selector:string):never=>fail('InvalidContract',{path:id,start:0,end:0},selector+': finite inert contract data required');
 const copy=(value:any,selector:string,depth:number):any=>{
  if(++nodes>32768||depth>64)bad(selector);
  if(typeof value==='string'){bytes+=Buffer.byteLength(value);if(bytes>2097152||!value.isWellFormed())bad(selector);return value;}
  if(value===null||typeof value==='boolean'||typeof value==='number'&&Number.isSafeInteger(value))return value;
  if(!value||typeof value!=='object'||host.isProxy(value)||active.has(value))bad(selector);
  const array=Array.isArray(value),prototype=Object.getPrototypeOf(value);
  if(array?prototype!==Array.prototype:prototype!==Object.prototype&&prototype!==null)bad(selector);
  const descriptors=Object.getOwnPropertyDescriptors(value),names=Reflect.ownKeys(descriptors);
  if(names.some(name=>typeof name!=='string'))bad(selector);
  active.add(value);try{
   if(array){const length=descriptors.length?.value;if(!Number.isSafeInteger(length)||length<0||length>32768||names.length!==length+1)bad(selector);const out=[];
    for(let index=0;index<length;index++){const descriptor=descriptors[String(index)];if(!descriptor||!descriptor.enumerable||!Object.hasOwn(descriptor,'value'))bad(selector);out.push(copy(descriptor!.value,selector+'['+index+']',depth+1));}return out;}
   const out=Object.create(null);for(const name of names as string[]){const descriptor=descriptors[name]!;if(!descriptor.enumerable||!Object.hasOwn(descriptor,'value'))bad(selector+'.'+name);bytes+=Buffer.byteLength(name);if(bytes>2097152||!name.isWellFormed())bad(selector);out[name]=copy(descriptor.value,selector+'.'+name,depth+1);}return out;
  }finally{active.delete(value);}
 };return copy(input,'$',0);
}

/** Both artifacts use the same reachable, checked finite business type.
 * Invariants/predicates require original compiled declaration custody, which this
 * data-only API does not possess: reached constraints reject before any output.
 * Strings whose UTF8 bound cannot be expressed exactly by this strict subset,
 * nested optionals, outcomes and tagged enums likewise reject explicitly.
 */
export function generateGenericCapabilityCodec(values:GenericValueSchemaV1,type:ValueTypeV1,options:GenericCapabilityCodecOptions):GenericCapabilityCodec {
 const o=inert(options,'capability-codec'),id=typeof o?.id==='string'?o.id:'capability-codec',at={path:id,start:0,end:0};
 const bad=(selector:string,message:string):never=>fail('UnsupportedCapability',at,selector+': '+message);
 const invalid=(selector:string,message:string):never=>fail('InvalidContract',at,selector+': '+message);
 const bound=(n:unknown,selector:string,maximum=1048576):number=>typeof n==='number'&&Number.isSafeInteger(n)&&n>=0&&n<=maximum?n:invalid(selector,'finite nonnegative bound required');
 if(!id||id.length>1024||Object.keys(o).sort().join(',')!=='id,max_bytes,max_items')invalid('options','closed codec options required');
 if(!bound(o.max_bytes,'options.max_bytes')||!bound(o.max_items,'options.max_items',65536))invalid('options','positive input/output and collection bounds required');
 const v=inert(values,id),root=inert(type,id);
 if(v?.schema_version!=='craft.generic-values/v1-candidate'||!Array.isArray(v.records)||!Array.isArray(v.enums)||!Array.isArray(v.refinements)||!Array.isArray(v.collection_predicates))invalid('values','generic value schema required');
 const index=<T extends {readonly name:string}>(rows:readonly T[],selector:string)=>{const map=new Map<string,T>();for(const row of rows){if(typeof row?.name!=='string'||!row.name||map.has(row.name))invalid(selector,'unique named definitions required');map.set(row.name,row);}return map;};
 const records=index(v.records,'values.records'),enums=index(v.enums,'values.enums'),refinements=index(v.refinements,'values.refinements');
 const selectedRecords=new Map<string,GenericValueSchemaV1['records'][number]>(),selectedEnums=new Map<string,GenericValueSchemaV1['enums'][number]>(),selectedRefinements=new Map<string,GenericValueSchemaV1['refinements'][number]>();
 let visits=0;
 const project=(t:ValueTypeV1,selector:string,active=new Set<string>(),depth=0):Record<string,Json>=>{
  if(++visits>4096||depth>28)bad(selector,'finite schema expansion/depth exceeded');
  if(!t||typeof t!=='object')invalid(selector,'business value type required');
  const key=dataDigest(t);if(active.has(key))bad(selector,'recursive business type is outside the strict finite subset');
  const next=new Set(active);next.add(key);const child=(x:ValueTypeV1,name:string)=>project(x,selector+name,next,depth+1);
  const text=(maxBytes:number,maxScalars:number,minBytes=0,minScalars=0,pattern:string|null=null):Record<string,Json>=>{
   bound(maxBytes,selector+'.max_bytes');bound(maxScalars,selector+'.max_scalars');bound(minBytes,selector+'.min_bytes');bound(minScalars,selector+'.min_scalars');
   if(minBytes>maxBytes||minScalars>maxScalars)invalid(selector,'inverted string bound');
   const ascii=pattern!==null;
   if(pattern!==null)checkCoreRefinementPattern(pattern,at);
   // The finite Core pattern language is wholly ASCII, so byte/scalar counts
   // coincide. General scalar strings need redundant UTF8 minima and maxima.
   if(!ascii&&(maxBytes<4*maxScalars||minBytes>minScalars))bad(selector,'strict schema cannot express this nonredundant UTF8 byte bound');
   const schema:Record<string,Json>={type:'string',minLength:ascii?Math.max(minBytes,minScalars):minScalars,maxLength:ascii?Math.min(maxBytes,maxScalars):maxScalars,pattern:ascii?pattern!.slice(0,-1)+end:unicode};
   return schema;
  };
  switch(t.kind){
   case'scalar':if(t.name==='Bool')return {type:'boolean'};if(t.name==='UInt64')return {type:'string',minLength:1,maxLength:20,pattern:uint64Pattern};return invalid(selector,'unknown scalar');
   case'string':return text(t.max_bytes,t.max_scalars);
   case'literal':if(typeof t.value!=='string')return invalid(selector,'string literal required');return {type:'string',enum:[t.value]};
   case'optional':if(t.element?.kind==='optional')bad(selector,'nested Optional has ambiguous null wire representation');return {anyOf:[child(t.element,'.element'),{type:'null'}]};
   case'list':{
    const minimum=bound(t.min_items,selector+'.min_items',65536),maximum=bound(t.max_items,selector+'.max_items',65536);
    if(minimum>maximum)invalid(selector,'inverted list bound');if(minimum>o.max_items)bad(selector,'list minimum exceeds codec collection bound');
    if(v.collection_predicates.some(p=>dataDigest(p.type)===key))bad(selector,'collection predicates require the original compiled declaration owner');
    return {type:'array',items:child(t.element,'.element'),minItems:minimum,maxItems:Math.min(maximum,o.max_items)};
   }
   case'record':{
    const record=records.get(t.name);if(!record)bad(selector,'unavailable record '+t.name);
    if(!Array.isArray(record!.invariants)||record!.invariants.length)bad(selector,'record invariants require the original compiled declaration owner');
    if(!record!.fields||typeof record!.fields!=='object'||Array.isArray(record!.fields))invalid(selector,'record fields required');
    const entries=Object.entries(record!.fields);if(entries.length>128)bad(selector,'bounded record field count exceeded');
    selectedRecords.set(t.name,record!);const properties:Record<string,Json>=Object.create(null);
    for(const [name,field]of entries)properties[name]=child(field,'.fields.'+name);
    return {type:'object',properties,required:entries.map(([name])=>name),additionalProperties:false};
   }
   case'enum':case'variant':{
    const name=t.kind==='variant'?t.enum_name:t.name,definition=enums.get(name);if(!definition||!Array.isArray(definition.variants)||!definition.variants.length)bad(selector,'unavailable finite enum '+name);
    const variants=definition!.variants;if(variants.length>128||variants.some(x=>!x.fields||Object.keys(x.fields).length))bad(selector,'tagged enum wire shapes are outside the strict schema subset');
    if(new Set(variants.map(x=>x.wire)).size!==variants.length||new Set(variants.map(x=>x.name)).size!==variants.length||variants.some(x=>typeof x.wire!=='string'||typeof x.name!=='string'))invalid(selector,'unique finite enum names/wire strings required');
    const selected=t.kind==='variant'?variants.filter(x=>x.name===t.variant):variants;if(!selected.length)bad(selector,'unavailable enum variant');selectedEnums.set(name,definition!);
    return {type:'string',enum:selected.map(x=>x.wire)};
   }
   case'refinement':{
    const refinement=refinements.get(t.name);if(!refinement)bad(selector,'unavailable refinement '+t.name);
    const r=refinement!;if(r.carrier.kind!=='string'||r.normalization!=='none'||r.equality!=='exact-scalar-sequence')bad(selector,'only exact bounded string refinements are supported');
    if(r.carrier.kind!=='string')return bad(selector,'string refinement carrier required');
    if(r.carrier.max_bytes>r.max_utf8_bytes||r.carrier.max_scalars>r.max_unicode_scalars)bad(selector,'refinement maxima differ from the established kernel carrier');
    const schema=text(r.carrier.max_bytes,r.carrier.max_scalars,r.min_utf8_bytes,r.min_unicode_scalars,r.pattern);selectedRefinements.set(t.name,r);return schema;
   }
   default:return bad(selector,'unsupported strict schema business type '+t.kind);
  }
 };
 const schema=coreFreeze(project(root,'type'));
 const closure={...v,records:[...selectedRecords.values()],enums:[...selectedEnums.values()],refinements:[...selectedRefinements.values()],collection_predicates:[],root};
 // Read the original reusable semantic kernel; generated output embeds its JS
 // implementation and has no path/import dependency on the compiler checkout.
 const extension=import.meta.url.endsWith('.ts')?'.ts':'.js';
 const original=readFileSync(new URL('../commerce/commerce-computation-kernel'+extension,import.meta.url),'utf8');
 const kernel=(extension==='.ts'?stripTypeScriptTypes(original,{mode:'strip'}):original).replace('export function createCommerceValueKernel','function createCommerceValueKernel');
 const spec={schema_version:'craft.generic-computation/v1-candidate',values:closure,inputs:[{name:'value',type:root}],result:root,limits:{max_input_bytes:o.max_bytes+10,max_output_bytes:o.max_bytes,max_value_bytes:o.max_bytes,max_items:o.max_items,max_iterations:65536,max_ast_nodes:4096,max_ast_depth:32,max_call_depth:32,fuel:Math.min(16777216,65536+64*o.max_bytes)}};
 const source='// Generated finite business codec; no runtime/effect authority.\n// Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions.\nimport {types as host} from "node:util";\n'+kernel+'\nconst spec='+JSON.stringify(spec)+';\n'+String.raw`
const k=createCommerceValueKernel(spec,host,{record:()=>true,predicate:()=>false});
const encoder=new TextEncoder();
const prefix=encoder.encode('{"value":'),suffix=encoder.encode('}');
const freeze=value=>{if(value&&typeof value==='object'){for(const child of Object.values(value))freeze(child);Object.freeze(value);}return value;};
/** Validate provider JSON bytes, preserving exact canonical scalar strings. */
export function decode(wire){
 const a=k.fresh(),s=k.site('$');
 try{
  if(host.isProxy(wire)||!host.isUint8Array(wire))k.fail('InputType',s);
  let bytes;
  try{
   const prototype=Object.getPrototypeOf(Uint8Array.prototype),get=name=>Object.getOwnPropertyDescriptor(prototype,name).get.call(wire),length=get('byteLength'),buffer=get('buffer');
   if(length>spec.limits.max_output_bytes)k.fail('InputBound',s);
   if(host.isSharedArrayBuffer(buffer))k.fail('InputType',s);
   bytes=new Uint8Array(prefix.length+length+suffix.length);bytes.set(prefix);Uint8Array.prototype.set.call(bytes,new Uint8Array(buffer,get('byteOffset'),length),prefix.length);bytes.set(suffix,prefix.length+length);
  }catch(error){if(error&&error.error)throw error;k.fail('InputType',s);}
  const native=k.input(bytes,a).value;
  const canonical=k.output(native,a);
  const value=k.wire(native,spec.result,a,s);
  return Object.freeze({ok:true,value:freeze(value),wire:canonical,fuel_used:a.used});
 }catch(error){const result=k.failure(error,a);return Object.freeze({...result,error:Object.freeze({code:result.error.code,path:result.error.expression_path.replace(/^\$\.inputs\.value/,'$').replace(/^\$\.inputs/,'$')})});}
}
`;
 return coreFreeze({schema,schema_sha256:sha(JSON.stringify(schema)),source,codec_sha256:sha(source),type:root});
}

/** Reserved finite technical vector wire, not an AlchLang business value type.
 * JSON numbers are parsed as IEEE754 binary64. Both returned values and canonical
 * wire normalize negative zero to positive zero. No business scalar, UInt64 or
 * money conversion is performed. Input/output are bounded independently.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions.
 */
export function generateGenericNativeVectorCodec(dimensions:number,options:GenericNativeVectorCodecOptions):GenericNativeVectorCodec {
 const o=inert(options,'native-vector-codec'),id=typeof o?.id==='string'?o.id:'native-vector-codec',at={path:id,start:0,end:0};
 const invalid=(selector:string,message:string):never=>fail('InvalidContract',at,selector+': '+message);
 if(!o||typeof o!=='object'||!id||id.length>1024||!['id,max_bytes','id,max_bytes,max_items'].includes(Object.keys(o).sort().join(',')))invalid('options','closed native vector codec options required');
 if(!Number.isSafeInteger(dimensions)||dimensions<1||dimensions>65536)invalid('dimensions','finite dimension count in 1..65536 required');
 if(!Number.isSafeInteger(o.max_bytes)||o.max_bytes<2*dimensions+1||o.max_bytes>1048576)invalid('options.max_bytes','input/output bound must cover the minimum vector wire and remain at most 1MiB');
 const maxItems=o.max_items??dimensions;
 if(!Number.isSafeInteger(maxItems)||maxItems<dimensions||maxItems>65536)invalid('options.max_items','collection bound must cover the declared dimensions and remain at most 65536');
 const schema=coreFreeze({type:'array',items:{type:'number',minimum:-Number.MAX_VALUE,maximum:Number.MAX_VALUE},minItems:dimensions,maxItems:dimensions});
 const source='// Generated finite technical vector codec; no business/effect authority.\n// JSON numbers use IEEE754 binary64; negative zero becomes positive zero in value and wire.\n// Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions.\nimport {types as host} from "node:util";\nconst dimensions='+dimensions+',maxBytes='+o.max_bytes+';\n'+String.raw`
const reject=(code,path='$')=>Object.freeze({ok:false,error:Object.freeze({code,path})});
const encoder=new TextEncoder();
/** Accept raw UTF8 JSON only. Native typed-array getters avoid caller accessors. */
export function decode(wire){
 if(host.isProxy(wire)||!host.isUint8Array(wire))return reject('InputType');
 let bytes;
 try{
  const prototype=Object.getPrototypeOf(Uint8Array.prototype),get=name=>Object.getOwnPropertyDescriptor(prototype,name).get.call(wire),length=get('byteLength');
  // Establish the byte ceiling before allocating or copying any caller input.
  if(length>maxBytes)return reject('InputBound');
  for(const name of ['byteLength','byteOffset','buffer','length']){const own=Object.getOwnPropertyDescriptor(wire,name);if(own&&!Object.hasOwn(own,'value'))return reject('InputType');}
  const buffer=get('buffer');if(host.isSharedArrayBuffer(buffer))return reject('InputType');
  bytes=new Uint8Array(length);Uint8Array.prototype.set.call(bytes,new Uint8Array(buffer,get('byteOffset'),length));
 }catch{return reject('InputType');}
 let json;try{json=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes);}catch{return reject('InvalidUnicode');}
 let raw;try{raw=JSON.parse(json);}catch{return reject('InputType');}
 if(!Array.isArray(raw))return reject('InputType');
 if(raw.length!==dimensions)return reject('InputBound');
 const value=[];
 for(let index=0;index<dimensions;index++){
  const number=raw[index];if(typeof number!=='number'||!Number.isFinite(number))return reject('InputType','$['+index+']');
  value.push(number===0?0:number);
 }
 const canonical=encoder.encode(JSON.stringify(value));if(canonical.length>maxBytes)return reject('OutputBound');
 return Object.freeze({ok:true,value:Object.freeze(value),wire:canonical});
}
`;
 return coreFreeze({schema,schema_sha256:sha(JSON.stringify(schema)),source,codec_sha256:sha(source),type:{kind:'native-vector' as const,dimensions}});
}
