import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkU0WireConfiguration,U0_CONFIG_EXAMPLE,U0_ADAPTER_FAILURES,U0_CANONICAL_MAX_BYTES} from '../../src/profile-engine/u0-realization-contract.js';
// Configuration/ABI contracts only; no native codec/handler/loader evidence.
// Open Questions: docs/U0-NATIVE-CONTRACT.md.
test('C03 explicit configuration fits native domains and returns data only',()=>{
 const config=checkU0WireConfiguration(U0_CONFIG_EXAMPLE);
 assert.deepEqual({...config},{...U0_CONFIG_EXAMPLE});assert.ok(Object.isFrozen(config));
 assert.equal(Object.hasOwn(config,'accepted'),false);assert.equal(Object.hasOwn(config,'basis_sha256'),false);
});
test('C03 rejects unsafe, clamped, truncated and under-capacity values',()=>{
 for(const key of ['request_bytes','response_bytes','body_timeout_ms'] as const){
  for(const value of [0,-1,1.1,NaN,Infinity,2147483648,Number.MAX_SAFE_INTEGER+1,'4096'])assert.throws(()=>checkU0WireConfiguration({...U0_CONFIG_EXAMPLE,[key]:value}),/U0_CONFIG|PROFILE_DATA/);
 }
 assert.throws(()=>checkU0WireConfiguration({...U0_CONFIG_EXAMPLE,request_bytes:45}),/U0_CONFIG_COVERAGE/);
 assert.throws(()=>checkU0WireConfiguration({...U0_CONFIG_EXAMPLE,response_bytes:73}),/U0_CONFIG_COVERAGE/);
});
test('C03 wire configuration cannot carry a callable, override or readiness claim',()=>{
 for(const field of ['ready','accepted','asset_sha256','callable','invoke','store','observer'])assert.throws(()=>checkU0WireConfiguration({...U0_CONFIG_EXAMPLE,[field]:true}),/U0_CONFIG_SHAPE/);
 assert.throws(()=>checkU0WireConfiguration({...U0_CONFIG_EXAMPLE,schema_version:'craft.operation-json-post/v1-candidate'}),/U0_CONFIG_VERSION/);
 assert.throws(()=>checkU0WireConfiguration({...U0_CONFIG_EXAMPLE,pathname:'/other'}),/U0_CONFIG_VERSION/);
 let calls=0;assert.throws(()=>checkU0WireConfiguration({get schema_version(){calls++;return 'forged';}}));assert.equal(calls,0);
 assert.throws(()=>checkU0WireConfiguration(new Proxy({...U0_CONFIG_EXAMPLE},{})),/PROFILE_DATA_PROXY/);
});
test('C03 selected canonical byte bounds have independent literal witnesses',()=>{
 assert.equal(Buffer.byteLength('{"id":"18446744073709551615","verified":false}'),46);
 assert.equal(Buffer.byteLength('{"kind":"completed","value":{"id":"18446744073709551615","verified":true}}'),74);
 assert.equal(Buffer.byteLength('{"kind":"rejected","code":"delivery-verification-required"}'),59);
 assert.deepEqual(U0_CANONICAL_MAX_BYTES,{request:46,completed:74,rejected:59});
 assert.equal(new Set(U0_ADAPTER_FAILURES.map(row=>row.code)).size,9);
 for(const {code} of U0_ADAPTER_FAILURES)assert.ok(Buffer.byteLength('{"kind":"adapter-error","code":"'+code+'"}')<=74);
});
test('C03 old descriptor stays distinct; new loader is a later producer',()=>{
 const old=JSON.parse(readFileSync(new URL('../../profiles/node-http-entry-local-v3/profile.json',import.meta.url),'utf8'));
 assert.equal(old.schema_version,'craft.profile-package/v3-candidate');assert.notEqual(old.id,'node-http-entry-u0-v4');
});
