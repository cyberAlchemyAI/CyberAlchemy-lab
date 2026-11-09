#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,symlinkSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {build,node,root,sha,selection,inputs} from './build.mjs';
import {implementationRoot as craftRoot} from '../../../../craft/implementation/source-bindings.mjs';
if(realpathSync(process.execPath)!==realpathSync(node)){
 const result=spawnSync(node,[import.meta.filename,...process.argv.slice(2)],{stdio:'inherit'});if(result.error)throw result.error;process.exit(result.status??1);
}
const mode=process.argv[2]??'build';
if(mode==='verify'&&selection.primary!=='define.alch')throw Error('Use verify-remediation-workflow.mjs for the preparation selection');
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
  subjects:[{id:'define-fixture-author',evidence:'isolated-define-fixture-evidence',session:'isolated-define-fixture-session'},{id:'define-fixture-author-only',evidence:'isolated-author-only-evidence',session:'isolated-author-only-session'}],
  grants:[...[selection.entry,'Define.ReadProjectionEntry','Define.ConfirmObservedPackageEntry'].map(entry=>({subject:'define-fixture-author',entry})),{subject:'define-fixture-author-only',entry:selection.entry}],sessionTtlSeconds:7200});
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
 assert.equal(first.outcome.kind,'Returned');
 const original=JSON.parse(JSON.stringify(first.outcome.value.fields.value.fields.value));
 const ready={...original,context_evaluation:{project:scope.project,work:scope.work,source_snapshot:'local:fixture',status:'Sufficient',explanation:'Scoped fixture input',evidence:[]}};
 function rejected(name,result,code){assert.equal(result.ok,true,JSON.stringify(result));assert.equal(result.outcome.kind,'Rejected',JSON.stringify(result));assert.equal(result.outcome.code,code,JSON.stringify(result));checks.push(name);}
 const saturated={...ready,required_concepts:Array.from({length:24},(_,index)=>({concept_id:'concept:'+index,question:'Question '+index,scope:'Fixture scope'}))};
 rejected('concept-capacity-before-output',await command(saturated,variant('Ask',{question_id:'question:overflow',concept_id:'concept:25',question:'An additional required concept?',owner_route:'example:owner',status:'Open'})),'concept-capacity');
 const digest='a'.repeat(64), binding={path:'shared.json',sha256:digest,bytes:'1',digest_kind:'original-file-sha256'};
 const meaning={meaning_id:'meaning:fixture',revision:'1',statement:'A fixture meaning',scope:'Fixture scope',boundaries:['No authority'],parameters:[],ownership_posture:'Candidate only',lineage:[],status:'local-proposed',authority_effect:'none'};
 const populated={...ready,required_concepts:[{concept_id:'one',question:'What is one?',scope:'Fixture'}],handling:[{tag:'Propose',fields:{value:{concept_id:'one',working_meaning:meaning,applicability:'Fixture'}}}],source_bindings:[binding]};
 const conflict={...binding,sha256:'b'.repeat(64)};
 rejected('source-evidence-conflict',await command(populated,variant('BindEvidence',conflict)),'source-conflict');
 rejected('conflicting-export-rejected',await invoke({...populated,evidence_bindings:[conflict]},{tag:'Export',fields:{marker:true}}),'source-conflict');
 const hiddenConflict=structuredClone(populated);hiddenConflict.context_evaluation.evidence=[conflict];
 rejected('context-evidence-conflict',await invoke(hiddenConflict,{tag:'Export',fields:{marker:true}}),'source-conflict');
 const confirmation={package_sha256:digest,request_sha256:'b'.repeat(64),actor:'example:declared-author'};
 rejected('unready-confirmation',await command(original,variant('Confirm',confirmation)),'context-insufficient');
 rejected('eligible-forged-public-confirmation',await command(populated,variant('Confirm',confirmation)),'confirmation-observation-required');
 const exported=await invoke(populated,{tag:'Export',fields:{marker:true}});assert.equal(exported.outcome.kind,'Returned');
 const observed=exported.outcome.value.fields.value.fields.value;
 async function observe(input){
  const selected='Define.ConfirmObservedPackageEntry',prepared=runtime.prepareInput(runtime.entry(selected),wire(input));
  try {const allowed=await runtime.authorize(auth.actor(runtime,'define-fixture-author',selected),prepared);assert.equal(allowed.ok,true,JSON.stringify(allowed));const transfer=await runtime.consume(allowed.value,prepared);assert.equal(transfer.ok,true);return await runtime.execute(transfer.value);} finally {runtime.disposePrepared(prepared);}
 }
 const observation={current:populated,invocation:variant('Command',{command_id:'observed-confirmation',session_id:populated.session_id,project:scope.project,work:scope.work,actor:'example:declared-author',expected_revision:populated.revision,payload:variant('Confirm',confirmation)}),observation:{request:observed,package_binding:{...binding,path:'manifest.json'},request_binding:{...binding,path:'request.json',sha256:confirmation.request_sha256}}};
 const restricted=runtime.prepareInput(runtime.entry('Define.ConfirmObservedPackageEntry'),wire(observation));
 try {const denied=await runtime.authorize(auth.actor(runtime,'define-fixture-author-only','Define.ConfirmObservedPackageEntry'),restricted);assert.equal(denied.ok,false,JSON.stringify(denied));checks.push('author-grant-cannot-observe-package');} finally {runtime.disposePrepared(restricted);}
 const accepted=await observe(observation);assert.equal(accepted.ok,true,JSON.stringify(accepted));assert.equal(accepted.outcome.kind,'Returned',JSON.stringify(accepted));assert.equal(accepted.outcome.value.confirmation.package_sha256,digest);checks.push('protected-exact-observation-continuation');
 const forged=structuredClone(observation);forged.observation.request.goal='A different request';
 rejected('protected-request-mismatch',await observe(forged),'package-request-mismatch');
 rejected('protected-revision-mismatch',await observe({...observation,invocation:variant('Command',{...observation.invocation.fields.value,expected_revision:'99'})}),'revision-conflict');
 rejected('protected-member-mismatch',await observe({...observation,observation:{...observation.observation,package_binding:{...binding,path:'pack.json'}}}),'package-member-mismatch');
 const report={schema_version:'define-remediation-authoring-verification/v1',status:'PASS',source:artifact.source,checks,check_count:checks.length,fixture_auth_only:true,python_define_engine_imported:false,scope:'Generated policy and protected observer boundary only; actual production package byte observation and CLI cutover remain unqualified.'};
 writeFileSync(path.join(root,'.local/REMEDIATION-AUTHORING-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{
 const errors=[];for(const close of [()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined])try{await close();}catch(error){errors.push(error);}
 if(errors.length)throw new AggregateError(errors,'Authoring remediation cleanup failed');
}
