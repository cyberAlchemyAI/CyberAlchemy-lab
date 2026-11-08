import test from 'node:test';
import assert from 'node:assert/strict';
import {dataDigest} from '../../src/profile-engine/contracts.js';
import {coreParentIdentityDigestV1,coreParentIdentityDigestTrustedV1,CoreParentDigestErrorV1,
 type CoreParentIdentityV1} from '../../src/commerce/commerce-core-parent-digest-v1.js';

const row=(path:string,link:string|null=null):CoreParentIdentityV1=>
 ({path,device:'2049',inode:'987654321',mode:link===null?'16877':'41471',link});
const invalid=(code:string)=>(error:unknown)=>error instanceof CoreParentDigestErrorV1&&error.code===code;

test('fast Core parent identity digest equals generic canonical digest for the closed shape',()=>{
 const cases:readonly (readonly CoreParentIdentityV1[])[]=[
  [],[row('/')],[row('/'),row('/home'),row('/home/user/project')],
  [row('/home/caf\u00e9/\u4e16\u754c'),row('/home/caf\u00e9/link','../\u96ea/\ud83e\uddad')],
  [row('/with \"quotes\" and \\ backslash'),row('/tab\tnewline\npath','../line\n\u0001')],
  [row('/lone-\ud800','\udc00')],
  [Object.create(null,Object.fromEntries(Object.entries(row('/null-prototype')).map(
    ([name,value])=>[name,{value,enumerable:true,writable:true,configurable:true}])))],
 ];
 for(const parents of cases){
  assert.equal(coreParentIdentityDigestV1(parents),dataDigest(parents));
  assert.equal(coreParentIdentityDigestTrustedV1(parents),dataDigest(parents));
 }
 const baseline=[row('/'),row('/root/file')],replacement=[row('/'),{...row('/root/file'),inode:'987654322'}];
 assert.notEqual(coreParentIdentityDigestV1(baseline),coreParentIdentityDigestV1(replacement));
});

test('fast Core parent digest rejects values outside the inert ancestor shape',()=>{
 assert.throws(()=>coreParentIdentityDigestV1([new Proxy(row('/'),{})]),invalid('InvalidParent'));
 assert.throws(()=>coreParentIdentityDigestV1(new Proxy([row('/')],{})),invalid('InvalidParents'));
 assert.throws(()=>coreParentIdentityDigestV1([Object.assign(Object.create(null),row('/'),{extra:'x'})]),invalid('InvalidParent'));
 assert.throws(()=>coreParentIdentityDigestV1([{...row('/'),inode:'not-an-inode'}]),invalid('InvalidParent'));
 const accessor={...row('/')};Object.defineProperty(accessor,'path',{get(){throw Error('getter must not run');},enumerable:true});
 assert.throws(()=>coreParentIdentityDigestV1([accessor]),invalid('InvalidParent'));
 const sparse=new Array<CoreParentIdentityV1>(1);
 assert.throws(()=>coreParentIdentityDigestV1(sparse),invalid('InvalidParents'));
 const polluted=[row('/')];Object.defineProperty(polluted,'extra',{value:true,enumerable:false});
 assert.throws(()=>coreParentIdentityDigestV1(polluted),invalid('InvalidParents'));
});
