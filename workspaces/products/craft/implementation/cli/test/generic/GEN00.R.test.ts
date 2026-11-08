/** Real fixed Rust child, physical producer and private-pipe origin controls.
 * Open Questions: implementation/craft-alchlang-generic-applications-2026-10-18-r2/evidence/GEN00.R/attempts/repair-001/RESULT.json.
 * The original12 Auth native controls replay unchanged in a fresh owned root. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,chmodSync,renameSync,copyFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {COMMERCE_AUTH_READY_ABI_V1,produceCommerceAuthNativeOwnerV1,assertCommerceAuthNativeOwnerV1,checkCommerceAuthResponseV1,captureCommerceAuthRequestV1,inspectCommerceAuthFixtureDatabaseV1,type CommerceAuthNativeOwnerV1,type AuthBridgeRequestV1} from '../../src/commerce/commerce-auth-ready-bridge-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.js';
const repo=fileURLToPath(new URL('../'.repeat(7),import.meta.url)),parent=path.resolve(repo,process.env.CRAFT_AUTH_RECOVERY_ROOT!);
let a:CommerceAuthNativeOwnerV1,b:CommerceAuthNativeOwnerV1,f:ReturnType<typeof seedCommerceAuthFixtureDatabaseV1>;
const request=():AuthBridgeRequestV1=>({abi:COMMERCE_AUTH_READY_ABI_V1,request:{request_id:'private-request-1',authentication_evidence_ref:'private-evidence-1',route_id:'commerce:Orders.PlaceOrderEntry'},binding:{invocation_id:'private-invocation-1',logical_entry_id:'Orders.PlaceOrderEntry',bound_operation_id:'Orders.PlaceOrder',canonical_input_sha256:'1'.repeat(64),checked_source_sha256:'2'.repeat(64),profile_config_sha256:'3'.repeat(64),native_basis_sha256:'4'.repeat(64),actor_owner_identity:'private-actor-1',causal_owner_identity:null,target_service_id:'orders',store_or_event_epoch:'private-fixture-epoch-1'},expected_permission:{resource:'orders',action:'place',scope:'commerce-shop'}});
before(async()=>{
 const root=mkdtempSync(path.join(parent,'core-native-controls-'));a=await produceCommerceAuthNativeOwnerV1(path.join(root,'first'));b=await produceCommerceAuthNativeOwnerV1(path.join(root,'second'));
 f=seedCommerceAuthFixtureDatabaseV1(a,{subject:'customer-1',evidence:'private-evidence-1',session:'fixture-session-1',routes:[{entry:'Orders.PlaceOrderEntry',permission:request().expected_permission}]});
});
after(async()=>{await Promise.all([a?.dispose(),b?.dispose()]);});
const code=(value:string)=>(e:any)=>e.code===value;
test('fixed source build produces original native owner and real READY projection',async()=>{
 const start=performance.now();assertCommerceAuthNativeOwnerV1(a);console.log(JSON.stringify({phase:'fresh-native-currentness',elapsed_ms:performance.now()-start,members:(a.inspect().members as any[]).length}));const complete=await a.execute(f.handle,request()),data=a.inspectCompletion(complete);
 assert.equal(data.response.outcome,'allow');assert.equal(data.response.ready?.authenticated_subject_id,'customer-1');assert.equal(data.response.ready?.session_id,'fixture-session-1');assert.equal(data.response.ready?.authentication_evidence_revision,'3');assert.equal(data.response.ready?.current_authorization_revision,'7');assert.equal(data.response.ready?.required_permission.scope,'commerce-shop');a.assertCompletionDatabase(complete,f.handle);assert.deepEqual(a.inspectWork(),{active:0,queued:0,unsettled:0});
});
test('completion and database JSON lookalikes or foreign factories confer no ownership',async()=>{
 const complete=await a.execute(f.handle,request());assert.throws(()=>a.inspectCompletion({...complete}),code('ForeignOwner'));assert.throws(()=>b.inspectCompletion(complete),code('ForeignOwner'));await assert.rejects(a.execute({...f.handle},request()),code('ForeignOwner'));await assert.rejects(b.execute(f.handle,request()),code('ForeignOwner'));assert.throws(()=>assertCommerceAuthNativeOwnerV1({kind:a.kind}as any),code('ForeignOwner'));
});
test('actual policy revocation yields deny with no READY projection',async()=>{
 f.mutate('UPDATE auth_authentication_evidence SET revoked=1');const c=await a.execute(f.handle,request());assert.equal(a.inspectCompletion(c).response.outcome,'deny');assert.equal(a.inspectCompletion(c).response.ready,null);f.mutate('UPDATE auth_authentication_evidence SET revoked=0');
});
test('request projections reject forged principal, wrong entry route and oversized values',()=>{
 assert.throws(()=>captureCommerceAuthRequestV1({...request(),authorized:true}as any),code('InvalidRequest'));
 const r=request();assert.throws(()=>captureCommerceAuthRequestV1({...r,binding:{...r.binding,logical_entry_id:'Orders.Other'}}),code('InvalidRequest'));assert.throws(()=>captureCommerceAuthRequestV1({...r,request:{...r.request,request_id:'é'.repeat(129)}}),code('InvalidRequest'));
});
test('pure closed-response parser rejects extra duplicate malformed foreign and short frames without minting owners',async()=>{
 const r=request(),completion=await a.execute(f.handle,r),response=a.inspectCompletion(completion).response,raw=JSON.stringify(response);
 for(const bytes of [raw+'\n',raw+raw,raw.replace('{','{"abi":"wrong",'),'{',JSON.stringify({...response,binding:{...response.binding,logical_entry_id:'Orders.Other'}}),JSON.stringify({...response,ready:null})])assert.throws(()=>checkCommerceAuthResponseV1(Buffer.from(bytes),r),code('MalformedResponse'));
 const dto=checkCommerceAuthResponseV1(Buffer.from(raw),r);assert.throws(()=>a.inspectCompletion(dto as any),code('ForeignOwner'));
});
test('abort retains actual child resources until observed close and grants no completion',async()=>{
 const controller=new AbortController(),p=a.execute(f.handle,request(),controller.signal);controller.abort();assert.equal(a.inspectWork().unsettled,1);await assert.rejects(p,code('Cancelled'));
 for(let i=0;i<200&&a.inspectWork().unsettled;i++)await new Promise(r=>setTimeout(r,5));assert.equal(a.inspectWork().unsettled,0);
});
test('an actual child response observed beyond the fixed deadline cannot grant a late completion',async()=>{
 const p=a.execute(f.handle,request());const end=performance.now()+2050;
 // Delay only the real parent event loop. The fixed Rust program and clock
 // stay unchanged; its response/exit must not override an elapsed deadline.
 while(performance.now()<end){}
 await assert.rejects(p,code('BridgeTimeout'));
 for(let i=0;i<200&&a.inspectWork().unsettled;i++)await new Promise(r=>setTimeout(r,5));assert.equal(a.inspectWork().unsettled,0);
});
test('replacement of an actual active fixture database cannot mint a completion',async()=>{
 const fixture=seedCommerceAuthFixtureDatabaseV1(a,{subject:'customer-1',evidence:'private-evidence-1',session:'fixture-session-1',routes:[{entry:'Orders.PlaceOrderEntry',permission:request().expected_permission}]}),file=inspectCommerceAuthFixtureDatabaseV1(a,fixture.handle).file;
 const result=a.execute(fixture.handle,request()).then(()=> 'complete',(e:any)=>e.code);assert.equal(a.inspectWork().active,1);
 renameSync(file,file+'.original');copyFileSync(file+'.original',file);chmodSync(file,0o600);
 assert.equal(await result,'StaleOwner');await assert.rejects(a.execute(fixture.handle,request()),code('StaleOwner'));assert.equal(a.inspectWork().unsettled,0);
});
test('replacement of a queued fixture is rejected before starting its child',async()=>{
 const fixture=seedCommerceAuthFixtureDatabaseV1(a,{subject:'customer-1',evidence:'private-evidence-1',session:'fixture-session-1',routes:[{entry:'Orders.PlaceOrderEntry',permission:request().expected_permission}]}),file=inspectCommerceAuthFixtureDatabaseV1(a,fixture.handle).file;
 const controllers=Array.from({length:4},()=>new AbortController()),active=controllers.map(c=>a.execute(f.handle,request(),c.signal).catch((e:any)=>e.code));
 const queued=a.execute(fixture.handle,request()).then(()=> 'complete',(e:any)=>e.code);assert.equal(a.inspectWork().queued,1);
 renameSync(file,file+'.original');copyFileSync(file+'.original',file);chmodSync(file,0o600);for(const c of controllers)c.abort();
 assert.equal(await queued,'StaleOwner');await Promise.all(active);await a.execute(f.handle,request());assert.deepEqual(a.inspectWork(),{active:0,queued:0,unsettled:0});
});
test('fixed four-child and sixty-four-queued limits reject excess work and retain settlement ownership',async()=>{
 const controllers=Array.from({length:70},()=>new AbortController()),observed=controllers.map(c=>a.execute(f.handle,request(),c.signal).then(()=> 'complete',(e:any)=>e.code));
 assert.deepEqual(a.inspectWork(),{active:4,queued:64,unsettled:4});for(const c of controllers)c.abort();const results=await Promise.all(observed);assert.equal(results.filter(c=>c==='QueueFull').length,2);assert.ok(results.every(c=>['QueueFull','Cancelled','BridgeTimeout'].includes(c)));
 for(let i=0;i<200&&a.inspectWork().unsettled;i++)await new Promise(r=>setTimeout(r,5));assert.deepEqual(a.inspectWork(),{active:0,queued:0,unsettled:0});
});
test('changed exact native binary retires its producer while another original producer remains current',async()=>{
 const binary=(a.inspect().binary as any).path,old=readFileSync(binary);try{writeFileSync(binary,Buffer.concat([old,Buffer.from([0])]));assert.throws(()=>a.assertCurrent(),code('StaleOwner'));b.assertCurrent();}finally{writeFileSync(binary,old);chmodSync(binary,0o700);}assert.throws(()=>a.assertCurrent(),code('StaleOwner'));
});
test('all dispose callers wait for actual owned child settlement',async()=>{
 const other=seedCommerceAuthFixtureDatabaseV1(b,{subject:'customer-1',evidence:'private-evidence-1',session:'fixture-session-1',routes:[{entry:'Orders.PlaceOrderEntry',permission:request().expected_permission}]});
 const pending=b.execute(other.handle,request()).then(()=> 'complete',(e:any)=>e.code),one=b.dispose(),two=b.dispose();assert.equal(b.inspectWork().unsettled,1);await Promise.all([one,two]);assert.equal(await pending,'DisposedOwner');assert.deepEqual(b.inspectWork(),{active:0,queued:0,unsettled:0});assert.throws(()=>b.assertCurrent(),code('DisposedOwner'));
});
