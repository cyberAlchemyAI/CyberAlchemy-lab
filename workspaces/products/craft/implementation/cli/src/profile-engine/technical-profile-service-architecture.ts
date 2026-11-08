/** Source-selected grouping of unchanged protected application artifacts.
 * Both realizations delegate business generation/Auth/SQLite to original owners.
 * Open Questions: goals/plans/craft-technical-profiles-2026-10-31/UNIFIED-DESIGN.md.
 */
import {mkdirSync,readFileSync,readdirSync,realpathSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {renderTechnicalProfileCommandClient} from './technical-profile-client.js';
import {captureJson,dataDigest,reject} from './contracts.js';
import {createTechnicalProfileSourceOwner,assertTechnicalProfileSourceOwner,type CheckedTechnicalProfileSource} from './technical-profile-source.js';
import {createGenericServiceArtifactOwner,type GenericServiceArtifactHandle} from '../generic/service-artifact-owner.js';
import {requireGenericCompositionRuntime,requireGenericWorkflowRuntime,type GenericCompositionHandle} from '../generic/public-sdk.js';
import {pinCorePhysicalCaptures,readCorePhysicalFile,pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import type {GenericRuntimeOptions,GenericTransactionApplicationRuntime} from '../generic/invocation-owner.js';

type SDK=Parameters<typeof createGenericServiceArtifactOwner>[0];
type SourceOwner=ReturnType<typeof createTechnicalProfileSourceOwner>;
type Layout='EntryModules'|'ServiceAssembly';
type File={path:string;sha256:string;bytes:number};
const extension=path.extname(fileURLToPath(import.meta.url));
const implementation=pinCoreImplementation(import.meta.url,['technical-profile-source'+extension,'technical-profile-client'+extension,'../generic/service-artifact-owner'+extension]);
export interface TechnicalServiceArchitectureHandle {readonly kind:'original-technical-service-architecture/v1'}
function fail(detail:string):never{return reject('PROFILE_SERVICE_ARCHITECTURE','/',detail);}
// Generated aggregate views can exceed the 1 MiB source-file budget. Keep that
// source limit for every other file, including nested per-Entry artifacts.
const GENERATED_VIEW_BYTES=16*1024*1024,GENERATED_INVENTORY_BYTES=64*1024*1024;
export function captureTechnicalServiceArchitectureArtifacts(root:string):ReturnType<typeof readCorePhysicalFile>[] {
 const files:ReturnType<typeof readCorePhysicalFile>[]=[];
 let bytes=0;
 const walk=(directory:string)=>{for(const entry of readdirSync(directory,{withFileTypes:true})){const full=path.join(directory,entry.name);if(entry.isDirectory())walk(full);else if(entry.isFile()){if(files.length>=4096)fail('bounded generated file inventory required');const relative=path.relative(root,full),maximum=['system-graph.json','business-system-bridge.json'].includes(relative)?GENERATED_VIEW_BYTES:1048576,captured=readCorePhysicalFile(full,maximum);bytes+=captured.file.bytes;if(bytes>GENERATED_INVENTORY_BYTES)fail('bounded generated artifact bytes required');files.push(captured);}else fail('generated artifacts must be regular owned files');}};
 walk(root);return files.sort((a,b)=>a.file.path.localeCompare(b.file.path));
}

export function createTechnicalProfileServiceArchitectureOwner(input:Readonly<{
 sourceOwner:SourceOwner;sourceHandle:CheckedTechnicalProfileSource;sdk:SDK;application:GenericCompositionHandle;workflowIntegration?:'original-application-workflow';
}>){
 assertTechnicalProfileSourceOwner(input.sourceOwner);
 const binding=requireGenericCompositionRuntime(input.sdk,input.application);
 if(binding.application.kind!=='original-generic-transaction-application/v1-candidate')fail('original protected transaction application required');
 const application=binding.plans.inspectSourceApplication(binding.application),entryContracts=application.contract.entries;
 const originalInspection=input.sdk.inspect(input.application) as any;
 const workflowIntegration=input.workflowIntegration===undefined?null:input.workflowIntegration==='original-application-workflow'?requireGenericWorkflowRuntime(input.sdk,input.application):fail('unsupported application Workflow join');workflowIntegration?.assertCurrent();
 const source=input.sourceOwner.inspect(input.sourceHandle) as any;
 if(source.target_consumer!=='craft.generic-service-artifacts/v1-candidate'||!source.topology||Object.keys(source.topology).join(',')!=='layout'||!['EntryModules','ServiceAssembly'].includes(source.topology.layout))fail('checked finite service architecture Mapping required');
 const layout=source.topology.layout as Layout,sourceDigest=dataDigest(source),rows=new WeakMap<object,{
  directory:string;manifest:any;physical:ReturnType<typeof pinCorePhysicalCaptures>;files:File[];entryDirectories:Map<string,string>;
  serviceOwner:ReturnType<typeof createGenericServiceArtifactOwner>|null;serviceHandle:GenericServiceArtifactHandle|null;
 }>();
 const runtimes=new WeakMap<object,{handle:TechnicalServiceArchitectureHandle;service:string}>();
 const sourceCurrent=()=>{implementation.assertCurrent();assertTechnicalProfileSourceOwner(input.sourceOwner);input.sourceOwner.assertCurrent(input.sourceHandle);if(dataDigest(input.sourceOwner.inspect(input.sourceHandle))!==sourceDigest)fail('technical Mapping changed');binding.assertCurrent();};
 const state=(handle:TechnicalServiceArchitectureHandle)=>{sourceCurrent();const row=rows.get(handle);if(!row)fail('original emitted architecture handle required');row.physical.assertCurrent();const actual=captureTechnicalServiceArchitectureArtifacts(row.directory).map(file=>({path:path.relative(row.directory,file.file.path).split(path.sep).join('/'),sha256:file.file.sha256,bytes:file.file.bytes}));if(dataDigest(actual)!==dataDigest(row.files))fail('generated layout inventory changed');if(row.serviceOwner&&row.serviceHandle)row.serviceOwner.inspect(row.serviceHandle);sourceCurrent();return row;};
 sourceCurrent();
 return Object.freeze({
  emit(request:{outputDirectory:string}):TechnicalServiceArchitectureHandle{
   sourceCurrent();const captured=captureJson(request) as unknown as typeof request;
   if(Object.keys(captured).join(',')!=='outputDirectory'||!path.isAbsolute(captured.outputDirectory)||path.normalize(captured.outputDirectory)!==captured.outputDirectory||realpathSync(path.dirname(captured.outputDirectory))!==path.dirname(captured.outputDirectory))fail('exclusive output under a real existing parent required');
   const output=captured.outputDirectory;mkdirSync(output);
   const entryDirectories=new Map<string,string>(),views:{id:string;system:any;bridge:any}[]=[],originalFiles:File[]=[];
   let serviceOwner:ReturnType<typeof createGenericServiceArtifactOwner>|null=null,serviceHandle:GenericServiceArtifactHandle|null=null;
   if(layout==='ServiceAssembly'){
    serviceOwner=createGenericServiceArtifactOwner(input.sdk,input.application);serviceHandle=serviceOwner.emit({outputDirectory:path.join(output,'assembly'),entries:entryContracts.map(entry=>entry.entry),requireCompleteApplication:!workflowIntegration});
    const manifest=serviceOwner.inspect(serviceHandle);
    for(const entry of manifest.services.flatMap(service=>service.entries))entryDirectories.set(entry.entry,path.join('assembly',entry.directory));
    views.push({id:'assembly',system:JSON.parse(readFileSync(path.join(output,'assembly/application-system-graph.json'),'utf8')),bridge:JSON.parse(readFileSync(path.join(output,'assembly/application-business-system-bridge.json'),'utf8'))});
   }else{
    mkdirSync(path.join(output,'entries'));
    for(const entry of entryContracts){const relative='entries/'+dataDigest(entry.entry),directory=path.join(output,relative),generated=input.sdk.generate(input.application,{entry:entry.entry,outputDirectory:directory}) as any;for(const file of generated.files)originalFiles.push({...file,path:relative+'/'+file.path});const manifest=readCorePhysicalFile(path.join(directory,'manifest.json'));if(dataDigest(JSON.parse(manifest.text))!==dataDigest(generated))fail('original Entry manifest changed');originalFiles.push({...manifest.file,path:relative+'/manifest.json'});entryDirectories.set(entry.entry,relative);views.push({id:entry.entry,system:JSON.parse(readFileSync(path.join(directory,'system-graph.json'),'utf8')),bridge:JSON.parse(readFileSync(path.join(directory,'business-system-bridge.json'),'utf8'))});}
   }
   sourceCurrent();
   if(!('application_namespace' in application.contract))fail('original command application namespace required');
   const commandClient=originalInspection.http_contract?renderTechnicalProfileCommandClient({application:application.contract,applicationSha256:application.contract_sha256,http:originalInspection.http_contract}):workflowIntegration?null:fail('original checked HTTP contract required for command client');if(commandClient)writeFileSync(path.join(output,'command-client.mjs'),commandClient.source,{flag:'wx'});
   const profileNode={id:'technical-profile',kind:'source-selected-service-architecture',mapping:source.mapping,source_closure_sha256:source.source_closure_sha256,executable_semantics_sha256:source.executable_semantics_sha256,layout};
   const system={schema_version:'craft.technical-service-system-view/v1',nodes:[profileNode,...views.flatMap(view=>view.system.nodes.map((node:any)=>({...node,id:view.id+'::'+node.id})))],edges:[...views.flatMap(view=>view.system.nodes.filter((node:any)=>node.kind==='generated-application-facade'||node.kind==='node-esm-application').map((node:any)=>({from:'technical-profile',to:view.id+'::'+node.id,kind:'selects-original-generated-assembly'}))),...views.flatMap(view=>view.system.edges.map((edge:any)=>({...edge,from:view.id+'::'+(edge.from??edge.source),to:view.id+'::'+(edge.to??edge.target)})))],authority_effect:'none'};
   const bridge={schema_version:'craft.technical-service-business-system-bridge/v1',links:views.flatMap(view=>view.bridge.links.map((link:any)=>({...link,system:view.id+'::'+link.system,technical_mapping:source.mapping,technical_source_closure_sha256:source.source_closure_sha256}))),authority_effect:'none'};
   if(commandClient){
    const clientNodes:any[]=[{id:'command-client',kind:'generated-command-client',artifact:'command-client.mjs',sha256:readCorePhysicalFile(path.join(output,'command-client.mjs')).file.sha256,identity_store_abi:commandClient.contract.identity_store_abi},{id:'command-identity-resource',kind:'operator-supplied-durable-identity-port',abi:commandClient.contract.identity_store_abi},...commandClient.contract.routes.map(route=>({id:'command-client:'+route.entry,kind:'generated-command-endpoint',entry:route.entry,service:route.service,source:route.source,entry_contract_sha256:route.entry_contract_sha256,input_schema_sha256:route.input_schema_sha256}))];
    system.nodes.push(...clientNodes);system.edges.push({from:'technical-profile',to:'command-client',kind:'generates-protected-command-client'},{from:'command-client',to:'command-identity-resource',kind:'requires-original-durable-allocation-port'},...commandClient.contract.routes.map(route=>({from:'command-client',to:'command-client:'+route.entry,kind:'prepares-explicit-original-entry-command'})));bridge.links.push(...commandClient.contract.routes.map(route=>({business:route.entry,system:'command-client:'+route.entry,source:route.source,technical_mapping:source.mapping,technical_source_closure_sha256:source.source_closure_sha256})));
   }
   const nodeIds=new Set(system.nodes.map((node:any)=>node.id));if(nodeIds.size!==system.nodes.length||system.edges.some((edge:any)=>!nodeIds.has(edge.from)||!nodeIds.has(edge.to))||bridge.links.some((link:any)=>!nodeIds.has(link.system)))fail('original generated views do not form a closed layout graph');
   const manifest={schema_version:'craft.technical-service-architecture/v1',layout,...(workflowIntegration?{workflow_integration:{owner:'createApplicationWorkflow',contract_sha256:dataDigest(workflowIntegration.contract),service_facade_complete_application:false,qualification:'split-service-artifacts;original-application-workflow-supplies-execution'}}:{}),command_client:commandClient?{artifact:'command-client.mjs',contract:commandClient.contract}:null,technical_source:source,application_contract_sha256:application.contract_sha256,source_capture_sha256:application.source_capture_sha256,executable_semantics_sha256:originalInspection.expanded.executable_semantics_sha256,entries:[...entryDirectories].map(([entry,directory])=>({entry,directory})),authority_effect:'none'};
   for(const [name,value]of [['system-graph.json',system],['business-system-bridge.json',bridge],['technical-profile.json',manifest]] as const)writeFileSync(path.join(output,name),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
   sourceCurrent();const captures=captureTechnicalServiceArchitectureArtifacts(output),files=captures.map(file=>({path:path.relative(output,file.file.path).split(path.sep).join('/'),sha256:file.file.sha256,bytes:file.file.bytes})),physical=pinCorePhysicalCaptures(captures),handle=Object.freeze({kind:'original-technical-service-architecture/v1' as const});
   for(const expected of originalFiles)if(!files.some(actual=>actual.path===expected.path&&actual.sha256===expected.sha256&&actual.bytes===expected.bytes))fail('original generated Entry bytes changed before layout capture');
   rows.set(handle,{directory:output,manifest,physical,files,entryDirectories,serviceOwner,serviceHandle});state(handle);return handle;
  },
  inspect(handle:TechnicalServiceArchitectureHandle){const row=state(handle);return Object.freeze({...row.manifest,files:row.files,inventory_sha256:dataDigest(row.files)});},
  async openRuntime(handle:TechnicalServiceArchitectureHandle,options:GenericRuntimeOptions):Promise<GenericTransactionApplicationRuntime>{
   const row=state(handle);if(!application.contract.services.some(service=>service.id===options.service))fail('original checked service required');
   const {service,...serviceOptions}=options;
   const runtime=await(row.serviceOwner&&row.serviceHandle?row.serviceOwner.openServiceRuntime(row.serviceHandle,service,serviceOptions):input.sdk.openRuntime(input.application,options));
   if(!('prepareCommand'in runtime)){await runtime.close();fail('original transaction runtime required');}try{state(handle);}catch(error){await runtime.close();throw error;}runtimes.set(runtime,{handle,service:options.service});return runtime;
  },
  async bindHttp(handle:TechnicalServiceArchitectureHandle,runtime:GenericTransactionApplicationRuntime,routeId:string){
   const row=state(handle),opened=runtimes.get(runtime),route=originalInspection.http_contract?.entries?.find((entry:any)=>entry.route.id===routeId);
   if(!opened||opened.handle!==handle||!route||route.route.service!==opened.service)fail('same original emitted runtime and checked route required');
   const directory=row.entryDirectories.get(route.route.entry);if(!directory)fail('original emitted Entry required');
   const module=await import(pathToFileURL(path.join(row.directory,directory,'entry-http.mjs')).href);state(handle);runtime.assertCurrent();return module.createGeneratedHttpHandler(input.sdk,input.application,runtime,routeId);
  },
 });
}
