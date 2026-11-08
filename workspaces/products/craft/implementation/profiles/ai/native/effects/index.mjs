import {DatabaseSync} from 'node:sqlite';
import {randomUUID} from 'node:crypto';
import {DurableWriteIntentStore} from '@domainspec-v2/cli/generic';
import {canonical,digest} from '../source-release/index.mjs';
import {freeze} from '../shared.mjs';

export const EFFECTS_ABI='effects-dispatch/v1';
const fail=code=>{throw new Error(code);};
const text=v=>typeof v==='string'&&v.length>0&&v.length<=2048||fail('EFFECT_IDENTITY');
const uint=v=>Number.isSafeInteger(v)&&v>=0||fail('EFFECT_INTEGER');
const finiteKinds=new Set(['local','model','document','index','provider']);
const copy=v=>JSON.parse(canonical(v));

/** Selected adapters are trusted technical code. They receive owned exact bytes,
 * never arbitrary caller callbacks, SQL, shell commands or plugin names. One
 * durable original C11 journal owns dispatch retirement; adjunct rows describe
 * the new selected-provider attempts and immutable native observations.
 * Open Questions: README.md. */
export function createEffectDispatcher({path,slots,releasePort,assertCurrent,observer,now=Date.now,policy={}}) {
  text(path);if(typeof assertCurrent!=='function'||!Array.isArray(slots)||!slots.length||slots.length>64)fail('EFFECT_CONFIGURATION');
  const selected=new Map();
  for(const s of slots) {
    for(const k of ['id','provider','account','operation','resourceId','action'])text(s[k]);
    if(!finiteKinds.has(s.kind)||selected.has(s.id)||typeof s.execute!=='function'||typeof s.validateObservation!=='function')fail('EFFECT_SLOT');
    selected.set(s.id,Object.freeze({...s}));
  }
  const limits={maxAttempts:3,maxInspections:8,maxInspectionConcurrency:2,inspectionTimeoutMs:30000,maxConcurrency:2,rateLimit:60,rateWindowMs:60000,circuitFailures:3,circuitCooldownMs:30000,timeoutMs:30000,backoffMs:0,allowAlternateAfterNoEffect:false,...policy};
  for(const k of ['maxAttempts','maxInspections','maxInspectionConcurrency','inspectionTimeoutMs','maxConcurrency','rateLimit','rateWindowMs','circuitFailures','circuitCooldownMs','timeoutMs'])if(!Number.isSafeInteger(limits[k])||limits[k]<1||limits[k]>86400000)fail('EFFECT_POLICY');
  uint(limits.backoffMs);if(limits.timeoutMs>300000||limits.inspectionTimeoutMs>300000||limits.maxInspections>1024||typeof limits.allowAlternateAfterNoEffect!=='boolean')fail('EFFECT_POLICY');
  const db=new DatabaseSync(path);db.exec('PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;');
  const journal=new DurableWriteIntentStore(db);
  db.exec(`CREATE TABLE IF NOT EXISTS fx_intents(id TEXT PRIMARY KEY, body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS fx_attempts(id TEXT PRIMARY KEY,intent TEXT NOT NULL,slot TEXT NOT NULL,effect TEXT NOT NULL UNIQUE,created INTEGER NOT NULL,body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS fx_dispatch(id TEXT PRIMARY KEY,started INTEGER NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS fx_observations(id INTEGER PRIMARY KEY,attempt TEXT NOT NULL,kind TEXT NOT NULL CHECK(kind IN ('confirmed','no-effect','unknown')),at INTEGER NOT NULL,body TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS fx_retired(slot TEXT PRIMARY KEY,reason TEXT NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS fx_retry_plans(id INTEGER PRIMARY KEY,attempt TEXT NOT NULL,not_before INTEGER NOT NULL,deadline INTEGER NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS fx_inspections(id TEXT PRIMARY KEY,attempt TEXT NOT NULL,intent TEXT NOT NULL,started INTEGER NOT NULL,deadline INTEGER NOT NULL) STRICT;
    CREATE TABLE IF NOT EXISTS fx_inspection_results(id TEXT PRIMARY KEY,finished INTEGER NOT NULL,body TEXT NOT NULL) STRICT;`);
  for(const table of ['fx_intents','fx_attempts','fx_dispatch','fx_observations','fx_inspections','fx_inspection_results','fx_retry_plans'])db.exec(`CREATE TRIGGER IF NOT EXISTS ${table}_no_update BEFORE UPDATE ON ${table} BEGIN SELECT RAISE(ABORT,'IMMUTABLE_EFFECT'); END;
    CREATE TRIGGER IF NOT EXISTS ${table}_no_delete BEFORE DELETE ON ${table} BEGIN SELECT RAISE(ABORT,'IMMUTABLE_EFFECT'); END;`);
  const permits=new Map(),active=new Set(),activeInspections=new Set();
  const emit=(transition,id,code)=>{if(!observer)return;try{const event={category:'provider',transition,correlation_id:id,...(code?{code}:{})};const result=typeof observer==='function'?observer(event):observer.emit(event);if(result&&typeof result.catch==='function')result.catch(()=>{});}catch{}};
  const tx=fn=>{db.exec('BEGIN IMMEDIATE');try{const r=fn();db.exec('COMMIT');return r;}catch(e){if(db.isTransaction)db.exec('ROLLBACK');throw e;}};
  function attempt(id){text(id);const row=db.prepare('SELECT body FROM fx_attempts WHERE id=?').get(id);if(!row)fail('ATTEMPT_MISSING');return JSON.parse(row.body);}
  function observation(id){const r=db.prepare('SELECT body FROM fx_observations WHERE attempt=? ORDER BY id DESC LIMIT 1').get(id);return r?JSON.parse(r.body):null;}
  function input(a){const effect=canonical({abi:EFFECTS_ABI,intentId:a.intentId,attemptId:a.id,cause:a.cause});const payload=canonical({sha256:a.payloadSha256});const binding=canonical(a.binding);
    return {effect_canonical_json:effect,effect_sha256:digest(effect),payload_canonical_json:payload,payload_sha256:digest(payload),binding_canonical_json:binding,binding_sha256:digest(binding),request_bytes:Buffer.from(a.payloadBase64,'base64')};}
  function fresh(a){const value=assertCurrent(Object.freeze(copy(a.binding)));if(value&&typeof value.then==='function')fail('ASYNC_FENCE_CHECK');if(value!==true)fail('STALE_EFFECT_AUTHORITY');if(now()>=a.deadlineAt)fail('EFFECT_DEADLINE');}
  function immutableObservation(a,o){
    const prev=observation(a.id);if(prev&&prev.kind!=='unknown'){if(canonical(prev)!==canonical(o))fail('DEFINITE_OBSERVATION_CONFLICT');return prev;}
    db.prepare('INSERT INTO fx_observations(attempt,kind,at,body) VALUES(?,?,?,?)').run(a.id,o.kind,now(),canonical(o));return copy(o);
  }
  function slotFor(a){const s=selected.get(a.slotId);if(!s||canonical({provider:s.provider,account:s.account,operation:s.operation,resourceId:s.resourceId,action:s.action,kind:s.kind})!==canonical(a.selection))fail('ORIGINAL_PROVIDER_REQUIRED');return s;}
  function requestIdentity(request,{allowExpired=false}={}){
    const {intentId,slotId,tenant,principal,resourceId,action,approvalRevision,sourceRevision,fence,payload,deadlineAt,cause,retryOf}=request;
    for(const v of [intentId,slotId,tenant,principal,resourceId,action,approvalRevision,sourceRevision])text(v);uint(fence);
    if(!(payload instanceof Uint8Array)||payload.byteLength>1048576||!Number.isSafeInteger(deadlineAt)||!allowExpired&&deadlineAt<=now())fail('EFFECT_BOUND');canonical(cause);
    const slot=selected.get(slotId);if(!slot||slot.resourceId!==resourceId||slot.action!==action)fail('UNSUPPORTED_EFFECT_SLOT');
    const payloadSha256=digest(payload),binding={tenant,principal,resourceId,action,approvalRevision,sourceRevision,fence},selection={provider:slot.provider,account:slot.account,operation:slot.operation,resourceId,action,kind:slot.kind};
    return {intentId,slotId,tenant,principal,resourceId,action,approvalRevision,sourceRevision,fence,payload,deadlineAt,cause,retryOf,slot,binding,selection,payloadSha256,business:canonical({intentId,tenant,principal,resourceId,action,cause,payloadSha256})};
  }
  function capacity(a){
    const rows=db.prepare('SELECT a.body,d.started FROM fx_attempts a JOIN fx_dispatch d ON d.id=a.id').all()
      .filter(r=>{const s=JSON.parse(r.body).selection;return s.provider===a.selection.provider&&s.account===a.selection.account&&s.operation===a.selection.operation;});
    const recent=rows.filter(r=>r.started>now()-limits.rateWindowMs);
    if(recent.length>=limits.rateLimit)fail('EFFECT_RATE_LIMIT');
    const pending=rows.filter(r=>{const o=observation(JSON.parse(r.body).id);return !o||o.kind==='unknown';});
    if(pending.length>=limits.maxConcurrency)fail('EFFECT_CONCURRENCY_LIMIT');
    const latest=rows.sort((a,b)=>b.started-a.started).slice(0,limits.circuitFailures);
    if(latest.length===limits.circuitFailures&&latest.every(r=>observation(JSON.parse(r.body).id)?.kind==='unknown')&&now()<latest[0].started+limits.circuitCooldownMs)fail('EFFECT_CIRCUIT_OPEN');
  }
  async function invoke(a,s,method,signal){
    const controller=new AbortController();const onAbort=()=>controller.abort();if(signal?.aborted)return {kind:'unknown',reason:'cancelled'};
    signal?.addEventListener('abort',onAbort,{once:true});let timer,abort;
    try{
      const result=await Promise.race([
        Promise.resolve().then(()=>s[method](Object.freeze({attemptId:a.id,intentId:a.intentId,selection:Object.freeze(copy(a.selection)),binding:Object.freeze(copy(a.binding)),payload:Buffer.from(a.payloadBase64,'base64'),signal:controller.signal,deadlineAt:a.deadlineAt}))),
        new Promise(resolve=>{timer=setTimeout(()=>{controller.abort();resolve({kind:'unknown',reason:'timeout'});},Math.max(1,Math.min(method==='inspect'?limits.inspectionTimeoutMs:limits.timeoutMs,a.deadlineAt-now())));}),
        new Promise(resolve=>{abort=()=>resolve({kind:'unknown',reason:'cancelled'});controller.signal.addEventListener('abort',abort,{once:true});}),
      ]);
      if(!result||!['confirmed','no-effect','unknown'].includes(result.kind))return {kind:'unknown',reason:'malformed-observation'};
      if(result.kind!=='unknown'&&s.validateObservation(result,Object.freeze(copy(a)))!==true)return {kind:'unknown',reason:'unverified-observation'};
      canonical(result);return copy(result);
    }catch{return {kind:'unknown',reason:'transport'};}
    finally{clearTimeout(timer);signal?.removeEventListener('abort',onAbort);controller.signal.removeEventListener('abort',abort);}
  }
  function retryState({attemptId,deadlineAt,binding:currentBinding}){
    const a=attempt(attemptId);slotFor(a);const binding=currentBinding===undefined?a.binding:copy(currentBinding);if(canonical(Object.keys(binding).sort())!==canonical(Object.keys(a.binding).sort())||canonical({...binding,fence:a.binding.fence})!==canonical(a.binding)||!Number.isSafeInteger(binding.fence)||binding.fence<0)fail('IMMUTABLE_RETRY_SCOPE');const authority=assertCurrent(Object.freeze(copy(binding)));if(authority&&typeof authority.then==='function')fail('ASYNC_FENCE_CHECK');if(authority!==true)fail('STALE_EFFECT_AUTHORITY');
    const history=db.prepare('SELECT body FROM fx_attempts WHERE intent=? ORDER BY created,rowid').all(a.intentId).map(r=>JSON.parse(r.body)),root=history[0],latest=history.at(-1),o=observation(a.id),sendsUsed=db.prepare('SELECT count(*) AS n FROM fx_dispatch d JOIN fx_attempts a ON a.id=d.id WHERE a.intent=?').get(a.intentId).n;
    const requestedDeadline=deadlineAt===undefined?root.deadlineAt:deadlineAt;if(!Number.isSafeInteger(requestedDeadline)||requestedDeadline>root.deadlineAt)fail('ORIGINAL_DEADLINE_REQUIRED');const planned=db.prepare('SELECT MAX(not_before) AS notBefore,MIN(deadline) AS deadline FROM fx_retry_plans WHERE attempt=?').get(a.id),deadline=Math.min(requestedDeadline,db.prepare('SELECT MIN(p.deadline) AS deadline FROM fx_retry_plans p JOIN fx_attempts a ON p.attempt=a.id WHERE a.intent=?').get(a.intentId).deadline??requestedDeadline);
    const base={attemptId:a.id,retryOf:a.id,intentId:a.intentId,deadlineAt:deadline,attemptsUsed:history.length,sendsUsed};
    if(db.prepare('SELECT slot FROM fx_retired WHERE slot=?').get(a.slotId))return {...base,kind:'blocked',reason:'provider-retired'};
    const blocked=reason=>({...base,kind:'blocked',reason});
    if(latest.id!==a.id)return blocked('not-latest-attempt');if(o?.kind!=='no-effect')return blocked(o?.kind==='confirmed'?'already-confirmed':'inspection-required');
    if(!root.policy)return blocked('legacy-policy-unverified');
    if(o.retryable===false)return blocked('terminal-no-effect');if(o.retryable!==undefined&&typeof o.retryable!=='boolean')return blocked('retryability-unavailable');
    const maxAttempts=Math.min(limits.maxAttempts,root.policy?.maxAttempts??limits.maxAttempts);if(history.length>=maxAttempts)return blocked('attempt-budget');
    const providerDelay=o.retryAfterMs??0;if(!Number.isSafeInteger(providerDelay)||providerDelay<0)return blocked('provider-delay-unavailable');
    const lastTime=db.prepare('SELECT at FROM fx_observations WHERE attempt=? ORDER BY id DESC LIMIT 1').get(a.id).at,delay=Math.max(limits.backoffMs,root.policy?.backoffMs??limits.backoffMs,providerDelay),notBefore=Math.max(lastTime+delay,planned.notBefore??0);
    if(!Number.isSafeInteger(notBefore))return blocked('provider-delay-unrepresentable');if(notBefore>=deadline||now()>=deadline)return {...blocked('deadline-exhausted'),notBefore};
    return {...base,kind:now()<notBefore?'waiting':'due',notBefore};
  }
  const port=Object.freeze({
    abi:EFFECTS_ABI,
    prepare(request){
      const identity=requestIdentity(request),{intentId,slotId,payload,deadlineAt,cause,retryOf,business,binding,selection,payloadSha256}=identity;
      if(db.prepare('SELECT slot FROM fx_retired WHERE slot=?').get(slotId))fail('PROVIDER_RETIRED');
      const old=db.prepare('SELECT body FROM fx_intents WHERE id=?').get(intentId);if(old&&old.body!==business)fail('LOGICAL_INTENT_CONFLICT');
      const previous=db.prepare('SELECT body FROM fx_attempts WHERE intent=? ORDER BY created,rowid').all(intentId).map(r=>JSON.parse(r.body));
      if(previous.length){const last=previous.at(-1),o=observation(last.id);if(!retryOf)return {kind:'existing',...port.getAttempt(last.id)};
        if(retryOf!==last.id||o?.kind!=='no-effect')fail('INSPECTION_REQUIRED');if(previous.length>=limits.maxAttempts)fail('ATTEMPT_BUDGET');
        if(slotId!==last.slotId&&!limits.allowAlternateAfterNoEffect)fail('ALTERNATE_PROVIDER_DENIED');
        const status=retryState({attemptId:last.id,deadlineAt,binding});if(deadlineAt>status.deadlineAt)fail('ORIGINAL_DEADLINE_REQUIRED');if(status.kind==='waiting')fail('EFFECT_BACKOFF');if(status.kind!=='due')fail(status.reason==='deadline-exhausted'?'EFFECT_DEADLINE':status.reason==='attempt-budget'?'ATTEMPT_BUDGET':'RETRY_NOT_ADMITTED');}
      const rootPolicy=previous[0]?.policy??{maxAttempts:limits.maxAttempts,maxInspections:limits.maxInspections,backoffMs:limits.backoffMs};
      const id=randomUUID();const a={id,intentId,slotId,cause:copy(cause),selection,binding,payloadSha256,payloadBase64:Buffer.from(payload).toString('base64'),deadlineAt,policy:copy(rootPolicy)};
      fresh(a);const journalInput=input(a);const prepared=journal.prepare(journalInput);if(prepared.kind!=='new')fail('ATTEMPT_IDENTITY_COLLISION');
      tx(()=>{const existing=db.prepare('SELECT body FROM fx_intents WHERE id=?').get(intentId);if(existing&&existing.body!==business)fail('LOGICAL_INTENT_CONFLICT');
        const count=db.prepare('SELECT count(*) AS n FROM fx_attempts WHERE intent=?').get(intentId).n;if(count!==previous.length)fail('CONCURRENT_ATTEMPT');
        db.prepare('INSERT OR IGNORE INTO fx_intents VALUES(?,?)').run(intentId,business);db.prepare('INSERT INTO fx_attempts VALUES(?,?,?,?,?,?)').run(id,intentId,slotId,journalInput.effect_sha256,now(),canonical(a));});
      permits.set(id,prepared.dispatch);emit('prepared',id);return {kind:'prepared',attemptId:id,state:'prepared'};
    },
    retryStatus(request){return freeze(retryState(request));},
    scheduleRetry(request){if(request.notBefore===undefined)return freeze(retryState(request));return tx(()=>{const status=retryState(request);if(!['due','waiting'].includes(status.kind))return freeze(status);if(!Number.isSafeInteger(request.notBefore)||request.notBefore<status.notBefore||request.notBefore>=status.deadlineAt)fail('RETRY_PLAN_BOUND');db.prepare('INSERT INTO fx_retry_plans(attempt,not_before,deadline) VALUES(?,?,?)').run(request.attemptId,request.notBefore,status.deadlineAt);return freeze(retryState(request));});},
    async dispatch({attemptId,ticket,signal}) {
      const a=attempt(attemptId),s=slotFor(a);fresh(a);if(signal?.aborted)fail('EFFECT_CANCELLED_BEFORE_DISPATCH');
      const permit=permits.get(attemptId);if(!permit)fail('ORIGINAL_DISPATCH_CUSTODY_REQUIRED');
      tx(()=>{if(db.prepare('SELECT slot FROM fx_retired WHERE slot=?').get(a.slotId))fail('PROVIDER_RETIRED');
        if(['confirmed','no-effect'].includes(observation(a.id)?.kind))fail('ATTEMPT_ALREADY_DEFINITE');
        if(db.prepare('SELECT id FROM fx_dispatch WHERE id=?').get(attemptId))fail('ALREADY_DISPATCHED');fresh(a);capacity(a);db.prepare('INSERT INTO fx_dispatch VALUES(?,?)').run(attemptId,now());});
      // Retire the original journal permit before consuming disclosure. A crash
      // at either boundary requires original-provider inspection, never resend.
      const i=input(a),custody=journal.markDispatched(permit);permits.delete(attemptId);journal.assertDispatchCurrent(custody,i);emit('dispatched',a.id);
      try{
        if(s.requiresRelease!==false){if(!releasePort)fail('SOURCE_RELEASE_REQUIRED');releasePort.consumeRelease(ticket,{...a.binding,attemptId:a.id,sink:s.sink??s.provider,recipient:s.recipient??s.account,payload:Buffer.from(a.payloadBase64,'base64')});}
        fresh(a);
      }catch(e){journal.retainUnknown(i);immutableObservation(a,{kind:'no-effect',reason:'not-invoked',detail:e.message});emit('denied',a.id,'PermissionDenied');throw e;}
      active.add(a.id);
      let o=await invoke(a,s,'execute',signal);
      try{fresh(a);}catch{o={kind:'unknown',reason:'stale-fence-or-deadline-at-commit'};}
      try{const result=tx(()=>{journal.assertLedgerCurrent();return immutableObservation(a,o);});emit(o.kind==='unknown'?'unknown':'returned',a.id);return result;}
      finally{active.delete(a.id);if(o.kind==='unknown')journal.retainUnknown(i);}
    },
    getAttempt(id){const a=attempt(id),o=observation(id),dispatched=!!db.prepare('SELECT id FROM fx_dispatch WHERE id=?').get(id),view={attemptId:a.id,intentId:a.intentId,slotId:a.slotId,selection:copy(a.selection),binding:copy(a.binding),payloadSha256:a.payloadSha256,state:o?.kind??(dispatched?'unknown':'prepared'),observation:o};
      // Historical inspection may compare this original cause, but cannot
      // reinterpret or replace it. It conveys no dispatch/retry authority.
      Object.defineProperty(view,'cause',{value:freeze(copy(a.cause)),enumerable:true});return view;},
    inspectIntent(intentId,expected){
      text(intentId);const identity=expected===undefined?null:requestIdentity(expected,{allowExpired:true});if(identity&&identity.intentId!==intentId)fail('LOGICAL_INTENT_CONFLICT');
      const original=db.prepare('SELECT body FROM fx_intents WHERE id=?').get(intentId);if(!original)return null;if(identity&&original.body!==identity.business)fail('LOGICAL_INTENT_CONFLICT');
      const found=db.prepare('SELECT body FROM fx_attempts WHERE intent=? ORDER BY created DESC,rowid DESC LIMIT 1').get(intentId);if(!found)fail('OWNED_INTENT_ATTEMPT_MISSING');const a=JSON.parse(found.body);slotFor(a);
      if(identity&&(a.slotId!==identity.slotId||canonical(a.binding)!==canonical(identity.binding)||canonical(a.selection)!==canonical(identity.selection)||canonical(a.cause)!==canonical(identity.cause)||a.payloadSha256!==identity.payloadSha256||!Buffer.from(a.payloadBase64,'base64').equals(Buffer.from(identity.payload))))fail('IMMUTABLE_ATTEMPT_CONFLICT');
      const authority=assertCurrent(Object.freeze(copy(a.binding)));if(authority&&typeof authority.then==='function')fail('ASYNC_FENCE_CHECK');if(authority!==true)fail('STALE_EFFECT_AUTHORITY');
      if(!journal.inspect(input(a)))fail('ORIGINAL_INTENT_JOURNAL_MISSING');return port.getAttempt(a.id);
    },
    async inspect({attemptId,signal,deadlineAt}) {
      if(deadlineAt!==undefined&&!Number.isSafeInteger(deadlineAt))fail('EFFECT_INSPECTION_DEADLINE');
      const a=attempt(attemptId),s=slotFor(a),o=observation(attemptId),deadline=deadlineAt===undefined?now()+limits.inspectionTimeoutMs:Math.min(deadlineAt,now()+limits.inspectionTimeoutMs);
      if(!Number.isSafeInteger(deadline)||deadline<=now())fail('EFFECT_INSPECTION_DEADLINE');fresh({...a,deadlineAt:deadline});if(signal?.aborted)fail('EFFECT_CANCELLED_BEFORE_INSPECTION');
      if(o&&o.kind!=='unknown')return copy(o);
      if(active.has(attemptId)||activeInspections.has(attemptId))fail('ATTEMPT_IN_FLIGHT');if(typeof s.inspect!=='function')fail('ORIGINAL_PROVIDER_INSPECTION_UNAVAILABLE');
      const inspectionId=randomUUID();
      tx(()=>{
        const root=JSON.parse(db.prepare('SELECT body FROM fx_attempts WHERE intent=? ORDER BY created,rowid LIMIT 1').get(a.intentId).body),used=db.prepare('SELECT count(*) AS n FROM fx_inspections WHERE intent=?').get(a.intentId).n;
        if(used>=Math.min(limits.maxInspections,root.policy?.maxInspections??limits.maxInspections))fail('INSPECTION_BUDGET');
        const pending=db.prepare('SELECT i.attempt FROM fx_inspections i LEFT JOIN fx_inspection_results r ON i.id=r.id WHERE r.id IS NULL AND i.deadline>?').all(now()).map(r=>attempt(r.attempt)).filter(p=>p.selection.provider===a.selection.provider&&p.selection.account===a.selection.account&&p.selection.operation===a.selection.operation);
        if(pending.some(p=>p.id===a.id)||pending.length>=limits.maxInspectionConcurrency)fail('INSPECTION_CONCURRENCY_LIMIT');
        fresh({...a,deadlineAt:deadline});db.prepare('INSERT INTO fx_inspections VALUES(?,?,?,?,?)').run(inspectionId,a.id,a.intentId,now(),deadline);
      });
      activeInspections.add(a.id);
      try{
        // Recovery is a separately bounded inspection lifecycle, never a repeat
        // mutation. The original exact bytes/account/attempt stay unchanged.
        const result=await invoke({...a,deadlineAt:deadline},s,'inspect',signal);
        let admitted=result;try{fresh({...a,deadlineAt:deadline});}catch{admitted={kind:'unknown',reason:'stale-fence-at-inspection-commit'};}
        const value=tx(()=>{const out=immutableObservation(a,admitted);db.prepare('INSERT INTO fx_inspection_results VALUES(?,?,?)').run(inspectionId,now(),canonical(out));return out;});
        if(value.kind==='unknown'){const i=input(a);if(journal.inspect(i)?.state==='dispatched')journal.retainUnknown(i);}emit(value.kind==='unknown'?'unknown':'reconciled',a.id);return value;
      }finally{activeInspections.delete(a.id);}
    },
    reconcile(request){return port.inspect(request);},
    retireProvider({slotId,reviewReason}) {text(slotId);if(!selected.has(slotId))fail('UNSUPPORTED_EFFECT_SLOT');const unresolved=db.prepare('SELECT id FROM fx_attempts WHERE slot=?').all(slotId).filter(r=>!['confirmed','no-effect'].includes(observation(r.id)?.kind));
      if(unresolved.length&&!reviewReason)fail('UNRESOLVED_PROVIDER_REQUIRES_INSPECTION_OR_REVIEW');if(reviewReason)text(reviewReason);db.prepare('INSERT OR REPLACE INTO fx_retired VALUES(?,?)').run(slotId,reviewReason??'no unresolved attempts');return {unresolved:unresolved.map(r=>r.id),inspectionRetained:true};},
  });
  return Object.freeze({...port,close(){if(active.size||activeInspections.size)fail('EFFECTS_IN_FLIGHT');db.close();}});
}
