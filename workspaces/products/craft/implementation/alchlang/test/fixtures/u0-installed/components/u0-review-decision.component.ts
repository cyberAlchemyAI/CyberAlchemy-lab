// H01 installed adaptation of craft/projects/domainspec-v2/impl/cli/test/u0-review-decision.test.ts.
// All positive producers are actual packaged dist modules; negative-only custody stubs retain component scope.
// Open Questions: ../README.md and H01 CONTEXT. No original task file changed.
import test,{type TestContext} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,mkdirSync,writeFileSync,rmSync,statSync,renameSync,unlinkSync,symlinkSync,chmodSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
const installedCore=path.join(process.env.U0_INSTALLED_CONSUMER!,'node_modules/@domainspec-v2/cli');
const {createSourceBusinessReviewOwnerV2,createBusinessReviewSubjectOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-review.js')).href);
const {createSourceBusinessDecisionOwnerV2,createBusinessReviewOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-decision.js')).href);
const {createBusinessCoreRecipeOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-recipes.js')).href);
const {projectDirectExecutableV2,projectOptionalAssuranceV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-identity-v2.js')).href);
const {sha256,dataDigest}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/contracts.js')).href);
// Real source/file custody only. No successful fake native/selection/application
// handle is used. Actual selected production witness is explicitly K02.
// Open Questions: J01/J02/K02 and L02/G01/native/installed qualification.
const fixtures=new URL('../',import.meta.url);
const original=readFileSync(new URL('business.alch',fixtures),'utf8');
const base=JSON.parse(readFileSync(new URL('spec.json',fixtures),'utf8'));
const vectors=JSON.parse(readFileSync(new URL('identity-vectors.json',fixtures),'utf8')).vectors;
const clone=<T>(v:T):T=>JSON.parse(JSON.stringify(v));
function transfer(text=original,spec:any=clone(base)){
 const hash=sha256(text),rows=text.split('\n').map((raw,i,list)=>({raw:i<list.length-1?raw.replace(/\r$/,''):raw,line:i+1})).filter(row=>row.raw.trim()&&!row.raw.trimStart().startsWith('#'));
 spec.source_spans=rows.map(row=>({selector:'line:'+row.line,source:'business.alch',line:row.line,column:row.raw.length-row.raw.trimStart().length+1,text:row.raw,source_sha256:hash}));
 spec.obligations=rows.map(row=>({selector:'line:'+row.line,kind:'clause',span_selector:'line:'+row.line}));
 return {source:{path:'business.alch',text,sha256:hash,bytes:Buffer.byteLength(text)},spec,executable:projectDirectExecutableV2(spec),assurance:projectOptionalAssuranceV2(spec)};
}
const optional=`
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
function fixture(t:TestContext,text=original,spec:any=clone(base)){
 const root=mkdtempSync(path.join(os.tmpdir(),'craft-k01-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 const source=path.join(root,'source','business.alch'),decisions=path.join(root,'decisions');mkdirSync(path.dirname(source));mkdirSync(decisions);writeFileSync(source,text);
 const owner=createSourceBusinessReviewOwnerV2(),review=owner.prepare(source,transfer(text,spec)),decisionOwner=createSourceBusinessDecisionOwnerV2(owner);
 const request={decision_id:'FixtureAccepted',owner:review.subject.owner,outcome:'accepted',reviewed_digest:review.review_sha256};
 return {root,source,decisions,owner,review,decisionOwner,request,file:(name='accepted.json')=>path.join(decisions,name)};
}
test('K01 independently reconstructed zero-claim source review matches fixed C02 subject',t=>{
 const f=fixture(t);assert.equal(f.review.review_sha256,'6deae9b3ac1b4e64da16f8bb6e8825791ff21dbc5e7f166ad4b82e1b0658fa39');
 assert.equal(f.review.review_sha256,vectors[0].expected.review_sha256);assert.equal(f.review.subject.assurance.claims.length,0);assert.equal(Object.hasOwn(f.review,'selection'),false);assert.equal(Object.hasOwn(f.review,'accepted'),false);assert.ok(Object.isFrozen(f.review));
 const rendered=f.owner.render(f.review);for(const expected of ['Condition: item.verified is true','Guard CanProcess','Result: request','Effects: none','permission public','Optional assurance: 0 claims','Source-only review; no native selection','business.alch'])assert.ok(rendered.includes(expected),expected);
 assert.equal(f.review.source_capture.source.sha256,sha256(original));assert.equal(f.review.authority_effect,'none');
});
test('K01 optional FOL assurance is inspected but never required for execution or acceptance',t=>{
 const f=fixture(t,original+optional,clone(vectors[1].spec));assert.equal(f.review.subject.assurance.claims.length,1);assert.equal(f.review.subject.executable_sha256,vectors[0].expected.executable_sha256);
 assert.equal(f.review.review_sha256,vectors[1].expected.review_sha256);const rendered=f.owner.render(f.review);assert.match(rendered,/Proposition: Eligible\(current\)/);assert.match(rendered,/Subjects: CanProcess, Process/);
 const decision=f.decisionOwner.recordDecision(f.review,f.request,f.file());assert.equal(f.decisionOwner.requireAccepted(f.review,decision).authority_effect,'none');
});
test('K01 genuine explicit fixture decisions retain original source/review and physical file identity',t=>{
 const f=fixture(t);const decision=f.decisionOwner.recordDecision(f.review,f.request,f.file()),stat=statSync(f.file(),{bigint:true});
 assert.equal(decision.kind,'captured-source-business-decision-v2');assert.equal(decision.review,f.review);assert.equal(decision.file.device,String(stat.dev));assert.equal(decision.file.inode,String(stat.ino));assert.equal(decision.file.mtime_ns,String(stat.mtimeNs));assert.equal(decision.file.sha256,sha256(readFileSync(f.file())));assert.equal(decision.file.bytes,Number(stat.size));
 assert.equal(decision.decision.capture_sha256,f.review.source_capture.capture_sha256);assert.equal(decision.decision.subject.sha256,f.review.review_sha256);
 const accepted=f.decisionOwner.requireAccepted(f.review,decision);assert.equal(accepted.review,f.review);assert.equal(accepted.decision,decision);assert.equal(accepted.kind,'accepted-source-business-review-v2');f.decisionOwner.assertAcceptedCurrent(accepted);
 const captured=f.decisionOwner.captureDecision(f.review,f.file());assert.notEqual(captured,decision);assert.equal(captured.file.sha256,decision.file.sha256);
});
test('K01 decline stays recorded and never produces accepted scope',t=>{
 const f=fixture(t),decision=f.decisionOwner.recordDecision(f.review,{...f.request,outcome:'declined'},f.file());assert.equal(decision.decision.outcome,'declined');f.decisionOwner.assertDecisionCurrent(decision);
 assert.throws(()=>f.decisionOwner.requireAccepted(f.review,decision),/BUSINESS_DECISION_DECLINED/);
});
test('K01 exact recorded request and file cannot be silently overwritten, even by identical repeats',t=>{
 const f=fixture(t);const oldUmask=process.umask(0o777);try{f.decisionOwner.recordDecision(f.review,f.request,f.file());}finally{process.umask(oldUmask);}
 assert.equal(Number(statSync(f.file()).mode)&0o777,0o600);const old=readFileSync(f.file());
 assert.throws(()=>f.decisionOwner.recordDecision(f.review,f.request,f.file()),/DESTINATION_OCCUPIED/);assert.deepEqual(readFileSync(f.file()),old);
 mkdirSync(f.file('directory'));assert.throws(()=>f.decisionOwner.recordDecision(f.review,f.request,f.file('directory')),/DESTINATION_OCCUPIED/);
});
test('K01 wrong owner, subject, capture, executable, assurance or accepted flag reject',t=>{
 const f=fixture(t),decision=f.decisionOwner.recordDecision(f.review,f.request,f.file());
 const mutators=[(v:any)=>{v.owner='other';},(v:any)=>{v.subject.sha256='0'.repeat(64);},(v:any)=>{v.subject.canonicalization='old';},(v:any)=>{v.capture_sha256='0'.repeat(64);},(v:any)=>{v.executable_sha256='0'.repeat(64);},(v:any)=>{v.assurance_sha256='0'.repeat(64);},(v:any)=>{v.accepted=true;}];
 for(const [i,mutate]of mutators.entries()){const raw=clone(decision.decision);mutate(raw);const file=f.file('bad-'+i+'.json');writeFileSync(file,JSON.stringify(raw));assert.throws(()=>f.decisionOwner.captureDecision(f.review,file));}
 for(const request of [{...f.request,owner:'other'},{...f.request,reviewed_digest:'0'.repeat(64)},{...f.request,outcome:'yes'},{...f.request,decision_id:'not a closed id'},{...f.request,accepted:true}])assert.throws(()=>f.decisionOwner.recordDecision(f.review,request as any,f.file('invalid.json')));
 assert.equal(readFileSync(f.file()).includes(Buffer.from('FixtureAccepted')),true);
});
test('K01 decision JSON preserves duplicate-member rejection including escaped names',t=>{
 const f=fixture(t),decision=f.decisionOwner.recordDecision(f.review,f.request,f.file());const text=JSON.stringify(decision.decision);
 for(const [i,duplicate]of [text.replace('"owner":"dispatch-team"','"owner":"wrong","owner":"dispatch-team"'),text.replace('"owner":"dispatch-team"','"owner":"wrong","\\u006fwner":"dispatch-team"'),text.replace('"algorithm":"sha256"','"algorithm":"wrong","algorithm":"sha256"')].entries()){
  const file=f.file('duplicate-'+i+'.json');writeFileSync(file,duplicate);assert.throws(()=>f.decisionOwner.captureDecision(f.review,file),/BUSINESS_DECISION_FILE_JSON/);
 }
});
test('K01 cloned/proxied/wrong-owner review, decision and accepted handles reject',t=>{
 const f=fixture(t),decision=f.decisionOwner.recordDecision(f.review,f.request,f.file()),accepted=f.decisionOwner.requireAccepted(f.review,decision);
 const other=createSourceBusinessReviewOwnerV2(),otherDecision=createSourceBusinessDecisionOwnerV2(other);
 for(const review of [clone(f.review),{...f.review},new Proxy(f.review,{})])assert.throws(()=>f.owner.assertCurrent(review),/HANDLE/);
 assert.throws(()=>other.assertCurrent(f.review),/HANDLE/);assert.throws(()=>otherDecision.assertDecisionCurrent(decision));
 for(const value of [clone(decision),{...decision},new Proxy(decision,{})])assert.throws(()=>f.decisionOwner.assertDecisionCurrent(value),/UNREGISTERED/);
 for(const value of [clone(accepted),{...accepted},new Proxy(accepted,{})])assert.throws(()=>f.decisionOwner.assertAcceptedCurrent(value),/UNREGISTERED/);
 assert.throws(()=>createSourceBusinessDecisionOwnerV2({...f.owner}),/BUSINESS_REVIEW_OWNER/);
});
test('K01 equal review data still needs explicit decision recapture for a different original handle',t=>{
 const f=fixture(t),a=f.decisionOwner.recordDecision(f.review,f.request,f.file()),next=f.owner.prepare(f.source,transfer());
 assert.equal(next.review_sha256,f.review.review_sha256);assert.equal(next.source_capture.capture_sha256,f.review.source_capture.capture_sha256);
 assert.throws(()=>f.decisionOwner.requireAccepted(next,a),/FOREIGN_REVIEW/);const recaptured=f.decisionOwner.captureDecision(next,f.file());assert.equal(f.decisionOwner.requireAccepted(next,recaptured).review,next);
});
test('K01 decision rewrites, identical inode replacement and mode changes retire old handles',t=>{
 const f=fixture(t);for(const mode of ['rewrite','replace','permissions']){
  const file=f.file(mode+'.json'),decision=f.decisionOwner.recordDecision(f.review,f.request,file),accepted=f.decisionOwner.requireAccepted(f.review,decision),data=readFileSync(file);
  if(mode==='rewrite')writeFileSync(file,data);else if(mode==='replace'){renameSync(file,file+'.before');writeFileSync(file,data);}else chmodSync(file,0o640);
  assert.throws(()=>f.decisionOwner.assertDecisionCurrent(decision),/STALE/);assert.throws(()=>f.decisionOwner.assertAcceptedCurrent(accepted),/STALE/);
 }
});
test('K01 decision symlink and parent replacement do not transfer original file custody',t=>{
 const f=fixture(t),decision=f.decisionOwner.recordDecision(f.review,f.request,f.file());const fileData=readFileSync(f.file());
 renameSync(f.file(),f.file('original.json'));symlinkSync(f.file('original.json'),f.file());assert.throws(()=>f.decisionOwner.assertDecisionCurrent(decision),/STALE/);assert.throws(()=>f.decisionOwner.captureDecision(f.review,f.file()),/SYMLINK/);
 unlinkSync(f.file());renameSync(f.decisions,f.decisions+'-old');mkdirSync(f.decisions);writeFileSync(f.file(),fileData);assert.throws(()=>f.decisionOwner.assertDecisionCurrent(decision),/STALE/);f.owner.assertCurrent(f.review);
});
test('K01 original physical source is required and source replacement/disposal retires acceptance',t=>{
 const f=fixture(t),decision=f.decisionOwner.recordDecision(f.review,f.request,f.file()),accepted=f.decisionOwner.requireAccepted(f.review,decision);
 const bad=transfer(original.replace('  condition item.verified','  condition item.id'));assert.throws(()=>f.owner.prepare(f.source,bad));
 renameSync(f.source,f.source+'.before');writeFileSync(f.source,original);assert.throws(()=>f.owner.assertCurrent(f.review),/SOURCE_STALE/);assert.throws(()=>f.decisionOwner.assertAcceptedCurrent(accepted));
 const fresh=f.owner.prepare(f.source,transfer());f.owner.dispose(fresh);assert.throws(()=>f.owner.assertCurrent(fresh),/DISPOSED/);
});
test('K01 source/comment recapture preserves business digest but cannot reuse old decision capture',t=>{
 const f=fixture(t),decision=f.decisionOwner.recordDecision(f.review,f.request,f.file());const text=original+'\n# capture-only edit\n';writeFileSync(f.source,text);
 const review=f.owner.prepare(f.source,transfer(text));assert.equal(review.review_sha256,f.review.review_sha256);assert.notEqual(review.source_capture.capture_sha256,f.review.source_capture.capture_sha256);
 assert.throws(()=>f.decisionOwner.captureDecision(review,f.file()),/REVIEW_MISMATCH/);assert.throws(()=>f.decisionOwner.assertDecisionCurrent(decision));
});
test('K01 explanation and optional assurance changes alter reviewed scope without rewriting execution',t=>{
 const f=fixture(t),changed=original.replace('Require the supplied verified flag.','Inspect this supplied flag.');const spec=clone(base);spec.rules[0].meaning='Inspect this supplied flag.';writeFileSync(f.source,changed);
 const review=f.owner.prepare(f.source,transfer(changed,spec));assert.equal(review.subject.executable_sha256,f.review.subject.executable_sha256);assert.notEqual(review.review_sha256,f.review.review_sha256);
 const optionalSpec=clone(vectors[1].spec);writeFileSync(f.source,original+optional);const assurance=f.owner.prepare(f.source,transfer(original+optional,optionalSpec));assert.equal(assurance.subject.executable_sha256,f.review.subject.executable_sha256);assert.notEqual(assurance.subject.assurance_sha256,f.review.subject.assurance_sha256);
});
test('K01 accessors, proxies, nonregular source/decision and symlink source reject',t=>{
 const f=fixture(t);let calls=0;assert.throws(()=>f.decisionOwner.recordDecision(f.review,{...f.request,get outcome(){calls++;return 'accepted' as const;}},f.file()));assert.equal(calls,0);
 assert.throws(()=>f.owner.prepare(f.source,new Proxy(transfer(),{})));assert.throws(()=>f.decisionOwner.captureDecision(f.review,f.decisions));
 const link=path.join(path.dirname(f.source),'alias.alch');symlinkSync(f.source,link);assert.throws(()=>f.owner.prepare(link,transfer()),/SYMLINK/);
 const wrongSource=path.join(path.dirname(f.source),'wrong.alch');writeFileSync(wrongSource,original+'\n');assert.throws(()=>f.owner.prepare(wrongSource,transfer()),/CORRESPONDENCE/);
});
test('K01 source-only fixture acceptance never satisfies a genuine selected review owner',t=>{
 const f=fixture(t),decision=f.decisionOwner.recordDecision(f.review,f.request,f.file()),accepted=f.decisionOwner.requireAccepted(f.review,decision);let nativeCaptures=0;
 const recipes=createBusinessCoreRecipeOwnerV2({assertCurrent(){throw Error('ACTUAL_NATIVE_REQUIRED');},capture(){nativeCaptures++;throw Error('not supplied');}}),owner=createBusinessReviewOwnerV2(recipes),subjects=createBusinessReviewSubjectOwnerV2(recipes);
 assert.throws(()=>owner.assertCurrent(f.review as any),/BUSINESS_REVIEW_HANDLE/);assert.throws(()=>owner.assertDecisionCurrent(decision as any),/UNREGISTERED/);assert.throws(()=>owner.assertAcceptedCurrent(accepted as any),/UNREGISTERED/);
 assert.throws(()=>owner.prepare(f.review as any,'dispatching',f.review.subject),/UNREGISTERED/);assert.throws(()=>subjects.prepare({kind:'business-recipe-selection-v2'} as any,'dispatching',f.review.subject),/UNREGISTERED/);assert.equal(nativeCaptures,0);
});
test('K01 actual Alch direct-source adapter rejects forged or source-only custody through public owners',async t=>{
 const f=fixture(t),root=process.env.U0_INSTALLED_CONSUMER!,alch=path.join(root,'node_modules/@cyberalchemy/alchlang/dist');
 const resolver=await import(pathToFileURL(path.join(alch,'business-authoring-resolve.js')).href),carrier=await import(pathToFileURL(path.join(alch,'business-authoring-carriers.js')).href),adapter=await import(pathToFileURL(path.join(alch,'business-authoring-review.js')).href);
 const resolved=resolver.prepareBusinessSpecFileV2(path.dirname(f.source),'business.alch'),lowered=carrier.lowerDirectBusinessV2(resolved);
 const recipes=createBusinessCoreRecipeOwnerV2({assertCurrent(){throw Error('ACTUAL_NATIVE_REQUIRED');},capture(){throw Error('no native basis fixture');}}),owner=createBusinessReviewOwnerV2(recipes);
 assert.throws(()=>adapter.prepareDirectBusinessReviewV2(lowered,f.review,owner),/UNREGISTERED/);
 for(const method of ['assertPreparedDirectBusinessReviewV2Current','assertCapturedDirectBusinessDecisionV2Current','assertAcceptedDirectBusinessReviewV2Current'])assert.throws(()=>adapter[method]({kind:'forged',accepted:true}),/registered/);
 resolver.disposeResolvedBusinessSpecV2(resolved);assert.throws(()=>adapter.prepareDirectBusinessReviewV2(lowered,f.review,owner),/DISPOSED/);
});
