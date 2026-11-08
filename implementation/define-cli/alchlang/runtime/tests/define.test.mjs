import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,readdirSync,cpSync,symlinkSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {spawnSync} from 'node:child_process';
import {build,root,node,sha} from '../build.mjs';
import {evaluate,transition,variant,exportRequest,commit,load,canonical} from '../runtime.mjs';

const temporary=mkdtempSync(path.join(tmpdir(),'define-alch-tests-'));
const scope={project:'project:context-management',work:'work:retrieval',goal:'Define useful context',
 originating_intent:'Preserve useful context between sessions',context_description:'One project Work item',consumer:'project-team',intended_use:'inspect-preparation'};
const start={scope,request_revision:'1',request_lineage:{predecessor_package_binding:null,language_evidence_binding:null,field_supplement_binding:null},
 validation_scope:{required_checks:['exact bytes'],evidence_scope:'Candidate authoring',claim_ceiling:'No semantic acceptance or admission'}};
const context={project:scope.project,work:scope.work,source_snapshot:'local:authored-request',status:'Sufficient',
 explanation:'The author supplied the bounded candidate context.',evidence:[]};
const command=(session,payload,extra={})=>({command_id:'command-'+(session?.revision??'0')+'-'+payload.tag,session_id:session?.session_id??'session:context-management',
 project:scope.project,work:scope.work,actor:'person:author',expected_revision:session?.revision??'0',payload,...extra});
const initialized=()=>transition(null,command(null,variant('Initialize',start)));
async function ready(){const session=await initialized();return transition(session,command(session,variant('SetContext',context)));}
const question={question_id:'question:retention',concept_id:'retention',question:'What should the agent retain?',owner_route:'role:work-author',status:'Open'};
const response=status=>({response_id:'response:retention',question_id:question.question_id,content:status==='Answered'?'Attributable decisions and unresolved questions.':'The retention boundary remains unanswered.',status,evidence:[]});
function port(operation,data){
 const result=spawnSync('python3',['-B',path.join(root,'pack-port.py')],{input:JSON.stringify({operation,...data}),encoding:'utf8',maxBuffer:16*1024*1024});
 assert.equal(result.status,0,result.stderr);return JSON.parse(result.stdout);
}
function cli(args){return spawnSync(node,[path.join(root,'cli.mjs'),...args],{encoding:'utf8',maxBuffer:16*1024*1024});}
function fixture(name){const result=spawnSync('python3',['-B',path.join(root,'examples/request.py'),name],{encoding:'utf8',maxBuffer:4*1024*1024});assert.equal(result.status,0,result.stderr);return JSON.parse(result.stdout);}
async function importFixture(name){
 const source=fixture(name),imported=port('import-request',{request:source.request,project:scope.project,work:scope.work,context});
 let session=null;
 for(const payload of imported.payloads)session=await transition(session,command(session,payload,{session_id:source.request.request_id}));
 return {...source,session};
}

test('compiler produces an executable full-record Define operation',()=>{assert.equal(build().toolchain.craft,'1.3.0');assert.equal(build().toolchain.alchlang,'0.7.0-candidate.0');});
test('initialization retains actual intent and validation records without authority',async()=>{const session=await initialized();assert.deepEqual(session.scope,scope);assert.equal(session.status,'candidate');assert.equal(session.authority_effect,'none');assert.equal(session.context_evaluation,null);});
test('project, Work, session and expected revision are enforced by AlchLang',async()=>{
 const session=await ready();
 for(const [patch,reason]of [[{project:'project:other'},'ProjectMismatch'],[{work:'work:other'},'WorkMismatch'],[{session_id:'session:other'},'SessionMismatch'],[{expected_revision:'0'},'RevisionConflict']]){
  await assert.rejects(()=>transition(session,command(session,variant('Ask',question),patch)),new RegExp(reason));
 }
});
test('opening a question needs context and retains its prompt, owner and concept',async()=>{
 const initial=await initialized();await assert.rejects(()=>transition(initial,command(initial,variant('Ask',question))),/ContextInsufficient/);
 const session=await ready(),opened=await transition(session,command(session,variant('Ask',question)));
 assert.deepEqual(opened.questions,[question]);assert.equal(opened.required_concepts[0].concept_id,'retention');
 await assert.rejects(()=>transition(opened,command(opened,variant('Ask',{...question,question_id:'second'}))),/CurrentQuestionConflict/);
 await assert.rejects(()=>exportRequest(opened),/QuestionOpen/);
});
test('answers preserve actual text, attribution and evidence and close only the matching question',async()=>{
 const session=await ready(),opened=await transition(session,command(session,variant('Ask',question)));
 await assert.rejects(()=>transition(opened,command(opened,variant('Respond',{...response('Answered'),question_id:'wrong'}))),/InvalidResponse/);
 const answered=await transition(opened,command(opened,variant('Respond',response('Answered'))));
 assert.equal(answered.questions[0].status,'Answered');assert.equal(answered.responses[0].content,response('Answered').content);assert.equal(answered.responses[0].actor,'person:author');
 assert.deepEqual(opened.responses,[]);await assert.rejects(()=>exportRequest(answered),/UnhandledConcept/);
});
test('deferred and refused questions become explicit open handling in an actual Pack request',async()=>{
 for(const status of ['Deferred','Refused']){
  const session=await ready(),opened=await transition(session,command(session,variant('Ask',question)));
  const deferred=await transition(opened,command(opened,variant('Respond',response(status))));
  const request=port('translate',{request:await exportRequest(deferred)}).request;
  assert.equal(request.handling[0].disposition,'open');assert.equal(request.handling[0].payload.reason,response(status).content);
  assert.equal(deferred.questions[0].status,status);assert.equal(request.authority_effect,'none');
 }
});
test('source path collisions refuse differing original-byte bindings',async()=>{
 let session=await ready();const binding={path:'source.json',sha256:'a'.repeat(64),bytes:'5',digest_kind:'original-file-sha256'};
 session=await transition(session,command(session,variant('BindSource',binding)));
 await assert.rejects(()=>transition(session,command(session,variant('BindSource',{...binding,sha256:'b'.repeat(64)}))),/SourceConflict/);
 const repeated=await transition(session,command(session,variant('BindSource',binding)));assert.equal(repeated.source_bindings.length,1);
});
test('meaning disposition requires a declared concept instead of inventing one',async()=>{
 const session=await ready();const value=variant('Open',{concept_id:'undeclared',question:'Meaning?',reason:'Unanswered',affected_use:'inspect-preparation',owner_route:null,continuation:'Ask owner'});
 await assert.rejects(()=>transition(session,command(session,variant('HandleMeaning',value))),/RequiredConceptMissing/);
});
test('complete incident request roundtrips all meanings, values, assessment limits and references',async()=>{
 const source=await importFixture('incident');
 const request=port('translate',{request:await exportRequest(source.session)}).request;
 assert.deepEqual(request,source.request);
 assert.equal(request.assessments[0].reported_result,'FAIL');assert.equal(request.assessments[0].producer.execution_posture,'synthetic');
 assert.equal(source.session.revision!=='1',true);assert.equal(request.request_revision,1);
});
test('the actual User Journey candidate and materialization selections survive AlchLang unchanged',async()=>{
 const source=await importFixture('user-journey');
 const request=port('translate',{request:await exportRequest(source.session)}).request;
 assert.deepEqual(request,source.request);
 assert.equal(request.materialization_selection[0].definition_binding.sha256,'693045f6c86f0faa8b168d072e473bbb48f1e75cb71d440fc559c7440f147fe7');
});
test('saved Work replays through generated AlchLang and repeats the same command without a duplicate event',async()=>{
 const directory=path.join(temporary,'replay');let cmd=command(null,variant('Initialize',start));
 const first=await commit(directory,cmd);const second=await commit(directory,cmd);
 assert.equal(second.outcome,'replayed');assert.equal(second.head,first.head);assert.equal(second.revision,'1');
 const replayed=await load(directory);assert.deepEqual(replayed.current,first.current);assert.equal(replayed.events.length,1);
 await assert.rejects(()=>commit(directory,{...cmd,actor:'person:other'}),/command-id-conflict/);
 const shown=cli(['show','--work',directory]);assert.equal(shown.status,0,shown.stderr);assert.deepEqual(JSON.parse(shown.stdout).current,first.current);
});
test('a cloned Work reconstructs the same candidate history without copying a database or keys',async()=>{
 const original=path.join(temporary,'original'),clone=path.join(temporary,'clone');
 await commit(original,command(null,variant('Initialize',start)));cpSync(path.join(original,'define'),path.join(clone,'define'),{recursive:true});
 assert.deepEqual((await load(original)).current,(await load(clone)).current);
});
test('tampered history is refused before any new record is written',async()=>{
 const directory=path.join(temporary,'tampered');await commit(directory,command(null,variant('Initialize',start)));
 const records=path.join(directory,'define'),file=path.join(records,'session.jsonl');
 const value=JSON.parse(readFileSync(file));value.command.actor='forged';writeFileSync(file,JSON.stringify(value)+'\n');
 await assert.rejects(()=>load(directory),/session-history-or-model-mismatch/);assert.equal(readdirSync(records).length,1);
});
test('closed sessions refuse edits and explicit resume clears stale confirmation',async()=>{
 let session=await ready();session=await transition(session,command(session,{tag:'Close',fields:{marker:true}}));
 await assert.rejects(()=>transition(session,command(session,variant('RequireConcept',{concept_id:'a',question:'A?',scope:'Work'}))),/SessionClosed/);
 session=await transition(session,command(session,{tag:'Resume',fields:{marker:true}}));assert.equal(session.closed,false);assert.equal(session.confirmation,null);
});
test('malformed content is a typed input failure rather than an inferred answer',async()=>{
 const session=await ready();await assert.rejects(()=>transition(session,command(session,variant('Ask',{...question,question:''}))),/alch-evaluation-/);
});
test('CLI imports, prepares, materializes and reconstructs User Journey in separate processes',async()=>{
 const source=fixture('user-journey'),directory=path.join(temporary,'user-journey-cli');mkdirSync(directory);
 const work=path.join(directory,'work'),inputs=path.join(directory,'inputs');mkdirSync(inputs);
 for(const [name,raw]of Object.entries(source.members))writeFileSync(path.join(inputs,name),Buffer.from(raw,'base64'));
 const requestFile=path.join(directory,'request.json'),contextFile=path.join(directory,'context.json');
 writeFileSync(requestFile,JSON.stringify(source.request));writeFileSync(contextFile,JSON.stringify(context));
 const imported=cli(['import-request','--work',work,'--file',requestFile,'--context',contextFile,'--project',scope.project,'--work-ref',scope.work,'--actor','person:author']);assert.equal(imported.status,0,imported.stderr);
 const package_=path.join(directory,'package');const prepared=cli(['prepare','--work',work,'--source-root',inputs,'--output',package_,'--permit-retention']);assert.equal(prepared.status,0,prepared.stderr);
 const pack=JSON.parse(readFileSync(path.join(package_,'pack.json')));assert.equal(pack.status,'candidate');assert.equal(pack.authority_effect,'none');
 const before=JSON.parse(cli(['show','--work',work]).stdout).current;
 const confirmed=cli(['confirm','--work',work,'--package',package_,'--actor','person:author','--expected-revision',before.revision]);assert.equal(confirmed.status,0,confirmed.stderr);
 assert.equal(JSON.parse(confirmed.stdout).current.confirmation.package_sha256,sha(readFileSync(path.join(package_,'manifest.json'))));
 const repeated=cli(['confirm','--work',work,'--package',package_,'--actor','person:author','--expected-revision',before.revision]);assert.equal(repeated.status,0,repeated.stderr);assert.equal(JSON.parse(repeated.stdout).outcome,'replayed');
 const materialized=path.join(directory,'materialized'),materialization=cli(['materialize','--package',package_,'--output',materialized]);assert.equal(materialization.status,0,materialization.stderr);
 function files(directory,prefix=''){return readdirSync(directory,{withFileTypes:true}).flatMap(item=>item.isDirectory()?files(path.join(directory,item.name),prefix+item.name+'/'):[prefix+item.name]);}
 assert(files(materialized).some(name=>name.endsWith('DEFINITION.md')));
 const restored=path.join(directory,'restored');const reconstruction=cli(['reconstruct','--package',package_,'--output',restored]);assert.equal(reconstruction.status,0,reconstruction.stderr);
 for(const file of files(package_))assert.deepEqual(readFileSync(path.join(package_,file)),readFileSync(path.join(restored,file)));
 assert.equal(sha(readFileSync(path.join(package_,'inputs/user-journey.json'))),'693045f6c86f0faa8b168d072e473bbb48f1e75cb71d440fc559c7440f147fe7');
 console.log('User Journey exact outputs: '+directory);
});

test('scope placement and Lab outcome continuation execute from AlchLang',async()=>{
 for(const [scope,wanted]of [['Work','WorkDefinitions'],['Project','ProjectAuthorityDefinitions'],['Imported','UpstreamContribution']]){
  const result=await evaluate(null,{tag:'PlaceDefinition',fields:{scope}});assert.equal(result.fields.value,wanted);
 }
 for(const [tag,fields,wanted]of [['Unknown',{operation_id:'operation:unknown'},'InspectBeforeRedispatch'],
  ['DefinitiveNoEffect',{operation_id:'operation:none'},'ObtainFreshOperationPermission'],['Refused',{reason:'Permission unavailable'},'PreserveRefusal']]){
  const result=await evaluate(null,variant('ObserveLab',{tag,fields}));assert.equal(result.fields.value,wanted);
 }
});
test('competing local commands cannot commit two successors at the same revision',async()=>{
 const work=path.join(temporary,'competition'),session=(await commit(work,command(null,variant('Initialize',start)))).current;
 const candidates=[command(session,variant('SetContext',context),{command_id:'a'}),command(session,variant('SetContext',context),{command_id:'b'})];
 const results=await Promise.allSettled(candidates.map(value=>commit(work,value)));
 assert.equal(results.filter(result=>result.status==='fulfilled').length,1);assert.equal((await load(work)).events.length,2);
});
test('a directory fsync failure after publication reports unknown and preserves the actual bytes',()=>{
 const target=path.join(temporary,'published.json');
 const script=`import fs from 'node:fs'; import {syncBuiltinESMExports} from 'node:module'; import assert from 'node:assert/strict';
 import {writeExclusive} from ${JSON.stringify(new URL('../runtime.mjs',import.meta.url).href)};
 const original=fs.fsyncSync;fs.fsyncSync=fd=>{if(fs.fstatSync(fd).isDirectory())throw Error('injected-directory-sync-failure');return original(fd);};syncBuiltinESMExports();
 assert.throws(()=>writeExclusive(${JSON.stringify(target)},'exact retained bytes'),/publication-outcome-unknown/);
 assert.equal(fs.readFileSync(${JSON.stringify(target)},'utf8'),'exact retained bytes');`;
 const result=spawnSync(node,['--input-type=module','--eval',script],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);
});
test('post-publication lock cleanup failure reconciles by command ID without another event',()=>{
 const work=path.join(temporary,'unknown-write'),value=command(null,variant('Initialize',start));
 const script=`import fs from 'node:fs';import {syncBuiltinESMExports} from 'node:module';import assert from 'node:assert/strict';
 import {commit,load} from ${JSON.stringify(new URL('../runtime.mjs',import.meta.url).href)};
 const original=fs.rmdirSync;fs.rmdirSync=directory=>{original(directory);throw Error('injected-cleanup-failure');};syncBuiltinESMExports();
 await assert.rejects(()=>commit(${JSON.stringify(work)},${JSON.stringify(value)}),/publication-outcome-unknown/);
 fs.rmdirSync=original;syncBuiltinESMExports();
 const retried=await commit(${JSON.stringify(work)},${JSON.stringify(value)});assert.equal(retried.outcome,'replayed');assert.equal((await load(${JSON.stringify(work)})).events.length,1);`;
 const result=spawnSync(node,['--input-type=module','--eval',script],{encoding:'utf8',maxBuffer:4*1024*1024});assert.equal(result.status,0,result.stderr);
});
test('CLI rejects ignored options and direct unchecked confirmation commands',()=>{
 const result=cli(['show','--work',temporary,'--pretend-authority','yes']);assert.notEqual(result.status,0);assert.match(result.stderr,/unsupported-command-option/);
 const file=path.join(temporary,'unchecked-confirmation.json');writeFileSync(file,JSON.stringify({payload:{tag:'Confirm'}}));
 const attempted=cli(['command','--work',temporary,'--file',file]);assert.notEqual(attempted.status,0);assert.match(attempted.stderr,/use-confirm-with-exact-package/);
});

test('a repository session directory cannot redirect replay through a symlink',async()=>{
 const original=path.join(temporary,'symlink-original'),redirect=path.join(temporary,'symlink-redirect');
 await commit(original,command(null,variant('Initialize',start)));mkdirSync(redirect);
 symlinkSync(path.join(original,'define'),path.join(redirect,'define'),'dir');
 await assert.rejects(()=>load(redirect),/session-directory-symlink/);
});

test('a successor request needs a higher explicit Pack revision and a predecessor binding',async()=>{
 const session=await ready(),binding={path:'previous-package.json',sha256:'a'.repeat(64),bytes:'100',digest_kind:'original-file-sha256'};
 const seed={...start,request_revision:'2',request_lineage:{...start.request_lineage,predecessor_package_binding:binding}};
 await assert.rejects(()=>transition(session,command(session,variant('ReviseRequest',{...seed,request_revision:'1'}))),/RevisionConflict/);
 await assert.rejects(()=>transition(session,command(session,variant('ReviseRequest',{...seed,request_lineage:start.request_lineage}))),/SourceConflict/);
 const revised=await transition(session,command(session,variant('ReviseRequest',seed)));
 assert.equal(revised.request_revision,'2');assert.equal(revised.revision,String(BigInt(session.revision)+1n));
 assert.equal(session.request_revision,'1');assert.equal(revised.context_evaluation,null);assert.deepEqual(revised.required_concepts,[]);
});
test('CLI input rejects duplicate JSON keys and unsafe numbers before any journal write',()=>{
 for(const [name,contents]of [['duplicates','{"scope":{},"scope":{}}'],['numbers','{"request_revision":9007199254740993}']]){
  const file=path.join(temporary,name+'.json');writeFileSync(file,contents);
  const result=cli(['init','--work',path.join(temporary,name),'--file',file,'--actor','person:author']);
  assert.notEqual(result.status,0);assert.match(result.stderr,/duplicate-key|unsupported-number/);
 }
});

test('corrections retain their own status without manufacturing an unresolved gap',async()=>{
 const session=await ready(),opened=await transition(session,command(session,variant('Ask',question)));
 const corrected=await transition(opened,command(opened,variant('Respond',response('Corrected'))));
 assert.equal(corrected.questions[0].status,'Corrected');assert.equal(corrected.responses[0].status,'Corrected');assert.deepEqual(corrected.handling,[]);
});

test('a self-consistent journal with an unsupported event version is not treated as the current protocol',async()=>{
 const directory=path.join(temporary,'unknown-version');await commit(directory,command(null,variant('Initialize',start)));
 const file=path.join(directory,'define/session.jsonl'),record=JSON.parse(readFileSync(file));
 record.schema_version='cal.define.alch-session-event/v999';const {event_sha256,...body}=record;record.event_sha256=sha(canonical(body));
 writeFileSync(file,canonical(record)+'\n');await assert.rejects(()=>load(directory),/unsupported-session-record/);
});
