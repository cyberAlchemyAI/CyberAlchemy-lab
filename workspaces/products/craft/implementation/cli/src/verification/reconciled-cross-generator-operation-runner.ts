import {OPERATION_FIXTURE_RUNNER} from './reconciled-operation-fixture.js';
import {OPERATION_BINDING_RUNNER} from './reconciled-operation-runner.js';
import {CROSS_GENERATOR_OPERATION_PROTOCOL_SHA256} from './reconciled-cross-generator-operation.js';
/** Run-local facades call original methods and preserve original owned returns. */
export const CROSS_GENERATOR_OPERATION_RUNNER=String.raw`
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';
const payload=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),root=path.resolve(process.argv[3]),require=createRequire(import.meta.url);
if(payload.protocol_sha256!=='__PROTOCOL_HASH__'||!Array.isArray(payload.rows)||!payload.rows.length)throw Error('OPERATION_PROBE_PROFILE');
const safe=p=>{if(typeof p!=='string'||!p.endsWith('.ts')||path.posix.normalize(p)!==p||p.startsWith('../')||path.isAbsolute(p)||p.includes('\\'))throw Error('OPERATION_PROBE_PATH');return path.join(root,p.replace(/\.ts$/,'.js'));};
const data=(v,key)=>{const p=Object.getOwnPropertyDescriptor(v,key);if(!p||!Object.hasOwn(p,'value')||!p.enumerable)throw Error('OPERATION_PROBE_DATA');return p.value;};
const facade=(original,replacements)=>{
 if(!original||typeof original!=='object'||!Object.isFrozen(original))throw Error('OPERATION_PROBE_FACADE');
 const descriptors=Object.getOwnPropertyDescriptors(original);
 for(const[key,value]of Object.entries(replacements)){const p=descriptors[key];if(!p||!Object.hasOwn(p,'value')||typeof p.value!=='function')throw Error('OPERATION_PROBE_METHOD');descriptors[key]={...p,value};}
 return Object.freeze(Object.create(Object.getPrototypeOf(original),descriptors));
};
function expand(recipes,id){
 let visits=0;const active=new Set();
 const read=(r,depth=0)=>{
  if(++visits>65536||depth>64)throw Error('OPERATION_PROBE_RECIPE_CAPACITY');
  if(r.tag==='ref'){const i=Number(r.value);if(!Number.isSafeInteger(i)||i<0||i>=recipes.length||active.has(i))throw Error('OPERATION_PROBE_RECIPE');active.add(i);const v=read(recipes[i],depth);active.delete(i);return v;}
  return {...r,...(r.base?{base:read(r.base,depth+1)}:{}),...(r.input?{input:read(r.input,depth+1)}:{}),...(r.payload?{payload:read(r.payload,depth+1)}:{}),...(r.items?{items:r.items.map(v=>read(v,depth+1))}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,read(v,depth+1)]))}:{})};
 };return read({tag:'ref',value:String(id)});
}
`.replace('__PROTOCOL_HASH__',CROSS_GENERATOR_OPERATION_PROTOCOL_SHA256)+OPERATION_BINDING_RUNNER+
OPERATION_FIXTURE_RUNNER.replace(/^export (async )?function /gm,(_,a:string|undefined)=>(a??'')+'function ')+String.raw`
const rows=[];
for(const row of payload.rows){
 if(row.adapter!=='operation-protocol')throw Error('OPERATION_PROBE_ADAPTER');
 const allowed=new Set(row.modules.map(m=>safe(m.relative_path))),load=p=>{const f=safe(p);if(!allowed.has(f))throw Error('OPERATION_PROBE_MODULE');return require(f);};
 for(const p of allowed)delete require.cache[p];
 const owned=new WeakMap(),singletons=new Map(),clocks=new WeakMap(),fingerprintIds=new Map();let fingerprintNext=0,active=null,depth=0,initializing=false,nextInstance=0,totalCalls=0;
 const initialization=[],restores=[];
 const wire=(v,level=0)=>{
  if(level>64)throw Error('OPERATION_PROBE_VALUE_DEPTH');
  if(v!==null&&(typeof v==='object'||typeof v==='function')){const clock=clocks.get(v);if(clock!==undefined)return ['clock',clock];const token=owned.get(v);if(token!==undefined)return ['owned',token];}
  if(v===null)return ['null'];if(typeof v==='bigint')return ['bigint',String(v)];
  if(typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return [typeof v,v];
  if(!v||typeof v!=='object')throw Error('OPERATION_PROBE_ACTIVE_VALUE');
  const d=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(d);
  if(keys.some(k=>typeof k!=='string'||!Object.hasOwn(d[k],'value')))throw Error('OPERATION_PROBE_ACTIVE_VALUE');
  if(Array.isArray(v)){if(Object.getPrototypeOf(v)!==Array.prototype||keys.length!==v.length+1)throw Error('OPERATION_PROBE_ARRAY');return ['array',Array.from({length:v.length},(_,i)=>{if(!d[i]?.enumerable)throw Error('OPERATION_PROBE_ARRAY');return wire(d[i].value,level+1);})];}
  if(![Object.prototype,null].includes(Object.getPrototypeOf(v))||keys.some(k=>!d[k].enumerable))throw Error('OPERATION_PROBE_RECORD');
  return ['record',keys.sort().map(k=>[k,wire(d[k].value,level+1)])];
 };
 const fingerprint=value=>{
  const seen=new Set();let visits=0;
  const id=v=>{if(!fingerprintIds.has(v))fingerprintIds.set(v,fingerprintNext++);return fingerprintIds.get(v);};
  const walk=(v,level=0)=>{
   if(++visits>65536||level>64)throw Error('OPERATION_PROBE_FINGERPRINT_CAPACITY');
   if(typeof v==='symbol'||typeof v==='function')return [typeof v,id(v)];
   if(v===null||typeof v!=='object')return [typeof v,typeof v==='bigint'?String(v):Object.is(v,-0)?'-0':v];
   if(seen.has(v))return ['ref',id(v)];seen.add(v);const d=Object.getOwnPropertyDescriptors(v),proto=Object.getPrototypeOf(v);
   return [id(v),proto===null?null:id(proto),Object.isExtensible(v),Reflect.ownKeys(d).map(k=>{const p=d[k];return [typeof k==='symbol'?['symbol',id(k)]:k,p.enumerable,p.configurable,Object.hasOwn(p,'value')?['value',p.writable,walk(p.value,level+1)]:['accessor',p.get?id(p.get):null,p.set?id(p.set):null]];})];
  };return JSON.stringify(walk(value));
 };
 const valueToken=(value,provider,method,index,component)=>{
  if(!value||typeof value!=='object'||!Object.isFrozen(value)||component.isOwned(value)!==true)throw Error('OPERATION_PROBE_OWNED_RETURN');
  const token=method==='fromVariant'?'enum:'+JSON.stringify([provider,data(value,'variant')]):'owned:'+active.id+':'+index;
  if(method==='fromVariant'){
   if(singletons.has(token)&&singletons.get(token)!==value)throw Error('OPERATION_PROBE_ENUM_SINGLETON');
   singletons.set(token,value);
  }
  if(!owned.has(value))owned.set(value,token);return value;
 };
 const replacement=(native,name,value)=>{const descriptor=Object.getOwnPropertyDescriptor(native,name);if(!descriptor||!Object.hasOwn(descriptor,'value'))throw Error('OPERATION_PROBE_EXPORT');restores.push(()=>Object.defineProperty(native,name,descriptor));Object.defineProperty(native,name,{...descriptor,value});};
 const invoke=(provider,method,instance,original,receiver,args,project)=>{
  if(depth||!initializing&&!active)return Reflect.apply(original,receiver,args);
  if(++totalCalls>65536)throw Error('OPERATION_PROBE_CALL_CAPACITY');
  const list=active?active.calls:initialization,index=list.length,before=fingerprint(args);
  const call={provider,method,instance,arity:args.length,arguments:wire(args),result:null,input_changed:false};list.push(call);depth++;
  try{const value=Reflect.apply(original,receiver,args);call.result={kind:'value',value:wire(project(value,index))};return value;}
  catch(e){call.result={kind:'error',name:e?.name,message:e?.message};throw e;}
  finally{depth--;call.input_changed=before!==fingerprint(args);}
 };
 const factoryFacade=(factory,m,instance,component)=>facade(factory,{create:(...args)=>invoke(m.selector,'create',instance,data(factory,'create'),factory,args,(result,index)=>{
  const ok=data(result,'ok'),value=data(result,'value');if(ok)valueToken(value,m.selector,'create',index,component);
  return {ok,value,fields:ok?data(value,'fields'):null,failure_codes:data(result,'failure_codes'),owned:ok?component.isOwned(value):false,frozen:Object.isFrozen(result)&&(!ok||Object.isFrozen(value))};
 })});
 try{
  // Original dependencies are initialized before instrumentation; target Operation is not.
  for(const m of row.modules.filter(m=>!m.role.startsWith('operation-')))load(m.relative_path);
  const identity={operation:false,events:row.modules.filter(m=>m.role==='event-wrapper').map(m=>({selector:m.selector,original:data(load(m.relative_path),m.callable)===data(load(m.relative_path.replace(/\.ts$/,'.provider.ts')),'make')}))};
  const provider=row.modules.find(m=>m.role==='operation-provider');if(!provider)throw Error('OPERATION_PROBE_PROVIDER');
  for(const imp of provider.imports.filter(i=>!i.type_only)){
   const m=row.modules.find(m=>m.relative_path===imp.target_path),native=load(imp.target_path),symbol=imp.names[0],original=data(native,symbol);
   if(!m||imp.names.length!==1)throw Error('OPERATION_PROBE_IMPORT');
   if(m.role==='rule'||m.role==='event-wrapper'){
    if(typeof original!=='function')throw Error('OPERATION_PROBE_CALLABLE');
    replacement(native,symbol,(...args)=>invoke(m.selector,m.role==='rule'?'guard':'event',null,original,undefined,args,value=>m.role==='rule'?value:{value,frozen:Object.isFrozen(value)}));
   }else if(m.role==='factory'){
    const component=data(native,m.value_exports.find(n=>n.endsWith('ValueComponent')));
    replacement(native,symbol,(...args)=>{
     const recording=!depth&&(initializing||active),instance=nextInstance++;
     if(recording&&initializing){
      if(++totalCalls>65536)throw Error('OPERATION_PROBE_CALL_CAPACITY');
      const before=fingerprint(args);depth++;let factory;try{factory=Reflect.apply(original,undefined,args);}finally{depth--;}
      initialization.push({provider:m.selector,method:'factory',instance,arity:args.length,arguments:wire(args),result:{instance,frozen:Object.isFrozen(factory),extensions:data(factory,'extensions')},input_changed:before!==fingerprint(args)});
      return factoryFacade(factory,m,instance,component);
     }
     return factoryFacade(invoke(m.selector,'factory',instance,original,undefined,args,value=>({instance,frozen:Object.isFrozen(value),extensions:data(value,'extensions')})),m,instance,component);
    });
   }else if(m.role==='sum'||m.role==='enum-component'){
    const method=m.role==='sum'?'create':'fromVariant';
    replacement(native,symbol,facade(original,{[method]:(...args)=>invoke(m.selector,method,null,data(original,method),original,args,(value,index)=>{
     valueToken(value,m.selector,method,index,original);const variant=data(value,'variant'),p=Object.getOwnPropertyDescriptor(value,'payload'),view={variant,...(p?{payload:data(value,'payload')}:{})};
     return {value,data:view,owned:original.isOwned(value),frozen:Object.isFrozen(value)};
    })}));
   }else throw Error('OPERATION_PROBE_UNDECLARED_PROVIDER');
  }
  initializing=true;let native;try{native=load(row.relative_path);}finally{initializing=false;}
  const fn=data(native,row.callable);identity.operation=fn===data(load(row.provider_path),'execute');const descriptor=operationDescriptor(fn),cases=[];
  for(const c of row.cases){
   active={id:c.id,calls:[]};const input=expand(row.recipes,c.data.input),effects={reads:c.data.reads.map(r=>({...r,value:expand(row.recipes,r.value)})),clocks:c.data.clocks};
   const call=(input,dependencies)=>{for(const[slot,p]of Object.entries(Object.getOwnPropertyDescriptors(dependencies.clocks)))if(Object.hasOwn(p,'value')&&typeof p.value==='function')clocks.set(p.value,slot);return fn(input,dependencies);};
   const mutate=c.data.capture?(input,dependencies)=>{
    for(const key of Object.keys(input))input[key]=typeof input[key]==='boolean'?!input[key]:typeof input[key]==='string'?input[key]+'-changed':typeof input[key]==='bigint'?input[key]+1n:typeof input[key]==='number'?input[key]+1:null;
    for(const key of Object.keys(dependencies.clocks))dependencies.clocks[key]=()=>{throw Error('late-operation-clock');};
   }:null;
   const semantic=await observeOperationFixture(call,input,c.data.mode,mutate,effects);cases.push({id:c.id,calls:active.calls,semantic});active=null;
  }
  rows.push({selector:row.selector,initialization,identity,descriptor,cases});
 }finally{active=null;initializing=false;for(const restore of restores.reverse())restore();}
}
console.log(JSON.stringify({controls_sha256:payload.controls_sha256,rows}));
`;
