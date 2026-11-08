/** Original protected Entry integration; synthetic finite inputs, no provider qualification.
 * Open Questions: goals/plans/craft-domain-execution-separation-2026-11-01/DESIGN.md#open-questions. */
import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';import path from 'node:path';import {tmpdir} from 'node:os';import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericCompositionOwner} from '@domainspec-v2/cli/generic';
import {createGenericAuthFixture,prepareGenericFixtureRuntime} from '@domainspec-v2/cli/generic/testing';
import {compileApplicationProfile,validateApplicationProfile,applicationSelectors} from './compiler.mjs';
import {createApplicationAccess} from './access.mjs';
const root=fileURLToPath(new URL('../../../../',import.meta.url));
const source=`module GuardBusiness version 1
value-object Message:
  carrier String
  utf8-bytes 1..100
  unicode-scalars 1..100
value-object ReviewRequest:
  allowed Bool
value-object ModelRequest:
  prompt Message
value-object Proposal:
  industry Message
value-object Decision:
  ready Bool
mapping ToDecision:
  input request ReviewRequest
  target Decision
  total true
  field ready <- request.allowed
operation Decide:
  input request ReviewRequest
  output Decision
  on not request.allowed reject domain-denied
  return ToDecision(request)
operation DoNotReviewTechnical:
  input request ReviewRequest
  output ReviewRequest
  requires false on-false reject unexpected-review
  return request
entry GuardBusiness.DecideEntry:
  invokes GuardBusiness.Decide
  interaction request-response
  access:
    authenticated customer
    permission example.decide
    auth-resource example
    auth-action decide
    auth-scope guard-example
`;
const context=()=>{const binding={subjectId:'1',objectVersion:'2',sourceVersion:'3',inputDigest:'a'.repeat(64),outputDigest:'b'.repeat(64),manifestDigest:'c'.repeat(64)};return {...binding,sourceCurrent:true,releaseAllowed:true,policyVersion:'4',recipientId:'5',now:'100',candidateOrigin:{...binding,providerId:'original-receipt'},approval:{...binding,policyVersion:'4',recipientId:'5',expiresAt:'101'}};};
const table={schema_version:'craft.error-presentation-table/v1',producer:'GuardBusiness.Decide',reason_type:'GuardBusiness.BusinessReason',presentation_version:'a'.repeat(64),rows:[{internalCode:'domain-denied',publicCode:'domain-denied',message:'Business conditions are not met.',category:'Forbidden',httpStatus:403}]};
const accept=(owner,handle,dir,id)=>{const review=owner.review(handle,id);owner.accept(handle,{decision_id:id,owner:id,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,id+'.json'));};
test('original generated admission Entry bypasses business review and retains genuine protected diagnostic producer',{timeout:300000},async()=>{
 const directory=mkdtempSync(path.join(tmpdir(),'craft-protected-admission-'));let build,built,owner,handle,auth,runtime;
 try{const business=path.join(directory,'business.alch');writeFileSync(business,source);const raw={schema:'craft.ai-application-profile/v1',id:'guard-profile',module:'GuardBusiness',service:'GuardService',scope:'guard-example',operation:'Decide',reviewOperation:'DoNotReviewTechnical',entryAccess:{sourcePath:business,entry:'GuardBusiness.DecideEntry'},types:{request:'ReviewRequest',modelInput:'ModelRequest',proposal:'Proposal',decision:'Decision'},stages:[{name:'fixture',kind:'model',capability_binding:'Guard.Fixture',capability_sha256:'a'.repeat(64),deadline_ms:1000}],executionAdmission:{schema:'craft.application-execution-admission/v1',contract:'crm-contact-enrichment/domain-v1'},errorPresentation:table};
 const missing={...raw};delete missing.errorPresentation;assert.throws(()=>validateApplicationProfile(missing),/typed error presentation/);const profile=validateApplicationProfile(raw);assert.equal(profile.errorPresentation.tables.length,2);assert.equal(validateApplicationProfile(profile).errorPresentation.tables.length,2);assert.equal(profile.operation,'Decide');const bad=structuredClone(profile);bad.errorPresentation.tables[1].rows[0].publicCode='changed';assert.throws(()=>validateApplicationProfile(bad));const legacy={...raw};delete legacy.executionAdmission;assert.equal(applicationSelectors(legacy).executionAdmission,null);
 const compiled=compileApplicationProfile({businessSourcePath:business,profile,baseProfile:JSON.parse(readFileSync(path.join(root,'implementation/craft-ai-reference-apps/crm/contracts/eligibility-profile.json'))),outputDirectory:path.join(directory,'source')});assert.equal(readFileSync(compiled.sourcePath,'utf8').slice(0,source.length),source);assert.match(compiled.origins.executionAdmissionKernel.sha256,/^[a-f0-9]{64}$/);build=createGenericCompositionOwner();built=await build.prepare({sourcePath:compiled.sourcePath,profilePath:compiled.profilePath});accept(build,built,directory,'accept-generation');const generated=path.join(directory,'generated');build.generate(built,{entry:compiled.selectors.start,outputDirectory:generated});const {createGeneratedApplicationOwner}=await import(pathToFileURL(path.join(generated,'application.mjs')).href);owner=createGeneratedApplicationOwner();handle=await owner.prepare();accept(owner,handle,directory,'accept-runtime');const selectors=compiled.selectors;
 auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),subjects:[{id:'operator',evidence:'operator-evidence',session:'operator-session'}],grants:[selectors.executionAdmission,selectors.review,selectors.evaluate].map(entry=>({subject:'operator',entry}))});const fixture=await prepareGenericFixtureRuntime(owner,handle,{service:profile.service,ownedDirectory:path.join(directory,'store'),nativeAuth:auth.nativeAuth});runtime=fixture.runtime;const access=createApplicationAccess({composition:owner,handle,runtime,profile}),actor=entry=>auth.actor(runtime,'operator',entry);
 let result=await access.admitExecution(actor(selectors.executionAdmission),context());assert.equal(result.ok,true);assert.equal(result.outcome.kind,'Returned');assert.equal(result.outcome.value,true);const denied=context();denied.sourceCurrent=false;result=await access.admitExecution(actor(selectors.executionAdmission),denied);assert.equal(result.outcome.kind,'Rejected');assert.equal(result.outcome.code,'source-stale');const diagnostic=access.diagnostic(result);assert.equal(diagnostic.producer,'GuardBusiness.ProfileAdmitExecution');assert.throws(()=>access.diagnostic({...result}),/actual original invocation result/);const reviewed=await access.evaluate(actor(selectors.evaluate),{allowed:true});assert.equal(reviewed.outcome.kind,'Rejected');assert.equal(reviewed.outcome.code,'unexpected-review');assert.equal(access.diagnostic(reviewed).producer,'GuardBusiness.DoNotReviewTechnical');auth.setPermission('operator',selectors.executionAdmission,false);await assert.rejects(access.admitExecution(actor(selectors.executionAdmission),context()),/PermissionDenied|permission|denied/i);
 }finally{await runtime?.close();await auth?.close();if(handle)owner.dispose(handle);if(built)build.dispose(built);rmSync(directory,{recursive:true,force:true});}
});
