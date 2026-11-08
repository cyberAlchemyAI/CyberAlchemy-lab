/** Direct TypeScript expression emission from genuine original checked v2 data.
 * No serialized AST interpreter, private import or caller formula is emitted.
 * Open Questions: docs/COMMERCE-COMPUTATION-RUNTIME-V2.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {types as host} from 'node:util';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertGenericComputationDomainOwner,type GenericComputationDomainOwner,type GenericComputationDomainHandle} from '../generic/computation-domain.js';
import {createGenericPureCallOwner} from '../generic/pure-call-owner.js';
import type {GenericExprV1} from '../generic/computation-data-v1.js';
import {createCommerceValueKernel} from './commerce-computation-kernel.js';
import type {ExprV1} from './commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-computation-kernel'+ext,'commerce-computation-domain'+ext,'commerce-computation-environment'+ext,'../generic/computation-domain'+ext,'../generic/pure-call-owner'+ext]);
const json=(v:unknown)=>JSON.stringify(v);
// Fixed typed implementation template. Source correspondence is checked against
// commerce-computation-kernel.ts before this component can be qualified.
// It remains available when the emitter itself is built JavaScript.
function kernelTypeScriptSource(generic:boolean):string{return String.raw`function createCommerceValueKernel(spec:any,host:any,invariant:any){
${generic?" const generic=spec.schema_version==='craft.generic-computation/v1-candidate';\n":''} const limits=spec.limits,records=new Map<string,any>(spec.values.records.map((r:any)=>[r.name,r])),enums=new Map<string,any>(spec.values.enums.map((r:any)=>[r.name,r])),refinements=new Map<string,any>(spec.values.refinements.map((r:any)=>[r.name,r]));
 const encoder=new TextEncoder(),max=18446744073709551615n;
 class Fault extends Error {error:any;actions:any[]=[];constructor(code:string,s:any){super(code);this.error={code,expression_path:s.p,index_path:[...s.i],call_path:[...s.c]};}}
 const site=(p:string,i:number[]=[],c:string[]=[])=>({p,i,c});
 const fail=(code:string,s:any):never=>{throw new Fault(code,s);};
 const fresh=(observe=false)=>({used:0,phase:'input-validation',observe,decisions:[] as any[],observation_status:'complete',pending:[] as any[],checked:new WeakMap<object,Map<string,number>>(),sizes:new WeakMap<object,Map<string,{length:number;size:number}>>(),strings:new Map<string,Set<string>>(),stringSizes:new Map<string,Map<string,number>>(),validationDepth:0});
 const charge=(a:any,s:any,count=1)=>{if(count<0||!Number.isSafeInteger(count))fail('InvalidContract',s);if(count>limits.fuel-a.used){a.used=limits.fuel;fail('ResourceLimit',s);}a.used+=count;};
 // One byte-work unit covers at most 32 UTF8 bytes; expression/call/iteration work remains one unit each.
 const byteWork=(a:any,s:any,bytes:number)=>charge(a,s,Math.ceil(bytes/32));
 const scalar=(v:string)=>{for(let i=0;i<v.length;i++){const n=v.charCodeAt(i);if(n>=0xd800&&n<=0xdbff){const next=v.charCodeAt(++i);if(!(next>=0xdc00&&next<=0xdfff))return false;}else if(n>=0xdc00&&n<=0xdfff)return false;}return true;};
 const utf8=(v:string)=>encoder.encode(v).length;
 const quote=(v:string)=>'"'+v.replace(/["\\\u0000-\u001f]/g,(c:string)=>c==='"'?'\\"':c==='\\'?'\\\\':'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+'"';
 const canonical=(v:any):string=>v===null?'null':typeof v==='bigint'?quote(String(v)):typeof v==='boolean'?String(v):typeof v==='string'?quote(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>quote(k)+':'+canonical(v[k])).join(',')+'}';
 const key=(t:any)=>JSON.stringify(t),object=(v:any,s:any)=>{if(!v||typeof v!=='object'||Array.isArray(v)||host.isProxy(v))fail('InputType',s);return v;};
 const closed=(v:any,keys:string[],s:any)=>{object(v,s);const got=Object.keys(v);if(got.length!==keys.length||keys.some(k=>!Object.hasOwn(v,k)))fail('InputType',s);};
 const primitiveString=(v:any,t:any,a:any,s:any)=>{if(typeof v!=='string')fail('InputType',s);if(!scalar(v))fail('InvalidUnicode',s);const bytes=utf8(v),scalars=[...v].length;byteWork(a,s,bytes);if(bytes>t.max_bytes||scalars>t.max_scalars)fail('InputBound',s);return v;};
 const finitePattern=(pattern:string,value:string,a:any,s:any)=>{
  const atoms:any[]=[];let pos=1;while(pos<pattern.length-1){const chars=new Set<string>();if(pattern[pos]==='['){const end=pattern.indexOf(']',pos+1),body=pattern.slice(pos+1,end);for(let i=0;i<body.length;i++){if(body[i+1]==='-'&&i+2<body.length){for(let n=body.charCodeAt(i);n<=body.charCodeAt(i+2);n++){charge(a,s);chars.add(String.fromCharCode(n));}i+=2;}else chars.add(body[i]!);}pos=end+1;}else chars.add(pattern[pos++]!);let low=1,high=1;if(pattern[pos]==='{'){const q=/^\{([0-9]+)(?:,([0-9]+))?\}/.exec(pattern.slice(pos))!;low=Number(q[1]);high=Number(q[2]??q[1]);pos+=q[0].length;}atoms.push({chars,low,high});}
  const cs=[...value];let positions=new Set<number>([0]);for(const atom of atoms){const next=new Set<number>();for(const start of positions){charge(a,s);if(!atom.low)next.add(start);let n=0;while(n<atom.high&&start+n<cs.length){charge(a,s);if(!atom.chars.has(cs[start+n]!))break;n++;if(n>=atom.low)next.add(start+n);}}positions=next;if(!positions.size)return false;}return positions.has(cs.length);
 };
 const variant=(v:any,t:any,s:any)=>{const def=enums.get(t.kind==='variant'?t.enum_name:t.name);if(!def)fail('InvalidContract',s);const simple=def.variants.every((x:any)=>!Object.keys(x.fields).length),name=simple?v:object(v,s).kind,x=def.variants.find((x:any)=>x.name===name);if(!x||t.kind==='variant'&&x.name!==t.variant)fail('InputType',s);if(simple&&typeof v!=='string')fail('InputType',s);if(!simple){closed(v,['kind','fields'],s);closed(v.fields,Object.keys(x.fields),s);}return {def,x,simple,fields:simple?{}:v.fields};};
 const schemaHeights=new Map<string,number>();
 const checkSchema=(t:any,active=new Set<string>(),depth=0):number=>{
  const typeKey=key(t),prior=schemaHeights.get(typeKey);if(prior!==undefined){if(depth+prior>32)fail('UnsupportedCapability',site('$.values'));return prior;}
  if(depth>32||active.has(typeKey))fail('UnsupportedCapability',site('$.values'));const next=new Set(active);next.add(typeKey);let height=0;
  const child=(type:any)=>{height=Math.max(height,1+checkSchema(type,next,depth+1));};
  if(t.kind==='optional'){if(t.element.kind==='optional')fail('UnsupportedCapability',site('$.values'));child(t.element);}
  else if(t.kind==='list')child(t.element);
  else if(t.kind==='outcome'){child(t.state);child(t.intent);}
  else if(t.kind==='record'){const record=records.get(t.name);if(!record)fail('InvalidContract',site('$.values'));for(const f of Object.values(record.fields))child(f);}
  else if(t.kind==='enum'||t.kind==='variant'){const definition=enums.get(t.kind==='variant'?t.enum_name:t.name);if(!definition)fail('InvalidContract',site('$.values'));for(const x of definition.variants)for(const f of Object.values(x.fields))child(f);}
  schemaHeights.set(typeKey,height);return height;
 };
 const assertBoundary=()=>{for(const b of spec.inputs)checkSchema(b.type);checkSchema(spec.result);};
 const validate=(v:any,t:any,a:any,s:any,depth=0):any=>{
  if(depth>32||a.validationDepth>=64)fail('ResourceLimit',s);const k=key(t),length=Array.isArray(v)?v.length:-1;
  if(v&&typeof v==='object'&&a.checked.get(v)?.get(k)===length)return v;
  if(typeof v==='string'&&a.strings.get(k)?.has(v))return v;
  charge(a,s);a.validationDepth++;
  try{
   switch(t.kind){
    case'scalar':if(t.name==='Bool'){if(typeof v!=='boolean')fail('InputType',s);}else if(typeof v!=='bigint'||v<0n||v>max)fail('InputType',s);break;
    case'literal':if(v!==t.value)fail('InputType',s);primitiveString(v,{max_bytes:utf8(t.value),max_scalars:[...t.value].length},a,s);break;
    case'string':primitiveString(v,t,a,s);break;
    case'refinement':{const r=refinements.get(t.name);if(!r)fail('InvalidContract',s);primitiveString(v,r.carrier,a,s);if(utf8(v)<r.min_utf8_bytes||[...v].length<r.min_unicode_scalars||r.pattern!==null&&!finitePattern(r.pattern,v,a,s))fail('InputType',s);}break;
    case'optional':object(v,s);if(v.kind==='none')closed(v,['kind'],s);else if(v.kind==='some'){closed(v,['kind','value'],s);validate(v.value,t.element,a,s,depth+1);}else fail('InputType',s);break;
    case'list':if(!Array.isArray(v)||host.isProxy(v))fail('InputType',s);if(v.length<t.min_items||v.length>t.max_items||v.length>limits.max_items)fail('InputBound',s);for(let i=0;i<v.length;i++)validate(v[i],t.element,a,site(s.p+'['+i+']',s.i,s.c),depth+1);break;
    case'record':{const r=records.get(t.name);if(!r)fail('InvalidContract',s);closed(v,Object.keys(r.fields),s);for(const [name,type]of Object.entries(r.fields))validate(v[name],type,a,site(s.p+'.'+name,s.i,s.c),depth+1); }break;
    case'enum':case'variant':{const x=variant(v,t,s);for(const [name,type]of Object.entries(x.x.fields))validate(x.fields[name],type,a,site(s.p+'.fields.'+name,s.i,s.c),depth+1);}break;
    case'outcome':closed(v,['tag','state','intents','machine','branch','reason'],s);if(!['transition','stayed','rejected'].includes(v.tag)||typeof v.machine!=='string'||typeof v.branch!=='string'||typeof v.reason!=='string')fail('InputType',s);validate(v.state,t.state,a,s,depth+1);validate(v.intents,{kind:'list',element:t.intent,min_items:0,max_items:t.max_intents},a,s,depth+1);for(const name of ['machine','branch','reason'])primitiveString(v[name],{max_bytes:256,max_scalars:256},a,s);break;
    default:fail('UnsupportedCapability',s);
   }
   if(v&&typeof v==='object'){let m=a.checked.get(v);if(!m){m=new Map();a.checked.set(v,m);}m.set(k,length);}else if(typeof v==='string'&&a.strings.size<4096){let set=a.strings.get(k);if(!set){set=new Set();a.strings.set(k,set);}if(set.size<4096)set.add(v);}
   // Structural validation precedes semantic constraints; a predicate can inspect its own already-checked argument.
   if(t.kind==='record'&&!invariant.record(t.name,v,a,s))fail('InputType',s);
   if(t.kind==='list')for(const p of spec.values.collection_predicates)if(key(p.type)===k&&!invariant.predicate(p.rule,v,a,s${generic?',p.type':''}))fail('InputType',s);
   return v;
  }finally{a.validationDepth--;}
 };
 const wire=(v:any,t:any,a:any,s:any,depth=0):any=>{
  if(depth>32)fail('ResourceLimit',s);switch(t.kind){case'scalar':return t.name==='UInt64'?String(v):v;case'string':case'literal':case'refinement':return v;
   case'optional':return v.kind==='none'?null:wire(v.value,t.element,a,s,depth+1);
   case'list':return v.map((x:any)=>wire(x,t.element,a,s,depth+1));
   case'record':{const out=Object.create(null);for(const [name,type]of Object.entries(records.get(t.name).fields))out[name]=wire(v[name],type,a,s,depth+1);return out;}
   case'enum':case'variant':{const x=variant(v,t,s);if(x.simple)return x.x.wire;const fields=Object.create(null);for(const [name,type]of Object.entries(x.x.fields))fields[name]=wire(x.fields[name],type,a,s,depth+1);return {tag:x.x.wire,fields};}
   case'outcome':return {...v,state:wire(v.state,t.state,a,s,depth+1),intents:v.intents.map((x:any)=>wire(x,t.intent,a,s,depth+1))};default:return fail('UnsupportedCapability',s);}
 };
 const size=(v:any,t:any,a:any,s:any):number=>{
  const typeKey=key(t),length=Array.isArray(v)?v.length:-1,prior=v&&typeof v==='object'?a.sizes.get(v)?.get(typeKey):undefined;
  if(prior&&prior.length===length)return prior.size;
  const stringPrior=typeof v==='string'?a.stringSizes.get(typeKey)?.get(v):undefined;if(stringPrior!==undefined)return stringPrior;
  let n:number;
  // Only internal append-only builders can change a list. Reuse its checked prefix rather than walking it again.
  if(Array.isArray(v)&&t.kind==='list'&&prior&&length===prior.length+1){const extra=utf8(canonical(wire(v[length-1],t.element,a,s)))+(prior.length?1:0);byteWork(a,s,extra);n=prior.size+extra;}
  else{n=utf8(canonical(wire(v,t,a,s)));byteWork(a,s,n);}
  if(v&&typeof v==='object'){let m=a.sizes.get(v);if(!m){m=new Map();a.sizes.set(v,m);}m.set(typeKey,{length,size:n});}
  else if(typeof v==='string'&&a.stringSizes.size<4096){let m=a.stringSizes.get(typeKey);if(!m){m=new Map();a.stringSizes.set(typeKey,m);}if(m.size<4096)m.set(v,n);}
  return n;
 };
 const checkpoint=(v:any,t:any,a:any,s:any)=>{validate(v,t,a,s);if(size(v,t,a,s)>limits.max_value_bytes)fail('OutputBound',s);return v;};
 const partial=(v:any,t:any,a:any,s:any)=>{if(!Array.isArray(v)||v.length>t.max_items||v.length>limits.max_items)fail('OutputBound',s);if(size(v,t,a,s)>limits.max_value_bytes)fail('OutputBound',s);return v;};
 const decode=(v:any,t:any,a:any,s:any,depth=0):any=>{
  if(depth>32)fail('InputBound',s);charge(a,s);let out:any;
  switch(t.kind){case'scalar':if(t.name==='Bool')out=v;else{if(typeof v!=='string'||v.length>20||!/^(0|[1-9][0-9]*)$/.test(v))fail('InputType',s);out=BigInt(v);if(out>max)fail('InputBound',s);}break;
   case'string':case'literal':case'refinement':out=v;break;
   case'optional':out=v===null?{kind:'none'}:{kind:'some',value:decode(v,t.element,a,s,depth+1)};break;
   case'list':if(!Array.isArray(v))fail('InputType',s);if(v.length>t.max_items||v.length>limits.max_items)fail('InputBound',s);out=v.map((x:any,i:number)=>decode(x,t.element,a,site(s.p+'['+i+']',s.i,s.c),depth+1));break;
   case'record':{const r=records.get(t.name);closed(v,Object.keys(r.fields),s);out=Object.create(null);for(const [name,type]of Object.entries(r.fields))out[name]=decode(v[name],type,a,site(s.p+'.'+name,s.i,s.c),depth+1);}break;
   case'enum':case'variant':{const def=enums.get(t.kind==='variant'?t.enum_name:t.name),simple=def.variants.every((x:any)=>!Object.keys(x.fields).length);let tag:any;if(simple)tag=v;else{closed(v,['tag','fields'],s);tag=v.tag;}const x=def.variants.find((x:any)=>x.wire===tag);if(!x)fail('InputType',s);if(simple)out=x.name;else{closed(v.fields,Object.keys(x.fields),s);const fields=Object.create(null);for(const [name,type]of Object.entries(x.fields))fields[name]=decode(v.fields[name],type,a,s,depth+1);out={kind:x.name,fields};}}break;
   case'outcome':closed(v,['tag','state','intents','machine','branch','reason'],s);out={...v,state:decode(v.state,t.state,a,s,depth+1),intents:decode(v.intents,{kind:'list',element:t.intent,min_items:0,max_items:t.max_intents},a,s,depth+1)};break;
   default:fail('UnsupportedCapability',s);
  }return checkpoint(out,t,a,s);
 };
 const parse=(json:string)=>{
  let at=0;const bad=():never=>fail('InputType',site('$.inputs'));const ws=()=>{while(/[\x20\t\r\n]/.test(json[at]??'!'))at++;};
  const string=()=>{const start=at++;while(at<json.length){const ch=json[at++];if(ch==='"'){let v:string;try{v=JSON.parse(json.slice(start,at));}catch{return bad();}if(!scalar(v))fail('InvalidUnicode',site('$.inputs'));return v;}if(ch==='\\')at++;}return bad();};
  const value=(depth:number):any=>{if(depth>32)fail('InputBound',site('$.inputs'));ws();const ch=json[at];if(ch==='"')return string();if(ch==='{'){at++;ws();const out=Object.create(null);if(json[at]==='}'){at++;return out;}for(;;){ws();if(json[at]!=='"')return bad();const name=string();if(Object.hasOwn(out,name))return bad();ws();if(json[at++]!==':')return bad();out[name]=value(depth+1);ws();const next=json[at++];if(next==='}')return out;if(next!==',')return bad();}}if(ch==='['){at++;ws();const out:any[]=[];if(json[at]===']'){at++;return out;}for(;;){out.push(value(depth+1));ws();const next=json[at++];if(next===']')return out;if(next!==',')return bad();}}const m=/^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(json.slice(at));if(!m)return bad();at+=m[0].length;return JSON.parse(m[0]);};
  const out=value(0);ws();if(at!==json.length)return bad();return out;
 };
 const input=(bytes:any,a:any)=>{
  assertBoundary();const s=site('$.inputs');if(host.isProxy(bytes)||!host.isUint8Array(bytes))fail('InputType',s);let copied:Uint8Array;
  try{const prototype=Object.getPrototypeOf(Uint8Array.prototype),get=(name:string)=>Object.getOwnPropertyDescriptor(prototype,name)!.get!.call(bytes),length=get('byteLength');if(length>limits.max_input_bytes)fail('InputBound',s);if(host.isSharedArrayBuffer(get('buffer')))fail('InputType',s);byteWork(a,s,length);const view=new Uint8Array(get('buffer'),get('byteOffset'),length);copied=new Uint8Array(length);Uint8Array.prototype.set.call(copied,view);}catch(error){if(error instanceof Fault)throw error;return fail('InputType',s);}
  let json:string;try{json=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(copied);}catch{return fail('InvalidUnicode',s);}const raw=parse(json);closed(raw,spec.inputs.map((b:any)=>b.name),s);const env=Object.create(null);for(const b of spec.inputs)env[b.name]=decode(raw[b.name],b.type,a,site('$.inputs.'+b.name));return env;
 };
 const output=(v:any,a:any)=>{const s=site('$.expression');checkpoint(v,spec.result,a,s);const json=canonical(wire(v,spec.result,a,s));const bytes=encoder.encode(json);byteWork(a,s,bytes.length);if(bytes.length>limits.max_output_bytes)fail('OutputBound',s);return bytes;};
 const equal=(left:any,right:any,a:any,s:any):boolean=>{charge(a,s);if(left===right${generic?"&&(!generic||left===null||typeof left!=='object')":''}){if(typeof left==='string')byteWork(a,s,utf8(left));return true;}if(typeof left!==typeof right)return false;if(typeof left==='string'){byteWork(a,s,utf8(left)+utf8(right));return false;}if(!left||!right||typeof left!=='object')return false;if(Array.isArray(left)!==Array.isArray(right))return false;const lk=Object.keys(left),rk=Object.keys(right);${generic?'if(generic&&!Array.isArray(left)){lk.sort();rk.sort();}':''}if(lk.length!==rk.length)return false;for(const k of lk)if(!Object.hasOwn(right,k)||!equal(left[k],right[k],a,s))return false;return true;};
 const lexical=(left:string,right:string)=>{const a=[...left],b=[...right];for(let i=0;i<Math.min(a.length,b.length);i++){const x=a[i]!.codePointAt(0)!,y=b[i]!.codePointAt(0)!;if(x!==y)return x<y?-1:1;}return a.length-b.length;};
 const compare=(left:any,right:any,mode:string,a:any,s:any):number=>{charge(a,s);if(mode==='numeric')return left===right?0:left<right?-1:1;byteWork(a,s,utf8(left)+utf8(right));if(mode==='lexical')return lexical(left,right);const aa=left.match(/[0-9]+|[^0-9]+/g)??[],bb=right.match(/[0-9]+|[^0-9]+/g)??[];for(let i=0;i<Math.min(aa.length,bb.length);i++){const x=aa[i]!,y=bb[i]!;let n;if(/^[0-9]+$/.test(x)&&/^[0-9]+$/.test(y)){const xx=x.replace(/^0+/,'')||'0',yy=y.replace(/^0+/,'')||'0';n=xx.length-yy.length||lexical(xx,yy)||x.length-y.length;}else n=lexical(x,y);if(n)return n<0?-1:1;}return aa.length-bb.length;};
 const select=(a:any,s:any,policy:string,branch:string,calculation:string,path:string)=>{const row={policy,branch,calculation,expression_path:s.p,index_path:[...s.i],call_path:[...s.c],invocation_entered:false};if(a.observe&&a.decisions.length<100&&utf8(JSON.stringify([...a.decisions,row]))<=65536)a.decisions.push(row);else if(a.observe)a.observation_status='truncated';const pending={path,row};a.pending.push(pending);return pending;};
 const enter=(a:any,s:any)=>{charge(a,s);if(s.c.length>limits.max_call_depth)fail('ResourceLimit',s);for(const p of a.pending)if(p.path===s.p)p.row.invocation_entered=true;};
 const annotate=(error:any,declaration:string,action:any)=>{if(error instanceof Fault&&action)error.actions.push({declaration,action});return error;};
 const observation=(a:any,result:any)=>({result,evaluation_phase:a.phase,declared_actions:result.ok?[]:(a.failureActions??[]),policy_decisions:a.decisions,observation_status:a.observation_status});
 const failure=(error:any,a:any)=>{if(!(error instanceof Fault))throw error;a.failureActions=error.actions;return {ok:false,error:error.error,fuel_used:a.used};};
 return {assertBoundary,fresh,site,fail,charge,byteWork,checkpoint,partial,decode,wire,input,output,equal,compare,select,enter,annotate,observation,failure,records,enums,refinements,variant,max};
}${generic?'':'\n'}`;}
export function compileCommerceComputationTypeScript(owner:CommerceComputationDomainOwner,handle:CommerceComputationDomainHandle){
 return compileChecked({kind:'commerce',owner,handle});
}
export function compileGenericComputationTypeScript(owner:GenericComputationDomainOwner,handle:GenericComputationDomainHandle){return compileChecked({kind:'generic',owner,handle});}
type Subject={kind:'commerce';owner:CommerceComputationDomainOwner;handle:CommerceComputationDomainHandle}|{kind:'generic';owner:GenericComputationDomainOwner;handle:GenericComputationDomainHandle};
function compileChecked(subject:Subject){
 const current=()=>{pin.assertCurrent();if(subject.kind==='generic'){assertGenericComputationDomainOwner(subject.owner);subject.owner.assertCurrent(subject.handle);}else{assertCommerceComputationDomainOwner(subject.owner);subject.owner.assertCurrent(subject.handle);}};current();
 const inspection=subject.kind==='generic'?subject.owner.inspect(subject.handle):subject.owner.inspect(subject.handle),generic=subject.kind==='generic',callOwner=subject.kind==='generic'?createGenericPureCallOwner(subject.owner,subject.handle):null,c=inspection.contract,slots=inspection.environment.expressions,indices=new Map(slots.map((slot,i)=>[slot.path,i])),functions=new Map(c.functions.map((f,i)=>[f.name,i])),policies=new Map(inspection.environment.policy_actions.map(s=>[s.path,s]));
 // Boundary eligibility is checked before returning any generated source.
 createCommerceValueKernel(c,host,{}).assertBoundary();
 const at=(p:string):GenericExprV1=>{let value:any=c;for(const key of p.match(/[^.[\]]+/g)!.slice(1))value=value[key];return value;};
 const callBindings:Readonly<Record<string,unknown>>[]=[];
 const emitted=slots.map((slot,index)=>{
  const e=at(slot.path),p=slot.path;
  const sub=(key:string,en='env',ix='i')=>`e${indices.get(p+'.'+key)}(a,${en},${ix},c,r)`,scope=(bindings:string)=>`Object.assign(Object.create(null),env,${bindings})`,point=(ix='i')=>`k.site(${json(p)},${ix},c)`,check=(v:string,ix='i')=>`k.checkpoint(${v},T[${index}],a,${point(ix)})`,partial=(v:string,ix='i')=>`k.partial(${v},T[${index}],a,${point(ix)})`;
  const fields=(values:Readonly<Record<string,GenericExprV1>>,variable:string)=>Object.keys(values).map(name=>`${variable}[${json(name)}]=${sub('fields.'+name)};`).join('');
  let body:string;
  switch(e.op){
   case'literal':body=`v=${e.type.kind==='scalar'&&e.type.name==='UInt64'?String(e.value)+'n':json(e.value)};`;break;
   case'validate_refinement':body=`v=${sub('value')};k.checkpoint(v,${json({kind:'refinement',name:e.refinement})},a,s);`;break;
   case'var':body=`v=env[${json(e.name)}];`;break;
   case'field':body=`v=${sub('value')}${slots[indices.get(p+'.value')!]!.type.kind==='variant'?'.fields':''}[${json(e.field)}];`;break;
   case'record':body=`v=Object.create(null);${fields(e.fields,'v')}`;break;
   case'record_update':body=`v=Object.assign(Object.create(null),${sub('value')});${fields(e.fields,'v')}`;break;
   case'enum_value':{const simple=c.values.enums.find(x=>x.name===e.type_name)!.variants.every(x=>!Object.keys(x.fields).length);body=simple?`v=${json(e.variant)};`:`const fs=Object.create(null);${fields(e.fields,'fs')}v={kind:${json(e.variant)},fields:fs};`;}break;
   case'list':body=`v=[${e.items.map((_,j)=>sub('items['+j+']')).join(',')}];`;break;
   case'append':body=`const source=${sub('source')},item=${sub('item')};k.checkpoint(item,${json(e.list_type.element)},a,s);if(source.length>=${Math.min(e.list_type.max_items,c.limits.max_items)})k.fail('OutputBound',s);k.charge(a,s,source.length+1);v=[...source,item];${partial('v')};`;break;
   case'none':body="v={kind:'none'};";break;
   case'some':body=`v={kind:'some',value:${sub('value')}};`;break;
   case'present':case'absent':body=`v=${sub('value')}.kind===${json(e.op==='present'?'some':'none')};`;break;
   case'require_some':body=`const value=${sub('value')};if(value.kind!=='some')k.fail('InputType',s);v=value.value;`;break;
   case'require_variant':body=`v=${sub('value')};k.variant(v,${json({kind:'variant',enum_name:e.enum_name,variant:e.variant})},s);`;break;
   case'tag':body=`const value=${sub('value')};v=typeof value==='string'?value:(value.kind??value.tag);`;break;
   case'all_unique_exact':body=generic?`const values=${sub('value')};v=true;outer:for(let j=0;j<values.length;j++)for(let z=0;z<j;z++)if(k.equal(values[j],values[z],a,k.site(${json(p)},[...i,j,z],c))){v=false;break outer;}`:`const values=${sub('value')},seen=new Set();v=true;for(let j=0;j<values.length;j++){const item=values[j];const itemSite=k.site(${json(p)},[...i,j],c);k.charge(a,itemSite);if(typeof item==='string')k.byteWork(a,itemSite,new TextEncoder().encode(item).length);if(seen.has(item)){v=false;break;}seen.add(item);}`;break;
   case'length':body=`const value=${sub('value')};${e.unit==='items'?'v=BigInt(value.length);':`k.byteWork(a,s,new TextEncoder().encode(value).length);v=BigInt(${e.unit==='unicode-scalars'?'[...value].length':'new TextEncoder().encode(value).length'});`}`;break;
   case'let':body=`const value=${sub('value')};${generic?`k.checkpoint(value,${json(e.binding.type)},a,k.site(${json(p+'.value')},i,c));`:''}v=${sub('body',scope(`{[${json(e.binding.name)}]:value}`))};`;break;
   case'if':body=`v=${sub('condition')}===true?${sub('then')}:${sub('else')};`;break;
   case'unary':body=`v=!${sub('value')};`;break;
   case'concat':body=`const left=${sub('left')},right=${sub('right')};if(typeof left!=='string'||typeof right!=='string')k.fail('InputType',s);v=k.checkpoint(left+right,${json(e.result_type)},a,s);`;break;
   case'binary':{
    const operator=e.operator;
    let operation:string;
    switch(operator){
     case'and':case'or':operation='v=right;';break;
     case'eq':operation='v=k.equal(left,right,a,s);';break;
     case'lt':case'lte':case'gt':case'gte':operation=`v=left${({lt:'<',lte:'<=',gt:'>',gte:'>='})[operator]}right;`;break;
     case'add':operation="v=left+right;if(v>k.max)k.fail('ArithmeticOverflow',s);";break;
     case'subtract':operation="v=left-right;if(v<0n)k.fail('ArithmeticUnderflow',s);";break;
     case'multiply':operation="v=left*right;if(v>k.max)k.fail('ArithmeticOverflow',s);";break;
     case'divide':operation="if(right===0n)k.fail('DivideByZero',s);const aa=left as bigint,bb=right as bigint,remainder=aa%bb;if(remainder!==0n&&r==='reject')k.fail('InexactDivision',s);v=aa/bb+(remainder!==0n&&r==='ceil'?1n:0n);";break;
    }
    body=`const left:any=${sub('left')};${operator==='and'?`if(left===false)v=false;else{`:operator==='or'?`if(left===true)v=true;else{`:''}const right:any=${sub('right')};${operation}${operator==='and'||operator==='or'?'}':''}`;
   }break;
   case'call':if(callOwner){const h=callOwner.bind(p);callOwner.assertCall(h,p,e.declaration);callBindings.push(callOwner.inspect(h));}body=`v=f${functions.get(e.declaration)}(a,[${e.arguments.map((_,j)=>sub('arguments['+j+']')).join(',')}],${json(p)},i,c);`;break;
   case'map':case'filter':body=`const source=${sub('source')},out:any[]=[];${partial('out')};for(let j=0;j<source.length;j++){const ind=[...i,j];k.charge(a,${point('ind')});const en=${scope(`{[${json(e.item.name)}]:source[j]}`)},item=${e.op==='map'?sub('body','en','ind'):sub('predicate','en','ind')};${e.op==='map'?'out.push(item);':'if(item===true)out.push(source[j]);'}${partial('out','ind')};}v=out;`;break;
   case'fold':case'indexed_fold':body=`const source=${sub('source')};let state=${sub('initial')};${check('state')};for(let j=0;j<source.length;j++){const ind=[...i,j];k.charge(a,${point('ind')});const en=${scope(`{[${json(e.state.name)}]:state,[${json(e.item.name)}]:source[j]${e.op==='indexed_fold'?`,[${json(e.index.name)}]:BigInt(j)`:''}}`)};state=${sub('body','en','ind')};${check('state','ind')};}v=state;`;break;
   case'repeat':body=`const count=${sub('count')};if(count>BigInt(${e.max_iterations}))k.fail('IterationBound',k.site(${json(p+'.count')},i,c));let state=${sub('initial')};${check('state')};for(let j=0;j<Number(count);j++){const ind=[...i,j];k.charge(a,${point('ind')});state=${sub('body',scope(`{[${json(e.state.name)}]:state,[${json(e.index.name)}]:BigInt(j)}`),'ind')};${check('state','ind')};}v=state;`;break;
   case'while_bounded':case'until_bounded':body=`let state=${sub('initial')};${check('state')};let j=0;for(;;){const ind=[...i,j],en=${scope(`{[${json(e.state.name)}]:state}`)},guard=${sub('guard','en','ind')};if(${e.op==='until_bounded'?'guard':'!guard'})break;if(j>=${e.max_iterations})k.fail('IterationLimit',${point('ind')});k.charge(a,${point('ind')});state=${sub('body','en','ind')};${check('state','ind')};j++;}v=state;`;break;
   case'range':body=`const start:bigint=${sub('start')},end:bigint=${sub('end')},step:bigint=${sub('step')};if(step===0n)k.fail('IterationBound',s);const count=start>=end?0n:(end-start+step-1n)/step;if(count>BigInt(${e.max_iterations}))k.fail('IterationBound',s);const out:any[]=[];${partial('out')};for(let j=0;j<Number(count);j++){const ind=[...i,j];k.charge(a,${point('ind')});out.push(start+BigInt(j)*step);${partial('out','ind')};}v=out;`;break;
   case'sort':body=`const source=${sub('source')},decorated:any[]=[];for(let j=0;j<source.length;j++){const ind=[...i,j];k.charge(a,${point('ind')});const en=${scope(`{[${json(e.item.name)}]:source[j]}`)};decorated.push({value:source[j],ordinal:j,keys:[${e.keys.map((_,z)=>sub('keys['+z+'].value','en','ind')).join(',')}]});}const sorted:any[]=[],sized:any[]=[];${partial('sized')};const compare=(left:any,right:any)=>{${e.keys.map((key,j)=>`{const n=k.compare(left.keys[${j}],right.keys[${j}],${json(key.mode)},a,k.site(${json(p)},[...i,left.ordinal,right.ordinal,${j}],c));if(n)return ${key.direction==='desc'?'-n':'n'};}`).join('')}return 0;};for(const item of decorated){let j=sorted.length;while(j>0&&compare(item,sorted[j-1])<0)j--;sorted.splice(j,0,item);sized.push(item.value);${partial('sized','[...i,item.ordinal]')};}v=sorted.map(x=>x.value);`;break;
   case'policy':{
    const action=(key:string)=>{const b=policies.get(p+'.'+key)!;return `const pending=k.select(a,s,${json(e.declaration)},${json(b.branch)},${json(b.calculation)},${json(b.invocation_path)});try{v=${sub(key+'.expression')};}finally{a.pending.splice(a.pending.indexOf(pending),1);}`;};
    body=e.cases.map((_,j)=>`${j?'else ':''}if(${sub('cases['+j+'].condition')}===true){${action('cases['+j+'].action')}}`).join('')+(e.cases.length?'else{':'{')+action('otherwise')+'}';
   }break;
   case'match':body=`const value=${sub('value')},en=${scope(`{[${json(e.binding.name)}]:value}`)};`+e.cases.map((_,j)=>`${j?'else ':''}if(${sub('cases['+j+'].when','en')}===true)v=${sub('cases['+j+'].then','en')};`).join('')+(e.cases.length?'else ':'')+`v=${sub('otherwise','en')};`;break;
   case'match_variant':{const vt=slots[indices.get(p+'.value')!]!.type;body=`const value=${sub('value')},variant=k.variant(value,${json(vt)},s);`+e.cases.map((cs,j)=>`${j?'else ':''}if(variant.x.name===${json(cs.variant)}){${cs.binding?`const names=Object.keys(variant.x.fields),en=${scope(`{[${json(cs.binding)}]:names.length===1?variant.fields[names[0]!]:value}`)};`:''}v=${sub('cases['+j+'].then',cs.binding?'en':'env')};}`).join('')+(e.cases.length?'else ':'')+(e.otherwise?`v=${sub('otherwise')};`:`k.fail('InvalidContract',s);`);}break;
   case'state_machine':body=`const state=${sub('state')},event=${sub('event')},en=${scope(`{[${json(e.state_binding.name)}]:state,[${json(e.event_binding.name)}]:event}`)};v={tag:${json(e.otherwise==='stay'?'stayed':'rejected')},state,intents:[],machine:${json(e.declaration)},branch:'otherwise',reason:${json(e.otherwise_reason??'no-match-stay')}};`+e.transitions.map((tr,j)=>`${j?'else ':''}if(${sub('transitions['+j+'].guard','en')}===true){const next=${sub('transitions['+j+'].next','en')},intents:any[]=[];${tr.intents.map((_,z)=>`intents.push(${sub('transitions['+j+'].intents['+z+']','en')});k.checkpoint(intents,${json({kind:'list',element:e.intent_type,min_items:0,max_items:e.max_intents})},a,s);`).join('')}v={tag:'transition',state:next,intents,machine:${json(e.declaration)},branch:${json('transition:'+j)},reason:'matched'};}`).join('');break;
  }
  return `function e${index}(a:any,env:any,i:number[],c:string[],r:string):any{const s=${point()};k.charge(a,s);let v:any;${body}return ${check('v')};}`;
 });
 const functionCode=c.functions.map((f,index)=>`function f${index}(a:any,args:any[],p:string,i:number[],c:string[]):any{const next=[...c,${json(f.name)}],s=k.site(p,i,next);k.enter(a,s);const env=Object.create(null);${f.parameters.map((b,j)=>`env[${json(b.name)}]=k.checkpoint(args[${j}],${json(b.type)},a,s);`).join('')}try{return k.checkpoint(e${indices.get('$.functions['+index+'].body')}(a,env,i,next,${json(f.rounding)}),${json(f.result)},a,s);}catch(error){throw k.annotate(error,${json(f.name)},${json(f.on_evaluation_error)});}}`);
 const schema={...(generic?{schema_version:c.schema_version}:{}),limits:c.limits,inputs:c.inputs,result:c.result,values:{...c.values,records:c.values.records.map(({invariants,...record})=>record)}};
 const recordChecks=c.values.records.map((record,i)=>`case ${json(record.name)}:return ${record.invariants.map((_,j)=>`e${indices.get('$.values.records['+i+'].invariants['+j+']')}(a,value,s.i,s.c,${json(generic?'reject':c.rounding)})===true`).join('&&')||'true'};`).join('');
 if(callOwner)for(const p of c.values.collection_predicates){const h=callOwner.bindPredicate(p.type);callOwner.assertPredicate(h,p.type,p.rule);callBindings.push(callOwner.inspect(h));}
 const predicates=[...new Set(c.values.collection_predicates.map(p=>p.rule))].map(name=>`case ${json(name)}:return f${functions.get(name)}(a,[value],s.p,s.i,s.c)===true;`).join('');
 const kernelSource=kernelTypeScriptSource(generic);
 const source=`// Generated original-source pure computation. Builtin runtime dependency: node:util.\nimport {types as host} from 'node:util';\nconst __name=(value:any,_name?:string)=>value;\nconst createCommerceValueKernel=${kernelSource};\nconst S=JSON.parse(${json(json(schema))}),T=${json(slots.map(s=>s.type))};\nconst k=createCommerceValueKernel(S,host,{record(name:string,value:any,a:any,s:any){switch(name){${recordChecks}default:return k.fail('UnknownReference',s);}},predicate(name:string,value:any,a:any,s:any){switch(name){${predicates}default:return k.fail('UnknownReference',s);}}});\n${functionCode.join('\n')}\n${emitted.join('\n')}\nexport function evaluateObserved(input:Uint8Array,observe=true){const a=k.fresh(observe);let result:any;try{const env=k.input(input,a);a.phase='expression';const value=e${indices.get('$.expression')}(a,env,[],[],${json(c.rounding)});a.phase='output-validation';const wire=k.output(value,a);a.phase='complete';result={ok:true,wire,fuel_used:a.used};}catch(error){result=k.failure(error,a);}return k.observation(a,result);}\nexport function evaluate(input:Uint8Array){return evaluateObserved(input,false).result;}\n`;
 current();
 const manifest=coreFreeze({kind:generic?'generic-computation-typescript-component/v1-candidate':'commerce-computation-typescript-component/v2-candidate',...(generic?{pure_call_bindings:callBindings}:{}),source_node:c.source_node,source:inspection.source,source_capture_sha256:inspection.source_capture_sha256,contract_sha256:inspection.contract_sha256,environment_sha256:inspection.environment.subject_sha256,domain_code_epoch_sha256:inspection.code_epoch_sha256,emitter_code_epoch_sha256:pin.sha256,source_sha256:createHash('sha256').update(source).digest('hex'),runtime_dependencies:['node:util'],runtime_template:{kind:'fixed-typed-value-kernel',sha256:createHash('sha256').update(kernelSource).digest('hex')},symbols:inspection.symbols,bindings:slots.map((s,i)=>({expression_path:s.path,owner:s.owner,generated_function:'e'+i})),declarations:c.functions.map((f,i)=>({declaration:f.name,kind:f.kind,generated_function:'f'+i})),qualification:'standalone-pure-component-only;not-selected-native-basis-or-application-owner',authority_effect:'none'});
 return Object.freeze({source,manifest});
}
