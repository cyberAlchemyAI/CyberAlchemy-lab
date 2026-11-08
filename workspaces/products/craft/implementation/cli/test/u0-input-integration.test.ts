import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Original public selection/early/accepted -> original L02 input only.
// Open Questions: U04 context; no graph, callable or late binding here.
const core=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),root=path.resolve(core,'../../../../..'),alch=path.join(root,'language/capabilities/alchlang/plans/general-compiler-v1/implementation'),out=path.join(root,'implementation/craft-alchlang-commerce-2026-10-16/evidence/U04'),sourceRoot=path.join(out,'../J02/selected-project'),decision=path.join(out,'../K02/qualification-accepted.json');
process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT=core;const front=await import(pathToFileURL(path.join(alch,'dist/index.js')).href),choice={profile:'node-http-entry-u0-v4',output:'code'},expected=JSON.parse(fs.readFileSync(path.join(core,'test/profile-engine/fixtures/u0-v2/spec.json'),'utf8'));
const prepare=async(source=sourceRoot)=>{const p=await front.prepareDirectBusinessAuthoringProjectV2(source,'business.alch',choice),capture=front.captureDirectBusinessReviewDecisionV2(p.review,decision),accepted=front.requireAcceptedDirectBusinessReviewV2(p.review,capture);return {p,capture,accepted};};
const form=(state:any)=>state.p.runtime.inputs.form(state.p.selection,'dispatching',state.accepted.accepted,state.p.early);

test('real original input retains current selection/early/acceptance/capture and independently declared zero-claim semantics',async()=>{
 const s=await prepare(),p=s.p;try{const input=form(s),model=p.selection.models[0];p.runtime.inputs.assertCurrent(input);assert.equal(input.kind,'authoring-business-input-v2');assert.equal(input.selection,p.selection);assert.equal(input.early_requests,p.early);assert.equal(input.accepted,s.accepted.accepted);assert.equal(input.capture,model.capture);assert.equal(input.spec,model.spec);assert.deepEqual(JSON.parse(JSON.stringify(input.spec)),expected);assert.equal(input.spec.claims.length,0);assert.equal(input.spec.definitions.length,0);
  for(const key of ['resources','formal_claim_join','request_graph','callable','handler','realized_sha256'])assert.equal(Object.hasOwn(input,key),false);assert.equal(input.early_requests.entries[0].unresolved_native_obligations.length,4);
  fs.writeFileSync(path.join(out,'original-input-observation.json'),JSON.stringify({schema_version:'craft.u0-original-input-observation/v1-candidate',input,original_pointers:{selection:true,early:true,accepted:true,capture:true,spec:true},independent_fixed_spec_matches:true,formal_claims:0,decision_scope:'qualification fixture only; not user/product approval',graph:'not-compiled',callable:'not-generated',authority_effect:'none',open_questions_ref:'CONTEXT.md#open-questions'},null,2)+'\n',{flag:'wx'});
 }finally{front.disposeDirectBusinessAuthoringProjectV2(p);}
});

test('cross-selection, serialized/foreign handles and forged source fail despite matching data identities',async()=>{
 const s=await prepare(),p=s.p,foreign=await prepare();try{const input=form(s),runtime=p.runtime,other=runtime.recipes.select(p.selection.models,runtime.basis),otherEarly=runtime.requests.prepareEarly(other);assert.equal(other.selection_sha256,p.selection.selection_sha256);assert.notEqual(other,p.selection);
  assert.throws(()=>runtime.inputs.form(other,'dispatching',s.accepted.accepted,otherEarly));assert.throws(()=>runtime.inputs.form(p.selection,'dispatching',s.accepted.accepted,otherEarly));assert.throws(()=>runtime.inputs.form(p.selection,'dispatching',structuredClone(s.accepted.accepted),p.early));assert.throws(()=>runtime.inputs.form(p.selection,'dispatching',s.accepted.accepted,structuredClone(p.early)));assert.throws(()=>runtime.inputs.form(p.selection,'wrong-model',s.accepted.accepted,p.early));assert.throws(()=>runtime.inputs.assertCurrent(structuredClone(input)));assert.throws(()=>foreign.p.runtime.inputs.assertCurrent(input));
  const model=p.selection.models[0],fake={...model,source:{...model.source,text:model.source.text+'\n'}};assert.throws(()=>runtime.recipes.select([fake],runtime.basis));
 }finally{front.disposeDirectBusinessAuthoringProjectV2(p);front.disposeDirectBusinessAuthoringProjectV2(foreign.p);}
});

test('changed accepted fixture file invalidates the already formed original input',async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'craft-u04-decision-')),s=await prepare(),p=s.p;try{const file=path.join(temp,'qualification.json'),capture=front.recordDirectBusinessReviewDecisionV2(p.review,{decision_id:'qualification-u04-stale',owner:'dispatch-team',outcome:'accepted',reviewed_digest:p.review.review.review_sha256},file),accepted=front.requireAcceptedDirectBusinessReviewV2(p.review,capture),input=p.runtime.inputs.form(p.selection,'dispatching',accepted.accepted,p.early);p.runtime.inputs.assertCurrent(input);fs.appendFileSync(file,'\n');assert.throws(()=>p.runtime.inputs.assertCurrent(input));}finally{front.disposeDirectBusinessAuthoringProjectV2(p);fs.rmSync(temp,{recursive:true,force:true});}
});

test('physical source drift invalidates original accepted input without changing its copied JSON',async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'craft-u04-source-'));try{const file=path.join(temp,'business.alch');fs.copyFileSync(path.join(sourceRoot,'business.alch'),file);const s=await prepare(temp),input=form(s),before=JSON.stringify(input);fs.appendFileSync(file,'\n');assert.equal(JSON.stringify(input),before);assert.throws(()=>s.p.runtime.inputs.assertCurrent(input));}finally{fs.rmSync(temp,{recursive:true,force:true});}
});
