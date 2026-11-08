import test from 'node:test';
import assert from 'node:assert/strict';
import {selectCoreCommerceWorkerActorRequirements} from '../../src/generic/core-commerce-worker-actor-selection.ts';

const call=(entry,target,role='Operation')=>({entry,target,role});
const entry=(id,target,service,permission,role='Operation')=>({id,service,interaction:'request-response',
 invokes:{module:target.split('.')[0],role,name:target.split('.')[1]},
 access:{principal_kind:'service',caller:'orders',permission,auth_route_id:'route:'+id,
  auth_permission:{resource:service,action:permission,scope:'shop'}}});

test('C14 Workflow service actors derive from driver/remote calls and inline Entry permissions',()=>{
 const workflow={owner:'orders',drivers:[{kind:'claim',call:call('Orders.ClaimEntry','Orders.Claim')},
  {kind:'snapshot',call:call('Orders.SnapshotEntry','Orders.ReadSnapshot','Query')},
  {kind:'observation',call:call('Orders.ObserveEntry','Orders.Observe')}],
  steps:[{kind:'remote',name:'reserve',call:call('Inventory.ReserveEntry','Inventory.Reserve')}],};
 const rows=selectCoreCommerceWorkerActorRequirements(workflow,[
  entry('Orders.ClaimEntry','Orders.Claim','orders','orders.claim'),
  entry('Orders.SnapshotEntry','Orders.ReadSnapshot','orders','orders.snapshot','Query'),
  entry('Orders.ObserveEntry','Orders.Observe','orders','orders.observe'),
  entry('Inventory.ReserveEntry','Inventory.Reserve','inventory','inventory.reserve')]);
 assert.deepEqual(rows.map(row=>[row.usage,row.entry,row.caller_service,row.target_service,row.permission]),[
  ['claim','Orders.ClaimEntry','orders','orders','orders.claim'],
  ['snapshot','Orders.SnapshotEntry','orders','orders','orders.snapshot'],
  ['observation','Orders.ObserveEntry','orders','orders','orders.observe'],
  ['remote','Inventory.ReserveEntry','orders','inventory','inventory.reserve']]);
 assert.equal(rows[3].auth_route_id,'route:Inventory.ReserveEntry');
});

test('C14 Workflow actor selection rejects mismatched caller, target, and permission owner',()=>{
 const workflow={owner:'orders',drivers:[{kind:'claim',call:call('Orders.ClaimEntry','Orders.Claim')}],steps:[]};
 const valid=entry('Orders.ClaimEntry','Orders.Claim','orders','orders.claim');
 for(const altered of [
  {...valid,access:{...valid.access,caller:'inventory'}},
  {...valid,invokes:{...valid.invokes,name:'Other'}},
  {...valid,access:{...valid.access,principal_kind:'customer'}},
 ])assert.throws(()=>selectCoreCommerceWorkerActorRequirements(workflow,[altered]),/exact checked service Entry/);
});
