use rusqlite::{Connection,params,ToSql,types::ValueRef};
use serde_json::{Value as V,json};
use chrono::{DateTime,SecondsFormat};
type R<T> = Result<T,String>;
macro_rules! need {($c:expr,$e:expr)=>{if !$c{return Err($e.into())}};}
fn s(v:&V)->&str{v.as_str().unwrap_or("")}
fn n(v:&V)->i64{v.as_i64().unwrap_or(-1)}
fn integer(v:&V)->bool{v.as_i64().map(|x|x>=0&&x<=9007199254740991).unwrap_or(false)}
fn arr(v:&V)->Vec<V>{v.as_array().cloned().unwrap_or_default()}
fn contains(v:&V,x:&V)->bool{arr(v).contains(x)}
fn canonical(v:&V)->String{serde_json::to_string(v).unwrap()}
fn timestamp(v:&V)->Option<i64>{let d=DateTime::parse_from_rfc3339(s(v)).ok()?;if d.to_rfc3339_opts(SecondsFormat::Millis,true)!=s(v){return None}Some(d.timestamp_millis())}
fn sql(db:&Connection,q:&str,p:&[&dyn ToSql])->R<usize>{db.execute(q,p).map_err(|e|e.to_string())}
fn rows(db:&Connection,q:&str,p:&[&dyn ToSql])->R<Vec<V>>{let mut stmt=db.prepare(q).map_err(|e|e.to_string())?;let names=stmt.column_names().iter().map(|s|s.to_string()).collect::<Vec<_>>();let mapped=stmt.query_map(p,|row|{let mut value=serde_json::Map::new();for (i,name) in names.iter().enumerate(){let v=match row.get_ref(i)?{ValueRef::Null=>V::Null,ValueRef::Integer(n)=>json!(n),ValueRef::Real(n)=>json!(n),ValueRef::Text(t)=>json!(String::from_utf8_lossy(t)),_=>V::Null};value.insert(name.clone(),v);}Ok(V::Object(value))}).map_err(|e|e.to_string())?;mapped.map(|v|v.map_err(|e|e.to_string())).collect()}
fn one(db:&Connection,q:&str,p:&[&dyn ToSql])->R<V>{Ok(rows(db,q,p)?.into_iter().next().unwrap_or(V::Null))}
fn expression(e:&V,f:&V)->V{if e.get("node").is_some(){return if e["node"]=="literal"{e["value"].clone()}else{f[s(&e["ref"])].clone()}}let vals=arr(&e["operands"]).iter().map(|x|expression(x,f)).collect::<Vec<_>>();let a=vals.first().unwrap_or(&V::Null);let b=vals.get(1).unwrap_or(&V::Null);json!(match s(&e["operator"]){"eq"=>a==b,"neq"=>a!=b,"and"=>a==&json!(true)&&b==&json!(true),"or"=>a==&json!(true)||b==&json!(true),"not"=>a!=&json!(true),"exists"=>!a.is_null(),"absent"=>a.is_null(),_=>false})}
fn facts(c:&V,f:&V,subject:&V)->R<()>{need!(f.is_object(),"FACTS");let fields=arr(&c["model"]["facts"]).into_iter().filter(|v|&v["subject_ref"]==subject).collect::<Vec<_>>();for key in f.as_object().unwrap().keys(){need!(fields.iter().any(|v|v["id"]==*key),"FACTS")};for field in fields{let v=&f[s(&field["id"])];if f.get(s(&field["id"])).is_none(){need!(field["required"]!=true,"FACTS");continue}let valid=match s(&field["type"]){"integer"=>v.as_i64().map(|x|x.abs()<=9007199254740991).unwrap_or(false),"boolean"=>v.is_boolean(),"record"=>v.is_object(),"timestamp"=>timestamp(v).is_some(),_=>!s(v).is_empty()};need!(valid,"FACTS")}Ok(())}
fn mapping(c:&V,id:&V,f:&V)->V{let m=arr(&c["model"]["mappings"]).into_iter().find(|x|&x["id"]==id).unwrap();let mut o=serde_json::Map::new();for clause in arr(&m["clauses"]){let value=if clause["source_field"].is_null(){clause["default_value"]["value"].clone()}else{f[s(&clause["source_field"])].clone()};o.insert(s(&clause["target_field"]).into(),value);}V::Object(o)}
fn authorize(c:&V,a:&V,f:&V,context:&V)->R<()>{need!(contains(&context["grants"],&a["authority_boundary_ref"]),"AUTHORITY_DENIED");need!(arr(&a["actor_refs"]).is_empty()||contains(&a["actor_refs"],&context["actor"]),"ACTOR_DENIED");for id in arr(&a["precondition_rule_refs"]){let r=arr(&c["model"]["rules"]).into_iter().find(|x|x["id"]==id).unwrap();need!(expression(&r["condition"],f)==true,"RULE_DENIED")};for id in arr(&a["permission_refs"]){let p=arr(&c["model"]["permissions"]).into_iter().find(|x|x["id"]==id).unwrap();need!(contains(&p["actor_refs"],&context["actor"])&&expression(&p["condition"],f)==true,"PERMISSION_DENIED")};Ok(())}
fn observe(db:&Connection,c:&V,r:&V,stage:&str,m:&V)->R<()>{if !contains(&c["observation"]["stages"],&json!(stage)){return Ok(())}sql(db,"UPDATE accounting SET offered=offered+1 WHERE id=1",&[])?;let key=canonical(&json!([m["messageId"],m["eventType"],stage]));let mut count=n(&one(db,"SELECT COUNT(*) n FROM cardinality",&[])?["n"]);if one(db,"SELECT 1 FROM cardinality WHERE key=?",params![key])?.is_null(){if count>=n(&c["observation"]["cardinalityBudget"]){sql(db,"UPDATE accounting SET rejected=rejected+1 WHERE id=1",&[])?;return Ok(())}sql(db,"INSERT INTO cardinality VALUES(?)",params![key])?;count+=1};let id=n(&one(db,"SELECT COALESCE(MAX(id),0)+1 n FROM observations",&[])?["n"]);let data=json!({"schema_version":"domainspec.orodi.observation/v1","observation_id":format!("event:{id}"),"plane":"product","kind":"log","mode":"simulation","correlation_id":m["messageId"],"attributes":{"message-id":m["messageId"],"event-type":m["eventType"],"stage":stage},"attribute_allowlist":c["observation"]["attributes"],"cardinality":{"observed":count,"budget":c["observation"]["cardinalityBudget"]},"telemetry":{"offered":1,"queued":1,"exported":0,"rejected":0,"dropped":0,"pending":1,"partial_success":0},"deployment_effect":false,"independently_observed":false,"observed_at":r["at"],"invalidation_key_digest":c["binding_digest"]});sql(db,"INSERT INTO observations(id,data) VALUES(?,?)",params![id,canonical(&data)])?;Ok(())}
fn inspect(db:&Connection)->R<V>{let mut states=rows(db,"SELECT * FROM state ORDER BY operation,key",&[])?;for x in &mut states{x["state"]=serde_json::from_str(s(&x["state"])).map_err(|e|format!("{e}"))?}let mut outbox=rows(db,"SELECT id,body,attempts,status,available,lease_owner,lease_until FROM outbox ORDER BY id",&[])?;for x in &mut outbox{x["body"]=serde_json::from_str(s(&x["body"])).map_err(|e|format!("{e}"))?}let observations=rows(db,"SELECT data FROM observations ORDER BY id",&[])?.iter().map(|x|serde_json::from_str::<V>(s(&x["data"])).unwrap()).collect::<Vec<_>>();Ok(json!({"states":states,"outbox":outbox,"inbox":rows(db,"SELECT operation,id FROM inbox ORDER BY operation,id",&[])?,"observations":observations,"accounting":one(db,"SELECT offered,rejected FROM accounting WHERE id=1",&[])?}))}

fn normalize(v:&V)->R<V>{match v{V::Number(number)=>{let value=number.as_f64().ok_or("NUMBER_RANGE")?;need!(value.is_finite()&&value.fract()==0.0&&value.abs()<=9007199254740991.0,"NUMBER_RANGE");Ok(json!(value as i64))},V::Array(items)=>Ok(V::Array(items.iter().map(normalize).collect::<R<Vec<_>>>()?)),V::Object(items)=>{let mut result=serde_json::Map::new();for (k,v) in items{result.insert(k.clone(),normalize(v)?);}Ok(V::Object(result))},_=>Ok(v.clone())}}

/// Trusted host context is separate from the application invocation body.
pub fn handler(r:&V,context:&V,database:&str,failpoint:Option<&str>)->R<V>{
 let normalized=normalize(r)?;let r=&normalized;
 need!(!database.is_empty(),"DATABASE_REQUIRED");let c:V=serde_json::from_str(include_str!("../config.json")).unwrap();if r["command"]!="invoke"{need!(contains(&context["transport_grants"],&c["transport"]),"TRANSPORT_DENIED")}let db=Connection::open(database).map_err(|e|e.to_string())?;
 db.execute_batch("PRAGMA busy_timeout=5000;PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;
CREATE TABLE IF NOT EXISTS state(operation TEXT,key TEXT,state TEXT,version INTEGER,PRIMARY KEY(operation,key));
CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY,body TEXT,commit_json TEXT,attempts INTEGER,status TEXT,available INTEGER,lease_owner TEXT,lease_until INTEGER);
CREATE TABLE IF NOT EXISTS inbox(operation TEXT,id TEXT,body TEXT,PRIMARY KEY(operation,id));
CREATE TABLE IF NOT EXISTS observations(id INTEGER PRIMARY KEY AUTOINCREMENT,data TEXT);
CREATE TABLE IF NOT EXISTS cardinality(key TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS accounting(id INTEGER PRIMARY KEY,offered INTEGER,rejected INTEGER);
INSERT OR IGNORE INTO accounting VALUES(1,0,0);").map_err(|e|e.to_string())?;
 if r["command"]=="inspect"{return inspect(&db)}need!(integer(&r["now"])&&timestamp(&r["at"])==Some(n(&r["now"])),"TIME");
 db.execute_batch("BEGIN IMMEDIATE").map_err(|e|e.to_string())?;
 let mut failed_message:Option<V>=None;
 let result=(||->R<V>{
 if r["command"]=="invoke"{
  let b=arr(&c["executions"]).into_iter().find(|x|x["operation"]==r["operation"]).ok_or("OPERATION")?;let a=arr(&c["model"]["actions"]).into_iter().find(|x|x["id"]==b["operation"]).unwrap();let producer=b["kind"]=="producer";let f=if producer{&r["facts"]}else{&r["message"]["payload"]};facts(&c,f,&a["subject_refs"][0])?;authorize(&c,&a,f,context)?;
  let key=s(&f[s(&b["key"])]);let id=s(&f[s(&b["message-id"])]);need!(!key.is_empty()&&!id.is_empty(),"IDENTITY");let state=canonical(&mapping(&c,&b["state"],f));let operation=s(&b["operation"]);
  if producer{
   need!(integer(&r["expected_version"]),"VERSION");let body=json!({"messageId":id,"eventType":c["event"],"payload":mapping(&c,&b["payload"],f),"occurredAt":f[s(&b["timestamp"])],"aggregateType":a["subject_refs"][0],"aggregateId":key});let fingerprint=canonical(&json!({"operation":operation,"facts":f,"expected_version":r["expected_version"]}));let prior=one(&db,"SELECT commit_json FROM outbox WHERE id=?",params![id])?;
   if !prior.is_null(){need!(s(&prior["commit_json"])==fingerprint,"MESSAGE_ID_CONFLICT");return Ok(json!({"status":"already-committed","message_id":id}))}
   let prev=one(&db,"SELECT version FROM state WHERE operation=? AND key=?",params![operation,key])?;need!((if prev.is_null(){0}else{n(&prev["version"])})==n(&r["expected_version"]),"VERSION_CONFLICT");
   sql(&db,"INSERT INTO state VALUES(?,?,?,?) ON CONFLICT(operation,key) DO UPDATE SET state=excluded.state,version=excluded.version",params![operation,key,state,n(&r["expected_version"])+1])?;need!(failpoint!=Some("after-state"),"FAILPOINT");
   sql(&db,"INSERT INTO outbox VALUES(?,?,?,0,'pending',?,NULL,NULL)",params![id,canonical(&body),fingerprint,n(&r["now"])])?;observe(&db,&c,r,"outbox-committed",&body)?;return Ok(json!({"status":"committed","message_id":id}))
  }
  let m=&r["message"];need!(m["eventType"]==c["event"]&&s(&m["messageId"])==id&&s(&m["aggregateId"])==key&&m["aggregateType"]==a["subject_refs"][0]&&m["occurredAt"]==f[s(&b["timestamp"])],"MESSAGE");let prior=one(&db,"SELECT body FROM inbox WHERE operation=? AND id=?",params![operation,id])?;need!(prior.is_null()||s(&prior["body"])==canonical(m),"MESSAGE_ID_CONFLICT");observe(&db,&c,r,"consumer-received",m)?;
  if !prior.is_null(){observe(&db,&c,r,"consumer-duplicate",m)?;return Ok(json!({"status":"duplicate","message_id":id}))}
  failed_message=Some(m.clone());
  sql(&db,"INSERT INTO state VALUES(?,?,?,1) ON CONFLICT(operation,key) DO UPDATE SET state=excluded.state,version=state.version+1",params![operation,key,state])?;need!(failpoint!=Some("after-state"),"FAILPOINT");sql(&db,"INSERT INTO inbox VALUES(?,?,?)",params![operation,id,canonical(m)])?;observe(&db,&c,r,"consumer-committed",m)?;return Ok(json!({"status":"processed","message_id":id}))
 }
 if r["command"]=="claim"{
  need!(!s(&r["worker"]).is_empty(),"WORKER");let row=one(&db,"SELECT * FROM outbox WHERE (status='pending' AND available<=?) OR (status='leased' AND lease_until<=?) ORDER BY id LIMIT 1",params![n(&r["now"]),n(&r["now"])])?;
  if row.is_null(){return Ok(json!({"status":"empty"}))}if n(&row["attempts"])>=n(&c["max_attempts"]){sql(&db,"UPDATE outbox SET status='dead',lease_owner=NULL,lease_until=NULL WHERE id=?",params![s(&row["id"])])?;return Ok(json!({"status":"dead","message_id":row["id"]}))}
  let attempt=n(&row["attempts"])+1;sql(&db,"UPDATE outbox SET status='leased',attempts=?,lease_owner=?,lease_until=? WHERE id=?",params![attempt,s(&r["worker"]),n(&r["now"])+n(&c["lease_ms"]),s(&row["id"])])?;return Ok(json!({"status":"leased","attempt":attempt,"message":serde_json::from_str::<V>(s(&row["body"])).unwrap()}))
 }
 if r["command"]=="settle"{
  let row=one(&db,"SELECT * FROM outbox WHERE id=? AND status='leased' AND lease_owner=? AND attempts=? AND lease_until>?",params![s(&r["message_id"]),s(&r["worker"]),n(&r["attempt"]),n(&r["now"])])?;need!(!row.is_null(),"LEASE");need!(r["outcome"]=="provider-accepted"||r["outcome"]=="unknown","OUTCOME");let accepted=r["outcome"]=="provider-accepted";let status=if accepted{"published"}else if n(&row["attempts"])>=n(&c["max_attempts"]){"dead"}else{"pending"};let delay=(1000_i64*2_i64.pow((n(&row["attempts"])-1).min(16) as u32)).min(60000);
  sql(&db,"UPDATE outbox SET status=?,available=?,lease_owner=NULL,lease_until=NULL WHERE id=?",params![status,n(&r["now"])+if accepted{0}else{delay},s(&row["id"])])?;let m=serde_json::from_str(s(&row["body"])).unwrap();observe(&db,&c,r,if accepted{"provider-accepted"}else{"transport-unknown"},&m)?;return Ok(json!({"status":status,"message_id":row["id"]}))
 }
 Err("COMMAND".into())
 })();match result{Ok(v)=>{db.execute_batch("COMMIT").map_err(|e|e.to_string())?;Ok(v)},Err(e)=>{let _=db.execute_batch("ROLLBACK");if let Some(message)=failed_message{if db.execute_batch("BEGIN IMMEDIATE").is_ok(){if observe(&db,&c,r,"consumer-failed",&message).is_ok(){let _=db.execute_batch("COMMIT");}else{let _=db.execute_batch("ROLLBACK");}}}Err(e)}}
}
