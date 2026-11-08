import test from 'node:test';
import assert from 'node:assert/strict';
import {businessApplicationFixture} from '../helpers/business-application.ts';
import {selectProfileConfiguration,composeProfile} from '../../src/profile-engine/compose.ts';
import {prepareRequestApplicationCallable} from '../../src/profile-engine/application-adapter.ts';
import {compileRequestApplicationBindingV1} from '../../src/system-integration/application-binding-v1.ts';
import {composeRequestApplicationPlanV1} from '../../src/generation/request-application-plan-v1.ts';
import {assertBusinessInputV2Current} from '../../src/profile-engine/business-input-v2.ts';
import {createProfileCoverage,assertProfileCoverageComplete} from '../../src/profile-engine/coverage.ts';
import {projectProfileViews} from '../../src/profile-engine/views.ts';
// Open questions: fresh installed projection/coverage replay BA18.
test('v2 coverage independently includes source clauses, meaning, guard/result paths, intent/access and claims',async t=>{
 const f=await businessApplicationFixture(t),selection=selectProfileConfiguration(f.input.snapshot),binding=compileRequestApplicationBindingV1(f.graph,f.source,f.plan),plan=composeRequestApplicationPlanV1(f.plan,binding);
 const d=f.derived,lineage={application_id:'commerce',original_source:'domain.alch',original_source_sha256:d.original_source_sha256,original_semantics_sha256:d.original_semantics_sha256,derived_source_sha256:d.source_sha256,derivation_sha256:d.derivation_sha256,line_map:d.line_map};
 const callable=prepareRequestApplicationCallable(f.graph,plan,binding,f.input.snapshot.project.application_intents[0]!,lineage,()=>assertBusinessInputV2Current(f.input)),composition=composeProfile(selection,[],[callable]),coverage=createProfileCoverage(composition);assertProfileCoverageComplete(composition,coverage);
 const required=['application-source:receiveNotice#formal-claim:IdentityClaim','application-source:receiveNotice#operation:ReceiveNotice','application-intent:receiveNotice','application-access:receiveNotice','application-argument:receiveNotice#payload','application-meaning:receiveNotice#/declarations/OrderNotice/properties/id/ontology','application-meaning:receiveNotice#/rule_meanings/IdentityValid/constants/identity','application-meaning:receiveNotice#/operation_behaviors/ReceiveNotice/result/root','application-meaning:receiveNotice#/required_guarantees/0'];
 for(const id of required)assert.ok(coverage.items.some(i=>i.id===id),id);
 for(const id of required){const altered=JSON.parse(JSON.stringify(coverage));altered.items=altered.items.filter((i:any)=>i.id!==id);assert.throws(()=>assertProfileCoverageComplete(composition,altered),/DENOMINATOR/);}
 const claims=coverage.items.filter(i=>i.kind==='formal-claim');assert.ok(claims.length>0);assert.ok(claims.every(i=>i.state==='claim-residue'));
 const inflated=JSON.parse(JSON.stringify(coverage));inflated.items.find((i:any)=>i.kind==='formal-claim').state='retained';assert.throws(()=>assertProfileCoverageComplete(composition,inflated),/UNSUPPORTED/);
 const views=projectProfileViews(composition),entry=views.system.applications[0]!;assert.equal(entry.request_application_plan_sha256,plan.plan_sha256);assert.equal(entry.lineage!.original_source_sha256,f.input.applications[0]!.source_sha256);assert.equal(views.bridge.ontology_admitted,false);assert.equal(views.business.application_models.length,1);
});
