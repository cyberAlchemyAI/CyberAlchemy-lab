/** Original C12 relay custody. Claims and ACKs are added only through this
 * source/profile/store-bound owner; caller event DTOs do not confer custody.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {deriveGenericEventOccurrence} from './event-occurrence.js';
import type {GenericEventTransactionApplicationV1} from './event-data-v1.js';
import {assertGenericRepositoryPlanOwner,type GenericRepositoryPlanOwner,type GenericTransactionApplicationHandle} from './repository-plan.js';
import {assertGenericSqliteRepository,type GenericSqliteRepository} from './sqlite-repository.js';
import type {GenericEventClaim} from './event-store.js';
import type {GenericEventReceiverCommitReceipt} from './execution-session.js';
import {deliverGenericEventToRuntime,type GenericEventDeliveryResult} from './execution-session.js';
import type {GenericTransactionApplicationRuntime} from './invocation-owner.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['repository-plan'+ext,'sqlite-repository'+ext]);
const at={path:'generic-event-relay',start:0,end:0};

export interface GenericEventRelayOwner {
 readonly kind:'original-generic-event-relay-owner/v1-candidate';
 assertCurrent():void;
 claimNext(leaseMs:number):GenericEventRelayClaim|null;
 claimWorkflowEvent(bindingId:string,causalCommandTupleSha256:string,leaseMs:number):GenericEventRelayClaim|null;
 deliver(claim:GenericEventRelayClaim,receiver:GenericTransactionApplicationRuntime):Promise<GenericEventDeliveryResult>;
 ack(claim:GenericEventRelayClaim,receipt:GenericEventReceiverCommitReceipt):void;
 close():void;
}

/** A claim's envelope/fence are held only by this module. A caller-created
 * value with the same visible shape cannot stand in for the original claim. */
export interface GenericEventRelayClaim {
 readonly kind:'original-generic-event-relay-claim/v1-candidate';
}

type RelayBinding={
 readonly plans:GenericRepositoryPlanOwner;
 readonly application:GenericTransactionApplicationHandle;
 readonly repository:GenericSqliteRepository;
 readonly service:string;
 readonly store_epoch_sha256:string;
 readonly source_capture_sha256:string;
 readonly profile_sha256:string;
 readonly event_bindings_sha256:string;
 readonly closed:()=>boolean;
};
const registered=new WeakMap<object,RelayBinding>();
const claims=new WeakMap<object,{owner:GenericEventRelayOwner;claim:GenericEventClaim;retired:boolean}>();
export function inspectGenericAckedWorkflowEvent(owner:GenericEventRelayOwner,bindingId:string,causalCommandTupleSha256:string):import('./event-store.js').GenericEventEnvelope|null{
 const registeredOwner=requireGenericEventRelayOwnerBinding(owner),selected=registeredOwner.plans.inspectSourceApplication(registeredOwner.application).contract as GenericEventTransactionApplicationV1;
 if(typeof bindingId!=='string'||!/^[0-9a-f]{64}$/.test(causalCommandTupleSha256))fail('InvalidContract',at,'exact workflow Event identity required');
 const binding=selected.event_bindings.find(b=>b.id===bindingId&&b.producer_service===registeredOwner.service);
 const operation=binding&&selected.stateful_operations.find(o=>o.operation===binding.producer_operation);
 const emissions:any[]=[];const visit=(value:unknown)=>{if(!value||typeof value!=='object')return;if((value as {kind?:string}).kind==='emit-event'){emissions.push(value);return;}for(const child of Object.values(value))if(typeof child==='object')visit(child);};
 if(operation)visit(operation.transaction.body);
 const matches=emissions.filter(e=>e.binding_ref===bindingId);
 if(!binding||matches.length!==1||matches[0]!.event_selector!==binding.event_selector||matches[0]!.event_version!==binding.event_version)
  fail('MissingMapping',at,'unique checked workflow Event emission required');
 const emission=matches[0]!,occurrence=deriveGenericEventOccurrence({producer_namespace:registeredOwner.service,causal_command_tuple_sha256:causalCommandTupleSha256,event_selector:binding.event_selector,event_version:binding.event_version,emission_ordinal:emission.emission_ordinal});
 const envelope=registeredOwner.repository.inspectAckedEvent(owner,occurrence);
 if(envelope&&(envelope.binding_ref!==bindingId||envelope.binding_sha256!==dataDigest(binding)||envelope.source_site!==emission.source_site||envelope.causal_command_tuple_sha256!==causalCommandTupleSha256))fail('ForeignOwner',at,'ACKed Event differs from checked workflow emission');
 return envelope;
}

export function createGenericEventRelayOwner(
 plans:GenericRepositoryPlanOwner,
 application:GenericTransactionApplicationHandle,
 repository:GenericSqliteRepository,
 service:string,
):GenericEventRelayOwner {
 assertGenericRepositoryPlanOwner(plans);
 plans.assertCurrent(application);
 assertGenericSqliteRepository(repository);
 repository.assertApplication(plans,application);
 const selected=plans.inspectSourceApplication(application);
 const contract=selected.contract as typeof selected.contract&{admission_mode:string;event_bindings?:readonly unknown[]};
 if(contract.admission_mode!=='event-handoff-entry'||!Array.isArray(contract.event_bindings)||contract.event_bindings.length===0)
  fail('UnsupportedCapability',at,'checked event handoff application required');
 plans.assertChild(plans.bindService(application,service),application);
 if(!contract.event_bindings.some((binding:any)=>binding.producer_service===service))
  fail('ForeignOwner',at,'selected producer service has no event binding');
 const store_epoch_sha256=repository.inspect().store_epoch_sha256;
 const event_bindings_sha256=dataDigest(contract.event_bindings);
 const eventContract=contract as GenericEventTransactionApplicationV1;
 let closed=false;
 const current=()=>{
  if(closed)fail('DisposedOwner',at,'relay owner closed');
  pin.assertCurrent();
  assertGenericRepositoryPlanOwner(plans);
  plans.assertCurrent(application);
  repository.assertApplication(plans,application);
  const live=plans.inspectSourceApplication(application);
  if(live.source_capture_sha256!==selected.source_capture_sha256||live.derivation.profile_sha256!==selected.derivation.profile_sha256||dataDigest((live.contract as typeof contract).event_bindings)!==event_bindings_sha256)
   fail('StaleOwner',at,'event source or profile changed');
  if(repository.inspect().store_epoch_sha256!==store_epoch_sha256)
   fail('StaleOwner',at,'relay store epoch changed');
 };
 const owner:GenericEventRelayOwner=Object.freeze({kind:'original-generic-event-relay-owner/v1-candidate',assertCurrent:current,
  claimNext(leaseMs:number){
   current();
   if(!Number.isSafeInteger(leaseMs)||leaseMs<1||leaseMs>300000)fail('InvalidContract',at,'bounded relay lease required');
   const physical=repository.claimNextEvent(owner,leaseMs);
   if(!physical)return null;
   repository.assertEventClaimCurrent(owner,physical);
   const handle:GenericEventRelayClaim=Object.freeze({kind:'original-generic-event-relay-claim/v1-candidate'});
   claims.set(handle,{owner,claim:physical,retired:false});
   return handle;
  },
  claimWorkflowEvent(bindingId:string,causalCommandTupleSha256:string,leaseMs:number){
   current();
   if(typeof bindingId!=='string'||!/^[0-9a-f]{64}$/.test(causalCommandTupleSha256)||!Number.isSafeInteger(leaseMs)||leaseMs<1||leaseMs>300000)
    fail('InvalidContract',at,'exact bounded workflow Event claim required');
   const selected=eventContract.event_bindings.find(b=>b.id===bindingId&&b.producer_service===service);
   const operation=selected&&eventContract.stateful_operations.find(o=>o.operation===selected.producer_operation);
   const emissions:any[]=[];
   const visit=(value:unknown)=>{if(!value||typeof value!=='object')return;if((value as {kind?:string}).kind==='emit-event'){emissions.push(value);return;}for(const child of Object.values(value))if(typeof child==='object')visit(child);};
   if(operation)visit(operation.transaction.body);
   const matches=emissions.filter(e=>e.binding_ref===bindingId);
   if(!selected||matches.length!==1||matches[0]!.event_selector!==selected.event_selector||matches[0]!.event_version!==selected.event_version)
    fail('MissingMapping',at,'unique checked workflow Event emission required');
   const emission=matches[0]!,occurrence=deriveGenericEventOccurrence({producer_namespace:service,causal_command_tuple_sha256:causalCommandTupleSha256,event_selector:selected.event_selector,event_version:selected.event_version,emission_ordinal:emission.emission_ordinal});
   const physical=repository.claimExactEvent(owner,occurrence,leaseMs);
   if(!physical)return null;
   if(physical.envelope.binding_ref!==bindingId||physical.envelope.binding_sha256!==dataDigest(selected)||physical.envelope.causal_command_tuple_sha256!==causalCommandTupleSha256||physical.envelope.source_site!==emission.source_site)
    fail('ForeignOwner',at,'claimed Event differs from checked workflow emission');
   repository.assertEventClaimCurrent(owner,physical);
   const handle:GenericEventRelayClaim=Object.freeze({kind:'original-generic-event-relay-claim/v1-candidate'});
   claims.set(handle,{owner,claim:physical,retired:false});
   return handle;
  },
  async deliver(handle:GenericEventRelayClaim,receiver:GenericTransactionApplicationRuntime){
   requireGenericEventRelayClaim(owner,handle);
   return deliverGenericEventToRuntime(owner,handle,receiver);
  },
  ack(handle:GenericEventRelayClaim,receipt:GenericEventReceiverCommitReceipt){
   requireGenericEventRelayClaim(owner,handle);
   repository.ackEvent(owner,handle,receipt);
   claims.get(handle)!.retired=true;
  },
  close(){if(closed)return;closed=true;}});
 registered.set(owner,{plans,application,repository,service,store_epoch_sha256,source_capture_sha256:selected.source_capture_sha256,profile_sha256:selected.derivation.profile_sha256,event_bindings_sha256,closed:()=>closed});
 current();
 return owner;
}

export function requireGenericEventRelayOwnerBinding(owner:GenericEventRelayOwner):Readonly<RelayBinding>{
 const binding=owner&&typeof owner==='object'?registered.get(owner):undefined;
 if(!binding||binding.closed())fail('ForeignOwner',at,'original event relay owner required');
 owner.assertCurrent();return binding;
}

/** Internal relay/receiver seam. Neither a copied claim nor a stale fence can
 * authorize delivery. The same guard is required again after receiver commit. */
export function requireGenericEventRelayClaim(owner:GenericEventRelayOwner,handle:GenericEventRelayClaim):GenericEventClaim {
 const binding=registered.get(owner),row=handle&&typeof handle==='object'?claims.get(handle):undefined;
 if(!binding||!row||row.owner!==owner||row.retired)fail('ForeignOwner',at,'original live relay claim required');
 owner.assertCurrent();
 binding.repository.assertEventClaimCurrent(owner,row.claim);
 return row.claim;
}

export function retireGenericEventRelayClaim(owner:GenericEventRelayOwner,handle:GenericEventRelayClaim):void {
 requireGenericEventRelayClaim(owner,handle);
 claims.get(handle)!.retired=true;
}

/** Internal storage guard. No public payload, route or caller token can mint it. */
export function requireGenericEventRelayResourceAccess(owner:GenericEventRelayOwner,repository:GenericSqliteRepository):Readonly<RelayBinding> {
 const binding=owner&&typeof owner==='object'?registered.get(owner):undefined;
 if(!binding||binding.repository!==repository||binding.closed())fail('ForeignOwner',at,'original relay/store relation required');
 owner.assertCurrent();
 return binding;
}
