import test from 'node:test';
import assert from 'node:assert/strict';
import * as alch from '../src/index.js';
import type {BusinessParserOwnerV2,BusinessResolverOwnerV2,BusinessInputOwnerV2,BusinessRequestStagesOwnerV2,BusinessPureGenerationOwnerV2,BusinessDirectApplicationOwnerV2,U0HandlerAssetOwnerV2,PreparedBusinessReviewV2,AcceptedBusinessReviewV2,BusinessRecipeSelectionV2,BusinessEarlyRequestsV2,AuthoringBusinessInputV2,ImportedU0CallableV2,U0ResolvedNativeBasis,BoundU0EntryV2} from '../src/business-authoring-public-v2.js';
// Checked by the actual Alch typecheck. Not called and does not construct owner handles.
// Open Questions: Core docs/U0-SHARED-CONTRACTS.md.
function checkedProducerOrder(parser:BusinessParserOwnerV2,resolver:BusinessResolverOwnerV2,inputOwner:BusinessInputOwnerV2,requests:BusinessRequestStagesOwnerV2,generator:BusinessPureGenerationOwnerV2,application:BusinessDirectApplicationOwnerV2,handler:U0HandlerAssetOwnerV2,selection:BusinessRecipeSelectionV2,review:PreparedBusinessReviewV2,accepted:AcceptedBusinessReviewV2,early:BusinessEarlyRequestsV2,basis:U0ResolvedNativeBasis,callable:ImportedU0CallableV2,bound:BoundU0EntryV2){
 const parsed=parser.parse('source');const resolved=resolver.resolve(parsed);
 resolver.assertCurrent(resolved);
 // @ts-expect-error parsed data has not been resolved.
 resolver.assertCurrent(parsed);
 const input:AuthoringBusinessInputV2=inputOwner.form(selection,'model',accepted,early);
 // @ts-expect-error a review has no captured accepted decision custody.
 inputOwner.form(selection,'model',review,early);
 // @ts-expect-error bound request graph is not an early intent.
 inputOwner.form(selection,'model',accepted,bound);
 const checked=application.check(input);const emitted=generator.generate(checked);
 void generator.importGenerated(emitted,'/actual-generated-module.mjs');
 void requests.bindLate(early,callable,basis);
 // @ts-expect-error emitted source is not an actual generated/imported callable.
 void requests.bindLate(early,emitted,basis);
 // @ts-expect-error an async evaluator violates the synchronous native ABI.
 handler.create(async value=>({kind:'completed',value}),basis.configuration,{rejection_code:'authored-code'});
}
void checkedProducerOrder;
test('J00 Alch public source exposes local successor contracts beside v1',()=>{
 assert.equal(alch.BUSINESS_SPEC_V2,'alchlang.business-spec/v2-candidate');
 assert.equal(alch.BUSINESS_STAGES_V2,'craft.business-authoring-stages/v2-candidate');
 assert.equal(alch.BUSINESS_CONTRACT_RESOURCES_V2.length,10);
 assert.equal(alch.U0_NATIVE_ABI,'craft.u0.pure-submission/v1-candidate');
 assert.equal(typeof alch.parseBusinessSource,'function');
 assert.equal(typeof alch.alchDirectExecutableDigestV2,'function');
 assert.equal(Object.hasOwn(alch,'checkU0WireConfiguration'),false,'Core runtime checker is not a frontend data mirror');
 assert.equal(Object.hasOwn(alch,'inventoryBusinessSourceContractV2'),false);
});
