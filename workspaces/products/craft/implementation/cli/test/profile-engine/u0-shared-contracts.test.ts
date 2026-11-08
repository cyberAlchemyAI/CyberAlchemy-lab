import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {profileEngine} from '../../src/index.js';
import {BUSINESS_MIRROR_FILES_V2,checkBusinessMirrorV2,materializeBusinessMirrorsV2,expectedBusinessMirrorV2} from '../../tools/materialize-business-contracts-v2.mjs';
// Open Questions: docs/U0-SHARED-CONTRACTS.md. No runtime producer is forged here.
const packageJson=JSON.parse(readFileSync(new URL('../../package.json',import.meta.url),'utf8'));
test('J00 public Core source exports expose additive contracts and retain legacy identity',()=>{
 assert.equal(profileEngine.BUSINESS_SPEC_V2,'alchlang.business-spec/v2-candidate');
 assert.equal(profileEngine.BUSINESS_AUTHORING_CONTRACT,'craft.business-authoring-contracts/1-candidate');
 assert.equal(profileEngine.BUSINESS_STAGES_V2,'craft.business-authoring-stages/v2-candidate');
 assert.equal(profileEngine.U0_NATIVE_ABI,'craft.u0.pure-submission/v1-candidate');
 assert.equal(typeof profileEngine.selectBusinessAuthoringRecipe,'function');
 assert.equal(typeof profileEngine.directExecutableIdentityV2,'function');
 assert.equal(typeof profileEngine.inventoryBusinessSourceContractV2,'function');
 assert.equal(typeof profileEngine.checkU0WireConfiguration,'function');
 // J01 builds the implemented successor owners; original J00 absence was historical.
 assert.equal(typeof profileEngine.createBusinessCoreRecipeOwnerV2,'function');
 assert.equal(typeof profileEngine.createBusinessU0RuntimeV4,'function');
});
test('J00 ten closed schema resources are explicit package members with original versions',()=>{
 const resources=profileEngine.BUSINESS_CONTRACT_RESOURCES_V2;
 assert.equal(resources.length,10);assert.equal(new Set(resources.map(row=>row.file)).size,10);
 assert.ok(Object.isFrozen(resources));
 for(const row of resources){
  const schema=JSON.parse(readFileSync(new URL('../../contracts/'+row.file,import.meta.url),'utf8'));
  assert.equal(schema.$id,row.version);assert.equal(schema.properties.schema_version.const,row.version);
  assert.equal(schema.additionalProperties,false);assert.ok(packageJson.files.includes('contracts/'+row.file));
 }
 const old=JSON.parse(readFileSync(new URL('../../contracts/business-spec-v1.schema.json',import.meta.url),'utf8'));
 assert.equal(old.properties.claims.minItems,1);
 assert.ok(packageJson.files.includes('contracts/business-spec-v1.schema.json'));
 assert.equal(packageJson.files.includes('examples/u0-contracts'),false,'private construction prototype stays private');
});
test('J00 exact Core to frontend data mirrors reject one-byte and executable-owner drift',()=>{
 assert.equal(materializeBusinessMirrorsV2(false).length,6);
 for(const file of BUSINESS_MIRROR_FILES_V2){
  const source=readFileSync(new URL('../../src/profile-engine/'+file,import.meta.url),'utf8');
  const expected=expectedBusinessMirrorV2(file,source);
  assert.doesNotThrow(()=>checkBusinessMirrorV2(file,source,expected));
  assert.throws(()=>checkBusinessMirrorV2(file,source,expected+'\n'),/mirror drift/);
 }
 assert.throws(()=>expectedBusinessMirrorV2('unregistered.ts',''),/fixed Core/);
 assert.throws(()=>expectedBusinessMirrorV2('business-authoring-stages-v2.ts','export function fakeOwner() {}'),/runtime owner/);
 assert.throws(()=>expectedBusinessMirrorV2('u0-realization-contract.ts','missing boundary'),/boundary changed/);
});
test('J00 public zero-claim identity and required-output policy keep separate semantics',()=>{
 const spec=JSON.parse(readFileSync(new URL('fixtures/u0-v2/spec.json',import.meta.url),'utf8'));
 assert.equal(spec.claims.length,0);
 const executable=profileEngine.directExecutableIdentityV2(spec);
 assert.match(executable.sha256,/^[a-f0-9]{64}$/);
 assert.equal(profileEngine.projectBusinessReviewSubjectV2(spec).authored_rules[0]!.condition.kind,'boolean-field');
 assert.throws(()=>profileEngine.planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind:'base-model',requiredness:'required'}]),/UNSUPPORTED_REQUIRED/);
 const planned=profileEngine.planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind:'base-model',requiredness:'optional'}]);
 assert.equal(planned.outputs[0]!.state,'pending-producer');assert.equal(planned.outputs[1]!.state,'unsupported-optional');
});

test('J01 public source entry can inspect contracts but cannot resolve a built native basis',async()=>{
 await assert.rejects(()=>profileEngine.loadBusinessU0ProfileV4(),/built public SDK required/);
});
