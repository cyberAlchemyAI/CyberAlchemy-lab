/** Shared transport/value primitives. Business expressions are emitted as Rust statements. */
export const rustCargo=`[package]
name = "alch-function"
version = "0.1.0"
edition = "2024"
rust-version = "1.94"
[dependencies]
serde_json = "=1.0.149"
regex = "=1.13.1"
sha2 = "=0.10.9"
chrono = { version = "=0.4.45", default-features = false, features = ["std"] }
axum = "=0.8.4"
tokio = { version = "=1.48.0", features = ["macros", "rt-multi-thread", "net", "time"] }
reqwest = { version = "=0.12.28", default-features = false, features = ["rustls-tls", "json"] }
[workspace]
[profile.dev]
debug = 0
`;
export const rustRuntime=String.raw`
use serde_json::{json,Value};
use std::collections::BTreeMap;
use sha2::{Sha256,Digest};
pub type R=Result<Value,String>;
fn model()->Value{serde_json::from_str(include_str!("../function.json")).expect("generated model")}
fn ontology()->Value{serde_json::from_str(include_str!("../ontology.json")).expect("generated ontology")}
fn bindings()->Value{serde_json::from_str(include_str!("../bindings.json")).expect("generated bindings")}
fn hash(bytes:&[u8])->String{format!("{:x}",Sha256::digest(bytes))}
fn string(v:Value)->Result<String,String>{v.as_str().map(str::to_owned).ok_or("FUNCTION_TYPE".into())}
fn boolean(v:Value)->Result<bool,String>{v.as_bool().ok_or("FUNCTION_BOOLEAN".into())}
fn list(v:Value)->Result<Vec<Value>,String>{v.as_array().cloned().ok_or("FUNCTION_LIST".into())}
fn uint64(v:Value)->Result<u64,String>{
 if let Some(n)=v.as_u64(){return Ok(n);}
 if let Some(s)=v.as_str(){if !s.is_empty() && s.bytes().all(|c|c.is_ascii_digit()) && (s=="0"||!s.starts_with('0')) {return s.parse().map_err(|_|"FUNCTION_UINT64".into());}}
 Err("FUNCTION_UINT64".into())
}
fn compare(a:Value,b:Value)->Result<i8,String>{let a=a.as_i64().map(i128::from).or_else(||a.as_u64().map(i128::from)).ok_or("FUNCTION_TYPE")?;let b=b.as_i64().map(i128::from).or_else(||b.as_u64().map(i128::from)).ok_or("FUNCTION_TYPE")?;Ok(if a<b{-1}else if a>b{1}else{0})}
fn decimal(s:String,scale:u32)->Result<u64,String>{let parts:Vec<_>=s.split('.').collect();if parts.len()>2||parts[0].is_empty()||!parts[0].bytes().all(|c|c.is_ascii_digit())||(parts[0].starts_with('0')&&parts[0]!="0"){return Err("FUNCTION_DECIMAL".into());}let f=parts.get(1).copied().unwrap_or("");if parts.len()==2&&(scale==0||f.is_empty()||f.len()>scale as usize||!f.bytes().all(|c|c.is_ascii_digit())){return Err("FUNCTION_DECIMAL".into());}let whole:u64=parts[0].parse().map_err(|_|"FUNCTION_UINT64")?;let fraction:u64=format!("{f:0<width$}",width=scale as usize).parse().unwrap_or(0);whole.checked_mul(10u64.pow(scale)).and_then(|n|n.checked_add(fraction)).ok_or("FUNCTION_UINT64".into())}
fn money(n:u64,scale:u32)->String{if scale==0{return n.to_string();}let base=10u64.pow(scale);format!("{}.{:0width$}",n/base,n%base,width=scale as usize)}
fn one(v:Value)->R{let mut rows=list(v)?;if rows.len()!=1{return Err("DS_QUERY_CARDINALITY".into());}Ok(rows.remove(0))}
fn distinct(v:Value)->R{let mut out=Vec::new();for v in list(v)?{if !out.contains(&v){out.push(v);}}Ok(Value::Array(out))}
fn sorted(v:Value)->R{let mut rows=list(v)?;rows.sort_by(|a,b|if let (Some(a),Some(b))=(a.as_str(),b.as_str()){a.encode_utf16().cmp(b.encode_utf16())}else{compare(a.clone(),b.clone()).expect("typed scalar").cmp(&0)});Ok(Value::Array(rows))}
fn calculation_error(e:String)->String{if e.contains("subtract range"){"CALCULATION_UNDERFLOW"}else if e.contains("range error"){"CALCULATION_OVERFLOW"}else if e.contains("division by zero"){"CALCULATION_DIVIDE_BY_ZERO"}else if e.contains("inexact"){"CALCULATION_INEXACT"}else{"EVALUATION_FAILED"}.into()}
fn normalize(v:Value)->Value{match v{Value::Array(rows)=>Value::Array(rows.into_iter().map(normalize).collect()),Value::Object(fields)=>Value::Object(fields.into_iter().map(|(k,v)|(k,normalize(v))).collect()),Value::Number(n)=>{if n.is_f64(){if let Some(f)=n.as_f64(){if f.fract()==0.0&&f.abs()<=9007199254740991.0{return json!(f as i64);}}}Value::Number(n)},other=>other}}
struct Context{roots:Value,memo:BTreeMap<String,Value>,events:Vec<Value>,tracing:bool,truncated:bool,bytes:usize}
impl Context{
 fn new(input:Value,tracing:bool)->Self{Self{roots:json!({"input":normalize(input)}),memo:BTreeMap::new(),events:vec![],tracing,truncated:false,bytes:0}}
 fn emit(&mut self,mut e:Value){if !self.tracing{return;}let o=ontology();if e.get("module").is_none(){if let Some(name)=e["declaration"].as_str(){if let Some(n)=o["nodes"].as_array().unwrap().iter().find(|n|n["name"]==name){e["definition"]=n.clone();}}}let size=e.to_string().len();if self.events.len()>=10000||self.bytes+size>2097152{self.truncated=true;return;}self.bytes+=size;self.events.push(e);}
 fn observed(&mut self,name:&str,kind:&str,r:&R){match r{Ok(v)=>{let mut e=json!({"kind":"node-result","declaration":name,"node_kind":kind});if kind=="Query"{e["count"]=json!(v.as_array().unwrap().len());}else{e["value"]=v.clone();}self.emit(e);},Err(code)=>self.emit(json!({"kind":"node-error","declaration":name,"node_kind":kind,"code":code}))}}
}
fn missing(v:&Value)->bool{v.as_object().is_some_and(|o|o.len()==1&&o.get("\u{0}absent")==Some(&Value::Bool(true)))}
fn field(v:Value,key:&str)->Value{v.get(key).cloned().unwrap_or_else(||json!({"\u{0}absent":true}))}
fn nullish(v:&Value)->bool{v.is_null()||missing(v)}
fn portable_timestamp(text:&str)->bool{
 let re=regex::Regex::new(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]{1,9}))?(Z|[+-][0-9]{2}:[0-9]{2})$").unwrap();let Some(m)=re.captures(text)else{return false;};let n=|i:usize|m[i].parse::<u32>().unwrap();let y=n(1);let days=[31,if y%4==0&&(y%100!=0||y%400==0){29}else{28},31,30,31,30,31,31,30,31,30,31];let z=&m[8];
 y>=1&&n(2)>=1&&n(2)<=12&&n(3)>=1&&n(3)<=days[(n(2)-1)as usize]&&n(4)<=23&&n(5)<=59&&n(6)<=59&&(z=="Z"||z[1..3].parse::<u32>().unwrap()<=23&&z[4..6].parse::<u32>().unwrap()<=59)
}
fn valid_id(text:&str,portable:bool)->bool{if portable{!text.trim_matches([' ','\t','\r','\n']).is_empty()}else{!text.trim().is_empty()}}
fn schema(m:&Value,name:&str,v:&Value,depth:usize)->Result<(),String>{
 if depth>32{return Err("FUNCTION_DEPTH".into());}let fields=m["schemas"][name].as_object().ok_or("FUNCTION_SCHEMA")?;let record=v.as_object().ok_or("FUNCTION_RECORD")?;
 if record.keys().any(|k|!fields.contains_key(k)){return Err("FUNCTION_UNKNOWN_FIELD".into());}
 for (key,s) in fields{let Some(v)=record.get(key)else{if s["optional"]==true{continue;}return Err("FUNCTION_REQUIRED".into());};
  if v.is_null(){if s["nullable"]!=true{return Err("FUNCTION_TYPE".into());}if s.get("const").is_some_and(|c|!c.is_null()){return Err("FUNCTION_CONST".into());}continue;}
  match s["type"].as_str().ok_or("FUNCTION_SCHEMA")?{
   "string"|"identifier"|"timestamp"=>{let text=v.as_str().ok_or("FUNCTION_TYPE")?;if s["type"]=="identifier"&&!valid_id(text,m["portability"]=="node-rust-v1"){return Err("FUNCTION_ID".into());}if s["type"]=="timestamp"&&!(if m["portability"]=="node-rust-v1"{portable_timestamp(text)}else{chrono::DateTime::parse_from_rfc3339(text).is_ok()}){return Err("FUNCTION_TIMESTAMP".into());}if s["max"].as_u64().is_some_and(|n|text.encode_utf16().count()as u64>n){return Err("FUNCTION_LIMIT".into());}if let Some(p)=s["pattern"].as_str(){if !regex::Regex::new(p).map_err(|_|"FUNCTION_PATTERN")?.is_match(text){return Err("FUNCTION_PATTERN".into());}}},
   "integer"=>{let n=v.as_i64().ok_or("FUNCTION_TYPE")?;if n.unsigned_abs()>9007199254740991{return Err("FUNCTION_TYPE".into());}if s["min"].as_i64().is_some_and(|b|n<b)||s["max"].as_i64().is_some_and(|b|n>b){return Err("FUNCTION_RANGE".into());}},
   "boolean"=>{if !v.is_boolean(){return Err("FUNCTION_BOOLEAN".into());}},
   "list"=>{let rows=v.as_array().ok_or("FUNCTION_LIST")?;if s["max"].as_u64().is_some_and(|n|rows.len() as u64>n){return Err("FUNCTION_LIMIT".into());}let item=s["items"].as_str().ok_or("FUNCTION_SCHEMA")?;for row in rows{if item=="string"||item=="identifier"{let text=row.as_str().ok_or("FUNCTION_TYPE")?;if item=="identifier"&&!valid_id(text,m["portability"]=="node-rust-v1"){return Err("FUNCTION_TYPE".into());}}else{schema(m,item,row,depth+1)?;}}},
   other=>schema(m,other,v,depth+1)?
  }
  if s.get("const").is_some_and(|c|c!=v){return Err("FUNCTION_CONST".into());}
 }Ok(())
}
fn access<'a>(root:&'a Value,selector:&str)->Option<&'a Value>{let mut v=root;for k in selector.split('.') {v=v.get(k)?;}Some(v)}
fn prepare_request(b:&Value,roots:&Value,env:&BTreeMap<String,String>)->R{
 let raw=env.get(b["urlEnv"].as_str().ok_or("FUNCTION_ENV_REQUIRED")?).filter(|v|!v.is_empty()).ok_or("FUNCTION_ENV_REQUIRED")?;
 let mut url=reqwest::Url::parse(raw).map_err(|_|"FUNCTION_URL")?;
 if url.scheme()!="https"||!url.username().is_empty()||url.password().is_some(){return Err("FUNCTION_URL".into());}
 let query=b["query"].as_object().ok_or("FUNCTION_INTEGRATION_QUERY")?;
 let retained:Vec<(String,String)>=url.query_pairs().filter(|(k,_)|!query.contains_key(k.as_ref())).map(|(k,v)|(k.into_owned(),v.into_owned())).collect();
 url.set_query(None);{let mut pairs=url.query_pairs_mut();for(k,v)in retained{pairs.append_pair(&k,&v);}for(k,s)in query{let v=access(roots,s.as_str().ok_or("FUNCTION_INTEGRATION_QUERY")?).ok_or("FUNCTION_INTEGRATION_QUERY")?;let text=if let Some(s)=v.as_str(){s.to_owned()}else if v.is_number(){v.to_string()}else{return Err("FUNCTION_INTEGRATION_QUERY".into());};pairs.append_pair(k,&text);}}
 let mut headers=json!({"accept":"application/json"});if let Some(key)=b["secretEnv"].as_str(){headers["authorization"]=json!(format!("Bearer {}",env.get(key).filter(|v|!v.is_empty()).ok_or("FUNCTION_ENV_REQUIRED")?));}
 Ok(json!({"url":url.as_str(),"method":"GET","headers":headers,"redirect":"error","timeout_ms":b["timeout"],"max_bytes":b["maxBytes"]}))
}
fn decode_response(status:u16,bytes:&[u8],limit:usize)->R{if !(200..300).contains(&status){return Err("FUNCTION_INTEGRATION_STATUS".into());}if bytes.len()>limit{return Err("FUNCTION_INTEGRATION_LIMIT".into());}serde_json::from_slice(bytes).map(normalize).map_err(|_|"FUNCTION_INTEGRATION_FAILED".into())}
fn accepted_status(b:&Value,status:u16)->bool{if b["transport"]=="module-http"{model()["modules"][b["module"].as_str().unwrap()]["statuses"].as_object().unwrap().values().any(|v|v.as_u64()==Some(status as u64))}else{(200..300).contains(&status)}}
fn decode_binding_response(b:&Value,status:u16,bytes:&[u8],limit:usize)->R{if !accepted_status(b,status){return Err("FUNCTION_INTEGRATION_STATUS".into());}let value=decode_response(200,bytes,limit)?;if b["transport"]=="module-http"&&model()["modules"][b["module"].as_str().unwrap()]["statuses"][value["status"].as_str().unwrap_or("")].as_u64()!=Some(status as u64){return Err("FUNCTION_INTEGRATION_STATUS".into());}Ok(value)}
struct Controlled{responses:Vec<Value>,requests:Vec<Value>,used:usize}
async fn fetch_binding(b:&Value,roots:&Value,env:&BTreeMap<String,String>,controlled:Option<&mut Controlled>)->R{
 let mut prepared=prepare_request(b,roots,env)?;
 if b["transport"]=="module-http"{let argument=access(roots,b["input"].as_str().unwrap()).ok_or("FUNCTION_REQUIRED")?;prepared["method"]=json!("POST");prepared["body"]=json!(argument.to_string());prepared["headers"]["content-type"]=json!("application/json");}
 let limit=b["maxBytes"].as_u64().unwrap()as usize;
 if let Some(c)=controlled{c.requests.push(prepared);let response=c.responses.get(c.used).ok_or("CONFORMANCE_RESPONSE_REQUIRED")?;c.used+=1;if let Some(error)=response["error"].as_str(){return Err(error.into());}let raw=response["raw"].as_str().map(str::to_owned).unwrap_or_else(||response["body"].to_string());return decode_binding_response(b,response["status"].as_u64().unwrap_or(200)as u16,raw.as_bytes(),limit);}
 let client=reqwest::Client::builder().redirect(reqwest::redirect::Policy::none()).timeout(std::time::Duration::from_millis(b["timeout"].as_u64().unwrap())).build().map_err(|_|"FUNCTION_INTEGRATION_FAILED")?;
 let mut request=if prepared["method"]=="POST"{client.post(prepared["url"].as_str().unwrap()).body(prepared["body"].as_str().unwrap().to_owned())}else{client.get(prepared["url"].as_str().unwrap())};for(k,v)in prepared["headers"].as_object().unwrap(){request=request.header(k,v.as_str().unwrap());}
 let mut response=request.send().await.map_err(|e|if e.is_timeout(){"FUNCTION_INTEGRATION_TIMEOUT"}else{"FUNCTION_INTEGRATION_FAILED"})?;let status=response.status().as_u16();if !accepted_status(b,status){return Err("FUNCTION_INTEGRATION_STATUS".into());}
 let mut bytes=Vec::new();while let Some(chunk)=response.chunk().await.map_err(|e|if e.is_timeout(){"FUNCTION_INTEGRATION_TIMEOUT"}else{"FUNCTION_INTEGRATION_FAILED"})?{if bytes.len()+chunk.len()>limit{return Err("FUNCTION_INTEGRATION_LIMIT".into());}bytes.extend_from_slice(&chunk);}
 decode_binding_response(b,status,&bytes,limit)
}
async fn call_module(ctx:&mut Context,step:&Value,b:&Value,env:&BTreeMap<String,String>,local:bool,mut controlled:Option<&mut Controlled>)->R{
 let alias=b["module"].as_str().unwrap();let argument=if let Some(input)=step.get("input"){
 let result: R=(||{let value=ctx.binding_input(step["name"].as_str().unwrap())?;schema(&model(),input["type"].as_str().unwrap(),&value,0).map_err(|_|"FUNCTION_MODULE_INPUT_SCHEMA")?;Ok(value)})();
 match result{Ok(v)=>{ctx.emit(json!({"kind":"binding-input","declaration":step["integration"],"binding":step["name"]}));v},Err(code)=>{ctx.emit(json!({"kind":"binding-input-error","declaration":step["integration"],"binding":step["name"],"code":code}));return Err(code);}}
 }else{access(&ctx.roots,b["input"].as_str().unwrap()).cloned().ok_or("FUNCTION_REQUIRED")?};if argument.to_string().len()>b["maxBytes"].as_u64().unwrap()as usize{return Err("FUNCTION_MODULE_LIMIT".into());}
 ctx.emit(json!({"kind":"module-start","declaration":step["integration"],"module":alias,"transport":b["transport"]}));
 let result: R=async{
  let value=if b["transport"]=="module-local"{
   let responses=controlled.as_ref().map(|c|c.responses[c.used..].to_vec());
   let report=tokio::time::timeout(std::time::Duration::from_millis(b["timeout"].as_u64().unwrap()),invoke_import(alias,argument,env,responses,local,ctx.tracing)).await.map_err(|_|"FUNCTION_MODULE_TIMEOUT")??;
   if let Some(c)=controlled.as_deref_mut(){c.used=c.responses.len()-report["unused_responses"].as_u64().unwrap()as usize;c.requests.extend(report["requests"].as_array().unwrap().iter().cloned());}
   ctx.truncated|=report["capture"]["complete"]!=true;
   for event in report["events"].as_array().unwrap(){let mut event=event.clone();event["module"]=json!(match event["module"].as_str(){Some(child)=>format!("{alias}.{child}"),None=>alias.to_owned()});ctx.emit(event);}
   if report["outcome"]["status"]=="failed"{return Err(report["outcome"]["code"].as_str().unwrap().into());}report["outcome"]["result"].clone()
  }else{if local{return Err("FUNCTION_INTEGRATION_REQUIRED".into());}let mut binding=b.clone();binding["input"]=json!("argument");fetch_binding(&binding,&json!({"argument":argument}),env,controlled).await?};
  schema(&model(),b["output"].as_str().unwrap(),&value,0).map_err(|_|"FUNCTION_INTEGRATION_SCHEMA")?;if value.to_string().len()>b["maxBytes"].as_u64().unwrap()as usize{return Err("FUNCTION_MODULE_LIMIT".into());}Ok(value)
 }.await;
 if result.as_ref().err().is_some_and(|e|e=="FUNCTION_MODULE_TIMEOUT"){ctx.truncated=true;}
 match &result{Ok(_)=>ctx.emit(json!({"kind":"module-result","declaration":step["integration"],"module":alias,"transport":b["transport"]})),Err(code)=>ctx.emit(json!({"kind":"module-error","declaration":step["integration"],"module":alias,"transport":b["transport"],"code":code}))};result
}
async fn run(ctx:&mut Context,env:&BTreeMap<String,String>,local:bool,mut controlled:Option<&mut Controlled>)->R{
 let m=model();schema(&m,m["endpoint"]["input"].as_str().unwrap(),&ctx.roots["input"],0)?;ctx.precheck()?;
 for step in bindings().as_array().unwrap(){let b=&m["integrations"][step["integration"].as_str().unwrap()];if step.get("condition").is_some(){let passed=match ctx.binding_guard(step["name"].as_str().unwrap()){Ok(v)=>v,Err(code)=>{ctx.emit(json!({"kind":"binding-error","declaration":step["integration"],"binding":step["name"],"code":code}));return Err(code);}};ctx.emit(json!({"kind":"binding-guard","declaration":step["integration"],"binding":step["name"],"passed":passed}));if !passed{ctx.emit(json!({"kind":"module-skipped","declaration":step["integration"],"binding":step["name"],"module":b["module"],"transport":b["transport"]}));continue;}}if b["transport"]=="module-local"||b["transport"]=="module-http"{let data=call_module(ctx,step,b,env,local,controlled.as_deref_mut()).await?;ctx.roots[step["name"].as_str().unwrap()]=data;continue;}let provided=b["provided"].as_str().and_then(|s|access(&ctx.roots,s)).cloned();let remote=provided.is_none();let data=if let Some(v)=provided{v}else{if local||b["transport"]=="provided"{return Err("FUNCTION_INTEGRATION_REQUIRED".into());}fetch_binding(b,&ctx.roots,env,controlled.as_deref_mut()).await?};schema(&m,b["output"].as_str().unwrap(),&data,0).map_err(|e|if remote{"FUNCTION_INTEGRATION_SCHEMA".into()}else{e})?;ctx.roots[step["name"].as_str().unwrap()]=data;}
 let result=ctx.execute()?;schema(&m,m["endpoint"]["output"].as_str().unwrap(),&result,0).map_err(|_|"FUNCTION_OUTPUT_SCHEMA")?;Ok(result)
}
pub async fn invoke(input:Value,env:&BTreeMap<String,String>)->R{run(&mut Context::new(input,false),env,false,None).await}
pub async fn trace(input:Value,manifest:Value)->Value{
 let input=normalize(input);let input_hash=hash(input.to_string().as_bytes());let mut ctx=Context::new(input,true);let result=run(&mut ctx,&BTreeMap::new(),true,None).await;let outcome=match result{Ok(v)=>json!({"status":"succeeded","result":v}),Err(code)=>json!({"status":"failed","code":code})};let selected=ctx.events.iter().find(|e|e.get("module").is_none()&&e["kind"]=="selected-case").map(|e|e["index"].clone());
 json!({"schema_version":"alchlang.rust-invocation-trace/v1","binding":{"source_sha256":hash(include_bytes!("../source.alch")),"ontology_sha256":hash(include_bytes!("../ontology.json")),"behavior_sha256":hash(include_bytes!("lib.rs")),"contract_sha256":hash(include_bytes!("../composition.json")),"build_manifest_sha256":hash(manifest.to_string().as_bytes()),"input_sha256":input_hash},"execution_mode":"local-provided-inputs","outcome":outcome,"capture":{"complete":!ctx.truncated,"truncated":ctx.truncated,"recorded_bytes":ctx.bytes},"selected_case":selected,"events":ctx.events,"authority_effect":"none","claim":"native local observation; UInt64 events use exact JSON integers; not a signed attestation"})
}
/// Diagnostic controlled transport; never reads ambient credentials or opens a connection.
pub async fn module_call(input:Value,env:&BTreeMap<String,String>,responses:Option<Vec<Value>>,local:bool,tracing:bool)->Value{
 let mut c=responses.map(|responses|Controlled{responses,requests:vec![],used:0});let mut ctx=Context::new(input,tracing);
 let result=run(&mut ctx,env,local,c.as_mut()).await;let outcome=match result{Ok(result)=>json!({"status":"succeeded","result":result}),Err(code)=>json!({"status":"failed","code":code})};let (requests,unused)=c.map(|c|(c.requests,c.responses.len()-c.used)).unwrap_or_default();
 json!({"outcome":outcome,"events":ctx.events,"requests":requests,"capture":{"complete":!ctx.truncated},"unused_responses":unused})
}
pub async fn conform(envelope:Value)->Value{
 let env:BTreeMap<String,String>=serde_json::from_value(envelope["env"].clone()).unwrap_or_default();module_call(envelope["input"].clone(),&env,Some(envelope["responses"].as_array().cloned().unwrap_or_default()),false,true).await
}
pub async fn handler(request:axum::extract::Request)->axum::response::Response{
 use axum::response::IntoResponse;let m=model();let ep=&m["endpoint"];let env:BTreeMap<String,String>=std::env::vars().collect();
 fn reply(status:u16,value:Value)->axum::response::Response{(axum::http::StatusCode::from_u16(status).unwrap(),[("cache-control","no-store")],axum::Json(value)).into_response()}
 if request.uri().path()!=ep["path"].as_str().unwrap(){return reply(404,json!({"error":"NOT_FOUND"}));}if request.method()!=axum::http::Method::POST{return reply(405,json!({"error":"METHOD_NOT_ALLOWED"}));}
 let Some(token)=env.get(ep["authEnv"].as_str().unwrap())else{return reply(503,json!({"error":"FUNCTION_ENV_REQUIRED"}));};if token.is_empty(){return reply(503,json!({"error":"FUNCTION_ENV_REQUIRED"}));}
 if request.headers().get("authorization").and_then(|v|v.to_str().ok())!=Some(format!("Bearer {token}").as_str()){return reply(401,json!({"error":"UNAUTHORIZED"}));}
 if request.headers().get("content-type").and_then(|v|v.to_str().ok()).and_then(|v|v.split(';').next()).map(str::trim)!=Some("application/json"){return reply(415,json!({"error":"CONTENT_TYPE"}));}
 let result: R=async{let bytes=tokio::time::timeout(std::time::Duration::from_millis(ep["timeout"].as_u64().unwrap()),axum::body::to_bytes(request.into_body(),ep["maxBytes"].as_u64().unwrap()as usize)).await.map_err(|_|"FUNCTION_TIMEOUT")?.map_err(|_|"FUNCTION_BODY_LIMIT")?;let input=serde_json::from_slice(&bytes).map_err(|_|"INVALID_JSON")?;invoke(input,&env).await}.await;
 match result{Ok(v)=>{let status=v["status"].as_str().and_then(|s|ep["statuses"][s].as_u64()).unwrap_or(200);reply(status as u16,v)},Err(code)=>{let status=if code=="INVALID_JSON"{400}else{ep["errors"][&code].as_u64().unwrap_or(ep["errorStatus"].as_u64().unwrap())};reply(status as u16,json!({"error":code}))}}
}
`;
export const rustMain=String.raw`
use std::io::{self,Read};
#[tokio::main]
async fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<String>=std::env::args().skip(1).collect();
 if args.is_empty()||args==["serve"]{let host=std::env::var("HOST").unwrap_or("127.0.0.1".into());let port=std::env::var("PORT").unwrap_or("3000".into());let listener=tokio::net::TcpListener::bind(format!("{host}:{port}")).await?;println!("{}",serde_json::json!({"address":listener.local_addr()?.to_string()}));axum::serve(listener,axum::Router::new().fallback(alch_function::handler)).await?;return Ok(());}
 if args!=["invoke"]&&args!=["trace"]&&args!=["conform"]{return Err("usage: alch-function [serve|invoke|trace|conform]".into());}
 let mut bytes=Vec::new();io::stdin().take(1048577).read_to_end(&mut bytes)?;if bytes.len()>1048576{return Err("FUNCTION_BODY_LIMIT".into());}let input=serde_json::from_slice(&bytes)?;
 if args==["conform"]{println!("{}",alch_function::conform(input).await);}
 else if args==["trace"]{let manifest_path=std::env::current_exe()?.parent().ok_or("executable parent")?.join("manifest.json");let manifest=serde_json::from_slice(&std::fs::read(manifest_path)?)?;let result=alch_function::trace(input,manifest).await;println!("{}",result);if result["outcome"]["status"]=="failed"{std::process::exit(1);}}
 else{match alch_function::invoke(input,&std::collections::BTreeMap::new()).await{Ok(v)=>println!("{v}"),Err(code)=>{println!("{}",serde_json::json!({"error":code}));std::process::exit(1);}}}Ok(())
}
`;
