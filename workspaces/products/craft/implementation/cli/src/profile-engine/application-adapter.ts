import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertWholeApplicationPlan,type WholeApplicationPlanV1} from '../generation/whole-application-v1.js';
import {assertApplicationIntegrationBinding,type ApplicationIntegrationBindingV1} from '../system-integration/application-binding-v1.js';
import {captureJson,dataDigest,reject,type Json} from './contracts.js';
import {assertRequestApplicationPlanV1,type RequestApplicationPlanV1} from '../generation/request-application-plan-v1.js';
import {assertRequestApplicationBindingV1,type RequestApplicationBindingV1} from '../system-integration/application-binding-v1.js';
import type {BusinessApplicationIntent} from './contracts-v2.js';
import {assertSelectedReconciledProject,selectedReconciledIdentity,type SelectedReconciledProject} from '../generation/selected-reconciled-project.js';

/** Existing graph/whole-plan/Mapping-to-Operation bridge. No provider execution.
 * Open questions: full profile composition/installed qualification PE16/23. */
export interface ApplicationPublicIntent {
 readonly id:string;readonly source:string;readonly operation_ref:string;readonly mapping_binding_ref:string;
 readonly access:Readonly<{kind:'public'}>;
}
interface ApplicationCallableBase {
 readonly intent:ApplicationPublicIntent;readonly graph:CompiledProjectGraph;
 readonly operation_module:string;readonly source_sha256:string;readonly assert_current:()=>void;
}
export interface CheckedLegacyApplicationCallable extends ApplicationCallableBase {
 readonly kind:'legacy-whole';readonly artifact_plan:WholeApplicationPlanV1;
 readonly intent:ApplicationPublicIntent;readonly graph:CompiledProjectGraph;readonly whole:WholeApplicationPlanV1;
 readonly binding:ApplicationIntegrationBindingV1;readonly operation_module:string;readonly source_sha256:string;
 readonly assert_current:()=>void;
}
export interface CheckedRequestApplicationCallable extends ApplicationCallableBase {
 readonly kind:'request-application';readonly artifact_plan:RequestApplicationPlanV1;
 readonly binding:RequestApplicationBindingV1;readonly authored_intent:BusinessApplicationIntent;
 readonly lineage:Readonly<{application_id:string;original_source:string;original_source_sha256:string;original_semantics_sha256:string;derived_source_sha256:string;derivation_sha256:string;line_map:readonly Readonly<{derived_line:number;original_line:number|null;origin:'business'|'adapter'}>[]}>
}
export type CheckedApplicationCallable=CheckedLegacyApplicationCallable|CheckedRequestApplicationCallable;
const checked=new WeakMap<object,string>();
/** Validate owning graph/plan custody without recompiling already captured artifacts. */
export function assertBusinessApplicationPlanCurrent(graph:CompiledProjectGraph,plan:SelectedReconciledProject):void {
 assertCompiledProjectSnapshot(graph);assertSelectedReconciledProject(plan);const identity=selectedReconciledIdentity(plan);
 if(identity.project_id!==graph.project_id||identity.source_manifest_sha256!==graph.source_manifest.manifest_sha256)reject('PROFILE_APPLICATION_PLAN_JOIN','/','registered domain/plan manifest differs');
}
export function prepareApplicationCallable(graph:CompiledProjectGraph,whole:WholeApplicationPlanV1,binding:ApplicationIntegrationBindingV1,intentInput:ApplicationPublicIntent,assertCurrent:()=>void):CheckedLegacyApplicationCallable {
 assertCurrent();assertCompiledProjectSnapshot(graph);assertWholeApplicationPlan(whole);assertApplicationIntegrationBinding(binding);
 const intent=captureJson(intentInput) as unknown as ApplicationPublicIntent;
 if(Object.keys(intent).sort().join(',')!=='access,id,mapping_binding_ref,operation_ref,source'||!intent.access||Object.keys(intent.access).join(',')!=='kind'||intent.access.kind!=='public'||!/^[A-Za-z][A-Za-z0-9_-]*$/.test(intent.id))reject('PROFILE_APPLICATION_INTENT','/','explicit closed public Operation intent required');
 if(whole.language!=='typescript'||whole.domain_source_manifest_sha256!==graph.source_manifest.manifest_sha256||binding.domain_source_manifest_sha256!==graph.source_manifest.manifest_sha256||whole.binding_sha256!==binding.binding_sha256)reject('PROFILE_APPLICATION_JOIN',intent.id,'registered whole/domain/application identity differs');
 const operation=graph.nodes.find(n=>n.selector===intent.operation_ref);if(operation?.kind!=='Operation')reject('PROFILE_APPLICATION_OPERATION',intent.operation_ref,'checked Operation required');
 const request=binding.application_graph.operation_requests.find(r=>r.operation_ref===intent.operation_ref&&r.mapping_binding_refs.includes(intent.mapping_binding_ref));
 const mapping=binding.application_graph.runtime_bindings.find(b=>b.binding_id===intent.mapping_binding_ref);
 if(!request||!mapping||mapping.target_ref!==request.request_ref||!request.bindings.some(b=>b.mapping_binding_ref===mapping.binding_id&&b.source_ref===mapping.source_ref))reject('PROFILE_APPLICATION_MAPPING',intent.id,'authored checked request Mapping and Operation join required');
 const handlers=whole.artifacts.find(a=>a.relative_path==='src/integrations/application-request-handlers.ts');if(!handlers)reject('PROFILE_APPLICATION_HANDLER',intent.id,'whole plan lacks typed request handlers');
 const match=/export const APPLICATION_REQUEST_HANDLER_BINDINGS=(\[[\s\S]*?\]) as const;/.exec(handlers.content);if(!match)reject('PROFILE_APPLICATION_HANDLER',intent.id,'exact generated handler descriptor required');
 const descriptors=JSON.parse(match[1]!) as {mapping_binding_ref:string;operation_ref:string;operation_module:string}[];
 const descriptor=descriptors.find(d=>d.mapping_binding_ref===intent.mapping_binding_ref&&d.operation_ref===intent.operation_ref);
 if(!descriptor||!whole.artifacts.some(a=>a.relative_path===descriptor.operation_module))reject('PROFILE_APPLICATION_EXPORT',intent.id,'actual checked Operation export artifact missing');
 const value=Object.freeze({kind:'legacy-whole' as const,artifact_plan:whole,intent,graph,whole,binding,operation_module:descriptor.operation_module,source_sha256:graph.source_manifest.manifest_sha256,assert_current:assertCurrent});checked.set(value,fingerprint(value));assertApplicationCallableCurrent(value);return value;
}
export function prepareRequestApplicationCallable(graph:CompiledProjectGraph,plan:RequestApplicationPlanV1,binding:RequestApplicationBindingV1,authoredInput:BusinessApplicationIntent,lineageInput:CheckedRequestApplicationCallable['lineage'],assertCurrent:()=>void):CheckedRequestApplicationCallable {
 assertCurrent();assertCompiledProjectSnapshot(graph);assertRequestApplicationPlanV1(plan);assertRequestApplicationBindingV1(binding);
 const authored=captureJson(authoredInput) as unknown as BusinessApplicationIntent,lineage=captureJson(lineageInput) as unknown as CheckedRequestApplicationCallable['lineage'];
 if(authored.application_id!==lineage.application_id||authored.access.kind!=='public'||plan.domain_source_manifest_sha256!==graph.source_manifest.manifest_sha256||binding.domain_source_manifest_sha256!==graph.source_manifest.manifest_sha256||plan.binding_sha256!==binding.binding_sha256)reject('PROFILE_APPLICATION_JOIN',authored.id,'registered request/domain/lineage identity differs');
 const descriptor=plan.handlers.find(h=>h.intent_id===authored.id),entry=binding.source.entries.find(e=>e.id===authored.id);
 if(!descriptor||!entry||descriptor.operation_ref!==entry.operation_ref||!plan.artifacts.some(a=>a.relative_path===descriptor.operation_module))reject('PROFILE_APPLICATION_EXPORT',authored.id,'actual checked request entry missing');
 const intent=captureJson({id:authored.id,source:lineage.original_source,operation_ref:descriptor.operation_ref,mapping_binding_ref:descriptor.mapping_binding_ref,access:authored.access}) as unknown as ApplicationPublicIntent;
 const value=Object.freeze({kind:'request-application' as const,artifact_plan:plan,intent,authored_intent:authored,lineage,graph,binding,operation_module:descriptor.operation_module,source_sha256:lineage.original_source_sha256,assert_current:assertCurrent});checked.set(value,fingerprint(value));assertApplicationCallableCurrent(value);return value;
}
function fingerprint(v:CheckedApplicationCallable):string {return dataDigest({kind:v.kind,intent:v.intent,plan:v.artifact_plan.plan_sha256,binding:v.binding.binding_sha256,source:v.source_sha256,module:v.operation_module,...(v.kind==='request-application'?{lineage:v.lineage,authored_intent:v.authored_intent}:{})});}
export function assertApplicationCallableCurrent(value:CheckedApplicationCallable):void {
 if(!checked.has(value)||checked.get(value)!==fingerprint(value))reject('PROFILE_APPLICATION_UNREGISTERED_OR_CHANGED','/','rebuild registered checked application callable');value.assert_current();assertCompiledProjectSnapshot(value.graph);if(value.kind==='legacy-whole'){assertWholeApplicationPlan(value.whole);assertApplicationIntegrationBinding(value.binding);}else{assertRequestApplicationPlanV1(value.artifact_plan);assertRequestApplicationBindingV1(value.binding);}
}
export function renderApplicationCallableSource(value:CheckedApplicationCallable,limits:Readonly<{request_bytes:number;timeout_ms:number}>={request_bytes:16384,timeout_ms:2000},assembly?:Readonly<{settlement_import:string;transport_import:string}>):string {
 assertApplicationCallableCurrent(value);if(!Number.isSafeInteger(limits.request_bytes)||limits.request_bytes<1||limits.request_bytes>1048576||!Number.isSafeInteger(limits.timeout_ms)||limits.timeout_ms<1||limits.timeout_ms>30000)reject('PROFILE_APPLICATION_LIMITS','/','bounded request bytes and read timeout required');const key=JSON.stringify(value.intent.mapping_binding_ref),id=JSON.stringify(value.intent.id);
 if(value.kind==='request-application'){
  if(!assembly||Object.keys(assembly).sort().join(',')!=='settlement_import,transport_import'||Object.values(assembly).some(p=>!/^\.\.?\/[A-Za-z0-9_./-]+$/.test(p)||p.includes('\\')))reject('PROFILE_APPLICATION_ASSEMBLY_REQUIRED',value.intent.id,'owned typed transport and settlement imports required');
  return `import {APPLICATION_REQUEST_HANDLERS} from './integrations/application-request-handlers.js';
import {createEmptyEffectsStore} from ${JSON.stringify(assembly.settlement_import)};
import {createOperationHttpHandler,type InvocationContext} from ${JSON.stringify(assembly.transport_import)};
const run=APPLICATION_REQUEST_HANDLERS[${key}];
export type Dependencies=Parameters<typeof run>[1];
const DEFAULT_DEPENDENCIES:Dependencies=Object.freeze({store:createEmptyEffectsStore()});
export interface ApplicationIo extends InvocationContext {readonly applications?:Readonly<Record<string,Dependencies|null>>;}
function event(context:InvocationContext,phase:string):void {try{context.observe?.({phase,adapter:'operation',intent:${id}});}catch{}}
export async function invoke(input:unknown,dependencies:Dependencies|null=DEFAULT_DEPENDENCIES,context:InvocationContext={}){
 if(context.cancellation==='required')return {status:'not-returned' as const,failure:{code:'PROFILE_OPERATION_CANCELLATION_UNSUPPORTED',stage:'preflight'}};
 if(context.signal?.aborted)return {status:'not-returned' as const,failure:{code:'FUNCTION_CANCELLED',stage:'preflight'}};
 if(!dependencies?.store||typeof dependencies.store.begin!=='function')return {status:'not-returned' as const,failure:{code:'PROFILE_OPERATION_PORTS_REQUIRED',stage:'preflight'}};
 event(context,'start');
 try{const outcome=await run(input,dependencies);if(outcome.status==='committed'){event(context,'return');return {status:'returned' as const,value:outcome.value,outcome};}event(context,'failure');return {status:'not-returned' as const,failure:outcome};}
 catch(error){event(context,'failure');return {status:'not-returned' as const,failure:{code:'PROFILE_OPERATION_MAPPING',stage:'mapping',detail:error instanceof Error?error.message:'mapping failed'}};}
}
const dispatch=createOperationHttpHandler<ApplicationIo>(${JSON.stringify(limits)},(body,io,context)=>invoke(body,io.applications&&Object.hasOwn(io.applications,${id})?io.applications[${id}]??null:DEFAULT_DEPENDENCIES,context));
export const handler=(request:Request,env:Readonly<Record<string,string|undefined>>={},io:ApplicationIo={})=>dispatch(request,env,io);
`;
 }
 return `import {APPLICATION_REQUEST_HANDLERS} from './integrations/application-request-handlers.js';
const run=APPLICATION_REQUEST_HANDLERS[${key}];
export type Dependencies=Parameters<typeof run>[1];
export interface InvocationContext {signal?:AbortSignal;cancellation?:'preflight'|'required';observe?:(event:Readonly<{phase:string;adapter:string;intent:string}>)=>void;}
function event(context:InvocationContext,phase:string){try{context.observe?.({phase,adapter:'operation',intent:${id}});}catch{}}
export async function invoke(input:unknown,dependencies:Dependencies,context:InvocationContext={}){
 if(context.cancellation==='required')return {status:'not-returned' as const,failure:{code:'PROFILE_OPERATION_CANCELLATION_UNSUPPORTED',stage:'preflight'}};
 if(context.signal?.aborted)return {status:'not-returned' as const,failure:{code:'FUNCTION_CANCELLED',stage:'preflight'}};
 if(!dependencies?.store||typeof dependencies.store.begin!=='function')return {status:'not-returned' as const,failure:{code:'PROFILE_OPERATION_PORTS_REQUIRED',stage:'preflight'}};
 event(context,'start');
 try{const outcome=await run(input,dependencies);if(outcome.status==='committed'){event(context,'return');return {status:'returned' as const,value:outcome.value,outcome};}event(context,'failure');return {status:'not-returned' as const,failure:outcome};}
 catch(error){event(context,'failure');return {status:'not-returned' as const,failure:{code:'PROFILE_OPERATION_MAPPING',stage:'mapping',detail:error instanceof Error?error.message:'mapping failed'}};}
}
export async function handler(request:Request,env:Readonly<Record<string,string|undefined>>={},io:{applications?:Readonly<Record<string,Dependencies>>;signal?:AbortSignal;cancellation?:'preflight'|'required';observe?:InvocationContext['observe']}={}){
 void env;const reply=(body:unknown,status:number)=>new Response(JSON.stringify(body,(_key,value)=>typeof value==='bigint'?value.toString():value),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
 if(request.method!=='POST')return reply({error:'METHOD_NOT_ALLOWED'},405);
 if(request.headers.get('content-type')?.split(';')[0].trim()!=='application/json')return reply({error:'CONTENT_TYPE'},415);
 let body:unknown;try{const reader=request.body?.getReader();if(!reader)throw Error('missing body');const parts:Uint8Array[]=[];let size=0,timedOut=false;const timer=setTimeout(()=>{timedOut=true;void reader.cancel().catch(()=>{});},${limits.timeout_ms});try{for(;;){const chunk=await reader.read();if(chunk.done){if(timedOut)return reply({error:'FUNCTION_TIMEOUT'},504);break;}size+=chunk.value.byteLength;if(size>${limits.request_bytes}){await reader.cancel();return reply({error:'FUNCTION_BODY_LIMIT'},413);}parts.push(chunk.value);}}finally{clearTimeout(timer);reader.releaseLock();}const bytes=new Uint8Array(size);let offset=0;for(const part of parts){bytes.set(part,offset);offset+=part.length;}body=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}catch{return reply({error:'INVALID_JSON'},400);}
 const result=await invoke(body,io.applications?.[${id}] as Dependencies,{...(io.signal?{signal:AbortSignal.any([request.signal,io.signal])}:{signal:request.signal}),...(io.cancellation?{cancellation:io.cancellation}:{}),...(io.observe?{observe:io.observe}:{})});
 return reply(result,result.status==='returned'?200:result.failure.code==='FUNCTION_CANCELLED'?409:result.failure.code==='PROFILE_OPERATION_PORTS_REQUIRED'?503:result.failure.code==='PROFILE_OPERATION_MAPPING'?400:409);
}
`;
}

// U05 pure successor owner. Legacy callable/settlement methods above are retained.
// Open Questions: J01 SDK emission, G01 actual accepted application witness.
import {closeSync,constants,fstatSync,lstatSync,openSync,readSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {types as nativeTypes} from 'node:util';
import {sha256} from './contracts.js';
import {assertDirectBusinessSourceGraphV2Current,type CheckedDirectBusinessSourceGraphV2} from '../formalization/direct-condition-binding.js';
import {renderConfiguredDirectPureOperationV2} from '../generation/configured-operation-source.js';
import {renderDirectApplicationInvocationV2} from '../generation/application-request-handlers.js';
import type {BusinessDirectApplicationImplementationV2} from './business-authoring-application.js';
import type {BusinessPureGenerationOwnerV2,GeneratedU0CallableSourceV2,ImportedU0CallableV2,CheckedDirectApplicationV2,U0SourceArtifactV2,U0FileArtifactV2} from './business-authoring-stages-v2.js';
import type {U0PureInvoke} from './u0-realization-contract.js';

interface PurePhysicalFileV2 {readonly artifact:U0FileArtifactV2;readonly fingerprint:string;readonly text:string}
const pureFail:(code:string,at:string,message:string)=>never=(code,at,message)=>reject('BUSINESS_PURE_'+code,at,message);
function purePhysicalFileV2(file:string):PurePhysicalFileV2 {
 if(typeof file!=='string'||file.length>4096||!path.isAbsolute(file)||path.normalize(file)!==file||/[\\\u0000-\u001f\u007f]/.test(file))return pureFail('FILE',String(file),'normalized absolute file required');
 const parents=()=>{let at=path.parse(file).root;const rows:string[]=[];for(const part of ['',...path.dirname(file).slice(at.length).split(path.sep).filter(Boolean)]){if(part)at=path.join(at,part);const stat=lstatSync(at,{bigint:true});if(!stat.isDirectory()||stat.isSymbolicLink())pureFail('FILE',file,'original nonsymlink parent required');rows.push(at+':'+stat.dev+':'+stat.ino);}return rows;};
 const chain=parents(),before=lstatSync(file,{bigint:true});
 if(!before.isFile()||before.isSymbolicLink()||before.size<1n||before.size>16777216n)return pureFail('FILE',file,'bounded regular original file required');
 const physical=(s:typeof before)=>[s.dev,s.ino,s.size,s.mode,s.mtimeNs,s.ctimeNs].map(String);
 const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);let size=0;const chunks:Buffer[]=[];
 try{
  if(dataDigest(physical(fstatSync(fd,{bigint:true})))!==dataDigest(physical(before)))pureFail('FILE_STALE',file,'file changed while opening');
  for(;;){const bytes=Buffer.alloc(65536),n=readSync(fd,bytes,0,bytes.length,null);if(!n)break;size+=n;if(size>16777216)pureFail('FILE',file,'byte bound exceeded');chunks.push(bytes.subarray(0,n));}
  if(dataDigest(physical(fstatSync(fd,{bigint:true})))!==dataDigest(physical(before)))pureFail('FILE_STALE',file,'file changed while reading');
 }finally{closeSync(fd);}
 if(dataDigest(physical(lstatSync(file,{bigint:true})))!==dataDigest(physical(before))||dataDigest(parents())!==dataDigest(chain)||size!==Number(before.size))pureFail('FILE_STALE',file,'original path identity changed');
 const bytes=Buffer.concat(chunks),artifact=Object.freeze({path:file,sha256:sha256(bytes),bytes:size});
 return {artifact,text:bytes.toString('utf8'),fingerprint:dataDigest({artifact,chain,physical:physical(before)})};
}
const pureModuleExtensionV2=path.extname(fileURLToPath(import.meta.url));
const pureImplementationPathsV2=[import.meta.url,...[
 '../generation/configured-operation-source','../generation/application-request-handlers',
 '../generation/configured-rule-values','../generation/configured-value-types',
 '../generation/configured-value-expressions','../generation/configured-rule-value-support',
 '../generation/configured-exact-uint64-source',
].map(relative=>new URL(relative+pureModuleExtensionV2,import.meta.url).href)];
const pureImplementationV2=()=>dataDigest({node:process.version,files:pureImplementationPathsV2.map(url=>purePhysicalFileV2(fileURLToPath(url)).fingerprint)});
const executingPureImplementationV2=pureImplementationV2();
/** Distinct component data/handles. None carries an accepted application or basis. */
export interface GeneratedDirectPureSourceComponentV2 {
 readonly kind:'generated-direct-pure-source-component-v2';readonly checked:CheckedDirectBusinessSourceGraphV2;
 readonly files:readonly U0SourceArtifactV2[];readonly source_sha256:string;readonly authority_effect:'none';
}
export interface ImportedDirectPureSourceComponentV2 {
 readonly kind:'imported-direct-pure-source-component-v2';readonly source:GeneratedDirectPureSourceComponentV2;
 readonly artifact:U0FileArtifactV2;readonly invoke:U0PureInvoke<string>;readonly authority_effect:'none';
}
// Canonical module paths cannot be reused across producer instances or epochs.
// J01 must emit to a fresh owned root, not an externally preimported module URL.
const pureImportClaimsV2=new Set<string>();
export function createDirectPureSourceComponentOwnerV2(){
 const generated=new WeakMap<object,{checked:CheckedDirectBusinessSourceGraphV2;fingerprint:string}>();
 const imported=new WeakMap<object,{source:GeneratedDirectPureSourceComponentV2;files:readonly PurePhysicalFileV2[];invoke:U0PureInvoke<string>;fingerprint:string}>();
 const assertImplementation=()=>{if(pureImplementationV2()!==executingPureImplementationV2)pureFail('IMPLEMENTATION_STALE','/generation','reload the changed pure source owner and renderers');};
 const assertSourceCurrent=(value:GeneratedDirectPureSourceComponentV2):void=>{
  const state=value&&typeof value==='object'?generated.get(value):undefined;if(!state)pureFail('HANDLE','/source','original generated source component required');
  assertImplementation();assertDirectBusinessSourceGraphV2Current(state.checked);
  if(value.checked!==state.checked||dataDigest(value)!==state.fingerprint)pureFail('STALE','/source','original checked source/files changed');
 };
 const importedFingerprint=(value:ImportedDirectPureSourceComponentV2)=>dataDigest({kind:value.kind,source:value.source.source_sha256,artifact:value.artifact,authority_effect:value.authority_effect});
 const assertCurrent=(value:ImportedDirectPureSourceComponentV2):void=>{
  const state=value&&typeof value==='object'?imported.get(value):undefined;if(!state)pureFail('HANDLE','/callable','original imported source component required');
  assertSourceCurrent(state.source);
  if(value.source!==state.source||value.invoke!==state.invoke||importedFingerprint(value)!==state.fingerprint)pureFail('STALE','/callable','original callable lineage changed');
  for(const file of state.files)if(purePhysicalFileV2(file.artifact.path).fingerprint!==file.fingerprint)pureFail('FILE_STALE',file.artifact.path,'generated source/module closure changed');
 };
 return Object.freeze({
  generate(checked:CheckedDirectBusinessSourceGraphV2):GeneratedDirectPureSourceComponentV2{
   assertImplementation();assertDirectBusinessSourceGraphV2Current(checked);
   const code=renderConfiguredDirectPureOperationV2(checked),typed=[{path:'rule.mts',content:code.rule},{path:'operation.mts',content:code.operation},{path:'invoke.mts',content:renderDirectApplicationInvocationV2(checked)}];
   const files=Object.freeze([...typed,...typed.map(file=>({path:file.path.replace(/\.mts$/,'.mjs'),content:stripTypeScriptTypes(file.content,{mode:'strip'})}))].map(file=>Object.freeze({...file,sha256:sha256(file.content)})));
   const value:GeneratedDirectPureSourceComponentV2=Object.freeze({kind:'generated-direct-pure-source-component-v2',checked,files,source_sha256:dataDigest({check:checked.check_sha256,abi:'craft.u0.pure-submission/v1-candidate',files}),authority_effect:'none'});
   generated.set(value,{checked,fingerprint:dataDigest(value)});assertSourceCurrent(value);return value;
  },
  async importGenerated(source:GeneratedDirectPureSourceComponentV2,absoluteModulePath:string):Promise<ImportedDirectPureSourceComponentV2>{
   assertSourceCurrent(source);
   if(typeof absoluteModulePath!=='string'||!path.isAbsolute(absoluteModulePath)||path.normalize(absoluteModulePath)!==absoluteModulePath||path.basename(absoluteModulePath)!=='invoke.mjs')pureFail('MODULE_PATH','/callable','actual fresh emitted invoke.mjs path required');
   const directory=path.dirname(absoluteModulePath),files=source.files.map(file=>{
    if(!/^(rule|operation|invoke)\.m[jt]s$/.test(file.path))return pureFail('MODULE_PATH',file.path,'closed pure module closure required');
    const actual=purePhysicalFileV2(path.join(directory,file.path));
    if(actual.artifact.sha256!==file.sha256||actual.artifact.bytes!==Buffer.byteLength(file.content)||actual.text!==file.content)pureFail('EMITTED_BYTES',actual.artifact.path,'actual emitted bytes must match generated source');return actual;
   });
   const url=pathToFileURL(absoluteModulePath).href;
   if(files.some(file=>pureImportClaimsV2.has(pathToFileURL(file.artifact.path).href)))pureFail('IMPORT_EPOCH',absoluteModulePath,'canonical paths are already captured; emit a new owned root');
   for(const file of files)pureImportClaimsV2.add(pathToFileURL(file.artifact.path).href);
   const module=await import(url) as {invoke?:unknown;U0_ABI?:unknown;U0_SOURCE_CHECK?:unknown};
   assertSourceCurrent(source);
   for(const file of files)if(purePhysicalFileV2(file.artifact.path).fingerprint!==file.fingerprint)pureFail('FILE_STALE',file.artifact.path,'closure changed during import');
   if(module.U0_ABI!=='craft.u0.pure-submission/v1-candidate'||module.U0_SOURCE_CHECK!==source.checked.check_sha256||typeof module.invoke!=='function'||module.invoke.length!==1||nativeTypes.isProxy(module.invoke)||nativeTypes.isAsyncFunction(module.invoke))pureFail('EXPORT','/callable','actual synchronous generated invoke and source/ABI required');
   const invoke=module.invoke as U0PureInvoke<string>,artifact=files.find(file=>file.artifact.path===absoluteModulePath)!.artifact;
   const value:ImportedDirectPureSourceComponentV2=Object.freeze({kind:'imported-direct-pure-source-component-v2',source,artifact,invoke,authority_effect:'none'});
   imported.set(value,{source,files,invoke,fingerprint:importedFingerprint(value)});assertCurrent(value);return value;
  },assertSourceCurrent,assertCurrent,
 });
}
/** Trusted public SDK assembly retains this exact original application owner. */
export function createBusinessPureGenerationOwnerV2(applications:BusinessDirectApplicationImplementationV2):BusinessPureGenerationOwnerV2 {
 const originals=[applications.assertCurrent,applications.assertConditionCurrent,applications.source];
 const components=createDirectPureSourceComponentOwnerV2();
 const generated=new WeakMap<object,{application:CheckedDirectApplicationV2;component:GeneratedDirectPureSourceComponentV2;fingerprint:string}>();
 const imported=new WeakMap<object,{source:GeneratedU0CallableSourceV2;component:ImportedDirectPureSourceComponentV2;fingerprint:string}>();
 const assertOwner=()=>{if(originals.some((method,i)=>method!==[applications.assertCurrent,applications.assertConditionCurrent,applications.source][i]))pureFail('OWNER_STALE','/application','exact original application producer methods required');};
 const assertSource=(source:GeneratedU0CallableSourceV2)=>{
  const state=source&&typeof source==='object'?generated.get(source):undefined;if(!state)return pureFail('HANDLE','/source','original application-generated source required');
  assertOwner();applications.assertCurrent(state.application);applications.assertConditionCurrent(state.application.condition);components.assertSourceCurrent(state.component);
  if(source.application!==state.application||applications.source(state.application)!==state.component.checked||source.files!==state.component.files||dataDigest(source)!==state.fingerprint)pureFail('STALE','/source','original application/source lineage changed');return state;
 };
 const fingerprint=(callable:ImportedU0CallableV2)=>dataDigest({kind:callable.kind,source:callable.source.source_sha256,artifact:callable.artifact,authority_effect:callable.authority_effect});
 const assertCurrent=(callable:ImportedU0CallableV2):void=>{
  const state=callable&&typeof callable==='object'?imported.get(callable):undefined;if(!state)pureFail('HANDLE','/callable','original application-generated import required');
  assertSource(state.source);components.assertCurrent(state.component);
  if(callable.source!==state.source||callable.invoke!==state.component.invoke||callable.artifact!==state.component.artifact||fingerprint(callable)!==state.fingerprint)pureFail('STALE','/callable','original imported callable lineage changed');
 };
 return Object.freeze({
  generate(application:CheckedDirectApplicationV2):GeneratedU0CallableSourceV2{
   assertOwner();applications.assertCurrent(application);applications.assertConditionCurrent(application.condition);
   const component=components.generate(applications.source(application));
   const source:GeneratedU0CallableSourceV2=Object.freeze({kind:'generated-u0-callable-source-v2',application,abi:'craft.u0.pure-submission/v1-candidate',export_name:'invoke',files:component.files,source_sha256:dataDigest({application:application.plan_sha256,generated:component.source_sha256}),authority_effect:'none'});
   generated.set(source,{application,component,fingerprint:dataDigest(source)});assertSource(source);return source;
  },
  async importGenerated(source:GeneratedU0CallableSourceV2,absoluteModulePath:string):Promise<ImportedU0CallableV2>{
   const state=assertSource(source),component=await components.importGenerated(state.component,absoluteModulePath);assertSource(source);
   const callable:ImportedU0CallableV2=Object.freeze({kind:'imported-u0-callable-v2',source,artifact:component.artifact,invoke:component.invoke,authority_effect:'none'});
   imported.set(callable,{source,component,fingerprint:fingerprint(callable)});assertCurrent(callable);return callable;
  },assertCurrent,
 });
}
