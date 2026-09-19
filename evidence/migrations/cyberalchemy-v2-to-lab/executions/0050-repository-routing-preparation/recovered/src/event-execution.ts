import {createHash} from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, rmSync, cpSync, existsSync, renameSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { tmpdir } from "node:os";
import { compileEventProfile } from "./event-profile.js";

const fields = ["kind","transport","key","message-id","timestamp","state","payload"];
const reject = (detail:string):never => {throw Error(`EVENT_EXECUTION: ${detail}`)};
export async function compileEventExecution(source:string) {
 const stripped:string[]=[];const bindings:Record<string,Record<string,string>>={};let current:Record<string,string>|undefined;let profiles=0;
 for(const line of source.split(/\r?\n/)){
  if(line==='profile event-execution-v1'){profiles++;stripped.push('profile event-function-v1');current=undefined;continue}
  if(!line.trim()||line.trimStart().startsWith('#')){stripped.push('');continue}
  if(current&&/^\s/.test(line)){
   const m=/^  ([a-z-]+) ([A-Za-z_][\w.-]*)$/.exec(line);
   if(!m||!fields.includes(m[1])||Object.hasOwn(current,m[1]))reject('invalid or duplicate execution field');
   current[m![1]]=m![2];stripped.push('');continue;
  }
  current=undefined;const m=/^execution ([a-z][a-z0-9-]*):$/.exec(line);
  if(m){if(bindings[m[1]])reject('duplicate execution');current={};bindings[m[1]]=current;stripped.push('')}else stripped.push(line);
 }
 if(profiles!==1)reject('one execution profile required');
 const compiled=await compileEventProfile(stripped.join('\n'));const model=compiled.business.plan.model;
 if(compiled.bindingSet.transport_bindings.length!==1||compiled.observations.length!==1)reject('one transport and observation required in this execution slice');
 const transport=compiled.bindingSet.transport_bindings[0];const channel=compiled.bindingSet.message_channels.find(c=>c.channel_id===transport.channel_ref)!;
 const producer=transport.operation_ref.split(':')[1];const consumers=channel.consumer_operation_refs.map(r=>r.split(':')[1]);
 if(consumers.length!==1||Object.keys(bindings).length!==2)reject('exactly one producer and one consumer execution required');
 const validateFormula=(v:any):void=>{
  if(v.node){if(!['literal','fact_ref'].includes(v.node))reject('unsupported SFOL term');return}
  if(!['eq','neq','and','or','not','exists','absent'].includes(v.operator))reject('unsupported SFOL operator');v.operands.forEach(validateFormula);
 };
 for(const r of model.rules)validateFormula(r.condition);
 for(const p of model.permissions)validateFormula(p.condition);
 const supported=['string','identifier','timestamp','boolean','integer','record'];
 for(const f of model.facts)if(!supported.includes(f.type))reject(`unsupported runtime scalar ${f.type}`);
 const executions=Object.entries(bindings).map(([operation,b])=>{
  if(fields.some(k=>!b[k]))reject(`missing execution field ${operation}`);
  const action=model.actions.find(a=>a.id===operation&&a.declaration_kind==='operation');if(!action)reject('unknown operation');
  if(b.transport!==transport.binding_id || b.kind!==(operation===producer?'producer':consumers.includes(operation)?'consumer':'invalid'))reject('operation/transport role mismatch');
  if(action!.subject_refs.length!==1)reject('one operation subject required');
  for(const k of ['key','message-id','timestamp']){
   const f=model.facts.find(f=>f.id===b[k]&&f.subject_ref===action!.subject_refs[0]);if(!f||!f.required||(k==='timestamp'?f.type!=='timestamp':!['identifier','string'].includes(f.type)))reject(`identity field ${k}`);
  }
  if(b.kind==='consumer'&&b.payload!=='none')reject('consumer payload must be none');
  for(const name of [b.state,...(b.kind==='producer'?[b.payload]:[])]){
   const m=model.mappings.find(m=>m.id===name);if(!m||!m.total)reject('total mapping required');
   if(m!.source_ref!==action!.subject_refs[0]||m!.target_ref!==action!.subject_refs[0])reject('mapping subject mismatch');
   const targetFacts=model.facts.filter(f=>f.subject_ref===m!.target_ref);
   if(m!.clauses.some(c=>!targetFacts.some(f=>f.id===c.target_field)))reject('mapping target outside subject');
   if(targetFacts.filter(f=>f.required).some(f=>!m!.clauses.some(c=>c.target_field===f.id)))reject('incomplete total mapping');
   for(const c of m!.clauses)if(c.source_field&&!model.facts.some(f=>f.id===c.source_field&&f.subject_ref===m!.source_ref))reject('mapping source outside subject');
  }
  if(b.kind==='producer'){
   const event=model.events.find(e=>e.id===transport.event_ref.split(':')[1])!;
   const payload=model.mappings.find(m=>m.id===b.payload)!;
   for(const k of ['key','message-id','timestamp'])if(!payload.clauses.some(c=>c.target_field===b[k]&&c.source_field===b[k]))reject('event identity must be preserved by payload mapping');
   if(JSON.stringify([...event.payload_facts].sort())!==JSON.stringify(payload.clauses.map(c=>c.target_field).sort()))reject('payload mapping must exactly cover event payload');
  }
  return {operation,...b} as Record<string,string>;
 });
 for(const k of ['key','message-id','timestamp'])if(executions[0][k]!==executions[1][k])reject('producer and consumer identity fields must agree');
 const failure=compiled.bindingSet.transport_failure_policies.find(p=>p.policy_id===transport.failure_policy_ref)!;
 const delivery=compiled.bindingSet.delivery_policies.find(p=>p.policy_id===transport.delivery_policy_ref)!;
 return {compiled,config:{schema_version:'alch.event-execution/v1',binding_digest:createHash('sha256').update(source).digest('hex'),model,executions,event:transport.event_ref.split(':')[1],transport:transport.binding_id,max_attempts:failure.max_attempts,lease_ms:delivery.visibility_timeout_seconds*1000,observation:compiled.observations[0],authority_effect:'none'}};
}

export async function buildEventExecution(file:string,output:string){
 if(path.extname(file)!=='.alch')reject('source extension');if(existsSync(output))reject('output exists');
 const source=readFileSync(file,'utf8');const {compiled,config}=await compileEventExecution(source);
 const stage=mkdtempSync(path.join(path.dirname(path.resolve(output)),'.alch-event-'));
 try{
  writeFileSync(path.join(stage,'source.alch'),source);writeFileSync(path.join(stage,'config.json'),JSON.stringify(config,null,2)+'\n');
  for(const language of ['typescript','rust'] as const){writeFileSync(path.join(stage,`bindings.${language==='rust'?'rs':'ts'}`),compiled.targets[language].source);writeFileSync(path.join(stage,`${language}.manifest.json`),JSON.stringify(compiled.targets[language].manifest,null,2)+'\n')}
  writeFileSync(path.join(stage,'binding-set.json'),JSON.stringify(compiled.bindingSet,null,2)+'\n');
  cpSync(new URL('./event-templates/handler.mjs',import.meta.url),path.join(stage,'handler.mjs'));
  mkdirSync(path.join(stage,'rust/src'),{recursive:true});
  for(const f of ['lib.rs','main.rs'])cpSync(new URL(`./event-templates/${f}`,import.meta.url),path.join(stage,'rust/src',f));
  cpSync(path.join(stage,'config.json'),path.join(stage,'rust/config.json'));
  writeFileSync(path.join(stage,'rust/Cargo.toml'),'[package]\nname="alch-event"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nserde_json="=1.0.149"\nrusqlite={version="=0.32.1",features=["bundled"]}\nchrono={version="=0.4.45",default-features=false,features=["std"]}\n');
  const runtimeDigest=createHash('sha256').update(JSON.stringify(config)).update(readFileSync(path.join(stage,'handler.mjs'))).update(readFileSync(path.join(stage,'rust/src/lib.rs'))).update(readFileSync(path.join(stage,'rust/src/main.rs'))).update(readFileSync(path.join(stage,'rust/Cargo.toml'))).digest('hex');
  const target=path.join(tmpdir(),'alch-event-execution-rust-target',runtimeDigest);
  execFileSync('cargo',['build','--offline','--manifest-path',path.join(stage,'rust/Cargo.toml'),'--target-dir',target],{stdio:'pipe',maxBuffer:16*1024*1024});
  cpSync(path.join(target,'debug/alch-event'),path.join(stage,'alch-event'));
  if(readFileSync(file,'utf8')!==source)reject('source changed during build');
  writeFileSync(path.join(stage,'deployment.json'),JSON.stringify({profile:'event-execution-v1',node_entry:'handler.mjs',rust_entry:'alch-event',rust_library:'rust/src/lib.rs',storage_environment:'ALCH_EVENT_DATABASE',invocation:'JSON stdin or library handler with trusted host context',transport:'host-driven claim and settle; no network dispatch',control_context:'transport_grants must contain the declared transport ID',provisioned:false,authority_effect:'none'},null,2)+'\n');
  const files=(dir:string):string[]=>readdirSync(dir,{withFileTypes:true}).flatMap(x=>x.isDirectory()?files(path.join(dir,x.name)):[path.join(dir,x.name)]);
  const inventory=Object.fromEntries(files(stage).sort().map(p=>[path.relative(stage,p),createHash('sha256').update(readFileSync(p)).digest('hex')]));
  writeFileSync(path.join(stage,'manifest.json'),JSON.stringify({profile:'event-execution-v1',source_sha256:createHash('sha256').update(source).digest('hex'),runtime_digest:runtimeDigest,files:inventory,authority_effect:'none'},null,2)+'\n');
  renameSync(stage,output);return {status:'built',profile:'event-execution-v1',output:path.resolve(output),authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true})}
}
