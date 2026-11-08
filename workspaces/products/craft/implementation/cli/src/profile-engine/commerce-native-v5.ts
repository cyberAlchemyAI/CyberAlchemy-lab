/** Reusable pure native basis, followed by original application source/output
 * binding. No application functions or reconstructed owners are accepted.
 * Open Questions: docs/COMMERCE-SDK-V5.md#open-questions. */
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {mkdirSync,readdirSync} from 'node:fs';
import {AsyncLocalStorage} from 'node:async_hooks';
import {dataDigest} from './contracts.js';
import {validateProfilePackageV5} from './contracts-v5.js';
import {assertFamilyOwnerV5,type CommerceFamilyOwnerV5} from './family-v5.js';
import {assertCommercePublicSdkCurrentV5,inspectCommercePublicSdkV5,commercePublicAlchSourceApiV5,type CommerceSdkClosureHandleV5} from './commerce-sdk-physical-v5.js';
import {createCommercePureNativeProducerV5,type CommerceProducedPureHandleV5} from './commerce-native-producer-v5.js';
import {createCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from '../commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from '../commerce/commerce-core-stage-owner.js';
import {readCorePhysicalFile,writeCoreExclusiveFile,pinCoreImplementation,type CorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import type {CommerceDerivedFamilyHandle,CommerceSourceHandle} from '../commerce/commerce-stages-v1.js';
import type {BoundedValuesNativeV1,PureComputationNativeV2} from '../commerce/commerce-native-v1.js';
import type {ProfilePackageV1} from '../commerce/commerce-data-v1.js';

const extension=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-sdk-physical-v5'+extension,'commerce-native-producer-v5'+extension,'loader-v5'+extension,'contracts-v5'+extension]);
const where={path:'commerce-native-basis-v5',start:0,end:0};
const methods=Object.freeze({values:['checkCommerceSchema','decodeCommerceValue','encodeCommerceValue','copyCommerceValue'],pure:['checkCommerceComputation','compileCommerceComputation','evaluateCommerceComputation']} as const);
type Method=typeof methods.values[number]|typeof methods.pure[number];
export interface CommercePureBasisHandleV5 {readonly kind:'original-reusable-commerce-pure-basis/v5-candidate'}
export interface CommerceSourcePrefixHandleV5 {readonly kind:'original-post-basis-commerce-source-prefix/v5-candidate'}
export interface CommerceNativeBindingHandleV5 {readonly kind:'original-commerce-source-component-binding/v5-candidate'}
export interface CommercePureBasisInspectionV5 {
 readonly kind:'actual-reusable-commerce-pure-basis/v5-candidate';readonly root:string;
 readonly profile:ProfilePackageV1;readonly profile_sha256:string;readonly native_basis_sha256:string;
 readonly sdk_sha256:string;readonly family_sha256:string;
 readonly members:readonly {readonly path:string;readonly sha256:string;readonly bytes:number}[];
 readonly qualification:'reusable-native-basis;application-source-and-output-binding-required';readonly authority_effect:'none';
}
type NativeApi=Readonly<{values:BoundedValuesNativeV1;pure:PureComputationNativeV2}>;
type DispatchContext={current:()=>void;modules:NativeApi;binding:object};
// The only context issuer is this module's original owner. Public native modules
// expose fixed methods; neither an arbitrary function nor a context DTO can enter.
const active=new AsyncLocalStorage<DispatchContext>();
const returnedHandles=new WeakMap<object,object>();
const consumers=new Set<Method>(['decodeCommerceValue','encodeCommerceValue','copyCommerceValue','compileCommerceComputation','evaluateCommerceComputation']);
function dispatch(group:'values'|'pure',name:Method,args:unknown[]):any {
 const context=active.getStore();if(!context)fail('ForeignOwner',where,'original post-basis source/output binding is required');
 context.current();
 if(consumers.has(name)){
  const handle=args[0];if(!handle||typeof handle!=='object'||returnedHandles.get(handle)!==context.binding)fail('ForeignOwner',where,'native handle belongs to another source/output binding');
 }
 const result=(context.modules[group] as any)[name](...args);
 context.current();
 if(name==='checkCommerceSchema'||name==='checkCommerceComputation'){
  if(result.ok)returnedHandles.set(result.value,context.binding);
 }else if(name==='compileCommerceComputation')returnedHandles.set(result,context.binding);
 return result;
}
/** Actual reusable ABI implementation. Calling these exports outside an original
 * owner's guarded binding fails; a module namespace is not application custody. */
export const commerceNativeDispatchV5=Object.freeze({
 checkCommerceSchema:(...args:unknown[])=>dispatch('values','checkCommerceSchema',args),
 decodeCommerceValue:(...args:unknown[])=>dispatch('values','decodeCommerceValue',args),
 encodeCommerceValue:(...args:unknown[])=>dispatch('values','encodeCommerceValue',args),
 copyCommerceValue:(...args:unknown[])=>dispatch('values','copyCommerceValue',args),
 checkCommerceComputation:(...args:unknown[])=>dispatch('pure','checkCommerceComputation',args),
 compileCommerceComputation:(...args:unknown[])=>dispatch('pure','compileCommerceComputation',args),
 evaluateCommerceComputation:(...args:unknown[])=>dispatch('pure','evaluateCommerceComputation',args),
});
const owners=new WeakSet<object>();
export interface CommerceNativeStageParentsV5 {
 readonly prefix:CommerceSourcePrefixHandleV5;readonly sources:CoreCommerceSourceOwner;readonly capture:CoreCommerceSourceCapture;
 readonly semantics:CoreCommerceSemanticOwner;readonly semantic:CoreCommerceSemanticCapture;
 readonly stage:CoreCommerceStageSourceOwner;readonly source:CommerceSourceHandle;readonly basis:CommercePureBasisInspectionV5;
 current():void;
}
const stageParents=new WeakMap<object,(prefix:CommerceSourcePrefixHandleV5)=>CommerceNativeStageParentsV5>();
export function assertCommerceNativeOwnerV5(owner:object){if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original commerce native owner required');}
/** Internal assembly bridge retains original parents; data or callbacks cannot adopt them. */
export function commerceNativeStageParentsV5(owner:object,prefix:CommerceSourcePrefixHandleV5):CommerceNativeStageParentsV5 {
 assertCommerceNativeOwnerV5(owner);const access=stageParents.get(owner);if(!access)fail('ForeignOwner',where,'original native stage assembly bridge required');return access(prefix);
}

export function createCommerceNativeOwnerV5(sdk:CommerceSdkClosureHandleV5,families:CommerceFamilyOwnerV5){
 assertCommercePublicSdkCurrentV5(sdk);assertFamilyOwnerV5(families);pin.assertCurrent();
 const sdkData=inspectCommercePublicSdkV5(sdk),front=commercePublicAlchSourceApiV5(sdk),producer=createCommercePureNativeProducerV5(families);
 type Basis={family:CommerceDerivedFamilyHandle;files:CorePhysicalFile[];inspection:CommercePureBasisInspectionV5;names:string[];native:NativeApi;disposed:boolean};
 type Prefix={basis:CommercePureBasisHandleV5;sources:CoreCommerceSourceOwner;capture:CoreCommerceSourceCapture;semantics:CoreCommerceSemanticOwner;semantic:CoreCommerceSemanticCapture;stage:CoreCommerceStageSourceOwner;source:CommerceSourceHandle;alch:object;sourceFilesSha256:string;root:string;disposed:boolean};
 type Binding={prefix:CommerceSourcePrefixHandleV5;product:CommerceProducedPureHandleV5;modules:NativeApi;disposed:boolean};
 const bases=new WeakMap<object,Basis>(),prefixes=new WeakMap<object,Prefix>(),bindings=new WeakMap<object,Binding>();
 const basisState=(h:CommercePureBasisHandleV5):Basis=>{
  const s=h&&typeof h==='object'?bases.get(h):undefined;if(!s)fail('ForeignOwner',where,'original reusable basis from this exact owner required');if(s.disposed)fail('DisposedOwner',where,'native basis disposed');
  pin.assertCurrent();assertCommercePublicSdkCurrentV5(sdk);families.assertCurrent(s.family);
  for(const row of s.files)if(readCorePhysicalFile(row.file.path).fingerprint!==row.fingerprint)fail('StaleOwner',where,'actual original reusable native member changed');
  if(dataDigest(readdirSync(s.inspection.root).sort())!==dataDigest(s.names))fail('StaleOwner',where,'reusable native package membership changed');return s;
 };
 const prefixState=(h:CommerceSourcePrefixHandleV5):Prefix=>{
  const s=h&&typeof h==='object'?prefixes.get(h):undefined;if(!s)fail('ForeignOwner',where,'original post-basis source prefix from this exact owner required');if(s.disposed)fail('DisposedOwner',where,'source prefix disposed');
  basisState(s.basis);s.sources.assertCurrent(s.capture);s.semantics.assertSource(s.semantic,s.capture);s.stage.assertCurrent(s.source);front.assertCommerceSourceCurrent(s.alch);return s;
 };
 const bindingState=(h:CommerceNativeBindingHandleV5):Binding=>{
  const s=h&&typeof h==='object'?bindings.get(h):undefined;if(!s)fail('ForeignOwner',where,'original source/output binding from this exact owner required');if(s.disposed)fail('DisposedOwner',where,'source/output binding disposed');
  const p=prefixState(s.prefix),b=basisState(p.basis);producer.assertSourceParent(s.product,p.stage,p.source);producer.assertFamily(s.product,b.family);return s;
 };
 const owner=Object.freeze({
  async produceAndLoad(family:CommerceDerivedFamilyHandle,output:string):Promise<CommercePureBasisHandleV5>{
   assertCommercePublicSdkCurrentV5(sdk);pin.assertCurrent();const f=families.inspect(family);
   if(f.descriptor.scope.kind!=='pure-pricing'||f.native_requirements.length!==2||f.native_requirements.some(r=>!['bounded-values','pure-computation'].includes(r.primitive_id)))fail('NativeImplementationUnavailable',where,'only implemented finite pure native basis is supported');
   if(typeof output!=='string'||!path.isAbsolute(output)||path.normalize(output)!==output)fail('InvalidContract',where,'fresh normalized absolute native basis root required');
   const entry=pathToFileURL(path.join(sdkData.core_root,'dist/index.js')).href,files:CorePhysicalFile[]=[];
   mkdirSync(output,{mode:0o700});
   const put=(name:string,text:string)=>{const row=writeCoreExclusiveFile(path.join(output,name),text);files.push(row);return row;};
   for(const group of ['values','pure'] as const){
    const text=`import {commerce} from ${JSON.stringify(entry)};\nconst native=commerce.commerceNativeDispatchV5;\n`+methods[group].map(name=>`export const ${name}=native.${name};`).join('\n')+'\n';put(group+'.js',text);
   }
   put('package.json','{"type":"module"}\n');
   const native={values:await import(pathToFileURL(path.join(output,'values.js')).href),pure:await import(pathToFileURL(path.join(output,'pure.js')).href)} as NativeApi;
   const code=files.map(r=>({path:path.basename(r.file.path),sha256:r.file.sha256,bytes:r.file.bytes})).sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0),closure=dataDigest({members:code,sdk_sha256:sdkData.sdk_sha256});
   const resolved=f.native_requirements.map(r=>{
    const group=r.primitive_id==='bounded-values'?'values':'pure',namespace=native[group],file=files.find(x=>path.basename(x.file.path)===group+'.js')!;
    if(r.required_exports.some(name=>!(methods[group] as readonly string[]).includes(name)||typeof (namespace as any)[name]!=='function'))fail('NativeImplementationUnavailable',where,'required implemented ABI/export unavailable');
    // ABI identity is checked against this implementation, not copied unchecked
    // from the requirement into a claim of availability.
    const abi=group==='values'?'craft.commerce-values/v1-candidate':'domainspec.iteration-expression/v2-candidate';
    if(r.abi!==abi)fail('NativeImplementationUnavailable',where,'unknown native semantic ABI');
    return {dependency_id:'commerce-'+r.primitive_id,origin:'produced-artifact' as const,version_comparison:'exact' as const,version_operand:sdkData.core_version,actual_version:sdkData.core_version,semantic_abi:abi,artifact:{...file.file,path:path.basename(file.file.path)},closure_sha256:closure,exports:[...methods[group]].sort(),platform:process.platform,architecture:process.arch};
   });
   const profile=validateProfilePackageV5({...f.descriptor,resolved_dependencies:resolved});put('profile.json',JSON.stringify(profile,null,2)+'\n');
   const subject={schema_version:'craft.commerce-reusable-native-basis/v5-candidate',profile_sha256:dataDigest(profile),sdk_sha256:sdkData.sdk_sha256,family_sha256:f.family_sha256,closure_sha256:closure,code_members:code,actual_public_sdk_entry:entry,late_source_binding:'original-post-basis-source-and-produced-component-only',authority_effect:'none'};
   put('manifest.json',JSON.stringify({...subject,open_questions_ref:'docs/COMMERCE-SDK-V5.md#open-questions'},null,2)+'\n');
   const inspection:CommercePureBasisInspectionV5=coreFreeze({kind:'actual-reusable-commerce-pure-basis/v5-candidate',root:output,profile,profile_sha256:subject.profile_sha256,native_basis_sha256:dataDigest(subject),sdk_sha256:sdkData.sdk_sha256,family_sha256:f.family_sha256,members:files.map(r=>({path:path.basename(r.file.path),sha256:r.file.sha256,bytes:r.file.bytes})),qualification:'reusable-native-basis;application-source-and-output-binding-required',authority_effect:'none'});
   const h=Object.freeze({kind:'original-reusable-commerce-pure-basis/v5-candidate' as const});bases.set(h,{family,files,inspection,native,names:readdirSync(output).sort(),disposed:false});basisState(h);return h;
  },
  inspectBasis(h:CommercePureBasisHandleV5){return basisState(h).inspection;},
  assertBasisCurrent(h:CommercePureBasisHandleV5){basisState(h);},
  async prepareSource(basis:CommercePureBasisHandleV5,root:string,application='application.alch'):Promise<CommerceSourcePrefixHandleV5>{
   // No source factory is invoked until original basis currentness succeeds.
   const b=basisState(basis),sources=createCoreCommerceSourceOwner(),semantics=createCoreCommerceSemanticOwner(sources),stage=createCoreCommerceStageSourceOwner(sources,semantics);
   const capture=sources.prepare(root,application);let source:CommerceSourceHandle|undefined,alch:object|undefined,semantic:CoreCommerceSemanticCapture|undefined;
   try{
    semantic=semantics.check(capture);
    source=await stage.prepare(root,application);alch=front.captureCommerceSource(root,application);
    const core=stage.inspect(source),captured=sources.inspect(capture),other=front.inspectCommerceSource(alch);
    const fileSubject=(rows:readonly {path:string;sha256:string;bytes:number}[])=>rows.map(({path,sha256,bytes})=>({path,sha256,bytes})).sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0);
    const sourceFilesSha256=dataDigest(fileSubject(captured.files));
    // Core's capture includes physical custody and implementation identity;
    // Alch's independent capture uses its own identity algorithm. Join actual
    // complete member subjects, never pretend these two capture IDs are equal.
    if(core.source_sha256!==captured.capture_sha256||core.source_sha256!==families.inspect(b.family).source_capture_sha256||sourceFilesSha256!==dataDigest(fileSubject(other.files)))fail('ForeignOwner',where,'fresh original Core/Alch file closures must agree with the checked family source');
    basisState(basis);const h=Object.freeze({kind:'original-post-basis-commerce-source-prefix/v5-candidate' as const});prefixes.set(h,{basis,sources,capture,semantics,semantic,stage,source,alch,sourceFilesSha256,root,disposed:false});prefixState(h);return h;
   }catch(error){if(alch)try{front.disposeCommerceSource(alch);}catch{}if(source)try{stage.dispose(source);}catch{}if(semantic)try{semantics.dispose(semantic);}catch{}try{sources.dispose(capture);}catch{}throw error;}
  },
  inspectPrefix(h:CommerceSourcePrefixHandleV5){const p=prefixState(h),b=basisState(p.basis),source=p.stage.inspect(p.source);return coreFreeze({stage:'original-post-basis-commerce-source-prefix/v5-candidate',source_sha256:source.source_sha256,alch_source_sha256:front.inspectCommerceSource(p.alch).source_sha256,source_files_sha256:p.sourceFilesSha256,profile_sha256:b.inspection.profile_sha256,native_basis_sha256:b.inspection.native_basis_sha256,sdk_sha256:sdkData.sdk_sha256,output_sha256:null,qualification:'original-source-prefix;not-checked-or-generated-application',authority_effect:'none'});},
  async produceForSource(h:CommerceSourcePrefixHandleV5,output:string){const p=prefixState(h),b=basisState(p.basis),product=await producer.produceForSource(b.family,p.root,p.stage,p.source,output);prefixState(h);producer.assertSourceParent(product,p.stage,p.source);return product;},
  inspectProduct(product:CommerceProducedPureHandleV5){return producer.inspect(product);},
  async bindComponents(prefix:CommerceSourcePrefixHandleV5,product:CommerceProducedPureHandleV5):Promise<CommerceNativeBindingHandleV5>{
   const p=prefixState(prefix),b=basisState(p.basis);producer.assertSourceParent(product,p.stage,p.source);producer.assertFamily(product,b.family);const modules=await producer.modules(product) as NativeApi;
   const h=Object.freeze({kind:'original-commerce-source-component-binding/v5-candidate' as const});bindings.set(h,{prefix,product,modules,disposed:false});bindingState(h);return h;
  },
  native(binding:CommerceNativeBindingHandleV5):NativeApi {
   const s=bindingState(binding),p=prefixState(s.prefix),b=basisState(p.basis),context:DispatchContext={current:()=>{bindingState(binding);},modules:s.modules,binding};
   const wrap=(group:'values'|'pure')=>Object.freeze(Object.fromEntries(methods[group].map(name=>[name,(...args:unknown[])=>{
    bindingState(binding);const result=active.run(context,()=>((b.native[group] as any)[name])(...args));bindingState(binding);return result;
   }])));
   return Object.freeze({values:wrap('values'),pure:wrap('pure')}) as unknown as NativeApi;
  },
  inspectBinding(h:CommerceNativeBindingHandleV5){const s=bindingState(h),p=prefixState(s.prefix),b=basisState(p.basis),output=producer.inspect(s.product);return coreFreeze({kind:h.kind,source_sha256:output.source_capture_sha256,profile_sha256:b.inspection.profile_sha256,native_basis_sha256:b.inspection.native_basis_sha256,sdk_sha256:sdkData.sdk_sha256,output_sha256:dataDigest(output.members),qualification:'original-source-compiled-native-component-binding;not-whole-application-or-entry',authority_effect:'none'});},
  assertBindingCurrent(h:CommerceNativeBindingHandleV5){bindingState(h);},
  disposeBinding(h:CommerceNativeBindingHandleV5){bindingState(h).disposed=true;},
  disposePrefix(h:CommerceSourcePrefixHandleV5){const p=prefixState(h);p.disposed=true;front.disposeCommerceSource(p.alch);p.stage.dispose(p.source);p.semantics.dispose(p.semantic);p.sources.dispose(p.capture);},
  disposeBasis(h:CommercePureBasisHandleV5){basisState(h).disposed=true;},
 });
 owners.add(owner);stageParents.set(owner,h=>{const p=prefixState(h),b=basisState(p.basis);return Object.freeze({prefix:h,sources:p.sources,capture:p.capture,semantics:p.semantics,semantic:p.semantic,stage:p.stage,source:p.source,basis:b.inspection,current(){prefixState(h);}});});return owner;
}
