/** C13 service-owned SQLite workflow journal. This is storage, not execution
 * authority: the original, source-bound worker must check the workflow,
 * command outcomes, event receipts, and compensation before writing here.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';
import {DatabaseSync} from 'node:sqlite';
import {canonicalJson, type Json} from '../profile-engine/contracts.js';
import type {GenericContinuationDecisionV1} from './capability-data-v1.js';

const HEX=/^[0-9a-f]{64}$/;
const NAME=/^[A-Za-z_][A-Za-z0-9_]*$/;
const QUALIFIED=/^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$/;
const STATES=['scheduled','claimed','step-prepared','step-committed','suspended-unknown',
  'waiting-event','completed','compensating','compensated','needs-review',
  'continuation-prepared','waiting-condition','retry-later','rejected','cancelled'] as const;
const MAX_INSTANCES=512;
const MAX_HISTORY=8192;
const MAX_STEPS=64;
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const checkedHash=(value:unknown):value is string=>typeof value==='string'&&HEX.test(value);

export type WorkflowState=typeof STATES[number];
export type WorkflowStep=Readonly<{
  name:string;
  entry_id:string;
  entry_contract_sha256:string;
  kind:'operation'|'provider'|'event'|'model'|'document'|'index'|'agent-run';
  binding_sha256?:string;
  compensation_entry_id?:string;
  compensation_contract_sha256?:string;
  continuation_entry_id?:string;
  continuation_contract_sha256?:string;
  maximum_attempts?:number;
}>;
export type WorkflowRunIdentity=Readonly<{
  workflow_id:string;
  owner_service:string;
  /** Durable canonical source closure hash; process-local physical capture IDs are never persisted. */
  source_capture_sha256:string;
  profile_sha256:string;
  contract_sha256:string;
  correlation_name:string;
  correlation_canonical_json:string;
  start_client_key:string;
  start_command_tuple_sha256:string;
  input_canonical_json:string;
  steps:readonly WorkflowStep[];
}>;
export type OwnedWorkflowEpoch=Readonly<{
  store_id:string;
  owner_service:string;
  compatibility_sha256:string;
}>;
export type WorkflowClaim=Readonly<{
  instance_sha256:string;
  fence:number;
  lease_until_ms:number;
}>;
export type WorkflowJournalEvent=Readonly<{
  revision:number;
  from_state:WorkflowState|null;
  to_state:WorkflowState;
  step_index:number;
  fence:number;
  commitment_json:string;
}>;
export type WorkflowInspection=Readonly<{
  instance_sha256:string;
  identity:WorkflowRunIdentity;
  state:WorkflowState;
  step_index:number;
  fence:number;
  lease_until_ms:number;
  revision:number;
  history:readonly WorkflowJournalEvent[];
}>;

type InstanceRow={instance_sha256:string;identity_json:string;state:WorkflowState;
  step_index:number;fence:number;lease_until_ms:number;revision:number};
type HistoryRow={instance_sha256:string;revision:number;from_state:WorkflowState|null;
  to_state:WorkflowState;step_index:number;fence:number;commitment_json:string};
type EpochRow={id:number;store_id:string;owner_service:string;compatibility_sha256:string;
  instance_count:number;history_count:number;ledger_sha256:string};

export const workflowStorageSchemaSQL=`CREATE TABLE IF NOT EXISTS _craft_workflow_instances_v1 (
  instance_sha256 TEXT PRIMARY KEY,
  identity_json TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN (${STATES.map(s=>`'${s}'`).join(',')})),
  step_index INTEGER NOT NULL CHECK(step_index>=-1),
  fence INTEGER NOT NULL CHECK(fence>=0),
  lease_until_ms INTEGER NOT NULL CHECK(lease_until_ms>=0),
  revision INTEGER NOT NULL CHECK(revision>=0)
) STRICT;
CREATE TABLE IF NOT EXISTS _craft_workflow_history_v1 (
  instance_sha256 TEXT NOT NULL REFERENCES _craft_workflow_instances_v1(instance_sha256),
  revision INTEGER NOT NULL CHECK(revision>=0),
  from_state TEXT CHECK(from_state IN (${STATES.map(s=>`'${s}'`).join(',')})),
  to_state TEXT NOT NULL CHECK(to_state IN (${STATES.map(s=>`'${s}'`).join(',')})),
  step_index INTEGER NOT NULL CHECK(step_index>=-1),
  fence INTEGER NOT NULL CHECK(fence>=0),
  commitment_json TEXT NOT NULL,
  PRIMARY KEY(instance_sha256,revision)
) STRICT;
CREATE TABLE IF NOT EXISTS _craft_workflow_epoch_v1 (
  id INTEGER PRIMARY KEY CHECK(id=1),
  store_id TEXT NOT NULL,
  owner_service TEXT NOT NULL,
  compatibility_sha256 TEXT NOT NULL,
  instance_count INTEGER NOT NULL CHECK(instance_count>=0),
  history_count INTEGER NOT NULL CHECK(history_count>=0),
  ledger_sha256 TEXT NOT NULL
) STRICT;
CREATE TRIGGER IF NOT EXISTS _craft_workflow_instance_no_delete_v1
  BEFORE DELETE ON _craft_workflow_instances_v1 BEGIN
    SELECT RAISE(ABORT,'C13_WORKFLOW_DELETE_FORBIDDEN');
  END;
CREATE TRIGGER IF NOT EXISTS _craft_workflow_instance_identity_guard_v1
  BEFORE UPDATE ON _craft_workflow_instances_v1
  WHEN NEW.instance_sha256 IS NOT OLD.instance_sha256 OR NEW.identity_json IS NOT OLD.identity_json
  BEGIN SELECT RAISE(ABORT,'C13_WORKFLOW_IDENTITY_IMMUTABLE'); END;
CREATE TRIGGER IF NOT EXISTS _craft_workflow_history_no_delete_v1
  BEFORE DELETE ON _craft_workflow_history_v1 BEGIN
    SELECT RAISE(ABORT,'C13_WORKFLOW_HISTORY_DELETE_FORBIDDEN');
  END;
CREATE TRIGGER IF NOT EXISTS _craft_workflow_history_no_update_v1
  BEFORE UPDATE ON _craft_workflow_history_v1 BEGIN
    SELECT RAISE(ABORT,'C13_WORKFLOW_HISTORY_UPDATE_FORBIDDEN');
  END;`;

function checkedCanonical(value:unknown,maxBytes:number):Json{
  if(typeof value!=='string'||Buffer.byteLength(value)>maxBytes||value.length<1)
    throw Error('C13_CANONICAL_BOUND');
  try{
    const parsed=JSON.parse(value) as Json;
    if(canonicalJson(parsed)!==value)throw Error('noncanonical');
    return parsed;
  }catch{throw Error('C13_NONCANONICAL_JSON');}
}
function checkedIdentity(identity:WorkflowRunIdentity,owner:string):string{
  if(!identity||typeof identity!=='object'||Array.isArray(identity)||
    !QUALIFIED.test(identity.workflow_id)||!NAME.test(identity.owner_service)||
    identity.owner_service!==owner||
    !checkedHash(identity.source_capture_sha256)||!checkedHash(identity.profile_sha256)||
    !checkedHash(identity.contract_sha256)||!NAME.test(identity.correlation_name)||
    typeof identity.start_client_key!=='string'||identity.start_client_key.length<1||
    [...identity.start_client_key].length>128||Buffer.byteLength(identity.start_client_key)>128||
    !checkedHash(identity.start_command_tuple_sha256)||!Array.isArray(identity.steps)||
    identity.steps.length<1||identity.steps.length>MAX_STEPS)
    throw Error('C13_WORKFLOW_IDENTITY');
  const correlation=checkedCanonical(identity.correlation_canonical_json,8192),
    input=checkedCanonical(identity.input_canonical_json,1048576);
  if(!input||typeof input!=='object'||Array.isArray(input)||
    !Object.hasOwn(input,identity.correlation_name)||
    canonicalJson((input as Record<string,Json>)[identity.correlation_name]!)!==canonicalJson(correlation))
    throw Error('C13_WORKFLOW_CORRELATION_INPUT');
  const names=new Set<string>();
  for(const step of identity.steps){
    if(!step||!NAME.test(step.name)||names.has(step.name)||
      !QUALIFIED.test(step.entry_id)||!checkedHash(step.entry_contract_sha256)||
      !['operation','provider','event','model','document','index','agent-run'].includes(step.kind)||
      (step.binding_sha256!==undefined&&!checkedHash(step.binding_sha256))||
      (step.compensation_entry_id!==undefined&&!QUALIFIED.test(step.compensation_entry_id))||
      (step.compensation_contract_sha256!==undefined&&!checkedHash(step.compensation_contract_sha256))||
      Boolean(step.compensation_entry_id)!==Boolean(step.compensation_contract_sha256)||
      (step.continuation_entry_id!==undefined&&!QUALIFIED.test(step.continuation_entry_id))||
      (step.continuation_contract_sha256!==undefined&&!checkedHash(step.continuation_contract_sha256))||
      Boolean(step.continuation_entry_id)!==Boolean(step.continuation_contract_sha256)||
      (step.maximum_attempts!==undefined&&(!Number.isSafeInteger(step.maximum_attempts)||step.maximum_attempts<1||step.maximum_attempts>8)))
      throw Error('C13_WORKFLOW_STEP_IDENTITY');
    names.add(step.name);
  }
  const json=canonicalJson(identity as Json);
  if(Buffer.byteLength(json)>1114112)throw Error('C13_WORKFLOW_IDENTITY_BOUND');
  return json;
}
export function deriveWorkflowInstance(identity:WorkflowRunIdentity):string{
  // A repeated start command at the same correlation is the same run. Source,
  // profile, plan and input still have to match the immutable stored identity.
  return sha(canonicalJson({workflow_id:identity.workflow_id,
    correlation_canonical_json:identity.correlation_canonical_json,
    start_command_tuple_sha256:identity.start_command_tuple_sha256}));
}
function checkedCommitment(value:Json):string{
  const json=canonicalJson(value);
  if(Buffer.byteLength(json)>65536)throw Error('C13_WORKFLOW_COMMITMENT_BOUND');
  return json;
}
const ACTIVE=new Set<WorkflowState>(['scheduled','claimed','step-prepared','step-committed',
  'suspended-unknown','waiting-event','compensating','continuation-prepared','waiting-condition','retry-later']);
const TERMINAL=new Set<WorkflowState>(['completed','compensated','needs-review','rejected','cancelled']);
function safeTime(value:number):boolean{return Number.isSafeInteger(value)&&value>=0;}
function previousCompensableStep(identity:WorkflowRunIdentity,from:number):number{
  for(let index=from;index>=0;index--){
    if(identity.steps[index]?.compensation_entry_id)return index;
  }
  return -1;
}

/** Physical journal. The service-owned original worker is the only permitted
 * caller for transitions; this module never dispatches an Entry or interprets
 * a provider result supplied by a caller. */
export class GenericWorkflowStore {
  private readonly db:DatabaseSync;
  private readonly owned:OwnedWorkflowEpoch;
  private readonly schemaVersion:number;
  private readonly expectedSchema:string;
  constructor(db:DatabaseSync,owned:OwnedWorkflowEpoch,private readonly assertStorageCurrent:()=>void=()=>{}){
    this.assertStorageCurrent();
    if(!owned||!NAME.test(owned.owner_service)||typeof owned.store_id!=='string'||
      owned.store_id.length<1||owned.store_id.length>256||!checkedHash(owned.compatibility_sha256))
      throw Error('C13_WORKFLOW_OWNER');
    this.db=db;this.owned=Object.freeze({...owned});
    db.exec(workflowStorageSchemaSQL);
    this.schemaVersion=Number((db.prepare('PRAGMA schema_version').get() as {schema_version:number}).schema_version);
    const expected=new DatabaseSync(':memory:');
    try{expected.exec(workflowStorageSchemaSQL);this.expectedSchema=this.schemaOf(expected);}
    finally{expected.close();}
    const epoch=db.prepare('SELECT * FROM _craft_workflow_epoch_v1 WHERE id=1').get() as EpochRow|undefined;
    if(!epoch){
      const count=Number((db.prepare('SELECT COUNT(*) AS n FROM _craft_workflow_instances_v1').get() as {n:number}).n);
      const history=Number((db.prepare('SELECT COUNT(*) AS n FROM _craft_workflow_history_v1').get() as {n:number}).n);
      if(count!==0||history!==0)throw Error('C13_WORKFLOW_EPOCH_MISSING');
      db.prepare('INSERT INTO _craft_workflow_epoch_v1 VALUES(1,?,?,?,?,?,?)').run(
        owned.store_id,owned.owner_service,owned.compatibility_sha256,0,0,sha(canonicalJson({instances:[],history:[]})));
    }
    this.assertCurrent();
  }
  assertOwner(expected:OwnedWorkflowEpoch):void{
    this.assertCurrent();
    if(expected.store_id!==this.owned.store_id||expected.owner_service!==this.owned.owner_service||
      expected.compatibility_sha256!==this.owned.compatibility_sha256)
      throw Error('C13_WORKFLOW_OWNER_MISMATCH');
  }
  private schemaOf(db:DatabaseSync):string{
    return JSON.stringify(db.prepare("SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE name LIKE '_craft_workflow_%' ORDER BY type,name").all());
  }
  private ledger():{instances:InstanceRow[];history:HistoryRow[];digest:string}{
    const instances=this.db.prepare('SELECT * FROM _craft_workflow_instances_v1 ORDER BY instance_sha256').all() as InstanceRow[];
    const history=this.db.prepare('SELECT * FROM _craft_workflow_history_v1 ORDER BY instance_sha256,revision').all() as HistoryRow[];
    if(instances.length>MAX_INSTANCES||history.length>MAX_HISTORY)throw Error('C13_WORKFLOW_LEDGER_BOUND');
    const byId=new Map<string,HistoryRow[]>();
    for(const row of history){
      if(!checkedHash(row.instance_sha256)||!safeTime(row.revision)||!safeTime(row.fence)||
        !Number.isSafeInteger(row.step_index)||row.step_index< -1||
        !STATES.includes(row.to_state)||
        (row.from_state!==null&&!STATES.includes(row.from_state)))throw Error('C13_WORKFLOW_HISTORY_INVALID');
      checkedCanonical(row.commitment_json,65536);
      const group=byId.get(row.instance_sha256)??[];group.push(row);byId.set(row.instance_sha256,group);
    }
    for(const row of instances){
      let identity:WorkflowRunIdentity;
      try{identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
        if(checkedIdentity(identity,this.owned.owner_service)!==row.identity_json||
          deriveWorkflowInstance(identity)!==row.instance_sha256)throw Error('identity');
      }catch{throw Error('C13_WORKFLOW_STORED_IDENTITY');}
      if(!STATES.includes(row.state)||!safeTime(row.revision)||!safeTime(row.fence)||
        !safeTime(row.lease_until_ms)||!Number.isSafeInteger(row.step_index)||
        row.step_index< -1||row.step_index>=identity.steps.length||
        (row.state==='scheduled'&&(row.step_index!==-1||row.fence!==0||row.lease_until_ms!==0))||
        (row.state==='claimed'&&row.fence<1)||
        (TERMINAL.has(row.state)&&row.lease_until_ms!==0))throw Error('C13_WORKFLOW_STORED_STATE');
      const entries=byId.get(row.instance_sha256)??[];
      if(entries.length!==row.revision+1||entries[0]?.revision!==0||
        entries[0]?.from_state!==null||entries[0]?.to_state!=='scheduled')
        throw Error('C13_WORKFLOW_HISTORY_GAP');
      for(let i=1;i<entries.length;i++){
        if(entries[i]!.revision!==i||entries[i]!.from_state!==entries[i-1]!.to_state||
          entries[i]!.fence<entries[i-1]!.fence)throw Error('C13_WORKFLOW_HISTORY_GAP');
      }
      const last=entries.at(-1)!;
      if(last.to_state!==row.state||last.step_index!==row.step_index||last.fence!==row.fence)
        throw Error('C13_WORKFLOW_HISTORY_MISMATCH');
      byId.delete(row.instance_sha256);
    }
    if(byId.size)throw Error('C13_WORKFLOW_ORPHAN_HISTORY');
    return {instances,history,digest:sha(canonicalJson({instances,history} as Json))};
  }
  private assertCurrent():void{
    this.assertStorageCurrent();
    if(Number((this.db.prepare('PRAGMA schema_version').get() as {schema_version:number}).schema_version)!==this.schemaVersion||
      this.schemaOf(this.db)!==this.expectedSchema)throw Error('C13_WORKFLOW_SCHEMA_DRIFT');
    const epoch=this.db.prepare('SELECT * FROM _craft_workflow_epoch_v1 WHERE id=1').get() as EpochRow|undefined;
    if(!epoch||epoch.store_id!==this.owned.store_id||epoch.owner_service!==this.owned.owner_service||
      epoch.compatibility_sha256!==this.owned.compatibility_sha256)
      throw Error('C13_WORKFLOW_EPOCH_IDENTITY');
    const ledger=this.ledger();
    if(epoch.instance_count!==ledger.instances.length||epoch.history_count!==ledger.history.length||
      epoch.ledger_sha256!==ledger.digest)throw Error('C13_WORKFLOW_EPOCH_DRIFT');
  }
  private transaction<T>(work:()=>T):T{
    this.assertStorageCurrent();
    this.db.exec('BEGIN IMMEDIATE');
    try{
      this.assertCurrent();
      const value=work();
      const ledger=this.ledger();
      this.db.prepare('UPDATE _craft_workflow_epoch_v1 SET instance_count=?,history_count=?,ledger_sha256=? WHERE id=1')
        .run(ledger.instances.length,ledger.history.length,ledger.digest);
      this.db.exec('COMMIT');return value;
    }catch(error){this.db.exec('ROLLBACK');throw error;}
  }
  private row(id:string):InstanceRow{
    if(!checkedHash(id))throw Error('C13_WORKFLOW_INSTANCE_ID');
    const row=this.db.prepare('SELECT * FROM _craft_workflow_instances_v1 WHERE instance_sha256=?').get(id) as InstanceRow|undefined;
    if(!row)throw Error('C13_WORKFLOW_ABSENT');
    return row;
  }
  private append(row:InstanceRow,next:WorkflowState,step:number,fence:number,commitment:Json,lease:number):void{
    const revision=row.revision+1;
    const updated=this.db.prepare('UPDATE _craft_workflow_instances_v1 SET state=?,step_index=?,fence=?,lease_until_ms=?,revision=? WHERE instance_sha256=? AND state=? AND step_index=? AND fence=? AND lease_until_ms=? AND revision=?')
      .run(next,step,fence,lease,revision,row.instance_sha256,row.state,row.step_index,row.fence,row.lease_until_ms,row.revision);
    if(updated.changes!==1)throw Error('C13_WORKFLOW_CAS_LOST');
    this.db.prepare('INSERT INTO _craft_workflow_history_v1 VALUES(?,?,?,?,?,?,?)')
      .run(row.instance_sha256,revision,row.state,next,step,fence,checkedCommitment(commitment));
  }
  schedule(identity:WorkflowRunIdentity):{instance_sha256:string;created:boolean}{
    const identity_json=checkedIdentity(identity,this.owned.owner_service);
    const instance_sha256=deriveWorkflowInstance(identity);
    return this.transaction(()=>{
      const existing=this.db.prepare('SELECT identity_json FROM _craft_workflow_instances_v1 WHERE instance_sha256=?')
        .get(instance_sha256) as {identity_json:string}|undefined;
      if(existing){
        if(existing.identity_json!==identity_json)throw Error('C13_WORKFLOW_INSTANCE_COLLISION');
        return {instance_sha256,created:false};
      }
      const count=Number((this.db.prepare('SELECT COUNT(*) AS n FROM _craft_workflow_instances_v1').get() as {n:number}).n);
      if(count>=MAX_INSTANCES)throw Error('C13_WORKFLOW_LEDGER_BOUND');
      this.db.prepare('INSERT INTO _craft_workflow_instances_v1 VALUES(?,?,?,?,?,?,?)')
        .run(instance_sha256,identity_json,'scheduled',-1,0,0,0);
      this.db.prepare('INSERT INTO _craft_workflow_history_v1 VALUES(?,?,?,?,?,?,?)')
        .run(instance_sha256,0,null,'scheduled',-1,0,checkedCommitment({kind:'schedule'}));
      return {instance_sha256,created:true};
    });
  }
  inspect(instance_sha256:string):WorkflowInspection{
    this.assertCurrent();
    const row=this.row(instance_sha256);
    const history=this.db.prepare('SELECT * FROM _craft_workflow_history_v1 WHERE instance_sha256=? ORDER BY revision')
      .all(instance_sha256) as HistoryRow[];
    return Object.freeze({instance_sha256,identity:JSON.parse(row.identity_json) as WorkflowRunIdentity,
      state:row.state,step_index:row.step_index,fence:row.fence,lease_until_ms:row.lease_until_ms,
      revision:row.revision,history:history.map(({revision,from_state,to_state,step_index,fence,commitment_json})=>
        Object.freeze({revision,from_state,to_state,step_index,fence,commitment_json}))});
  }
  claimNext(lease_ms:number):WorkflowClaim|null{
    if(!Number.isSafeInteger(lease_ms)||lease_ms<1||lease_ms>300000)throw Error('C13_WORKFLOW_LEASE_BOUND');
    return this.transaction(()=>{
      const now=Date.now();
      const row=this.db.prepare(`SELECT * FROM _craft_workflow_instances_v1
        WHERE state IN ('scheduled','claimed','step-prepared','step-committed','suspended-unknown','waiting-event','compensating','continuation-prepared','waiting-condition','retry-later')
        AND lease_until_ms<=? AND (state<>'retry-later' OR COALESCE((
          SELECT CASE WHEN json_extract(h.commitment_json,'$.kind')='native-no-effect-wait'
            THEN json_extract(h.commitment_json,'$.not_before_ms') ELSE 0 END
          FROM _craft_workflow_history_v1 h WHERE h.instance_sha256=_craft_workflow_instances_v1.instance_sha256
            AND json_extract(h.commitment_json,'$.kind') NOT IN ('claim','renew-lease','native-retry-release')
          ORDER BY h.revision DESC LIMIT 1),0)<=?)
        ORDER BY instance_sha256 LIMIT 1`).get(now,now) as InstanceRow|undefined;
      if(!row)return null;
      const fence=row.fence+1;
      if(!safeTime(fence)||!safeTime(now+lease_ms))throw Error('C13_WORKFLOW_FENCE_BOUND');
      const next=row.state==='scheduled'?'claimed':row.state;
      const lease_until_ms=now+lease_ms;
      this.append(row,next,row.step_index,fence,{kind:'claim'},lease_until_ms);
      return Object.freeze({instance_sha256:row.instance_sha256,fence,lease_until_ms});
    });
  }
  renewClaim(claim:WorkflowClaim,lease_ms:number):WorkflowClaim{
    if(!Number.isSafeInteger(lease_ms)||lease_ms<1||lease_ms>300000)throw Error('C13_WORKFLOW_LEASE_BOUND');
    return this.transaction(()=>{
      const row=this.claimedRow(claim);
      const lease_until_ms=Math.max(row.lease_until_ms+1,Date.now()+lease_ms);
      if(!safeTime(lease_until_ms))throw Error('C13_WORKFLOW_LEASE_BOUND');
      this.append(row,row.state,row.step_index,row.fence,{kind:'renew-lease'},lease_until_ms);
      return Object.freeze({instance_sha256:row.instance_sha256,fence:row.fence,lease_until_ms});
    });
  }
  private claimedRow(claim:WorkflowClaim):InstanceRow{
    if(!claim||!checkedHash(claim.instance_sha256)||!safeTime(claim.fence)||claim.fence<1||
      !safeTime(claim.lease_until_ms))throw Error('C13_WORKFLOW_CLAIM');
    const row=this.row(claim.instance_sha256);
    if(row.fence!==claim.fence||row.lease_until_ms!==claim.lease_until_ms||
      row.lease_until_ms<=Date.now()||!ACTIVE.has(row.state)||row.state==='scheduled')
      throw Error('C13_WORKFLOW_STALE_CLAIM');
    return row;
  }
  private lastEffectiveCommitment(instance_sha256:string):{kind:string;step_name?:string}{
    const entries=this.db.prepare('SELECT commitment_json FROM _craft_workflow_history_v1 WHERE instance_sha256=? ORDER BY revision DESC')
      .all(instance_sha256) as {commitment_json:string}[];
    for(const entry of entries){
      const commitment=JSON.parse(entry.commitment_json) as {kind:string;step_name?:string};
      if(commitment.kind!=='claim'&&commitment.kind!=='renew-lease'&&commitment.kind!=='native-retry-release')return commitment;
    }
    throw Error('C13_WORKFLOW_HISTORY_GAP');
  }
  assertClaimCurrent(claim:WorkflowClaim):WorkflowInspection{
    this.assertCurrent();this.claimedRow(claim);return this.inspect(claim.instance_sha256);
  }
  /** Record the exact next checked step and original command identity before
   * the worker dispatches it. Reopen leaves this record available for C11/C12
   * same-command inspection rather than permitting a fresh command. */
  prepareStep(claim:WorkflowClaim,step_name:string,command_tuple_sha256:string,input_sha256:string):void{
    if(!checkedHash(command_tuple_sha256)||!checkedHash(input_sha256))throw Error('C13_WORKFLOW_COMMAND_IDENTITY');
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='claimed'&&row.state!=='step-committed')throw Error('C13_WORKFLOW_TRANSITION');
      const step_index=row.step_index+1;
      const identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      const step=identity.steps[step_index];
      if(!step||step.name!==step_name||step.kind==='event')throw Error('C13_WORKFLOW_STEP_ORDER');
      this.append(row,'step-prepared',step_index,row.fence,{kind:'prepare-step',step_name,
        entry_id:step.entry_id,command_tuple_sha256,input_sha256},row.lease_until_ms);
    });
  }
  /** A commitment to a result already established by the original adapter.
   * The journal itself cannot decide whether that result is authoritative. */
  commitStep(claim:WorkflowClaim,outcome_sha256:string,output_canonical_json?:string,dispatch_evidence?:'proven-not-dispatched'):void{
    if(!checkedHash(outcome_sha256))throw Error('C13_WORKFLOW_OUTCOME_COMMITMENT');
    if(output_canonical_json!==undefined)checkedCanonical(output_canonical_json,32768);
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='step-prepared'&&row.state!=='suspended-unknown')throw Error('C13_WORKFLOW_TRANSITION');
      this.append(row,'step-committed',row.step_index,row.fence,{kind:'commit-step',outcome_sha256,...(output_canonical_json!==undefined?{output_canonical_json}:{}),...(dispatch_evidence?{dispatch_evidence}:{})},row.lease_until_ms);
    });
  }
  prepareContinuation(claim:WorkflowClaim,command_tuple_sha256:string,input_sha256:string):void{
    if(!checkedHash(command_tuple_sha256)||!checkedHash(input_sha256))throw Error('C13_WORKFLOW_CONTINUATION_IDENTITY');
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(!['step-committed','waiting-condition','retry-later'].includes(row.state))throw Error('C13_WORKFLOW_TRANSITION');
      const identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      if(!identity.steps[row.step_index]?.continuation_entry_id)throw Error('C13_WORKFLOW_CONTINUATION_SOURCE');
      const ordinal=Number((this.db.prepare("SELECT count(*) n FROM _craft_workflow_history_v1 WHERE instance_sha256=? AND step_index=? AND json_extract(commitment_json,'$.kind')='prepare-continuation'").get(row.instance_sha256,row.step_index) as {n:number}).n)+1;
      if(ordinal>64)throw Error('C13_WORKFLOW_CONTINUATION_BOUND');
      this.append(row,'continuation-prepared',row.step_index,row.fence,{kind:'prepare-continuation',command_tuple_sha256,input_sha256,ordinal},row.lease_until_ms);
    });
  }
  commitContinuation(claim:WorkflowClaim,decision:GenericContinuationDecisionV1,outcome_sha256:string):void{
    if(!checkedHash(outcome_sha256))throw Error('C13_WORKFLOW_CONTINUATION_IDENTITY');
    this.transaction(()=>{
      const row=this.claimedRow(claim),identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      if(row.state!=='continuation-prepared')throw Error('C13_WORKFLOW_TRANSITION');
      const kinds=['advance','complete','business-rejection','wait','review','unknown','cancel','retry'];
      if(!decision||!kinds.includes(decision.kind))throw Error('C13_WORKFLOW_CONTINUATION_DECISION');
      if(decision.kind==='advance'||decision.kind==='complete'){if(!checkedHash(decision.result_sha256))throw Error('C13_WORKFLOW_CONTINUATION_DECISION');}
      if(decision.kind==='wait'&&(!QUALIFIED.test(decision.condition)||!safeTime(decision.deadline_ms)||decision.deadline_ms<=Date.now()||decision.deadline_ms>Date.now()+86400000))throw Error('C13_WORKFLOW_WAIT_BOUND');
      if(decision.kind==='retry'){
        const retries=Number((this.db.prepare("SELECT count(*) n FROM _craft_workflow_history_v1 WHERE instance_sha256=? AND step_index=? AND json_extract(commitment_json,'$.kind')='retry-stage'").get(row.instance_sha256,row.step_index) as {n:number}).n);
        if(decision.dispatch_evidence!=='proven-not-dispatched'||decision.maximum!==(identity.steps[row.step_index]?.maximum_attempts??1)||decision.attempt!==retries+2||decision.attempt>decision.maximum||!safeTime(decision.not_before_ms)||decision.not_before_ms>Date.now()+86400000)throw Error('C13_WORKFLOW_RETRY_BOUND');
      }
      const next:WorkflowState=decision.kind==='advance'?'step-committed':decision.kind==='complete'?'completed':decision.kind==='wait'?'waiting-condition':decision.kind==='retry'?'retry-later':decision.kind==='cancel'?'cancelled':decision.kind==='business-rejection'?'rejected':'needs-review';
      this.append(row,next,row.step_index,row.fence,{kind:'continuation-decision',decision:decision as Json,outcome_sha256},TERMINAL.has(next)?0:row.lease_until_ms);
    });
  }
  prepareRetryStep(claim:WorkflowClaim,command_tuple_sha256:string,input_sha256:string):void{
    if(!checkedHash(command_tuple_sha256)||!checkedHash(input_sha256))throw Error('C13_WORKFLOW_RETRY_IDENTITY');
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='retry-later')throw Error('C13_WORKFLOW_TRANSITION');
      const last=this.lastEffectiveCommitment(row.instance_sha256) as {kind:string;decision?:GenericContinuationDecisionV1},decision=last.decision;
      if(last.kind!=='continuation-decision'||decision?.kind!=='retry'||Date.now()<decision.not_before_ms)throw Error('C13_WORKFLOW_RETRY_NOT_READY');
      this.append(row,'step-prepared',row.step_index,row.fence,{kind:'retry-stage',command_tuple_sha256,input_sha256,attempt:decision.attempt},row.lease_until_ms);
    });
  }
  /** Native no-effect evidence is distinct from a local not-dispatched retry.
   * Timing is a durable commitment; original effect owners still authorize and
   * bound every new attempt. No business command/key/attempt is replaced. */
  waitNativeRetry(claim:WorkflowClaim,evidence:Readonly<{original_attempt:string;not_before_ms:number;deadline_ms:number}>):void{
    if(!evidence||Object.keys(evidence).sort().join(',')!=='deadline_ms,not_before_ms,original_attempt'||typeof evidence.original_attempt!=='string'||!evidence.original_attempt.length||evidence.original_attempt.length>256||!safeTime(evidence.not_before_ms)||!safeTime(evidence.deadline_ms)||evidence.not_before_ms>=evidence.deadline_ms||evidence.deadline_ms<=Date.now()||evidence.deadline_ms>Date.now()+86400000)throw Error('R03_NATIVE_RETRY_BOUND');
    this.transaction(()=>{const row=this.claimedRow(claim);if(row.state!=='step-prepared'&&row.state!=='suspended-unknown')throw Error('C13_WORKFLOW_TRANSITION');
      const count=Number((this.db.prepare("SELECT count(*) n FROM _craft_workflow_history_v1 WHERE instance_sha256=? AND step_index=? AND json_extract(commitment_json,'$.kind')='native-no-effect-wait'").get(row.instance_sha256,row.step_index) as {n:number}).n);if(count>=1024)throw Error('R03_NATIVE_RETRY_BOUND');
      this.append(row,'retry-later',row.step_index,row.fence,{kind:'native-no-effect-wait',...evidence,evidence:'original-confirmed-no-effect'},0);
    });
  }
  releaseNativeRetry(claim:WorkflowClaim):void{
    this.transaction(()=>{const row=this.claimedRow(claim);if(row.state!=='retry-later'||this.lastEffectiveCommitment(row.instance_sha256).kind!=='native-no-effect-wait')throw Error('C13_WORKFLOW_TRANSITION');this.append(row,'retry-later',row.step_index,row.fence,{kind:'native-retry-release'},0);});
  }
  resumeNativeRetry(claim:WorkflowClaim):void{
    this.transaction(()=>{const row=this.claimedRow(claim),pending=this.lastEffectiveCommitment(row.instance_sha256) as {kind:string;original_attempt:string;not_before_ms:number;deadline_ms:number};if(row.state!=='retry-later'||pending.kind!=='native-no-effect-wait'||Date.now()<pending.not_before_ms||Date.now()>=pending.deadline_ms)throw Error('R03_NATIVE_RETRY_NOT_READY');
      this.append(row,'step-prepared',row.step_index,row.fence,{kind:'native-retry-resume',original_attempt:pending.original_attempt,deadline_ms:pending.deadline_ms},row.lease_until_ms);
    });
  }
  suspendUnknown(claim:WorkflowClaim):void{
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='step-prepared')throw Error('C13_WORKFLOW_TRANSITION');
      this.append(row,'suspended-unknown',row.step_index,row.fence,{kind:'unknown-outcome'},row.lease_until_ms);
    });
  }
  /** Original worker calls this only after a definite, checked failure. The
   * failed step has no committed effect and is never compensated. */
  definiteStepFailure(claim:WorkflowClaim,failure_sha256:string):void{
    if(!checkedHash(failure_sha256))throw Error('C13_WORKFLOW_FAILURE_COMMITMENT');
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='step-prepared'&&row.state!=='suspended-unknown')
        throw Error('C13_WORKFLOW_TRANSITION');
      const identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      const step_index=previousCompensableStep(identity,row.step_index-1);
      this.append(row,'compensating',step_index,row.fence,{kind:'definite-step-failure',
        failed_step:identity.steps[row.step_index]!.name,failure_sha256},row.lease_until_ms);
    });
  }
  waitForEvent(claim:WorkflowClaim,step_name:string):void{
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='claimed'&&row.state!=='step-committed')throw Error('C13_WORKFLOW_TRANSITION');
      const step_index=row.step_index+1;
      const identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      const step=identity.steps[step_index];
      if(!step||step.name!==step_name||step.kind!=='event')throw Error('C13_WORKFLOW_STEP_ORDER');
      this.append(row,'waiting-event',step_index,row.fence,{kind:'wait-event',step_name,
        entry_id:step.entry_id,binding_sha256:step.binding_sha256??null},row.lease_until_ms);
    });
  }
  commitEvent(claim:WorkflowClaim,occurrence_sha256:string,consumer_command_tuple_sha256:string):void{
    if(!checkedHash(occurrence_sha256)||!checkedHash(consumer_command_tuple_sha256))
      throw Error('C13_WORKFLOW_EVENT_COMMITMENT');
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='waiting-event')throw Error('C13_WORKFLOW_TRANSITION');
      this.append(row,'step-committed',row.step_index,row.fence,{kind:'commit-event',
        occurrence_sha256,consumer_command_tuple_sha256},row.lease_until_ms);
    });
  }
  complete(claim:WorkflowClaim):void{
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      const identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      if(row.state!=='step-committed'||row.step_index!==identity.steps.length-1)
        throw Error('C13_WORKFLOW_TRANSITION');
      this.append(row,'completed',row.step_index,row.fence,{kind:'complete'},0);
    });
  }
  beginCompensation(claim:WorkflowClaim):void{
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='step-committed'&&row.state!=='waiting-event')throw Error('C13_WORKFLOW_TRANSITION');
      const identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      const step_index=previousCompensableStep(identity,row.step_index);
      this.append(row,'compensating',step_index,row.fence,{kind:'begin-compensation'},row.lease_until_ms);
    });
  }
  /** Persist the exact compensating command before dispatch. A reopened worker
   * must inspect this record and resume the same command, never prepare a new
   * tuple for an unknown previous attempt. */
  prepareCompensation(claim:WorkflowClaim,step_name:string,command_tuple_sha256:string,
    input_sha256:string):void{
    if(!checkedHash(command_tuple_sha256)||!checkedHash(input_sha256))
      throw Error('C13_WORKFLOW_COMPENSATION_COMMITMENT');
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='compensating')throw Error('C13_WORKFLOW_TRANSITION');
      if(this.lastEffectiveCommitment(row.instance_sha256).kind==='prepare-compensation')
        throw Error('C13_WORKFLOW_COMPENSATION_PENDING');
      const identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      const step=identity.steps[row.step_index];
      if(!step||step.name!==step_name||!step.compensation_entry_id)
        throw Error('C13_WORKFLOW_COMPENSATION_ORDER');
      this.append(row,'compensating',row.step_index,row.fence,{kind:'prepare-compensation',step_name,
        compensation_entry_id:step.compensation_entry_id,command_tuple_sha256,input_sha256},row.lease_until_ms);
    });
  }
  commitCompensation(claim:WorkflowClaim,outcome_sha256:string):void{
    if(!checkedHash(outcome_sha256))throw Error('C13_WORKFLOW_COMPENSATION_COMMITMENT');
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='compensating')throw Error('C13_WORKFLOW_TRANSITION');
      const prepared=this.lastEffectiveCommitment(row.instance_sha256);
      if(prepared.kind!=='prepare-compensation')throw Error('C13_WORKFLOW_COMPENSATION_NOT_PREPARED');
      const identity=JSON.parse(row.identity_json) as WorkflowRunIdentity;
      const next_index=previousCompensableStep(identity,row.step_index-1);
      this.append(row,'compensating',next_index,row.fence,{kind:'compensated-step',
        step_name:prepared.step_name!,outcome_sha256},row.lease_until_ms);
    });
  }
  finishCompensation(claim:WorkflowClaim):void{
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      if(row.state!=='compensating'||row.step_index!==-1)throw Error('C13_WORKFLOW_TRANSITION');
      this.append(row,'compensated',-1,row.fence,{kind:'compensated'},0);
    });
  }
  needsReview(claim:WorkflowClaim,reason:'missing-compensation'|'ambiguous-outcome'|'external-reconciliation'):void{
    if(!['missing-compensation','ambiguous-outcome','external-reconciliation'].includes(reason))
      throw Error('C13_WORKFLOW_REVIEW_REASON');
    this.transaction(()=>{
      const row=this.claimedRow(claim);
      this.append(row,'needs-review',row.step_index,row.fence,{kind:'needs-review',reason},0);
    });
  }
}
