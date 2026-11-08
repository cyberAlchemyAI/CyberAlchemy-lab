import assert from 'node:assert/strict';
import {writeFileSync,readFileSync} from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {composeProfile,assertCheckedCompositionCurrent,selectProfileConfiguration,profileTechnicalSelections} from '../../src/profile-engine/compose.js';
import {compiledProfileFixture,createProfileFixture} from './profile-fixture.js';
// Open questions: PE08 executable dispatcher and PE14 actual application graph adapter.
test('locked rules bind registered domain graphs, exact business artifacts and unique owners',async t=>{
 const f=await compiledProfileFixture(t),composed=composeProfile(f.selection,f.functions);assertCheckedCompositionCurrent(composed);
 assert.equal(composed.data.components.filter(c=>c.role==='http-entry').length,2);assert.equal(composed.data.components.filter(c=>c.role==='domain-function').length,2);assert.ok(composed.artifacts.length>20);
 assert.equal(new Set(composed.data.components.flatMap(c=>c.artifact_paths)).size,composed.data.components.flatMap(c=>c.artifact_paths).length);
 assert.ok(composed.data.components.find(c=>c.role==='http-dispatch')!.depends_on.length===2);
 assert.throws(()=>assertCheckedCompositionCurrent(JSON.parse(JSON.stringify(composed))),/PROFILE_COMPOSITION_UNREGISTERED_OR_CHANGED/);
 const body=readFileSync(path.join(f.root,'quote.alch'),'utf8');writeFileSync(path.join(f.root,'quote.alch'),body+'\n# source drift');assert.throws(()=>assertCheckedCompositionCurrent(composed),/PROFILE_SNAPSHOT_STALE/);
});
test('missing intent owners, duplicate routes/functions and forged graphs reject',async t=>{
 const f=await compiledProfileFixture(t);assert.throws(()=>composeProfile(f.selection,f.functions.slice(0,1)),/PROFILE_CALLABLE_UNRESOLVED|PROFILE_DOMAIN_UNCOVERED/);
 assert.throws(()=>composeProfile(f.selection,[...f.functions,f.functions[0]!]),/PROFILE_FUNCTION_CONFLICT/);
 assert.throws(()=>composeProfile(f.selection,[{...f.functions[0]!,graph:JSON.parse(JSON.stringify(f.functions[0]!.graph))},f.functions[1]!]),{code:'MTCLI_COMPILED_SNAPSHOT'});
 const collision=await compiledProfileFixture(t,p=>{p.rules[0].fields.output_prefix={literal:'same'};});assert.throws(()=>composeProfile(collision.selection,collision.functions),/PROFILE_ARTIFACT_OWNER_CONFLICT/);
});
test('native feature glue cannot replace compiled business artifacts',async t=>{
 const f=await compiledProfileFixture(t),first=f.functions[0]!,key=Object.keys(first.artifacts).find(k=>k.endsWith('behavior.mjs'))!;
 assert.throws(()=>composeProfile(f.selection,[{...first,artifacts:{...first.artifacts,[key]:'export const execute=()=>({status:"fake"});'}},f.functions[1]!]),/PROFILE_SEMANTIC_ARTIFACT_MISMATCH/);
});
test('uncaptured public intents and malformed technical defaults reject before rendering',t=>{
 const missing=createProfileFixture(t,p=>p.rules.splice(1,1));assert.throws(()=>profileTechnicalSelections(selectProfileConfiguration(missing.load())),/PROFILE_PUBLIC_INTENT_UNCOVERED/);
 const fake=createProfileFixture(t,p=>p.rules[1].fields.id={literal:'inventedIntent'});assert.throws(()=>profileTechnicalSelections(selectProfileConfiguration(fake.load())),/PROFILE_ENTRY_INTENT_UNKNOWN/);
 const defaults=createProfileFixture(t,p=>p.rules[1].fields.technical.literal.business_rounding='floor');assert.throws(()=>profileTechnicalSelections(selectProfileConfiguration(defaults.load())),/PROFILE_TECHNICAL_VOCABULARY/);
});
