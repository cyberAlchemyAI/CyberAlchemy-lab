/** C12 original SQLite event storage data and physical protocol.
 * The generic repository owns the database and checks execution/relay custody
 * before calling this module. No caller event DTO or test callback mints an event.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';
import {DatabaseSync} from 'node:sqlite';
import {deriveGenericEventOccurrence} from './event-occurrence.js';
import {canonicalJson,type Json} from '../profile-engine/contracts.js';

export type GenericCommittedEventIntent=Readonly<{
  binding_ref:string;
  binding_sha256:string;
  source_site:string;
  event_selector:string;
  event_version:1;
  emission_ordinal:number;
  target_service:string;
  target_entry:string;
  route:string;
  payload_schema_sha256:string;
  payload_sha256:string;
  payload_bytes:Uint8Array;
}>;

export type GenericEventEnvelope=Readonly<GenericCommittedEventIntent&{
  producer_namespace:string;
  causal_command_tuple_sha256:string;
  occurrence_sha256:string;
  envelope_sha256:string;
}>;

const HEX=/^[0-9a-f]{64}$/;
const NAME=/^[A-Za-z_][A-Za-z0-9_]*$/;
const QUALIFIED=/^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$/;
const MAX_ROWS=1024;
const MAX_PAYLOAD_BYTES=1048576;
const sha=(value:Uint8Array|string)=>createHash('sha256').update(value).digest('hex');

function checkedPayload(bytes:Uint8Array,expected:string):Buffer{
  if(!(bytes instanceof Uint8Array)||bytes.byteLength<1||bytes.byteLength>MAX_PAYLOAD_BYTES||!HEX.test(expected))
    throw Error('C12_EVENT_PAYLOAD_BOUND');
  const copy=Buffer.from(bytes);
  if(sha(copy)!==expected)throw Error('C12_EVENT_PAYLOAD_IDENTITY');
  let value:unknown,text:string;
  try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(copy);value=JSON.parse(text);}
  catch{throw Error('C12_EVENT_PAYLOAD_ENCODING');}
  if(canonicalJson(value as Json)!==text)throw Error('C12_EVENT_PAYLOAD_NONCANONICAL');
  return copy;
}

function checkedIntent(intent:GenericCommittedEventIntent,producer:string,causal:string):GenericEventEnvelope{
  if(!intent||typeof intent!=='object'||Array.isArray(intent)||!NAME.test(producer)||!HEX.test(causal)||
    !QUALIFIED.test(intent.event_selector)||
    intent.event_version!==1||!Number.isSafeInteger(intent.emission_ordinal)||intent.emission_ordinal<0||intent.emission_ordinal>0xffffffff||
    typeof intent.binding_ref!=='string'||intent.binding_ref.length<1||intent.binding_ref.length>256||!HEX.test(intent.binding_sha256)||
    typeof intent.source_site!=='string'||intent.source_site.length<1||Buffer.byteLength(intent.source_site)>4096||
    !NAME.test(intent.target_service)||!QUALIFIED.test(intent.target_entry)||
    typeof intent.route!=='string'||intent.route.length<1||Buffer.byteLength(intent.route)>512||/[\u0000-\u001f\u007f]/.test(intent.route)||
    !HEX.test(intent.payload_schema_sha256))throw Error('C12_EVENT_INTENT_IDENTITY');
  const payload_bytes=checkedPayload(intent.payload_bytes,intent.payload_sha256);
  const occurrence_sha256=deriveGenericEventOccurrence({producer_namespace:producer,causal_command_tuple_sha256:causal,
    event_selector:intent.event_selector,event_version:intent.event_version,emission_ordinal:intent.emission_ordinal});
  const envelope={binding_ref:intent.binding_ref,binding_sha256:intent.binding_sha256,source_site:intent.source_site,
    producer_namespace:producer,causal_command_tuple_sha256:causal,occurrence_sha256,
    event_selector:intent.event_selector,event_version:intent.event_version,emission_ordinal:intent.emission_ordinal,
    target_service:intent.target_service,target_entry:intent.target_entry,route:intent.route,
    payload_schema_sha256:intent.payload_schema_sha256,payload_sha256:intent.payload_sha256};
  const envelope_sha256=sha(canonicalJson(envelope as Json));
  return Object.freeze({...envelope,envelope_sha256,payload_bytes});
}

export {checkedIntent as checkGenericCommittedEventIntent};
function envelopeIdentityJson(envelope:GenericEventEnvelope):string{
  const {payload_bytes:unusedBytes,envelope_sha256:unusedHash,...identity}=envelope;
  void unusedBytes;void unusedHash;
  return canonicalJson(identity as Json);
}
function checkedEnvelope(envelope:GenericEventEnvelope):GenericEventEnvelope{
  if(!envelope||typeof envelope!=='object')throw Error('C12_EVENT_ENVELOPE_IDENTITY');
  const checked=checkedIntent(envelope,envelope.producer_namespace,envelope.causal_command_tuple_sha256);
  if(checked.occurrence_sha256!==envelope.occurrence_sha256||checked.envelope_sha256!==envelope.envelope_sha256||
    envelopeIdentityJson(checked)!==envelopeIdentityJson(envelope))throw Error('C12_EVENT_ENVELOPE_IDENTITY');
  return checked;
}

export const eventOutboxSchemaSQL=`CREATE TABLE _craft_event_outbox_v1 (
  occurrence_sha256 TEXT PRIMARY KEY,
  producer_namespace TEXT NOT NULL,
  causal_command_tuple_sha256 TEXT NOT NULL,
  binding_ref TEXT NOT NULL,
  binding_sha256 TEXT NOT NULL,
  source_site TEXT NOT NULL,
  event_selector TEXT NOT NULL,
  event_version INTEGER NOT NULL CHECK(event_version=1),
  emission_ordinal INTEGER NOT NULL CHECK(emission_ordinal>=0 AND emission_ordinal<=4294967295),
  target_service TEXT NOT NULL,
  target_entry TEXT NOT NULL,
  route TEXT NOT NULL,
  payload_schema_sha256 TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  payload_bytes BLOB NOT NULL,
  envelope_sha256 TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('pending','claimed','acked')),
  fence INTEGER NOT NULL CHECK(fence>=0),
  lease_until_ms INTEGER NOT NULL CHECK(lease_until_ms>=0),
  CHECK((state='pending' AND fence=0 AND lease_until_ms=0)
    OR (state='claimed' AND fence>0 AND lease_until_ms>0)
    OR (state='acked' AND fence>0 AND lease_until_ms=0))
) STRICT`;
export const eventInboxSchemaSQL=`CREATE TABLE _craft_event_inbox_v1 (
  occurrence_sha256 TEXT PRIMARY KEY,
  envelope_sha256 TEXT NOT NULL,
  envelope_json TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  payload_bytes BLOB NOT NULL,
  consumer_command_tuple_sha256 TEXT NOT NULL
) STRICT`;
export const eventEpochSchemaSQL=`CREATE TABLE _craft_event_epoch_v1 (
  id INTEGER PRIMARY KEY CHECK(id=1),
  store_id TEXT NOT NULL,
  compatibility_sha256 TEXT NOT NULL,
  outbox_count INTEGER NOT NULL CHECK(outbox_count>=0),
  outbox_sha256 TEXT NOT NULL,
  inbox_count INTEGER NOT NULL CHECK(inbox_count>=0),
  inbox_sha256 TEXT NOT NULL
) STRICT`;
export const eventGuardsSQL=`CREATE TRIGGER _craft_event_outbox_no_delete_v1
  BEFORE DELETE ON _craft_event_outbox_v1 BEGIN
    SELECT RAISE(ABORT,'C12_OUTBOX_DELETE_FORBIDDEN');
  END;
CREATE TRIGGER _craft_event_outbox_guard_update_v1
  BEFORE UPDATE ON _craft_event_outbox_v1
  WHEN NEW.occurrence_sha256 IS NOT OLD.occurrence_sha256
    OR NEW.producer_namespace IS NOT OLD.producer_namespace
    OR NEW.causal_command_tuple_sha256 IS NOT OLD.causal_command_tuple_sha256
    OR NEW.binding_ref IS NOT OLD.binding_ref
    OR NEW.binding_sha256 IS NOT OLD.binding_sha256
    OR NEW.source_site IS NOT OLD.source_site
    OR NEW.event_selector IS NOT OLD.event_selector
    OR NEW.event_version IS NOT OLD.event_version
    OR NEW.emission_ordinal IS NOT OLD.emission_ordinal
    OR NEW.target_service IS NOT OLD.target_service
    OR NEW.target_entry IS NOT OLD.target_entry
    OR NEW.route IS NOT OLD.route
    OR NEW.payload_schema_sha256 IS NOT OLD.payload_schema_sha256
    OR NEW.payload_sha256 IS NOT OLD.payload_sha256
    OR NEW.payload_bytes IS NOT OLD.payload_bytes
    OR NEW.envelope_sha256 IS NOT OLD.envelope_sha256
    OR NOT ((OLD.state='pending' AND NEW.state='claimed' AND NEW.fence=1 AND NEW.lease_until_ms>0)
      OR (OLD.state='claimed' AND NEW.state='claimed' AND NEW.fence=OLD.fence+1 AND NEW.lease_until_ms>0)
      OR (OLD.state='claimed' AND NEW.state='acked' AND NEW.fence=OLD.fence AND NEW.lease_until_ms=0))
  BEGIN SELECT RAISE(ABORT,'C12_OUTBOX_UPDATE_FORBIDDEN'); END;
CREATE TRIGGER _craft_event_inbox_no_delete_v1
  BEFORE DELETE ON _craft_event_inbox_v1 BEGIN
    SELECT RAISE(ABORT,'C12_INBOX_DELETE_FORBIDDEN');
  END;
CREATE TRIGGER _craft_event_inbox_no_update_v1
  BEFORE UPDATE ON _craft_event_inbox_v1 BEGIN
    SELECT RAISE(ABORT,'C12_INBOX_UPDATE_FORBIDDEN');
  END`;
export const eventStorageSchemaSQL=[eventOutboxSchemaSQL,eventInboxSchemaSQL,eventEpochSchemaSQL,eventGuardsSQL].join(';\n')+';';
export const emptyEventLedgerDigest=sha('[]');
export type OwnedEventEpoch=Readonly<{store_id:string;compatibility_sha256:string}>;

type StoredOutbox=GenericEventEnvelope&{
  state:'pending'|'claimed'|'acked';fence:number;lease_until_ms:number;
};
type StoredInbox={occurrence_sha256:string;envelope_sha256:string;envelope_json:string;
  payload_sha256:string;payload_bytes:Uint8Array;consumer_command_tuple_sha256:string};
export type GenericEventClaim=Readonly<{envelope:GenericEventEnvelope;fence:number;lease_until_ms:number}>;
export type GenericInboxInspection=Readonly<{kind:'absent'|'same'|'collision';consumer_command_tuple_sha256?:string}>;

/** Low-level physical store. Only the source-bound generic repository exposes
 * its operations after command, READY/Auth or relay ownership checks. */
export class GenericEventStore {
  private readonly db:DatabaseSync;
  private readonly owned:OwnedEventEpoch|null;
  private readonly schemaVersion:number;
  private readonly expectedSchema:string;
  constructor(db:DatabaseSync,owned:OwnedEventEpoch|null=null){
    this.db=db;this.owned=owned;
    if(!owned)db.exec(eventStorageSchemaSQL);
    this.schemaVersion=Number((db.prepare('PRAGMA schema_version').get() as {schema_version:number}).schema_version);
    const expected=new DatabaseSync(':memory:');
    try{expected.exec(eventStorageSchemaSQL);this.expectedSchema=JSON.stringify(expected.prepare(
      "SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE name LIKE '_craft_event_%' ORDER BY type,name").all());}
    finally{expected.close();}
    this.assertCurrent();
  }
  private outboxRow(row:StoredOutbox):GenericEventEnvelope{
    try{
      const envelope=checkedIntent(row,row.producer_namespace,row.causal_command_tuple_sha256);
      if(envelope.occurrence_sha256!==row.occurrence_sha256||envelope.envelope_sha256!==row.envelope_sha256||
        !Number.isSafeInteger(row.fence)||row.fence<0||!Number.isSafeInteger(row.lease_until_ms)||row.lease_until_ms<0||
        !((row.state==='pending'&&row.fence===0&&row.lease_until_ms===0)||
          (row.state==='claimed'&&row.fence>0&&row.lease_until_ms>0)||
          (row.state==='acked'&&row.fence>0&&row.lease_until_ms===0)))throw Error('stored');
      return envelope;
    }catch{throw Error('C12_STORED_OUTBOX_INVALID');}
  }
  private inboxRow(row:StoredInbox):void{
    try{
      if(!HEX.test(row.occurrence_sha256)||!HEX.test(row.envelope_sha256)||!HEX.test(row.payload_sha256)||
        !HEX.test(row.consumer_command_tuple_sha256)||typeof row.envelope_json!=='string'||
        Buffer.byteLength(row.envelope_json)>8192||sha(row.envelope_json)!==row.envelope_sha256)
        throw Error('identity');
      const parsed=JSON.parse(row.envelope_json) as Json;
      if(canonicalJson(parsed)!==row.envelope_json||typeof parsed!=='object'||parsed===null||Array.isArray(parsed)||
        (parsed as Record<string,unknown>).occurrence_sha256!==row.occurrence_sha256||
        (parsed as Record<string,unknown>).payload_sha256!==row.payload_sha256)
        throw Error('envelope');
      checkedPayload(row.payload_bytes,row.payload_sha256);
      checkedEnvelope({...parsed as unknown as GenericEventEnvelope,envelope_sha256:row.envelope_sha256,
        payload_bytes:row.payload_bytes});
    }catch{throw Error('C12_STORED_INBOX_INVALID');}
  }
  private ledger(){
    const outbox=this.db.prepare('SELECT * FROM _craft_event_outbox_v1 ORDER BY occurrence_sha256').all() as StoredOutbox[];
    const inbox=this.db.prepare('SELECT * FROM _craft_event_inbox_v1 ORDER BY occurrence_sha256').all() as StoredInbox[];
    if(outbox.length>MAX_ROWS||inbox.length>MAX_ROWS)throw Error('C12_EVENT_LEDGER_BOUND');
    const outboxRows=outbox.map(row=>{this.outboxRow(row);return [row.occurrence_sha256,row.producer_namespace,
      row.causal_command_tuple_sha256,row.binding_ref,row.binding_sha256,row.source_site,row.event_selector,row.event_version,
      row.emission_ordinal,row.target_service,row.target_entry,row.route,row.payload_schema_sha256,row.payload_sha256,
      Buffer.from(row.payload_bytes).toString('hex'),row.envelope_sha256,row.state,row.fence,row.lease_until_ms];});
    const inboxRows=inbox.map(row=>{this.inboxRow(row);return [row.occurrence_sha256,row.envelope_sha256,row.envelope_json,
      row.payload_sha256,Buffer.from(row.payload_bytes).toString('hex'),row.consumer_command_tuple_sha256];});
    return {outbox_count:outbox.length,outbox_sha256:sha(JSON.stringify(outboxRows)),
      inbox_count:inbox.length,inbox_sha256:sha(JSON.stringify(inboxRows))};
  }
  assertCurrent():void{
    const version=Number((this.db.prepare('PRAGMA schema_version').get() as {schema_version:number}).schema_version);
    const schema=JSON.stringify(this.db.prepare(
      "SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE name LIKE '_craft_event_%' ORDER BY type,name").all());
    if(version!==this.schemaVersion||schema!==this.expectedSchema)throw Error('C12_EVENT_SCHEMA_CHANGED');
    if(this.owned){
      const row=this.db.prepare('SELECT * FROM _craft_event_epoch_v1 WHERE id=1').get() as
        ({store_id:string;compatibility_sha256:string}&ReturnType<GenericEventStore['ledger']>)|undefined;
      const actual=this.ledger();
      if(!row||row.store_id!==this.owned.store_id||row.compatibility_sha256!==this.owned.compatibility_sha256||
        row.outbox_count!==actual.outbox_count||row.outbox_sha256!==actual.outbox_sha256||
        row.inbox_count!==actual.inbox_count||row.inbox_sha256!==actual.inbox_sha256)
        throw Error('C12_EVENT_EPOCH_CONFLICT');
    }
  }
  private refresh():void{
    if(!this.owned)return;
    const next=this.ledger();
    const changed=this.db.prepare(`UPDATE _craft_event_epoch_v1
      SET outbox_count=?,outbox_sha256=?,inbox_count=?,inbox_sha256=?
      WHERE id=1 AND store_id=? AND compatibility_sha256=?`).run(next.outbox_count,next.outbox_sha256,
        next.inbox_count,next.inbox_sha256,this.owned.store_id,this.owned.compatibility_sha256);
    if(changed.changes!==1)throw Error('C12_EVENT_EPOCH_CONFLICT');
  }
  /** Called only between the original command journal INSERT and its COMMIT. */
  insertProducedInCommand(intent:GenericCommittedEventIntent,producer:string,causal:string):GenericEventEnvelope{
    if(!this.db.isTransaction)throw Error('C12_EVENT_COMMAND_TRANSACTION_REQUIRED');
    this.assertCurrent();
    const envelope=checkedIntent(intent,producer,causal),count=(this.db.prepare('SELECT COUNT(*) AS n FROM _craft_event_outbox_v1').get() as {n:number}).n;
    if(count>=MAX_ROWS)throw Error('C12_EVENT_OUTBOX_CAPACITY');
    const previous=this.db.prepare('SELECT * FROM _craft_event_outbox_v1 WHERE occurrence_sha256=?').get(envelope.occurrence_sha256) as StoredOutbox|undefined;
    if(previous)throw Error(this.outboxRow(previous).envelope_sha256===envelope.envelope_sha256?'C12_EVENT_DUPLICATE':'C12_EVENT_COLLISION');
    this.db.prepare(`INSERT INTO _craft_event_outbox_v1
      (occurrence_sha256,producer_namespace,causal_command_tuple_sha256,binding_ref,binding_sha256,source_site,
       event_selector,event_version,emission_ordinal,target_service,target_entry,route,payload_schema_sha256,
       payload_sha256,payload_bytes,envelope_sha256,state,fence,lease_until_ms)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,0)`).run(envelope.occurrence_sha256,envelope.producer_namespace,
       envelope.causal_command_tuple_sha256,envelope.binding_ref,envelope.binding_sha256,envelope.source_site,
       envelope.event_selector,envelope.event_version,envelope.emission_ordinal,envelope.target_service,
       envelope.target_entry,envelope.route,envelope.payload_schema_sha256,envelope.payload_sha256,
       envelope.payload_bytes,envelope.envelope_sha256,'pending');
    this.refresh();this.assertCurrent();return envelope;
  }
  /** Original relay calls this after source/store binding; no callback supplies
   * an event. A fresh fence invalidates every older claim. */
  private claim(producer:string,leaseMs:number,occurrenceSha256:string|null):GenericEventClaim|null{
    if(this.db.isTransaction)throw Error('C12_EVENT_CLAIM_BUSY');
    if(!NAME.test(producer)||!Number.isSafeInteger(leaseMs)||leaseMs<1||leaseMs>300000)
      throw Error('C12_EVENT_LEASE_BOUND');
    if(occurrenceSha256!==null&&!HEX.test(occurrenceSha256))throw Error('C12_EVENT_OCCURRENCE_IDENTITY');
    const now=Date.now(),until=now+leaseMs;
    if(!Number.isSafeInteger(now)||!Number.isSafeInteger(until))throw Error('C12_EVENT_CLOCK_BOUND');
    this.db.exec('BEGIN IMMEDIATE');
    try{
      this.assertCurrent();
      const row=(occurrenceSha256===null
        ?this.db.prepare(`SELECT * FROM _craft_event_outbox_v1
          WHERE producer_namespace=? AND (state='pending' OR (state='claimed' AND lease_until_ms<=?))
          ORDER BY rowid LIMIT 1`).get(producer,now)
        :this.db.prepare(`SELECT * FROM _craft_event_outbox_v1
          WHERE producer_namespace=? AND occurrence_sha256=? AND
          (state='pending' OR (state='claimed' AND lease_until_ms<=?))`).get(producer,occurrenceSha256,now)) as StoredOutbox|undefined;
      if(!row){this.db.exec('COMMIT');return null;}
      const envelope=this.outboxRow(row),next=row.fence+1;
      if(!Number.isSafeInteger(next))throw Error('C12_EVENT_FENCE_EXHAUSTED');
      const updated=this.db.prepare(`UPDATE _craft_event_outbox_v1 SET state='claimed',fence=?,lease_until_ms=?
        WHERE occurrence_sha256=? AND state=? AND fence=? AND lease_until_ms=?`).run(next,until,
          row.occurrence_sha256,row.state,row.fence,row.lease_until_ms);
      if(updated.changes!==1)throw Error('C12_EVENT_CLAIM_CONFLICT');
      this.refresh();this.assertCurrent();this.db.exec('COMMIT');
      return Object.freeze({envelope,fence:next,lease_until_ms:until});
    }catch(error){if(this.db.isTransaction)this.db.exec('ROLLBACK');throw error;}
  }
  claimNext(producer:string,leaseMs:number):GenericEventClaim|null{return this.claim(producer,leaseMs,null);}
  claimExact(producer:string,occurrenceSha256:string,leaseMs:number):GenericEventClaim|null{return this.claim(producer,leaseMs,occurrenceSha256);}
  /** Validates the physical fence immediately before a checked relay action. */
  assertClaimCurrent(claim:GenericEventClaim):void{
    this.assertCurrent();
    if(!claim||typeof claim!=='object'||!HEX.test(claim.envelope?.occurrence_sha256)||
      !Number.isSafeInteger(claim.fence)||claim.fence<1||!Number.isSafeInteger(claim.lease_until_ms))
      throw Error('C12_EVENT_CLAIM_IDENTITY');
    const checked=checkedEnvelope(claim.envelope);
    const row=this.db.prepare('SELECT * FROM _craft_event_outbox_v1 WHERE occurrence_sha256=?').get(
      claim.envelope.occurrence_sha256) as StoredOutbox|undefined;
    if(!row||row.state!=='claimed'||row.fence!==claim.fence||row.lease_until_ms!==claim.lease_until_ms||
      this.outboxRow(row).envelope_sha256!==checked.envelope_sha256||
      !Buffer.from(row.payload_bytes).equals(Buffer.from(checked.payload_bytes))||Date.now()>row.lease_until_ms)
      throw Error('C12_EVENT_STALE_CLAIM');
  }
  /** Relay ACK is a separate transaction after an original receiver commit.
   * Its caller must first validate the opaque receiver receipt and live fence. */
  ackClaim(claim:GenericEventClaim):void{
    if(this.db.isTransaction)throw Error('C12_EVENT_ACK_BUSY');
    this.db.exec('BEGIN IMMEDIATE');
    try{
      this.assertClaimCurrent(claim);
      const changed=this.db.prepare(`UPDATE _craft_event_outbox_v1
        SET state='acked',lease_until_ms=0
        WHERE occurrence_sha256=? AND state='claimed' AND fence=? AND lease_until_ms=? AND envelope_sha256=?`)
        .run(claim.envelope.occurrence_sha256,claim.fence,claim.lease_until_ms,claim.envelope.envelope_sha256);
      if(changed.changes!==1)throw Error('C12_EVENT_STALE_CLAIM');
      this.refresh();this.assertCurrent();this.db.exec('COMMIT');
    }catch(error){if(this.db.isTransaction)this.db.exec('ROLLBACK');throw error;}
  }
  /** A checked, already ACKed producer occurrence for post-crash reconciliation. */
  inspectAcked(producer:string,occurrenceSha256:string):GenericEventEnvelope|null{
    if(!NAME.test(producer)||!HEX.test(occurrenceSha256))throw Error('C12_EVENT_OCCURRENCE_IDENTITY');
    this.assertCurrent();
    const row=this.db.prepare('SELECT * FROM _craft_event_outbox_v1 WHERE producer_namespace=? AND occurrence_sha256=?')
      .get(producer,occurrenceSha256) as StoredOutbox|undefined;
    if(!row)return null;
    const envelope=this.outboxRow(row);
    return row.state==='acked'?envelope:null;
  }
  /** Private receiver owner must establish READY before this method is called. */
  inspectInbox(envelope:GenericEventEnvelope):GenericInboxInspection{
    this.assertCurrent();
    const checked=checkedEnvelope(envelope);
    const previous=this.db.prepare('SELECT * FROM _craft_event_inbox_v1 WHERE occurrence_sha256=?').get(
      envelope.occurrence_sha256) as StoredInbox|undefined;
    if(!previous)return Object.freeze({kind:'absent'});
    this.inboxRow(previous);
    return Object.freeze({kind:previous.envelope_sha256===envelope.envelope_sha256&&
      previous.envelope_json===envelopeIdentityJson(checked)&&
      previous.payload_sha256===envelope.payload_sha256&&
      Buffer.from(previous.payload_bytes).equals(Buffer.from(envelope.payload_bytes))?'same':'collision',
      consumer_command_tuple_sha256:previous.consumer_command_tuple_sha256});
  }
  /** Called only after the consumer command's business write and journal INSERT
   * in its original transaction. Exact replay is handled before this path. */
  insertInboxInCommand(envelope:GenericEventEnvelope,consumerCommandTupleSha256:string):void{
    if(!this.db.isTransaction)throw Error('C12_INBOX_COMMAND_TRANSACTION_REQUIRED');
    if(!HEX.test(consumerCommandTupleSha256))throw Error('C12_INBOX_COMMAND_IDENTITY');
    this.assertCurrent();
    const checked=checkedEnvelope(envelope);
    const count=(this.db.prepare('SELECT COUNT(*) AS n FROM _craft_event_inbox_v1').get() as {n:number}).n;
    if(count>=MAX_ROWS)throw Error('C12_EVENT_INBOX_CAPACITY');
    const previous=this.db.prepare('SELECT * FROM _craft_event_inbox_v1 WHERE occurrence_sha256=?').get(
      checked.occurrence_sha256) as StoredInbox|undefined;
    if(previous){this.inboxRow(previous);throw Error(previous.envelope_sha256===checked.envelope_sha256&&
      previous.envelope_json===envelopeIdentityJson(checked)&&
      Buffer.from(previous.payload_bytes).equals(Buffer.from(checked.payload_bytes))?'C12_INBOX_DUPLICATE':'C12_INBOX_COLLISION');}
    this.db.prepare(`INSERT INTO _craft_event_inbox_v1
      (occurrence_sha256,envelope_sha256,envelope_json,payload_sha256,payload_bytes,consumer_command_tuple_sha256)
      VALUES (?,?,?,?,?,?)`).run(checked.occurrence_sha256,checked.envelope_sha256,envelopeIdentityJson(checked),
        checked.payload_sha256,checked.payload_bytes,consumerCommandTupleSha256);
    this.refresh();this.assertCurrent();
  }
}
