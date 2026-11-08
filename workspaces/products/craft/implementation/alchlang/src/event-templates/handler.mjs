import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const config=JSON.parse(readFileSync(new URL('./config.json',import.meta.url),'utf8'));
const schema=`
CREATE TABLE IF NOT EXISTS state(operation TEXT,key TEXT,state TEXT,version INTEGER,PRIMARY KEY(operation,key));
CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY,body TEXT,commit_json TEXT,attempts INTEGER,status TEXT,available INTEGER,lease_owner TEXT,lease_until INTEGER);
CREATE TABLE IF NOT EXISTS inbox(operation TEXT,id TEXT,body TEXT,PRIMARY KEY(operation,id));
CREATE TABLE IF NOT EXISTS observations(id INTEGER PRIMARY KEY AUTOINCREMENT,data TEXT);
CREATE TABLE IF NOT EXISTS cardinality(key TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS accounting(id INTEGER PRIMARY KEY,offered INTEGER,rejected INTEGER);
INSERT OR IGNORE INTO accounting VALUES(1,0,0);`;
const error=code=>{throw Error(code)};
const canonical=v=>JSON.stringify(sort(v));
function sort(v){if(Array.isArray(v))return v.map(sort);if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,sort(v[k])]));return v}
const integer=n=>Number.isSafeInteger(n)&&n>=0;
const text=v=>typeof v==='string'&&v.length>0;
function safeJson(v){if(typeof v==='number'&&!Number.isSafeInteger(v))error('NUMBER_RANGE');if(v&&typeof v==='object')for(const x of Object.values(v))safeJson(x)}
const timestamp=v=>typeof v==='string'&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(v)&&Number.isFinite(Date.parse(v))&&new Date(v).toISOString()===v;
function expression(e,f){if(e.node)return e.node==='literal'?e.value:(f[e.ref]??null);const v=e.operands.map(x=>expression(x,f));switch(e.operator){case'eq':return canonical(v[0])===canonical(v[1]);case'neq':return canonical(v[0])!==canonical(v[1]);case'and':return v[0]===true&&v[1]===true;case'or':return v[0]===true||v[1]===true;case'not':return v[0]!==true;case'exists':return v[0]!==null;case'absent':return v[0]===null;default:error('FORMULA')}}
function validateFacts(f,subject){if(!f||Array.isArray(f)||typeof f!=='object')error('FACTS');const fields=config.model.facts.filter(x=>x.subject_ref===subject);if(Object.keys(f).some(k=>!fields.some(x=>x.id===k)))error('FACTS');for(const field of fields){const v=f[field.id];if(v===undefined){if(field.required)error('FACTS');continue}const valid=field.type==='integer'?Number.isSafeInteger(v):field.type==='boolean'?typeof v==='boolean':field.type==='record'?v!==null&&!Array.isArray(v)&&typeof v==='object':field.type==='timestamp'?timestamp(v):text(v);if(!valid)error('FACTS')}}
function mapping(id,f){const m=config.model.mappings.find(x=>x.id===id);return Object.fromEntries(m.clauses.map(c=>[c.target_field,c.source_field?f[c.source_field]:c.default_value.value]))}
function authorize(action,f,context){if(!context||!Array.isArray(context.grants)||!context.grants.includes(action.authority_boundary_ref))error('AUTHORITY_DENIED');if(action.actor_refs.length&&!action.actor_refs.includes(context.actor))error('ACTOR_DENIED');for(const id of action.precondition_rule_refs)if(expression(config.model.rules.find(r=>r.id===id).condition,f)!==true)error('RULE_DENIED');for(const id of action.permission_refs){const p=config.model.permissions.find(x=>x.id===id);if(!p.actor_refs.includes(context.actor)||expression(p.condition,f)!==true)error('PERMISSION_DENIED')}}

/** context comes from the trusted host adapter, never from an untrusted HTTP body. */
export function handler(request,context,{database=process.env.ALCH_EVENT_DATABASE,failpoint}={}){
 safeJson(request);
 if(!database)error('DATABASE_REQUIRED');if(!request||typeof request!=='object')error('REQUEST');
 if(request.command!=='invoke'&&!context?.transport_grants?.includes(config.transport))error('TRANSPORT_DENIED');
 const db=new DatabaseSync(database);try{
 db.exec('PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;');db.exec(schema);
 const r=request;
 const observe=(stage,message)=>{
  if(!config.observation.stages.includes(stage))return;
  db.prepare('UPDATE accounting SET offered=offered+1 WHERE id=1').run();
  const key=canonical([message.messageId,message.eventType,stage]);let count=Number(db.prepare('SELECT COUNT(*) n FROM cardinality').get().n);
  if(!db.prepare('SELECT 1 FROM cardinality WHERE key=?').get(key)){if(count>=config.observation.cardinalityBudget){db.prepare('UPDATE accounting SET rejected=rejected+1 WHERE id=1').run();return}db.prepare('INSERT INTO cardinality VALUES(?)').run(key);count++}
  const id=Number(db.prepare('SELECT COALESCE(MAX(id),0)+1 n FROM observations').get().n);
  const data={schema_version:'domainspec.orodi.observation/v1',observation_id:`event:${id}`,plane:'product',kind:'log',mode:'simulation',correlation_id:message.messageId,attributes:{'message-id':message.messageId,'event-type':message.eventType,stage},attribute_allowlist:config.observation.attributes,cardinality:{observed:count,budget:config.observation.cardinalityBudget},telemetry:{offered:1,queued:1,exported:0,rejected:0,dropped:0,pending:1,partial_success:0},deployment_effect:false,independently_observed:false,observed_at:r.at,invalidation_key_digest:config.binding_digest};
  db.prepare('INSERT INTO observations(id,data) VALUES(?,?)').run(id,canonical(data));
 };
 const snapshot=()=>({states:db.prepare('SELECT * FROM state ORDER BY operation,key').all().map(x=>({...x,state:JSON.parse(x.state)})),outbox:db.prepare('SELECT id,body,attempts,status,available,lease_owner,lease_until FROM outbox ORDER BY id').all().map(x=>({...x,body:JSON.parse(x.body)})),inbox:db.prepare('SELECT operation,id FROM inbox ORDER BY operation,id').all(),observations:db.prepare('SELECT data FROM observations ORDER BY id').all().map(x=>JSON.parse(x.data)),accounting:db.prepare('SELECT offered,rejected FROM accounting WHERE id=1').get()});
 if(r.command==='inspect')return snapshot();
 if(!integer(r.now)||!timestamp(r.at)||Date.parse(r.at)!==r.now)error('TIME');
 db.exec('BEGIN IMMEDIATE');let committed=false;let failedMessage;
 try{
 let result;
 if(r.command==='invoke'){
  const b=config.executions.find(x=>x.operation===r.operation);if(!b)error('OPERATION');const action=config.model.actions.find(x=>x.id===b.operation);
  const f=b.kind==='producer'?r.facts:r.message?.payload;validateFacts(f,action.subject_refs[0]);authorize(action,f,context);
  const key=f[b.key],id=f[b['message-id']];if(!text(key)||!text(id))error('IDENTITY');const state=mapping(b.state,f);
  if(b.kind==='producer'){
   if(!integer(r.expected_version))error('VERSION');const body={messageId:id,eventType:config.event,payload:mapping(b.payload,f),occurredAt:f[b.timestamp],aggregateType:action.subject_refs[0],aggregateId:key};
   const fingerprint=canonical({operation:b.operation,facts:f,expected_version:r.expected_version});const prior=db.prepare('SELECT commit_json FROM outbox WHERE id=?').get(id);
   if(prior){if(prior.commit_json!==fingerprint)error('MESSAGE_ID_CONFLICT');result={status:'already-committed',message_id:id}}
   else{
    const previous=db.prepare('SELECT version FROM state WHERE operation=? AND key=?').get(b.operation,key);if((previous?.version??0)!==r.expected_version)error('VERSION_CONFLICT');
    db.prepare('INSERT INTO state VALUES(?,?,?,?) ON CONFLICT(operation,key) DO UPDATE SET state=excluded.state,version=excluded.version').run(b.operation,key,canonical(state),r.expected_version+1);
    if(failpoint==='after-state')error('FAILPOINT');
    db.prepare('INSERT INTO outbox VALUES(?,?,?,0,\'pending\',?,NULL,NULL)').run(id,canonical(body),fingerprint,r.now);observe('outbox-committed',body);result={status:'committed',message_id:id};
   }
  }else{
   const m=r.message;if(m.eventType!==config.event||m.messageId!==id||m.aggregateId!==key||m.aggregateType!==action.subject_refs[0]||m.occurredAt!==f[b.timestamp])error('MESSAGE');
   const prior=db.prepare('SELECT body FROM inbox WHERE operation=? AND id=?').get(b.operation,id);if(prior&&prior.body!==canonical(m))error('MESSAGE_ID_CONFLICT');
   observe('consumer-received',m);
   if(prior){observe('consumer-duplicate',m);result={status:'duplicate',message_id:id}}
   else{
    failedMessage=m;
    db.prepare('INSERT INTO state VALUES(?,?,?,1) ON CONFLICT(operation,key) DO UPDATE SET state=excluded.state,version=state.version+1').run(b.operation,key,canonical(state));
    if(failpoint==='after-state')error('FAILPOINT');db.prepare('INSERT INTO inbox VALUES(?,?,?)').run(b.operation,id,canonical(m));observe('consumer-committed',m);result={status:'processed',message_id:id};
   }
  }
 }else if(r.command==='claim'){
  if(!text(r.worker))error('WORKER');const row=db.prepare("SELECT * FROM outbox WHERE (status='pending' AND available<=?) OR (status='leased' AND lease_until<=?) ORDER BY id LIMIT 1").get(r.now,r.now);
  if(!row)result={status:'empty'};else if(row.attempts>=config.max_attempts){db.prepare("UPDATE outbox SET status='dead',lease_owner=NULL,lease_until=NULL WHERE id=?").run(row.id);result={status:'dead',message_id:row.id}}
  else{const attempt=row.attempts+1;db.prepare("UPDATE outbox SET status='leased',attempts=?,lease_owner=?,lease_until=? WHERE id=?").run(attempt,r.worker,r.now+config.lease_ms,row.id);result={status:'leased',attempt,message:JSON.parse(row.body)}}
 }else if(r.command==='settle'){
  const row=db.prepare("SELECT * FROM outbox WHERE id=? AND status='leased' AND lease_owner=? AND attempts=? AND lease_until>?").get(r.message_id,r.worker,r.attempt,r.now);if(!row)error('LEASE');
  if(!['provider-accepted','unknown'].includes(r.outcome))error('OUTCOME');
  const accepted=r.outcome==='provider-accepted',status=accepted?'published':row.attempts>=config.max_attempts?'dead':'pending';
  const delay=Math.min(1000*2**Math.min(row.attempts-1,16),60000);db.prepare('UPDATE outbox SET status=?,available=?,lease_owner=NULL,lease_until=NULL WHERE id=?').run(status,accepted?r.now:r.now+delay,row.id);
  observe(accepted?'provider-accepted':'transport-unknown',JSON.parse(row.body));result={status,message_id:row.id};
 }else error('COMMAND');
 db.exec('COMMIT');committed=true;return result;
 }finally{if(!committed){
   db.exec('ROLLBACK');
   // Failure evidence is a separate transaction after business rollback.
   if(failedMessage){try{db.exec('BEGIN IMMEDIATE');observe('consumer-failed',failedMessage);db.exec('COMMIT')}catch{try{db.exec('ROLLBACK')}catch{}}}
 }}
 }finally{db.close()}
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 try{const bytes=readFileSync(0);if(bytes.length>1048576)error('INPUT_LIMIT');const input=JSON.parse(bytes);console.log(canonical(handler(input.request,input.context,{failpoint:process.env.ALCH_EVENT_TEST_FAILPOINT})));}
 catch(e){console.log(JSON.stringify({error:e.message}));process.exitCode=1}
}
