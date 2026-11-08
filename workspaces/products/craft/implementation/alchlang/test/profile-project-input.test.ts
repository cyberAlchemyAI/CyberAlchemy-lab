import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {deriveProfileSources,assertLoweredProfileSourcesCurrent,type ProfileTechnicalSelection} from '../src/profile-project-input.js';
import {prepareServicePlan,assertPreparedServiceCurrent,disposePreparedService} from '../src/service-builder.js';
import {loadDomainSpecCompiler} from '../src/domainspec-cli.js';
import {loadProfileProject} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/src/profile-engine/loader.js';
import {prepareProfileBusinessInput,assertProfileBusinessInputCurrent} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/src/profile-engine/business-input.js';
import {PROFILE_ROLE_CONTRACTS,dataDigest} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/src/profile-engine/contracts.js';
// Cross-package construction fixture; public exports integrate at PE11. Open questions: PE08 public boundary.
const repo=path.resolve(import.meta.dirname,'../../../../../../../');
function fixture(t:{after(fn:()=>void):void}){
 const root=mkdtempSync(path.join(os.tmpdir(),'profile-business-lower-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 cpSync(path.join(repo,'craft/projects/domainspec-v2/impl/cli/test/profile-engine/fixtures/quote-business'),root,{recursive:true});mkdirSync(path.join(root,'profile'));
 const project=JSON.parse(readFileSync(path.join(root,'project.json'),'utf8'));project.profiles=[{id:'Example',version:'1.0.0',path:'profile'}];writeFileSync(path.join(root,'project.json'),JSON.stringify(project));
 const cap=PROFILE_ROLE_CONTRACTS['domain-function'];writeFileSync(path.join(root,'profile/profile.json'),JSON.stringify({schema_version:'craft.profile-package/v1',id:'Example',version:'1.0.0',engine:'craft.profile-engine/v1',conflict_policy:'reject',dependencies:[],capabilities:[{role:'domain-function',descriptor_ref:cap.descriptor_ref,recipe_ref:cap.recipe_ref}],budgets:{operations:100,rows:100,join_pairs:100,depth:16,bytes:8192},rules:[{id:'defaults',op:'defaults',as:'defaults',values:{method:'POST'}}],assets:[]}));
 const identity={engine:[{key:'engine',path:path.join(root,'profile/profile.json')}],tools:[{key:'tool',path:path.join(root,'provider.json')}]};
 const prepare=()=>prepareProfileBusinessInput(loadProfileProject(path.join(root,'project.json'),identity));
 const selections:ProfileTechnicalSelection[]=project.public_intents.map((intent:any)=>({intent_id:intent.id,route:'/'+intent.id,method:'POST',request_bytes:16384,timeout_ms:2000,read_timeout_ms:500,read_max_bytes:8192,read_credentials:'none',success_status:200,rejection_status:409,origin:{source:'profile/profile.json',selector:'entryRule',sha256:'a'.repeat(64)}}));
 return {root,project,prepare,selections};
}
test('business-only input derives checked carriers, service entries and origins',async t=>{
 const f=fixture(t),input=f.prepare(),compiler=await loadDomainSpecCompiler(),lowered=deriveProfileSources(input,{assertProfileBusinessInputCurrent},compiler,f.selections);
 assert.equal(lowered.entries.length,2);assert.equal(lowered.functions.length,2);assert.ok(lowered.files['service.alch']!.includes('profile service-v1'));
 assert.deepEqual(lowered.entries.map(e=>e.access),['public','public']);assert.ok(lowered.entries[0]!.environment.includes('DEPENDENCY_INVENTORY_URL'));assert.ok(!lowered.entries.some(e=>e.environment.includes('INTERNAL_COMPATIBILITY_AUTH')));
 for(const intent of input.project.public_intents)assert.ok(lowered.origins.some(o=>o.business_selector==='public-intent:'+intent.id));for(const read of input.project.external_reads)assert.ok(lowered.origins.some(o=>o.configuration_selector==='binding:'+read.id));
 assertLoweredProfileSourcesCurrent(lowered);assert.throws(()=>assertLoweredProfileSourcesCurrent(JSON.parse(JSON.stringify(lowered))),/PROFILE_LOWERED_SOURCES_UNREGISTERED_OR_CHANGED/);
 const derived=path.join(f.root,'derived');mkdirSync(derived);for(const [file,bytes]of Object.entries(lowered.files)){const target=path.join(derived,file);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,bytes);}
 const registered=await prepareServicePlan(path.join(derived,'service.alch'));assertPreparedServiceCurrent(registered);assert.equal(registered.functions.length,2);disposePreparedService(registered);
 assert.ok(lowered.functions.every(f=>f.compiled.source.includes('export')));assert.ok(lowered.functions[0]!.ontology.nodes.some((n:any)=>n.name==='EnoughStock'));
 assert.throws(()=>deriveProfileSources(JSON.parse(JSON.stringify(input)),{assertProfileBusinessInputCurrent},compiler,f.selections),/PROFILE_BUSINESS_INPUT_UNREGISTERED/);
 assert.throws(()=>deriveProfileSources(input,{assertProfileBusinessInputCurrent},compiler,[f.selections[0]!,{...f.selections[1]!,route:f.selections[0]!.route}]),/PROFILE_ROUTE_CONFLICT/);
});
test('technical authoring, absent wire contracts, semantic smuggling and unknown policies reject',t=>{
 const f=fixture(t);writeFileSync(path.join(f.root,'quote.alch'),readFileSync(path.join(f.root,'quote.alch'),'utf8')+'\nendpoint Sneaky:\n  path "/hidden"\n');assert.throws(()=>f.prepare(),/PROFILE_TECHNICAL_SOURCE_FORBIDDEN/);
 const missing=fixture(t);writeFileSync(path.join(missing.root,'provider.json'),JSON.stringify({schema_version:'craft.integration-configuration/v1',bindings:[]}));assert.throws(()=>missing.prepare(),/PROFILE_WIRE_CONTRACT_REQUIRED/);
 const smuggle=fixture(t);const wire=JSON.parse(readFileSync(path.join(smuggle.root,'provider.json'),'utf8'));wire.bindings[0].correspondence.stock='stock * 2';writeFileSync(path.join(smuggle.root,'provider.json'),JSON.stringify(wire));assert.throws(()=>smuggle.prepare(),/PROFILE_WIRE_CORRESPONDENCE/);
 const policy=fixture(t);policy.project.public_intents[0].access={kind:'policy',policy_ref:'MissingPolicy'};writeFileSync(path.join(policy.root,'project.json'),JSON.stringify(policy.project));assert.throws(()=>policy.prepare(),/PROFILE_AUTH_POLICY_UNSUPPORTED/);
});
test('wire writes, undeclared dependencies and mutable source reject',t=>{
 const f=fixture(t),prepared=f.prepare();writeFileSync(path.join(f.root,'quote.alch'),readFileSync(path.join(f.root,'quote.alch'),'utf8')+'\n# source changed\n');assert.throws(()=>assertProfileBusinessInputCurrent(prepared),/PROFILE_SNAPSHOT_STALE/);
 const write=fixture(t),wire=JSON.parse(readFileSync(path.join(write.root,'provider.json'),'utf8'));wire.bindings[0].operation.method='POST';writeFileSync(path.join(write.root,'provider.json'),JSON.stringify(wire));assert.throws(()=>write.prepare(),/PROFILE_WIRE_OPERATION_UNSUPPORTED/);
 const names=fixture(t),other=JSON.parse(readFileSync(path.join(names.root,'provider.json'),'utf8'));other.bindings[0].intent_id='Unknown';writeFileSync(path.join(names.root,'provider.json'),JSON.stringify(other));assert.throws(()=>names.prepare(),/PROFILE_WIRE_INTENT_UNKNOWN/);
});

test('wire correspondence cannot weaken authored value types or bounds',async t=>{
 const f=fixture(t),wire=JSON.parse(readFileSync(path.join(f.root,'provider.json'),'utf8'));wire.bindings[0].wire_schema.fields.stock.type='boolean';wire.bindings[0].wire_schema_sha256=dataDigest(wire.bindings[0].wire_schema);writeFileSync(path.join(f.root,'provider.json'),JSON.stringify(wire));const input=f.prepare(),compiler=await loadDomainSpecCompiler();assert.throws(()=>deriveProfileSources(input,{assertProfileBusinessInputCurrent},compiler,f.selections),/PROFILE_WIRE_VALUE_TYPE/);
 const g=fixture(t),bounds=JSON.parse(readFileSync(path.join(g.root,'provider.json'),'utf8'));bounds.bindings[0].wire_schema.fields.stock.max=20000;bounds.bindings[0].wire_schema_sha256=dataDigest(bounds.bindings[0].wire_schema);writeFileSync(path.join(g.root,'provider.json'),JSON.stringify(bounds));assert.throws(()=>deriveProfileSources(g.prepare(),{assertProfileBusinessInputCurrent},compiler,g.selections),/PROFILE_BUSINESS_CONSTRAINT_CONFLICT/);
});
