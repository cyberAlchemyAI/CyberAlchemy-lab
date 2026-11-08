import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {formU0Submission,copyU0Submission,U0ValueError} from '../profiles/node-http-entry-u0-v4/runtime/u0-values.js';
import {decodeU0Json} from '../profiles/node-http-entry-u0-v4/runtime/u0-json-decode.js';
import {renderExactUInt64Support} from '../src/generation/configured-exact-uint64-source.js';
import type {U0ValueOwnerV2} from '../src/profile-engine/business-authoring-stages-v2.js';
// Open Questions: U06c/U07 and genuinely generated/profile/installed witnesses.
const owner:U0ValueOwnerV2=Object.freeze({form:formU0Submission,copy:copyU0Submission});
const vectors=JSON.parse(readFileSync(new URL('profile-engine/fixtures/u0-v2/wire-vectors.json',import.meta.url),'utf8'));
for(const row of vectors.decoder){
 test('U06b fixed C03 decode + form: '+row.id,()=>{
  const invoke=()=>owner.form(decodeU0Json(Buffer.from(row.bytes_hex,'hex'),4096));
  if(row.expected.kind==='decoded'){
   const value=invoke();assert.equal(String(value.id),row.expected.value.id_decimal);assert.equal(value.verified,row.expected.value.verified);
   assert.equal(typeof value.id,'bigint');assert.ok(Object.isFrozen(value));assert.equal(Object.getPrototypeOf(value),null);
  }else assert.throws(invoke);
 });
}
test('U06b reuses the original selected exact scalar normalization source',()=>{
 const actual=readFileSync(new URL('../profiles/node-http-entry-u0-v4/runtime/u0-values.ts',import.meta.url),'utf8');
 assert.ok(actual.includes(renderExactUInt64Support()),'materialized existing scalar protocol must remain exact');
});
test('U06b independent full-width boundary literals survive formation and native copies',()=>{
 const rows:[string,bigint][]=[['0',0n],['1',1n],['9007199254740991',9007199254740991n],['9007199254740992',9007199254740992n],['9007199254740993',9007199254740993n],['18446744073709551615',18446744073709551615n]];
 for(const [decimal,expected] of rows)for(const verified of [true,false]){
  const formed=owner.form({id:decimal,verified});assert.equal(formed.id,expected);assert.equal(formed.verified,verified);
  const copy=owner.copy(formed);assert.notEqual(copy,formed);assert.equal(copy.id,expected);assert.equal(copy.verified,verified);assert.equal(Object.getPrototypeOf(copy),null);
 }
 const escaped=owner.form(decodeU0Json(Buffer.from('{"id":"\\u0039'+'007199254740993","verified":true}'),4096));assert.equal(escaped.id,9007199254740993n);
});
test('U06b rejects noncanonical/range strings before any bigint conversion',()=>{
 const original=globalThis.BigInt;let calls=0;
 try{
  globalThis.BigInt=((...args:Parameters<BigIntConstructor>)=>{calls++;return original(...args);}) as BigIntConstructor;
  for(const id of ['','00','01','+1','-1','1.0','1e0','1\n','1 ',' 1','١','１','NaN','Infinity','18446744073709551616','99999999999999999999','1'.repeat(1000000)])assert.throws(()=>owner.form({id,verified:true}),U0ValueError);
  assert.equal(calls,0);assert.equal(owner.form({id:'9007199254740993',verified:true}).id,9007199254740993n);assert.equal(calls,1);
 }finally{globalThis.BigInt=original;}
});
test('U06b accepts only the closed wire shape and exact native bigint ABI',()=>{
 for(const id of [1,0,-0,9007199254740992,NaN,Infinity,1n,null,{},new String('1')])assert.throws(()=>owner.form({id,verified:true} as any),U0ValueError);
 for(const verified of ['true',1,0,null,{},new Boolean(true)])assert.throws(()=>owner.form({id:'1',verified} as any),U0ValueError);
 for(const id of ['1',1,0,NaN,-1n,18446744073709551616n])assert.throws(()=>owner.copy({id,verified:true} as any),U0ValueError);
 for(const raw of [null,[],{id:'1'},{verified:true},{id:'1',verified:true,extra:0},Object.assign(Object.create({id:'1'}),{verified:true}),new Date()])assert.throws(()=>owner.form(raw as any),U0ValueError);
});
test('U06b rejects active or disguised input without invoking getters or coercion hooks',()=>{
 let calls=0;
 const active={get id(){calls++;return '1';},verified:true};
 const inherited=Object.assign(Object.create({get id(){calls++;return '1';}}),{verified:true});
 const proxy=new Proxy({id:'1',verified:true},{getPrototypeOf(){calls++;throw Error('trap');},ownKeys(){calls++;throw Error('trap');}});
 const hidden=Object.defineProperty({verified:true},'id',{value:'1',enumerable:false});
 const symbol=Object.assign({id:'1',verified:true},{[Symbol('extra')]:0});
 const coerced={id:{toString(){calls++;return '1';},valueOf(){calls++;return 1;}},verified:true};
 for(const raw of [active,inherited,proxy,hidden,symbol,coerced])assert.throws(()=>owner.form(raw as any),U0ValueError);
 const native={get id(){calls++;return 1n;},verified:true};assert.throws(()=>owner.copy(native),U0ValueError);assert.equal(calls,0);
});
test('U06b records own frozen data and never retain the mutable caller record',()=>{
 const raw={id:'31',verified:true};const value=owner.form(raw);raw.id='32';raw.verified=false;
 assert.equal(value.id,31n);assert.equal(value.verified,true);assert.deepEqual(Reflect.ownKeys(value),['id','verified']);
 for(const descriptor of Object.values(Object.getOwnPropertyDescriptors(value))){assert.ok('value' in descriptor);assert.equal(descriptor.writable,false);assert.equal(descriptor.configurable,false);}
 assert.throws(()=>{(value as {id:bigint}).id=32n;},TypeError);
 const nullInput=Object.assign(Object.create(null),{id:'32',verified:false});assert.equal(owner.form(nullInput).id,32n);
});
