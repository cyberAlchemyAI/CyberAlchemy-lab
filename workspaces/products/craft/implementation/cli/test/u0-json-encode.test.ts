import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {encodeU0Request,encodeU0Outcome,encodeU0AdapterError,u0WireBounds,checkU0EncoderConfiguration,U0_ADAPTER_ERROR_CODES,U0JsonEncodeError} from '../profiles/node-http-entry-u0-v4/runtime/u0-json-encode.js';
import {decodeU0Json} from '../profiles/node-http-entry-u0-v4/runtime/u0-json-decode.js';
import {formU0Submission} from '../profiles/node-http-entry-u0-v4/runtime/u0-values.js';
import {U0_ADAPTER_FAILURES,U0_CONFIG_EXAMPLE} from '../src/profile-engine/u0-realization-contract.js';
import type {U0EncoderOwnerV2} from '../src/profile-engine/business-authoring-stages-v2.js';
// Open Questions: U07 and genuine loaded/generated/installed qualification.
const owner:U0EncoderOwnerV2=Object.freeze({request:encodeU0Request,outcome:encodeU0Outcome,error:encodeU0AdapterError,bounds:u0WireBounds,checkConfiguration:checkU0EncoderConfiguration});
const domain=Object.freeze({rejection_code:'delivery-verification-required'});
const text=(value:Uint8Array)=>new TextDecoder().decode(value);
test('U06c independent literal canonical envelopes and structural maxima',()=>{
 const value={id:18446744073709551615n,verified:false};
 assert.equal(text(owner.request(value)),'{"id":"18446744073709551615","verified":false}');
 const completed={...value,verified:true};
 assert.equal(text(owner.outcome({kind:'completed',value:completed},domain)),'{"kind":"completed","value":{"id":"18446744073709551615","verified":true}}');
 assert.throws(()=>owner.outcome({kind:'completed',value},domain),/U0_ENCODE_OUTCOME/);
 assert.equal(text(owner.outcome({kind:'rejected',code:'delivery-verification-required'},domain)),'{"kind":"rejected","code":"delivery-verification-required"}');
 const bounds=owner.bounds(domain);assert.equal(bounds.request,46);assert.equal(bounds.completed,74);assert.equal(bounds.rejected,59);
 assert.equal(owner.request(value).length,bounds.request);assert.equal(owner.outcome({kind:'completed',value:completed},domain).length,bounds.completed);
 assert.equal(owner.outcome({kind:'rejected',code:domain.rejection_code},domain).length,bounds.rejected);
});
test('U06c fixed C03 encoder literals are independently replayed',()=>{
 const vectors=JSON.parse(readFileSync(new URL('profile-engine/fixtures/u0-v2/wire-vectors.json',import.meta.url),'utf8'));
 for(const row of vectors.encoder){
  const value=row.value.kind==='completed'?{kind:'completed' as const,value:{id:18446744073709551615n,verified:true}}:{kind:'rejected' as const,code:domain.rejection_code};
  assert.equal(text(owner.outcome(value,domain)),row.canonical);
 }
});
test('U06c fixed adapter code materialization and all nine literal error envelopes',()=>{
 assert.deepEqual(U0_ADAPTER_ERROR_CODES,U0_ADAPTER_FAILURES.map(row=>row.code));
 const rows=[['route-not-found','{"kind":"adapter-error","code":"route-not-found"}'],['method-not-allowed','{"kind":"adapter-error","code":"method-not-allowed"}'],['unsupported-media-type','{"kind":"adapter-error","code":"unsupported-media-type"}'],['request-aborted','{"kind":"adapter-error","code":"request-aborted"}'],['request-too-large','{"kind":"adapter-error","code":"request-too-large"}'],['body-timeout','{"kind":"adapter-error","code":"body-timeout"}'],['body-read-failed','{"kind":"adapter-error","code":"body-read-failed"}'],['invalid-request','{"kind":"adapter-error","code":"invalid-request"}'],['adapter-contract-defect','{"kind":"adapter-error","code":"adapter-contract-defect"}']] as const;
 let largest=0;for(const [code,expected]of rows){assert.equal(text(owner.error(code)),expected);largest=Math.max(largest,expected.length);}
 assert.equal(largest,owner.bounds(domain).adapter_error);
 assert.throws(()=>owner.error('caller-secret' as any),U0JsonEncodeError);
});
test('U06c canonical ASCII handles actual authored Unicode/control/quote rejection text',()=>{
 const code='a"\\\b\f\n\r\t\u0001é😀';const own={rejection_code:code};
 const expected='{"kind":"rejected","code":"a\\"\\\\\\b\\f\\n\\r\\t\\u0001\\u00e9\\ud83d\\ude00"}';
 const output=owner.outcome({kind:'rejected',code},own);assert.equal(text(output),expected);assert.ok([...output].every(byte=>byte<128));assert.equal(output.length,owner.bounds(own).rejected);
 assert.equal(JSON.parse(text(output)).code,code);
 for(const rejected of ['', '\ud800','\udc00','x'.repeat(4097),'😀'.repeat(4097)])assert.throws(()=>owner.bounds({rejection_code:rejected}),U0JsonEncodeError);
 const maximum={rejection_code:'😀'.repeat(4096)};assert.equal(owner.bounds(maximum).rejected,29+12*4096);
});
test('U06c configuration checks actual rejection bound rather than fixture size',()=>{
 const own={rejection_code:'x'.repeat(200)};const bounds=owner.bounds(own);assert.equal(bounds.rejected,229);
 const exact={...U0_CONFIG_EXAMPLE,request_bytes:46,response_bytes:229,body_timeout_ms:1};const accepted=owner.checkConfiguration(exact,own);assert.ok(Object.isFrozen(accepted));assert.equal(accepted.response_bytes,229);
 assert.throws(()=>owner.checkConfiguration({...exact,request_bytes:45},own),/U0_ENCODE_COVERAGE/);
 assert.throws(()=>owner.checkConfiguration({...exact,response_bytes:228},own),/U0_ENCODE_COVERAGE/);
 for(const key of ['request_bytes','response_bytes','body_timeout_ms'])for(const n of [0,-1,0.5,NaN,Infinity,2147483648,'4096'])assert.throws(()=>owner.checkConfiguration({...exact,[key]:n} as any,own),/U0_ENCODE_CONFIGURATION/);
 assert.throws(()=>owner.checkConfiguration({...exact,method:'GET'} as any,own));
 const captured=owner.checkConfiguration(exact,own);exact.response_bytes=999;assert.equal(captured.response_bytes,229);
});
test('U06c full scalar-domain bound follows exact bigint and Boolean shape; fixed boundary roundtrips',()=>{
 for(const id of [0n,1n,9007199254740991n,9007199254740992n,9007199254740993n,18446744073709551615n])for(const verified of [false,true]){
  const source={id,verified},encoded=owner.request(source),decoded=formU0Submission(decodeU0Json(encoded,46));assert.equal(decoded.id,id);assert.equal(decoded.verified,verified);
  assert.ok(encoded.length<=46);
  if(verified)assert.ok(owner.outcome({kind:'completed',value:source},domain).length<=74);
  else assert.throws(()=>owner.outcome({kind:'completed',value:source},domain),/U0_ENCODE_OUTCOME/);
 }
});
test('U06c rejects nonconforming outcomes, unowned accessors/proxies and serialization hooks',()=>{
 let calls=0;
 const active={kind:'completed',get value(){calls++;return {id:1n,verified:true};}};
 const proxy=new Proxy({rejection_code:'x'},{ownKeys(){calls++;throw Error('trap');},getPrototypeOf(){calls++;throw Error('trap');}});
 for(const value of [active,{kind:'completed',value:{id:1,verified:true}},{kind:'completed',value:{id:1n,verified:true},extra:0},{kind:'rejected',code:'other'},{kind:'other'},Promise.resolve({kind:'rejected',code:'x'})])assert.throws(()=>owner.outcome(value as any,domain));
 assert.throws(()=>owner.bounds(proxy));assert.throws(()=>owner.bounds({get rejection_code(){calls++;return 'x';}}));
 assert.throws(()=>owner.outcome({kind:'rejected',code:domain.rejection_code,toJSON(){calls++;return {};}} as any,domain));
 assert.throws(()=>owner.checkConfiguration(new Proxy(U0_CONFIG_EXAMPLE,{ownKeys(){calls++;throw Error('trap');}}),domain));assert.equal(calls,0);
});
