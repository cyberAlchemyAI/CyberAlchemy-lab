import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,readdirSync,renameSync,rmSync,statSync,symlinkSync,writeFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import * as core from '../../../../../../../craft/projects/domainspec-v2/impl/cli/src/profile-engine/index.js';
import {prepareBusinessSpecFile,disposeResolvedBusinessSpec} from '../src/business-authoring-resolve.js';
import {lowerBusinessFormalSemantics} from '../src/business-authoring-semantics.js';
import {lowerBusinessBehavior} from '../src/business-authoring-behavior.js';
import {prepareBusinessRecipeSelection} from '../src/business-authoring-profile-selection.js';
import {previewBusinessSemantics,materializeAcceptedBusinessApplication,assertMaterializedBusinessApplicationCurrent} from '../src/business-authoring-carriers.js';
import {prepareBusinessReview,recordBusinessReviewDecision,requireAcceptedBusinessReviewDecision} from '../src/business-authoring-review.js';
import {assertInsertedBusinessRequestMappingsCurrent} from '../src/business-authoring-request.js';

// All acceptance in this suite is an explicit request recorded in a new owned
// temporary fixture file. Open questions: contracts/business-materialization-api.md.
const repo=path.resolve(import.meta.dirname,'../../../../../../..'),cli=path.join(repo,'craft/projects/domainspec-v2/impl/cli');
const plan=path.join(repo,'research/craft-alchlang-user-readiness-2026-10-12/business-authoring-design-2026-10-14/implementation-plan');
const reference=readFileSync(path.join(plan,'contracts/reference-business.alch'),'utf8');
const canonical=(value:unknown):string=>Array.isArray(value)?'['+value.map(canonical).join(',')+']':value!==null&&typeof value==='object'?'{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+canonical((value as Record<string,unknown>)[key])).join(',')+'}':JSON.stringify(value);
const hash=(value:string)=>createHash('sha256').update(value).digest('hex'),plain=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
function fixture(t:{after(fn:()=>void):void},text=reference,variant='node-http-entry-local-v2'){
 const root=mkdtempSync(path.join(os.tmpdir(),'business-materialization-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 cpSync(path.join(cli,'profiles',variant),path.join(root,'profile'),{recursive:true});
 const profile=JSON.parse(readFileSync(path.join(root,'profile/profile.json'),'utf8'));
 const application=profile.rules.find((rule:any)=>rule.op==='emit'&&rule.role==='application-operation'),limits=application.fields.technical.literal;
 Object.assign(profile,{schema_version:'craft.profile-package/v3-candidate',id:variant.replace(/v2$/,'v3'),engine:'craft.profile-engine/v3-candidate',authoring:{contract:core.BUSINESS_AUTHORING_CONTRACT,input_schema:'alchlang.business-spec/v1-candidate',recipe_ref:core.BUSINESS_AUTHORING_RECIPE,logic_profile:core.BUSINESS_AUTHORING_LOGIC,target:'node-typescript',effects:'none',wire:{schema_version:'craft.operation-json-post/v1-candidate',method:'POST',body:'whole-input',route_prefix:application.fields.route.concat[0].literal,request_bytes:limits.request_bytes,timeout_ms:limits.timeout_ms}}});
 writeFileSync(path.join(root,'profile/profile.json'),JSON.stringify(profile));writeFileSync(path.join(root,'business.alch'),text);
 const business=prepareBusinessSpecFile(root,'business.alch'),behavior=lowerBusinessBehavior(lowerBusinessFormalSemantics(business));
 const project={schema_version:'craft.business-authoring-project/v1-candidate',id:'materialization-fixture',models:[{id:behavior.data.model_id,source:'business.alch'}],profiles:[{id:profile.id,version:profile.version,path:'profile'}],decisions:[]};
 writeFileSync(path.join(root,'project.json'),JSON.stringify(project));
 const snapshot=core.loadBusinessAuthoringProject(path.join(root,'project.json'),{engine:['business-authoring-recipes.ts','business-authoring-request.ts'].map(key=>({key,path:path.join(cli,'src/profile-engine',key)})),tools:['business-authoring-carriers.ts'].map(key=>({key,path:path.join(import.meta.dirname,'../src',key)}))});
 const prepared=prepareBusinessRecipeSelection(snapshot,[behavior],core),preview=previewBusinessSemantics(prepared,behavior.data.model_id),review=prepareBusinessReview(preview,core),requests=core.prepareBusinessAuthoringRequests(prepared.selection);
 const decisionFile=path.join(root,'explicit-fixture-decision.json'),record=(outcome:'accepted'|'declined'='accepted')=>recordBusinessReviewDecision(review,{decision_id:'fixture-explicit-materialization',owner:preview.review.model_identity.owner,outcome,reviewed_digest:review.review.subject.digest},decisionFile,core);
 const accept=()=>requireAcceptedBusinessReviewDecision(review,record(),core);
 return {root,business,prepared,preview,review,requests,decisionFile,record,accept,materialize:()=>materializeAcceptedBusinessApplication(accept(),requests,core)};
}

test('real recorded acceptance produces the unchanged accepted legacy carrier and actual Mapping syntax',t=>{
 const f=fixture(t),accepted=f.accept(),before=readFileSync(f.decisionFile),sourceBefore=readFileSync(path.join(f.root,'business.alch')),value=materializeAcceptedBusinessApplication(accepted,f.requests,core);
 assertMaterializedBusinessApplicationCurrent(value);assertInsertedBusinessRequestMappingsCurrent(value.inserted);
 assert.equal(value.accepted,accepted);assert.equal(value.requests,f.requests);assert.equal(value.inserted.prepared,f.prepared);assert.equal(value.inserted.preparation,f.requests);
 assert.equal(value.source_sha256,hash(value.compatibility.source));assert.equal(value.inserted.source_sha256,hash(value.application_source));assert.equal(value.application_source.split('\n').filter(line=>line==='profile application-v1').length,1);
 assert.equal(value.compatibility.source.includes('profile application-v1'),false);assert.match(value.compatibility.source,/mapping CraftRequest_dispatching_delivery_acknowledgement:/);
 assert.equal(value.semantics_text,JSON.stringify(value.compatibility.semantics,null,2)+'\n');assert.equal(value.semantics_sha256,hash(value.semantics_text));
 const semantics=value.compatibility.semantics,claim=semantics.claim_meanings.DeliveryReady!;
 assert.equal(canonical(core.validateBusinessApplication(semantics)),canonical(semantics));assert.equal(semantics.schema_version,'craft.business-application/v1-candidate');
 assert.equal(claim.business_meaning.status,'accepted');assert.equal(claim.owner_acceptance.decision_id,'fixture-explicit-materialization');assert.equal(claim.owner_acceptance.owner,accepted.decision.capture.decision.owner);
 assert.equal(claim.owner_acceptance.subject.digest,hash(canonical(claim.business_meaning)));assert.deepEqual(plain(claim.owner_acceptance.subject),plain(f.preview.legacy_meaning_subjects[0]));
 assert.deepEqual(plain(claim.business_meaning),{...plain(f.preview.projections.meaning_drafts.DeliveryReady!),status:'accepted'});
 assert.deepEqual(claim.definition_refs,accepted.accepted.definition_closure.definition_ids);assert.equal(claim.definitions[0]!.status,'accepted');
 assert.deepEqual(Object.keys(semantics.declarations.Delivery!).sort(),['meaning','ontology','properties']);
 for(const mapping of f.requests.models[0]!.mappings)assert.deepEqual(semantics.declarations[mapping.mapping_id],mapping.declaration_binding);
 assert.deepEqual(semantics.operation_behaviors,f.preview.projections.operation_behaviors);assert.deepEqual(semantics.rule_meanings,f.preview.projections.rule_meanings);
 assert.equal(Object.hasOwn(value,'graph'),false);assert.equal(Object.hasOwn(value,'plan'),false);assert.equal(value.authority_effect,'none');
 assert.deepEqual(readFileSync(f.decisionFile),before);assert.deepEqual(readFileSync(path.join(f.root,'business.alch')),sourceBefore);assert.equal(statSync(f.decisionFile).mode&0o777,0o600);
 assert.deepEqual(readdirSync(f.root).sort(),['business.alch','explicit-fixture-decision.json','profile','project.json']);
});
test('both independent business domains materialize their actual differing formal and runtime meanings',t=>{
 for(const [domain,field] of [['delivery-acknowledgement','verified'],['publication-consent','consented']]){
  const source=readFileSync(new URL('./fixtures/business-authoring/'+domain+'/business.alch',import.meta.url),'utf8'),f=fixture(t,source),value=f.materialize(),claim=value.compatibility.semantics.claim_meanings.Ready!;
  assert.equal(claim.business_meaning.status,'accepted');assert.equal(Object.values(value.compatibility.semantics.rule_meanings.CanProcess!.predicates)[0],field);
  assert.match(claim.definitions[0]!.formal.expression,new RegExp('item\\.'+field+' = true'));
  assert.deepEqual(claim.business_meaning.examples,f.business.data.requirements[0]!.examples);assert.deepEqual(claim.business_meaning.boundaries,f.business.data.requirements[0]!.boundaries);
 }
});
test('unused reviewed definitions remain outside every accepted legacy definition closure',t=>{
 const definition=reference.slice(reference.indexOf('definition DeliveryEligibility:'),reference.indexOf('formal-claim DeliveryReady')).replace('definition DeliveryEligibility:','definition UnusedDefinition:');
 const f=fixture(t,reference+'\n'+definition),value=f.materialize(),claim=value.compatibility.semantics.claim_meanings.DeliveryReady!;
 assert.equal(f.preview.review.definitions.length,2);assert.equal(claim.definitions.length,1);assert.equal(claim.definitions[0]!.definition_id,'DEF-DISPATCHING-DELIVERY-ELIGIBILITY');
 assert.equal(value.semantics_text.includes('UnusedDefinition'),false);assert.ok(f.preview.review.definitions.every(definition=>!Object.hasOwn(definition,'status')));
});
test('shared definitions are copied only to each claim exact closure while compound propositions remain exact',t=>{
 const other=reference.slice(reference.indexOf('formal-claim DeliveryReady'),reference.indexOf('rule CanConfirm:')).replace('formal-claim DeliveryReady','formal-claim OtherClaim');
 const f=fixture(t,(reference+'\n'+other).replaceAll('proposition Permitted(current)','proposition (Permitted(current) and not not Permitted(current)) implies Permitted(current)')),value=f.materialize();
 for(const claim of Object.values(value.compatibility.semantics.claim_meanings)){assert.equal(claim.definitions.length,1);assert.deepEqual(claim.definition_refs,['DEF-DISPATCHING-DELIVERY-ELIGIBILITY']);assert.equal(claim.definitions[0]!.status,'accepted');}
 assert.equal(f.preview.review.definitions.length,1);assert.equal(value.inserted.parsed.formal_claims.length,2);assert.equal(value.inserted.parsed.formal_claims[0]!.proposition_source,f.preview.review.claims[0]!.proposition);assert.match(value.inserted.parsed.formal_claims[0]!.proposition_source,/and not not/);
});
test('canonical materialization is deterministic across source ordering/comments and technical profiles',t=>{
 const [header,...blocks]=reference.trimEnd().split('\n\n'),first=fixture(t),second=fixture(t,'# irrelevant byte provenance\n'+[header,...blocks.reverse()].join('\n\n')+'\n'),third=fixture(t,reference,'node-http-shared-ports-v2');
 const values=[first.materialize(),second.materialize(),third.materialize()];
 for(const value of values){assert.equal(value.compatibility.source,values[0]!.compatibility.source);assert.deepEqual(value.compatibility.semantics,values[0]!.compatibility.semantics);assert.equal(value.semantics_sha256,values[0]!.semantics_sha256);}
 assert.notEqual(values[0]!.ledger.business_sha256,undefined);assert.notEqual(values[0]!.ledger.lock_sha256,values[2]!.ledger.lock_sha256);
});
test('materialization ledger resolves every generated leaf with current original or exact intermediate origins',t=>{
 const f=fixture(t),value=f.materialize(),targets=new Set<string>(),resolve=(root:unknown,pointer:string):unknown=>pointer.split('/').slice(1).reduce<unknown>((at,key)=>(at as Record<string,unknown>)[key.replaceAll('~1','/').replaceAll('~0','~')],root);
 core.validateBusinessAuthoringContract('ledger',value.ledger);
 for(const entry of value.ledger.entries){assert.equal(entry.target.artifact,'materialization.json');assert.notEqual(resolve(value,entry.target.pointer),undefined);assert.ok(!targets.has(entry.target.pointer));targets.add(entry.target.pointer);
  for(const origin of entry.origins){
   if(origin.kind==='owner-decision'){assert.equal(origin.source,f.decisionFile);assert.equal(origin.sha256,value.accepted.decision.capture.file.sha256);assert.notEqual(resolve(value.accepted.decision.capture.decision,origin.selector),undefined);}
   if(origin.kind==='semantic-adapter'&&['preview.json','materialization.json','business-authoring-request-preparation.json'].includes(origin.source)){
    const root=origin.source==='preview.json'?f.preview:origin.source==='materialization.json'?value:f.requests;assert.equal(origin.sha256,hash(canonical(resolve(root,origin.selector))));
   }
   if(origin.kind==='business')assert.ok(f.business.data.source_spans.some(span=>span.source===origin.source&&span.selector===origin.selector&&span.source_sha256===origin.sha256));
  }
 }
 const walk=(node:unknown,prefix:string):void=>{if(node&&typeof node==='object'&&Object.keys(node).length){for(const [key,child] of Object.entries(node))walk(child,prefix+'/'+key.replaceAll('~','~0').replaceAll('/','~1'));}else assert.ok(targets.has(prefix),prefix);};
 for(const key of ['model_id','compatibility','application_source','source_sha256','semantics_text','semantics_sha256','authority_effect'] as const)walk(value[key],'/'+key);
 assert.deepEqual(new Set(value.ledger.entries.flatMap(entry=>entry.origins.map(origin=>origin.kind))),new Set(['business','profile','owner-decision','semantic-adapter']));
});
test('copied accepted/materialized/request inputs, declines and foreign original selections cannot cross the owner',t=>{
 const f=fixture(t),accepted=f.accept(),value=materializeAcceptedBusinessApplication(accepted,f.requests,core);
 for(const forged of [plain(value),{...value},new Proxy(value,{})])assert.throws(()=>assertMaterializedBusinessApplicationCurrent(forged));
 for(const forged of [plain(accepted),{...accepted},new Proxy(accepted,{})])assert.throws(()=>materializeAcceptedBusinessApplication(forged,f.requests,core));
 assert.throws(()=>materializeAcceptedBusinessApplication(accepted,{...f.requests},core));
 const other=fixture(t);assert.throws(()=>materializeAcceptedBusinessApplication(accepted,other.requests,core));
 const declined=fixture(t);assert.throws(()=>requireAcceptedBusinessReviewDecision(declined.review,declined.record('declined'),core));
 assert.throws(()=>{(value.compatibility.semantics.claim_meanings.DeliveryReady!.definitions as unknown[]).push({});},TypeError);
});
test('business disposal, source/profile/decision drift and same-byte decision replacement revoke retained materializations',t=>{
 for(const change of ['dispose','source','profile','decision','replace']){
  const f=fixture(t),value=f.materialize();
  if(change==='dispose')disposeResolvedBusinessSpec(f.business);
  else if(change==='replace'){const replacement=path.join(f.root,'replacement.json');writeFileSync(replacement,readFileSync(f.decisionFile));renameSync(replacement,f.decisionFile);}
  else{const target=change==='source'?path.join(f.root,'business.alch'):change==='profile'?path.join(f.root,'profile/profile.json'):f.decisionFile;writeFileSync(target,readFileSync(target,'utf8')+'\n');}
  assert.throws(()=>assertMaterializedBusinessApplicationCurrent(value),change);assert.throws(()=>materializeAcceptedBusinessApplication(value.accepted,value.requests,core),change);
 }
});
test('new materialization module custody rejects isolated same-byte file, symlink and ancestor replacements',async t=>{
 const f=fixture(t),accepted=f.accept(),originalDirectory=path.join(import.meta.dirname,'../src'),moduleName='business-authoring-carriers.ts';
 for(const replacement of ['same-byte','symlink','ancestor']){
  const isolated=mkdtempSync(path.join(os.tmpdir(),'business-materializer-module-'));t.after(()=>rmSync(isolated,{recursive:true,force:true}));
  writeFileSync(path.join(isolated,'package.json'),JSON.stringify({type:'module'}));
  const directory=path.join(isolated,'src');mkdirSync(directory);
  // Real original module URLs preserve the genuine owners under tsx; sibling
  // symlinks can produce distinct loader identities and therefore distinct WeakMaps.
  const originalText=readFileSync(path.join(originalDirectory,moduleName),'utf8');
  const isolatedText=originalText.replace(/from '(\.\/[^']+)\.js'/g,(_match,relative:string)=>`from '${pathToFileURL(path.join(originalDirectory,relative+'.ts')).href}'`);
  writeFileSync(path.join(directory,moduleName),isolatedText);
  const modulePath=path.join(directory,moduleName),producer=await import(pathToFileURL(modulePath).href) as typeof import('../src/business-authoring-carriers.js');
  const value=producer.materializeAcceptedBusinessApplication(accepted,f.requests,core);producer.assertMaterializedBusinessApplicationCurrent(value);
  if(replacement==='ancestor'){
   renameSync(directory,path.join(isolated,'retired'));mkdirSync(directory);cpSync(path.join(isolated,'retired',moduleName),modulePath);
  }else{
   renameSync(modulePath,path.join(directory,'retired.ts'));
   if(replacement==='symlink')symlinkSync(path.join(directory,'retired.ts'),modulePath);
   else cpSync(path.join(directory,'retired.ts'),modulePath);
  }
  assert.throws(()=>producer.assertMaterializedBusinessApplicationCurrent(value),/BUSINESS_MATERIALIZATION/);
  assert.throws(()=>producer.materializeAcceptedBusinessApplication(accepted,f.requests,core),/BUSINESS_MATERIALIZATION/);
 }
});
