#!/usr/bin/env node
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,realpathSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import path from 'node:path';
import {build,node,root,sha} from './build.mjs';
if(realpathSync(process.execPath)!==realpathSync(node)){
 const result=spawnSync(node,[import.meta.filename,...process.argv.slice(2)],{stdio:'inherit'});
 if(result.error)throw result.error;process.exit(result.status??1);
}
const [command,...arguments_]=process.argv.slice(2);
const help=`Define authored in AlchLang; explicit candidate implementation.
  build | doctor | sources
  example --output NEW_DIRECTORY
  init --work DIRECTORY --file START.json --actor ACTOR [--id COMMAND_ID]
  import-request --work DIRECTORY --file REQUEST_V3.json --context CONTEXT.json --project PROJECT --work-ref WORK --actor ACTOR [--successor]
  command --work DIRECTORY --file COMMAND.json
  show --work DIRECTORY
  request --work DIRECTORY [--output NEW_FILE]
  prepare --work DIRECTORY --source-root DIRECTORY --output NEW_DIRECTORY [--permit-retention]
  confirm --work DIRECTORY --package DIRECTORY --actor ACTOR --expected-revision REVISION
  placement --scope Work|Project|Imported
  lab-plan --file NATIVE_OBSERVATION.json
  inspect --package DIRECTORY
  reconstruct | materialize --package DIRECTORY --output NEW_DIRECTORY
  lab <existing explicit Define/Lab command and arguments>
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
export function translate(request){return python([path.join(root,'pack-port.py')],JSON.stringify({operation:'translate',request})).request;}
const readDocument=file=>python([path.join(root,'pack-port.py')],JSON.stringify({operation:'decode-json',bytes_base64:readFileSync(file).toString('base64')})).document;
const standalone=path.resolve(root,'../../standalone/define.py');
try{
 if(!command||['help','--help'].includes(command)){console.log(help);process.exit(0);}
 if(command==='sources'){process.stdout.write(readFileSync(path.join(root,'../ALL-ALCHLANG.md'),'utf8'));process.exit(0);}
 if(command==='lab'){
  const result=spawnSync(path.resolve(root,'../../../../define/define-lab'),arguments_,{stdio:'inherit'});
  if(result.error)throw result.error;process.exit(result.status??1);
 }
 if(command==='build'||command==='doctor'){
  console.log(JSON.stringify({outcome:'completed',implementation:'define-alch',session_engine:'frozen-source-replay',current_model:'implementation/define-cli/alchlang/sources.json',...build(),authority_effect:'none'}));process.exit(0);
 }
 const args=options();
 const allowed={example:['--output'],init:['--work','--file','--actor','--id'],command:['--work','--file'],show:['--work'],
  'import-request':['--work','--file','--context','--project','--work-ref','--actor','--successor'],
  request:['--work','--output'],prepare:['--work','--source-root','--output','--permit-retention'],
  confirm:['--work','--package','--actor','--expected-revision'],placement:['--scope'],'lab-plan':['--file'],
  inspect:['--package'],reconstruct:['--package','--output'],materialize:['--package','--output']};
 if(!allowed[command]||Object.keys(args).some(key=>!allowed[command].includes(key)))throw Error('unsupported-command-option');
 const required=key=>{if(typeof args[key]!=='string')throw Error('required-option-'+key);return args[key];};
 const {commit,load,variant,evaluate,exportRequest,writeExclusive,canonical}=await import('./runtime.mjs');
 if(command==='example'){
  const example=python([path.join(root,'examples/request.py'),'user-journey']);
  const destination=path.resolve(required('--output'));mkdirSync(destination);
  const sources=path.join(destination,'sources');mkdirSync(sources);
  for(const [name,raw]of Object.entries(example.members))writeExclusive(path.join(sources,name),Buffer.from(raw,'base64'));
  const context={project:'project:cyberalchemy-v2-to-lab-migration',work:'work:define-alch-user-journey',
   source_snapshot:'local:authored-user-journey-request',status:'Sufficient',
   explanation:'Explicit candidate exercise over the repository User Journey source; not a current native Lab context.',evidence:[]};
  writeExclusive(path.join(destination,'request.json'),JSON.stringify(example.request,null,2)+'\n');
  writeExclusive(path.join(destination,'context.json'),JSON.stringify(context,null,2)+'\n');
  console.log(JSON.stringify({outcome:'prepared-example',directory:destination,context,authority_effect:'none'},null,2));
 }else if(command==='init'){
  const start=readDocument(required('--file'));
  const value={command_id:args['--id']??randomUUID(),session_id:start.session_id,project:start.scope.project,work:start.scope.work,
   actor:required('--actor'),expected_revision:'0',payload:variant('Initialize',{scope:start.scope,validation_scope:start.validation_scope,request_revision:start.request_revision,request_lineage:start.request_lineage})};
  console.log(JSON.stringify(await commit(required('--work'),value),null,2));
 }else if(command==='import-request'){
  const raw=readFileSync(required('--file'));
  const imported=python([path.join(root,'pack-port.py')],JSON.stringify({operation:'import-request',request_base64:raw.toString('base64'),
   context:readDocument(required('--context')),project:required('--project'),work:required('--work-ref')}));
  const loaded=await load(required('--work')),prefix='import:'+sha(raw)+':';
  const prior=loaded.events.find(event=>event.command.command_id===prefix+'0');
  if(loaded.current&&!prior&&!args['--successor'])throw Error('existing-session-use-explicit-successor');
  if(args['--successor'])imported.payloads[0].tag='ReviseRequest';
  const base=BigInt(prior?.command.expected_revision??loaded.current?.revision??'0');
  let result;
  for(let index=0;index<imported.payloads.length;index++){
   result=await commit(required('--work'),{command_id:'import:'+sha(raw)+':'+index,
    session_id:imported.seed.session_id,project:args['--project'],work:args['--work-ref'],actor:required('--actor'),
    expected_revision:String(base+BigInt(index)),payload:imported.payloads[index]});
  }
  console.log(JSON.stringify(result,null,2));
 }else if(command==='command'){
  const value=readDocument(required('--file'));
  if(value.payload?.tag==='Confirm')throw Error('use-confirm-with-exact-package');
  console.log(JSON.stringify(await commit(required('--work'),value),null,2));
 }else if(command==='placement'){
  console.log(JSON.stringify(await evaluate(null,{tag:'PlaceDefinition',fields:{scope:required('--scope')}}),null,2));
 }else if(command==='lab-plan'){
  console.log(JSON.stringify(await evaluate(null,variant('ObserveLab',readDocument(required('--file')))),null,2));
 }else if(command==='confirm'){
  const work=required('--work'),package_=required('--package'),{current}=await load(work);
  python([standalone,'inspect',package_]);
  const request=translate(await exportRequest(current)),original=readFileSync(path.join(package_,'request.json'));
  if(canonical(request)!==canonical(JSON.parse(original)))throw Error('package-does-not-match-current-session');
  const manifest=readFileSync(path.join(package_,'manifest.json'));
  const result=await commit(work,{command_id:'confirm:'+sha(manifest),session_id:current.session_id,
   project:current.scope.project,work:current.scope.work,actor:required('--actor'),expected_revision:required('--expected-revision'),
   payload:variant('Confirm',{package_sha256:sha(manifest),request_sha256:sha(original),actor:args['--actor']})});
  console.log(JSON.stringify(result,null,2));
 }else if(command==='show'){
  const {current,head}=await load(required('--work'));console.log(JSON.stringify({current,head,authority_effect:'none'},null,2));
 }else if(command==='request'||command==='prepare'){
  const {current}=await load(required('--work'));
  const request=translate(await exportRequest(current));
  const raw=JSON.stringify(request,null,2)+'\n';
  if(command==='request'){
   if(args['--output'])writeExclusive(args['--output'],raw);else process.stdout.write(raw);
  }else{
   const base=path.join(root,'.local');mkdirSync(base,{recursive:true});const temporary=mkdtempSync(path.join(base,'prepare-'));
   const requestFile=path.join(temporary,'request.json');writeFileSync(requestFile,raw,{flag:'wx',mode:0o600});
   const capture=path.join(temporary,'capture');
   python([standalone,'capture-local','--request',requestFile,'--source-root',required('--source-root'),'--output',capture,...(args['--permit-retention']?['--permit-retention']:[])]);
   const result=python([standalone,'prepare','--request',requestFile,'--capture',capture,'--output',required('--output')]);
   console.log(JSON.stringify({...result,alch_source_sha256:build().source,session_revision:current.revision},null,2));
  }
 }else if(['inspect','reconstruct','materialize'].includes(command)){
  console.log(JSON.stringify(python([standalone,command,required('--package'),...(command==='inspect'?[]:['--output',required('--output')])]),null,2));
 }else throw Error('unknown-command');
}catch(error){
 const message=String(error.message),unknown=message.includes('outcome-unknown');
 console.error(JSON.stringify({outcome:unknown?'outcome-unknown':'refused',diagnostic:message,authority_effect:'none'}));process.exitCode=1;
}
