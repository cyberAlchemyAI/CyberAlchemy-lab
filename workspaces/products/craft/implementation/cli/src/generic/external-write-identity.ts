/** Internal inert C11 tuple data; no dispatch, principal, command or journal authority.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {types} from 'node:util';
import {createHash} from 'node:crypto';
import {captureJson,canonicalJson,type Json} from '../profile-engine/contracts.js';
import {coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import type {GenericRootCommandTupleV1} from './transaction-data-v1.js';
import type {GenericChildCommandTupleV1,GenericExternalEffectTupleV1,GenericCausalIdentityLimitsV1} from './external-write-data-v1.js';
import type {GenericEventOperatorRootCommandTupleV2,GenericEventServiceRootCommandTupleV2,GenericEventExternalEffectTupleV2} from './event-data-v1.js';

type Tuple=GenericRootCommandTupleV1|GenericChildCommandTupleV1|GenericExternalEffectTupleV1|GenericEventOperatorRootCommandTupleV2|GenericEventServiceRootCommandTupleV2|GenericEventExternalEffectTupleV2;
type Row={readonly [key:string]:Json};
const at={path:'generic-causal-identity',start:0,end:0};
const ROOT='craft.generic-root-command/v1-candidate',ROOT_V2='craft.generic-root-command/v2-candidate',CHILD='craft.generic-child-command/v1-candidate',EFFECT='craft.generic-external-effect/v1-candidate',EFFECT_V2='craft.generic-external-effect/v2-candidate';
function invalid(detail:string):never{return fail('InvalidContract',at,detail);}
function bound(detail:string):never{return fail('ResourceLimit',at,detail);}
function row(value:Json,keys:readonly string[]):Row{
 if(value===null||typeof value!=='object'||Array.isArray(value))invalid('closed inert record required');
 const actual=Object.keys(value);if(actual.length!==keys.length||actual.some(k=>!keys.includes(k)))invalid('exact causal record fields required');return value as Row;
}
function integer(value:Json|undefined,min:number,max:number):number{
 if(typeof value!=='number'||!Number.isSafeInteger(value)||Object.is(value,-0)||value<min||value>max)invalid('bounded exact nonnegative integer required');return value;
}
function scalar(value:Json|undefined,min:number,max:number):string{
 if(typeof value!=='string')invalid('Unicode scalar string required');let count=0;
 for(let i=0;i<value.length;i++){const c=value.charCodeAt(i);if(c>=0xd800&&c<=0xdbff){const low=value.charCodeAt(++i);if(!(low>=0xdc00&&low<=0xdfff))invalid('unpaired high surrogate');}else if(c>=0xdc00&&c<=0xdfff)invalid('unpaired low surrogate');count++;}
 if(count<min||count>max)invalid('bounded Unicode scalar count required');return value;
}
function name(value:Json|undefined,property=false):string{
 const s=scalar(value,1,property?128:256);if(!(property?/^[A-Za-z_][A-Za-z0-9_]*$/:/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/).test(s))invalid('actual source-name spelling required');return s;
}
function limits(input:unknown):GenericCausalIdentityLimitsV1{
 const v=row(captureJson(input),['schema_version','max_child_depth','max_local_call_frames','max_site_occurrences','max_total_occurrences','max_tuple_bytes','wrapper_depth']);
 if(v.schema_version!=='craft.generic-causal-identity-limits/v1-candidate')invalid('exact causal limits version required');
 integer(v.max_child_depth,1,60);integer(v.max_local_call_frames,1,64);integer(v.max_site_occurrences,1,2147483647);integer(v.max_total_occurrences,1,2147483647);integer(v.max_tuple_bytes,1,1048576);integer(v.wrapper_depth,0,60);
 return v as unknown as GenericCausalIdentityLimitsV1;
}
/** Inspect only the parent spine before capture: cycles must never reach hashing.
 * Node's selected proxy detector precedes descriptor inspection. A plain data value
 * remains untrusted source metadata, regardless of this structural check. */
function parentSpine(input:unknown,max:number):void{
 const seen=new Set<object>();let value:unknown=input,links=0;
 while(value!==null&&typeof value==='object'){
  if(types.isProxy(value))invalid('proxy causal tuple rejected');if(seen.has(value))invalid('cyclic causal parent');seen.add(value);
  let proto:object|null,ds:PropertyDescriptorMap;
  try{proto=Object.getPrototypeOf(value);ds=Object.getOwnPropertyDescriptors(value);}catch{invalid('causal own-data inspection failed');}
  if(proto!==Object.prototype&&proto!==null)invalid('plain causal tuple required');
  for(const key of Reflect.ownKeys(ds)){const d=ds[key as string];if(typeof key!=='string'||!d?.enumerable||!Object.hasOwn(d,'value'))invalid('inert enumerable own data required');}
  const version=ds.schema_version?.value;if(version===ROOT||version===ROOT_V2)return;
  if(version!==CHILD&&version!==EFFECT&&version!==EFFECT_V2)invalid('exact causal tuple version required');
  if((version===EFFECT||version===EFFECT_V2)&&links!==0)invalid('effect cannot be a causal parent');
  if(version===CHILD&&++links>max)bound('selected child ancestor depth exceeded');
  if(!ds.parent||!Object.hasOwn(ds.parent,'value'))invalid('full own parent tuple required');value=ds.parent.value;
 }
 invalid('full ROOT parent required');
}
function site(value:Json|undefined):void{if(value===undefined)invalid('authored site data required');const v=row(value,['operation','binding']);name(v.operation);name(v.binding,true);}

/** Capture and derive a plain identity commitment. Returned data has no owner brand.
 * Site uniqueness/provenance and global occurrence accounting require the later
 * original source/dispatch owners; max_total_occurrences is not a stateless proof. */
export function deriveGenericCausalIdentityData(input:unknown,selectedLimits:unknown):Readonly<{tuple:Tuple;canonical_json:string;sha256:string;nodes:number;depth:number;child_ancestors:number;authority_effect:'none'}>{
 const selected=limits(selectedLimits);parentSpine(input,selected.max_child_depth);const captured=captureJson(input);let current:Json=captured,children=0,position=0,expectedRoot:string|null=null;
 while(true){
  if(current===null||typeof current!=='object'||Array.isArray(current))invalid('full causal tuple required');const version=(current as Row).schema_version;
  if(version===ROOT||version===ROOT_V2){
   if(expectedRoot&&version!==expectedRoot)invalid('causal tuple versions cannot be mixed');
   const r=row(current,['schema_version','application_namespace','service','principal','root_entry','client_key']);name(r.application_namespace);name(r.service);name(r.root_entry);
   const rawPrincipal=r.principal as Row|undefined;
   const principal=row(r.principal!,version===ROOT_V2&&rawPrincipal?.kind==='service'?['kind','service','subject','tenant']:['kind','subject','tenant']);
   if((version===ROOT?principal.kind!=='customer':principal.kind!=='operator'&&principal.kind!=='service')||principal.tenant!==null)invalid('exact versioned ROOT principal data required');
   if(principal.kind==='service')name(principal.service);
   const subject=scalar(principal.subject,1,256);if(subject.length>256)invalid('original ROOT subject UTF16 length bound exceeded');
   const key=scalar(r.client_key,1,128);if(Buffer.byteLength(key,'utf8')>128)invalid('original command key byte bound exceeded');
   if(Buffer.byteLength(canonicalJson(current),'utf8')>4096)bound('original ROOT canonical byte limit4096 exceeded');break;
  }
  const isChild=version===CHILD;if(!isChild&&!((version===EFFECT||version===EFFECT_V2)&&position===0))invalid('ROOT or CHILD parent required');
  if(isChild){if(expectedRoot===ROOT_V2)invalid('V1 child cannot extend V2 root');expectedRoot=ROOT;}
  else expectedRoot=version===EFFECT_V2?ROOT_V2:ROOT;
  const targets=isChild?['target_service','target_entry']:['interface_ref','contract_operation_ref'];
  const r=row(current,['schema_version','parent','site','local_calls',...targets,'ordinal']);site(r.site);for(const key of targets)name(r[key]);integer(r.ordinal,0,selected.max_site_occurrences-1);
  if(!Array.isArray(r.local_calls))invalid('local call spine array required');if(r.local_calls.length>selected.max_local_call_frames)bound('selected local call frame bound exceeded');
  for(const item of r.local_calls){const frame=row(item,['site','ordinal']);site(frame.site);integer(frame.ordinal,0,selected.max_site_occurrences-1);}
  if(isChild&&++children>selected.max_child_depth)bound('selected child ancestor depth exceeded');current=r.parent!;position++;
 }
 let nodes=0,depth=0;const pending:{value:Json;depth:number}[]=[{value:captured,depth:0}];
 while(pending.length){const item=pending.pop()!;nodes++;depth=Math.max(depth,item.depth);if(nodes>100000||item.depth+selected.wrapper_depth>64)bound('actual tuple nodes/wrapper depth exceeded');
  if(item.value!==null&&typeof item.value==='object')for(const value of Object.values(item.value))pending.push({value,depth:item.depth+1});
 }
 const canonical=canonicalJson(captured);if(Buffer.byteLength(canonical,'utf8')>selected.max_tuple_bytes)bound('selected full causal tuple UTF8 byte bound exceeded');
 return Object.freeze({tuple:captured as unknown as Tuple,canonical_json:canonical,sha256:createHash('sha256').update(canonical,'utf8').digest('hex'),nodes,depth,child_ancestors:children,authority_effect:'none'});
}

/** Full bytes remain the comparison authority; no caller-supplied digest is read. */
export function sameGenericCausalIdentityData(left:unknown,right:unknown,selectedLimits:unknown):boolean{
 const a=deriveGenericCausalIdentityData(left,selectedLimits),b=deriveGenericCausalIdentityData(right,selectedLimits);return a.canonical_json===b.canonical_json;
}
