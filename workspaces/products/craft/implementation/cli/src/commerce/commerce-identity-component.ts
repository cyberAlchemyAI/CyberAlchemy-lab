/** Genuine source/physical native identity component custody, no effect owner.
 * Open Questions: docs/COMMERCE-NATIVE-IDENTITY.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {types as host} from 'node:util';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {pinCoreImplementation,pinCorePhysicalCaptures,writeCoreExclusiveFile,type CorePhysicalFile} from './commerce-core-physical.js';
import {generateCommerceIdentityBundle} from './commerce-identity-generation.js';
import {assertCommerceIdentityCallOwner,type CommerceIdentityCallOwner,type CommerceIdentityCallHandle} from './commerce-identity-call-owner.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-identity-generation'+ext,'commerce-identity-call-owner'+ext,'commerce-core-physical'+ext,'commerce-value-codec-generation'+ext,'commerce-computation-native'+ext,'commerce-computation-kernel'+ext,'commerce-computation-environment'+ext,'../../profiles/commerce-local-v1-candidate/runtime/context.ts','../../profiles/commerce-local-v1-candidate/runtime/values-and-codecs.ts']),where={path:'application.alch',start:0,end:0};
export interface CommerceIdentityComponentHandle {readonly kind:'original-commerce-physical-identity-component/v1-candidate'}
export function createCommerceIdentityComponentOwner(calls:CommerceIdentityCallOwner,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle){
 assertCommerceIdentityCallOwner(calls);pin.assertCurrent();calls.sourceDomain();
 type State={files:readonly CorePhysicalFile[];physical:ReturnType<typeof pinCorePhysicalCaptures>;handles:readonly CommerceIdentityCallHandle[];manifest:ReturnType<typeof generateCommerceIdentityBundle>['manifest'];runtime:any;disposed:boolean};const owned=new WeakMap<object,State>();
 const current=(h:CommerceIdentityComponentHandle)=>{const s=h&&typeof h==='object'?owned.get(h):undefined;if(!s)fail('ForeignOwner',where,'original physical identity component from this exact factory required');if(s.disposed)fail('DisposedOwner',where,'identity component disposed');pin.assertCurrent();stage.assertCurrent(source);domain.assertCurrent(baseline);calls.assertCurrentSet(s.handles);s.physical.assertCurrent();return s;};
 return Object.freeze({async materialize(handles:readonly CommerceIdentityCallHandle[],directory:string):Promise<CommerceIdentityComponentHandle>{
  pin.assertCurrent();const bundle=generateCommerceIdentityBundle(calls,handles,stage,source,domain,baseline);if(host.isProxy(handles)||!Array.isArray(handles))fail('InvalidContract',where,'original source-call array required');const originals:CommerceIdentityCallHandle[]=[];for(let i=0;i<handles.length;i++){const d=Object.getOwnPropertyDescriptor(handles,String(i));if(!d||!Object.hasOwn(d,'value'))fail('InvalidContract',where,'original source-call data required');originals.push(d.value);}if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)fail('InvalidContract',where,'existing normalized absolute component directory required');
  const files:CorePhysicalFile[]=[],texts=new Map<string,string>(),put=(name:string,text:string)=>{const f=writeCoreExclusiveFile(path.join(directory,name),text);files.push(f);texts.set(name,f.text);};
  put('package.json','{"type":"module"}\n');for(const f of bundle.files){put(f.path,f.text);put(f.path.replace(/\.ts$/,'.js'),stripTypeScriptTypes(f.text));}put('identity-component.json',JSON.stringify(bundle.manifest,null,2)+'\n');
  // Import the exact captured JS bytes, with a fixed sibling closure. No later
  // filesystem read, arbitrary resolver, source checkout or evaluator callback.
  const url=(s:string)=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
  const domainUrl=url(texts.get('commerce-domain-values.js')!),modelUrl=url(texts.get('commerce-identity-model.js')!),codec=texts.get('values-and-codecs.js')!,codecNeedle="'./commerce-domain-values.js'";
  if(!codec.includes(codecNeedle))fail('InvalidContract',where,'fixed captured codec dependency absent');const codecUrl=url(codec.replace(codecNeedle,JSON.stringify(domainUrl))),context=texts.get('context.js')!,modelNeedle="'./commerce-identity-model.js'",valueNeedle="'./values-and-codecs.js'";
  if(!context.includes(modelNeedle)||!context.includes(valueNeedle))fail('InvalidContract',where,'fixed captured identity dependency absent');const native=await import(url(context.replace(modelNeedle,JSON.stringify(modelUrl)).replace(valueNeedle,JSON.stringify(codecUrl))));
  const physical=pinCorePhysicalCaptures(files),h=Object.freeze({kind:'original-commerce-physical-identity-component/v1-candidate' as const});owned.set(h,{files:coreFreeze(files),physical,handles:Object.freeze(originals),manifest:bundle.manifest,runtime:native.createCommerceIdentityPrimitives(),disposed:false});current(h);return h;
 },inspect(h:CommerceIdentityComponentHandle){const s=current(h);return coreFreeze({kind:h.kind,manifest:s.manifest,physical_members:s.files.map(f=>({...f.file,fingerprint:f.fingerprint})),tool_basis:{node:process.versions.node,platform:process.platform,architecture:process.arch,typescript_transform:'actual Node stripTypeScriptTypes builtin;not installed selected TS basis'},qualification:'actual-original-source/physical-native-data-component-only;no-original-invocation-or-private-context',authority_effect:'none'});},
 evaluateBoundParameters(h:CommerceIdentityComponentHandle,call:CommerceIdentityCallHandle,parameters:readonly unknown[]){const s=current(h);if(!s.handles.includes(call))fail('ForeignOwner',where,'exact original captured source-call token required');const binding=calls.inspect(call),result=s.runtime.evaluateNativeIdentityData(binding.key,parameters);current(h);return result;},assertCurrent(h:CommerceIdentityComponentHandle){current(h);},dispose(h:CommerceIdentityComponentHandle){current(h).disposed=true;},
 });
}
