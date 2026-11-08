/** C14 source-bound Core Commerce application artifacts.
 * The existing Core assembly owns source selection and executable storage.
 * Generated modules compose its process-local HTTP, Workflow and Event paths.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';
import {existsSync,mkdirSync,readFileSync,readdirSync,statSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {createCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from '../commerce/commerce-application-assembly-v1.js';
import type {CommerceServiceStorageOwnerV1} from '../commerce/commerce-service-storage-v1.js';
import type {CommerceAuthNativeOwnerV1} from '../commerce/commerce-auth-ready-bridge-v1.js';
import type {CommerceAuthActorV1,CommerceEntryContextOwnerV1} from '../commerce/commerce-entry-context-v1.js';
import type {CommerceEventPublicationResultV1} from '../commerce/commerce-service-storage-v1.js';
import type {DemoPayCommerceRawBytePortV1} from '../commerce/commerce-demopay-wire-v1.js';
import type {CoreCommerceEventDeliveryResult} from './core-commerce-event-delivery.js';
import type {CommerceOperationInvocationHandle} from '../commerce/commerce-stages-v1.js';
import type {OperationControlStepV1,TransactionPlanV1,TransactionStepV1} from '../commerce/commerce-data-v1.js';
import type {CoreCommerceExternalQueryBinding} from './core-commerce-external-query-selection.js';
import {createCoreCommerceSourceOwner,parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../commerce/commerce-core-semantic-owner.js';
import {coreSourceChildren,coreSourceDescendants,coreSourceText,coreSourceTokens,coreRelativePath} from '../commerce/commerce-core-syntax.js';
import {createCoreValueTypes} from '../commerce/commerce-core-types.js';
import {projectCoreServiceTopologyV1,type CoreServiceTopologyV1} from './core-topology-bridge.js';
import {isCoreCommerceMutableServiceFile,staticCoreCommerceServiceFiles} from './core-commerce-runtime-inventory.js';
import {selectCoreCommerceHttpGetSuccessProjection,projectCoreCommerceHttpGetSuccessValue,
 type CoreCommerceHttpGetSuccessProjection} from './core-commerce-http-success-projection.js';
import {emitCoreCommerceApplicationRuntime} from './core-commerce-application-runtime-emission.js';

type FileRow=Readonly<{path:string;sha256:string;bytes:number}>;
type ServiceRow=Readonly<{id:string;source_capture_sha256:string;family_sha256:string;schema_sha256:string;store_id:string;
 storage_mode:'create'|'reopen';files:readonly FileRow[]}>;
export type CoreCommerceServiceStorageSelection=Readonly<{mode:'create'}|{mode:'reopen';directory:string}>;
export type CoreCommerceServiceStorageOptions=Readonly<{services:Readonly<Record<string,CoreCommerceServiceStorageSelection>>}>;
type RouteRow=Readonly<{id:string;entry:string;service:string;method:'GET'|'POST';path:string;permission:string;auth_route_id:string;entry_contract_sha256:string;binding_file_sha256:string;request_bytes:number;response_bytes:number;body_timeout_ms:number|null;success_status:number;success_body_kind:string;success_projection:CoreCommerceHttpGetSuccessProjection|null}>;
type SelectedHttp=Readonly<{routes:readonly RouteRow[];error_statuses:Readonly<Record<string,number>>;
 topology:CoreServiceTopologyV1;
 workflow_owners:readonly Readonly<{workflow:string;service:string;input_entry:string}>[];
 workflow_calls:readonly Readonly<{workflow:string;entry:string}>[];
 event_deliveries:readonly Readonly<{event:string;entry:string}>[];
 event_productions:readonly Readonly<{event:string;entry:string;outbox:string;service:string}>[];
 event_inboxes:readonly Readonly<{entry:string;inbox:string;service:string}>[];
 event_publication:Readonly<{machine:string;signal:string}>}>;
export type CoreCommerceRouteSelection=
 Readonly<{kind:'matched';route:RouteRow;path_parameters:Readonly<Record<string,string>>}>|
 Readonly<{kind:'method-not-allowed';allow:readonly string[]}>|
 Readonly<{kind:'route-not-found'}>;
export interface CoreCommerceServiceArtifactManifest {
 readonly schema_version:'craft.core-commerce-service-artifacts/v1-candidate';
 readonly application:string;
 readonly source_capture_sha256:string;
 readonly family_sha256:string;
 readonly services:readonly ServiceRow[];
 readonly routes:readonly RouteRow[];
 readonly http_error_statuses:Readonly<Record<string,number>>;
 readonly files:readonly FileRow[];
 readonly complete_application:true;
 readonly missing_complete_application_classes:readonly [];
 readonly qualification:'original-selected-process-local-application;runtime-ports-required';
 readonly authority_effect:'none';
}
export interface CoreCommerceServiceArtifactOwner {
 inspect():CoreCommerceServiceArtifactManifest;
 serviceStorage(id:string):CommerceServiceStorageOwnerV1;
 selectHttpRoute(method:string,pathname:string):CoreCommerceRouteSelection;
 openSelectedEntryAuth(native:CommerceAuthNativeOwnerV1):ReturnType<CommerceApplicationAssemblyV1['openSelectedEntryAuth']>;
 openDemoPayDispatch(port:DemoPayCommerceRawBytePortV1):ReturnType<CommerceApplicationAssemblyV1['openDemoPayDispatch']>;
 openGeneratedOperation(invocation:CommerceOperationInvocationHandle):ReturnType<CommerceApplicationAssemblyV1['openGeneratedOperation']>;
 openGeneratedQuery(invocation:CommerceOperationInvocationHandle):ReturnType<CommerceApplicationAssemblyV1['openGeneratedQuery']>;
 openWorkflowIngress(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openWorkflowIngress']>;
 openOutboxRelay(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openOutboxRelay']>;
 openWorkflowClaimExecutor(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openWorkflowClaimExecutor']>;
 openWorkflowSnapshotQuery(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openWorkflowSnapshotQuery']>;
 openWorkflowContinuation(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openWorkflowContinuation']>;
 openWorkflowStepRunner(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openWorkflowStepRunner']>;
 openWorkflowLocalObservation(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openWorkflowLocalObservation']>;
 openWorkflowLocalObservationRunner(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openWorkflowLocalObservationRunner']>;
 openWorkflowPass(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['openWorkflowPass']>;
 openCrossServiceEvent(entryId:string):ReturnType<CommerceApplicationAssemblyV1['openCrossServiceEvent']>;
 openSelectedEventPass(entryId:string):CoreCommerceSelectedEventPass;
 inspectWorkerActorRequirements(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['inspectWorkerActorRequirements']>;
 openSelectedHttpRuntime(native:CommerceAuthNativeOwnerV1):Promise<CoreCommerceSelectedHttpRuntime>;
 assertCurrent():void;
 close():void;
}
type SelectedEventRoute=ReturnType<CommerceApplicationAssemblyV1['openCrossServiceEvent']>;
export type CoreCommerceSelectedEventPassResult=
 Readonly<{kind:'not-ready';authority_effect:'none'}>|
 Readonly<{kind:'receiver-result';result:Exclude<CoreCommerceEventDeliveryResult,{kind:'receiver-committed'}>}>|
 Readonly<{kind:'publication-result';result:CommerceEventPublicationResultV1}>;
export interface CoreCommerceSelectedEventPass {
 inspect():Readonly<{entry:string;event:string;outbox:string;inbox:string;
  producer_service:string;receiver_service:string;source_capture_sha256:string;
  qualification:'source-selected-in-process-event-delivery-and-publication'}>;
 inspectActorRequirement():ReturnType<ReturnType<SelectedEventRoute['openDelivery']>['inspectActorRequirement']>;
 scanReady(cursor:string|null,limit:number):Readonly<{occurrence_ids:readonly string[];next_cursor:string|null}>;
 runReady(occurrenceId:string,actor:CommerceAuthActorV1|null,signal?:AbortSignal):Promise<CoreCommerceSelectedEventPassResult>;
 assertCurrent():void;
}
export interface CoreCommerceSelectedHttpRuntime {
 readonly qualification:'source-selected-in-process-GET-Query-and-POST-Operation;generated-event-worker-runtime';
 readonly auth:CommerceEntryContextOwnerV1;
 readonly service_actor_requirements:readonly CoreCommerceExternalQueryBinding[];
 bindServiceActor(actor:CommerceAuthActorV1):readonly string[];
 handle(request:Request,actor:CommerceAuthActorV1|null):Promise<Response>;
 assertCurrent():void;
 close():void;
}
const digest=(value:Buffer|string)=>createHash('sha256').update(value).digest('hex');
const text=(value:unknown)=>JSON.stringify(value,null,2)+'\n';
const segments=(value:string)=>value.split('/').slice(1);
function sourceTransactions(steps:readonly OperationControlStepV1[]):readonly TransactionPlanV1[]{
 const found:TransactionPlanV1[]=[];
 const visit=(rows:readonly OperationControlStepV1[],depth:number):void=>{
  if(depth>64||found.length>128)throw new Error('bounded source transaction graph required');
  for(const row of rows){
   if(row.kind==='transaction')found.push(row.transaction);
   else if(row.kind==='present'&&row.transaction)found.push(row.transaction);
   else if(row.kind==='conditional'){visit(row.then,depth+1);visit(row.otherwise,depth+1);}
   else if(row.kind==='read-set')visit(row.body,depth+1);
  }
 };
 visit(steps,0);return found;
}
function sourceMutations(steps:readonly TransactionStepV1[]):readonly Extract<TransactionStepV1,{kind:'mutation'}>[]{
 const found:Extract<TransactionStepV1,{kind:'mutation'}>[]=[];
 const visit=(rows:readonly TransactionStepV1[],depth:number):void=>{
  if(depth>64||found.length>256)throw new Error('bounded source mutation graph required');
  for(const row of rows){
   if(row.kind==='mutation')found.push(row);
   else if(row.kind==='conditional'){visit(row.then,depth+1);visit(row.otherwise,depth+1);}
   else if(row.kind==='for')visit(row.body,depth+1);
  }
 };
 visit(steps,0);return found;
}
function routeParameters(template:string,pathname:string):Readonly<Record<string,string>>|null{
 const expected=segments(template),actual=segments(pathname);
 if(expected.length!==actual.length)return null;
 const parameters:Record<string,string>={};
 for(let i=0;i<expected.length;i++){
  const token=expected[i]!,value=actual[i]!;
  if(token.startsWith('{')&&token.endsWith('}')){
   let decoded:string;try{decoded=decodeURIComponent(value);}catch{return null;}
   if(!decoded||decoded.includes('/')||decoded.includes('\\')||Object.hasOwn(parameters,token.slice(1,-1)))return null;
   parameters[token.slice(1,-1)]=decoded;
  }else if(token!==value)return null;
 }
 return Object.freeze(parameters);
}
type BodyResult={ok:true;value:unknown}|{ok:false;code:'request-aborted'|'request-too-large'|'body-timeout'|'body-read-failed'|'invalid-request'};
async function readBoundedJson(request:Request,bytes:number,timeoutMs:number):Promise<BodyResult>{
 if(request.signal.aborted)return {ok:false,code:'request-aborted'};
 if(!request.body)return {ok:false,code:'invalid-request'};
 const reader=request.body.getReader();
 let timer:ReturnType<typeof setTimeout>|undefined,abort:()=>void=()=>{};
 const stopped=new Promise<BodyResult>(resolve=>{
  timer=setTimeout(()=>resolve({ok:false,code:'body-timeout'}),timeoutMs);
  abort=()=>resolve({ok:false,code:'request-aborted'});
  request.signal.addEventListener('abort',abort,{once:true});
 });
 const reading=(async():Promise<BodyResult>=>{
  const parts:Uint8Array[]=[];let size=0;
  try{
   for(;;){
    const next=await reader.read();
    if(next.done)break;
    size+=next.value.byteLength;
    if(size>bytes)return {ok:false,code:'request-too-large'};
    parts.push(next.value);
   }
   const raw=Buffer.concat(parts.map(part=>Buffer.from(part)));
   let decoded:string;
   try{decoded=new TextDecoder('utf-8',{fatal:true}).decode(raw);}
   catch{return {ok:false,code:'invalid-request'};}
   let value:unknown;
   try{value=JSON.parse(decoded);}
   catch{return {ok:false,code:'invalid-request'};}
   if(!value||typeof value!=='object'||Array.isArray(value))return {ok:false,code:'invalid-request'};
   return {ok:true,value};
  }catch{return {ok:false,code:'body-read-failed'};}
 })();
 const result=await Promise.race([reading,stopped]);
 if(timer)clearTimeout(timer);
 request.signal.removeEventListener('abort',abort);
 if(!result.ok)void reader.cancel().catch(()=>{});
 return result;
}
function selectedRoutes(sourceRoot:string,expectedSourceSha:string,expectedApplication:string,expectedServices:readonly string[]):SelectedHttp{
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(sourceRoot,'application.alch');
 const semantics=createCoreCommerceSemanticOwner(sources);
 let semantic:ReturnType<typeof semantics.check>|undefined;
 try{
  const checked=sources.inspect(capture);
  if(checked.capture_sha256!==expectedSourceSha)throw new Error('selected HTTP source differs from original application assembly');
  semantic=semantics.check(capture);
  const topology=projectCoreServiceTopologyV1(sources,capture,semantics,semantic);
  if(topology.application!==expectedApplication||JSON.stringify(topology.services.map(service=>service.id).sort())!==JSON.stringify([...expectedServices].sort()))
   throw new Error('selected HTTP topology differs from original application assembly');
  const root=checked.reconstruction.modules.flatMap(module=>module.declarations).find(declaration=>declaration.interface_kind==='application-composition');
  if(!root||root.id!==expectedApplication)throw new Error('original application declaration required for HTTP selection');
  const clauses=coreSourceChildren(root.syntax,'interface-clause').filter(clause=>coreSourceTokens(clause).find(token=>!token.layout)?.token==='http-bindings');
  if(clauses.length!==1)throw new Error('one original application HTTP binding reference required');
  const references=coreSourceDescendants(clauses[0]!,'reference');
  if(references.length!==1)throw new Error('one exact original HTTP binding reference required');
  const reference=coreSourceText(references[0]!),parts=reference.split('#');
  if(parts.length!==2||parts[1]!=='/bindings')throw new Error('original HTTP reference must select /bindings');
  const selectedPath=path.posix.normalize(path.posix.join(path.posix.dirname(checked.application_path),parts[0]!));
  if(!coreRelativePath(selectedPath)||!selectedPath.endsWith('.json'))throw new Error('normalized original HTTP binding asset required');
  const file=checked.files.find(row=>row.path===selectedPath);
  if(!file)throw new Error('original HTTP binding asset absent from captured source');
  const selected=parseCoreCommerceJson(file.text,file.path) as {schema_version?:unknown;bindings?:unknown;errors?:unknown;$defs?:unknown};
  if(selected.schema_version!=='craft.commerce-entry-outcomes/v1-candidate'||!Array.isArray(selected.bindings)||!Array.isArray(selected.errors))
   throw new Error('checked Commerce HTTP bindings required');
  const errorStatuses:Record<string,number>={};
  for(const candidate of selected.errors){
   if(!candidate||typeof candidate!=='object'||Array.isArray(candidate))throw new Error('HTTP error mapping object required');
   const row=candidate as Record<string,unknown>;
   if(typeof row.code!=='string'||!row.code||Object.hasOwn(errorStatuses,row.code)||
    !Number.isSafeInteger(row.status)||Number(row.status)<400||Number(row.status)>599)
    throw new Error('bounded unique source HTTP error mapping required');
   errorStatuses[row.code]=Number(row.status);
  }
  for(const code of ['route-not-found','method-not-allowed','unauthorized','forbidden','resource-not-found','adapter-contract-defect'])
   if(errorStatuses[code]===undefined)throw new Error('required source HTTP error mapping absent');
  const entries=new Map(topology.entries.map(entry=>[entry.id,entry]));
  const checkedSemantic=semantics.inspect(semantic),checkedReads=checkedSemantic.reads;
  const routes:RouteRow[]=[],ids=new Set<string>(),keys=new Set<string>();
  for(const candidate of selected.bindings){
   if(!candidate||typeof candidate!=='object'||Array.isArray(candidate))throw new Error('HTTP binding object required');
   const binding=candidate as Record<string,unknown>,entry=entries.get(String(binding.logical_entry));
   if(typeof binding.id!=='string'||!binding.id||ids.has(binding.id)||!entry||entry.interaction!=='request-response'||
    !['GET','POST'].includes(String(binding.method))||typeof binding.path!=='string'||!/^\/(?:[A-Za-z0-9_-]+|\{[A-Za-z][A-Za-z0-9_]*\})(?:\/(?:[A-Za-z0-9_-]+|\{[A-Za-z][A-Za-z0-9_]*\}))*$/.test(binding.path))
    throw new Error('HTTP binding must select one original request Entry and bounded route');
   if(!Number.isSafeInteger(binding.request_bytes)||Number(binding.request_bytes)<0||Number(binding.request_bytes)>1048576||
    !Number.isSafeInteger(binding.response_bytes)||Number(binding.response_bytes)<1||Number(binding.response_bytes)>8388608||
    (binding.body_timeout_ms!==undefined&&(!Number.isSafeInteger(binding.body_timeout_ms)||Number(binding.body_timeout_ms)<1||Number(binding.body_timeout_ms)>30000))||
    (binding.method==='POST'&&(entry.target_role!=='Operation'||Number(binding.request_bytes)<1||binding.body_timeout_ms===undefined))||
    (binding.method==='GET'&&(entry.target_role!=='Query'||binding.request_bytes!==0)))
    throw new Error('selected HTTP route must retain bounded original transport and target role');
   const success=binding.success;
   if(!success||typeof success!=='object'||Array.isArray(success)||!Number.isSafeInteger((success as Record<string,unknown>).status)||
    Number((success as Record<string,unknown>).status)<200||Number((success as Record<string,unknown>).status)>299)
    throw new Error('selected HTTP success status required');
   const successBody=(success as Record<string,unknown>).body;
   if(binding.method==='GET'&&(!successBody||typeof successBody!=='object'||Array.isArray(successBody)||
     (successBody as Record<string,unknown>).kind!=='ok'||typeof (successBody as Record<string,unknown>).value_ref!=='string'))
    throw new Error('selected GET Query response projection required');
   let successProjection:CoreCommerceHttpGetSuccessProjection|null=null;
   if(binding.method==='GET'){
    const reads=checkedReads.filter(read=>read.query.module+'.'+read.query.name===entry.target);
    if(reads.length!==1||reads[0]!.service!==entry.service||entry.target_service!==entry.service)
     throw new Error('selected GET route requires one original service-owned Query');
    successProjection=selectCoreCommerceHttpGetSuccessProjection(reads[0]!,
     (successBody as Record<string,unknown>).value_ref as string);
    if(successProjection.query!==entry.target)throw new Error('selected GET Query target changed');
   }
   let bodyKind='ok';
   if(binding.method==='POST'){
    const defs=selected.$defs;
    if(!defs||typeof defs!=='object'||Array.isArray(defs)||
     typeof binding.request_ref!=='string'||typeof (success as Record<string,unknown>).body_ref!=='string')
     throw new Error('selected POST request and response references required');
    const resolve=(reference:string):Record<string,unknown>=>{
     const match=/^#\/\$defs\/([A-Za-z][A-Za-z0-9]*)$/.exec(reference);
     const value=match?(defs as Record<string,unknown>)[match[1]!]:undefined;
     if(!value||typeof value!=='object'||Array.isArray(value))
      throw new Error('selected POST local schema reference required');
     return value as Record<string,unknown>;
    };
    const request=resolve(binding.request_ref);
    const body=resolve((success as Record<string,unknown>).body_ref as string);
    const properties=body.properties;
    if(request.type!=='object'||!request.properties||typeof request.properties!=='object'||Array.isArray(request.properties)||
     body.type!=='object'||!Array.isArray(body.required)||!body.required.includes('kind')||!body.required.includes('value')||
     !properties||typeof properties!=='object'||Array.isArray(properties))
     throw new Error('selected POST object request and response projection required');
    const kind=(properties as Record<string,unknown>).kind;
    const value=(properties as Record<string,unknown>).value;
    if(!kind||typeof kind!=='object'||Array.isArray(kind)||typeof (kind as Record<string,unknown>).const!=='string'||
     !value||typeof value!=='object'||Array.isArray(value)||typeof (value as Record<string,unknown>).$ref!=='string')
     throw new Error('selected POST response kind and value required');
    resolve((value as Record<string,unknown>).$ref as string);
    bodyKind=(kind as Record<string,unknown>).const as string;
   }
   const key=binding.method+' '+binding.path;
   if(keys.has(key))throw new Error('duplicate original HTTP binding route');
   ids.add(binding.id);keys.add(key);
   routes.push(Object.freeze({id:binding.id,entry:entry.id,service:entry.service,method:binding.method as 'GET'|'POST',path:binding.path,
    permission:entry.permission,auth_route_id:entry.auth_route_id,entry_contract_sha256:entry.contract_sha256,binding_file_sha256:file.sha256,
    request_bytes:Number(binding.request_bytes),response_bytes:Number(binding.response_bytes),body_timeout_ms:binding.body_timeout_ms===undefined?null:Number(binding.body_timeout_ms),
    success_status:Number((success as Record<string,unknown>).status),success_body_kind:bodyKind,
    success_projection:successProjection}));
  }
  for(let i=0;i<routes.length;i++)for(let j=i+1;j<routes.length;j++){
   const left=routes[i]!,right=routes[j]!,a=segments(left.path),b=segments(right.path);
   if(left.method===right.method&&a.length===b.length&&a.every((part,index)=>part===b[index]||part.startsWith('{')||b[index]!.startsWith('{')))
    throw new Error('ambiguous original HTTP binding routes');
  }
  if(!routes.length)throw new Error('original application has no selected HTTP binding');
  const topologyEntries=new Map(topology.entries.map(entry=>[entry.id,entry]));
  const checkedWorkflows=checkedSemantic.workflows;
  const workflowOwners=checkedWorkflows.map(workflow=>{
   const id=workflow.workflow.module+'.'+workflow.workflow.name;
   const input=topologyEntries.get(workflow.input_entry);
   if(!topology.workflows.some(row=>row.id===id)||
    !topology.services.some(service=>service.id===workflow.service)||
    !input||input.target!==id||input.service!==workflow.service||input.target_role!=='Workflow')
    throw new Error('checked Workflow owner and input Entry differ from selected topology');
   return Object.freeze({workflow:id,service:workflow.service,input_entry:input.id});
  });
  const workflowCalls=checkedWorkflows.flatMap(workflow=>{
   const id=workflow.workflow.module+'.'+workflow.workflow.name;
   const calls=[...workflow.drivers.map(driver=>driver.call),
    ...workflow.steps.flatMap(step=>step.kind==='remote'?[step.call]:[])];
   return calls.map(call=>{
    const entry=topologyEntries.get(call.entry);
    if(!entry||entry.target!==call.target||entry.target_role!==call.role)
     throw new Error('checked Workflow call differs from source-selected Entry topology');
    return Object.freeze({workflow:id,entry:entry.id});
   });
  });
  const eventDeliveries=checkedSemantic.entries.flatMap(entry=>{
   if(entry.interaction!=='event')return [];
   const event=entry.parameters.length===1&&entry.parameters[0]!.type.kind==='record'
    ?entry.parameters[0]!.type.name:null;
   if(!event||!topology.events.some(row=>row.id===event)||
    topologyEntries.get(entry.id)?.interaction!=='event')
    throw new Error('checked Event delivery differs from source-selected Entry topology');
   return [Object.freeze({event,entry:entry.id})];
  });
  const declarations=checked.reconstruction.modules.flatMap(module=>module.declarations),
   entities=new Map(declarations.filter(row=>row.surface==='Entity').map(row=>[row.id,row])),
   valueTypes=createCoreValueTypes(checked.reconstruction);
  const eventProductions=checkedSemantic.effects.flatMap(effect=>{
   const operation=effect.operation.module+'.'+effect.operation.name;
   return sourceTransactions(effect.body).flatMap(transaction=>{
    const mutations=sourceMutations(transaction.body);
    return mutations.filter(row=>row.operation==='record-event').flatMap(record=>{
     if(!topology.events.some(event=>event.id===record.target))
      throw new Error('source Event emission lacks a checked Event declaration');
     const outboxes=mutations.filter(row=>{
      const entity=entities.get(row.target),field=entity?.fields.find(field=>field.name==='event');
      if(row.operation!=='create'||!entity||!field||
       entity.identity.length!==1||entity.identity[0]!=='eventId'||
       !transaction.participants.includes(entity.id))return false;
      const type=valueTypes.type(entity.module,field.type,field.span);
      return type.kind==='record'&&type.name===record.target;
     });
     const entries=topology.entries.filter(entry=>entry.target_role==='Operation'&&
      entry.target===operation&&entry.service===effect.service);
     // A source record-event can be local to an Operation. Only a transaction
     // that also creates an Event outbox crosses the application boundary.
     if(outboxes.length===0)return [];
     if(outboxes.length!==1||entries.length!==1||effect.service===null)
      throw new Error('one checked producer Entry and atomic Event outbox required');
     return [Object.freeze({event:record.target,entry:entries[0]!.id,outbox:outboxes[0]!.target,
      service:effect.service})];
    });
   });
  });
  const eventInboxes=checkedSemantic.effects.flatMap(effect=>{
   const operation=effect.operation.module+'.'+effect.operation.name;
   const entries=topology.entries.filter(entry=>entry.interaction==='event'&&
    entry.target_role==='Operation'&&entry.target===operation&&entry.service===effect.service);
   if(!entries.length)return [];
   const acknowledgements=effect.body.filter(step=>step.kind==='acknowledge');
   if(entries.length!==1||acknowledgements.length!==1||acknowledgements[0]!.kind!=='acknowledge'||
    effect.service===null)throw new Error('one checked Event receiver inbox required');
   const inbox=acknowledgements[0]!.inbox,entity=entities.get(inbox);
   if(!entity||!sourceTransactions(effect.body).some(transaction=>
    transaction.participants.includes(inbox)&&sourceMutations(transaction.body).some(
     mutation=>mutation.operation==='create'&&mutation.target===inbox)))
    throw new Error('Event receiver must atomically create its source inbox');
   return [Object.freeze({entry:entries[0]!.id,inbox,service:effect.service})];
  });
  const familyClauses=coreSourceChildren(root.syntax,'interface-clause').filter(clause=>
   coreSourceTokens(clause).find(token=>!token.layout)?.token==='profile-family');
  if(familyClauses.length!==1)throw new Error('one original profile family asset required');
  const familyReferences=coreSourceDescendants(familyClauses[0]!,'reference');
  if(familyReferences.length!==1)throw new Error('one exact original profile family reference required');
  const familyPath=path.posix.normalize(path.posix.join(path.posix.dirname(checked.application_path),
   coreSourceText(familyReferences[0]!)));
  if(!coreRelativePath(familyPath)||!familyPath.endsWith('.json'))
   throw new Error('normalized original profile family asset required');
  const familyFile=checked.files.find(row=>row.path===familyPath),familyValue=familyFile&&
   parseCoreCommerceJson(familyFile.text,familyFile.path) as {families?:Record<string,unknown>}|undefined;
  const family=familyValue?.families?.EventInboxOutbox as
   {primitive?:unknown;publication?:{machine?:unknown;signal?:unknown}}|undefined;
  if(family?.primitive!=='event-inbox-outbox'||typeof family.publication?.machine!=='string'||
   typeof family.publication.signal!=='string'||!checkedSemantic.pure.declarations.some(row=>
    row.kind==='StateMachine'&&row.name===family.publication!.machine))
   throw new Error('one source-selected Event publication StateMachine required');
  const eventPublication=Object.freeze({machine:family.publication.machine,signal:family.publication.signal});
  return Object.freeze({routes:Object.freeze(routes.sort((a,b)=>a.method.localeCompare(b.method)||a.path.localeCompare(b.path))),
   error_statuses:Object.freeze(errorStatuses),topology,
   workflow_owners:Object.freeze(workflowOwners),workflow_calls:Object.freeze([...new Map(
    workflowCalls.map(call=>[call.workflow+'|'+call.entry,call] as const)).values()]),
   event_deliveries:Object.freeze(eventDeliveries),event_productions:Object.freeze(eventProductions),
   event_inboxes:Object.freeze(eventInboxes),event_publication:eventPublication});
 }finally{if(semantic)semantics.dispose(semantic);sources.dispose(capture);}
}
function inventory(root:string,skipMutableServiceFiles=false):FileRow[]{
 const rows:FileRow[]=[];let seen=0;
 const visit=(relative:string)=>{
  for(const entry of readdirSync(path.join(root,relative),{withFileTypes:true})){
   const child=relative?relative+'/'+entry.name:entry.name;
   if(entry.isDirectory())visit(child);
   else if(entry.isFile()){
    if(++seen>8192)throw new Error('Core Commerce artifact inventory limit exceeded');
    if(skipMutableServiceFiles&&isCoreCommerceMutableServiceFile(child))continue;
    if(rows.length>=2048)throw new Error('Core Commerce artifact inventory limit exceeded');
    const full=path.join(root,child),stats=statSync(full);
    if(stats.size>64*1024*1024)throw new Error('Core Commerce artifact file limit exceeded');
    const bytes=readFileSync(full);rows.push({path:child,sha256:digest(bytes),bytes:bytes.length});
   }else throw new Error('Core Commerce artifact must be a regular file');
  }
 };
 visit('');return rows.sort((a,b)=>a.path.localeCompare(b.path));
}
/** Build the real selected Core Commerce assembly once, open every service
 * stores, then emit a physical inventory and graph/bridge view of that assembly.
 * Native Entry, HTTP, provider and worker custody remain with their source owners. */
export async function createCoreCommerceServiceArtifactOwner(sourceRoot:string,outputRoot:string,
 options?:CoreCommerceServiceStorageOptions):Promise<CoreCommerceServiceArtifactOwner>{
 if(!path.isAbsolute(sourceRoot)||!path.isAbsolute(outputRoot)||path.normalize(sourceRoot)!==sourceRoot||path.normalize(outputRoot)!==outputRoot||existsSync(outputRoot))
  throw new Error('normalized source and fresh absolute artifact output roots required');
 const relation=path.relative(sourceRoot,outputRoot);
 if(!relation||relation!=='..'&&!relation.startsWith('..'+path.sep)&&!path.isAbsolute(relation))
  throw new Error('artifact output must be outside original source');
 if(options!==undefined&&(!options||typeof options!=='object'||Array.isArray(options)||
   Object.keys(options).length!==1||!Object.hasOwn(options,'services')||
   !options.services||typeof options.services!=='object'||Array.isArray(options.services)))
  throw new Error('exact explicit per-service storage selections required');
 let assembly:CommerceApplicationAssemblyV1|undefined;
 try{
  mkdirSync(outputRoot,{mode:0o700});
  assembly=await createCommerceApplicationAssemblyV1(sourceRoot,path.join(outputRoot,'runtime'));
  const source=assembly.inspect(),stores=new Map<string,CommerceServiceStorageOwnerV1>(),storeDirectories=new Map<string,string>();
  if(!source.services.length||new Set(source.services).size!==source.services.length)
   throw new Error('Core Commerce projection requires distinct original selected services');
  if(options&&JSON.stringify(Object.keys(options.services).sort())!==JSON.stringify([...source.services].sort()))
   throw new Error('explicit storage selection must cover exactly the original services');
  const selections=new Map(source.services.map(id=>{
   const selection=options?.services[id]??{mode:'create' as const};
   if(!selection||typeof selection!=='object'||Array.isArray(selection)||
     (selection.mode==='create'&&Object.keys(selection).length!==1)||
     (selection.mode==='reopen'&&(Object.keys(selection).length!==2||
       typeof selection.directory!=='string'||!path.isAbsolute(selection.directory)||
       path.normalize(selection.directory)!==selection.directory))||
     (selection.mode!=='create'&&selection.mode!=='reopen'))
    throw new Error('exact create or reopened storage selection required for '+id);
   return [id,selection] as const;
  }));
  const recoveredDirectories=source.services.map(id=>selections.get(id)!).filter(
   (selection):selection is Readonly<{mode:'reopen';directory:string}>=>selection.mode==='reopen').map(selection=>selection.directory);
  if(new Set(recoveredDirectories).size!==recoveredDirectories.length)
   throw new Error('recovered services require distinct original store directories');
  const selectedHttp=selectedRoutes(sourceRoot,source.source_capture_sha256,source.application,source.services),routes=selectedHttp.routes;
  const services:ServiceRow[]=[];
  for(const id of source.services){
   const selection=selections.get(id)!;
   const storeDirectory=selection.mode==='reopen'?selection.directory:path.join(outputRoot,'runtime',id);
   const store=selection.mode==='reopen'
    ?await assembly.openRecoveredServiceStorage(id,storeDirectory)
    :await assembly.openServiceStorage(id);
   const view=store.inspect();stores.set(id,store);storeDirectories.set(id,storeDirectory);
   if(view.service!==id||view.source_capture_sha256!==source.source_capture_sha256||view.family_sha256!==source.family_sha256)
    throw new Error('service storage lost original source/profile selection');
   services.push({id,source_capture_sha256:view.source_capture_sha256,family_sha256:view.family_sha256,
    schema_sha256:view.schema_sha256,store_id:view.store_id,storage_mode:selection.mode,files:inventory(storeDirectory)});
  }
  services.sort((a,b)=>a.id.localeCompare(b.id));
  for(const service of services){
   for(const file of service.files)Object.freeze(file);
   Object.freeze(service.files);Object.freeze(service);
  }
  Object.freeze(services);
  const artifacts=path.join(outputRoot,'artifacts');mkdirSync(artifacts,{recursive:true,mode:0o700});
  const topology=selectedHttp.topology;
  const runtimeModules=emitCoreCommerceApplicationRuntime({application:source.application,
   source_capture_sha256:source.source_capture_sha256,family_sha256:source.family_sha256,
   services:services.map(service=>service.id),workflows:topology.workflows.map(workflow=>workflow.id),
   event_entries:selectedHttp.event_deliveries.map(delivery=>delivery.entry)});
  for(const module of runtimeModules)
   writeFileSync(path.join(artifacts,module.path),module.content,{mode:0o600,flag:'wx'});
  const runtimeModule=(name:string)=>{
   const found=runtimeModules.find(module=>module.path===name);
   if(!found)throw new Error('selected Commerce runtime module absent: '+name);
   return found;
  };
  const outboxes=[...new Map(selectedHttp.event_productions.map(row=>[row.outbox,row] as const)).values()];
  const inboxes=[...new Map(selectedHttp.event_inboxes.map(row=>[row.inbox,row] as const)).values()];
  if(outboxes.length!==selectedHttp.event_productions.length||
   inboxes.length!==selectedHttp.event_inboxes.length)
   throw new Error('one source-selected Event route per outbox and inbox required');
  const graph={schema_version:'craft.core-commerce-system-graph/v1-candidate',application:source.application,
   source_capture_sha256:source.source_capture_sha256,family_sha256:source.family_sha256,
   nodes:[{id:'application:'+source.application,kind:'application',source_selector:source.application},
    {id:'runtime:application',kind:'generated-application-runtime',artifact:'application.mjs',
     sha256:runtimeModule('application.mjs').sha256},
    {id:'runtime:workflow-worker',kind:'generated-workflow-worker-runtime',artifact:'workflow-worker.mjs',
     sha256:runtimeModule('workflow-worker.mjs').sha256},
    {id:'runtime:event-relay',kind:'generated-event-relay-runtime',artifact:'event-relay.mjs',
     sha256:runtimeModule('event-relay.mjs').sha256},
    ...services.flatMap(service=>[
     {id:'service:'+service.id,kind:'service',source_selector:service.id},
     {id:'storage:'+service.id,kind:'sqlite-storage',
      ...(service.storage_mode==='create'?{artifact:'runtime/'+service.id+'/store.sqlite'}:{recovered_store_ref:'storage:'+service.id}),
      storage_mode:service.storage_mode,schema_sha256:service.schema_sha256,store_id:service.store_id}]),
    ...topology.entries.map(entry=>({id:'entry:'+entry.id,kind:'entry',source_selector:entry.id,
     contract_sha256:entry.contract_sha256,permission:entry.permission,auth_route_id:entry.auth_route_id})),
    ...topology.events.map(event=>({id:'event:'+event.id,kind:'event',source_selector:event.id,
     source_site:event.source_site})),
    ...topology.workflows.map(workflow=>({id:'workflow:'+workflow.id,kind:'workflow',
     source_selector:workflow.id,source_site:workflow.source_site,contract_sha256:workflow.contract_sha256})),
    ...outboxes.map(outbox=>({id:'outbox:'+outbox.outbox,kind:'event-outbox',
     source_selector:outbox.outbox})),
    ...inboxes.map(inbox=>({id:'inbox:'+inbox.inbox,kind:'event-inbox',
     source_selector:inbox.inbox})),
    {id:'publication:'+selectedHttp.event_publication.machine,kind:'event-publication',
     source_selector:selectedHttp.event_publication.machine,signal:selectedHttp.event_publication.signal},
    ...routes.map(route=>({id:'http:'+route.id,kind:'http-route',method:route.method,path:route.path,
     binding_file_sha256:route.binding_file_sha256}))],
   edges:[{from:'application:'+source.application,to:'runtime:application',relation:'runs-as'},
    {from:'runtime:application',to:'runtime:workflow-worker',relation:'opens-worker'},
    {from:'runtime:application',to:'runtime:event-relay',relation:'opens-relay'},
    ...topology.workflows.map(workflow=>({from:'runtime:workflow-worker',to:'workflow:'+workflow.id,
     relation:'executes-workflow'})),
    ...selectedHttp.event_deliveries.map(delivery=>({from:'runtime:event-relay',to:'entry:'+delivery.entry,
     relation:'delivers-selected-event'})),
    ...services.flatMap(service=>[
    {from:'application:'+source.application,to:'service:'+service.id,relation:'selects-service'},
    {from:'service:'+service.id,to:'storage:'+service.id,relation:'owns-storage'}])]
    .concat(topology.entries.map(entry=>({from:'service:'+entry.service,to:'entry:'+entry.id,relation:'owns-entry'})))
    .concat(routes.map(route=>({from:'entry:'+route.entry,to:'http:'+route.id,relation:'exposes-route'})))
    .concat(selectedHttp.workflow_owners.flatMap(owner=>[
     {from:'service:'+owner.service,to:'workflow:'+owner.workflow,relation:'owns-workflow'},
     {from:'entry:'+owner.input_entry,to:'workflow:'+owner.workflow,relation:'starts-workflow'}]))
    .concat(selectedHttp.workflow_calls.map(call=>({from:'workflow:'+call.workflow,
     to:'entry:'+call.entry,relation:'invokes-entry'})))
    .concat(selectedHttp.event_deliveries.map(delivery=>({from:'event:'+delivery.event,
     to:'entry:'+delivery.entry,relation:'delivers-event'})))
    .concat(selectedHttp.event_productions.flatMap(production=>[
     {from:'entry:'+production.entry,to:'event:'+production.event,relation:'produces-event'},
     {from:'service:'+production.service,to:'outbox:'+production.outbox,relation:'owns-outbox'},
     {from:'outbox:'+production.outbox,to:'event:'+production.event,relation:'contains-event'},
     {from:'publication:'+selectedHttp.event_publication.machine,to:'outbox:'+production.outbox,
      relation:'transitions-outbox'}]))
    .concat(selectedHttp.event_inboxes.flatMap(inbox=>[
     {from:'service:'+inbox.service,to:'inbox:'+inbox.inbox,relation:'owns-inbox'},
     {from:'entry:'+inbox.entry,to:'inbox:'+inbox.inbox,relation:'commits-inbox'}]))};
  const nodeIds=new Set(graph.nodes.map(node=>node.id));
  if(nodeIds.size!==graph.nodes.length||graph.edges.some(edge=>!nodeIds.has(edge.from)||!nodeIds.has(edge.to))||
   new Set(graph.edges.map(edge=>edge.from+'|'+edge.relation+'|'+edge.to)).size!==graph.edges.length)
   throw new Error('selected Commerce graph must have distinct closed nodes and edges');
  const bridge={schema_version:'craft.core-commerce-business-system-bridge/v1-candidate',application:source.application,
   source_capture_sha256:source.source_capture_sha256,family_sha256:source.family_sha256,
   links:[{business:source.application,system:'application:'+source.application,relation:'realizes-application'},
    {business:source.application,system:'runtime:application',relation:'runs-application'},
    ...topology.workflows.map(workflow=>({business:workflow.id,system:'runtime:workflow-worker',
     relation:'runs-workflow'})),
    ...selectedHttp.event_deliveries.map(delivery=>({business:delivery.event,system:'runtime:event-relay',
     relation:'delivers-event'})),
    ...services.map(service=>({business:service.id,system:'service:'+service.id,relation:'realizes-service'})),
    ...topology.entries.map(entry=>({business:entry.id,system:'entry:'+entry.id,relation:'realizes-entry',
     permission:entry.permission,auth_route_id:entry.auth_route_id})),
    ...topology.events.map(event=>({business:event.id,system:'event:'+event.id,relation:'realizes-event'})),
    ...topology.workflows.map(workflow=>({business:workflow.id,system:'workflow:'+workflow.id,
     relation:'realizes-workflow'})),
    ...outboxes.map(outbox=>({business:outbox.outbox,system:'outbox:'+outbox.outbox,
     relation:'realizes-outbox'})),
    ...inboxes.map(inbox=>({business:inbox.inbox,system:'inbox:'+inbox.inbox,
     relation:'realizes-inbox'})),
    {business:selectedHttp.event_publication.machine,
     system:'publication:'+selectedHttp.event_publication.machine,relation:'realizes-publication'},
    ...routes.map(route=>({business:route.entry,system:'http:'+route.id,relation:'exposes-entry',permission:route.permission,auth_route_id:route.auth_route_id}))]};
  if(bridge.links.some(link=>!nodeIds.has(link.system)))
   throw new Error('selected Commerce bridge must reference emitted system nodes');
  writeFileSync(path.join(artifacts,'system-graph.json'),text(graph),{mode:0o600});
  writeFileSync(path.join(artifacts,'business-system-bridge.json'),text(bridge),{mode:0o600});
  for(const service of services)writeFileSync(path.join(artifacts,service.id+'.json'),text(service),{mode:0o600});
  const files=inventory(artifacts);
  for(const file of files)Object.freeze(file);
  Object.freeze(files);
  const manifest:CoreCommerceServiceArtifactManifest=Object.freeze({
   schema_version:'craft.core-commerce-service-artifacts/v1-candidate',application:source.application,
   source_capture_sha256:source.source_capture_sha256,family_sha256:source.family_sha256,
   services,routes,http_error_statuses:selectedHttp.error_statuses,files,complete_application:true,
   missing_complete_application_classes:Object.freeze([] as const),
   qualification:'original-selected-process-local-application;runtime-ports-required',authority_effect:'none'});
  writeFileSync(path.join(artifacts,'manifest.json'),text(manifest),{mode:0o600});
  let closed=false,selectedEntryAuthOpened=false;
  const eventRoutes=new Map<string,SelectedEventRoute>();
  const eventPasses=new Map<string,CoreCommerceSelectedEventPass>();
  const selectedEvent=(entryId:string):SelectedEventRoute=>{
   current();
   const existing=eventRoutes.get(entryId);
   if(existing)return existing;
   const delivery=selectedHttp.event_deliveries.filter(row=>row.entry===entryId),
    inbox=selectedHttp.event_inboxes.filter(row=>row.entry===entryId),
    producers=delivery.length===1?selectedHttp.event_productions.filter(row=>row.event===delivery[0]!.event):[];
   if(delivery.length!==1||inbox.length!==1||producers.length!==1)
    throw new Error('one checked source producer, Event delivery and receiver inbox required');
   const selected=assembly!.openCrossServiceEvent(entryId),route=selected.relay.inspect().route;
   if(route.event_type!==delivery[0]!.event||route.outbox_entity!==producers[0]!.outbox||
    route.producer_service!==producers[0]!.service||route.consumer_inbox_entity!==inbox[0]!.inbox||
    route.receiver_service!==inbox[0]!.service||route.source_capture_sha256!==manifest.source_capture_sha256)
    throw new Error('original Event route differs from checked application composition');
   eventRoutes.set(entryId,selected);
   return selected;
  };
  const current=()=>{
   if(closed)throw new Error('Core Commerce service artifact owner closed');
   const now=assembly!.inspect();
   if(now.source_capture_sha256!==manifest.source_capture_sha256||now.family_sha256!==manifest.family_sha256||now.application!==manifest.application)
    throw new Error('Core Commerce source/profile selection changed');
   for(const service of services){
    // Assembly inspection rechecks every original store. The store metadata
    // was captured from these private store owners at construction.
    const physical=inventory(storeDirectories.get(service.id)!,true);
    if(JSON.stringify(physical)!==JSON.stringify(staticCoreCommerceServiceFiles(service.files)))
     throw new Error('Core Commerce service artifact changed');
   }
   if(JSON.stringify(inventory(artifacts))!==JSON.stringify([...manifest.files,{path:'manifest.json',sha256:digest(text(manifest)),bytes:Buffer.byteLength(text(manifest))}].sort((a,b)=>a.path.localeCompare(b.path))))
    throw new Error('Core Commerce graph/bridge artifact changed');
  };
  const owner:CoreCommerceServiceArtifactOwner=Object.freeze({
   inspect(){current();return manifest;},
   serviceStorage(id:string){current();const store=stores.get(id);if(!store)throw new Error('service absent from original application selection');return store;},
   selectHttpRoute(method:string,pathname:string){
    current();
    if(typeof method!=='string'||!method||typeof pathname!=='string'||!pathname.startsWith('/')||pathname.includes('?')||pathname.includes('#'))
     throw new Error('HTTP selector requires method and pathname');
    const matches=routes.map(route=>({route,parameters:routeParameters(route.path,pathname)})).filter(row=>row.parameters!==null);
    const selected=matches.find(row=>row.route.method===method);
    if(selected)return Object.freeze({kind:'matched' as const,route:selected.route,path_parameters:selected.parameters!});
    if(matches.length)return Object.freeze({kind:'method-not-allowed' as const,allow:Object.freeze([...new Set(matches.map(row=>row.route.method))].sort())});
    return Object.freeze({kind:'route-not-found' as const});
   },
   async openSelectedEntryAuth(native:CommerceAuthNativeOwnerV1){
    current();const selected=await assembly!.openSelectedEntryAuth(native);
    selectedEntryAuthOpened=true;current();return selected;
   },
   openDemoPayDispatch(port:DemoPayCommerceRawBytePortV1){current();return assembly!.openDemoPayDispatch(port);},
   openGeneratedOperation(invocation:CommerceOperationInvocationHandle){current();return assembly!.openGeneratedOperation(invocation);},
   openGeneratedQuery(invocation:CommerceOperationInvocationHandle){current();return assembly!.openGeneratedQuery(invocation);},
   openWorkflowIngress(workflowId:string){current();return assembly!.openWorkflowIngress(workflowId);},
   openOutboxRelay(workflowId:string){current();return assembly!.openOutboxRelay(workflowId);},
   openWorkflowClaimExecutor(workflowId:string){current();return assembly!.openWorkflowClaimExecutor(workflowId);},
   openWorkflowSnapshotQuery(workflowId:string){current();return assembly!.openWorkflowSnapshotQuery(workflowId);},
   openWorkflowContinuation(workflowId:string){current();return assembly!.openWorkflowContinuation(workflowId);},
   openWorkflowStepRunner(workflowId:string){current();return assembly!.openWorkflowStepRunner(workflowId);},
   openWorkflowLocalObservation(workflowId:string){current();return assembly!.openWorkflowLocalObservation(workflowId);},
   openWorkflowLocalObservationRunner(workflowId:string){current();return assembly!.openWorkflowLocalObservationRunner(workflowId);},
   openWorkflowPass(workflowId:string){current();return assembly!.openWorkflowPass(workflowId);},
   openCrossServiceEvent(entryId:string){return selectedEvent(entryId);},
   openSelectedEventPass(entryId:string){
    current();
    const existing=eventPasses.get(entryId);
    if(existing)return existing;
    if(!selectedEntryAuthOpened)
     throw new Error('selected Entry/Auth required before opening an Event pass');
    const selected=selectedEvent(entryId),delivery=selected.openDelivery(),
     route=selected.relay.inspect().route;
    const inspection=Object.freeze({entry:route.entry,event:route.event_type,
     outbox:route.outbox_entity,inbox:route.consumer_inbox_entity,
     producer_service:route.producer_service,receiver_service:route.receiver_service,
     source_capture_sha256:route.source_capture_sha256,
     qualification:'source-selected-in-process-event-delivery-and-publication' as const});
    const passCurrent=()=>{current();delivery.assertCurrent();selected.relay.assertCurrent();};
    const pass:CoreCommerceSelectedEventPass=Object.freeze({
     inspect(){passCurrent();return inspection;},
     inspectActorRequirement(){passCurrent();return delivery.inspectActorRequirement();},
     scanReady(cursor:string|null,limit:number){passCurrent();return selected.relay.scanReady(cursor,limit);},
     async runReady(occurrenceId:string,actor:CommerceAuthActorV1|null,signal?:AbortSignal){
      passCurrent();
      // A published outbox is no longer Ready. Reconcile its original producer
      // command and receiver inbox before attempting a new delivery.
      const recorded=await selected.reconcilePublished(occurrenceId);
      if(recorded.kind==='recorded')
       return Object.freeze({kind:'publication-result' as const,result:recorded});
      const ready=selected.relay.readReady(occurrenceId);
      if(ready.kind==='not-ready'){
       return Object.freeze({kind:'not-ready' as const,authority_effect:'none' as const});
      }
      const proof=selected.provenance.inspectRecorded(ready.occurrence),
       candidate=selected.publication.prepare(ready.occurrence);
      const received=await delivery.deliver(ready.occurrence,actor,signal);
      if(received.kind!=='receiver-committed')
       return Object.freeze({kind:'receiver-result' as const,result:received});
      const published=await selected.publish({candidate,proof,delivery,
       acknowledgement:received.acknowledgement});
      if(published.kind==='indeterminate'){
       const reconciled=selected.reconcile(published.attempt);
       return Object.freeze({kind:'publication-result' as const,result:reconciled});
      }
      return Object.freeze({kind:'publication-result' as const,result:published});
     },
     assertCurrent:passCurrent,
    });
    passCurrent();eventPasses.set(entryId,pass);return pass;
   },
   inspectWorkerActorRequirements(workflowId:string){current();return assembly!.inspectWorkerActorRequirements(workflowId);},
   async openSelectedHttpRuntime(native:CommerceAuthNativeOwnerV1){
    current();
    const selected=await assembly!.openSelectedEntryAuth(native);
    selectedEntryAuthOpened=true;
    let httpClosed=false;
    const httpCurrent=()=>{if(httpClosed)throw new Error('selected HTTP runtime closed');current();selected.auth.assertCurrent();selected.entries.assertCurrent();};
    const error=(code:string,allow?:string):Response=>{
     const status=selectedHttp.error_statuses[code];
     if(status===undefined)throw new Error('source HTTP error projection missing: '+code);
     return new Response(JSON.stringify({kind:'error',code}),{status,headers:{'content-type':'application/json; charset=utf-8',...(allow?{allow}:{})}});
    };
    const runtime:CoreCommerceSelectedHttpRuntime=Object.freeze({
     qualification:'source-selected-in-process-GET-Query-and-POST-Operation;generated-event-worker-runtime' as const,
     auth:selected.auth,service_actor_requirements:assembly!.inspectExternalQueryActorRequirements(),
     bindServiceActor(actor:CommerceAuthActorV1){httpCurrent();return assembly!.bindServiceActor(actor);},
     async handle(request:Request,actor:CommerceAuthActorV1|null){
      httpCurrent();if(!(request instanceof Request))throw new Error('Web Request required');
      const selection=owner.selectHttpRoute(request.method,new URL(request.url).pathname);
      if(selection.kind==='route-not-found')return error('route-not-found');
      if(selection.kind==='method-not-allowed')return error('method-not-allowed',selection.allow.join(', '));
      const {route,path_parameters}=selection;
      let sourceArguments:unknown=path_parameters;
      if(route.method==='GET'){
       if(request.body!==null||Number(request.headers.get('content-length')??'0')>0)return error('invalid-request');
      }else{
       if(!/^application\/json(?:;\s*charset=utf-8)?$/i.test(request.headers.get('content-type')??''))
        return error('unsupported-media-type');
       if(route.body_timeout_ms===null)throw new Error('selected POST body bound absent');
       const body=await readBoundedJson(request,route.request_bytes,route.body_timeout_ms);
       if(!body.ok)return error(body.code);
       sourceArguments=body.value;
      }
      const entry=selected.auth.bindEntry(route.entry);
      let invocation:CommerceOperationInvocationHandle|undefined;
      try{
       const definition=selected.auth.inspectEntry(entry);
       if(definition.service!==route.service||definition.access.permission!==route.permission||
         definition.access.auth_route_id!==route.auth_route_id)
        throw new Error('selected HTTP Entry permission differs from original source');
       let wire:Uint8Array;
       try{wire=selected.auth.encodeEntryArguments(entry,sourceArguments);}
       catch(problem){
        if(problem&&typeof problem==='object'&&(problem as {code?:unknown}).code==='InputRejected')return error('invalid-request');
        throw problem;
       }
       const started=await selected.entries.begin(actor,route.entry,wire,sourceArguments,request.signal);
       if(!started.ok)return error(started.code);
       invocation=started.invocation;
       let result:Readonly<Record<string,unknown>>;
       if(route.method==='GET')result=(await assembly!.openGeneratedQuery(invocation)).run();
       else{
        const operation=await assembly!.openGeneratedOperation(invocation);
        try{result=await operation.run(invocation);}
        finally{assembly!.releaseGeneratedOperation(invocation);}
       }
       if(route.method==='GET')invocation=undefined;
       if(result.kind!=='returned'){
        const code=result.code;
        if((result.kind==='rejected'||result.kind==='failed')&&typeof code==='string'&&
         selectedHttp.error_statuses[code]!==undefined)return error(code);
        return error('adapter-contract-defect');
       }
       let value=result.value;
       if(route.method==='GET'){
        if(!route.success_projection)throw new Error('selected GET success projection absent');
        try{value=projectCoreCommerceHttpGetSuccessValue(route.success_projection,result.value);}
        catch{return error('adapter-contract-defect');}
       }
       const body=JSON.stringify({kind:route.success_body_kind,value},(_key,value)=>typeof value==='bigint'?value.toString():value);
       if(Buffer.byteLength(body)>route.response_bytes)throw new Error('selected HTTP response exceeds source bound');
       httpCurrent();return new Response(body,{status:route.success_status,headers:{'content-type':'application/json; charset=utf-8'}});
      }finally{
       if(invocation)try{selected.entries.retire(invocation);}catch{}
       selected.auth.disposeEntry(entry);
      }
     },
     assertCurrent:httpCurrent,close(){httpClosed=true;},
    });
    httpCurrent();return runtime;
   },
   assertCurrent:current,
   close(){if(closed)return;closed=true;assembly!.close();},
  });
  current();return owner;
 }catch(error){assembly?.close();throw error;}
}
