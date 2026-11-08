#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,symlinkSync,realpathSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {implementationRoot as craftRoot} from '../../../craft/implementation/source-bindings.mjs';
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
 const ids=['Define.BeginPreparationEntry','Define.ContinuePreparationEntry','Define.PrepareCandidateEntry'];
 auth=await fixture.createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),subjects:[{id:'workflow-fixture',evidence:'isolated-workflow-evidence',session:'isolated-workflow-session'}],grants:ids.map(entry=>({subject:'workflow-fixture',entry})),sessionTtlSeconds:7200});
 const setup=await fixture.prepareGenericFixtureRuntime(owner,handle,{service:'DefineService',ownedDirectory:path.join(directory,'durable-define-store'),nativeAuth:auth.nativeAuth});runtime=setup.runtime;
 fixture.loadGenericFixture(setup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
 const receiver=await fixture.prepareGenericFixtureRuntime(owner,handle,{service:'LabIntegrationService',ownedDirectory:path.join(directory,'durable-review-inbox'),nativeAuth:auth.nativeAuth});inbox=receiver.runtime;
 fixture.loadGenericFixture(receiver.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
 const receiverEntry='LabIntegration.ReceiveCandidateEntry';auth.bindReceiver(inbox,receiverEntry);
 const actors=new Map(ids.map(id=>[id,auth.actor(runtime,'workflow-fixture',id)]));
 const python=(file,input,args=[])=>{const child=spawnSync('python3',['-B',file,...args],{encoding:'utf8',input:input===undefined?undefined:JSON.stringify(input),maxBuffer:4*1024*1024});assert.equal(child.status,0,child.stderr||child.stdout);return JSON.parse(child.stdout);};
 const example=python(path.resolve(root,'runtime/examples/request.py'),undefined,['user-journey']);
 const project='project:context-management',work='work:user-journey-definition';
 const context={project,work,source_snapshot:'fixture:exact-user-journey',status:'Sufficient',explanation:'Explicit qualification context only',evidence:[]};
 const imported=python(path.resolve(root,'runtime/pack-port.py'),{operation:'import-request',request:example.request,project,work,context});
 const reference=await import(new URL('./runtime/runtime.mjs',import.meta.url));let session=null;
 for(const payload of imported.payloads)session=await reference.transition(session,{command_id:'seed-'+(session?.revision??'0'),session_id:example.request.request_id,project,work,actor:'example:fixture-author',expected_revision:session?.revision??'0',payload});
 const journal=path.join(directory,'durable-workflow-journal');
 workflow=await owner.openWorkflow(handle,{runtime,actors,journal:{directory:journal,mode:'create'}});
 const start=await workflow.scheduleStart(wire({id:'1',session,source_digest:artifact.source}),'user-journey-preparation');assert(start);
 let claim=workflow.claimNext(300000);assert(claim);
 let progress=await workflow.advance(claim);
 check('Workflow executes the checked PrepareCandidate Operation',()=>{assert.equal(progress.state,'step-committed',JSON.stringify(progress));});
 const persisted=workflow.inspect(start.instance_sha256);
 const outputs=persisted.history.flatMap(row=>{if(!row.commitment_json)return [];const record=JSON.parse(row.commitment_json);return record.output_canonical_json?[JSON.parse(record.output_canonical_json)]:[];});
 const prepared=outputs.find(output=>output.request?.schema_version==='cal.define.prepare-request/v3');assert(prepared,JSON.stringify(persisted));
 check('workflow stores the complete typed candidate request and source binding',()=>{assert.equal(prepared.id,'1');assert.equal(prepared.source_digest,artifact.source);assert.equal(prepared.request.authority_effect,'none');});
 const pack=python(path.join(root,'qualify-pack.py'),prepared.request);
 check('workflow output materializes and reconstructs exact User Journey bytes',()=>{assert.equal(pack.reconstructed_exactly,true);assert.equal(pack.package_members,9);assert.equal(pack.pack_status,'candidate');});
 await workflow.close();workflow=await owner.openWorkflow(handle,{runtime,actors,journal:{directory:journal,mode:'reopen'}});
 progress=await workflow.advance(progress.active_claim);
 check('reopened Workflow resumes its committed stage without preparing again',()=>{assert.equal(progress.kind,'completed',JSON.stringify(progress));assert.equal(workflow.inspect(start.instance_sha256).state,'completed');});
 relay=runtime.openEventRelay();const delivery=relay.claimNext(300000);assert(delivery);
 await assert.rejects(()=>relay.deliver({...delivery},inbox));checks.push('copied event claims cannot acquire relay custody');console.log('PASS '+checks.at(-1));
 const delivered=await relay.deliver(delivery,inbox);
 check('CandidatePrepared Event reaches the separate review inbox',()=>assert.equal(delivered.kind,'committed',JSON.stringify(delivered)));
 const redelivery=await relay.deliver(delivery,inbox);
 check('event redelivery replays the original inbox receipt',()=>assert.equal(redelivery.kind,'replayed',JSON.stringify(redelivery)));
 relay.ack(delivery,redelivery.receipt);
 check('acknowledged preparation has no second event to dispatch',()=>assert.equal(relay.claimNext(1000),null));
 const {DatabaseSync}=await import('node:sqlite');
 const count=(store,entity)=>{const schema=(store===setup.storePath?runtime:inbox).inspect().storage,table=schema.tables.find(row=>row.entity===entity);assert(table);const db=new DatabaseSync(store,{readOnly:true});try{return db.prepare('SELECT COUNT(*) AS n FROM "'+table.physical_name.replaceAll('"','""')+'"').get().n;}finally{db.close();}};
 check('restart and event replay retain one prepared candidate and one review request',()=>{assert.equal(count(setup.storePath,'Define.PreparedCandidate'),1);assert.equal(count(receiver.storePath,'LabIntegration.ReceiveCandidate.ReviewRequest'),1);});
 // A rejected preparation cannot emit another event or claim successful candidate work.
 const badSession={...session,context_evaluation:null};
 const rejected=await workflow.scheduleStart(wire({id:'2',session:badSession,source_digest:artifact.source}),'missing-context-preparation');assert(rejected);
 claim=workflow.claimNext(300000);assert(claim);const refusal=await workflow.advance(claim);
 check('PreparationEligibility stops workflow progression for missing context',()=>{assert.notEqual(refusal.state,'step-committed');assert.notEqual(workflow.inspect(rejected.instance_sha256).state,'completed');assert.equal(count(setup.storePath,'Define.PreparedCandidate'),1);assert.equal(relay.claimNext(1000),null);});
 const report={schema_version:'cal.define.module-use-case-preparation-qualification/v1',status:'PASS',completed_at:new Date().toISOString(),model_sha256:artifact.source,toolchain:artifact.toolchain,alch_files:1+selection.additional.length,checks,check_count:checks.length,user_journey:pack,fixture_directory:directory,fixture_auth_only:true,lab_owner_operations_executed:false,default_cli_rebound:false,durable_workflow_state_is_cache:false,source_sha256:Object.fromEntries([...inputs,'build.mjs','verify-preparation.mjs','qualify-pack.py'].map(name=>[name,sha(readFileSync(path.join(root,name)))]))};
 writeFileSync(path.join(root,'PREPARATION-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks:checks.length,fixture_directory:directory}));
}finally{
 const errors=[];for(const close of [()=>relay?.close(),()=>workflow?.close(),()=>inbox?.close(),()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined])try{await close();}catch(error){errors.push(error);}
 if(errors.length)throw new AggregateError(errors,'Preparation qualification cleanup failed');
}
