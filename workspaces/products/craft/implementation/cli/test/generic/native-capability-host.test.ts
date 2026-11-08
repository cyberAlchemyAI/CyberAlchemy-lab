/** Qualified native package + original checked application/Auth/codec integration.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import test from 'node:test';import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync} from 'node:fs';import path from 'node:path';import {tmpdir} from 'node:os';import {fileURLToPath} from 'node:url';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';
import {createGenericAuthFixture,prepareGenericFixtureRuntime} from '../../src/generic/testing.js';
import {captureGenericNativeProfileArtifact,inspectGenericNativeProfileArtifact} from '../../src/generic/native-profile-resource.js';
import {createGenericNativeCapabilityHost} from '../../src/generic/native-capability-host.js';
import {createGenericQueryObservationOwner} from '../../src/generic/query-observation.js';
import {DatabaseSync} from 'node:sqlite';
import {coreSha256} from '../../src/commerce/commerce-core-syntax.js';import {dataDigest} from '../../src/profile-engine/contracts.js';import {capabilityFixture} from './capability-fixtures.js';
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url)),c07=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C07'),wire=(v:unknown)=>new TextEncoder().encode(JSON.stringify(v));
const source=`module Example version 1
value-object Request:
  id UInt64
  verified Bool
interface Model:
  kind bounded-schema
  exposes Request
mapping Echo:
  input request Request
  target Request
  total true
  field id <- request.id
  field verified <- request.verified
operation Answer:
  input request Request
  output Request
  return Echo(request)
entity OwnedRequest:
  owner Craft.Generated.Auth.ReadySubjectId
  id UInt64
  value Request
  identity owner, id
query ReadOwnedRequest:
  input id UInt64
  context actor Craft.Generated.Auth.CustomerContext
  source stored OwnedRequest
  output optional<Request>
  where stored.owner == actor.customerId and stored.id == id and actor.currentActionAllowed
  project stored.value
  on-missing return none
  on-unavailable fail read-unavailable
entry Example.ReadEntry:
  invokes Example.ReadOwnedRequest
  interaction request-response
  access:
    authenticated customer
    permission example.read-own
    auth-resource example
    auth-action read-own
    auth-scope example
`;
async function fixture(t:test.TestContext){const dir=mkdtempSync(path.join(tmpdir(),'craft-native-host-'));const closers:Array<()=>unknown|Promise<unknown>>=[];t.after(async()=>{try{for(const close of closers.reverse())await close();}finally{rmSync(dir,{recursive:true,force:true});}});const cleanup=(f:()=>unknown|Promise<unknown>)=>closers.push(f);mkdirSync(path.join(dir,'contracts'));const pkg=path.join(dir,'consumer/node_modules/@craft/selected-native');mkdirSync(pkg,{recursive:true});writeFileSync(path.join(pkg,'package.json'),JSON.stringify({name:'@craft/selected-native',version:'1.0.0',type:'module',license:'Apache-2.0',exports:{'./resource':'./resource.mjs'}}));writeFileSync(path.join(pkg,'resource.mjs'),`export function createCapabilityResource(binding,callback){return Object.freeze({abi:'craft.native-capability-resource/v1',operations:binding.realization.operations,capabilities:binding.realization.capabilities,async invoke(r){await callback?.(r);return new Uint8Array(r.input);}});}\n`);
 const artifact=captureGenericNativeProfileArtifact(pkg),profile=JSON.parse(readFileSync(path.join(c07,'profile.json'),'utf8'));profile.services=[{id:'ExampleService',module:'Example'}];writeFileSync(path.join(dir,'business.alch'),source);writeFileSync(path.join(dir,'profile.json'),JSON.stringify(profile));writeFileSync(path.join(dir,'contracts/bounds.json'),readFileSync(path.join(c07,'bounds.json')));const {selection,kernel}=capabilityFixture();selection.source_sha256=coreSha256(source);selection.profile_sha256=coreSha256(JSON.stringify(profile));selection.bindings[0].contract.result_type='Example.Request';selection.realizations[0].implementation={package:'@craft/selected-native',version:'1.0.0',export:'./resource',sha256:inspectGenericNativeProfileArtifact(artifact).sha256};selection.kernel.sha256=dataDigest(kernel);writeFileSync(path.join(dir,'selection.json'),JSON.stringify(selection));writeFileSync(path.join(dir,'kernel.json'),JSON.stringify(kernel));
 const composition=createGenericCompositionOwner(),handle=await composition.prepare({sourcePath:path.join(dir,'business.alch'),profilePath:path.join(dir,'profile.json'),capabilitySelectionPath:path.join(dir,'selection.json')});cleanup(()=>composition.dispose(handle));const review=composition.review(handle,'native-host');composition.accept(handle,{decision_id:'native-host',owner:'native-host',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,'decision.json'));
 const auth=await createGenericAuthFixture(composition,handle,{ownedDirectory:path.join(dir,'auth'),subjects:[{id:'subject',evidence:'synthetic-evidence',session:'synthetic-session'}],grants:[{subject:'subject',entry:'Example.ReadEntry'}]});cleanup(()=>auth.close());const setup=await prepareGenericFixtureRuntime(composition,handle,{service:'ExampleService',ownedDirectory:path.join(dir,'store'),nativeAuth:auth.nativeAuth}),runtime=setup.runtime;cleanup(()=>runtime.close());const actor=auth.actor(runtime,'subject','Example.ReadEntry');return {dir,pkg,artifact,composition,handle,runtime,auth,actor,cleanup,storePath:setup.storePath};}
test('native profile dispatch joins genuine application/runtime/Auth and exact generated UInt64 codecs',async t=>{const f=await fixture(t);let disclosures=0;const host=createGenericNativeCapabilityHost(f.composition,f.handle,{runtime:f.runtime,bindings:new Map([['Example.Selection',{artifact:f.artifact,entries:['Example.ReadEntry'],configure:(namespace,binding,getInvocation)=>namespace.createCapabilityResource(binding,()=>{const i=getInvocation();assert.equal(i.principal.actor,'subject');assert.equal(i.principal.tenant,'example');assert.equal(i.value.id,'18446744073709551615');}),assertDisclosure:()=>{disclosures++;}}]])});f.cleanup(()=>host.close());const h=host.openInvocation(f.actor,'Example.ReadEntry','Example.Selection',{deadline_ms:Date.now()+29000});const result=await host.invoke(h,wire({id:'18446744073709551615',verified:true}));assert.equal(result.value.id,'18446744073709551615');assert.equal(disclosures,1);await assert.rejects(host.invoke(h,wire({id:'1',verified:true})));assert.throws(()=>host.openInvocation(f.actor,'Other.Entry','Example.Selection',{deadline_ms:Date.now()+29000}));});
test('fresh grants and original source disclosure recheck prevent native result release',async t=>{const f=await fixture(t);let release=false;const host=createGenericNativeCapabilityHost(f.composition,f.handle,{runtime:f.runtime,bindings:new Map([['Example.Selection',{artifact:f.artifact,entries:['Example.ReadEntry'],configure:(namespace,binding)=>namespace.createCapabilityResource(binding,()=>{f.auth.setPermission('subject','Example.ReadEntry',false);}),assertDisclosure:()=>{release=true;}}]])});f.cleanup(()=>host.close());const h=host.openInvocation(f.actor,'Example.ReadEntry','Example.Selection',{deadline_ms:Date.now()+29000});await assert.rejects(host.invoke(h,wire({id:'1',verified:true})));assert.equal(release,false);});
test('captured installed artifact cannot be replaced by JSON or drifted file bytes',async t=>{const f=await fixture(t);assert.throws(()=>inspectGenericNativeProfileArtifact({...f.artifact}));writeFileSync(path.join(f.pkg,'resource.mjs'),'throw Error("replaced native module");');assert.throws(()=>inspectGenericNativeProfileArtifact(f.artifact),(error:any)=>error?.diagnostics?.[0]?.code==='StaleOwner');});

test('direct generated Query observation retains original Auth and SQLite custody without an agent binding',async t=>{const f=await fixture(t),owner=createGenericQueryObservationOwner(f.composition,f.handle,f.runtime);f.cleanup(()=>owner.close());const settings={deadline_ms:Date.now()+300000},lease=await owner.read(f.actor,'Example.ReadEntry',wire({id:'18446744073709551615'}),settings);assert.equal(owner.inspect(lease).value,null);assert.equal(owner.inspect(lease).principal.actor,'subject');assert.equal(owner.inspect(lease).principal.tenant,'example');assert.throws(()=>owner.inspect({...lease}));await owner.refresh(lease);f.auth.setPermission('subject','Example.ReadEntry',false);assert.throws(()=>owner.assertCurrent(lease));await assert.rejects(owner.refresh(lease));f.auth.setPermission('subject','Example.ReadEntry',true);const next=await owner.read(f.actor,'Example.ReadEntry',wire({id:'2'}),settings);const db=new DatabaseSync(f.storePath);try{db.exec('CREATE TABLE external_observation_mutation(value TEXT)');}finally{db.close();}assert.throws(()=>owner.inspect(next),error=>(error as any)?.diagnostics?.[0]?.code==='StaleOwner');});
