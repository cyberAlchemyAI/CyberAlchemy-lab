import type {CompiledProjectGraph} from '../input/project-model.js';
import type {TypedType} from '../typed-operation/contracts.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
import {createMappingReference} from './reconciled-mapping-reference.js';
import {OperationReferenceUnsupported} from './reconciled-operation-reference.js';

const invalid=():never=>{throw new TypeError('OPERATION_REFERENCE_VALUE');};
/** Interpret fixture data, never execute fixture JavaScript or generated normalizers.
 * Invalid descriptors are rejected symbolically: no getter/coercion is invoked.
 */
export function captureOperationRecipe(recipe:FactRecipe,port:'input'|'read'='input'):any{
 let visits=0;
 const limit=():never=>{if(port==='read')throw new OperationReferenceUnsupported('OPERATION_REFERENCE_READ_CAPACITY');return invalid();};
 const walk=(r:FactRecipe,depth=0):any=>{
  if(++visits>(port==='input'?20000:65536)||depth>64)limit();
  if(r.tag==='bad'){
   const mode=r.mode!,field=r.field??'variant';
   if(['getter','symbol','non-enumerable','inherited','undefined','coercion','nan','infinity','collection-extra','collection-symbol','collection-inherited','sparse','collection-getter','collection-hidden'].includes(mode))invalid();
   if(mode==='null')return null;
   if(mode==='number')return 0;if(mode==='boolean')return false;if(mode==='string')return 'invalid';
   if(mode==='array')return [];if(mode==='object')return {};
   if(mode==='negative')return '-1';if(mode==='overflow')return '18446744073709551616';if(mode==='padded')return '01';
   if(mode==='unsafe')return 9007199254740992;if(mode==='fraction')return 1.5;
   // Wrapping changes descriptors, not the captured value's depth or visit budget.
   visits--;const v=walk(r.base!,depth);
   if(mode==='frozen'||mode==='null-prototype')return v;
   if(mode==='duplicate'){if(!Array.isArray(v)||v.length===0)invalid();if(port==='input'&&v.length>=1024)invalid();return [...v,v[0]];}
   if(mode==='extra'){let key='extra';while(Object.hasOwn(v,key))key+='_';return {...v,[key]:true};}
   if(mode==='missing-field'){delete v[field];return v;}
   if(mode==='missing-variant'){delete v.variant;return v;}
   if(mode==='unknown-variant')return {...v,variant:'__semantic_unknown__'};
   if(mode==='missing-payload'){delete v.payload;return v;}
   if(mode==='surplus-payload')return {...v,payload:null};
   throw new OperationReferenceUnsupported('OPERATION_REFERENCE_RECIPE:'+mode);
  }
  if(r.tag==='null')return null;
  if(r.tag==='scalar'){
   const v=r.format==='bigint'?BigInt(r.value as string):r.format==='number'?Number(r.value):r.value;
   return typeof v==='string'||typeof v==='boolean'||typeof v==='bigint'||typeof v==='number'&&Number.isFinite(v)?v:invalid();
  }
  if(r.tag==='named'){visits--;return walk(r.input!,depth);}
  if(r.tag==='list'||r.tag==='set'){if(port==='input'&&r.items!.length>1024)invalid();return r.items!.map(v=>walk(v,depth+1));}
  if(r.tag==='sum')return {variant:walk({tag:'scalar',value:r.variant!},depth+1),...(r.payload?{payload:walk(r.payload,depth+1)}:{})};
  if(r.tag==='fields'||r.tag==='record'){
   const entries=Object.entries(r.fields!);if(port==='input'&&entries.length>2048)invalid();
   return Object.fromEntries(entries.map(([k,v])=>[k,walk(v,depth+1)]));
  }
  throw new OperationReferenceUnsupported('OPERATION_REFERENCE_RECIPE:'+r.tag);
 };
 const captured=walk(recipe);let capturedVisits=0;
 const check=(v:any,depth=0):void=>{
  if(++capturedVisits>(port==='input'?20000:65536)||depth>64)limit();
  if(v===null||typeof v!=='object')return;
  if(port==='input'){if(Array.isArray(v)){if(v.length>1024)invalid();}else if(Object.keys(v).length>2048)invalid();}
  Object.values(v).forEach(x=>check(x,depth+1));
 };check(captured);return captured;
}
export function operationReferenceFields(v:any,allowed:readonly string[],required=allowed):Record<string,any>{
 if(v===null||typeof v!=='object'||Array.isArray(v))invalid();
 if(Object.keys(v).some(k=>!allowed.includes(k))||required.some(k=>!Object.hasOwn(v,k)))invalid();return v;
}
/** Mathematical typed normalization uses source declarations, not emitted provider code. */
export function createOperationValueReference(graph:CompiledProjectGraph){
 const reference=createMappingReference(graph);
 const normalize=(t:TypedType,v:any,depth=0):any=>{
  if(depth>64)throw new OperationReferenceUnsupported('OPERATION_REFERENCE_TYPE_DEPTH');
  if(t.kind==='scalar'){
   if(t.name==='String')return typeof v==='string'?v:invalid();
   if(t.name==='Bool')return typeof v==='boolean'?v:invalid();
   if(typeof v==='number'&&!Number.isSafeInteger(v)||typeof v==='string'&&!/^(?:0|[1-9][0-9]*)$/.test(v)||!['bigint','number','string'].includes(typeof v))invalid();
   const n=BigInt(v);return n>=0n&&n<=18446744073709551615n?n:invalid();
  }
  if(t.kind==='optional')return v===null?null:normalize(t.element,v,depth+1);
  if(t.kind==='list'||t.kind==='set'){
   if(!Array.isArray(v))invalid();const values:any[]=(v as any[]).map(x=>normalize(t.element,x,depth+1));
   if(t.kind==='list')return values;
   const keys=values.map(x=>reference.key(t.element,x));if(new Set(keys).size!==keys.length)invalid();
   return values.map((v,i)=>({v,k:keys[i]!})).sort((a,b)=>a.k<b.k?-1:a.k>b.k?1:0).map(x=>x.v);
  }
  if(t.kind==='sum'){
   operationReferenceFields(v,['variant','payload'],['variant']);const variant=t.variants.find(x=>x.name===v.variant);
   if(!variant||!!variant.payload!==Object.hasOwn(v,'payload'))invalid();
   return {variant:variant!.name,...(variant!.payload?{payload:normalize(variant!.payload,v.payload,depth+1)}:{})};
  }
  const d=reference.get(t);if(d.kind==='Enum')return normalize({kind:'sum',variants:d.variants},v,depth+1);
  operationReferenceFields(v,d.properties.map(p=>p.name),d.properties.filter(p=>p.type.kind!=='optional').map(p=>p.name));
  return Object.fromEntries(d.properties.map(p=>[p.name,normalize(p.type as TypedType,Object.hasOwn(v,p.name)?v[p.name]:null,depth+1)]));
 };
 return {...reference,normalize};
}

/** Event fields are not UInt64 domain fields: integer is signed 64-bit. */
export function operationReferenceEvent(body:any,input:any,clock:()=>unknown,referenceScalar:(selector:string)=>'String'|'UInt64'=()=> 'String'):any{
 const field=(f:any,v:any):any=>{
  if(f.type_ref.kind==='reference'){
   if(referenceScalar(f.type_ref.selector)==='String')return typeof v==='string'&&v.length?v:invalid();
   if(typeof v==='number'&&!Number.isSafeInteger(v)||typeof v==='string'&&!/^(?:0|[1-9][0-9]*)$/.test(v)||!['bigint','number','string'].includes(typeof v))invalid();
   const n=BigInt(v);return n>=0n&&n<=18446744073709551615n?n:invalid();
  }
  const type=f.type_ref.name;
  if(type==='string')return typeof v==='string'?v:invalid();
  if(type==='uuid'||type==='timestamp')return typeof v==='string'&&v.length?v:invalid();
  if(type==='boolean')return typeof v==='boolean'?v:invalid();
  if(type==='decimal')return typeof v==='number'&&Number.isFinite(v)?v:invalid();
  if(type==='integer'){
   if(typeof v==='number'&&!Number.isSafeInteger(v)||typeof v==='string'&&!/^(?:0|-[1-9][0-9]*|[1-9][0-9]*)$/.test(v)||!['bigint','number','string'].includes(typeof v))invalid();
   const n=BigInt(v);return n>=-9223372036854775808n&&n<=9223372036854775807n?n:invalid();
  }
  throw new OperationReferenceUnsupported('OPERATION_REFERENCE_EVENT_TYPE:'+type);
 };
 const generated=body.occurred_at_policy==='generated';
 operationReferenceFields(input,generated?['occurrence','payload']:['occurrence','payload','occurredAt']);
 const occurrence=operationReferenceFields(input.occurrence,[body.occurrence_id.field_id]);
 const payload=operationReferenceFields(input.payload,body.payload.map((f:any)=>f.field_id),body.payload.filter((f:any)=>f.required).map((f:any)=>f.field_id));
 const identity=field(body.occurrence_id,occurrence[body.occurrence_id.field_id]);
 const values=Object.fromEntries(body.payload.filter((f:any)=>Object.hasOwn(payload,f.field_id)).map((f:any)=>[f.field_id,field(f,payload[f.field_id])]));
 const occurredAt=generated?clock():input.occurredAt;if(typeof occurredAt!=='string'||occurredAt.length===0)invalid();
 return {type:body.event_type,version:body.version,occurrence:{[body.occurrence_id.field_id]:identity},payload:values,occurredAt};
}
