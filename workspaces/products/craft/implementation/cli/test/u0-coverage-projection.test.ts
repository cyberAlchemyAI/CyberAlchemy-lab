import test,{type TestContext} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync,renameSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {compileProject} from '../src/compilation/certificate.js';
import {checkDirectBusinessSourceGraphV2} from '../src/formalization/direct-condition-binding.js';
import {checkDirectSourceCoverageV2,assertDirectSourceCoverageV2Current,lookupDirectSourceCoverageOwnerV2,createBusinessDirectCoverageOwnerV2} from '../src/profile-engine/business-authoring-coverage.js';
import {projectDirectSourceViewsV2,assertDirectSourceViewsV2Current,createBusinessCoverageViewsOwnerV2} from '../src/profile-engine/business-authoring-views.js';
import {createBusinessCoreRecipeOwnerV2} from '../src/profile-engine/business-authoring-recipes.js';
import {createBusinessReviewOwnerV2} from '../src/profile-engine/business-decision.js';
import {createBusinessRequestStagesOwnerV2} from '../src/profile-engine/business-authoring-request.js';
import {createAuthoringBusinessInputOwnerV2} from '../src/profile-engine/business-authoring-input.js';
import {createBusinessDirectApplicationOwnerV2} from '../src/profile-engine/business-authoring-application.js';
import type {BusinessPureGenerationOwnerV2} from '../src/profile-engine/business-authoring-stages-v2.js';
import {dataDigest,sha256} from '../src/profile-engine/contracts.js';
// Original source/compiler/typed component projections only. U09 owns the actual
// accepted application/native view witness. Open Questions: CONTEXT S01, U09.
const root=path.resolve(import.meta.dirname,'../../../../../..'),alch=path.join(root,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src');
const original=readFileSync(new URL('profile-engine/fixtures/u0-v2/business.alch',import.meta.url),'utf8');
async function fixture(t:TestContext,text=original){
 const parser=await import(pathToFileURL(path.join(alch,'business-authoring-parser.ts')).href),resolver=await import(pathToFileURL(path.join(alch,'business-authoring-resolve.ts')).href),carriers=await import(pathToFileURL(path.join(alch,'business-authoring-carriers.ts')).href),lower=await import(pathToFileURL(path.join(alch,'application-domain-lowering.ts')).href);
 const business=resolver.resolveBusinessSpecV2(parser.parseBusinessSourceV2(text)),lowered=carriers.lowerDirectBusinessV2(business),formation=lower.lowerDirectApplicationDomainV2(lowered),directory=mkdtempSync(path.join(os.tmpdir(),'craft-s01-'));t.after(()=>rmSync(directory,{recursive:true,force:true}));
 for(const [relative,content]of Object.entries(formation.projectFiles)){const file=path.join(directory,relative);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,content as string);}
 const source=checkDirectBusinessSourceGraphV2(compileProject(directory).graph,{source:business.source,spec:business.data,executable:lowered.executable,assurance:lowered.assurance}),coverage=checkDirectSourceCoverageV2(source);
 return {source,coverage,directory};
}
const candidate=(coverage:ReturnType<typeof checkDirectSourceCoverageV2>)=>structuredClone({inventory:coverage.inventory,owners:coverage.owners,unresolved_native_obligations:coverage.unresolved_native_obligations});
test('S01 independent physical source denominator includes all facts and separately checked executable/Mapping/native obligations',async t=>{
 const {source,coverage}=await fixture(t),facts=original.split(/\r?\n/).filter(line=>line.trim()&&!line.trimStart().startsWith('#'));
 assert.equal(coverage.kind,'checked-direct-source-coverage-v2');assert.equal(Object.hasOwn(coverage,'application'),false);
 const authored=coverage.inventory.obligations.filter(row=>row.kind==='authored-fact');assert.equal(authored.length,facts.length);
 assert.deepEqual(authored.map(row=>row.origins[0]!.selector),source.checked.transfer.spec.source_spans.map(span=>span.selector));
 for(const kind of ['entity-shape','condition','guard','result','rejection','effects','entry','permission'])assert.equal(coverage.inventory.obligations.filter(row=>row.id==='executable:'+kind).length,1);
 for(const side of ['input','output'])assert.equal(lookupDirectSourceCoverageOwnerV2(coverage,'derived:'+side+'-mapping').state,'checked-owner');
 assert.equal(coverage.unresolved_native_obligations.length,7);assert.equal(coverage.inventory.obligations.length,facts.length+8+2+7);
 assert.equal(coverage.owners.length,facts.length+8+2);assertDirectSourceCoverageV2Current(coverage);
});
test('S01 exact Rule/Entity/Operation/Interface/Mapping lookup resolves original typed closure identities',async t=>{
 const {source,coverage}=await fixture(t);
 for(const [id,selector]of [['executable:entity-shape','dispatching:submission'],['executable:condition','dispatching:can-process'],['executable:guard','dispatching:process'],['executable:result','dispatching:process'],['executable:rejection','dispatching:process'],['executable:effects','dispatching:process'],['executable:entry','dispatching:process-http'],['executable:permission','dispatching:process-http'],['derived:input-mapping','dispatching:craftrequest-process-http-input'],['derived:output-mapping','dispatching:craftrequest-process-http-output']]){
  const result=lookupDirectSourceCoverageOwnerV2(coverage,id!);assert.equal(result.state,'checked-owner');if(result.state!=='checked-owner')assert.fail();assert.equal(result.owner.owner_selector,selector);assert.equal(result.owner.owner_sha256,source.closures.find(row=>row.selector===selector)!.typed_closure_sha256);
 }
 for(const id of coverage.unresolved_native_obligations)assert.deepEqual(lookupDirectSourceCoverageOwnerV2(coverage,id),{state:'pending-producer',owner:null});
 assert.throws(()=>lookupDirectSourceCoverageOwnerV2(coverage,'not-an-obligation'),/DIRECT_SELECTOR/);
});
test('S01 missing/duplicated conditions, owner selectors and invented FormalClaim coverage reject',async t=>{
 const {source,coverage}=await fixture(t);
 for(const mutate of [
  (value:any)=>value.owners.splice(value.owners.findIndex((row:any)=>row.obligation_id==='executable:condition'),1),
  (value:any)=>value.owners.push(value.owners[0]),
  (value:any)=>value.owners.find((row:any)=>row.obligation_id==='executable:condition').owner_selector='dispatching:invented',
  (value:any)=>value.owners.push({obligation_id:'formal-claim:Invented',owner_selector:'claim:fake',owner_sha256:'a'.repeat(64)}),
  (value:any)=>value.inventory.obligations.pop(),
  (value:any)=>value.owners.push({obligation_id:'native:handler',owner_selector:'native:fake',owner_sha256:'b'.repeat(64)}),
 ]){const value=candidate(coverage);mutate(value);assert.throws(()=>checkDirectSourceCoverageV2(source,value),/DIRECT_COVERAGE/);}
 checkDirectSourceCoverageV2(source,candidate(coverage));
});
test('S01 no generated/native subject or formal proof is invented by the actual source projection',async t=>{
 const {coverage}=await fixture(t),views=projectDirectSourceViewsV2(coverage);assertDirectSourceViewsV2Current(views);
 assert.equal(views.kind,'checked-direct-source-views-v2');assert.equal(views.system.stage,'checked-source-only');assert.equal(views.system.generated_source,null);assert.equal(views.system.native,null);assert.equal(views.system.selection,null);assert.equal(views.bridge.selection_sha256,null);assert.equal(views.bridge.capture_sha256,null);assert.equal(views.bridge.entry_intent_sha256,null);
 assert.equal((views.business.assurance as any).claims.length,0);assert.equal(views.bridge.ontology_admitted,false);assert.equal(views.bridge.realized_sha256,null);
 assert.equal((views.bridge.links as any[]).filter(row=>row.state==='pending-producer').length,7);assert.equal(views.files.length,3);
 assert.deepEqual(views.files.map(file=>file.kind),['business-graph','system-graph','business-system-bridge']);
 for(const file of views.files){assert.equal(sha256(file.artifact.content),file.artifact.sha256);assert.ok(JSON.parse(file.artifact.content).open_questions.length);}
});
test('S01 system projection uses original six checked graph nodes and five actual relationships',async t=>{
 const {source,coverage}=await fixture(t),views=projectDirectSourceViewsV2(coverage),graph=(views.system.domain_graphs as any[])[0];
 assert.equal(graph.graph_sha256,source.graph_sha256);assert.deepEqual(graph.nodes.map((node:any)=>[node.selector,node.kind]),source.graph.nodes.map(node=>[node.selector,node.kind]));
 assert.equal(dataDigest(graph.relationships),dataDigest(source.graph.relationships));assert.equal(graph.relationships.length,5);
 for(const node of graph.nodes)assert.equal(node.typed_closure_sha256,source.closures.find(row=>row.selector===node.selector)!.typed_closure_sha256);
});
test('S01 bridge links preserve every original source span and actual typed owner',async t=>{
 const {source,coverage}=await fixture(t),views=projectDirectSourceViewsV2(coverage),links=views.bridge.links as any[];
 assert.equal(links.length,coverage.inventory.obligations.length);assert.equal(new Set(links.map(row=>row.obligation_id)).size,links.length);
 for(const row of links){
  for(const origin of row.origins){const span=source.checked.transfer.spec.source_spans.find(span=>span.selector===origin.selector);assert.ok(span);assert.equal(origin.source,span.source);assert.equal(origin.sha256,span.source_sha256);}
  const owner=lookupDirectSourceCoverageOwnerV2(coverage,row.obligation_id);assert.equal(row.state,owner.state);assert.equal(dataDigest(row.owner),dataDigest(owner.owner));
 }
});
test('S01 changing authored rejection changes checked operation and projected bridge while retaining native pending',async t=>{
 const first=await fixture(t),second=await fixture(t,original.replace('on-rejection delivery-verification-required','on-rejection acknowledgement-not-approved'));
 const a=projectDirectSourceViewsV2(first.coverage),b=projectDirectSourceViewsV2(second.coverage);assert.notEqual(a.views_sha256,b.views_sha256);
 assert.equal((b.system.pure_operation as any).rejection_code,'acknowledgement-not-approved');assert.deepEqual(b.system.unresolved_native_obligations,a.system.unresolved_native_obligations);
});
test('S01 projection is deterministic immutable display data, not rehydratable view custody',async t=>{
 const {coverage}=await fixture(t),a=projectDirectSourceViewsV2(coverage),b=projectDirectSourceViewsV2(coverage);assert.equal(a.views_sha256,b.views_sha256);assert.ok(Object.isFrozen(a.files)&&Object.isFrozen(a.business));
 for(const fake of [{...a},structuredClone(a),new Proxy(a,{})])assert.throws(()=>assertDirectSourceViewsV2Current(fake),/DIRECT_HANDLE/);
 for(const fake of [{...coverage},structuredClone(coverage),new Proxy(coverage,{})]){assert.throws(()=>assertDirectSourceCoverageV2Current(fake),/DIRECT_HANDLE/);assert.throws(()=>projectDirectSourceViewsV2(fake),/DIRECT_HANDLE/);}
});
test('S01 source rewrite or physical replacement retires original coverage and all projected views',async t=>{
 const {coverage,directory}=await fixture(t),views=projectDirectSourceViewsV2(coverage),file=path.join(directory,'specs/dispatching/nodes/can-process.json'),bytes=readFileSync(file);
 renameSync(file,file+'.old');writeFileSync(file,bytes);assert.throws(()=>assertDirectSourceCoverageV2Current(coverage),/BUSINESS_DIRECT_CONDITION_FILE_STALE/);assert.throws(()=>assertDirectSourceViewsV2Current(views),/BUSINESS_DIRECT_CONDITION_FILE_STALE/);
});
function productionOwners(){
 let graphReads=0,nativeReads=0;
 const recipes=createBusinessCoreRecipeOwnerV2({assertCurrent(){nativeReads++;throw Error('actual native required');},capture(){throw Error('actual capture required');}}),reviews=createBusinessReviewOwnerV2(recipes);
 const generation:BusinessPureGenerationOwnerV2={generate(){throw Error('actual generated application required');},async importGenerated(){throw Error('actual import required');},assertCurrent(){throw Error('actual import required');}};
 const requests=createBusinessRequestStagesOwnerV2(recipes,generation,{assertCurrent(){throw Error('actual basis required');},assertSelectionBasis(){throw Error('actual selection required');},assets(){throw Error('actual assets required');}});
 const inputs=createAuthoringBusinessInputOwnerV2(recipes,reviews,requests),applications=createBusinessDirectApplicationOwnerV2(inputs,{capture(){graphReads++;throw Error('actual graph required');},assertCurrent(){throw Error('actual graph required');}});
 const coverage=createBusinessDirectCoverageOwnerV2(inputs,applications,requests,generation),views=createBusinessCoverageViewsOwnerV2(coverage);
 return {coverage,views,reads:()=>graphReads+nativeReads};
}
test('S01 raw source/input/application/coverage/view JSON cannot mint production projection custody',async t=>{
 const {coverage,views,reads}=productionOwners(),f=await fixture(t),sourceView=projectDirectSourceViewsV2(f.coverage);let getters=0;
 for(const fake of [{},{accepted:true},{get application(){getters++;throw Error('do not read');}},f.coverage,sourceView]){
  assert.throws(()=>coverage.inventory(fake as never),/UNREGISTERED/);assert.throws(()=>coverage.check(fake as never),/UNREGISTERED/);assert.throws(()=>coverage.assertCurrent(fake as never),/DIRECT_HANDLE/);assert.throws(()=>views.project(fake as never),/DIRECT_HANDLE/);assert.throws(()=>views.assertCurrent(fake as never),/DIRECT_HANDLE/);
 }
 assert.equal(getters,0);assert.equal(reads(),0);
});
test('S01 optional established FOL claim remains source-linked unproved residue and never replaces direct condition ownership',async t=>{
 const assurance=`
definition Eligibility:
  requirement Processing
  input item Submission
  meaning "Supplied eligibility."
  boolean-field item.verified

formal-claim EligibilityClaim version 1:
  requirement Processing
  supersedes none
  profile fol-core/1-candidate
  sort SubmissionValue interpreted-as Submission
  predicate Eligible(SubmissionValue) defined-by Eligibility
  constant current: SubmissionValue
  proposition Eligible(current)
  ceiling "One supplied flag; no proof."
  subject CanProcess
  subject Process
`;
 const bare=await fixture(t),claimed=await fixture(t,original+assurance),views=projectDirectSourceViewsV2(claimed.coverage);
 assert.equal(claimed.coverage.inventory.executable_sha256,bare.coverage.inventory.executable_sha256);
 const claims=(views.business.assurance as any).claims;assert.equal(claims.length,1);assert.equal(claims[0].evidence,'unproved-residue');assert.equal(claims[0].claim.proposition,'Eligible(current)');
 assert.equal(lookupDirectSourceCoverageOwnerV2(claimed.coverage,'executable:condition').owner?.owner_selector,'dispatching:can-process');
 assert.equal(claimed.coverage.owners.some(owner=>owner.obligation_id.startsWith('formal-claim:')),false);assert.equal(claimed.coverage.unresolved_native_obligations.length,7);
});
test('S01 replaced producer methods are detected before raw input or projection is inspected',()=>{
 const {coverage}=productionOwners(),peer={...coverage},views=createBusinessCoverageViewsOwnerV2(peer);let invoked=0;
 peer.source=()=>{invoked++;throw Error('replaced');};assert.throws(()=>views.inventory({} as never),/DIRECT_OWNER_STALE/);assert.equal(invoked,0);
});
