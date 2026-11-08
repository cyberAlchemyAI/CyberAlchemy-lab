/** Native producer provenance for one checked atomic Event/outbox/action.
 * Reopened replay must use the original command journal and persisted aliases;
 * an in-memory commit receipt is never treated as durable across process open.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import {deriveCommerceCommandTransactionNamespaceV1}
 from '../commerce/commerce-command-identity-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceSqliteCommandKeyV1} from '../commerce/commerce-service-storage-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1}
 from '../commerce/commerce-selected-entry-auth-v1.js';
import {assertCommerceGeneratedOperationRuntimeV1,type CommerceGeneratedOperationRuntimeV1}
 from '../commerce/commerce-generated-operation-runtime-v1.js';
import type {CommerceOperationInvocationHandle} from '../commerce/commerce-stages-v1.js';
import {assertCoreCommerceCrossServiceEventRelay,type CoreCommerceCrossServiceEventRelay,
 type CoreCommerceCrossServiceOccurrence} from './core-commerce-cross-service-event-relay.js';
import {assertCoreCommerceEventProducerSource,type CoreCommerceEventProducerSource}
 from './core-commerce-event-producer-source.js';

export interface CoreCommerceEventProducerProof {
 readonly kind:'original-event-producer-committed-emission/v1-candidate';
}
export interface CoreCommerceEventProducerProvenance {
 acceptFresh(input:Readonly<{occurrence:CoreCommerceCrossServiceOccurrence;
  selected:CommerceSelectedEntryAuthOwnerV1;invocation:CommerceOperationInvocationHandle;
  runtime:CommerceGeneratedOperationRuntimeV1;result:unknown}>):CoreCommerceEventProducerProof;
 inspectRecorded(occurrence:CoreCommerceCrossServiceOccurrence):CoreCommerceEventProducerProof;
 inspectProof(proof:CoreCommerceEventProducerProof):Readonly<{
  entry:string;operation:string;transaction_path:string;occurrence_id:string;
  outbox_entity:string;producer_store_id:string;source_capture_sha256:string;
  provenance:'fresh-native-commit'|'persisted-command-replay';
  qualification:'original-recorded-producer-command-and-atomic-event-outbox-action';
  authority_effect:'none'}>;
 assertCurrent():void;close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceEventProducerProvenance(owner:CoreCommerceEventProducerProvenance):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))
  throw new Error('original Event producer provenance owner required');
 owner.assertCurrent();
}
const record=(value:unknown):Readonly<Record<string,unknown>>=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(value)))
  throw new Error('original bounded producer Event record required');
 return value as Readonly<Record<string,unknown>>;
};

export function createCoreCommerceEventProducerProvenance(input:Readonly<{
 relay:CoreCommerceCrossServiceEventRelay;source:CoreCommerceEventProducerSource;
 producer:CommerceServiceStorageOwnerV1;
}>):CoreCommerceEventProducerProvenance {
 const {relay,source,producer}=input;
 assertCoreCommerceCrossServiceEventRelay(relay);
 assertCoreCommerceEventProducerSource(source);assertCommerceServiceStorageOwnerV1(producer);
 const route=relay.inspect().route,selected=source.inspect(),store=producer.inspect();
 if(selected.operation!==route.producer_operation||
  selected.event_type!==route.event_type||
  selected.outbox_entity!==route.outbox_entity||
  selected.service!==route.producer_service||
  selected.source_capture_sha256!==route.source_capture_sha256||
  store.service!==route.producer_service||store.source_capture_sha256!==route.source_capture_sha256||
  store.store_id!==relay.inspect().producer_store_id)
  throw new Error('original checked Event producer source and store required');
 const issued=new WeakMap<object,{occurrence:CoreCommerceCrossServiceOccurrence;
  id:string;identity:CommerceSqliteCommandKeyV1;outbox:unknown;action:unknown;
  provenance:'fresh-native-commit'|'persisted-command-replay';fresh:object|null}>();
 let closed=false;
 const current=()=>{
  if(closed)throw new Error('Event producer provenance owner closed');
  relay.assertCurrent();source.assertCurrent();producer.assertCurrent();
  if(producer.inspect().store_id!==store.store_id||
   source.inspect().source_capture_sha256!==selected.source_capture_sha256)
   throw new Error('Event producer provenance source or store changed');
 };
 const inspectRows=(occurrence:CoreCommerceCrossServiceOccurrence)=>{
  current();const view=relay.inspectOccurrence(occurrence),outbox=record(view.outbox),
   event=record(view.event),metadata=record(event.metadata),id=view.occurrence_id;
  if(outbox.eventId!==id||metadata.eventId!==id||metadata.producer!==selected.service||
   typeof metadata.commandId!=='string'||!metadata.commandId||
   typeof event.orderId!=='string'||!event.orderId||
   metadata.aggregateId!==event.orderId)
   throw new Error('original producer Event occurrence and command identity required');
  const actionValue=producer.inspectStoredRecord(selected.action_entity,0,{commandId:metadata.commandId}),
   action=record(actionValue);
  if(action.commandId!==metadata.commandId||action.orderId!==event.orderId||
   typeof action.requestFingerprint!=='string'||!/^[a-f0-9]{64}$/.test(action.requestFingerprint)||
   !Object.hasOwn(action,'result'))
   throw new Error('original producer action result required');
  const identity:CommerceSqliteCommandKeyV1=coreFreeze({logicalEntryId:selected.entry,
   principalId:selected.service,commandId:metadata.commandId,
   fingerprint:action.requestFingerprint,
   transactionNamespace:deriveCommerceCommandTransactionNamespaceV1(
    selected.operation,selected.transaction)});
  const journal=producer.inspectRecordedCommand(identity);
  if(journal.kind!=='recorded'||journal.service!==selected.service||
   journal.store_id!==store.store_id||
   journal.source_capture_sha256!==selected.source_capture_sha256)
   throw new Error('original producer command is not durably recorded');
  const aliases=record(journal.result);
  if(!isDeepStrictEqual(aliases[selected.outbox_binding],view.outbox)||
   !isDeepStrictEqual(aliases[selected.event_binding],view.event)||
   !isDeepStrictEqual(aliases[selected.action_binding],actionValue))
   throw new Error('recorded producer Event, outbox and action aliases differ from stored rows');
  return {view,outbox:view.outbox,action:actionValue,identity};
 };
 const mint=(occurrence:CoreCommerceCrossServiceOccurrence,
  rows:ReturnType<typeof inspectRows>,provenance:'fresh-native-commit'|'persisted-command-replay',
  fresh:object|null)=>{
  const proof:CoreCommerceEventProducerProof=Object.freeze({
   kind:'original-event-producer-committed-emission/v1-candidate'});
  issued.set(proof,{occurrence,id:rows.view.occurrence_id,identity:rows.identity,
   outbox:rows.outbox,action:rows.action,provenance,fresh});
  return proof;
 };
 const owner:CoreCommerceEventProducerProvenance=Object.freeze({
  acceptFresh({occurrence,selected:auth,invocation,runtime,result}:Parameters<CoreCommerceEventProducerProvenance['acceptFresh']>[0]){
   current();assertCommerceSelectedEntryAuthOwnerV1(auth);
   assertCommerceGeneratedOperationRuntimeV1(runtime);runtime.assertStorage(producer);
   const call=auth.inspectInvocation(invocation),execution=record(result),
    input=record(auth.parameters(invocation));
   if(call.entry!==selected.entry||call.operation!==selected.operation||
    call.service!==selected.service||call.source_sha256!==selected.source_capture_sha256||
    runtime.inspect().operation!==selected.operation||
    runtime.inspect().service!==selected.service||execution.kind!=='returned'||
    !Array.isArray(execution.commits)||execution.commits.length!==1)
    throw new Error('exact generated producer invocation and fresh result required');
   const receipt=execution.commits[0];
   if(!receipt||typeof receipt!=='object')
    throw new Error('original native producer commit receipt required');
   const native=producer.inspectFreshGeneratedCommit(receipt),rows=inspectRows(occurrence),
    event=record(rows.view.event),action=record(rows.action);
   if(native.operation!==selected.operation||native.transaction_path!==selected.transaction_path||
    native.service!==selected.service||native.store_id!==store.store_id||
    native.source_capture_sha256!==selected.source_capture_sha256||
    !isDeepStrictEqual(native.command_identity,rows.identity)||
    input.orderId!==event.orderId||!isDeepStrictEqual(execution.value,action.result))
    throw new Error('fresh native ConfirmOrder commit differs from original Event rows');
   current();return mint(occurrence,rows,'fresh-native-commit',receipt);
  },
  inspectRecorded(occurrence:CoreCommerceCrossServiceOccurrence){
   const rows=inspectRows(occurrence);current();
   return mint(occurrence,rows,'persisted-command-replay',null);
  },
  inspectProof(proof:CoreCommerceEventProducerProof){
   current();const saved=proof&&typeof proof==='object'?issued.get(proof):undefined;
   if(!saved)throw new Error('original producer emission proof required');
   const rows=inspectRows(saved.occurrence);
   if(rows.view.occurrence_id!==saved.id||
    !isDeepStrictEqual(rows.outbox,saved.outbox)||
    !isDeepStrictEqual(rows.action,saved.action)||
    !isDeepStrictEqual(rows.identity,saved.identity))
    throw new Error('original producer emission changed');
   if(saved.fresh){const native=producer.inspectFreshGeneratedCommit(saved.fresh);
    if(native.operation!==selected.operation||
     native.transaction_path!==selected.transaction_path||
     !isDeepStrictEqual(native.command_identity,rows.identity))
     throw new Error('original fresh producer commit changed');}
   return coreFreeze({entry:selected.entry,operation:selected.operation,
    transaction_path:selected.transaction_path,occurrence_id:saved.id,
    outbox_entity:selected.outbox_entity,producer_store_id:store.store_id,
    source_capture_sha256:selected.source_capture_sha256,
    provenance:saved.provenance,
    qualification:'original-recorded-producer-command-and-atomic-event-outbox-action' as const,
    authority_effect:'none' as const});
  },
  assertCurrent:current,close(){closed=true;},
 });
 owners.add(owner);current();return owner;
}
