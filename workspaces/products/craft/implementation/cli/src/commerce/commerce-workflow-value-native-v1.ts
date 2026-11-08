/** Exact checked-value projection from Workflow expression representation to
 * generated Entry input representation. The source schema supplies every
 * nested field and variant; callers cannot supply a conversion callback.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {types as host} from 'node:util';
import type {ValueSchemaV1,ValueTypeV1} from './commerce-data-v1.js';

export class CommerceWorkflowValueNativeErrorV1 extends Error {
 readonly code='InvalidObservation' as const;
 constructor(){super('InvalidObservation');this.name='CommerceWorkflowValueNativeErrorV1';}
}
const bad=():never=>{throw new CommerceWorkflowValueNativeErrorV1();};
const plain=(value:unknown):value is Record<string,unknown>=>
 Boolean(value&&typeof value==='object'&&!Array.isArray(value)&&!host.isProxy(value)&&
  [Object.prototype,null].includes(Object.getPrototypeOf(value as object)));
const fields=(value:unknown,expected:readonly string[]):Record<string,unknown>=>{
 if(!plain(value))bad();
 const keys=Reflect.ownKeys(value as object);
 if(keys.length!==expected.length||keys.some(key=>typeof key!=='string'||!expected.includes(key)))bad();
 for(const key of expected){
  const descriptor=Object.getOwnPropertyDescriptor(value,key);
  if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad();
 }
 return value as Record<string,unknown>;
};
const unicode=(value:string)=>Buffer.from(value,'utf8').toString('utf8')===value;

/** The projection validates before converting, so a typed source expression
 * cannot smuggle an extra JS property or a private `fields` wrapper through
 * the public generated Entry codec. */
export function projectCommerceWorkflowValueToNativeV1(
 value:unknown,type:ValueTypeV1,schema:ValueSchemaV1,
):unknown {
 const visit=(input:unknown,selected:ValueTypeV1,depth:number):unknown=>{
  if(depth>64)bad();
  switch(selected.kind){
   case 'scalar':
    if(selected.name==='Bool'){
     if(typeof input!=='boolean')bad();return input;
    }
    if(typeof input!=='bigint'||input<0n||input>18446744073709551615n)bad();
    return input;
   case 'string':
    if(typeof input!=='string'||!unicode(input)||
     Buffer.byteLength(input,'utf8')>selected.max_bytes||
     [...input].length>selected.max_scalars)bad();
    return input;
   case 'literal':if(input!==selected.value)bad();return input;
   case 'refinement':{
    const declared=schema.refinements.find(row=>row.name===selected.name);
    if(!declared||typeof input!=='string'||!unicode(input)||
     Buffer.byteLength(input,'utf8')<declared.min_utf8_bytes||
     Buffer.byteLength(input,'utf8')>declared.max_utf8_bytes||
     [...input].length<declared.min_unicode_scalars||
     [...input].length>declared.max_unicode_scalars||
     declared.pattern!==null&&declared.pattern!==undefined&&
      !new RegExp(declared.pattern,'u').test(input))bad();
    visit(input,declared!.carrier,depth+1);return input;
   }
   case 'record':{
    const declared=schema.records.find(row=>row.name===selected.name);
    if(!declared)bad();
    const members=declared!.fields,record=fields(input,Object.keys(members));
    return Object.freeze(Object.fromEntries(Object.entries(members).map(([name,member])=>
     [name,visit(record[name],member,depth+1)])));
   }
   case 'enum':case 'variant':{
    const name=selected.kind==='enum'?selected.name:
     (selected as Extract<ValueTypeV1,{kind:'variant'}>).enum_name,
     declared=schema.enums.find(row=>row.name===name);
    if(!declared)bad();
    const tag=typeof input==='string'?input:plain(input)?fields(input,['kind','fields']).kind:null;
    if(typeof tag!=='string'||selected.kind==='variant'&&tag!==selected.variant)bad();
    const choice=declared!.variants.find(row=>row.name===tag);
    if(!choice)bad();
    if(declared!.variants.every(row=>Object.keys(row.fields).length===0)){
     if(typeof input!=='string')bad();return input;
    }
    const wrapper=fields(input,['kind','fields']),members=choice!.fields,
     values=fields(wrapper.fields,Object.keys(members));
    if(Object.hasOwn(members,'kind'))bad();
    return Object.freeze(Object.fromEntries([['kind',tag],
     ...Object.entries(members).map(([field,member])=>
      [field,visit(values[field],member,depth+1)] as const)]));
   }
   case 'list':{
    if(!Array.isArray(input)||host.isProxy(input)||Object.getPrototypeOf(input)!==Array.prototype||
     input.length<selected.min_items||input.length>selected.max_items||
     Reflect.ownKeys(input).length!==input.length+1)bad();
    return Object.freeze((input as readonly unknown[]).map((item:unknown,index:number)=>{
     const descriptor=Object.getOwnPropertyDescriptor(input,String(index));
     if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad();
     return visit(item,selected.element,depth+1);
    }));
   }
   case 'optional':{
    if(plain(input)&&input.kind==='none'){
     fields(input,['kind']);return Object.freeze({kind:'none' as const});
    }
    const value=fields(input,['kind','value']);
    if(value.kind!=='some')bad();
    return Object.freeze({kind:'some' as const,value:visit(value.value,selected.element,depth+1)});
   }
   case 'outcome':return bad();
  }
 };
 return visit(value,type,0);
}
