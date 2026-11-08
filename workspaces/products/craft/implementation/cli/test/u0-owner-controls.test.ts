import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Actual built public owners and a new source/decision/project/output branch.
// No serialized object is treated as custody and no business callback is supplied.
// Open Questions: V02 CONTEXT; installed controls belong to H01/V03.
const core=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),repo=path.resolve(core,'../../../../..'),alch=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation'),out=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/V02'),run=fs.mkdtempSync(path.join(out,'owners-')),sha=(v:Buffer|string)=>crypto.createHash('sha256').update(v).digest('hex');
process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT=core;
const front=await import(pathToFileURL(path.join(alch,'dist/index.js')).href),api=(await import(pathToFileURL(path.join(core,'dist/index.js')).href)).profileEngine;
const observed:any[]=[],observe=(id:string,detail:unknown)=>{observed.push({id,detail});process.stdout.write('V02 '+id+'\n');fs.writeFileSync(path.join(run,'progress.json'),JSON.stringify({observed,scope:'original public owner controls in progress',authority_effect:'none'},null,2)+'\n');};
const reject=(id:string,fn:()=>unknown,expected?:RegExp)=>{assert.throws(fn,expected,id);observe(id,'rejected by actual owner');};
const choice={profile:'node-http-entry-u0-v4',output:'code'};
test('current original prefix rejects wrong custody and publishes complete fresh output through actual owners',async()=>{
 const source=path.join(run,'business-source');fs.mkdirSync(source);fs.copyFileSync(path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/J02/selected-project/business.alch'),path.join(source,'business.alch'));
 const p=await front.prepareDirectBusinessAuthoringProjectV2(source,'business.alch',choice),rt=p.runtime;observe('prepared-original-source',{sdk:rt.basis.sdk_sha256,basis:rt.basis.basis_sha256});
 // Explicit acceptance of a known qualification fixture, never human/product approval.
 const file=path.join(run,'accepted.json');front.recordDirectBusinessReviewDecisionV2(p.review,{decision_id:'v02-controls-qualification-only',owner:'dispatch-team',outcome:'accepted',reviewed_digest:p.review.review.review_sha256},file);
 const joined=await front.replayDirectBusinessAuthoringPrefixV2(p,file,path.join(run,'source-project'),path.join(run,'callable'));observe('original-prefix',{realized:joined.bound.subject.realized_sha256});
 const {input,application,generated,callable,bound,coverage,views}=joined;
 assert.equal(input.selection,p.selection);assert.equal(input.early_requests,p.early);assert.equal(application.input,input);assert.equal(generated.application,application);assert.equal(callable.source,generated);assert.equal(bound.callable,callable);assert.equal(coverage.bound,bound);assert.equal(views.coverage,coverage);
 for(const [id,fn]of [
 ['cloned-review',()=>rt.reviews.assertCurrent({...p.review.review})],
 ['graph-clone',()=>rt.applications.assertCurrent({...application,graph:{...application.graph}})],
 ['early-clone',()=>rt.requests.assertEarlyCurrent({...p.early})],
 ['view-clone',()=>rt.views.assertCurrent({...views})],
 ['native-basis-data-only',()=>rt.native.assertCurrent(structuredClone(rt.basis))],
 ['caller-auth-assertion',()=>rt.inputs.assertCurrent({accepted:true,authorized:true,input})],
 ['cloned-input',()=>rt.inputs.assertCurrent(structuredClone(input))],
 ['cloned-bound',()=>rt.requests.assertBoundCurrent({...bound})],
 ] as [string,()=>unknown][])reject(id,fn);
 const otherOwner=api.createBusinessReviewOwnerV2(rt.recipes);reject('wrong-owner-instance',()=>otherOwner.assertCurrent(p.review.review));
 reject('wrong-review-subject',()=>rt.reviews.prepare(p.selection,'dispatching',{...p.review.review.subject,executable_sha256:'0'.repeat(64)}));
 const otherSelection=rt.recipes.select(p.selection.models,rt.basis),otherEarly=rt.requests.prepareEarly(otherSelection);assert.equal(otherSelection.selection_sha256,p.selection.selection_sha256);
 reject('wrong-selection',()=>rt.inputs.form(otherSelection,'dispatching',joined.accepted.accepted,otherEarly));
 reject('wrong-entry',()=>rt.inputs.form(p.selection,'wrong-model',joined.accepted.accepted,p.early));
 await assert.rejects(()=>rt.requests.bindLate(otherEarly,callable,rt.basis));observe('equal-data-foreign-early','rejected actual distinct early pointer');
 let injected=0;await assert.rejects(()=>rt.requests.bindLate(p.early,{invoke(){injected++;}},rt.basis));assert.equal(injected,0);observe('callable-substitution','rejected before injected callable executes');
 const declined=path.join(run,'declined.json'),decline=front.recordDirectBusinessReviewDecisionV2(p.review,{decision_id:'v02-declined-fixture',owner:'dispatch-team',outcome:'declined',reviewed_digest:p.review.review.review_sha256},declined);reject('declined-decision',()=>front.requireAcceptedDirectBusinessReviewV2(p.review,decline),/DECLINED/);
 for(const kind of ['byte-drift','inode-replacement']){const target=path.join(run,'decision-'+kind+'.json'),decision=front.recordDirectBusinessReviewDecisionV2(p.review,{decision_id:'v02-'+kind,owner:'dispatch-team',outcome:'accepted',reviewed_digest:p.review.review.review_sha256},target);if(kind==='byte-drift')fs.appendFileSync(target,'\n');else{const bytes=fs.readFileSync(target);fs.renameSync(target,target+'.original');fs.writeFileSync(target,bytes);}
 reject('decision-'+kind,()=>front.assertCapturedDirectBusinessDecisionV2Current(decision));}
 const required=['code','api-contracts','business-graph','system-graph','business-system-bridge'],plan=api.planBusinessOutputsV2([...required.map(kind=>({kind,requiredness:'required'})),{kind:'base-model',requiredness:'optional'},{kind:'conjecture-problems',requiredness:'optional'}]);
 for(const kind of ['base-model','conjecture-problems'])reject('output-required-formal:'+kind,()=>api.planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind,requiredness:'required'}]),/UNSUPPORTED/);
 const artifacts=rt.output.prepareArtifacts(plan,application,bound,views);observe('original-output-producers',{files:artifacts.length});
 const target=path.join(run,'application'),request={target,plan,application,bound,views,artifacts};
 reject('output-required-missing',()=>rt.output.publish({...request,artifacts:artifacts.slice(1)}),/OUTPUT_HANDLE/);assert.equal(fs.existsSync(target),false);
 reject('output-view-forgery',()=>rt.output.publish({...request,views:{...views}}),/OUTPUT_JOIN/);
 const result=rt.output.publish(request);assert.equal(result.rows.filter((r:any)=>r.state==='produced').length,5);assert.equal(result.rows.filter((r:any)=>r.state==='unsupported-optional'&&r.artifact===null).length,2);observe('output-fresh-and-optional-formal',result);
 const module=await import(pathToFileURL(path.join(target,'entry.mjs')).href),response=await module.handler(new Request('https://qualification.invalid/confirm-delivery',{method:'POST',headers:{'content-type':'application/json'},body:'{"id":"18446744073709551615","verified":true}'}));assert.equal(response.status,200);assert.equal(await response.text(),'{"kind":"completed","value":{"id":"18446744073709551615","verified":true}}');observe('actual-output-behavior','literal UInt64 max positive expected result');
 const occupied=path.join(run,'occupied');fs.mkdirSync(occupied);fs.writeFileSync(path.join(occupied,'prior'),'keep');const inode=fs.statSync(occupied,{bigint:true}).ino;reject('output-target-nonempty',()=>rt.output.publish({...request,target:occupied}));assert.equal(fs.statSync(occupied,{bigint:true}).ino,inode);assert.equal(fs.readFileSync(path.join(occupied,'prior'),'utf8'),'keep');
 const empty=path.join(run,'empty');fs.mkdirSync(empty);const emptyInode=fs.statSync(empty,{bigint:true}).ino;reject('output-target-empty',()=>rt.output.publish({...request,target:empty}));assert.equal(fs.statSync(empty,{bigint:true}).ino,emptyInode);assert.deepEqual(fs.readdirSync(empty),[]);
 // Independent original callable import permits a destructive control without
 // invalidating the principal generated branch or its bound output evidence.
 const branch=path.join(run,'drift-callable');api.publishBusinessAuthoringDirectory(branch,generated.files.map((f:any)=>({relative_path:f.path,content:f.content})),'.domainspec-direct-control-',()=>rt.applications.assertCurrent(application));const imported=await rt.generation.importGenerated(generated,path.join(branch,'invoke.mjs'));fs.appendFileSync(path.join(branch,'invoke.mjs'),'\n');reject('callable-file-drift',()=>rt.generation.assertCurrent(imported));
 // Source edit is last: the original shared checkout is never mutated and no
 // changed bytes are relabeled current or silently repaired.
 fs.appendFileSync(path.join(source,'business.alch'),'\n# V02 capture-only physical drift\n');reject('source-whitespace-drift',()=>rt.inputs.assertCurrent(input));const stale=rt.output.check(request);assert(stale.rows.filter((r:any)=>r.requiredness==='required').every((r:any)=>r.state==='stale'));observe('output-source-drift-currentness',stale);
 fs.writeFileSync(path.join(run,'owner-controls-observation.json'),JSON.stringify({schema_version:'craft.u0-owner-controls/v1-candidate',sdk_sha256:rt.basis.sdk_sha256,basis_sha256:rt.basis.basis_sha256,realized_subject:bound.subject,source_root:path.relative(repo,source),source_mutation:'owned branch only, retained; original capture now stale',observed,actual_original_owner_pointers:true,qualification_decision_only:true,installed:'not-performed',authority_effect:'none',open_questions_ref:'../CONTEXT.md#open-questions'},null,2)+'\n',{flag:'wx'});
});
