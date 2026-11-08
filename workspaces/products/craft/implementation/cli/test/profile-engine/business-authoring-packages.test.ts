import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,lstatSync,mkdirSync,mkdtempSync,readFileSync,readdirSync,rmSync,writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {validateProfilePackageV3} from '../../src/profile-engine/contracts-v3.js';
import {assertBusinessAuthoringRequestsCurrent} from '../../src/profile-engine/business-authoring-request.js';
import {evaluateProfile} from '../../src/profile-engine/evaluate.js';
import {prepareBusinessSpecFile} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-resolve.js';
import {lowerBusinessFormalSemantics} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-semantics.js';
import {lowerBusinessBehavior} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-behavior.js';
import {prepareBusinessRecipeSelection} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-profile-selection.js';
import * as core from '../../src/profile-engine/index.js';
import {loadDomainSpecCompiler} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/domainspec-cli.js';
import {previewBusinessSemantics} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-carriers.js';
import {prepareBusinessReview,recordBusinessReviewDecision,requireAcceptedBusinessReviewDecision} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-review.js';
import {prepareBusinessAuthoringApplication as prepareChecked,assertPreparedBusinessAuthoringApplicationCurrent,disposePreparedBusinessAuthoringApplication} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-prepare.js';
// Genuine source normalization and Core recipe/request owners; no accepted input.
// Open questions: B09.2/B10 native+installed matrix, docs/BUSINESS-AUTHORING.md.
const cli=path.resolve(import.meta.dirname,'../..'),alch=path.resolve(cli,'../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation');
const ids=['node-http-entry-local-v3','node-http-shared-ports-v3','node-http-api-prefix-v3'];
const json=(file:string)=>JSON.parse(readFileSync(file,'utf8')),copy=<T>(v:T):T=>JSON.parse(JSON.stringify(v));
const hash=(v:string|Buffer)=>createHash('sha256').update(v).digest('hex');
function files(root:string,prefix=''):Record<string,string>{const out:Record<string,string>={};for(const e of readdirSync(path.join(root,prefix),{withFileTypes:true})){const relative=prefix+e.name;if(e.isDirectory())Object.assign(out,files(root,relative+'/'));else{assert.ok(e.isFile());out[relative]=hash(readFileSync(path.join(root,relative)));}}return out;}
function fixture(t:{after(fn:()=>void):void},id=ids[0]!,mutate?:(profile:any)=>void,engine:typeof core=core){
 const root=mkdtempSync(path.join(os.tmpdir(),'business-successor-package-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(cli,'profiles',id),path.join(root,'profile'),{recursive:true});
 const profileFile=path.join(root,'profile/profile.json'),profile=json(profileFile);if(mutate){mutate(profile);writeFileSync(profileFile,JSON.stringify(profile));}
 const models=[{id:'delivery_ack',source:'delivery-acknowledgement/business.alch'},{id:'publication_consent',source:'publication-consent/business.alch'}];for(const m of models){const file=path.join(root,m.source);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,readFileSync(path.join(cli,'test/profile-engine/fixtures/business-authoring',m.source)));}
 const project={schema_version:'craft.business-authoring-project/v1-candidate',id:'successor-package-test',models,profiles:[{id:profile.id,version:'1.0.0',path:'profile'}],decisions:[]};const projectFile=path.join(root,'project.json');writeFileSync(projectFile,JSON.stringify(project));
 const identity={engine:['loader-v3','business-authoring-recipes','business-authoring-request','business-authoring-input','business-review','business-decision'].map(name=>{const key=name+(engine===core?'.ts':'.js');return {key,path:path.join(cli,engine===core?'src/profile-engine':'dist/profile-engine',key)};}),tools:['business-authoring-resolve.ts','business-authoring-semantics.ts','business-authoring-behavior.ts','business-authoring-profile-selection.ts'].map(key=>({key,path:path.join(alch,'src',key)}))};
 const prepare=()=>{const snapshot=engine.loadBusinessAuthoringProject(projectFile,identity),behaviors=models.map(m=>lowerBusinessBehavior(lowerBusinessFormalSemantics(prepareBusinessSpecFile(root,m.source)))),prepared=prepareBusinessRecipeSelection(snapshot,behaviors,engine),requests=engine.prepareBusinessAuthoringRequests(prepared.selection);return {snapshot,behaviors,prepared,requests};};return {root,profile,profileFile,project,projectFile,prepare};
}
test('new 1.0.0 manifests preserve each corresponding v2 asset closure and technical rules',()=>{
 for(const id of ids){const directory=path.join(cli,'profiles',id),previous=path.join(cli,'profiles',id.replace(/v3$/,'v2')),raw=json(path.join(directory,'profile.json')),pkg=validateProfilePackageV3(raw),old=json(path.join(previous,'profile.json'));
  assert.equal(pkg.id,id);assert.equal(pkg.version,'1.0.0');assert.equal(pkg.authoring.recipe_ref,'ground-entity-bool-operation/v1-candidate');assert.equal(pkg.authoring.effects,'none');assert.equal(pkg.authoring.logic_profile,'fol-core/1-candidate');assert.equal(pkg.authoring.target,'node-typescript');assert.equal(pkg.authoring.wire.body,'whole-input');assert.equal(pkg.authoring.wire.method,'POST');
  assert.deepEqual(copy(pkg.assets),old.assets);assert.deepEqual(copy(pkg.application_runtime),old.application_runtime);assert.deepEqual(copy(pkg.rules),old.rules);assert.deepEqual(copy(pkg.capabilities),old.capabilities);
  for(const asset of pkg.assets){const current=path.join(directory,asset.path),original=path.join(previous,asset.path);assert.ok(lstatSync(current).isFile()&&!lstatSync(current).isSymbolicLink());assert.equal(hash(readFileSync(current)),asset.sha256);assert.deepEqual(readFileSync(current),readFileSync(original));}
  assert.deepEqual(raw.rules.find((r:any)=>r.role==='application-operation').fields.technical.literal,{request_bytes:pkg.authoring.wire.request_bytes,timeout_ms:pkg.authoring.wire.timeout_ms});
 }
});
for(const id of ids)test('actual composed source recipe/request owner selects '+id,t=>{
 const f=fixture(t,id),before=files(f.root),{snapshot,behaviors,prepared,requests}=f.prepare(),prefix=id==='node-http-api-prefix-v3'?'/api/':'/';assertBusinessAuthoringRequestsCurrent(requests);
 assert.equal(prepared.selection.technical.profile_id,id);assert.equal(prepared.selection.technical.profile_version,'1.0.0');assert.equal(prepared.selection.technical.wire.route_prefix,prefix);assert.deepEqual(prepared.selection.models.map(m=>m.model_id),['delivery_ack','publication_consent']);
 assert.deepEqual(requests.request_source.entries.map(e=>e.route.path),[prefix+'confirmDelivery',prefix+'checkPublicationConsent']);assert.ok(requests.request_source.entries.every(e=>e.route.method==='POST'&&e.access.kind==='public'&&e.mapping_arguments.length===1&&e.mapping_arguments[0]!.path.length===0));
 for(const model of requests.models){assert.equal(model.mappings.length,1);const mapping=model.mappings[0]!;assert.equal(mapping.input_parameter,'body');assert.ok(mapping.fields.every(field=>field.path[0]==='body'&&field.path[1]===field.target));for(const type of ['UInt64','String','Bool'])assert.ok(mapping.fields.some(field=>field.type===type));}
 assert.equal(new Set(requests.models.flatMap(m=>m.mappings.map(m=>m.mapping_selector))).size,2);assert.equal(new Set(requests.models.flatMap(m=>m.mappings.map(m=>m.operation_selector))).size,2);assert.ok(behaviors.every(b=>b.data.operations[0]!.effects.length===0));assert.equal(snapshot.project.decisions.length,0);assert.deepEqual(files(f.root),before);
});
test('finite evaluator selects one real shared transport owner and authored prefix routes',t=>{
 const values=ids.map(id=>({id,...fixture(t,id).prepare()}));assert.equal(new Set(values.map(v=>v.prepared.selection.business_sha256)).size,1);
 for(const v of values){const runtime=v.snapshot.packages.find(p=>p.data.schema_version==='craft.profile-package/v3-candidate')!,tables={applications:{fields:{id:'string' as const,source:'string' as const,selector:'string' as const},rows:v.requests.project_intents.map(intent=>({id:intent.id,source:`derived/${intent.application_id}/domain.alch`,selector:intent.operation_ref}))}},evaluation=evaluateProfile(runtime.data,tables),shared=evaluation.emissions.filter(e=>e.role==='shared-http-port'),entries=evaluation.emissions.filter(e=>e.role==='application-operation'),dispatcher=evaluation.emissions.filter(e=>e.role==='http-dispatch');
  assert.equal(entries.length,2);assert.equal(dispatcher.length,1);assert.equal(shared.length,v.id==='node-http-shared-ports-v3'?1:0);assert.equal(runtime.data.application_runtime.transport,v.id==='node-http-shared-ports-v3'?'shared':'entry-local');
  if(shared.length){assert.equal(shared[0]!.fields.artifact_path,'runtime/application-http.mts');assert.deepEqual(copy(shared[0]!.fields.technical),{kind:'application-operation'});assert.equal(runtime.assets[runtime.data.application_runtime.transport_asset]!.sha256,'9a94cef566d9f1062323629233eac5425b1b8ee7d9ed026e7787af96bb67276a');}
  assert.deepEqual(entries.map(e=>e.fields.route),v.requests.request_source.entries.map(e=>e.route.path));assert.equal(dispatcher[0]!.fields.artifact_path,v.id==='node-http-api-prefix-v3'?'api/index.mjs':'app/index.mjs');
 }
});
const mutations:[string,(p:any)=>void][]=[
 ['unsupported semantic recipe',p=>p.authoring.recipe_ref='a-different-business-recipe'],['new effect',p=>p.authoring.effects='persistence'],['different body boundary',p=>p.authoring.wire.body='payload-envelope'],
 ['profile supplied access',p=>p.rules.find((r:any)=>r.role==='application-operation').fields.access={literal:{kind:'protected'}}],
 ['predicate hidden in technical dictionary',p=>p.rules.find((r:any)=>r.role==='application-operation').fields.technical.literal.predicate='always-true'],
 ['rejection override hidden in technical dictionary',p=>p.rules.find((r:any)=>r.role==='application-operation').fields.technical.literal.failure_continuation='replace-failure'],
 ['semantic defaults',p=>p.rules.splice(0,0,{id:'semantic-defaults',op:'defaults',as:'technical-spoof',values:{meaning:'A replaced business meaning'}})],
 ['reserved table clobber',p=>p.rules.splice(0,0,{id:'shadow',op:'defaults',as:'applications',values:{id:'stolen'}})],
 ['substitute selected Operation',p=>p.rules.find((r:any)=>r.role==='application-operation').fields.selector={literal:'AnotherOperation'}],
 ['inconsistent route',p=>p.rules.find((r:any)=>r.role==='application-operation').fields.route={concat:[{literal:'/unexpected/'},{field:['id']}] }],['runtime ownership mismatch',p=>p.application_runtime.transport='shared'],
];
for(const [name,mutate] of mutations)test('successor rejects '+name,t=>{const f=fixture(t,ids[0]!,mutate);assert.throws(()=>f.prepare(),(error:any)=>typeof error?.code==='string'&&/^(BUSINESS_|PROFILE_)/.test(error.code));});
test('retained predecessor digest cannot conceal changed successor asset bytes',t=>{const f=fixture(t),asset=path.join(f.root,'profile/runtime/application-http.mts');writeFileSync(asset,readFileSync(asset,'utf8')+'\n');assert.throws(()=>f.prepare(),(error:any)=>typeof error?.code==='string'&&/ASSET|HASH|DRIFT/.test(error.code));});

for(const id of ids)test('genuine two-model checked application rendering consumes selected '+id+' transport',async t=>{
 const compiler=await loadDomainSpecCompiler(cli),engine=compiler.profileEngine as any;
 assert.equal(typeof engine.prepareBusinessAuthoringApplication,'function','build the public B07.2 owner before this join');
 const f=fixture(t,id,undefined,engine),{prepared,requests}=f.prepare(),before=files(f.root),checked=[];
 for(const model of prepared.selection.models){const preview=previewBusinessSemantics(prepared,model.model_id),review=prepareBusinessReview(preview,engine),decision=recordBusinessReviewDecision(review,{decision_id:'synthetic-package-fixture-'+model.model_id,owner:preview.review.model_identity.owner,outcome:'accepted',reviewed_digest:review.review.subject.digest},path.join(f.root,'synthetic-'+model.model_id+'-decision.json'),engine),accepted=requireAcceptedBusinessReviewDecision(review,decision,engine),value=prepareChecked(accepted,requests,compiler);checked.push(value);t.after(()=>{try{disposePreparedBusinessAuthoringApplication(value);}catch{}rmSync(value.workspace,{recursive:true,force:true});});}
 const result=engine.prepareBusinessAuthoringApplication(checked,assertPreparedBusinessAuthoringApplicationCurrent);engine.assertBusinessAuthoringApplicationCurrent(result);
 const rendered=engine.renderBusinessAuthoringApplication(result);assert.deepEqual(copy(rendered),copy(result.files));
 const components=result.composition.components??result.composition.data?.components;assert.ok(Array.isArray(components));const shared=components.filter((c:any)=>c.role==='shared-http-port'),applications=components.filter((c:any)=>c.role==='application-operation');assert.equal(applications.length,2);assert.equal(shared.length,id==='node-http-shared-ports-v3'?1:0);
 for(const publicName of ['confirmDelivery','checkPublicationConsent']){const entry=result.files[`applications/${publicName}/src/profile-entry.ts`];assert.equal(typeof entry,'string');if(shared.length){assert.match(entry,/\.\.\/\.\.\/\.\.\/runtime\/lib\/application-http\.mjs/);assert.equal(result.files[`applications/${publicName}/src/application-http.mts`],undefined);}else{assert.equal(hash(result.files[`applications/${publicName}/src/application-http.mts`]),'9a94cef566d9f1062323629233eac5425b1b8ee7d9ed026e7787af96bb67276a');assert.match(entry,/application-http\.mjs/);}}
 if(shared.length){assert.equal(hash(result.files['runtime/application-http.mts']),'9a94cef566d9f1062323629233eac5425b1b8ee7d9ed026e7787af96bb67276a');assert.ok(applications.every((c:any)=>c.depends_on.includes(shared[0].id)));}else assert.ok(applications.every((c:any)=>c.depends_on.length===0));
 assert.deepEqual(result.routes.map((route:any)=>route.route),id==='node-http-api-prefix-v3'?['/api/confirmDelivery','/api/checkPublicationConsent']:['/confirmDelivery','/checkPublicationConsent']);assert.ok(result.routes.every((route:any)=>route.method==='POST'));assert.equal(typeof result.files[id==='node-http-api-prefix-v3'?'api/index.mjs':'app/index.mjs'],'string');
 const after=files(f.root);for(const [file,sha] of Object.entries(before))assert.equal(after[file],sha,'original source/profile/project unchanged');assert.equal(Object.keys(after).length,Object.keys(before).length+2,'only explicit synthetic recorder files added');
});
