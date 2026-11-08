/** C14 per-service emission over an accepted, original generic application.
 * This joins existing Entry bundles; it never invents business behavior or
 * treats a caller's artifact list as source authority.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';
import {mkdtempSync,mkdirSync,readFileSync,readdirSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {pinCorePhysicalCaptures,readCorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {publishAtomicDirectory} from '../generation/atomic-publication.js';
import {requireGenericCompositionRuntime,requireGenericWorkflowRuntime,type GenericCompositionHandle,createGenericCompositionOwner,createGenericBundledApplicationOwner} from './public-sdk.js';
import type {GenericRuntimeOptions,GenericTransactionApplicationRuntime} from './invocation-owner.js';
import {createGenericWorkflowWorker,type GenericWorkflowWorkerOptions} from './workflow-worker.js';
import {createGenericServiceHttpDispatch} from './service-http-dispatch.js';
import {createGenericHttpHandler} from './http-adapter.js';
import {createGenericDemoPayFetchPort} from './service-provider-port.js';

const at={path:'generic-service-artifact-owner',start:0,end:0};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const hex=/^[0-9a-f]{64}$/;
const serviceDir=(id:string)=>'services/'+sha(id);
const entryDir=(id:string)=>'entries/'+sha(id);
type SDK=ReturnType<typeof createGenericCompositionOwner>;
type FileRow=Readonly<{path:string;sha256:string;bytes:number}>;
type HttpRoute=Readonly<{id:string;method:'GET'|'POST';path:string}>;
type EntryRow=Readonly<{entry:string;service:string;directory:string;interaction:'request-response'|'event';application_export:'createGeneratedApplicationOwner';http_export:'createGeneratedHttpHandler'|null;http_routes:readonly HttpRoute[];http_module_sha256:string|null;manifest_sha256:string;artifact_sha256:string}>;
type ServiceRow=Readonly<{service:string;module:string;directory:string;entries:readonly EntryRow[];all_entries_covered:boolean;service_export:'createGeneratedServiceOwners';http_export:'createGeneratedServiceHttpHandlers';module_sha256:string;runtime_module_sha256:string;worker_module_sha256:string|null;wiring_sha256:string;system_graph_sha256:string;bridge_sha256:string;entities:readonly string[];event_bindings:readonly string[];workflow:string|null}>;
export interface GenericServiceArtifactManifest {
 readonly schema_version:'craft.generic-service-artifacts/v1-candidate';
 readonly application_contract_sha256:string;
 readonly source_capture_sha256:string;
 readonly profile_sha256:string;
 readonly executable_semantics_sha256:string;
 readonly services:readonly ServiceRow[];
 readonly files:readonly FileRow[];
 readonly inventory_sha256:string;
 readonly application_module_sha256:string;
 readonly missing_complete_application_classes:readonly string[];
 readonly complete_application:boolean;
 readonly qualification:'checked-selected-entry-service-artifacts;full-application-pending'|'checked-complete-application-assembly;runtime-environment-required';
 readonly authority_effect:'none';
}
export interface GenericServiceArtifactHandle {readonly kind:'original-generic-service-artifact/v1-candidate'}
export interface GenericServiceBundledApplicationBinding {
 readonly kind:'original-generic-service-bundled-application/v1-candidate';
 readonly entry:string;
 readonly owner:ReturnType<typeof createGenericBundledApplicationOwner>;
}
const genuineServiceArtifactOwners=new WeakSet<object>();

function filesUnder(root:string):{relative_path:string;content:string}[]{
 const result:{relative_path:string;content:string}[]=[];
 const visit=(relative:string)=>{
  const full=path.join(root,relative);
  for(const child of readdirSync(full,{withFileTypes:true})){
   const name=relative?relative+'/'+child.name:child.name;
   if(child.isDirectory())visit(name);
   else if(child.isFile()){
    if(result.length>=1024)fail('ResourceLimit',at,'bounded generated artifact inventory required');
    result.push({relative_path:name,content:readCorePhysicalFile(path.join(root,name)).text});
   }else fail('StaleOwner',at,'generated artifact is not a regular file');
  }
 };
 visit('');return result.sort((a,b)=>a.relative_path.localeCompare(b.relative_path));
}
function pathsUnder(root:string):string[]{
 const result:string[]=[];
 const visit=(relative:string)=>{
  for(const child of readdirSync(path.join(root,relative),{withFileTypes:true})){
   const name=relative?relative+'/'+child.name:child.name;
   if(child.isDirectory())visit(name);
   else if(child.isFile()){
    if(result.length>=1024)fail('ResourceLimit',at,'bounded generated artifact inventory required');
    result.push(name);
   }else fail('StaleOwner',at,'generated artifact is not a regular file');
  }
 };
 visit('');return result.sort();
}
function checkedJson(file:string):any{try{return JSON.parse(readCorePhysicalFile(file).text);}catch{return fail('InvalidContract',at,'generated JSON artifact required');}}
function usedWriteBindingIds(operations:readonly unknown[],service:string):ReadonlySet<string>{
 const ids=new Set<string>();
 const visit=(value:unknown):void=>{
  if(!value||typeof value!=='object')return;
  if(Array.isArray(value)){for(const part of value)visit(part);return;}
  const node=value as Record<string,unknown>;
  if(node.kind==='write-external'){
   const id=(node.call as {binding_ref?:unknown}|undefined)?.binding_ref;
   if(typeof id!=='string')fail('InvalidContract',at,'checked provider step requires binding reference');
   ids.add(id);return;
  }
  for(const part of Object.values(node))visit(part);
 };
 for(const operation of operations){
  if((operation as {service?:unknown}).service===service)visit(operation);
 }
 return ids;
}
function checkedGeneratedEntry(root:string,manifest:any,entry:string,service:string,entityNames:readonly string[],workflow:string|null,
 eventBindings:readonly {id:string;event_selector:string;payload_schema_sha256:string;producer_service:string;target_service:string}[]):void{
 if(!manifest||manifest.entry!==entry||!Array.isArray(manifest.files)||!hex.test(manifest.output_sha256)||
   dataDigest(manifest.files)!==manifest.output_sha256)
  fail('InvalidContract',at,'original generated Entry manifest required');
 const seen=new Set<string>();
 for(const file of manifest.files){
  if(!file||typeof file.path!=='string'||file.path.startsWith('/')||file.path.split('/').some((part:string)=>!part||part==='.'||part==='..')||seen.has(file.path)||!hex.test(file.sha256)||!Number.isSafeInteger(file.bytes))
   fail('InvalidContract',at,'bounded exact generated Entry file list required');
  seen.add(file.path);
  const actual=readCorePhysicalFile(path.join(root,file.path));
  if(actual.file.sha256!==file.sha256||actual.file.bytes!==file.bytes)fail('StaleOwner',at,'generated Entry file differs from original manifest');
 }
 const actualPaths=filesUnder(root).map(file=>file.relative_path),expectedPaths=[...seen,'manifest.json'].sort();
 if(dataDigest(actualPaths)!==dataDigest(expectedPaths))fail('InvalidContract',at,'generated Entry has missing or foreign artifact');
 for(const required of ['application.mjs','entry-http.mjs','storage/schema.json','business-graph.json','system-graph.json','business-system-bridge.json'])
  if(!readFileSync(path.join(root,required),'utf8'))fail('MissingMapping',at,'required generated Entry artifact absent');
 const storage=checkedJson(path.join(root,'storage/schema.json')),
  system=checkedJson(path.join(root,'system-graph.json')),
  bridge=checkedJson(path.join(root,'business-system-bridge.json'));
 if(storage.service!==service||!Array.isArray(storage.tables)||
   dataDigest(storage.tables.map((table:any)=>table.entity).sort())!==dataDigest([...entityNames].sort())||
   !system.nodes?.some((node:any)=>node.id==='generated:'+entry&&node.artifact==='application.mjs')||
   !system.nodes?.some((node:any)=>node.id==='storage:'+service&&node.artifact==='storage/schema.json')||
   !bridge.links?.some((link:any)=>link.business===entry&&link.system==='generated:'+entry))
  fail('InvalidContract',at,'generated service storage, graph or bridge lacks checked Entry lineage');
 if(workflow&&(!seen.has('workflow-plan.json')||checkedJson(path.join(root,'workflow-plan.json')).contract?.workflow!==workflow||
   !system.nodes?.some((node:any)=>node.id==='workflow:'+workflow&&node.artifact==='workflow-plan.json')))
  fail('InvalidContract',at,'checked Workflow lineage absent from generated Entry');
 for(const binding of eventBindings){
  if(!system.nodes?.some((node:any)=>node.id==='event:'+binding.id&&node.selector===binding.event_selector&&node.payload_schema_sha256===binding.payload_schema_sha256)||
    !bridge.links?.some((link:any)=>link.business===binding.event_selector&&link.system==='event:'+binding.id&&link.payload_schema_sha256===binding.payload_schema_sha256)||
    binding.producer_service===service&&!system.nodes?.some((node:any)=>node.id==='outbox:'+binding.id&&node.service===service)||
    binding.target_service===service&&!system.nodes?.some((node:any)=>node.id==='inbox:'+binding.id&&node.service===service))
   fail('InvalidContract',at,'generated Event graph lacks original checked binding lineage');
 }
}

/** The caller may select Entries, but every service and selected Entry is
 * reselected through the original accepted plan owner before generation. */
export function createGenericServiceArtifactOwner(sdk:SDK,sourceHandle:GenericCompositionHandle){
 const binding=requireGenericCompositionRuntime(sdk,sourceHandle);
 if(binding.application.kind!=='original-generic-transaction-application/v1-candidate')fail('UnsupportedCapability',at,'stateful generic application required');
 const {plans,application}=binding,original=plans.inspectSourceApplication(application),contract=original.contract;
 const initialSha=original.contract_sha256,sourceSha=original.source_capture_sha256,profileSha=original.derivation.profile_sha256;
 const workflowCandidate=(sdk.inspect(sourceHandle) as {workflow_contract?:{workflow?:string}}).workflow_contract;
 const workflow=workflowCandidate?.workflow?requireGenericWorkflowRuntime(sdk,sourceHandle).contract:null;
 const workflowEntries=workflow?[...new Set([workflow.start_entry,...workflow.steps.flatMap(step=>[step.entry,...(step.compensation_entry?[step.compensation_entry]:[])])])].sort():[];
 const serviceRows=contract.services.map(service=>{
  const owned=plans.inspectService(plans.bindService(application,service.id));
  return {id:owned.id,module:owned.module,entities:contract.values.records.filter(record=>record.role==='Entity'&&record.name.startsWith(owned.module+'.')).map(record=>record.name).sort()};
 });
 const entryRows=contract.entries.map(entry=>{
  const owned=plans.inspectEntry(plans.bindEntry(application,entry.entry));
  return {id:owned.entry,service:owned.service,interaction:entry.interaction};
 });
 const sourceInspection=sdk.inspect(sourceHandle) as {http_contract?:{profile?:{route_prefix?:string};entries?:readonly {route?:{id?:string;entry?:string;service?:string;method?:string;path?:string}}[]}};
 const httpContract=sourceInspection.http_contract;
 const sourceExecutableSha=(sdk.inspect(sourceHandle) as {expanded:{executable_semantics_sha256:string}}).expanded.executable_semantics_sha256;
 if(!hex.test(sourceExecutableSha))fail('InvalidContract',at,'checked composed executable identity required');
 if(httpContract&&(!httpContract.profile||typeof httpContract.profile.route_prefix!=='string'||!Array.isArray(httpContract.entries)))
  fail('InvalidContract',at,'checked HTTP profile and route selection required');
 const routesByEntry=new Map<string,HttpRoute[]>();
 if(httpContract)for(const candidate of httpContract.entries!){
  const route=candidate.route,declared=entryRows.find(entry=>entry.id===route?.entry);
  if(!route||!declared||declared.service!==route.service||declared.interaction!=='request-response'||
    typeof route.id!=='string'||!route.id||!['GET','POST'].includes(route.method??'')||
    typeof route.path!=='string'||!route.path.startsWith('/')||!/^\/[A-Za-z0-9/_{}-]+$/.test(route.path))
   fail('InvalidContract',at,'HTTP route must select an original request-response Entry');
  const fullPath=httpContract.profile!.route_prefix!+route.path;
  const selected=routesByEntry.get(declared.id)??[];
  selected.push({id:route.id,method:route.method as 'GET'|'POST',path:fullPath});routesByEntry.set(declared.id,selected);
 }
 const current=()=>{
  binding.assertCurrent();const now=plans.inspectSourceApplication(application);
  if(now.contract_sha256!==initialSha||now.source_capture_sha256!==sourceSha||now.derivation.profile_sha256!==profileSha)
   fail('StaleOwner',at,'original application/source/profile changed');
  if(workflow)requireGenericWorkflowRuntime(sdk,sourceHandle).assertCurrent();
 };
 const emitted=new WeakMap<object,{directory:string;manifest:GenericServiceArtifactManifest;files:readonly FileRow[];physical:ReturnType<typeof pinCorePhysicalCaptures>}>();
 const bundled=new WeakMap<object,{artifact:GenericServiceArtifactHandle;entry:string}>();
 const opened=new WeakMap<object,{artifact:GenericServiceArtifactHandle;service:string;binding?:GenericServiceBundledApplicationBinding;handle?:GenericCompositionHandle}>();
 const relays=new WeakMap<object,{artifact:GenericServiceArtifactHandle;service:string}>();
 current();
 const owner=Object.freeze({
  emit(request:{outputDirectory:string;entries:readonly string[];requireCompleteApplication?:boolean}):GenericServiceArtifactHandle{
   current();
   if(!request||typeof request.outputDirectory!=='string'||!path.isAbsolute(request.outputDirectory)||path.normalize(request.outputDirectory)!==request.outputDirectory||
     !Array.isArray(request.entries)||request.entries.length<serviceRows.length||request.entries.length>128||
     new Set(request.entries).size!==request.entries.length||request.entries.some(id=>typeof id!=='string'))
    fail('InvalidContract',at,'normalized output and bounded distinct checked Entry selection required');
   const selected=request.entries.map(id=>{const found=entryRows.find(entry=>entry.id===id);if(!found)fail('UnknownReference',at,'selected Entry absent from original application');plans.assertChild(plans.bindEntry(application,id),application);return found;});
   if(serviceRows.some(service=>!selected.some(entry=>entry.service===service.id)))fail('MissingMapping',at,'every checked service needs a generated Entry artifact');
   const omitted=entryRows.filter(entry=>!selected.some(s=>s.id===entry.id)).map(entry=>entry.id);
   const unsupportedWrites='write_bindings'in contract?contract.write_bindings.filter(binding=>binding.protocol_id!=='DemoPay-v1'):[];
   const uncoveredEvents='event_bindings'in contract?contract.event_bindings.filter(binding=>
    !serviceRows.some(row=>row.id===binding.producer_service)||!serviceRows.some(row=>row.id===binding.target_service)||
    !selected.some(entry=>entry.id===binding.target_entry&&entry.service===binding.target_service)):[];
   const hasEvents='event_bindings'in contract&&contract.event_bindings.length>0;
   const hasWrites='write_bindings'in contract&&contract.write_bindings.length>0;
   const complete=omitted.length===0&&unsupportedWrites.length===0&&uncoveredEvents.length===0&&
    !workflow&&!hasEvents&&!hasWrites;
   const missing=complete?[]:[...omitted.map(id=>'entry:'+id),...unsupportedWrites.map(binding=>'provider-protocol:'+binding.id),
    ...uncoveredEvents.map(binding=>'event-target:'+binding.id),
    ...(omitted.length?['service-repository-runtime-verification','api-transport-adapter']:[]),
    ...(workflow?['workflow-worker-runtime-verification']:[]),...(hasEvents?['event-relay-adapter']:[]),...(hasWrites?['provider-write-adapter']:[])];
   if(request.requireCompleteApplication&&!complete)fail('MissingMapping',at,'complete application requires every original Entry and executable service adapters');
   const stage=mkdtempSync(path.join(tmpdir(),'craft-service-emission-'));
   try{
    const services:ServiceRow[]=[],extra:{relative_path:string;content:string}[]=[],serviceViews:{service:string;system:any;bridge:any}[]=[];
    for(const service of serviceRows){
     const directory=serviceDir(service.id),entries:EntryRow[]=[];
     for(const choice of selected.filter(entry=>entry.service===service.id).sort((a,b)=>a.id.localeCompare(b.id))){
      current();const relative=directory+'/'+entryDir(choice.id),destination=path.join(stage,relative);
      mkdirSync(path.dirname(destination),{recursive:true});
      const generated=sdk.generate(sourceHandle,{entry:choice.id,outputDirectory:destination}) as any;
      const eventBindings='event_bindings'in contract?contract.event_bindings.filter(binding=>binding.producer_service===service.id||binding.target_service===service.id):[];
      checkedGeneratedEntry(destination,generated,choice.id,service.id,service.entities,workflow?.workflow??null,eventBindings);
      const actual=checkedJson(path.join(destination,'manifest.json'));
      if(dataDigest(actual)!==dataDigest(generated))fail('InvalidContract',at,'emitted Entry manifest differs from original generator result');
      const httpFile=generated.files.find((file:any)=>file.path==='entry-http.mjs');
      if(!httpFile||!hex.test(httpFile.sha256))fail('InvalidContract',at,'original generated HTTP artifact digest required');
      const routes=routesByEntry.get(choice.id)??[];
      const checkedHttp=generated.runtime_contract?.http;
      if(httpContract){
       if(!Array.isArray(checkedHttp?.routes)||dataDigest(routes.map(route=>route.id).sort())!==dataDigest(checkedHttp.routes.filter((route:any)=>route.entry===choice.id).map((route:any)=>route.id).sort()))
        fail('InvalidContract',at,'generated HTTP routes differ from accepted profile selection');
      }else if(choice.interaction==='request-response'&&(checkedHttp?.method!=='POST'||typeof checkedHttp.route!=='string'))
       fail('InvalidContract',at,'generated legacy HTTP Entry route required');
      const exposed=choice.interaction==='request-response'&&(!httpContract||routes.length>0);
      entries.push({entry:choice.id,service:service.id,directory:relative,interaction:choice.interaction,application_export:'createGeneratedApplicationOwner',http_export:exposed?'createGeneratedHttpHandler':null,http_routes:routes,http_module_sha256:exposed?httpFile.sha256:null,manifest_sha256:sha(readFileSync(path.join(destination,'manifest.json'),'utf8')),artifact_sha256:generated.output_sha256});
     }
     const imports=entries.flatMap((entry,index)=>[
      `import {createGeneratedApplicationOwner as entry${index}} from './${entryDir(entry.entry)}/application.mjs';`,
      // Existing per-Entry bundles include entry-http.mjs for Event receivers.
      // Do not expose that legacy direct-import artifact as a service HTTP route.
      ...(!httpContract&&entry.http_export?[`import {createGeneratedHttpHandler as http${index}} from './${entryDir(entry.entry)}/entry-http.mjs';`]:[]),
     ]).join('\n');
     const members=entries.map((entry,index)=>`${JSON.stringify(entry.entry)}:entry${index}`).join(',');
     const handlers=entries.flatMap((entry,index)=>entry.http_export&&!httpContract?[`${JSON.stringify(entry.entry)}:http${index}(runtime)`]:[]).join(',');
     const module=`${imports}\nexport const serviceId=${JSON.stringify(service.id)};\nexport const entryIds=Object.freeze(${JSON.stringify(entries.map(entry=>entry.entry))});\nexport function createGeneratedServiceOwners(){return Object.freeze({${members}});}\nexport function createGeneratedServiceHttpHandlers(runtime${httpContract?',owner,artifact':''}){${httpContract?`if(!owner||typeof owner.openServiceHttpDispatch!=='function')throw Error('GENERATED_SERVICE_HTTP_OWNER');return owner.openServiceHttpDispatch(artifact,serviceId,runtime);`:`return Object.freeze({${handlers}});`}}\n`;
     const events='event_bindings'in contract?contract.event_bindings.filter(binding=>binding.producer_service===service.id||binding.target_service===service.id).map(binding=>({id:binding.id,contract_sha256:dataDigest(binding),role:binding.producer_service===service.id&&binding.target_service===service.id?'both':binding.producer_service===service.id?'producer':'receiver',producer_service:binding.producer_service,target_service:binding.target_service,target_entry:binding.target_entry,payload_schema_sha256:binding.payload_schema_sha256})).sort((a,b)=>a.id.localeCompare(b.id)):[];
     const usedWrites='write_bindings'in contract?usedWriteBindingIds(contract.stateful_operations,service.id):new Set<string>();
     const writes='write_bindings'in contract?contract.write_bindings.filter(binding=>usedWrites.has(binding.id)).map(binding=>({id:binding.id,contract_sha256:dataDigest(binding),interface_ref:binding.interface_ref,protocol_id:binding.protocol_id,native_family_ref:binding.native_family_ref})).sort((a,b)=>a.id.localeCompare(b.id)):[];
     if(usedWrites.size!==writes.length)fail('InvalidContract',at,'checked service provider step lacks selected binding');
     const selectedWorkflow=workflow?.service===service.id?{id:workflow.workflow,contract_sha256:dataDigest(workflow),source_capture_sha256:workflow.source_capture_sha256,profile_sha256:workflow.profile_sha256,start_entry:workflow.start_entry}:null;
     const wiring=coreFreeze({schema_version:'craft.generic-service-wiring/v1-candidate',service:service.id,application_contract_sha256:initialSha,source_capture_sha256:sourceSha,profile_sha256:profileSha,selected_entries:entries.map(entry=>entry.entry),worker:selectedWorkflow?{...selectedWorkflow,owner:'original-generic-workflow-worker',binding:'original-source-and-journal-required',module:'worker.mjs',required_entries:workflowEntries,required_entries_covered:workflowEntries.every(id=>selected.some(entry=>entry.id===id)),runtime_verified:false}:null,event_relay:{bindings:events,producer_binding:'original-runtime-openEventRelay',receiver_binding:'original-generic-event-receiver-runtime',relay_delivery_adapter:false},provider_adapter:{bindings:writes,port:'caller-supplied-raw-http-port',native_binding:'original-runtime-openRuntime',provider_port_implementation:false},qualification:complete?'checked-pure-service-adapters;runtime-environment-required':'checked-wiring-descriptors;runtime-integration-pending',authority_effect:'none'});
     const runtimeModule=`export const serviceId=${JSON.stringify(service.id)};\nexport const sourceContractSha256=${JSON.stringify(initialSha)};\nexport const sourceCaptureSha256=${JSON.stringify(sourceSha)};\nexport const executableSemanticsSha256=${JSON.stringify(sourceExecutableSha)};\nconst opened=new WeakSet();\nexport async function openGeneratedServiceRuntime(sdk,acceptedSource,options){if(!sdk||typeof sdk.inspect!=='function'||typeof sdk.openRuntime!=='function'||!options||typeof options!=='object'||Array.isArray(options)||Object.hasOwn(options,'service'))throw Error('GENERATED_SERVICE_RUNTIME_INPUT');const inspection=sdk.inspect(acceptedSource);if(inspection?.expanded?.capture_sha256!==sourceCaptureSha256||inspection?.expanded?.executable_semantics_sha256!==executableSemanticsSha256)throw Error('GENERATED_SERVICE_SOURCE_MISMATCH');const runtime=await sdk.openRuntime(acceptedSource,{...options,service:serviceId});opened.add(runtime);return runtime;}\n${events.some(event=>event.role!=='receiver')?"export function openGeneratedServiceRelay(runtime){if(!opened.has(runtime))throw Error('GENERATED_SERVICE_RUNTIME_OWNER');return runtime.openEventRelay();}\n":''}`;
     const workerModule=selectedWorkflow?`export const serviceId=${JSON.stringify(service.id)};\nexport const workflowId=${JSON.stringify(selectedWorkflow.id)};\nexport const workflowContractSha256=${JSON.stringify(selectedWorkflow.contract_sha256)};\nexport const requiredEntryIds=Object.freeze(${JSON.stringify(workflowEntries)});\nexport function createGeneratedServiceWorkflowWorker(owner,artifact,options){if(!owner||typeof owner.inspect!=='function'||typeof owner.createServiceWorkflowWorker!=='function')throw Error('GENERATED_WORKFLOW_OWNER');const manifest=owner.inspect(artifact);if(manifest?.application_contract_sha256!==${JSON.stringify(initialSha)}||manifest?.source_capture_sha256!==${JSON.stringify(sourceSha)}||!manifest.services?.some(row=>row.service===serviceId&&row.workflow===workflowId))throw Error('GENERATED_WORKFLOW_SOURCE_MISMATCH');const selected=new Set(manifest.services.flatMap(row=>row.entries.map(entry=>entry.entry)));if(requiredEntryIds.some(id=>!selected.has(id)))throw Error('GENERATED_WORKFLOW_ENTRY_MISSING');return owner.createServiceWorkflowWorker(artifact,serviceId,options);}\n`:null;
     const artifactRuntimeModule=runtimeModule+`\nexport const selectedProfileSha256=${JSON.stringify(profileSha)};\nfunction checkedServiceArtifact(owner,artifact){if(!owner||typeof owner.inspect!=='function'||typeof owner.openServiceRuntime!=='function')throw Error('GENERATED_SERVICE_ARTIFACT_OWNER');const manifest=owner.inspect(artifact);if(manifest?.application_contract_sha256!==sourceContractSha256||manifest?.source_capture_sha256!==sourceCaptureSha256||manifest?.profile_sha256!==selectedProfileSha256||manifest?.executable_semantics_sha256!==executableSemanticsSha256||!manifest.services?.some(row=>row.service===serviceId))throw Error('GENERATED_SERVICE_ARTIFACT_MISMATCH');return manifest;}\nexport async function openGeneratedServiceArtifactRuntime(owner,artifact,options,binding,generatedHandle){checkedServiceArtifact(owner,artifact);return owner.openServiceRuntime(artifact,serviceId,options,binding,generatedHandle);}\n${events.some(event=>event.role!=='receiver')?"export function openGeneratedServiceArtifactRelay(owner,artifact,runtime){checkedServiceArtifact(owner,artifact);if(typeof owner.openServiceRelay!=='function')throw Error('GENERATED_SERVICE_ARTIFACT_OWNER');return owner.openServiceRelay(artifact,serviceId,runtime);}\n":''}`;
     const referencedEntries=workerModule?workflowEntries.filter(id=>!entries.some(entry=>entry.entry===id)).map(id=>{
      const declared=entryRows.find(entry=>entry.id===id),emitted=selected.some(entry=>entry.id===id);
      if(!declared)fail('UnknownReference',at,'original Workflow Entry absent from checked application');
      return {id:'entry:'+id,kind:'workflow-required-entry-reference',service:declared.service,emitted,artifact:emitted?serviceDir(declared.service)+'/'+entryDir(id)+'/application.mjs':null};
     }):[];
     const apiEntries=entries.filter(entry=>entry.http_export!==null);
     const apiNodes=apiEntries.flatMap(entry=>entry.http_routes.length?
      entry.http_routes.map(route=>({id:'api:'+route.id,kind:'original-generated-profile-http-handler',artifact:entry.directory+'/entry-http.mjs',sha256:entry.http_module_sha256,entry:entry.entry,route})):
      [{id:'api:'+entry.entry,kind:'original-generated-entry-http-handler',artifact:entry.directory+'/entry-http.mjs',sha256:entry.http_module_sha256,entry:entry.entry}]);
     const runtimeRelations=[{from:'service:'+service.id,to:'runtime:'+service.id,kind:'opens-original-service-runtime'},...entries.flatMap(entry=>[{from:'runtime:'+service.id,to:'entry:'+entry.entry,kind:'binds-original-entry-runtime'},{from:'runtime:'+service.id,to:'storage:'+entry.entry,kind:'opens-original-service-storage'}]),...events.map(binding=>({from:'runtime:'+service.id,to:'event:'+binding.id,kind:binding.role==='receiver'?'accepts-checked-event':binding.role==='both'?'opens-and-accepts-checked-event':'opens-checked-event-relay'})),...writes.map(binding=>({from:'runtime:'+service.id,to:'provider:'+binding.id,kind:'requires-checked-provider-binding'})),...(workerModule?[{from:'runtime:'+service.id,to:'worker:'+selectedWorkflow!.id,kind:'supplies-original-worker-runtime'}]:[]),...apiNodes.flatMap(node=>[{from:'service:'+service.id,to:node.id,kind:'exports-original-http-handler'},{from:'runtime:'+service.id,to:node.id,kind:'supplies-original-runtime-to-http-handler'}])];
     const runtimeBridgeLinks=[{business:service.id,system:'runtime:'+service.id,application_contract_sha256:initialSha},...apiNodes.flatMap(node=>[{business:service.id,system:node.id,entry:node.entry,artifact_sha256:node.sha256},{business:node.entry,system:node.id,artifact_sha256:node.sha256}])];
     const serviceSystem=coreFreeze({schema_version:'craft.generic-service-system-view/v1-candidate',service:service.id,application_contract_sha256:initialSha,nodes:[{id:'service:'+service.id,kind:'generated-service-export',artifact:directory+'/service.mjs',sha256:sha(module)},{id:'runtime:'+service.id,kind:'original-sdk-delegating-service-runtime',artifact:directory+'/runtime.mjs',sha256:sha(artifactRuntimeModule)},...entries.flatMap(entry=>[{id:'entry:'+entry.entry,kind:'original-generated-entry',artifact:entry.directory+'/application.mjs',manifest_sha256:entry.manifest_sha256,interaction:entry.interaction},{id:'storage:'+entry.entry,kind:'original-generated-storage',artifact:entry.directory+'/storage/schema.json'}]),...referencedEntries,...apiNodes,...events.map(binding=>({id:'event:'+binding.id,kind:'checked-event-relay-binding',artifact:directory+'/service-wiring.json',contract_sha256:binding.contract_sha256,role:binding.role})),...writes.map(binding=>({id:'provider:'+binding.id,kind:'checked-provider-write-binding',artifact:directory+'/service-wiring.json',contract_sha256:binding.contract_sha256})),...(workerModule?[{id:'worker:'+selectedWorkflow!.id,kind:'original-worker-delegating-module',artifact:directory+'/worker.mjs',sha256:sha(workerModule),contract_sha256:selectedWorkflow!.contract_sha256,required_entries_covered:workflowEntries.every(id=>selected.some(entry=>entry.id===id))}]:[])],edges:[...runtimeRelations,...entries.flatMap(entry=>[{from:'service:'+service.id,to:'entry:'+entry.entry,kind:'exports-checked-entry'},{from:'entry:'+entry.entry,to:'storage:'+entry.entry,kind:'uses-original-generated-storage'}]),...(workerModule?workflowEntries.map(id=>({from:'worker:'+selectedWorkflow!.id,to:'entry:'+id,kind:'requires-original-entry'})):[])],authority_effect:'none'});
     const serviceBridge=coreFreeze({schema_version:'craft.generic-service-business-system-bridge/v1-candidate',service:service.id,application_contract_sha256:initialSha,links:[...runtimeBridgeLinks,...entries.map(entry=>({business:entry.entry,system:'entry:'+entry.entry,manifest_sha256:entry.manifest_sha256})),...referencedEntries.map(entry=>({business:entry.id.slice(6),system:entry.id,emitted:entry.emitted})),...events.map(binding=>({business:binding.id,system:'event:'+binding.id,contract_sha256:binding.contract_sha256})),...writes.map(binding=>({business:binding.id,system:'provider:'+binding.id,contract_sha256:binding.contract_sha256})),...(workerModule?[{business:selectedWorkflow!.id,system:'worker:'+selectedWorkflow!.id,contract_sha256:selectedWorkflow!.contract_sha256}]:[])],authority_effect:'none'});
     const graphIds=new Set(serviceSystem.nodes.map(node=>node.id));
     if(graphIds.size!==serviceSystem.nodes.length||serviceSystem.edges.some(edge=>!graphIds.has(edge.from)||!graphIds.has(edge.to))||serviceBridge.links.some(link=>!graphIds.has(link.system)))fail('InvalidContract',at,'emitted service graph or business bridge has an unbound node');
     serviceViews.push({service:service.id,system:serviceSystem,bridge:serviceBridge});
     const wiringText=JSON.stringify(wiring,null,2)+'\n',systemText=JSON.stringify(serviceSystem,null,2)+'\n',bridgeText=JSON.stringify(serviceBridge,null,2)+'\n';
     extra.push({relative_path:directory+'/service.mjs',content:module},{relative_path:directory+'/runtime.mjs',content:artifactRuntimeModule},{relative_path:directory+'/service-wiring.json',content:wiringText},{relative_path:directory+'/service-system-graph.json',content:systemText},{relative_path:directory+'/service-business-system-bridge.json',content:bridgeText});
     if(workerModule)extra.push({relative_path:directory+'/worker.mjs',content:workerModule});
     services.push({service:service.id,module:service.module,directory,entries,all_entries_covered:!omitted.some(id=>entryRows.find(entry=>entry.id===id)?.service===service.id),service_export:'createGeneratedServiceOwners',http_export:'createGeneratedServiceHttpHandlers',module_sha256:sha(module),runtime_module_sha256:sha(artifactRuntimeModule),worker_module_sha256:workerModule?sha(workerModule):null,wiring_sha256:sha(wiringText),system_graph_sha256:sha(systemText),bridge_sha256:sha(bridgeText),entities:service.entities,event_bindings:events.map(event=>event.id),workflow:selectedWorkflow?.id??null});
    }
    const eventDestinations='event_bindings'in contract?Object.fromEntries(contract.event_bindings.map(binding=>
     [binding.id,{producer:binding.producer_service,receiver:binding.target_service}])):{};
    const workflowReceiver=workflow?workflow.steps.filter(step=>step.kind==='event-await').map(step=>
     'event_bindings'in contract?contract.event_bindings.find(binding=>binding.id===step.event_binding)?.target_service:undefined):[];
    if(workflowReceiver.some(target=>!target)||new Set(workflowReceiver).size>1)
     fail('UnsupportedCapability',at,'generated Workflow needs one checked receiver service');
    const workerReceivers=workflow&&workflowReceiver.length?{[workflow.service]:workflowReceiver[0]}:{};
    const applicationModule=`export const applicationContractSha256=${JSON.stringify(initialSha)};\nexport const sourceCaptureSha256=${JSON.stringify(sourceSha)};\nexport const profileSha256=${JSON.stringify(profileSha)};\nexport const executableSemanticsSha256=${JSON.stringify(sourceExecutableSha)};\nexport const serviceIds=Object.freeze(${JSON.stringify(serviceRows.map(row=>row.id).sort())});\nexport const completeApplication=${complete};\nexport const eventDestinations=Object.freeze(${JSON.stringify(eventDestinations)});\nexport const workerReceivers=Object.freeze(${JSON.stringify(workerReceivers)});\nexport async function openGeneratedApplication(owner,artifact,optionsByService){if(!owner||typeof owner.inspect!=='function'||typeof owner.openServiceRuntime!=='function'||typeof owner.openServiceHttpDispatch!=='function'||typeof owner.openServiceRelay!=='function'||typeof owner.createServiceWorkflowWorker!=='function'||typeof owner.deliverServiceWorkflowEvent!=='function')throw Error('GENERATED_APPLICATION_OWNER');const manifest=owner.inspect(artifact);if(!manifest?.services?.length||!manifest.services.every(row=>row.all_entries_covered)||manifest.application_contract_sha256!==applicationContractSha256||manifest.source_capture_sha256!==sourceCaptureSha256||manifest.profile_sha256!==profileSha256||manifest.executable_semantics_sha256!==executableSemanticsSha256||JSON.stringify(manifest.services.map(row=>row.service).sort())!==JSON.stringify(serviceIds))throw Error('GENERATED_APPLICATION_SOURCE_MISMATCH');if(!optionsByService||typeof optionsByService!=='object'||Array.isArray(optionsByService)||JSON.stringify(Object.keys(optionsByService).sort())!==JSON.stringify(serviceIds))throw Error('GENERATED_APPLICATION_SERVICE_OPTIONS');const runtimes=new Map();let closed=false;const current=()=>{if(closed)throw Error('GENERATED_APPLICATION_CLOSED');const now=owner.inspect(artifact);if(now!==manifest)throw Error('GENERATED_APPLICATION_SOURCE_MISMATCH');};try{for(const service of serviceIds){const options=optionsByService[service];if(!options||typeof options!=='object'||Array.isArray(options)||Object.hasOwn(options,'service'))throw Error('GENERATED_APPLICATION_SERVICE_OPTIONS');runtimes.set(service,await owner.openServiceRuntime(artifact,service,options));}current();}catch(error){for(const runtime of [...runtimes.values()].reverse())try{await runtime.close();}catch{}throw error;}return Object.freeze({serviceIds,runtime(service){current();if(!runtimes.has(service))throw Error('GENERATED_APPLICATION_SERVICE');return runtimes.get(service);},async http(service){current();const runtime=runtimes.get(service);if(!runtime)throw Error('GENERATED_APPLICATION_SERVICE');return owner.openServiceHttpDispatch(artifact,service,runtime);},relay(service){current();const runtime=runtimes.get(service);if(!runtime)throw Error('GENERATED_APPLICATION_SERVICE');return owner.openServiceRelay(artifact,service,runtime);},async deliverWorkflowEvent(bindingId,causalCommandTupleSha256,leaseMs){current();const selected=eventDestinations[bindingId];if(!selected)throw Error('GENERATED_APPLICATION_EVENT');return owner.deliverServiceWorkflowEvent(artifact,bindingId,causalCommandTupleSha256,leaseMs,runtimes.get(selected.producer),runtimes.get(selected.receiver));},worker(service,options){current();const runtime=runtimes.get(service);if(!runtime||!options||typeof options!=='object'||Array.isArray(options)||Object.hasOwn(options,'runtime'))throw Error('GENERATED_APPLICATION_WORKER_OPTIONS');const receiver=workerReceivers[service];if(receiver&&Object.hasOwn(options,'receiver'))throw Error('GENERATED_APPLICATION_WORKER_OPTIONS');return owner.createServiceWorkflowWorker(artifact,service,{...options,runtime,...(receiver?{receiver:runtimes.get(receiver)}:{})});},async close(){if(closed)return;closed=true;const failures=[];for(const runtime of [...runtimes.values()].reverse())try{await runtime.close();}catch(error){failures.push(error);}if(failures.length)throw new AggregateError(failures,'generated application close failed');}});}\n`;
    extra.push({relative_path:'application.mjs',content:applicationModule});
    const applicationSystem=coreFreeze({schema_version:'craft.generic-application-system-view/v1-candidate',application_contract_sha256:initialSha,nodes:[{id:'application',kind:'generated-application-facade',artifact:'application.mjs',sha256:sha(applicationModule)},...serviceViews.flatMap(view=>view.system.nodes.map((node:any)=>({...node,id:view.service+'::'+node.id})))],edges:[...serviceViews.map(view=>({from:'application',to:view.service+'::service:'+view.service,kind:'opens-checked-service'})),...serviceViews.flatMap(view=>view.system.edges.map((edge:any)=>({...edge,from:view.service+'::'+edge.from,to:view.service+'::'+edge.to})))],authority_effect:'none'});
    const applicationBridge=coreFreeze({schema_version:'craft.generic-application-business-system-bridge/v1-candidate',application_contract_sha256:initialSha,links:serviceViews.flatMap(view=>view.bridge.links.map((link:any)=>({...link,system:view.service+'::'+link.system}))),authority_effect:'none'});
    const applicationNodeIds=new Set(applicationSystem.nodes.map(node=>node.id));
    if(applicationNodeIds.size!==applicationSystem.nodes.length||applicationSystem.edges.some(edge=>!applicationNodeIds.has(edge.from)||!applicationNodeIds.has(edge.to))||applicationBridge.links.some(link=>!applicationNodeIds.has(link.system)))
     fail('InvalidContract',at,'composed application graph or bridge has an unbound node');
    extra.push({relative_path:'application-system-graph.json',content:JSON.stringify(applicationSystem,null,2)+'\n'},
     {relative_path:'application-business-system-bridge.json',content:JSON.stringify(applicationBridge,null,2)+'\n'});
    const generated=filesUnder(stage),contents=[...generated,...extra].sort((a,b)=>a.relative_path.localeCompare(b.relative_path)),files=contents.map(file=>({path:file.relative_path,sha256:sha(file.content),bytes:Buffer.byteLength(file.content)}));
    const manifest:GenericServiceArtifactManifest=coreFreeze({schema_version:'craft.generic-service-artifacts/v1-candidate',application_contract_sha256:initialSha,source_capture_sha256:sourceSha,profile_sha256:profileSha,executable_semantics_sha256:sourceExecutableSha,services,files,inventory_sha256:dataDigest(files),application_module_sha256:sha(applicationModule),missing_complete_application_classes:missing,complete_application:complete,qualification:complete?'checked-complete-application-assembly;runtime-environment-required':'checked-selected-entry-service-artifacts;full-application-pending',authority_effect:'none'});
    const inventoryText=JSON.stringify(manifest,null,2)+'\n';
    contents.push({relative_path:'service-inventory.json',content:inventoryText});
    publishAtomicDirectory(request.outputDirectory,contents,'.domainspec-service-',()=>current());
    const pinnedRows=[...files,{path:'service-inventory.json',sha256:sha(inventoryText),bytes:Buffer.byteLength(inventoryText)}];
    const captures=pinnedRows.map(file=>{
     const captured=readCorePhysicalFile(path.join(request.outputDirectory,file.path));
     if(captured.file.sha256!==file.sha256||captured.file.bytes!==file.bytes)
      fail('StaleOwner',at,'emitted service artifact differs from original generated bytes');
     return captured;
    });
    const physical=pinCorePhysicalCaptures(captures);
    const result:GenericServiceArtifactHandle=Object.freeze({kind:'original-generic-service-artifact/v1-candidate'});
    emitted.set(result,{directory:request.outputDirectory,manifest,files,physical});current();return result;
   }finally{rmSync(stage,{recursive:true,force:true});}
  },
  inspect(result:GenericServiceArtifactHandle):GenericServiceArtifactManifest{
   current();const row=result&&typeof result==='object'?emitted.get(result):undefined;
   if(!row)fail('ForeignOwner',at,'original emitted service artifact handle required');
   row.physical.assertCurrent();
   const paths=pathsUnder(row.directory),expected=[...row.files.map(file=>file.path),'service-inventory.json'].sort();
   if(dataDigest(paths)!==dataDigest(expected))fail('StaleOwner',at,'generated service inventory has missing or foreign artifact');
   row.physical.assertCurrent();
   current();return row.manifest;
  },
  bindGeneratedApplication(result:GenericServiceArtifactHandle,entry:string):GenericServiceBundledApplicationBinding{
   const manifest=owner.inspect(result),row=manifest.services.flatMap(service=>service.entries).find(candidate=>candidate.entry===entry);
   if(!row)fail('UnknownReference',at,'checked emitted Entry required for bundled application');
   const state=emitted.get(result)!;
   const modulePath=path.join(state.directory,row.directory,'application.mjs'),text=readCorePhysicalFile(modulePath).text;
   const marker='const bundle=',start=text.indexOf(marker),end=text.indexOf(';\nexport function',start);
   if(start<0||end<0)fail('InvalidContract',at,'original generated Entry bundle declaration required');
   let proposal:unknown;
   try{proposal=JSON.parse(text.slice(start+marker.length,end));}catch{return fail('InvalidContract',at,'original generated Entry bundle JSON required');}
   const generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,proposal);
   const binding:GenericServiceBundledApplicationBinding=Object.freeze({kind:'original-generic-service-bundled-application/v1-candidate',entry,owner:generated});
   bundled.set(binding,{artifact:result,entry});
   owner.inspect(result);
   return binding;
  },
  async openServiceRuntime(result:GenericServiceArtifactHandle,service:string,options:Omit<GenericRuntimeOptions,'service'>&{externalWriteEndpoint?:string},
   binding?:GenericServiceBundledApplicationBinding,generatedHandle?:GenericCompositionHandle):Promise<GenericTransactionApplicationRuntime>{
   const manifest=owner.inspect(result);
   if(!manifest.services.some(row=>row.service===service))fail('UnknownReference',at,'checked emitted service required');
   if(!options||typeof options!=='object'||Object.hasOwn(options,'service'))fail('InvalidContract',at,'service is fixed by emitted artifact');
   const {externalWriteEndpoint,...originalOptions}=options;
   let runtimeOptions:Omit<GenericRuntimeOptions,'service'>=originalOptions;
   if(externalWriteEndpoint!==undefined){
    const used=usedWriteBindingIds('stateful_operations'in contract?contract.stateful_operations:[],service);
    const bindings='write_bindings'in contract?contract.write_bindings.filter(row=>used.has(row.id)):[];
    if(typeof externalWriteEndpoint!=='string'||!used.size||bindings.length!==used.size||
      bindings.some(row=>row.protocol_id!=='DemoPay-v1')||originalOptions.externalWritePort!==undefined)
     fail('UnsupportedCapability',at,'checked DemoPay service and one external HTTP endpoint required');
    runtimeOptions={...originalOptions,externalWritePort:createGenericDemoPayFetchPort(externalWriteEndpoint)};
   }
   if((binding===undefined)!==(generatedHandle===undefined))fail('InvalidContract',at,'bundled owner and handle must be supplied together');
   const captured=binding&&typeof binding==='object'?bundled.get(binding):undefined;
   if(binding&&(!captured||captured.artifact!==result))fail('ForeignOwner',at,'checked emitted Entry bundled owner required');
   if(binding&&generatedHandle){
    const fresh=binding.owner.inspect(generatedHandle);
    if(fresh.logical.executable_semantics_sha256!==manifest.executable_semantics_sha256)
     fail('StaleOwner',at,'generated bundled application differs from accepted source semantics');
   }
   const runtime=await (binding&&generatedHandle?binding.owner.openRuntime(generatedHandle,{...runtimeOptions,service}):sdk.openRuntime(sourceHandle,{...runtimeOptions,service}));
   if(!('prepareCommand'in runtime)){
    await runtime.close();fail('UnsupportedCapability',at,'original transaction runtime required');
   }
   try{owner.inspect(result);}catch(error){await runtime.close();throw error;}
   opened.set(runtime,{artifact:result,service,...(binding&&generatedHandle?{binding,handle:generatedHandle}:{})});
   return runtime;
  },
  openServiceRelay(result:GenericServiceArtifactHandle,service:string,runtime:GenericTransactionApplicationRuntime){
   owner.inspect(result);
   const originalRuntime=runtime&&typeof runtime==='object'?opened.get(runtime):undefined;
   if(!originalRuntime||originalRuntime.artifact!==result||originalRuntime.service!==service)
    fail('ForeignOwner',at,'same original emitted service runtime required');
   if(!('event_bindings'in contract)||!contract.event_bindings.some(binding=>binding.producer_service===service))
    fail('UnsupportedCapability',at,'checked producer Event binding required');
   runtime.assertCurrent();const relay=runtime.openEventRelay();relays.set(relay,{artifact:result,service});return relay;
  },
  async deliverServiceWorkflowEvent(result:GenericServiceArtifactHandle,bindingId:string,causalCommandTupleSha256:string,
   leaseMs:number,producerRuntime:GenericTransactionApplicationRuntime,receiverRuntime:GenericTransactionApplicationRuntime){
   owner.inspect(result);
   const selected='event_bindings'in contract?contract.event_bindings.find(binding=>binding.id===bindingId):undefined;
   if(!selected)fail('UnknownReference',at,'checked workflow Event binding required');
   const producer=producerRuntime&&typeof producerRuntime==='object'?opened.get(producerRuntime):undefined;
   const receiver=receiverRuntime&&typeof receiverRuntime==='object'?opened.get(receiverRuntime):undefined;
   if(!producer||producer.artifact!==result||producer.service!==selected.producer_service||
     !receiver||receiver.artifact!==result||receiver.service!==selected.target_service||
     producer.binding!==receiver.binding||producer.handle!==receiver.handle)
    fail('ForeignOwner',at,'original producer and receiver service runtimes required');
   const relay=owner.openServiceRelay(result,selected.producer_service,producerRuntime);
   try{
    const claim=relay.claimWorkflowEvent(bindingId,causalCommandTupleSha256,leaseMs);
    if(!claim)return null;
    const delivered=await relay.deliver(claim,receiverRuntime);
    if(delivered.kind==='committed')relay.ack(claim,delivered.receipt);
    owner.inspect(result);return delivered;
   }finally{relay.close();}
  },
  async openServiceHttpDispatch(result:GenericServiceArtifactHandle,service:string,runtime:GenericTransactionApplicationRuntime){
   const inventory=owner.inspect(result),selected=inventory.services.find(row=>row.service===service);
   if(!selected)fail('UnknownReference',at,'checked emitted HTTP service required');
   const originalRuntime=runtime&&typeof runtime==='object'?opened.get(runtime):undefined;
   if(!originalRuntime||originalRuntime.artifact!==result||originalRuntime.service!==service)
    fail('ForeignOwner',at,'same original emitted service runtime required for HTTP dispatch');
   const routes=selected.entries.filter(entry=>entry.interaction==='request-response');
   if(!routes.length)fail('UnsupportedCapability',at,'checked service has no request-response HTTP Entry');
   const directory=emitted.get(result)!.directory;
   if(httpContract){
    const handlers=new Map<string,{method:'GET'|'POST';path:string;handler:(request:Request)=>Promise<Response>}>();
    const runtimeBinding=originalRuntime.binding&&originalRuntime.handle?originalRuntime.binding.owner:sdk;
    const runtimeHandle=originalRuntime.handle??sourceHandle;
    for(const entry of routes){
     const manifest=checkedJson(path.join(directory,entry.directory,'manifest.json'));
     const actual=manifest.runtime_contract?.http?.routes;
     const expected=entry.http_routes;
     if(!Array.isArray(actual)||dataDigest(actual.filter((route:any)=>route.entry===entry.entry).map((route:any)=>({id:route.id,method:route.method,path:httpContract.profile!.route_prefix!+route.path})).sort((a:any,b:any)=>a.id.localeCompare(b.id)))!==dataDigest([...expected].sort((a,b)=>a.id.localeCompare(b.id))))
      fail('InvalidContract',at,'generated route selection differs from accepted service profile');
     const httpModule=readCorePhysicalFile(path.join(directory,entry.directory,'entry-http.mjs')).text;
     if(!httpModule.includes('.bindHttp(')||!httpModule.includes('createGeneratedHttpHandler'))
      fail('InvalidContract',at,'original generated HTTP route module required');
     for(const route of expected){
      if(handlers.has(route.id))fail('InvalidContract',at,'duplicate checked HTTP route identity');
      handlers.set(route.id,{...route,handler:createGenericHttpHandler(runtimeBinding,runtimeHandle,runtime,route.id)});
     }
    }
    owner.inspect(result);
    const selectedRoutes=[...handlers.entries()].map(([id,row])=>({id,...row,parts:row.path.split('/')}));
    const matches=(expected:readonly string[],actual:readonly string[])=>expected.length===actual.length&&expected.every((segment,index)=>segment.startsWith('{')&&segment.endsWith('}')?actual[index]!.length>0:segment===actual[index]);
    const errorResponse=(status:number,code:string,allow?:string)=>new Response(JSON.stringify({kind:'adapter-error',code}),{status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store',...(allow?{allow}:{})}});
    const dispatch=async(request:Request):Promise<Response>=>{
     owner.inspect(result);runtime.assertCurrent();
     if(!(request instanceof Request))return errorResponse(400,'invalid-request');
     let pathname:string;try{pathname=new URL(request.url).pathname;}catch{return errorResponse(400,'invalid-request');}
     const candidates=selectedRoutes.filter(row=>matches(row.parts,pathname.split('/')));
     const chosen=candidates.find(row=>row.method===request.method);
     if(chosen)return chosen.handler(request);
     if(candidates.length)return errorResponse(405,'method-not-allowed',[...new Set(candidates.map(row=>row.method))].sort().join(', '));
     return errorResponse(404,'route-not-found');
    };
    return Object.freeze(Object.assign(dispatch,{handlerForRoute:(routeId:string)=>{
     owner.inspect(result);const row=handlers.get(routeId);if(!row)fail('UnknownReference',at,'checked generated HTTP route required');return row.handler;
    }}));
   }
   const bindings=[];
   for(const entry of routes){
    const manifest=checkedJson(path.join(directory,entry.directory,'manifest.json'));
    const modulePath=path.join(directory,entry.directory,'entry-http.mjs');
    const http=await import(pathToFileURL(modulePath).href);
    if(typeof http.createGeneratedHttpHandler!=='function')
     fail('InvalidContract',at,'original generated Entry HTTP handler required');
    bindings.push({entry:entry.entry,manifest,handler:http.createGeneratedHttpHandler(runtime)});
   }
   owner.inspect(result);
   const selectedProfileFileSha256=(sdk.inspect(sourceHandle) as {profile?:{sha256?:string}}).profile?.sha256;
   if(typeof selectedProfileFileSha256!=='string'||!/^([a-f0-9]{64})$/.test(selectedProfileFileSha256))
    fail('InvalidContract',at,'original selected profile file identity required for HTTP dispatch');
   return createGenericServiceHttpDispatch({service,inventory,selectedProfileFileSha256,bindings,inspectCurrent:()=>owner.inspect(result)});
  },
  createServiceWorkflowWorker(result:GenericServiceArtifactHandle,service:string,options:Omit<GenericWorkflowWorkerOptions,'source'>){
   const manifest=owner.inspect(result);
   if(!workflow||workflow.service!==service)fail('UnsupportedCapability',at,'checked service Workflow required');
   const runtime=options?.runtime&&typeof options.runtime==='object'?opened.get(options.runtime):undefined;
   if(!runtime||runtime.artifact!==result||runtime.service!==service)
    fail('ForeignOwner',at,'Workflow runtime must be opened for the emitted owner service');
   const workflowOwner=runtime.binding&&runtime.handle?
    requireGenericWorkflowRuntime(runtime.binding.owner,runtime.handle):requireGenericWorkflowRuntime(sdk,sourceHandle);
   const comparable=(value:typeof workflow)=>{const {source_capture_sha256:_capture,...identity}=value!;return identity;};
   if(workflowOwner.contract.workflow!==workflow.workflow||workflowOwner.contract.service!==workflow.service||
     dataDigest(comparable(workflowOwner.contract))!==dataDigest(comparable(workflow)))
    fail('StaleOwner',at,'generated Workflow differs from checked service owner');
   const selected=new Set(manifest.services.flatMap(row=>row.entries.map(entry=>entry.entry)));
   const required=[workflowOwner.contract.start_entry,...workflowOwner.contract.steps.flatMap(step=>[step.entry,...(step.compensation_entry?[step.compensation_entry]:[])])];
   if(required.some(entry=>!selected.has(entry)))fail('MissingMapping',at,'every original Workflow Entry requires an emitted artifact');
   if(workflowOwner.contract.steps.some(step=>step.kind==='event-await')){
    const receiver=options.receiver&&typeof options.receiver==='object'?opened.get(options.receiver):undefined;
    const targets=workflowOwner.contract.steps.filter(step=>step.kind==='event-await').map(step=>
     workflowOwner.baseApplication.event_bindings.find(binding=>binding.id===step.event_binding)?.target_service);
    if(targets.some(target=>!target)||!receiver||receiver.artifact!==result||!targets.includes(receiver.service)||receiver.binding!==runtime.binding||receiver.handle!==runtime.handle)
     fail('ForeignOwner',at,'original emitted Event receiver runtime required');
   }
   if(options.relay){
    const relay=typeof options.relay==='object'?relays.get(options.relay):undefined;
    if(!relay||relay.artifact!==result||relay.service!==service)
     fail('ForeignOwner',at,'original emitted producer relay required');
   }
   return createGenericWorkflowWorker({...options,source:workflowOwner.contract});
  },
  assertComplete(result:GenericServiceArtifactHandle):void{
   const inspection=owner.inspect(result);
   if(inspection.missing_complete_application_classes.length||!inspection.complete_application)fail('MissingMapping',at,'complete application artifacts are not yet emitted');
  },
 });
 genuineServiceArtifactOwners.add(owner);
 return owner;
}

/** Rejects lookalike objects before another owner trusts a service inventory. */
export function assertGenericServiceArtifactOwner(owner:unknown):asserts owner is ReturnType<typeof createGenericServiceArtifactOwner>{
 if(!owner||typeof owner!=='object'||!genuineServiceArtifactOwners.has(owner))
  fail('ForeignOwner',at,'original generic service artifact owner required');
}
