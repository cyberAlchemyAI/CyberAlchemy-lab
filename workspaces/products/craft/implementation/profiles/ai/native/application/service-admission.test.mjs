/** Dispatch-window and stage-specific guard checks; original model receipts and
 * generated typed kernel are covered by service-origin/families invoice tests.
 * Open Questions: goals/plans/craft-service-profile-extensions-2026-11-02/DESIGN.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {serviceAdmission} from './service-admission.mjs';
import {sha256} from '../shared.mjs';
function fixture(family){
 const wire=new TextEncoder().encode('{}'),origin={outputDigest:sha256(wire),manifestDigest:'a'.repeat(64)},calls={receipt:0,disclosure:0,kernel:0},source={facts:{destinationAllowed:true,scheduleAt:'300'},approval:{approvedAudienceDigest:'preferences-sha'},sources:{dispatchWindow:{json:{createdAt:'90',expiresAt:'150'}},review:{json:{outputDigest:origin.outputDigest,manifestDigest:origin.manifestDigest}},preferences:{sha256:'preferences-sha'}}},context={execution:{now:'100'},domain:{business:'clean'},approvalDeadlineMs:200};
 const access={profile:{businessInputContract:family,stages:['review','reply','draftPosting','createDraft','setContent','schedule','metrics'].map(name=>({name}))},async admitExecution(){calls.kernel++;return {ok:true,outcome:{kind:'Returned',value:true}};}};
 const gateway={verifyServiceCandidate(){calls.receipt++;return origin;},disclose(){calls.disclosure++;},review(){return context.domain;},executionReview(){return context;},inspect(){return source;}};
 return {calls,source,access,gateway,origin,args:{gateway,access,actor:{},snapshot:{},proposal:{},wire,previous:{accepted:true,candidateOrigin:'persisted-original'}}};
}
test('nonfinal marketing draft mutations require original candidate and release, without premature human approval',async()=>{
 const f=fixture('marketing-campaign/domain-v1');await serviceAdmission({...f.args,stage:'createDraft'});assert.equal(f.calls.receipt,1);assert.equal(f.calls.disclosure,1);assert.equal(f.calls.kernel,0);
 f.gateway.verifyServiceCandidate=()=>{throw Object.assign(Error('original model receipt missing'),{code:'ForeignOwner'});};await assert.rejects(serviceAdmission({...f.args,stage:'setContent'}),{code:'ForeignOwner'});assert.equal(f.calls.kernel,0);
});
test('invoice typed approval expires at the earlier original dispatch-window deadline',async()=>{
 const f=fixture('invoice-draft/domain-v1'),admitted=await serviceAdmission({...f.args,stage:'draftPosting'});assert.equal(admitted.approvalDeadlineMs,150);assert.equal(f.calls.kernel,1);assert.equal(f.args.previous.accepted,true);
 f.source.sources.dispatchWindow.json.expiresAt='100';assert.equal((await serviceAdmission({...f.args,stage:'draftPosting'})).denied,'idempotency-expired');
});
test('support content review is bound to the actual original candidate and full manifest',async()=>{
 const f=fixture('customer-support/domain-v1');f.source.sources.review.json.outputDigest='b'.repeat(64);assert.equal((await serviceAdmission({...f.args,stage:'reply'})).denied,'content-review-required');assert.equal(f.calls.kernel,1);
});
test('schedule admission rejects changed audience custody and expired scheduling without affecting draft formation',async()=>{
 const f=fixture('marketing-campaign/domain-v1');f.source.approval.approvedAudienceDigest='old';assert.equal((await serviceAdmission({...f.args,stage:'schedule'})).denied,'audience-preference-changed');f.source.approval.approvedAudienceDigest='preferences-sha';f.source.facts.scheduleAt='100';assert.equal((await serviceAdmission({...f.args,stage:'schedule'})).denied,'schedule-expired');assert.equal(f.calls.kernel,2);
});
