import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {BusinessSourceRejected} from '../src/business-authoring-model.js';
import {prepareBusinessSpecFile,disposeResolvedBusinessSpec} from '../src/business-authoring-resolve.js';
import {lowerBusinessFormalSemantics} from '../src/business-authoring-semantics.js';
import {lowerBusinessBehavior} from '../src/business-authoring-behavior.js';
import {prepareBusinessRecipeSelection} from '../src/business-authoring-profile-selection.js';
import {previewBusinessSemantics,assertBusinessSemanticPreviewCurrent,type DetailedBusinessSemanticPreview} from '../src/business-authoring-carriers.js';
import {loadBusinessAuthoringProject} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/src/profile-engine/loader-v3.js';
import {selectBusinessAuthoringRecipe,assertBusinessRecipeSelectionCurrent} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/src/profile-engine/business-authoring-recipes.js';
import {validateBusinessAuthoringContract} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/src/profile-engine/business-authoring-contracts.js';
const repo=path.resolve(import.meta.dirname,'../../../../../../..'),core=path.join(repo,'craft/projects/domainspec-v2/impl/cli');
const plan=path.join(repo,'research/craft-alchlang-user-readiness-2026-10-12/business-authoring-design-2026-10-14/implementation-plan');
const reference=readFileSync(path.join(plan,'contracts/reference-business.alch'),'utf8');
const engine={selectBusinessAuthoringRecipe,assertBusinessRecipeSelectionCurrent};
const canonical=(value:unknown):string=>Array.isArray(value)?'['+value.map(canonical).join(',')+']':value!==null&&typeof value==='object'?'{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+canonical((value as Record<string,unknown>)[key])).join(',')+'}':JSON.stringify(value);
const digest=(value:unknown)=>createHash('sha256').update(canonical(value)).digest('hex');
const plain=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
function fixture(t:{after(fn:()=>void):void},text=reference,variant='node-http-entry-local-v2'){
 const root=mkdtempSync(path.join(os.tmpdir(),'business-preview-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 cpSync(path.join(core,'profiles',variant),path.join(root,'profile'),{recursive:true});
 const profile=JSON.parse(readFileSync(path.join(root,'profile/profile.json'),'utf8'));
 const wire=variant==='node-http-api-prefix-v2'?{route_prefix:'/api/',request_bytes:8192,timeout_ms:1500}:{route_prefix:'/',request_bytes:16384,timeout_ms:2000};
 Object.assign(profile,{schema_version:'craft.profile-package/v3-candidate',id:variant.replace(/v2$/,'v3'),engine:'craft.profile-engine/v3-candidate',authoring:{contract:'craft.business-authoring-contracts/1-candidate',input_schema:'alchlang.business-spec/v1-candidate',recipe_ref:'ground-entity-bool-operation/v1-candidate',logic_profile:'fol-core/1-candidate',target:'node-typescript',effects:'none',wire:{schema_version:'craft.operation-json-post/v1-candidate',method:'POST',body:'whole-input',...wire}}});
 writeFileSync(path.join(root,'profile/profile.json'),JSON.stringify(profile));writeFileSync(path.join(root,'business.alch'),text);
 const business=prepareBusinessSpecFile(root,'business.alch'),behavior=lowerBusinessBehavior(lowerBusinessFormalSemantics(business));
 const project={schema_version:'craft.business-authoring-project/v1-candidate',id:'preview-fixture',models:[{id:behavior.data.model_id,source:'business.alch'}],profiles:[{id:profile.id,version:profile.version,path:'profile'}],decisions:[]};
 writeFileSync(path.join(root,'project.json'),JSON.stringify(project));
 const snapshot=loadBusinessAuthoringProject(path.join(root,'project.json'),{engine:[{key:'recipe.ts',path:path.join(core,'src/profile-engine/business-authoring-recipes.ts')}],tools:[{key:'preview.ts',path:path.join(import.meta.dirname,'../src/business-authoring-carriers.ts')}]});
 const prepared=prepareBusinessRecipeSelection(snapshot,[behavior],engine);
 return {root,business,behavior,snapshot,prepared,preview:()=>previewBusinessSemantics(prepared,behavior.data.model_id)};
}

test('preview deterministically projects complete status-free metadata and the exact prospective legacy subject',t=>{
 const f=fixture(t),value=f.preview();assertBusinessSemanticPreviewCurrent(value);
 assert.equal(value.business,f.business);assert.equal(value.prepared,f.prepared);assert.equal(value.model_id,'dispatching');
 assert.deepEqual(plain(value.projections.declarations.Delivery),{ontology:'BUSINESS-DISPATCHING-DELIVERY',meaning:'One received delivery acknowledgement.',properties:{id:{ontology:'BUSINESS-DISPATCHING-DELIVERY#id',meaning:'Delivery identity.'},label:{ontology:'BUSINESS-DISPATCHING-DELIVERY#label',meaning:'Label retained in the acknowledgement.'},verified:{ontology:'BUSINESS-DISPATCHING-DELIVERY#verified',meaning:'Caller supplied eligibility flag.'}}});
 assert.deepEqual(Object.keys(value.projections.declarations.Delivery!).sort(),['meaning','ontology','properties']);
 const draft=value.projections.meaning_drafts.DeliveryReady!;
 assert.deepEqual(draft.inputs,['Rule CanConfirm input delivery: Delivery {id: UInt64, label: String, verified: Bool}.','Operation ConfirmDelivery input request: Delivery {id: UInt64, label: String, verified: Bool}.']);
 assert.deepEqual(draft.outcomes,['Operation ConfirmDelivery returns request: Delivery; on-rejection return-confirmation-error; effects none.']);
 assert.equal(draft.meaning_id,'Meaning:dispatching:delivery-ready');assert.equal(value.projections.claim_drafts.DeliveryReady!.claim_id,'FormalClaim:dispatching:delivery-ready');
 assert.equal(value.projections.claim_drafts.DeliveryReady!.meaning_ref,draft.meaning_id);assert.deepEqual(value.projections.claim_drafts.DeliveryReady!.definition_refs,['DEF-DISPATCHING-DELIVERY-ELIGIBILITY']);
 assert.equal(value.legacy_meaning_subjects[0]!.digest,'7b9fd62db182c23223ab2c63d6b99fbe514c85a927b0fd4d5a1bcded6d29dc23');
 assert.equal(value.legacy_meaning_subjects[0]!.digest,digest({...draft,status:'accepted'}));
 assert.ok(!Object.hasOwn(draft,'status'));assert.ok(!Object.hasOwn(value.projections,'owner_acceptance'));assert.ok(!Object.hasOwn(value.projections,'schema_version'));
 assert.equal(value.projections.definitions[0]!.formal,f.behavior.formal.data.definitions[0]!.formal);
 assert.equal(value.projections.definitions[0]!.plain_language,f.business.data.definitions[0]!.meaning);
 assert.equal(value.projections.definitions[0]!.source_concept_refs[0],'business:dispatching:definition:delivery-eligibility');
 assert.deepEqual(value.projections.definitions[0]!.business_fact_refs,['#/inputs']);assert.deepEqual(value.projections.definitions[0]!.interpretation_refs,['#/rule']);
 assert.deepEqual(value.projections.definitions[0]!.forbidden_collapses,f.business.data.requirements[0]!.boundaries);
 assert.equal(canonical(value.review),canonical(validateBusinessAuthoringContract('review',value.review)));
 validateBusinessAuthoringContract('ledger',value.ledger);
 assert.equal(digest(value.review),digest(f.preview().review));assert.equal(value.preview_sha256,f.preview().preview_sha256);
});
test('each independent source keeps authored scenarios and its independently pinned legacy digest',t=>{
 for(const [domain,expected] of [['delivery-acknowledgement','f46394dcf54215cf89f9ea2d9456d99e9b5c9eb03ab4249c787b516240537074'],['publication-consent','19cec833ae6f831745f64b2bd3559422209b2b2df64ca627859e1c6b134bb68b']]){
  const source=readFileSync(new URL('./fixtures/business-authoring/'+domain+'/business.alch',import.meta.url),'utf8'),f=fixture(t,source),value=f.preview(),draft=value.projections.meaning_drafts.Ready!;
  assert.equal(value.legacy_meaning_subjects[0]!.digest,expected);assert.deepEqual(draft.examples,f.business.data.requirements[0]!.examples);assert.deepEqual(draft.counterexamples,f.business.data.requirements[0]!.counterexamples);
  assert.deepEqual(value.projections.operation_behaviors.Process,{input_name:'request',guards:[{rule:'CanProcess',arguments:{item:{root:'request',path:[]}}}],result:{root:'request',path:[]}});
  validateBusinessAuthoringContract('review',value.review);
 }
});
test('technical architecture/profile changes preserve the exact business review and legacy subjects',t=>{
 const values=['node-http-entry-local-v2','node-http-shared-ports-v2','node-http-api-prefix-v2'].map(profile=>fixture(t,reference,profile).preview());
 for(const value of values){assert.deepEqual(value.review,values[0]!.review);assert.deepEqual(value.legacy_meaning_subjects,values[0]!.legacy_meaning_subjects);assert.deepEqual(value.projections,values[0]!.projections);}
 assert.notEqual(values[0]!.ledger.lock_sha256,values[1]!.ledger.lock_sha256);assert.notEqual(values[0]!.preview_sha256,values[2]!.preview_sha256);
});
test('original paths/comments affect byte provenance while business subject and structural field order remain stable',t=>{
 const original=fixture(t),commented=fixture(t,'# source commentary\r\n'+reference.replaceAll('\n','\r\n'));
 const first=original.preview(),second=commented.preview();assert.deepEqual(first.review,second.review);assert.deepEqual(first.projections,second.projections);assert.notEqual(first.preview_sha256,second.preview_sha256);
 const [header,...declarations]=reference.trimEnd().split('\n\n');const reordered=fixture(t,[header,...declarations.reverse()].join('\n\n')+'\n').preview();assert.deepEqual(reordered.review,first.review);
});
test('legacy request-root adaptation retains the exact authored input name and rejection metadata',t=>{
 const value=fixture(t,reference.replace('input request Delivery','input payload Delivery').replace('requires CanConfirm(delivery: request)','requires CanConfirm(delivery: payload)').replace('returns request','returns payload')).preview();
 assert.equal(value.projections.operation_behaviors.ConfirmDelivery!.input_name,'payload');assert.equal(value.projections.operation_behaviors.ConfirmDelivery!.result.root,'request');
 assert.equal(value.projections.operation_behaviors.ConfirmDelivery!.guards[0]!.arguments.delivery!.root,'request');
 assert.equal(value.review.behaviors[0]!.input.name,'payload');assert.equal(value.review.behaviors[0]!.result.root,'payload');assert.equal(value.projections.declarations.ConfirmDelivery!.failure_continuation,'return-confirmation-error');
});
test('shared definitions appear once and per-claim closures come only from explicit predicate references',t=>{
 const claim=reference.slice(reference.indexOf('formal-claim DeliveryReady'),reference.indexOf('rule CanConfirm:')).replace('formal-claim DeliveryReady','formal-claim OtherClaim');
 const value=fixture(t,reference+'\n'+claim).preview();assert.equal(value.projections.definitions.length,1);assert.equal(value.review.definitions.length,1);assert.equal(Object.keys(value.projections.claim_drafts).length,2);
 assert.deepEqual(value.projections.claim_drafts.OtherClaim!.definition_refs,value.projections.claim_drafts.DeliveryReady!.definition_refs);assert.deepEqual(value.projections.meaning_drafts.OtherClaim!.inputs,[]);assert.deepEqual(value.projections.meaning_drafts.OtherClaim!.outcomes,[]);
 assert.equal(value.review.definitions[0]!.formal.expression,'DeliveryReady::Permitted(delivery: DeliveryValue) iff (delivery.verified = true); OtherClaim::Permitted(delivery: DeliveryValue) iff (delivery.verified = true)');
});
test('ledger targets every actual projection/review leaf with exact source and honest adapter/profile origins',t=>{
 const f=fixture(t),value=f.preview(),targets=new Set<string>();
 const resolve=(pointer:string):unknown=>pointer.split('/').slice(1).reduce<unknown>((at,key)=>(at as Record<string,unknown>)[key.replaceAll('~1','/').replaceAll('~0','~')],value);
 for(const entry of value.ledger.entries){assert.equal(entry.target.artifact,'preview.json');assert.ok(entry.target.pointer.startsWith('/review/')||entry.target.pointer.startsWith('/projections/'));assert.notEqual(resolve(entry.target.pointer),undefined);assert.ok(!targets.has(entry.target.pointer));targets.add(entry.target.pointer);
  for(const origin of entry.origins){assert.match(origin.sha256,/^[a-f0-9]{64}$/);if(origin.kind==='business')assert.ok(f.business.data.source_spans.some(span=>span.selector===origin.selector&&span.source===origin.source&&span.source_sha256===origin.sha256));if(origin.kind==='semantic-adapter'&&origin.source==='preview.json'){const intermediate=resolve(origin.selector);assert.notEqual(intermediate,undefined);assert.equal(origin.sha256,digest(intermediate));}if(origin.kind==='profile'){assert.equal(origin.source,'profile:'+f.prepared.selection.technical.profile_id);assert.equal(origin.sha256,f.prepared.selection.technical.manifest_sha256);assert.ok(entry.target.pointer.startsWith('/projections/required_guarantees/'));}}
 }
 const leaves=(node:unknown,prefix:string)=>{if(node&&typeof node==='object'&&Object.keys(node).length){for(const [key,child] of Object.entries(node))leaves(child,prefix+'/'+key.replaceAll('~','~0').replaceAll('/','~1'));}else assert.ok(targets.has(prefix),prefix);};leaves(value.review,'/review');leaves(value.projections,'/projections');
 const forbidden=new Set(['status','owner_acceptance','wire','ledger','source_spans','obligations','lock_sha256','profile_id','technical','mapping_arguments']);
 const businessOnly=(node:unknown)=>{if(node&&typeof node==='object')for(const [key,child] of Object.entries(node)){assert.ok(!forbidden.has(key),key);businessOnly(child);}};businessOnly(value.review);
});
test('preview registration retains genuine original owners and rejects cloned/currentness/disposal drift',t=>{
 const f=fixture(t),value=f.preview();for(const forged of [plain(value),{...value},Object.create(value),new Proxy(value,{})])assert.throws(()=>assertBusinessSemanticPreviewCurrent(forged as DetailedBusinessSemanticPreview),/BUSINESS_HANDLE/);
 assert.throws(()=>previewBusinessSemantics(plain(f.prepared),'dispatching'),/BUSINESS_HANDLE/);assert.throws(()=>previewBusinessSemantics(f.prepared,'absent'),/BUSINESS_REFERENCE/);
 assert.throws(()=>{(value.projections.meaning_drafts.DeliveryReady!.examples as unknown[]).push({});},TypeError);
 disposeResolvedBusinessSpec(f.business);assert.throws(()=>assertBusinessSemanticPreviewCurrent(value),/BUSINESS_DISPOSED/);assert.throws(()=>f.preview(),/BUSINESS_DISPOSED/);
});
test('source or captured profile byte drift invalidates a retained preview',t=>{
 const source=fixture(t),sourcePreview=source.preview();writeFileSync(path.join(source.root,'business.alch'),reference+'\n# changed\n');assert.throws(()=>assertBusinessSemanticPreviewCurrent(sourcePreview),/BUSINESS_SOURCE_DRIFT|BUSINESS_PROFILE_SNAPSHOT_STALE/);
 const profile=fixture(t),profilePreview=profile.preview();writeFileSync(path.join(profile.root,'profile/profile.json'),readFileSync(path.join(profile.root,'profile/profile.json'),'utf8')+'\n');assert.throws(()=>assertBusinessSemanticPreviewCurrent(profilePreview),/BUSINESS_PROFILE_SNAPSHOT_STALE/);
});

test('derived legacy text and invalid backend identities reject without truncation or suffixes',t=>{
 const additional=Array.from({length:50},(_,index)=>`  field_${'long'.repeat(22)}_${index} String meaning "Preserved field."`).join('\n');
 const large=fixture(t,reference.replace('  identity id','  identity id\n'+additional));
 assert.throws(()=>large.preview(),/BUSINESS_SOURCE_BUDGET/);
 const invalid=fixture(t,reference.replace('business-model dispatching','business-model _dispatching'));
 assert.throws(()=>invalid.preview(),/BUSINESS_UNSUPPORTED/);
});
test('a definition-only field edit changes aggregate review without inventing a legacy v1 dependency',t=>{
 const extended=reference.replace('  verified Bool meaning "Caller supplied eligibility flag."','  verified Bool meaning "Caller supplied eligibility flag."\n  approved Bool meaning "Another authored Bool field."');
 const original=fixture(t,extended).preview(),changed=fixture(t,extended.replace('boolean-field delivery.verified','boolean-field delivery.approved')).preview();
 assert.notEqual(digest(original.review),digest(changed.review));assert.deepEqual(original.projections.meaning_drafts,changed.projections.meaning_drafts);assert.deepEqual(original.legacy_meaning_subjects,changed.legacy_meaning_subjects);
 assert.equal(changed.projections.rule_meanings.CanConfirm!.predicates.Permitted,'approved');assert.match(changed.review.definitions[0]!.formal.expression,/delivery\.approved = true/);
});

test('legacy duplicate actors and applicability reject before any prospective subject is returned',t=>{
 for(const clause of ['  actor "Delivery API caller"','  applies-when "ConfirmDelivery is requested."']){
  const text=reference.replace(clause,clause+'\n'+clause),f=fixture(t,text);
  const property=clause.includes('actor')?'actors':'applies_when';
  assert.equal(f.business.data.requirements[0]![property].length,2,'B02 and Core retain both authored facts');
  const expectedLine=Math.max(...text.split('\n').flatMap((line,index)=>line===clause?[index+1]:[]));
  assert.throws(()=>f.preview(),error=>{assert.ok(error instanceof BusinessSourceRejected);assert.equal(error.code,'BUSINESS_AMBIGUOUS');assert.equal(error.line,expectedLine);assert.equal(error.column,3);assert.match(error.message,new RegExp(property));return true;});
 }
});
test('distinct legacy string sets copy exact authored text and order without deduplication or rewriting',t=>{
 const text=reference.replace('  actor "Delivery API caller"','  actor "Delivery API caller"\n  actor "A second actor; no authentication claim."').replace('  applies-when "ConfirmDelivery is requested."','  applies-when "ConfirmDelivery is requested."\n  applies-when "An explicitly supplied second condition."').replace('  does-not-mean "The supplied flag independently proves delivery or provenance."','  does-not-mean "The supplied flag independently proves delivery or provenance."\n  does-not-mean "A second exact boundary."');
 const f=fixture(t,text),value=f.preview(),requirement=f.business.data.requirements[0]!,draft=value.projections.meaning_drafts.DeliveryReady!;
 assert.deepEqual(draft.actors,requirement.actors);assert.deepEqual(draft.applies_when,requirement.applies_when);assert.deepEqual(draft.boundaries,requirement.boundaries);
 assert.deepEqual(draft.actors,['Delivery API caller','A second actor; no authentication claim.']);
 for(const property of ['applies_when','actors','inputs','outcomes','boundaries'] as const)assert.equal(new Set(draft[property]).size,draft[property].length);
 assert.equal(value.legacy_meaning_subjects[0]!.digest,digest({...draft,status:'accepted'}));
});

test('derived flat ontology and definition namespaces reject genuine composed-model collisions',t=>{
 const prepare=(texts:readonly string[])=>{
  const f=fixture(t);
  const behaviors=texts.map((text,index)=>{const source='composed-'+index+'.alch';writeFileSync(path.join(f.root,source),text);return lowerBusinessBehavior(lowerBusinessFormalSemantics(prepareBusinessSpecFile(f.root,source)));});
  const project={...f.snapshot.project,models:behaviors.map((behavior,index)=>({id:behavior.data.model_id,source:'composed-'+index+'.alch'}))};
  writeFileSync(path.join(f.root,'project.json'),JSON.stringify(project));
  const snapshot=loadBusinessAuthoringProject(path.join(f.root,'project.json'),{engine:[{key:'recipe.ts',path:path.join(core,'src/profile-engine/business-authoring-recipes.ts')}],tools:[{key:'preview.ts',path:path.join(import.meta.dirname,'../src/business-authoring-carriers.ts')}]});
  return prepareBusinessRecipeSelection(snapshot,behaviors,engine);
 };
 const modelA=reference.replace('business-model dispatching','business-model a'),modelAB=reference.replace('business-model dispatching','business-model a_b').replace('public-name confirmDelivery','public-name confirmAnotherDelivery');
 const ontologyCollision=prepare([modelA.replaceAll('Delivery','B_C'),modelAB.replaceAll('Delivery','C')]);
 for(const model of ['a','a_b'])assert.throws(()=>previewBusinessSemantics(ontologyCollision,model),error=>{assert.ok(error instanceof BusinessSourceRejected);assert.equal(error.code,'BUSINESS_AMBIGUOUS');assert.match(error.message,/BUSINESS-A-B-C/);assert.equal(error.source,'composed-1.alch');return true;});
 const definitionCollision=prepare([modelA.replaceAll('DeliveryEligibility','B_C'),modelAB.replaceAll('DeliveryEligibility','C')]);
 for(const model of ['a','a_b'])assert.throws(()=>previewBusinessSemantics(definitionCollision,model),error=>{assert.ok(error instanceof BusinessSourceRejected);assert.equal(error.code,'BUSINESS_AMBIGUOUS');assert.match(error.message,/DEF-A-B-C/);return true;});
 const distinct=prepare([modelA,reference.replace('business-model dispatching','business-model other').replace('public-name confirmDelivery','public-name confirmOtherDelivery')]);
 assert.notEqual(previewBusinessSemantics(distinct,'a').projections.declarations.Delivery!.ontology,previewBusinessSemantics(distinct,'other').projections.declarations.Delivery!.ontology);
});
