/** Source-selected producer transaction for the finite Core Event family.
 * This is only a checked plan selector; a native commit and stored rows are
 * required before an emitted occurrence gains producer provenance.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from '../commerce/commerce-core-semantic-owner.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1}
 from '../commerce/commerce-local-plan-owner-v1.js';
import {assertCoreCommerceCrossServiceEventRelay,type CoreCommerceCrossServiceEventRelay}
 from './core-commerce-cross-service-event-relay.js';
import type {TransactionStepV1} from '../commerce/commerce-data-v1.js';

export interface CoreCommerceEventProducerSource {
 inspect():Readonly<{entry:string;operation:string;service:string;
  transaction:string;transaction_path:string;event_type:string;outbox_entity:string;
  action_entity:string;event_binding:string;outbox_binding:string;action_binding:string;
  source_capture_sha256:string;
  qualification:'checked-atomic-producer-event-outbox-and-action-plan-only';
  authority_effect:'none'}>;
 assertCurrent():void;close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceEventProducerSource(owner:CoreCommerceEventProducerSource):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))
  throw new Error('original Event producer source selector required');
 owner.assertCurrent();
}

export function createCoreCommerceEventProducerSource(input:Readonly<{
 semantics:CoreCommerceSemanticOwner;semantic:CoreCommerceSemanticCapture;
 plans:CommerceLocalPlanOwnerV1;relay:CoreCommerceCrossServiceEventRelay;
}>):CoreCommerceEventProducerSource {
 const {semantics,semantic,plans,relay}=input;
 assertCoreCommerceSemanticOwner(semantics);assertCommerceLocalPlanOwnerV1(plans);
 assertCoreCommerceCrossServiceEventRelay(relay);
 const route=relay.inspect().route,checked=semantics.inspect(semantic),
  entries=checked.entries.filter(row=>row.invokes.role==='Operation'&&
   row.invokes.module+'.'+row.invokes.name===route.producer_operation&&
   row.service===route.producer_service);
 if(checked.source_capture_sha256!==route.source_capture_sha256||entries.length!==1)
  throw new Error('one original producer Operation Entry required');
 const operation=plans.bindOperation(route.producer_operation);
 let closed=false;
 try{
  const selected=plans.inspectOperation(operation);
  if(selected.source_capture_sha256!==route.source_capture_sha256||
   selected.plan.service!==route.producer_service)
   throw new Error('producer Operation plan differs from selected Event route');
  const rows=selected.transactions.flatMap(row=>{
   const mutations=row.plan.body.filter((step):step is Extract<TransactionStepV1,{kind:'mutation'}>=>
    step.kind==='mutation'),
    events=mutations.filter(step=>step.operation==='record-event'&&step.target===route.event_type),
    outboxes=mutations.filter(step=>step.operation==='create'&&
     step.target===route.outbox_entity),
    actions=mutations.filter(step=>step.operation==='create'&&
     step.target!==route.outbox_entity&&
     ['commandId','orderId','requestFingerprint','result'].every(field=>
      step.fields.some(value=>value.name===field)));
   if(!row.plan.participants.includes(route.outbox_entity)||events.length!==1||
    outboxes.length!==1||actions.length!==1||
    !row.plan.participants.includes(actions[0]!.target))return [];
   const event=events[0]!,outbox=outboxes[0]!;
   if(!outbox.fields.some(field=>field.name==='eventId')||
    !outbox.fields.some(field=>field.name==='event'&&
     field.value.expression.op==='var'&&field.value.expression.name===event.binding)||
    !outbox.fields.some(field=>field.name==='state')||
    !outbox.fields.some(field=>field.name==='version'))return [];
   return [{transaction:row.plan.name,path:row.path,action:actions[0]!.target,
    eventBinding:event.binding,outboxBinding:outbox.binding,
    actionBinding:actions[0]!.binding}];
  });
  if(rows.length!==1)throw new Error('one checked atomic producer Event/outbox/action transaction required');
  const record=coreFreeze({entry:entries[0]!.id,operation:route.producer_operation,
   service:route.producer_service,transaction:rows[0]!.transaction,
   transaction_path:rows[0]!.path,event_type:route.event_type,
   outbox_entity:route.outbox_entity,action_entity:rows[0]!.action,
   event_binding:rows[0]!.eventBinding,outbox_binding:rows[0]!.outboxBinding,
   action_binding:rows[0]!.actionBinding,
   source_capture_sha256:route.source_capture_sha256,
   qualification:'checked-atomic-producer-event-outbox-and-action-plan-only' as const,
   authority_effect:'none' as const});
  const current=()=>{
   if(closed)throw new Error('Event producer source selector closed');
   semantics.assertCurrent(semantic);plans.assertOperationCurrent(operation);relay.assertCurrent();
   if(relay.inspect().route.source_capture_sha256!==record.source_capture_sha256)
    throw new Error('Event producer source changed');
  };
  const owner:CoreCommerceEventProducerSource=Object.freeze({
   inspect(){current();return record;},assertCurrent:current,
   close(){if(closed)return;closed=true;plans.disposeOperation(operation);},
  });
  owners.add(owner);current();return owner;
 }catch(error){if(!closed)plans.disposeOperation(operation);throw error;}
}
