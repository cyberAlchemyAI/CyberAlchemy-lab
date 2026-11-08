import { DatabaseSync } from "node:sqlite";

export type DurableOutboxStatus = "pending" | "leased" | "published" | "dead";
export interface DurableOutboxMessage { readonly messageId:string; readonly eventType:string; readonly payload:Readonly<Record<string,unknown>>; readonly occurredAt:string; readonly maxAttempts?:number }
export interface DurableCommitRequest { readonly aggregateType:string; readonly aggregateId:string; readonly state:Readonly<Record<string,unknown>>; readonly expectedVersion:number; readonly messages:readonly DurableOutboxMessage[] }
export interface DurableOutboxRecord extends DurableOutboxMessage { readonly aggregateType:string; readonly aggregateId:string; readonly status:DurableOutboxStatus; readonly attempts:number; readonly maxAttempts:number; readonly availableAt:string; readonly leaseOwner:string|null; readonly leaseUntil:string|null; readonly leaseGeneration:number; readonly lastError:string|null; readonly publishedAt:string|null }
export interface DurableOutboxTransport { publish(message:DurableOutboxRecord):Promise<void> }
export interface OutboxTelemetryEvent { kind:"committed"|"replayed"|"claimed"|"published"|"retry-scheduled"|"dead-lettered"|"dead-requeued"; messageId?:string; workerId?:string; at:string }
export interface OutboxTelemetrySink { record(event:OutboxTelemetryEvent):void }
export class CollectingOutboxTelemetry implements OutboxTelemetrySink { readonly events:OutboxTelemetryEvent[]=[]; record(event:OutboxTelemetryEvent):void{this.events.push(structuredClone(event));} }
const noop:OutboxTelemetrySink={record(){}};
const outboxTable=`CREATE TABLE domainspec_outbox (message_id TEXT PRIMARY KEY,aggregate_type TEXT NOT NULL,aggregate_id TEXT NOT NULL,event_type TEXT NOT NULL,payload_json TEXT NOT NULL,occurred_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','leased','published','dead')),attempts INTEGER NOT NULL DEFAULT 0,max_attempts INTEGER NOT NULL DEFAULT 5,available_at TEXT NOT NULL,lease_owner TEXT,lease_until TEXT,lease_generation INTEGER NOT NULL DEFAULT 0,last_error TEXT,published_at TEXT)`;
type Row={message_id:string;aggregate_type:string;aggregate_id:string;event_type:string;payload_json:string;occurred_at:string;status:DurableOutboxStatus;attempts:number;max_attempts:number;available_at:string;lease_owner:string|null;lease_until:string|null;lease_generation:number;last_error:string|null;published_at:string|null};
function text(value:unknown,code:string):asserts value is string{if(typeof value!=="string"||!value)throw new Error(code)}
function timestamp(value:string,code:string):string{const time=Date.parse(value);if(!Number.isFinite(time))throw new Error(code);return new Date(time).toISOString()}
function commitIdentity(request:DurableCommitRequest):string{return JSON.stringify({state:request.state,expectedVersion:request.expectedVersion,messages:request.messages.map(m=>({messageId:m.messageId,eventType:m.eventType,payload:m.payload,occurredAt:timestamp(m.occurredAt,"OUTBOX_OCCURRED_AT_INVALID"),maxAttempts:m.maxAttempts??5}))})}
function validate(request:DurableCommitRequest):void{text(request.aggregateType,"OUTBOX_AGGREGATE_TYPE_REQUIRED");text(request.aggregateId,"OUTBOX_AGGREGATE_ID_REQUIRED");if(!Number.isSafeInteger(request.expectedVersion)||request.expectedVersion<0)throw new Error("OUTBOX_EXPECTED_VERSION_INVALID");if(!request.messages.length)throw new Error("OUTBOX_MESSAGE_REQUIRED");for(const m of request.messages){text(m.messageId,"OUTBOX_MESSAGE_ID_REQUIRED");text(m.eventType,"OUTBOX_EVENT_TYPE_REQUIRED");timestamp(m.occurredAt,"OUTBOX_OCCURRED_AT_INVALID");if(m.maxAttempts!==undefined&&(!Number.isSafeInteger(m.maxAttempts)||m.maxAttempts<1))throw new Error("OUTBOX_MAX_ATTEMPTS_INVALID")}}

export class DurableSqliteTransactionalOutbox implements Disposable {
  readonly database:DatabaseSync;
  constructor(path:string,private readonly telemetry:OutboxTelemetrySink=noop){text(path,"OUTBOX_DATABASE_PATH_REQUIRED");this.database=new DatabaseSync(path);try{this.migrate()}catch(error){this.database.close();throw error}}
  private emit(event:OutboxTelemetryEvent):void{try{this.telemetry.record(event)}catch{/* Observation cannot change a committed outcome. */}}
  private migrate():void{
    this.database.exec("BEGIN IMMEDIATE");
    try{
      this.database.exec("CREATE TABLE IF NOT EXISTS domainspec_outbox_migrations(version INTEGER PRIMARY KEY,applied_at TEXT NOT NULL);CREATE TABLE IF NOT EXISTS domainspec_aggregate_state(aggregate_type TEXT NOT NULL,aggregate_id TEXT NOT NULL,state_json TEXT NOT NULL,version INTEGER NOT NULL,updated_at TEXT NOT NULL,PRIMARY KEY(aggregate_type,aggregate_id));");
      const needsMigration=(this.database.prepare("SELECT COALESCE(MAX(version),0) version FROM domainspec_outbox_migrations").get() as {version:number}).version<3;
      const old=this.database.prepare("SELECT sql FROM sqlite_master WHERE type='table' AND name='domainspec_outbox'").get() as {sql:string}|undefined;
      if(!old){if(!needsMigration)throw new Error("OUTBOX_SCHEMA_MIGRATION_INCOMPLETE");this.database.exec(outboxTable)}
      else if(!old.sql.includes("'leased'")){if(!needsMigration)throw new Error("OUTBOX_SCHEMA_MIGRATION_INCOMPLETE");this.database.exec(`ALTER TABLE domainspec_outbox RENAME TO domainspec_outbox_v1;${outboxTable};INSERT INTO domainspec_outbox(message_id,aggregate_type,aggregate_id,event_type,payload_json,occurred_at,status,attempts,max_attempts,available_at,last_error) SELECT message_id,aggregate_type,aggregate_id,event_type,payload_json,occurred_at,status,attempts,5,occurred_at,last_error FROM domainspec_outbox_v1;DROP TABLE domainspec_outbox_v1;`)}
      else{const columns=this.database.prepare("PRAGMA table_info(domainspec_outbox)").all() as Array<{name:string}>;if(!columns.some(c=>c.name==="lease_generation")){if(!needsMigration)throw new Error("OUTBOX_SCHEMA_MIGRATION_INCOMPLETE");this.database.exec("ALTER TABLE domainspec_outbox ADD COLUMN lease_generation INTEGER NOT NULL DEFAULT 0")}}
      if(needsMigration)this.database.exec("UPDATE domainspec_outbox SET status='dead',lease_owner=NULL,lease_until=NULL WHERE status IN ('pending','leased') AND attempts>=max_attempts;UPDATE domainspec_outbox SET status='pending',lease_owner=NULL,lease_until=NULL WHERE status='leased';");
      if(needsMigration){
        const legacy=this.database.prepare("SELECT message_id,occurred_at,available_at,lease_until,published_at FROM domainspec_outbox").all() as Array<{message_id:string;occurred_at:string;available_at:string;lease_until:string|null;published_at:string|null}>;
        const normalize=this.database.prepare("UPDATE domainspec_outbox SET occurred_at=?,available_at=?,lease_until=?,published_at=? WHERE message_id=?");
        for(const row of legacy)normalize.run(timestamp(row.occurred_at,"OUTBOX_LEGACY_TIME_INVALID"),timestamp(row.available_at,"OUTBOX_LEGACY_TIME_INVALID"),row.lease_until===null?null:timestamp(row.lease_until,"OUTBOX_LEGACY_TIME_INVALID"),row.published_at===null?null:timestamp(row.published_at,"OUTBOX_LEGACY_TIME_INVALID"),row.message_id);
      }
      const commits=this.database.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='domainspec_outbox_commits'").get();if(!commits&&!needsMigration)throw new Error("OUTBOX_SCHEMA_MIGRATION_INCOMPLETE");
      this.database.exec("CREATE TABLE IF NOT EXISTS domainspec_outbox_commits(aggregate_type TEXT NOT NULL,aggregate_id TEXT NOT NULL,version INTEGER NOT NULL,identity_json TEXT NOT NULL,PRIMARY KEY(aggregate_type,aggregate_id,version));CREATE INDEX IF NOT EXISTS domainspec_outbox_dispatch_idx ON domainspec_outbox(status,available_at,lease_until,occurred_at,message_id)");
      const columns=this.database.prepare("PRAGMA table_info(domainspec_outbox)").all() as Array<{name:string}>;if(!columns.some(c=>c.name==="lease_generation"))throw new Error("OUTBOX_SCHEMA_MIGRATION_INCOMPLETE");
      this.database.prepare("INSERT OR IGNORE INTO domainspec_outbox_migrations VALUES(3,?)").run(new Date().toISOString());
      this.database.exec("COMMIT");
    }catch(e){this.database.exec("ROLLBACK");throw e}
  }
  schemaVersion():number{return(this.database.prepare("SELECT COALESCE(MAX(version),0) version FROM domainspec_outbox_migrations").get() as {version:number}).version}
  commit(request:DurableCommitRequest,failpoint?:"after-state-write"):{status:"committed"|"already-committed";version:number}{
    validate(request);const at=timestamp(request.messages[0]!.occurredAt,"OUTBOX_OCCURRED_AT_INVALID"),identity=commitIdentity(request);
    let outcome:{status:"committed"|"already-committed";version:number};this.database.exec("BEGIN IMMEDIATE");
    try{
      const state=this.database.prepare("SELECT version FROM domainspec_aggregate_state WHERE aggregate_type=? AND aggregate_id=?").get(request.aggregateType,request.aggregateId) as {version:number}|undefined;
      if(state?.version===request.expectedVersion+1){const prior=this.database.prepare("SELECT identity_json FROM domainspec_outbox_commits WHERE aggregate_type=? AND aggregate_id=? AND version=?").get(request.aggregateType,request.aggregateId,state.version) as {identity_json:string}|undefined;if(prior?.identity_json!==identity)throw new Error("OUTBOX_VERSION_CONFLICT");outcome={status:"already-committed",version:state.version}}
      else{
        if((state?.version??0)!==request.expectedVersion)throw new Error("OUTBOX_VERSION_CONFLICT");
        this.database.prepare("INSERT INTO domainspec_aggregate_state VALUES(?,?,?,?,?) ON CONFLICT(aggregate_type,aggregate_id) DO UPDATE SET state_json=excluded.state_json,version=excluded.version,updated_at=excluded.updated_at").run(request.aggregateType,request.aggregateId,JSON.stringify(request.state),request.expectedVersion+1,at);
        if(failpoint)throw new Error("OUTBOX_FAILPOINT_AFTER_STATE_WRITE");
        const insert=this.database.prepare("INSERT INTO domainspec_outbox(message_id,aggregate_type,aggregate_id,event_type,payload_json,occurred_at,max_attempts,available_at)VALUES(?,?,?,?,?,?,?,?)");for(const m of request.messages){const occurredAt=timestamp(m.occurredAt,"OUTBOX_OCCURRED_AT_INVALID");insert.run(m.messageId,request.aggregateType,request.aggregateId,m.eventType,JSON.stringify(m.payload),occurredAt,m.maxAttempts??5,occurredAt)}
        this.database.prepare("INSERT INTO domainspec_outbox_commits VALUES(?,?,?,?)").run(request.aggregateType,request.aggregateId,request.expectedVersion+1,identity);
        outcome={status:"committed",version:request.expectedVersion+1};
      }
      this.database.exec("COMMIT");
    }catch(e){this.database.exec("ROLLBACK");throw e}
    this.emit({kind:outcome.status==="committed"?"committed":"replayed",at});return outcome;
  }
  private decode(r:Row):DurableOutboxRecord{return{messageId:r.message_id,aggregateType:r.aggregate_type,aggregateId:r.aggregate_id,eventType:r.event_type,payload:JSON.parse(r.payload_json),occurredAt:r.occurred_at,status:r.status,attempts:r.attempts,maxAttempts:r.max_attempts,availableAt:r.available_at,leaseOwner:r.lease_owner,leaseUntil:r.lease_until,leaseGeneration:r.lease_generation,lastError:r.last_error,publishedAt:r.published_at}}
  state(type:string,id:string):{state:Readonly<Record<string,unknown>>;version:number}|null{const r=this.database.prepare("SELECT state_json,version FROM domainspec_aggregate_state WHERE aggregate_type=? AND aggregate_id=?").get(type,id)as{state_json:string;version:number}|undefined;return r?{state:JSON.parse(r.state_json),version:r.version}:null}
  records(status?:DurableOutboxStatus,limit=100):readonly DurableOutboxRecord[]{const rows=(status?this.database.prepare("SELECT * FROM domainspec_outbox WHERE status=? ORDER BY occurred_at,message_id LIMIT ?").all(status,limit):this.database.prepare("SELECT * FROM domainspec_outbox ORDER BY occurred_at,message_id LIMIT ?").all(limit))as Row[];return rows.map(r=>this.decode(r))}
  pending(limit=100):readonly DurableOutboxRecord[]{return this.records("pending",limit)}
  claim(workerId:string,now:string,leaseMs:number,limit=100):readonly DurableOutboxRecord[]{
    text(workerId,"OUTBOX_WORKER_ID_REQUIRED");const at=timestamp(now,"OUTBOX_NOW_INVALID");if(!Number.isSafeInteger(leaseMs)||leaseMs<1)throw new Error("OUTBOX_LEASE_MS_INVALID");const until=new Date(Date.parse(at)+leaseMs).toISOString();
    let rows:Row[],exhausted:string[];this.database.exec("BEGIN IMMEDIATE");
    try{
      exhausted=(this.database.prepare("UPDATE domainspec_outbox SET status='dead',lease_owner=NULL,lease_until=NULL WHERE status IN ('pending','leased') AND attempts>=max_attempts AND (status='pending' OR lease_until<=?) RETURNING message_id").all(at)as Array<{message_id:string}>).map(r=>r.message_id);
      const ids=this.database.prepare("SELECT message_id FROM domainspec_outbox WHERE ((status='pending' AND available_at<=?) OR (status='leased' AND lease_until<=?)) AND attempts<max_attempts ORDER BY occurred_at,message_id LIMIT ?").all(at,at,limit)as Array<{message_id:string}>;
      const claim=this.database.prepare("UPDATE domainspec_outbox SET status='leased',lease_owner=?,lease_until=?,attempts=attempts+1,lease_generation=lease_generation+1,last_error=NULL WHERE message_id=? RETURNING *");rows=ids.map(({message_id})=>claim.get(workerId,until,message_id)as Row);
      this.database.exec("COMMIT");
    }catch(e){this.database.exec("ROLLBACK");throw e}
    for(const messageId of exhausted)this.emit({kind:"dead-lettered",messageId,at});for(const row of rows)this.emit({kind:"claimed",messageId:row.message_id,workerId,at});return rows.map(r=>this.decode(r));
  }
  markPublished(id:string,worker:string,generation:number,at:string):void{const time=timestamp(at,"OUTBOX_NOW_INVALID");const x=this.database.prepare("UPDATE domainspec_outbox SET status='published',published_at=?,lease_owner=NULL,lease_until=NULL,last_error=NULL WHERE message_id=? AND status='leased' AND lease_owner=? AND lease_generation=?").run(time,id,worker,generation);if(x.changes!==1)throw new Error(`OUTBOX_LEASE_NOT_OWNED:${id}`);this.emit({kind:"published",messageId:id,workerId:worker,at:time})}
  markFailed(id:string,worker:string,generation:number,error:string,at:string):"pending"|"dead"{const time=timestamp(at,"OUTBOX_NOW_INVALID");const row=this.database.prepare("UPDATE domainspec_outbox SET status=CASE WHEN attempts>=max_attempts THEN 'dead' ELSE 'pending' END,available_at=?,lease_owner=NULL,lease_until=NULL,last_error=? WHERE message_id=? AND status='leased' AND lease_owner=? AND lease_generation=? RETURNING status").get(time,error,id,worker,generation)as{status:"pending"|"dead"}|undefined;if(!row)throw new Error(`OUTBOX_LEASE_NOT_OWNED:${id}`);this.emit({kind:row.status==="dead"?"dead-lettered":"retry-scheduled",messageId:id,workerId:worker,at:time});return row.status}
  requeueDead(id:string,at:string):void{const time=timestamp(at,"OUTBOX_NOW_INVALID");const x=this.database.prepare("UPDATE domainspec_outbox SET status='pending',attempts=0,available_at=?,last_error=NULL WHERE message_id=? AND status='dead'").run(time,id);if(x.changes!==1)throw new Error(`OUTBOX_DEAD_MESSAGE_NOT_FOUND:${id}`);this.emit({kind:"dead-requeued",messageId:id,at:time})}
  stats():Record<DurableOutboxStatus,number>{const x={pending:0,leased:0,published:0,dead:0};for(const r of this.database.prepare("SELECT status,COUNT(*) count FROM domainspec_outbox GROUP BY status").all()as Array<{status:DurableOutboxStatus;count:number}>)x[r.status]=r.count;return x}
  close():void{this.database.close()}[Symbol.dispose]():void{this.close()}
}
export interface DurableWorkerOptions{workerId:string;clock?:()=>string;leaseMs?:number;retryBaseMs?:number;maxRetryMs?:number}
export class DurableOutboxWorker{constructor(private readonly store:DurableSqliteTransactionalOutbox,private readonly transport:DurableOutboxTransport,private readonly options:DurableWorkerOptions){}async dispatch(limit=100):Promise<{published:number;failed:number;dead:number}>{const now=this.options.clock?.()??new Date().toISOString();const claimed=this.store.claim(this.options.workerId,now,this.options.leaseMs??30000,limit);let published=0,failed=0,dead=0;for(const m of claimed){try{await this.transport.publish(m)}catch(e){const delay=Math.min((this.options.retryBaseMs??1000)*2**Math.max(0,m.attempts-1),this.options.maxRetryMs??60000);if(this.store.markFailed(m.messageId,this.options.workerId,m.leaseGeneration,e instanceof Error?e.message:String(e),new Date(Date.parse(now)+delay).toISOString())==="dead")dead++;failed++;continue}this.store.markPublished(m.messageId,this.options.workerId,m.leaseGeneration,now);published++}return{published,failed,dead}}}
