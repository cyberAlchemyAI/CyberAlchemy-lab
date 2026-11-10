import {verifyRecord} from '../preparation/journal.mjs';
import {normalizeTypedDocument} from './wire.mjs';
import {readFileSync,readdirSync,mkdirSync,writeFileSync,openSync,closeSync,fsyncSync,linkSync,renameSync,unlinkSync,rmdirSync,existsSync,lstatSync,realpathSync,fstatSync,constants} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {randomUUID} from 'node:crypto';
import {build,sha,root} from './build.mjs';
import {evaluatePipeline} from '../../../../../../../implementation/artifact-runtime/pure-pipeline.mjs';
export const canonical=value=>JSON.stringify(value&&typeof value==='object'?(Array.isArray(value)?value.map(item=>JSON.parse(canonical(item))):Object.fromEntries(Object.keys(value).sort().map(key=>[key,JSON.parse(canonical(value[key]))]))):value);
export const variant=(tag,value)=>({tag,fields:{value}});
let compiled;
const verifiedPureResults=new Map();
export async function evaluate(current,invocation,observation=null){
 const selected=build();
 if(compiled&&compiled.selected.source!==selected.source)throw Error('model-changed-during-execution');
 if(!compiled)compiled={selected};
 const key=sha(JSON.stringify([selected.source,current,invocation,observation]));if(verifiedPureResults.has(key))return JSON.parse(verifiedPureResults.get(key));
 const result=await evaluatePipeline(selected.output,selected.files['manifest.json'],{current,invocation,observation});
 if(!result.ok)throw Error('alch-evaluation-'+result.error.code);
 const wire=JSON.parse(new TextDecoder().decode(result.wire));
 if(wire.tag!=='Returned')throw Error('define-'+wire.tag.toLowerCase()+'-'+wire.fields.code);
 if(verifiedPureResults.size>=256)verifiedPureResults.delete(verifiedPureResults.keys().next().value);verifiedPureResults.set(key,JSON.stringify(wire.fields.value));return wire.fields.value;
}
export async function transition(current,command,observation=null){
 const reply=await evaluate(current,variant('Command',command),observation);
 const result=reply.fields.value;
 if(result.tag==='Rejected')throw Error('define-rejected-'+result.fields.reason);
 return result.fields.value;
}
export async function exportRequest(current){
 const reply=await evaluate(current,{tag:'Export',fields:{marker:true}});
 const result=reply.fields.value;
 if(result.tag==='Rejected')throw Error('define-rejected-'+result.fields.reason);
 return result.fields.value;
}
function publish(destination,raw,expected=null){
 const target=path.resolve(destination),temporary=path.join(path.dirname(target),'.define-'+randomUUID());
 let linked=false,failure;
 try{
  const fd=openSync(temporary,'wx',0o600);
  try{writeFileSync(fd,raw);fsyncSync(fd);}finally{closeSync(fd);}
  if(expected===null){linkSync(temporary,target);linked=true;}
  else{if(sha(readJournal(target))!==expected)throw Error('session-head-changed-before-publication');renameSync(temporary,target);linked=true;}
  const directory=openSync(path.dirname(target),'r');try{fsyncSync(directory);}finally{closeSync(directory);}
 }catch(error){failure=error;}
 try{if(existsSync(temporary))unlinkSync(temporary);}catch(error){failure??=error;}
 if(failure){if(linked)throw Error('publication-outcome-unknown: inspect '+target,{cause:failure});throw failure;}
}

export const writeExclusive=(destination,raw)=>publish(destination,raw);
function checkedDirectory(work,relative){
 const base=path.resolve(work);
 for(const item of [base,...relative.split('/').map((_,index)=>path.join(base,...relative.split('/').slice(0,index+1)))]){
  if(existsSync(item)&&lstatSync(item).isSymbolicLink())throw Error('session-directory-symlink');
 }
 return path.join(base,relative);
}
const journal=work=>path.join(checkedDirectory(work,'define'),'session.jsonl');
function readJournal(file){
 const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
 try{
  const before=fstatSync(fd);if(!before.isFile()||before.size>64*1024*1024)throw Error('session-record-bound');
  const raw=readFileSync(fd),after=fstatSync(fd),named=lstatSync(file);
  const identity=value=>[value.dev,value.ino,value.size,value.mtimeMs,value.ctimeMs].join(':');
  if(identity(before)!==identity(after)||identity(after)!==identity(named))throw Error('session-record-changed-during-read');
  return raw;
 }finally{closeSync(fd);}
}
export async function load(work,{commandId=null}={}){
 const file=journal(work);
 if(!existsSync(file)){
  if(existsSync(checkedDirectory(work,'define/session')))throw Error('unsupported-prototype-session-layout');
  return {current:null,events:[],head:null,journal_raw:Buffer.alloc(0),journal_sha256:null};
 }
 const raw=readJournal(file),text=raw.toString('utf8');
 if(!text.endsWith('\n'))throw Error('incomplete-session-journal');
 const lines=text.slice(0,-1).split('\n');if(lines.length>10000)throw Error('session-history-bound');
 const events=[];let current=null,head=null,before;
 for(const line of lines){
  if(Buffer.byteLength(line)>16*1024*1024)throw Error('session-record-bound');
  const record=JSON.parse(line),{event_sha256,...body}=record;
  if(canonical(record)!==line)throw Error('noncanonical-session-history');
  const version=body.schema_version;const keys=version==='cal.define.alch-session-event/v3'?'command,event_sha256,model,observation,preparation,previous,schema_version,state_sha256':'command,event_sha256,model,observation,previous,schema_version,state_sha256';
  if(!['cal.define.alch-session-event/v2','cal.define.alch-session-event/v3'].includes(version)||Object.keys(record).sort().join(',')!==keys)throw Error('unsupported-session-record');
  if(event_sha256!==sha(canonical(body))||body.previous!==head||body.model!==build().source)throw Error('session-history-or-model-mismatch');
  if(events.some(event=>event.command.command_id===body.command.command_id))throw Error('duplicate-command-in-history');
  if(body.command.command_id===commandId)before=current;
  if(version==='cal.define.alch-session-event/v3')await verifyRecord(current,body.model,body.command,body.preparation);
  current=await transition(current,body.command,body.observation);
  if(sha(canonical(current))!==body.state_sha256)throw Error('session-replay-mismatch');
  events.push(record);head=event_sha256;
 }
 return {current,events,head,before,journal_raw:raw,journal_sha256:sha(raw)};
}

export async function commit(work,command,{observation=null,preparation=null}={}){
 command=await normalizeTypedDocument(command);
 const local=checkedDirectory(work,'.local');mkdirSync(local,{recursive:true});
 const lock=path.join(local,'define-session.lock');mkdirSync(lock);
 let published=false,result,failure;
 try{
  const selected=build(),loaded=await load(work);
  const prior=loaded.events.find(event=>event.command.command_id===command.command_id);
  if(prior){
   if(canonical(prior.command)!==canonical(command)||canonical(prior.observation)!==canonical(observation)||canonical(prior.preparation??null)!==canonical(preparation))throw Error('command-id-conflict');
   result={outcome:'replayed',revision:String(BigInt(prior.command.expected_revision)+1n),head:prior.event_sha256,current:loaded.current};
  }else{
   if(preparation!==null)await verifyRecord(loaded.current,selected.source,command,preparation);
   const current=await transition(loaded.current,command,observation);
   if(build().source!==selected.source)throw Error('model-changed-during-execution');
   const body={schema_version:preparation===null?'cal.define.alch-session-event/v2':'cal.define.alch-session-event/v3',model:selected.source,previous:loaded.head,command,observation,...(preparation===null?{}:{preparation}),state_sha256:sha(canonical(current))};
   const record={...body,event_sha256:sha(canonical(body))};if(Buffer.byteLength(canonical(record))>16*1024*1024)throw Error('session-record-bound');
   const file=journal(work),directory=path.dirname(file);mkdirSync(directory,{recursive:true});
   const raw=Buffer.concat([loaded.journal_raw,Buffer.from(canonical(record)+'\n')]);
   if(raw.length>64*1024*1024)throw Error('session-history-byte-bound');
   publish(file,raw,loaded.journal_sha256);published=true;
   for(const parent of [directory,path.resolve(work)]){
    const fd=openSync(parent,'r');try{fsyncSync(fd);}finally{closeSync(fd);}
   }
   result={outcome:'recorded',revision:current.revision,head:record.event_sha256,current};
  }
 }catch(error){failure=error;}
 try{rmdirSync(lock);}catch(error){failure??=error;}
 if(failure){if(published&&!String(failure.message).includes('outcome-unknown'))throw Error('publication-outcome-unknown: inspect command '+command.command_id,{cause:failure});throw failure;}
 return result;
}
