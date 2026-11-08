/** Candidate C11 durable effect ledger. This module owns no Auth, provider or
 * Operation capability; the original generated owner must bind those before use.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import { createHash } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';
import { readCheckedDemoPayObservation, type CheckedDemoPayObservation } from './external-write-runtime.js';

type State = 'prepared' | 'dispatched' | 'unknown' | 'observed';
export type EffectInput = Readonly<{
  effect_canonical_json: string;
  effect_sha256: string;
  payload_canonical_json: string;
  payload_sha256: string;
  binding_canonical_json: string;
  binding_sha256: string;
  request_bytes: Uint8Array;
}>;
export type EffectRow = Readonly<{
  effect_sha256: string;
  state: State;
  request_sha256: string;
}>;
export type DefiniteExternalObservation = Readonly<{
  kind: 'Captured' | 'DefinitivelyDeclined'; providerReference: string;
}>;
export type RecoveredEffectInput = Readonly<{
  state: State; input: EffectInput; request_sha256: string;
  observation: DefiniteExternalObservation | null;
}>;
export type PrepareResult = Readonly<
  | { kind: 'new'; dispatch: DispatchPermit }
  | { kind: 'inspect-required'; state: State }
  | { kind: 'observed' }
>;
export interface DispatchPermit { readonly kind: 'private-c11-dispatch-permit/v1-candidate' }
/** Ephemeral proof of a committed dispatch retirement in this store instance.
 * The original owner must check it immediately before native invocation. */
export interface DispatchCustody { readonly kind: 'private-c11-dispatch-custody/v1-candidate' }

const hex = /^[0-9a-f]{64}$/;
const digest = (bytes: Uint8Array | string): string => createHash('sha256').update(bytes).digest('hex');
const same = (left: Uint8Array, right: Uint8Array): boolean => Buffer.from(left).equals(Buffer.from(right));
function canonical(value: unknown): string {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return JSON.stringify(value);
  if (typeof value === 'number' && Number.isFinite(value) && !Object.is(value, -0)) return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object' && Object.getPrototypeOf(value) === Object.prototype)
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as Record<string, unknown>)[key])}`).join(',')}}`;
  throw new Error('C11_NONCANONICAL_VALUE');
}
function checkedJson(value: string, sha: string, label: string): void {
  if (typeof value !== 'string' || !hex.test(sha) || Buffer.byteLength(value, 'utf8') > 1048576 || digest(value) !== sha)
    throw new Error(`C11_${label}_IDENTITY`);
  let parsed: unknown;
  try { parsed = JSON.parse(value); } catch { throw new Error(`C11_${label}_JSON`); }
  if (canonical(parsed) !== value) throw new Error(`C11_${label}_NONCANONICAL`);
}
function checkedInput(value: EffectInput): void {
  checkedJson(value.effect_canonical_json, value.effect_sha256, 'EFFECT');
  checkedJson(value.payload_canonical_json, value.payload_sha256, 'PAYLOAD');
  checkedJson(value.binding_canonical_json, value.binding_sha256, 'BINDING');
  if (!(value.request_bytes instanceof Uint8Array) || value.request_bytes.byteLength > 1048576)
    throw new Error('C11_REQUEST_BYTES');
}
type Stored = {
  effect_sha256: string; effect_json: string; payload_sha256: string; payload_json: string;
  binding_sha256: string; binding_json: string; request_sha256: string; request_bytes: Uint8Array;
  state: State; observation: string | null;
};
export const externalWriteIntentSchemaSQL = `CREATE TABLE IF NOT EXISTS _craft_external_write_intents_v1 (
      effect_sha256 TEXT PRIMARY KEY, effect_json TEXT NOT NULL,
      payload_sha256 TEXT NOT NULL, payload_json TEXT NOT NULL,
      binding_sha256 TEXT NOT NULL, binding_json TEXT NOT NULL,
      request_sha256 TEXT NOT NULL, request_bytes BLOB NOT NULL,
      state TEXT NOT NULL CHECK(state IN ('prepared','dispatched','unknown','observed')),
      observation TEXT,
      CHECK((state='observed')=(observation IS NOT NULL))
    ) STRICT`;
export const externalWriteIntentEpochSchemaSQL = `CREATE TABLE IF NOT EXISTS _craft_external_write_epoch_v1 (
      id INTEGER PRIMARY KEY CHECK(id=1), store_id TEXT NOT NULL,
      compatibility_sha256 TEXT NOT NULL, intent_count INTEGER NOT NULL CHECK(intent_count>=0),
      intent_sha256 TEXT NOT NULL
    ) STRICT`;
export const externalWriteIntentGuardSQL = `CREATE TRIGGER _craft_external_write_no_delete_v1
    BEFORE DELETE ON _craft_external_write_intents_v1 BEGIN
      SELECT RAISE(ABORT, 'C11_INTENT_DELETE_FORBIDDEN');
    END;
    CREATE TRIGGER _craft_external_write_guard_update_v1
    BEFORE UPDATE ON _craft_external_write_intents_v1
    WHEN NEW.effect_sha256 IS NOT OLD.effect_sha256 OR NEW.effect_json IS NOT OLD.effect_json
      OR NEW.payload_sha256 IS NOT OLD.payload_sha256 OR NEW.payload_json IS NOT OLD.payload_json
      OR NEW.binding_sha256 IS NOT OLD.binding_sha256 OR NEW.binding_json IS NOT OLD.binding_json
      OR NEW.request_sha256 IS NOT OLD.request_sha256 OR NEW.request_bytes IS NOT OLD.request_bytes
      OR NOT ((OLD.state='prepared' AND NEW.state='dispatched')
        OR (OLD.state='dispatched' AND NEW.state='unknown' AND NEW.observation IS NULL)
        OR (OLD.state IN ('dispatched','unknown') AND NEW.state='observed'
          AND OLD.observation IS NULL AND NEW.observation IS NOT NULL))
    BEGIN SELECT RAISE(ABORT, 'C11_INTENT_UPDATE_FORBIDDEN'); END`;
export const emptyExternalWriteIntentDigest = digest('[]');
export type OwnedIntentEpoch = Readonly<{store_id:string;compatibility_sha256:string}>;

/** All methods are synchronous. No SQLite transaction is held over a provider
 * await. A reopened prepared/dispatched/unknown row always requires inspection,
 * so an interrupted send cannot acquire a new key or silently recapture. */
export class DurableWriteIntentStore {
  private readonly permits = new WeakMap<object, { effect: string; used: boolean }>();
  private readonly custodies = new WeakMap<object, { effect: string }>();
  private readonly db: DatabaseSync;
  private readonly owned: OwnedIntentEpoch | null;
  private readonly schemaVersion: number | null;
  constructor(db: DatabaseSync, owned: OwnedIntentEpoch | null = null) {
    this.db = db;
    this.owned = owned;
    if (!owned) db.exec(externalWriteIntentSchemaSQL);
    this.schemaVersion=owned?Number((db.prepare('PRAGMA schema_version').get() as {schema_version:number}).schema_version):null;
    this.assertSchema();
    this.assertLedgerCurrent();
  }
  private assertSchema(): void {
    if(this.schemaVersion!==null&&Number((this.db.prepare('PRAGMA schema_version').get() as {schema_version:number}).schema_version)!==this.schemaVersion)
      throw new Error('C11_INTENT_SCHEMA_EPOCH_CHANGED');
    const actual = this.db.prepare("SELECT sql FROM sqlite_master WHERE type='table' AND name='_craft_external_write_intents_v1'")
      .get() as { sql: string } | undefined;
    const triggers = this.db.prepare("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='_craft_external_write_intents_v1'")
      .all() as Array<{ name: string }>;
    if (!actual || actual.sql !== externalWriteIntentSchemaSQL.replace('IF NOT EXISTS ', '') ||
      (!this.owned && triggers.length))
      throw new Error('C11_INTENT_SCHEMA_CONFLICT');
    if (this.owned) {
      const expected=new DatabaseSync(':memory:');let expectedTriggers:string;
      try {expected.exec(externalWriteIntentSchemaSQL+';'+externalWriteIntentGuardSQL);
        expectedTriggers=JSON.stringify(expected.prepare("SELECT name,sql FROM sqlite_master WHERE type='trigger' AND tbl_name='_craft_external_write_intents_v1' ORDER BY name").all());}
      finally {expected.close();}
      const actualTriggers=JSON.stringify(this.db.prepare("SELECT name,sql FROM sqlite_master WHERE type='trigger' AND tbl_name='_craft_external_write_intents_v1' ORDER BY name").all());
      if(actualTriggers!==expectedTriggers)throw new Error('C11_INTENT_GUARD_CONFLICT');
      const epoch=this.db.prepare("SELECT sql FROM sqlite_master WHERE type='table' AND name='_craft_external_write_epoch_v1'").get() as {sql:string}|undefined;
      const epochTriggers=this.db.prepare("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='_craft_external_write_epoch_v1'").all();
      if (!epoch || epoch.sql!==externalWriteIntentEpochSchemaSQL.replace('IF NOT EXISTS ', '') || epochTriggers.length)
        throw new Error('C11_INTENT_EPOCH_SCHEMA_CONFLICT');
    }
  }
  private ledger(): {count:number;sha256:string} {
    const rows=this.db.prepare('SELECT * FROM _craft_external_write_intents_v1 ORDER BY effect_sha256').all() as Stored[];
    if(rows.length>1024)throw new Error('C11_INTENT_LEDGER_BOUND');
    const encoded=rows.map(r=>{
      if(typeof r.effect_sha256!=='string')throw new Error('C11_STORED_INTENT_INVALID');
      this.row(r.effect_sha256);
      return [r.effect_sha256,r.effect_json,r.payload_sha256,r.payload_json,r.binding_sha256,r.binding_json,
        r.request_sha256,Buffer.from(r.request_bytes).toString('hex'),r.state,r.observation];
    });
    return {count:rows.length,sha256:digest(JSON.stringify(encoded))};
  }
  assertLedgerCurrent(): void {
    if(!this.owned)return;
    this.assertSchema();
    const row=this.db.prepare('SELECT * FROM _craft_external_write_epoch_v1 WHERE id=1').get() as
      {store_id:string;compatibility_sha256:string;intent_count:number;intent_sha256:string}|undefined;
    const actual=this.ledger();
    if(!row||row.store_id!==this.owned.store_id||row.compatibility_sha256!==this.owned.compatibility_sha256||
      row.intent_count!==actual.count||row.intent_sha256!==actual.sha256)
      throw new Error('C11_INTENT_EPOCH_CONFLICT');
  }
  private refreshLedger(): void {
    if(!this.owned)return;
    const actual=this.ledger();
    const changed=this.db.prepare('UPDATE _craft_external_write_epoch_v1 SET intent_count=?,intent_sha256=? WHERE id=1 AND store_id=? AND compatibility_sha256=?')
      .run(actual.count,actual.sha256,this.owned.store_id,this.owned.compatibility_sha256);
    if(changed.changes!==1)throw new Error('C11_INTENT_EPOCH_CONFLICT');
  }
  private row(sha: string): Stored | undefined {
    const value = this.db.prepare('SELECT * FROM _craft_external_write_intents_v1 WHERE effect_sha256=?')
      .get(sha) as Stored | undefined;
    if (!value) return undefined;
    try {
      checkedJson(value.effect_json, value.effect_sha256, 'STORED_EFFECT');
      checkedJson(value.payload_json, value.payload_sha256, 'STORED_PAYLOAD');
      checkedJson(value.binding_json, value.binding_sha256, 'STORED_BINDING');
      if (!(value.request_bytes instanceof Uint8Array) || digest(value.request_bytes) !== value.request_sha256 ||
          !['prepared', 'dispatched', 'unknown', 'observed'].includes(value.state) ||
          (value.state === 'observed') !== (value.observation !== null)) throw new Error('stored shape');
      if (value.observation !== null) {
        const observation: unknown = JSON.parse(value.observation);
        if (canonical(observation) !== value.observation || !observation || typeof observation !== 'object' ||
            Array.isArray(observation) || Object.keys(observation).sort().join(',') !== 'kind,providerReference' ||
            !['Captured', 'DefinitivelyDeclined'].includes(
              (observation as Record<string, unknown>).kind as string) ||
            typeof (observation as Record<string, unknown>).providerReference !== 'string' ||
            ((observation as Record<string, unknown>).providerReference as string).length === 0)
          throw new Error('stored observation');
      }
    } catch { throw new Error('C11_STORED_INTENT_INVALID'); }
    return value;
  }
  private matching(stored: Stored, input: EffectInput): void {
    if (stored.effect_json !== input.effect_canonical_json || stored.payload_sha256 !== input.payload_sha256 ||
        stored.payload_json !== input.payload_canonical_json || stored.binding_sha256 !== input.binding_sha256 ||
        stored.binding_json !== input.binding_canonical_json || stored.request_sha256 !== digest(input.request_bytes) ||
        !same(stored.request_bytes, input.request_bytes)) throw new Error('C11_EFFECT_IDENTITY_CONFLICT');
  }
  prepare(input: EffectInput): PrepareResult {
    checkedInput(input);
    this.db.exec('BEGIN IMMEDIATE');
    try {
      this.assertSchema();
      this.assertLedgerCurrent();
      const previous = this.row(input.effect_sha256);
      if (previous) {
        this.matching(previous, input);
        this.db.exec('COMMIT');
        return previous.state === 'observed'
          ? { kind: 'observed' }
          : { kind: 'inspect-required', state: previous.state };
      }
      this.db.prepare(`INSERT INTO _craft_external_write_intents_v1
        (effect_sha256,effect_json,payload_sha256,payload_json,binding_sha256,binding_json,
         request_sha256,request_bytes,state,observation) VALUES (?,?,?,?,?,?,?,?,?,NULL)`)
        .run(input.effect_sha256, input.effect_canonical_json, input.payload_sha256, input.payload_canonical_json,
          input.binding_sha256, input.binding_canonical_json, digest(input.request_bytes), input.request_bytes, 'prepared');
      this.refreshLedger();
      this.db.exec('COMMIT');
      const dispatch = Object.freeze({ kind: 'private-c11-dispatch-permit/v1-candidate' as const });
      this.permits.set(dispatch, { effect: input.effect_sha256, used: false });
      return { kind: 'new', dispatch };
    } catch (error) { this.db.exec('ROLLBACK'); throw error; }
  }
  /** Original owned-store recovery only. The returned bytes are a defensive
   * copy of the checked persisted request, never a caller-supplied sidecar. */
  recover(effectSha256: string): RecoveredEffectInput {
    if (!this.owned) throw new Error('C11_RECOVERY_ORIGINAL_OWNER_REQUIRED');
    if (typeof effectSha256 !== 'string' || !hex.test(effectSha256)) throw new Error('C11_RECOVERY_IDENTITY');
    this.db.exec('BEGIN IMMEDIATE');
    try {
      this.assertSchema();this.assertLedgerCurrent();
      const stored=this.row(effectSha256);
      if (!stored) throw new Error('C11_INTENT_MISSING');
      const input:EffectInput=Object.freeze({effect_canonical_json:stored.effect_json,effect_sha256:stored.effect_sha256,
        payload_canonical_json:stored.payload_json,payload_sha256:stored.payload_sha256,
        binding_canonical_json:stored.binding_json,binding_sha256:stored.binding_sha256,
        request_bytes:Buffer.from(stored.request_bytes)});
      checkedInput(input);
      const observation=stored.observation===null?null:JSON.parse(stored.observation) as DefiniteExternalObservation;
      const result=Object.freeze({state:stored.state,input,request_sha256:stored.request_sha256,
        observation:observation===null?null:Object.freeze(observation)});
      this.db.exec('COMMIT');return result;
    } catch(error){if(this.db.isTransaction)this.db.exec('ROLLBACK');throw error;}
  }
  /** Conditional retirement proves one winner under this candidate ledger's
   * retire-before-send protocol. It is not yet operational provider custody or
   * fresh action Auth. No database lock remains held for a provider await. */
  retireRecoveredPrepared(input: EffectInput): DispatchCustody {
    if (!this.owned) throw new Error('C11_RECOVERY_ORIGINAL_OWNER_REQUIRED');
    checkedInput(input);
    this.db.exec('BEGIN IMMEDIATE');
    try {
      this.assertSchema();this.assertLedgerCurrent();
      const stored=this.row(input.effect_sha256);
      if(!stored)throw new Error('C11_INTENT_MISSING');
      this.matching(stored,input);
      if(stored.state!=='prepared')throw new Error('C11_RECOVERY_NOT_PREPARED');
      const changed=this.db.prepare("UPDATE _craft_external_write_intents_v1 SET state='dispatched' WHERE effect_sha256=? AND state='prepared'").run(input.effect_sha256);
      if(changed.changes!==1)throw new Error('C11_RECOVERY_RACE');
      this.refreshLedger();this.db.exec('COMMIT');
      const custody=Object.freeze({kind:'private-c11-dispatch-custody/v1-candidate' as const});
      this.custodies.set(custody,{effect:input.effect_sha256});return custody;
    }catch(error){if(this.db.isTransaction)this.db.exec('ROLLBACK');throw error;}
  }
  /** Must commit before the original owner invokes the selected native adapter. */
  markDispatched(permit: DispatchPermit): DispatchCustody {
    const found = this.permits.get(permit);
    if (!found || found.used) throw new Error('C11_FOREIGN_OR_USED_DISPATCH');
    this.db.exec('BEGIN IMMEDIATE');
    try {
      this.assertSchema();
      this.assertLedgerCurrent();
      const change = this.db.prepare(`UPDATE _craft_external_write_intents_v1 SET state='dispatched'
        WHERE effect_sha256=? AND state='prepared'`).run(found.effect);
      if (change.changes !== 1) throw new Error('C11_DISPATCH_STATE');
      const after = this.row(found.effect);
      if (!after || after.state !== 'dispatched') throw new Error('C11_DISPATCH_NOT_DURABLE');
      this.refreshLedger();
      this.db.exec('COMMIT');
      found.used = true;
      const custody = Object.freeze({ kind: 'private-c11-dispatch-custody/v1-candidate' as const });
      this.custodies.set(custody, { effect: found.effect });
      return custody;
    } catch (error) { this.db.exec('ROLLBACK'); throw error; }
  }
  /** This check is necessary but not sufficient for an external send: only the
   * original owner can protect the post-check interval and bind current Auth. */
  assertDispatchCurrent(custody: DispatchCustody, input: EffectInput): void {
    const found = custody && typeof custody === 'object' ? this.custodies.get(custody) : undefined;
    if (!found || found.effect !== input.effect_sha256) throw new Error('C11_FOREIGN_DISPATCH_CUSTODY');
    checkedInput(input);
    this.db.exec('BEGIN IMMEDIATE');
    try {
      this.assertSchema();
      this.assertLedgerCurrent();
      const row = this.row(found.effect);
      if (!row || row.state !== 'dispatched') throw new Error('C11_DISPATCH_NOT_CURRENT');
      this.matching(row, input);
      this.db.exec('COMMIT');
    } catch (error) { this.db.exec('ROLLBACK'); throw error; }
  }
  /** Unknown includes timeout, transport loss and invalid response. It never
   * means decline, absent effect, or permission to make a fresh capture. */
  retainUnknown(input: EffectInput): void {
    checkedInput(input);
    this.db.exec('BEGIN IMMEDIATE');
    try {
      this.assertSchema();
      this.assertLedgerCurrent();
      const prior = this.row(input.effect_sha256);
      if (!prior) throw new Error('C11_INTENT_MISSING');
      this.matching(prior, input);
      if (prior.state === 'prepared') throw new Error('C11_DISPATCH_OR_PROVEN_INSPECTION_REQUIRED');
      if (prior.state === 'observed') throw new Error('C11_OBSERVATION_CONFLICT');
      if (prior.state === 'dispatched') this.db.prepare(`UPDATE _craft_external_write_intents_v1
        SET state='unknown' WHERE effect_sha256=?`).run(input.effect_sha256);
      const after = this.row(input.effect_sha256);
      if (!after || after.state !== 'unknown') throw new Error('C11_UNKNOWN_NOT_DURABLE');
      this.refreshLedger();
      this.db.exec('COMMIT');
    } catch (error) { this.db.exec('ROLLBACK'); throw error; }
  }
  /** Persist only an opaque, identity-matched definite provider observation.
   * The original generated owner must also check its selected source rule and
   * current Auth before this transition is used for business continuation. */
  recordCheckedObservation(input: EffectInput, handle: CheckedDemoPayObservation): void {
    checkedInput(input);
    const checked = readCheckedDemoPayObservation(handle, input);
    const observation = canonical({kind: checked.kind, providerReference: checked.providerReference});
    this.db.exec('BEGIN IMMEDIATE');
    try {
      this.assertSchema();
      this.assertLedgerCurrent();
      const prior = this.row(input.effect_sha256);
      if (!prior) throw new Error('C11_INTENT_MISSING');
      this.matching(prior, input);
      if (prior.state === 'observed') {
        if (prior.observation !== observation) throw new Error('C11_OBSERVATION_CONFLICT');
        this.db.exec('COMMIT');
        return;
      }
      if (prior.state !== 'dispatched' && prior.state !== 'unknown')
        throw new Error('C11_DISPATCH_OR_PROVEN_INSPECTION_REQUIRED');
      const changed = this.db.prepare(`UPDATE _craft_external_write_intents_v1
        SET state='observed',observation=? WHERE effect_sha256=? AND state=? AND observation IS NULL`)
        .run(observation, input.effect_sha256, prior.state);
      if (changed.changes !== 1) throw new Error('C11_OBSERVATION_RACE');
      this.refreshLedger();
      this.db.exec('COMMIT');
    } catch (error) { if (this.db.isTransaction) this.db.exec('ROLLBACK'); throw error; }
  }
  /** A definite result can be replayed from the exact intent without a send. */
  readObserved(input: EffectInput): DefiniteExternalObservation | null {
    checkedInput(input);
    this.assertSchema();
    this.assertLedgerCurrent();
    const prior = this.row(input.effect_sha256);
    if (!prior) throw new Error('C11_INTENT_MISSING');
    this.matching(prior, input);
    if (prior.state !== 'observed' || prior.observation === null) return null;
    return Object.freeze(JSON.parse(prior.observation) as DefiniteExternalObservation);
  }
  inspect(input: EffectInput): EffectRow | null {
    checkedInput(input);
    this.assertSchema();
    this.assertLedgerCurrent();
    const prior = this.row(input.effect_sha256);
    if (!prior) return null;
    this.matching(prior, input);
    return Object.freeze({ effect_sha256: prior.effect_sha256, state: prior.state,
      request_sha256: prior.request_sha256 });
  }
}
