/** The complete Commerce graph must expose the generated Workflow/Event path.
 * Opt in after the C13/C14 executable path is qualified; the current artifact
 * projection still reports these classes as missing.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceServiceArtifactOwner}
 from '../../src/generic/core-commerce-service-artifact-owner.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 complete Commerce graph and bridge trace source-selected Workflow and Event delivery',
 {skip:process.env.CRAFT_C14_GRAPH_FULL_RUN!=='1'},async()=>{
  const work=mkdtempSync(path.join('/var/tmp','craft-c14-complete-graph-'));
  let owner,successful=false;
  try{
   owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
   const manifest=owner.inspect(),artifacts=path.join(work,'generated','artifacts');
   const graph=JSON.parse(readFileSync(path.join(artifacts,'system-graph.json'),'utf8'));
   const bridge=JSON.parse(readFileSync(path.join(artifacts,'business-system-bridge.json'),'utf8'));
   assert.equal(graph.source_capture_sha256,manifest.source_capture_sha256);
   assert.equal(bridge.source_capture_sha256,manifest.source_capture_sha256);
   assert.equal(graph.family_sha256,manifest.family_sha256);
   assert.equal(bridge.family_sha256,manifest.family_sha256);
   const nodes=new Map(graph.nodes.map(node=>[node.id,node]));
   assert.equal(nodes.size,graph.nodes.length,'generated graph node IDs must be unique');
   const requiredNodes=[
    ['workflow:Orders.Checkout.Checkout','workflow','Orders.Checkout.Checkout'],
    ['event:Shop.Events.OrderPlaced','event','Shop.Events.OrderPlaced'],
    ['event:Shop.Events.OrderConfirmed','event','Shop.Events.OrderConfirmed'],
    ['entry:Orders.CheckoutStartEntry','entry','Orders.CheckoutStartEntry'],
    ['entry:Orders.ConfirmOrderEntry','entry','Orders.ConfirmOrderEntry'],
    ['entry:Fulfillment.OnOrderConfirmed','entry','Fulfillment.OnOrderConfirmed'],
    ['outbox:Orders.OrderConfirmedOutbox','event-outbox','Orders.OrderConfirmedOutbox'],
    ['inbox:Fulfillment.ShipmentInbox','event-inbox','Fulfillment.ShipmentInbox'],
    ['publication:Shop.Events.OutboxPublication','event-publication','Shop.Events.OutboxPublication'],
   ];
   for(const [id,kind,selector] of requiredNodes){
    const node=nodes.get(id);assert.ok(node,`missing generated node ${id}`);
    assert.equal(node.kind,kind);assert.equal(node.source_selector,selector);
   }
   const edges=new Set(graph.edges.map(edge=>`${edge.from}|${edge.relation}|${edge.to}`));
   assert.equal(edges.size,graph.edges.length,'generated graph edges must be unique');
   for(const [from,relation,to] of [
    ['service:orders','owns-workflow','workflow:Orders.Checkout.Checkout'],
    ['event:Shop.Events.OrderPlaced','delivers-event','entry:Orders.CheckoutStartEntry'],
    ['entry:Orders.CheckoutStartEntry','starts-workflow','workflow:Orders.Checkout.Checkout'],
    ['workflow:Orders.Checkout.Checkout','invokes-entry','entry:Orders.ConfirmOrderEntry'],
    ['entry:Orders.ConfirmOrderEntry','produces-event','event:Shop.Events.OrderConfirmed'],
    ['service:orders','owns-outbox','outbox:Orders.OrderConfirmedOutbox'],
    ['outbox:Orders.OrderConfirmedOutbox','contains-event','event:Shop.Events.OrderConfirmed'],
    ['event:Shop.Events.OrderConfirmed','delivers-event','entry:Fulfillment.OnOrderConfirmed'],
    ['service:fulfillment','owns-entry','entry:Fulfillment.OnOrderConfirmed'],
    ['entry:Fulfillment.OnOrderConfirmed','commits-inbox','inbox:Fulfillment.ShipmentInbox'],
    ['publication:Shop.Events.OutboxPublication','transitions-outbox','outbox:Orders.OrderConfirmedOutbox'],
   ])assert.ok(edges.has(`${from}|${relation}|${to}`),`missing generated edge ${from} ${relation} ${to}`);
   assert.ok(graph.edges.every(edge=>nodes.has(edge.from)&&nodes.has(edge.to)),
    'every generated edge must end at an emitted node');
   const links=new Set(bridge.links.map(link=>`${link.business}|${link.system}`));
   for(const [business,system] of [
    ['Orders.Checkout.Checkout','workflow:Orders.Checkout.Checkout'],
    ['Shop.Events.OrderPlaced','event:Shop.Events.OrderPlaced'],
    ['Shop.Events.OrderConfirmed','event:Shop.Events.OrderConfirmed'],
    ['Orders.CheckoutStartEntry','entry:Orders.CheckoutStartEntry'],
    ['Orders.ConfirmOrderEntry','entry:Orders.ConfirmOrderEntry'],
    ['Fulfillment.OnOrderConfirmed','entry:Fulfillment.OnOrderConfirmed'],
    ['Orders.OrderConfirmedOutbox','outbox:Orders.OrderConfirmedOutbox'],
    ['Fulfillment.ShipmentInbox','inbox:Fulfillment.ShipmentInbox'],
    ['Shop.Events.OutboxPublication','publication:Shop.Events.OutboxPublication'],
   ])assert.ok(links.has(`${business}|${system}`),`missing business-system bridge ${business}`);
   assert.ok(bridge.links.every(link=>nodes.has(link.system)),
    'every bridge link must point to an emitted system node');
   // The structure can be checked while the executable C13/C14 path is still
   // being completed. The final run must also prove the complete manifest.
   if(process.env.CRAFT_C14_GRAPH_STRUCTURE_ONLY!=='1'){
    assert.equal(manifest.complete_application,true);
    assert.deepEqual(manifest.missing_complete_application_classes,[]);
   }
   successful=true;
  }finally{
   owner?.close();
   if(successful)rmSync(work,{recursive:true,force:true});
   else console.error('C14 complete graph diagnostic fixture retained at '+work);
  }
 });
