/** DE03 source/release integration; Auth facade is a local fixture, not Auth/provider qualification.
 * Open Questions: ../../../../goals/plans/craft-domain-execution-separation-2026-11-01/DESIGN.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync,readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericCompositionOwner} from '@domainspec-v2/cli/generic';
import {createGenericAuthFixture,prepareGenericFixtureRuntime} from '@domainspec-v2/cli/generic/testing';
import {compileApplicationProfile} from './compiler.mjs';
import {createApplicationAccess} from './access.mjs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createApplicationSourceGateway} from './gateway.mjs';
import {createSourceReleaseService} from '../source-release/index.mjs';
import {createDocumentAuthority} from '../documents/source-access/index.mjs';
import {canonical,sha256} from '../shared.mjs';
const bytes=value=>new TextEncoder().encode(canonical(value));
async function fixture(t,{envelope=false,recipientRelease=false,profileOverride=null}={}){
 const directory=mkdtempSync(path.join(tmpdir(),'de03-gateway-'));let clock=1700000000000,fault=null;
 const release=createSourceReleaseService({path:path.join(directory,'release.sqlite'),now:()=>clock});
 const documents=createDocumentAuthority({path:path.join(directory,'docs.sqlite'),releaseAuthority:release.authority,now:()=>clock});
 t.after(()=>{documents.close();release.close();rmSync(directory,{recursive:true,force:true});});
 const profile=profileOverride??{id:'clean-domain-fixture',scope:'tenant',stages:[{},{}],executionAdmission:{schema:'craft.application-execution-admission/v1',contract:'crm-contact-enrichment/domain-v1'}};
 const access={profile,assertCurrent(){},async refresh(){},async principal(){return {tenant:'tenant',actor:'operator'};},async job(){return {id:'8',configurationDigest:sha256(canonical(profile))};},async captureInput(){}};
 const put=(role,revision,value)=>documents.authority.put({id:role+'-8',tenant:'tenant',version:revision,aclRevision:'1',readers:['operator','customer'],classifications:['public'],mediaType:'text/plain',bytes:bytes(value)});
 const policy=allowed=>release.authority.setPolicy({id:'review',revision:allowed?'4':'5',tenants:['tenant'],actions:['candidate.review'],sinks:['crm'],recipients:[allowed?'customer':'elsewhere'],classifications:['public']});policy(true);
 put('facts','1',{objectVersion:'3',label:'Business facts',contactAllowed:true});put('approval','1',{approved:true});
 const boundary={authority:release.authority,port:{...release.port,issueRelease(args){const injected=typeof fault==='function'?fault(args):fault;if(injected)throw injected;return release.port.issueRelease(args);}}};
 const gateway=createApplicationSourceGateway({access,documents:documents.port,release:boundary,roles:[{role:'facts',prefix:'facts-',format:'json',disclose:true},{role:'approval',prefix:'approval-',format:'json',disclose:false}],...(recipientRelease?{recipientRelease:{policyId:'review',action:'candidate.review',sink:'crm',recipients:{literal:[{recipient:'customer'}]}}}:{}),policyId:'review',target:{sink:'crm',recipient:'customer',recipientId:'7'},timeUnit:'unix-seconds',now:()=>clock,projections:{modelInput:{subjectId:{from:'id'},prompt:{from:'facts.label'}},review:{objectVersion:{from:'facts.objectVersion'},contactAllowed:{from:'facts.contactAllowed'}},...(envelope?{reviewEnvelope:Object.fromEntries(['subjectId','objectVersion','contactAllowed','approval','proposal'].map(name=>[name,{from:'review.'+name}]))}:{})}});
 const work={id:'8',run:'1',ordinal:'1',attempt:'1'},load=()=>gateway.load('operator',work,{deferCapture:true});
 const proposal={industry:'software',evidenceIds:[]},wire=bytes(proposal),snapshot=await load(),input=gateway.modelInput(snapshot),origin=gateway.captureCandidateOrigin(snapshot,{input,wire,providerId:'original-confirmed-receipt'}),binding=gateway.binding(snapshot);
 put('approval','2',{...binding,policyVersion:'4',outputDigest:sha256(wire),expiresAt:String(Math.floor(clock/1000)+60),approved:true});
 return {gateway,put,load,proposal,wire,origin,input,binding,policy,setFault:value=>fault=value,setClock:value=>clock=value,clock};
}
test('DE03 clean domain excludes owner metadata; private context survives a clean review envelope',async t=>{
 const f=await fixture(t,{envelope:true}),snapshot=await f.load(),review=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin});
 assert.deepEqual(JSON.parse(canonical(review.domain)),{subjectId:'8',objectVersion:'3',contactAllowed:true,approval:{approved:true},proposal:f.proposal});
 assert.equal(review.execution.sourceCurrent,true);assert.equal(review.execution.releaseAllowed,true);assert.equal(review.execution.policyVersion,'4');assert.equal(review.execution.inputDigest,sha256(bytes(f.input)));assert.equal(review.execution.outputDigest,sha256(f.wire));assert.equal(review.approvalDeadlineMs,(Math.floor(f.clock/1000)+60)*1000);
 assert.equal(review.execution.candidateOrigin.inputDigest,review.execution.inputDigest);assert.equal(review.execution.candidateOrigin.manifestDigest,review.execution.manifestDigest);
 assert.equal(Object.hasOwn(review.execution.approval,'approved'),false);assert.equal(Object.hasOwn(review.domain,'sourceCurrent'),false);
 const original=JSON.parse(f.origin);assert.throws(()=>f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:canonical({...original,profileDigest:'0'.repeat(64)})}),{code:'ForeignOwner'});
 assert.throws(()=>f.gateway.captureCandidateOrigin(snapshot,{wire:f.wire,providerId:'copied-receipt',input:{...f.input,prompt:'different'}}),{code:'ForeignOwner'});
});
test('DE03 saved candidate origin is not relabeled by newer source, changed wire, denied release or clock',async t=>{
 const f=await fixture(t),origin=JSON.parse(f.origin);f.put('facts','2',{objectVersion:'4',label:'Updated facts',contactAllowed:true});const snapshot=await f.load();
 let review=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin});
 assert.equal(review.execution.sourceVersion,'2');assert.equal(review.execution.candidateOrigin.sourceVersion,'1');assert.equal(review.execution.candidateOrigin.manifestDigest,origin.manifestDigest);assert.notEqual(review.execution.inputDigest,review.execution.candidateOrigin.inputDigest);
 const different=bytes({...f.proposal,industry:'manufacturing'});review=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:different,candidateOrigin:f.origin});assert.notEqual(review.execution.outputDigest,review.execution.candidateOrigin.outputDigest);
 f.policy(false);review=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin});assert.equal(review.execution.sourceCurrent,true);assert.equal(review.execution.releaseAllowed,false);const observations=f.gateway.inspectExecutionObservations(review.execution);assert.equal(observations.length,1);assert.equal(observations[0].phase,'candidate-disclosure');assert.equal(observations[0].error.message,'DISCLOSURE_DENIED');assert.equal(JSON.stringify(review).includes('candidate-disclosure'),false);assert.throws(()=>f.gateway.inspectExecutionObservations({...review.execution}),{code:'ForeignOwner'});
 f.setClock(f.clock+120000);review=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin});assert.ok(BigInt(review.execution.now)>BigInt(review.execution.approval.expiresAt));
});

test('DE03 unknown SOURCE-looking owner faults propagate; recognized source changes retain private original cause',async t=>{
 const f=await fixture(t),snapshot=await f.load(),fault=new Error('SOURCE_UNRECOGNIZED_ENGINE_FAULT');f.setFault(fault);
 assert.throws(()=>f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin}),error=>error===fault);
 f.setFault(null);f.put('facts','2',{objectVersion:'4',label:'changed after admission',contactAllowed:true});
 const review=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin});assert.equal(review.execution.sourceCurrent,false);assert.equal(review.execution.releaseAllowed,false);
 const observations=f.gateway.inspectExecutionObservations(review.execution);assert.equal(observations[0].phase,'source-currentness');assert.equal(observations[0].error.code,'StaleOwner');
});

test('DE03 additional recipient denial joins private technical release observation without swallowing unknown faults',async t=>{
 const f=await fixture(t,{recipientRelease:true}),snapshot=await f.load();f.setFault(request=>request.attemptId.startsWith('recipient-')?new Error('DISCLOSURE_DENIED'):null);
 const review=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin});assert.equal(review.execution.releaseAllowed,false);assert.equal(review.execution.sourceCurrent,true);assert.equal(f.gateway.inspectExecutionObservations(review.execution)[0].phase,'recipient-disclosure');
 const fault=new Error('SOURCE_UNKNOWN_RECIPIENT_ENGINE');f.setFault(request=>request.attemptId.startsWith('recipient-')?fault:null);assert.throws(()=>f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin}),error=>error===fault);
});

// This joins actual protected kernel/business execution with original source and
// release owners. Job/principal formation and the final connector are explicit
// fixture host surfaces; the full generated test owns actual workflow dispatch.
test('DE03 original protected re-admission rejects expiry after genuine business evaluation',{timeout:300000},async t=>{
 const directory=mkdtempSync(path.join(tmpdir(),'de03-readmission-'));let build,built,owner,handle,auth,runtime;
 t.after(async()=>{await runtime?.close();await auth?.close();if(handle)owner.dispose(handle);if(built)build.dispose(built);rmSync(directory,{recursive:true,force:true});});
 const source=`module GatewayGuard version 1
value-object Approval:
  approved Bool
value-object Proposal:
  industry String
  evidenceIds List<UInt64,8>
value-object ModelRequest:
  subjectId UInt64
  prompt String
value-object ReviewRequest:
  subjectId UInt64
  objectVersion UInt64
  contactAllowed Bool
  approval Approval
  proposal Proposal
value-object Decision:
  accepted Bool
mapping Accept:
  input request ReviewRequest
  target Decision
  total true
  field accepted <- request.contactAllowed
operation Decide:
  input request ReviewRequest
  output Decision
  on not request.contactAllowed reject domain-denied
  return Accept(request)
entry GatewayGuard.DecideEntry:
  invokes GatewayGuard.Decide
  interaction request-response
  access:
    authenticated customer
    permission example.decide
    auth-resource example
    auth-action decide
    auth-scope tenant
`;
 const business=path.join(directory,'business.alch');writeFileSync(business,source);
 const profile={schema:'craft.ai-application-profile/v1',id:'clean-domain-fixture',module:'GatewayGuard',service:'GuardService',scope:'tenant',operation:'Decide',entryAccess:{sourcePath:business,entry:'GatewayGuard.DecideEntry'},types:{request:'ReviewRequest',modelInput:'ModelRequest',proposal:'Proposal',decision:'Decision'},stages:[{name:'fixture',kind:'model',capability_binding:'Guard.Fixture',capability_sha256:'a'.repeat(64),deadline_ms:1000}],executionAdmission:{schema:'craft.application-execution-admission/v1',contract:'crm-contact-enrichment/domain-v1'},errorPresentation:{schema_version:'craft.error-presentation-table/v1',producer:'GatewayGuard.Decide',reason_type:'GatewayGuard.BusinessReason',presentation_version:'a'.repeat(64),rows:[{internalCode:'domain-denied',publicCode:'domain-denied',message:'Business conditions are not met.',category:'Forbidden',httpStatus:403}]}};
 const root=fileURLToPath(new URL('../../../../',import.meta.url)),baseProfile=JSON.parse(readFileSync(path.join(root,'implementation/craft-ai-reference-apps/crm/contracts/eligibility-profile.json')));
 const compiled=compileApplicationProfile({businessSourcePath:business,profile,baseProfile,outputDirectory:path.join(directory,'source')});
 const accept=(o,h,id)=>{const review=o.review(h,id);o.accept(h,{decision_id:id,owner:id,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,id+'.json'));};
 build=createGenericCompositionOwner();built=await build.prepare({sourcePath:compiled.sourcePath,profilePath:compiled.profilePath});accept(build,built,'de03-generate');const generated=path.join(directory,'generated');build.generate(built,{entry:compiled.selectors.start,outputDirectory:generated});
 const module=await import(pathToFileURL(path.join(generated,'application.mjs')).href);owner=module.createGeneratedApplicationOwner();handle=await owner.prepare();accept(owner,handle,'de03-runtime');const selectors=compiled.selectors;
 auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),subjects:[{id:'operator',evidence:'operator-evidence',session:'operator-session'}],grants:[selectors.executionAdmission,selectors.evaluate].map(entry=>({subject:'operator',entry}))});const prepared=await prepareGenericFixtureRuntime(owner,handle,{service:profile.service,ownedDirectory:path.join(directory,'store'),nativeAuth:auth.nativeAuth});runtime=prepared.runtime;
 const access=createApplicationAccess({composition:owner,handle,runtime,profile}),actor=entry=>auth.actor(runtime,'operator',entry),f=await fixture(t,{profileOverride:access.profile}),snapshot=await f.load();let sends=0,businessCalls=0;
 const initial=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin});let result=await access.admitExecution(actor(selectors.executionAdmission),initial.execution);assert.equal(result.outcome.kind,'Returned');assert.equal(result.outcome.value,true);
 result=await access.evaluate(actor(selectors.evaluate),initial.domain);businessCalls++;assert.equal(result.outcome.kind,'Returned');assert.equal(result.outcome.value.accepted,true);
 f.setClock(f.clock+120000);const final=f.gateway.executionReview(snapshot,{proposal:f.proposal,wire:f.wire,candidateOrigin:f.origin});result=await access.admitExecution(actor(selectors.executionAdmission),final.execution);if(result.outcome.kind==='Returned')sends++;
 assert.equal(result.outcome.kind,'Rejected');assert.equal(result.outcome.code,'approval-stale');assert.equal(access.diagnostic(result).producer,'GatewayGuard.ProfileAdmitExecution');assert.equal(businessCalls,1);assert.equal(sends,0);assert.ok(final.approvalDeadlineMs<Number(final.execution.now)*1000);
});
