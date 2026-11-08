import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
// Genuine public Alch and one built public Core SDK own all inputs. Decisions are
// explicit temporary fixture records; no native compiler or business code runs.
// Open questions: B08.2 presentation and independent installed qualification.
const cli=path.resolve(import.meta.dirname,'../..'),repo=path.resolve(cli,'../../../../..'),alch=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation');
const plain=<T>(value:T):T=>JSON.parse(JSON.stringify(value)),json=(file:string)=>JSON.parse(readFileSync(file,'utf8'));
async function fixture(t:{after(fn:()=>void):void},profile='node-http-entry-local-v3',count=1){
 const A=await import(pathToFileURL(path.join(alch,'src/index.ts')).href),compiler=await A.loadDomainSpecCompiler(cli),core=compiler.profileEngine as any;
 assert.equal(typeof core.inventoryBusinessAuthoringObligations,'function','root must export/build the actual coverage owner');
 const root=mkdtempSync(path.join(os.tmpdir(),'business-coverage-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(cli,'profiles',profile),path.join(root,'profile'),{recursive:true});
 const pkg=json(path.join(root,'profile/profile.json')),models=json(path.join(alch,'test/fixtures/business-authoring/composition-intent.json')).models.slice(0,count);
 for(const model of models){const target=path.join(root,model.source);mkdirSync(path.dirname(target),{recursive:true});cpSync(path.join(alch,'test/fixtures/business-authoring',model.source),target);}
 const project={schema_version:'craft.business-authoring-project/v1-candidate',id:'coverage-fixture',models:models.map((model:any)=>({id:model.model_id,source:model.source})),profiles:[{id:pkg.id,version:pkg.version,path:'profile'}],decisions:[]};writeFileSync(path.join(root,'project.json'),JSON.stringify(project));
 const identity={engine:['business-authoring-recipes.js','business-authoring-input.js','business-authoring-request.js','business-authoring-application.js','business-authoring-coverage.js','business-review.js','business-decision.js','loader-v3.js'].map(key=>({key,path:path.join(cli,'dist/profile-engine',key)})),tools:['business-authoring-semantics.ts','business-authoring-behavior.ts','business-authoring-profile-selection.ts','business-authoring-carriers.ts','business-authoring-request.ts','business-authoring-review.ts','business-authoring-prepare.ts'].map(key=>({key,path:path.join(alch,'src',key)}))};
 const snapshot=core.loadBusinessAuthoringProject(path.join(root,'project.json'),identity),business=models.map((model:any)=>A.prepareBusinessSpecFile(root,model.source));
 // Capture the denominator before any formal/behavior lowering or recipe output.
 const inventories=business.map((value:any,index:number)=>core.inventoryBusinessAuthoringObligations(snapshot,models[index].model_id,value.data));
 const behaviors=business.map((value:any)=>A.lowerBusinessBehavior(A.lowerBusinessFormalSemantics(value))),prepared=A.prepareBusinessRecipeSelection(snapshot,behaviors,core),requests=core.prepareBusinessAuthoringRequests(prepared.selection),checked:any[]=[];
 for(const model of models){const preview=A.previewBusinessSemantics(prepared,model.model_id),review=A.prepareBusinessReview(preview,core),decision=A.recordBusinessReviewDecision(review,{decision_id:'coverage-explicit-'+model.model_id,owner:preview.review.model_identity.owner,outcome:'accepted',reviewed_digest:review.review.subject.digest},path.join(root,'decision-'+model.model_id+'.json'),core),accepted=A.requireAcceptedBusinessReviewDecision(review,decision,core),value=A.prepareBusinessAuthoringApplication(accepted,requests,compiler);checked.push(value);t.after(()=>{try{A.disposePreparedBusinessAuthoringApplication(value);}catch{}rmSync(value.workspace,{recursive:true,force:true});});}
 const application=core.prepareBusinessAuthoringApplication(checked,A.assertPreparedBusinessAuthoringApplicationCurrent),coverage=core.prepareBusinessAuthoringCoverage(prepared.selection,models[0].model_id,inventories[0]),report=core.assessBusinessAuthoringCoverage(coverage,application);
 return {A,core,root,snapshot,business,models,inventories,prepared,requests,checked,application,coverage,report};
}
const links=(report:any)=>report.items.map(({obligation_id,origins,targets}:any)=>({obligation_id,origins,targets}));
test('independent original denominator is complete before lowering and covers every obligation class',async t=>{
 const f=await fixture(t),inventory=f.inventories[0],source=f.business[0];f.core.assertBusinessAuthoringObligationInventoryCurrent(inventory);
 assert.equal(inventory.snapshot,f.snapshot);assert.equal(inventory.data.authored.length,source.data.obligations.length);assert.equal(inventory.data.business_sha256,source.business_sha256);
 assert.equal(inventory.data.authored.length,source.source.text.split('\n').filter((line:string)=>line.trim()&&!line.trimStart().startsWith('#')).length);
 const classes=new Set(inventory.data.authored.map((row:any)=>row.class));for(const kind of ['identity','declaration','field','formal-symbol','behavior','audience','exposure','scenario','reference','clause'])assert.ok(classes.has(kind),kind);
 const derived=new Set(inventory.data.derived.map((row:any)=>row.class));for(const kind of ['semantic-declaration','semantic-field','formal-definition','formal-claim','legacy-meaning','rule-interpretation','guard','result','failure','effects','public-intent','request-mapping','request-field','request-contract','request-method','route','request-body','request-limits','timeout','transport','owner-decision','recipe-profile','runtime-guarantee','profile-role'])assert.ok(derived.has(kind),kind);
 for(const row of inventory.data.authored){const origin=row.origins[0];assert.equal(origin.kind,'business');assert.ok(source.data.source_spans.some((span:any)=>span.selector===origin.selector&&span.source===origin.source&&span.source_sha256===origin.sha256));}
 assert.equal(new Set([...inventory.data.authored,...inventory.data.derived].map((row:any)=>row.id)).size,inventory.data.authored.length+inventory.data.derived.length);
 f.core.assertBusinessAuthoringCoverageComplete(f.report);assert.equal(f.report.items.length,inventory.data.authored.length+inventory.data.derived.length);
});
test('remove every authored and derived class independently: original denominator makes completeness fail',async t=>{
 const f=await fixture(t),all=links(f.report),classes=new Set(f.report.items.map((item:any)=>item.family+':'+item.class));
 for(const kind of classes){const retained=all.filter((link:any)=>{const row=f.report.items.find((item:any)=>item.obligation_id===link.obligation_id);return row.family+':'+row.class!==kind;}),report=f.core.assessBusinessAuthoringCoverage(f.coverage,f.application,retained);
  assert.equal(report.complete,false,kind);assert.ok(report.missing.length>0,kind);assert.equal(report.items.length,f.report.items.length,kind);assert.throws(()=>f.core.assertBusinessAuthoringCoverageComplete(report),/BUSINESS_COVERAGE_INCOMPLETE/,kind);
 }
});
test('coverage rejects self-certified targets, wrong source/profile origins, duplicate IDs and foreign owners',async t=>{
 const f=await fixture(t),all=links(f.report);
 for(const change of [(row:any)=>{row.targets=[{artifact:'invented.json',pointer:'/anything'}];},(row:any)=>{row.targets=[{artifact:'lineage/models/'+f.models[0].model_id+'.json',pointer:'/spec/source_spans/0'}];},(row:any)=>{row.origins[0].sha256='0'.repeat(64);},(row:any)=>{row.origins[0].kind='profile';}]){
  const candidate=plain(all);change(candidate[1]);assert.throws(()=>f.core.assessBusinessAuthoringCoverage(f.coverage,f.application,candidate));
 }
 assert.throws(()=>f.core.assessBusinessAuthoringCoverage(f.coverage,f.application,[...all,all[0]]));assert.throws(()=>f.core.assessBusinessAuthoringCoverage({...f.coverage},f.application));assert.throws(()=>f.core.assessBusinessAuthoringCoverage(f.coverage,{...f.application}));assert.throws(()=>f.core.assertBusinessAuthoringCoverageComplete({...f.report}));
 const missing=plain(f.business[0].data);missing.obligations.pop();assert.throws(()=>f.core.inventoryBusinessAuthoringObligations(f.snapshot,f.models[0].model_id,missing),/DENOMINATOR/);
 const foreign=await fixture(t);assert.throws(()=>f.core.prepareBusinessAuthoringCoverage(f.prepared.selection,f.models[0].model_id,foreign.inventories[0]));
});
test('closed mixed ledger resolves actual retained artifacts and keeps technical origins distinct from authorship',async t=>{
 const f=await fixture(t,'node-http-shared-ports-v3',2);f.core.validateBusinessAuthoringContract('ledger',f.report.ledger);f.core.assertBusinessAuthoringCoverageComplete(f.report);
 for(const entry of f.report.ledger.entries){assert.ok(Object.hasOwn(f.report.artifacts,entry.target.artifact));assert.notEqual(f.core.resolveBusinessAuthoringCoveragePointer(f.report.artifacts[entry.target.artifact],entry.target.pointer),undefined);assert.ok(Object.hasOwn(f.report.artifact_text,entry.target.artifact));}
 const audiences=f.report.items.filter((item:any)=>item.class==='audience');assert.ok(audiences.length);for(const item of audiences)assert.ok(item.origins.every((origin:any)=>origin.kind==='business'));
 for(const kind of ['route','request-body','request-limits','timeout','transport'])for(const item of f.report.items.filter((row:any)=>row.class===kind))assert.ok(item.origins.some((origin:any)=>origin.kind==='profile'&&origin.source==='profile:'+f.prepared.selection.technical.profile_id));
 const decision=f.report.items.find((item:any)=>item.class==='owner-decision');assert.ok(decision.origins.some((origin:any)=>origin.kind==='owner-decision'&&origin.source==='lineage/decisions/'+f.models[0].model_id+'.json'));
 assert.ok(f.report.items.filter((item:any)=>item.class==='formal-claim').every((item:any)=>item.state==='claim-residue'));
 for(const item of f.report.items)assert.ok(item.evidence_states.every((state:string)=>['linked','generated'].includes(state)));
 const encoded=JSON.stringify({items:f.report.items,ledger:f.report.ledger,artifacts:f.report.artifacts});assert.equal(encoded.includes(f.root),false);for(const value of f.checked)assert.equal(encoded.includes(value.workspace),false);
 for(const pointer of ['/__proto__','/spec/~2bad','/spec/source_spans/01'])assert.throws(()=>f.core.resolveBusinessAuthoringCoveragePointer(f.report.artifacts['lineage/models/'+f.models[0].model_id+'.json'],pointer));
});
test('original disposal and byte drift invalidate coverage rather than recapturing a new denominator',async t=>{
 const first=await fixture(t);first.A.disposePreparedBusinessAuthoringApplication(first.checked[0]);assert.throws(()=>first.core.assertBusinessAuthoringCoverageCurrent(first.report));
 const second=await fixture(t),file=path.join(second.root,second.models[0].source);writeFileSync(file,readFileSync(file,'utf8')+'\n# drift\n');assert.throws(()=>second.core.assertBusinessAuthoringObligationInventoryCurrent(second.inventories[0]));assert.throws(()=>second.core.assertBusinessAuthoringCoverageCurrent(second.report));
});
