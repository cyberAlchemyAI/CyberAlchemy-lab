import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {generateGenericCapabilityCodec as generate,generateGenericNativeVectorCodec as generateVector} from '../../src/generic/capability-codec.js';
import type {GenericValueSchemaV1} from '../../src/generic/computation-data-v1.js';
import type {ValueTypeV1} from '../../src/commerce/commerce-data-v1.js';
import {captureJson,captureSchemaJson} from '../../src/profile-engine/contracts.js';
const u64:ValueTypeV1={kind:'scalar',name:'UInt64'},bool:ValueTypeV1={kind:'scalar',name:'Bool'};
const options={id:'Example.Model.result',max_bytes:4096,max_items:16};
const encoder=new TextEncoder(),encode=(value:unknown)=>encoder.encode(JSON.stringify(value));
test('C03 finite native schema numbers do not weaken exact metadata capture',()=>{
 const schema={type:'number',minimum:-Number.MAX_VALUE,maximum:Number.MAX_VALUE};
 assert.throws(()=>captureJson(schema),/finite safely represented/);
 assert.equal((captureSchemaJson(schema) as any).maximum,Number.MAX_VALUE);
 assert.throws(()=>captureSchemaJson({type:'number',maximum:Infinity}));
 let getters=0;const hostile=Object.defineProperty({},'maximum',{enumerable:true,get(){getters++;return Number.MAX_VALUE;}});
 assert.throws(()=>captureSchemaJson(hostile));assert.equal(getters,0);assert.throws(()=>captureSchemaJson(new Proxy({},{})));
});
function universe(root:ValueTypeV1):GenericValueSchemaV1{return {schema_version:'craft.generic-values/v1-candidate',records:[],enums:[],refinements:[],collection_predicates:[],root};}
async function materialize(values:GenericValueSchemaV1,type=values.root,limits=options){
 const codec=generate(values,type,limits),directory=mkdtempSync(path.join(tmpdir(),'craft-capability-codec-'));
 try{const file=path.join(directory,'decoder.mjs');writeFileSync(file,codec.source);const module=await import(pathToFileURL(file).href);return {...codec,decode:module.decode};}finally{rmSync(directory,{recursive:true,force:true});}
}
test('C03 standalone UInt64 schema and original kernel preserve exact wire strings',async()=>{
 const codec=await materialize(universe(u64)),schema=codec.schema as any,pattern=new RegExp(schema.pattern,'u');
 assert.equal(codec.schema_sha256,createHash('sha256').update(JSON.stringify(codec.schema)).digest('hex'));
 assert.equal(codec.codec_sha256,createHash('sha256').update(codec.source).digest('hex'));
 assert.ok(Object.isFrozen(codec.schema));assert.doesNotMatch(codec.source,/from ['"](?:\.\.|\/home|.*src\/)/);
 for(const value of ['0','1','9007199254740993','18446744073709551614','18446744073709551615']){
  assert.ok(pattern.test(value),value);const result=codec.decode(encode(value));assert.equal(result.ok,true);assert.equal(result.value,value);assert.equal(new TextDecoder().decode(result.wire),JSON.stringify(value));
 }
 for(const value of ['-1','01','+1','1.0','1e2','18446744073709551616','99999999999999999999','100000000000000000000','1\n',' 1','']){
  assert.equal(pattern.test(value),false,value);assert.equal(codec.decode(encode(value)).ok,false,value);
 }
 for(const value of [0,1,1.25,1e100,9007199254740992,true,null,{},[]])assert.equal(codec.decode(encode(value)).ok,false);
 // Whole UInt64 boundary neighborhood exercises exact schema/decoder parity.
 for(let n=18446744073709551550n;n<=18446744073709551650n;n++)assert.equal(pattern.test(String(n)),codec.decode(encode(String(n))).ok,String(n));
});
test('C03 record field rename propagates to strict schema and decoder from one business type',async()=>{
 const root:ValueTypeV1={kind:'record',name:'Example.Decision'},values=universe(root);
 const record={name:'Example.Decision',role:'ValueObject' as const,fields:{approved:bool,score:u64},invariants:[],event_version:null,entity:null};
 const before=await materialize({...values,records:[record]});
 assert.equal(before.decode(encode({approved:true,score:'9007199254740993'})).ok,true);
 const renamed={...record,fields:{accepted:bool,score:u64}},after=await materialize({...values,records:[renamed]});
 assert.deepEqual((after.schema as any).required,['accepted','score']);assert.equal((after.schema as any).additionalProperties,false);
 assert.notEqual(after.schema_sha256,before.schema_sha256);assert.notEqual(after.codec_sha256,before.codec_sha256);
 assert.equal(after.decode(encode({accepted:true,score:'2'})).ok,true);assert.equal(after.decode(encode({approved:true,score:'2'})).ok,false);
 for(const raw of ['{"accepted":true,"score":"2","extra":false}','{"accepted":true}','{"accepted":true,"accepted":false,"score":"2"}','{"accepted":true,"\\u0061ccepted":false,"score":"2"}'])assert.equal(after.decode(encoder.encode(raw)).ok,false);
});
test('C03 finite string refinements, simple enum, List and Optional use established kernel validation',async()=>{
 const root:ValueTypeV1={kind:'record',name:'Example.Result'},values=universe(root);
 const record={name:'Example.Result',role:'ValueObject' as const,fields:{code:{kind:'refinement',name:'Example.Code'} as ValueTypeV1,state:{kind:'enum',name:'Example.State'} as ValueTypeV1,items:{kind:'list',element:u64,min_items:1,max_items:3} as ValueTypeV1,detail:{kind:'optional',element:{kind:'string',max_bytes:32,max_scalars:8}} as ValueTypeV1},invariants:[],event_version:null,entity:null};
 const refinement={name:'Example.Code',carrier:{kind:'string' as const,max_bytes:8,max_scalars:8},min_utf8_bytes:2,max_utf8_bytes:8,min_unicode_scalars:2,max_unicode_scalars:8,pattern:'^[A-Z]{2,8}$',normalization:'none' as const,equality:'exact-scalar-sequence' as const};
 const codec=await materialize({...values,records:[record],enums:[{name:'Example.State',variants:[{name:'Ready',wire:'ready',fields:{}},{name:'Done',wire:'done',fields:{}}]}],refinements:[refinement]});
 const valid={code:'AB',state:'ready',items:['1','18446744073709551615'],detail:'🦉'};
 const result=codec.decode(encode(valid));assert.equal(result.ok,true);assert.equal(result.value.state,'ready');assert.deepEqual(result.value.items,valid.items);assert.equal(result.value.detail,'🦉');assert.ok(Object.isFrozen(result.value));assert.ok(result.fuel_used>0);
 assert.equal(codec.decode(encode({...valid,detail:null})).ok,true);
 const stringSchema=(codec.schema as any).properties.detail.anyOf[0];assert.ok(new RegExp(stringSchema.pattern,'u').test('🦉'));assert.equal(new RegExp(stringSchema.pattern,'u').test('\ud800'),false);
 for(const delta of [{code:'A'},{code:'abcdef'},{code:'A\n'},{state:'Ready'},{items:[]},{items:['1','2','3','4']},{detail:'123456789'}])assert.equal(codec.decode(encode({...valid,...delta})).ok,false);
 const optional=await materialize({...values,records:[record],enums:[{name:'Example.State',variants:[{name:'Ready',wire:'ready',fields:{}}]}],refinements:[refinement]},{kind:'optional',element:root});
 assert.equal(optional.decode(encode(null)).ok,true);assert.equal(optional.decode(encode(valid)).ok,true);
});
test('C03 raw bytes reject malformed Unicode, hostile inputs and input/output bounds',async()=>{
 const type:ValueTypeV1={kind:'string',max_bytes:32,max_scalars:8},codec=await materialize(universe(type));
 for(const raw of ['"\\ud800"','"\\udfff"','"x" trailing','"x"\u0000','{"__proto__":true}', '"x"} , "extra": true, {"value":"y"'])assert.equal(codec.decode(encoder.encode(raw)).ok,false,raw);
 for(const raw of [new Uint8Array([34,0xc0,0xaf,34]),new Uint8Array([34,0xed,0xa0,0x80,34]),new Uint8Array([239,187,191,34,120,34])])assert.equal(codec.decode(raw).ok,false);
 for(const raw of ['"x"',{},new Proxy(new Uint8Array([1]),{}),new Uint8Array(new SharedArrayBuffer(2)),new ArrayBuffer(2)])assert.equal(codec.decode(raw).ok,false);
 let observed=false;const accessor={get value(){observed=true;throw Error('getter');}};assert.equal(codec.decode(accessor).ok,false);assert.equal(observed,false);
 const small=await materialize(universe(type),type,{...options,max_bytes:3});
 assert.equal(small.decode(encode('ab')).error.code,'InputBound');
 // Existing canonical encoder spells control characters with six bytes.
 assert.equal(small.decode(encoder.encode('"\t"')).ok,false);
 const outputBound=await materialize(universe(type),type,{...options,max_bytes:4});
 assert.equal(outputBound.decode(encoder.encode('"\\t"')).error.code,'OutputBound');
});
test('C03 unsupported semantics fail before artifacts with business selector diagnostics',()=>{
 const root:ValueTypeV1={kind:'record',name:'Example.Result'},values=universe(root),record={name:'Example.Result',role:'ValueObject' as const,fields:{count:u64},invariants:[],event_version:null,entity:null};
 const reject=(v:GenericValueSchemaV1,t:ValueTypeV1=root)=>assert.throws(()=>generate(v,t,options),(error:any)=>error.diagnostics?.[0]?.path===options.id&&/type/.test(error.diagnostics[0].message));
 reject({...values,records:[{...record,invariants:[{op:'literal',type:bool,value:true}]}]});
 reject({...values,records:[{...record,fields:{recursive:root}}]});reject(values);
 reject(values,{kind:'optional',element:{kind:'optional',element:u64}});
 reject(values,{kind:'string',max_bytes:10,max_scalars:10});
 reject({...values,enums:[{name:'Example.Tagged',variants:[{name:'One',wire:'one',fields:{count:u64}}]}]},{kind:'enum',name:'Example.Tagged'});
 const list:ValueTypeV1={kind:'list',element:u64,min_items:0,max_items:5};reject({...values,collection_predicates:[{type:list,rule:'Example.Rule'}]},list);
 reject({...values,collection_predicates:[{type:{max_items:5,min_items:0,element:u64,kind:'list'},rule:'Example.Rule'}]},list);
 reject(values,{kind:'outcome',state:u64,intent:u64,max_intents:1});
 let called=false;const hostile=Object.defineProperty({...values},'records',{get(){called=true;return [];}});assert.throws(()=>generate(hostile,root,options));assert.equal(called,false);
});

async function vectorCodec(dimensions:number,limits:{id:string;max_bytes:number;max_items?:number}=options){
 const codec=generateVector(dimensions,limits),directory=mkdtempSync(path.join(tmpdir(),'craft-native-vector-codec-'));
 try{const file=path.join(directory,'decoder.mjs');writeFileSync(file,codec.source);const module=await import(pathToFileURL(file).href);return Object.freeze({...codec,decode:module.decode});}finally{rmSync(directory,{recursive:true,force:true});}
}
test('C03 native vector is a finite dimension-checked technical result with binary64 canonical wire',async()=>{
 const values=[Math.fround(1/3),1/3,Number.MIN_VALUE,Number.MAX_VALUE,-Number.MAX_VALUE,0,-0,42.5];
 const codec=await vectorCodec(values.length),result=codec.decode(encode(values));
 assert.equal(result.ok,true);assert.deepEqual(codec.type,{kind:'native-vector',dimensions:values.length});
 assert.deepEqual(codec.schema,{type:'array',items:{type:'number',minimum:-Number.MAX_VALUE,maximum:Number.MAX_VALUE},minItems:values.length,maxItems:values.length});
 assert.equal(codec.schema_sha256,createHash('sha256').update(JSON.stringify(codec.schema)).digest('hex'));
 assert.equal(codec.codec_sha256,createHash('sha256').update(codec.source).digest('hex'));
 assert.ok(Object.isFrozen(codec));assert.ok(Object.isFrozen(codec.schema));assert.ok(Object.isFrozen(result.value));
 assert.deepEqual(result.value,values.map(n=>n===0?0:n));assert.equal(Object.is(result.value[6],-0),false);
 assert.equal(new TextDecoder().decode(result.wire),JSON.stringify(values));assert.doesNotMatch(codec.source,/from ['"](?:\.\.|\/home|.*src\/)/);
 const zero=await vectorCodec(2);assert.equal(new TextDecoder().decode(zero.decode(encoder.encode('[0,-0]')).wire),'[0,0]');
});
test('C03 native vector rejects dimensions, nonfinite numbers, wrong kinds and invalid UTF8 JSON',async()=>{
 const codec=await vectorCodec(2);
 for(const raw of ['[]','[1]','[1,2,3]','[1e999,0]','[-1e999,0]','[NaN,0]','[Infinity,0]','[-Infinity,0]','["1",0]','[null,0]','[true,0]','[[1],0]','[{},0]','{"0":1,"1":2}','1','null','[1,2,]','[1,2]trailing','["\\ud800",0]','[1,2]\u0000','[1,\t]'])assert.equal(codec.decode(encoder.encode(raw)).ok,false,raw);
 for(const raw of [new Uint8Array([91,0xc0,0xaf,44,48,93]),new Uint8Array([91,0xed,0xa0,0x80,44,48,93]),new Uint8Array([239,187,191,91,49,44,50,93])])assert.equal(codec.decode(raw).ok,false);
 for(const raw of ['[1,2]',[],{},new Proxy(new Uint8Array([1]),{}),new Uint8Array(new SharedArrayBuffer(2)),new ArrayBuffer(2)])assert.equal(codec.decode(raw).ok,false);
 let observed=false;const accessors={get byteLength(){observed=true;throw Error('getter');},get buffer(){observed=true;throw Error('getter');}};assert.equal(codec.decode(accessors).ok,false);assert.equal(observed,false);
 const shadowed=Object.defineProperty(encode([1,2]),'byteLength',{get(){observed=true;throw Error('getter');}});assert.equal(codec.decode(shadowed).ok,false);assert.equal(observed,false);
 const bounded=await vectorCodec(2,{id:'Example.Embed.result',max_bytes:5});assert.equal(bounded.decode(encoder.encode('[10,0]')).error.code,'InputBound');
 const expanding=await vectorCodec(1,{id:'Example.Embed.result',max_bytes:5});assert.equal(expanding.decode(encoder.encode('[1e3]')).error.code,'OutputBound');
});
test('C03 native vector declaration rejects unsupported dimensions and inconsistent bounds before output',()=>{
 for(const dimensions of [0,-1,1.25,NaN,Infinity,65537])assert.throws(()=>generateVector(dimensions,{id:'Example.Vector',max_bytes:1048576}));
 for(const limits of [{max_bytes:4},{max_bytes:1048577},{max_bytes:100,max_items:1},{max_bytes:100,max_items:65537},{max_bytes:100,unexpected:true}])assert.throws(()=>generateVector(2,{id:'Example.Vector',...limits}));
 const maximum=generateVector(65536,{id:'Example.Vector',max_bytes:131073});assert.equal(maximum.type.dimensions,65536);
 let called=false;const hostile=Object.defineProperty({id:'Example.Vector',max_bytes:100},'max_items',{get(){called=true;return 10;},enumerable:true});assert.throws(()=>generateVector(2,hostile));assert.equal(called,false);
});
