import test from 'node:test';
import assert from 'node:assert/strict';
import {createCommerceGeneratedReadSetScopeV1} from '../src/commerce/commerce-generated-read-set-v1.js';

const code=(name:string)=>(error:any)=>error?.code===name;

test('generated read-set custody closes before writes and rejects foreign paths and leases',()=>{
 const sites={
  '$.body[1]':{kind:'read-set',before_writes:true},
  '$.body[1].body[0]':{kind:'read'},
  '$.body[2]':{kind:'transaction'},
 };
 let current=true;
 const owner=createCommerceGeneratedReadSetScopeV1(sites,()=>{if(!current)throw Object.assign(new Error('StaleOwner'),{code:'StaleOwner'});});
 const lease=owner.open('$.body[1]');
 owner.assertRead('$.body[1].body[0]');
 assert.throws(()=>owner.assertWritable(),code('ReadSetStillOpen'));
 assert.throws(()=>owner.assertRead('$.body[2]'),code('ForeignScope'));
 assert.throws(()=>owner.close(Object.freeze({kind:'original-generated-read-set-lease/v1-candidate'})),code('ForeignScope'));
 owner.close(lease);
 owner.assertWritable();owner.assertReleased();
 assert.throws(()=>owner.close(lease),code('ForeignScope'));
 assert.throws(()=>owner.open('$.body[2]'),code('ForeignScope'));
 current=false;
 assert.throws(()=>owner.open('$.body[1]'),code('StaleOwner'));
});
