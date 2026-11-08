import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Explicit qualification-fixture decisions only. Never user/product approval.
// Open Questions: K02 context; U04/G01 still own accepted input and application.
const alch=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),root=path.resolve(alch,'../../../../../..'),core=path.join(root,'craft/projects/domainspec-v2/impl/cli'),out=path.join(root,'implementation/craft-alchlang-commerce-2026-10-16/evidence/K02'),sourceRoot=path.join(out,'../J02/selected-project');
process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT=core;
const front=await import(pathToFileURL(path.join(alch,'dist/index.js')).href),choice={profile:'node-http-entry-u0-v4',output:'code'},hash=(bytes:Buffer)=>crypto.createHash('sha256').update(bytes).digest('hex');
const prepare=()=>front.prepareDirectBusinessAuthoringProjectV2(sourceRoot,'business.alch',choice);
const decisionRequest=(p:any,outcome='accepted',id='qualification-accepted')=>({decision_id:id,owner:'dispatch-team',outcome,reviewed_digest:p.review.review.review_sha256});

test('zero-claim original review yields explicit qualification decision/file capture and genuine accepted owner',async()=>{
 const p=await prepare();try{const review=p.review.review;assert.equal(p.lowered.business.data.claims.length,0);assert.equal(review.selection,p.selection);assert.equal(Object.hasOwn(p,'accepted'),false);assert.throws(()=>p.runtime.inputs.form(p.selection,'dispatching',{accepted:true},p.early));
  const rendered=p.runtime.reviews.render(review);assert.equal(typeof rendered,'string');assert(rendered.includes('CanProcess'));fs.writeFileSync(path.join(out,'qualification-review.txt'),rendered,{flag:'wx'});
  const file=path.join(out,'qualification-accepted.json'),recorded=front.recordDirectBusinessReviewDecisionV2(p.review,decisionRequest(p),file),captured=front.captureDirectBusinessReviewDecisionV2(p.review,file),accepted=front.requireAcceptedDirectBusinessReviewV2(p.review,captured);front.assertAcceptedDirectBusinessReviewV2Current(accepted);p.runtime.reviews.assertAcceptedCurrent(accepted.accepted);
  assert.equal(accepted.prepared,p.review);assert.equal(accepted.decision,captured);assert.equal(accepted.accepted.review,review);assert.equal(accepted.accepted.decision,captured.decision);assert.equal(recorded.decision.decision.subject.sha256,review.review_sha256);assert.equal(captured.decision.decision.capture_sha256,p.selection.models[0].capture.capture_sha256);
  const bytes=fs.readFileSync(file),stat=fs.statSync(file,{bigint:true});assert.equal(captured.decision.file.sha256,hash(bytes));assert.equal(captured.decision.file.bytes,bytes.length);assert.equal(captured.decision.file.inode,String(stat.ino));assert.equal(stat.mode&0o777n,0o600n);
  assert.throws(()=>front.recordDirectBusinessReviewDecisionV2(p.review,decisionRequest(p,'accepted','qualification-second'),file));assert.equal(hash(fs.readFileSync(file)),hash(bytes));
  assert.throws(()=>front.assertAcceptedDirectBusinessReviewV2Current(structuredClone(accepted)));assert.throws(()=>p.runtime.reviews.assertAcceptedCurrent(structuredClone(accepted.accepted)));assert.throws(()=>front.requireAcceptedDirectBusinessReviewV2(p.review,structuredClone(captured)));
  fs.writeFileSync(path.join(out,'accepted-review-observation.json'),JSON.stringify({schema_version:'craft.u0-accepted-review-observation/v1-candidate',decision_scope:'explicit qualification fixture only; not user/product/release approval',source_sha256:p.selection.models[0].source.sha256,selection_sha256:p.selection.selection_sha256,review_sha256:review.review_sha256,decision:captured.decision.decision,file:captured.decision.file,original_review_decision_acceptance_pointers:true,formal_claims:0,accepted_application_input:'not-created',callable:'not-generated',authority_effect:'none',open_questions_ref:'CONTEXT.md#open-questions'},null,2)+'\n',{flag:'wx'});
 }finally{front.disposeDirectBusinessAuthoringProjectV2(p);}
});

test('declined, wrong subject/capture/executable/owner and foreign/serialized decisions fail before input',async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'craft-k02-negative-')),p=await prepare(),foreign=await prepare();try{
  const declined=front.recordDirectBusinessReviewDecisionV2(p.review,decisionRequest(p,'declined','qualification-declined'),path.join(temp,'declined.json'));assert.throws(()=>front.requireAcceptedDirectBusinessReviewV2(p.review,declined));
  const good=front.recordDirectBusinessReviewDecisionV2(p.review,decisionRequest(p,'accepted','qualification-control'),path.join(temp,'accepted.json')),accepted=front.requireAcceptedDirectBusinessReviewV2(p.review,good);
  assert.throws(()=>foreign.runtime.reviews.assertAcceptedCurrent(accepted.accepted));assert.throws(()=>front.requireAcceptedDirectBusinessReviewV2(foreign.review,good));
  for(const [name,mutate]of [['subject',(v:any)=>{v.subject.sha256='0'.repeat(64);}],['capture',(v:any)=>{v.capture_sha256='0'.repeat(64);}],['executable',(v:any)=>{v.executable_sha256='0'.repeat(64);}],['owner',(v:any)=>{v.owner='foreign-team';}]] as const){const value=structuredClone(good.decision.decision);mutate(value);const file=path.join(temp,name+'.json');fs.writeFileSync(file,JSON.stringify(value));assert.throws(()=>front.captureDirectBusinessReviewDecisionV2(p.review,file));}
  for(const [name,change]of [['wrong-owner',{owner:'foreign-team'}],['wrong-reviewed-digest',{reviewed_digest:'0'.repeat(64)}],['implicit',{accepted:true}]] as const){const file=path.join(temp,name+'.json');assert.throws(()=>front.recordDirectBusinessReviewDecisionV2(p.review,{...decisionRequest(p),...change},file));assert.equal(fs.existsSync(file),false);}
  assert.throws(()=>p.runtime.inputs.form(p.selection,'dispatching',declined,p.early));
 }finally{front.disposeDirectBusinessAuthoringProjectV2(p);front.disposeDirectBusinessAuthoringProjectV2(foreign);fs.rmSync(temp,{recursive:true,force:true});}
});

test('physical same-byte decision replacement invalidates original capture and acceptance',async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'craft-k02-stale-')),p=await prepare();try{const file=path.join(temp,'accepted.json'),capture=front.recordDirectBusinessReviewDecisionV2(p.review,decisionRequest(p,'accepted','qualification-stale-control'),file),accepted=front.requireAcceptedDirectBusinessReviewV2(p.review,capture),bytes=fs.readFileSync(file);fs.rmSync(file);fs.writeFileSync(file,bytes,{mode:0o600});assert.throws(()=>front.assertCapturedDirectBusinessDecisionV2Current(capture));assert.throws(()=>front.assertAcceptedDirectBusinessReviewV2Current(accepted));}finally{front.disposeDirectBusinessAuthoringProjectV2(p);fs.rmSync(temp,{recursive:true,force:true});}
});
