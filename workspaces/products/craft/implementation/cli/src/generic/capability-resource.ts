/** Original installed-resource owner. Loading is an explicit trusted native-code
 * action; compilation only emits the selection. This is not a JavaScript sandbox.
 * First profile: self-contained UTF8 ESM packages, local static imports and the
 * listed builtins only. External dependencies/provider effects await M00/G01.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import {lstatSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import {registerHooks} from 'node:module';
import {fileURLToPath} from 'node:url';
import {types} from 'node:util';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {readCorePhysicalFile,pinCorePhysicalCaptures,pinCoreImplementation,type CorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import {captureJson,captureSchemaJson,dataDigest} from '../profile-engine/contracts.js';
import {inventoryGeneratedModule} from '../generation/generated-module-surface.js';
import type {GenericCapabilityRealizationV1,GenericCapabilityBoundsV1} from './capability-data-v1.js';

const at={path:'generic-capability-resource',start:0,end:0};
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['../commerce/commerce-core-physical'+ext,'../generation/generated-module-surface'+ext,'../profile-engine/contracts'+ext]);
const abi='craft.native-capability-resource/v1' as const;
const builtins=new Set(['node:assert/strict','node:buffer','node:crypto','node:util']);
const operations=new Set(['text.generate','text.structured','vector.embed','agent.run','document.parse','search.query']);
const boundKeys=['deadline_ms','max_input_bytes','max_items','max_model_attempts','max_output_bytes','max_tool_calls'] as const;
export interface GenericCapabilityResourceHandle {readonly kind:'original-capability-resource/v1'}
export interface GenericCapabilityProviderLineage {readonly resource_ref:string;readonly [key:string]:string}
export interface GenericCapabilityToolBroker {invoke(name:string,input:Uint8Array):Promise<Uint8Array>}
export interface GenericCapabilityToolSchema {readonly name:string;readonly argument_schema:unknown;readonly result_schema:unknown}
export interface GenericCapabilityResourceRequest {
 readonly operation:string;readonly input:Uint8Array;readonly result_schema:unknown;readonly limits:GenericCapabilityBoundsV1;
 /** Source dispatcher derives these from the selected original Query Entries. */
 readonly tool_schemas?:readonly GenericCapabilityToolSchema[];
 /** Absolute wall clock deadline, bounded by selected duration. */
 readonly deadline_ms:number;readonly signal?:AbortSignal;readonly toolBroker?:GenericCapabilityToolBroker;
}
export interface GenericNativeCapabilityResource {
 readonly abi:typeof abi;readonly operations:readonly string[];readonly capabilities:readonly string[];
 /** The sole selected harness, required only for agent.run. */
 readonly harness_owner?:string;
 invoke(request:GenericCapabilityResourceRequest):Promise<Uint8Array>|Uint8Array;
 dispose?():Promise<void>|void;
}

function absolute(root:string){if(typeof root!=='string'||!path.isAbsolute(root)||path.normalize(root)!==root||root.endsWith('/')||/[\\\u0000-\u001f\u007f]/.test(root))fail('InvalidContract',at,'normalized explicit absolute consumer/package root required');}
function portable(p:string){return typeof p==='string'&&p.length>0&&p.length<=4096&&!/[\\%?#\u0000-\u001f\u007f]/.test(p)&&p.split('/').every(v=>v!==''&&v!=='.'&&v!=='..');}
function packagePaths(root:string):string[]{
 absolute(root);const out:string[]=[];let directories=0;
 const walk=(relative:string,depth:number)=>{
  if(depth>16||++directories>256)fail('ResourceLimit',at,'bounded package directory inventory required');
  const dir=path.join(root,relative),stat=lstatSync(dir);if(!stat.isDirectory()||stat.isSymbolicLink())fail('InvalidContract',at,'nonsymlink package directories required');
  for(const name of readdirSync(dir).sort()){
   if(!portable(name)||name==='node_modules')fail('UnsupportedCapability',at,'self-contained portable package without nested dependencies required');
   const rel=relative?relative+'/'+name:name,s=lstatSync(path.join(root,rel));
   if(s.isSymbolicLink()||!s.isFile()&&!s.isDirectory())fail('InvalidContract',at,'package symlink/nonregular member rejected');
   if(s.isDirectory())walk(rel,depth+1);else {out.push(rel);if(out.length>256)fail('ResourceLimit',at,'package file inventory limit');}
  }
 };walk('',0);return out.sort();
}
function capturePackage(root:string){
 const paths=packagePaths(root),files=paths.map(p=>readCorePhysicalFile(path.join(root,p),16777216));
 if(files.reduce((n,f)=>n+f.file.bytes,0)>16777216)fail('ResourceLimit',at,'16MiB self-contained package byte limit');
 const inventory=files.map((f,i)=>({path:paths[i]!,sha256:f.file.sha256,bytes:f.file.bytes}));
 const physical=pinCorePhysicalCaptures(files),sha256=dataDigest({schema_version:'craft.native-capability-package-bytes/v1',files:inventory});
 const assertCurrent=()=>{pin.assertCurrent();physical.assertCurrent();if(dataDigest(packagePaths(root))!==dataDigest(paths))fail('StaleOwner',at,'installed package inventory changed');physical.assertCurrent();};assertCurrent();
 return {files:new Map(paths.map((p,i)=>[p,files[i]!])),inventory,sha256,assertCurrent};
}
/** Descriptor implementation.sha256 is dataDigest of this exact sorted portable
 * {schema_version,files:[{path,sha256,bytes}]} inventory, including package.json.
 * No absolute paths, timestamps, filesystem identities or exclusions enter it. */
export function captureGenericCapabilityPackage(packageRoot:string){const c=capturePackage(packageRoot);return coreFreeze({sha256:c.sha256,files:c.inventory});}

function staticClosure(files:Map<string,CorePhysicalFile>,entry:string){
 const seen=new Set<string>(),edges=new Map<string,Map<string,string>>();
 const visit=(relative:string)=>{
  if(seen.has(relative))return;seen.add(relative);
  if(!portable(relative)||!['.mjs','.js'].includes(path.posix.extname(relative)))fail('UnsupportedCapability',at,'static local JavaScript ESM files required');
  const file=files.get(relative);if(!file)fail('InvalidContract',at,'selected module/import absent from pinned package');
  // Conservative restrictions for this first trusted-native profile. Escaped
  // identifiers, ambient loaders and dynamic code are unsupported, not audited.
  if(/\\u|\b(?:require|createRequire|eval|Function|process|globalThis|global|fetch|WebSocket|Worker)\b/.test(file.text))fail('UnsupportedCapability',at,'ambient/dynamic loader outside supported static resource profile');
  let surface:ReturnType<typeof inventoryGeneratedModule>;try{surface=inventoryGeneratedModule(file.text);}catch{return fail('UnsupportedCapability',at,'unsupported or dynamic resource module syntax');}
  const imports=new Map<string,string>();edges.set(relative,imports);
  for(const item of surface.imports){
   const spec=item.specifier;if(item.type_only)fail('UnsupportedCapability',at,'native JavaScript imports only');
   if(builtins.has(spec)){imports.set(spec,spec);continue;}
   if(!spec.startsWith('./')&&!spec.startsWith('../')||/[\\%?#\u0000-\u001f\u007f]/.test(spec))fail('UnsupportedCapability',at,'unselected bare/private/absolute resource import');
   const next=path.posix.normalize(path.posix.join(path.posix.dirname(relative),spec));
   if(!portable(next))fail('UnsupportedCapability',at,'resource import escapes selected package');
   imports.set(spec,next);visit(next);
  }
 };visit(entry);return edges;
}
function checkTime(deadline:number,signal?:AbortSignal){if(signal!==undefined&&!(signal instanceof AbortSignal))fail('InvalidContract',at,'actual AbortSignal required');if(signal?.aborted)fail('StaleOwner',at,'capability invocation cancelled');if(!Number.isSafeInteger(deadline)||Date.now()>=deadline)fail('StaleOwner',at,'capability invocation deadline expired');}
/** Bounds yielding native work; it cannot preempt synchronous trusted code or
 * prove no effect. Late settlement is observed and discarded. Abandoning native
 * work quarantines its resource so callers cannot dispatch another attempt. */
function boundedAwait<T>(work:()=>T|PromiseLike<T>,deadline:number,signal:AbortSignal|undefined,abandon:()=>void):Promise<T>{
 checkTime(deadline,signal);
 let pending:Promise<T>;try{pending=Promise.resolve(work());}catch(error){checkTime(deadline,signal);throw error;}
 return new Promise<T>((resolve,reject)=>{
  let done=false,timer:ReturnType<typeof setTimeout>|undefined;
  const cleanup=()=>{if(timer!==undefined)clearTimeout(timer);signal?.removeEventListener('abort',cancel);};
  const expired=()=>{if(done)return;done=true;cleanup();abandon();try{checkTime(deadline,signal);fail('StaleOwner',at,'native resource wait abandoned');}catch(error){reject(error);}};
  const cancel=()=>expired();
  const arm=()=>{if(done)return;const remaining=deadline-Date.now();if(remaining<=0){expired();return;}timer=setTimeout(arm,Math.min(remaining,2147483647));};
  pending.then(value=>{if(done)return;try{checkTime(deadline,signal);}catch{expired();return;}done=true;cleanup();resolve(value);},error=>{if(done)return;try{checkTime(deadline,signal);}catch{expired();return;}done=true;cleanup();reject(error);});
  signal?.addEventListener('abort',cancel,{once:true});if(signal?.aborted||Date.now()>=deadline)expired();else arm();
 });
}
function checkBounds(raw:GenericCapabilityBoundsV1,maximum?:GenericCapabilityBoundsV1){
 const b=captureJson(raw) as unknown as GenericCapabilityBoundsV1;
 if(!b||Object.keys(b).sort().join(',')!==boundKeys.join(',')||boundKeys.some(k=>!Number.isSafeInteger(b[k])||b[k]<0||maximum&&b[k]>maximum[k])||b.deadline_ms<1||b.max_input_bytes<1||b.max_output_bytes<1||b.max_items<1)fail('InvalidContract',at,'finite bounds must narrow selected realization');return b;
}
function frozenInstance(raw:unknown,realization:GenericCapabilityRealizationV1):GenericNativeCapabilityResource {
 if(!raw||typeof raw!=='object'||types.isProxy(raw)||!Object.isFrozen(raw))fail('InvalidContract',at,'one frozen native resource instance required');
 const ds=Object.getOwnPropertyDescriptors(raw),keys=Reflect.ownKeys(ds);
 if(![Object.prototype,null].includes(Object.getPrototypeOf(raw))||['abi','operations','capabilities','invoke'].some(k=>!ds[k])||keys.some(k=>typeof k!=='string'||!['abi','operations','capabilities','harness_owner','invoke','dispose'].includes(k)||!Object.hasOwn(ds[k]??{},'value')))fail('InvalidContract',at,'closed inert native resource ABI required');
 const v=raw as GenericNativeCapabilityResource;
 if(v.abi!==abi||typeof v.invoke!=='function'||v.dispose!==undefined&&typeof v.dispose!=='function'||dataDigest(v.operations)!==dataDigest(realization.operations)||dataDigest(v.capabilities)!==dataDigest(realization.capabilities))fail('InvalidContract',at,'native resource support must exactly match selected descriptor');
 if(realization.contract==='agent-run/v1'?v.harness_owner!==realization.target.model_or_harness:v.harness_owner!==undefined)fail('InvalidContract',at,'exactly one selected agent harness owner required');return v;
}

/** INTERNAL: the source-bound public dispatcher owns calls to this factory.
 * Its handle records loaded bytes/selection, never actor or release authority. */
export function createGenericCapabilityResourceOwner(consumerRoot:string){
 absolute(consumerRoot);pin.assertCurrent();
 type Row={realization:GenericCapabilityRealizationV1;lineage:GenericCapabilityProviderLineage;capture:ReturnType<typeof capturePackage>;instance:GenericNativeCapabilityResource;closed:boolean;active:boolean;abandoned:boolean};
 const rows=new WeakMap<object,Row>(),retired=new WeakSet<object>(),resources=new Set<string>();
 const row=(h:GenericCapabilityResourceHandle)=>{const r=h&&typeof h==='object'?rows.get(h):undefined;if(!r||r.closed)fail('ForeignOwner',at,'live original resource handle required');if(r.abandoned)fail('StaleOwner',at,'abandoned native resource remains quarantined; no repeated dispatch');r.capture.assertCurrent();return r;};
 const owner=Object.freeze({
  async load(raw:GenericCapabilityRealizationV1,providerLineage:GenericCapabilityProviderLineage,expectedTarget:GenericCapabilityRealizationV1['target']=raw.target,options:{deadline_ms?:number;signal?:AbortSignal}={}):Promise<GenericCapabilityResourceHandle>{
   pin.assertCurrent();const realization=captureJson(raw) as unknown as GenericCapabilityRealizationV1,lineage=captureJson(providerLineage) as unknown as GenericCapabilityProviderLineage;
   // Selected target mismatch is checked before touching the consumer filesystem.
   if(dataDigest(realization.target)!==dataDigest(expectedTarget))fail('InvalidContract',at,'runtime target differs from exact selected destination/API/model/revision');
   const impl=realization.implementation;
   if(!impl||!/^(@[a-z0-9][a-z0-9._-]*\/)?[a-z0-9][a-z0-9._-]*$/.test(impl.package)||!/^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(impl.version)||!/^[a-f0-9]{64}$/.test(impl.sha256)||!(impl.export==='.'||impl.export.startsWith('./')&&portable(impl.export.slice(2))))fail('InvalidContract',at,'exact npm package/version/portable export/byte digest required');
   checkBounds(realization.bounds);
   if(!Array.isArray(realization.operations)||!realization.operations.length||new Set(realization.operations).size!==realization.operations.length||realization.operations.some(op=>!operations.has(op))||!Array.isArray(realization.capabilities)||!['fixture','provider'].includes(realization.mode))fail('InvalidContract',at,'closed finite resource support required');
   const kind=realization.contract,allowed=kind==='agent-run/v1'?['agent.run']:kind==='inference/v1'?['text.generate','text.structured','vector.embed']:kind==='document/v1'?['document.parse']:kind==='search/v1'?['search.query']:[];
   if(realization.operations.some(op=>!allowed.includes(op))||!lineage?.resource_ref||Object.values(lineage).some(v=>typeof v!=='string'||!v)||resources.has(lineage.resource_ref))fail('InvalidContract',at,'one noncompeting selected resource and matching contract required');
   if(realization.lifecycle.fallback!=='none'||realization.lifecycle.compatibility!=='exact-contract-and-target'||realization.lifecycle.completion!=='validated-proposal-only'||realization.lifecycle.unknown_effect!=='reconcile-before-retry')fail('UnsupportedCapability',at,'selected no-fallback lifecycle required');
   const signal=options.signal,deadline=options.deadline_ms??Date.now()+realization.bounds.deadline_ms;checkTime(deadline,signal);
   if(deadline-Date.now()>realization.bounds.deadline_ms)fail('InvalidContract',at,'load deadline exceeds selected bound');
   if(realization.mode!=='fixture')fail('UnsupportedCapability',at,'provider loading/activation requires original M00/G01 execution owners');
   resources.add(lineage.resource_ref);
   let instance:GenericNativeCapabilityResource|undefined,abandoned=false;
   try{
    const root=path.join(consumerRoot,'node_modules',impl.package),capture=capturePackage(root);
    if(capture.sha256!==impl.sha256)fail('StaleOwner',at,'installed package byte inventory differs from selected digest');
    const packageFile=capture.files.get('package.json');if(!packageFile)fail('InvalidContract',at,'selected installed package manifest missing');
    const manifest=parseCoreCommerceJson(packageFile.text,'package.json') as Record<string,unknown>;
    if(manifest.name!==impl.package||manifest.version!==impl.version||manifest.type!=='module')fail('InvalidContract',at,'installed exact package name/version and ESM type required');
    if(manifest.private!==undefined&&manifest.private!==false)fail('UnsupportedCapability',at,'private installed capability packages cannot supply public consumer resources');
    for(const key of ['dependencies','optionalDependencies','peerDependencies','bundledDependencies','bundleDependencies'])if(manifest[key]!==undefined&&Object.keys(manifest[key] as object).length)fail('UnsupportedCapability',at,'transitive package dependencies unsupported in first resource profile');
    if([...capture.files.keys()].some(p=>p!=='package.json'&&p.endsWith('/package.json')))fail('UnsupportedCapability',at,'nested module package identities unsupported');
    const exports=manifest.exports;let selected=typeof exports==='string'&&impl.export==='.'?exports:exports&&typeof exports==='object'&&!Array.isArray(exports)?(exports as Record<string,unknown>)[impl.export]:undefined;
    if(selected===undefined&&impl.export==='.'&&exports&&typeof exports==='object'&&!Array.isArray(exports)&&Object.keys(exports).every(k=>!k.startsWith('.')))selected=exports;
    if(selected&&typeof selected==='object'&&!Array.isArray(selected)){
     const branches=selected as Record<string,unknown>;if(Object.keys(branches).some(k=>!['import','types'].includes(k)))fail('UnsupportedCapability',at,'ambiguous or unsupported conditional resource export');selected=branches.import;
    }
    if(typeof selected!=='string'||!selected.startsWith('./')||!portable(selected.slice(2)))fail('InvalidContract',at,'one exact explicit installed resource export required');
    const entry=selected.slice(2),edges=staticClosure(capture.files,entry),prefix='craft-capability://'+randomUUID()+'/',urls=new Map([...edges.keys()].map(rel=>[prefix+rel,rel]));
    capture.assertCurrent();checkTime(deadline,signal);
    const hooks=registerHooks({
     resolve(specifier,context,next){
      if(urls.has(specifier))return {url:specifier,format:'module',shortCircuit:true};
      const parent=context.parentURL&&urls.get(context.parentURL);
      if(parent){capture.assertCurrent();const target=edges.get(parent)!.get(specifier);if(!target)fail('UnsupportedCapability',at,'module request outside verified static import closure');return {url:builtins.has(target)?target:prefix+target,format:builtins.has(target)?'builtin':'module',shortCircuit:true};}
      return next(specifier,context);
     },
     load(url,context,next){const rel=urls.get(url);if(rel){capture.assertCurrent();return {format:'module',source:capture.files.get(rel)!.text,shortCircuit:true};}return next(url,context);},
    });
    let module:Record<string,unknown>;try{module=await boundedAwait(()=>import(prefix+entry),deadline,signal,()=>{abandoned=true;}) as Record<string,unknown>;}finally{hooks.deregister();}
    capture.assertCurrent();checkTime(deadline,signal);
    if(Object.keys(module).join(',')!=='createCapabilityResource'||typeof module.createCapabilityResource!=='function')fail('InvalidContract',at,'one createCapabilityResource export required');
    const factory=module.createCapabilityResource;
    const created=await boundedAwait(()=>factory(coreFreeze({abi,realization,provider_lineage:lineage,target:realization.target})),deadline,signal,()=>{abandoned=true;});
    capture.assertCurrent();checkTime(deadline,signal);instance=frozenInstance(created,realization);
    const h=Object.freeze({kind:'original-capability-resource/v1' as const});rows.set(h,{realization,lineage,capture,instance,closed:false,active:false,abandoned:false});return h;
   }catch(error){if(!abandoned)resources.delete(lineage.resource_ref);throw error;}
  },
  inspect(h:GenericCapabilityResourceHandle){const r=row(h);return coreFreeze({abi,realization:r.realization,provider_lineage:r.lineage,package_sha256:r.capture.sha256,files:r.capture.inventory,qualification:r.realization.mode==='fixture'?'local-fixture-native-execution':'provider-execution-unqualified',authority_effect:'none'});},
  assertCurrent(h:GenericCapabilityResourceHandle){row(h);},
  async invoke(h:GenericCapabilityResourceHandle,request:GenericCapabilityResourceRequest):Promise<Uint8Array>{
   const r=row(h),limits=checkBounds(request.limits,r.realization.bounds),deadline=request.deadline_ms,signal=request.signal,broker=request.toolBroker,operation=request.operation;checkTime(deadline,signal);
   if(r.active)fail('InvalidContract',at,'one active invocation per selected resource');
   if(r.realization.mode!=='fixture')fail('UnsupportedCapability',at,'provider invocation requires original M00/G01 execution owners');
   if(!r.realization.operations.includes(operation as typeof r.realization.operations[number])||!types.isUint8Array(request.input)||request.input.byteLength>limits.max_input_bytes||deadline-Date.now()>limits.deadline_ms)fail('InvalidContract',at,'invocation must narrow selected operation/input/deadline');
   const agent=operation==='agent.run';
   if(!agent&&(broker!==undefined||request.tool_schemas!==undefined||limits.max_tool_calls!==0||limits.max_model_attempts!==1&&r.realization.contract==='inference/v1'))fail('UnsupportedCapability',at,'direct invocation cannot supply tools or an agent loop');
   if(agent&&(limits.max_model_attempts<1||limits.max_tool_calls>0&&!broker||broker!==undefined&&(!r.realization.capabilities.includes('readonly-tools')||typeof broker.invoke!=='function')))fail('UnsupportedCapability',at,'selected harness tools require original read-only mediation');
   const toolSchemas=request.tool_schemas===undefined?undefined:captureSchemaJson(request.tool_schemas) as unknown as readonly GenericCapabilityToolSchema[];
   const jsonSchema=(v:unknown)=>typeof v==='boolean'||!!v&&typeof v==='object'&&!Array.isArray(v);
   if(toolSchemas!==undefined&&(!Array.isArray(toolSchemas)||toolSchemas.length>32||toolSchemas.some(t=>!t||Object.keys(t).sort().join(',')!=='argument_schema,name,result_schema'||typeof t.name!=='string'||t.name.length>256||!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(t.name)||!jsonSchema(t.argument_schema)||!jsonSchema(t.result_schema))||new Set(toolSchemas.map(t=>t.name)).size!==toolSchemas.length))fail('InvalidContract',at,'at most 32 distinct closed named tool schema declarations required');
   if(toolSchemas?.length&&(!broker||!r.realization.capabilities.includes('readonly-tools')))fail('UnsupportedCapability',at,'declared tool schemas require selected read-only mediation');
   const toolNames=toolSchemas===undefined?undefined:new Set(toolSchemas.map(t=>t.name));
   const schema=captureSchemaJson(request.result_schema),input=new Uint8Array(request.input),invokeTool=broker?.invoke.bind(broker),fresh=()=>{row(h);checkTime(deadline,signal);};let calls=0,active=true;
   const abandon=()=>{r.abandoned=true;active=false;};
   const tools=invokeTool?Object.freeze({invoke(name:string,wire:Uint8Array){const pending=(async()=>{fresh();if(!active||typeof name!=='string'||!name||toolNames&&!toolNames.has(name)||!types.isUint8Array(wire)||wire.byteLength>limits.max_input_bytes||++calls>limits.max_tool_calls)fail('InvalidContract',at,'bounded active declared read-only harness tool invocation required');const output=await boundedAwait(()=>invokeTool(name,new Uint8Array(wire)),deadline,signal,abandon);fresh();if(!active||!types.isUint8Array(output)||output.byteLength>limits.max_output_bytes)fail('InvalidContract',at,'bounded active read-only tool result required');return new Uint8Array(output);})();void pending.catch(()=>{});return pending;}}):undefined;
   const nativeRequest={operation,input,result_schema:schema,limits,deadline_ms:deadline,...(signal?{signal}:{}),...(tools?{toolBroker:tools}:{}),...(toolSchemas!==undefined?{tool_schemas:toolSchemas}:{})};
   r.active=true;
   try{fresh();const output=await boundedAwait(()=>r.instance.invoke(Object.freeze(nativeRequest)),deadline,signal,abandon);fresh();if(!types.isUint8Array(output)||output.byteLength>limits.max_output_bytes)fail('InvalidContract',at,'bounded raw resource result bytes required');return new Uint8Array(output);}catch(error){if(!r.abandoned)fresh();throw error;}finally{active=false;r.active=false;}
  },
  /** Retire custody even when code/bytes are stale or native work was abandoned.
   * Never run stale/active cleanup. Healthy native cleanup is best effort with a
   * bounded yielding wait; synchronous trusted code remains non-preemptible.
   * Unconfirmed cleanup keeps its resource reference reserved, not reusable. */
  async dispose(h:GenericCapabilityResourceHandle){
   if(h&&typeof h==='object'&&retired.has(h))return;
   const r=h&&typeof h==='object'?rows.get(h):undefined;if(!r)fail('ForeignOwner',at,'original resource handle required for retirement');
   r.closed=true;rows.delete(h);retired.add(h);
   if(r.abandoned||r.active)return;
   try{r.capture.assertCurrent();}catch{return;}
   if(!r.instance.dispose){resources.delete(r.lineage.resource_ref);return;}
   try{
    await boundedAwait(()=>r.instance.dispose!(),Date.now()+Math.min(1000,r.realization.bounds.deadline_ms),undefined,()=>{r.abandoned=true;});
    r.capture.assertCurrent();resources.delete(r.lineage.resource_ref);
   }catch{/* Retirement must not replace the original failure with cleanup failure. */}
  },
 });return owner;
}
