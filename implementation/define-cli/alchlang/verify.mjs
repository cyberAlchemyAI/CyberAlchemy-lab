#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,symlinkSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {build,node,root,sha,selection,inputs} from './build.mjs';
import {implementationRoot as craftRoot} from '../../../craft/implementation/source-bindings.mjs';
if(realpathSync(process.execPath)!==realpathSync(node)){
 const result=spawnSync(node,[import.meta.filename,...process.argv.slice(2)],{stdio:'inherit'});if(result.error)throw result.error;process.exit(result.status??1);
}
const mode=process.argv[2]??'build';
if(mode==='verify'&&selection.primary!=='define.alch')throw Error('Use verify-preparation.mjs for the preparation selection');
assert(['build','verify'].includes(mode));
const artifact=build();
if(mode==='build'){
 console.log(JSON.stringify({status:'BUILT',source:artifact.source,output:artifact.output,alch_files:1+selection.additional.length},null,2));
 process.exit(0);
}
// Fixture identity is confined to this explicit qualification driver. It never
// provisions or qualifies an actual Lab owner or operator grant.
const fixture=await import(pathToFileURL(path.join(craftRoot,'cli/dist/generic/testing.js')).href);
const dependency=path.join(root,'.local/node_modules/@domainspec-v2');mkdirSync(dependency,{recursive:true});
const peer=path.join(dependency,'cli');if(!existsSync(peer))symlinkSync(path.join(craftRoot,'cli'),peer,'dir');
assert.equal(realpathSync(peer),path.join(craftRoot,'cli'));
const {createGeneratedApplicationOwner}=await import(pathToFileURL(path.join(artifact.output,'application.mjs')).href);
const owner=createGeneratedApplicationOwner(),directory=mkdtempSync(path.join(root,'.local/qualification-'));
const wire=value=>new Uint8Array(Buffer.from(JSON.stringify(value)));
let handle,auth,runtime;
const checks=[];
const check=(name,fn)=>{fn();checks.push(name);console.log('PASS '+name);};
const variant=(tag,value)=>({tag,fields:{value}});
try{
 handle=await owner.prepare();
 const review=owner.review(handle,'define-modular-fixture');
 owner.accept(handle,{decision_id:'define-modular-fixture',owner:'define-modular-fixture',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,'review.json'));
 auth=await fixture.createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),
  subjects:[{id:'define-fixture-author',evidence:'isolated-define-fixture-evidence',session:'isolated-define-fixture-session'}],
  grants:[selection.entry,'Define.ReadProjectionEntry'].map(entry=>({subject:'define-fixture-author',entry})),sessionTtlSeconds:7200});
 const setup=await fixture.prepareGenericFixtureRuntime(owner,handle,{service:'DefineService',ownedDirectory:path.join(directory,'cache'),nativeAuth:auth.nativeAuth});
 runtime=setup.runtime;
 fixture.loadGenericFixture(setup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
 let sequence=0;
 async function invoke(current,invocation,options={}){
  const entry=runtime.entry(selection.entry),key=options.key??'define-witness-'+(++sequence);
  const prepared=runtime.prepareCommand(entry,wire({current,invocation}),{client_key:key});
  try{
   const actor=options.noActor?null:auth.actor(runtime,'define-fixture-author',selection.entry);
   const authorization=await runtime.authorize(actor,prepared);
   if(!authorization.ok)return {denied:authorization};
   const transfer=await runtime.consume(authorization.value,prepared);assert.equal(transfer.ok,true,JSON.stringify(transfer));
   return await runtime.executeCommand(transfer.value);
  }finally{runtime.disposePrepared(prepared);}
 }
 async function command(current,payload,patch={}){
  const command={command_id:'cmd-'+sequence,session_id:current?.session_id??'define-operation-witness',
   project:'project:context-management',work:'work:retention',actor:'example:declared-author',expected_revision:current?.revision??'0',payload,...patch};
  return invoke(current,variant('Command',command));
 }
 const scope={project:'project:context-management',work:'work:retention',goal:'Define useful retained context',originating_intent:'Keep useful context between sessions',context_description:'An explicit local candidate',consumer:'project-team',intended_use:'inspect-preparation'};
 const start={request_revision:'1',request_lineage:{predecessor_package_binding:null,language_evidence_binding:null,field_supplement_binding:null},scope,
  validation_scope:{required_checks:['Exact source bytes'],evidence_scope:'Isolated fixture authoring',claim_ceiling:'No semantic acceptance or native Lab admission'}};
 const first=await command(null,variant('Initialize',start));
 writeFileSync(path.join(directory,'first.json'),JSON.stringify(first,null,2)+'\n');
 check('StartSession executes as an Operation',()=>{assert.equal(first.ok,true,JSON.stringify(first));assert.equal(first.outcome.kind,'Returned');});
 const sessionOf=result=>{assert.equal(result.ok,true,JSON.stringify(result));assert.equal(result.outcome.kind,'Returned',JSON.stringify(result));return JSON.parse(JSON.stringify(result.outcome.value.fields.value.fields.value));};
 let session=sessionOf(first);
 check('session records preserve authored scope and candidate standing',()=>{assert.deepEqual(session.scope,scope);assert.equal(session.status,'candidate');assert.equal(session.revision,'1');});
 const unready=await invoke(session,{tag:'Export',fields:{marker:true}});
 check('PreparationEligibility rejects missing evaluated context',()=>{assert.equal(unready.outcome.kind,'Rejected');assert.equal(unready.outcome.code,'context-insufficient');});
 const denied=await invoke(session,{tag:'Export',fields:{marker:true}},{noActor:true});
 check('missing fixture authentication is denied',()=>assert(denied.denied&&!denied.denied.ok));
 const wrong=await command(session,{tag:'Resume',fields:{marker:true}},{project:'project:other'});
 check('project mismatch propagates as an Operation rejection',()=>{assert.equal(wrong.ok,true);assert.equal(wrong.outcome.kind,'Rejected');assert.equal(wrong.outcome.code,'project-mismatch');});
 const context={project:scope.project,work:scope.work,source_snapshot:'local:fixture',status:'Sufficient',explanation:'Authored candidate context; not live native Lab context.',evidence:[]};
 session=sessionOf(await command(session,variant('SetContext',context)));
 const question={question_id:'question:retention',concept_id:'retention',question:'Which context should be retained?',owner_route:'example:author',status:'Open'};
 const opened=await command(session,variant('Ask',question));session=sessionOf(opened);
 check('AskQuestion preserves the actual prompt through the composed Operations',()=>{assert.deepEqual(session.questions,[question]);assert.equal(session.revision,'3');});
 const duplicate=await command(session,variant('Ask',{...question,question_id:'question:second'}));
 check('one-question guard rejects before producing a new session',()=>{assert.equal(duplicate.outcome.kind,'Rejected');assert.equal(duplicate.outcome.code,'question-already-open');});
 session=sessionOf(await command(session,variant('Respond',{response_id:'response:deferred',question_id:question.question_id,content:'The retention boundary remains unanswered.',status:'Deferred',evidence:[]})));
 check('RespondToQuestion retains attribution and an explicit open meaning',()=>{assert.equal(session.responses[0].actor,'example:declared-author');assert.equal(session.handling[0].tag,'Open');});
 const closed=sessionOf(await command(session,{tag:'Close',fields:{marker:true}}));
 check('SessionLifecycle closes the actual session',()=>assert.equal(closed.closed,true));
 session=sessionOf(await command(closed,{tag:'Resume',fields:{marker:true}}));
 check('SessionLifecycle resumes the actual session',()=>assert.equal(session.closed,false));
 const exported=await invoke(session,{tag:'Export',fields:{marker:true}});
 check('ExportPreparation is an Operation with a complete typed request',()=>{assert.equal(exported.outcome.kind,'Returned');assert.equal(exported.outcome.value.fields.value.tag,'Prepared');});
 const request=exported.outcome.value.fields.value.fields.value;
 const translated=spawnSync('python3',['-B',path.resolve(root,'runtime/pack-port.py')],{encoding:'utf8',input:JSON.stringify({operation:'translate',request})});
 check('request representation validates against the real Pack v3 schema',()=>{assert.equal(translated.status,0,translated.stderr||translated.stdout);assert.equal(JSON.parse(translated.stdout).request.handling[0].disposition,'open');});
 // Start from the frozen journal reference Session, then exercise the new named
 // Operation and request export through the current generated application.
 const exampleProcess=spawnSync('python3',['-B',path.resolve(root,'runtime/examples/request.py'),'user-journey'],{encoding:'utf8'});
 assert.equal(exampleProcess.status,0,exampleProcess.stderr);const example=JSON.parse(exampleProcess.stdout);
 const importProcess=spawnSync('python3',['-B',path.resolve(root,'runtime/pack-port.py')],{encoding:'utf8',input:JSON.stringify({operation:'import-request',request:example.request,project:scope.project,work:scope.work,context})});
 assert.equal(importProcess.status,0,importProcess.stderr);const imported=JSON.parse(importProcess.stdout);
 const reference=await import(new URL('./runtime/runtime.mjs',import.meta.url));
 let referenceSession=null;
 for(const payload of imported.payloads){referenceSession=await reference.transition(referenceSession,{command_id:'reference-'+(referenceSession?.revision??'0'),session_id:example.request.request_id,project:scope.project,work:scope.work,actor:'example:declared-author',expected_revision:referenceSession?.revision??'0',payload});}
 const meaning=imported.payloads.find(item=>item.tag==='HandleMeaning');
 const expected=await reference.transition(referenceSession,{command_id:'reference-update',session_id:referenceSession.session_id,project:scope.project,work:scope.work,actor:'example:declared-author',expected_revision:referenceSession.revision,payload:meaning});
 const updatedMeaning=sessionOf(await command(referenceSession,meaning));
 check('RecordMeaning Operation agrees with the frozen journal behavior',()=>assert.deepEqual(updatedMeaning,expected));
 const fullExport=await invoke(updatedMeaning,{tag:'Export',fields:{marker:true}});
 assert.equal(fullExport.outcome.kind,'Returned');
 const qualification=spawnSync('python3',['-B',path.join(root,'qualify-pack.py')],{encoding:'utf8',input:JSON.stringify(fullExport.outcome.value.fields.value.fields.value),maxBuffer:4*1024*1024});
 let userJourney;
 check('actual User Journey materializes and reconstructs exact Pack bytes',()=>{assert.equal(qualification.status,0,qualification.stderr||qualification.stdout);userJourney=JSON.parse(qualification.stdout);assert.equal(userJourney.reconstructed_exactly,true);assert.equal(userJourney.pack_status,'candidate');});
 for(const [tag,fields,expected]of [
  ['Unknown',{operation_id:'op:uncertain'},'InspectBeforeRedispatch'],
  ['DefinitiveNoEffect',{operation_id:'op:no-effect'},'ObtainFreshOperationPermission'],
  ['Refused',{reason:'Owner refused'},'PreserveRefusal']]){
   const observed=await invoke(null,variant('ObserveLab',{tag,fields}));
   check('Lab continuation Policy: '+tag,()=>assert.equal(observed.outcome.value.fields.value,expected));
 }
 for(const [scope,expected]of [['Work','WorkDefinitions'],['Project','ProjectAuthorityDefinitions'],['Imported','UpstreamContribution']]){
  const placed=await invoke(null,{tag:'PlaceDefinition',fields:{scope}});
  check('definition placement: '+scope,()=>assert.equal(placed.outcome.value.fields.value,expected));
 }
 const projected=await invoke(null,variant('CacheProjection',{projection_id:'1',source_digest:'a'.repeat(64),session}),{key:'cache-one'});
 const replayed=await invoke(null,variant('CacheProjection',{projection_id:'1',source_digest:'a'.repeat(64),session}),{key:'cache-one'});
 check('explicit disposable SQLite projection commits and replays',()=>{assert.equal(projected.observation.kind,'committed');assert.equal(replayed.observation.kind,'replayed');assert.deepEqual(projected.outcome,replayed.outcome);});
 const conflict=await invoke(null,variant('CacheProjection',{projection_id:'1',source_digest:'b'.repeat(64),session}),{key:'cache-conflict'});
 check('projection identity conflict refuses an inconsistent cache row',()=>{assert.equal(conflict.outcome.kind,'Rejected');assert.equal(conflict.outcome.code,'projection-identity-conflict');});
 const {DatabaseSync}=await import('node:sqlite');const db=new DatabaseSync(setup.storePath,{readOnly:true});
 let rows;try{const schema=JSON.parse(readFileSync(path.join(artifact.output,'storage/schema.json')));const name=schema.tables.find(table=>table.entity==='Define.Projection').physical_name;rows=db.prepare('SELECT COUNT(*) AS n FROM "'+name.replaceAll('"','""')+'"').get().n;}finally{db.close();}
 check('cache has one projection after replay and conflict',()=>assert.equal(rows,1));
 await runtime.close();runtime=await owner.openRuntime(handle,{service:'DefineService',storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
 const coldReplay=await invoke(null,variant('CacheProjection',{projection_id:'1',source_digest:'a'.repeat(64),session}),{key:'cache-one'});
 check('a reopened disposable cache replays the original command without another row',()=>{assert.equal(coldReplay.observation.kind,'replayed');assert.deepEqual(coldReplay.outcome,projected.outcome);});
 async function readProjection(project,work){
  const selected='Define.ReadProjectionEntry',prepared=runtime.prepareInput(runtime.entry(selected),wire({id:'1',project,work}));
  try{
   const allowed=await runtime.authorize(auth.actor(runtime,'define-fixture-author',selected),prepared);assert.equal(allowed.ok,true);
   const transferred=await runtime.consume(allowed.value,prepared);assert.equal(transferred.ok,true);
   return await runtime.execute(transferred.value);
  }finally{runtime.disposePrepared(prepared);}
 }
 const found=await readProjection(scope.project,scope.work);
 check('ReadProjection Query retrieves the exact retained Work projection',()=>{assert.equal(found.ok,true,JSON.stringify(found));assert.deepEqual(JSON.parse(JSON.stringify(found.outcome.value.value)),session);});
 const foreign=await readProjection('project:other',scope.work);
 check('ReadProjection Query excludes a different project selector',()=>{assert.equal(foreign.ok,true);assert.equal(foreign.outcome.value,null);});
 const otherWork=await readProjection(scope.project,'work:other');
 check('ReadProjection Query excludes a different Work selector',()=>assert.equal(otherWork.outcome.value,null));
 const report={schema_version:'cal.define.module-use-case-authoring-qualification/v1',status:'PASS',completed_at:new Date().toISOString(),
  model_sha256:artifact.source,user_journey:userJourney,toolchain:artifact.toolchain,alch_files:1+selection.additional.length,checks,check_count:checks.length,
  fixture_directory:directory,fixture_auth_only:true,lab_owner_operations_executed:false,default_cli_rebound:false,
  source_sha256:Object.fromEntries([...inputs,'build.mjs','verify.mjs','qualify-pack.py'].map(name=>[name,sha(readFileSync(path.join(root,name)))]))};
 writeFileSync(path.join(root,'VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:'PASS',checks:checks.length,fixture_directory:directory}));
}finally{
 const errors=[];for(const close of [()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined])try{await close();}catch(error){errors.push(error);}
 if(errors.length)throw new AggregateError(errors,'Qualification cleanup failed');
}
