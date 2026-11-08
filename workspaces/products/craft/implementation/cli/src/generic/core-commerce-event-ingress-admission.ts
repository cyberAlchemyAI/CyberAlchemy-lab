/** Source-bound admission data for an original cross-service Event occurrence.
 * This owner cannot authorize, invoke, acknowledge, or mutate either store.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {isDeepStrictEqual} from 'node:util';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import {evaluateCommerceFlowDataV1} from '../commerce/commerce-flow-expression-data-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from '../commerce/commerce-core-semantic-owner.js';
import {assertCoreCommerceCrossServiceEventRelay,type CoreCommerceCrossServiceEventRelay,
 type CoreCommerceCrossServiceOccurrence} from './core-commerce-cross-service-event-relay.js';
import type {FlowExprV1} from '../commerce/commerce-data-v1.js';

export interface CoreCommerceEventIngressTicket {
 readonly kind:'original-cross-service-event-ingress-admission/v1-candidate';
}
export interface CoreCommerceEventIngressAdmission {
 prepare(occurrence:CoreCommerceCrossServiceOccurrence):CoreCommerceEventIngressTicket;
 inspectTicket(ticket:CoreCommerceEventIngressTicket):Readonly<{
  entry:string;operation:string;producer_service:string;receiver_service:string;
  occurrence_id:string;parameters:Readonly<Record<string,unknown>>;
  qualification:'original-outbox-and-checked-entry-resource-data-only;fresh-auth-and-receiver-commit-pending';
  authority_effect:'none';
 }>;
 assertCurrent():void;
 close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceEventIngressAdmission(owner:CoreCommerceEventIngressAdmission):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))
  throw new Error('original Event ingress admission owner required');
 owner.assertCurrent();
}

/** The relay is the only occurrence producer. The checked Entry condition is
 * evaluated over the exact persisted Event, with no caller-supplied payload. */
export function createCoreCommerceEventIngressAdmission(input:Readonly<{
 relay:CoreCommerceCrossServiceEventRelay;
 semantics:CoreCommerceSemanticOwner;semantic:CoreCommerceSemanticCapture;
}>):CoreCommerceEventIngressAdmission {
 const {relay,semantics,semantic}=input;
 assertCoreCommerceCrossServiceEventRelay(relay);assertCoreCommerceSemanticOwner(semantics);
 semantics.assertCurrent(semantic);
 const route=relay.inspect().route,checked=semantics.inspect(semantic),
  entry=checked.entries.find(row=>row.id===route.entry);
 if(checked.source_capture_sha256!==route.source_capture_sha256||
  !entry||entry.interaction!=='event'||entry.service!==route.receiver_service||
  entry.event_argument!==route.argument||entry.invokes.role!=='Operation'||
  entry.invokes.module+'.'+entry.invokes.name!==route.operation||
  entry.access.producer!==route.producer_service||entry.access.caller!==route.producer_service||
  entry.access.principal_kind!=='service'||entry.access.permission!==route.permission||
  entry.access.auth_route_id!==route.auth_route_id||
  entry.access.resource_phase!=='causal-before-invocation'||
  entry.access.matching_replay_resource_check!=='not-applicable'||
  entry.access.on_resource_missing_or_false!=='forbidden'||
  entry.access.resource_bindings.length!==0||!entry.access.resource_condition||
  entry.access.resource_condition.local_records.length!==1||
  entry.access.resource_condition.local_records[0]!.name!==entry.id+'.CoreEntryInput'||
  entry.access.resource_condition.local_records[0]!.public_constructor!==false||
  entry.access.resource_condition.local_records[0]!.qualification!=='source-local-projection-data-only'||
  entry.parameters.length!==1||entry.parameters[0]!.name!==route.argument)
  throw new Error('selected Event Entry must use its checked local input condition');
 const condition=entry.access.resource_condition.expression;
 let nodes=0;
 const scan=(expression:FlowExprV1,depth:number):void=>{
  if(++nodes>128||depth>32)throw new Error('bounded Event resource condition required');
  if(expression.op==='field'){scan(expression.value,depth+1);return;}
  if(expression.op==='var'){
   if(expression.name!=='input')throw new Error('Event resource condition must use only original input');
   return;
  }
  if(expression.op==='literal')return;
  if(expression.op==='binary'&&['eq','and'].includes(expression.operator)){
   scan(expression.left,depth+1);scan(expression.right,depth+1);return;
  }
  throw new Error('unsupported Event resource condition');
 };
 scan(condition,0);
 let closed=false;
 const issued=new WeakMap<object,{occurrence:CoreCommerceCrossServiceOccurrence;id:string;event:unknown}>();
 const current=()=>{
  if(closed)throw new Error('Event ingress admission closed');
  semantics.assertCurrent(semantic);
  const observed=relay.inspect().route;
  if(observed!==route&&!isDeepStrictEqual(observed,route))
   throw new Error('selected Event route changed');
 };
 const checkedOccurrence=(occurrence:CoreCommerceCrossServiceOccurrence)=>{
  current();const view=relay.inspectOccurrence(occurrence);
  if(view.route.entry!==route.entry||view.route.source_capture_sha256!==route.source_capture_sha256||
   view.route.producer_service!==route.producer_service||view.route.receiver_service!==route.receiver_service)
   throw new Error('original selected Event occurrence required');
  const parameters=coreFreeze({[route.argument]:view.event});
  let fuel=0;
  const allowed=evaluateCommerceFlowDataV1(condition,'$.access.resource_condition.expression',
   {input:parameters},{
    charge(){if(++fuel>512)throw new Error('bounded Event resource evaluation required');},
    pure(){throw new Error('Event resource condition cannot call pure code');},
    native(){throw new Error('Event resource condition cannot call native code');},
    context(){throw new Error('Event resource condition cannot use private context');},
    isNullaryEnum(){return false;},
   });
  if(allowed!==true)throw new Error('original Event resource condition false');
  return {view,parameters};
 };
 const owner:CoreCommerceEventIngressAdmission=Object.freeze({
  prepare(occurrence:CoreCommerceCrossServiceOccurrence){const {view}=checkedOccurrence(occurrence);
   const ticket:CoreCommerceEventIngressTicket=Object.freeze({kind:'original-cross-service-event-ingress-admission/v1-candidate'});
   issued.set(ticket,{occurrence,id:view.occurrence_id,event:view.event});return ticket;},
  inspectTicket(ticket:CoreCommerceEventIngressTicket){current();const saved=ticket&&typeof ticket==='object'?issued.get(ticket):undefined;
   if(!saved)throw new Error('original Event ingress ticket required');
   const {view,parameters}=checkedOccurrence(saved.occurrence);
   if(view.occurrence_id!==saved.id||!isDeepStrictEqual(view.event,saved.event))
    throw new Error('original Event occurrence changed');
   return coreFreeze({entry:route.entry,operation:route.operation,
    producer_service:route.producer_service,receiver_service:route.receiver_service,
    occurrence_id:view.occurrence_id,parameters,
    qualification:'original-outbox-and-checked-entry-resource-data-only;fresh-auth-and-receiver-commit-pending' as const,
    authority_effect:'none' as const});
  },
  assertCurrent:current,close(){closed=true;},
 });
 owners.add(owner);current();return owner;
}
