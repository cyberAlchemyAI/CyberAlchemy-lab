/** Original selected Entry through the real Auth bridge into source invocation.
 * This is a component join, not HTTP, command, effect, or V5 admission.
 * Open Questions: docs/COMMERCE-AUTH-READY-BRIDGE-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {isDeepStrictEqual,types as host} from 'node:util';
import {dataDigest} from '../profile-engine/contracts.js';
import {projectCoreServiceTopologyV1} from '../generic/core-topology-bridge.js';
import {assertCoreCommerceEventIngressAdmission,type CoreCommerceEventIngressAdmission,
 type CoreCommerceEventIngressTicket} from '../generic/core-commerce-event-ingress-admission.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {assertCommerceBindingAssemblyOwnerV1,type CommerceBindingAssemblyOwnerV1} from './commerce-binding-assembly-v1.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceAuthActorV1,type CommerceAuthEntryV1,type CommerceAuthInputV1} from './commerce-entry-context-v1.js';
import {createCommerceSourceInvocationOwnerV1,type CommerceSourceInvocationOwnerV1} from './commerce-source-invocation-owner-v1.js';
import {qualifiesCommerceEffectIntentV1} from './commerce-effect-intent-qualifier-v1.js';
import {evaluateCommerceFlowDataV1} from './commerce-flow-expression-data-v1.js';
import {assertCommerceWorkflowServiceStepAdmissionV1} from './commerce-workflow-service-step-admission-v1.js';
import {assertCommerceWorkflowWorkerStepAdmissionV1} from './commerce-workflow-worker-step-admission-v1.js';
import {inspectCommerceWorkflowAnyObservationAdmissionV1,type CommerceWorkflowAnyObservationAdmissionV1} from './commerce-workflow-observation-admission-any-v1.js';
import {deriveCommerceWorkflowDelegatedQueryV1} from './commerce-workflow-delegated-query-v1.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CommerceLocalPlanOwnerV1} from './commerce-local-plan-owner-v1.js';
import type {CommerceLocalOperationHandleV1} from './commerce-local-plan-owner-v1.js';
import type {CommerceServiceStorageOwnerV1,CommerceClaimJournalV1} from './commerce-service-storage-v1.js';
import type {CommerceWorkerContextOwnerV1,CommerceWorkerContextV1} from './commerce-worker-context-v1.js';
import type {CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import type {CommerceWorkflowProtectedCallBindingV1} from './commerce-workflow-protected-call-binding-v1.js';
import type {EffectPlanV1,OperationCallV1,FlowExprV1} from './commerce-data-v1.js';
import type {CommerceBindingAssemblyHandle,CommerceSourceHandle,CommerceOperationInvocationHandle} from './commerce-stages-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-binding-assembly-v1'+ext,'commerce-entry-context-v1'+ext,'commerce-source-invocation-owner-v1'+ext,'commerce-effect-intent-qualifier-v1'+ext,'commerce-flow-expression-data-v1'+ext,'commerce-workflow-service-step-admission-v1'+ext,'commerce-workflow-worker-step-admission-v1'+ext,'commerce-workflow-observation-admission-any-v1'+ext,'../generic/core-topology-bridge'+ext,'../generic/core-commerce-event-ingress-admission'+ext]);
const where={path:'selected-entry-auth',start:0,end:0};
export class CommerceSelectedScopedResourceNotFoundV1 extends Error {
 readonly code='ScopedResourceNotFound' as const;
 constructor(){super('original scoped resource condition is false');this.name='CommerceSelectedScopedResourceNotFoundV1';}
}
export type CommerceSelectedEntryStartV1=
 {readonly ok:true;readonly invocation:CommerceOperationInvocationHandle}|
 {readonly ok:false;readonly code:'unauthorized'|'forbidden';readonly status:401|403};
export interface CommerceSelectedDelegatedReadV1 {readonly kind:'original-selected-customer-delegation/v1-candidate'}
export interface CommerceSelectedEntryAuthOwnerV1 {
 begin(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,signal?:AbortSignal,delegation?:CommerceSelectedDelegatedReadV1):Promise<CommerceSelectedEntryStartV1>;
 beginEvent(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
  admission:CoreCommerceEventIngressAdmission,ticket:CoreCommerceEventIngressTicket,
  signal?:AbortSignal):Promise<CommerceSelectedEntryStartV1>;
 beginWorkflowServiceStep(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
  protectedCall:CommerceWorkflowProtectedCallBindingV1,signal?:AbortSignal):Promise<CommerceSelectedEntryStartV1>;
 beginWorkflowWorkerStep(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
  storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,
  protectedCall:CommerceWorkflowProtectedCallBindingV1,workerOwner:CommerceWorkerContextOwnerV1,
  workerContext:CommerceWorkerContextV1,signal?:AbortSignal):Promise<CommerceSelectedEntryStartV1>;
 beginWorkflowObservation(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
  storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,
  admission:CommerceWorkflowAnyObservationAdmissionV1,workerOwner:CommerceWorkerContextOwnerV1,
  workerContext:CommerceWorkerContextV1,signal?:AbortSignal):Promise<CommerceSelectedEntryStartV1>;
 beginWorker(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceClaimJournalV1,workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1,signal?:AbortSignal):Promise<CommerceSelectedEntryStartV1>;
 beginWorkerRead(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceClaimJournalV1,workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1,signal?:AbortSignal):Promise<CommerceSelectedEntryStartV1>;
 delegatedReadCallPath(parent:CommerceOperationInvocationHandle,targetEntry:string):string;
 issueDelegatedRead(parent:CommerceOperationInvocationHandle,sourcePath:string):CommerceSelectedDelegatedReadV1;
 registerServiceActor(entryId:string,actor:CommerceAuthActorV1):void;
 beginDelegatedQuery(parent:CommerceOperationInvocationHandle,sourcePath:string,signal?:AbortSignal,boundArguments?:Readonly<Record<string,unknown>>):Promise<CommerceSelectedEntryStartV1>;
 scopedDelegation(invocation:CommerceOperationInvocationHandle):Readonly<Record<string,unknown>>;
 assertScopedQueryRow(invocation:CommerceOperationInvocationHandle,queryId:string,sourceSha:string,exactRow:unknown):void;
 localCallPath(parent:CommerceOperationInvocationHandle,targetOperation:string):string;
 deriveLocalCall(parent:CommerceOperationInvocationHandle,sourcePath:string,boundArguments:unknown):CommerceOperationInvocationHandle;
 operation(invocation:CommerceOperationInvocationHandle):CommerceLocalOperationHandleV1;
 parameters(invocation:CommerceOperationInvocationHandle):ReturnType<CommerceSourceInvocationOwnerV1['parameters']>;
 principalIdentity(invocation:CommerceOperationInvocationHandle):ReturnType<CommerceSourceInvocationOwnerV1['principalIdentity']>;
 context(invocation:CommerceOperationInvocationHandle,sourcePath:string):ReturnType<CommerceSourceInvocationOwnerV1['context']>;
 workerObservation(invocation:CommerceOperationInvocationHandle,sourcePath:string,args:Parameters<CommerceSourceInvocationOwnerV1['workerObservation']>[2]):boolean;
 workerCommandIdentity(invocation:CommerceOperationInvocationHandle,transactionPath:string):ReturnType<CommerceSourceInvocationOwnerV1['workerCommandIdentity']>;
 isWorkflowObservationInvocation(invocation:CommerceOperationInvocationHandle):boolean;
 inspectWorkflowObservationCommitBinding(invocation:CommerceOperationInvocationHandle,transactionPath:string):ReturnType<CommerceSourceInvocationOwnerV1['inspectWorkflowObservationCommitBinding']>;
 withWorkerTransaction<T>(invocation:CommerceOperationInvocationHandle,storage:CommerceServiceStorageOwnerV1,transactionPath:string,execute:()=>T):T;
 assertSelectedLocalChild(child:CommerceOperationInvocationHandle,expectedRootEntry:string,expectedOperation:string):void;
 assertAssembly(owner:CommerceBindingAssemblyOwnerV1,assembly:CommerceBindingAssemblyHandle):void;
 inspectInvocation(invocation:CommerceOperationInvocationHandle):Readonly<Omit<ReturnType<CommerceSourceInvocationOwnerV1['inspect']>,'actual_business_resource_owners_qualified'|'qualification'>&{actual_business_resource_owners_qualified:boolean;qualification:string}>;
 retire(invocation:CommerceOperationInvocationHandle):void;
 inspect():Readonly<{kind:'original-selected-entry-auth/v1-candidate';source_capture_sha256:string;family_sha256:string;entries:number;native_basis_qualified:false;bound_application_qualified:false;qualification:'selected-source-entry-auth-and-invocation-component-only;transport-command-effects-pending';authority_effect:'none'}>;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function isCommerceSelectedEntryAuthOwnerV1(value:unknown):value is CommerceSelectedEntryAuthOwnerV1 {
 return !!value&&typeof value==='object'&&owners.has(value);
}
export function assertCommerceSelectedEntryAuthOwnerV1(owner:CommerceSelectedEntryAuthOwnerV1):void {
 if(!isCommerceSelectedEntryAuthOwnerV1(owner))fail('ForeignOwner',where,'original selected Entry/Auth owner required');owner.assertCurrent();
}

/** The actor must come from the existing private native Auth fixture issuer.
 * No application callback or fabricated authorization is accepted. */
export async function createCommerceSelectedEntryAuthOwnerV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 plans:CommerceLocalPlanOwnerV1,assemblyOwner:CommerceBindingAssemblyOwnerV1,assembly:CommerceBindingAssemblyHandle,
 auth:CommerceEntryContextOwnerV1,directory:string,
):Promise<CommerceSelectedEntryAuthOwnerV1> {
 assertCommerceBindingAssemblyOwnerV1(assemblyOwner);assemblyOwner.assertCurrent(assembly);assertCommerceEntryContextOwnerV1(auth);pin.assertCurrent();
 const selected=assemblyOwner.inspect(assembly).selection,topology=projectCoreServiceTopologyV1(sources,capture,semantics,semantic),sourceSha=stage.inspect(source).source_sha256;
 const sourceEntries=stage.moduleContracts(source).flatMap(module=>module.entries);
 if(selected.source_capture_sha256!==sourceSha||selected.topology_sha256!==dataDigest(topology)||auth.inspect().source_sha256!==sourceSha)
  fail('ForeignOwner',where,'selected assembly, original source and Auth owner must match');
 if(!selected.native_requirements.some(r=>r.primitive_id==='auth-ready-bridge'))fail('UnsupportedCapability',where,'selected Auth primitive required');
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)fail('InvalidContract',where,'absolute invocation directory required');
 const invocations=await createCommerceSourceInvocationOwnerV1(stage,source,domain,baseline,plans,auth,directory);
 const effectPlans=new Map<string,EffectPlanV1>();
 const effectPlan=(id:string)=>{let plan=effectPlans.get(id);if(!plan){const bound=plans.bindOperation(id);try{plan=plans.inspectOperation(bound).plan;effectPlans.set(id,plan);}finally{plans.disposeOperation(bound);}}return plan;};
 const issued=new WeakMap<object,{entry:CommerceAuthEntryV1;input:CommerceAuthInputV1;root:CommerceOperationInvocationHandle;kind:'root'|'child';resourceQualified:boolean;scopedProjection:Readonly<Record<string,unknown>>|null;
  workflowStep?:{storage:CommerceServiceStorageOwnerV1;binding:CommerceWorkflowCoordinationBindingV1;protectedCall:CommerceWorkflowProtectedCallBindingV1}}>();
 const delegations=new WeakMap<object,{parent:CommerceOperationInvocationHandle;entry:string;arguments:Readonly<Record<string,unknown>>;projection:Readonly<Record<string,unknown>>;used:boolean}>();
 const serviceActors=new Map<string,CommerceAuthActorV1>();
 let disposed=false;
 // The immutable assembly selection was compared with this original topology
 // at construction. Its currentness check already pins the source and semantic
 // owners, so rebuilding the full topology at every invocation repeats the
 // same source walk without detecting an additional kind of change.
 const current=()=>{if(disposed)fail('DisposedOwner',where,'selected Entry/Auth owner disposed');pin.assertCurrent();assemblyOwner.assertCurrent(assembly);invocations.assertCurrent();};
 const live=(h:CommerceOperationInvocationHandle)=>{current();const row=h&&typeof h==='object'?issued.get(h):undefined;if(!row)fail('ForeignOwner',where,'selected original invocation required');return row;};
 const callAt=(parent:CommerceOperationInvocationHandle,sourcePath:string):OperationCallV1=>{
  live(parent);if(typeof sourcePath!=='string'||sourcePath.length>8192)fail('InvalidContract',where,'bounded source call path required');
  const plan=plans.inspectOperation(invocations.operation(parent)).plan,found=new Map<string,unknown>();let nodes=0;
  const visit=(value:unknown,at:string,depth:number):void=>{if(!value||typeof value!=='object')return;if(++nodes>65536||depth>128)fail('InvalidContract',where,'bounded source call traversal required');found.set(at,value);if(Array.isArray(value))value.forEach((item,index)=>visit(item,at+'['+index+']',depth+1));else for(const [key,item] of Object.entries(value))visit(item,at+'.'+key,depth+1);};
  visit(plan,'$',0);const call=found.get(sourcePath) as OperationCallV1|undefined;
  if(!call||!Array.isArray(call.arguments)||!Array.isArray(call.contexts)||call.role!=='Query'||call.authorization!=='fresh-original-entry-decision-required'||!call.entry)fail('ForeignOwner',where,'exact source-owned delegated Query call required');
  return call;
 };
 const inspection=coreFreeze({kind:'original-selected-entry-auth/v1-candidate' as const,source_capture_sha256:sourceSha,family_sha256:selected.family_sha256,entries:topology.entries.length,native_basis_qualified:false as const,bound_application_qualified:false as const,qualification:'selected-source-entry-auth-and-invocation-component-only;transport-command-effects-pending' as const,authority_effect:'none' as const});
 const owner:CommerceSelectedEntryAuthOwnerV1=Object.freeze({
  async begin(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,signal?:AbortSignal,delegation?:CommerceSelectedDelegatedReadV1){
   current();const declaration=topology.entries.find(e=>e.id===entryId);
   if(!declaration||!selected.services.some(s=>s.id===declaration.service)||!['Operation','Query'].includes(declaration.target_role))fail('ForeignOwner',where,'selected request Entry required');
   if(host.isProxy(wire)||!(wire instanceof Uint8Array))fail('InvalidContract',where,'original byte input required');
   const entry=auth.bindEntry(entryId),actual=auth.inspectEntry(entry);
   if(actual.service!==declaration.service||actual.invokes.module+'.'+actual.invokes.name!==declaration.target||actual.access.auth_route_id!==declaration.auth_route_id)
    fail('ForeignOwner',where,'original Auth Entry must match selected topology');
   const input=auth.prepareInput(entry,wire);
   try{
    let scopedProjection:Readonly<Record<string,unknown>>|null=null;
    if(delegation){const row=delegations.get(delegation);if(!row||row.used)fail('ForeignOwner',where,'fresh original selected delegation required');row.used=true;live(row.parent);
     if(row.entry!==entryId||actual.access.resource_phase!=='scoped-read-before-response'||!auth.matchesPreparedInput(input,row.arguments)){
      auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }scopedProjection=row.projection;
    }
    const decision=await auth.authorizeCommerceEntry(actor,entry,input,signal);current();
    if(!decision.ok){auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze(decision);}
    const authorization=await auth.consumeCommerceEntryContext(decision.value,entry,input,signal);current();
    const resource=auth.inspectInvocation(authorization),requiresResource=actual.access.resource_bindings.length>0||actual.access.resource_condition!==null;
    const scope=auth.inspectScope(auth.principalScope(authorization));
    const effectIntentQualified=requiresResource&&actual.access.resource_phase==='fresh-intent-before-effects'&&
     qualifiesCommerceEffectIntentV1(actual,effectPlan(declaration.target),scope);
    const resourceQualified=resource.actual_business_resource_owners_qualified===true||effectIntentQualified;
    const direct=actual.access.resource_bindings.find(binding=>binding.origin.kind==='current-invocation');
    const directScoped=!delegation&&!resourceQualified&&actual.invokes.role==='Query'&&
     actual.access.principal_kind==='customer'&&scope.kind==='customer'&&
     actual.access.resource_phase==='scoped-read-before-response'&&actual.access.resource_bindings.length===2&&
     actual.access.resource_condition!==null&&
     actual.access.resource_bindings.some(binding=>binding.origin.kind==='scoped-query-row')&&
     direct?.type.kind==='private-projection'&&direct.type.source_type===actual.access.context.source_type&&
     direct.type.abi===actual.access.context.abi&&direct.abi===actual.access.context.abi&&
     dataDigest(direct.fields)===dataDigest(direct.type.fields)&&
     direct.required_fields.includes('customerId')&&
     direct.required_fields.every(name=>Object.hasOwn(direct.fields,name)&&Object.hasOwn(scope,name))&&
     typeof scope.customerId==='string'&&scope.customerId.length>0;
    if(directScoped){
     const projection:Record<string,unknown>=Object.create(null);
     for(const name of Object.keys(direct.fields)){
      if(!Object.hasOwn(scope,name))fail('ForeignOwner',where,'original customer scope field required');
      projection[name]=scope[name];
     }
     scopedProjection=coreFreeze(projection);
    }
    const scopedPending=!resourceQualified&&scopedProjection!==null&&actual.invokes.role==='Query'&&
     actual.access.resource_phase==='scoped-read-before-response'&&actual.access.resource_bindings.length===2&&
     actual.access.resource_condition!==null&&
     actual.access.resource_bindings.some(binding=>binding.origin.kind==='scoped-query-row')&&
     (directScoped||!!delegation&&actual.access.resource_bindings.some(binding=>binding.origin.kind==='parent-customer-delegation'));
    if(requiresResource&&!resourceQualified&&!scopedPending){
     auth.disposeInput(input);auth.disposeEntry(entry);
     return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
    }
    const invocation=invocations.begin(authorization,parameters),view=invocations.inspect(invocation);
    if(view.entry!==entryId||view.service!==declaration.service||view.operation!==declaration.target||view.source_sha256!==sourceSha)
     fail('ForeignOwner',where,'authorized source invocation must match selected Entry');
    issued.set(invocation,{entry,input,root:invocation,kind:'root',resourceQualified,scopedProjection});return coreFreeze({ok:true as const,invocation});
   }catch(error){auth.disposeInput(input);auth.disposeEntry(entry);throw error;}
  },
  async beginEvent(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
   admission:CoreCommerceEventIngressAdmission,ticket:CoreCommerceEventIngressTicket,signal?:AbortSignal){
   current();assertCoreCommerceEventIngressAdmission(admission);
   const observed=admission.inspectTicket(ticket),declaration=topology.entries.find(row=>row.id===entryId);
   if(entryId!==observed.entry||!declaration||declaration.interaction!=='event'||
    declaration.target_role!=='Operation'||declaration.target!==observed.operation||
    declaration.service!==observed.receiver_service||!selected.services.some(service=>service.id===declaration.service)||
    !isDeepStrictEqual(parameters,observed.parameters))
    fail('ForeignOwner',where,'original selected Event occurrence and Entry required');
   if(host.isProxy(wire)||!(wire instanceof Uint8Array))fail('InvalidContract',where,'original byte input required');
   const entry=auth.bindEntry(entryId),actual=auth.inspectEntry(entry);
   try{
    if(actual.service!==declaration.service||actual.interaction!=='event'||
     actual.invokes.module+'.'+actual.invokes.name!==declaration.target||
     actual.access.auth_route_id!==declaration.auth_route_id||
     actual.access.principal_kind!=='service'||actual.access.caller!==observed.producer_service||
     actual.access.producer!==observed.producer_service||
     actual.access.resource_phase!=='causal-before-invocation'||
     actual.access.event_completion!=='requires-original-consumer-inbox-and-result-commit')
     fail('ForeignOwner',where,'original Event Auth Entry must match selected occurrence');
    const input=auth.prepareInput(entry,wire);
    try{
     if(!auth.matchesPreparedInput(input,observed.parameters)){
      auth.disposeInput(input);auth.disposeEntry(entry);
      return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }
     const decision=await auth.authorizeCommerceEntry(actor,entry,input,signal);current();admission.inspectTicket(ticket);
     if(!decision.ok){auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze(decision);}
     const authorization=await auth.consumeCommerceEntryContext(decision.value,entry,input,signal);current();
     const refreshed=admission.inspectTicket(ticket),scope=auth.inspectScope(auth.principalScope(authorization));
     if(scope.kind!=='service'||scope.serviceId!==refreshed.producer_service||
      scope.currentEntryId!==entryId||scope.currentActionAllowed!==true||
      !isDeepStrictEqual(parameters,refreshed.parameters)){
      auth.disposeInput(input);auth.disposeEntry(entry);
      return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }
     const invocation=invocations.begin(authorization,parameters),view=invocations.inspect(invocation);
     if(view.entry!==entryId||view.service!==declaration.service||view.operation!==declaration.target||
      view.role!=='Operation'||view.source_sha256!==sourceSha)
      fail('ForeignOwner',where,'authorized Event invocation must match original Entry');
     issued.set(invocation,{entry,input,root:invocation,kind:'root',resourceQualified:true,scopedProjection:null});
     return coreFreeze({ok:true as const,invocation});
    }catch(error){auth.disposeInput(input);throw error;}
   }catch(error){auth.disposeEntry(entry);throw error;}
  },
  async beginWorkflowServiceStep(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
   protectedCall:CommerceWorkflowProtectedCallBindingV1,signal?:AbortSignal){
   current();const declaration=topology.entries.find(e=>e.id===entryId);
   if(!declaration||!selected.services.some(s=>s.id===declaration.service)||
    !['Operation','Query'].includes(declaration.target_role))
    fail('ForeignOwner',where,'selected protected service Entry required');
   if(host.isProxy(wire)||!(wire instanceof Uint8Array))fail('InvalidContract',where,'original byte input required');
   const entry=auth.bindEntry(entryId),actual=auth.inspectEntry(entry);
   try{
    if(actual.service!==declaration.service||actual.invokes.module+'.'+actual.invokes.name!==declaration.target||
     actual.access.auth_route_id!==declaration.auth_route_id)
     fail('ForeignOwner',where,'original Auth Entry must match selected topology');
    const call=assertCommerceWorkflowServiceStepAdmissionV1(actual,sourceSha,protectedCall);
    const input=auth.prepareInput(entry,wire);
    try{
     if(!auth.matchesPreparedInput(input,call.arguments)){
      auth.disposeInput(input);auth.disposeEntry(entry);
      return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }
     // The native Auth decision is bound to this Entry and canonical input.
     // Recheck the protected Workflow call after context consumption, before
     // issuing any service invocation; another deep walk here would repeat it.
     const decision=await auth.authorizeCommerceEntry(actor,entry,input,signal);current();
     if(!decision.ok){auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze(decision);}
     const authorization=await auth.consumeCommerceEntryContext(decision.value,entry,input,signal);current();
     const refreshed=protectedCall.recheck(),scope=auth.inspectScope(auth.principalScope(authorization));
     if(scope.kind!=='service'||scope.serviceId!==refreshed.caller_service){
      auth.disposeInput(input);auth.disposeEntry(entry);
      return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }
     const invocation=invocations.begin(authorization,parameters),view=invocations.inspect(invocation);
     if(view.entry!==entryId||view.service!==declaration.service||view.operation!==declaration.target||
      view.role!==refreshed.role||view.source_sha256!==sourceSha)
      fail('ForeignOwner',where,'authorized service invocation must match original Workflow call');
     issued.set(invocation,{entry,input,root:invocation,kind:'root',resourceQualified:true,scopedProjection:null});
     return coreFreeze({ok:true as const,invocation});
    }catch(error){auth.disposeInput(input);throw error;}
   }catch(error){auth.disposeEntry(entry);throw error;}
  },
  async beginWorkflowWorkerStep(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
   storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,
   protectedCall:CommerceWorkflowProtectedCallBindingV1,workerOwner:CommerceWorkerContextOwnerV1,
   workerContext:CommerceWorkerContextV1,signal?:AbortSignal){
   current();storage.assertSelectedAssembly(owner);
   const declaration=topology.entries.find(candidate=>candidate.id===entryId);
   if(!declaration||!selected.services.some(service=>service.id===declaration.service)||
    !['Operation','Query'].includes(declaration.target_role))
    fail('ForeignOwner',where,'selected protected worker Operation or Query Entry required');
   if(host.isProxy(wire)||!(wire instanceof Uint8Array))fail('InvalidContract',where,'original byte input required');
   const entry=auth.bindEntry(entryId),actual=auth.inspectEntry(entry);
   try{
    if(actual.service!==declaration.service||actual.invokes.module+'.'+actual.invokes.name!==declaration.target||
     actual.access.auth_route_id!==declaration.auth_route_id)
     fail('ForeignOwner',where,'original worker Auth Entry must match selected topology');
    const call=assertCommerceWorkflowWorkerStepAdmissionV1(actual,sourceSha,protectedCall,storage,workerOwner,workerContext);
    if(binding.inspect().workflow.name!==call.workflow)fail('ForeignOwner',where,'original Workflow binding required');
    const input=auth.prepareInput(entry,wire);
    try{
     if(!auth.matchesPreparedInput(input,call.arguments)){
      auth.disposeInput(input);auth.disposeEntry(entry);
      return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }
     const decision=await auth.authorizeCommerceEntry(actor,entry,input,signal);current();protectedCall.recheck();
     if(!decision.ok){auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze(decision);}
     const authorization=await auth.consumeCommerceEntryContext(decision.value,entry,input,signal);current();
     const scope=auth.inspectScope(auth.principalScope(authorization)),refreshed=protectedCall.recheck();
     if(scope.kind!=='service'||scope.serviceId!==refreshed.caller_service){
      auth.disposeInput(input);auth.disposeEntry(entry);
      return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }
     const invocation=invocations.beginWorkflowWorkerStep(authorization,parameters,storage,binding,
      protectedCall,workerOwner,workerContext),view=invocations.inspect(invocation);
     if(view.entry!==entryId||view.service!==declaration.service||view.operation!==declaration.target||
      view.role!==refreshed.role||view.source_sha256!==sourceSha)
      fail('ForeignOwner',where,'authorized worker invocation must match original Workflow step');
     issued.set(invocation,{entry,input,root:invocation,kind:'root',resourceQualified:true,scopedProjection:null,
      workflowStep:{storage,binding,protectedCall}});
     return coreFreeze({ok:true as const,invocation});
    }catch(error){auth.disposeInput(input);throw error;}
   }catch(error){auth.disposeEntry(entry);throw error;}
  },
  async beginWorkflowObservation(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
   storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,
   admission:CommerceWorkflowAnyObservationAdmissionV1,workerOwner:CommerceWorkerContextOwnerV1,
   workerContext:CommerceWorkerContextV1,signal?:AbortSignal){
   current();storage.assertSelectedAssembly(owner);
   const observed=inspectCommerceWorkflowAnyObservationAdmissionV1(admission).inspection,
    declaration=topology.entries.find(candidate=>candidate.id===entryId);
   if(entryId!==observed.entry_id||!declaration||!selected.services.some(service=>service.id===declaration.service)||
    declaration.target_role!=='Operation'||declaration.target!==observed.target||declaration.service!=='orders'||
    observed.source_capture_sha256!==sourceSha||binding.inspect().workflow.name!==observed.workflow)
    fail('ForeignOwner',where,'original selected observation Entry and admitted Workflow required');
   if(host.isProxy(wire)||!(wire instanceof Uint8Array))fail('InvalidContract',where,'original byte input required');
   const entry=auth.bindEntry(entryId),actual=auth.inspectEntry(entry);
   try{
    if(actual.service!==declaration.service||actual.invokes.module+'.'+actual.invokes.name!==observed.target||
     actual.access.auth_route_id!==declaration.auth_route_id||
     actual.access.worker_lifetime!=='requires-original-local-worker-owner'||
     actual.access.resource_bindings.length!==1||actual.access.resource_bindings[0]!.origin.kind!=='worker-observation')
     fail('ForeignOwner',where,'original observation Entry must match selected topology');
    const input=auth.prepareInput(entry,wire);
    try{
     if(!auth.matchesPreparedInput(input,observed.input)){
      auth.disposeInput(input);auth.disposeEntry(entry);
      return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }
     const decision=await auth.authorizeCommerceEntry(actor,entry,input,signal);
     current();admission.assertCurrent();
     if(!decision.ok){auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze(decision);}
     const authorization=await auth.consumeCommerceEntryContext(decision.value,entry,input,signal);
     current();admission.assertCurrent();
     const scope=auth.inspectScope(auth.principalScope(authorization));
     if(scope.kind!=='service'||scope.serviceId!==actual.access.caller){
      auth.disposeInput(input);auth.disposeEntry(entry);
      return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
     }
     const invocation=await invocations.beginWorkflowObservation(authorization,parameters,storage,binding,
      admission,workerOwner,workerContext),view=invocations.inspect(invocation);
     if(view.entry!==entryId||view.service!==declaration.service||view.operation!==observed.target||
      view.role!=='Operation'||view.source_sha256!==sourceSha)
      fail('ForeignOwner',where,'authorized observation invocation must match original Workflow');
     issued.set(invocation,{entry,input,root:invocation,kind:'root',resourceQualified:true,scopedProjection:null});
     return coreFreeze({ok:true as const,invocation});
    }catch(error){auth.disposeInput(input);throw error;}
   }catch(error){auth.disposeEntry(entry);throw error;}
  },
  async beginWorker(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
   storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceClaimJournalV1,workerOwner:CommerceWorkerContextOwnerV1,
   workerContext:CommerceWorkerContextV1,signal?:AbortSignal){
   current();storage.assertSelectedAssembly(owner);const declaration=topology.entries.find(e=>e.id===entryId);
   if(!declaration||!selected.services.some(s=>s.id===declaration.service)||declaration.target_role!=='Operation')
    fail('ForeignOwner',where,'selected worker Operation Entry required');
   if(host.isProxy(wire)||!(wire instanceof Uint8Array))fail('InvalidContract',where,'original byte input required');
   const entry=auth.bindEntry(entryId),actual=auth.inspectEntry(entry);
   if(actual.service!==declaration.service||actual.invokes.module+'.'+actual.invokes.name!==declaration.target||
    actual.access.auth_route_id!==declaration.auth_route_id||actual.access.worker_lifetime!=='requires-original-local-worker-owner')
    fail('ForeignOwner',where,'original worker Entry must match selected topology');
   const input=auth.prepareInput(entry,wire);
   try{
    const decision=await auth.authorizeCommerceEntry(actor,entry,input,signal);current();
    if(!decision.ok){auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze(decision);}
    const authorization=await auth.consumeCommerceEntryContext(decision.value,entry,input,signal);current();
    const invocation=await invocations.beginWorker(authorization,parameters,storage,binding,journal,workerOwner,workerContext),view=invocations.inspect(invocation);
    if(view.entry!==entryId||view.service!==declaration.service||view.operation!==declaration.target||view.source_sha256!==sourceSha)
     fail('ForeignOwner',where,'authorized worker invocation must match selected source Entry');
    issued.set(invocation,{entry,input,root:invocation,kind:'root',resourceQualified:true,scopedProjection:null});
    return coreFreeze({ok:true as const,invocation});
   }catch(error){auth.disposeInput(input);auth.disposeEntry(entry);throw error;}
  },
  async beginWorkerRead(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
   storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceClaimJournalV1,workerOwner:CommerceWorkerContextOwnerV1,
   workerContext:CommerceWorkerContextV1,signal?:AbortSignal){
   current();storage.assertSelectedAssembly(owner);const declaration=topology.entries.find(e=>e.id===entryId);
   if(!declaration||!selected.services.some(s=>s.id===declaration.service)||declaration.target_role!=='Query')
    fail('ForeignOwner',where,'selected worker Query Entry required');
   if(host.isProxy(wire)||!(wire instanceof Uint8Array))fail('InvalidContract',where,'original byte input required');
   const entry=auth.bindEntry(entryId),actual=auth.inspectEntry(entry);
   if(actual.service!==declaration.service||actual.invokes.module+'.'+actual.invokes.name!==declaration.target||
    actual.access.auth_route_id!==declaration.auth_route_id||actual.access.worker_lifetime!=='requires-original-local-worker-owner')
    fail('ForeignOwner',where,'original worker Query Entry must match selected topology');
   const input=auth.prepareInput(entry,wire);
   try{
    const decision=await auth.authorizeCommerceEntry(actor,entry,input,signal);current();
    if(!decision.ok){auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze(decision);}
    const authorization=await auth.consumeCommerceEntryContext(decision.value,entry,input,signal);current();
    const invocation=await invocations.beginWorkerRead(authorization,parameters,storage,binding,journal,workerOwner,workerContext),
     view=invocations.inspect(invocation);
    if(view.entry!==entryId||view.service!==declaration.service||view.operation!==declaration.target||view.role!=='Query'||view.source_sha256!==sourceSha)
     fail('ForeignOwner',where,'authorized worker Query invocation must match selected source Entry');
    issued.set(invocation,{entry,input,root:invocation,kind:'root',resourceQualified:true,scopedProjection:null});
    return coreFreeze({ok:true as const,invocation});
   }catch(error){auth.disposeInput(input);auth.disposeEntry(entry);throw error;}
  },
  delegatedReadCallPath(parent:CommerceOperationInvocationHandle,targetEntry:string){
   const row=live(parent);if(row.kind!=='root'||!row.resourceQualified)fail('ForeignOwner',where,'qualified selected parent root required');
   const plan=plans.inspectOperation(invocations.operation(parent)).plan,found:string[]=[];let nodes=0;
   const visit=(value:unknown,at:string,depth:number):void=>{if(!value||typeof value!=='object')return;if(++nodes>65536||depth>128)fail('InvalidContract',where,'bounded source traversal required');if(!Array.isArray(value)&&'arguments'in value&&'authorization'in value&&'role'in value){const call=value as Partial<OperationCallV1>;if(call.entry===targetEntry&&call.role==='Query'&&call.authorization==='fresh-original-entry-decision-required')found.push(at);}if(Array.isArray(value))value.forEach((item,index)=>visit(item,at+'['+index+']',depth+1));else for(const [key,item] of Object.entries(value))visit(item,at+'.'+key,depth+1);};
   visit(plan,'$',0);if(found.length!==1)fail('MissingMapping',where,'one exact delegated Query call required');return found[0]!;
  },
  issueDelegatedRead(parent:CommerceOperationInvocationHandle,sourcePath:string){
   const row=live(parent);if(row.kind!=='root'||!row.resourceQualified)fail('ForeignOwner',where,'qualified selected parent root required');
   const call=callAt(parent,sourcePath),target=sourceEntries.find(entry=>entry.id===call.entry);
   if(!target||target.invokes.role!=='Query'||target.invokes.module+'.'+target.invokes.name!==call.target||target.service===invocations.inspect(parent).service||target.access.caller!==invocations.inspect(parent).service||target.access.resource_phase!=='scoped-read-before-response')
    fail('ForeignOwner',where,'selected cross-service Query Entry and caller required');
   const causal=target.access.resource_bindings.find(binding=>binding.origin.kind==='parent-customer-delegation');
   if(!causal||causal.required_fields.length===0||call.arguments.length!==target.parameters.length)fail('MissingMapping',where,'source-bound parent customer delegation required');
   const parameters=invocations.parameters(parent),args:Record<string,unknown>=Object.create(null),projection:Record<string,unknown>=Object.create(null);let fuel=0;
   for(const [index,argument]of call.arguments.entries()){
    if(!target.parameters.some(parameter=>parameter.name===argument.parameter)||Object.hasOwn(args,argument.parameter))fail('MissingMapping',where,'exact target Entry argument required');
    const at=sourcePath+'.arguments['+index+'].value.expression';
    args[argument.parameter]=evaluateCommerceFlowDataV1(argument.value.expression,at,parameters,{
     charge(){if(++fuel>4096)fail('InvalidContract',where,'bounded source arguments required');},
     pure(){return fail('MissingMapping',where,'delegated argument needs original pure owner');},native(){return fail('MissingMapping',where,'delegated argument needs original native owner');},
     context(sourceAt){return invocations.context(parent,sourceAt);},isNullaryEnum(){return false;},
    });
   }
   for(const name of causal.required_fields){const argument=call.arguments.find(item=>item.parameter===name),expr=argument?.value.expression;
    if(!argument||!expr||expr.op!=='field'||expr.value.op!=='private_context'||expr.field!==name||!Object.hasOwn(args,name))
     fail('MissingMapping',where,'causal field must come from exact native parent context at source call');
    const contextNode=expr.value;
    if(!plans.inspectOperation(invocations.operation(parent)).plan.contexts.some(context=>context.binding===contextNode.binding&&context.source_type===contextNode.source_type&&context.abi===contextNode.abi))
     fail('MissingMapping',where,'causal field requires original native parent context');
    projection[name]=args[name];
   }
   const token=Object.freeze({kind:'original-selected-customer-delegation/v1-candidate' as const});
   delegations.set(token,{parent,entry:target.id,arguments:coreFreeze(args),projection:coreFreeze(projection),used:false});return token;
  },
  registerServiceActor(entryId:string,actor:CommerceAuthActorV1){
   current();auth.assertActor(actor);const assignment=auth.inspectActor(actor),entry=sourceEntries.find(candidate=>candidate.id===entryId),target=topology.entries.find(candidate=>candidate.id===entryId);
   if(!entry||!target||entry.access.principal_kind!=='service'||entry.invokes.role!=='Query'||target.target_role!=='Query'||!selected.services.some(service=>service.id===entry.service))
    fail('ForeignOwner',where,'selected service Query Entry required for native actor registration');
   if(assignment.principal_kind!=='service'||assignment.service_id!==entry.access.caller||assignment.scope!==entry.access.auth_permission.scope)
    fail('ForeignOwner',where,'native service actor must match the checked Entry caller and scope');
   const previous=serviceActors.get(entryId);if(previous&&previous!==actor)fail('ForeignOwner',where,'selected service actor cannot be replaced');
   serviceActors.set(entryId,actor);
  },
  async beginDelegatedQuery(parent:CommerceOperationInvocationHandle,sourcePath:string,signal?:AbortSignal,
   boundArguments?:Readonly<Record<string,unknown>>){
   const call=callAt(parent,sourcePath),entryId=call.entry!,actor=serviceActors.get(entryId),
    target=sourceEntries.find(candidate=>candidate.id===entryId);
   if(!actor||!target)fail('MissingMapping',where,'original native service actor and source Query Entry required');
   auth.assertActor(actor);
   if(target.access.resource_phase==='causal-before-invocation'){
    const parentRow=live(parent),workflow=parentRow.workflowStep;
    if(parentRow.kind!=='root'||!parentRow.resourceQualified||!workflow||
     target.invokes.role!=='Query'||target.invokes.module+'.'+target.invokes.name!==call.target||
     call.arguments.length!==target.parameters.length||!boundArguments)
     fail('ForeignOwner',where,'source-selected Workflow parent and checked Query arguments required');
    const proof=deriveCommerceWorkflowDelegatedQueryV1(workflow.protectedCall,workflow.binding,
     workflow.storage,target,sourceSha,boundArguments);
    const declaration=topology.entries.find(candidate=>candidate.id===entryId),entry=auth.bindEntry(entryId);
    try{
     const actual=auth.inspectEntry(entry);
     if(!declaration||declaration.target_role!=='Query'||declaration.target!==call.target||
      declaration.service!==target.service||actual.service!==declaration.service||
      actual.invokes.module+'.'+actual.invokes.name!==declaration.target||
      actual.access.auth_route_id!==declaration.auth_route_id)
      fail('ForeignOwner',where,'selected causal Query must match original Auth Entry');
     const wire=auth.encodeEntryArguments(entry,proof.arguments),input=auth.prepareInput(entry,wire);
     try{
      if(!auth.matchesPreparedInput(input,proof.arguments)){
       auth.disposeInput(input);auth.disposeEntry(entry);
       return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
      }
      proof.recheck();
      const decision=await auth.authorizeCommerceEntry(actor,entry,input,signal);current();proof.recheck();
      if(!decision.ok){auth.disposeInput(input);auth.disposeEntry(entry);return coreFreeze(decision);}
      const authorization=await auth.consumeCommerceEntryContext(decision.value,entry,input,signal);
      current();proof.recheck();
      const scope=auth.inspectScope(auth.principalScope(authorization));
      if(scope.kind!=='service'||scope.serviceId!==workflow.protectedCall.recheck().caller_service||
       scope.targetServiceId!==target.service){
       auth.disposeInput(input);auth.disposeEntry(entry);
       return coreFreeze({ok:false as const,code:'forbidden' as const,status:403 as const});
      }
      const invocation=invocations.begin(authorization,proof.arguments),view=invocations.inspect(invocation);
      if(view.entry!==entryId||view.service!==target.service||view.operation!==call.target||
       view.role!=='Query'||view.source_sha256!==sourceSha)
       fail('ForeignOwner',where,'fresh authorized service Query invocation must retain source identity');
      issued.set(invocation,{entry,input,root:invocation,kind:'root',resourceQualified:true,scopedProjection:null});
      return coreFreeze({ok:true as const,invocation});
     }catch(error){auth.disposeInput(input);throw error;}
    }catch(error){auth.disposeEntry(entry);throw error;}
   }
   const token=owner.issueDelegatedRead(parent,sourcePath),delegation=delegations.get(token)!;
   const entry=auth.bindEntry(entryId);let wire:Uint8Array;
   try{wire=auth.encodeEntryArguments(entry,delegation.arguments);}finally{auth.disposeEntry(entry);}
   return owner.begin(actor,entryId,wire,delegation.arguments,signal,token);
  },
  scopedDelegation(h:CommerceOperationInvocationHandle){const row=live(h);if(row.kind!=='root'||row.scopedProjection===null||
    !auth.inspectEntry(row.entry).access.resource_bindings.some(binding=>binding.origin.kind==='parent-customer-delegation'))
    fail('ForeignOwner',where,'selected scoped Query delegation required');return row.scopedProjection;},
  assertScopedQueryRow(h:CommerceOperationInvocationHandle,queryId:string,sourceHash:string,exactRow:unknown){
   const row=live(h),view=invocations.inspect(h),entry=auth.inspectEntry(row.entry);
   if(row.kind!=='root'||row.scopedProjection===null||view.role!=='Query'||view.operation!==queryId||view.source_sha256!==sourceHash||sourceHash!==sourceSha||
      entry.access.resource_phase!=='scoped-read-before-response'||entry.access.resource_bindings.length!==2||!entry.access.resource_condition)
    fail('ForeignOwner',where,'live selected scoped Query and original resource condition required');
   const causal=entry.access.resource_bindings.find(binding=>binding.origin.kind==='parent-customer-delegation'||binding.origin.kind==='current-invocation');
   const stored=entry.access.resource_bindings.find(binding=>binding.origin.kind==='scoped-query-row');
   if(causal?.origin.kind==='current-invocation'){
    const principal=invocations.principalIdentity(h);
    if(entry.access.principal_kind!=='customer'||causal.type.kind!=='private-projection'||
       causal.type.source_type!==entry.access.context.source_type||causal.type.abi!==entry.access.context.abi||
       causal.abi!==entry.access.context.abi||dataDigest(causal.fields)!==dataDigest(causal.type.fields)||
       principal.kind!=='customer'||row.scopedProjection.customerId!==principal.id)
     fail('ForeignOwner',where,'original customer context must own the direct scoped resource');
   }
   if(!causal||!stored||stored.origin.declaration!==queryId||!stored.origin.binding||!exactRow||typeof exactRow!=='object'||host.isProxy(exactRow)||Array.isArray(exactRow)||
      ![Object.prototype,null].includes(Object.getPrototypeOf(exactRow)))fail('ForeignOwner',where,'exact selected row shape required');
   const descriptors=Object.getOwnPropertyDescriptors(exactRow);
   if(stored.required_fields.some(name=>!descriptors[name]?.enumerable||!Object.hasOwn(descriptors[name]!,'value'))||
      causal.required_fields.some(name=>!Object.hasOwn(row.scopedProjection!,name)))fail('ForeignOwner',where,'required original resource fields missing');
   let fuel=0,nodes=0,privateContextSeen=false;
   const inputRecord=entry.id+'.CoreEntryInput',causalRecord=entry.id+'.CorePrivateResource.'+causal.name;
   const expected=new Map<string,unknown>([[inputRecord,Object.fromEntries(entry.parameters.map(parameter=>[parameter.name,parameter.type]))]]);
   if(causal.origin.kind==='parent-customer-delegation')expected.set(causalRecord,causal.fields);
   const required=new Set<string>();
   const scan=(value:FlowExprV1,depth:number):void=>{if(++nodes>4096||depth>64)fail('InvalidContract',where,'bounded Entry resource condition required');
    if(value.op==='field'){scan(value.value,depth+1);return;}
    if(value.op==='var'){
     if(!['input',causal.name,stored.name].includes(value.name)||
        value.name===causal.name&&causal.origin.kind!=='parent-customer-delegation')
      fail('MissingMapping',where,'condition reads an unbound resource');
     if(value.name==='input')required.add(inputRecord);
     if(value.name===causal.name)required.add(causalRecord);
     return;
    }
    if(value.op==='private_context'){
     if(causal.origin.kind!=='current-invocation'||value.binding!==causal.name||
        value.source_type!==entry.access.context.source_type||value.abi!==entry.access.context.abi||
        value.public_constructor!==false||value.custody!=='required-from-original-native-owner'||
        dataDigest(value.fields)!==dataDigest(causal.fields))
      fail('ForeignOwner',where,'only the exact original invocation context may evaluate scoped access');
     privateContextSeen=true;return;
    }
    if(value.op==='binary'&&['eq','and'].includes(value.operator)){scan(value.left,depth+1);scan(value.right,depth+1);return;}
    fail('MissingMapping',where,'unsupported scoped resource condition');
   };
   scan(entry.access.resource_condition.expression,0);
   if(causal.origin.kind==='current-invocation'&&!privateContextSeen||
      causal.origin.kind==='parent-customer-delegation'&&!required.has(causalRecord))
    fail('ForeignOwner',where,'checked causal resource is absent from the scoped condition');
   const records=entry.access.resource_condition.local_records;
   if(records.length!==required.size||records.some(record=>record.public_constructor!==false||
      record.qualification!=='source-local-projection-data-only'||!required.has(record.name)||
      !expected.has(record.name)||dataDigest(record.fields)!==dataDigest(expected.get(record.name))))
    fail('ForeignOwner',where,'only exact used input and causal projection records may evaluate scoped access');
   const env:Record<string,unknown>=Object.create(null);env.input=invocations.parameters(h);
   if(causal.origin.kind==='parent-customer-delegation')env[causal.name]=row.scopedProjection;
   env[stored.name]=exactRow;
   const allowed=evaluateCommerceFlowDataV1(entry.access.resource_condition.expression,'$.access.resource_condition.expression',env,{
    charge(){if(++fuel>4096)fail('InvalidContract',where,'bounded Entry resource evaluation required');},
    pure(){return fail('MissingMapping',where,'scoped access cannot invoke pure code');},native(){return fail('MissingMapping',where,'scoped access cannot invoke native code');},
    context(){if(!privateContextSeen)fail('ForeignOwner',where,'selected private context was not checked');return row.scopedProjection;},isNullaryEnum(){return false;},
   });
   if(allowed!==true)throw new CommerceSelectedScopedResourceNotFoundV1();
  },
  localCallPath(parent:CommerceOperationInvocationHandle,targetOperation:string){
   live(parent);const operation=invocations.operation(parent),plan=plans.inspectOperation(operation).plan;
   if(typeof targetOperation!=='string'||!targetOperation.length)fail('InvalidContract',where,'target Operation selector required');
   const found:string[]=[];let nodes=0;
   const visit=(value:unknown,at:string,depth:number):void=>{
    if(!value||typeof value!=='object')return;
    if(++nodes>65536||depth>128)fail('InvalidContract',where,'bounded checked source call traversal required');
    if(!Array.isArray(value)&&'target' in value&&'authorization' in value&&'role' in value){
     const call=value as {target?:unknown;authorization?:unknown;role?:unknown;entry?:unknown};
     if(call.target===targetOperation&&call.authorization==='original-local-context-forwarding-required'&&call.role==='Operation'&&call.entry===null)found.push(at);
    }
    if(Array.isArray(value))value.forEach((item,index)=>visit(item,at+'['+index+']',depth+1));
    else for(const [key,item] of Object.entries(value))visit(item,at+'.'+key,depth+1);
   };
   visit(plan,'$',0);if(found.length!==1)fail('MissingMapping',where,'one exact original local Operation call required');
   return found[0]!;
  },
  deriveLocalCall(parent:CommerceOperationInvocationHandle,sourcePath:string,boundArguments:unknown){
   const row=live(parent),child=invocations.deriveLocalCall(parent,sourcePath,boundArguments),view=invocations.inspect(child),root=invocations.inspect(row.root);
   if(view.source_sha256!==sourceSha||view.service!==root.service||view.entry!==root.entry||view.depth<=root.depth||view.parent_call_path!==sourcePath||!selected.services.some(s=>s.id===view.service))
    fail('ForeignOwner',where,'derived local call must retain selected root and service');
   issued.set(child,{entry:row.entry,input:row.input,root:row.root,kind:'child',resourceQualified:row.resourceQualified,scopedProjection:row.scopedProjection});return child;
  },
  operation(h:CommerceOperationInvocationHandle){live(h);return invocations.operation(h);},
  parameters(h:CommerceOperationInvocationHandle){live(h);return invocations.parameters(h);},
  principalIdentity(h:CommerceOperationInvocationHandle){live(h);return invocations.principalIdentity(h);},
  context(h:CommerceOperationInvocationHandle,sourcePath:string){live(h);return invocations.context(h,sourcePath);},
  workerObservation(h:CommerceOperationInvocationHandle,sourcePath:string,args:Parameters<CommerceSourceInvocationOwnerV1['workerObservation']>[2]){live(h);return invocations.workerObservation(h,sourcePath,args);},
  workerCommandIdentity(h:CommerceOperationInvocationHandle,transactionPath:string){live(h);return invocations.workerCommandIdentity(h,transactionPath);},
  isWorkflowObservationInvocation(h:CommerceOperationInvocationHandle){live(h);return invocations.isWorkflowObservationInvocation(h);},
  inspectWorkflowObservationCommitBinding(h:CommerceOperationInvocationHandle,transactionPath:string){
   live(h);return invocations.inspectWorkflowObservationCommitBinding(h,transactionPath);
  },
  withWorkerTransaction<T>(h:CommerceOperationInvocationHandle,storage:CommerceServiceStorageOwnerV1,transactionPath:string,execute:()=>T):T {
   live(h);storage.assertSelectedAssembly(owner);return invocations.withWorkerTransaction(h,storage,transactionPath,execute);
  },
  assertSelectedLocalChild(h:CommerceOperationInvocationHandle,expectedRootEntry:string,expectedOperation:string){
   const row=live(h);if(row.kind!=='child')fail('ForeignOwner',where,'selected local child invocation required');
   const root=invocations.inspect(row.root),child=invocations.inspect(h);
   if(root.entry!==expectedRootEntry||child.entry!==expectedRootEntry||child.operation!==expectedOperation||child.service!==root.service||child.source_sha256!==sourceSha||child.depth<=root.depth||child.parent_call_path===null)
    fail('ForeignOwner',where,'local child must descend from the exact selected authorized root');
  },
  assertAssembly(owner:CommerceBindingAssemblyOwnerV1,token:CommerceBindingAssemblyHandle){
   current();if(owner!==assemblyOwner||token!==assembly)fail('ForeignOwner',where,'exact selected application assembly required');
   assemblyOwner.assertCurrent(assembly);
  },
  inspectInvocation(h:CommerceOperationInvocationHandle){const row=live(h),view=invocations.inspect(h);return coreFreeze({...view,actual_business_resource_owners_qualified:row.resourceQualified,qualification:row.resourceQualified?'selected-original-entry-auth-and-original-resource-equality;effects-still-pending':view.qualification});},
  retire(h:CommerceOperationInvocationHandle){const row=live(h);invocations.retire(h);if(row.kind==='root'){auth.disposeInput(row.input);auth.disposeEntry(row.entry);}issued.delete(h);},
  inspect(){current();return inspection;},assertCurrent:current,
  dispose(){if(disposed)return;invocations.dispose();disposed=true;},
 });owners.add(owner);current();return owner;
}
