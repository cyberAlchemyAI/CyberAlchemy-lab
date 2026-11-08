/** Binary representation controls only; input cells are already-validated data
 * fixtures. Genuine source/store/codec tests are in the native UOW suite.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/PHYSICAL-STORAGE-CONTEXT-05.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {encodeCommerceSqliteTypedTupleV1} from '../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.js';
import type {ValueTypeV1} from '../src/commerce/commerce-data-v1.js';
const text:ValueTypeV1={kind:'string',max_bytes:128,max_scalars:128};
const field=(name:string,value:string,type:ValueTypeV1=text)=>({name,type,cell:JSON.stringify(value)});
const encoded=(entity:string,fields:ReturnType<typeof field>[])=>encodeCommerceSqliteTypedTupleV1(entity,fields,4096);
test('fixed key wire has an explicit magic, byte lengths, field count and exact type descriptor',()=>{
 const key=encoded('X',[field('id','a',{kind:'string',max_bytes:2,max_scalars:2})]);
 assert.equal(key.toString('hex'),'434b31000000000158000000010000000269640000002f7b226b696e64223a22737472696e67222c226d61785f6279746573223a322c226d61785f7363616c617273223a327d00000003226122');
});
test('exact two-field tuples cannot collide at delimiter, empty, NUL or Unicode boundaries',()=>{
 const atoms=['','a','b','a:b','é','é','\u0000','🧪'],seen=new Set<string>();
 for(const a of atoms)for(const b of atoms){const key=encoded('Two',[field('a',a),field('b',b)]).toString('hex');assert.equal(seen.has(key),false,JSON.stringify([a,b]));seen.add(key);}
 assert.equal(seen.size,64);
});
test('entity, field name, tuple arity and exact type identity participate in key equality',()=>{
 const base=encoded('X',[field('id','1')]),variants=[encoded('Y',[field('id','1')]),encoded('X',[field('other','1')]),encoded('X',[field('id','1',{kind:'literal',value:'1'})]),encoded('X',[field('id','1',{kind:'scalar',name:'UInt64'})]),encoded('X',[field('id','1'),field('second','')])];
 for(const key of variants)assert.notDeepEqual(key,base);
 assert.deepEqual(encoded('X',[field('id','1',{max_scalars:128,max_bytes:128,kind:'string'})]),base);
});
test('lengths count UTF8 bytes and neither normalize nor case-fold input cells',()=>{
 const a=encoded('X',[field('id','é')]),b=encoded('X',[field('id','é')]);assert.notDeepEqual(a,b);assert.notDeepEqual(encoded('X',[field('id','A')]),encoded('X',[field('id','a')]));
 const changed=encoded('X',[field('id','é')]);changed.fill(0);assert.deepEqual(encoded('X',[field('id','é')]),a);
});
test('key byte bounds and malformed Unicode fail before returning a tuple',()=>{
 assert.throws(()=>encodeCommerceSqliteTypedTupleV1('X',[field('id','a')],8),(e:any)=>e.code==='StorageBound');
 assert.throws(()=>encoded('X',[{name:'id',type:text,cell:'\ud800'}]),(e:any)=>e.code==='StorageType');
 assert.throws(()=>encodeCommerceSqliteTypedTupleV1('X',[field('id','a')],Number.NaN),(e:any)=>e.code==='StorageBound');
});
