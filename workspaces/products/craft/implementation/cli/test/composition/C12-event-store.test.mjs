import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {DatabaseSync} from 'node:sqlite';
import {setTimeout as delay} from 'node:timers/promises';
import {deriveGenericEventOccurrence} from '../../src/generic/event-occurrence.ts';
import {GenericEventStore,checkGenericCommittedEventIntent,eventStorageSchemaSQL,emptyEventLedgerDigest} from '../../src/generic/event-store.ts';

const sha=value=>createHash('sha256').update(value).digest('hex');
const owned={store_id:'11111111-1111-4111-8111-111111111111',compatibility_sha256:'c'.repeat(64)};
const causal='d'.repeat(64);
const payload=Buffer.from('{"decision":"Approved","requestId":"R-001"}');
const intent=()=>({binding_ref:'RequestService.RequestApproved',binding_sha256:'b'.repeat(64),
  source_site:'RequestService.ApproveRequest/transaction/emit/0',
  event_selector:'RequestService.RequestApproved',event_version:1,emission_ordinal:0,
  target_service:'AuditService',target_entry:'AuditService.RecordApprovedEntry',
  route:'audit-service.record-approved',payload_schema_sha256:'a'.repeat(64),
  payload_sha256:sha(payload),payload_bytes:Buffer.from(payload)});
const setup=()=>{
 const db=new DatabaseSync(':memory:',{enableForeignKeyConstraints:true,enableDoubleQuotedStringLiterals:false,allowExtension:false,timeout:0,defensive:true});
 db.exec('PRAGMA trusted_schema=OFF; PRAGMA busy_timeout=0;');
 db.exec(eventStorageSchemaSQL);
 db.exec('CREATE TABLE business(id TEXT PRIMARY KEY,state TEXT NOT NULL) STRICT; CREATE TABLE command_journal(tuple_sha256 TEXT PRIMARY KEY) STRICT;');
 db.prepare('INSERT INTO _craft_event_epoch_v1 VALUES(1,?,?,0,?,0,?)').run(
   owned.store_id,owned.compatibility_sha256,emptyEventLedgerDigest,emptyEventLedgerDigest);
 return {db,store:new GenericEventStore(db,owned)};
};

test('C12 outbox insertion shares the original business/journal transaction',()=>{
 const {db,store}=setup();
 try{
  db.exec('BEGIN IMMEDIATE');
  db.prepare('INSERT INTO business VALUES(?,?)').run('R-001','Approved');
  db.prepare('INSERT INTO command_journal VALUES(?)').run(causal);
  const envelope=store.insertProducedInCommand(intent(),'RequestService',causal);
  assert.equal(envelope.occurrence_sha256,deriveGenericEventOccurrence({producer_namespace:'RequestService',
    causal_command_tuple_sha256:causal,event_selector:intent().event_selector,event_version:1,emission_ordinal:0}));
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM _craft_event_outbox_v1').get().n,1);
  db.exec('ROLLBACK');
  store.assertCurrent();
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM business').get().n,0);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM command_journal').get().n,0);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM _craft_event_outbox_v1').get().n,0);
  db.exec('BEGIN IMMEDIATE');
  db.prepare('INSERT INTO business VALUES(?,?)').run('R-001','Approved');
  db.prepare('INSERT INTO command_journal VALUES(?)').run(causal);
  store.insertProducedInCommand(intent(),'RequestService',causal);
  db.exec('COMMIT');
  store.assertCurrent();
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM business').get().n,1);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM command_journal').get().n,1);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM _craft_event_outbox_v1').get().n,1);
 }finally{db.close();}
});

test('C12 event identity keeps service IDs distinct from source module names',()=>{
 const {db,store}=setup();
 try{
  const produced={...intent(),event_selector:'ReviewDesk.ApprovalCommitted',target_entry:'Audit.RecordEntry',target_service:'AuditService'};
  db.exec('BEGIN IMMEDIATE');
  const envelope=store.insertProducedInCommand(produced,'ReviewDeskService',causal);
  db.exec('COMMIT');
  assert.equal(envelope.producer_namespace,'ReviewDeskService');
  assert.equal(envelope.event_selector,'ReviewDesk.ApprovalCommitted');
  assert.equal(envelope.target_entry,'Audit.RecordEntry');
 }finally{if(db.isTransaction)db.exec('ROLLBACK');db.close();}
});

test('C12 outbox refuses forged payload, duplicate occurrence, and source collision',()=>{
 const {db,store}=setup();
 try{
  assert.throws(()=>store.insertProducedInCommand(intent(),'RequestService',causal),/COMMAND_TRANSACTION_REQUIRED/);
  db.exec('BEGIN IMMEDIATE');
  assert.throws(()=>store.insertProducedInCommand({...intent(),payload_bytes:Buffer.from('{}')},'RequestService',causal),/PAYLOAD_IDENTITY/);
  store.insertProducedInCommand(intent(),'RequestService',causal);
  assert.throws(()=>store.insertProducedInCommand(intent(),'RequestService',causal),/C12_EVENT_DUPLICATE/);
  assert.throws(()=>store.insertProducedInCommand({...intent(),route:'audit-service.other'},'RequestService',causal),/C12_EVENT_COLLISION/);
  db.exec('COMMIT');
  store.assertCurrent();
 }finally{if(db.isTransaction)db.exec('ROLLBACK');db.close();}
});

test('C12 relay claim has a monotone fence and stale claim cannot continue',async()=>{
 const {db,store}=setup();
 try{
  db.exec('BEGIN IMMEDIATE');store.insertProducedInCommand(intent(),'RequestService',causal);db.exec('COMMIT');
  const first=store.claimNext('RequestService',1);assert.ok(first);
  assert.equal(first.fence,1);
  await delay(5);
  const second=store.claimNext('RequestService',60000);assert.ok(second);
  assert.equal(second.fence,2);
  assert.throws(()=>store.assertClaimCurrent(first),/STALE_CLAIM/);
  store.assertClaimCurrent(second);
  assert.equal(store.claimNext('RequestService',60000),null);
  assert.throws(()=>store.ackClaim(first),/STALE_CLAIM/);
  store.ackClaim(second);
  assert.equal(db.prepare('SELECT state FROM _craft_event_outbox_v1').get().state,'acked');
  assert.throws(()=>store.assertClaimCurrent(second),/STALE_CLAIM/);
  assert.equal(store.claimNext('RequestService',60000),null);
 }finally{db.close();}
});

test('C12 exact Event claim cannot capture another pending occurrence',()=>{
 const {db,store}=setup();
 try{
  db.exec('BEGIN IMMEDIATE');
  const first=store.insertProducedInCommand(intent(),'RequestService',causal);
  const second=store.insertProducedInCommand({...intent(),source_site:'RequestService.ApproveRequest/transaction/emit/1',emission_ordinal:1},'RequestService',causal);
  db.exec('COMMIT');
  assert.equal(store.claimExact('RequestService','f'.repeat(64),60000),null);
  const selected=store.claimExact('RequestService',second.occurrence_sha256,60000);
  assert.equal(selected.envelope.occurrence_sha256,second.occurrence_sha256);
  const remaining=store.claimNext('RequestService',60000);
  assert.equal(remaining.envelope.occurrence_sha256,first.occurrence_sha256);
 }finally{if(db.isTransaction)db.exec('ROLLBACK');db.close();}
});

test('C12 inbox stores exact envelope with consumer command and refuses collision',()=>{
 const {db,store}=setup();
 try{
  db.exec('BEGIN IMMEDIATE');const envelope=store.insertProducedInCommand(intent(),'RequestService',causal);db.exec('COMMIT');
  assert.deepEqual(store.inspectInbox(envelope),{kind:'absent'});
  const consumer='e'.repeat(64);
  db.exec('BEGIN IMMEDIATE');store.insertInboxInCommand(envelope,consumer);db.exec('COMMIT');
  assert.deepEqual(store.inspectInbox(envelope),{kind:'same',consumer_command_tuple_sha256:consumer});
  db.exec('BEGIN IMMEDIATE');
  assert.throws(()=>store.insertInboxInCommand(envelope,consumer),/C12_INBOX_DUPLICATE/);
  const changed=checkGenericCommittedEventIntent({...intent(),route:'audit-service.other'},'RequestService',causal);
  assert.deepEqual(store.inspectInbox(changed),{kind:'collision',consumer_command_tuple_sha256:consumer});
  db.exec('ROLLBACK');store.assertCurrent();
 }finally{if(db.isTransaction)db.exec('ROLLBACK');db.close();}
});
