#!/usr/bin/env node
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,realpathSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import path from 'node:path';
import {build,node,root,sha} from './build.mjs';
import {exportWireRequest,importRequest} from './wire.mjs';
import {packageCli,materializeCli,inspectPackage,prepareCli} from './package.mjs';
import {commands as preparationCommands,run as runPreparation} from '../preparation/cli.mjs';
import {exampleData} from './example.mjs';
if(realpathSync(process.execPath)!==realpathSync(node)){
 const result=spawnSync(node,[import.meta.filename,...process.argv.slice(2)],{stdio:'inherit'});
 if(result.error)throw result.error;process.exit(result.status??1);
}
const [command,...arguments_]=process.argv.slice(2);
const help=`Define authored in AlchLang; explicit candidate implementation.
  build | doctor | sources
  example --output NEW_DIRECTORY
  start | init --work DIRECTORY --file START.json --actor ACTOR [--id COMMAND_ID]
  import-request --work DIRECTORY --file REQUEST_V3.json --context CONTEXT.json --project PROJECT --work-ref WORK --actor ACTOR [--successor]
  command --work DIRECTORY --file COMMAND.json
  ask | respond --work DIRECTORY --file QUESTION_OR_RESPONSE.json --actor ACTOR [--id COMMAND_ID]
  discover --work DIRECTORY (--catalog REGISTRY.json | --snapshot-db DATABASE --workspace WORKSPACE) --query EXACT_ID_OR_TERM --actor ACTOR [--id COMMAND_ID]
  show --work DIRECTORY
  request --work DIRECTORY [--output NEW_FILE]
  prepare --work DIRECTORY --source-root DIRECTORY --output NEW_DIRECTORY [--permit-retention]
  confirm --work DIRECTORY --package DIRECTORY --actor ACTOR --expected-revision REVISION
  next | notes | replay --work DIRECTORY
  bind --file ORIGINAL_FILE
  context | lookup | assessment | contribute | candidate | fields | revise | assess | handoff-input | handoff | ack
    --work DIRECTORY --file BOUND_INPUT.json --actor ACTOR [--id COMMAND_ID] [--package DIRECTORY]
  placement --scope Work|Project|Imported
  lab-plan --file NATIVE_OBSERVATION.json
  inspect --package DIRECTORY
  reconstruct | materialize --package DIRECTORY --output NEW_DIRECTORY
  lab workspace <list|inspect|resolve|verify|dispatch> ...
Saved session records are candidate Work, not owner grants or admission.
`;
function options(){
 const values={};
 for(let index=0;index<arguments_.length;index++){
  const key=arguments_[index];if(!key.startsWith('--')||Object.hasOwn(values,key))throw Error('invalid-option');
  if(key==='--permit-retention'||key==='--successor')values[key]=true;
  else{const value=arguments_[++index];if(!value||value.startsWith('--'))throw Error('missing-option-value');values[key]=value;}
 }
 return values;
}
function python(args,input){
 const result=spawnSync('python3',['-B',...args],{encoding:'utf8',input,maxBuffer:24*1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
 if(result.status!==0)throw Error(result.stdout||result.stderr||String(result.error));
 return JSON.parse(result.stdout);
}
export async function translate(request){return exportWireRequest(request);}
const genericJsonPort=path.resolve(root,'../../../../../../../implementation/artifact-runtime/json-port.py');
const decodeDocument=raw=>python([genericJsonPort],JSON.stringify({operation:'decode',bytes_base64:raw.toString('base64')})).result.value;
const readDocument=file=>decodeDocument(readFileSync(file));
try{
 if(!command||['help','--help'].includes(command)){console.log(help);process.exit(0);}
 if(command==='sources'){await new Promise((resolve,reject)=>process.stdout.write(readFileSync(path.join(root,'../ALL-ALCHLANG.md')),error=>error?reject(error):resolve()));process.exit(0);}
 if(command==='lab'){
  const result=spawnSync(path.resolve(root,'../../../../define-lab'),arguments_,{stdio:'inherit'});
  if(result.error)throw result.error;process.exit(result.status??1);
 }
 if(command==='build'||command==='doctor'){
  console.log(JSON.stringify({outcome:'completed',implementation:'define-alch',session_engine:'current-authored-source',current_model:'workspaces/products/define/implementation/cli/alchlang/sources.json',...build(),authority_effect:'none'}));process.exit(0);
 }
 const args=options();
 const allowed={example:['--output'],init:['--work','--file','--actor','--id'],command:['--work','--file'],show:['--work'],
  'import-request':['--work','--file','--context','--project','--work-ref','--actor','--successor'],
  request:['--work','--output'],prepare:['--work','--source-root','--output','--permit-retention'],
  confirm:['--work','--package','--actor','--expected-revision'],placement:['--scope'],'lab-plan':['--file'],
  inspect:['--package'],reconstruct:['--package','--output'],materialize:['--package','--output']};
 allowed.start=allowed.init;allowed.ask=['--work','--file','--actor','--id'];allowed.respond=allowed.ask;
 for(const name of preparationCommands)allowed[name]=['--work','--file','--actor','--id'];for(const name of ['next','notes','replay'])allowed[name]=['--work'];allowed.bind=['--file'];allowed.discover=['--work','--catalog','--snapshot-db','--snapshot-trust','--workspace','--query','--actor','--id'];for(const name of ['assess','handoff','handoff-input'])allowed[name].push('--package');allowed.revise.push('--package','--start','--evaluation');
 if(!allowed[command]||Object.keys(args).some(key=>!allowed[command].includes(key)))throw Error('unsupported-command-option');
 const required=key=>{if(typeof args[key]!=='string')throw Error('required-option-'+key);return args[key];};
 const {commit,load,variant,evaluate,exportRequest,writeExclusive,canonical}=await import('./runtime.mjs');
 if(preparationCommands.includes(command)){console.log(JSON.stringify(await runPreparation(command,args),null,2));
 }else if(command==='example'){
  const example=await exampleData({destination:required('--output')});
  console.log(JSON.stringify(example.reply,null,2));
 }else if(command==='init'||command==='start'){
  const start=readDocument(required('--file'));
  const value={command_id:args['--id']??randomUUID(),session_id:start.session_id,project:start.scope.project,work:start.scope.work,
   actor:required('--actor'),expected_revision:'0',payload:variant('Initialize',{scope:start.scope,validation_scope:start.validation_scope,request_revision:start.request_revision,request_lineage:start.request_lineage})};
  console.log(JSON.stringify(await commit(required('--work'),value),null,2));
 }else if(command==='import-request'){
  const raw=readFileSync(required('--file'));
  const loaded=await load(required('--work')),prefix='import:'+sha(raw)+':';
  const prior=loaded.events.find(event=>event.command.command_id===prefix+'0');
  const imported=await importRequest({request:decodeDocument(raw),context:readDocument(required('--context')),
   project:required('--project'),work:required('--work-ref'),successor:!!args['--successor'],current_present:loaded.current!==null,prefix_present:!!prior});
  const base=BigInt(prior?.command.expected_revision??loaded.current?.revision??'0');
  let result;
  for(let index=0;index<imported.payloads.length;index++){
   result=await commit(required('--work'),{command_id:'import:'+sha(raw)+':'+index,
    session_id:imported.seed.session_id,project:args['--project'],work:args['--work-ref'],actor:required('--actor'),
    expected_revision:String(base+BigInt(index)),payload:imported.payloads[index]});
  }
  console.log(JSON.stringify(result,null,2));
 }else if(command==='ask'||command==='respond'){const work=required('--work'),{current}=await load(work);if(!current)throw Error('session-missing');console.log(JSON.stringify(await commit(work,{command_id:args['--id']??randomUUID(),session_id:current.session_id,project:current.scope.project,work:current.scope.work,actor:required('--actor'),expected_revision:current.revision,payload:variant(command==='ask'?'Ask':'Respond',readDocument(required('--file')))}),null,2));
 }else if(command==='command'){
  const value=readDocument(required('--file'));
  if(value.payload?.tag==='Confirm')throw Error('use-confirm-with-exact-package');
  console.log(JSON.stringify(await commit(required('--work'),value),null,2));
 }else if(command==='placement'){
  console.log(JSON.stringify(await evaluate(null,{tag:'PlaceDefinition',fields:{scope:required('--scope')}}),null,2));
 }else if(command==='lab-plan'){
  console.log(JSON.stringify(await evaluate(null,variant('ObserveLab',readDocument(required('--file')))),null,2));
 }else if(command==='confirm'){
  const work=required('--work'),{observation}=await inspectPackage(required('--package'),{observe:true}),{current}=await load(work);
  if(current===null)throw Error('session-missing');
  const result=await commit(work,{command_id:'confirm:'+observation.package_binding.sha256,session_id:current.session_id,
   project:current.scope.project,work:current.scope.work,actor:required('--actor'),expected_revision:required('--expected-revision'),
   payload:variant('Confirm',{package_sha256:observation.package_binding.sha256,request_sha256:observation.request_binding.sha256,actor:args['--actor']})},{observation});
  console.log(JSON.stringify(result,null,2));
 }else if(command==='show'){
  const {current,head}=await load(required('--work'));console.log(JSON.stringify({current,head,authority_effect:'none'},null,2));
 }else if(command==='request'||command==='prepare'){
  const {current,events}=await load(required('--work'));
  const {evidenceMembers}=await import('../preparation/journal.mjs');const supplemental=evidenceMembers(events);
  const request=await translate(await exportRequest(current));
  const raw=JSON.stringify(request,null,2)+'\n';
  if(command==='request'){
   if(args['--output'])writeExclusive(args['--output'],raw);else process.stdout.write(raw);
  }else{
   const result=await prepareCli(Buffer.from(raw),required('--source-root'),required('--output'),{supplemental,permitRetention:!!args['--permit-retention']});
   console.log(JSON.stringify({...result,alch_source_sha256:build().source,session_revision:current.revision},null,2));
  }
 }else if(['inspect','reconstruct'].includes(command)){
  console.log(JSON.stringify(await packageCli(required('--package'),command==='reconstruct'?{destination:required('--output')}:{ }),null,2));
 }else if(command==='materialize'){
  console.log(JSON.stringify(await materializeCli(required('--package'),required('--output')),null,2));
 }else throw Error('unknown-command');
}catch(error){
 const message=String(error.message),unknown=message.includes('outcome-unknown');
 console.error(JSON.stringify({outcome:unknown?'outcome-unknown':'refused',diagnostic:message,authority_effect:'none'}));process.exitCode=1;
}
