/** Original application/Auth -> checked generated codecs -> explicitly installed
 * native profile -> original source disclosure. Host configuration is trusted
 * operator code; remote callers receive only opaque invocation handles.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {AsyncLocalStorage} from 'node:async_hooks';
import {types} from 'node:util';
import {coreFreeze,coreSha256,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {requireGenericCapabilityGenerationBinding,type GenericCompositionHandle} from './public-sdk.js';
import {requireGenericCapabilityRuntimeBinding} from './execution-session.js';
import type {GenericApplicationRuntime} from './invocation-owner.js';
import type {GenericFixtureActor} from './entry-authorization.js';
import type {GenericGeneratedCodec} from './capability-generation.js';
import {assertGenericNativeProfileArtifact,loadGenericNativeProfileModule,type GenericNativeProfileArtifact} from './native-profile-resource.js';
const ext=import.meta.url.endsWith('.ts')?'.ts':'.js',pin=pinCoreImplementation(import.meta.url,['native-profile-resource'+ext,'capability-generation'+ext,'public-sdk'+ext,'execution-session'+ext,'entry-authorization'+ext,'../profile-engine/contracts'+ext]);
const at={path:'generic-native-capability-host',start:0,end:0};
export interface GenericNativeInvocation {readonly kind:'original-native-capability-invocation/v1'}
type Generation=ReturnType<ReturnType<typeof requireGenericCapabilityGenerationBinding>['generation']>;
type Binding=Generation['plan']['bindings'][number];
type Principal={readonly actor:string;readonly tenant:string;readonly grants_revision:string;readonly authentication_revision:string};
type NativeResource={readonly abi:string;readonly operations:readonly string[];readonly capabilities:readonly string[];readonly harness_owner?:string;invoke(request:unknown):Promise<Uint8Array>|Uint8Array;dispose?():Promise<void>|void};
export interface GenericNativeInvocationView {readonly invocation:GenericNativeInvocation;readonly originalActor:GenericFixtureActor;readonly binding:Binding;readonly entry:string;readonly principal:Principal;readonly input:Uint8Array;readonly value:unknown;readonly deadline_ms:number;readonly signal?:AbortSignal}
export interface GenericNativeProfileConfiguration {
 readonly artifact:GenericNativeProfileArtifact;
 /** Exact source Entry associations selected by the operator's implementation profile. */
 readonly entries:readonly string[];
 /** Configure actual selected module, never a caller-provided native callback. */
 readonly configure:(namespace:Record<string,any>,binding:Binding,getInvocation:()=>GenericNativeInvocationView)=>Promise<NativeResource>|NativeResource;
 /** Original source owner revalidates full dependencies and exact actual sink. */
 readonly assertDisclosure:(invocation:GenericNativeInvocationView,output:Uint8Array)=>Promise<void>|void;
}
export interface GenericNativeCapabilityHostOptions {readonly runtime:GenericApplicationRuntime;readonly bindings:ReadonlyMap<string,GenericNativeProfileConfiguration>}
function bounded<T>(operation:()=>T|PromiseLike<T>,deadline:number,signal?:AbortSignal):Promise<T>{return new Promise((resolve,reject)=>{let done=false;const finish=(error:unknown,value?:T)=>{if(done)return;done=true;clearTimeout(timer);signal?.removeEventListener('abort',abort);error?reject(error):resolve(value!);},abort=()=>{try{fail('StaleOwner',at,'native wait cancelled or expired');}catch(e){finish(e);}},timer=setTimeout(abort,Math.max(1,deadline-Date.now()));signal?.addEventListener('abort',abort,{once:true});if(signal?.aborted){abort();return;}Promise.resolve().then(operation).then(value=>finish(null,value),error=>finish(error));});}
function bytes(wire:Uint8Array,maximum:number){if(types.isProxy(wire)||!types.isUint8Array(wire))fail('InvalidContract',at,'actual native byte input');const p=Object.getPrototypeOf(Uint8Array.prototype),get=(name:string)=>Object.getOwnPropertyDescriptor(p,name)!.get!.call(wire),length=get('byteLength') as number,buffer=get('buffer');if(length>maximum||types.isSharedArrayBuffer(buffer))fail('ResourceLimit',at,'unshared bounded native bytes');const out=new Uint8Array(length);out.set(new Uint8Array(buffer,get('byteOffset'),length));return out;}
export function genericNativeCapabilityIdentity(binding:Binding){return dataDigest({contract_sha256:binding.contract_sha256,realization_sha256:binding.realization_sha256,provider_lineage:binding.provider_lineage,implementation_sha256:binding.realization.implementation.sha256});}
export function createGenericNativeCapabilityHost(composition:unknown,handle:GenericCompositionHandle,options:GenericNativeCapabilityHostOptions){
 const parent=requireGenericCapabilityGenerationBinding(composition,handle),runtime=options.runtime,original=requireGenericCapabilityRuntimeBinding(runtime,composition,handle),generated=parent.generation();
 if(!(options.bindings instanceof Map)||types.isProxy(options.bindings)||options.bindings.size>64)fail('InvalidContract',at,'finite original native profile registrations');
 const configs=new Map([...options.bindings].map(([id,c])=>[id,Object.freeze({...c,entries:Object.freeze([...c.entries])})])),lifetime=new AbortController(),loaded=new Map<string,Promise<{resource:NativeResource;assertCurrent:()=>void;close:()=>void}>>(),decoders=new Map<string,Promise<any>>(),scope=new AsyncLocalStorage<GenericNativeInvocationView>();let closed=false;
 const current=()=>{pin.assertCurrent();if(closed)fail('StaleOwner',at,'native host closed');parent.assertCurrent();original.assertCurrent();for(const c of configs.values())assertGenericNativeProfileArtifact(c.artifact);};current();
 for(const [id,config] of configs){const b=generated.plan.bindings.find(b=>b.id===id);if(!b||!Array.isArray(config.entries)||!config.entries.length||config.entries.length>128||new Set(config.entries).size!==config.entries.length||typeof config.configure!=='function'||typeof config.assertDisclosure!=='function')fail('InvalidContract',at,'checked native binding/Entry/configuration');for(const e of config.entries)runtime.entry(e);}
 type Row={actor:GenericFixtureActor;entry:string;binding:Binding;config:GenericNativeProfileConfiguration;deadline:number;signal?:AbortSignal;retired:boolean};const invocations=new WeakMap<object,Row>();
 const row=(inv:GenericNativeInvocation)=>{current();const r=inv&&typeof inv==='object'?invocations.get(inv):undefined;if(!r||r.retired)fail('ForeignOwner',at,'fresh original native invocation');if(Date.now()>=r.deadline||r.signal?.aborted)fail('StaleOwner',at,'native invocation deadline/cancelled');return r;};
 const rawDecode=async(spec:GenericGeneratedCodec,input:Uint8Array)=>{current();let p=decoders.get(spec.decoder_path);if(!p){const f=generated.files.find(f=>f.relative_path===spec.decoder_path);if(!f||coreSha256(f.content)!==spec.decoder_sha256)fail('InvalidContract',at,'original generated decoder source');p=import('data:text/javascript;base64,'+Buffer.from(f.content).toString('base64'));decoders.set(spec.decoder_path,p);}const codec=await p;current();return codec.decode(input);};
 const decode=async(spec:GenericGeneratedCodec,input:Uint8Array)=>{const result=await rawDecode(spec,input);if(!result?.ok||!types.isUint8Array(result.wire))fail('TypeMismatch',at,'native input/result must satisfy generated business type');return result;};
 const fresh=async(inv:GenericNativeInvocation,inputSha:string):Promise<Principal>=>{const r=row(inv),e=runtime.entry(r.entry),a=await original.authorization.authorize(r.actor,e,inputSha);row(inv);if(!a.ok)fail('ForeignOwner',at,'current original Entry permission required');const f=await original.authorization.consume(a.value);row(inv);if(!f.ok)fail('ForeignOwner',at,'fresh native Auth READY required');try{return original.authorization.capabilityPrincipal(f.value,e);}finally{original.authorization.retire(f.value);}};
 const resource=async(r:Row)=>{let p=loaded.get(r.binding.id);if(!p){p=(async()=>{const module=await bounded(()=>loadGenericNativeProfileModule(r.config.artifact,r.binding.realization),r.deadline,r.signal);current();try{const value=await bounded(()=>r.config.configure(module.namespace,r.binding,()=>{current();const v=scope.getStore();if(!v)fail('ForeignOwner',at,'original active async invocation scope');row(v.invocation);return v;}),r.deadline,r.signal);current();
    if(!value||!Object.isFrozen(value)||value.abi!=='craft.native-capability-resource/v1'||typeof value.invoke!=='function'||dataDigest(value.operations)!==dataDigest(r.binding.realization.operations)||dataDigest(value.capabilities)!==dataDigest(r.binding.realization.capabilities)||r.binding.contract.kind==='agent-run/v1'&&value.harness_owner!==r.binding.realization.target.model_or_harness)fail('InvalidContract',at,'exact selected native resource ABI/capabilities/harness');return {resource:value,assertCurrent:module.assertCurrent,close:module.close};
   }catch(e){module.close();throw e;}})();loaded.set(r.binding.id,p);}return p;};
 const host=Object.freeze({
  inspect(){current();return coreFreeze({schema_version:'craft.checked-native-host/v1',source_sha256:generated.plan.source_sha256,profile_sha256:generated.plan.profile_sha256,bindings:generated.plan.bindings.filter(b=>configs.has(b.id)).map(b=>({id:b.id,capability_sha256:genericNativeCapabilityIdentity(b)})),provider_qualification:'not-established-by-native-registration'});},
  openInvocation(actor:GenericFixtureActor,entry:string,bindingId:string,settings:Readonly<{deadline_ms:number;signal?:AbortSignal}>){current();const b=generated.plan.bindings.find(b=>b.id===bindingId),config=configs.get(bindingId);if(!b||!config||!config.entries.includes(entry))fail('ForeignOwner',at,'profile-declared native binding for this exact Entry');runtime.entry(entry);if(!Number.isSafeInteger(settings.deadline_ms)||settings.deadline_ms<=Date.now()||settings.deadline_ms-Date.now()>b.bounds.deadline_ms||settings.signal!==undefined&&!(settings.signal instanceof AbortSignal))fail('InvalidContract',at,'bounded original invocation controls');const inv=Object.freeze({kind:'original-native-capability-invocation/v1' as const});invocations.set(inv,{actor,entry,binding:b,config,deadline:settings.deadline_ms,signal:AbortSignal.any([lifetime.signal,...(settings.signal?[settings.signal]:[])]),retired:false});return inv;},
  async invoke(inv:GenericNativeInvocation,wire:Uint8Array){const r=row(inv),input=bytes(wire,r.binding.bounds.max_input_bytes);try{let principal=await fresh(inv,coreSha256(input));const checked=await decode(r.binding.input,input),inputSha=coreSha256(checked.wire);row(inv);principal=await fresh(inv,inputSha);const native=await resource(r);row(inv);native.assertCurrent();principal=await fresh(inv,inputSha);
    const view=Object.freeze({invocation:inv,originalActor:r.actor,binding:r.binding,entry:r.entry,principal,input:new Uint8Array(checked.wire),value:checked.value,deadline_ms:r.deadline,...(r.signal?{signal:r.signal}:{})});
    const schema=JSON.parse(generated.files.find(f=>f.relative_path===r.binding.result.schema_path)!.content);
    const raw=await bounded(()=>scope.run(view,()=>native.resource.invoke(Object.freeze({operation:r.binding.contract.operation,input:new Uint8Array(checked.wire),result_schema:schema,limits:r.binding.bounds,deadline_ms:r.deadline,...(r.signal?{signal:r.signal}:{}),decodeResult:async(output:Uint8Array)=>rawDecode(r.binding.result,bytes(output,r.binding.bounds.max_output_bytes))}))),r.deadline,r.signal);
    row(inv);native.assertCurrent();await fresh(inv,inputSha);const result=await decode(r.binding.result,bytes(raw,r.binding.bounds.max_output_bytes));row(inv);await bounded(()=>r.config.assertDisclosure(view,result.wire),r.deadline,r.signal);row(inv);await fresh(inv,inputSha);return Object.freeze({ok:true as const,value:result.value,wire:new Uint8Array(result.wire),binding:r.binding.id,contract:r.binding.contract.kind,qualification:'checked-native-local-execution;provider-qualification-separate'});
   }finally{r.retired=true;}},
  assertCurrent:current,
  async close(){if(closed)return;closed=true;lifetime.abort();const resources=await Promise.allSettled([...loaded.values()]);for(const r of resources)if(r.status==='fulfilled')try{await r.value.resource.dispose?.();}finally{r.value.close();}},
 });return host;
}
