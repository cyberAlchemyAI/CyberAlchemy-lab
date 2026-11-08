import {closeSync,constants,fstatSync,lstatSync,openSync,readSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest,ProfileRejected,reject,sha256,validateCoverageShape,type CoverageData,type CoverageItem,type Origin} from './contracts.js';
import {validateBusinessAuthoringContract} from './business-authoring-contracts.js';
import {assertBusinessAuthoringApplicationCurrent,type BusinessAuthoringApplication} from './business-authoring-application.js';
import {assessBusinessAuthoringCoverage,assertBusinessAuthoringCoverageComplete,assertBusinessAuthoringCoverageCurrent,prepareBusinessAuthoringCoverage,resolveBusinessAuthoringCoveragePointer,type BusinessAuthoringCoverageReport,type BusinessAuthoringCoverageItem} from './business-authoring-coverage.js';
import type {BusinessLoweringLedger} from './business-authoring-protocol.js';
import {withBusinessAuthoringSnapshotValidation} from './loader-v3.js';

/** Existing business/system/bridge projections with original authoring lineage.
 * These are explanation artifacts of actual owners, not another executable graph.
 * Open questions: source/native/installed qualification; no proof or admission. */
export interface BusinessAuthoringViews {
 readonly kind:'business-authoring-views';readonly application:BusinessAuthoringApplication;readonly reports:readonly BusinessAuthoringCoverageReport[];
 readonly business:Readonly<Record<string,unknown>>;readonly system:Readonly<Record<string,unknown>>;readonly bridge:Readonly<Record<string,unknown>>;
 readonly coverage:CoverageData;readonly ledger:BusinessLoweringLedger;readonly text:Readonly<{business:string;system:string;bridge:string}>;
 readonly files:Readonly<Record<string,string>>;readonly views_sha256:string;readonly authority_effect:'none';
}
const registry=new WeakMap<object,{application:BusinessAuthoringApplication;reports:readonly BusinessAuthoringCoverageReport[];fingerprint:string}>();
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
function fail(code:string,at:string,message:string):never{return reject('BUSINESS_AUTHORING_VIEWS_'+code,at,message);}
const ownPath=fileURLToPath(import.meta.url);
function implementation():string {
 try{
  const ancestry=()=>{let at=path.parse(ownPath).root;const result:string[]=[];for(const part of ['',...ownPath.slice(at.length).split(path.sep).filter(Boolean)]){if(part)at=path.join(at,part);const stat=lstatSync(at,{bigint:true});if(stat.isSymbolicLink())fail('MODULE',ownPath,'implementation symlinks forbidden');result.push(`${stat.dev}:${stat.ino}:${stat.mode}`);}return result;};
  const beforeAncestors=ancestry(),before=lstatSync(ownPath,{bigint:true});if(!before.isFile()||before.size>16777216n)fail('MODULE',ownPath,'bounded regular implementation required');
  const current=(value:BigIntStats)=>value.isFile()&&value.dev===before.dev&&value.ino===before.ino&&value.mode===before.mode&&value.size===before.size&&value.mtimeNs===before.mtimeNs&&value.ctimeNs===before.ctimeNs;
  const fd=openSync(ownPath,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),buffers:Buffer[]=[];let bytes=0;
  try{if(!current(fstatSync(fd,{bigint:true})))fail('MODULE',ownPath,'implementation changed while opening');for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>16777216)fail('MODULE',ownPath,'implementation byte budget exceeded');buffers.push(buffer.subarray(0,count));}if(!current(fstatSync(fd,{bigint:true})))fail('MODULE',ownPath,'implementation changed while reading');}finally{closeSync(fd);}
  if(BigInt(bytes)!==before.size||!current(lstatSync(ownPath,{bigint:true}))||dataDigest(ancestry())!==dataDigest(beforeAncestors))fail('MODULE',ownPath,'implementation path or ancestor changed');
  return dataDigest({ancestors:beforeAncestors,sha256:sha256(Buffer.concat(buffers)),mtime:String(before.mtimeNs),ctime:String(before.ctimeNs)});
 }catch(error){if(error instanceof ProfileRejected)throw error;return fail('MODULE','/','owning view implementation unavailable');}
}
const executingImplementation=implementation();
function assertImplementation():void{if(implementation()!==executingImplementation)fail('MODULE','/','reload current view implementation');}
function primaryOrigin(item:BusinessAuthoringCoverageItem):Origin {
 const business=item.origins.find(origin=>origin.kind==='business'),profile=item.origins.find(origin=>origin.kind==='profile');
 if(business)return {kind:'business',source:business.source,selector:business.selector,sha256:business.sha256};
 if(profile)return {kind:'profile-rule',source:profile.source,selector:profile.selector,sha256:profile.sha256};
 return fail('ORIGIN',item.obligation_id,'one original business or profile origin is required; all mixed origins remain in the authoring ledger');
}
function legacyItem(item:BusinessAuthoringCoverageItem):CoverageItem {
 const kind:CoverageItem['kind']=item.state==='claim-residue'?'formal-claim':item.class==='audience'?'access-policy':item.class==='exposure'||item.class==='public-intent'?'public-intent':['profile-role','recipe-profile','runtime-guarantee'].includes(item.class)?'generated-role':['request-mapping','request-field','request-contract','request-method','request-body','route','request-limits','timeout','transport'].includes(item.class)?'integration-binding':'business-obligation';
 return {id:item.obligation_id,origin:primaryOrigin(item),kind,state:item.state,reason:item.state==='claim-residue'?'Exact authored formal subject retained as unproved residue; acceptance, generation and finite cases do not establish truth.':item.family==='authored'?'Exact original source obligation retained in the generated authoring view and linked to its captured source.':'Required source/profile derivation linked to actual checked semantic/request/system owners and generated target pointers.',artifact_refs:[...new Set(item.targets.map(target=>target.artifact))].sort(compare),evidence_states:item.evidence_states};
}
function fingerprint(value:BusinessAuthoringViews):string{return dataDigest({business:value.business,system:value.system,bridge:value.bridge,coverage:value.coverage,ledger:value.ledger,text:value.text,files:value.files,views_sha256:value.views_sha256});}

export function projectBusinessAuthoringViews(application:BusinessAuthoringApplication,supplied?:readonly BusinessAuthoringCoverageReport[]):BusinessAuthoringViews {
 assertBusinessAuthoringApplicationCurrent(application);
 return withBusinessAuthoringSnapshotValidation(application.authoring_snapshot,()=>projectViews(application,supplied));
}
function projectViews(application:BusinessAuthoringApplication,supplied?:readonly BusinessAuthoringCoverageReport[]):BusinessAuthoringViews {
 assertBusinessAuthoringApplicationCurrent(application);assertImplementation();
 const reports=Object.freeze(supplied?[...supplied]:application.selection.models.map(model=>assessBusinessAuthoringCoverage(prepareBusinessAuthoringCoverage(application.selection,model.model_id),application)));
 if(reports.length!==application.models.length||new Set(reports.map(report=>report.model_id)).size!==reports.length||dataDigest(reports.map(report=>report.model_id).sort(compare))!==dataDigest(application.models.map(model=>model.model_id).sort(compare)))fail('MODELS','/reports','one complete original coverage report for every selected model required');
 for(const report of reports){assertBusinessAuthoringCoverageComplete(report);if(report.application!==application||report.prepared.selection!==application.selection)fail('CORRESPONDENCE',report.model_id,'coverage must retain this exact original application owner');}
 const items=reports.flatMap(report=>report.items),coverage=validateCoverageShape({schema_version:'craft.profile-coverage/v1',source_sha256:application.composition.source_sha256,lock_sha256:application.composition.lock_sha256,items:items.map(legacyItem),authority_effect:'none'});
 const entries=reports.flatMap(report=>report.ledger.entries).sort((a,b)=>compare(a.id,b.id));if(entries.length>10000)fail('BUDGET','/ledger','aggregate closed ledger exceeds 10000 entries');
 const ledger=validateBusinessAuthoringContract('ledger',{schema_version:'craft.business-lowering/v1-candidate',recipe_ref:application.selection.recipe_ref,business_sha256:application.selection.business_sha256,lock_sha256:application.selection.technical.lock_sha256,entries,authority_effect:'none'}) as BusinessLoweringLedger;
 const business=captureJson({schema_version:'craft.profile-business-view/v1',source_sha256:coverage.source_sha256,intents:[],application_intents:application.requests.project_intents,application_models:application.models.flatMap(model=>model.input.applications.map(value=>value.model)),obligations:coverage.items.filter(item=>['business-obligation','public-intent','access-policy','formal-claim'].includes(item.kind)),authoring:{models:application.selection.models.map(model=>({model_id:model.model_id,source:model.source,spec:model.spec})),reviews:application.models.map(model=>({model_id:model.model_id,review:model.input.accepted.review.review,decision_subject:model.input.accepted.subject,definition_closure:model.input.accepted.definition_closure}))},authority_effect:'none'}) as Readonly<Record<string,unknown>>;
 const system=captureJson({schema_version:'craft.profile-system-view/v1',composition_sha256:application.composition.composition_sha256,components:application.composition.components,domain_graphs:[],applications:application.models.flatMap(model=>model.callables.map(callable=>({intent_id:callable.intent.id,operation_module:callable.operation_module,domain_source_manifest_sha256:model.graph.source_manifest.manifest_sha256,domain_nodes:model.graph.nodes.map(node=>({selector:node.selector,kind:node.kind})),domain_relationships:model.graph.relationships,application_graph:model.binding.application_graph,request_application_plan_sha256:model.plan.plan_sha256,lineage:callable.lineage}))),authoring:{recipe_ref:application.selection.recipe_ref,profile_id:application.selection.technical.profile_id,profile_version:application.selection.technical.profile_version,manifest_sha256:application.selection.technical.manifest_sha256,wire:application.selection.technical.wire,transport:application.selection.technical.transport,routes:application.routes},authority_effect:'none'}) as Readonly<Record<string,unknown>>;
 const bridge=captureJson({schema_version:'craft.profile-bridge-view/v1',source_sha256:coverage.source_sha256,lock_sha256:coverage.lock_sha256,links:coverage.items,authoring:{obligations:items,inventory_sha256:reports.map(report=>({model_id:report.model_id,sha256:report.prepared.inventory.inventory_sha256})),ledger},ontology_admitted:false,authority_effect:'none'}) as Readonly<Record<string,unknown>>;
 const technical=application.selection.technical;
 const text=Object.freeze({
  business:'# Business view\n\n'+application.selection.models.map(model=>`## ${model.spec.identity.title}\n\nModel ${model.model_id}; owner ${model.spec.identity.owner}; version ${model.spec.identity.version}.\n\n`+model.spec.requirements.map(requirement=>`${requirement.id}: ${requirement.meaning}\nContext: ${requirement.context}\n${requirement.boundaries.map(boundary=>'Boundary: '+boundary).join('\n')}`).join('\n\n')+'\n\n'+model.spec.capabilities.map(exposure=>`Exposure ${exposure.id}: ${exposure.public_name} invokes ${exposure.operation_ref}; explicit audience ${exposure.audience}.`).join('\n')).join('\n\n')+'\n\nFormal claims remain unproved residue. Recorded acceptance is a decision on meaning, not proof.\n\n## Open Questions\n\nNative checks, finite observations, proof and admission remain separate evidence.\n',
  system:'# System view\n\nProfile '+technical.profile_id+'; recipe '+application.selection.recipe_ref+'.\nWire '+technical.wire.schema_version+'; '+technical.wire.method+' '+technical.wire.body+'; prefix '+technical.wire.route_prefix+'; body limit '+technical.wire.request_bytes+'; timeout '+technical.wire.timeout_ms+'ms; transport '+technical.transport+'.\n\n'+application.composition.components.map(component=>`- ${component.id}: ${component.role}; owner ${component.owner}; depends on ${component.depends_on.join(', ')||'none'}`).join('\n')+'\n\n## Open Questions\n\nGenerated structure is checked by its registered owners; this view adds no native/runtime observation or proof.\n',
  bridge:'# Business-system bridge\n\n'+items.map(item=>`- ${item.obligation_id}: ${item.state}; ${item.origins.map(origin=>origin.kind+':'+origin.source+'#'+origin.selector).join('; ')} -> ${item.targets.map(target=>target.artifact+'#'+target.pointer).join(', ')}`).join('\n')+'\n\n## Open Questions\n\nLinked/generated, accepted meaning, native checks, finite observation, proof and ontology admission remain distinct. Ontology admitted: false.\n',
 });
 const files:Record<string,string>=Object.create(null),put=(file:string,body:string):void=>{if(Object.hasOwn(files,file)&&files[file]!==body)fail('ARTIFACT',file,'one exact generated target owner required');files[file]=body;};
 for(const [file,body] of Object.entries(application.files))put(file,body);for(const report of reports)for(const [file,body] of Object.entries(report.artifact_text))put(file,body);
 for(const [name,data] of [['business',business],['system',system],['bridge',bridge]] as const){put('views/'+name+'.json',JSON.stringify(data,null,2)+'\n');put('views/'+name+'.md',text[name]);}
 put('evidence/coverage.json',JSON.stringify(coverage,null,2)+'\n');put('evidence/business-authoring-ledger.json',JSON.stringify(ledger,null,2)+'\n');put('evidence/composition.json',JSON.stringify(application.composition,null,2)+'\n');
 for(const report of reports){
  put('evidence/authoring-obligations/'+report.model_id+'.json',JSON.stringify(report.prepared.inventory.data,null,2)+'\n');
  for(const entry of report.ledger.entries){if(!Object.hasOwn(files,entry.target.artifact))fail('ARTIFACT',entry.target.artifact,'every lineage target must be emitted');const text=files[entry.target.artifact]!,data=entry.target.artifact.endsWith('.json')?JSON.parse(text):text;resolveBusinessAuthoringCoveragePointer(data,entry.target.pointer);}
 }
 const fileInventory=Object.fromEntries(Object.keys(files).sort(compare).map(file=>[file,{sha256:sha256(files[file]!),bytes:Buffer.byteLength(files[file]!)}])),viewsHash=dataDigest({business,system,bridge,coverage,ledger,text,files:fileInventory});
 put('evidence/business-authoring-manifest.json',JSON.stringify({schema_version:'craft.business-authoring-view-manifest/v1-candidate',source_sha256:coverage.source_sha256,lock_sha256:coverage.lock_sha256,views_sha256:viewsHash,files:fileInventory,authority_effect:'none'},null,2)+'\n');
 const result=Object.freeze({kind:'business-authoring-views' as const,application,reports,business,system,bridge,coverage,ledger,text,files:Object.freeze(files),views_sha256:viewsHash,authority_effect:'none' as const});registry.set(result,{application,reports,fingerprint:fingerprint(result)});assertBusinessAuthoringViewsCurrent(result);return result;
}
export function assertBusinessAuthoringViewsCurrent(value:BusinessAuthoringViews):void {
 const state=value&&typeof value==='object'?registry.get(value):undefined;if(!state)fail('HANDLE','/','original registered authoring views required');
 withBusinessAuthoringSnapshotValidation(state.application.authoring_snapshot,()=>{assertImplementation();assertBusinessAuthoringApplicationCurrent(state.application);for(const report of state.reports)assertBusinessAuthoringCoverageCurrent(report);
  if(value.application!==state.application||value.reports!==state.reports||fingerprint(value)!==state.fingerprint)fail('STALE','/','view data or original coverage/application custody changed');
 });
}
export function renderBusinessAuthoringViews(value:BusinessAuthoringViews):Readonly<Record<string,string>> {assertBusinessAuthoringViewsCurrent(value);return value.files;}

// S01 successor projections of existing graph owners; never executable custody.
import {assertDirectSourceCoverageV2Current,type DirectSourceCoverageV2,type BusinessDirectCoverageImplementationV2} from './business-authoring-coverage.js';
import type {BusinessCheckedCoverageV2,BusinessCheckedViewsV2,BusinessCoverageViewsOwnerV2,GeneratedU0CallableSourceV2,U0SourceArtifactV2} from './business-authoring-stages-v2.js';

interface DirectProjectionDataV2 {
 readonly business:Readonly<Record<string,unknown>>;readonly system:Readonly<Record<string,unknown>>;readonly bridge:Readonly<Record<string,unknown>>;
 readonly files:BusinessCheckedViewsV2['files'];
}
export interface DirectSourceViewsV2 extends DirectProjectionDataV2 {
 readonly kind:'checked-direct-source-views-v2';readonly coverage:DirectSourceCoverageV2;
 readonly views_sha256:string;readonly authority_effect:'none';
}
const directSourceViewsRegistryV2=new WeakMap<object,{coverage:DirectSourceCoverageV2;fingerprint:string}>();
function directProjectionDataV2(source:DirectSourceCoverageV2,production?:Readonly<{coverage:BusinessCheckedCoverageV2;generated:GeneratedU0CallableSourceV2}>):DirectProjectionDataV2 {
 assertImplementation();assertDirectSourceCoverageV2Current(source);
 const checked=source.source,spec=checked.checked.transfer.spec,coverage=production?.coverage,generated=production?.generated,bound=coverage?.bound??null;
 const links=coverage?.owners??source.owners,unresolved=source.inventory.obligations.filter(row=>!links.some(link=>link.obligation_id===row.id)).map(row=>row.id);
 const business=captureJson({schema_version:'craft.profile-business-view/v2-candidate',source_sha256:source.inventory.source_sha256,model:spec.identity,requirements:spec.requirements,entities:spec.entities,rules:spec.rules,operations:spec.operations,logical_entries:spec.entries,source_facts:spec.source_spans,assurance:{definitions:spec.definitions,claims:spec.claims.map(claim=>({claim,evidence:'unproved-residue'}))},executable_sha256:source.inventory.executable_sha256,authority_effect:'none',open_questions:['Optional claims have no proof or native formal-model observation here.']}) as Readonly<Record<string,unknown>>;
 const system=captureJson({schema_version:'craft.profile-system-view/v2-candidate',stage:bound?'native-bound':production?'generated-source':'checked-source-only',selection:coverage?{selection_sha256:coverage.application.input.selection.selection_sha256,capture:coverage.application.input.capture,native_basis_reference:coverage.application.input.selection.native_basis,early_entry_intents:coverage.application.input.early_requests.entries}:null,domain_graphs:[{project_id:checked.graph.project_id,graph_sha256:checked.graph_sha256,source_manifest:checked.graph.source_manifest,nodes:checked.graph.nodes.map(node=>({selector:node.selector,kind:node.kind,typed_closure_sha256:checked.closures.find(closure=>closure.selector===node.selector)!.typed_closure_sha256})),relationships:checked.graph.relationships}],pure_operation:checked.operation,generated_source:generated?{source_sha256:generated.source_sha256,abi:generated.abi,export_name:generated.export_name,files:generated.files.map(file=>({path:file.path,sha256:file.sha256,bytes:Buffer.byteLength(file.content)}))}:null,native:bound?{basis:bound.basis,callable:bound.callable.artifact,handler:bound.handler_artifact,subject:bound.subject}:null,unresolved_native_obligations:unresolved,authority_effect:'none',open_questions:bound?['Native binding is not an installed test, proof, hosting or publication.']:['Native callable, codec, handler and request graph remain pending until actual late binding.']}) as Readonly<Record<string,unknown>>;
 const rows=source.inventory.obligations.map(obligation=>{
  const owners=links.filter(link=>link.obligation_id===obligation.id);if(owners.length>1||owners.length===0&&obligation.owner_required!=='native-realization')fail('DIRECT_OWNER',obligation.id,'one actual semantic owner or explicit native pending required');
  return {obligation_id:obligation.id,kind:obligation.kind,origins:obligation.origins,owner_required:obligation.owner_required,state:owners.length?'checked-owner':'pending-producer',owner:owners[0]??null};
 });
 const bridge=captureJson({schema_version:'craft.profile-bridge-view/v2-candidate',source_sha256:source.inventory.source_sha256,inventory_sha256:source.inventory.inventory_sha256,checked_source_sha256:checked.check_sha256,graph_sha256:checked.graph_sha256,application_plan_sha256:coverage?.application.plan_sha256??null,selection_sha256:coverage?.application.input.selection.selection_sha256??null,capture_sha256:coverage?.application.input.capture.capture_sha256??null,entry_intent_sha256:coverage?.application.input.early_requests.request_sha256??null,generated_source_sha256:generated?.source_sha256??null,realized_sha256:bound?.subject.realized_sha256??null,links:rows,unresolved_native_obligations:unresolved,ontology_admitted:false,authority_effect:'none',open_questions:['Source links, checked behavior, native binding, installed evidence and optional proof remain separate stages.']}) as Readonly<Record<string,unknown>>;
 const files=Object.freeze(([['business-graph','business',business],['system-graph','system',system],['business-system-bridge','bridge',bridge]] as const).map(([kind,name,data])=>{
  const content=JSON.stringify(data,null,2)+'\n',artifact:U0SourceArtifactV2=Object.freeze({path:'views/'+name+'.json',content,sha256:sha256(content)});return Object.freeze({kind,artifact});
 }));
 return Object.freeze({business,system,bridge,files});
}
/** Positive component projection over an original genuine source coverage.
 * This tag cannot satisfy BusinessCheckedViewsV2 or downstream output custody. */
export function projectDirectSourceViewsV2(coverage:DirectSourceCoverageV2):DirectSourceViewsV2 {
 assertDirectSourceCoverageV2Current(coverage);const data=directProjectionDataV2(coverage);
 const value:DirectSourceViewsV2=Object.freeze({kind:'checked-direct-source-views-v2',coverage,...data,views_sha256:dataDigest(data),authority_effect:'none'});
 directSourceViewsRegistryV2.set(value,{coverage,fingerprint:dataDigest({kind:value.kind,coverage:coverage.coverage_sha256,...data,views_sha256:value.views_sha256})});assertDirectSourceViewsV2Current(value);return value;
}
export function assertDirectSourceViewsV2Current(value:DirectSourceViewsV2):void {
 const state=value&&typeof value==='object'?directSourceViewsRegistryV2.get(value):undefined;if(!state)fail('DIRECT_HANDLE','/views','original source-projected view handle required');
 assertImplementation();assertDirectSourceCoverageV2Current(state.coverage);
 if(value.coverage!==state.coverage||dataDigest({kind:value.kind,coverage:value.coverage.coverage_sha256,business:value.business,system:value.system,bridge:value.bridge,files:value.files,views_sha256:value.views_sha256})!==state.fingerprint)fail('DIRECT_STALE','/views','original projected source data changed');
}
/** Join the original production coverage owner once in the public SDK. All JSON
 * files are explanatory projections and cannot be rehydrated into these handles. */
export function createBusinessCoverageViewsOwnerV2(coverageOwner:BusinessDirectCoverageImplementationV2):BusinessCoverageViewsOwnerV2 {
 const original=[coverageOwner.inventory,coverageOwner.check,coverageOwner.assertCurrent,coverageOwner.source,coverageOwner.generated];
 const owned=new WeakMap<object,{coverage:BusinessCheckedCoverageV2;fingerprint:string}>();
 const assertOwner=()=>{assertImplementation();if(original.some((method,i)=>method!==[coverageOwner.inventory,coverageOwner.check,coverageOwner.assertCurrent,coverageOwner.source,coverageOwner.generated][i]))fail('DIRECT_OWNER_STALE','/views','original coverage producer methods required');};
 const fingerprint=(views:BusinessCheckedViewsV2)=>dataDigest({kind:views.kind,coverage:views.coverage.coverage_sha256,files:views.files,views_sha256:views.views_sha256,authority_effect:views.authority_effect});
 const assertCurrent=(views:BusinessCheckedViewsV2):void=>{
  const state=views&&typeof views==='object'?owned.get(views):undefined;if(!state)fail('DIRECT_HANDLE','/views','original production views from this owner required');
  assertOwner();coverageOwner.assertCurrent(state.coverage);
  if(views.coverage!==state.coverage||fingerprint(views)!==state.fingerprint)fail('DIRECT_STALE','/views','original coverage/view custody changed');
 };
 return Object.freeze({inventory(input:Parameters<BusinessDirectCoverageImplementationV2['inventory']>[0]){assertOwner();return coverageOwner.inventory(input);},check(application:Parameters<BusinessDirectCoverageImplementationV2['check']>[0],bound?:Parameters<BusinessDirectCoverageImplementationV2['check']>[1]){assertOwner();return coverageOwner.check(application,bound);},project(coverage:BusinessCheckedCoverageV2):BusinessCheckedViewsV2{
  assertOwner();coverageOwner.assertCurrent(coverage);const source=coverageOwner.source(coverage),generated=coverageOwner.generated(coverage),data=directProjectionDataV2(source,{coverage,generated});
  const views:BusinessCheckedViewsV2=Object.freeze({kind:'checked-business-views-v2',coverage,files:data.files,views_sha256:dataDigest({coverage:coverage.coverage_sha256,files:data.files}),authority_effect:'none'});
  owned.set(views,{coverage,fingerprint:fingerprint(views)});assertCurrent(views);return views;
 },assertCurrent});
}
