/** Private source/paid-model/approval custody around the existing typed Alch
 * admission kernel. Business predicates remain authored policies/operations.
 * Open Questions: goals/plans/craft-service-profile-extensions-2026-11-02/DESIGN.md. */
import {assert,sha256,u64} from '../shared.mjs';
import {isServiceApplication} from './compiler.mjs';
import {serviceFamilyDescriptor as support} from './families/support.mjs';
import {serviceFamilyDescriptor as invoice} from './families/invoice.mjs';
import {serviceFamilyDescriptor as marketing} from './families/marketing.mjs';
const approvalStages=Object.freeze(Object.fromEntries([support,invoice,marketing].map(descriptor=>[descriptor.family,descriptor.approvalStages])));
export async function serviceAdmission({gateway,access,actor,snapshot,proposal,wire,technical={},previous,stage}){
 assert(isServiceApplication(access.profile),'UnsupportedCapability','finite business-only service');
 const name=typeof stage==='string'?stage:stage?.name;assert(access.profile.stages.some(item=>item.name===name),'InvalidContract','actual selected service stage');
 const origin=gateway.verifyServiceCandidate(snapshot,{wire,candidateOrigin:previous?.candidateOrigin});
 assert(origin.outputDigest===sha256(wire),'ForeignOwner','actual original confirmed model candidate');
 if(!approvalStages[access.profile.businessInputContract].includes(name)){
  gateway.disclose(snapshot,wire);return {domain:gateway.review(snapshot,{proposal,wire,technical}),approvalDeadlineMs:Number.MAX_SAFE_INTEGER};
 }
 const checked=gateway.executionReview(snapshot,{proposal,wire,technical,candidateOrigin:previous.candidateOrigin}),evaluated=await access.admitExecution(actor,checked.execution);
 assert(evaluated.ok,'SourceUnavailable','original protected typed execution admission');
 if(evaluated.outcome.kind!=='Returned')return {denied:evaluated.outcome.code};
 assert(evaluated.outcome.value===true,'InvalidContract','typed execution admission returns true only');
 const source=gateway.inspect(snapshot),family=access.profile.businessInputContract;
 if(family==='customer-support/domain-v1'){
  const review=source.sources.review?.json;
  if(!review||review.outputDigest!==origin.outputDigest||review.manifestDigest!==origin.manifestDigest)return {denied:'content-review-required'};
 }
 if(family==='invoice-draft/domain-v1'){
  if(source.facts.destinationAllowed!==true)return {denied:'destination-denied'};
  const window=source.sources.dispatchWindow?.json;
  assert(window,'InvalidContract','original invoice dispatch window');
  if(u64(window.createdAt)>u64(checked.execution.now)||u64(window.expiresAt)<=u64(checked.execution.now))return {denied:'idempotency-expired'};
  if(!previous.accepted)return {denied:'document-review-required'};
  return {...checked,approvalDeadlineMs:Math.min(checked.approvalDeadlineMs,Number(u64(window.expiresAt)))};
 }
 if(family==='marketing-campaign/domain-v1'){
  if(source.approval.approvedAudienceDigest!==source.sources.preferences?.sha256)return {denied:'audience-preference-changed'};
  if(u64(source.facts.scheduleAt)<=u64(checked.execution.now))return {denied:'schedule-expired'};
 }
 return checked;
}
