import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, rmSync} from 'node:fs';
import path from 'node:path';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.ts';
import {createGenericEventTransactionSourceContract} from '../../src/generic/transaction-source.ts';
import {buildEventSourceFixture} from './C12-source-fixture.mjs';

function contract(root){const owner=createCoreCommerceSourceOwner('event-handoff-entry');return createGenericEventTransactionSourceContract(owner.inspect(owner.prepare(root))).contract;}
function edit(root,file,from,to){const p=path.join(root,file),before=readFileSync(p,'utf8');assert.ok(before.includes(from));writeFileSync(p,before.replace(from,to));}

for(const kind of ['request','permit'])test(`C12 frozen ${kind} Event source binds exact emit and receiver`,()=>{
 const root=buildEventSourceFixture(kind);
 try{
  const app=contract(root);
  assert.equal(app.admission_mode,'event-handoff-entry');
  assert.equal(app.event_bindings.length,1);
  assert.equal(app.external_bindings.length,0);
  assert.equal(app.write_bindings.length,0);
  const binding=app.event_bindings[0];
  assert.equal(binding.event_version,1);
  assert.ok(app.entries.some(e=>e.entry===binding.target_entry&&e.interaction==='event'));
  assert.ok(app.stateful_operations.some(o=>o.operation===binding.producer_operation&&o.transaction.body.some(s=>s.kind==='emit-event'&&s.binding_ref===binding.id&&s.emission_ordinal===0)));
 }finally{rmSync(path.dirname(root),{recursive:true,force:true});}
});

const negatives=[
 ['wrong payload type','request-service.alch','payload RequestApprovedPayload','payload Decision'],
 ['wrong Event version','request-service.alch','event RequestApproved version 1:','event RequestApproved version 2:'],
 ['wrong consumer entry','request-service.alch','delivered-to AuditService.RecordApprovedEntry','delivered-to AuditService.MissingEntry'],
 ['wrong emitted expression','request-service.alch','emit RequestApproved payload ToApprovedPayload(ToDecision(changed))','emit RequestApproved payload ToDecision(changed)'],
 ['missing emission','request-service.alch','    emit RequestApproved payload ToApprovedPayload(ToDecision(changed))\n',''],
 ['missing protected receiver permission','audit-service.alch','    permission audit-request.record\n',''],
];
for(const [name,file,from,to] of negatives)test(`C12 rejects ${name}`,()=>{
 const root=buildEventSourceFixture('request');
 try{edit(root,file,from,to);assert.throws(()=>contract(root));}
 finally{rmSync(path.dirname(root),{recursive:true,force:true});}
});
