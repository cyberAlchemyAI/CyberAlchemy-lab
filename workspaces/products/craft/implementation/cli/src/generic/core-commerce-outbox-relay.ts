/** Bounded source-selected relay from committed producer outbox to checked
 * Workflow inbox/schedule. A worker must claim and execute the schedule.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import type {CommerceWorkflowEnqueueResultV1} from '../commerce/commerce-service-storage-v1.js';
import {assertCoreCommerceWorkflowIngress,type CoreCommerceWorkflowIngress} from './core-commerce-workflow-ingress.js';

export interface CoreCommerceOutboxRelay {
 inspect():ReturnType<CoreCommerceWorkflowIngress['inspect']>;
 relayPage(cursor:string|null,limit:number):Promise<Readonly<{
  results:readonly Readonly<{occurrence_id:string;outcome:CommerceWorkflowEnqueueResultV1}>[];
  next_cursor:string|null;
 }>>;
 assertCurrent():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceOutboxRelay(owner:CoreCommerceOutboxRelay):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))throw new Error('original checked outbox relay required');
 owner.assertCurrent();
}
export function createCoreCommerceOutboxRelay(ingress:CoreCommerceWorkflowIngress):CoreCommerceOutboxRelay {
 assertCoreCommerceWorkflowIngress(ingress);
 const selection=ingress.inspect();
 const current=()=>{
  ingress.assertCurrent();
  const now=ingress.inspect();
  if(now.source_capture_sha256!==selection.source_capture_sha256||now.workflow!==selection.workflow||
    now.owner_service!==selection.owner_service||now.input_outbox_entity!==selection.input_outbox_entity)
   throw new Error('selected outbox relay source changed');
 };
 const owner:CoreCommerceOutboxRelay=Object.freeze({
  inspect(){current();return selection;},
  async relayPage(cursor:string|null,limit:number){
   current();const page=ingress.scanReady(cursor,limit);
   const results:{occurrence_id:string;outcome:CommerceWorkflowEnqueueResultV1}[]=[];
   for(const id of page.occurrence_ids){
    current();const outcome=await ingress.enqueue(id);
    results.push(Object.freeze({occurrence_id:id,outcome}));
   }
   current();return Object.freeze({results:Object.freeze(results),next_cursor:page.next_cursor});
  },
  assertCurrent:current,
 });
 owners.add(owner);current();return owner;
}
