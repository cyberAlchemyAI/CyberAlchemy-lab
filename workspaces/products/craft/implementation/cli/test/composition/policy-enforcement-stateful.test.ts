/** Stateful preflight through original source/Auth/SQLite owners.
 * Open Questions: docs/POLICY-ENFORCEMENT.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.js';

const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const fixture=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C08/fixtures-candidate-002/approval');
const original=readFileSync(path.join(fixture,'business.alch'),'utf8');
const declarations=`
enum EligibilityRejection:
  value Unverified wire "eligibility-unverified"
enum EligibilityResult:
  variant Allow
  variant Reject reason EligibilityRejection
calculation Eligible:
  pure
  result EligibilityResult
  expression EligibilityResult.Allow()
calculation Ineligible:
  pure
  result EligibilityResult
  expression EligibilityResult.Reject(reason=EligibilityRejection.Unverified)
policy BeforeApproval:
  input verified Bool
  result EligibilityResult
  ordered-cases:
    denied when not verified -> Ineligible()
    otherwise -> Eligible()
`;
const source=original+declarations;
const enforced=source.replace('  call decision ApproveRequest(request=stored.value)','  enforce BeforeApproval(verified=stored.value.verified)\n  call decision ApproveRequest(request=stored.value)');
const entry='ReviewDesk.CommitRequestApprovalEntry',read='ReviewDesk.ReadStoredRequestEntry',subject='enforce-reviewer';
const wire=(v:unknown)=>new Uint8Array(Buffer.from(JSON.stringify(v)));

async function setup(text=enforced){
 const directory=mkdtempSync(path.join(tmpdir(),'craft-enforce-stateful-'));const owner:any=createGenericCompositionOwner();let auth:any,runtime:any,handle:any;
 try{
  mkdirSync(path.join(directory,'contracts'));
  const profile=JSON.parse(readFileSync(path.join(fixture,'profile.json'),'utf8'));profile.capabilities.push('operation-policy-enforcement');
  writeFileSync(path.join(directory,'business.alch'),text);writeFileSync(path.join(directory,'profile.json'),JSON.stringify(profile));
  for(const name of ['bounds.json','transactions.json'])writeFileSync(path.join(directory,'contracts',name),readFileSync(path.join(fixture,'contracts',name)));
  handle=await owner.prepare({sourcePath:path.join(directory,'business.alch'),profilePath:path.join(directory,'profile.json')});
  const review=owner.review(handle,'typed-policy-enforcement focused test');owner.accept(handle,{decision_id:'EN04-focused',owner:'typed-policy-enforcement focused test',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,'decision.json'));
  auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),subjects:[{id:subject,evidence:'enforce-evidence',session:'enforce-session'}],grants:[{subject,entry},{subject,entry:read}]});
  const prepared=await prepareGenericFixtureRuntime(owner,handle,{service:'ReviewDeskService',ownedDirectory:path.join(directory,'store'),nativeAuth:auth.nativeAuth});runtime=prepared.runtime;
  loadGenericFixture(prepared.fixture,new Uint8Array(readFileSync(path.join(fixture,'fixture-rows.json'))));
  return {owner,handle,runtime,auth,async close(){await runtime.close();await auth.close();owner.dispose(handle);rmSync(directory,{recursive:true,force:true});}};
 }catch(error){if(runtime)await runtime.close();if(auth)await auth.close();if(handle)owner.dispose(handle);rmSync(directory,{recursive:true,force:true});throw error;}
}
async function command(f:any,id:string,key:string){
 const p=f.runtime.prepareCommand(f.runtime.entry(entry),wire({id}),{client_key:key});
 const a=await f.runtime.authorize(f.auth.actor(f.runtime,subject,entry),p);if(!a.ok)return a;
 const c=await f.runtime.consume(a.value,p);if(!c.ok)return c;return f.runtime.executeCommand(c.value);
}
async function stored(f:any,id:string){
 const p=f.runtime.prepareInput(f.runtime.entry(read),wire({id}));const a=await f.runtime.authorize(f.auth.actor(f.runtime,subject,read),p);assert.equal(a.ok,true,JSON.stringify(a));const c=await f.runtime.consume(a.value,p);assert.equal(c.ok,true,JSON.stringify(c));const result=await f.runtime.execute(c.value);assert.equal(result.ok,true,JSON.stringify(result));return result.outcome.value;
}

test('EN04 stateful enforcement rejects before mutations, allows commit and retains Auth-before-replay',{timeout:600000},async()=>{
 const f=await setup();try{
  const before=await stored(f,'24');
  const denied=await command(f,'24','enforce-denied-24');assert.equal(denied.ok,true,JSON.stringify(denied));assert.deepEqual(denied.outcome,{kind:'Rejected',code:'eligibility-unverified'});
  assert.deepEqual(await stored(f,'24'),before,'denied preflight cannot mutate original observed row');
  const replay=await command(f,'24','enforce-denied-24');assert.equal(replay.ok,true,JSON.stringify(replay));assert.deepEqual(replay.outcome,denied.outcome);
  const allowed=await command(f,'23','enforce-allowed-23');assert.equal(allowed.ok,true,JSON.stringify(allowed));assert.equal(allowed.outcome.kind,'Returned');assert.equal((await stored(f,'23')).value.state,'Approved');
  f.auth.setPermission(subject,entry,false);const revoked=await command(f,'23','enforce-allowed-23');assert.equal(revoked.ok,false,JSON.stringify(revoked));assert.equal(revoked.error.code,'PermissionDenied');
 }finally{await f.close();}
});

test('EN04 source refuses enforcement in transaction body',{timeout:120000},async()=>{
 const text=source.replace('    atomic-participants StoredRequest','    atomic-participants StoredRequest\n    enforce BeforeApproval(verified=stored.value.verified)');
 await assert.rejects(()=>setup(text),(e:any)=>e?.diagnostics?.[0]?.code==='UnsupportedCapability');
});

test('EN02 source refuses enforcement after a completed transaction',{timeout:120000},async()=>{
 const text=source.replace('  return CommittedDecision(stored=changed,decision=decision)','  enforce BeforeApproval(verified=true)\n  return CommittedDecision(stored=changed,decision=decision)');
 await assert.rejects(()=>setup(text),(e:any)=>e?.diagnostics?.[0]?.code==='UnsupportedCapability'&&e.diagnostics[0].message.includes('pre-effect'));
});

test('EN02 source refuses enforcement after an incoming conditional effectful local call',{timeout:120000},async()=>{
 const text=source+`\noperation GuardAfterCall:
  input id UInt64
  output Bool
  when id > 0:
    call prior CommitRequestApproval(id=id)
  enforce BeforeApproval(verified=true)
  return true
`;
 await assert.rejects(()=>setup(text),(e:any)=>e?.diagnostics?.[0]?.code==='UnsupportedCapability'&&e.diagnostics[0].message.includes('pre-effect'));
});

test('EN04 enforcement inside a supported preflight conditional keeps the rejection code',{timeout:600000},async()=>{
 const text=enforced.replace('  enforce BeforeApproval(verified=stored.value.verified)','  when stored.value.verified:\n    enforce BeforeApproval(verified=true)\n  otherwise:\n    enforce BeforeApproval(verified=false)');
 const f=await setup(text);try{const before=await stored(f,'24');const denied=await command(f,'24','conditional-enforce-24');assert.equal(denied.ok,true,JSON.stringify(denied));assert.deepEqual(denied.outcome,{kind:'Rejected',code:'eligibility-unverified'});assert.deepEqual(await stored(f,'24'),before);}finally{await f.close();}
});

test('EN04 a reached Policy arithmetic error remains a fault and cannot mutate the row',{timeout:600000},async()=>{
 const text=enforced.replace('denied when not verified','denied when verified and (18446744073709551615 + 1 == 0)');
 const f=await setup(text);try{const before=await stored(f,'23');const fault=await command(f,'23','fault-enforce-23');assert.equal(fault.ok,false,JSON.stringify(fault));assert.equal(fault.error.code,'ArithmeticOverflow');assert.deepEqual(await stored(f,'23'),before);}finally{await f.close();}
});
