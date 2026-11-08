import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {decodeU0Json,inspectU0JsonDecode,U0JsonDecodeError} from '../profiles/node-http-entry-u0-v4/runtime/u0-json-decode.js';
import type {U0DecoderOwnerV2} from '../src/profile-engine/business-authoring-stages-v2.js';
// Original C03 corpus is fixed independent data; seven decimal/range failures are
// U06b obligations. This task tests their token shape without claiming value validity.
// Open Questions: U06b/U06c/U07 and actual registered/generated assembly.
const owner:U0DecoderOwnerV2=Object.freeze({decode:decodeU0Json});
const vectors=JSON.parse(readFileSync(new URL('profile-engine/fixtures/u0-v2/wire-vectors.json',import.meta.url),'utf8'));
const formation=new Set(['leading-zero','leading-plus','negative','fraction','exponent','over-uint64','over-digit-limit']);
for(const row of vectors.decoder){
 test('U06a fixed C03 bytes: '+row.id+(formation.has(row.id)?' (formation deferred)':''),()=>{
  const bytes=Buffer.from(row.bytes_hex,'hex');
  if(row.expected.kind==='decoded')assert.deepEqual(owner.decode(bytes,4096),{id:row.expected.value.id_decimal,verified:row.expected.value.verified});
  else if(formation.has(row.id))assert.equal(typeof owner.decode(bytes,4096).id,'string');
  else assert.throws(()=>owner.decode(bytes,4096),U0JsonDecodeError);
 });
}
const bytes=(text:string)=>Buffer.from(text,'utf8');
const wire=(text:string)=>decodeU0Json(bytes(text),4096);
test('U06a accepts JSON whitespace, either field order and escaped key/digit spellings',()=>{
 assert.deepEqual(wire('\r\n\t{ "verified" : false , "\\u0069d" : "\\u0030" } \t'),{id:'0',verified:false});
 assert.deepEqual(wire('{"id":"31","\\u0076erified":true}'),{id:'31',verified:true});
 for(const text of ['{"id":"31","id":"32","verified":true}','{"id":"31","\\u0069d":"32","verified":true}','{"id":"31","verified":true,"\\u0076erified":false}'])assert.throws(()=>wire(text),e=>e instanceof U0JsonDecodeError&&e.code==='U0_DECODE_DUPLICATE');
});
test('U06a string scanner decodes all JSON escapes and complete Unicode scalar pairs',()=>{
 assert.equal(wire('{"id":"\\\"\\\\\\/\\b\\f\\n\\r\\t","verified":false}').id,'"\\/\b\f\n\r\t');
 assert.equal(wire('{"id":"\\uD83D\\uDE00","verified":true}').id,'😀');
 assert.equal(wire('{"id":"😀","verified":true}').id,'😀');
 assert.equal(wire('{"id":"x},:\\u0030","verified":false}').id,'x},:0');
 for(const value of ['\\uD800','\\uDC00','\\uD800\\u0041','\\uD800x','\\x31','\\uZZZZ','\\q','\n','\u0001'])assert.throws(()=>wire('{"id":"'+value+'","verified":true}'),U0JsonDecodeError);
});
test('U06a rejects every nested/extra/missing/non-JSON/literal/trailing shape',()=>{
 for(const text of ['{}','[]','null','{"id":null,"verified":true}','{"id":[],"verified":false}','{"id":"1","verified":{}}','{"id":"1","verified":True}','{"id":"1","verified":truefalse}','{"id":"1","verified":false,}','{"id":"1","verified":true} {}','{"id":"1","verified":true,"__proto__":{}}','{"id":"1","verified":true} // comment','\u00a0{"id":"1","verified":true}','{"id":"1"\u00a0,"verified":true}'])assert.throws(()=>wire(text),U0JsonDecodeError,text);
 assert.throws(()=>wire('{"id":"1","other":true,"verified":true}'),e=>e instanceof U0JsonDecodeError&&e.code==='U0_DECODE_FIELD');
 assert.throws(()=>wire('{"id":"1"}'),e=>e instanceof U0JsonDecodeError&&e.code==='U0_DECODE_MISSING');
});
test('U06a fatal UTF-8 rejects invalid continuation, overlong and encoded surrogate bytes',()=>{
 const prefix=bytes('{"id":"'),suffix=bytes('","verified":true}');
 for(const hex of ['c328','c0af','eda080','f4908080','e282'])assert.throws(()=>decodeU0Json(Buffer.concat([prefix,Buffer.from(hex,'hex'),suffix]),4096),e=>e instanceof U0JsonDecodeError&&e.code==='U0_DECODE_UTF8');
 assert.throws(()=>decodeU0Json(Buffer.concat([Buffer.from('efbbbf','hex'),bytes('{"id":"1","verified":true}')]),4096),e=>e instanceof U0JsonDecodeError&&e.code==='U0_DECODE_BOM');
});
test('U06a counts actual UTF-8 bytes before decode and rejects invalid configured domains',()=>{
 const encoded=bytes('{"id":"1","verified":true}');
 assert.deepEqual(decodeU0Json(encoded,encoded.byteLength),{id:'1',verified:true});
 assert.throws(()=>decodeU0Json(encoded,encoded.byteLength-1),e=>e instanceof U0JsonDecodeError&&e.code==='U0_DECODE_BYTES');
 const multibyte=bytes('{"id":"😀","verified":true}');assert.throws(()=>decodeU0Json(multibyte,'{"id":"😀","verified":true}'.length),/U0_DECODE_BYTES/);
 for(const cap of [0,-1,0.1,NaN,Infinity,2147483648,'4096',{}])assert.throws(()=>decodeU0Json(encoded,cap as number),/U0_DECODE_LIMIT/);
});
test('U06a owns input bytes without subclass length/offset getters, iterators or shared mutation',()=>{
 let calls=0;const input=Uint8Array.from(bytes('{"id":"1","verified":false}'));
 for(const key of ['byteLength','byteOffset','buffer'])Object.defineProperty(input,key,{get(){calls++;throw Error('caller getter must not execute');}});
 assert.deepEqual(decodeU0Json(input,4096),{id:'1',verified:false});assert.equal(calls,0);
 assert.throws(()=>decodeU0Json(input,1),/U0_DECODE_BYTES/);assert.equal(calls,0);
 assert.throws(()=>decodeU0Json(new Proxy(input,{}),4096),/U0_DECODE_ARGUMENT/);
 assert.throws(()=>decodeU0Json(new DataView(new ArrayBuffer(8)) as any,4096),/U0_DECODE_ARGUMENT/);
 assert.throws(()=>decodeU0Json(new Uint8Array(new SharedArrayBuffer(32)),4096),/U0_DECODE_ARGUMENT/);
});
test('U06a uses no JSON.parse and treats decimal validity as a separate formation stage',()=>{
 const original=JSON.parse;
 try{JSON.parse=()=>{throw Error('generic JSON parse forbidden');};assert.deepEqual(wire('{"id":"9007199254740993","verified":true}'),{id:'9007199254740993',verified:true});assert.throws(()=>wire('{"id":"1","id":"2","verified":true}'),/U0_DECODE_DUPLICATE/);}
 finally{JSON.parse=original;}
 assert.equal(wire('{"id":"not-a-number","verified":true}').id,'not-a-number');
 assert.equal(wire('{"id":"18446744073709551616","verified":true}').id,'18446744073709551616');
});
test('U06a observed scanner work grows within a fixed linear bound for padding and escapes',()=>{
 for(const count of [32,128,512,1024,2048]){
  const text=' '.repeat(count)+'{"id":"31","verified":false}',encoded=bytes(text),result=inspectU0JsonDecode(encoded,4096);
  assert.equal(result.work.cursor_advances,text.length);assert.equal(result.work.source_code_units,text.length);
  assert.ok(result.work.code_unit_reads<=4*encoded.byteLength+64);assert.ok(result.work.decoded_string_units<=encoded.byteLength);
 }
 for(const count of [1,16,64,256,512]){
  const text='{"id":"'+'\\u0031'.repeat(count)+'","verified":true}',encoded=bytes(text),result=inspectU0JsonDecode(encoded,4096);
  assert.equal(result.value.id,'1'.repeat(count));assert.ok(result.work.code_unit_reads<=4*encoded.byteLength+64);assert.equal(result.work.cursor_advances,text.length);
 }
});
test('U06a records are immutable own data; diagnostics expose fixed code/offset only',()=>{
 const value=wire('{"id":"1","verified":true}');assert.ok(Object.isFrozen(value));assert.deepEqual(Object.keys(value),['id','verified']);
 assert.throws(()=>{(value as {id:string}).id='other';},TypeError);
 try{wire('{"secret":"caller-data","verified":true}');assert.fail('must reject');}catch(error){assert.ok(error instanceof U0JsonDecodeError);assert.equal(error.message.includes('caller-data'),false);assert.ok(Number.isInteger(error.offset));}
});
