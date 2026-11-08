import assert from 'node:assert/strict';
import test from 'node:test';
import {composeProfile} from '../../src/profile-engine/compose.js';
import {createProfileCoverage,assertProfileCoverageComplete} from '../../src/profile-engine/coverage.js';
import {projectProfileViews} from '../../src/profile-engine/views.js';
import {compiledProfileFixture} from './profile-fixture.js';
// Open questions: native/runtime evidence remains PE08/12 and ORODI separate.
test('complete denominator includes guards/calculations/clauses/intents/access/wire/roles/claims',async t=>{
 const f=await compiledProfileFixture(t),composition=composeProfile(f.selection,f.functions),coverage=createProfileCoverage(composition);assertProfileCoverageComplete(composition,coverage);
 for(const id of ['business:quote.alch#rule:EnoughStock','business:quote.alch#calculation:QuoteTotal','intent:requestQuote','access:requestQuote','integration:quote.alch#Inventory','integration-field:quote.alch#Inventory#stock','claim:ExactQuoteTotal'])assert.ok(coverage.items.some(i=>i.id===id),id);
 assert.ok(coverage.items.some(i=>i.id.includes('#clause:')));assert.equal(coverage.items.find(i=>i.id==='claim:ExactQuoteTotal')!.state,'claim-residue');
 const a=projectProfileViews(composition),b=projectProfileViews(composition);assert.equal(a.sha256,b.sha256);assert.equal(a.bridge.ontology_admitted,false);assert.ok(a.system.domain_graphs.every(g=>g.node_selectors.length>0));
});
test('missing guard/calculation/limit/integration/claim and false evidence states reject',async t=>{
 const f=await compiledProfileFixture(t),composition=composeProfile(f.selection,f.functions),coverage=createProfileCoverage(composition);
 for(const needle of ['rule:EnoughStock','calculation:QuoteTotal','#clause:','integration-field:','claim:']){const bad=JSON.parse(JSON.stringify(coverage));bad.items.splice(bad.items.findIndex((i:any)=>i.id.includes(needle)),1);assert.throws(()=>assertProfileCoverageComplete(composition,bad),/PROFILE_COVERAGE_DENOMINATOR/);}
 const inflated=JSON.parse(JSON.stringify(coverage));inflated.items[0].evidence_states.push('finite-observed');assert.throws(()=>assertProfileCoverageComplete(composition,inflated),/PROFILE_COVERAGE_EVIDENCE/);
 const unowned=JSON.parse(JSON.stringify(coverage));unowned.items[0].artifact_refs=['invented.mjs'];assert.throws(()=>assertProfileCoverageComplete(composition,unowned),/PROFILE_COVERAGE_DENOMINATOR/);
});
