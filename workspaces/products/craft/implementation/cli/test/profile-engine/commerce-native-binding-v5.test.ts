/** Public binding boundary regressions. Valid seven-operation execution is
 * separately exercised against actual built public SDKs, never source tokens.
 * Open Questions: docs/COMMERCE-SDK-V5.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {commerceNativeDispatchV5,createCommerceNativeOwnerV5,assertCommerceNativeOwnerV5} from '../../src/profile-engine/commerce-native-v5.js';
import {captureCommercePublicSdkV5} from '../../src/profile-engine/commerce-sdk-physical-v5.js';

test('all reusable ABI operations reject outside a private original source/output context',()=>{
 let touched=0;const input=new Proxy({}, {get(){touched++;throw Error('must not read unbound input');},getPrototypeOf(){touched++;throw Error('must not inspect unbound input');}});
 for(const method of Object.values(commerceNativeDispatchV5))assert.throws(()=>method(input),/original post-basis source\/output binding/);
 assert.equal(touched,0);
});
test('a reported SDK inspection or matching kind cannot construct a native owner',()=>{
 assert.throws(()=>createCommerceNativeOwnerV5({kind:'original-commerce-public-sdk-closure/v5-candidate'} as any,{} as any),/original public SDK closure token/);
 assert.throws(()=>assertCommerceNativeOwnerV5({kind:'original-commerce-native-owner/v5-candidate'}),/original commerce native owner/);
});
test('source execution cannot substitute for an actual built public SDK',async()=>{
 await assert.rejects(()=>captureCommercePublicSdkV5('/missing-but-never-resolved'),/actual built public SDK required/);
});
test('public generic dispatch surface has exactly the seven finite methods and is immutable',()=>{
 assert(Object.isFrozen(commerceNativeDispatchV5));
 assert.deepEqual(Object.keys(commerceNativeDispatchV5).sort(),['checkCommerceSchema','decodeCommerceValue','encodeCommerceValue','copyCommerceValue','checkCommerceComputation','compileCommerceComputation','evaluateCommerceComputation'].sort());
 assert.throws(()=>Object.assign(commerceNativeDispatchV5,{checkCommerceSchema:()=>({ok:true,value:{}})}));
});
