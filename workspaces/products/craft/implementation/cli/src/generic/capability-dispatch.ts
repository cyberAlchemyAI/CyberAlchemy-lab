/** Source-bound generated native dispatch. The original composition remains the
 * only application owner; native resources and Query authority stay opaque.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {types} from 'node:util';
import {coreFreeze,CoreCommerceSourceError,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {readCorePhysicalFile,pinCorePhysicalCaptures} from '../commerce/commerce-core-physical.js';
import {dataDigest,captureJson} from '../profile-engine/contracts.js';
import {createGenericCapabilityResourceOwner,type GenericCapabilityResourceHandle} from './capability-resource.js';
import {createGenericCapabilityContextOwner,type GenericCapabilityContext} from './capability-context.js';
import {requireGenericCapabilityGenerationBinding,type GenericCompositionHandle} from './public-sdk.js';
import type {GenericApplicationRuntime} from './invocation-owner.js';
import type {GenericFixtureActor} from './entry-authorization.js';
import type {GenericGeneratedCodec} from './capability-generation.js';
const at={path:'generated-capability-dispatch',start:0,end:0};
type Codec={decode(wire:Uint8Array):{ok:boolean;wire?:Uint8Array;value?:unknown;error?:unknown}};
export interface GenericCapabilityDispatchOptions {readonly consumerRoot:string;readonly runtime?:GenericApplicationRuntime}
function controls(value:unknown,allowed:readonly string[]):Record<string,unknown>{
 if(!value||typeof value!=='object'||types.isProxy(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))fail('InvalidContract',at,'plain invocation controls required');
 const ds=Object.getOwnPropertyDescriptors(value),out:Record<string,unknown>=Object.create(null);for(const key of Reflect.ownKeys(ds)){if(typeof key!=='string'||!allowed.includes(key)||!ds[key]?.enumerable||!Object.hasOwn(ds[key]!,'value'))fail('InvalidContract',at,'closed inert invocation controls required');out[key]=ds[key]!.value;}return out;
}
export function createGenericGeneratedCapabilityOwner(moduleUrl:string,proposal:unknown,composition:unknown,handle:GenericCompositionHandle,options:GenericCapabilityDispatchOptions){
 const capturedOptions=controls(options,['consumerRoot','runtime']);options={consumerRoot:capturedOptions.consumerRoot as string,...(capturedOptions.runtime?{runtime:capturedOptions.runtime as GenericApplicationRuntime}:{})};
 const parent=requireGenericCapabilityGenerationBinding(composition,handle),expected=parent.generation(),plan=captureJson(proposal);
 if(dataDigest(plan)!==dataDigest(expected.plan))fail('ForeignOwner',at,'generated native wiring must match this original application/source/profile');
 const url=new URL(moduleUrl);if(url.protocol!=='file:')fail('InvalidContract',at,'physical generated native module required');const directory=path.dirname(fileURLToPath(url));
 if(path.basename(fileURLToPath(url))!=='capabilities.mjs')fail('InvalidContract',at,'original generated capabilities module required');
 const captures=expected.files.map(f=>{const p=readCorePhysicalFile(path.join(directory,f.relative_path));if(p.text!==f.content)fail('StaleOwner',at,'generated capability artifact changed: '+f.relative_path);return p;}),physical=pinCorePhysicalCaptures(captures);
 const resources=createGenericCapabilityResourceOwner(options.consumerRoot),contexts=options.runtime?createGenericCapabilityContextOwner(composition,handle,options.runtime):null;
 const loaded=new Map<string,Promise<GenericCapabilityResourceHandle>>(),codecs=new Map<string,Promise<Codec>>();let closed=false;
 const current=()=>{if(closed)fail('StaleOwner',at,'generated capability dispatcher closed');parent.assertCurrent();physical.assertCurrent();};current();
 const binding=(id:string)=>{current();const b=expected.plan.bindings.find(b=>b.id===id);if(!b)fail('UnknownReference',at,'explicit checked capability selector required');return b;};
 const codec=async(spec:GenericGeneratedCodec)=>{current();let p=codecs.get(spec.decoder_path);if(!p){const source=expected.files.find(f=>f.relative_path===spec.decoder_path);if(!source)fail('InvalidContract',at,'original generated decoder required');p=import('data:text/javascript;base64,'+Buffer.from(source.content).toString('base64')).then(m=>{current();if(typeof m.decode!=='function')fail('InvalidContract',at,'generated decoder export required');return m as Codec;});codecs.set(spec.decoder_path,p);}const c=await p;current();return c;};
 const bytes=(wire:Uint8Array,maximum:number)=>{if(types.isProxy(wire)||!types.isUint8Array(wire))fail('InvalidContract',at,'owned byte input required');try{const proto=Object.getPrototypeOf(Uint8Array.prototype),get=(key:string)=>Object.getOwnPropertyDescriptor(proto,key)!.get!.call(wire),length=get('byteLength') as number,buffer=get('buffer') as ArrayBuffer;if(length>maximum)fail('ResourceLimit',at,'native input exceeds selected byte bound');if(types.isSharedArrayBuffer(buffer))fail('InvalidContract',at,'shared byte input rejected');const out=new Uint8Array(length);Uint8Array.prototype.set.call(out,new Uint8Array(buffer,get('byteOffset') as number,length));return out;}catch(e){if(e instanceof CoreCommerceSourceError)throw e;return fail('InvalidContract',at,'actual attached byte input required');}};
 const checked=async(spec:GenericGeneratedCodec,wire:Uint8Array)=>{const c=await codec(spec),v=c.decode(wire);current();if(!v.ok||!v.wire)fail('TypeMismatch',at,'native argument/result failed its generated business codec: '+JSON.stringify(v.error));return v;};
 const assertContext=(b:ReturnType<typeof binding>,context:GenericCapabilityContext|undefined)=>{if(b.contract.kind==='agent-run/v1'&&b.tools.length||b.contract.kind==='search/v1'){if(!contexts||!context)fail('ForeignOwner',at,'original same-application Query context required');contexts.assertBinding(context,b.id);contexts.assertCurrent(context);}};
 const owner=Object.freeze({
  inspect(){current();return coreFreeze({plan:expected.plan,scope:'generated-local-dispatch;provider-adapters-unrun',authority_effect:'none'});},
  openContext(actor:GenericFixtureActor,entry:string,id:string,settings:{deadline_ms:number;tool_names:readonly string[];max_tool_calls:number}){const b=binding(id);if(!contexts)fail('ForeignOwner',at,'original same-application runtime required');return contexts.open(actor,entry,b.id,settings);},
  async invoke(id:string,wire:Uint8Array,settings:Readonly<{deadline_ms:number;signal?:AbortSignal;context?:GenericCapabilityContext}>){
   const b=binding(id),input=bytes(wire,b.bounds.max_input_bytes),captured=controls(settings,['deadline_ms','signal','context']),deadline=captured.deadline_ms as number,signal=captured.signal as AbortSignal|undefined,context=captured.context as GenericCapabilityContext|undefined;
   const aborted=()=>{if(signal===undefined)return false;try{return Object.getOwnPropertyDescriptor(AbortSignal.prototype,'aborted')!.get!.call(signal) as boolean;}catch{return fail('InvalidContract',at,'actual cancellation signal required');}};
   const live=()=>{current();if(!Number.isSafeInteger(deadline)||deadline<=Date.now()||deadline-Date.now()>b.bounds.deadline_ms||aborted())fail('StaleOwner',at,'current bounded deadline/cancellation required');assertContext(b,context);};live();
   const decoded=await checked(b.input,input);live();
   let promise=loaded.get(b.id);if(!promise){promise=resources.load(b.realization,b.provider_lineage,b.realization.target,{deadline_ms:deadline,...(signal?{signal}:{})});loaded.set(b.id,promise);}const resource=await promise;live();
   const toolBroker=b.contract.kind==='agent-run/v1'&&b.tools.length?Object.freeze({async invoke(name:string,args:Uint8Array){live();const t=b.tools.find(t=>t.name===name);if(!t)fail('UnknownReference',at,'undeclared tool proposal');const checkedArgs=await checked(t.argument,bytes(args,b.bounds.max_input_bytes));live();const outcome=await contexts!.invokeTool(context!,name,new TextEncoder().encode(JSON.stringify({[t.argument_parameter]:checkedArgs.value})));live();if(!outcome.ok||outcome.outcome.kind!=='Returned')fail('ForeignOwner',at,'original Query did not authorize and return tool data');const result=await checked(t.result,new TextEncoder().encode(JSON.stringify(outcome.outcome.value)));live();await contexts!.assertRelease(context!);live();return result.wire!;}}):undefined;
   const raw=await resources.invoke(resource,{operation:b.contract.operation,input:decoded.wire!,result_schema:JSON.parse(readCorePhysicalFile(path.join(directory,b.result.schema_path)).text),limits:{...b.bounds,max_tool_calls:toolBroker?b.bounds.max_tool_calls:0},deadline_ms:deadline,...(toolBroker?{tool_schemas:b.tools.map(t=>({name:t.name,argument_schema:JSON.parse(readCorePhysicalFile(path.join(directory,t.argument.schema_path)).text),result_schema:JSON.parse(readCorePhysicalFile(path.join(directory,t.result.schema_path)).text)}))}:{}),...(signal?{signal}:{}),...(toolBroker?{toolBroker}:{})});live();
   const result=await checked(b.result,raw);live();if(context&&contexts){await contexts.assertRelease(context);live();}return Object.freeze({ok:true as const,value:result.value,wire:result.wire!,binding:b.id,contract:b.contract.kind,resource:b.provider_lineage.resource_ref,qualification:'local-fixture-native-dispatch;no-provider-qualification' as const});
  },
  assertCurrent:current,
  async close(){if(closed)return;closed=true;const rows=await Promise.allSettled([...loaded.values()]);for(const r of rows)if(r.status==='fulfilled')await resources.dispose(r.value);},
 });return owner;
}
