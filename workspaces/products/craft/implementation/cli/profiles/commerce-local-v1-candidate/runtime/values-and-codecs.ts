/** Closed native value boundary; contexts and receipts are never data codecs.
 * Open Questions: docs/COMMERCE-NATIVE-VALUES.md#open-questions. */
import {types as host} from 'node:util';
import {createHash} from 'node:crypto';
import {commerceCodecDomain as model,validateCommerceComputationValue as validateDomain} from './commerce-domain-values.js';
export type NativeCommerceValue=boolean|string|bigint|readonly NativeCommerceValue[]|{readonly [key:string]:NativeCommerceValue};
export interface NativeCodecHandle {readonly kind:'original-commerce-value-codec/v1-candidate'}
export type NativeCodecFailure={readonly code:'InputType'|'InputBound'|'InvalidUnicode'|'OutputBound';readonly path:string;readonly byte_offset:number};
export type NativeCodecResult<T>={readonly ok:true;readonly value:T}|{readonly ok:false;readonly error:NativeCodecFailure};
class CodecFault extends Error {readonly error:NativeCodecFailure;constructor(error:NativeCodecFailure){super(error.code);this.error=error;}}
const fail=(code:NativeCodecFailure['code'],path='$',byte_offset=0):never=>{throw new CodecFault({code,path,byte_offset});};
const encoder=new TextEncoder(),MAX=18446744073709551615n;
const records=new Map<string,any>(model.values.records.map((r:any)=>[r.name,r])),enums=new Map<string,any>(model.values.enums.map((r:any)=>[r.name,r])),refinements=new Map<string,any>(model.values.refinements.map((r:any)=>[r.name,r]));
const scalar=(s:string)=>{for(let i=0;i<s.length;i++){const c=s.charCodeAt(i);if(c>=0xd800&&c<=0xdbff){const n=s.charCodeAt(++i);if(!(n>=0xdc00&&n<=0xdfff))return false;}else if(c>=0xdc00&&c<=0xdfff)return false;}return true;};
const quote=(s:string)=>'"'+s.replace(/["\\\u0000-\u001f]/g,c=>c==='"'?'\\"':c==='\\'?'\\\\':'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+'"';
const canonical=(v:any):string=>v===null?'null':typeof v==='string'?quote(v):typeof v==='boolean'?String(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>quote(k)+':'+canonical(v[k])).join(',')+'}';
const metaJson=(v:any):string=>Array.isArray(v)?'['+v.map(metaJson).join(',')+']':v!==null&&typeof v==='object'?'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+metaJson(v[k])).join(',')+'}':JSON.stringify(v);
const digest=(v:any)=>createHash('sha256').update(metaJson(v)).digest('hex');
const copyInert=(input:any,metadata=false)=>{
 const active=new WeakSet<object>();let nodes=0,bytes=0;
 const visit=(v:any,p:string,depth:number):any=>{
  if(++nodes>65536||depth>32)fail('InputBound',p);
  if(typeof v==='boolean')return v;
  if(typeof v==='string'){if(v.length>model.limits.max_value_bytes)fail('InputBound',p);if(!scalar(v))fail('InvalidUnicode',p);bytes+=encoder.encode(v).length;if(bytes>model.limits.max_value_bytes)fail('InputBound',p);return v;}
  if(metadata&&v===null)return null;
  if(typeof v==='bigint'&&!metadata){if(v<0n||v>MAX)fail('InputBound',p);return v;}
  if(metadata&&typeof v==='number'&&Number.isSafeInteger(v))return v;
  if(!v||typeof v!=='object'||host.isProxy(v)||active.has(v))fail('InputType',p);
  const array=Array.isArray(v),prototype=Object.getPrototypeOf(v);if(array?prototype!==Array.prototype:prototype!==Object.prototype&&prototype!==null)fail('InputType',p);
  const length=array?Object.getOwnPropertyDescriptor(v,'length')!.value:0;if(array&&(!Number.isSafeInteger(length)||length>(metadata?65535:model.limits.max_items)))fail('InputBound',p);
  const names=Reflect.ownKeys(v);if(names.length>(array?length+1:metadata?256:128)||names.some(k=>typeof k!=='string'))fail('InputType',p);
  const ds=Object.getOwnPropertyDescriptors(v);active.add(v);try{if(array){if(names.length!==length+1)fail('InputType',p);const out:any[]=[];for(let i=0;i<length;i++){const d=ds[String(i)];if(!d||!d.enumerable||!Object.hasOwn(d,'value'))fail('InputType',p+'['+i+']');out.push(visit(d.value,p+'['+i+']',depth+1));}return out;}
   const out=Object.create(null);for(const name of names as string[]){const d=ds[name]!;if(!d.enumerable||!Object.hasOwn(d,'value'))fail('InputType',p+'.'+name);bytes+=encoder.encode(name).length;if(bytes>model.limits.max_value_bytes)fail('InputBound',p);out[name]=visit(d.value,p+'.'+name,depth+1);}return out;
  }finally{active.delete(v);}
 };return visit(input,'$',0);
};
function ownedBytes(input:any):Uint8Array {
 if(host.isProxy(input)||!host.isUint8Array(input))fail('InputType');
 try{const p=Object.getPrototypeOf(Uint8Array.prototype),get=(name:string)=>Object.getOwnPropertyDescriptor(p,name)!.get!.call(input),n=get('byteLength'),buffer=get('buffer');if(n>model.limits.max_input_bytes)fail('InputBound');if(host.isSharedArrayBuffer(buffer))fail('InputType');const out=new Uint8Array(n);Uint8Array.prototype.set.call(out,new Uint8Array(buffer,get('byteOffset'),n));return out;}catch(e){if(e instanceof CodecFault)throw e;return fail('InputType');}
}
function parseWire(input:any):any {
 const bytes=ownedBytes(input);if(bytes[0]===239&&bytes[1]===187&&bytes[2]===191)fail('InputType');
 // Explicit UTF8 scan locates the bad byte and forbids overlong/surrogate forms.
 for(let i=0;i<bytes.length;i++){const b=bytes[i]!;if(b<128)continue;let n:number,low=128,high=191;if(b>=194&&b<=223)n=1;else if(b>=224&&b<=239){n=2;if(b===224)low=160;if(b===237)high=159;}else if(b>=240&&b<=244){n=3;if(b===240)low=144;if(b===244)high=143;}else return fail('InvalidUnicode','$',i);if(i+n>=bytes.length)fail('InvalidUnicode','$',i);if(bytes[i+1]!<low||bytes[i+1]!>high)fail('InvalidUnicode','$',i+1);for(let j=2;j<=n;j++)if(bytes[i+j]!<128||bytes[i+j]!>191)fail('InvalidUnicode','$',i+j);i+=n;}
 const text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes);let pos=0,nodes=0;const bad=(code:NativeCodecFailure['code']='InputType'):never=>fail(code,'$',encoder.encode(text.slice(0,pos)).length),ws=()=>{while(/[\x20\t\r\n]/.test(text[pos]??'!'))pos++;};
 const string=()=>{const start=pos++;while(pos<text.length){const ch=text[pos++];if(ch==='"'){let value:any;try{value=JSON.parse(text.slice(start,pos));}catch{return bad();}if(!scalar(value))bad('InvalidUnicode');return value;}if(ch==='\\')pos++;}return bad();};
 const value=(depth:number):any=>{if(++nodes>65536||depth>32)bad('InputBound');ws();const ch=text[pos];if(ch==='"')return string();if(ch==='{'){pos++;ws();const out=Object.create(null);if(text[pos]==='}'){pos++;return out;}let count=0;for(;;){if(++count>128)bad('InputBound');ws();if(text[pos]!=='"')bad();const key=string();if(Object.hasOwn(out,key))bad();ws();if(text[pos++]!==':')bad();out[key]=value(depth+1);ws();const next=text[pos++];if(next==='}')return out;if(next!==',')bad();}}
  if(ch==='['){pos++;ws();const out:any[]=[];if(text[pos]===']'){pos++;return out;}for(;;){if(out.length>=model.limits.max_items)bad('InputBound');out.push(value(depth+1));ws();const next=text[pos++];if(next===']')return out;if(next!==',')bad();}}
  for(const [token,v]of [['true',true],['false',false],['null',null]]as const)if(text.startsWith(token,pos)){pos+=token.length;return v;}return bad();
 };const out=value(0);ws();if(pos!==text.length)bad();return out;
}
const closed=(v:any,names:string[],p:string)=>{if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).length!==names.length||names.some(k=>!Object.hasOwn(v,k)))fail('InputType',p);};
function convert(v:any,t:any,direction:'native-to-private'|'private-to-native'|'wire-to-private'|'computation-wire-to-private'|'native-to-wire'|'private-wire',p='$',depth=0):any {
 if(depth>32)fail('InputBound',p);const fromComputation=direction==='computation-wire-to-private',fromWire=direction==='wire-to-private'||fromComputation,fromPrivate=direction==='private-to-native',toWire=direction==='native-to-wire'||direction==='private-wire',privateWire=direction==='private-wire',recur=(x:any,type:any,name:string)=>convert(x,type,direction,p+name,depth+1);
 switch(t.kind){
  case'scalar':if(t.name==='Bool'){if(typeof v!=='boolean')fail('InputType',p);return v;}if(fromWire){if(typeof v!=='string'||v.length>20||/^(0|[1-9][0-9]*)$/.exec(v)?.[0]!==v)fail('InputType',p);const n=BigInt(v);if(n>MAX)fail('InputBound',p);return n;}if(typeof v!=='bigint'||v<0n||v>MAX)fail('InputType',p);return toWire?String(v):v;
  case'string':case'literal':case'refinement':if(typeof v!=='string'||!scalar(v))fail('InputType',p);return v;
  case'optional':if(fromWire){if(v===null)return {kind:'none'};return {kind:'some',value:recur(v,t.element,'.value')};}if(!v||typeof v!=='object')fail('InputType',p);if(v.kind==='none'){closed(v,['kind'],p);return toWire?null:Object.freeze({kind:'none'});}if(v.kind!=='some')fail('InputType',p);closed(v,['kind','value'],p);const some=recur(v.value,t.element,'.value');return toWire?some:Object.freeze({kind:'some',value:some});
  case'list':if(!Array.isArray(v))fail('InputType',p);if(v.length>t.max_items||v.length<t.min_items)fail('InputBound',p);return Object.freeze(v.map((x:any,i:number)=>recur(x,t.element,'['+i+']')));
  case'record':{const r=records.get(t.name);if(!r)fail('InputType',p);closed(v,Object.keys(r.fields),p);const out=Object.create(null);for(const [name,type]of Object.entries(r.fields))out[name]=recur(v[name],type,'.'+name);return Object.freeze(out);}
  case'enum':case'variant':{const e=enums.get(t.kind==='variant'?t.enum_name:t.name);if(!e)fail('InputType',p);const simple=e.variants.every((x:any)=>!Object.keys(x.fields).length),name=simple?v:fromComputation?v?.tag:v?.kind,x=e.variants.find((x:any)=>(fromWire?x.wire:x.name)===name);if(!x||t.kind==='variant'&&x.name!==t.variant)fail('InputType',p);if(simple)return toWire?x.wire:x.name;const names=Object.keys(x.fields);if(names.includes('kind'))fail('InputType',p);let fields:any;
   if(fromComputation){closed(v,['tag','fields'],p);closed(v.fields,names,p);fields=v.fields;}else if(fromPrivate||privateWire){closed(v,['kind','fields'],p);closed(v.fields,names,p);fields=v.fields;}else{closed(v,['kind',...names],p);fields=v;}
   const out=Object.create(null);for(const [name,type]of Object.entries(x.fields))out[name]=recur(fields[name],type,'.'+name);
   if(direction==='native-to-private'||fromWire)return {kind:x.name,fields:out};if(privateWire)return {tag:x.wire,fields:out};return Object.freeze(Object.assign(Object.create(null),{kind:toWire?x.wire:x.name},out));
  }
  case'outcome':{closed(v,['tag','state','intents','machine','branch','reason'],p);const out={...v,state:recur(v.state,t.state,'.state'),intents:recur(v.intents,{kind:'list',element:t.intent,min_items:0,max_items:t.max_intents},'.intents')};if(!['transition','stayed','rejected'].includes(v.tag)||typeof v.machine!=='string'||typeof v.reason!=='string'||typeof v.branch!=='string')fail('InputType',p);const machine=model.machines.find((m:any)=>m.name===v.machine&&digest(m.result)===digest(t));if(!machine)fail('InputType',p);if(v.tag==='transition'){if(!/^transition:(0|[1-9][0-9]*)$/.test(v.branch)||Number(v.branch.slice(11))>=machine.transitions||v.reason!=='matched')fail('InputType',p);}else if(v.branch!=='otherwise'||v.tag!==(machine.otherwise==='stay'?'stayed':'rejected')||v.reason!==(machine.reason??'no-match-stay')||v.intents.length!==0)fail('InputType',p);return Object.freeze(out);}
  default:return fail('InputType',p);
 }
}
function refinementMaximum(r:any):bigint {
 if(r.pattern===null)return 2n+6n*BigInt(Math.min(r.max_utf8_bytes,r.max_unicode_scalars));
 const atoms:{low:number;high:number;width:number}[]=[];let pos=1;
 while(pos<r.pattern.length-1){let width=1;if(r.pattern[pos]==='['){const end=r.pattern.indexOf(']',pos+1),body=r.pattern.slice(pos+1,end),codes:number[]=[];for(let i=0;i<body.length;i++){if(body[i+1]==='-'&&i+2<body.length){for(let c=body.charCodeAt(i);c<=body.charCodeAt(i+2);c++)codes.push(c);i+=2;}else codes.push(body.charCodeAt(i));}if(codes.includes(34)||codes.includes(92))width=2;pos=end+1;}else{width=[34,92].includes(r.pattern.charCodeAt(pos))?2:1;pos++;}let low=1,high=1;if(r.pattern[pos]==='{'){const m=/^\{([0-9]+)(?:,([0-9]+))?\}/.exec(r.pattern.slice(pos));if(!m)throw new Error('UnsupportedCapability');low=Number(m[1]);high=Number(m[2]??m[1]);pos+=m[0].length;}atoms.push({low,high,width});}
 const low=atoms.reduce((n,a)=>n+a.low,0),high=atoms.reduce((n,a)=>n+a.high,0),cap=Math.min(r.max_utf8_bytes,r.max_unicode_scalars,high);if(cap<Math.max(low,r.min_utf8_bytes,r.min_unicode_scalars))throw new Error('UnsupportedCapability');let remaining=cap-low,cost=atoms.reduce((n,a)=>n+a.low*a.width,0);for(const a of atoms.sort((a,b)=>b.width-a.width)){const used=Math.min(remaining,a.high-a.low);cost+=used*a.width;remaining-=used;}return 2n+BigInt(cost);
}
const maxMemo=new Map<string,bigint>();
const rootRows=new Map<string,any>(model.roots.map((r:any)=>[r.key,r.type]));
function maximumUncached(type:any,privateWire=false,active=new Set<string>()):bigint {
 const key=digest({type,privateWire});const prior=maxMemo.get(key);if(prior!==undefined)return prior;if(active.has(key))throw new Error('UnsupportedCapability');const next=new Set(active);next.add(key);const child=(t:any)=>maximum(t,privateWire,next),object=(fields:Readonly<Record<string,any>>)=>2n+Object.entries(fields).reduce((sum,[name,t],i)=>sum+BigInt(encoder.encode(quote(name)).length+1+(i?1:0))+child(t),0n);
 switch(type.kind){case'scalar':return type.name==='UInt64'?22n:5n;case'literal':return BigInt(encoder.encode(quote(type.value)).length);case'string':return 2n+6n*BigInt(Math.min(type.max_bytes,type.max_scalars));case'refinement':{const r=refinements.get(type.name);if(!r)throw new Error('UnsupportedCapability');return refinementMaximum(r);}case'list':return 2n+BigInt(type.max_items)*child(type.element)+BigInt(Math.max(0,type.max_items-1));case'optional':if(type.element.kind==='optional')throw new Error('UnsupportedCapability');return child(type.element)>4n?child(type.element):4n;case'record':{const r=records.get(type.name);if(!r)throw new Error('UnsupportedCapability');return object(r.fields);}case'enum':case'variant':{const e=enums.get(type.kind==='variant'?type.enum_name:type.name);if(!e)throw new Error('UnsupportedCapability');const simple=e.variants.every((v:any)=>!Object.keys(v.fields).length);let max=0n;for(const v of e.variants){if(type.kind==='variant'&&v.name!==type.variant)continue;if(Object.hasOwn(v.fields,'kind'))throw new Error('UnsupportedCapability');const n=simple?BigInt(encoder.encode(quote(v.wire)).length):privateWire?object({tag:{kind:'literal',value:v.wire},fields:{kind:'codec-inline-record',fields:v.fields}}):object({kind:{kind:'literal',value:v.wire},...v.fields});if(n>max)max=n;}return max;}case'codec-inline-record':return object(type.fields);case'outcome':return object({tag:{kind:'string',max_bytes:10,max_scalars:10},state:type.state,intents:{kind:'list',element:type.intent,min_items:0,max_items:type.max_intents},machine:{kind:'string',max_bytes:256,max_scalars:256},branch:{kind:'string',max_bytes:256,max_scalars:256},reason:{kind:'string',max_bytes:256,max_scalars:256}});default:throw new Error('UnsupportedCapability');}
}
function maximum(type:any,privateWire=false,active=new Set<string>()):bigint{const key=digest({type,privateWire}),prior=maxMemo.get(key);if(prior!==undefined)return prior;const n=maximumUncached(type,privateWire,active);maxMemo.set(key,n);return n;}
type Spec={kind:'value';type:any;key:string;maximum:number}|{kind:'arguments';parameters:readonly any[];maximum:number};
export function createCommerceValueCodecs(){
 const owned=new WeakMap<object,Spec>();
 const valueSpec=(type:any):Spec=>{const key=digest(type),actual=rootRows.get(key);if(!actual)throw new Error('UnsupportedCapability');const size=maximum(actual),privateSize=maximum(actual,true);if(size>BigInt(model.limits.max_value_bytes)||privateSize>BigInt(model.limits.max_value_bytes))throw new Error('UnsupportedCapability');return {kind:'value',type:actual,key,maximum:Number(size)};};
 const token=(spec:Spec):NativeCodecHandle=>{const handle=Object.freeze({kind:'original-commerce-value-codec/v1-candidate' as const});owned.set(handle,spec);return handle;};
 const get=(h:NativeCodecHandle)=>{const s=h&&typeof h==='object'?owned.get(h):undefined;if(!s)throw new Error('ForeignCodecHandle');return s;};
 const checked=(v:any,s:Spec,wire:false|true|'computation'=false):any=>{if(s.kind==='arguments'){closed(v,s.parameters.map(p=>p.name),'$');const out=Object.create(null);for(const p of s.parameters)out[p.name]=checked(v[p.name],valueSpec(p.type),wire);return Object.freeze(out);}const internal=convert(v,s.type,wire==='computation'?'computation-wire-to-private':wire?'wire-to-private':'native-to-private'),r=validateDomain(s.key,internal);if(!r.ok){const code=r.error.code==='InvalidUnicode'?'InvalidUnicode':r.error.code==='InputBound'||r.error.code==='ResourceLimit'||r.error.code==='OutputBound'?'InputBound':'InputType';fail(code,r.error.expression_path??'$');}return convert(r.value,s.type,'private-to-native');};
 const toWire=(v:any,s:Spec,privateWire=false):any=>{if(s.kind==='arguments'){const out=Object.create(null);for(const p of s.parameters)out[p.name]=toWire(v[p.name],valueSpec(p.type),privateWire);return out;}return privateWire?convert(convert(v,s.type,'native-to-private'),s.type,'private-wire'):convert(v,s.type,'native-to-wire');};
 const attempt=<T>(run:()=>T):NativeCodecResult<T>=>{try{return {ok:true,value:run()};}catch(e){if(e instanceof CodecFault)return {ok:false,error:e.error};throw e;}};
 return Object.freeze({
  checkCommerceSchema(schema:any){try{const input=copyInert(schema,true);if(digest({...input,root:null})!==model.universe_sha256)throw new Error('InvalidContract');return {ok:true,value:token(valueSpec(input.root))};}catch(e){return {ok:false,diagnostics:[{code:e instanceof CodecFault?'InvalidContract':(e as Error).message==='UnsupportedCapability'?'UnsupportedCapability':'InvalidContract',path:'$',start:0,end:0,message:'exact supported source value schema required'}]};}},
  schemaForType(name:string){if(typeof name!=='string')throw new Error('UnsupportedCapability');for(const type of rootRows.values())if(['record','enum','refinement'].includes(type.kind)&&type.name===name)return token(valueSpec(type));throw new Error('UnsupportedCapability');},
  schemaForEntryArguments(id:string){const entry=model.entries.find((e:any)=>e.id===id);if(!entry)throw new Error('UnsupportedCapability');let size=2;for(let i=0;i<entry.parameters.length;i++){const p=entry.parameters[i],s=valueSpec(p.type);size+=encoder.encode(quote(p.name)).length+1+(i?1:0)+s.maximum;}if(size>model.limits.max_value_bytes)throw new Error('UnsupportedCapability');return token({kind:'arguments',parameters:entry.parameters,maximum:size});},
  inspectSchema(handle:NativeCodecHandle){const s=get(handle);return Object.freeze({kind:s.kind,maximum_canonical_bytes:s.maximum,source_capture_sha256:model.source_capture_sha256,authority_effect:'none',qualification:'data-codec-schema-only;not-private-context-or-owner'});},
  schemaForCallableArguments(id:string){const call=model.callables.find((e:any)=>e.id===id);if(!call)throw new Error('UnsupportedCapability');let size=2;for(let i=0;i<call.parameters.length;i++){const p=call.parameters[i],s=valueSpec(p.type);size+=encoder.encode(quote(p.name)).length+1+(i?1:0)+s.maximum;}if(size>model.limits.max_value_bytes)throw new Error('UnsupportedCapability');return token({kind:'arguments',parameters:call.parameters,maximum:size});},
  decodeComputationValue(handle:NativeCodecHandle,bytes:Uint8Array){const s=get(handle);return attempt(()=>checked(parseWire(bytes),s,'computation'));},
  decodeCommerceValue(handle:NativeCodecHandle,bytes:Uint8Array){const s=get(handle);return attempt(()=>checked(parseWire(bytes),s,true));},
  copyCommerceValue(handle:NativeCodecHandle,value:NativeCommerceValue){const s=get(handle);return attempt(()=>checked(copyInert(value),s));},
  encodeCommerceValue(handle:NativeCodecHandle,value:NativeCommerceValue){const s=get(handle);return attempt(()=>{const v=checked(copyInert(value),s),out=encoder.encode(canonical(toWire(v,s)));if(out.length>model.limits.max_output_bytes||out.length>s.maximum)fail('OutputBound');return out;});},
  encodeComputationParameters(handle:NativeCodecHandle,value:NativeCommerceValue){const s=get(handle);if(s.kind!=='arguments')throw new Error('ArgumentSchemaRequired');return attempt(()=>{const v=checked(copyInert(value),s),out=encoder.encode(canonical(toWire(v,s,true)));if(out.length>model.limits.max_input_bytes)fail('OutputBound');return out;});},
 });
}
