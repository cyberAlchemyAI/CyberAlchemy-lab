/** Assembly rejects DTO owners before inspecting caller-supplied parents.
 * Accepted installed replay is qualified separately against real public bytes.
 * Open Questions: docs/COMMERCE-SDK-V5.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createCommercePrefixStagesV5} from '../../src/profile-engine/commerce-prefix-stages-v5.js';
import {commerceNativeStageParentsV5} from '../../src/profile-engine/commerce-native-v5.js';

test('a forged native owner cannot inject callable stage parents',()=>{
 let touched=0;
 const forgery=new Proxy({},{get(){touched++;throw Error('untrusted native callback invoked');}});
 assert.throws(()=>createCommercePrefixStagesV5(forgery as any),/original commerce native owner/);
 assert.equal(touched,0);
});
test('a prefix kind or JSON cannot substitute for an original native owner',()=>{
 let touched=0;
 const prefix=new Proxy({kind:'original-post-basis-commerce-source-prefix/v5-candidate'},{get(){touched++;throw Error('untrusted prefix inspected');}});
 assert.throws(()=>commerceNativeStageParentsV5({kind:'original-commerce-native-owner/v5-candidate'},prefix as any),/original commerce native owner/);
 assert.equal(touched,0);
});
