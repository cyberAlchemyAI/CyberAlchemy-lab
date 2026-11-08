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
import {serviceFamilyDescriptor} from './invoice.mjs';

const root=fileURLToPath(new URL('../../../../../',import.meta.url));
const library=path.join(root,'craft/projects/domainspec-v2/impl/cli/examples/technical-profile-source');
const example=path.join(library,'invoice-application-example');
const json=file=>JSON.parse(readFileSync(file,'utf8'));

test('invoice recipe reuses the original parser/model and Xero DRAFT owners',()=>{
 assert.deepEqual(serviceFamilyDescriptor.stages.map(s=>s.kind),['model','provider']);
 assert.equal(serviceFamilyDescriptor.stages[1].operation,'bill.draft');
 assert.deepEqual(serviceFamilyDescriptor.approvalStages,['draftPosting']);
 const source=readFileSync(path.join(example,'business.alch'),'utf8');
 assert.doesNotMatch(source,/\b(sourceCurrent|releaseAllowed|attempt|now|inputDigest|outputDigest|manifestDigest|destinationAllowed|idempotencyExpiresAt)\b/);
 assert.match(source,/enforce ReconciliationEligibility/);assert.match(source,/enforce InvoiceEligibility/);
});

test('original generated protected invoice operation checks all fifteen clean business cases',{timeout:600000},async t=>{
 const directory=mkdtempSync(path.join(tmpdir(),'invoice-business-domain-')),builder=createGenericCompositionOwner();let built,owner,handle,auth,runtime;
 t.after(async()=>{await runtime?.close();await auth?.close();if(handle)owner.dispose(handle);if(built)builder.dispose(built);rmSync(directory,{recursive:true,force:true});});
 const profile={schema:'craft.ai-application-profile/v1',id:'invoice-domain-semantics',module:'InvoiceOperations',service:'InvoiceDomainService',scope:'local-invoice',businessInputContract:'invoice-draft/domain-v1',sourceSelection:json(path.join(library,'contracts/invoice-application-sources.json')),entryAccess:{sourcePath:path.join(example,'entries.alch'),entry:'InvoiceOperationsAccess.PrepareDraftPostingEntry'},operation:'PrepareDraftPosting',types:{request:'ReconciliationRequest',modelInput:'ModelRequest',proposal:'PostingProposal',decision:'Decision'},stages:[{name:'review',kind:'document',capability_binding:'Invoice.PureDecision',capability_sha256:'1'.repeat(64),deadline_ms:30000}]};
 const compiled=compileApplicationProfile({businessSourcePath:path.join(example,'business.alch'),profile,baseProfile:json(path.join(library,'contracts/invoice-application-base.json')),outputDirectory:path.join(directory,'source')});
 const accept=(o,h,name)=>{const review=o.review(h,name);o.accept(h,{decision_id:name,owner:name,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,name+'.json'));};
 built=await builder.prepare({sourcePath:compiled.sourcePath,profilePath:compiled.profilePath});accept(builder,built,'invoice-generation');const output=path.join(directory,'generated');builder.generate(built,{entry:compiled.selectors.start,outputDirectory:output});
 const module=await import(pathToFileURL(path.join(output,'application.mjs')).href);owner=module.createGeneratedApplicationOwner();handle=await owner.prepare();accept(owner,handle,'invoice-runtime');
 const entries=[compiled.selectors.publicEvaluate,compiled.selectors.effectEvaluate,compiled.selectors.executionAdmission];auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),sessionTtlSeconds:7200,subjects:[{id:'customer',evidence:'support-evidence',session:'support-session'}],grants:entries.map(entry=>({subject:'customer',entry}))});
 ({runtime}=await prepareGenericFixtureRuntime(owner,handle,{service:profile.service,ownedDirectory:path.join(directory,'store'),nativeAuth:auth.nativeAuth}));const access=createApplicationAccess({composition:owner,handle,runtime,profile});
 const cases=json(path.join(example,'fixtures/business-cases.json'));assert.equal(cases.length,15);
 for(const sample of cases){const entry=compiled.selectors.publicEvaluate,actor=auth.actor(runtime,'customer',entry),result=await access.evaluate(actor,sample.request,entry);
  assert.equal(result.ok,true,sample.id);assert.equal(result.outcome.kind,sample.expected.kind,sample.id);
  if(sample.expected.kind==='Rejected')assert.equal(result.outcome.code,sample.expected.code,sample.id);
  else assert.deepEqual(JSON.parse(JSON.stringify(result.outcome.value)),sample.expected.value,sample.id);
 }
 // The same service source emits the original technical Alch kernel and Entry;
 // no CRM executionAdmission contract or copied business predicates are needed.
 const digest='a'.repeat(64),origin={subjectId:'1',objectVersion:'1',sourceVersion:'1',inputDigest:digest,outputDigest:digest,manifestDigest:digest,providerId:'actual-original-paid-receipt'},approval={...origin,policyVersion:'1',recipientId:'5',expiresAt:'200'};delete approval.providerId;
 const execution={sourceCurrent:true,releaseAllowed:true,subjectId:'1',objectVersion:'1',sourceVersion:'1',policyVersion:'1',recipientId:'5',now:'100',inputDigest:digest,outputDigest:digest,manifestDigest:digest,candidateOrigin:origin,approval};
 const actor=auth.actor(runtime,'customer',compiled.selectors.executionAdmission);
 const accepted=await access.admitExecution(actor,execution);assert.equal(accepted.outcome.kind,'Returned');assert.equal(accepted.outcome.value,true);
 for(const [code,patch]of [['source-stale',{sourceCurrent:false}],['disclosure-denied',{releaseAllowed:false}],['candidate-stale',{candidateOrigin:{...origin,outputDigest:'b'.repeat(64)}}],['approval-stale',{approval:{...approval,expiresAt:'100'}}]]){
  const denied=await access.admitExecution(actor,{...execution,...patch});assert.equal(denied.outcome.kind,'Rejected');assert.equal(denied.outcome.code,code);
 }

});
