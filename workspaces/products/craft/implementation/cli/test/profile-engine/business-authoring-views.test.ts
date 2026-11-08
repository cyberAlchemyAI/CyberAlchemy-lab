import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
// Actual public owner joins only; local explicit fixture approvals are recorded.
// No native compiler, listener, business invocation or publication. Open questions:
// independent source/installed qualification and the whole-plan completion audit.
const cli=path.resolve(import.meta.dirname,'../..'),repo=path.resolve(cli,'../../../../..'),alch=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation');
const json=(file:string)=>JSON.parse(readFileSync(file,'utf8')),plain=<T>(value:T):T=>JSON.parse(JSON.stringify(value)),hash=(text:string)=>createHash('sha256').update(text).digest('hex');
async function fixture(t:{after(fn:()=>void):void},profile='node-http-entry-local-v3',count=1){
 const A=await import(pathToFileURL(path.join(alch,'src/index.ts')).href),compiler=await A.loadDomainSpecCompiler(cli),core=compiler.profileEngine as any;
 assert.equal(typeof core.projectBusinessAuthoringViews,'function','root must export/build the genuine view owner before tests');
 const root=mkdtempSync(path.join(os.tmpdir(),'business-authoring-views-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(cli,'profiles',profile),path.join(root,'profile'),{recursive:true});const pkg=json(path.join(root,'profile/profile.json'));
 const models=json(path.join(alch,'test/fixtures/business-authoring/composition-intent.json')).models.slice(0,count);for(const model of models){const file=path.join(root,model.source);mkdirSync(path.dirname(file),{recursive:true});cpSync(path.join(alch,'test/fixtures/business-authoring',model.source),file);}
 writeFileSync(path.join(root,'project.json'),JSON.stringify({schema_version:'craft.business-authoring-project/v1-candidate',id:'views-fixture',models:models.map((model:any)=>({id:model.model_id,source:model.source})),profiles:[{id:pkg.id,version:pkg.version,path:'profile'}],decisions:[]}));
 const identity={engine:['business-authoring-recipes.js','business-authoring-input.js','business-authoring-request.js','business-authoring-application.js','business-authoring-coverage.js','business-authoring-views.js','business-review.js','business-decision.js','loader-v3.js'].map(key=>({key,path:path.join(cli,'dist/profile-engine',key)})),tools:['business-authoring-semantics.ts','business-authoring-behavior.ts','business-authoring-profile-selection.ts','business-authoring-carriers.ts','business-authoring-request.ts','business-authoring-review.ts','business-authoring-prepare.ts'].map(key=>({key,path:path.join(alch,'src',key)}))};
 const snapshot=core.loadBusinessAuthoringProject(path.join(root,'project.json'),identity),business=models.map((model:any)=>A.prepareBusinessSpecFile(root,model.source)),behavior=business.map((value:any)=>A.lowerBusinessBehavior(A.lowerBusinessFormalSemantics(value))),prepared=A.prepareBusinessRecipeSelection(snapshot,behavior,core),requests=core.prepareBusinessAuthoringRequests(prepared.selection),checked:any[]=[];
 for(const model of models){const preview=A.previewBusinessSemantics(prepared,model.model_id),review=A.prepareBusinessReview(preview,core),decision=A.recordBusinessReviewDecision(review,{decision_id:'views-explicit-'+model.model_id,owner:preview.review.model_identity.owner,outcome:'accepted',reviewed_digest:review.review.subject.digest},path.join(root,'decision-'+model.model_id+'.json'),core),accepted=A.requireAcceptedBusinessReviewDecision(review,decision,core),value=A.prepareBusinessAuthoringApplication(accepted,requests,compiler);checked.push(value);t.after(()=>{try{A.disposePreparedBusinessAuthoringApplication(value);}catch{}rmSync(value.workspace,{recursive:true,force:true});});}
 const application=core.prepareBusinessAuthoringApplication(checked,A.assertPreparedBusinessAuthoringApplicationCurrent),value=core.projectBusinessAuthoringViews(application);return {A,core,root,models,snapshot,business,prepared,checked,application,value};
}
test('existing view schemas retain complete original business facts and actual system/request owners',async t=>{
 const f=await fixture(t,'node-http-shared-ports-v3',2),v=f.value;f.core.assertBusinessAuthoringViewsCurrent(v);
 assert.equal(v.application,f.application);assert.equal(v.reports.length,2);assert.equal(v.business.schema_version,'craft.profile-business-view/v1');assert.equal(v.system.schema_version,'craft.profile-system-view/v1');assert.equal(v.bridge.schema_version,'craft.profile-bridge-view/v1');
 assert.deepEqual(plain(v.business.application_intents),plain(f.application.requests.project_intents));assert.deepEqual(plain(v.system.components),plain(f.application.composition.components));
 for(const model of f.application.selection.models){const actual=v.business.authoring.models.find((value:any)=>value.model_id===model.model_id);assert.deepEqual(plain(actual.spec),plain(model.spec));assert.deepEqual(plain(actual.source),plain(model.source));}
 assert.equal(v.system.applications.length,2);for(const actual of v.system.applications){const model=f.application.models.find((value:any)=>value.callables.some((callable:any)=>callable.intent.id===actual.intent_id));assert.deepEqual(plain(actual.application_graph),plain(model.binding.application_graph));assert.equal(actual.request_application_plan_sha256,model.plan.plan_sha256);}
 assert.equal(v.bridge.ontology_admitted,false);assert.ok(v.coverage.items.some((item:any)=>item.state==='claim-residue'));assert.ok(v.coverage.items.every((item:any)=>item.evidence_states.every((state:string)=>['linked','generated'].includes(state))));
 assert.match(v.text.business,/Formal claims remain unproved residue/);assert.match(v.text.system,/Wire craft\.operation-json-post/);assert.match(v.text.bridge,/accepted meaning, native checks, finite observation, proof and ontology admission remain distinct/);
});
test('every bridge pointer resolves to an actually emitted artifact and exact original/decision origin',async t=>{
 const f=await fixture(t),v=f.value;f.core.validateBusinessAuthoringContract('ledger',v.ledger);f.core.validateCoverageShape(v.coverage);
 for(const entry of v.ledger.entries){assert.ok(Object.hasOwn(v.files,entry.target.artifact));const text=v.files[entry.target.artifact],data=entry.target.artifact.endsWith('.json')?JSON.parse(text):text;assert.notEqual(f.core.resolveBusinessAuthoringCoveragePointer(data,entry.target.pointer),undefined);
  for(const origin of entry.origins){if(origin.kind==='business')assert.ok(f.business.some((model:any)=>model.data.source_spans.some((span:any)=>span.source===origin.source&&span.selector===origin.selector&&span.source_sha256===origin.sha256)));
   if(origin.kind==='owner-decision'){assert.ok(Object.hasOwn(v.files,origin.source));assert.equal(hash(v.files[origin.source]),origin.sha256);assert.notEqual(f.core.resolveBusinessAuthoringCoveragePointer(JSON.parse(v.files[origin.source]),origin.selector),undefined);}
   if(origin.kind==='semantic-adapter'&&origin.source.startsWith('lineage/')){assert.ok(Object.hasOwn(v.files,origin.source));const value=f.core.resolveBusinessAuthoringCoveragePointer(JSON.parse(v.files[origin.source]),origin.selector);assert.equal(f.core.dataDigest(value),origin.sha256);}
  }
 }
 for(const [file,body] of Object.entries(f.application.files))assert.equal(v.files[file],body);
 for(const model of f.application.models)for(const captured of model.input.applications){assert.equal(v.files[captured.model.source],captured.source);assert.equal(hash(v.files[captured.model.source]),captured.source_sha256);assert.equal(hash(v.files[captured.model.semantics]),captured.semantics_sha256);assert.deepEqual(JSON.parse(v.files[captured.model.semantics]),plain(captured.semantics));}
 for(const model of f.application.models){const index=JSON.parse(v.files['lineage/formal-index/'+model.model_id+'.json']);assert.equal(index.claim_state,'unproved');for(const [key,body] of Object.entries(model.formal.sources) as [string,string][]){assert.equal(v.files[index.sources[key].artifact],body);assert.equal(index.sources[key].sha256,hash(body));}for(const claim of f.application.selection.models.find((value:any)=>value.model_id===model.model_id).spec.claims){const actual=JSON.parse(v.files[index.sources['formalization/claims/'+claim.id+'.json'].artifact]);assert.equal(actual.schema_version,'domainspec-v2.formal-claim-source/v4-candidate');assert.equal(actual.canonical_proposition.representation,claim.proposition);}}
 const manifest=JSON.parse(v.files['evidence/business-authoring-manifest.json']);assert.equal(manifest.views_sha256,v.views_sha256);assert.equal(Object.hasOwn(manifest.files,'evidence/business-authoring-manifest.json'),false);
 for(const [file,fingerprint] of Object.entries(manifest.files) as [string,any][]){assert.equal(hash(v.files[file]),fingerprint.sha256);assert.equal(Buffer.byteLength(v.files[file]),fingerprint.bytes);}
 assert.equal(f.core.renderBusinessAuthoringViews(v),v.files);assert.ok(Object.isFrozen(v.files));
});
test('relocating identical fixture captures and scratch keeps portable views and manifest bytes deterministic',async t=>{
 const first=await fixture(t),second=await fixture(t),a=first.value,b=second.value;
 assert.notEqual(first.root,second.root);assert.notEqual(first.checked[0].workspace,second.checked[0].workspace);
 assert.deepEqual(a.business,b.business);assert.deepEqual(a.system,b.system);assert.deepEqual(a.bridge,b.bridge);assert.equal(a.views_sha256,b.views_sha256);assert.deepEqual(a.files,b.files);
 const encoded=JSON.stringify({business:a.business,system:a.system,bridge:a.bridge,coverage:a.coverage,ledger:a.ledger,text:a.text,files:a.files});assert.equal(encoded.includes(first.root),false);for(const value of first.checked)assert.equal(encoded.includes(value.workspace),false);
});
test('profile architecture/prefix changes expose technical conventions without replacing authored facts or public audience',async t=>{
 const local=await fixture(t),shared=await fixture(t,'node-http-shared-ports-v3'),prefix=await fixture(t,'node-http-api-prefix-v3');
 for(const f of [shared,prefix])assert.deepEqual(f.value.business.authoring,local.value.business.authoring);
 assert.equal(local.value.system.authoring.transport,'entry-local');assert.equal(shared.value.system.authoring.transport,'shared');assert.equal(prefix.value.system.authoring.wire.route_prefix,'/api/');assert.equal(prefix.value.system.authoring.routes[0].route,'/api/confirmDelivery');
 for(const f of [local,shared,prefix]){assert.equal(f.value.business.authoring.models[0].spec.capabilities[0].audience,'public');assert.equal(Object.hasOwn(f.value.business.authoring.reviews[0].review,'wire'),false);}
});
test('each missing obligation class independently prevents view projection; no emitted denominator can hide it',async t=>{
 const f=await fixture(t),report=f.value.reports[0],classes=new Set(report.items.map((item:any)=>item.family+':'+item.class));
 for(const kind of classes){const links=report.items.filter((item:any)=>item.family+':'+item.class!==kind).map(({obligation_id,origins,targets}:any)=>({obligation_id,origins,targets})),incomplete=f.core.assessBusinessAuthoringCoverage(report.prepared,f.application,links);assert.equal(incomplete.complete,false);assert.throws(()=>f.core.projectBusinessAuthoringViews(f.application,[incomplete]),/INCOMPLETE/,String(kind));}
 assert.throws(()=>f.core.projectBusinessAuthoringViews(f.application,[]));assert.throws(()=>f.core.projectBusinessAuthoringViews(f.application,[report,report]));
});
test('clones and disposed/currently changed owners revoke every view/render path',async t=>{
 const f=await fixture(t);assert.throws(()=>f.core.assertBusinessAuthoringViewsCurrent({...f.value}));assert.throws(()=>f.core.projectBusinessAuthoringViews({...f.application}));assert.throws(()=>f.core.renderBusinessAuthoringViews(plain(f.value)));
 f.A.disposePreparedBusinessAuthoringApplication(f.checked[0]);assert.throws(()=>f.core.assertBusinessAuthoringViewsCurrent(f.value));assert.throws(()=>f.core.renderBusinessAuthoringViews(f.value));
 const drift=await fixture(t),file=path.join(drift.root,'decision-'+drift.models[0].model_id+'.json');writeFileSync(file,readFileSync(file,'utf8')+'\n');assert.throws(()=>drift.core.assertBusinessAuthoringViewsCurrent(drift.value));
});
