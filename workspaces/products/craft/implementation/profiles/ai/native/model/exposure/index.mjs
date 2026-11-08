import {DatabaseSync} from 'node:sqlite';
import {canonical,digest} from '../../source-release/index.mjs';

export const EXPOSURE_ABI='model-exposure-ledger/v1';
const fail=code=>{throw new Error(code);};
const text=v=>typeof v==='string'&&v.length>0&&v.length<=2048||fail('EXPOSURE_IDENTITY');
const uint=v=>Number.isSafeInteger(v)&&v>=0||fail('EXPOSURE_UNITS');
const money=v=>typeof v==='string'&&/^(0|[1-9][0-9]{0,29})$/.test(v)||fail('EXPOSURE_MONEY');
const hex=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v)||fail('EXPOSURE_DIGEST');
const copy=v=>JSON.parse(canonical(v));
const total=(rows,key)=>rows.reduce((n,r)=>n+BigInt(r[key]??0),0n);

/** Trusted model/effect owners hold port; host alone holds authority. Reservation
 * is admission, never proof of provider usage. Existing R02 dispatch owns every
 * provider invocation; no second effect store, retry loop or provider client.
 * Open Questions: README.md. */
export function createExposureLedger({path,now=Date.now,observer,releasePort}) {
  text(path);const db=new DatabaseSync(path);db.exec(`PRAGMA busy_timeout=5000;PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;
    CREATE TABLE IF NOT EXISTS mx_allocations(id TEXT PRIMARY KEY,body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS mx_runs(id TEXT PRIMARY KEY,body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS mx_reservations(id TEXT PRIMARY KEY,attempt TEXT NOT NULL UNIQUE,run TEXT,child TEXT,body TEXT NOT NULL,UNIQUE(run,child)) STRICT;
    CREATE TABLE IF NOT EXISTS mx_events(id INTEGER PRIMARY KEY,reservation TEXT NOT NULL,kind TEXT NOT NULL,at INTEGER NOT NULL,body TEXT NOT NULL) STRICT;`);
  for(const table of ['mx_runs','mx_reservations','mx_events'])db.exec(`CREATE TRIGGER IF NOT EXISTS ${table}_no_update BEFORE UPDATE ON ${table} BEGIN SELECT RAISE(ABORT,'IMMUTABLE_EXPOSURE'); END;
    CREATE TRIGGER IF NOT EXISTS ${table}_no_delete BEFORE DELETE ON ${table} BEGIN SELECT RAISE(ABORT,'IMMUTABLE_EXPOSURE'); END;`);
  const handles=new WeakMap();
  const tx=fn=>{db.exec('BEGIN IMMEDIATE');try{const r=fn();db.exec('COMMIT');return r;}catch(e){if(db.isTransaction)db.exec('ROLLBACK');throw e;}};
  const emit=(transition,id)=>{try{const e={category:'model',transition,correlation_id:id};const r=typeof observer==='function'?observer(e):observer?.emit(e);r?.catch?.(()=>{});}catch{}};
  const get=(table,id)=>{text(id);const r=db.prepare(`SELECT body FROM ${table} WHERE id=?`).get(id);return r?JSON.parse(r.body):fail('EXPOSURE_MISSING');};
  const events=id=>db.prepare('SELECT kind,body FROM mx_events WHERE reservation=? ORDER BY id').all(id).map(r=>({kind:r.kind,...JSON.parse(r.body)}));
  function handle(id){const h=Object.freeze({kind:EXPOSURE_ABI+'/reservation',id});handles.set(h,id);return h;}
  function read(h){const id=handles.get(h);if(!id)fail('FOREIGN_RESERVATION');return get('mx_reservations',id);}
  function event(r,kind,body={}){db.prepare('INSERT INTO mx_events(reservation,kind,at,body) VALUES(?,?,?,?)').run(r.id,kind,now(),canonical(body));}
  function used(r){const e=events(r.id).filter(e=>e.kind==='observed'||e.kind==='settled').at(-1);return {attempts:1,tokens:e?.actualTokens??r.maxTokens,tokenKind:e?'observed':'reserved',costMicros:e?.actualCostMicros??r.maxCostMicros??'0',costBounded:r.maxCostMicros!==undefined,costKind:e?.actualCostMicros!==undefined?'observed':r.maxCostMicros!==undefined?'reserved':'unknown'};}
  function rows(){return db.prepare('SELECT body FROM mx_reservations').all().map(r=>JSON.parse(r.body));}
  function matches(a,r){return a.billingAccount===r.billingAccount&&a.tenant===r.tenant&&(a.application==='*'||a.application===r.application);}
  function assertBudget(a,reservations,extra){const usage=[...reservations.map(used),extra];
    if(total(usage,'attempts')>BigInt(a.maxAttempts)||total(usage,'tokens')>BigInt(a.maxTokens))fail('EXPOSURE_BUDGET');
    if(a.maxCostMicros!==undefined){if(usage.some(u=>!u.costBounded))fail('MONETARY_BOUND_REQUIRED');if(total(usage,'costMicros')>BigInt(a.maxCostMicros))fail('EXPOSURE_COST_BUDGET');}}
  function inspect(r){const history=events(r.id),last=history.filter(e=>e.kind!=='estimated').at(-1);return {id:r.id,attemptId:r.attemptId,identity:copy(r),state:last?.kind??'reserved',exposure:used(r),events:history};}
  const authority=Object.freeze({
    configureAllocation(a){for(const k of ['id','billingAccount','tenant','application'])text(a[k]);uint(a.maxAttempts);uint(a.maxTokens);if(a.maxCostMicros!==undefined)money(a.maxCostMicros);
      const value=Object.fromEntries(['id','billingAccount','tenant','application','maxAttempts','maxTokens',...(a.maxCostMicros===undefined?[]:['maxCostMicros'])].map(k=>[k,a[k]]));
      return tx(()=>{const old=db.prepare('SELECT body FROM mx_allocations WHERE id=?').get(a.id);if(old){const previous=JSON.parse(old.body);for(const k of ['billingAccount','tenant','application'])if(previous[k]!==a[k])fail('ALLOCATION_IDENTITY_IMMUTABLE');}
        assertBudget(value,rows().filter(r=>matches(value,r)),{attempts:0,tokens:0,costMicros:'0',costBounded:true});db.prepare('INSERT INTO mx_allocations VALUES(?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body').run(a.id,canonical(value));return copy(value);});},
    settle({reservationId,reason,actualTokens,actualCostMicros}){text(reason);uint(actualTokens);if(actualCostMicros!==undefined)money(actualCostMicros);
      return tx(()=>{const r=get('mx_reservations',reservationId);event(r,'settled',{reason,actualTokens,...(actualCostMicros===undefined?{}:{actualCostMicros})});return inspect(r);});},
  });
  const port=Object.freeze({
    abi:EXPOSURE_ABI,
    createRun(run){for(const k of ['runId','billingAccount','tenant','application'])text(run[k]);uint(run.maxChildAttempts);uint(run.maxTokens);if(run.maxCostMicros!==undefined)money(run.maxCostMicros);
      if(run.accounting!==undefined&&run.accounting!=='explicit')fail('OPAQUE_ACCOUNTING_UNSUPPORTED');
      const value={runId:run.runId,billingAccount:run.billingAccount,tenant:run.tenant,application:run.application,maxChildAttempts:run.maxChildAttempts,maxTokens:run.maxTokens,...(run.maxCostMicros===undefined?{}:{maxCostMicros:run.maxCostMicros}),accounting:'explicit'};
      return tx(()=>{const old=db.prepare('SELECT body FROM mx_runs WHERE id=?').get(run.runId);if(old&&old.body!==canonical(value))fail('RUN_IDENTITY_CONFLICT');db.prepare('INSERT OR IGNORE INTO mx_runs VALUES(?,?)').run(run.runId,canonical(value));return copy(value);});},
    reserve(request){
      const required=['requestId','attemptId','billingAccount','tenant','application','modelId','destination','resourceId'];for(const k of required)text(request[k]);
      for(const k of ['promptSha256','inputSha256','payloadSha256'])hex(request[k]);uint(request.fence);uint(request.maxTokens);
      if(request.maxCostMicros!==undefined){money(request.maxCostMicros);text(request.pricePolicyRevision);}
      if(request.runId!==undefined){text(request.runId);text(request.childId);}else if(request.childId!==undefined)fail('CHILD_REQUIRES_RUN');
      if(request.accounting!==undefined&&request.accounting!=='explicit')fail('OPAQUE_ACCOUNTING_UNSUPPORTED');
      const keys=[...required,'promptSha256','inputSha256','payloadSha256','fence','maxTokens',...(request.maxCostMicros===undefined?[]:['maxCostMicros','pricePolicyRevision']),...(request.runId===undefined?[]:['runId','childId'])];
      const data=Object.fromEntries(keys.map(k=>[k,request[k]]));const id=digest(canonical(data));const r={id,...data};
      return tx(()=>{const existing=db.prepare('SELECT body FROM mx_reservations WHERE attempt=?').get(r.attemptId);if(existing){if(existing.body!==canonical(r))fail('RESERVATION_IDENTITY_CONFLICT');return handle(id);}
        const allocations=db.prepare('SELECT body FROM mx_allocations').all().map(r=>JSON.parse(r.body)).filter(a=>matches(a,r));
        if(!allocations.length)fail('ALLOCATION_REQUIRED');const existingRows=rows();const extra={attempts:1,tokens:r.maxTokens,costMicros:r.maxCostMicros??'0',costBounded:r.maxCostMicros!==undefined};
        for(const a of allocations)assertBudget(a,existingRows.filter(x=>matches(a,x)),extra);
        if(r.runId){const run=get('mx_runs',r.runId);for(const k of ['billingAccount','tenant','application'])if(run[k]!==r[k])fail('RUN_SCOPE');
          if(existingRows.some(x=>x.runId===r.runId&&x.childId===r.childId))fail('CHILD_ALREADY_CHARGED');assertBudget({...run,maxAttempts:run.maxChildAttempts},existingRows.filter(x=>x.runId===r.runId),extra);}
        db.prepare('INSERT INTO mx_reservations VALUES(?,?,?,?,?)').run(id,r.attemptId,r.runId??null,r.childId??null,canonical(r));event(r,'reserved');emit('prepared',r.attemptId);return handle(id);});
    },
    recoverReservation(id){get('mx_reservations',id);return handle(id);},
    inspect(reservation){return inspect(read(reservation));},
    markRelease(reservation,{ticket}){if(typeof releasePort?.describeRelease!=='function')fail('ORIGINAL_SOURCE_RELEASE_REQUIRED');const b=releasePort.describeRelease(ticket);return tx(()=>{const r=read(reservation);
      for(const [k,v] of [['attemptId',r.attemptId],['fence',r.fence],['tenant',r.tenant],['resourceId',r.resourceId],['payloadSha256',r.payloadSha256],['sink',r.destination]])if(b[k]!==v)fail('EXPOSURE_RELEASE_MISMATCH');
      if(b.expiresAt<=now()||releasePort.inspectConsumption(ticket))fail('EXPOSURE_RELEASE_NOT_CURRENT');
      const release={manifestId:b.manifestId,releaseSha256:digest(canonical(b))};const previous=events(r.id).find(e=>e.kind==='released');if(previous){if(previous.releaseSha256!==release.releaseSha256)fail('RELEASE_IDENTITY_CONFLICT');return inspect(r);}if(events(r.id).some(e=>e.kind==='dispatched'))fail('RELEASE_AFTER_DISPATCH');event(r,'released',release);return inspect(r);});},
    markUnknown(reservation,{attemptId,fence,reason='usage-unknown'}){text(reason);return tx(()=>{const r=read(reservation);if(r.attemptId!==attemptId||r.fence!==fence)fail('STALE_USAGE_IDENTITY');if(!events(r.id).some(e=>['observed','settled'].includes(e.kind)))event(r,'unknown',{reason});emit('unknown',r.attemptId);return inspect(r);});},
    observeUsage(reservation,{attemptId,fence,inputTokens,outputTokens,costMicros,receiptId}) {
      uint(inputTokens);uint(outputTokens);text(receiptId);if(costMicros!==undefined)money(costMicros);const actualTokens=inputTokens+outputTokens;uint(actualTokens);
      return tx(()=>{const r=read(reservation);if(r.attemptId!==attemptId||r.fence!==fence)fail('STALE_USAGE_IDENTITY');
        const history=events(r.id);if(!history.some(e=>e.kind==='dispatched'))fail('USAGE_BEFORE_DISPATCH');
        const body={attemptId,fence,inputTokens,outputTokens,actualTokens,receiptId,...(costMicros===undefined?{}:{actualCostMicros:costMicros})};
        const prior=history.find(e=>e.kind==='observed');if(prior){const {kind,...p}=prior;if(canonical(p)!==canonical(body))fail('USAGE_OBSERVATION_CONFLICT');return inspect(r);}
        if(history.some(e=>e.kind==='settled'))fail('USAGE_AFTER_MANUAL_SETTLEMENT');event(r,'observed',body);emit('returned',r.attemptId);return inspect(r);});
    },
    recordEstimate(reservation,{attemptId,fence,inputTokens,outputTokens}){uint(inputTokens);uint(outputTokens);return tx(()=>{const r=read(reservation);if(r.attemptId!==attemptId||r.fence!==fence)fail('STALE_USAGE_IDENTITY');event(r,'estimated',{inputTokens,outputTokens});return inspect(r);});},
    async dispatch({reservation,dispatcher,attemptId,ticket,signal}) {
      const r=read(reservation);if(r.attemptId!==attemptId)fail('RESERVATION_ATTEMPT_MISMATCH');if(!dispatcher||typeof dispatcher.dispatch!=='function'||typeof dispatcher.getAttempt!=='function')fail('ORIGINAL_EFFECT_OWNER_REQUIRED');
      const a=dispatcher.getAttempt(attemptId);if(a.payloadSha256!==r.payloadSha256||a.binding.tenant!==r.tenant||a.binding.resourceId!==r.resourceId||a.binding.fence!==r.fence||a.selection.provider!==r.destination)fail('RESERVATION_DISPATCH_MISMATCH');
      tx(()=>{const history=events(r.id);if(history.some(e=>['observed','settled'].includes(e.kind)))fail('RESERVATION_SETTLED');if(history.some(e=>e.kind==='dispatched'))fail('RESERVATION_ALREADY_DISPATCHED');const release=history.find(e=>e.kind==='released');if(!release)fail('SOURCE_RELEASE_CHECKPOINT_REQUIRED');
        if(!releasePort||digest(canonical(releasePort.describeRelease(ticket)))!==release.releaseSha256)fail('EXPOSURE_RELEASE_MISMATCH');event(r,'dispatched',{attemptId,fence:r.fence,destination:r.destination});});emit('dispatched',r.attemptId);
      try{const result=await dispatcher.dispatch({attemptId,ticket,signal});if(result.kind==='unknown')port.markUnknown(reservation,{attemptId,fence:r.fence});return result;}
      catch(error){port.markUnknown(reservation,{attemptId,fence:r.fence,reason:'dispatch-interrupted'});throw error;}
    },
    allocationSummary(id){const a=get('mx_allocations',id),reservations=rows().filter(r=>matches(a,r)),usage=reservations.map(used);return {allocation:copy(a),attempts:usage.length,tokens:total(usage,'tokens').toString(),costMicros:total(usage,'costMicros').toString(),unknownCost:usage.filter(u=>u.costKind!=='observed').length,reservations:reservations.map(r=>r.id)};},
    runSummary(runId){const run=get('mx_runs',runId),children=rows().filter(r=>r.runId===runId),usage=children.map(used);return {run:copy(run),attempts:children.length,tokens:total(usage,'tokens').toString(),costMicros:total(usage,'costMicros').toString(),children:children.map(r=>({childId:r.childId,reservationId:r.id,attemptId:r.attemptId,state:inspect(r).state})),summaryDebit:0};},
  });
  return Object.freeze({port,authority,close(){db.close();}});
}
