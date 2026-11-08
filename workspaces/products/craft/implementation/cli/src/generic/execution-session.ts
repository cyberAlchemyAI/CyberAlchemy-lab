/** Private execution-account registry; exported opaque preparations are not accounts.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';
import {AsyncLocalStorage} from 'node:async_hooks';
import type * as T from './transaction-data-v1.js';
import type * as X from './external-read-data-v1.js';
import type * as W from './external-write-data-v1.js';
import type * as E from './event-data-v1.js';
import {createGenericExternalReadOwner} from './external-read-runtime.js';
import {buildDemoPayCaptureRequest,createDemoPayNativeWriteAdapter,demoPayAttemptKey} from './external-write-runtime.js';
import {mayAttestProviderNoEffect,providerEffectPossibleAfterObservation} from './provider-effect-evidence.js';
import {deriveGenericCausalIdentityData} from './external-write-identity.js';
import type {EffectInput,DefiniteExternalObservation} from './durable-write-intent-store.js';
import type {GenericCommittedEventIntent,GenericEventEnvelope} from './event-store.js';
import {createGenericEventRelayOwner,inspectGenericAckedWorkflowEvent,requireGenericEventRelayClaim,requireGenericEventRelayOwnerBinding,type GenericEventRelayOwner,type GenericEventRelayClaim} from './event-relay.js';
import {openOriginalV3PreAuthStoreIdentity,inspectOriginalV3PreAuthEpoch,assertOriginalV3PreAuthMetadataCurrentOnce,assertOriginalV3PreAuthPhysicalCurrent,closeOriginalV3PreAuthStoreIdentity} from './v3-preauth-store-identity.js';
import {createGenericOperationAssembly} from './operation-assembly.js';
import {createGenericTransactionOwner,assertGenericTransactionOwner,type GenericTransactionOwner,type GenericExecutionCommandGrant,type GenericMutationIntent,type GenericValidatedCommandResult,type GenericNewCommandPath,type GenericReplayPath} from './transaction-owner.js';
import path from 'node:path';import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {assertGenericRepositoryPlanOwner,type GenericRepositoryPlanOwner,type GenericApplicationPlanHandle,type GenericTransactionApplicationHandle,type GenericEntryPlanHandle,type GenericQueryPlanHandle,type GenericHttpEntryPlanHandle} from './repository-plan.js';
import type {GenericHttpEntryV1,GenericHttpResultV1,GenericHttpObservationV1} from './http-data-v1.js';
import {deriveGenericComputationEnvironment} from '../commerce/commerce-computation-environment.js';
import type {GenericComputationContractV1,GenericPureDeclarationV1} from './computation-data-v1.js';
import type {BinderV1,ValueTypeV1} from '../commerce/commerce-data-v1.js';
import type * as Q from './query-data-v1.js';
import {lowerOperationContract} from './pure-operation.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['repository-plan'+ext,'pure-call-owner'+ext,'pure-operation'+ext,'fixture-loader'+ext,'invocation-owner'+ext,'transaction-owner'+ext,'operation-assembly'+ext,'sqlite-repository'+ext,'../commerce/commerce-computation-evaluate'+ext,'../commerce/commerce-computation-kernel'+ext]);
const at={path:'generic-execution',start:0,end:0};
export interface GenericInternalExecutionToken{readonly kind:'private-generic-execution-token/v1-candidate'}
interface Role {selector:string;path:string;function_name:string;parameters:readonly BinderV1[];slots:readonly Q.GenericContextSlotV1[]}
const tokens=new WeakMap<object,{current:()=>void;plans:GenericRepositoryPlanOwner;application:GenericApplicationPlanHandle;entry:GenericEntryPlanHandle;inspection:{contract:GenericComputationContractV1;environment:ReturnType<typeof deriveGenericComputationEnvironment>;source_capture_sha256:string;contract_sha256:string};roles:readonly Role[];disposed:boolean}>();
type ExecutionProgram=Pick<NonNullable<ReturnType<typeof tokens.get>>,'inspection'|'roles'>;
// Immutable checked programs may be shared; invocation tokens, fuel, READY
// frames, reads, results and mutable machine state remain new for every call.
const executionPrograms=new WeakMap<object,WeakMap<object,ExecutionProgram>>();
// Only this module can open a synchronous lease. No lease spans Auth, SQLite,
// a fixture transaction or an await. The full physical owner chain is checked
// before and in finally, so neither results nor typed failures escape unchecked.
interface RuntimeLifetime {closed:boolean}
const tokenLifetimes=new WeakMap<object,RuntimeLifetime>();
const pureSegments=new WeakSet<object>(),retiredTokens=new WeakSet<object>();
const commandScopes=new AsyncLocalStorage<GenericInternalExecutionToken>();
function pureSegment<T>(token:GenericInternalExecutionToken,work:()=>T):T {
 const row=assertGenericInternalExecutionToken(token);
 if(pureSegments.has(token))return work();
 pureSegments.add(token);
 try{return work();}finally{pureSegments.delete(token);assertGenericInternalExecutionToken(token);}
}
/** Only the private constructor below mints this token; no public DTO/factory returns it. */
export function assertGenericInternalExecutionToken(token:GenericInternalExecutionToken){const r=token&&typeof token==='object'?tokens.get(token):undefined;if(!r)fail('ForeignOwner',at,'private original execution token required');if(r.disposed||retiredTokens.has(token)||tokenLifetimes.get(token)?.closed)fail('DisposedOwner',at,'execution token disposed');if(!pureSegments.has(token)&&commandScopes.getStore()!==token)r.current();return r;}
/** The store may use this only with its original READY frame at an effect boundary. */
export function assertGenericExecutionTokenBinding(token:GenericInternalExecutionToken,plans:GenericRepositoryPlanOwner,application:GenericApplicationPlanHandle,entry:GenericEntryPlanHandle):void{
 const row=assertGenericInternalExecutionToken(token);
 if(row.plans!==plans||row.application!==application||row.entry!==entry)fail('ForeignOwner',at,'external effect token belongs to another application or Entry');
 row.current();
}
export function genericCommandScopeContains(token:GenericInternalExecutionToken){return commandScopes.getStore()===token&&tokens.has(token)&&!retiredTokens.has(token)&&!tokenLifetimes.get(token)?.closed;}
function forceGenericInternalExecutionTokenCurrent(token:GenericInternalExecutionToken){const row=assertGenericInternalExecutionToken(token);row.current();}
function makeToken(plans:GenericRepositoryPlanOwner,application:GenericApplicationPlanHandle,entry:GenericEntryPlanHandle,parentCurrent:()=>void,lifetime:RuntimeLifetime){
 const current=()=>{parentCurrent();pin.assertCurrent();assertGenericRepositoryPlanOwner(plans);if(application.kind!=='original-generic-transaction-application/v1-candidate')plans.assertCurrent(application);plans.assertChild(entry,application);};current();const prior=executionPrograms.get(application)?.get(entry);if(prior){const token=Object.freeze({kind:'private-generic-execution-token/v1-candidate' as const});tokens.set(token,Object.freeze({current,plans,application,entry,...prior,disposed:false}));tokenLifetimes.set(token,lifetime);return token;}const original=plans.inspectSourceApplication(application),app=original.contract,selected=plans.inspectEntry(entry),functions:GenericPureDeclarationV1[]=[...app.functions],occupied=new Set(functions.map(f=>f.name)),roles:Role[]=[];let ordinal=0;
 const add=(selector:string,p:string,value:Q.GenericKeyedRoleExpressionV1,env:readonly BinderV1[],slots:readonly Q.GenericContextSlotV1[])=>{
  let id:string;do{id='Craft.Generated.Execution.Role'+ordinal++;}while(occupied.has(id));occupied.add(id);
  const used=slots.filter(s=>s.expression_path===p+'.expression'),parameters=[...env,...used.map(s=>({name:s.id,type:s.type}))];if(new Set(parameters.map(p=>p.name)).size!==parameters.length)fail('InvalidContract',at,'private role binding collides');
  functions.push({name:id,kind:'Calculation',pure:true,parameters,result:value.result,body:value.expression,preconditions:[],precondition_mode:'embedded-once-in-body',rounding:'reject',on_evaluation_error:null});roles.push({selector,path:p,function_name:id,parameters:env,slots:used});
 };
 const terminal=(selector:string,a:Q.GenericTerminalActionV1,p:string,env:readonly BinderV1[],slots:readonly Q.GenericContextSlotV1[])=>{if(a.kind==='return')add(selector,p+'.value',a.value,env,slots);};
 for(const q of app.queries){const env=q.parameters,row=[...env,{name:q.source.binding,type:{kind:'record',name:q.source.entity} as ValueTypeV1}];q.key.fields.forEach((f,i)=>add(q.query,'$.key.fields['+i+'].value',f.value,env,q.context_slots.map(s=>s.expression_path===f.predicate_path+'.expression'?{...s,expression_path:'$.key.fields['+i+'].value.expression'}:s)));add(q.query,'$.predicate',q.predicate,row,q.context_slots);q.guards.forEach((g,i)=>{add(q.query,'$.guards['+i+'].condition',g.condition,row,q.context_slots);terminal(q.query,g.on_false,'$.guards['+i+'].on_false',row,q.context_slots);});add(q.query,'$.projection',q.projection,row,q.context_slots);terminal(q.query,q.on_missing,'$.on_missing',env,q.context_slots);terminal(q.query,q.on_unavailable,'$.on_unavailable',env,q.context_slots);}
 const readonlySteps=(selector:string,rows:readonly Q.GenericReadonlyStepV1[],p:string,start:readonly BinderV1[],slots:readonly Q.GenericContextSlotV1[])=>{let env=[...start];rows.forEach((s,i)=>{const sp=p+'['+i+']';if(s.kind==='guard'){add(selector,sp+'.condition',s.condition,env,slots);terminal(selector,s.on_false,sp+'.on_false',env,slots);}else if(s.kind==='conditional'){add(selector,sp+'.condition',s.condition,env,slots);readonlySteps(selector,s.then,sp+'.then',env,slots);readonlySteps(selector,s.otherwise,sp+'.otherwise',env,slots);}else if(s.kind==='read-entry'){s.call.arguments.forEach((a,j)=>add(selector,sp+'.call.arguments['+j+'].value',a.value,env,slots));terminal(selector,s.on_missing,sp+'.on_missing',env,slots);terminal(selector,s.on_unavailable,sp+'.on_unavailable',env,slots);env.push({name:s.binding,type:s.type});}else if(s.action.kind==='invoke-return-local')s.action.call.arguments.forEach((a,j)=>add(selector,sp+'.action.call.arguments['+j+'].value',a.value,env,slots));else terminal(selector,s.action,sp+'.action',env,slots);});};
 for(const o of app.readonly_operations)readonlySteps(o.operation,o.body,'$.body',o.parameters,o.context_slots);
 if(application.kind==='original-generic-transaction-application/v1-candidate'){const assembly=createGenericOperationAssembly(plans,application),actual=plans.inspectSourceApplication(application).contract;if(!('stateful_operations' in actual))fail('InvalidContract',at,'actual transaction source required');for(const o of actual.stateful_operations){const h=assembly.bind(plans.bindStatefulOperation(application,o.operation)),inspection=assembly.inspectSource(h);for(const r of inspection.roles)add(o.operation,r.path,r.value,r.parameters,r.slots);assembly.dispose(h);}}
 const bool:ValueTypeV1={kind:'scalar',name:'Bool'};let contract:GenericComputationContractV1={schema_version:'craft.generic-computation/v1-candidate',semantics_revision:app.pure_semantics_revision,source_node:app.source_node,values:{...app.values,root:bool},inputs:selected.parameters,functions,result:bool,rounding:'reject',limits:app.limits,expression:{op:'literal',type:bool,value:true},invariant_policy:app.invariant_policy,record_layout:app.record_layout,equality_policy:app.equality_policy,append_policy:app.append_policy};
 // Reuse the actual original pure Operation lowering under this same account.
 for(const o of app.pure_operations){const id=o.operation.module+'.'+o.operation.name,lowered=lowerOperationContract({...contract,functions:[...functions]},o,app.pure_operations.map(p=>p.operation.module+'.'+p.operation.name)).contract;let fn:string;do{fn='Craft.Generated.Execution.Role'+ordinal++;}while(occupied.has(fn));occupied.add(fn);functions.push({name:fn,kind:'Calculation',pure:true,parameters:o.parameters,result:lowered.result,body:lowered.expression,preconditions:[],precondition_mode:'embedded-once-in-body',rounding:'reject',on_evaluation_error:null});roles.push({selector:id,path:'$.pure-operation',function_name:fn,parameters:o.parameters,slots:[]});contract={...contract,functions,values:{...contract.values,enums:lowered.values.enums}};}
 const environment=deriveGenericComputationEnvironment(contract),token=Object.freeze({kind:'private-generic-execution-token/v1-candidate' as const}),program=Object.freeze({inspection:coreFreeze({contract,environment,source_capture_sha256:original.source_capture_sha256,contract_sha256:dataDigest(contract)}),roles:coreFreeze(roles)});current();let programs=executionPrograms.get(application);if(!programs){programs=new WeakMap();executionPrograms.set(application,programs);}programs.set(entry,program);tokens.set(token,Object.freeze({current,plans,application,entry,...program,disposed:false}));tokenLifetimes.set(token,lifetime);return token;
}

// The runtime creates this grant immediately before its actual child observation.
// It never returns the token or grant to callers; the repository consumes it once.
const queryGrants=new WeakMap<object,{repository:object;authorization:object;frame:object;entry:GenericEntryPlanHandle;query:GenericQueryPlanHandle;key:Uint8Array}>();
export function consumeGenericExecutionQueryGrant(token:GenericInternalExecutionToken,repository:object,authorization:object,frame:object,entry:GenericEntryPlanHandle,query:GenericQueryPlanHandle):Uint8Array{assertGenericInternalExecutionToken(token);const r=queryGrants.get(token);if(!r||r.repository!==repository||r.authorization!==authorization||r.frame!==frame||r.entry!==entry||r.query!==query)fail('ForeignOwner',at,'exact private session/store/Query grant required');queryGrants.delete(token);return new Uint8Array(r.key);}
const fixtureGrants=new WeakMap<object,{repository:object;rows:readonly {entity:string;bindings:readonly (string|null|Uint8Array)[]}[]}>();
export function consumeGenericExecutionFixtureGrant(token:GenericInternalExecutionToken,repository:object){assertGenericInternalExecutionToken(token);const r=fixtureGrants.get(token);if(!r||r.repository!==repository)fail('ForeignOwner',at,'exact private one-use fixture grant required');fixtureGrants.delete(token);return r.rows;}

import {types as host} from 'node:util';
import {canonicalJson,type Json} from '../profile-engine/contracts.js';
import {requireGenericCompositionRuntime,requireGenericWorkflowRuntime,type GenericCompositionHandle} from './public-sdk.js';
import type {GenericWorkflowSourceContractV1} from './workflow-source.js';
import {createInternalGenericExecutionMachine} from '../commerce/commerce-computation-evaluate.js';
import {encodeSourceSqliteTypedTupleV1} from '../commerce/commerce-sqlite-generation-v1.js';
import {createGenericSqliteRepository,type GenericSqlObservation,GenericTransactionResourceError} from './sqlite-repository.js';
import {createGenericEntryAuthorizationOwner,type GenericFixtureActor,type GenericEntryAuthorization,type GenericReadyFrame} from './entry-authorization.js';
import type {CommerceAuthFixtureDatabaseV1} from '../commerce/commerce-auth-ready-bridge-v1.js';
import {captureGenericRuntimeOptions,captureGenericCommandMetadata,GenericCommandPreparationError} from './invocation-owner.js';
import type {GenericApplicationRuntime,GenericRuntimeOptions,GenericPreparedInput,GenericInvocationAuthorization,GenericInvocationTransfer,GenericPreparedCommand,GenericCommandAuthorization,GenericCommandTransfer,GenericTransactionApplicationRuntime} from './invocation-owner.js';
import type {ExpressionFailureV1} from '../commerce/commerce-data-v1.js';
import type {GenericStorageTable} from './value-codec.js';
type Machine=ReturnType<typeof createInternalGenericExecutionMachine>;
function createMachine(token:GenericInternalExecutionToken):Machine{try{return createInternalGenericExecutionMachine(token);}catch(error){retiredTokens.add(token);throw error;}}
type PreparedState='prepared'|'authorizing'|'authorized'|'consuming'|'transferred'|'retired';
interface Prepared {querySnapshot?:object;entry:GenericEntryPlanHandle;token:GenericInternalExecutionToken;machine:Machine;account:any;env:Record<string,any>;canonical:string;state:PreparedState;http?:{handle:GenericHttpEntryPlanHandle;descriptor:GenericHttpEntryV1;executing:boolean;used:boolean;result:GenericHttpResultV1|null};command?:{key:string;payload:Uint8Array;control:T.GenericStatefulControlV1|X.GenericExternalStatefulControlV1|W.GenericExternalWriteStatefulControlV1|E.GenericEventStatefulControlV1;reads:GenericSqlObservation[];intents:GenericMutationIntent[];events:GenericCommittedEventIntent[];delivery:GenericEventEnvelope|null;trace:T.GenericCommandPermissionTraceItemV1[];origins:Map<string,GenericSqlObservation>;lastObservation:GenericSqlObservation|null;lastOrigin:GenericSqlObservation|null;children:{entry:GenericEntryPlanHandle;canonical:string;trace:T.GenericCommandPermissionTraceItemV1}[];outcome:CommandOutcome|null;env:Record<string,any>;rootTuple?:T.GenericRootCommandTupleV1|E.GenericEventOperatorRootCommandTupleV2|E.GenericEventServiceRootCommandTupleV2;effectOccurrences?:Map<string,number>;totalEffectOccurrences?:number;providerEffectPossible?:boolean}}
function retirePrepared(p:Prepared){p.state='retired';retiredTokens.add(p.token);}
export type GenericEventDeliveryResult=Readonly<{kind:'committed'|'replayed';receipt:GenericEventReceiverCommitReceipt}|{kind:'denied'|'unavailable'}>;
const runtimes=new WeakMap<object,{current:()=>void;owner:unknown;handle:GenericCompositionHandle;service:string;plans:GenericRepositoryPlanOwner;application:GenericApplicationPlanHandle;store:ReturnType<typeof createGenericSqliteRepository>|null;authorization:ReturnType<typeof createGenericEntryAuthorizationOwner>;serviceCredentials:Map<string,GenericFixtureActor>;deliverEvent:(relay:GenericEventRelayOwner,claim:GenericEventRelayClaim)=>Promise<GenericEventDeliveryResult>;inspectCommittedEvent:(envelope:GenericEventEnvelope)=>Promise<{kind:'same';consumer_command_tuple_sha256:string}|{kind:'absent'|'collision'|'denied'|'unavailable'}>;prepareHttp:(route:GenericHttpEntryPlanHandle,wire:Uint8Array,metadata:T.GenericCommandMetadataV1|null)=>GenericPreparedInput|GenericPreparedCommand;executeHttp:(transfer:GenericInvocationTransfer|GenericCommandTransfer,route:GenericHttpEntryPlanHandle)=>Promise<GenericHttpResultV1>;querySnapshot:(prepared:GenericPreparedInput)=>object;fixtureUsed:boolean;firstEntry:()=>GenericEntryPlanHandle;native:GenericRuntimeOptions['nativeAuth'];lifetime:RuntimeLifetime}>();
export function assertGenericWorkflowRuntimeSource(runtime:GenericTransactionApplicationRuntime,source:GenericWorkflowSourceContractV1):void{
 const selected=runtime&&typeof runtime==='object'?runtimes.get(runtime):undefined;
 if(!selected||!source||source.schema_version!=='craft.generic-workflow-source/v1-candidate')fail('ForeignOwner',at,'original Workflow runtime and checked source required');
 selected.current();
 const original=requireGenericWorkflowRuntime(selected.owner,selected.handle);
 original.assertCurrent();
 const application=selected.plans.inspectSourceApplication(selected.application);
 if(source.service!==selected.service||source.source_capture_sha256!==application.source_capture_sha256||
   dataDigest(source)!==dataDigest(original.contract)||dataDigest(application.contract)!==dataDigest(original.baseApplication))
  fail('ForeignOwner',at,'Workflow source differs from original runtime and selected profile');
 selected.current();
}
/** Check an original receiver before a public driver opens its journal.
 * This does not dispatch, read business rows or manufacture a service actor. */
export function assertGenericWorkflowReceiverSource(producer:GenericTransactionApplicationRuntime,receiver:GenericTransactionApplicationRuntime,source:GenericWorkflowSourceContractV1):void{
 assertGenericWorkflowRuntimeSource(producer,source);
 const p=runtimes.get(producer),r=receiver&&typeof receiver==='object'?runtimes.get(receiver):undefined;
 if(!p||!r||p===r||p.plans!==r.plans||p.application!==r.application)
  fail('ForeignOwner',at,'original same-application distinct Workflow receiver required');
 r.current();
 const original=requireGenericWorkflowRuntime(p.owner,p.handle);
 const targets=source.steps.filter(step=>step.kind==='event-await').map(step=>
  original.baseApplication.event_bindings.find(binding=>binding.id===step.event_binding)?.target_service);
 if(!targets.length||targets.some(target=>!target||target!==r.service)||p.service===r.service)
  fail('ForeignOwner',at,'original Workflow receiver service differs from checked Event binding');
}
/** Reprove both sides of a delivery after a process restart. A journal row or
 * copied Event envelope never substitutes for the producer ACK and the
 * receiver's freshly authorized, exact inbox observation. */
export async function inspectGenericWorkflowEventDelivery(producer:GenericTransactionApplicationRuntime,receiver:GenericTransactionApplicationRuntime,source:GenericWorkflowSourceContractV1,bindingId:string,causalCommandTupleSha256:string):Promise<{kind:'acknowledged';occurrence_sha256:string;consumer_command_tuple_sha256:string}|{kind:'pending'|'collision'|'denied'|'unavailable'}>{
 assertGenericWorkflowRuntimeSource(producer,source);
 const p=runtimes.get(producer),r=runtimes.get(receiver);
 if(!p||!r||p===r||p.plans!==r.plans||p.application!==r.application||p.store===r.store)fail('ForeignOwner',at,'original distinct workflow producer and receiver required');
 r.current();
 const relay=producer.openEventRelay();
 try{
  const envelope=inspectGenericAckedWorkflowEvent(relay,bindingId,causalCommandTupleSha256);
  if(!envelope)return Object.freeze({kind:'pending'});
  if(envelope.target_service!==r.service)fail('ForeignOwner',at,'ACKed workflow Event targets another receiver');
  const inbox=await r.inspectCommittedEvent(envelope);
  p.current();r.current();
  if(inbox.kind==='same')return Object.freeze({kind:'acknowledged',occurrence_sha256:envelope.occurrence_sha256,consumer_command_tuple_sha256:inbox.consumer_command_tuple_sha256});
  if(inbox.kind==='collision')return Object.freeze({kind:'collision'});
  if(inbox.kind==='denied')return Object.freeze({kind:'denied'});
  return Object.freeze({kind:'unavailable'});
 }finally{relay.close();}
}
export interface GenericEventReceiverCommitReceipt {readonly kind:'original-generic-event-receiver-commit/v1-candidate'}
const eventReceipts=new WeakMap<object,{relay:GenericEventRelayOwner;claim:GenericEventRelayClaim;envelopeSha256:string;occurrenceSha256:string;consumerCommandTupleSha256:string;assertReceiverCurrent:()=>void;used:boolean}>();
function mintGenericEventReceiverCommitReceipt(relay:GenericEventRelayOwner,claim:GenericEventRelayClaim,envelope:GenericEventEnvelope,consumerCommandTupleSha256:string,assertReceiverCurrent:()=>void):GenericEventReceiverCommitReceipt{
 if(!/^[0-9a-f]{64}$/.test(consumerCommandTupleSha256))fail('InvalidContract',at,'original consumer command tuple required');
 assertReceiverCurrent();requireGenericEventRelayClaim(relay,claim);
 const receipt:GenericEventReceiverCommitReceipt=Object.freeze({kind:'original-generic-event-receiver-commit/v1-candidate'});
 eventReceipts.set(receipt,{relay,claim,envelopeSha256:envelope.envelope_sha256,occurrenceSha256:envelope.occurrence_sha256,consumerCommandTupleSha256,assertReceiverCurrent,used:false});
 return receipt;
}
/** Only the receiver's original post-COMMIT or current-inbox path may mint this.
 * ACK never accepts a caller-supplied boolean, DTO, or structural copy. */
export function requireGenericEventReceiverCommitReceipt(receipt:GenericEventReceiverCommitReceipt,relay:GenericEventRelayOwner,claim:GenericEventRelayClaim){
 const row=receipt&&typeof receipt==='object'?eventReceipts.get(receipt):undefined;
 if(!row||row.relay!==relay||row.claim!==claim||row.used)fail('ForeignOwner',at,'original receiver commit receipt required');
 row.assertReceiverCurrent();
 return Object.freeze({envelope_sha256:row.envelopeSha256,occurrence_sha256:row.occurrenceSha256,consumer_command_tuple_sha256:row.consumerCommandTupleSha256});
}
export function consumeGenericEventReceiverCommitReceipt(receipt:GenericEventReceiverCommitReceipt,relay:GenericEventRelayOwner,claim:GenericEventRelayClaim):void{
 const row=receipt&&typeof receipt==='object'?eventReceipts.get(receipt):undefined;
 if(!row||row.relay!==relay||row.claim!==claim||row.used)fail('ForeignOwner',at,'original receiver commit receipt required');
 row.used=true;
}
export async function deliverGenericEventToRuntime(relay:GenericEventRelayOwner,claim:GenericEventRelayClaim,receiver:GenericTransactionApplicationRuntime):Promise<GenericEventDeliveryResult>{
 const row=receiver&&typeof receiver==='object'?runtimes.get(receiver):undefined;
 if(!row)fail('ForeignOwner',at,'original receiver runtime required');
 row.current();requireGenericEventRelayClaim(relay,claim);
 return row.deliverEvent(relay,claim);
}
const resourceCodes=new Set(['ResourceLimit','IterationBound','IterationLimit','InputBound','OutputBound']);
const httpExpressionCodes=new Set(['ArithmeticOverflow','ArithmeticUnderflow','DivideByZero','InexactDivision','ResourceLimit','IterationBound','IterationLimit','InputType','InputBound','OutputBound','UnsupportedCapability','UnknownReference','InvalidContract','InvalidUnicode']);
const httpFaultCodes=new Set(['MalformedRequest','PayloadTooLarge','BodyTimeout','UnsupportedMediaType','RouteNotFound','MethodNotAllowed','InvalidCommandKey','InvalidInput','AuthenticationRequired','PermissionDenied','AuthorizationUnavailable','CommandPayloadConflict','CommandIdentityCollision','CommandCapacity','ReadConflict','RevisionExhausted','StorageUnavailable','StoredCommandInvalid','StorageDataInvalid','CommitIndeterminate','ExternalOutcomeUnknown','CommittedResultWithheld']);
function projectHttpResult(result:Q.GenericEntryResultV1|T.GenericCommandResultV1):GenericHttpResultV1{
 const observation:GenericHttpObservationV1='observation'in result?result.observation:{kind:result.ok?'read-completed':'read-failed'},fuel={operation_fuel_used:result.fuel_used,response_fuel_used:0,total_fuel_used:result.fuel_used},base={schema_version:'craft.generic-http-result/v1-candidate' as const,observation,fuel};
 if(result.ok)return result.outcome.kind==='Returned'?coreFreeze({...base,kind:'returned' as const,value:result.outcome.value}):coreFreeze({...base,kind:result.outcome.kind==='Rejected'?'rejected' as const:'failed' as const,code:result.outcome.code});
 const code=result.error.code,cause='cause_code'in result.error?result.error.cause_code:null;
 if(code==='CommittedResultWithheld')return coreFreeze({...base,kind:'fault',code,cause_code:cause}) as GenericHttpResultV1;
 if(httpExpressionCodes.has(code))return coreFreeze({...base,kind:'fault',code:'ExecutionFault',cause_code:code}) as GenericHttpResultV1;
 if(!httpFaultCodes.has(code))fail('InvalidContract',at,'unknown original HTTP execution fault');
 return coreFreeze({...base,kind:'fault',code,cause_code:null}) as GenericHttpResultV1;
}
class BoundaryFault extends Error{constructor(readonly error:Q.GenericAuthFaultV1|Q.GenericStorageFaultV1){super(error.code);}}
export class GenericInputPreparationError extends Error{constructor(readonly error:ExpressionFailureV1,readonly fuel_used:number){super(error.code);this.name='GenericInputPreparationError';}}
function canonicalInput(p:Prepared,parameters:readonly BinderV1[],captureRoot=false){const wire=Object.create(null),k=p.machine.kernel,s=k.site('$.inputs');for(const b of parameters)wire[b.name]=k.wire(p.env[b.name],b.type,p.account,s);const text=canonicalJson(wire),bytes=Buffer.byteLength(text);k.byteWork(p.account,s,bytes);if(bytes>p.machine.contract.limits.max_input_bytes)k.fail('InputBound',s);if(captureRoot&&p.command){if(p.command.payload.length)fail('ForeignOwner',at,'root command payload already captured');p.command.payload=Buffer.from(text);}return dataDigest(wire);}
function encodeRow(p:Prepared,table:GenericStorageTable,value:any){const k=p.machine.kernel,s=k.site('$.storage.'+table.entity),type:ValueTypeV1={kind:'record',name:table.entity};k.checkpoint(value,type,p.account,s);const wire=k.wire(value,type,p.account,s),text=canonicalJson(wire as Json),row=Buffer.from(text),limit=Math.min(p.machine.contract.limits.max_value_bytes,524288);if(row.length>limit)k.fail('OutputBound',s);k.byteWork(p.account,s,row.length);const cells:Record<string,string|null>=Object.create(null),bindings:(string|null|Uint8Array)[]=[];let dataBytes=0;
 for(const c of table.columns){const v=wire[c.name],cell=v===null?null:canonicalJson(v);cells[c.name]=cell;const physical=c.type.kind==='scalar'&&c.type.name==='UInt64'&&cell!==null?JSON.parse(cell):cell;dataBytes+=physical===null?0:Buffer.byteLength(physical);bindings.push(physical);}if(dataBytes>limit)k.fail('OutputBound',s);bindings.push(row);
 for(const fields of table.keys){let key:Buffer;try{key=encodeSourceSqliteTypedTupleV1(table.entity,fields.map(name=>{const cell=cells[name];if(cell===null||cell===undefined)k.fail('InputType',s);return {name,type:table.record.fields[name]!,cell:cell!};}),limit);}catch(error){if(error&&typeof error==='object'&&'code' in error&&error.code==='StorageBound')return k.fail('OutputBound',s);throw error;}k.byteWork(p.account,s,key.length);bindings.push(key);}return {cells,bindings};
}
function storageFailure(p:Prepared,q:Q.GenericKeyedQueryV1,cause:Q.GenericStorageFaultV1['cause']):never{throw new BoundaryFault({code:'StorageDataInvalid',site:{entity:q.source.entity,query:q.query,path:'$.storage'},cause});}
function decodeObservation(p:Prepared,q:Q.GenericKeyedQueryV1,raw:readonly Record<string,unknown>[],m:Q.GenericSqlMaterializationV1|T.GenericTransactionSqlMaterializationV1,table:GenericStorageTable|T.GenericTransactionStorageTableV1){const k=p.machine.kernel,s=k.site('$.storage.'+q.query),a=p.account;k.charge(a,s,1+raw.length*(3*m.columns.length+2));if(raw.length>1)storageFailure(p,q,{code:'Cardinality',path:s.p});if(!raw.length)return null;const row=raw[0]!,expected=[...m.columns.flatMap(c=>[c.type_alias,c.length_alias,c.payload_alias]),m.shape_alias,m.bound_alias];if(Object.keys(row).length!==expected.length||expected.some(x=>!Object.hasOwn(row,x)))storageFailure(p,q,{code:'PhysicalShape',path:s.p});const shape=row[m.shape_alias],bound=row[m.bound_alias];if(![0,1].includes(shape as number)||![0,1].includes(bound as number))storageFailure(p,q,{code:'PhysicalShape',path:s.p});
 for(const c of m.columns){const t=row[c.type_alias],n=row[c.length_alias];if(typeof t!=='string'||!Number.isSafeInteger(n)||Number(n)<0||(t==='null'?!c.nullable||n!==0:t!==c.representation))storageFailure(p,q,{code:'PhysicalShape',path:s.p});}if(shape!==1)storageFailure(p,q,{code:'PhysicalShape',path:s.p});if(bound!==1||m.columns.some(c=>Number(row[c.length_alias])>c.max_bytes))k.fail('InputBound',s);
 const cells:Record<string,unknown>=Object.create(null);for(const c of m.columns){const v=row[c.payload_alias],n=Number(row[c.length_alias]),actual=v===null?0:typeof v==='string'?Buffer.byteLength(v):v instanceof Uint8Array?v.byteLength:-1;if(actual!==n||(v===null?row[c.type_alias]!=='null':c.representation==='text'?typeof v!=='string':!(v instanceof Uint8Array)))storageFailure(p,q,{code:'PhysicalShape',path:s.p});k.byteWork(a,s,n);cells[c.sql_name]=v;}
 if(m.columns.filter(c=>c.role==='field').reduce((n,c)=>n+Number(row[c.length_alias]),0)>m.data_bytes_max||m.columns.reduce((n,c)=>n+Number(row[c.length_alias]),0)>m.aggregate_bytes_max)k.fail('InputBound',s);
 const wire=Object.create(null);for(const column of table.columns){const cell=cells[column.sql_name];try{wire[column.name]=cell===null?null:column.type.kind==='scalar'&&column.type.name==='UInt64'?cell:JSON.parse(cell as string);}catch{storageFailure(p,q,{code:'InputType',expression_path:s.p,index_path:[],call_path:[]});}}
 let value:any;try{value=k.decode(wire,{kind:'record',name:table.entity},a,s);}catch(error){const f=k.failure(error,a);if(resourceCodes.has(f.error.code))throw error;storageFailure(p,q,f.error);}
 const canonical=encodeRow(p,table,value),names=[...table.columns.map(c=>c.sql_name),table.row_column,...table.key_columns];for(let i=0;i<names.length;i++){const actual=cells[names[i]!],expected=canonical.bindings[i];if(expected instanceof Uint8Array?!(actual instanceof Uint8Array)||!Buffer.from(expected).equals(actual):actual!==expected)storageFailure(p,q,{code:'CanonicalMismatch',path:s.p});}return value;
}
type CommandOutcome={kind:'Returned';value:any}|{kind:'Rejected'|'Failed';code:string};
interface CommandContext{p:Prepared;owner:GenericTransactionOwner;repository:ReturnType<typeof createGenericSqliteRepository>;material:GenericExecutionCommandGrant['command'];phase:{kind:'initial'|'prepared'|'replay';path?:GenericNewCommandPath|GenericReplayPath}|null;active:{kind:'initial'|'prepared'|'replay';path?:GenericNewCommandPath|GenericReplayPath}|null;finish:()=>GenericValidatedCommandResult;replay:(bytes:Uint8Array)=>Q.GenericEntryOutcomeV1;finished:boolean;assertPhase:(force?:boolean)=>void;assertEffectCurrent:()=>void}
const commandContexts=new WeakMap<object,CommandContext>();
const commandContext=(token:GenericInternalExecutionToken,owner:GenericTransactionOwner)=>{const c=commandContexts.get(token);if(!c||c.owner!==owner||!c.p.command)fail('ForeignOwner',at,'actual original command action required');assertGenericInternalExecutionToken(token);return c;};
export function consumeGenericExecutionCommandGrant(token:GenericInternalExecutionToken,owner:GenericTransactionOwner,repository:ReturnType<typeof createGenericSqliteRepository>,kind:'initial'|'prepared'|'replay',path?:GenericNewCommandPath|GenericReplayPath):GenericExecutionCommandGrant{const c=commandContext(token,owner);c.assertPhase();if(c.repository!==repository||c.phase?.kind!==kind||c.phase.path!==path)fail('ForeignOwner',at,'exact one-use private command phase required');c.active=c.phase;c.phase=null;const q=c.p.command!;return Object.freeze({command:c.material,entry:c.p.entry,reads:Object.freeze([...q.reads]),intents:Object.freeze([...q.intents]),events:Object.freeze([...q.events]),delivery:q.delivery,trace:Object.freeze([...q.trace])});}
export function assertGenericExecutionCommandPhase(token:GenericInternalExecutionToken,owner:GenericTransactionOwner){const c=commandContext(token,owner);if(!c.active)fail('ForeignOwner',at,'actual active command phase required');c.assertPhase();}
/** Private original transaction/store boundary; no caller can mint its token. */
export function assertGenericExecutionCommandEffectBoundary(token:GenericInternalExecutionToken,owner:GenericTransactionOwner,repository:ReturnType<typeof createGenericSqliteRepository>){const c=commandContext(token,owner);if(!c.active||c.repository!==repository)fail('ForeignOwner',at,'original active command/store boundary required');c.assertEffectCurrent();}
export function finishGenericExecutionCommand(token:GenericInternalExecutionToken,owner:GenericTransactionOwner,path:GenericNewCommandPath):GenericValidatedCommandResult{const c=commandContext(token,owner);if(c.active?.kind!=='prepared'||c.active.path!==path||c.finished)fail('ForeignOwner',at,'original prepared continuation phase required');c.finished=true;return c.finish();}
export function decodeGenericExecutionReplay(token:GenericInternalExecutionToken,owner:GenericTransactionOwner,path:GenericReplayPath,bytes:Uint8Array):Q.GenericEntryOutcomeV1{const c=commandContext(token,owner);if(c.active?.kind!=='replay'||c.active.path!==path||c.finished)fail('ForeignOwner',at,'original replay decode phase required');c.finished=true;return c.replay(bytes);}
export function meterGenericExecutionCommandRecord(token:GenericInternalExecutionToken,owner:GenericTransactionOwner,bytes:number){const p=commandContext(token,owner).p;const k=p.machine.kernel,s=k.site('$.command.record');k.charge(p.account,s);k.byteWork(p.account,s,bytes);}
export function commandExecutionFuel(token:GenericInternalExecutionToken,owner:GenericTransactionOwner):number{return commandContext(token,owner).p.account.used;}
export function commandExecutionFault(token:GenericInternalExecutionToken,owner:GenericTransactionOwner,error:unknown):ExpressionFailureV1|Q.GenericAuthFaultV1|Q.GenericStorageFaultV1{const p=commandContext(token,owner).p;if(error instanceof BoundaryFault)return error.error;return p.machine.kernel.failure(error,p.account).error;}

export async function createGenericRuntimeSession(sdk:unknown,handle:GenericCompositionHandle,options:GenericRuntimeOptions):Promise<GenericApplicationRuntime|GenericTransactionApplicationRuntime>{
 options=captureGenericRuntimeOptions(options);const binding=requireGenericCompositionRuntime(sdk,handle),{plans,application}=binding;binding.assertCurrent();const app=plans.inspectSourceApplication(application).contract,selectedModule=app.services.find(s=>s.id===options.service)?.module,v4ServiceWrites=app.admission_mode==='event-handoff-entry'&&app.write_bindings.some(b=>b.interface_ref.slice(0,b.interface_ref.lastIndexOf('.'))===selectedModule),v3Reopen=(app.admission_mode==='external-write-entry'||v4ServiceWrites)&&options.mode==='reopen',preauth=v3Reopen?openOriginalV3PreAuthStoreIdentity(plans,application,options.storePath):null;
 let store!:ReturnType<typeof createGenericSqliteRepository>,storeView!:ReturnType<ReturnType<typeof createGenericSqliteRepository>['inspect']>,fullStore=!v3Reopen,preauthClosed=false;
 if(fullStore){store=createGenericSqliteRepository(plans,application,options);storeView=store.inspect();}
 const expectedEpoch=preauth?inspectOriginalV3PreAuthEpoch(preauth).store_epoch_sha256:storeView.store_epoch_sha256,authorization=createGenericEntryAuthorizationOwner(plans,application,options.nativeAuth,expectedEpoch),prepared=new WeakMap<object,Prepared>(),authorizations=new WeakMap<object,{prepared:GenericPreparedInput|GenericPreparedCommand;authorization:GenericEntryAuthorization;used:boolean}>(),transfers=new WeakMap<object,{prepared:GenericPreparedInput|GenericPreparedCommand;frame:GenericReadyFrame;used:boolean}>(),entryCache=new Map<string,GenericEntryPlanHandle>(),lifetime:RuntimeLifetime={closed:false};
 const provenNoProviderEffect=new WeakSet<object>();
 const current=()=>{if(lifetime.closed)fail('DisposedOwner',at,'runtime closed');binding.assertCurrent();if(fullStore)store.assertPhysicalCurrent();else if(preauth)assertOriginalV3PreAuthPhysicalCurrent(preauth);authorization.assertCurrent();};
 const effectCurrent=(token:GenericInternalExecutionToken)=>{forceGenericInternalExecutionTokenCurrent(token);binding.assertEffectCurrent?.();transaction?.assertCurrent();commandContexts.get(token)?.assertPhase(true);};
 const entry=(id:string)=>{current();let h=entryCache.get(id);if(!h){h=plans.bindEntry(application,id);if(plans.inspectEntry(h).service!==options.service)fail('ForeignOwner',at,'entry belongs to another service');entryCache.set(id,h);}return h;};
 const state=(h:GenericPreparedInput|GenericPreparedCommand)=>{const p=h&&typeof h==='object'?prepared.get(h):undefined;if(!p)fail('ForeignOwner',at,'original prepared input required');current();return p;};
 const runRole=(p:Prepared,selector:string,path:string,env:Record<string,any>,frame:GenericReadyFrame,e:GenericEntryPlanHandle)=>{if(p.command){if(!genericCommandScopeContains(p.token))authorization.assertFrame(frame,e);return pureSegment(p.token,()=>{const r=assertGenericInternalExecutionToken(p.token).roles.find(r=>r.selector===selector&&r.path===path);if(!r)fail('InvalidContract',at,'actual checked role expression absent');return p.machine.runRole(r.function_name,env,p.account,(name,a,s)=>{const slot=r.slots.find(x=>x.id===name);if(!slot)return {found:false,value:undefined};const value=authorization.scalar(frame,e,slot);return {found:true,value:p.machine.kernel.checkpoint(value,slot.type,a,s)};},[selector]);});}current();authorization.assertFrame(frame,e);const r=assertGenericInternalExecutionToken(p.token).roles.find(r=>r.selector===selector&&r.path===path);if(!r)fail('InvalidContract',at,'actual checked role expression absent');return pureSegment(p.token,()=>p.machine.runRole(r.function_name,env,p.account,(name,a,s)=>{const slot=r.slots.find(x=>x.id===name);if(!slot)return {found:false,value:undefined};const value=authorization.scalar(frame,e,slot);return {found:true,value:p.machine.kernel.checkpoint(value,slot.type,a,s)};},[selector]));};
 type Outcome={kind:'Returned';value:any}|{kind:'Rejected'|'Failed';code:string;unavailable?:boolean};
 const terminal=(p:Prepared,selector:string,action:Q.GenericTerminalActionV1,path:string,env:Record<string,any>,frame:GenericReadyFrame,e:GenericEntryPlanHandle,unavailable=false):Outcome=>action.kind==='return'?{kind:'Returned',value:runRole(p,selector,path+'.value',env,frame,e)}:{kind:action.kind==='reject'?'Rejected':'Failed',code:action.code,...(unavailable&&action.kind==='fail'?{unavailable:true}:{})};
 const args=(p:Prepared,selector:string,items:readonly Q.GenericCallArgumentV1[],path:string,env:Record<string,any>,frame:GenericReadyFrame,e:GenericEntryPlanHandle,target:readonly BinderV1[])=>{const out=Object.create(null);for(const [i,item]of items.entries()){const t=target.find(t=>t.name===item.parameter);if(!t)fail('InvalidContract',at,'actual target parameter absent');out[item.parameter]=p.machine.kernel.checkpoint(runRole(p,selector,path+'['+i+'].value',env,frame,e),t.type,p.account,p.machine.kernel.site(path+'['+i+']'));}return out;};
 const query=async(p:Prepared,q:Q.GenericKeyedQueryV1,env:Record<string,any>,frame:GenericReadyFrame,e:GenericEntryPlanHandle):Promise<Outcome>=>{
  const k=p.machine.kernel,s=k.site('$.key.'+q.query),fields=q.key.fields.map((f,i)=>{const value=k.checkpoint(runRole(p,q.query,'$.key.fields['+i+'].value',env,frame,e),f.type,p.account,s);return {name:f.field,type:f.type,cell:canonicalJson(k.wire(value,f.type,p.account,s))};});let key:Buffer;try{key=encodeSourceSqliteTypedTupleV1(q.source.entity,fields,Math.min(app.limits.max_value_bytes,524288));}catch(error){if(error&&typeof error==='object'&&'code' in error&&error.code==='StorageBound')return k.fail('InputBound',s);throw error;}k.byteWork(p.account,s,key.length);k.charge(p.account,s);const qh=plans.bindQuery(application,q.query);queryGrants.set(p.token,{repository:store,authorization,frame,entry:e,query:qh,key});const observation=store.observe(p.token,qh,authorization,frame,e),observed=store.consumeObservation(p.token,observation,qh);if(!p.command&&!observed.unavailable)p.querySnapshot=store.captureQueryCapabilitySnapshot(observation);if(p.command){if(p.command.reads.length>=p.command.control.transaction.transaction_bounds.max_read_observations)p.machine.kernel.fail('ResourceLimit',p.machine.kernel.site('$.reads'));if(observed.witness)p.command.reads.push(observed.witness);p.command.lastObservation=observed.witness;p.command.lastOrigin=null;}if(observed.unavailable)return terminal(p,q.query,q.on_unavailable,'$.on_unavailable',env,frame,e,true);const table=storeView.storage.tables.find(t=>t.entity===q.source.entity)!;const row=pureSegment(p.token,()=>decodeObservation(p,q,observed.rows!,observed.materialization,table));if(row===null)return terminal(p,q.query,q.on_missing,'$.on_missing',env,frame,e);const locals=Object.assign(Object.create(null),env,{[q.source.binding]:row});if(runRole(p,q.query,'$.predicate',locals,frame,e)!==true)return terminal(p,q.query,q.on_missing,'$.on_missing',env,frame,e);for(const [i,g]of q.guards.entries())if(runRole(p,q.query,'$.guards['+i+'].condition',locals,frame,e)!==true)return terminal(p,q.query,g.on_false,'$.guards['+i+'].on_false',locals,frame,e);const value=runRole(p,q.query,'$.projection',locals,frame,e);if(p.command)p.command.lastOrigin=observed.witness;return {kind:'Returned',value};
 };
 const operation=async(p:Prepared,selector:string,steps:readonly Q.GenericReadonlyStepV1[],path:string,env:Record<string,any>,frame:GenericReadyFrame,e:GenericEntryPlanHandle):Promise<Outcome|null>=>{let locals=Object.assign(Object.create(null),env);for(const [i,step]of steps.entries()){const sp=path+'['+i+']';p.machine.kernel.charge(p.account,p.machine.kernel.site(sp));if(step.kind==='guard'){if(runRole(p,selector,sp+'.condition',locals,frame,e)!==true)return terminal(p,selector,step.on_false,sp+'.on_false',locals,frame,e);}else if(step.kind==='conditional'){const branch=runRole(p,selector,sp+'.condition',locals,frame,e)===true?'then':'otherwise',out=await operation(p,selector,step[branch],sp+'.'+branch,locals,frame,e);if(out)return out;}else if(step.kind==='read-entry'){
   const child=entry(step.call.entry),target=plans.inspectEntry(child),q=app.queries.find(q=>q.query===step.call.query)!;const childEnv=args(p,selector,step.call.arguments,sp+'.call.arguments',locals,frame,e,target.parameters),oldEnv=p.env;p.env=childEnv;let canonical:string;try{canonical=canonicalInput(p,target.parameters);}finally{p.env=oldEnv;}const a=await authorization.authorize(authorization.actorForFrame(frame,e),child,canonical,'child-auth');try{current();assertGenericInternalExecutionToken(p.token);}catch(error){if(a.ok)authorization.retireAuthorization(a.value);throw error;}if(!a.ok)throw new BoundaryFault(a.error);const f=await authorization.consume(a.value);try{current();assertGenericInternalExecutionToken(p.token);}catch(error){if(f.ok)authorization.retire(f.value);throw error;}if(!f.ok)throw new BoundaryFault(f.error);let out:Outcome;try{out=await query(p,q,childEnv,f.value,child);}finally{authorization.retire(f.value);}if(out.kind==='Returned'){if(!out.value||!['some','none'].includes(out.value.kind))p.machine.kernel.fail('InputType',p.machine.kernel.site(sp));if(out.value.kind==='none')return terminal(p,selector,step.on_missing,sp+'.on_missing',locals,frame,e);locals[step.binding]=p.machine.kernel.checkpoint(out.value.value,step.type,p.account,p.machine.kernel.site(sp));}else if(out.kind==='Failed'&&out.unavailable)return terminal(p,selector,step.on_unavailable,sp+'.on_unavailable',locals,frame,e);else return out;
  }else if(step.action.kind==='invoke-return-local'){const call=step.action.call,target=app.pure_operations.find(o=>o.operation.module+'.'+o.operation.name===call.target);if(!target||dataDigest(target)!==step.action.call.target_contract_sha256)fail('InvalidContract',at,'actual local Operation dependency differs');const callEnv=args(p,selector,step.action.call.arguments,sp+'.action.call.arguments',locals,frame,e,target.parameters);const outcome=runRole(p,call.target,'$.pure-operation',callEnv,frame,e);return outcome.kind==='Returned'?{kind:'Returned',value:outcome.fields.value}:{kind:outcome.kind,code:outcome.fields.code};}else return terminal(p,selector,step.action,sp+'.action',locals,frame,e);}return null;};
 const atomicApplication=app.admission_mode==='atomic-state-entry'||app.admission_mode==='external-read-entry'||app.admission_mode==='external-write-entry'||app.admission_mode==='event-handoff-entry'?application:null;
 if(atomicApplication&&atomicApplication.kind!=='original-generic-transaction-application/v1-candidate')fail('ForeignOwner',at,'actual atomic application handle required');
 let transaction=fullStore&&atomicApplication&&atomicApplication.kind==='original-generic-transaction-application/v1-candidate'?createGenericTransactionOwner(plans,atomicApplication,store,authorization):null;
 const ensureStoreAfterRootReady=(frame:GenericReadyFrame,p:Prepared)=>{
  if(fullStore)return;
  if(!preauth||!atomicApplication||atomicApplication.kind!=='original-generic-transaction-application/v1-candidate')fail('ForeignOwner',at,'original V3 root and pre-Auth store required');
  plans.assertChild(p.entry,application);
  authorization.assertFrame(frame,p.entry,p.canonical);
  let opened:ReturnType<typeof createGenericSqliteRepository>|undefined;
  try{
   assertOriginalV3PreAuthMetadataCurrentOnce(preauth);assertOriginalV3PreAuthPhysicalCurrent(preauth);
   opened=createGenericSqliteRepository(plans,application,options);const view=opened.inspect();
   if(view.store_epoch_sha256!==expectedEpoch)fail('StaleOwner',at,'reopened full store differs from pre-Auth identity');
   const resumed=createGenericTransactionOwner(plans,atomicApplication,opened,authorization);
   closeOriginalV3PreAuthStoreIdentity(preauth);preauthClosed=true;
   store=opened;storeView=view;transaction=resumed;fullStore=true;
   const registered=runtimes.get(runtime);if(registered)registered.store=store;
  }catch(error){if(opened&&!fullStore)try{opened.close();}catch{}if(!preauthClosed){try{closeOriginalV3PreAuthStoreIdentity(preauth);}finally{preauthClosed=true;}}throw error;}
 };
 const external=(app.admission_mode==='external-read-entry'||app.admission_mode==='external-write-entry'||app.admission_mode==='event-handoff-entry'&&app.external_bindings.length>0)&&atomicApplication?.kind==='original-generic-transaction-application/v1-candidate'?createGenericExternalReadOwner(plans,atomicApplication):undefined;
 const writeAdapter=(app.admission_mode==='external-write-entry'||app.admission_mode==='event-handoff-entry'&&app.write_bindings.length>0)&&options.externalWritePort?createDemoPayNativeWriteAdapter({protocol_id:'DemoPay-v1'},options.externalWritePort):undefined;
 const sourceFailure=(action:T.GenericTransactionSourceFailureV1):CommandOutcome=>({kind:action.kind==='reject'?'Rejected':'Failed',code:action.code});
 type SourcePrefix=readonly (readonly [string,string|number])[];
 const freshFrame=async(p:Prepared,actor:GenericFixtureActor,e:GenericEntryPlanHandle,canonical:string)=>{
  current();assertGenericInternalExecutionToken(p.token);const auth=await authorization.authorize(actor,e,canonical,'child-auth');
  try{current();assertGenericInternalExecutionToken(p.token);}catch(error){if(auth.ok)authorization.retireAuthorization(auth.value);throw error;}
  if(!auth.ok)throw new BoundaryFault(auth.error);const frame=await authorization.consume(auth.value);
  try{current();assertGenericInternalExecutionToken(p.token);}catch(error){if(frame.ok)authorization.retire(frame.value);throw error;}
  if(!frame.ok)throw new BoundaryFault(frame.error);return frame.value;
 };
 const preflight=async(p:Prepared,rows:readonly (X.GenericExternalPreflightStepV1|W.GenericExternalWritePreflightStepV1)[],prefix:SourcePrefix,env:Record<string,any>,frame:GenericReadyFrame):Promise<CommandOutcome|null>=>{
  const c=p.command!,selector=c.control.operation,k=p.machine.kernel;
  for(const [i,step]of rows.entries()){
   const sp='$.preflight'+JSON.stringify([...prefix,i]);k.charge(p.account,k.site(sp));
   if(step.kind==='source-failure'){
    if((app.admission_mode!=='external-read-entry'&&app.admission_mode!=='external-write-entry'&&app.admission_mode!=='event-handoff-entry')||!['craft.generic-stateful-control/v2-candidate','craft.generic-stateful-control/v3-candidate','craft.generic-stateful-control/v4-candidate'].includes(c.control.schema_version)||!prefix.length||i!==rows.length-1)fail('InvalidContract',at,'source failure requires actual external terminal branch');
    return pureSegment(p.token,()=>{if(!genericCommandScopeContains(p.token))authorization.assertFrame(frame,p.entry);return sourceFailure(step.action);});
   }else if(step.kind==='enforce-policy'){
    // runRole uses the original checked role and shared invocation account. A
    // kernel/decode/currentness fault propagates unchanged, never as a denial.
    const decision=runRole(p,selector,sp+'.value',env,frame,p.entry);
    if(decision.kind==='Allow')continue;
    if(decision.kind!=='Reject')k.fail('InputType',k.site(sp));
    let code:string|undefined;
    for(const item of step.rejections){k.charge(p.account,k.site(sp+'.reason'));if(item.variant===decision.fields.reason){code=item.code;break;}}
    if(code===undefined)return k.fail('InputType',k.site(sp+'.reason'));
    return sourceFailure({kind:'reject',code});
   }else if(step.kind==='guard'){if(runRole(p,selector,sp+'.condition',env,frame,p.entry)!==true)return sourceFailure(step.on_false);}
   else if(step.kind==='conditional'){const arm=runRole(p,selector,sp+'.condition',env,frame,p.entry)===true?'then':'otherwise';const out=await preflight(p,step[arm],[...prefix,['conditional',i],[arm==='then'?'then':'else',0]],Object.assign(Object.create(null),env),frame);if(out)return out;}
   else if(step.kind==='call-pure-local'){
    const target=app.pure_operations.find(o=>o.operation.module+'.'+o.operation.name===step.target);if(!target||dataDigest(target)!==step.target_contract_sha256)fail('InvalidContract',at,'actual pure callee differs');
    const locals=args(p,selector,step.arguments,sp+'.arguments',env,frame,p.entry,target.parameters),out=runRole(p,step.target,'$.pure-operation',locals,frame,p.entry);
    if(out.kind!=='Returned')return {kind:out.kind,code:out.fields.code};env[step.binding]=k.checkpoint(out.fields.value,step.result,p.account,k.site(sp));
   }else if(step.kind==='read-external'){
    if(!external||(app.admission_mode!=='external-read-entry'&&app.admission_mode!=='external-write-entry'&&app.admission_mode!=='event-handoff-entry'))fail('UnsupportedCapability',at,'actual original external owner required');
    const binding=app.external_bindings.find(b=>b.id===step.call.binding_ref);
    if(!binding||dataDigest(binding)!==step.call.binding_sha256||binding.binding_semantics_sha256!==step.call.binding_semantics_sha256)fail('InvalidContract',at,'actual checked external binding differs');
    const request=Object.create(null);for(const [j,a]of step.call.arguments.entries())request[a.parameter]=runRole(p,selector,sp+'.arguments['+j+'].value',env,frame,p.entry);
    const invoke=(name:string,values:Record<string,any>)=>{if(!genericCommandScopeContains(p.token))authorization.assertFrame(frame,p.entry);return pureSegment(p.token,()=>p.machine.runRole(name,values,p.account,()=>({found:false,value:undefined}),[selector,name]));};
    const wireRequest=invoke(binding.request_mapping.name,{request:k.checkpoint(request,binding.request_type,p.account,k.site(sp+'.request'))}),wire=k.wire(wireRequest,binding.wire_request_type,p.account,k.site(sp+'.wire-request'));
    effectCurrent(p.token);
    const observation=await external.read(p.token,selector,step,wire,(raw,mark,deadline)=>{
     authorization.assertFrame(frame,p.entry);return pureSegment(p.token,()=>{let response:any;try{response=k.decode(raw,binding.wire_response_type,p.account,k.site(sp+'.wire-response'));}catch(error){const fault=k.failure(error,p.account);if(['InputType','InputBound','InvalidUnicode'].includes(fault.error.code))return {kind:'malformed'};throw error;}
      mark('checked-decode');deadline();const valid=invoke(binding.response_validation_rule.name,{request:wireRequest,response});mark('validation-rule');if(valid!==true)return {kind:'malformed'};
      const mapped=invoke(binding.response_mapping.name,{response}),value=k.checkpoint(mapped,binding.result_type,p.account,k.site(sp+'.logical-result'));mark('response-mapping');deadline();return {kind:'value',value};});
    },dataDigest({entry:plans.inspectEntry(p.entry).entry,command:p.command?.key??p.canonical}));
    const observed=external.consume<any>(p.token,observation,()=>{effectCurrent(p.token);assertGenericInternalExecutionToken(p.token);});
    if(observed.kind==='value')env[step.binding]=observed.value;else if(observed.kind==='unavailable')return terminal(p,selector,step.on_unavailable,sp+'.on_unavailable',env,frame,p.entry);else return terminal(p,selector,step.on_malformed,sp+'.on_malformed',env,frame,p.entry);
   }else if(step.kind==='write-external'){
    if((app.admission_mode!=='external-write-entry'&&app.admission_mode!=='event-handoff-entry')||!writeAdapter||!c.rootTuple||app.admission_mode==='external-write-entry'&&c.rootTuple.principal.kind!=='customer'||!c.effectOccurrences||!app.identity_limits)fail('UnsupportedCapability',at,'selected original durable external write owner required');
    const binding=app.write_bindings.find(b=>b.id===step.call.binding_ref);
    if(!binding||binding.protocol_id!=='DemoPay-v1'||dataDigest(binding)!==step.call.binding_sha256||binding.interface_ref!==step.call.interface_ref||binding.write_operation_ref!==step.call.contract_operation_ref||step.call.authored_site.operation!==selector||step.call.authored_site.binding!==step.binding)fail('InvalidContract',at,'actual source-bound write call differs');
    const invokeSelected=(name:string,values:readonly unknown[])=>{const declaration=app.functions.find(f=>f.name===name);if(!declaration||declaration.parameters.length!==values.length)fail('InvalidContract',at,'actual selected pure continuation absent');const environment=Object.create(null);declaration.parameters.forEach((parameter,index)=>environment[parameter.name]=values[index]);authorization.assertFrame(frame,p.entry);return pureSegment(p.token,()=>p.machine.runRole(name,environment,p.account,()=>({found:false,value:undefined}),[selector,name]));};
    const request=Object.create(null);for(const [j,a]of step.call.arguments.entries())request[a.parameter]=runRole(p,selector,sp+'.arguments['+j+'].value',env,frame,p.entry);
    const logical=k.checkpoint(request,binding.request_type,p.account,k.site(sp+'.request'));
    const mapped=k.checkpoint(invokeSelected(binding.request_mapping_ref,[logical]),binding.wire_request_type,p.account,k.site(sp+'.mapped-request'));
    const physical=k.wire(mapped,binding.wire_request_type,p.account,k.site(sp+'.wire-request'));
    if(!physical||typeof physical!=='object'||Array.isArray(physical)||Object.keys(physical).sort().join(',')!=='amountMinor,currency,orderId'||typeof physical.orderId!=='string'||typeof physical.amountMinor!=='string'||physical.currency!=='USD')fail('InvalidContract',at,'selected DemoPay request carrier differs');
    const key=step.call.source_callsite,ordinal=c.effectOccurrences.get(key)??0;
    if(ordinal>=app.identity_limits.max_site_occurrences||(c.totalEffectOccurrences??0)>=app.identity_limits.max_total_occurrences)k.fail('ResourceLimit',k.site(sp));
    c.effectOccurrences.set(key,ordinal+1);c.totalEffectOccurrences=(c.totalEffectOccurrences??0)+1;
    const effect:W.GenericExternalEffectTupleV1|E.GenericEventExternalEffectTupleV2=c.rootTuple.schema_version==='craft.generic-root-command/v2-candidate'?{schema_version:'craft.generic-external-effect/v2-candidate',parent:c.rootTuple,site:step.call.authored_site,local_calls:[],interface_ref:binding.interface_ref,contract_operation_ref:binding.write_operation_ref,ordinal}:{schema_version:'craft.generic-external-effect/v1-candidate',parent:c.rootTuple,site:step.call.authored_site,local_calls:[],interface_ref:binding.interface_ref,contract_operation_ref:binding.write_operation_ref,ordinal};
    const identity=deriveGenericCausalIdentityData(effect,app.identity_limits),payload_canonical_json=canonicalJson(k.wire(logical,binding.request_type,p.account,k.site(sp+'.payload')) as Json),binding_canonical_json=canonicalJson(binding as unknown as Json);
    const input:EffectInput=Object.freeze({effect_canonical_json:identity.canonical_json,effect_sha256:identity.sha256,payload_canonical_json,payload_sha256:createHash('sha256').update(payload_canonical_json).digest('hex'),binding_canonical_json,binding_sha256:createHash('sha256').update(binding_canonical_json).digest('hex'),request_bytes:buildDemoPayCaptureRequest(identity.sha256,physical.orderId,physical.amountMinor,'USD')});
    // From this point the provider may have seen the request. Only a checked
    // definitive decline can discharge this possibility for this call.
    const earlierProviderEffect=c.providerEffectPossible===true;
    c.providerEffectPossible=true;
    effectCurrent(p.token);authorization.assertFrame(frame,p.entry);
    const prepared=store.prepareExternalWriteIntent(p.token,authorization,frame,p.entry,input);
    let observation:DefiniteExternalObservation|null=prepared.kind==='observed'?store.readExternalWriteObserved(p.token,authorization,frame,p.entry,input):null;
    if(!observation){
     if(prepared.kind==='inspect-required'){
      const inspectMapped=k.checkpoint(invokeSelected(binding.inspect_request_mapping_ref,[logical]),binding.wire_request_type,p.account,k.site(sp+'.inspect-request'));
      if(canonicalJson(k.wire(inspectMapped,binding.wire_request_type,p.account,k.site(sp+'.inspect-wire')) as Json)!==canonicalJson(physical as Json))fail('InvalidContract',at,'selected inspect request differs from original capture');
     }
     const nativePort=store.externalWritePort(p.token,authorization,frame,p.entry);
     let native=prepared.kind==='new'?await writeAdapter.capture(nativePort,store.retireExternalWriteDispatch(p.token,authorization,frame,p.entry,prepared.dispatch),input):await writeAdapter.inspect(nativePort,input);
     effectCurrent(p.token);authorization.assertFrame(frame,p.entry);
     if(prepared.kind==='inspect-required'&&prepared.state==='prepared'&&options.mode==='reopen'&&native.kind==='unknown'&&native.reason==='unknown-key'){
      const recovered=store.recoverExternalWriteIntent(p.token,authorization,frame,p.entry,input.effect_sha256),original=store.readRecoveredExternalWriteInput(p.token,authorization,frame,p.entry,recovered);
      if(original.effect_canonical_json!==input.effect_canonical_json||original.payload_canonical_json!==input.payload_canonical_json||original.binding_canonical_json!==input.binding_canonical_json||!Buffer.from(original.request_bytes).equals(input.request_bytes))fail('InvalidContract',at,'recovered prepared request differs from original source');
      const custody=store.retireRecoveredExternalWritePrepared(p.token,authorization,frame,p.entry,recovered);
      native=await writeAdapter.capture(nativePort,custody,original);
      effectCurrent(p.token);authorization.assertFrame(frame,p.entry);
     }
     if(native.kind==='observed'&&native.matches_request&&native.checked){
      store.recordExternalWriteObservation(p.token,authorization,frame,p.entry,input,native.checked);
      observation=store.readExternalWriteObserved(p.token,authorization,frame,p.entry,input);
     }else{
      const state=store.inspectExternalWriteIntent(p.token,authorization,frame,p.entry,input);
      if(state&&state.state!=='prepared'&&state.state!=='observed')store.retainExternalWriteUnknown(p.token,authorization,frame,p.entry,input);
      throw new GenericTransactionResourceError('ExternalOutcomeUnknown');
     }
    }
    if(!observation)throw new GenericTransactionResourceError('ExternalOutcomeUnknown');
    c.providerEffectPossible=providerEffectPossibleAfterObservation(earlierProviderEffect,observation.kind);
    const raw={attemptKey:demoPayAttemptKey(identity.sha256),orderId:physical.orderId,amountMinor:physical.amountMinor,currency:'USD',status:observation.kind,providerReference:observation.providerReference};
    const response=k.decode(raw,binding.wire_result_type,p.account,k.site(sp+'.wire-result'));
    if(invokeSelected(binding.response_validation_rule_ref,[mapped,response])!==true){const handler=step.handlers.find(h=>h.channel==='on-invalid-response');if(!handler)fail('InvalidContract',at,'source invalid-response handler required');return sourceFailure(handler.action);}
    env[step.binding]=k.checkpoint(invokeSelected(binding.response_mapping_ref,[response]),binding.result_type,p.account,k.site(sp+'.result'));
   }else if(step.kind==='read-entry'){
    const child=entry(step.call.entry),target=plans.inspectEntry(child),q=app.queries.find(q=>q.query===step.call.query);if(!q||target.target!==q.query)fail('InvalidContract',at,'actual protected child Query absent');
    const childEnv=args(p,selector,step.call.arguments,sp+'.arguments',env,frame,p.entry,target.parameters),old=p.env;let canonical:string;try{p.env=childEnv;canonical=canonicalInput(p,target.parameters);}finally{p.env=old;}
    const childFrame=await freshFrame(p,authorization.actorForFrame(frame,p.entry),child,canonical);let out:Outcome;
    try{
     if(c.trace.length>=c.control.transaction.transaction_bounds.max_permission_trace_items)k.fail('ResourceLimit',k.site(sp));
     const trace:T.GenericCommandPermissionTraceItemV1={entry:target.entry,source_callsite:step.call.source_callsite,ordinal:0,policy_sha256:dataDigest(target.access)};
     c.trace.push(trace);c.children.push({entry:child,canonical,trace});const traceBytes=Buffer.byteLength(canonicalJson(c.trace as unknown as Json));if(traceBytes>c.control.transaction.transaction_bounds.max_permission_trace_bytes)k.fail('OutputBound',k.site(sp));
     out=await query(p,q,childEnv,childFrame,child);
    }finally{authorization.retire(childFrame);}
    if(out.kind==='Returned'){
     if(!out.value||!['some','none'].includes(out.value.kind))k.fail('InputType',k.site(sp));
     if(out.value.kind==='none')return terminal(p,selector,step.on_missing,sp+'.on_missing',env,frame,p.entry);
     env[step.binding]=k.checkpoint(out.value.value,step.type,p.account,k.site(sp));
     if(step.row_origin&&c.lastOrigin)c.origins.set(step.binding,c.lastOrigin);
    }else if(out.kind==='Failed'&&out.unavailable)return terminal(p,selector,step.on_unavailable,sp+'.on_unavailable',env,frame,p.entry);else return out;
   }else fail('UnsupportedCapability',at,'unhandled preflight step');
  }return null;
 };
 const prepareIntents=(p:Prepared,rows:readonly (T.GenericTransactionStepV1|E.GenericEventEmitStepV1)[],prefix:SourcePrefix,env:Record<string,any>,frame:GenericReadyFrame):CommandOutcome|null=>{
  const c=p.command!,selector=c.control.operation,k=p.machine.kernel;
  for(const [i,step]of rows.entries()){
   const sp='$.transaction'+JSON.stringify([...prefix,i]),site=k.site(sp);k.charge(p.account,site);
   if(step.kind==='guard'){if(runRole(p,selector,sp+'.condition',env,frame,p.entry)!==true)return sourceFailure(step.on_false);}
   else if(step.kind==='let')env[step.binding]=k.checkpoint(runRole(p,selector,sp+'.value',env,frame,p.entry),step.type,p.account,site);
   else if(step.kind==='conditional'){const arm=runRole(p,selector,sp+'.condition',env,frame,p.entry)===true?'then':'otherwise',out=prepareIntents(p,step[arm],[...prefix,['conditional',i],[arm==='then'?'then':'else',0]],Object.assign(Object.create(null),env),frame);if(out)return out;}
   else if(step.kind==='for'){
    const list=runRole(p,selector,sp+'.source',env,frame,p.entry);if(step.source.result.kind!=='list'||!Array.isArray(list))fail('InvalidContract',at,'actual bounded loop list required');
    for(let j=0;j<list.length;j++){k.charge(p.account,k.site(sp,[j]));const locals=Object.assign(Object.create(null),env,{[step.item]:list[j]}),out=prepareIntents(p,step.body,[...prefix,['loop',i]],locals,frame);if(out)return out;}
   }else if(step.kind==='emit-event'){
    const selected=app as E.GenericEventTransactionApplicationV1;
    if(selected.admission_mode!=='event-handoff-entry'||c.intents.length+c.events.length>=c.control.transaction.transaction_bounds.max_mutations)k.fail('ResourceLimit',site);
    const binding=selected.event_bindings.find(b=>b.id===step.binding_ref);
    const target=binding&&selected.entries.find(e=>e.entry===binding.target_entry);
    if(!binding||!target||dataDigest(binding)!==step.binding_sha256||binding.producer_operation!==selector||binding.producer_service!==options.service||
      binding.event_selector!==step.event_selector||binding.event_version!==step.event_version||
      dataDigest(binding.payload_type)!==binding.payload_schema_sha256||dataDigest(step.payload_type)!==binding.payload_schema_sha256||
      target.service!==binding.target_service||target.access.route!==binding.target_route||
      dataDigest({permission:target.access.permission,resource:target.access.resource,action:target.access.action,scope:target.access.scope})!==dataDigest(binding.target_permission))
     fail('InvalidContract',at,'actual checked Event binding and consumer Entry required');
    if(c.events.some(e=>e.emission_ordinal===step.emission_ordinal||e.source_site===step.source_site))fail('InvalidContract',at,'duplicate original Event emission identity');
    const payload=k.checkpoint(runRole(p,selector,sp+'.payload',env,frame,p.entry),step.payload_type,p.account,site);
    const encoded=canonicalJson(k.wire(payload,step.payload_type,p.account,site) as Json),payload_bytes=Buffer.from(encoded,'utf8');
    if(payload_bytes.byteLength>Math.min(app.limits.max_value_bytes,1048576))k.fail('OutputBound',site);
    k.byteWork(p.account,site,payload_bytes.byteLength);
    c.events.push(Object.freeze({binding_ref:binding.id,binding_sha256:step.binding_sha256,source_site:step.source_site,
     event_selector:step.event_selector,event_version:step.event_version,emission_ordinal:step.emission_ordinal,
     target_service:binding.target_service,target_entry:binding.target_entry,route:binding.target_route,
     payload_schema_sha256:binding.payload_schema_sha256,payload_sha256:createHash('sha256').update(payload_bytes).digest('hex'),payload_bytes}));
   }else{
    if(c.intents.length+c.events.length>=c.control.transaction.transaction_bounds.max_mutations)k.fail('ResourceLimit',site);
    const table=storeView.storage.tables.find(t=>t.entity===step.entity);if(!table)fail('InvalidContract',at,'actual mutation Entity absent');
    const origin=step.kind==='update-observed'?c.origins.get(step.origin_read_binding):undefined;if(step.kind==='update-observed'&&!origin)fail('ForeignOwner',at,'original successful row read binding required');
    const value=Object.assign(Object.create(null),step.kind==='update-observed'?env[step.origin_read_binding]:{});
    for(const [j,field]of step.ordered_fields.entries()){const type=table.record.fields[field.name];if(!type)fail('InvalidContract',at,'actual field absent');value[field.name]=k.checkpoint(runRole(p,selector,sp+'.fields['+j+'].value',env,frame,p.entry),type,p.account,k.site(sp+'.fields['+j+']'));}
    k.checkpoint(value,{kind:'record',name:step.entity},p.account,site);const encoded=encodeRow(p,table,value);env[step.binding]=Object.freeze(value);
    c.intents.push({kind:step.kind==='create'?'create':'update',entity:step.entity,bindings:encoded.bindings,origin:origin??null});
   }
  }return null;
 };
 const commandTuple=(namespace:string,entryId:string,key:string,principal:ReturnType<typeof authorization.commandPrincipal>):T.GenericRootCommandTupleV1|E.GenericEventOperatorRootCommandTupleV2|E.GenericEventServiceRootCommandTupleV2=>{
  const root={application_namespace:namespace,service:options.service,root_entry:entryId,client_key:key};
  return principal.principal_kind==='service'?{...root,schema_version:'craft.generic-root-command/v2-candidate',principal:{kind:'service',service:principal.service,subject:principal.subject,tenant:null}}:principal.principal_kind==='operator'?{...root,schema_version:'craft.generic-root-command/v2-candidate',principal:{kind:'operator',subject:principal.subject,tenant:null}}:{...root,schema_version:'craft.generic-root-command/v1-candidate',principal:{kind:'customer',subject:principal.subject,tenant:null}};
 };
 const inspectTransferredCommandIdentity=(h:GenericCommandTransfer)=>{
  const transfer=h&&typeof h==='object'?transfers.get(h):undefined;
  const p=transfer&&prepared.get(transfer.prepared);
  if(!transfer||transfer.used||!p?.command||p.state!=='transferred'||!transaction||!atomicApplication||atomicApplication.kind!=='original-generic-transaction-application/v1-candidate')fail('ForeignOwner',at,'fresh original authorized command transfer required');
  current();assertGenericInternalExecutionToken(p.token);
  const target=plans.inspectEntry(p.entry),atomic=plans.inspectSourceApplication(atomicApplication).contract;
  if(!('transaction_bounds' in atomic)||target.service!==options.service)fail('ForeignOwner',at,'selected original command Entry required');
  authorization.assertFrame(transfer.frame,p.entry,p.canonical);
  const principal=authorization.commandPrincipal(transfer.frame,p.entry,p.canonical);
  const tuple=commandTuple(atomic.application_namespace,target.entry,p.command.key,principal),bytes=Buffer.from(canonicalJson(tuple as unknown as Json));
  if(bytes.length>atomic.transaction_bounds.max_command_tuple_bytes)fail('ResourceLimit',at,'command tuple exceeds original bound');
  current();return coreFreeze({command_tuple_sha256:createHash('sha256').update(bytes).digest('hex'),canonical_input_sha256:p.canonical});
 };
 function completeHttp(p:Prepared,result:Q.GenericEntryResultV1|T.GenericCommandResultV1):void{
  const selected=p.http;if(!selected||!selected.executing||selected.used)fail('ForeignOwner',at,'fresh original HTTP continuation required');
  selected.used=true;plans.assertHttpChild(selected.handle,application as GenericTransactionApplicationHandle);
  const projected=projectHttpResult(result);if(!result.ok||result.outcome.kind!=='Returned'||!('value'in result.outcome)){selected.result=projected;return;}
  const source=selected.descriptor,originalWire=result.outcome.value,operationFuel=result.fuel_used,k=p.machine.kernel,fuel=()=>({operation_fuel_used:operationFuel,response_fuel_used:p.account.used-operationFuel,total_fuel_used:p.account.used});
  const mapping=app.functions.find(f=>f.name===source.route.response_mapping&&f.kind==='Mapping');
  if(!mapping||mapping.parameters.length!==1||dataDigest({mapping,functions:app.functions,values:app.values,limits:app.limits})!==source.response_mapping_sha256)fail('InvalidContract',at,'actual checked response Mapping differs');
  try{
   const value=pureSegment(p.token,()=>{const site=k.site('$.http.response'),original=k.decode(originalWire,source.result,p.account,site),env=Object.assign(Object.create(null),{[mapping.parameters[0]!.name]:original}),mapped=p.machine.runRole(mapping.name,env,p.account,()=>({found:false,value:undefined}),[mapping.name]),wire=k.wire(k.checkpoint(mapped,source.response_result,p.account,site),source.response_result,p.account,site),bytes=Buffer.byteLength(canonicalJson(wire));k.byteWork(p.account,site,bytes);if(bytes>app.limits.max_output_bytes)k.fail('OutputBound',site);return wire;});
   const mapped=coreFreeze({schema_version:'craft.generic-http-result/v1-candidate' as const,kind:'returned' as const,value,observation:projected.observation,fuel:fuel()}),http=plans.inspectHttpApplication(application as GenericTransactionApplicationHandle);
   selected.result=Buffer.byteLength(canonicalJson(mapped as unknown as Json))>http.contract.profile.limits.response_bytes?coreFreeze({schema_version:'craft.generic-http-result/v1-candidate',kind:'response-withheld',code:'ResponseMappingFailed',cause_code:'ResponseByteBound',observation:projected.observation,fuel:fuel()}) as GenericHttpResultV1:mapped;
  }catch(error){const original=k.failure(error,p.account);selected.result=coreFreeze({schema_version:'craft.generic-http-result/v1-candidate',kind:'response-withheld',code:'ResponseMappingFailed',cause_code:original.error.code,observation:projected.observation,fuel:fuel()}) as GenericHttpResultV1;}
  plans.assertHttpChild(selected.handle,application as GenericTransactionApplicationHandle);current();
 }
 async function runCommand(h:GenericCommandTransfer,purpose:'execute'):Promise<T.GenericCommandResultV1>;
 async function runCommand(h:GenericCommandTransfer,purpose:'inspect'):Promise<T.GenericCommandInspectionV1>;
 async function runCommand(h:GenericCommandTransfer,purpose:'execute'|'inspect'):Promise<T.GenericCommandResultV1|T.GenericCommandInspectionV1>{
  const transfer=h&&typeof h==='object'?transfers.get(h):undefined;if(!transfer||transfer.used)fail('ForeignOwner',at,'fresh original command transfer required');transfer.used=true;
  const p=prepared.get(transfer.prepared),frames:GenericReadyFrame[]=[transfer.frame];let tupleSHA='';let rootFrame=transfer.frame;
  try{
   current();if(!p?.command||p.state!=='transferred'||!transaction||!atomicApplication||atomicApplication.kind!=='original-generic-transaction-application/v1-candidate')fail('ForeignOwner',at,'original atomic command transfer required');
   if(p.http&&(purpose!=='execute'||!p.http.executing))fail('ForeignOwner',at,'HTTP preparation requires its exact continuation');
   const c=p.command,k=p.machine.kernel,target=plans.inspectEntry(p.entry);if(target.schema_version!=='craft.generic-transaction-entry/v1-candidate'&&target.schema_version!=='craft.generic-operator-entry/v1-candidate'&&target.schema_version!=='craft.generic-event-entry/v1-candidate')fail('ForeignOwner',at,'actual transaction entry required');
   authorization.assertFrame(rootFrame,p.entry,p.canonical);const principal=authorization.commandPrincipal(rootFrame,p.entry,p.canonical),actor=authorization.actorForFrame(rootFrame,p.entry),atomic=plans.inspectSourceApplication(atomicApplication).contract;
   if(!('transaction_bounds' in atomic))fail('InvalidContract',at,'actual transaction source required');
   const tuple=commandTuple(atomic.application_namespace,target.entry,c.key,principal);
   c.rootTuple=tuple;c.effectOccurrences=new Map();c.totalEffectOccurrences=0;
   const tupleBytes=Buffer.from(canonicalJson(tuple as unknown as Json));tupleSHA=createHash('sha256').update(tupleBytes).digest('hex');if(tupleBytes.length>atomic.transaction_bounds.max_command_tuple_bytes)k.fail('InputBound',k.site('$.command.tuple'));k.byteWork(p.account,k.site('$.command.tuple'),tupleBytes.length);
   const material={tuple:tupleBytes,tuple_sha256:tupleSHA,payload:new Uint8Array(c.payload),payload_sha256:p.canonical};
   type PhaseMember=Readonly<{entry:GenericEntryPlanHandle;canonical:string;frame:GenericReadyFrame}>;
   let permissionPhase:Readonly<{path:GenericNewCommandPath|GenericReplayPath|null;root:PhaseMember;principal:typeof principal;members:readonly PhaseMember[]}>=Object.freeze({path:null,root:Object.freeze({entry:p.entry,canonical:p.canonical,frame:rootFrame}),principal,members:Object.freeze([])});
   const context:CommandContext={p,owner:transaction,repository:store,material,phase:{kind:'initial'},active:null,finished:false,
    assertEffectCurrent(){effectCurrent(p.token);},
    assertPhase(force=false){const bound=permissionPhase.root;if(bound.frame!==rootFrame||bound.entry!==p.entry||bound.canonical!==p.canonical||permissionPhase.principal.subject!==principal.subject)fail('ForeignOwner',at,'exact original principal frame binding required');if(force||!genericCommandScopeContains(p.token))authorization.assertFrame(bound.frame,bound.entry,bound.canonical);if((context.phase??context.active)?.kind!=='initial'&&permissionPhase.path!==(context.phase??context.active)?.path)fail('ForeignOwner',at,'exact refreshed command path required');for(const member of permissionPhase.members){plans.assertChild(member.entry,application);if(force||!genericCommandScopeContains(p.token))authorization.assertFrame(member.frame,member.entry,member.canonical);}},
    finish(){return pureSegment(p.token,()=>{const outcome=c.outcome??{kind:'Returned' as const,value:runRole(p,c.control.operation,'$.transaction.result_expression',c.env,rootFrame,p.entry)},site=k.site('$.output');const wire:Q.GenericEntryOutcomeV1=outcome.kind==='Returned'?{kind:'Returned',value:k.wire(k.checkpoint(outcome.value,target.result,p.account,site),target.result,p.account,site)}:{kind:outcome.kind,code:outcome.code};const bytes=Buffer.from(canonicalJson(wire as unknown as Json)),trace=Buffer.from(canonicalJson(c.trace as unknown as Json));k.byteWork(p.account,site,bytes.length);k.byteWork(p.account,k.site('$.command.permission_trace'),trace.length);if(bytes.length>app.limits.max_output_bytes||trace.length>atomic.transaction_bounds.max_permission_trace_bytes)k.fail('OutputBound',site);return {outcome:wire,bytes,sha256:createHash('sha256').update(bytes).digest('hex'),trace,fuel:p.account.used};});},
    replay(bytes){return pureSegment(p.token,()=>{const site=k.site('$.command.replay');k.byteWork(p.account,site,bytes.length);let parsed:any,text:string;try{text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);parsed=JSON.parse(text);}catch{throw new GenericTransactionResourceError('StoredCommandInvalid');}if(!parsed||typeof parsed!=='object'||Array.isArray(parsed)||!['Returned','Rejected','Failed'].includes(parsed.kind)||Object.keys(parsed).sort().join(',')!==(parsed.kind==='Returned'?'kind,value':'code,kind'))throw new GenericTransactionResourceError('StoredCommandInvalid');let outcome:Q.GenericEntryOutcomeV1;if(parsed.kind==='Returned'){let value:any;try{value=k.decode(parsed.value,target.result,p.account,site);}catch(error){const failure=k.failure(error,p.account);if(resourceCodes.has(failure.error.code))throw error;throw new GenericTransactionResourceError('StoredCommandInvalid');}outcome={kind:'Returned',value:k.wire(value,target.result,p.account,site)};}else{if(typeof parsed.code!=='string'||!/^[a-z][a-z0-9-]*$/.test(parsed.code))throw new GenericTransactionResourceError('StoredCommandInvalid');outcome={kind:parsed.kind,code:parsed.code};}if(canonicalJson(outcome as unknown as Json)!==text)throw new GenericTransactionResourceError('StoredCommandInvalid');return outcome;});}
   };commandContexts.set(p.token,context);
   let next=purpose==='execute'?transaction.startExecute(p.token):transaction.startInspect(p.token);
   const freshExecution=purpose==='execute'&&next.kind==='prepare-new';
   const refresh=async(path:GenericNewCommandPath|GenericReplayPath,trace:readonly T.GenericCommandPermissionTraceItemV1[]|null)=>{
    const freshRoot=await freshFrame(p,actor,p.entry,p.canonical);frames.push(freshRoot);const freshPrincipal=authorization.commandPrincipal(freshRoot,p.entry,p.canonical);if(freshPrincipal.subject!==principal.subject)fail('ForeignOwner',at,'stable original principal differs');const members:PhaseMember[]=[];
    const children=trace?trace.map(t=>({entry:entry(t.entry),canonical:p.canonical,trace:t})):c.children;
    for(const child of children){const final=await freshFrame(p,actor,child.entry,child.canonical);frames.push(final);members.push(Object.freeze({entry:child.entry,canonical:child.canonical,frame:final}));}
    current();assertGenericInternalExecutionToken(p.token);permissionPhase=Object.freeze({path,root:Object.freeze({entry:p.entry,canonical:p.canonical,frame:freshRoot}),principal:freshPrincipal,members:Object.freeze(members)});rootFrame=freshRoot;
   };
   if(next.kind==='prepare-new'){
    c.env=Object.assign(Object.create(null),p.env);c.outcome=await preflight(p,c.control.preflight,[],c.env,rootFrame);
    if(!c.outcome)c.outcome=prepareIntents(p,c.control.transaction.body,[['transaction',c.control.transaction.name]],c.env,rootFrame);
    if(c.outcome){c.intents=[];c.events=[];}
    await refresh(next.path,null);context.phase={kind:'prepared',path:next.path};effectCurrent(p.token);next=transaction.commitPrepared(p.token,next.path);
   }
   if(next.kind==='refresh-replay'){
    const trace=transaction.requireReplayPermissionTrace(p.token,next.path);await refresh(next.path,trace);context.phase={kind:'replay',path:next.path};context.finished=false;
    const completion=purpose==='execute'?transaction.finishExecuteReplay(p.token,next.path):transaction.finishInspectReplay(p.token,next.path);
    const result=purpose==='execute'?transaction.takeExecuteCompletion(p.token,completion):transaction.takeInspectCompletion(p.token,completion);if(p.http&&purpose==='execute')completeHttp(p,result as T.GenericCommandResultV1);return result;
   }
   const result=purpose==='execute'?transaction.takeExecuteCompletion(p.token,next.completion):transaction.takeInspectCompletion(p.token,next.completion);
   if('ok'in result&&mayAttestProviderNoEffect(freshExecution,result,c.providerEffectPossible===true))
    provenNoProviderEffect.add(result);
   if(p.http&&purpose==='execute')completeHttp(p,result as T.GenericCommandResultV1);return result;
  }catch(error){
   if(p?.http?.used)throw error;
   current();if(!p||!tupleSHA)throw error;const fault=error instanceof BoundaryFault?error.error:error instanceof GenericTransactionResourceError?{kind:'transaction' as const,code:error.code,site:'$.command',source_action:null}:p.machine.kernel.failure(error,p.account).error;
   if(fault.code==='CommitIndeterminate')throw error;
   if(purpose==='inspect')return coreFreeze({schema_version:'craft.generic-command-inspection/v1-candidate',kind:'fault',error:fault,fuel_used:p.account.used,command_tuple_sha256:tupleSHA});
   const result=coreFreeze({schema_version:'craft.generic-command-result/v1-candidate' as const,ok:false as const,error:fault,fuel_used:p.account.used,observation:{kind:'failed-before-write' as const,command_tuple_sha256:tupleSHA}});if(p.http&&p.http.executing&&!p.http.used)completeHttp(p,result as T.GenericCommandResultV1);return result;
  }finally{for(const frame of frames)authorization.retire(frame);if(p){transaction?.retire(p.token);commandContexts.delete(p.token);retirePrepared(p);}}
 }

 function authorize(actor:GenericFixtureActor|null,h:GenericPreparedInput):Promise<import('./invocation-owner.js').GenericRuntimeAccessResult<GenericInvocationAuthorization>>;
 function authorize(actor:GenericFixtureActor|null,h:GenericPreparedCommand):Promise<import('./invocation-owner.js').GenericRuntimeAccessResult<GenericCommandAuthorization>>;
async function authorize(actor:GenericFixtureActor|null,h:GenericPreparedInput|GenericPreparedCommand){const p=state(h);if(p.state!=='prepared')fail('ForeignOwner',at,'preparation is not fresh');p.state='authorizing';let issued:GenericEntryAuthorization|undefined;try{const a=await authorization.authorize(actor,p.entry,p.canonical);if(a.ok)issued=a.value;if(p.state!=='authorizing'){if(a.ok)authorization.retireAuthorization(a.value);fail('ForeignOwner',at,'preparation retired during authorization');}current();if(!a.ok){retirePrepared(p);return {...a,fuel_used:p.account.used};}const out=Object.freeze({kind:p.command?'original-generic-command-authorization/v1-candidate' as const:'original-generic-invocation-authorization/v1-candidate' as const});authorizations.set(out,{prepared:h,authorization:a.value,used:false});p.state='authorized';return {ok:true as const,value:out};}catch(error){if(issued)authorization.retireAuthorization(issued);retirePrepared(p);throw error;}}
 function consume(a:GenericInvocationAuthorization,h:GenericPreparedInput):Promise<import('./invocation-owner.js').GenericRuntimeAccessResult<GenericInvocationTransfer>>;
 function consume(a:GenericCommandAuthorization,h:GenericPreparedCommand):Promise<import('./invocation-owner.js').GenericRuntimeAccessResult<GenericCommandTransfer>>;
async function consume(a:GenericInvocationAuthorization|GenericCommandAuthorization,h:GenericPreparedInput|GenericPreparedCommand){const p=state(h),r=a&&typeof a==='object'?authorizations.get(a):undefined;if(!r||r.used||r.prepared!==h||p.state!=='authorized')fail('ForeignOwner',at,'exact original authorized preparation required');r.used=true;p.state='consuming';let issued:GenericReadyFrame|undefined;try{const final=await authorization.consume(r.authorization);if(final.ok)issued=final.value;if(p.state!=='consuming'){if(final.ok)authorization.retire(final.value);fail('ForeignOwner',at,'preparation retired during final authorization');}current();if(!final.ok){retirePrepared(p);return {...final,fuel_used:p.account.used};}if(v3Reopen)ensureStoreAfterRootReady(final.value,p);const out=Object.freeze({kind:p.command?'original-generic-command-transfer/v1-candidate' as const:'original-generic-invocation-transfer/v1-candidate' as const});transfers.set(out,{prepared:h,frame:final.value,used:false});p.state='transferred';return {ok:true as const,value:out};}catch(error){if(issued)authorization.retire(issued);retirePrepared(p);throw error;}}
 const deliverEvent=async(relay:GenericEventRelayOwner,claim:GenericEventRelayClaim):Promise<GenericEventDeliveryResult>=>{
  current();
  if(app.admission_mode!=='event-handoff-entry'||!fullStore)fail('UnsupportedCapability',at,'actual V4 receiver required');
  const producer=requireGenericEventRelayOwnerBinding(relay),physical=requireGenericEventRelayClaim(relay,claim),envelope=physical.envelope;
  if(producer.plans!==plans||producer.application!==application||producer.repository===store||producer.service!==envelope.producer_namespace||
    producer.source_capture_sha256!==plans.inspectSourceApplication(application).source_capture_sha256||
    producer.profile_sha256!==plans.inspectSourceApplication(application).derivation.profile_sha256)
   fail('ForeignOwner',at,'original distinct producer and receiver owners required');
  const binding=app.event_bindings.find(b=>b.id===envelope.binding_ref);
  const producerControl=binding&&app.stateful_operations.find(o=>o.operation===binding.producer_operation);
  const emission=producerControl?.transaction.body.find(s=>s.kind==='emit-event'&&s.binding_ref===envelope.binding_ref);
  if(!binding||dataDigest(binding)!==envelope.binding_sha256||binding.producer_service!==producer.service||
    binding.event_selector!==envelope.event_selector||binding.event_version!==envelope.event_version||
    binding.target_service!==options.service||binding.target_entry!==envelope.target_entry||
    binding.target_route!==envelope.route||binding.payload_schema_sha256!==envelope.payload_schema_sha256||
    !emission||emission.kind!=='emit-event'||emission.source_site!==envelope.source_site||emission.emission_ordinal!==envelope.emission_ordinal)
   fail('ForeignOwner',at,'checked Event envelope does not select this receiver');
  const target=entry(binding.target_entry),selected=plans.inspectEntry(target);
  if(selected.schema_version!=='craft.generic-event-entry/v1-candidate'||selected.mapping!==binding.consumer_mapping||
    selected.event_selector!==binding.event_selector||selected.event_version!==binding.event_version||
    dataDigest({permission:selected.access.permission,resource:selected.access.resource,action:selected.access.action,scope:selected.access.scope})!==dataDigest(binding.target_permission)||
    selected.parameters.length!==1)
   fail('InvalidContract',at,'actual generated Event Entry and permission required');
  const registered=runtimes.get(runtime),actor=registered?.serviceCredentials.get(selected.entry);
  if(!actor)fail('ForeignOwner',at,'private profile-owned service credential required');
  const mapping=app.functions.find(f=>f.name===binding.consumer_mapping);
  if(!mapping||mapping.parameters.length!==1||dataDigest(mapping.parameters[0]!.type)!==dataDigest(binding.payload_type)||
    dataDigest(mapping.result)!==dataDigest(selected.parameters[0]!.type))
   fail('InvalidContract',at,'authored Event payload Mapping required');
  const mappingToken=makeToken(plans,application,target,current,lifetime),machine=createMachine(mappingToken),account=machine.kernel.fresh(false);
  let wire:Uint8Array;
  try{wire=pureSegment(mappingToken,()=>{
   const k=machine.kernel,site=k.site('$.event.payload'),source=new TextDecoder('utf-8',{fatal:true}).decode(envelope.payload_bytes),payload=k.decode(JSON.parse(source),binding.payload_type,account,site),args=Object.assign(Object.create(null),{[mapping.parameters[0]!.name]:payload});
   const mapped=machine.runRole(mapping.name,args,account,()=>({found:false,value:undefined}),[mapping.name]);
   const output=k.wire(k.checkpoint(mapped,selected.parameters[0]!.type,account,site),selected.parameters[0]!.type,account,site);
   return Buffer.from(canonicalJson({[selected.parameters[0]!.name]:output} as Json));
  });}finally{retiredTokens.add(mappingToken);}
  const preparedCommand=runtime.prepareCommand(target,wire,{client_key:envelope.occurrence_sha256}),preparedRow=prepared.get(preparedCommand);
  if(!preparedRow?.command)fail('ForeignOwner',at,'original receiver command preparation required');
  preparedRow.command.delivery=envelope;
  const access=await runtime.authorize(actor,preparedCommand);
  if(!access.ok)return Object.freeze({kind:access.error.code==='AuthorizationUnavailable'?'unavailable':'denied'});
  const transferred=await runtime.consume(access.value,preparedCommand);
  if(!transferred.ok)return Object.freeze({kind:transferred.error.code==='AuthorizationUnavailable'?'unavailable':'denied'});
  const transfer=transfers.get(transferred.value);
  if(!transfer)fail('ForeignOwner',at,'original receiver READY transfer required');
  let inbox:ReturnType<typeof store.inspectEventInbox>;
  try{inbox=store.inspectEventInbox(preparedRow.token,authorization,transfer.frame,target,envelope);}catch(error){
   transfer.used=true;retirePrepared(preparedRow);authorization.retire(transfer.frame);throw error;
  }
  if(inbox.kind!=='absent'){
   transfer.used=true;retirePrepared(preparedRow);authorization.retire(transfer.frame);
   if(inbox.kind==='collision')return Object.freeze({kind:'unavailable'});
   if(inbox.kind!=='same'||!inbox.consumer_command_tuple_sha256)fail('InvalidContract',at,'exact committed receiver tuple required');
   return Object.freeze({kind:'replayed',receipt:mintGenericEventReceiverCommitReceipt(relay,claim,envelope,inbox.consumer_command_tuple_sha256,current)});
  }
  const result=await runtime.executeCommand(transferred.value);
  if(!result.ok)return Object.freeze({kind:result.error.code==='PermissionDenied'||result.error.code==='AuthenticationRequired'?'denied':'unavailable'});
  if(result.observation.kind!=='committed'||result.outcome.kind!=='Returned')return Object.freeze({kind:'unavailable'});
  return Object.freeze({kind:'committed',receipt:mintGenericEventReceiverCommitReceipt(relay,claim,envelope,result.observation.command_tuple_sha256,current)});
 };
 const inspectCommittedEvent=async(envelope:GenericEventEnvelope):Promise<{kind:'same';consumer_command_tuple_sha256:string}|{kind:'absent'|'collision'|'denied'|'unavailable'}>=>{
  current();
  if(app.admission_mode!=='event-handoff-entry'||!fullStore)fail('UnsupportedCapability',at,'actual V4 receiver required');
  const binding=app.event_bindings.find(b=>b.id===envelope.binding_ref);
  const producerControl=binding&&app.stateful_operations.find(o=>o.operation===binding.producer_operation);
  const emission=producerControl?.transaction.body.find(s=>s.kind==='emit-event'&&s.binding_ref===envelope.binding_ref);
  if(!binding||dataDigest(binding)!==envelope.binding_sha256||binding.producer_service!==envelope.producer_namespace||
    binding.event_selector!==envelope.event_selector||binding.event_version!==envelope.event_version||
    binding.target_service!==options.service||binding.target_entry!==envelope.target_entry||
    binding.target_route!==envelope.route||binding.payload_schema_sha256!==envelope.payload_schema_sha256||
    !emission||emission.kind!=='emit-event'||emission.source_site!==envelope.source_site||emission.emission_ordinal!==envelope.emission_ordinal)
   fail('ForeignOwner',at,'checked Event envelope does not select this receiver');
  const target=entry(binding.target_entry),selected=plans.inspectEntry(target);
  if(selected.schema_version!=='craft.generic-event-entry/v1-candidate'||selected.mapping!==binding.consumer_mapping||
    selected.event_selector!==binding.event_selector||selected.event_version!==binding.event_version||
    dataDigest({permission:selected.access.permission,resource:selected.access.resource,action:selected.access.action,scope:selected.access.scope})!==dataDigest(binding.target_permission)||
    selected.parameters.length!==1)
   fail('InvalidContract',at,'actual generated Event Entry and permission required');
  const actor=runtimes.get(runtime)?.serviceCredentials.get(selected.entry);
  if(!actor)fail('ForeignOwner',at,'private profile-owned service credential required');
  const mapping=app.functions.find(f=>f.name===binding.consumer_mapping);
  if(!mapping||mapping.parameters.length!==1||dataDigest(mapping.parameters[0]!.type)!==dataDigest(binding.payload_type)||
    dataDigest(mapping.result)!==dataDigest(selected.parameters[0]!.type))
   fail('InvalidContract',at,'authored Event payload Mapping required');
  const mappingToken=makeToken(plans,application,target,current,lifetime),machine=createMachine(mappingToken),account=machine.kernel.fresh(false);
  let wire:Uint8Array;
  try{wire=pureSegment(mappingToken,()=>{
   const k=machine.kernel,site=k.site('$.event.payload'),source=new TextDecoder('utf-8',{fatal:true}).decode(envelope.payload_bytes),payload=k.decode(JSON.parse(source),binding.payload_type,account,site),args=Object.assign(Object.create(null),{[mapping.parameters[0]!.name]:payload});
   const mapped=machine.runRole(mapping.name,args,account,()=>({found:false,value:undefined}),[mapping.name]);
   const output=k.wire(k.checkpoint(mapped,selected.parameters[0]!.type,account,site),selected.parameters[0]!.type,account,site);
   return Buffer.from(canonicalJson({[selected.parameters[0]!.name]:output} as Json));
  });}finally{retiredTokens.add(mappingToken);}
  const preparedCommand=runtime.prepareCommand(target,wire,{client_key:envelope.occurrence_sha256}),preparedRow=prepared.get(preparedCommand);
  if(!preparedRow?.command)fail('ForeignOwner',at,'original receiver command preparation required');
  preparedRow.command.delivery=envelope;
  let transferredFrame:GenericReadyFrame|undefined;
  try{
   const access=await runtime.authorize(actor,preparedCommand);
   if(!access.ok)return Object.freeze({kind:access.error.code==='AuthorizationUnavailable'?'unavailable':'denied'});
   const transferred=await runtime.consume(access.value,preparedCommand);
   if(!transferred.ok)return Object.freeze({kind:transferred.error.code==='AuthorizationUnavailable'?'unavailable':'denied'});
   const transfer=transfers.get(transferred.value);
   if(!transfer)fail('ForeignOwner',at,'original receiver READY transfer required');
   transfer.used=true;transferredFrame=transfer.frame;
   const inbox=store.inspectEventInbox(preparedRow.token,authorization,transfer.frame,target,envelope);
   if(inbox.kind==='same'){
    if(!inbox.consumer_command_tuple_sha256)fail('InvalidContract',at,'exact committed receiver tuple required');
    return Object.freeze({kind:'same',consumer_command_tuple_sha256:inbox.consumer_command_tuple_sha256});
   }
   return Object.freeze({kind:inbox.kind});
  }finally{
   if(transferredFrame)authorization.retire(transferredFrame);
   retirePrepared(preparedRow);
  }
 };
 const prepareHttp=(route:GenericHttpEntryPlanHandle,wire:Uint8Array,metadata:T.GenericCommandMetadataV1|null):GenericPreparedInput|GenericPreparedCommand=>{
  current();if(!atomicApplication||atomicApplication.kind!=='original-generic-transaction-application/v1-candidate')fail('UnsupportedCapability',at,'original atomic HTTP application required');
  plans.assertHttpChild(route,atomicApplication);const descriptor=plans.inspectHttpEntry(route),target=entry(descriptor.route.entry),original=plans.inspectEntry(target);
  if(descriptor.route.service!==options.service||dataDigest(original)!==descriptor.entry_contract_sha256)fail('ForeignOwner',at,'HTTP route differs from original service Entry');
  const h=descriptor.route.method==='GET'?(metadata===null?runtime.prepareInput(target,wire):fail('ForeignOwner',at,'GET cannot use command metadata')):(metadata!==null?runtime.prepareCommand(target,wire,metadata):fail('ForeignOwner',at,'POST requires command metadata'));
  const p=prepared.get(h);if(!p)fail('ForeignOwner',at,'original HTTP preparation required');p.http={handle:route,descriptor,executing:false,used:false,result:null};return h;
 };
 const executeHttp=async(h:GenericInvocationTransfer|GenericCommandTransfer,route:GenericHttpEntryPlanHandle):Promise<GenericHttpResultV1>=>{
  current();if(!atomicApplication||atomicApplication.kind!=='original-generic-transaction-application/v1-candidate')fail('UnsupportedCapability',at,'original atomic HTTP application required');
  plans.assertHttpChild(route,atomicApplication);const transfer=h&&typeof h==='object'?transfers.get(h):undefined,p=transfer&&prepared.get(transfer.prepared);
  if(!transfer||transfer.used||!p?.http||p.http.handle!==route||p.http.used||p.http.executing)fail('ForeignOwner',at,'exact original HTTP transfer required');
  p.http.executing=true;const result=p.command?await runtime.executeCommand(h as GenericCommandTransfer):await runtime.execute(h as GenericInvocationTransfer);
  current();plans.assertHttpChild(route,atomicApplication);if(!p.http.result)fail('ForeignOwner',at,'original HTTP response completion missing');return p.http.result;
 };
 const runtime:GenericTransactionApplicationRuntime=Object.freeze({entry,
  inspectTransferredCommandIdentity,
  provesProviderNoEffect(result:T.GenericCommandResultV1){current();return !!result&&typeof result==='object'&&provenNoProviderEffect.has(result);},
  openEventRelay(){current();if(app.admission_mode!=='event-handoff-entry'||!atomicApplication||atomicApplication.kind!=='original-generic-transaction-application/v1-candidate'||!fullStore)fail('UnsupportedCapability',at,'actual V4 producer store required');return createGenericEventRelayOwner(plans,atomicApplication,store,options.service);},
  prepareInput(e:GenericEntryPlanHandle,wire:Uint8Array){current();plans.assertChild(e,application);const target=plans.inspectEntry(e);if(target.schema_version==='craft.generic-transaction-entry/v1-candidate'||target.schema_version==='craft.generic-operator-entry/v1-candidate'||target.schema_version==='craft.generic-event-entry/v1-candidate')throw new GenericCommandPreparationError('MissingCommandIdentity');if(target.service!==options.service)fail('ForeignOwner',at,'entry service mismatch');const token=makeToken(plans,application,e,current,lifetime);let p:Prepared|undefined;try{const machine=createMachine(token),account=machine.kernel.fresh(false);p={entry:e,token,machine,account,env:Object.create(null),canonical:'',state:'prepared'};const selected=p;pureSegment(token,()=>{selected.env=machine.kernel.input(wire,account);selected.canonical=canonicalInput(selected,target.parameters);});current();const h=Object.freeze({kind:'original-generic-prepared-input/v1-candidate' as const});prepared.set(h,p);return h;}catch(error){retiredTokens.add(token);if(p){retirePrepared(p);const f=p.machine.kernel.failure(error,p.account);throw new GenericInputPreparationError(f.error,p.account.used);}throw error;}},
  prepareCommand(e:GenericEntryPlanHandle,wire:Uint8Array,metadata:T.GenericCommandMetadataV1){const captured=captureGenericCommandMetadata(metadata);current();plans.assertChild(e,application);const target=plans.inspectEntry(e);if((!transaction&&!v3Reopen)||!atomicApplication||atomicApplication.kind!=='original-generic-transaction-application/v1-candidate'||target.schema_version!=='craft.generic-transaction-entry/v1-candidate'&&target.schema_version!=='craft.generic-operator-entry/v1-candidate'&&target.schema_version!=='craft.generic-event-entry/v1-candidate')fail('UnsupportedCapability',at,'prepareCommand requires actual stateful entry');if(target.service!==options.service)fail('ForeignOwner',at,'entry service mismatch');const control=plans.inspectSourceStatefulOperation(plans.bindStatefulOperation(atomicApplication,target.target));if(Buffer.byteLength(captured.client_key)>control.transaction.transaction_bounds.max_command_key_bytes||[...captured.client_key].length>control.transaction.transaction_bounds.max_command_key_scalars)fail('InvalidContract',at,'command key exceeds selected original bounds');const token=makeToken(plans,application,e,current,lifetime);let p:Prepared|undefined;try{const machine=createMachine(token),account=machine.kernel.fresh(false);p={entry:e,token,machine,account,env:Object.create(null),canonical:'',state:'prepared',command:{key:captured.client_key,payload:new Uint8Array(),control,reads:[],intents:[],events:[],delivery:null,trace:[],origins:new Map(),lastObservation:null,lastOrigin:null,children:[],outcome:null,env:Object.create(null)}};const selected=p;pureSegment(token,()=>{selected.env=machine.kernel.input(wire,account);selected.canonical=canonicalInput(selected,target.parameters,true);});current();const h=Object.freeze({kind:'original-generic-prepared-command/v1-candidate' as const});prepared.set(h,p);return h;}catch(error){retiredTokens.add(token);if(p){retirePrepared(p);const f=p.machine.kernel.failure(error,p.account);throw new GenericInputPreparationError(f.error,p.account.used);}throw error;}},
  executeCommand:(h:GenericCommandTransfer)=>{
   const transfer=transfers.get(h);
   // Reject spent/foreign opaque handles before touching their retired token.
   // Every fresh original transfer still performs the full currentness check.
   if(!transfer||transfer.used)return runCommand(h,'execute');
   const p=prepared.get(transfer.prepared),work=()=>binding.withCommandCurrentnessScope?binding.withCommandCurrentnessScope(()=>runCommand(h,'execute')):runCommand(h,'execute');
   if(p)forceGenericInternalExecutionTokenCurrent(p.token);return p?commandScopes.run(p.token,work):work();
  },
  inspectCommand:(h:GenericCommandTransfer)=>{
   const transfer=transfers.get(h);if(!transfer||transfer.used)return runCommand(h,'inspect');
   const p=prepared.get(transfer.prepared),work=()=>binding.withCommandCurrentnessScope?binding.withCommandCurrentnessScope(()=>runCommand(h,'inspect')):runCommand(h,'inspect');
   if(p)forceGenericInternalExecutionTokenCurrent(p.token);return p?commandScopes.run(p.token,work):work();
  },
  authorize,consume,
  async execute(h:GenericInvocationTransfer):Promise<Q.GenericEntryResultV1>{const r=h&&typeof h==='object'?transfers.get(h):undefined;if(!r||r.used)fail('ForeignOwner',at,'fresh original transfer required');r.used=true;const p=prepared.get(r.prepared);try{if(!p)fail('ForeignOwner',at,'original transferred preparation required');current();if(p.command)fail('ForeignOwner',at,'command transfer requires executeCommand');if(p.http&&!p.http.executing)fail('ForeignOwner',at,'HTTP preparation requires its exact continuation');if(p.state!=='transferred')fail('ForeignOwner',at,'transferred preparation required');const target=plans.inspectEntry(p.entry);authorization.assertFrame(r.frame,p.entry,p.canonical);const q=app.queries.find(q=>q.query===target.target),o=app.readonly_operations.find(o=>o.operation===target.target),pure=app.pure_operations.find(o=>o.operation.module+'.'+o.operation.name===target.target);let outcome:Outcome|null;if(q)outcome=await query(p,q,p.env,r.frame,p.entry);else if(o)outcome=await operation(p,o.operation,o.body,'$.body',p.env,r.frame,p.entry);else if(pure){const result=runRole(p,target.target,'$.pure-operation',p.env,r.frame,p.entry);outcome=result.kind==='Returned'?{kind:'Returned',value:result.fields.value}:{kind:result.kind,code:result.fields.code};}else return fail('InvalidContract',at,'actual entry target absent');if(!outcome)fail('InvalidContract',at,'source control fell through');const selectedOutcome=outcome,publicOutcome=pureSegment(p.token,()=>{const k=p.machine.kernel,s=k.site('$.output'),value:Q.GenericEntryOutcomeV1=selectedOutcome.kind==='Returned'?{kind:'Returned',value:k.wire(k.checkpoint(selectedOutcome.value,target.result,p.account,s),target.result,p.account,s)}:{kind:selectedOutcome.kind,code:selectedOutcome.code};const text=canonicalJson(value as unknown as Json);k.byteWork(p.account,s,Buffer.byteLength(text));if(Buffer.byteLength(text)>app.limits.max_output_bytes)k.fail('OutputBound',s);return value;});current();const result=coreFreeze({ok:true as const,outcome:publicOutcome,fuel_used:p.account.used});if(p.http)completeHttp(p,result);return result;}catch(error){if(p?.http?.used)throw error;current();if(!p)throw error;const result=error instanceof BoundaryFault?coreFreeze({ok:false as const,error:error.error,fuel_used:p.account.used}):coreFreeze(p.machine.kernel.failure(error,p.account)) as Q.GenericEntryResultV1;if(p.http&&p.http.executing&&!p.http.used)completeHttp(p,result);return result;}finally{if(p)retirePrepared(p);authorization.retire(r.frame);}},
  inspectPrepared(h:GenericPreparedInput|GenericPreparedCommand){const p=state(h);return coreFreeze({state:p.state,fuel_used:p.account.used,entry:plans.inspectEntry(p.entry).entry,canonical_input_sha256:p.canonical});},
  disposePrepared(h:GenericPreparedInput|GenericPreparedCommand){const p=state(h);retirePrepared(p);},
  inspect(){current();const storage=fullStore?store.inspect():coreFreeze({mode:'reopen',store_epoch_sha256:expectedEpoch,authority_effect:'none'});return external?coreFreeze({...storage,external_read_diagnostics:external.inspect()}):storage;},assertCurrent(){current();if(fullStore)store.assertCurrent();},async close(){if(lifetime.closed)return;lifetime.closed=true;external?.close();if(fullStore)store.close();if(preauth&&!preauthClosed){closeOriginalV3PreAuthStoreIdentity(preauth);preauthClosed=true;}},
 });runtimes.set(runtime,{current,owner:sdk,handle,service:options.service,plans,application,store,authorization,serviceCredentials:new Map(),deliverEvent,inspectCommittedEvent,prepareHttp,executeHttp,querySnapshot(h:GenericPreparedInput){current();const p=prepared.get(h);if(!p?.querySnapshot)fail('ForeignOwner',at,'actual executed Query preparation required');store!.assertCapabilitySnapshot(p.querySnapshot);return p.querySnapshot;},fixtureUsed:false,firstEntry:()=>{const e=app.entries.find(e=>e.service===options.service);if(!e)fail('InvalidContract',at,'fixture service requires Entry');return entry(e.entry);},native:options.nativeAuth,lifetime});current();return runtime;
}
export function registerGenericRuntimeFixtureActor(runtime:GenericApplicationRuntime,database:CommerceAuthFixtureDatabaseV1,subject:string,evidence:string,entryId:string){const r=runtimes.get(runtime);if(!r)fail('ForeignOwner',at,'original runtime required');r.current();return r.authorization.registerFixtureActor(database,subject,evidence,runtime.entry(entryId));}

/** Internal credential provisioning seam. The test facade may install the
 * profile-derived service identity privately; it never returns the actor. */
export function registerGenericRuntimeServiceCredential(runtime:GenericApplicationRuntime,database:CommerceAuthFixtureDatabaseV1,subject:string,evidence:string,entryId:string,producerService:string):void{
 const r=runtimes.get(runtime);if(!r)fail('ForeignOwner',at,'original receiver runtime required');r.current();
 const selected=r.plans.inspectSourceApplication(r.application).contract;if(selected.admission_mode!=='event-handoff-entry')fail('UnsupportedCapability',at,'V4 receiver required');
 const binding=selected.event_bindings.find(b=>b.target_entry===entryId&&b.producer_service===producerService);
 if(!binding||binding.target_service!==r.plans.inspectEntry(runtime.entry(entryId)).service||r.serviceCredentials.has(entryId))fail('ForeignOwner',at,'unique checked receiver credential binding required');
 const actor=r.authorization.registerServiceCredential(database,subject,evidence,runtime.entry(entryId),producerService);
 r.serviceCredentials.set(entryId,actor);r.current();
}

export function requireGenericRuntimeServiceCredential(runtime:GenericApplicationRuntime,entryId:string):GenericFixtureActor{
 const r=runtimes.get(runtime);if(!r)fail('ForeignOwner',at,'original receiver runtime required');r.current();
 const actor=r.serviceCredentials.get(entryId);if(!actor)fail('ForeignOwner',at,'profile-owned receiver credential absent');
 r.plans.assertChild(runtime.entry(entryId),r.application);return actor;
}
export function assertGenericApplicationRuntime(runtime:GenericApplicationRuntime){const r=runtimes.get(runtime);if(!r)fail('ForeignOwner',at,'original runtime required');r.current();}
/** Same original application, without requiring an HTTP source profile. No grant is created. */
export function assertGenericErrorRuntimeBinding(runtime:GenericApplicationRuntime|GenericTransactionApplicationRuntime,plans:GenericRepositoryPlanOwner,application:GenericApplicationPlanHandle):void{const r=runtime&&typeof runtime==='object'?runtimes.get(runtime):undefined;if(!r||r.plans!==plans||r.application!==application)fail('ForeignOwner',at,'original error presentation runtime binding required');r.current();}
export function assertGenericHttpRuntimeBinding(runtime:GenericTransactionApplicationRuntime,plans:GenericRepositoryPlanOwner,application:GenericTransactionApplicationHandle):void{const r=runtime&&typeof runtime==='object'?runtimes.get(runtime):undefined;if(!r||r.plans!==plans||r.application!==application)fail('ForeignOwner',at,'original HTTP runtime binding required');r.current();plans.inspectHttpApplication(application);}
export function prepareGenericHttpInvocation(runtime:GenericTransactionApplicationRuntime,route:GenericHttpEntryPlanHandle,wire:Uint8Array,metadata:T.GenericCommandMetadataV1|null):GenericPreparedInput|GenericPreparedCommand{const r=runtime&&typeof runtime==='object'?runtimes.get(runtime):undefined;if(!r)fail('ForeignOwner',at,'original HTTP runtime required');r.current();return r.prepareHttp(route,wire,metadata);}
export async function executeGenericHttpContinuation(runtime:GenericTransactionApplicationRuntime,transfer:GenericInvocationTransfer|GenericCommandTransfer,route:GenericHttpEntryPlanHandle):Promise<GenericHttpResultV1>{const r=runtime&&typeof runtime==='object'?runtimes.get(runtime):undefined;if(!r)fail('ForeignOwner',at,'original HTTP runtime required');r.current();return r.executeHttp(transfer,route);}
export function assertGenericRuntimeNative(runtime:GenericApplicationRuntime,native:GenericRuntimeOptions['nativeAuth']){const r=runtimes.get(runtime);if(!r||r.native!==native)fail('ForeignOwner',at,'actual runtime native owner required');r.current();}
export function loadGenericRuntimeFixture(runtime:GenericApplicationRuntime,bytes:Uint8Array,fixture:GenericFixtureLoadHandle){assertGenericFixtureLoadInProgress(fixture,runtime);const r=runtimes.get(runtime);if(!r)fail('ForeignOwner',at,'original runtime required');r.current();if(r.fixtureUsed||!r.store||r.store.inspect().mode!=='create')fail('ForeignOwner',at,'one-use fresh runtime fixture required');r.fixtureUsed=true;const e=r.firstEntry(),token=makeToken(r.plans,r.application,e,r.current,r.lifetime),machine=createMachine(token),account=machine.kernel.fresh(false),p:Prepared={entry:e,token,machine,account,env:Object.create(null),canonical:'',state:'retired'},k=machine.kernel,s=k.site('$.fixture'),layout=r.store.inspect().storage;try{if(host.isProxy(bytes)||!host.isUint8Array(bytes))k.fail('InputType',s);let copied:Uint8Array;try{const prototype=Object.getPrototypeOf(Uint8Array.prototype),get=(name:string)=>Object.getOwnPropertyDescriptor(prototype,name)!.get!.call(bytes),length=get('byteLength');if(length>machine.contract.limits.max_input_bytes)k.fail('InputBound',s);if(host.isSharedArrayBuffer(get('buffer')))k.fail('InputType',s);k.byteWork(account,s,length);const view=new Uint8Array(get('buffer'),get('byteOffset'),length);copied=new Uint8Array(length);Uint8Array.prototype.set.call(copied,view);}catch(error){try{k.failure(error,account);}catch{k.fail('InputType',s);}throw error;}let raw:any;try{raw=JSON.parse(new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(copied));}catch{k.fail('InputType',s);}if(!raw||Object.keys(raw).sort().join(',')!=='rows,schema_version'||raw.schema_version!=='craft.generic-fixture-rows/v1-candidate'||!Array.isArray(raw.rows)||raw.rows.length>Math.min(100,machine.contract.limits.max_items))k.fail('InputType',s);const rows=raw.rows.map((row:any)=>{if(!row||Object.keys(row).sort().join(',')!=='entity,value')k.fail('InputType',s);const table=layout.tables.find(t=>t.entity===row.entity);if(!table)k.fail('UnknownReference',s);return pureSegment(token,()=>{const value=k.decode(row.value,{kind:'record',name:table!.entity},account,s);return {entity:table!.entity,bindings:encodeRow(p,table!,value).bindings};});});fixtureGrants.set(token,{repository:r.store,rows});const receipt=r.store.installFixture(token);r.current();return coreFreeze({...receipt,fuel_used:account.used});}catch(error){try{const f=k.failure(error,account);throw new GenericInputPreparationError(f.error,account.used);}catch(actual){throw actual;}}finally{retirePrepared(p);}}

import {assertGenericFixtureLoadInProgress,type GenericFixtureLoadHandle} from './fixture-loader.js';

/** Internal capability join: only an original runtime of this SDK/application.
 * Data projections and caller callbacks cannot create this custody. */
export function requireGenericCapabilityRuntimeBinding(runtime:GenericApplicationRuntime,owner:unknown,handle:GenericCompositionHandle){
 const r=runtime&&typeof runtime==='object'?runtimes.get(runtime):undefined;
 if(!r||r.owner!==owner||r.handle!==handle)fail('ForeignOwner',at,'capability context requires the original same-application runtime');
 r.current();if(!r.store)fail('UnsupportedCapability',at,'query capability requires original live store');const store=r.store;return {plans:r.plans,application:r.application,authorization:r.authorization,assertCurrent:r.current,captureSnapshot:()=>{r.current();return store.captureCapabilitySnapshot();},captureQuerySnapshot:(prepared:GenericPreparedInput)=>{r.current();return r.querySnapshot(prepared);},assertSnapshot:(snapshot:object)=>{r.current();return store.assertCapabilitySnapshot(snapshot);}};
}
