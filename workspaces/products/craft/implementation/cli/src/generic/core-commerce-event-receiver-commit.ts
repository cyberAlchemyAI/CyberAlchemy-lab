/** Fresh native receiver commit handoff for the finite Core Event family.
 * A genuine generated execution and its exact selected invocation are needed
 * to consume the storage receipt. Persisted replay needs a separate admission;
 * neither path publishes the producer outbox here.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceServiceStorageFreshExecutionV1,type CommerceServiceStorageFreshCommitReceiptV1}
 from '../commerce/commerce-service-storage-v1.js';
import {assertCommerceGeneratedOperationRuntimeV1,type CommerceGeneratedOperationRuntimeV1}
 from '../commerce/commerce-generated-operation-runtime-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1}
 from '../commerce/commerce-selected-entry-auth-v1.js';
import type {CommerceOperationInvocationHandle} from '../commerce/commerce-stages-v1.js';
import type {CommerceNativeValue} from '../commerce/commerce-native-v1.js';
import {assertCoreCommerceCrossServiceEventRelay,type CoreCommerceCrossServiceEventRelay,
 type CoreCommerceCrossServiceOccurrence} from './core-commerce-cross-service-event-relay.js';
import {assertCoreCommerceEventAckSelection,type CoreCommerceEventAckSelection}
 from './core-commerce-event-ack-selection.js';

export interface CoreCommerceEventFreshReceiverCommit {
 readonly kind:'original-event-fresh-receiver-commit/v1-candidate';
}
export interface CoreCommerceEventReceiverCommitOwner {
 acceptFresh(input:Readonly<{runtime:CommerceGeneratedOperationRuntimeV1;
  selected:CommerceSelectedEntryAuthOwnerV1;invocation:CommerceOperationInvocationHandle;
  occurrence:CoreCommerceCrossServiceOccurrence;transaction_path:string;
  execution:CommerceServiceStorageFreshExecutionV1;event_fingerprint:string}>):CoreCommerceEventFreshReceiverCommit;
 inspectWitness(witness:CoreCommerceEventFreshReceiverCommit):Readonly<{
  entry:string;operation:string;occurrence_id:string;inbox_entity:string;
  transaction_path:string;receiver_store_id:string;inbox_receipt:CommerceNativeValue;
  qualification:'exact-native-generated-commit-and-persisted-inbox;operation-result-and-producer-CAS-pending';
  authority_effect:'none'}>;
 assertCurrent():void;close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceEventReceiverCommitOwner(owner:CoreCommerceEventReceiverCommitOwner):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))
  throw new Error('original Event receiver commit owner required');
 owner.assertCurrent();
}
const record=(value:unknown):Readonly<Record<string,unknown>>=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(value)))
  throw new Error('original Event receiver record required');
 return value as Readonly<Record<string,unknown>>;
};
const eventOrderId=(event:unknown):string=>{
 const id=record(event).orderId;
 if(typeof id!=='string'||!id)throw new Error('original Event order identity required');
 return id;
};

export function createCoreCommerceEventReceiverCommitOwner(input:Readonly<{
 relay:CoreCommerceCrossServiceEventRelay;acknowledgement:CoreCommerceEventAckSelection;
 receiver:CommerceServiceStorageOwnerV1;
}>):CoreCommerceEventReceiverCommitOwner {
 const {relay,acknowledgement,receiver}=input;
 assertCoreCommerceCrossServiceEventRelay(relay);
 assertCoreCommerceEventAckSelection(acknowledgement);
 assertCommerceServiceStorageOwnerV1(receiver);
 const route=relay.inspect().route,ack=acknowledgement.inspect(),store=receiver.inspect();
 if(ack.source.entry!==route.entry||ack.source.operation!==route.operation||
  ack.source.inbox_entity!==route.consumer_inbox_entity||
  ack.source_capture_sha256!==route.source_capture_sha256||
  store.store_id!==ack.receiver_store_id||store.service!==route.receiver_service||
  store.source_capture_sha256!==route.source_capture_sha256)
  throw new Error('one original Event receiver source and native store required');
 const issued=new WeakMap<object,{occurrence:CoreCommerceCrossServiceOccurrence;
  id:string;native:CommerceServiceStorageFreshCommitReceiptV1;inbox:CommerceNativeValue;
  transactionPath:string;eventFingerprint:string}>();let closed=false;
 const current=()=>{
  if(closed)throw new Error('Event receiver commit owner closed');
  relay.assertCurrent();acknowledgement.assertCurrent();receiver.assertCurrent();
  if(receiver.inspect().store_id!==store.store_id||
   acknowledgement.inspect().source_capture_sha256!==route.source_capture_sha256)
   throw new Error('Event receiver source or store changed');
 };
 const readInbox=(id:string,fingerprint:string,orderId:string):CommerceNativeValue=>{
  const value=receiver.inspectStoredRecord(route.consumer_inbox_entity,0,
   {consumerEntryId:route.entry,occurrenceId:id});
  const inbox=record(value);
  if(inbox.consumerEntryId!==route.entry||inbox.occurrenceId!==id||inbox.orderId!==orderId||
   inbox.eventFingerprint!==fingerprint||
   typeof inbox.eventFingerprint!=='string'||!/^[a-f0-9]{64}$/.test(inbox.eventFingerprint)||
   !Object.hasOwn(inbox,'receipt'))
   throw new Error('exact persisted Event receiver inbox and result required');
  return value!;
 };
 const owner:CoreCommerceEventReceiverCommitOwner=Object.freeze({
  acceptFresh({runtime,selected,invocation,occurrence,transaction_path,execution,event_fingerprint}:Parameters<CoreCommerceEventReceiverCommitOwner['acceptFresh']>[0]){
   current();assertCommerceGeneratedOperationRuntimeV1(runtime);
   assertCommerceSelectedEntryAuthOwnerV1(selected);
   const selectedInvocation=selected.inspectInvocation(invocation),runtimeView=runtime.inspect(),
    view=relay.inspectOccurrence(occurrence),parameters=record(selected.parameters(invocation));
   if(selectedInvocation.entry!==route.entry||selectedInvocation.operation!==route.operation||
    selectedInvocation.service!==route.receiver_service||
    selectedInvocation.source_sha256!==route.source_capture_sha256||
    runtimeView.operation!==route.operation||runtimeView.service!==route.receiver_service||
    runtimeView.source_capture_sha256!==route.source_capture_sha256||
    !Object.hasOwn(parameters,route.argument)||
    !isDeepStrictEqual(parameters[route.argument],view.event)||
    !ack.source.candidates.some(candidate=>candidate.transaction_path===transaction_path)||
    typeof event_fingerprint!=='string'||!/^[a-f0-9]{64}$/.test(event_fingerprint))
    throw new Error('exact selected Event invocation and inbox transaction required');
   const native=receiver.consumeFreshCommit(execution,runtime,selected,invocation,transaction_path),
    inspected=receiver.inspectFreshGeneratedCommit(native);
   if(inspected.kind!=='committed'||inspected.operation!==route.operation||
    inspected.transaction_path!==transaction_path||
    inspected.source_capture_sha256!==route.source_capture_sha256||
    inspected.service!==route.receiver_service||inspected.store_id!==store.store_id)
    throw new Error('original Event receiver native transaction differs from checked source');
   const inbox=readInbox(view.occurrence_id,event_fingerprint,eventOrderId(view.event));
   const witness:CoreCommerceEventFreshReceiverCommit=Object.freeze({
    kind:'original-event-fresh-receiver-commit/v1-candidate'});
   issued.set(witness,{occurrence,id:view.occurrence_id,native,inbox,transactionPath:transaction_path,
    eventFingerprint:event_fingerprint});
   current();return witness;
  },
  inspectWitness(witness:CoreCommerceEventFreshReceiverCommit){
   current();const saved=witness&&typeof witness==='object'?issued.get(witness):undefined;
   if(!saved)throw new Error('original Event receiver commit witness required');
   const native=receiver.inspectFreshGeneratedCommit(saved.native),
    view=relay.inspectOccurrence(saved.occurrence),fresh=readInbox(saved.id,saved.eventFingerprint,
     eventOrderId(view.event));
   if(native.operation!==route.operation||native.transaction_path!==saved.transactionPath||
    native.store_id!==store.store_id||view.occurrence_id!==saved.id||
    !isDeepStrictEqual(fresh,saved.inbox))
    throw new Error('Event receiver native commit or inbox changed');
   return coreFreeze({entry:route.entry,operation:route.operation,
    occurrence_id:saved.id,inbox_entity:route.consumer_inbox_entity,
    transaction_path:saved.transactionPath,receiver_store_id:store.store_id,
    inbox_receipt:record(fresh).receipt as CommerceNativeValue,
    qualification:'exact-native-generated-commit-and-persisted-inbox;operation-result-and-producer-CAS-pending' as const,
    authority_effect:'none' as const});
  },
  assertCurrent:current,close(){closed=true;},
 });
 owners.add(owner);current();return owner;
}
