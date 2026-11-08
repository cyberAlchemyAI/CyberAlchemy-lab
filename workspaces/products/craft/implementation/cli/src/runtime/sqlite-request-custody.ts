import {evidenceJson,type CustodyReconciliation,type ReconciliationBinding,type ReconciliationAudit,type ReconciliationTarget} from './custody-reconciliation.js';
import {DatabaseSync} from 'node:sqlite';
import {createHmac,randomUUID,randomBytes,createCipheriv,createDecipheriv} from 'node:crypto';
import {openSync,closeSync,lstatSync,constants} from 'node:fs';
import {dirname,isAbsolute} from 'node:path';
import type {RequestCustody,RequestInspection,Reservation,ReservationRequest,ExecutionToken,LocalOutcome} from './request-custody.js';
// Explicit native custody backend. Open Questions: ../../REQUEST-CUSTODY.md.
function fail(code:string):never{throw Object.assign(Error(code),{code});}
export function openSqliteRequestCustody({path,key,policy,decisions,retentionMs=60000,maxEntries=128,maxBytes=65536,clock=Date.now,reconciliation}:any):RequestCustody&CustodyReconciliation&{inspectAll():RequestInspection[];close():void}{
 for(const n of [retentionMs,maxEntries,maxBytes])if(!Number.isSafeInteger(n)||n<1)fail('INVALID_LIMITS');
 if(!isAbsolute(path)||!Buffer.isBuffer(key)||key.length!==32||typeof policy!=='function')fail('CUSTODY_BINDING_REQUIRED');
 const recon:ReconciliationBinding|undefined=reconciliation?{operatorId:reconciliation.operatorId,authorize:reconciliation.authorize,resolveEvidence:reconciliation.resolveEvidence}:undefined;
 if(recon&&(typeof recon.operatorId!=='string'||!recon.operatorId||recon.operatorId.length>128||typeof recon.authorize!=='function'||typeof recon.resolveEvidence!=='function'))fail('RECONCILIATION_BINDING_REQUIRED');
 const privatePath=(p:string,dir=false)=>{const s=lstatSync(p);if(s.uid!==process.getuid!()||(s.mode&0o077)||s.isSymbolicLink()||!(dir?s.isDirectory():s.isFile()))fail('CUSTODY_PRIVATE_PATH');};
 privatePath(dirname(path),true);const fd=openSync(path,constants.O_CREAT|constants.O_RDWR|constants.O_NOFOLLOW,0o600);closeSync(fd);privatePath(path);
 const secret=Buffer.from(key);let db!:DatabaseSync;decisions=structuredClone(decisions);
 const config={retentionMs,maxEntries,maxBytes};
 const seal=(v:any)=>{const iv=randomBytes(12),c=createCipheriv('aes-256-gcm',secret,iv);c.setAAD(Buffer.from('request-custody/v1'));return Buffer.concat([iv,c.update(JSON.stringify(v)),c.final(),c.getAuthTag()]);};
 const unseal=(v:any)=>{const b=Buffer.from(v),c=createDecipheriv('aes-256-gcm',secret,b.subarray(0,12));c.setAAD(Buffer.from('request-custody/v1'));c.setAuthTag(b.subarray(-16));return JSON.parse(Buffer.concat([c.update(b.subarray(12,-16)),c.final()]).toString());};
 try{db=new DatabaseSync(path);db.exec('PRAGMA busy_timeout=1000; PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL; PRAGMA secure_delete=ON; BEGIN IMMEDIATE');
  const version=db.prepare('PRAGMA user_version').get()!.user_version;
  if(version===0){if(db.prepare("SELECT count(*) n FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").get()!.n)fail('CUSTODY_SCHEMA');db.exec('CREATE TABLE custody (id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, value BLOB NOT NULL); PRAGMA user_version=1');db.prepare('INSERT INTO custody VALUES(1,0,?)').run(seal({config,records:[]}));}else if(version!==1)fail('CUSTODY_SCHEMA');
  const data=unseal(db.prepare('SELECT value FROM custody WHERE id=1').get()!.value);if(JSON.stringify(data.config)!==JSON.stringify(config)||!Array.isArray(data.records))fail('CUSTODY_CONFIGURATION');db.exec('COMMIT');
 }catch{try{db!.exec('ROLLBACK');db!.close();}catch{}secret.fill(0);fail('CUSTODY_OPEN_FAILED');}
 type Row={request:ReservationRequest;token:ExecutionToken;attempt:any;outcome:LocalOutcome|null;transportSettled:boolean;finishedAt:number|null;reconciliation?:ReconciliationAudit};
 async function decide(input:any,signal:AbortSignal){let listener:()=>void=()=>{};const abort=new Promise<never>((_,reject)=>{listener=()=>reject(Object.assign(Error('CANCELLED'),{code:signal.reason==='deadline'?'DEADLINE_EXCEEDED':'CANCELLED'}));signal.addEventListener('abort',listener,{once:true});if(signal.aborted)listener();});try{return await Promise.race([Promise.resolve().then(()=>policy(input)),abort]);}finally{signal.removeEventListener('abort',listener);}}
 const read=()=>{const r=db.prepare('SELECT revision,value FROM custody WHERE id=1').get()!;return {revision:r.revision,data:unseal(r.value) as {config:any;records:Row[]}};};
 const prune=(data:{records:Row[]})=>{data.records=data.records.filter(r=>r.finishedAt===null||clock()-r.finishedAt<retentionMs);};
 function commit(revision:any,data:any,check=()=>{}){db.exec('BEGIN IMMEDIATE');try{check();if(db.prepare('SELECT revision FROM custody WHERE id=1').get()!.revision!==revision){db.exec('ROLLBACK');return false;}db.prepare('UPDATE custody SET revision=revision+1,value=? WHERE id=1').run(seal(data));db.exec('COMMIT');return true;}catch(e){db.exec('ROLLBACK');throw e;}}
 function mutate<T>(fn:(rows:Row[])=>T,check=()=>{}):T{for(let n=0;n<16;n++){const s=read();prune(s.data);const result=fn(s.data.records);if(commit(s.revision,s.data,check))return result;}return fail('REQUEST_STORE_BUSY');}
 const record=(rows:Row[],token:ExecutionToken)=>rows.find(r=>r.token===token)??fail('INVALID_EXECUTION_TOKEN');
 const finish=(r:Row)=>{if(r.finishedAt===null&&r.outcome&&r.transportSettled)r.finishedAt=clock();};
 const inspection=(r:Row):RequestInspection=>structuredClone({requestId:r.request.requestId,attempt:r.attempt,outcome:r.outcome?.kind??null,transportSettled:r.transportSettled,remoteCompletion:r.outcome?.kind==='json-completed'||r.outcome?.kind==='stream-completed'?'reported-complete':'unknown',usage:r.outcome&&'usage'in r.outcome?r.outcome.usage:null});

 const version=(r:Row)=>createHmac('sha256',secret).update(evidenceJson(r)).digest('hex');
 const target=(r:Row):ReconciliationTarget=>{const {key:_,...request}=r.request;return structuredClone({...request,attempt:r.attempt});};
 const review=(r:Row)=>({...inspection(r),version:version(r),reconciliation:structuredClone(r.reconciliation??null)});
 const find=(rows:Row[],input:any)=>rows.find(r=>r.request.requestId===input.requestId&&r.request.scope===input.scope)??fail('CUSTODY_NOT_FOUND');
 const validateCommand=(input:any,fields:string[])=>{if(!input||typeof input!=='object'||Array.isArray(input)||Object.keys(input).length!==fields.length||fields.some(k=>typeof input[k]!=='string'||!input[k]||Buffer.byteLength(input[k])>(k==='scope'?maxBytes:k==='evidenceRef'?512:128)))fail('INVALID_RECONCILIATION_COMMAND');};
 async function bounded<T>(control:any,fn:(c:any,wait:<V>(work:()=>Promise<V>)=>Promise<V>,check:()=>void)=>Promise<T>):Promise<T>{
  if(!control?.signal||!Number.isFinite(control.deadline))fail('INVALID_RECONCILIATION_CONTROL');
  const controller=new AbortController(),deadline=Math.min(control.deadline,clock()+30000),cancel=()=>controller.abort(control.signal.reason);
  control.signal.addEventListener('abort',cancel,{once:true});if(control.signal.aborted)cancel();
  const timer=setTimeout(()=>controller.abort('deadline'),Math.max(0,deadline-clock()));
  const check=()=>{if(controller.signal.aborted||clock()>=deadline)fail(controller.signal.reason==='deadline'||clock()>=deadline?'DEADLINE_EXCEEDED':'CANCELLED');};
  const c={signal:controller.signal,deadline};
  async function wait<V>(work:()=>Promise<V>):Promise<V>{check();let listener:()=>void=()=>{};const abort=new Promise<never>((_,reject)=>{listener=()=>reject(Object.assign(Error('RECONCILIATION_INTERRUPTED'),{code:controller.signal.reason==='deadline'?'DEADLINE_EXCEEDED':'CANCELLED'}));controller.signal.addEventListener('abort',listener,{once:true});});try{const value=await Promise.race([Promise.resolve().then(work),abort]);check();return value;}finally{controller.signal.removeEventListener('abort',listener);}}
  try{check();return await fn(c,wait,check);}finally{clearTimeout(timer);control.signal.removeEventListener('abort',cancel);}
 }
 let queued=0;
 return {
  async reserve(request,control):Promise<Reservation>{
   const req=structuredClone(request),check=()=>{if(control.signal.aborted)fail(control.signal.reason==='deadline'?'DEADLINE_EXCEEDED':'CANCELLED');if(clock()>=control.deadline)fail('DEADLINE_EXCEEDED');};check();
   if(['scope','requestId','fingerprintVersion','fingerprint'].some(k=>typeof (req as any)[k]!=='string'||!(req as any)[k])||typeof req.stream!=='boolean'||req.key!==null&&(typeof req.key!=='string'||!req.key||Buffer.byteLength(req.key)>128))fail('INVALID_RESERVATION');
   if(Buffer.byteLength(JSON.stringify(req))>maxBytes)fail('REQUEST_TOO_LARGE');if(queued>=maxEntries)return {kind:'reject',code:'REQUEST_STORE_BUSY'};queued++;
   try{for(let n=0;n<16;n++){
    check();const s=read();prune(s.data);const existing=req.key===null?undefined:s.data.records.find(r=>r.request.key===req.key&&r.request.scope===req.scope);
    const d=await decide({exists:!!existing,matches:!!existing&&existing.request.fingerprint===req.fingerprint&&existing.request.fingerprintVersion===req.fingerprintVersion,pending:!!existing&&existing.finishedAt===null,stream:existing?.request.stream??req.stream,succeeded:existing?.outcome?.kind==='json-completed'},control.signal);check();
    let result:Reservation;
    if(d?.status===decisions.replay){if(!existing||existing.finishedAt===null||existing.request.stream||existing.outcome?.kind!=='json-completed'||existing.request.fingerprint!==req.fingerprint||existing.request.fingerprintVersion!==req.fingerprintVersion)fail('INVALID_IDEMPOTENCY_DECISION');result={kind:'replay',requestId:existing.request.requestId,result:structuredClone(existing.outcome.result)};}
    else if(d?.status===decisions.execute){if(existing)fail('INVALID_IDEMPOTENCY_DECISION');if(s.data.records.length>=maxEntries)result={kind:'reject',code:'REQUEST_STORE_FULL'};else{if(s.data.records.some(r=>r.request.requestId===req.requestId))fail('DUPLICATE_REQUEST_ID');const token=randomUUID() as ExecutionToken;s.data.records.push({request:req,token,attempt:null,outcome:null,transportSettled:false,finishedAt:null});result={kind:'execute',requestId:req.requestId,token};}}
    else{if(!Object.hasOwn(decisions.reject,d?.status))fail('INVALID_IDEMPOTENCY_DECISION');result={kind:'reject',code:decisions.reject[d.status],...(existing?{requestId:existing.request.requestId}:{})};}
    if(commit(s.revision,s.data,check))return result;
   }return {kind:'reject',code:'REQUEST_STORE_BUSY'};}finally{queued--;}
  },
  async beginAttempt(token,binding){mutate(rows=>{const r=record(rows,token);if(r.reconciliation)fail('EXECUTION_FENCED');if(r.attempt||r.outcome||r.transportSettled)fail('ATTEMPT_NOT_ALLOWED');if(['id','version','model','policyVersion'].some(k=>typeof (binding as any)[k]!=='string'||!(binding as any)[k]||Buffer.byteLength((binding as any)[k])>128))fail('INVALID_ATTEMPT');r.attempt={id:binding.id,version:binding.version,model:binding.model,policyVersion:binding.policyVersion};});},
  async recordOutcome(token,outcome){mutate(rows=>{const r=record(rows,token);if(r.reconciliation)fail('EXECUTION_FENCED');if(r.outcome)fail('OUTCOME_ALREADY_RECORDED');if(!['json-completed','stream-completed','failed','cancelled'].includes(outcome.kind)||outcome.kind==='json-completed'&&r.request.stream||outcome.kind==='stream-completed'&&!r.request.stream||(outcome.kind==='json-completed'||outcome.kind==='stream-completed')&&!r.attempt)fail('INVALID_OUTCOME');if(Buffer.byteLength(JSON.stringify(outcome))>maxBytes)fail('RESULT_TOO_LARGE');r.outcome=structuredClone(outcome);finish(r);});},
  async markTransportSettled(token){mutate(rows=>{const r=record(rows,token);if(r.reconciliation)fail('EXECUTION_FENCED');r.transportSettled=true;finish(r);});},
  async inspect(id){return mutate(rows=>{const r=rows.find(r=>r.request.requestId===id);return r?inspection(r):null;});},
  inspectAll(){return mutate(rows=>rows.map(inspection));},
  async review(input,control){
   validateCommand(input,['requestId','scope']);if(!recon)fail('RECONCILIATION_BINDING_REQUIRED');const command=structuredClone(input);
   return bounded(control,async(c,wait,check)=>{if(await wait(()=>recon.authorize({...command,operatorId:recon.operatorId,action:'custody.review'},c))!==true)fail('FORBIDDEN');check();const snapshot=read();prune(snapshot.data);check();return review(find(snapshot.data.records,command));});
  },
  async reconcile(input,control){
   validateCommand(input,['requestId','scope','version','evidenceRef']);if(!recon)fail('RECONCILIATION_BINDING_REQUIRED');const command=structuredClone(input);
   return bounded(control,async(c,wait,check)=>{
    const authorize=()=>recon.authorize({requestId:command.requestId,scope:command.scope,operatorId:recon.operatorId,action:'custody.reconcile'},c);
    if(await wait(authorize)!==true)fail('FORBIDDEN');
    const snapshot=read();prune(snapshot.data);const old=find(snapshot.data.records,command);
    if(version(old)!==command.version||old.reconciliation||old.finishedAt!==null)fail('RECONCILIATION_STALE');
    const expected=target(old),proof=structuredClone(await wait(()=>recon.resolveEvidence(command.evidenceRef,structuredClone(expected),c)));
    if(!proof||Object.keys(proof).sort().join(',')!=='evidenceRef,outcome,target,transportSettled'||proof.evidenceRef!==command.evidenceRef||proof.transportSettled!==true||evidenceJson(proof.target)!==evidenceJson(expected))fail('INVALID_RECONCILIATION_EVIDENCE');
    const outcome=proof.outcome;
    if(!outcome||!['json-completed','stream-completed','failed','cancelled'].includes(outcome.kind))fail('INVALID_RECONCILIATION_EVIDENCE');
    const fields=outcome.kind==='json-completed'?'kind,result,usage':outcome.kind==='stream-completed'?'kind,usage':'code,kind';
    if(Object.keys(outcome).sort().join(',')!==fields||Buffer.byteLength(evidenceJson(outcome))>maxBytes)fail('INVALID_RECONCILIATION_EVIDENCE');
    if(outcome.kind==='json-completed'&&(old.request.stream||!old.attempt||(outcome.result as any)?.model!==old.attempt.model)||outcome.kind==='stream-completed'&&(!old.request.stream||!old.attempt)||'code'in outcome&&(typeof outcome.code!=='string'||!outcome.code||Buffer.byteLength(outcome.code)>128))fail('INVALID_RECONCILIATION_EVIDENCE');
    if(old.outcome&&evidenceJson(old.outcome)!==evidenceJson(outcome))fail('OUTCOME_ALREADY_RECORDED');
    if(await wait(authorize)!==true)fail('FORBIDDEN');
    return mutate(rows=>{check();const current=find(rows,command);if(version(current)!==command.version||current.reconciliation||current.finishedAt!==null)fail('RECONCILIATION_STALE');current.outcome=outcome;current.transportSettled=true;current.reconciliation={operatorId:recon.operatorId,evidenceRef:command.evidenceRef,at:clock(),outcome:outcome.kind};finish(current);return review(current);},check);
   });
  },
  close(){db.close();secret.fill(0);}
 };
}
