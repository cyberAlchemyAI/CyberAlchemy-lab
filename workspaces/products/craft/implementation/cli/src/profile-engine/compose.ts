import {planCompiledProjectBuild} from '../generation/project-build.js';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {captureJson,dataDigest,reject,validateCompositionShape,PROFILE_ROLE_CONTRACTS,type Json,type Component,type CompositionData,type Origin} from './contracts.js';
import {assertProfileSnapshotCurrent,type ProfileSnapshot,type ProfileSnapshotV2,type LoadedPackage} from './loader.js';
import {prepareProfileBusinessInput,assertProfileBusinessInputCurrent,type BusinessInput} from './business-input.js';
import {evaluateProfile,type TypedTable,type Emission,type Evaluation} from './evaluate.js';
import {assertApplicationCallableCurrent,type CheckedApplicationCallable} from './application-adapter.js';
import {prepareBusinessInputV2,assertBusinessInputV2Current,type BusinessInputV2} from './business-input-v2.js';
import {PROFILE_ROLE_CONTRACTS_V2} from './contracts-v2.js';
import {projectOperationalExpectations} from './operational-expectations.js';

/** Registered profile metadata -> existing checked domain graphs -> unique owned
 * artifacts. Open questions: PE14 application graph and PE08 native qualification. */
export interface SelectedEmission {readonly package_id:string;readonly package_sha256:string;readonly emission:Emission}
export interface ProfileSelection {readonly input:BusinessInput;readonly business_applications?:BusinessInputV2;readonly emissions:readonly SelectedEmission[];readonly evaluations:readonly Readonly<{package_id:string;evaluation:Evaluation}>[];readonly sha256:string}
export interface CompiledFunctionContribution {readonly intent_id:string;readonly source:string;readonly graph:CompiledProjectGraph;readonly artifacts:Readonly<Record<string,string>>;readonly assert_current:()=>void}
export interface OwnedArtifact {readonly path:string;readonly content:string;readonly owner:string;readonly origins:readonly Origin[]}
export interface CheckedComposition {readonly data:CompositionData;readonly selection:ProfileSelection;readonly artifacts:readonly OwnedArtifact[];readonly functions:readonly CompiledFunctionContribution[];readonly applications:readonly CheckedApplicationCallable[]}
const selections=new WeakMap<object,ProfileSnapshot|ProfileSnapshotV2>(),compositions=new WeakMap<object,{snapshot:ProfileSnapshot|ProfileSnapshotV2;fingerprint:string}>();
const normalizedPath=(p:string)=>{if(!p||p.startsWith('/')||p.includes('\\')||p.includes('\0')||p.split('/').some(v=>!v||v==='.'||v==='..')||p.split('/').some(v=>['.git','.profile-complete.json','.profile-manifest.json'].includes(v)))reject('PROFILE_ARTIFACT_PATH',p,'owned non-reserved relative artifact path required');return p;};
export function selectProfileConfiguration(snapshot:ProfileSnapshot|ProfileSnapshotV2):ProfileSelection {
 assertProfileSnapshotCurrent(snapshot);const input=prepareProfileBusinessInput(snapshot),business_applications=snapshot.project.schema_version==='craft.profile-project/v2-candidate'&&snapshot.project.application_models.length?prepareBusinessInputV2(snapshot as ProfileSnapshotV2):undefined;
 const tables:Record<string,TypedTable>={
  intents:{fields:{id:'string',source:'string',input_ref:'string',output_ref:'string',result_ref:'string',access_kind:'string'},rows:input.project.public_intents.map(i=>({id:i.id,source:i.source,input_ref:i.input_ref,output_ref:i.output_ref,result_ref:i.result_ref,access_kind:i.access.kind}))},
  reads:{fields:{id:'string',source:'string',output_ref:'string'},rows:input.project.external_reads.map(r=>({id:r.id,source:r.source,output_ref:r.output_ref}))},
  declarations:{fields:{id:'string',source:'string',selector:'string'},rows:input.selectors.filter(s=>!s.selector.includes('#clause:')).map(s=>({id:s.selector.split(':')[1]!,source:s.source,selector:s.selector}))},
  applications:{fields:{id:'string',source:'string',selector:'string'},rows:(input.project.application_calls??[]).map(call=>({id:call.id,source:call.source,selector:call.operation_ref}))},
 };
 const emissions:SelectedEmission[]=[],evaluations:{package_id:string;evaluation:Evaluation}[]=[];
 for(const pkg of snapshot.packages){const evaluation=evaluateProfile(pkg.data,pkg.data.schema_version==='craft.profile-package/v2-candidate'&&business_applications?{...tables,...business_applications.metadata_tables}:tables);evaluations.push({package_id:pkg.id,evaluation});for(const emission of evaluation.emissions)emissions.push(Object.freeze({package_id:pkg.id,package_sha256:pkg.manifest_sha256,emission}));}
 const body={source_sha256:input.source_sha256,lock_sha256:snapshot.lock.lock_sha256,emissions,evaluations};
 const selection=Object.freeze({input,...(business_applications?{business_applications}:{}),emissions:Object.freeze(emissions),evaluations:Object.freeze(evaluations.map(e=>Object.freeze(e))),sha256:dataDigest(body)});selections.set(selection,snapshot);return selection;
}
export function assertProfileSelectionCurrent(selection:ProfileSelection):ProfileSnapshot|ProfileSnapshotV2 {
 const snapshot=selections.get(selection);if(!snapshot)reject('PROFILE_SELECTION_UNREGISTERED','/','reconstruct selection from exact locked inputs');assertProfileBusinessInputCurrent(selection.input);if(selection.business_applications)assertBusinessInputV2Current(selection.business_applications);return snapshot;
}
export function profileTechnicalSelections(selection:ProfileSelection):readonly Readonly<Record<string,Json>>[] {
 assertProfileSelectionCurrent(selection);const out:Readonly<Record<string,Json>>[]=[],seen=new Set<string>(),routes=new Set<string>();
 for(const selected of selection.emissions.filter(e=>e.emission.role==='http-entry')){
  const fields=selected.emission.fields,intent=selection.input.project.public_intents.find(i=>i.id===fields.id&&i.source===fields.source);if(!intent)reject('PROFILE_ENTRY_INTENT_UNKNOWN',String(fields.id),'entry must originate in an authored public intent');
  if(seen.has(intent.id))reject('PROFILE_ENTRY_OWNER_CONFLICT',intent.id,'one selected public entry owner required');seen.add(intent.id);
  if(typeof fields.route!=='string'||!/^\/[A-Za-z0-9/_-]*$/.test(fields.route)||(fields.method??'POST')!=='POST')reject('PROFILE_ENTRY_ROUTE',intent.id,'supported POST route required');
  if(routes.has(fields.route))reject('PROFILE_ENTRY_ROUTE_CONFLICT',fields.route,'one public intent per route required');routes.add(fields.route);
  const technical=fields.technical;if(!technical||typeof technical!=='object'||Array.isArray(technical))reject('PROFILE_ENTRY_TECHNICAL_REQUIRED',intent.id,'locked rule must provide technical convention data');
  const allowed=['request_bytes','timeout_ms','read_timeout_ms','read_max_bytes','read_credentials','success_status','rejection_status'];if(Object.keys(technical).sort().join(',')!==allowed.sort().join(','))reject('PROFILE_TECHNICAL_VOCABULARY',intent.id,'closed technical convention fields required');
  out.push(captureJson({intent_id:intent.id,route:fields.route,method:fields.method??'POST',...technical,origin:{source:selected.package_id+'/profile.json',selector:selected.emission.rule,sha256:selected.package_sha256}}) as Readonly<Record<string,Json>>);
 }
 if(seen.size!==selection.input.project.public_intents.length)reject('PROFILE_PUBLIC_INTENT_UNCOVERED','/public_intents','every required intent needs one generated entry');return Object.freeze(out);
}
function profileOrigin(selected:SelectedEmission):Origin {return {kind:'profile-rule',source:selected.package_id+'/profile.json',selector:selected.emission.rule,sha256:selected.package_sha256};}
/** Profile-owned technical request choices over exact authored application intents. */
export function profileApplicationSelections(selection:ProfileSelection):readonly Readonly<{intent_id:string;route:string;request_bytes:number;timeout_ms:number}>[] {
 assertProfileSelectionCurrent(selection);const input=selection.business_applications;if(!input)return [];
 const out:{intent_id:string;route:string;request_bytes:number;timeout_ms:number}[]=[],seen=new Set<string>(),routes=new Set(profileTechnicalSelections(selection).map(s=>String(s.route)));
 for(const selected of selection.emissions.filter(e=>e.emission.role==='application-operation'&&e.package_id===input.runtime.id)){
  const fields=selected.emission.fields,intent=input.snapshot.project.application_intents.find(i=>i.id===fields.id),model=input.applications.find(a=>a.model.id===intent?.application_id);
  if(!intent||!model||fields.project_ref!==model.model.source||fields.selector!==intent.operation_ref||seen.has(intent.id))reject('PROFILE_APPLICATION_ROLE_UNRESOLVED',String(fields.id),'one exact authored application entry owner required');
  const limits=fields.technical;if(!limits||typeof limits!=='object'||Array.isArray(limits)||Object.keys(limits).sort().join(',')!=='request_bytes,timeout_ms')reject('PROFILE_APPLICATION_LIMITS',intent.id,'closed request limits required');
  const limit=limits as Record<string,Json>;
  if(typeof fields.route!=='string'||!/^\/[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*$/.test(fields.route)||routes.has(fields.route))reject('PROFILE_ENTRY_ROUTE_CONFLICT',String(fields.route),'unique public POST route required');
  if(!Number.isSafeInteger(limit.request_bytes)||Number(limit.request_bytes)<1||Number(limit.request_bytes)>1048576||!Number.isSafeInteger(limit.timeout_ms)||Number(limit.timeout_ms)<1||Number(limit.timeout_ms)>30000)reject('PROFILE_APPLICATION_LIMITS',intent.id,'bounded native request convention required');
  seen.add(intent.id);routes.add(fields.route);out.push(Object.freeze({intent_id:intent.id,route:fields.route,request_bytes:Number(limit.request_bytes),timeout_ms:Number(limit.timeout_ms)}));
 }
 if(out.length!==input.snapshot.project.application_intents.length)reject('PROFILE_APPLICATION_UNCOVERED','/application_intents','every authored intent requires one checked profile choice');return Object.freeze(out);
}
export function composeProfile(selection:ProfileSelection,functions:readonly CompiledFunctionContribution[],applications:readonly CheckedApplicationCallable[]=[]):CheckedComposition {
 const snapshot=assertProfileSelectionCurrent(selection);profileTechnicalSelections(selection);
 const functionByIntent=new Map<string,CompiledFunctionContribution>();for(const fn of functions){if(functionByIntent.has(fn.intent_id))reject('PROFILE_FUNCTION_CONFLICT',fn.intent_id,'one compiled callable contribution required');fn.assert_current();assertCompiledProjectSnapshot(fn.graph);
  const source=fn.graph.compositions?.[0]?.source as any;if(!source?.source_text||typeof source.source_text!=='string'||!source.source_text.replace(/^profile declarative-function-v1\n/m,'').startsWith(selection.input.sources[fn.source]??'__missing_business_source__'))reject('PROFILE_COMPILED_SOURCE_MISMATCH',fn.intent_id,'registered graph must retain exact authored source prefix');
  const expected=planCompiledProjectBuild(fn.graph,'typescript','domainspec.typescript-exact-uint64/v1','domainspec.application-layout/v1');for(const artifact of expected.artifacts)if(fn.artifacts[artifact.relative_path]!==artifact.content)reject('PROFILE_SEMANTIC_ARTIFACT_MISMATCH',artifact.relative_path,'compiled business artifact cannot be replaced by native feature glue');
  functionByIntent.set(fn.intent_id,fn);}
 const components:Component[]=[],artifacts:OwnedArtifact[]=[];const componentByRole=new Map<string,string>();
 const componentId=(role:string,id:string)=>role.replaceAll('-','_')+'_'+id;
 const selectedFunctions=selection.emissions.filter(e=>e.emission.role==='domain-function');
 for(const selected of selectedFunctions){const fields=selected.emission.fields,intent=selection.input.project.public_intents.find(i=>i.id===fields.id&&i.source===fields.source),fn=functionByIntent.get(String(fields.id));
  if(!intent||!fn||fn.source!==intent.source)reject('PROFILE_CALLABLE_UNRESOLVED',String(fields.id),'domain function must bind a registered graph and exact business source');
  const prefix=normalizedPath(String(fields.output_prefix)),id=componentId('domain-function',intent.id),origin:Origin={kind:'business',source:intent.source,selector:'public-intent:'+intent.id,sha256:snapshot.sources[intent.source]!.sha256};
  const owned=Object.entries(fn.artifacts).map(([p,content])=>Object.freeze({path:normalizedPath(prefix+'/'+p),content,owner:id,origins:Object.freeze([origin,profileOrigin(selected)])}));artifacts.push(...owned);
  components.push({id,role:'domain-function',owner:selected.package_id,artifact_paths:owned.map(a=>a.path),depends_on:[],origins:[origin,profileOrigin(selected)],contract_ref:'declarative-function-v1#invoke'});componentByRole.set('domain-function:'+intent.id,id);
 }
 if(selectedFunctions.length!==selection.input.project.public_intents.length||functionByIntent.size!==selectedFunctions.length)reject('PROFILE_DOMAIN_UNCOVERED','/functions','compiled domain contributions must match all required intents');
 const entryIds:string[]=[],sharedIds:string[]=[];
 const calls=selection.input.project.application_calls??[],business=selection.business_applications,choices=profileApplicationSelections(selection),newCalls=business?.snapshot.project.application_intents??[];
 if(applications.length!==calls.length+newCalls.length)reject('PROFILE_APPLICATION_UNCOVERED','/','every authored application call requires a registered contribution');
 const applicationIds=new Set<string>();for(const application of applications){assertApplicationCallableCurrent(application);
  if(applicationIds.has(application.intent.id))reject('PROFILE_APPLICATION_CONFLICT',application.intent.id,'one exact application contribution required');applicationIds.add(application.intent.id);
  if(application.kind==='legacy-whole'){const call=calls.find(c=>c.id===application.intent.id);if(!call||dataDigest(call)!==dataDigest(application.intent))reject('PROFILE_APPLICATION_CONFLICT',application.intent.id,'exact legacy authored contribution required');}
  else{const call=newCalls.find(c=>c.id===application.intent.id),model=business?.applications.find(a=>a.model.id===call?.application_id);if(!call||!model||dataDigest(call)!==dataDigest(application.authored_intent)||application.intent.source!==model.model.source||application.lineage.original_source_sha256!==model.source_sha256||application.lineage.original_semantics_sha256!==model.semantics_sha256)reject('PROFILE_APPLICATION_CONFLICT',application.intent.id,'exact captured original business/semantic lineage required');}
 }
 const appEmissions=selection.emissions.filter(e=>e.emission.role==='application-operation');if(appEmissions.length!==calls.length+newCalls.length)reject('PROFILE_APPLICATION_ROLE_UNCOVERED','/','locked profiles must own every authored application role');
 for(const selected of appEmissions){const fields=selected.emission.fields,application=applications.find(a=>a.intent.id===fields.id);if(!application)reject('PROFILE_APPLICATION_ROLE_UNRESOLVED',String(fields.id),'registered callable required');
  const call=application.kind==='legacy-whole'?calls.find(c=>c.id===fields.id&&c.source===fields.project_ref&&c.operation_ref===fields.selector):newCalls.find(c=>c.id===fields.id&&application.intent.source===fields.project_ref&&c.operation_ref===fields.selector&&selected.package_id===business?.runtime.id);
  if(!call)reject('PROFILE_APPLICATION_ROLE_UNRESOLVED',String(fields.id),'role must bind exact authored Operation/Mapping');
  if(typeof fields.route!=='string'||!/^\/[A-Za-z0-9/_-]*$/.test(fields.route)||selection.emissions.some(e=>e.emission.role==='http-entry'&&e.emission.fields.route===fields.route)||appEmissions.some(e=>e!==selected&&e.emission.fields.route===fields.route))reject('PROFILE_ENTRY_ROUTE_CONFLICT',String(fields.route),'unique supported public route required');
  const limits=fields.technical;if(!limits||typeof limits!=='object'||Array.isArray(limits)||Object.keys(limits).sort().join(',')!=='request_bytes,timeout_ms')reject('PROFILE_APPLICATION_LIMITS',call.id,'explicit closed technical request limits required');
  const id=componentId('application-operation',call.id),prefix='applications/'+call.id+'/',origin:Origin={kind:'business',source:application.intent.source,selector:application.intent.operation_ref,sha256:application.source_sha256};
  const owned=application.artifact_plan.artifacts.map(a=>Object.freeze({path:normalizedPath(prefix+a.relative_path),content:a.content,owner:id,origins:Object.freeze([origin,profileOrigin(selected)])}));artifacts.push(...owned);
  const entry=normalizedPath(String(fields.artifact_path??'entries/'+call.id+'.mjs')),runtime=application.kind==='request-application'?business!.runtime.data.application_runtime:undefined;
  const native=runtime?[prefix+'src/empty-settlement.ts',...(runtime.transport==='entry-local'?[prefix+'src/application-http.mts']:[])]:[];
  const shared=runtime?.transport==='shared'?selection.emissions.filter(e=>e.emission.role==='shared-http-port'&&e.package_id===selected.package_id):[];
  if(runtime?.transport==='shared'&&(shared.length!==1||dataDigest(shared[0]!.emission.fields.technical)!==dataDigest({kind:'application-operation'})))reject('PROFILE_APPLICATION_SHARED_PORT_REQUIRED',call.id,'one actual typed shared Operation transport required');
  if(runtime?.transport==='entry-local'&&selection.emissions.some(e=>e.emission.role==='shared-http-port'&&e.package_id===selected.package_id))reject('PROFILE_APPLICATION_TRANSPORT_CONFLICT',call.id,'local transport cannot also own a shared port');
  components.push({id,role:'application-operation',owner:selected.package_id,artifact_paths:[...owned.map(a=>a.path),prefix+'src/profile-entry.ts',...native,entry],depends_on:shared.map(e=>componentId('shared-http-port',String(e.emission.fields.id))),origins:[origin,profileOrigin(selected)],contract_ref:runtime?PROFILE_ROLE_CONTRACTS_V2['application-operation'].descriptor_ref:'typescript.bound-operation/v1'});entryIds.push(id);
 }
 for(const selected of selection.emissions.filter(e=>e.emission.role==='shared-http-port')){
  const f=selected.emission.fields,id=componentId('shared-http-port',String(f.id)),file=normalizedPath(String(f.artifact_path)),operation=selected.package_id===business?.runtime.id;
  if(operation&&!/^runtime\/[A-Za-z0-9_-]+\.mts$/.test(file))reject('PROFILE_APPLICATION_TRANSPORT_PATH',file,'typed shared transport must own a runtime module');
  components.push({id,role:'shared-http-port',owner:selected.package_id,artifact_paths:[file],depends_on:[],origins:[profileOrigin(selected)],contract_ref:operation?PROFILE_ROLE_CONTRACTS_V2['shared-http-port'].descriptor_ref:PROFILE_ROLE_CONTRACTS['shared-http-port'].descriptor_ref});if(!operation)sharedIds.push(id);
 }
 for(const selected of selection.emissions.filter(e=>e.emission.role==='http-entry')){
  const f=selected.emission.fields,intent=selection.input.project.public_intents.find(i=>i.id===f.id&&i.source===f.source)!;const dependency=componentByRole.get('domain-function:'+intent.id);if(!dependency)reject('PROFILE_ENTRY_CALLABLE_MISSING',intent.id,'entry callable absent');
  const id=componentId('http-entry',intent.id),path=normalizedPath(String(f.artifact_path??'entries/'+intent.id+'.mjs')),origin:Origin={kind:'business',source:intent.source,selector:'public-intent:'+intent.id,sha256:snapshot.sources[intent.source]!.sha256};
  components.push({id,role:'http-entry',owner:selected.package_id,artifact_paths:[path],depends_on:[dependency,...sharedIds],origins:[origin,profileOrigin(selected)],contract_ref:PROFILE_ROLE_CONTRACTS['http-entry'].descriptor_ref});entryIds.push(id);
 }
 const dispatch=selection.emissions.filter(e=>e.emission.role==='http-dispatch');if(dispatch.length!==1)reject('PROFILE_DISPATCH_CARDINALITY','/','one service dispatcher required');
 for(const selected of dispatch){const f=selected.emission.fields;components.push({id:componentId('http-dispatch',String(f.id)),role:'http-dispatch',owner:selected.package_id,artifact_paths:[normalizedPath(String(f.artifact_path))],depends_on:entryIds,origins:[profileOrigin(selected)],contract_ref:'service-v1#handler'});}
 const operational=selection.emissions.filter(e=>e.emission.role==='operational-expectation');projectOperationalExpectations(operational.map(e=>e.emission.fields.declaration),{source_sha256:snapshot.lock.source_sha256,lock_sha256:snapshot.lock.lock_sha256});
 for(const selected of operational)components.push({id:componentId('operational-expectation',String(selected.emission.fields.id)),role:'operational-expectation',owner:selected.package_id,artifact_paths:['evidence/operational/'+String(selected.emission.fields.id)+'.json'],depends_on:[],origins:[profileOrigin(selected)],contract_ref:PROFILE_ROLE_CONTRACTS['operational-expectation'].descriptor_ref});
 for(const selected of selection.emissions)if(!['domain-function','http-entry','http-dispatch','shared-http-port','application-operation','operational-expectation'].includes(selected.emission.role))reject('PROFILE_ROLE_NOT_IMPLEMENTED',selected.emission.role,'required role needs a registered composition adapter');
 const dataBody={schema_version:'craft.profile-composition/v1' as const,source_sha256:snapshot.lock.source_sha256,lock_sha256:snapshot.lock.lock_sha256,components,authority_effect:'none' as const};
 const data=validateCompositionShape({...dataBody,composition_sha256:dataDigest(dataBody)});
 const result=Object.freeze({data,selection,artifacts:Object.freeze(artifacts),functions:Object.freeze([...functions]),applications:Object.freeze([...applications])});compositions.set(result,{snapshot,fingerprint:dataDigest({data,artifacts})});assertCheckedCompositionCurrent(result);return result;
}
export function assertCheckedCompositionCurrent(value:CheckedComposition):void {
 const state=compositions.get(value);if(!state||dataDigest({data:value.data,artifacts:value.artifacts})!==state.fingerprint)reject('PROFILE_COMPOSITION_UNREGISTERED_OR_CHANGED','/','reconstruct exact checked composition');assertProfileSnapshotCurrent(state.snapshot);assertProfileSelectionCurrent(value.selection);for(const fn of value.functions){fn.assert_current();assertCompiledProjectSnapshot(fn.graph);}for(const app of value.applications)assertApplicationCallableCurrent(app);
}
