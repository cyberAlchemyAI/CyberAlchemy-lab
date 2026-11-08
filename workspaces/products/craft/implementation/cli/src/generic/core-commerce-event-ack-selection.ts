/** Source-owned selection of the receiver's Event acknowledgement paths.
 * This binds the checked Entry to the original local Operation plan; it does
 * not turn a stored inbox row or a caller receipt into a native commit witness.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture}
 from '../commerce/commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from '../commerce/commerce-core-semantic-owner.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1}
 from '../commerce/commerce-local-plan-owner-v1.js';
import {assertCoreCommerceCrossServiceEventRelay,type CoreCommerceCrossServiceEventRelay}
 from './core-commerce-cross-service-event-relay.js';
import {selectCoreCommerceEventAckSource,type CoreCommerceEventAckSource}
 from './core-commerce-event-ack-source.js';

export interface CoreCommerceEventAckSelection {
 inspect():Readonly<{source:CoreCommerceEventAckSource;source_capture_sha256:string;
  receiver_service:string;receiver_store_id:string;
  qualification:'source-selected-receiver-ack-paths;native-inbox-commit-witness-pending';
  authority_effect:'none'}>;
 assertCurrent():void;close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceEventAckSelection(owner:CoreCommerceEventAckSelection):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))
  throw new Error('original source-selected Event acknowledgement required');
 owner.assertCurrent();
}

/** The caller supplies only original owners, never an Entry/Operation DTO or
 * a candidate inbox path. The local plan owns the checked transaction paths. */
export function createCoreCommerceEventAckSelection(input:Readonly<{
 sources:CoreCommerceSourceOwner;capture:CoreCommerceSourceCapture;
 semantics:CoreCommerceSemanticOwner;semantic:CoreCommerceSemanticCapture;
 plans:CommerceLocalPlanOwnerV1;relay:CoreCommerceCrossServiceEventRelay;
}>):CoreCommerceEventAckSelection {
 const {sources,capture,semantics,semantic,plans,relay}=input;
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);
 semantics.assertSource(semantic,capture);assertCommerceLocalPlanOwnerV1(plans);
 assertCoreCommerceCrossServiceEventRelay(relay);
 const route=relay.inspect().route,checked=semantics.inspect(semantic);
 if(checked.source_capture_sha256!==route.source_capture_sha256)
  throw new Error('one original Event source capture required');
 const entries=checked.entries.filter(row=>row.id===route.entry);
 if(entries.length!==1)throw new Error('one checked receiver Event Entry required');
 const operation=plans.bindOperation(route.operation);
 let closed=false;
 try{
  const inspected=plans.inspectOperation(operation);
  if(inspected.source_capture_sha256!==route.source_capture_sha256||
   inspected.operation!==route.operation)
   throw new Error('original receiver Operation plan differs from Event route');
  const source=selectCoreCommerceEventAckSource(entries[0]!,inspected.plan,
   inspected.transactions.map(row=>({path:row.path,plan:row.plan})));
  if(source.entry!==route.entry||source.operation!==route.operation||
   source.inbox_entity!==route.consumer_inbox_entity)
   throw new Error('original Event acknowledgement differs from receiver inbox');
  const snapshot=coreFreeze({source,source_capture_sha256:route.source_capture_sha256,
   receiver_service:route.receiver_service,receiver_store_id:relay.inspect().receiver_store_id,
   qualification:'source-selected-receiver-ack-paths;native-inbox-commit-witness-pending' as const,
   authority_effect:'none' as const});
  const current=()=>{
   if(closed)throw new Error('Event acknowledgement selection closed');
   sources.assertCurrent(capture);semantics.assertSource(semantic,capture);
   plans.assertOperationCurrent(operation);relay.assertCurrent();
   if(relay.inspect().route.source_capture_sha256!==snapshot.source_capture_sha256||
    relay.inspect().receiver_store_id!==snapshot.receiver_store_id)
    throw new Error('Event acknowledgement source or receiver store changed');
  };
  const owner:CoreCommerceEventAckSelection=Object.freeze({
   inspect(){current();return snapshot;},assertCurrent:current,
   close(){if(closed)return;closed=true;plans.disposeOperation(operation);},
  });
  owners.add(owner);current();return owner;
 }catch(error){if(!closed)plans.disposeOperation(operation);throw error;}
}
