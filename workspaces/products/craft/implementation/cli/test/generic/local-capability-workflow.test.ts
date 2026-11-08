/** Source-generated V2 Workflow checks over the original transaction/Auth/journal owners.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {spawnSync} from 'node:child_process';
import {buildEventSourceFixture} from '../composition/C12-source-fixture.mjs';
import {createGenericCompositionOwner,createGenericBundledApplicationOwner,requireGenericWorkflowRuntime} from '../../src/generic/public-sdk.js';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.js';
import {createGenericWorkflowWorker,workflowCompatibilitySha256,registerGenericWorkflowStagePort} from '../../src/generic/workflow-worker.js';
import {GenericWorkflowStore} from '../../src/generic/workflow-store.js';
import {canonicalJson,dataDigest} from '../../src/profile-engine/contracts.js';
import {exportGenericWorkflowTlaModel} from '../../src/generic/formal-workflow-tla.js';

const txHandlers=`    on-unique-conflict reject duplicate\n    on-proven-rollback fail storage-rolled-back\n    on-unknown-commit fail outcome-unknown`;
const entry=(name:string,operation:string,principal='operator')=>`entry Work.${name}:\n  invokes Work.${operation}\n  interaction request-response\n  access:\n    authenticated ${principal}\n    permission workflow.${name}\n    auth-resource workflow\n    auth-action ${name}\n    auth-scope workflow-test\n`;
function business(){return `module Work version 1

rule IsCurrent:
  input id UInt64
  expression id > 0

entity Start:
  id UInt64
  started Bool
  identity id

entity WorkResult:
  id UInt64
  ordinal UInt64
  attempt UInt64
  identity id, ordinal, attempt

entity Decision:
  id UInt64
  stageRevision UInt64
  ordinal UInt64
  kind String
  condition String
  deadline_ms UInt64
  reason String
  code String
  attempt UInt64
  maximum UInt64
  not_before_ms UInt64
  identity id, stageRevision, ordinal

query ReadWork:
  input id UInt64
  input ordinal UInt64
  input attempt UInt64
  source result WorkResult
  output optional<WorkResult>
  where result.id == id and result.ordinal == ordinal and result.attempt == attempt
  project result
  on-missing return none
  on-unavailable fail read-unavailable

operation Begin:
  input id UInt64
  output Start
  transaction Begin:
    atomic-participants Start
    create started Start:
      id <- id
      started <- true
${txHandlers}
  return started

operation First:
  input id UInt64
  input stageAttempt UInt64
  output WorkResult
  transaction First:
    atomic-participants WorkResult
    create result WorkResult:
      id <- id
      ordinal <- 1
      attempt <- stageAttempt
${txHandlers}
  return result

operation Second:
  input id UInt64
  input stageAttempt UInt64
  output WorkResult
  transaction Second:
    atomic-participants WorkResult
    create result WorkResult:
      id <- id
      ordinal <- 2
      attempt <- stageAttempt
${txHandlers}
  return result

operation NextKind:
  input id UInt64
  input ordinal UInt64
  input stageRevision UInt64
  input stageAttempt UInt64
  output String
  when ordinal == 2:
    return "complete"
  otherwise:
    when id == 2 and stageRevision == 1:
      return "wait"
    otherwise:
      when id == 2:
        return "complete"
      otherwise:
        when id == 3:
          return "cancel"
        otherwise:
          when id == 4 and stageAttempt == 1:
            return "retry"
          otherwise:
            when id == 5:
              return "unknown"
            otherwise:
              when id == 6:
                return "business-rejection"
              otherwise:
                return "advance"

operation Continue:
  input id UInt64
  input stageResult WorkResult
  input stageAttempt UInt64
  input stageRevision UInt64
  output Decision
  call kind NextKind(id=id,ordinal=stageResult.ordinal,stageRevision=stageRevision,stageAttempt=stageAttempt)
  transaction Decide:
    atomic-participants Decision
    create decision Decision:
      id <- id
      stageRevision <- stageRevision
      ordinal <- stageResult.ordinal
      kind <- kind
      condition <- "Work.Approved"
      deadline_ms <- ${Date.now()+600000}
      reason <- "review-required"
      code <- "business-rejected"
      attempt <- 2
      maximum <- 2
      not_before_ms <- 0
${txHandlers}
  return decision

${entry('BeginEntry','Begin','customer')}
${entry('FirstEntry','First')}
${entry('SecondEntry','Second')}
${entry('ContinueEntry','Continue')}
${entry('ReadEntry','ReadWork')}
workflow Flow:
  owner WorkService
  scope generated-recoverable
  profile contracts/workflow-profile.json
  input id UInt64
  correlation id
  durable-state Work.Start
  start Work.BeginEntry
  step first invokes Work.FirstEntry
  step second invokes Work.SecondEntry
  recovery needed-compensations-only reverse-completion
`;}
async function setup(kind='local'){
 const root=buildEventSourceFixture(),work=mkdtempSync(path.join(tmpdir(),'craft-r03-'));
 const base=JSON.parse(readFileSync(path.join(root,'contracts/selected-profile.json'),'utf8'));base.services=[{id:'WorkService',module:'Work'}];
 writeFileSync(path.join(root,'business.alch'),business());writeFileSync(path.join(root,'contracts/selected-profile.json'),JSON.stringify(base));
 // Actual test-owned implementation source identity; this is not a production lock.
 const capabilitySha=dataDigest({schema:'r03.fixture-stage-bytes/v1',kind,source:readFileSync(new URL(import.meta.url),'utf8')});
 const stages=['first','second'].map(name=>({name,kind,continuation_entry:'Work.ContinueEntry',maximum_attempts:2,deadline_ms:5000,...(kind==='local'?{}:{capability_binding:'Work.Native',capability_sha256:capabilitySha,stage_result_type:'Work.WorkResult'})}));
 const profile={schema_version:'craft.generic-workflow-profile/v2',workflow:'Work.Flow',base_event_profile_sha256:dataDigest(base),capabilities:[...base.capabilities,'Workflow','recoverable-workflow'],recovery:'needed-compensations-only/reverse-completion-v1',storage:'service-owned-fenced-workflow-journal/v1-candidate',stages};
 writeFileSync(path.join(root,'contracts/workflow-profile.json'),JSON.stringify(profile));
 const source=createGenericCompositionOwner(),h=await source.prepare({sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json')});
 const review=source.review(h,'r03');source.accept(h,{decision_id:'r03',owner:'r03',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'accepted.json'));
 const out=path.join(work,'generated');source.generate(h,{entry:'Work.BeginEntry',outputDirectory:out});
 const modulePath=path.join(out,'application.mjs'),bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1]!.split(';\nexport function')[0]!);
 const owner=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle),handle=await owner.prepare();
 const generatedReview=owner.review(handle,'r03-generated');owner.accept(handle,{decision_id:'r03-generated',owner:'r03-generated',outcome:'accepted',reviewed_digest:generatedReview.review_sha256},path.join(work,'generated-accepted.json'));
 const checked=requireGenericWorkflowRuntime(owner,handle).contract;
 assert.throws(()=>exportGenericWorkflowTlaModel(owner,handle),/InvalidWorkflow/);
 assert.equal(requireGenericWorkflowRuntime(owner,handle).baseApplication.event_bindings.length,0);
 assert.equal(requireGenericWorkflowRuntime(owner,handle).baseApplication.write_bindings.length,0);
 const ids=['Work.BeginEntry','Work.FirstEntry','Work.SecondEntry','Work.ContinueEntry','Work.ReadEntry'];
 const auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(work,'auth'),sessionTtlSeconds:7200,subjects:[{id:'actor',evidence:'actor-evidence',session:'actor-session'}],grants:ids.map(entry=>({subject:'actor',entry}))});
 const fixture=await prepareGenericFixtureRuntime(owner,handle,{service:'WorkService',ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});loadGenericFixture(fixture.fixture,Buffer.from(JSON.stringify({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]})));await fixture.runtime.close();
 const runtime=await owner.openRuntime(handle,{service:'WorkService',storePath:fixture.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
 const actors=new Map(ids.map(id=>[id,auth.actor(runtime,'actor',id)]));
 const journalFile=path.join(work,'journal.sqlite');let db=new DatabaseSync(journalFile);
 let journal=new GenericWorkflowStore(db,{store_id:'work-flow',owner_service:'WorkService',compatibility_sha256:workflowCompatibilitySha256(checked)});
 let nativeCalls=0,nativeMode='normal';const seen=new Map<string,Uint8Array>(),uncertain=new Set<string>(),nativeWait=new Map<string,{kind:'no-effect-retry';original_attempt:string;not_before_ms:number;deadline_ms:number}>(),ports=new Map();
 let dispatchStarted:(()=>void)|undefined,settleNative:(()=>void)|undefined;
 if(kind!=='local')ports.set('Work.Native',registerGenericWorkflowStagePort(owner,handle,runtime,'Work.Native',Object.freeze({capability_sha256:capabilitySha,assertCurrent(){},async inspect(r:any){r.assertCurrent();const key=r.instance_sha256+':'+r.step+':'+r.attempt;if(uncertain.has(key))return {kind:'unknown' as const};if(nativeWait.has(key))return nativeWait.get(key)!;const output=seen.get(key);return output?{kind:'observed' as const,output}:{kind:'not-dispatched' as const};},async execute(r:any){r.assertCurrent();nativeCalls++;const key=r.instance_sha256+':'+r.step+':'+r.attempt;if(nativeMode==='unknown'){uncertain.add(key);return {kind:'unknown' as const};}if(nativeMode==='no-effect'){const wait={kind:'no-effect-retry' as const,original_attempt:'effect-'+r.step+'-'+r.attempt,not_before_ms:Date.now()+2000,deadline_ms:r.deadline_ms};nativeWait.set(key,wait);return wait;}if(nativeMode==='delay'){dispatchStarted?.();await new Promise<void>(resolve=>{settleNative=resolve;});}const output=new Uint8Array(r.input);seen.set(key,output);return {kind:'observed' as const,output};},async retry(r:any){r.assertCurrent();const key=r.instance_sha256+':'+r.step+':'+r.attempt,waiting=nativeWait.get(key);assert.ok(waiting);assert.equal(r.retry_of,waiting.original_attempt);assert.ok(Date.now()>=waiting.not_before_ms);assert.ok(Date.now()<waiting.deadline_ms);nativeCalls++;nativeWait.delete(key);const output=new Uint8Array(r.input);seen.set(key,output);return {kind:'observed' as const,output};}})));
 const worker=()=>createGenericWorkflowWorker({source:checked,runtime,journal,journal_store_id:'work-flow',actors,...(kind==='local'?{}:{stagePorts:ports})});
 return {root,work,source,owner,handle,runtime,auth,checked,actors,ports,storePath:fixture.storePath,journalFile,modulePath,get journal(){return journal;},worker,nativeCalls:()=>nativeCalls,setNativeMode(mode:string){nativeMode=mode;},waitNative(){return new Promise<void>(resolve=>{dispatchStarted=resolve;});},settleNative(){settleNative?.();},reopen(){db.close();db=new DatabaseSync(journalFile);journal=new GenericWorkflowStore(db,{store_id:'work-flow',owner_service:'WorkService',compatibility_sha256:workflowCompatibilitySha256(checked)});},async close(){db.close();await runtime.close();await auth.close();rmSync(path.dirname(root),{recursive:true,force:true});rmSync(work,{recursive:true,force:true});}};
}
async function start(f:any,id:string){const w=f.worker(),started=await w.scheduleStart(canonicalJson({id}),'start-'+id);assert.ok(started);const claim=w.claimNext(300000);assert.ok(claim);return {w,id:started.instance_sha256,claim};}
test('source-generated local-only finite workflow persists typed results and resumes original journal',async()=>{
 const f=await setup();try{
  const run=await start(f,'1');let progress=await run.w.advance(run.claim);assert.equal(progress.state,'step-committed');
  assert.ok(JSON.parse(f.journal.inspect(run.id).history.at(-2)!.commitment_json).output_canonical_json);
  f.reopen();const w=f.worker();progress=await w.advance(progress.active_claim!);assert.equal(progress.kind,'advanced');
  progress=await w.advance(progress.active_claim!);assert.equal(f.journal.inspect(run.id).step_index,1);
  progress=await w.advance(progress.active_claim!);assert.equal(progress.kind,'completed');assert.equal(w.inspect(run.id).state,'completed');
  const driver=await f.owner.openWorkflow(f.handle,{runtime:f.runtime,actors:f.actors,journal:{directory:path.join(f.work,'public-journal'),mode:'create'}});
  try{
   const started=await driver.scheduleStart(Buffer.from('{"id":"8"}'),'public-start-8');assert.ok(started);let claim=driver.claimNext(300000);assert.ok(claim);
   for(let i=0;i<4;i++){const next=await driver.advance(claim!);claim=next.active_claim;if(i===3)assert.equal(next.kind,'completed');}
   const generatedSource=path.join(f.work,'generated/model/business.alch');writeFileSync(generatedSource,readFileSync(generatedSource,'utf8')+'\n');
   assert.throws(()=>driver.claimNext(1000));
  }finally{await driver.close();}
 }finally{await f.close();}
});
test('authored wait/re-evaluation, cancel, rejection, unknown and bounded retry govern progression',async()=>{
 const f=await setup();try{
  for(const [id,expected] of [['2','waiting-condition'],['3','cancelled'],['4','retry-later'],['5','needs-review'],['6','rejected']]){
   const run=await start(f,id!);let p=await run.w.advance(run.claim);p=await run.w.advance(p.active_claim!);assert.equal(p.kind,expected,JSON.stringify(p));
   assert.equal(run.w.inspect(run.id).step_index,0);
   if(id==='2'){f.reopen();const w=f.worker();p=await w.advance(p.active_claim!);assert.equal(p.kind,'completed');}
   if(id==='4'){p=await run.w.advance(p.active_claim!);assert.equal(p.kind,'advanced');p=await run.w.advance(p.active_claim!);assert.equal(p.kind,'advanced');assert.equal(run.w.inspect(run.id).step_index,0);}
  }
 }finally{await f.close();}
});
for(const kind of ['model','document','index','provider','agent-run'])test(`checked ${kind} stage port uses same original journal, typed continuation and no duplicate dispatch`,async()=>{
 const f=await setup(kind);try{
  assert.throws(()=>registerGenericWorkflowStagePort(f.owner,f.handle,f.runtime,'Work.Native',Object.freeze({capability_sha256:'f'.repeat(64),assertCurrent(){},async execute(){throw Error('must not invoke');},async inspect(){throw Error('must not inspect');}})),/CAPABILITY_IDENTITY/);
  assert.throws(()=>createGenericWorkflowWorker({source:f.checked,runtime:f.runtime,journal:f.journal,journal_store_id:'work-flow',actors:f.actors,stagePorts:new Map([['Work.Native',{kind:'original-workflow-stage-port/v1'} as any]])}),/ORIGINAL_STAGE_PORT/);
  const run=await start(f,'1');let p=await run.w.advance(run.claim);assert.equal(f.nativeCalls(),1);f.reopen();
  const changed={...f.checked,steps:f.checked.steps.map(s=>({...s,capability_sha256:'e'.repeat(64)}))};assert.notEqual(workflowCompatibilitySha256(changed),workflowCompatibilitySha256(f.checked));
  const wrongDb=new DatabaseSync(f.journalFile);try{assert.throws(()=>new GenericWorkflowStore(wrongDb,{store_id:'work-flow',owner_service:'WorkService',compatibility_sha256:workflowCompatibilitySha256(changed)}),/EPOCH_IDENTITY/);}finally{wrongDb.close();}
  const w=f.worker();p=await w.advance(p.active_claim!);assert.equal(f.nativeCalls(),1);p=await w.advance(p.active_claim!);assert.equal(f.nativeCalls(),2);p=await w.advance(p.active_claim!);assert.equal(p.kind,'completed');
 }finally{await f.close();}
});
test('uncertain native work is inspected after restart without redispatch and stale late results cannot commit',async()=>{
 const f=await setup('model');try{
  f.setNativeMode('unknown');const unknown=await start(f,'1');let p=await unknown.w.advance(unknown.claim);assert.equal(p.kind,'suspended-unknown');assert.equal(f.nativeCalls(),1);
  f.reopen();const w=f.worker();p=await w.advance(p.active_claim!);assert.equal(p.kind,'suspended-unknown');assert.equal(f.nativeCalls(),1);assert.equal(w.inspect(unknown.id).step_index,0);
  // The waiting uncertain run keeps its live claim, so a separate start can run.
  f.setNativeMode('delay');const late=await start(f,'7'),began=f.waitNative(),pending=late.w.advance(late.claim);await began;
  const now=Date.now;Date.now=()=>now()+360000;
  try{f.settleNative();await assert.rejects(pending,/STALE_CLAIM/);}finally{Date.now=now;}
  assert.equal(late.w.inspect(late.id).state,'step-prepared');assert.equal(late.w.inspect(late.id).step_index,0);
 }finally{await f.close();}
});
test('standalone C12 application cannot use the finite Workflow zero-event exception',async()=>{
 const root=buildEventSourceFixture();try{
  const base=JSON.parse(readFileSync(path.join(root,'contracts/selected-profile.json'),'utf8'));base.services=[{id:'WorkService',module:'Work'}];
  writeFileSync(path.join(root,'contracts/selected-profile.json'),JSON.stringify(base));writeFileSync(path.join(root,'business.alch'),business().split('\nworkflow Flow:')[0]!);
  await assert.rejects(createGenericCompositionOwner().prepare({sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json')}),/declared Event\/receiver pair/);
 }finally{rmSync(path.dirname(root),{recursive:true,force:true});}
});
test('a fresh process reconstructs generated V2 source and resumes persisted typed results to completion',async()=>{
 const f=await setup();try{
  const run=await start(f,'1'),progress=await run.w.advance(run.claim);assert.equal(progress.state,'step-committed');
  const sdk=new URL('../../src/generic/public-sdk.ts',import.meta.url).href,testing=new URL('../../src/generic/testing.ts',import.meta.url).href,store=new URL('../../src/generic/workflow-store.ts',import.meta.url).href,worker=new URL('../../src/generic/workflow-worker.ts',import.meta.url).href;
  const loader=new URL('../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/node_modules/tsx/dist/loader.mjs',import.meta.url);
  const script=`import {readFileSync} from 'node:fs';import {pathToFileURL} from 'node:url';import path from 'node:path';import {DatabaseSync} from 'node:sqlite';
import {createGenericBundledApplicationOwner,requireGenericWorkflowRuntime} from ${JSON.stringify(sdk)};
import {createGenericAuthFixture} from ${JSON.stringify(testing)};
import {GenericWorkflowStore} from ${JSON.stringify(store)};
import {createGenericWorkflowWorker,workflowCompatibilitySha256} from ${JSON.stringify(worker)};
const [modulePath,storePath,journalFile,work,claimJson]=process.argv.slice(1);
const bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\\nexport function')[0]);
const owner=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle),handle=await owner.prepare();
const review=owner.review(handle,'child-r03');owner.accept(handle,{decision_id:'child-r03',owner:'child-r03',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'child-accepted.json'));
const checked=requireGenericWorkflowRuntime(owner,handle).contract,ids=['Work.BeginEntry','Work.FirstEntry','Work.SecondEntry','Work.ContinueEntry','Work.ReadEntry'];
const auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(work,'child-auth'),sessionTtlSeconds:7200,subjects:[{id:'actor',evidence:'child-evidence',session:'child-session'}],grants:ids.map(entry=>({subject:'actor',entry}))});
const runtime=await owner.openRuntime(handle,{service:'WorkService',storePath,mode:'reopen',nativeAuth:auth.nativeAuth}),actors=new Map(ids.map(id=>[id,auth.actor(runtime,'actor',id)])),db=new DatabaseSync(journalFile);
try{const journal=new GenericWorkflowStore(db,{store_id:'work-flow',owner_service:'WorkService',compatibility_sha256:workflowCompatibilitySha256(checked)}),worker=createGenericWorkflowWorker({source:checked,runtime,journal,journal_store_id:'work-flow',actors});let claim=JSON.parse(claimJson),progress;
for(let i=0;i<3;i++){progress=await worker.advance(claim);claim=progress.active_claim;}
process.stdout.write(JSON.stringify({state:progress.state,kind:progress.kind,source_capture_sha256:checked.source_capture_sha256,source_closure_sha256:checked.source_closure_sha256}));}finally{db.close();await runtime.close();await auth.close();}`;
  const child=spawnSync(process.execPath,['--import',loader.pathname,'--input-type=module','-e',script,f.modulePath,f.storePath,f.journalFile,f.work,JSON.stringify(progress.active_claim)],{encoding:'utf8',timeout:180000,maxBuffer:1048576});
  assert.equal(child.status,0,child.stderr);const r=JSON.parse(child.stdout);assert.equal(r.state,'completed');assert.equal(r.kind,'completed');assert.notEqual(r.source_capture_sha256,f.checked.source_capture_sha256);assert.equal(r.source_closure_sha256,f.checked.source_closure_sha256);
 }finally{await f.close();}
});

test('native confirmed-no-effect wait survives restart and retries the same original local stage only when due',async()=>{
 const f=await setup('model'),realNow=Date.now;let clock=realNow();Date.now=()=>clock;
 try{f.setNativeMode('no-effect');const run=await start(f,'1');let p=await run.w.advance(run.claim);assert.equal(p.kind,'retry-later');assert.equal(p.state,'retry-later');assert.equal(f.nativeCalls(),1);let history=f.journal.inspect(run.id).history.map(r=>JSON.parse(r.commitment_json));assert.equal(history.filter(r=>r.kind==='native-no-effect-wait').length,1);assert.equal(history.some(r=>r.dispatch_evidence==='proven-not-dispatched'),false);assert.equal(p.active_claim,null);f.reopen();const worker=f.worker();assert.equal(worker.claimNext(300000),null);assert.equal(f.nativeCalls(),1);clock+=2000;const due=worker.claimNext(300000);assert.ok(due);assert.equal(due.fence,2);p=await worker.advance(due);assert.equal(p.kind,'advanced');assert.equal(f.nativeCalls(),2);history=f.journal.inspect(run.id).history.map(r=>JSON.parse(r.commitment_json));assert.equal(history.filter(r=>r.kind==='prepare-step').length,1);assert.equal(history.filter(r=>r.kind==='retry-stage').length,0);assert.equal(history.filter(r=>r.kind==='native-retry-resume').length,1);f.setNativeMode('normal');p=await worker.advance(p.active_claim!);assert.equal(p.kind,'advanced');p=await worker.advance(p.active_claim!);assert.equal(p.kind,'advanced');p=await worker.advance(p.active_claim!);assert.equal(p.kind,'completed');
 }finally{Date.now=realNow;await f.close();}
});
test('native retry deadline expiry preserves no-effect record without another dispatch',async()=>{const f=await setup('model'),realNow=Date.now;let clock=realNow();Date.now=()=>clock;try{f.setNativeMode('no-effect');const run=await start(f,'1');let p=await run.w.advance(run.claim);assert.equal(p.kind,'retry-later');assert.equal(p.active_claim,null);clock+=6000;const expired=run.w.claimNext(300000);assert.ok(expired);p=await run.w.advance(expired);assert.equal(p.kind,'needs-review');assert.equal(f.nativeCalls(),1);assert.ok(f.journal.inspect(run.id).history.some(r=>JSON.parse(r.commitment_json).kind==='native-no-effect-wait'));}finally{Date.now=realNow;await f.close();}});
