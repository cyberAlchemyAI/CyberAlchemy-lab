/** Real protected business decisions; native/provider qualification is separate.
 * Open Questions: goals/plans/craft-service-profile-extensions-2026-11-02/DESIGN.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericCompositionOwner} from '@domainspec-v2/cli/generic';
import {createGenericAuthFixture,prepareGenericFixtureRuntime} from '@domainspec-v2/cli/generic/testing';
import {compileApplicationProfile,createApplicationAccess} from '../index.mjs';
import {serviceFamilyDescriptor} from './marketing.mjs';

const root=fileURLToPath(new URL('../../../../../',import.meta.url));
const library=path.join(root,'craft/projects/domainspec-v2/impl/cli/examples/technical-profile-source');
const example=path.join(library,'marketing-application-example');
const json=file=>JSON.parse(readFileSync(file,'utf8'));

test('marketing recipe preserves distinct original effects and approval only for scheduling',()=>{
 assert.deepEqual(serviceFamilyDescriptor.stages.filter(stage=>stage.kind==='provider').map(stage=>stage.operation),['draft.create','draft.content','campaign.schedule','campaign.metrics']);
 assert.deepEqual(serviceFamilyDescriptor.approvalStages,['schedule']);assert.equal(serviceFamilyDescriptor.stages.at(-1).readCurrent,true);
 const source=readFileSync(path.join(example,'business.alch'),'utf8'),review=source.match(/value-object ReviewRequest:\n([\s\S]*?)(?=\n\S)/)?.[1];assert.ok(review);assert.doesNotMatch(review,/\b(sourceCurrent|releaseAllowed|attempt|now|policyVersion|inputDigest|outputDigest|manifestDigest|expiresAt)\b/);assert.match(source,/enforce DraftEligibility/);assert.match(source,/enforce ScheduleEligibility/);
});

test('original generated protected marketing operation checks all twelve clean business cases',{timeout:600000},async t=>{
 const directory=mkdtempSync(path.join(tmpdir(),'marketing-business-domain-')),builder=createGenericCompositionOwner();let built,owner,handle,auth,runtime;
 t.after(async()=>{await runtime?.close();await auth?.close();if(handle)owner.dispose(handle);if(built)builder.dispose(built);rmSync(directory,{recursive:true,force:true});});
 const profile={schema:'craft.ai-application-profile/v1',id:'marketing-domain-semantics',module:'MarketingOperations',service:'MarketingDomainService',scope:'reference-operations',entryAccess:{sourcePath:path.join(example,'entries.alch'),entry:'MarketingOperationsAccess.PrepareScheduleEntry'},operation:'PrepareSchedule',types:{request:'PreferenceReviewRequest',modelInput:'ModelRequest',proposal:'Proposal',decision:'Decision'},stages:[{name:'proposal',kind:'model',businessOperation:'PrepareDraft',capability_binding:'Marketing.PureDecision',capability_sha256:'1'.repeat(64),deadline_ms:30000}]};
 const compiled=compileApplicationProfile({businessSourcePath:path.join(example,'business.alch'),profile,baseProfile:json(path.join(library,'contracts/marketing-application-base.json')),outputDirectory:path.join(directory,'source')});
 const accept=(o,h,name)=>{const review=o.review(h,name);o.accept(h,{decision_id:name,owner:name,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,name+'.json'));};
 built=await builder.prepare({sourcePath:compiled.sourcePath,profilePath:compiled.profilePath});accept(builder,built,'marketing-generation');const output=path.join(directory,'generated');builder.generate(built,{entry:compiled.selectors.start,outputDirectory:output});
 const module=await import(pathToFileURL(path.join(output,'application.mjs')).href);owner=module.createGeneratedApplicationOwner();handle=await owner.prepare();accept(owner,handle,'marketing-runtime');
 const entries=[compiled.selectors.publicEvaluate,compiled.selectors.stages[0].evaluate];auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),sessionTtlSeconds:7200,subjects:[{id:'customer',evidence:'marketing-evidence',session:'marketing-session'}],grants:entries.map(entry=>({subject:'customer',entry}))});
 ({runtime}=await prepareGenericFixtureRuntime(owner,handle,{service:profile.service,ownedDirectory:path.join(directory,'store'),nativeAuth:auth.nativeAuth}));const access=createApplicationAccess({composition:owner,handle,runtime,profile});
 const cases=json(path.join(example,'fixtures/business-cases.json'));assert.equal(cases.length,12);
 for(const sample of cases){const entry=sample.operation==='PrepareDraft'?compiled.selectors.stages[0].evaluate:compiled.selectors.publicEvaluate,actor=auth.actor(runtime,'customer',entry),result=await access.evaluate(actor,sample.request,entry);assert.equal(result.ok,true,sample.id);assert.equal(result.outcome.kind,sample.expected.kind,sample.id);if(sample.expected.kind==='Rejected')assert.equal(result.outcome.code,sample.expected.code,sample.id);else assert.deepEqual(JSON.parse(JSON.stringify(result.outcome.value)),sample.expected.value,sample.id);}
});
