import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceServiceArtifactOwner} from '../../src/generic/core-commerce-service-artifact-owner.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');
const expected=['catalog','fulfillment','inventory','orders','payments'];

test('C14 original Commerce source produces five physical service artifacts and a source-bound graph/bridge',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-core-artifacts-'));
 let owner;
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
  const manifest=owner.inspect();
  assert.equal(manifest.application,'Shop.Application.Ecommerce');
  assert.deepEqual(manifest.services.map(service=>service.id),expected);
  assert.equal(manifest.complete_application,true);
  assert.deepEqual(manifest.routes.map(route=>[route.method,route.path,route.entry]),[
   ['GET','/orders/{orderId}','Orders.GetOrderEntry'],
   ['POST','/orders','Orders.PlaceOrderEntry']]);
  assert.equal(manifest.routes.find(route=>route.method==='POST').request_bytes,4096);
  assert.equal(manifest.routes.find(route=>route.method==='GET').request_bytes,0);
  assert.deepEqual(manifest.routes.find(route=>route.method==='GET').success_projection,
   {query:'Orders.GetOrder',value_ref:'Orders.OrderView@1',kind:'unwrap-some'});
  assert.equal(manifest.http_error_statuses['route-not-found'],404);
  assert.equal(manifest.http_error_statuses['method-not-allowed'],405);
  assert.deepEqual(manifest.missing_complete_application_classes,[]);
  for(const service of manifest.services){
   assert.equal(service.source_capture_sha256,manifest.source_capture_sha256);
   assert.equal(service.family_sha256,manifest.family_sha256);
   assert.ok(service.files.some(file=>file.path==='store.sqlite'));
   assert.equal(owner.serviceStorage(service.id).inspect().store_id,service.store_id);
  }
  const artifacts=path.join(work,'generated','artifacts');
  const graph=JSON.parse(readFileSync(path.join(artifacts,'system-graph.json'),'utf8'));
  const bridge=JSON.parse(readFileSync(path.join(artifacts,'business-system-bridge.json'),'utf8'));
  assert.equal(graph.source_capture_sha256,manifest.source_capture_sha256);
  assert.equal(bridge.family_sha256,manifest.family_sha256);
  for(const [id,artifact] of [
   ['runtime:application','application.mjs'],
   ['runtime:workflow-worker','workflow-worker.mjs'],
   ['runtime:event-relay','event-relay.mjs']]){
   const file=manifest.files.find(row=>row.path===artifact);
   assert.ok(file,'emitted runtime must be in the physical manifest');
   assert.ok(graph.nodes.some(node=>node.id===id&&node.artifact===artifact&&node.sha256===file.sha256));
   assert.ok(bridge.links.some(link=>link.system===id));
  }
  for(const id of expected){
   assert.ok(graph.nodes.some(node=>node.id==='service:'+id));
   assert.ok(graph.nodes.some(node=>node.id==='storage:'+id&&node.artifact==='runtime/'+id+'/store.sqlite'));
   assert.ok(bridge.links.some(link=>link.business===id&&link.system==='service:'+id));
  }
  for(const route of manifest.routes){
   assert.ok(graph.nodes.some(node=>node.id==='http:'+route.id&&node.binding_file_sha256===route.binding_file_sha256));
   assert.ok(bridge.links.some(link=>link.business===route.entry&&link.system==='http:'+route.id&&link.permission===route.permission));
  }
  const selected=owner.selectHttpRoute('GET','/orders/order-7');
  assert.equal(selected.kind,'matched');
  assert.equal(selected.route.entry,'Orders.GetOrderEntry');
  assert.deepEqual(selected.path_parameters,{orderId:'order-7'});
  assert.deepEqual(owner.selectHttpRoute('GET','/orders'),{kind:'method-not-allowed',allow:['POST']});
  assert.deepEqual(owner.selectHttpRoute('POST','/missing'),{kind:'route-not-found'});
  assert.deepEqual(owner.selectHttpRoute('GET','/orders/%2F'),{kind:'route-not-found'});
  assert.equal(typeof owner.openSelectedEntryAuth,'function');
  assert.equal(typeof owner.openDemoPayDispatch,'function');
  assert.equal(typeof owner.openGeneratedOperation,'function');
  assert.equal(typeof owner.openGeneratedQuery,'function');
  const ingress=owner.openWorkflowIngress('Orders.Checkout.Checkout');
  const selectedWorkflow=ingress.inspect();
  assert.equal(selectedWorkflow.owner_service,'orders');
  assert.equal(selectedWorkflow.input_producer,'orders');
  assert.equal(selectedWorkflow.input_entry,'Orders.CheckoutStartEntry');
  assert.equal(selectedWorkflow.input_outbox_entity,'Orders.OrderPlacedOutbox');
  assert.equal(selectedWorkflow.source_capture_sha256,manifest.source_capture_sha256);
  assert.throws(()=>owner.openWorkflowIngress('missing.Workflow'),/one checked original Workflow required/);
  const relay=owner.openOutboxRelay('Orders.Checkout.Checkout');
  assert.equal(relay.inspect().input_outbox_entity,selectedWorkflow.input_outbox_entity);
  assert.deepEqual(await relay.relayPage(null,8),{results:[],next_cursor:null});
  await assert.rejects(()=>relay.relayPage(null,0),/InputType/);
  assert.equal(typeof owner.openSelectedHttpRuntime,'function');
  assert.throws(()=>owner.serviceStorage('absent'),/service absent/);
  owner.assertCurrent();
  const database=new DatabaseSync(path.join(work,'generated','runtime','orders','store.sqlite'));
  try{database.exec('CREATE TABLE unexpected_schema_change (id TEXT PRIMARY KEY)');}
  finally{database.close();}
  assert.throws(()=>owner.assertCurrent(),
   'assembly inspection must still reject an altered service schema');
 }finally{owner?.close();rmSync(work,{recursive:true,force:true});}
});
