#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,symlinkSync,realpathSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {implementationRoot as craftRoot} from '../../../../craft/implementation/source-bindings.mjs';
process.env.DEFINE_MODEL_SELECTION='preparation-sources.json';
const {build,node,root,sha,inputs,selection}=await import('./build.mjs');
if(realpathSync(process.execPath)!==realpathSync(node)){
 const child=spawnSync(node,[import.meta.filename],{stdio:'inherit'});if(child.error)throw child.error;process.exit(child.status??1);
}
const artifact=build(),wire=value=>new Uint8Array(Buffer.from(JSON.stringify(value)));
const fixture=await import(pathToFileURL(path.join(craftRoot,'cli/dist/generic/testing.js')).href);
const dependency=path.join(root,'.local/node_modules/@domainspec-v2');mkdirSync(dependency,{recursive:true});
const peer=path.join(dependency,'cli');if(!existsSync(peer))symlinkSync(path.join(craftRoot,'cli'),peer,'dir');assert.equal(realpathSync(peer),path.join(craftRoot,'cli'));
const {createGeneratedApplicationOwner}=await import(pathToFileURL(path.join(artifact.output,'application.mjs')).href);
const owner=createGeneratedApplicationOwner(),directory=mkdtempSync(path.join(root,'.local/preparation-qualification-'));
const checks=[];const check=(name,fn)=>{fn();checks.push(name);console.log('PASS '+name);};
let handle,auth,runtime,inbox,workflow,relay;
try{
 handle=await owner.prepare();const review=owner.review(handle,'define-preparation-fixture');
 owner.accept(handle,{decision_id:'define-preparation-fixture',owner:'define-preparation-fixture',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,'review.json'));
 const ids=['Define.BeginPreparationEntry','Define.ContinuePreparationEntry','Define.PrepareCandidateEntry','Define.ReadPreparationRunEntry','Define.ReadPreparedCandidateEntry'];
 auth=await fixture.createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),subjects:[{id:'workflow-fixture',evidence:'isolated-workflow-evidence',session:'isolated-workflow-session'}],grants:ids.map(entry=>({subject:'workflow-fixture',entry})),sessionTtlSeconds:7200});
 const setup=await fixture.prepareGenericFixtureRuntime(owner,handle,{service:'DefineService',ownedDirectory:path.join(directory,'durable-define-store'),nativeAuth:auth.nativeAuth});runtime=setup.runtime;
 fixture.loadGenericFixture(setup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
 const receiver=await fixture.prepareGenericFixtureRuntime(owner,handle,{service:'LabIntegrationService',ownedDirectory:path.join(directory,'durable-review-inbox'),nativeAuth:auth.nativeAuth});inbox=receiver.runtime;
 fixture.loadGenericFixture(receiver.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
 const receiverEntry='LabIntegration.ReceiveCandidateEntry';auth.bindReceiver(inbox,receiverEntry);
 const actors=new Map(ids.map(id=>[id,auth.actor(runtime,'workflow-fixture',id)]));

 const project='project:remediation',work='work:remediation',digest=artifact.source;
 const session={schema_version:'cal.define.alch-session/v1',session_id:'request:remediation',revision:'1',request_revision:'1',request_lineage:{predecessor_package_binding:null,language_evidence_binding:null,field_supplement_binding:null},scope:{project,work,goal:'Verify the corrected contracts',originating_intent:'Keep exact scope and evidence',context_description:'Isolated generated-code regression',consumer:'audit',intended_use:'inspect-preparation'},context_evaluation:{project,work,source_snapshot:'fixture:current',status:'Sufficient',explanation:'Fixture only',evidence:[]},questions:[],responses:[],required_concepts:[{concept_id:'one',question:'What is one?',scope:'Fixture'}],handling:[{tag:'Propose',fields:{value:{concept_id:'one',working_meaning:{meaning_id:'meaning:one',revision:'1',statement:'A bounded fixture meaning',scope:'Fixture',boundaries:['No authority'],parameters:[],ownership_posture:'Candidate',lineage:[],status:'local-proposed',authority_effect:'none'},applicability:'Fixture'}}}],source_bindings:[],evidence_bindings:[],applications:[],assessments:[],materialization_selection:[],validation_scope:{required_checks:['Exact correlation'],evidence_scope:'Generated fixture',claim_ceiling:'No native owner operation'},confirmation:null,closed:false,status:'candidate',authority_effect:'none'};
 let sequence=0;
 async function invoke(entry,input){const prepared=runtime.prepareCommand(runtime.entry(entry),wire(input),{client_key:'remediation-'+(++sequence)});try{const a=await runtime.authorize(actors.get(entry),prepared);assert.equal(a.ok,true,JSON.stringify(a));const t=await runtime.consume(a.value,prepared);assert.equal(t.ok,true);return await runtime.executeCommand(t.value);}finally{runtime.disposePrepared(prepared);}}
 const begin=await invoke('Define.BeginPreparationEntry',{id:'91',session,source_digest:digest});assert.equal(begin.outcome.kind,'Returned');checks.push('persisted-run');
 for(const [name,patch,code] of [
  ['foreign-session',{session:{...session,scope:{...session.scope,project:'project:other'}}},'preparation-session-mismatch'],
  ['wrong-source',{source_digest:'0'.repeat(64)},'preparation-source-mismatch'],
  ['absent-run',{id:'999'},'preparation-missing'],
  ['invalid-attempt',{stageAttempt:'0'},'invalid-stage-attempt']]){
  const r=await invoke('Define.PrepareCandidateEntry',{id:'91',session,source_digest:digest,stageAttempt:'1',...patch});assert.equal(r.ok,true,JSON.stringify(r));assert.equal(r.outcome.kind,'Rejected',JSON.stringify(r));assert.equal(r.outcome.code,code);checks.push('negative:'+name);
 }
 const first=await invoke('Define.PrepareCandidateEntry',{id:'91',session,source_digest:digest,stageAttempt:'1'}),second=await invoke('Define.PrepareCandidateEntry',{id:'91',session,source_digest:digest,stageAttempt:'2'});assert.equal(first.outcome.kind,'Returned');assert.equal(second.outcome.kind,'Returned');checks.push('distinct-attempts');
 const forged=structuredClone(first.outcome.value);forged.request.goal='Forged postimage';
 const rejected=await invoke('Define.ContinuePreparationEntry',{id:'91',stageResult:forged,stageRevision:'1'});assert.equal(rejected.outcome.kind,'Rejected');assert.equal(rejected.outcome.code,'candidate-result-mismatch');checks.push('negative:forged-continuation');
 const complete=await invoke('Define.ContinuePreparationEntry',{id:'91',stageResult:first.outcome.value,stageRevision:'1'});assert.equal(complete.outcome.kind,'Returned');assert.equal(complete.outcome.value.kind,'complete');checks.push('exact-continuation');
 relay=runtime.openEventRelay();const delivered=[];
 for(let index=0;index<2;index++){const claim=relay.claimNext(300000);assert(claim);const receipt=await relay.deliver(claim,inbox);assert.equal(receipt.kind,'committed',JSON.stringify(receipt));const replay=await relay.deliver(claim,inbox);assert.equal(replay.kind,'replayed');relay.ack(claim,replay.receipt);delivered.push(receipt.kind);checks.push('candidate-attempt-'+(index+1)+'-delivered-and-replayed');}
 assert.equal(relay.claimNext(1000),null);checks.push('no-extra-event');
 const {DatabaseSync}=await import('node:sqlite');const table=inbox.inspect().storage.tables.find(row=>row.entity==='LabIntegration.ReceiveCandidate.ReviewRequest');const db=new DatabaseSync(receiver.storePath,{readOnly:true});let count;try{count=db.prepare('SELECT COUNT(*) AS n FROM "'+table.physical_name.replaceAll('"','""')+'"').get().n;}finally{db.close();}assert.equal(count,2);checks.push('two-exact-review-identities');
 const report={schema_version:'define-remediation-workflow-verification/v1',status:'PASS',source:artifact.source,checks,check_count:checks.length,fixture_auth_only:true,python_define_engine_imported:false,review_requests:count};writeFileSync(path.join(root,'.local/REMEDIATION-WORKFLOW-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{const errors=[];for(const close of [()=>relay?.close(),()=>workflow?.close(),()=>inbox?.close(),()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined])try{await close();}catch(error){errors.push(error);}if(errors.length)throw new AggregateError(errors,'Remediation cleanup failed');}
