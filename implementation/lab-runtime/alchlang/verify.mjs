#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,symlinkSync,realpathSync,rmSync,chmodSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {build,node,root,sha,selection,inputs} from './build.mjs';
import {implementationRoot as craftRoot} from '../../../craft/implementation/source-bindings.mjs';
import {nativeCall,fixtureStagePort,capabilitySha} from './ports/native-fixture.mjs';
if(realpathSync(process.execPath)!==realpathSync(node)){
 const child=spawnSync(node,[import.meta.filename,...process.argv.slice(2)],{stdio:'inherit'});if(child.error)throw child.error;process.exit(child.status??1);
}
const mode=process.argv[2]??'verify';assert(['build','verify'].includes(mode));
const artifact=build();
if(mode==='build'){console.log(JSON.stringify({status:'BUILT',source:artifact.source,alch_files:1+selection.additional.length,output:artifact.output}));process.exit(0);}
const fixture=await import(pathToFileURL(path.join(craftRoot,'cli/dist/generic/testing.js')).href);
const workflowSdk=await import(pathToFileURL(path.join(craftRoot,'cli/dist/generic/workflow-worker.js')).href);
const dependency=path.join(root,'.local/node_modules/@domainspec-v2');mkdirSync(dependency,{recursive:true});const peer=path.join(dependency,'cli');if(!existsSync(peer))symlinkSync(path.join(craftRoot,'cli'),peer,'dir');assert.equal(realpathSync(peer),path.join(craftRoot,'cli'));
const {createGeneratedApplicationOwner}=await import(pathToFileURL(path.join(artifact.output,'application.mjs')).href);
const owner=createGeneratedApplicationOwner(),directory=mkdtempSync(path.join(root,'.local/qualification-'));
const wire=value=>new Uint8Array(Buffer.from(JSON.stringify(value))),plain=value=>JSON.parse(JSON.stringify(value));
const checks=[],nativeHomes=[],nativeEvidence=[],openDrivers=new Set();
const check=(name,fn)=>{fn();checks.push(name);console.log('PASS '+name);};
let handle,auth,runtime,inbox,relay;
try{
 handle=await owner.prepare();const review=owner.review(handle,'lab-model-qualification-fixture');owner.accept(handle,{decision_id:'lab-model-qualification-fixture',owner:'lab-model-qualification-fixture',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,'model-review.json'));
 const entries=[...readFileSync(path.join(root,'lab.alch'),'utf8').matchAll(/^entry (Lab\.\w+):/gm)].map(match=>match[1]);
 auth=await fixture.createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),subjects:[{id:'lab-model-fixture',evidence:'isolated-fixture-evidence',session:'isolated-fixture-session'}],grants:entries.map(entry=>({subject:'lab-model-fixture',entry})),sessionTtlSeconds:7200});
 const setup=await fixture.prepareGenericFixtureRuntime(owner,handle,{service:'LabService',ownedDirectory:path.join(directory,'durable-coordinator'),nativeAuth:auth.nativeAuth});runtime=setup.runtime;fixture.loadGenericFixture(setup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
 const audit=await fixture.prepareGenericFixtureRuntime(owner,handle,{service:'LabAuditService',ownedDirectory:path.join(directory,'durable-audit'),nativeAuth:auth.nativeAuth});inbox=audit.runtime;fixture.loadGenericFixture(audit.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));auth.bindReceiver(inbox,'LabAudit.ReceiveOutcomeEntry');
 relay=runtime.openEventRelay();
 async function read(entry,args,noActor=false){
  const prepared=runtime.prepareInput(runtime.entry(entry),wire(args));
  try{
   const allowed=await runtime.authorize(noActor?null:auth.actor(runtime,'lab-model-fixture',entry),prepared);if(!allowed.ok)return {denied:true,error:allowed.error};
   const transferred=await runtime.consume(allowed.value,prepared);assert.equal(transferred.ok,true,JSON.stringify(transferred));return plain(await runtime.execute(transferred.value));
  }finally{runtime.disposePrepared(prepared);}
 }
 const returned=result=>{assert.equal(result.ok,true,JSON.stringify(result));assert.equal(result.outcome.kind,'Returned',JSON.stringify(result));return result.outcome.value;};
 const rejected=(result,code)=>{assert.equal(result.ok,true,JSON.stringify(result));assert.equal(result.outcome.kind,'Rejected',JSON.stringify(result));assert.equal(result.outcome.code,code);};
 function seed(id,mode='normal'){
  const home=mkdtempSync(path.join(tmpdir(),'cal-lab-alch-fixture-'));chmodSync(home,0o700);nativeHomes.push(home);
  const data=nativeCall(home,'seed',{id,mode});return {id,home,...data};
 }
 const first=seed('1');const request=first.request,branch=request.branch;
 check('original native owner reviews and signs the actual User Journey plus Work proposal',()=>{assert.equal(first.review.target_count,2);assert.equal(request.checks.signature,'SignatureVerified');assert.equal(first.original_definition.sha256,'693045f6c86f0faa8b168d072e473bbb48f1e75cb71d440fc559c7440f147fe7');});
 const definitionInput=first.creations.definition.request,recordInput=first.creations.record.request;
 const definitionDraft=returned(await read('Lab.CreateDefinitionEntry',{request:definitionInput,branch}));
 check('CreateDefinition returns the exact native-validated candidate without authority',()=>assert.deepEqual(definitionDraft,first.creations.definition.draft));
 const recordDraft=returned(await read('Lab.CreateRecordEntry',{request:recordInput,branch}));
 check('CreateRecord preserves the original record binding and Work context',()=>assert.deepEqual(recordDraft,first.creations.record.draft));
 const workDefinition=returned(await read('Lab.CreateDefinitionEntry',{request:{...definitionInput,scope:'work',work:'work:local-definition'},branch}));
 check('work-specific definitions remain separate from project authority definitions',()=>{assert.equal(definitionDraft.location,'ProjectDefinitions');assert.equal(workDefinition.location,'WorkDefinitions');assert.equal(workDefinition.work,'work:local-definition');});
 const preparedCreation=returned(await read('Lab.PrepareCreationEntry',{branch,drafts:[recordDraft,definitionDraft],proposal_id:request.proposal.proposal_id,original:request.proposal.original}));
 check('PrepareCreation builds an unsigned exact-scope multi-target proposal',()=>{assert.equal(preparedCreation.approval,null);assert.equal(preparedCreation.expected_head,branch.head.transaction_digest);assert.equal(preparedCreation.source_snapshot,branch.sources.snapshot);assert.deepEqual(preparedCreation.targets,[recordDraft.target,definitionDraft.target]);});
 rejected(await read('Lab.PrepareCreationEntry',{branch,drafts:[recordDraft,recordDraft],proposal_id:'duplicate-creation',original:request.proposal.original}),'invalid-creation-drafts');checks.push('creation bundle refuses duplicate identities and Decisions');console.log('PASS '+checks.at(-1));
 rejected(await read('Lab.CreateRecordEntry',{request:{...recordInput,validation:{...recordInput.validation,semantic_kind:'typed-relation'}},branch}),'use-specialized-creation');checks.push('specialized type and relation creation cannot use the generic record route');console.log('PASS '+checks.at(-1));
 const mutations=[
  ['wrong project',{project:'project:other'},'project-mismatch'],
  ['missing Work',{scope:'work',work:null},'work-required'],
  ['ambiguous shared scope',{work:'work:other'},'project-scope-has-work'],
  ['stale validation',{validation:{...definitionInput.validation,head:'0'.repeat(64)}},'creation-validation-stale'],
  ['unbound original bytes',{source:{...definitionInput.source,sha256:'0'.repeat(64)}},'creation-body-unbound'],
  ['historical carrier',{validation:{...definitionInput.validation,current_carrier:false}},'carrier-not-current'],
  ['invalid schema',{validation:{...definitionInput.validation,schema_valid:false}},'creation-schema-invalid'],
  ['existing identity',{validation:{...definitionInput.validation,identity_available:false}},'creation-identity-exists'],
  ['self-admitted definition',{validation:{...definitionInput.validation,candidate_payload:false}},'creation-requires-candidate'],
 ];
 for(const [name,patch,code]of mutations){const result=await read('Lab.CreateDefinitionEntry',{request:{...definitionInput,...patch},branch});check('definition creation refuses '+name,()=>rejected(result,code));}
 rejected(await read('Lab.CreateRecordEntry',{request:definitionInput,branch}),'use-definition-creation');checks.push('generic record creation cannot bypass definition handling');console.log('PASS '+checks.at(-1));
 rejected(await read('Lab.CreateRecordEntry',{request:{...recordInput,validation:{...recordInput.validation,authored_target:false}},branch}),'creation-derived-target');checks.push('record creation refuses native generated consequences');console.log('PASS '+checks.at(-1));
 const drafts=nativeCall(first.home,'creation-checks');nativeEvidence.push(drafts);
 check('draft-only command creates exact definition/record files and reviewable unsigned proposals',()=>{assert.equal(drafts.definition_created,true);assert.equal(drafts.record_cli_created,true);assert.equal(drafts.unsigned_proposals_reviewable,true);assert.equal(drafts.approval_required,true);assert.equal(drafts.definition_original_sha256,first.original_definition.sha256);});
 check('creation idempotence and exact-byte inspection preserve authored input',()=>{assert.equal(drafts.idempotent_creation,true);assert.equal(drafts.exact_byte_tamper_refused,true);});
 check('native creation validation refuses malformed, mis-scoped and existing inputs',()=>assert.equal(drafts.blocked.length,7));
 check('interrupted creation preserves incomplete output and refuses overwrite',()=>assert.equal(drafts.incomplete_publication_preserved,true));
 check('draft publication does not advance native HEAD or update a registry',()=>{assert.equal(drafts.native_head_unchanged,true);assert.equal(drafts.native_sequence,0);assert.equal(drafts.registry_updated,false);});
 const types=nativeCall(seed('4').home,'artifact-type-checks');nativeEvidence.push(types);
 const typeDraft=returned(await read('Lab.CreateArtifactTypeEntry',{request:types.type.request,branch:types.type.branch}));
 check('CreateArtifactType returns the native-validated descriptor/schema/contract draft',()=>assert.deepEqual(typeDraft,types.type.draft));
 const typeProposal=returned(await read('Lab.PrepareCreationEntry',{branch:types.type.branch,drafts:[typeDraft],proposal_id:'register-work-type',original:types.type.original}));
 check('PrepareCreation preserves registered schema materials and exact native instance contract',()=>{assert.deepEqual(typeProposal.schemas,typeDraft.schemas);assert.deepEqual(typeProposal.targets[0].contract,types.type.request.contract);assert.equal(typeProposal.approval,null);});
 const noTypeActor=await read('Lab.CreateArtifactTypeEntry',{request:types.type.request,branch:types.type.branch},true);
 check('CreateArtifactType requires an authenticated actor at its protected Entry',()=>assert.equal(noTypeActor.denied,true));
 for(const [name,patch,code]of [
  ['host validation',{registration_valid:false},'artifact-type-binding-invalid'],
  ['schema digest',{schema:{...types.type.request.schema,sha256:'0'.repeat(64)}},'artifact-type-binding-invalid'],
  ['schema selector',{schema:{...types.type.request.schema,selector:'#/other'}},'artifact-type-binding-invalid'],
  ['unbound descriptor',{creation:{...types.type.request.creation,source:{...types.type.request.creation.source,sha256:'0'.repeat(64)}}},'creation-body-unbound'],
  ['stale validation',{creation:{...types.type.request.creation,validation:{...types.type.request.creation.validation,head:'0'.repeat(64)}}},'creation-validation-stale'],
 ]){const result=await read('Lab.CreateArtifactTypeEntry',{request:{...types.type.request,...patch},branch:types.type.branch});check('Artifact Type model refuses '+name,()=>rejected(result,code));}
 const registeredDraft=returned(await read('Lab.CreateRecordEntry',{request:types.record.request,branch:types.record.branch}));
 check('CreateRecord accepts a newly admitted inline schema with a custom identity field',()=>assert.deepEqual(registeredDraft,types.record.draft));
 check('Artifact Type command publishes inert drafts with exact originals and idempotent replay',()=>{assert.equal(types.type_cli_created,true);assert.equal(types.drafts_preserve_head,true);assert.equal(types.exact_originals_retained,true);assert.notEqual(types.original_schema_sha256,types.registered_schema_from_native_transaction.sha256);assert.equal(types.idempotent_before_and_after_admission,true);assert.equal(types.authority_effect_of_drafts,'none');});
 check('Artifact Type package detects tampering in descriptor, schema, contract and proposal',()=>assert.equal(types.all_draft_members_tamper_refused,true));
 check('native Artifact Type creation refuses invalid bindings, schemas, Definitions, owner and identity',()=>assert.equal(types.blocked.length,8));
 check('registered records refuse invalid discriminator, missing fields, duplicates and withdrawn carrier',()=>{assert.equal(types.record_blocked.length,4);assert(types.record_blocked.some(item=>item.name==='discriminator'&&item.reason==='carrier discriminator mismatch'));});
 check('fresh-process schema resolution binds the committed native transaction and selected schema',()=>{assert.equal(types.fresh_process_replay,true);assert.equal(types.record_native_sequence,'2');assert.equal(types.registered_schema_from_native_transaction.digest_kind,'native-json-sha256');assert.equal(types.registered_schema_from_native_transaction.provenance_digest,types.type_transaction);assert.equal(types.registered_schema_from_native_transaction.selector,null);});
 const selected=returned(await read('Lab.SelectContextEntry',{branch,project:branch.project,store:branch.store}));check('SelectContext preserves the actual project and native branch',()=>assert.deepEqual(selected,branch));
 const missing=await read('Lab.SelectContextEntry',{branch,project:branch.project,store:branch.store},true);check('missing fixture actor is denied at the protected Entry',()=>assert.equal(missing.denied,true));
 check('context selection refuses another project',()=>{});rejected(await read('Lab.SelectContextEntry',{branch,project:'project:other',store:branch.store}),'project-mismatch');
 rejected(await read('Lab.SelectContextEntry',{branch,project:branch.project,store:'store:other'}),'store-mismatch');checks.push('context selection refuses another store');console.log('PASS '+checks.at(-1));
 const reviewPlan=returned(await read('Lab.ReviewProposalEntry',{branch,proposal:request.proposal,checks:request.checks}));check('review remains inert and requires an exact owner approval',()=>{assert.equal(reviewPlan.target_count,'2');assert.equal(reviewPlan.approval_required,true);assert.equal(reviewPlan.repository_effect,'none');});
 const approved=returned(await read('Lab.AcknowledgeApprovalEntry',{request:{...request,phase:'AwaitingApproval'}}));check('AdmissionLifecycle records readiness from verified host approval evidence',()=>assert.equal(approved.phase,'ReadyToDispatch'));
 const ready=returned(await read('Lab.PrepareDispatchEntry',{request}));check('ApplyEligibility permits the signed exact current proposal',()=>assert.deepEqual(ready,request));
 rejected(await read('Lab.PrepareDispatchEntry',{request:{...request,phase:'AwaitingApproval'}}),'admission-not-ready');checks.push('AdmissionLifecycle refuses dispatch before approval readiness');console.log('PASS '+checks.at(-1));
 const negative=nativeCall(first.home,'negative-cases');
 const expected={'challenge-mismatch':'policy-mismatch'};
 for(const example of negative.cases){
  const result=await read('Lab.PrepareDispatchEntry',{request:example.request});
  check('native/model refusal agreement: '+example.name,()=>{assert.equal(example.native_allowed,false);rejected(result,expected[example.name]??example.name);});
 }
 for(const [outcome,next]of [['Unknown','InspectOriginalOperation'],['NotDispatched','ObtainFreshPermission'],['Committed','PreserveReceipt'],['Replayed','PreserveReceipt'],['Refused','PreserveRefusal']]){
  const result=returned(await read('Lab.ResolveOutcomeEntry',{outcome}));check('recovery continuation: '+outcome,()=>assert.equal(result,next));
 }
 async function deliver(id){
  const claim=relay.claimNext(300000);assert(claim,'Expected observed outcome Event for '+id);
  const first=await relay.deliver(claim,inbox);assert.equal(first.kind,'committed',JSON.stringify(first));
  const again=await relay.deliver(claim,inbox);assert.equal(again.kind,'replayed',JSON.stringify(again));relay.ack(claim,again.receipt);
  check('native outcome Event '+id+' commits once and replays its inbox receipt',()=>assert.equal(relay.claimNext(1000),null));
 }
 function actors(){return new Map(entries.map(entry=>[entry,auth.actor(runtime,'lab-model-fixture',entry)]));}
 const stageProfile=JSON.parse(readFileSync(path.join(root,'contracts/workflow-profile.json'))).stages[0];assert.equal(stageProfile.capability_sha256,capabilitySha());
 async function workflowRun(data){
  const stage=fixtureStagePort(data.home,stageProfile.capability_sha256);
  const registered=workflowSdk.registerGenericWorkflowStagePort(owner,handle,runtime,stageProfile.capability_binding,stage.implementation);
  const stagePorts=new Map([[stageProfile.capability_binding,registered]]),journal=path.join(directory,'workflow-'+data.id);
  let driver=await owner.openWorkflow(handle,{runtime,actors:actors(),stagePorts,journal:{directory:journal,mode:'create'}});openDrivers.add(driver);
  const start=await driver.scheduleStart(wire({id:data.id,request:data.request}),'local-admission-'+data.id);assert(start);
  let claim=driver.claimNext(300000);assert(claim);
  let progress=await driver.advance(claim);
  return {data,stage,start,journal,stagePorts,get driver(){return driver;},get progress(){return progress;},async advance(){assert(progress.active_claim);progress=await driver.advance(progress.active_claim);return progress;},async reopen(){await driver.close();openDrivers.delete(driver);driver=await owner.openWorkflow(handle,{runtime,actors:actors(),stagePorts,journal:{directory:journal,mode:'reopen'}});openDrivers.add(driver);},async close(){await driver.close();openDrivers.delete(driver);}};
 }
 const normal=await workflowRun(first);
 check('recoverable Workflow executes the original native signed admission',()=>{assert.equal(normal.progress.state,'step-committed',JSON.stringify(normal.progress));assert.equal(normal.stage.calls.execute,1);});
 await normal.reopen();await normal.advance();
 check('workflow resumes its committed native result after journal reopen',()=>{assert.equal(normal.progress.kind,'completed',JSON.stringify(normal.progress));assert.equal(normal.stage.calls.execute,1);});
 const row=returned(await read('Lab.ReadOutcomeEntry',{id:'1',stageRevision:'1'}));assert(row);
 check('ReadOutcome Query retains the observed native receipt and both history cursors',()=>{assert.equal(row.observation.outcome,'Committed');assert.equal(row.observation.sequence,'1');assert.equal(row.observation.semantic_cursor,'8');assert.equal(row.observation.governance_cursor,'8');assert(row.observation.receipt);});
 await deliver('1');await normal.close();
 const observed=nativeCall(first.home,'observations');nativeEvidence.push(observed);
 check('original native replay is idempotent and reconstructs one local transaction',()=>{assert.equal(observed.native_repeat,true);assert.equal(observed.sequence,'1');assert.equal(observed.cursor,'8');});
 const exactRepeat=returned(await read('Lab.PrepareDispatchEntry',{request:observed.repeat_request}));
 check('exact committed replay precedes stale expected-HEAD validation',()=>assert.equal(exactRepeat.existing,'SameCommittedBytes'));
 const subject=returned(await read('Lab.ResolveSubjectEntry',{project:branch.project,requested:observed.subject.identity_ref,subject:observed.subject}));
 check('catalog standing and authored candidate posture remain independent',()=>{assert.equal(subject.standing,'LocalCurrent');assert.equal(subject.candidate_payload,observed.subject.candidate_payload);assert.equal(subject.source.sha256,first.original_definition.sha256);});
 rejected(await read('Lab.ResolveSubjectEntry',{project:'project:other',requested:subject.version,subject}),'project-mismatch');checks.push('catalog refuses cross-project subject selection');console.log('PASS '+checks.at(-1));
 const traversal={root:'Lifecycle',direction:'both',depth:'1',max_nodes:'20',max_edges:'30'};
 const bounded=returned(await read('Lab.PlanTraversalEntry',{request:traversal,branch:observed.branch}));check('ontology planning preserves explicit bounded traversal without replay authority',()=>{assert.equal(bounded.confirmed_paths_allowed,true);assert.equal(bounded.replay_source,false);assert.equal(bounded.authority_effect,'none');});
 const staleBranch={...observed.branch,sources:{...observed.branch.sources,posture:'Stale'}};
 const stale=returned(await read('Lab.PlanTraversalEntry',{request:traversal,branch:staleBranch}));check('stale ontology sources yield no confirmed path permission',()=>{assert.equal(stale.confirmed_paths_allowed,false);assert.equal(observed.native_stale_confirmed_connections,'0');});
 rejected(await read('Lab.PlanTraversalEntry',{request:{...traversal,depth:'21'},branch}),'traversal-out-of-bounds');checks.push('ontology traversal rejects excessive depth');console.log('PASS '+checks.at(-1));
 const session=returned(await read('Lab.OpenContextEntry',{session_id:'session:model',branch:observed.branch,subject:request.proposal.targets[0].version,subject_resolved:true,now:'100',ttl:'10'}));
 const viewed=returned(await read('Lab.UseContextEntry',{view:session,branch:observed.branch,now:'105'}));check('source/head-bound session context is usable before expiry',()=>assert.equal(viewed.phase,'SessionOpen'));
 const note=returned(await read('Lab.AddNoteEntry',{view:session,branch:observed.branch,now:'105',text:'Ephemeral qualification note'}));check('session note is a process value without durable Entity storage',()=>assert.equal(note.memory.length,1));
 const closed=returned(await read('Lab.CloseContextEntry',{view:note}));check('closing a session erases modeled short memory',()=>{assert.equal(closed.phase,'SessionClosed');assert.deepEqual(closed.memory,[]);});
 rejected(await read('Lab.UseContextEntry',{view:note,branch:observed.branch,now:'110'}),'session-expired');checks.push('expired session context is refused');console.log('PASS '+checks.at(-1));
 const expired=returned(await read('Lab.ExpireContextEntry',{view:note,now:'110'}));check('expiry erasure agrees with original native Session behavior',()=>{assert.equal(expired.phase,'SessionExpired');assert.deepEqual(expired.memory,[]);assert.equal(observed.native_session_expired_and_erased,true);});
 rejected(await read('Lab.UseContextEntry',{view:{...session,head:branch.head.transaction_digest},branch:observed.branch,now:'105'}),'session-head-changed');checks.push('a changed native HEAD invalidates the old context');console.log('PASS '+checks.at(-1));
 rejected(await read('Lab.UseContextEntry',{view:session,branch:staleBranch,now:'105'}),'session-source-stale');checks.push('source drift invalidates session context');console.log('PASS '+checks.at(-1));
 const afterHead=await workflowRun(seed('2','crash-after-head'));
 check('native interruption after HEAD suspends the unobserved workflow outcome',()=>{assert.equal(afterHead.progress.kind,'suspended-unknown');assert.equal(afterHead.stage.calls.execute,1);});
 await afterHead.reopen();await afterHead.advance();await afterHead.advance();
 check('fresh native inspection recovers the committed receipt without redispatch',()=>{assert.equal(afterHead.progress.kind,'completed',JSON.stringify(afterHead.progress));assert.equal(afterHead.stage.calls.execute,1);});
 await deliver('2');nativeEvidence.push(nativeCall(afterHead.data.home,'recover'));await afterHead.close();
 const beforeHead=await workflowRun(seed('3','crash-before-head'));
 check('native interruption before HEAD remains unknown while staged files exist',()=>assert.equal(beforeHead.progress.kind,'suspended-unknown'));
 await beforeHead.reopen();await beforeHead.advance();check('unresolved native operation is inspected without a second dispatch',()=>{assert.equal(beforeHead.progress.kind,'suspended-unknown');assert.equal(beforeHead.stage.calls.execute,1);});
 const recovery=nativeCall(beforeHead.data.home,'recover');nativeEvidence.push(recovery);check('native recovery preserves HEAD and proves no committed admission',()=>{assert.equal(recovery.head_preserved,true);assert.equal(recovery.inspection.result.outcome,'NotDispatched');assert.equal(recovery.inspection.result.sequence,'0');});
 await beforeHead.advance();await beforeHead.advance();check('proven no-effect returns to review rather than automatic retry',()=>{assert.equal(beforeHead.progress.kind,'needs-review',JSON.stringify(beforeHead.progress));assert.equal(beforeHead.stage.calls.execute,1);});
 await deliver('3');await beforeHead.close();
 const {DatabaseSync}=await import('node:sqlite');const db=new DatabaseSync(audit.storePath,{readOnly:true});let count;
 try{const table=inbox.inspect().storage.tables.find(table=>table.entity==='LabAudit.OutcomeInbox');assert(table);count=db.prepare('SELECT COUNT(*) AS n FROM "'+table.physical_name.replaceAll('"','""')+'"').get().n;}finally{db.close();}
 check('audit inbox contains one observation per native operation after Event replay',()=>assert.equal(count,3));
 const report={schema_version:'cal.lab.authored-model-qualification/v1',status:'PASS',completed_at:new Date().toISOString(),model_sha256:artifact.source,toolchain:artifact.toolchain,alch_files:1+selection.additional.length,checks,check_count:checks.length,fixture_directory:directory,native_evidence:nativeEvidence,fixture_auth_only:true,native_ed25519_verification:true,native_owner_operations_scope:'fresh disposable fixture branches only',native_runtime_replaced:false,production_stores_accessed:false,external_native_fixture_keys_removed_on_close:true,source_sha256:Object.fromEntries([...inputs,'build.mjs','verify.mjs','create.py'].map(name=>[name,sha(readFileSync(path.join(root,name)))]))};
 writeFileSync(path.join(root,'VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks:checks.length,fixture_directory:directory}));
}finally{
 const errors=[];for(const close of [...openDrivers].map(driver=>()=>driver.close()).concat([()=>relay?.close(),()=>inbox?.close(),()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined]))try{await close();}catch(error){errors.push(error);}
 for(const home of nativeHomes)try{rmSync(home,{recursive:true,force:true});}catch(error){errors.push(error);}
 if(errors.length)throw new AggregateError(errors,'Lab model qualification cleanup failed');
}
