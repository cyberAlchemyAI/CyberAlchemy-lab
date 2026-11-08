/** Explicit consumer package execution; fixtures do not qualify paid providers.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,cpSync,readFileSync,writeFileSync,rmSync,symlinkSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {captureGenericCapabilityPackage,createGenericCapabilityResourceOwner,type GenericCapabilityResourceRequest} from '../../src/generic/capability-resource.js';
import type {GenericCapabilityRealizationV1} from '../../src/generic/capability-data-v1.js';
import {dataDigest} from '../../src/profile-engine/contracts.js';
const source=fileURLToPath(new URL('./fixtures/capability-resource/',import.meta.url));
const bounds={max_input_bytes:8192,max_output_bytes:8192,max_items:10,deadline_ms:60000,max_model_attempts:1,max_tool_calls:0};
function setup(t:test.TestContext,mutate?:(root:string)=>void){
 const consumer=mkdtempSync(path.join(tmpdir(),'craft-native-resource-')),root=path.join(consumer,'node_modules/@craft-fixtures/capability-native');mkdirSync(path.dirname(root),{recursive:true});cpSync(source,root,{recursive:true});t.after(()=>rmSync(consumer,{recursive:true,force:true}));mutate?.(root);
 const captured=captureGenericCapabilityPackage(root);
 const descriptor:GenericCapabilityRealizationV1={id:'FixtureResource',integration_binding_ref:'FixtureBinding',contract:'inference/v1',implementation:{package:'@craft-fixtures/capability-native',version:'1.0.0',sha256:captured.sha256,export:'./resource'},operations:['text.structured'],capabilities:['structured-output'],mode:'fixture',target:{destination:'fixture://selected',api:'resource/v1',model_or_harness:'fixture-echo',revision:'1',mutability:'immutable'},schema:{dialect:'https://json-schema.org/draft/2020-12/schema',subset:'checked-business-values/v1'},bounds,lifecycle:{credential_slot_ref:null,compatibility:'exact-contract-and-target',retention_policy_ref:'Retention',credential_lifecycle_ref:'Credentials',synchronization_ref:'Synchronization',retirement_ref:'Retirement',fallback:'none',completion:'validated-proposal-only',unknown_effect:'reconcile-before-retry'}};
 return {consumer,root,captured,descriptor,lineage:{resource_ref:'FixtureResource'},owner:createGenericCapabilityResourceOwner(consumer)};
}
const request=(overrides:Partial<GenericCapabilityResourceRequest>={}):GenericCapabilityResourceRequest=>({operation:'text.structured',input:Buffer.from('{"answer":"18446744073709551615"}'),result_schema:{type:'object'},limits:bounds,deadline_ms:Date.now()+30000,...overrides});
function agent(s:ReturnType<typeof setup>){const descriptor={...s.descriptor,contract:'agent-run/v1' as const,operations:['agent.run' as const],capabilities:['structured-output' as const,'readonly-tools' as const],bounds:{...bounds,max_tool_calls:1}};return descriptor;}
const errorCode=(code:string)=>(error:unknown)=>error instanceof Error&&error.message.includes(code);

test('portable inventory hashes exact package bytes and is independent of consumer path',t=>{
 const a=setup(t),b=setup(t);assert.equal(a.captured.sha256,b.captured.sha256);assert.equal(a.captured.sha256,dataDigest({schema_version:'craft.native-capability-package-bytes/v1',files:a.captured.files}));assert.deepEqual(a.captured.files.map(f=>f.path),['copy.mjs','package.json','resource.mjs']);assert.ok(!JSON.stringify(a.captured).includes(a.consumer));
 writeFileSync(path.join(b.root,'copy.mjs'),readFileSync(path.join(b.root,'copy.mjs'),'utf8')+'\n');assert.notEqual(captureGenericCapabilityPackage(b.root).sha256,a.captured.sha256);
});
test('imports and invokes the explicit installed resource and its local static dependency',async t=>{
 const s=setup(t),h=await s.owner.load(s.descriptor,s.lineage,s.descriptor.target),input=request();assert.deepEqual(await s.owner.invoke(h,input),new Uint8Array(input.input));assert.equal(s.owner.inspect(h).package_sha256,s.captured.sha256);await s.owner.dispose(h);assert.throws(()=>s.owner.inspect(h),errorCode('ForeignOwner'));
});
test('loads captured bytes with a fresh module identity despite preexisting Node cache',async t=>{
 const s=setup(t);await import(pathToFileURL(path.join(s.root,'resource.mjs')).href);
 writeFileSync(path.join(s.root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,async invoke(r){return new TextEncoder().encode('{}');}});}\n");
 const descriptor={...s.descriptor,implementation:{...s.descriptor.implementation,sha256:captureGenericCapabilityPackage(s.root).sha256}},h=await s.owner.load(descriptor,s.lineage);
 assert.equal(new TextDecoder().decode(await s.owner.invoke(h,request())),'{}');
});
test('allows an explicitly inventoried static builtin with local ESM closure',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'copy.mjs'),"import {Buffer} from 'node:buffer';\nexport function copyWire(input){return Buffer.from(input);}\n")),h=await s.owner.load(s.descriptor,s.lineage);assert.deepEqual(await s.owner.invoke(h,request()),new Uint8Array(request().input));
});
test('original opaque handles and one noncompeting resource owner are required',async t=>{
 const s=setup(t),h=await s.owner.load(s.descriptor,s.lineage);assert.throws(()=>s.owner.inspect({...h}),errorCode('ForeignOwner'));await assert.rejects(s.owner.load(s.descriptor,s.lineage),errorCode('InvalidContract'));assert.throws(()=>createGenericCapabilityResourceOwner(s.consumer).inspect(h),errorCode('ForeignOwner'));
});
test('target mismatch rejects before accessing an absent consumer filesystem',async t=>{
 const s=setup(t),owner=createGenericCapabilityResourceOwner(s.consumer+'/absent');await assert.rejects(owner.load(s.descriptor,s.lineage,{...s.descriptor.target,revision:'other'}),errorCode('InvalidContract'));
});
test('exact bytes, manifest version and export must match before native evaluation',async t=>{
 const s=setup(t);await assert.rejects(s.owner.load({...s.descriptor,implementation:{...s.descriptor.implementation,sha256:'0'.repeat(64)}},s.lineage),errorCode('StaleOwner'));await assert.rejects(s.owner.load({...s.descriptor,implementation:{...s.descriptor.implementation,version:'2.0.0'}},s.lineage),errorCode('InvalidContract'));await assert.rejects(s.owner.load({...s.descriptor,implementation:{...s.descriptor.implementation,export:'./missing'}},s.lineage),errorCode('InvalidContract'));
});
test('does not search ancestor or working-directory installations',async t=>{
 const s=setup(t),nested=path.join(s.consumer,'nested');mkdirSync(nested);await assert.rejects(createGenericCapabilityResourceOwner(nested).load(s.descriptor,s.lineage));
});
test('rejects symlink and competing conditional exports',async t=>{
 const s=setup(t);rmSync(path.join(s.root,'copy.mjs'));symlinkSync(path.join(source,'copy.mjs'),path.join(s.root,'copy.mjs'));assert.throws(()=>captureGenericCapabilityPackage(s.root),errorCode('InvalidContract'));
 const q=setup(t,root=>{const p=JSON.parse(readFileSync(path.join(root,'package.json'),'utf8'));p.exports['./resource']={import:'./resource.mjs',default:'./copy.mjs'};writeFileSync(path.join(root,'package.json'),JSON.stringify(p));});await assert.rejects(q.owner.load(q.descriptor,q.lineage),errorCode('UnsupportedCapability'));
});
test('supports exact root and subpath import-only export forms',async t=>{
 for(const exported of ['./resource.mjs',{import:'./resource.mjs'},{'.':{import:'./resource.mjs'}},{'./resource':{import:'./resource.mjs'}}]){
  const s=setup(t,root=>{const p=JSON.parse(readFileSync(path.join(root,'package.json'),'utf8'));p.exports=exported;writeFileSync(path.join(root,'package.json'),JSON.stringify(p));}),subpath=typeof exported==='object'&&'./resource'in exported?'./resource':'.',descriptor={...s.descriptor,implementation:{...s.descriptor.implementation,export:subpath}},h=await s.owner.load(descriptor,s.lineage);assert.deepEqual(await s.owner.invoke(h,request()),new Uint8Array(request().input));
 }
});
for(const [name,spec]of [['private absolute','/home/private/owner.mjs'],['escaping','../../private.mjs'],['bare dependency','private-owner'],['missing local','./missing.mjs'],['loader builtin','node:module']] as const)test('checks the full static closure before evaluation: '+name,async t=>{
 const s=setup(t,root=>{writeFileSync(path.join(root,'copy.mjs'),"import {hidden} from '"+spec+"';\nthrow Error('EVALUATED_BEFORE_CLOSURE');\nexport function copyWire(input){return input;}\n");});await assert.rejects(s.owner.load(s.descriptor,s.lineage),(e:unknown)=>e instanceof Error&&!e.message.includes('EVALUATED_BEFORE_CLOSURE')&&/InvalidContract|UnsupportedCapability/.test(e.message));
});
for(const code of ["const r=require;r('private-owner');","const r=import('private-owner');","const r=`${import('private-owner')}`;","const r=process.getBuiltinModule('module');","const r=eval('import(1)');"])test('rejects unsupported dynamic/CommonJS loading before evaluation: '+code.slice(0,30),async t=>{
 const s=setup(t,root=>{writeFileSync(path.join(root,'copy.mjs'),code+'\nexport function copyWire(input){return input;}\n');});await assert.rejects(s.owner.load(s.descriptor,s.lineage),errorCode('UnsupportedCapability'));
});
test('declared transitive packages are explicitly unsupported',async t=>{
 const s=setup(t,root=>{const p=JSON.parse(readFileSync(path.join(root,'package.json'),'utf8'));p.dependencies={'unselected':'1.0.0'};writeFileSync(path.join(root,'package.json'),JSON.stringify(p));});await assert.rejects(s.owner.load(s.descriptor,s.lineage),errorCode('UnsupportedCapability'));
});
test('stale byte closure, added members and removed members invalidate existing handles',async t=>{
 for(const change of ['edit','add','remove']){const s=setup(t),h=await s.owner.load(s.descriptor,s.lineage);if(change==='edit')writeFileSync(path.join(s.root,'copy.mjs'),'export function copyWire(input){return input;}\n');if(change==='add')writeFileSync(path.join(s.root,'extra.txt'),'extra');if(change==='remove')rmSync(path.join(s.root,'copy.mjs'));assert.throws(()=>s.owner.assertCurrent(h));await assert.rejects(s.owner.invoke(h,request()));}
});
test('direct inference refuses tool brokers and providers remain unqualified',async t=>{
 const s=setup(t),h=await s.owner.load(s.descriptor,s.lineage);await assert.rejects(s.owner.invoke(h,request({toolBroker:{async invoke(){return Buffer.from('{}');}}})),errorCode('UnsupportedCapability'));
 const q=setup(t);await assert.rejects(q.owner.load({...q.descriptor,mode:'provider'},q.lineage),errorCode('UnsupportedCapability'));
});
test('provider mode rejects before evaluating an installed module or factory',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"throw Error('PROVIDER_ACTIVATED');\nexport function createCapabilityResource(s){throw Error('FACTORY_ACTIVATED');}\n"));await assert.rejects(s.owner.load({...s.descriptor,mode:'provider'},s.lineage),errorCode('UnsupportedCapability'));
});
test('private installed package rejects before evaluating its module or factory',async t=>{
 const s=setup(t,root=>{const p=JSON.parse(readFileSync(path.join(root,'package.json'),'utf8'));p.private=true;writeFileSync(path.join(root,'package.json'),JSON.stringify(p));writeFileSync(path.join(root,'resource.mjs'),"throw Error('PRIVATE_PACKAGE_EVALUATED');\nexport function createCapabilityResource(s){throw Error('PRIVATE_FACTORY_EVALUATED');}\n");});
 await assert.rejects(s.owner.load(s.descriptor,s.lineage),errorCode('UnsupportedCapability'));
});
test('selected agent harness uses only bounded mediated tools',async t=>{
 const s=setup(t),d=agent(s),h=await s.owner.load(d,s.lineage);let calls=0;const input=request({operation:'agent.run',limits:d.bounds,toolBroker:{async invoke(name,wire){assert.equal(name,'lookup');calls++;return wire;}}});assert.deepEqual(await s.owner.invoke(h,input),new Uint8Array(input.input));assert.equal(calls,1);await assert.rejects(s.owner.invoke(h,request({operation:'agent.run',limits:d.bounds})),errorCode('UnsupportedCapability'));
});
test('agent harness identity cannot be replaced or plural',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,harness_owner:['one','two'],async invoke(r){return r.input;}});}\n"));await assert.rejects(s.owner.load(agent(s),s.lineage),errorCode('InvalidContract'));
});
test('post-await package drift/cancellation/deadline checks prevent returned fixture bytes',async t=>{
 for(const reason of ['drift','cancel','deadline']){
  const s=setup(t),d=agent(s),h=await s.owner.load(d,s.lineage),controller=new AbortController();
  await assert.rejects(s.owner.invoke(h,request({operation:'agent.run',limits:d.bounds,deadline_ms:reason==='deadline'?Date.now()+100:Date.now()+30000,signal:controller.signal,toolBroker:{async invoke(_name,wire){if(reason==='drift')writeFileSync(path.join(s.root,'copy.mjs'),readFileSync(path.join(s.root,'copy.mjs'),'utf8')+'\n');if(reason==='cancel')controller.abort();if(reason==='deadline')await new Promise(resolve=>setTimeout(resolve,130));return wire;}}})),errorCode('StaleOwner'));
 }
});
test('caller request mutation cannot replace a captured deadline or broker during await',async t=>{
 const s=setup(t),d=agent(s),h=await s.owner.load(d,s.lineage),controller=new AbortController();let replacementCalls=0;
 const input=request({operation:'agent.run',limits:d.bounds,signal:controller.signal,toolBroker:{async invoke(_name,wire){controller.abort();(input as {signal?:AbortSignal}).signal=new AbortController().signal;(input as {deadline_ms:number}).deadline_ms=Date.now()+60000;(input as {toolBroker?:unknown}).toolBroker={async invoke(){replacementCalls++;return wire;}};return wire;}}});
 await assert.rejects(s.owner.invoke(h,input),errorCode('StaleOwner'));assert.equal(replacementCalls,0);
});
test('load checks cancellation and expiry after awaited package factory',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return new Promise(resolve=>setTimeout(()=>resolve(Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,async invoke(r){return r.input;}})),50));}\n"));const controller=new AbortController();setTimeout(()=>controller.abort(),10);await assert.rejects(s.owner.load(s.descriptor,s.lineage,s.descriptor.target,{signal:controller.signal}),errorCode('StaleOwner'));
});
test('load rechecks current package and cancellation after awaited module evaluation',async t=>{
 for(const reason of ['drift','cancel']){
  const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"await new Promise(resolve=>setTimeout(resolve,70));\nexport function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,async invoke(r){return r.input;}});}\n")),controller=new AbortController();
  setTimeout(()=>{if(reason==='drift')writeFileSync(path.join(s.root,'copy.mjs'),readFileSync(path.join(s.root,'copy.mjs'),'utf8')+'\n');else controller.abort();},10);
  await assert.rejects(s.owner.load(s.descriptor,s.lineage,s.descriptor.target,{signal:controller.signal}),errorCode('StaleOwner'));
 }
});
test('checks bounded input/output and declared operations',async t=>{
 const s=setup(t),h=await s.owner.load(s.descriptor,s.lineage);await assert.rejects(s.owner.invoke(h,request({operation:'agent.run'})),errorCode('InvalidContract'));await assert.rejects(s.owner.invoke(h,request({input:Buffer.alloc(8193)})),errorCode('InvalidContract'));await assert.rejects(s.owner.invoke(h,request({limits:{...bounds,max_output_bytes:1}})),errorCode('InvalidContract'));await assert.rejects(s.owner.invoke(h,request({deadline_ms:Date.now()-1})),errorCode('StaleOwner'));
});
test('never-settling native invocation times out and cannot be dispatched again',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,invoke(r){return new Promise(()=>{});}});}\n")),h=await s.owner.load(s.descriptor,s.lineage),started=Date.now();
 await assert.rejects(s.owner.invoke(h,request({deadline_ms:Date.now()+150})),errorCode('deadline expired'));assert.ok(Date.now()-started<1500);
 await assert.rejects(s.owner.invoke(h,request()),errorCode('quarantined'));await assert.rejects(s.owner.load(s.descriptor,s.lineage),errorCode('InvalidContract'));
});
for(const phase of ['factory','module'])test('never-settling '+phase+' times out without reopening the resource identity',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),phase==='factory'?"export function createCapabilityResource(s){return new Promise(()=>{});}\n":"await new Promise(()=>{});\nexport function createCapabilityResource(s){throw Error('FACTORY_STARTED');}\n")),started=Date.now();
 await assert.rejects(s.owner.load(s.descriptor,s.lineage,s.descriptor.target,{deadline_ms:Date.now()+300}),errorCode('deadline expired'));assert.ok(Date.now()-started<1500);
 await assert.rejects(s.owner.load(s.descriptor,s.lineage),errorCode('InvalidContract'));
});
test('aborting a never-settling invocation rejects promptly and quarantines the handle',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,invoke(r){return new Promise(()=>{});}});}\n")),h=await s.owner.load(s.descriptor,s.lineage),controller=new AbortController(),started=Date.now();setTimeout(()=>controller.abort(),70);
 await assert.rejects(s.owner.invoke(h,request({signal:controller.signal})),errorCode('cancelled'));assert.ok(Date.now()-started<1500);await assert.rejects(s.owner.invoke(h,request()),errorCode('quarantined'));
});
test('tools attempted after native timeout cannot reach the original broker',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,harness_owner:s.target.model_or_harness,async invoke(r){await new Promise(resolve=>setTimeout(resolve,200));return r.toolBroker.invoke('lookup',r.input);}});}\n")),d=agent(s),h=await s.owner.load(d,s.lineage);let calls=0;
 await assert.rejects(s.owner.invoke(h,request({operation:'agent.run',limits:d.bounds,deadline_ms:Date.now()+70,toolBroker:{async invoke(_name,wire){calls++;return wire;}}})),errorCode('deadline expired'));
 await new Promise(resolve=>setTimeout(resolve,250));assert.equal(calls,0);await assert.rejects(s.owner.invoke(h,request({operation:'agent.run',limits:d.bounds})),errorCode('quarantined'));
});
test('late native rejection is observed after timeout',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,async invoke(r){await new Promise(resolve=>setTimeout(resolve,150));throw Error('LATE_NATIVE_REJECTION');}});}\n")),h=await s.owner.load(s.descriptor,s.lineage);
 await assert.rejects(s.owner.invoke(h,request({deadline_ms:Date.now()+60})),errorCode('deadline expired'));await new Promise(resolve=>setTimeout(resolve,200));
});
test('caller JSON cannot substitute an AbortSignal',async t=>{
 const s=setup(t),h=await s.owner.load(s.descriptor,s.lineage);await assert.rejects(s.owner.invoke(h,request({signal:{aborted:false} as AbortSignal})),errorCode('actual AbortSignal required'));
});
test('native harness receives detached frozen tool schemas from the dispatcher',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,harness_owner:s.target.model_or_harness,async invoke(r){await new Promise(resolve=>setTimeout(resolve,40));return new TextEncoder().encode(JSON.stringify({schemas:r.tool_schemas,frozen:Object.isFrozen(r.tool_schemas)&&Object.isFrozen(r.tool_schemas[0])&&Object.isFrozen(r.tool_schemas[0].argument_schema)}));}});}\n")),d=agent(s),h=await s.owner.load(d,s.lineage),schemas=[{name:'lookup',argument_schema:{type:'string'},result_schema:{type:'object'}}];
 const pending=s.owner.invoke(h,request({operation:'agent.run',limits:d.bounds,tool_schemas:schemas,toolBroker:{async invoke(_name,wire){return wire;}}}));schemas[0]!.argument_schema.type='number';schemas.push({name:'other',argument_schema:{type:'boolean'},result_schema:{type:'object'}});
 const result=JSON.parse(new TextDecoder().decode(await pending));assert.deepEqual(result,{schemas:[{name:'lookup',argument_schema:{type:'string'},result_schema:{type:'object'}}],frozen:true});
});
test('provided schemas reject unselected tool names before the original broker',async t=>{
 const s=setup(t),d=agent(s),h=await s.owner.load(d,s.lineage);let calls=0;
 await assert.rejects(s.owner.invoke(h,request({operation:'agent.run',limits:d.bounds,tool_schemas:[{name:'other',argument_schema:{type:'string'},result_schema:{type:'string'}}],toolBroker:{async invoke(_name,wire){calls++;return wire;}}})),errorCode('InvalidContract'));assert.equal(calls,0);
});
test('tool schema declarations are finite, closed and uniquely named',async t=>{
 const s=setup(t),d=agent(s),h=await s.owner.load(d,s.lineage),one={name:'lookup',argument_schema:{type:'string'},result_schema:{type:'string'}};
 for(const schemas of [[one,one],[{...one,unknown:true}],[{...one,name:'../private'}],[{...one,result_schema:null}],Array.from({length:33},(_,i)=>({...one,name:'Tool'+i}))])await assert.rejects(s.owner.invoke(h,request({operation:'agent.run',limits:d.bounds,tool_schemas:schemas as never,toolBroker:{async invoke(_name,wire){return wire;}}})),errorCode('InvalidContract'));
});
test('inference/document/search invocations reject tool schema declarations',async t=>{
 for(const [contract,operation,capability]of [['inference/v1','text.structured','structured-output'],['document/v1','document.parse','document-parse'],['search/v1','search.query','bounded-search']] as const){
  const s=setup(t),d={...s.descriptor,contract,operations:[operation],capabilities:[capability]},h=await s.owner.load(d,s.lineage);await assert.rejects(s.owner.invoke(h,request({operation,tool_schemas:[]})),errorCode('UnsupportedCapability'));
 }
});
test('retirement skips abandoned native cleanup, is idempotent and preserves quarantine',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,invoke(r){return new Promise(()=>{});},dispose(){return new Promise(resolve=>setTimeout(resolve,800));}});}\n")),h=await s.owner.load(s.descriptor,s.lineage);
 await assert.rejects(s.owner.invoke(h,request({deadline_ms:Date.now()+100})),errorCode('deadline expired'));const started=Date.now();await s.owner.dispose(h);assert.ok(Date.now()-started<400);await s.owner.dispose(h);assert.throws(()=>s.owner.inspect(h),errorCode('ForeignOwner'));await assert.rejects(s.owner.load(s.descriptor,s.lineage),errorCode('InvalidContract'));
});
test('retirement safely releases a stale handle without running stale cleanup',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,invoke(r){return r.input;},dispose(){return new Promise(resolve=>setTimeout(resolve,800));}});}\n")),h=await s.owner.load(s.descriptor,s.lineage);writeFileSync(path.join(s.root,'copy.mjs'),readFileSync(path.join(s.root,'copy.mjs'),'utf8')+'\n');
 const started=Date.now();await s.owner.dispose(h);assert.ok(Date.now()-started<400);await s.owner.dispose(h);assert.throws(()=>s.owner.inspect(h),errorCode('ForeignOwner'));
 await assert.rejects(s.owner.dispose({...h}),errorCode('ForeignOwner'));
});
test('never-settling native cleanup is bounded and cannot mask the original failure',async t=>{
 const s=setup(t,root=>writeFileSync(path.join(root,'resource.mjs'),"export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,invoke(r){throw Error('ORIGINAL_FIXTURE_FAILURE');},dispose(){return new Promise(()=>{});}});}\n")),h=await s.owner.load(s.descriptor,s.lineage),started=Date.now();
 const failure=await s.owner.invoke(h,request()).catch(error=>error);await s.owner.dispose(h);assert.match(failure.message,/ORIGINAL_FIXTURE_FAILURE/);assert.ok(Date.now()-started<2000);await s.owner.dispose(h);await assert.rejects(s.owner.load(s.descriptor,s.lineage),errorCode('InvalidContract'));
});
