/** Generated cross-service Event delivery through the selected Entry and
 * Operation owners. The receiver's persisted inbox/result is the only
 * positive completion evidence. Producer outbox publication is separate.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1}
 from '../commerce/commerce-application-assembly-v1.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceAuthActorV1}
 from '../commerce/commerce-entry-context-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1,
 type CommerceSelectedEntryStartV1} from '../commerce/commerce-selected-entry-auth-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from '../commerce/commerce-service-storage-v1.js';
import {assertCoreCommerceCrossServiceEventRelay,type CoreCommerceCrossServiceEventRelay,
 type CoreCommerceCrossServiceOccurrence} from './core-commerce-cross-service-event-relay.js';
import {assertCoreCommerceEventIngressAdmission,type CoreCommerceEventIngressAdmission,
 type CoreCommerceEventIngressTicket} from './core-commerce-event-ingress-admission.js';
import {assertCoreCommerceEventAckSelection,type CoreCommerceEventAckSelection}
 from './core-commerce-event-ack-selection.js';
import {assertCoreCommerceEventReceiverCommitOwner,type CoreCommerceEventReceiverCommitOwner}
 from './core-commerce-event-receiver-commit.js';
import type {CoreCommerceEventFreshReceiverCommit} from './core-commerce-event-receiver-commit.js';

/** This is implemented by the original selected Auth owner, never supplied by
 * a caller callback. The private owner assertion below rejects substitutes. */
export type CoreCommerceEventSelectedAuth=CommerceSelectedEntryAuthOwnerV1&Readonly<{
 beginEvent(actor:CommerceAuthActorV1|null,entryId:string,wire:Uint8Array,parameters:unknown,
  admission:CoreCommerceEventIngressAdmission,ticket:CoreCommerceEventIngressTicket,
  signal?:AbortSignal):Promise<CommerceSelectedEntryStartV1>;
}>;
export type CoreCommerceEventDeliveryResult=
 Readonly<{kind:'receiver-committed';occurrence_id:string;receipt:unknown;
  acknowledgement:CoreCommerceEventReceiverAcknowledgement;
  qualification:'original-consumer-inbox-and-result-commit;producer-publication-pending'}>|
 Readonly<{kind:'denied';status:401|403;authority_effect:'none'}>|
 Readonly<{kind:'retry';occurrence_id:string;reason:'unavailable'|'outcome-unknown'|'consumer-inbox-not-observed';
  authority_effect:'indeterminate'}>|
 Readonly<{kind:'rejected';occurrence_id:string;code:string;authority_effect:'not-established'}>;
export interface CoreCommerceEventReceiverAcknowledgement {
 readonly kind:'original-event-persisted-receiver-acknowledgement/v1-candidate';
}
export interface CoreCommerceEventDelivery {
 inspectActorRequirement():Readonly<{entry:string;caller_service:string;target_service:string;
  permission:string;auth_route_id:string;auth_permission:Readonly<{resource:string;action:string;scope:string}>;
  qualification:'checked-event-entry-permission-only;native-actor-required'}>;
 deliver(occurrence:CoreCommerceCrossServiceOccurrence,actor:CommerceAuthActorV1|null,
  signal?:AbortSignal):Promise<CoreCommerceEventDeliveryResult>;
 inspectAcknowledgement(acknowledgement:CoreCommerceEventReceiverAcknowledgement):Readonly<{
  entry:string;occurrence_id:string;event_fingerprint:string;receipt:unknown;
  producer_store_id:string;receiver_store_id:string;source_capture_sha256:string;
  qualification:'source-generated-result-and-original-persisted-receiver-inbox';
  authority_effect:'none'}>;
 assertCurrent():void;close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceEventDelivery(owner:CoreCommerceEventDelivery):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))throw new Error('original Event delivery owner required');
 owner.assertCurrent();
}
const record=(value:unknown):Readonly<Record<string,unknown>>=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(value)))
  throw new Error('original receiver inbox record required');
 return value as Readonly<Record<string,unknown>>;
};

/** All effects are invoked through the original assembly and selected Auth.
 * An injected Event port or domain handler is deliberately absent. */
export function createCoreCommerceEventDelivery(input:Readonly<{
 assembly:CommerceApplicationAssemblyV1;auth:CommerceEntryContextOwnerV1;
 selected:CoreCommerceEventSelectedAuth;producer:CommerceServiceStorageOwnerV1;
 receiver:CommerceServiceStorageOwnerV1;relay:CoreCommerceCrossServiceEventRelay;
 admission:CoreCommerceEventIngressAdmission;acknowledgement:CoreCommerceEventAckSelection;
 receiverCommit:CoreCommerceEventReceiverCommitOwner;
}>):CoreCommerceEventDelivery {
 const {assembly,auth,selected,producer,receiver,relay,admission,acknowledgement,receiverCommit}=input;
 assertCommerceApplicationAssemblyV1(assembly);assertCommerceEntryContextOwnerV1(auth);
 assertCommerceSelectedEntryAuthOwnerV1(selected);
 assertCommerceServiceStorageOwnerV1(producer);assertCommerceServiceStorageOwnerV1(receiver);
 assertCoreCommerceCrossServiceEventRelay(relay);assertCoreCommerceEventIngressAdmission(admission);
 assertCoreCommerceEventAckSelection(acknowledgement);
 assertCoreCommerceEventReceiverCommitOwner(receiverCommit);
 if(typeof selected.beginEvent!=='function')throw new Error('original selected Event Entry owner required');
 const route=relay.inspect().route,app=assembly.inspect(),producerId=producer.inspect(),receiverId=receiver.inspect();
 const ack=acknowledgement.inspect();
 if(ack.source.entry!==route.entry||ack.source.operation!==route.operation||
  ack.source.inbox_entity!==route.consumer_inbox_entity||
  ack.source_capture_sha256!==route.source_capture_sha256||
  ack.receiver_store_id!==receiverId.store_id)
  throw new Error('source-selected Event acknowledgement differs from receiver route');
 if(app.source_capture_sha256!==route.source_capture_sha256||
  producerId.source_capture_sha256!==route.source_capture_sha256||
  receiverId.source_capture_sha256!==route.source_capture_sha256||
  producerId.store_id===receiverId.store_id||
  producerId.service!==route.producer_service||receiverId.service!==route.receiver_service||
  !app.services.includes(route.producer_service)||!app.services.includes(route.receiver_service))
  throw new Error('original Event delivery application and service stores required');
 const bound=auth.bindEntry(route.entry);
 let actorRequirement:ReturnType<CoreCommerceEventDelivery['inspectActorRequirement']>;
 try{
  const entry=auth.inspectEntry(bound);
  if(entry.id!==route.entry||entry.interaction!=='event'||
   entry.access.principal_kind!=='service'||entry.access.caller!==route.producer_service||
   entry.service!==route.receiver_service||entry.access.permission!==route.permission||
   entry.access.auth_route_id!==route.auth_route_id)
   throw new Error('selected Event Auth Entry differs from checked relay');
  actorRequirement=coreFreeze({entry:entry.id,caller_service:route.producer_service,
   target_service:route.receiver_service,permission:entry.access.permission,
   auth_route_id:entry.access.auth_route_id,auth_permission:entry.access.auth_permission,
   qualification:'checked-event-entry-permission-only;native-actor-required' as const});
 }finally{auth.disposeEntry(bound);}
 let closed=false,running=false;
 const issued=new WeakMap<object,{occurrence:CoreCommerceCrossServiceOccurrence;
  receipt:unknown;inbox:unknown;fingerprint:string;
  fresh:CoreCommerceEventFreshReceiverCommit|null}>();
 const current=()=>{
  if(closed)throw new Error('Event delivery closed');
  assembly.assertCurrent();auth.assertCurrent();selected.assertCurrent();
  producer.assertCurrent();receiver.assertCurrent();relay.assertCurrent();admission.assertCurrent();
  acknowledgement.assertCurrent();receiverCommit.assertCurrent();
  if(producer.inspect().store_id!==producerId.store_id||receiver.inspect().store_id!==receiverId.store_id)
   throw new Error('Event delivery service store changed');
 };
 const owner:CoreCommerceEventDelivery=Object.freeze({
  inspectActorRequirement(){current();return actorRequirement;},
  async deliver(occurrence:CoreCommerceCrossServiceOccurrence,actor:CommerceAuthActorV1|null,
   signal?:AbortSignal){
   current();if(running)throw new Error('one selected Event delivery at a time');running=true;
   try{
    const ticket=admission.prepare(occurrence),view=admission.inspectTicket(ticket);
    if(view.entry!==route.entry||view.operation!==route.operation||
     view.producer_service!==route.producer_service||view.receiver_service!==route.receiver_service)
     throw new Error('Event ingress ticket differs from selected route');
    const entry=auth.bindEntry(route.entry);let wire:Uint8Array;
    try{wire=auth.encodeEntryArguments(entry,view.parameters);}finally{auth.disposeEntry(entry);}
    const start=await selected.beginEvent(actor,route.entry,wire,view.parameters,admission,ticket,signal);
    current();if(!start.ok)return coreFreeze({kind:'denied' as const,status:start.status,authority_effect:'none' as const});
    const invocation=start.invocation;
    let opened=false;
    try{
     const runtime=await assembly.openGeneratedOperation(invocation);opened=true;
     const result=await runtime.run(invocation);current();
     if(result.kind==='indeterminate')return coreFreeze({kind:'retry' as const,
      occurrence_id:view.occurrence_id,reason:'outcome-unknown' as const,authority_effect:'indeterminate' as const});
     if(result.kind==='failed')return coreFreeze({kind:'retry' as const,
      occurrence_id:view.occurrence_id,reason:'unavailable' as const,authority_effect:'indeterminate' as const});
     if(result.kind==='rejected'){
      if(typeof result.code!=='string'||!result.code||Buffer.byteLength(result.code)>256)
       throw new Error('bounded original Event rejection code required');
      if(result.code==='CommandNotFresh'||result.code==='StorageUnavailable')
       return coreFreeze({kind:'retry' as const,occurrence_id:view.occurrence_id,
        reason:'outcome-unknown' as const,authority_effect:'indeterminate' as const});
      return coreFreeze({kind:'rejected' as const,occurrence_id:view.occurrence_id,
       code:result.code,authority_effect:'not-established' as const});
     }
     if(result.kind!=='returned')throw new Error('original generated Event Operation outcome required');
     const expectedFingerprint=runtime.inspectEventFingerprint(invocation);
     const witness=runtime.inspectEventAcknowledgement(invocation);
     const commits=Array.isArray(result.commits)?result.commits:null;
     if(!commits||commits.length>1||(commits.length===1)!==Boolean(witness))
      throw new Error('generated Event outcome and native inbox commit witness differ');
     if(witness){
      const observed=receiverCommit.inspectWitness(witness);
      if(observed.entry!==route.entry||observed.operation!==route.operation||
       observed.occurrence_id!==view.occurrence_id||
       observed.inbox_entity!==route.consumer_inbox_entity||
       observed.receiver_store_id!==receiverId.store_id)
       throw new Error('original Event receiver native commit witness changed');
     }
     const row=receiver.inspectStoredRecord(route.consumer_inbox_entity,0,
      {consumerEntryId:route.entry,occurrenceId:view.occurrence_id});
     if(row===null)return coreFreeze({kind:'retry' as const,occurrence_id:view.occurrence_id,
      reason:'consumer-inbox-not-observed' as const,authority_effect:'indeterminate' as const});
     const inbox=record(row);
     if(inbox.consumerEntryId!==route.entry||inbox.occurrenceId!==view.occurrence_id||
      inbox.eventFingerprint!==expectedFingerprint||
      !isDeepStrictEqual(inbox.receipt,result.value))
      throw new Error('original consumer inbox/result differs from generated Event outcome');
     if(witness&&!isDeepStrictEqual(receiverCommit.inspectWitness(witness).inbox_receipt,inbox.receipt))
      throw new Error('original native Event commit and persisted result differ');
     const acknowledgement:CoreCommerceEventReceiverAcknowledgement=Object.freeze({
      kind:'original-event-persisted-receiver-acknowledgement/v1-candidate'});
     issued.set(acknowledgement,{occurrence,receipt:inbox.receipt,inbox:row,
      fingerprint:expectedFingerprint,fresh:witness});
     current();return coreFreeze({kind:'receiver-committed' as const,
      occurrence_id:view.occurrence_id,receipt:inbox.receipt,acknowledgement,
      qualification:'original-consumer-inbox-and-result-commit;producer-publication-pending' as const});
    }finally{
     try{if(opened)assembly.releaseGeneratedOperation(invocation);}finally{selected.retire(invocation);}
    }
   }finally{running=false;}
  },
  inspectAcknowledgement(acknowledgement:CoreCommerceEventReceiverAcknowledgement){
   current();const saved=acknowledgement&&typeof acknowledgement==='object'?
    issued.get(acknowledgement):undefined;
   if(!saved)throw new Error('original generated Event receiver acknowledgement required');
   const view=relay.inspectOccurrence(saved.occurrence),row=receiver.inspectStoredRecord(
    route.consumer_inbox_entity,0,{consumerEntryId:route.entry,occurrenceId:view.occurrence_id});
   if(row===null||!isDeepStrictEqual(row,saved.inbox))
    throw new Error('original Event receiver inbox changed after acknowledgement');
   const inbox=record(row);
   if(inbox.consumerEntryId!==route.entry||inbox.occurrenceId!==view.occurrence_id||
    inbox.eventFingerprint!==saved.fingerprint||
    !isDeepStrictEqual(inbox.receipt,saved.receipt))
    throw new Error('original Event receiver result changed after acknowledgement');
   if(saved.fresh){const native=receiverCommit.inspectWitness(saved.fresh);
    if(native.entry!==route.entry||native.occurrence_id!==view.occurrence_id||
     native.receiver_store_id!==receiverId.store_id||
     !isDeepStrictEqual(native.inbox_receipt,saved.receipt))
     throw new Error('original Event native receiver commit changed');}
   return coreFreeze({entry:route.entry,occurrence_id:view.occurrence_id,
    event_fingerprint:saved.fingerprint,receipt:saved.receipt,
    producer_store_id:producerId.store_id,receiver_store_id:receiverId.store_id,
    source_capture_sha256:route.source_capture_sha256,
    qualification:'source-generated-result-and-original-persisted-receiver-inbox' as const,
    authority_effect:'none' as const});
  },
  assertCurrent:current,close(){closed=true;},
 });
 owners.add(owner);current();return owner;
}
