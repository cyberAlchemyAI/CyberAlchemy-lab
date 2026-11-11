import assert from 'node:assert/strict';
import { generateKeyPairSync } from 'node:crypto';
import { mkdtempSync, writeFileSync, readFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { main } from './cli.mjs';
import { issue, execute } from './service.mjs';
import { signPacket, authenticatePacket } from './security.mjs';
import { digest } from './verified-projection.mjs';
import { transition, initializeJoin } from './runtime.mjs';
import { Journal } from './journal.mjs';
import { Snapshots } from './snapshots.mjs';
import { impactClosure, independentAssessment } from './ports.mjs';

const home = mkdtempSync(path.join(tmpdir(), 'lab-shared-integration-'));
const {privateKey,publicKey} = generateKeyPairSync('ed25519');
const privatePem = privateKey.export({format:'pem',type:'pkcs8'});
const publicPem = publicKey.export({format:'pem',type:'spki'});
const workspace='workspace:shared-integration',cut='a'.repeat(64);
const bytes=value=>Buffer.from(JSON.stringify(value));
const binding=(ref='fixture:body')=>({ref,sha256:cut,bytes:'10'});
const verification=(subject,scope=workspace,predicate='join-transition')=>({
  subject,scope,cut,predicate,issuer:'principal:fixture',policy:binding('fixture:policy'),proof:binding('fixture:proof')
});
const trust={principals:{'principal:fixture':{public_key:publicPem,grants:[]}},selections:{},schemas:{}};
function grant(predicate,operation) {
  trust.principals['principal:fixture'].grants.push({predicate,operation,scope:workspace,cut});
}
function packet(operation,input) {
  grant('verified-planning-input',operation);
  const artifact=bytes({operation,scope:workspace,cut,input});
  const receipt=signPacket(bytes({version:1,predicate:'verified-planning-input',operation,scope:workspace,cut,
    artifact:{sha256:digest(artifact),bytes:artifact.length}}),'principal:fixture',privatePem);
  return {operation,scope:workspace,cut,artifact:artifact.toString('base64'),receipt};
}
const checks=[];
async function check(name,fn) {
  await fn();
  checks.push(name);
  console.log('PASS '+name);
}
const observation={terminal_receipt:null,published_snapshot:null,published_verification:null,
  run_ref:'join:integration',workspace,phase:'Proposed',source_cut:cut,current_source_cut:cut,
  original_operation:'operation:integration',native_outcome:'Unobserved',publication_outcome:'Unobserved'};
const originalSchema=bytes({type:'object',required:['value'],properties:{value:{type:'object'}},additionalProperties:false});
writeFileSync(path.join(home,'original.schema.json'),originalSchema);
trust.schemas.original={path:path.join(home,'original.schema.json'),sha256:digest(originalSchema)};
trust.schemas.input={...trust.schemas.original};
const selection=bytes({version:1,operation:'PlanJoinContinuation',scope:workspace,input_schema:'input',
  requirements:[{predicate:'join-observation',schema:'original',mappings:[{from:'/value',to:'/value'}]}]});
writeFileSync(path.join(home,'selection.json'),selection);
trust.selections.join={path:path.join(home,'selection.json'),sha256:digest(selection)};
grant('join-observation','PlanJoinContinuation');
grant('verified-planning-input','PlanJoinContinuation');
const original=bytes({value:observation});
const originalReceipt=signPacket(bytes({version:1,predicate:'join-observation',operation:'PlanJoinContinuation',
  scope:workspace,cut,artifact:{sha256:digest(original),bytes:original.length}}),'principal:fixture',privatePem);
const issuance={selection_id:'join',operation:'PlanJoinContinuation',scope:workspace,cut,
  originals:[{artifact:original.toString('base64'),receipt:originalReceipt}]};
let issued;
await check('real-Ed25519-original-issuance-and-compiled-evaluation',async()=>{
  issued=await issue(issuance,trust,'principal:fixture',privatePem);
  const result=await execute({...issued,operation:'PlanJoinContinuation',scope:workspace,cut},trust);
  assert.equal(result.result,'NeedsPermission');
});
await check('real-signature-tamper-refused',async()=>{
  const changed={...originalReceipt,signature:'0'.repeat(128)};
  assert.throws(()=>authenticatePacket(changed,trust),/signature-invalid/);
});
await check('untrusted-signer-refused',async()=>{
  assert.throws(()=>authenticatePacket({...originalReceipt,issuer:'principal:unknown'},trust),/signer-untrusted/);
});
await check('old-original-receipt-refuses-changed-artifact',async()=>{
  await assert.rejects(()=>issue({...issuance,originals:[{receipt:originalReceipt,artifact:bytes({value:{...observation,phase:'Completed'}}).toString('base64')}]},trust,'principal:fixture',privatePem),/artifact-mismatch/);
});
await check('issuance-selection-source-drift-refused',async()=>{
  writeFileSync(path.join(home,'selection.json'),Buffer.concat([selection,Buffer.from(' ')]));
  await assert.rejects(()=>issue(issuance,trust,'principal:fixture',privatePem),/selection-mismatch/);
  writeFileSync(path.join(home,'selection.json'),selection);
});
await check('public-cli-issue-and-evaluate',async()=>{
  writeFileSync(path.join(home,'trust.json'),bytes(trust));
  writeFileSync(path.join(home,'owner.pem'),privatePem,{mode:0o600});
  writeFileSync(path.join(home,'issuance.json'),bytes(issuance));
  const result=await main(['issue','--file',path.join(home,'issuance.json'),'--trust',path.join(home,'trust.json'),
    '--issuer','principal:fixture','--key',path.join(home,'owner.pem')]);
  writeFileSync(path.join(home,'evaluation.json'),bytes({...result,operation:'PlanJoinContinuation',scope:workspace,cut}));
  const evaluated=await main(['evaluate','--file',path.join(home,'evaluation.json'),'--trust',path.join(home,'trust.json')]);
  assert.equal(evaluated.result,'NeedsPermission');
});
const database=path.join(home,'journal.sqlite');
let row=await initializeJoin({workspace,run_ref:observation.run_ref,original_operation:observation.original_operation,source_cut:cut},database);
await check('durable-initialization-idempotent-and-unique',async()=>{
  const same=await initializeJoin({workspace,run_ref:observation.run_ref,original_operation:observation.original_operation,source_cut:cut},database);
  assert.equal(same.id,row.id);
  await assert.rejects(()=>initializeJoin({workspace,run_ref:'join:duplicate',original_operation:observation.original_operation,source_cut:cut},database),/UNIQUE/);
});
function event(signal,outcome) {
  const fact=binding('event:'+row.revision);
  return {observed_operation:row.operation,observed_run:row.run,observed_phase:row.phase,
    observed_signal:signal,observed_outcome:outcome,
    join_key:{id:String(row.id),operation_key:String(row.id),run_ref:row.run,workspace,operation:row.operation,
      evidence:verification(binding(row.run),workspace,'stable-join-identity')},
    phase:row.phase,signal,revision:String(row.revision),observed_revision:String(row.revision),
    cut,past_fact:fact,evidence:verification(fact)};
}
const steps=[
 ['SelectContext','Unobserved'],['PrepareDraft','Unobserved'],['RequestReview','Unobserved'],
 ['ObserveSemanticAcceptance','Committed'],['ObservePermission','Committed'],
 ['ObserveNativeUnknown','Unknown'],['ObserveNativeCommit','Committed'],
 ['PreparePublication','Unobserved'],['ObservePublicationUnknown','Unknown'],
 ['ObservePublication','Committed'],['RequestSourceTransition','Unobserved'],['ObserveSourceTransition','Committed']
];
let firstRequest;
await check('persisted-join-full-unknown-recovery-and-source-transition',async()=>{
  for (const [signal,outcome] of steps) {
    const request={...packet('AssessJoinTransition',{value:event(signal,outcome)}),command:'command:'+row.revision};
    firstRequest??=request;
    await transition(request,trust,database);
    const reopened=new Journal(database);
    row=reopened.inspect(workspace,observation.run_ref);
    reopened.close();
  }
  assert.equal(row.phase,'Completed');
  assert.equal(row.events.length,steps.length);
});
await check('original-command-replay-after-later-transitions',async()=>{
  assert.equal((await transition(firstRequest,trust,database)).replayed,true);
});
await check('same-command-with-changed-bytes-refused',async()=>{
  const bad={...firstRequest,artifact:bytes({operation:'AssessJoinTransition',scope:workspace,cut,input:{value:event('ObserveRefusal','Refused')}}).toString('base64')};
  await assert.rejects(()=>transition(bad,trust,database),/artifact-mismatch/);
});
await check('actual-persisted-revision-cannot-be-forged',async()=>{
  const value={...event('ObserveRefusal','Refused'),phase:'AwaitingPermission',observed_phase:'AwaitingPermission'};
  await assert.rejects(()=>transition({...packet('AssessJoinTransition',{value}),command:'forged'},trust,database),/persisted-precondition/);
});
await check('snapshot-selector-CAS-idempotence-and-recovery',async()=>{
  const snapshots=new Snapshots(path.join(home,'snapshots.sqlite'));
  const staged=snapshots.stage(workspace,'publication:1',cut,{'registry.json':bytes({entries:[]}).toString('base64')});
  const args={workspace,operation:'publication:1',expected:null,snapshot:staged.binding.sha256,artifactDigest:cut};
  const committed=snapshots.publish(args);
  assert.equal(committed.selected.revision,1);
  assert.equal(snapshots.publish(args).replayed,true);
  assert.equal(snapshots.inspectPublication(workspace,'publication:1').selected.digest,staged.binding.sha256);
  const second=snapshots.stage(workspace,'publication:2',cut,{'registry.json':bytes({entries:[1]}).toString('base64')});
  assert.throws(()=>snapshots.publish({...args,operation:'publication:2',snapshot:second.binding.sha256}),/selector-conflict/);
  assert.equal(snapshots.material(staged.binding.sha256,'registry.json').bytes.toString(),JSON.stringify({entries:[]}));
  assert.throws(()=>snapshots.stage(workspace,'bad',cut,{'../escape':'eA=='}),/path-invalid/);
  snapshots.close();
});
await check('complete-impact-closure-keeps-cycles-and-refuses-unknowns',async()=>{
  const raw=Buffer.from('{}'),b={ref:'fixture:material',sha256:digest(raw),bytes:'2'};
  const manifest={source_cut:cut,cursor:'cursor:1',unresolved:0,subjects:[
    {ref:'a',binding:b,dependencies:['b']},{ref:'b',binding:b,dependencies:['a']},
    {ref:'c',binding:b,dependencies:['b']}]};
  assert.deepEqual(impactClosure(manifest,'a',()=>raw).affected,['a','b','c']);
  assert.throws(()=>impactClosure({...manifest,unresolved:1},'a',()=>raw),/incomplete/);
  assert.throws(()=>impactClosure({...manifest,subjects:[{ref:'a',binding:b,dependencies:['absent']}]},'a',()=>raw),/unresolved/);
});
await check('independent-executable-checks-use-qualified-original-bytes',async()=>{
  const executor=path.join(home,'check.py');
  writeFileSync(executor,'import json,sys\nx=json.load(sys.stdin)\nsys.exit(0 if x["output"]["ref"] == "fixture:output" else 1)\n');
  const hash=digest(readFileSync(executor));
  const spec={obligation:'obligation:1',executor:{ref:'executor:1',sha256:hash,bytes:String(readFileSync(executor).length)}};
  const selected={'executor:1':{path:executor,sha256:hash,command:'python3'}};
  assert.equal(independentAssessment([spec],{ref:'fixture:output'},selected)[0].outcome,'Passed');
  assert.equal(independentAssessment([spec],{ref:'fixture:wrong'},selected)[0].outcome,'Failed');
  writeFileSync(executor,'raise RuntimeError()');
  assert.throws(()=>independentAssessment([spec],{ref:'fixture:output'},selected),/drift/);
});

await check('journal-tampered-state-refused-after-restart',async()=>{
  const journal=new Journal(database);
  journal.db.prepare("UPDATE runs SET phase='Proposed' WHERE workspace=? AND run=?").run(workspace,observation.run_ref);
  assert.throws(()=>journal.inspect(workspace,observation.run_ref),/state-history-mismatch/);
  journal.db.prepare("UPDATE runs SET phase='Completed' WHERE workspace=? AND run=?").run(workspace,observation.run_ref);
  assert.equal(journal.inspect(workspace,observation.run_ref).phase,'Completed');
  journal.close();
});
await check('public-native-route-requires-construction-entry',async()=>{
  const file=path.join(home,'missing-construction.json');
  writeFileSync(file,bytes({}));
  await assert.rejects(()=>main(['native-apply','--file',file,'--trust',path.join(home,'trust.json')]),/construction-entry-required/);
});

await check('native-raw-public-key-format-supported',async()=>{
  const raw=publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('hex');
  const compatible=structuredClone(trust);
  compatible.principals['principal:fixture'].public_key=raw;
  assert.equal(authenticatePacket(originalReceipt,compatible).statement.predicate,'join-observation');
});
await check('signed-cross-workspace-input-refused',async()=>{
  await assert.rejects(()=>execute(packet('PlanJoinContinuation',{value:{...observation,workspace:'workspace:foreign'}}),trust),/workspace-scope-mismatch/);
});
await check('signed-cross-cut-input-refused',async()=>{
  await assert.rejects(()=>execute(packet('PlanJoinContinuation',{value:{...observation,source_cut:'b'.repeat(64)}}),trust),/cut-mismatch/);
});

await check('public-cli-attestation-retains-original-bytes',async()=>{
  const originalFile=path.join(home,'original-artifact.json');
  writeFileSync(originalFile,original);
  const statementFile=path.join(home,'attest.json');
  writeFileSync(statementFile,bytes({predicate:'join-observation',operation:'PlanJoinContinuation',scope:workspace,
    cut,schema:'original',artifact:originalFile}));
  const attested=await main(['attest','--file',statementFile,'--trust',path.join(home,'trust.json'),
    '--issuer','principal:fixture','--key',path.join(home,'owner.pem')]);
  assert.equal(Buffer.from(attested.artifact,'base64').toString(),original.toString());
  assert.equal(authenticatePacket(attested.receipt,trust).statement.artifact.sha256,digest(original));
});
const result={status:'PASS',check_count:checks.length,checks,
  scope:'Real signatures, schema validators, generated AlchLang, SQLite restart/replay, snapshot CAS and actual independent subprocess checks in isolated stores',
  user_authority_mutated:false};
writeFileSync(path.join(import.meta.dirname,'INTEGRATION-VERIFICATION.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
