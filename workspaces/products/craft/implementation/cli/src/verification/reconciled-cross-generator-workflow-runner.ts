import {WORKFLOW_FIXTURE_RUNNER} from './reconciled-workflow-fixture.js';
import {CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256} from './reconciled-cross-generator-workflow-reference.js';
import {WORKFLOW_PROTOCOL_CASES_DEFINITION_SHA256} from './reconciled-workflow-protocol-cases.js';

export const CROSS_GENERATOR_WORKFLOW_OBSERVER_SHA256='6721565f576c867632a847c6171260bf391c7c1810ff2f275206d0e3e2267c32';
/** Private actual ESM observation. No expected-answer values or generated-code rewrites. */
export const CROSS_GENERATOR_WORKFLOW_RUNNER=String.raw`
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
import {SourceTextModule,SyntheticModule} from 'node:vm';import {createHash} from 'node:crypto';
const protocolHash='__PROTOCOL__',casesHash='__CASES__';
const fail=s=>{throw Error('WORKFLOW_ESM_OBSERVER:'+s);};
const canonical=v=>JSON.stringify(v===null||typeof v!=='object'?v:Array.isArray(v)?v.map(normal):normal(v));
function normal(v){return v===null||typeof v!=='object'?v:Array.isArray(v)?v.map(normal):Object.fromEntries(Object.keys(v).sort().map(k=>[k,normal(v[k])]));}
const hash=v=>createHash('sha256').update(v).digest('hex');
const data=(v,k)=>{const p=Object.getOwnPropertyDescriptor(v,k);if(!p||!Object.hasOwn(p,'value'))fail('data descriptor');return p.value;};
function expand(recipes,id){
 let visits=0;const active=new Set();
 const read=(r,depth=0)=>{
  if(++visits>65536||depth>64)fail('recipe capacity');
  if(r.tag==='ref'){const i=Number(r.value);if(!Number.isSafeInteger(i)||i<0||i>=recipes.length||active.has(i))fail('recipe link');active.add(i);const v=read(recipes[i],depth);active.delete(i);return v;}
  return {...r,...(r.base?{base:read(r.base,depth+1)}:{}),...(r.input?{input:read(r.input,depth+1)}:{}),...(r.payload?{payload:read(r.payload,depth+1)}:{}),
   ...(r.items?{items:r.items.map(v=>read(v,depth+1))}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,read(v,depth+1)]))}:{})};
 };
 return read({tag:'ref',value:String(id)});
}
`.replace('__PROTOCOL__',CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256).replace('__CASES__',WORKFLOW_PROTOCOL_CASES_DEFINITION_SHA256)+WORKFLOW_FIXTURE_RUNNER+String.raw`
export async function createWorkflowNativeObserver(first,root){
 if(first.protocol_sha256!==protocolHash||first.cases_definition_sha256!==casesHash||!Array.isArray(first.rows)||first.rows.length!==1)fail('profile');
 const row=first.rows[0],withoutCases=({cases,...r})=>r,metadata=canonical(withoutCases(row)),controls=first.controls_sha256;
 if(row.adapter!=='workflow-protocol'||!Array.isArray(row.modules)||!row.modules.length||row.modules.length>8192||!Array.isArray(row.batches)||!row.batches.length||row.batches.length>4)fail('family');
 let total=0;for(const [i,b] of row.batches.entries()){if(b.index!==i||b.start!==total||!Number.isInteger(b.count)||b.count<1||b.count>4096)fail('batch plan');total+=b.count;}
 if(total>16384)fail('case capacity');
 const modules=new Map(row.modules.map(m=>[m.relative_path,m]));if(modules.size!==row.modules.length)fail('duplicate module');
 root=path.resolve(root);if(fs.realpathSync(root)!==root)fail('native root');
 const safe=p=>{if(typeof p!=='string'||!p.endsWith('.ts')||path.posix.normalize(p)!==p||p.startsWith('../')||path.isAbsolute(p)||p.includes('\\'))fail('module path');
  const f=path.join(root,p.replace(/\.ts$/,'.js'));if(fs.realpathSync(f)!==f)fail('symbolic module');return f;};
 const owned=new WeakMap(),loaded=new Map(),facades=new Map();let active=null,nextBatch=0,nextCase=0,totalCalls=0,broken=false;
 const bind=(value,id)=>{if(value!==null&&(typeof value==='object'||typeof value==='function')&&!owned.has(value))owned.set(value,id);return value;};
 const inspect=(value,identities=false,frozen=false)=>{
  let visits=0;const ancestors=new Set();
  const walk=(v,depth=0)=>{
   if(++visits>65536||depth>64)fail('value capacity');
   if(identities&&v!==null&&(typeof v==='object'||typeof v==='function')&&owned.has(v))return ['identity',owned.get(v)];
   if(v===null)return ['null'];if(typeof v==='bigint')return ['bigint',String(v)];
   if(typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return [typeof v,v];
   if(!v||typeof v!=='object'||ancestors.has(v)||frozen&&!Object.isFrozen(v))fail('inert frozen value');
   ancestors.add(v);const descriptors=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(descriptors);let result;
   if(Array.isArray(v)){
    const length=descriptors.length.value;if(Object.getPrototypeOf(v)!==Array.prototype||keys.length!==length+1)fail('array shape');
    result=['array',Array.from({length},(_,i)=>{const p=descriptors[i];if(!p?.enumerable||!Object.hasOwn(p,'value'))fail('array descriptor');return walk(p.value,depth+1);})];
   }else{
    if(![Object.prototype,null].includes(Object.getPrototypeOf(v))||keys.some(k=>typeof k!=='string'))fail('record shape');
    result=['record',keys.sort().map(k=>{const p=descriptors[k];if(!p.enumerable||!Object.hasOwn(p,'value'))fail('record descriptor');return [k,walk(p.value,depth+1)];})];
   }ancestors.delete(v);return result;
  };return walk(value);
 };
 const start=(provider,role,method,occurrence,args)=>{
  if(!active||++totalCalls>65536)fail('call state/capacity');
  const index=active.calls.length;
  const arguments_=method==='capture'&&args.length===1&&Object.is(args[0],active.input)?['array',[['source-input',active.id]]]:inspect(args,true);
  const call={provider,role,method,occurrence,arity:args.length,arguments:arguments_,awaited:role==='operation',result:null};active.calls.push(call);
  return {call,index,id:active.id};
 };
 const finish=(entry,value)=>{
  const tagged=inspect(value,false,true);bind(value,'return:'+entry.id+':'+entry.index);
  if(entry.call.role==='operation'&&data(value,'status')==='committed')bind(data(value,'value'),'operation-value:'+entry.id+':'+entry.index);
  entry.call.result={kind:'value',value:inspect(value,true),data_sha256:hash(canonical(tagged)),deep_frozen:true};
  return value;
 };
 const rejected=(entry,error)=>{entry.call.result={kind:'error',name:error?.name??'Error'};throw error;};
 const sync=(method,occurrence,original,receiver,args)=>{
  if(method==='step.arguments')active.lastStep=occurrence;
  const entry=start(row.selector,'material',method,occurrence,args);
  try{return finish(entry,Reflect.apply(original,receiver,args));}catch(error){return rejected(entry,error);}
 };
 const operation=(selector,original)=>(...args)=>{
  const entry=start(selector,'operation','execute',active.lastStep,args);
  let promise;try{promise=Reflect.apply(original,undefined,args);}catch(error){return rejected(entry,error);}
  if(!promise||typeof promise.then!=='function')fail('Operation promise');
  return promise.then(value=>finish(entry,value),error=>rejected(entry,error));
 };
 const methodTable=(table,method)=>{
  if(!Object.isFrozen(table))fail('material table freeze');
  const descriptors=Object.getOwnPropertyDescriptors(table);
  for(const id of Object.keys(descriptors)){
   const original=descriptors[id].value;if(!original||!Object.isFrozen(original))fail('material entry');
   const d=Object.getOwnPropertyDescriptors(original),fn=data(original,'arguments');
   d.arguments={...d.arguments,value:(...args)=>sync(method,id,fn,original,args)};
   descriptors[id]={...descriptors[id],value:Object.freeze(Object.create(Object.getPrototypeOf(original),d))};
  }return Object.freeze(Object.create(Object.getPrototypeOf(table),descriptors));
 };
 async function facade(p,native){
  if(facades.has(p))return facades.get(p);
  const m=modules.get(p),names=Object.keys(native.namespace),exports=Object.fromEntries(names.map(k=>[k,data(native.namespace,k)]));
  if(p===row.material_path){
   for(const key of ['capture','captureResult','result']){const original=exports[key];if(typeof original!=='function')fail('material export');exports[key]=(...args)=>sync(key,key==='captureResult'?args[1]:null,original,undefined,args);}
   exports.steps=methodTable(exports.steps,'step.arguments');exports.compensations=methodTable(exports.compensations,'compensation.arguments');
  }else{
   const forward=row.forward.find(o=>o.relative_path===p);if(!forward)fail('facade scope');
   const original=exports[forward.callable];if(typeof original!=='function'||!Object.isFrozen(original))fail('Operation wrapper');
   const fn=operation(forward.selector,original);Object.defineProperty(fn,'descriptor',Object.getOwnPropertyDescriptor(original,'descriptor'));exports[forward.callable]=Object.freeze(fn);
  }
  const result=new SyntheticModule(names,function(){for(const k of names)this.setExport(k,exports[k]);},{identifier:'facade:'+p});
  await result.link(()=>fail('facade import'));await result.evaluate();facades.set(p,result);return result;
 }
 async function load(p,stack=[]){
  if(stack.includes(p))fail('cyclic module graph');if(loaded.has(p))return loaded.get(p);
  const work=(async()=>{
   const m=modules.get(p);if(!m)fail('foreign module');
   const module=new SourceTextModule(fs.readFileSync(safe(p),'utf8'),{identifier:p,importModuleDynamically:()=>fail('dynamic import')});
   await module.link(async spec=>{
    const i=m.imports.find(i=>!i.type_only&&i.specifier===spec);if(!i)fail('undeclared import');
    if(i.target_path===null){
     if(p!==row.provider_path||spec!=='node:crypto')fail('external import');
     const crypto=new SyntheticModule(['createHash'],function(){this.setExport('createHash',createHash);});await crypto.link(()=>fail('crypto import'));await crypto.evaluate();return crypto;
    }
    const native=await load(i.target_path,[...stack,p]);
    return p===row.provider_path&&(i.target_path===row.material_path||row.forward.some(o=>o.relative_path===i.target_path))?facade(i.target_path,native):native;
   });
   await module.evaluate({timeout:1000});
   if(canonical(Object.keys(module.namespace).sort())!==canonical([...m.value_exports].sort()))fail('native exports');
   return module;
  })();loaded.set(p,work);return work;
 }
 const wrapper=await load(row.relative_path),provider=await load(row.provider_path),material=await load(row.material_path),fn=data(wrapper.namespace,row.callable);
 const identity={workflow:fn===data(provider.namespace,'execute'),operations:[]};
 for(const o of row.forward){const w=await load(o.relative_path),p=await load(o.provider_path);identity.operations.push({selector:o.selector,original:data(w.namespace,o.callable)===data(p.namespace,'execute')});}
 const descriptor=data(fn,'descriptor'),material_descriptor=data(material.namespace,'descriptor');
 return Object.freeze({
  async consume(payload){
   try{
    if(broken||payload.controls_sha256!==controls||payload.protocol_sha256!==protocolHash||payload.cases_definition_sha256!==casesHash||payload.rows?.length!==1||Buffer.byteLength(canonical(payload))>8388608)fail('batch envelope');
    const selected=payload.rows[0],batch=row.batches[nextBatch];
    if(!batch||canonical(payload.batch)!==canonical(batch)||canonical(withoutCases(selected))!==metadata||selected.cases.length!==batch.count)fail('batch identity/order');
    const cases=[];
    for(const c of selected.cases){
     if(c.id!=='case-'+nextCase++)fail('case identity/order');
     active={id:c.id,calls:[],input:undefined,lastStep:null};
     const data={...c.data,input:expand(row.recipes,c.data.input),steps:c.data.steps.map(s=>({...s,reads:s.reads.map(r=>({...r,value:expand(row.recipes,r.value)}))}))};
     const invoke=(input,ids,deps)=>{active.input=input;for(const o of row.forward)bind(dataDescriptor(deps,o.selector),'dependency:'+c.id+':'+o.selector);return fn(input,ids,deps);};
     const semantic=await observeWorkflowFixture(invoke,row.steps,data);
     cases.push({id:c.id,calls:active.calls,semantic_sha256:hash(canonical(semantic))});active=null;
    }
    nextBatch++;const result={controls_sha256:controls,selector:row.selector,identity,descriptor,material_descriptor,batch,cases};
    if(Buffer.byteLength(canonical(result))>8388608)fail('batch output capacity');return result;
   }catch(error){broken=true;active=null;throw error;}
  },
  finish(){if(broken||nextBatch!==row.batches.length||nextCase!==total)fail('incomplete family');return {selector:row.selector,batches:nextBatch,cases:nextCase};}
 });
}
const dataDescriptor=data;
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const manifest=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 if(!Array.isArray(manifest)||manifest.length<1||manifest.length>4)fail('manifest');
 const read=p=>{const bytes=fs.readFileSync(p);if(bytes.length>8388608)fail('batch input capacity');return JSON.parse(bytes);};
 const first=read(manifest[0]),observer=await createWorkflowNativeObserver(first,process.argv[3]);
 for(const [index,file] of manifest.entries())console.log(JSON.stringify(await observer.consume(index===0?first:read(file))));
 observer.finish();
}
`;
