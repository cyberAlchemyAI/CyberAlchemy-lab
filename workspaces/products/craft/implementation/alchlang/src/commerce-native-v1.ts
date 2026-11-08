// GENERATED Alch native API mirror; canonical owner is Core; interfaces implement no native support.
/** EC05 finite native module contracts. Interfaces implement no native support.
 * Open Questions: docs/COMMERCE-NATIVE-V1.md. */
import type {ComputationContractV1, EntryContractV1, RealizationScopeV1, RoleSelectorV1,
 TransactionPlanV1, ValueSchemaV1} from './commerce-data-v1.js';
import type {CommerceHandle, CommerceBindingAssemblyHandle, CommerceOperationInvocationHandle,
 CommerceBoundHandle, CommerceActorHandle, CommerceCausalHandle, CommerceEntryContextHandle,
 CommerceImportedHandle, CommerceNativeBasisHandle, CommerceResult, CommerceEvaluationResult,
 CommerceWorkerHandle} from './commerce-stages-v1.js';

/** UInt64 is bigint internally. Optionals are explicit tags; null exists only on
 * wire. All dictionaries are bounded checked data, never callbacks/contexts. */
export type CommerceNativeValue = boolean|string|bigint|readonly CommerceNativeValue[]|
 Readonly<{[key:string]:CommerceNativeValue}>;
export type CommerceOptional<T>={readonly kind:'none'}|{readonly kind:'some';readonly value:T};
export type CommerceSchemaHandle=CommerceHandle<'checked-codec-schema'>;
export type CommerceComputationHandle=CommerceHandle<'checked-computation'>;
export type CommerceCompiledComputationHandle=CommerceHandle<'compiled-computation-component'>;
export type CommerceCallsiteHandle=CommerceHandle<'original-checked-native-callsite'>;
export type CommerceServiceIdV1='catalog'|'orders'|'inventory'|'payments'|'fulfillment';
export type CommerceCommandNamespaceV1='inventory.reserve'|'payments.capture'|'inventory.allocate'|'inventory.release'|'orders.confirm'|'orders.cancel'|'inventory.reservation'|'fulfillment.shipment';
export type CommerceStockCommandKindV1='reserve'|'allocate'|'release';
export type CommerceOrderActionV1='confirm'|'cancel';
export type CommerceCancellationReasonV1='StockUnavailable'|'PaymentDeclined';
export type CommerceStockLineV1={readonly sku:string;readonly quantity:bigint};
export type CommerceEventMetadataV1={readonly eventId:string;readonly producer:CommerceServiceIdV1;readonly aggregateId:string;readonly aggregateVersion:bigint;readonly ordinal:bigint;readonly correlationId:string;readonly commandId:string};
export type CommerceIdentityHandle=CommerceHandle<'private-source-callsite-producers'> & CommerceIdentityProducersV1;
export type CommerceHttpEntryHandle=CommerceHandle<'bound-http-entry'>;
export type CommerceStoreDescriptorHandle=CommerceHandle<'original-generated-store-descriptor'>;
export type CommerceStoreHandle=CommerceHandle<'service-owned-store'> & {close():Promise<'closed'|'retained-active-resources'>};
export type CommerceTransactionHandle=CommerceHandle<'original-generated-transaction'>;
export type CommerceCommitReceipt=CommerceHandle<'actual-local-commit-receipt'>;
export type CommerceRollbackReceipt=CommerceHandle<'actual-proven-local-rollback'>;
export type CommerceTransactionTicket=CommerceHandle<'indeterminate-local-transaction'>;
export type CommerceCommandHandle=CommerceHandle<'original-command-inspection'>;
export type CommerceRawIoHandle=CommerceHandle<'registered-raw-infrastructure-port'>;
export type CommerceEventSlotHandle=CommerceHandle<'source-event-schema-slot'>;
export type CommerceOutboxRelayHandle=CommerceHandle<'original-service-outbox-relay'> & {relayOnce(bound:CommerceBoundHandle):Promise<CommerceResult<CommerceEventDeliveryV1>>;close():Promise<void>};
export type CommerceDemoPayHandle=CommerceHandle<'captured-demopay-v1-client'> & DemoPayClientOperationsV1;
export type CommerceServiceHandle=CommerceHandle<'original-generated-service-module'>;
export type CommercePortsHandle=CommerceHandle<'actual-composed-registered-ports'>;
export interface CommerceCodecFailure {readonly code:'InputType'|'InputBound'|'InvalidUnicode'|'OutputBound';readonly path:string;readonly byte_offset:number}
export type CommerceCodecResult<T>={readonly ok:true;readonly value:T}|{readonly ok:false;readonly error:CommerceCodecFailure};
export interface BoundedValuesNativeV1 {
 checkCommerceSchema(schema:ValueSchemaV1):CommerceResult<CommerceSchemaHandle>;
 decodeCommerceValue(schema:CommerceSchemaHandle,bytes:Uint8Array):CommerceCodecResult<CommerceNativeValue>;
 encodeCommerceValue(schema:CommerceSchemaHandle,value:CommerceNativeValue):CommerceCodecResult<Uint8Array>;
 copyCommerceValue(schema:CommerceSchemaHandle,value:CommerceNativeValue):CommerceCodecResult<CommerceNativeValue>;
}
export interface PureComputationNativeV2 {
 checkCommerceComputation(contract:ComputationContractV1):CommerceResult<CommerceComputationHandle>;
 compileCommerceComputation(checked:CommerceComputationHandle):CommerceCompiledComputationHandle;
 evaluateCommerceComputation(compiled:CommerceCompiledComputationHandle,input:Uint8Array):CommerceEvaluationResult;
}
/** Methods are source-selected by the original native owner. A caller cannot
 * supply an identity function, clock, hash implementation or business hook. */
export interface CommerceIdentityProducersV1 {
 checkoutFingerprint(logicalEntryId:string,customerId:string,quoteId:string):string;
 newOrderId(logicalEntryId:string,customerId:string,checkoutKey:string):string;
 commandId(namespace:CommerceCommandNamespaceV1,orderId:string):string;
 eventMetadata(producer:CommerceServiceIdV1,aggregateId:string,aggregateVersion:bigint,ordinal:bigint,correlationId:string,commandId:string):CommerceEventMetadataV1;
 stockLinesFingerprint(lines:readonly CommerceStockLineV1[]):string;
 stockCommandFingerprint(kind:CommerceStockCommandKindV1,orderId:string,lines:readonly CommerceStockLineV1[],expectedReservationVersion:CommerceOptional<bigint>):string;
 captureFingerprint(attemptKey:string,orderId:string,amountMinor:bigint,currency:'USD'):string;
 eventFingerprint(event:CommerceNativeValue):string;
 confirmedOrderFingerprint(orderId:string,customerId:string,lines:readonly CommerceStockLineV1[],payableMinor:bigint,currency:'USD',reservationId:string,reservationVersion:bigint,paymentAttemptKey:string,providerReference:string):string;
 orderActionFingerprint(action:CommerceOrderActionV1,orderId:string,reason:CommerceOptional<CommerceCancellationReasonV1>):string;
 clockEpochMs():bigint;
}
export interface IdentityContextNativeV1 {
 createCommerceIdentityProducers(invocation:CommerceOperationInvocationHandle,source:CommerceCallsiteHandle):CommerceIdentityHandle;
 assertCommerceIdentityContextCurrent(producers:CommerceIdentityHandle,invocation:CommerceOperationInvocationHandle):void;
}
export interface CommerceHttpConfigurationV1 {readonly request_bytes:number;readonly response_bytes:number;readonly body_timeout_ms:number}
export interface InjectedHttpNativeV1 {
 bindCommerceHttpEntry(assembly:CommerceBindingAssemblyHandle,entry:EntryContractV1,output:CommerceImportedHandle,configuration:CommerceHttpConfigurationV1):CommerceHttpEntryHandle;
 createCommerceRequestHandler(bound:CommerceBoundHandle,entries:readonly CommerceHttpEntryHandle[]):(request:Request)=>Promise<Response>;
}
/** Outcomes describe actual owner observations. A shape-identical result cannot
 * be supplied back as a receipt/ticket or used to renew invocation authority. */
export type CommerceTransactionOutcomeV1=
 {readonly kind:'committed';readonly receipt:CommerceCommitReceipt;readonly result:CommerceNativeValue}|
 {readonly kind:'version-conflict'|'unique-conflict';readonly rollback:CommerceRollbackReceipt}|
 {readonly kind:'rolled-back';readonly rollback:CommerceRollbackReceipt}|
 {readonly kind:'unavailable-before-start'}|
 {readonly kind:'indeterminate';readonly ticket:CommerceTransactionTicket};
export type CommerceCommandObservationV1=
 {readonly kind:'recorded';readonly value:CommerceNativeValue}|
 {readonly kind:'pending'|'unknown'|'missing'|'conflict'};
export interface ServiceSqliteNativeV1 {
 openCommerceStore(assembly:CommerceBindingAssemblyHandle,descriptor:CommerceStoreDescriptorHandle,absoluteScratchPath:string):CommerceResult<CommerceStoreHandle>;
 applyCommerceTransaction(invocation:CommerceOperationInvocationHandle,store:CommerceStoreHandle,plan:CommerceTransactionHandle,bindings:Readonly<Record<string,CommerceNativeValue>>):Promise<CommerceTransactionOutcomeV1>;
 readCommerceProjection(invocation:CommerceOperationInvocationHandle,store:CommerceStoreHandle,query:RoleSelectorV1,input:CommerceNativeValue):Promise<CommerceResult<CommerceNativeValue>>;
 inspectCommerceCommand(invocation:CommerceOperationInvocationHandle,store:CommerceStoreHandle,command:CommerceCommandHandle):Promise<CommerceCommandObservationV1>;
}
export interface AuthReadyNativeV1 {
 authorizeCommerceEntry(bound:CommerceBoundHandle,entry:string,inputBytes:Uint8Array,actor:CommerceActorHandle,causal:CommerceCausalHandle|null):Promise<CommerceResult<CommerceEntryContextHandle>>;
 consumeCommerceEntryContext(context:CommerceEntryContextHandle,entry:string,inputBytes:Uint8Array):CommerceOperationInvocationHandle;
 disposeCommerceEntryContext(context:CommerceEntryContextHandle):void;
}
/** Closed wire data only; this type cannot issue a producer or commit owner. */
export interface CommerceEventEnvelopeV1 {readonly schema_version:'craft.commerce-event/v1-candidate';readonly event_type:string;readonly event_version:'1';readonly event:CommerceNativeValue}
export interface CommerceEventDeliveryV1 {readonly transport_acceptance:'observed'|'not-observed'|'unknown';readonly consumer_completion:'observed-original-local-commit'|'not-observed'|'unknown'}
export interface EventInboxOutboxNativeV1 {
 encodeCommerceEvent(invocation:CommerceOperationInvocationHandle,slot:CommerceEventSlotHandle,event:CommerceNativeValue):CommerceCodecResult<Uint8Array>;
 createCommerceOutboxRelay(assembly:CommerceBindingAssemblyHandle,store:CommerceStoreHandle,port:CommerceRawIoHandle):CommerceOutboxRelayHandle;
 consumeCommerceEvent(bound:CommerceBoundHandle,entry:string,bytes:Uint8Array,producer:CommerceActorHandle):Promise<CommerceResult<CommerceEventDeliveryV1>>;
}
export interface DemoPayCaptureRequestV1 {readonly attemptKey:string;readonly orderId:string;readonly amountMinor:bigint;readonly currency:'USD'}
export interface DemoPayObservationV1 extends DemoPayCaptureRequestV1 {readonly status:'Captured'|'DefinitivelyDeclined'|'Pending'|'Unknown'|'UnknownKey';readonly providerReference:CommerceOptional<string>}
export interface DemoPayWireResponseV1 {readonly status:number;readonly headers:Readonly<Record<string,string>>;readonly bytes:Uint8Array}
export type DemoPayResultV1={readonly ok:true;readonly observation:DemoPayObservationV1}|
 {readonly ok:false;readonly code:'ProviderInputRejected'|'ProviderRequestConflict'|'ProviderTransportUnknown'|'ProviderProtocolRejected'};
export interface DemoPayClientOperationsV1 {
 Capture(invocation:CommerceOperationInvocationHandle,request:DemoPayCaptureRequestV1):Promise<DemoPayResultV1>;
 InspectCapture(invocation:CommerceOperationInvocationHandle,request:DemoPayCaptureRequestV1):Promise<DemoPayResultV1>;
}
export interface DemoPayNativeV1 {
 createDemoPayV1Client(assembly:CommerceBindingAssemblyHandle,port:CommerceRawIoHandle):CommerceDemoPayHandle;
 validateDemoPayV1Observation(operation:'Capture'|'InspectCapture',request:DemoPayCaptureRequestV1,response:DemoPayWireResponseV1):DemoPayResultV1;
}
export type CommerceWorkerClaimV1={readonly kind:'claimed';readonly worker:CommerceWorkerHandle}|
 {readonly kind:'contention'|'indeterminate'|'unavailable'};
export interface DurableWorkflowNativeV1 {
 createCommerceWorker(assembly:CommerceBindingAssemblyHandle,workflow:RoleSelectorV1,store:CommerceStoreHandle):CommerceWorkerHandle;
 claimCommerceWork(bound:CommerceBoundHandle,worker:CommerceWorkerHandle,consumerEntryId:string,occurrenceId:string):Promise<CommerceWorkerClaimV1>;
 resumeCommerceWork(bound:CommerceBoundHandle,worker:CommerceWorkerHandle):Promise<CommerceResult<'suspended'|'finished'|'contention'|'needs-review'>>;
}
export interface ServiceCompositionNativeV1 {
 composeCommerceServices(assembly:CommerceBindingAssemblyHandle,scope:RealizationScopeV1,services:readonly CommerceServiceHandle[],basis:CommerceNativeBasisHandle):CommercePortsHandle;
 bindCommercePorts(assembly:CommerceBindingAssemblyHandle,ports:CommercePortsHandle,output:CommerceImportedHandle):CommerceBoundHandle;
}
/** Transient binding/transaction definitions are private original graph/output
 * records. Their data shape alone does not authorize opening or changing state. */
export interface CommerceTransactionInspectionV1 {readonly source:RoleSelectorV1;readonly plan:TransactionPlanV1;readonly authority_effect:'none'}
