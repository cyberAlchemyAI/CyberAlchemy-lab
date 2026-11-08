import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {businessCanonical} from '../src/business-authoring-model.js';
import {projectAlchDirectExecutableV2,projectAlchOptionalAssuranceV2,alchDirectExecutableDigestV2,alchOptionalAssuranceDigestV2,projectAlchBusinessReviewSubjectV2,captureAlchBusinessIdentityV2} from '../src/business-authoring-identity-v2.js';
// Reads independent test oracles only; no private Core runtime source import.
// Open Questions: Core docs/BUSINESS-IDENTITIES-V2.md.
const core=new URL('../../../../../../../craft/projects/domainspec-v2/impl/cli/',import.meta.url);
const fixture=JSON.parse(readFileSync(new URL('test/profile-engine/fixtures/u0-v2/identity-vectors.json',core),'utf8'));
test('C02 independent Alch projections match fixed Python canonical/digest vectors',()=>{
 for(const {spec,expected} of fixture.vectors){
  assert.equal(businessCanonical(projectAlchDirectExecutableV2(spec)),expected.executable_canonical);
  assert.equal(alchDirectExecutableDigestV2(spec),expected.executable_sha256);
  assert.equal(businessCanonical(projectAlchOptionalAssuranceV2(spec)),expected.assurance_canonical);
  assert.equal(alchOptionalAssuranceDigestV2(spec),expected.assurance_sha256);
  assert.equal(businessCanonical(projectAlchBusinessReviewSubjectV2(spec)),expected.review_canonical);
 }
});
test('C02 Alch preserves claim independence, authored Rule prose and immutable data',()=>{
 const [base,claim]=fixture.vectors;assert.equal(alchDirectExecutableDigestV2(base.spec),alchDirectExecutableDigestV2(claim.spec));
 const value=projectAlchBusinessReviewSubjectV2(base.spec);assert.equal(value.authored_rules[0]!.meaning,base.spec.rules[0].meaning);
 assert.ok(Object.isFrozen(value));assert.ok(Object.isFrozen(value.executable));assert.equal(Object.hasOwn(value,'accepted'),false);
 let calls=0;assert.throws(()=>projectAlchDirectExecutableV2({get schema_version(){calls++;return base.spec.schema_version;}} as any));assert.equal(calls,0);
 assert.throws(()=>projectAlchDirectExecutableV2(new Proxy(base.spec,{})),/BUSINESS_IDENTITY_V2/);
});
test('C02 generated protocol mirror has a single canonical owner and no private import',()=>{
 const canonical=readFileSync(new URL('src/profile-engine/business-authoring-identity-protocol-v2.ts',core),'utf8');
 const mirror=readFileSync(new URL('../src/business-authoring-identity-protocol-v2.ts',import.meta.url),'utf8');
 assert.equal(mirror,'// GENERATED from Core business-authoring-identity-protocol-v2.ts; canonical owner is Core.\n'+canonical);
 assert.equal(readFileSync(new URL('../src/business-authoring-identity-v2.ts',import.meta.url),'utf8').includes('craft/projects/'),false);
});
test('C02 Alch capture manifest has deterministic artifact ordering without future native identity',()=>{
 const manifest={schema_version:'craft.business-capture/v2-candidate',recipe_ref:'direct-entity-bool-operation/v2-candidate',source:{path:'business.alch',sha256:'a'.repeat(64),bytes:123},profiles:[{id:'profile',version:'1.0.0',sha256:'b'.repeat(64)}],tools:[{id:'compiler',sha256:'c'.repeat(64)}],authority_effect:'none'} as const;
 const value=captureAlchBusinessIdentityV2(manifest);assert.match(value.capture_sha256,/^[a-f0-9]{64}$/);assert.equal(Object.hasOwn(value,'callable_sha256'),false);
 const changed=captureAlchBusinessIdentityV2({...manifest,source:{...manifest.source,sha256:'d'.repeat(64)}});assert.notEqual(value.capture_sha256,changed.capture_sha256);
 for(const extra of ['accepted','callable_sha256'])assert.throws(()=>captureAlchBusinessIdentityV2({...manifest,[extra]:true} as any),/BUSINESS_IDENTITY_V2/);
 assert.throws(()=>captureAlchBusinessIdentityV2({...manifest,source:{...manifest.source,bytes:0}}),/BUSINESS_IDENTITY_V2/);
});
