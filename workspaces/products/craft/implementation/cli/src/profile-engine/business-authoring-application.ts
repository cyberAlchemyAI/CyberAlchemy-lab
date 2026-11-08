import {closeSync,constants,fstatSync,lstatSync,openSync,readSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,canonicalJson,dataDigest,ProfileRejected,reject,sha256,validateCompositionShape,type Component,type CompositionData,type Json,type Origin} from './contracts.js';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertSelectedReconciledProject,type SelectedReconciledProject} from '../generation/selected-reconciled-project.js';
import {compileRequestApplicationBindingV1,type RequestApplicationBindingV1} from '../system-integration/application-binding-v1.js';
import {composeRequestApplicationPlanV1,type RequestApplicationPlanV1} from '../generation/request-application-plan-v1.js';
import {prepareRequestApplicationCallable,assertApplicationCallableCurrent,assertBusinessApplicationPlanCurrent,renderApplicationCallableSource,type CheckedRequestApplicationCallable} from './application-adapter.js';
import {assertAuthoringBusinessInputCurrent,type AuthoringBusinessInput} from './business-authoring-input.js';
import {assertBusinessAuthoringRequestsCurrent,type BusinessAuthoringRequestPreparation} from './business-authoring-request.js';
import {businessAuthoringRecipeSnapshot,type BusinessRecipeSelection} from './business-authoring-recipes.js';
import {withBusinessAuthoringSnapshotValidation,type BusinessAuthoringSnapshot} from './loader-v3.js';
import {compileFormalConditionBindings} from '../formalization/condition-binding.js';
import {evaluateProfile,type Evaluation} from './evaluate.js';
import {renderProfileTemplate} from './render.js';
import {outputImport} from '../generation/output-layout.js';
import type {SelectedEmission} from './compose.js';
import type {AuthoringBusinessInputV2,BusinessInputOwnerV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessDirectApplicationOwnerV2,CheckedDirectApplicationV2,U0CheckedBusinessGraphV2,DirectConditionBindingV2} from './business-authoring-stages-v2.js';
import {projectDirectExecutableV2,projectOptionalAssuranceV2} from './business-authoring-identity-v2.js';
import {checkDirectBusinessSourceGraphV2,assertDirectBusinessSourceGraphV2Current,createDirectConditionBindingOwnerV2,type CheckedDirectBusinessSourceGraphV2} from '../formalization/direct-condition-binding.js';

/** Actual checked Alch preparation supplied by a trusted host, never a profile callback.
 * Core independently checks every Core registry; this structural surface alone is not Alch provenance.
 * Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md; installed/CLI/output qualification is separate. */
export interface BusinessAuthoringCheckedPreparation {
 readonly kind:'prepared-business-authoring-application';readonly input:AuthoringBusinessInput;
 readonly materialized:Readonly<{model_id:string;requests:BusinessAuthoringRequestPreparation;compatibility:AuthoringBusinessInput['compatibility']}>;
 readonly derived:Readonly<{application_id:string;source_sha256:string;derivation_sha256:string;line_map:CheckedRequestApplicationCallable['lineage']['line_map'];files:Readonly<Record<string,string>>;formation:Readonly<{files:Readonly<Record<string,string>>;conditions:unknown}>}>;
 readonly graph:CompiledProjectGraph;readonly executable:Readonly<{plan:SelectedReconciledProject;join:unknown}>;
}
export interface BusinessAuthoringApplicationModel {
 readonly model_id:string;readonly input:AuthoringBusinessInput;readonly graph:CompiledProjectGraph;
 readonly application_plan:SelectedReconciledProject;readonly binding:RequestApplicationBindingV1;readonly plan:RequestApplicationPlanV1;
 readonly callables:readonly CheckedRequestApplicationCallable[];
 readonly formal:Readonly<{sources:Readonly<Record<string,string>>;conditions:Json;join:ReturnType<typeof compileFormalConditionBindings>}>;
}
export interface BusinessAuthoringApplicationRoute {readonly id:string;readonly model_id:string;readonly method:'POST';readonly route:string;readonly entry:string;readonly request_bytes:number;readonly timeout_ms:number}
export interface BusinessAuthoringApplication {
 readonly kind:'business-authoring-application';readonly checked:readonly BusinessAuthoringCheckedPreparation[];
 readonly requests:BusinessAuthoringRequestPreparation;readonly selection:BusinessRecipeSelection;readonly authoring_snapshot:BusinessAuthoringSnapshot;
 readonly models:readonly BusinessAuthoringApplicationModel[];readonly applications:readonly CheckedRequestApplicationCallable[];readonly callables:readonly CheckedRequestApplicationCallable[];
 readonly routes:readonly BusinessAuthoringApplicationRoute[];readonly emissions:readonly SelectedEmission[];readonly evaluations:readonly Readonly<{package_id:string;evaluation:Evaluation}>[];
 readonly composition:CompositionData;readonly files:Readonly<Record<string,string>>;readonly application_sha256:string;readonly authority_effect:'none';
}
type Owner={checked:readonly BusinessAuthoringCheckedPreparation[];assertChecked:(checked:BusinessAuthoringCheckedPreparation)=>void;models:readonly BusinessAuthoringApplicationModel[];requests:BusinessAuthoringRequestPreparation;snapshot:BusinessAuthoringSnapshot;module:string;fingerprint:string};
const registry=new WeakMap<object,Owner>();
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
function fail(code:string,at:string,message:string):never{return reject('BUSINESS_AUTHORING_APPLICATION_'+code,at,message);}
function same(a:unknown,b:unknown,at:string):void {if(dataDigest(a)!==dataDigest(b))fail('CORRESPONDENCE',at,'exact original checked/request/profile correspondence required');}
function ownedPath(value:unknown):string {if(typeof value!=='string'||!value||value.length>4096||path.posix.isAbsolute(value)||value.includes('\\')||value.split('/').some(part=>!part||part==='.'||part==='..'||part==='.git'||part.startsWith('.profile-'))||/[\x00-\x1f\x7f]/.test(value))fail('PATH',String(value),'owned nonreserved output path required');return value as string;}
function moduleIdentity():string {
 const file=fileURLToPath(import.meta.url);
 try{
  const ancestors=()=>{let cursor=path.parse(file).root;const result:string[]=[];for(const part of ['',...file.slice(cursor.length).split(path.sep).filter(Boolean)]){if(part)cursor=path.join(cursor,part);const stat=lstatSync(cursor,{bigint:true});if(stat.isSymbolicLink())fail('MODULE_STALE',file,'module path symlinks are forbidden');result.push(`${stat.dev}:${stat.ino}:${stat.mode}`);}return result;};
  const owners=ancestors(),before=lstatSync(file,{bigint:true});if(!before.isFile()||before.size>16777216n)fail('MODULE_STALE',file,'bounded regular implementation required');
  const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),buffers:Buffer[]=[];let bytes=0;
  const physical=(s:BigIntStats)=>s.isFile()&&s.dev===before.dev&&s.ino===before.ino&&s.mode===before.mode&&s.size===before.size&&s.mtimeNs===before.mtimeNs&&s.ctimeNs===before.ctimeNs;
  try{if(!physical(fstatSync(fd,{bigint:true})))fail('MODULE_STALE',file,'module changed while opening');for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>16777216)fail('MODULE_STALE',file,'module budget exceeded');buffers.push(buffer.subarray(0,count));}if(!physical(fstatSync(fd,{bigint:true})))fail('MODULE_STALE',file,'module changed during capture');}finally{closeSync(fd);}
  if(BigInt(bytes)!==before.size||!physical(lstatSync(file,{bigint:true}))||dataDigest(ancestors())!==dataDigest(owners))fail('MODULE_STALE',file,'module path or ancestor changed');
  return dataDigest({owners,sha256:sha256(Buffer.concat(buffers)),mtime:String(before.mtimeNs),ctime:String(before.ctimeNs)});
 }catch(error){if(error instanceof ProfileRejected)throw error;return fail('MODULE_STALE',file,'owning implementation is unavailable');}
}
const executingModule=moduleIdentity();
function assertModule():string {const current=moduleIdentity();if(current!==executingModule)fail('MODULE_STALE','/','reload the owning application implementation after changes');return current;}
function assertCheckedCore(value:BusinessAuthoringCheckedPreparation,requests:BusinessAuthoringRequestPreparation,snapshot:BusinessAuthoringSnapshot):void {
 if(value?.kind!=='prepared-business-authoring-application')fail('CHECKED','/checked','original checked preparation required');
 assertAuthoringBusinessInputCurrent(value.input);assertCompiledProjectSnapshot(value.graph);assertSelectedReconciledProject(value.executable.plan);assertBusinessApplicationPlanCurrent(value.graph,value.executable.plan);
 const input=value.input,modelId=value.materialized.model_id;
 if(input.requests!==requests||value.materialized.requests!==requests||input.authoring_snapshot!==snapshot||input.compatibility.model_id!==modelId||input.accepted.review.model_id!==modelId||value.derived.application_id!==modelId||input.applications.length!==1||input.applications[0]!.model.id!==modelId)fail('CHECKED','/checked','same original input, model, request and authoring snapshot required');
 same(value.materialized.compatibility,input.compatibility,'/compatibility');
 const explicitSource=input.compatibility.source.replace(/^(domain[^\n]*\n)/,'$1profile application-v1\n');if(sha256(explicitSource)!==value.derived.source_sha256)fail('CHECKED','/derived/source_sha256','actual generated domain source identity required');
 // The selected checked action owner must retain the finite one-input/empty-effects contract.
 const selected=requests.selection.models.find(model=>model.model_id===modelId)!;
 if(!selected)fail('CHECKED','/model_id','selected model required');
 const expected=selected.behavior.operations.map(operation=>selected.spec.identity.namespace.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase()+':'+operation.operation_ref.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase()).sort(compare);
 same(value.executable.plan.selection.operations.map(operation=>operation.selector).sort(compare),expected,'/plan/operations');
 const normalized=(name:string)=>name.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase(),feature=normalized(selected.spec.identity.namespace);
 for(const operation of value.executable.plan.selection.operations){
  if(operation.inputs.length!==1||operation.reads.length||operation.writes.length||operation.events.length)fail('EFFECTS',operation.selector,'one-input, empty-effects Operation required');
  const business=selected.behavior.operations.find(row=>feature+':'+normalized(row.operation_ref)===operation.selector)!;
  if(!business)fail('CHECKED',operation.selector,'exact normalized business Operation required');
  const parameter=normalized(business.input.name).replaceAll('-','_'),whole={op:'path',root:parameter,properties:[]};
  same(operation.inputs.map(input=>input.name),[parameter],'/plan/operations/input');same(operation.result.value,whole,'/plan/operations/result');same(operation.result.type,operation.inputs[0]!.type,'/plan/operations/result/type');
  same(operation.guards,business.guards.map(guard=>({selector:feature+':'+normalized(guard.rule_ref),arguments:[{parameter:normalized(guard.parameter.name).replaceAll('-','_'),value:whole}]})),'/plan/operations/guards');
 }

}
function fingerprint(value:BusinessAuthoringApplication):string {return dataDigest({models:value.models.map(model=>({model_id:model.model_id,binding:model.binding.binding_sha256,plan:model.plan.plan_sha256,application_plan:model.application_plan.plan_sha256,graph:model.graph.source_manifest.manifest_sha256,callables:model.callables.map(callable=>({intent:callable.intent,lineage:callable.lineage,operation_module:callable.operation_module})),formal:model.formal})),routes:value.routes,emissions:value.emissions,evaluations:value.evaluations,composition:value.composition,files:value.files,sha256:value.application_sha256});}
function prepareApplication(checked:readonly BusinessAuthoringCheckedPreparation[],assertCheckedCurrent:(checked:BusinessAuthoringCheckedPreparation)=>void):BusinessAuthoringApplication {
 if(!Array.isArray(checked)||!checked.length||checked.length>32||typeof assertCheckedCurrent!=='function')fail('CHECKED','/checked','nonempty bounded original checked preparations and trusted host currentness required');
 const supplied:readonly BusinessAuthoringCheckedPreparation[]=Object.freeze([...checked]);for(const value of supplied)assertCheckedCurrent(value);const originals=Object.freeze([...supplied].sort((a,b)=>compare(a.materialized.model_id,b.materialized.model_id))),module=assertModule(),requests=originals[0]!.input.requests;assertBusinessAuthoringRequestsCurrent(requests);const snapshot=businessAuthoringRecipeSnapshot(requests.selection);
 for(const value of originals)assertCheckedCore(value,requests,snapshot);
 same(originals.map(value=>value.materialized.model_id).sort(compare),requests.models.map(model=>model.model_id).sort(compare),'/checked/models');
 const runtime=originals[0]!.input.runtime,emissions:SelectedEmission[]=[],evaluations:{package_id:string;evaluation:Evaluation}[]=[],models:BusinessAuthoringApplicationModel[]=[],callables:CheckedRequestApplicationCallable[]=[],routes:BusinessAuthoringApplicationRoute[]=[],files:Record<string,string>=Object.create(null),components:Component[]=[];
 const put=(relative:unknown,body:string)=>{const file=ownedPath(relative);if(Object.hasOwn(files,file))fail('COLLISION',file,'one exact artifact owner required');files[file]=body;};
 const tables=originals.map(value=>value.input.metadata_tables),mergedTables=Object.fromEntries((Object.keys(tables[0]!) as (keyof AuthoringBusinessInput['metadata_tables'])[]).map(key=>[key,{fields:tables[0]![key].fields,rows:tables.flatMap(table=>table[key].rows)}]));
 for(const pkg of snapshot.packages){const evaluation=evaluateProfile(pkg.data,mergedTables);evaluations.push({package_id:pkg.id,evaluation});for(const emission of evaluation.emissions)emissions.push(Object.freeze({package_id:pkg.id,package_sha256:pkg.manifest_sha256,emission}));}
 const applicationEmissions=emissions.filter(row=>row.emission.role==='application-operation'),dispatchers=emissions.filter(row=>row.emission.role==='http-dispatch'),shared=emissions.filter(row=>row.emission.role==='shared-http-port');
 if(dispatchers.length!==1||applicationEmissions.length!==requests.project_intents.length||emissions.some(row=>!['application-operation','http-dispatch','shared-http-port'].includes(row.emission.role)))fail('ROLE','/emissions','one dispatcher and exact authored application roles required');
 if(runtime.data.application_runtime.transport==='shared'?(shared.length!==1||shared[0]!.package_id!==runtime.id):shared.length!==0)fail('TRANSPORT','/emissions','exact selected local/shared Operation transport owner required');
 const profileOrigin=(row:SelectedEmission):Origin=>({kind:'profile-rule',source:row.package_id+'/profile.json',selector:row.emission.rule,sha256:row.package_sha256});
 const sharedId=shared[0]?'shared_http_port_'+String(shared[0].emission.fields.id):undefined,sharedPath=shared[0]?ownedPath(shared[0].emission.fields.artifact_path):undefined;
 if(sharedPath){if(!/^runtime\/[A-Za-z0-9_-]+\.mts$/.test(sharedPath))fail('TRANSPORT',sharedPath,'shared typed transport must own one runtime module');same(shared[0]!.emission.fields.technical,{kind:'application-operation'},'/shared/technical');put(sharedPath,runtime.assets[runtime.data.application_runtime.transport_asset]!.text!);components.push({id:sharedId!,role:'shared-http-port',owner:runtime.id,artifact_paths:[sharedPath],depends_on:[],origins:[profileOrigin(shared[0]!)],contract_ref:'typescript.operation-http-port/v2-candidate'});}
 const seen=new Set<string>(),seenRoutes=new Set<string>();
 for(const original of originals){
  const modelId=original.materialized.model_id,request=requests.models.find(model=>model.model_id===modelId)!,input=original.input,application=input.applications[0]!,modelCallables:CheckedRequestApplicationCallable[]=[];
  const formalSources:Record<string,string>=Object.create(null);
  for(const source of [captureJson(original.derived.files),captureJson(original.derived.formation.files)]){
   if(!source||typeof source!=='object'||Array.isArray(source))fail('FORMAL','/formal/sources','actual captured formal source dictionaries required');
   for(const [key,body] of Object.entries(source)){ownedPath(key);if(typeof body!=='string'||Object.hasOwn(formalSources,key)&&formalSources[key]!==body)fail('FORMAL',key,'exact nonconflicting formal raw bytes required');formalSources[key]=body;}
  }
  const conditions=captureJson(original.derived.formation.conditions),join=compileFormalConditionBindings(original.graph,conditions,new Map(Object.entries(formalSources).map(([key,body])=>[key,Buffer.from(body)])));same(join,original.executable.join,'/formal/join');
  const formal=Object.freeze({sources:captureJson(formalSources) as Readonly<Record<string,string>>,conditions,join});
  const binding=compileRequestApplicationBindingV1(original.graph,request.request_source,original.executable.plan),plan=composeRequestApplicationPlanV1(original.executable.plan,binding);
  for(const intent of input.snapshot.project.application_intents){
   const choices=applicationEmissions.filter(row=>row.package_id===runtime.id&&row.emission.fields.id===intent.id),choice=choices[0];if(choices.length!==1||!choice||seen.has(intent.id))fail('ROLE',intent.id,'one exact selected application role required');
   const fields=choice.emission.fields,entry=ownedPath(fields.artifact_path??'entries/'+intent.id+'.mjs'),wire=request.request_source.entries.find(entry=>entry.id===intent.id)!;
   if(fields.project_ref!==application.model.source||fields.selector!==intent.operation_ref||fields.route!==wire.route.path||seenRoutes.has(wire.route.path))fail('ROLE',intent.id,'exact authored operation/exposure and selected route required');
   same(fields.technical,{request_bytes:requests.selection.technical.wire.request_bytes,timeout_ms:requests.selection.technical.wire.timeout_ms},'/emissions/'+intent.id+'/technical');
   const assertCurrent=()=>withBusinessAuthoringSnapshotValidation(snapshot,()=>{assertCheckedCurrent(original);assertCheckedCore(original,requests,snapshot);assertModule();});
   const callable=prepareRequestApplicationCallable(original.graph,plan,binding,intent,{application_id:modelId,original_source:application.model.source,original_source_sha256:application.source_sha256,original_semantics_sha256:application.semantics_sha256,derived_source_sha256:original.derived.source_sha256,derivation_sha256:original.derived.derivation_sha256,line_map:original.derived.line_map},assertCurrent);
   modelCallables.push(callable);callables.push(callable);seen.add(intent.id);seenRoutes.add(wire.route.path);
   const prefix='applications/'+intent.id+'/',owned:string[]=[];for(const artifact of plan.artifacts){const file=prefix+artifact.relative_path;put(file,artifact.content);owned.push(file);}
   put(prefix+'package.json','{"type":"module","private":true}\n');owned.push(prefix+'package.json');
   const settlement=prefix+'src/empty-settlement.ts';put(settlement,runtime.assets[runtime.data.application_runtime.settlement_asset]!.text!);owned.push(settlement);
   const transport=sharedPath?sharedPath.replace(/^runtime\//,'runtime/lib/').replace(/\.mts$/,'.mjs'):prefix+'src/application-http.mjs';
   if(!sharedPath){const local=prefix+'src/application-http.mts';put(local,runtime.assets[runtime.data.application_runtime.transport_asset]!.text!);owned.push(local);}
   const source=prefix+'src/profile-entry.ts';put(source,renderApplicationCallableSource(callable,{request_bytes:requests.selection.technical.wire.request_bytes,timeout_ms:requests.selection.technical.wire.timeout_ms},{settlement_import:'./empty-settlement.js',transport_import:outputImport(source,transport)}));owned.push(source);
   put(entry,`import {handler as invoke} from ${JSON.stringify(outputImport(entry,prefix+'lib/profile-entry.js'))};\nexport const config=${canonicalJson({method:'POST',route:wire.route.path})};\nexport const handler=invoke;\n`);owned.push(entry);
   const selectedModel=requests.selection.models.find(model=>model.model_id===modelId)!,exposure=request.mappings.find(mapping=>mapping.public_name===intent.id)!;
   components.push({id:'application_operation_'+intent.id,role:'application-operation',owner:runtime.id,artifact_paths:owned,depends_on:sharedId?[sharedId]:[],origins:[{kind:'business',source:selectedModel.source.path,selector:'capability:'+exposure.exposure_id,sha256:selectedModel.source.sha256},profileOrigin(choice)],contract_ref:'typescript.bound-operation/v2-candidate'});
   routes.push({id:intent.id,model_id:modelId,method:'POST',route:wire.route.path,entry,request_bytes:requests.selection.technical.wire.request_bytes,timeout_ms:requests.selection.technical.wire.timeout_ms});
  }
  models.push(Object.freeze({model_id:modelId,input,graph:original.graph,application_plan:original.executable.plan,binding,plan,callables:Object.freeze(modelCallables),formal}));
 }
 if(seen.size!==requests.project_intents.length)fail('ROLE','/applications','every exact authored exposure requires a checked callable');
 const dispatcher=dispatchers[0]!,dispatcherPath=ownedPath(dispatcher.emission.fields.artifact_path),dispatcherPackage=snapshot.packages.find(pkg=>pkg.id===dispatcher.package_id)!,imports=routes.map((route,index)=>({import:outputImport(dispatcherPath,route.entry),alias:'entry'+index}));
 const template=dispatcher.emission.fields.template_ref;
 put(dispatcherPath,typeof template==='string'?renderProfileTemplate(dispatcherPackage,template,{entries:imports as unknown as Json}):imports.map(row=>`import * as ${row.alias} from ${JSON.stringify(row.import)};`).join('\n')+`\nconst entries=[${imports.map(row=>row.alias).join(',')}];\n/** @param {Request} request @param {Record<string,string|undefined>} [env] @param {{applications?:Record<string,any>,signal?:AbortSignal,cancellation?:'preflight'|'required',observe?:(event:any)=>void}} [io] */\nexport async function handler(request,env={},io={}){const entry=entries.find(e=>e.config.route===new URL(request.url).pathname);return entry?entry.handler(request,env,io):new Response(JSON.stringify({error:'NOT_FOUND'}),{status:404,headers:{'content-type':'application/json'}});}\n`);
 components.push({id:'http_dispatch_'+String(dispatcher.emission.fields.id),role:'http-dispatch',owner:dispatcher.package_id,artifact_paths:[dispatcherPath],depends_on:routes.map(route=>'application_operation_'+route.id),origins:[profileOrigin(dispatcher)],contract_ref:'service-v1#handler'});put('package.json','{"type":"module","private":true}\n');
 const body={schema_version:'craft.profile-composition/v1',source_sha256:snapshot.lock.source_sha256,lock_sha256:snapshot.lock.lock_sha256,components,authority_effect:'none'},composition=validateCompositionShape({...body,composition_sha256:dataDigest(body)}),captured=captureJson({routes,files}) as unknown as {routes:BusinessAuthoringApplication['routes'];files:BusinessAuthoringApplication['files']},apps=Object.freeze(callables),frozenModels=Object.freeze(models);
 const value:BusinessAuthoringApplication=Object.freeze({kind:'business-authoring-application',checked:originals,requests,selection:requests.selection,authoring_snapshot:snapshot,models:frozenModels,applications:apps,callables:apps,routes:captured.routes,emissions:Object.freeze(emissions),evaluations:Object.freeze(evaluations.map(row=>Object.freeze(row))),composition,files:captured.files,application_sha256:dataDigest({composition,files:captured.files,plans:models.map(model=>model.plan.plan_sha256),formal:models.map(model=>model.formal)}),authority_effect:'none'});
 registry.set(value,{checked:originals,assertChecked:assertCheckedCurrent,models:frozenModels,requests,snapshot,module,fingerprint:fingerprint(value)});assertBusinessAuthoringApplicationCurrent(value);return value;
}
function assertApplication(value:BusinessAuthoringApplication):void {
 const state=value&&typeof value==='object'?registry.get(value):undefined;if(!state)fail('UNREGISTERED','/','original registered application bundle required; JSON is not custody');
 if(assertModule()!==state.module||value.checked!==state.checked||value.models!==state.models||value.requests!==state.requests||value.selection!==state.requests.selection||value.authoring_snapshot!==state.snapshot||value.applications!==value.callables||fingerprint(value)!==state.fingerprint)fail('STALE','/','application bundle ownership or data changed');
 assertBusinessAuthoringRequestsCurrent(state.requests);if(businessAuthoringRecipeSnapshot(state.requests.selection)!==state.snapshot)fail('STALE','/snapshot','original snapshot required');
 for(const original of state.checked){state.assertChecked(original);assertCheckedCore(original,state.requests,state.snapshot);}for(const callable of value.callables)assertApplicationCallableCurrent(callable);
}
/** Bracket pure construction in one fully checked synchronous snapshot epoch. */
export function prepareBusinessAuthoringApplication(checked:readonly BusinessAuthoringCheckedPreparation[],assertCheckedCurrent:(checked:BusinessAuthoringCheckedPreparation)=>void):BusinessAuthoringApplication {
 if(!Array.isArray(checked)||!checked.length||checked.length>32||typeof assertCheckedCurrent!=='function'||!checked[0]?.input?.authoring_snapshot)fail('CHECKED','/checked','nonempty original checked preparations required');
 return withBusinessAuthoringSnapshotValidation(checked[0]!.input.authoring_snapshot,()=>prepareApplication(checked,assertCheckedCurrent));
}
export function assertBusinessAuthoringApplicationCurrent(value:BusinessAuthoringApplication):void {
 const state=value&&typeof value==='object'?registry.get(value):undefined;if(!state)fail('UNREGISTERED','/','original registered application bundle required; JSON is not custody');
 withBusinessAuthoringSnapshotValidation(state.snapshot,()=>assertApplication(value));
}
export function renderBusinessAuthoringApplication(value:BusinessAuthoringApplication):Readonly<Record<string,string>> {assertBusinessAuthoringApplicationCurrent(value);return value.files;}

/** Trusted prefix/SDK graph capture, never profile JSON or a caller evaluator.
 * J01/G01 bind original input to the actual Alch-derived project workspace. */
export interface BusinessDirectGraphCaptureOwnerV2 {
 capture(input:AuthoringBusinessInputV2):CompiledProjectGraph;
 assertCurrent(input:AuthoringBusinessInputV2,graph:CompiledProjectGraph):void;
}
export interface BusinessDirectApplicationImplementationV2 extends BusinessDirectApplicationOwnerV2 {
 source(application:CheckedDirectApplicationV2):CheckedDirectBusinessSourceGraphV2;
}
/** Additive pure successor. No call to the mandatory formal-claim join, no empty
 * Rule inventory and no legacy transaction/settlement selection. Open Questions:
 * U04/G01 actual accepted-input/graph witness; U05 generated pure callable. */
export function createBusinessDirectApplicationOwnerV2(inputs:BusinessInputOwnerV2,graphs:BusinessDirectGraphCaptureOwnerV2):BusinessDirectApplicationImplementationV2 {
 const original=[inputs.form,inputs.assertCurrent,graphs.capture,graphs.assertCurrent];
 const graphOwned=new WeakMap<object,{input:AuthoringBusinessInputV2;source:CheckedDirectBusinessSourceGraphV2;fingerprint:string}>();
 const applicationOwned=new WeakMap<object,{input:AuthoringBusinessInputV2;graph:U0CheckedBusinessGraphV2;condition:DirectConditionBindingV2;source:CheckedDirectBusinessSourceGraphV2;fingerprint:string}>();
 const current=()=>{
  assertModule();if([inputs.form,inputs.assertCurrent,graphs.capture,graphs.assertCurrent].some((method,i)=>method!==original[i]))fail('OWNER_STALE','/direct-v2','exact original input/graph producer changed');
 };
 const assertGraphCurrent=(graph:U0CheckedBusinessGraphV2):void=>{
  const state=graph&&typeof graph==='object'?graphOwned.get(graph):undefined;if(!state)fail('UNREGISTERED','/direct-v2/graph','original registered checked graph required');
  current();inputs.assertCurrent(state.input);assertDirectBusinessSourceGraphV2Current(state.source);graphs.assertCurrent(state.input,state.source.graph);
  if(graph.input!==state.input||graph.closures!==state.source.closures||dataDigest(graph)!==state.fingerprint)fail('STALE','/direct-v2/graph','original input/source/graph correspondence changed');
 };
 const graphSource=(graph:U0CheckedBusinessGraphV2):CheckedDirectBusinessSourceGraphV2=>{assertGraphCurrent(graph);return graphOwned.get(graph)!.source;};
 const conditions=createDirectConditionBindingOwnerV2(Object.freeze({assertCurrent:assertGraphCurrent,source:graphSource}));
 const assertCurrent=(application:CheckedDirectApplicationV2):void=>{
  const state=application&&typeof application==='object'?applicationOwned.get(application):undefined;if(!state)fail('UNREGISTERED','/direct-v2/application','original checked application from this exact owner required');
  assertGraphCurrent(state.graph);conditions.assertCurrent(state.condition);
  if(application.input!==state.input||application.graph!==state.graph||application.condition!==state.condition||dataDigest(application)!==state.fingerprint)fail('STALE','/direct-v2/application','original pure application/input/condition changed');
 };
 return Object.freeze({check(input:AuthoringBusinessInputV2):CheckedDirectApplicationV2{
  current();inputs.assertCurrent(input);
  const model=input.selection.models.find(model=>model.model_id===input.model_id);if(!model)fail('CHECKED','/direct-v2/input','original selected model required');
  const graph=graphs.capture(input);graphs.assertCurrent(input,graph);assertCompiledProjectSnapshot(graph);
  const source=checkDirectBusinessSourceGraphV2(graph,{source:model.source,spec:input.spec,executable:projectDirectExecutableV2(input.spec),assurance:projectOptionalAssuranceV2(input.spec)});
  if(input.capture.capture_sha256!==model.capture.capture_sha256||source.checked.executable_sha256!==model.executable_sha256||source.checked.assurance_sha256!==model.assurance_sha256)fail('CHECKED','/direct-v2/input','original selected source/capture/meaning required');
  const body={kind:'checked-u0-business-graph-v2' as const,input,closures:source.closures,authority_effect:'none' as const};
  const checkedGraph:U0CheckedBusinessGraphV2=Object.freeze({...body,graph_sha256:dataDigest({input_sha256:input.input_sha256,core_graph_sha256:source.graph_sha256,source_check_sha256:source.check_sha256,closures:source.closures})});
  graphOwned.set(checkedGraph,{input,source,fingerprint:dataDigest(checkedGraph)});assertGraphCurrent(checkedGraph);
  const condition=conditions.bind(checkedGraph),operation=source.operation;
  const application:CheckedDirectApplicationV2=Object.freeze({kind:'checked-direct-application-v2',input,graph:checkedGraph,condition,operation_ref:operation.operation_ref,plan_sha256:dataDigest({input_sha256:input.input_sha256,graph_sha256:checkedGraph.graph_sha256,condition_sha256:condition.condition_sha256,pure_operation_sha256:operation.plan_sha256}),authority_effect:'none'});
  applicationOwned.set(application,{input,graph:checkedGraph,condition,source,fingerprint:dataDigest(application)});assertCurrent(application);return application;
 },assertCurrent,assertConditionCurrent:conditions.assertCurrent,source(application:CheckedDirectApplicationV2){assertCurrent(application);return applicationOwned.get(application)!.source;}});
}
