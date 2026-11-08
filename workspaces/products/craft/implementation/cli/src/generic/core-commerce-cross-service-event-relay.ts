/** Source/profile-selected cross-service Event route and producer outbox
 * custody. Delivery remains pending a native event Entry invocation and
 * receiver commit/ACK owner; an outbox row alone grants no delivery right.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import {createCoreValueTypes,sameCoreValueType} from '../commerce/commerce-core-types.js';
import {createCoreContextCatalog} from '../commerce/commerce-core-context.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture}
 from '../commerce/commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from '../commerce/commerce-core-semantic-owner.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from '../commerce/commerce-service-storage-v1.js';
import type {CommerceNativeValue} from '../commerce/commerce-native-v1.js';
import type {OperationControlStepV1,TransactionPlanV1} from '../commerce/commerce-data-v1.js';

type EventRoute=Readonly<{entry:string;event_type:string;event_version:1;argument:string;
 producer_service:string;receiver_service:string;operation:string;outbox_entity:string;
 producer_operation:string;consumer_inbox_entity:string;
 permission:string;auth_route_id:string;native_family:'EventInboxOutbox';
 source_capture_sha256:string;qualification:'checked-source-and-profile-cross-service-event-route;native-delivery-pending'}>;
export interface CoreCommerceCrossServiceOccurrence {
 readonly kind:'original-cross-service-outbox-occurrence/v1-candidate';
}
export interface CoreCommerceCrossServiceEventRelay {
 inspect():Readonly<{route:EventRoute;producer_store_id:string;receiver_store_id:string;
  qualification:'source-selected-cross-service-outbox-reader;native-event-delivery-and-ack-pending'}>;
 scanReady(cursor:string|null,limit:number):Readonly<{occurrence_ids:readonly string[];next_cursor:string|null}>;
 readReady(occurrenceId:string):Readonly<{kind:'ready';occurrence:CoreCommerceCrossServiceOccurrence}|
  {kind:'not-ready';authority_effect:'none'}>;
 inspectOccurrence(occurrence:CoreCommerceCrossServiceOccurrence):Readonly<{route:EventRoute;
  occurrence_id:string;event:CommerceNativeValue;outbox:CommerceNativeValue;
  qualification:'original-persisted-ready-producer-outbox-data-only;producer-commit-provenance-and-receiver-ack-pending';
  authority_effect:'none'}>;
 assertCurrent():void;
 close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceCrossServiceEventRelay(owner:CoreCommerceCrossServiceEventRelay):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))throw new Error('original cross-service relay selector required');
 owner.assertCurrent();
}
const record=(value:unknown):Readonly<Record<string,unknown>>=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(value)))
  throw new Error('original bounded Event/outbox record required');
 const names=Reflect.ownKeys(value);
 if(names.length>128||names.some(name=>typeof name!=='string'||
  !Object.getOwnPropertyDescriptor(value,name)?.enumerable||
  !Object.hasOwn(Object.getOwnPropertyDescriptor(value,name)!, 'value')))
  throw new Error('original bounded Event/outbox fields required');
 return value as Readonly<Record<string,unknown>>;
};
const closedEventRow=(value:unknown):Readonly<Record<string,unknown>>=>{
 const row=record(value),keys=['logical_entry','event_type','event_version','argument','producer','target','context','native_family'];
 if(Reflect.ownKeys(row).length!==keys.length||keys.some(name=>!Object.hasOwn(row,name)))
  throw new Error('closed authored Event projection required');
 return row;
};
const transactions=(steps:readonly OperationControlStepV1[]):readonly TransactionPlanV1[]=>{
 const found:TransactionPlanV1[]=[];
 const visit=(rows:readonly OperationControlStepV1[]):void=>{
  for(const row of rows){
   if(row.kind==='transaction')found.push(row.transaction);
   else if(row.kind==='present'&&row.transaction)found.push(row.transaction);
   else if(row.kind==='conditional'){visit(row.then);visit(row.otherwise);}
   else if(row.kind==='read-set')visit(row.body);
  }
 };
 visit(steps);return found;
};

/** Original capture and semantic owner must be the same ones used by the
 * application assembly. No route DTO, receiver callback, or SQL is accepted. */
export function createCoreCommerceCrossServiceEventRelay(input:Readonly<{
 sources:CoreCommerceSourceOwner;capture:CoreCommerceSourceCapture;
 semantics:CoreCommerceSemanticOwner;semantic:CoreCommerceSemanticCapture;
 producer:CommerceServiceStorageOwnerV1;receiver:CommerceServiceStorageOwnerV1;
 entryId:string;
}>):CoreCommerceCrossServiceEventRelay {
 const {sources,capture,semantics,semantic,producer,receiver,entryId}=input;
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);
 semantics.assertSource(semantic,capture);assertCommerceServiceStorageOwnerV1(producer);
 assertCommerceServiceStorageOwnerV1(receiver);
 const captured=sources.inspect(capture),checked=semantics.inspect(semantic),
  producerStore=producer.inspect(),receiverStore=receiver.inspect(),model=captured.reconstruction;
 if(checked.source_capture_sha256!==captured.capture_sha256||
  producerStore.source_capture_sha256!==captured.capture_sha256||
  receiverStore.source_capture_sha256!==captured.capture_sha256||
  producerStore.family_sha256!==receiverStore.family_sha256||
  producerStore.store_id===receiverStore.store_id||
  typeof entryId!=='string'||!entryId)
  throw new Error('one original cross-service source and two distinct service stores required');
 const root=model.modules.flatMap(module=>module.declarations)
  .filter(declaration=>declaration.interface_kind==='application-composition');
 if(root.length!==1)throw new Error('one original application composition required');
 const types=createCoreValueTypes(model),catalog=createCoreContextCatalog(types,captured.files.filter(file=>file.path.endsWith('.json'))),
  asset=catalog.asset(root[0]!,['coordination-contract']),document=asset?.value;
 if(!document||typeof document!=='object'||Array.isArray(document))
  throw new Error('captured authored coordination profile required');
 const rawRows=(document as Record<string,unknown>).event_projection;
 if(!Array.isArray(rawRows)||rawRows.length<1||rawRows.length>128)
  throw new Error('bounded authored Event projection required');
 const matching=rawRows.map(closedEventRow).filter(row=>row.logical_entry===entryId);
 if(matching.length!==1)throw new Error('one selected cross-service Event projection required');
 const raw=matching[0]!,entry=checked.entries.find(row=>row.id===entryId);
 if(!entry||entry.interaction!=='event'||entry.access.principal_kind!=='service'||
  entry.access.producer!==raw.producer||entry.access.caller!==raw.producer||
  entry.event_argument!==raw.argument||entry.service!==receiverStore.service||
  raw.producer!==producerStore.service||producerStore.service===receiverStore.service||
  entry.invokes.role!=='Operation'||entry.invokes.module+'.'+entry.invokes.name!==raw.target||
  entry.access.event_completion!=='requires-original-consumer-inbox-and-result-commit'||
  entry.access.auth_route_id!=='commerce:'+entry.id||
  raw.native_family!=='EventInboxOutbox'||
  typeof raw.event_type!=='string'||typeof raw.argument!=='string'||
  raw.event_version!==1||typeof raw.context!=='string'||
  !entry.access.context.source_type.endsWith('.'+raw.context))
  throw new Error('authored Event projection differs from checked Entry and native family');
 const event=checked.pure.value_declarations.find(row=>row.name===raw.event_type&&row.role==='Event');
 if(!event||event.event_version!==raw.event_version||entry.parameters.length!==1||
  entry.parameters[0]!.name!==raw.argument||entry.parameters[0]!.type.kind!=='record'||
  entry.parameters[0]!.type.name!==event.name)
  throw new Error('selected Event payload differs from original Event Entry');
 const outboxes=model.modules.flatMap(module=>module.declarations).filter(declaration=>{
  if(declaration.surface!=='Entity'||declaration.identity.length!==1||declaration.identity[0]!=='eventId'||
   model.ownership.find(row=>row.declaration===declaration.id)?.service!==producerStore.service)return false;
  const field=declaration.fields.find(row=>row.name==='event');
  return !!field&&sameCoreValueType(types.type(declaration.module,field.type,field.span),
   {kind:'record',name:event.name});
 });
 const outbox=outboxes[0],state=outbox?.fields.find(row=>row.name==='state'),
  version=outbox?.fields.find(row=>row.name==='version');
 if(outboxes.length!==1||!state||!version||
  types.type(outbox!.module,state.type,state.span).kind!=='enum'||
  !sameCoreValueType(types.type(outbox!.module,version.type,version.span),{kind:'UInt64'}))
  throw new Error('one source-owned producer Event outbox required');
 const emissions=checked.effects.flatMap(operation=>
  operation.service===producerStore.service?transactions(operation.body).filter(transaction=>
   transaction.participants.includes(outboxes[0]!.id)&&
   transaction.body.some(step=>step.kind==='mutation'&&step.operation==='record-event'&&step.target===event.name)&&
   transaction.body.some(step=>step.kind==='mutation'&&step.operation==='create'&&step.target===outboxes[0]!.id))
   .map(transaction=>({operation:operation.operation.module+'.'+operation.operation.name,transaction})):[]);
 if(emissions.length!==1)throw new Error('one source-owned atomic Event and outbox emission required');
 const consumer=checked.effects.find(operation=>operation.operation.module+'.'+operation.operation.name===raw.target&&
  operation.service===receiverStore.service);
 const acknowledgements=consumer?.body.filter(step=>step.kind==='acknowledge')??[];
 if(!consumer||acknowledgements.length!==1)
  throw new Error('selected receiver Operation must acknowledge its original inbox');
 const inbox=acknowledgements[0]!.kind==='acknowledge'?acknowledgements[0]!.inbox:null;
 const consumerInbox=model.modules.flatMap(module=>module.declarations).find(declaration=>declaration.id===inbox);
 if(!inbox||!consumerInbox||consumerInbox.surface!=='Entity'||
  !isDeepStrictEqual(consumerInbox.identity,['consumerEntryId','occurrenceId'])||
  !consumerInbox.fields.some(field=>field.name==='receipt')||
  !consumerInbox.fields.some(field=>field.name==='eventFingerprint')||
  model.ownership.find(row=>row.declaration===inbox)?.service!==receiverStore.service||
  !transactions(consumer.body).some(transaction=>transaction.participants.includes(inbox)&&
   transaction.body.some(step=>step.kind==='mutation'&&step.operation==='create'&&step.target===inbox)))
  throw new Error('receiver acknowledgement lacks a source-owned atomic inbox commit');
 const route:EventRoute=coreFreeze({entry:entry.id,event_type:event.name,event_version:1,
  argument:entry.event_argument!,producer_service:producerStore.service,
  receiver_service:receiverStore.service,operation:raw.target as string,
  outbox_entity:outboxes[0]!.id,producer_operation:emissions[0]!.operation,
  consumer_inbox_entity:inbox,permission:entry.access.permission,
  auth_route_id:entry.access.auth_route_id,native_family:'EventInboxOutbox',
  source_capture_sha256:captured.capture_sha256,
  qualification:'checked-source-and-profile-cross-service-event-route;native-delivery-pending'});
 const issued=new WeakMap<object,{id:string;original:CommerceNativeValue}>();let closed=false;
 const current=()=>{
  if(closed)throw new Error('cross-service Event relay closed');
  sources.assertCurrent(capture);semantics.assertCurrent(semantic);
  producer.assertCurrent();receiver.assertCurrent();
  if(producer.inspect().store_id!==producerStore.store_id||
   receiver.inspect().store_id!==receiverStore.store_id||
   semantics.inspect(semantic).source_capture_sha256!==route.source_capture_sha256)
   throw new Error('cross-service Event owner or source changed');
 };
 const read=(id:string):CommerceNativeValue|null=>{
  current();
  if(typeof id!=='string'||!id.length||Buffer.byteLength(id)>128||Buffer.from(id).toString('utf8')!==id)
   throw new Error('bounded original Event occurrence required');
  const value=producer.inspectStoredRecord(route.outbox_entity,0,{eventId:id});
  if(value===null)return null;
  const outbox=record(value),payload=record(outbox.event),metadata=record(payload.metadata);
  if(outbox.eventId!==id||outbox.state!=='Ready'||
   typeof outbox.version!=='bigint'||outbox.version<1n||
   metadata.eventId!==id||metadata.producer!==route.producer_service||
   typeof metadata.aggregateId!=='string'||!metadata.aggregateId||
   typeof metadata.aggregateVersion!=='bigint'||metadata.aggregateVersion<1n||
   typeof metadata.ordinal!=='bigint'||metadata.ordinal<0n||
   typeof metadata.correlationId!=='string'||!metadata.correlationId||
   typeof metadata.commandId!=='string'||!metadata.commandId)
   throw new Error('committed producer outbox differs from selected Event identity');
  current();return value;
 };
 const owner:CoreCommerceCrossServiceEventRelay=Object.freeze({
  inspect(){current();return Object.freeze({route,producer_store_id:producerStore.store_id,
   receiver_store_id:receiverStore.store_id,
   qualification:'source-selected-cross-service-outbox-reader;native-event-delivery-and-ack-pending' as const});},
  scanReady(cursor:string|null,limit:number){
   current();const page=producer.scanReadySelectedEventOutbox(route,cursor,limit);
   for(const id of page.occurrence_ids){
    if(read(id)===null)throw new Error('selected Ready Event outbox changed during discovery');
   }
   current();return page;
  },
  readReady(id:string){const original=read(id);
   if(original===null)return Object.freeze({kind:'not-ready' as const,authority_effect:'none' as const});
   const occurrence:CoreCommerceCrossServiceOccurrence=Object.freeze({kind:'original-cross-service-outbox-occurrence/v1-candidate'});
   issued.set(occurrence,{id,original});return Object.freeze({kind:'ready' as const,occurrence});},
  inspectOccurrence(occurrence:CoreCommerceCrossServiceOccurrence){
   current();const saved=occurrence&&typeof occurrence==='object'?issued.get(occurrence):undefined;
   if(!saved)throw new Error('original cross-service outbox occurrence required');
   const fresh=read(saved.id);
   if(fresh===null||!isDeepStrictEqual(fresh,saved.original))
    throw new Error('cross-service Event occurrence changed');
   const outbox=record(fresh);
   return coreFreeze({route,occurrence_id:saved.id,event:outbox.event as CommerceNativeValue,
    outbox:fresh,qualification:'original-persisted-ready-producer-outbox-data-only;producer-commit-provenance-and-receiver-ack-pending' as const,
    authority_effect:'none' as const});
  },
  assertCurrent:current,close(){closed=true;},
 });
 owners.add(owner);current();return owner;
}
