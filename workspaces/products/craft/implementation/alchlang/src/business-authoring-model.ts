import {createHash} from 'node:crypto';
import type {BusinessSpecData} from './business-authoring-protocol.js';
// Open questions are owned by the business-authoring implementation plan, B03 onward.
export class BusinessSourceRejected extends TypeError {
  constructor(readonly code:string, readonly source:string, readonly line:number, readonly column:number, message:string) {
    super(`${code} ${source}:${line}:${column}: ${message}`); this.name='BusinessSourceRejected';
  }
}
export function businessReject(code:string,source:string,line:number,column:number,message:string):never {
  throw new BusinessSourceRejected(code,source,line,column,message);
}
export const businessHash=(value:string|Buffer):string=>createHash('sha256').update(value).digest('hex');
/** Same recursive key sorting and UTF-8 semantics as Core canonicalJson. */
export function businessCanonical(value:unknown):string {
  if(Array.isArray(value))return '['+value.map(businessCanonical).join(',')+']';
  if(value!==null&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+businessCanonical((value as Record<string,unknown>)[k])).join(',')+'}';
  return JSON.stringify(value);
}
export function freezeBusinessData<T>(value:T,source:string):T {
  let nodes=0;
  const walk=(v:unknown,depth:number):void=>{
    if(++nodes>100000||depth>64)businessReject('BUSINESS_SOURCE_BUDGET',source,1,1,'plain-data capture budget exceeded');
    if(v&&typeof v==='object'){for(const child of Object.values(v))walk(child,depth+1);Object.freeze(v);}
  };walk(value,0);return value;
}
export function businessSourceKey(value:string):string {
  if(typeof value!=='string'||!value||value.length>4096||value.includes('\\')||value.includes(':')||value.includes('\0')||value.startsWith('/')||value.split('/').some(p=>!p||p==='.'||p==='..'||/[\x00-\x1f\x7f]/.test(p)))
    businessReject('BUSINESS_SOURCE_PATH',typeof value==='string'?value:'business.alch',1,1,'portable relative source key required');
  if(value.split('/').length>16)businessReject('BUSINESS_SOURCE_BUDGET',value,1,1,'path depth exceeded');
  return value;
}
/** Preserve backend camel-case splitting, punctuation collapsing and case folding. */
export const businessSymbol=(id:string):string=>id.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
export function businessIdentifier(id:string,source:string,line:number,column:number,portable=false):string {
  if(!(portable?/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/:/^[A-Za-z_][A-Za-z0-9_-]{0,127}$/).test(id))
    businessReject('BUSINESS_SYNTAX',source,line,column,'invalid identifier');
  // Underscore and camel-case spellings of the reserved prefix share backend identity.
  const normalized=businessSymbol(id).replace(/^craft-request-/, 'craftrequest-');
  if(normalized.startsWith('craftrequest-')||['constructor','prototype','__proto__'].includes(id.toLowerCase()))
    businessReject('BUSINESS_RESERVED',source,line,column,'reserved backend identifier');
  return id;
}
export function businessDataDigest(data:BusinessSpecData):string {
  const {source_spans:_spans,obligations:_obligations,...semantic}=data;
  const sort=<T extends {id:string}>(values:readonly T[]):T[]=>[...values].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
  const named=<T extends {name:string}>(values:readonly T[]):T[]=>[...values].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0);
  return businessHash(businessCanonical({...semantic,
    requirements:sort(data.requirements),entities:sort(data.entities).map(e=>({...e,fields:named(e.fields)})),definitions:sort(data.definitions),
    claims:sort(data.claims).map(c=>({...c,sorts:named(c.sorts),predicates:named(c.predicates),constants:named(c.constants)})),
    rules:sort(data.rules),operations:sort(data.operations),capabilities:sort(data.capabilities)}));
}
