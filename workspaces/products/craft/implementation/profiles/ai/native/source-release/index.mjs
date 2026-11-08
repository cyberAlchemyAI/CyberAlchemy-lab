import {DatabaseSync} from 'node:sqlite';
import {createHash, randomUUID} from 'node:crypto';
import {canonical as inertCanonical} from '../shared.mjs';

export const SOURCE_RELEASE_ABI = 'source-release-port/v1';
export const digest = bytes => createHash('sha256').update(bytes).digest('hex');
export function canonical(value) {
  return inertCanonical(value);
}
const fail = code => { throw new Error(code); };
const text = v => typeof v === 'string' && v.length > 0 && v.length <= 2048 || fail('INVALID_IDENTITY');
const strings = v => Array.isArray(v) && v.length <= 256 && v.every(x => typeof x === 'string' && x.length > 0) || fail('INVALID_LIST');
const bytes = v => v instanceof Uint8Array && v.byteLength <= 1048576 || fail('PAYLOAD_BOUND');
const clone = v => JSON.parse(canonical(v));

/** Only the original source owner receives authority. Business consumers receive
 * port. Neither manifest JSON nor a model citation is accepted as authority.
 * No transaction spans external I/O. Adapters must read current state synchronously.
 * Open Questions: README.md. */
export function createSourceReleaseService({path, now = Date.now}) {
  text(path);
  const db = new DatabaseSync(path);
  db.exec(`PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
    CREATE TABLE IF NOT EXISTS sr_sources(id TEXT PRIMARY KEY, body TEXT NOT NULL, bytes BLOB NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS sr_contexts(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS sr_policies(id TEXT PRIMARY KEY, body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS sr_manifests(id TEXT PRIMARY KEY, body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS sr_tickets(id TEXT PRIMARY KEY, body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS sr_consumed(id TEXT PRIMARY KEY REFERENCES sr_tickets(id), consumed_at INTEGER NOT NULL) STRICT;`);
  for (const table of ['sr_manifests','sr_tickets','sr_consumed']) db.exec(`CREATE TRIGGER IF NOT EXISTS ${table}_no_update BEFORE UPDATE ON ${table} BEGIN SELECT RAISE(ABORT,'IMMUTABLE_RELEASE'); END;
    CREATE TRIGGER IF NOT EXISTS ${table}_no_delete BEFORE DELETE ON ${table} BEGIN SELECT RAISE(ABORT,'IMMUTABLE_RELEASE'); END;`);
  const manifests = new WeakMap(), tickets = new WeakMap(), adapters = new Map();
  let closed = false;
  const transaction = fn => { db.exec('BEGIN IMMEDIATE'); try {const result = fn(); db.exec('COMMIT'); return result;} catch(e) {if(db.isTransaction)db.exec('ROLLBACK'); throw e;} };
  const row = (table,id) => {text(id); const r=db.prepare(`SELECT body FROM ${table} WHERE id=?`).get(id); return r ? JSON.parse(r.body) : fail('SOURCE_AUTHORITY_MISSING');};
  adapters.set('inline', {readCurrent({id}) {const r = db.prepare('SELECT body,bytes FROM sr_sources WHERE id=?').get(id); if(!r)fail('SOURCE_MISSING');return {...JSON.parse(r.body),bytes:Buffer.from(r.bytes)};}});
  function current(ref,tenant,principal) {
    const adapter=adapters.get(ref.adapter); if(!adapter)fail('SOURCE_ADAPTER_UNAVAILABLE');
    const s=adapter.readCurrent({id:ref.id,tenant,principal});
    if(s && typeof s.then === 'function')fail('ASYNC_AUTHORITY_UNSUPPORTED');
    if(!s || s.id!==ref.id || s.tenant!==tenant)fail('SOURCE_SCOPE');
    for(const key of ['id','tenant','revision','aclRevision'])text(s[key]);
    strings(s.classifications); strings(s.readers); bytes(s.bytes);if(!s.classifications.length)fail('SOURCE_CLASSIFICATION_REQUIRED');
    if(!s.readers.includes(principal))fail('SOURCE_ACCESS_DENIED');
    return {adapter:ref.adapter,id:s.id,tenant:s.tenant,revision:s.revision,aclRevision:s.aclRevision,
      classifications:[...s.classifications].sort(), readers:[...s.readers].sort(),sha256:digest(s.bytes)};
  }
  function currentManifest(m) {
    const context=row('sr_contexts',m.contextId);
    if(canonical(context)!==canonical(m.context))fail('CONTEXT_REVISION_CHANGED');
    const entries=context.inputs.map(r=>current(r,context.tenant,context.principal));
    if(canonical(entries)!==canonical(m.entries))fail('SOURCE_REVISION_CHANGED');
  }
  function allowed(m,binding) {
    currentManifest(m);
    const policy=row('sr_policies',binding.policyId);
    if(binding.policyRevision!==undefined && binding.policyRevision!==policy.revision)fail('POLICY_REVISION_CHANGED');
    if(!policy.tenants.includes(m.context.tenant)||!policy.actions.includes(binding.action)||!policy.sinks.includes(binding.sink)||!policy.recipients.includes(binding.recipient)||
      m.entries.some(e=>e.classifications.some(c=>!policy.classifications.includes(c))))fail('DISCLOSURE_DENIED');
    const processing=(policy.processingDestinations??[]).some(d=>d.sink===binding.sink&&d.recipient===binding.recipient);
    if(policy.requireRecipientRead!==false&&!processing)for(const entry of m.entries){const recipientView=current(entry,m.context.tenant,binding.recipient);if(canonical(recipientView)!==canonical(entry))fail('RECIPIENT_SOURCE_REVISION_CHANGED');}
    return policy;
  }
  function manifestHandle(id) {const h=Object.freeze({kind:SOURCE_RELEASE_ABI+'/manifest',id});manifests.set(h,id);return h;}
  function getManifest(handle) {const id=manifests.get(handle);if(!id)fail('FOREIGN_MANIFEST');return row('sr_manifests',id);}
  const authority=Object.freeze({
    putInlineSource(s) {
      for(const key of ['id','tenant','revision','aclRevision'])text(s[key]);strings(s.classifications);strings(s.readers);bytes(s.bytes);if(!s.classifications.length)fail('SOURCE_CLASSIFICATION_REQUIRED');
      const body={id:s.id,tenant:s.tenant,revision:s.revision,aclRevision:s.aclRevision,classifications:[...s.classifications],readers:[...s.readers]};
      const old=db.prepare('SELECT body,bytes FROM sr_sources WHERE id=?').get(s.id);
      if(old){const oldBody=JSON.parse(old.body);if(oldBody.tenant!==s.tenant)fail('SOURCE_TENANT_IMMUTABLE');
        if(oldBody.revision===s.revision && digest(old.bytes)!==digest(s.bytes))fail('SOURCE_REVISION_REUSED');
        if(oldBody.aclRevision===s.aclRevision && canonical([oldBody.readers,oldBody.classifications])!==canonical([body.readers,body.classifications]))fail('ACL_REVISION_REUSED');}
      db.prepare('INSERT INTO sr_sources VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body,bytes=excluded.bytes').run(s.id,canonical(body),s.bytes);
    },
    setPolicy(p) {for(const k of ['id','revision'])text(p[k]);for(const k of ['tenants','actions','sinks','recipients','classifications'])strings(p[k]);
      if(p.requireRecipientRead!==undefined&&typeof p.requireRecipientRead!=='boolean')fail('INVALID_RECIPIENT_POLICY');
      const processingDestinations=p.processingDestinations??[];if(!Array.isArray(processingDestinations)||processingDestinations.length>128)fail('INVALID_RECIPIENT_POLICY');
      for(const d of processingDestinations){if(!d||Object.keys(d).sort().join(',')!=='recipient,sink'||!p.sinks.includes(d.sink)||!p.recipients.includes(d.recipient))fail('INVALID_RECIPIENT_POLICY');text(d.sink);text(d.recipient);}
      const value={...Object.fromEntries(['id','revision','tenants','actions','sinks','recipients','classifications'].map(k=>[k,p[k]])),requireRecipientRead:p.requireRecipientRead??true,processingDestinations:clone(processingDestinations)};
      const old=db.prepare('SELECT body FROM sr_policies WHERE id=?').get(p.id);if(old && JSON.parse(old.body).revision===p.revision && old.body!==canonical(value))fail('POLICY_REVISION_REUSED');
      db.prepare('INSERT INTO sr_policies VALUES(?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body').run(p.id,canonical(value));},
    defineContext(c) {
      for(const k of ['id','tenant','principal'])text(c[k]);if(!Array.isArray(c.inputs)||c.inputs.length>256)fail('CONTEXT_BOUND');
      const inputs=c.inputs.map(r=>{text(r.adapter);text(r.id);return {adapter:r.adapter,id:r.id};});
      if(new Set(inputs.map(canonical)).size!==inputs.length)fail('DUPLICATE_CONTEXT_INPUT');
      return transaction(()=>{const old=db.prepare('SELECT revision FROM sr_contexts WHERE id=?').get(c.id);const context={id:c.id,tenant:c.tenant,principal:c.principal,inputs,revision:(old?.revision??0)+1};
        db.prepare('INSERT INTO sr_contexts VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,body=excluded.body').run(c.id,context.revision,canonical(context));return clone(context);});
    },
    registerAdapter(id,adapter) {
      text(id);if(closed)fail('SOURCE_ADAPTER_UNAVAILABLE');if(id==='inline'||adapters.has(id)||typeof adapter?.readCurrent!=='function')fail('SOURCE_ADAPTER_CONFLICT');
      adapters.set(id,adapter);let retired=false;
      // This closure retires only its own original registration. Keeping the old
      // token cannot remove a later registration, even if the same port is reused.
      return Object.freeze({
        assertCurrent(){if(closed||retired||adapters.get(id)!==adapter)fail('SOURCE_ADAPTER_UNAVAILABLE');},
        retire(){if(retired)return;retired=true;if(adapters.get(id)===adapter)adapters.delete(id);},
      });
    },
    revokeInlineSource(id) {text(id);db.prepare('DELETE FROM sr_sources WHERE id=?').run(id);},
  });
  const port=Object.freeze({
    abi:SOURCE_RELEASE_ABI,
    captureContext({contextId,tenant,principal}) {return transaction(()=>{const context=row('sr_contexts',contextId);if(context.tenant!==tenant||context.principal!==principal)fail('CONTEXT_SCOPE');
      const m={contextId,context,entries:context.inputs.map(r=>current(r,tenant,principal))};const id=digest(canonical(m));db.prepare('INSERT OR IGNORE INTO sr_manifests VALUES(?,?)').run(id,canonical(m));return manifestHandle(id);});},
    recoverManifest(id) {row('sr_manifests',id);return manifestHandle(id);},
    describeManifest(handle) {return clone(getManifest(handle));},
    issueRelease({manifest,policyId,attemptId,fence,resourceId,action,sink,recipient,payload,expiresAt}) {
      bytes(payload);for(const v of [policyId,attemptId,resourceId,action,sink,recipient])text(v);if(!Number.isSafeInteger(fence)||fence<0||!Number.isSafeInteger(expiresAt)||expiresAt<=now()||expiresAt-now()>300000)fail('RELEASE_BOUND');
      return transaction(()=>{const m=getManifest(manifest);const binding={manifestId:manifests.get(manifest),policyId,attemptId,fence,resourceId,action,sink,recipient,payloadSha256:digest(payload),expiresAt,tenant:m.context.tenant,principal:m.context.principal};
        const policy=allowed(m,binding);binding.policyRevision=policy.revision;const id=randomUUID();db.prepare('INSERT INTO sr_tickets VALUES(?,?)').run(id,canonical(binding));const h=Object.freeze({kind:SOURCE_RELEASE_ABI+'/ticket'});tickets.set(h,id);return h;});
    },
    consumeRelease(ticket,exact) {return transaction(()=>{const id=tickets.get(ticket);if(!id)fail('FOREIGN_RELEASE_TICKET');const b=row('sr_tickets',id);if(db.prepare('SELECT id FROM sr_consumed WHERE id=?').get(id))fail('RELEASE_ALREADY_CONSUMED');
      const m=row('sr_manifests',b.manifestId);allowed(m,b);if(now()>=b.expiresAt)fail('RELEASE_EXPIRED');
      bytes(exact.payload);for(const k of ['attemptId','fence','resourceId','action','sink','recipient','tenant','principal'])if(exact[k]!==b[k])fail('RELEASE_BINDING_MISMATCH');
      if(digest(exact.payload)!==b.payloadSha256)fail('RELEASE_PAYLOAD_MISMATCH');
      db.prepare('INSERT INTO sr_consumed VALUES(?,?)').run(id,now());return Object.freeze(clone(b));});},
    inspectConsumption(ticket) {const id=tickets.get(ticket);if(!id)fail('FOREIGN_RELEASE_TICKET');return !!db.prepare('SELECT id FROM sr_consumed WHERE id=?').get(id);},
    describeRelease(ticket) {const id=tickets.get(ticket);if(!id)fail('FOREIGN_RELEASE_TICKET');return {ticketId:id,...clone(row('sr_tickets',id))};},
  });
  return Object.freeze({port,authority,close(){if(closed)return;closed=true;adapters.clear();db.close();}});
}
