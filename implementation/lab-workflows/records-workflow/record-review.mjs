import {readFileSync} from 'node:fs';
import {isDeepStrictEqual} from 'node:util';
import {digest} from '../../lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {sameBinding} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
export function verifyRecordReviews(request,value,trust,native){
 const targets=request.proposal.targets.filter(t=>t.category==='artifact-instance');
 if(!targets.length)return [];
 const read=b=>{const selected=trust.materials?.[b.ref??b.path];if(!selected||selected.sha256!==b.sha256)throw Error('record-review-material-unqualified');const raw=readFileSync(selected.path);if(digest(raw)!==b.sha256||raw.length!==Number(b.bytes))throw Error('record-review-original-mismatch');return JSON.parse(raw);};
 if(!request.record_review_bundle)throw Error('record-owner-review-bundle-required');
 const artifactStage=value.stages.find(s=>s.stage==='Artifacts');
 if(!artifactStage||!sameBinding(artifactStage.subject,request.record_review_bundle))throw Error('record-review-not-in-construction-chain');
 const bundle=read(request.record_review_bundle);
 if(bundle.reviews.length!==targets.length||bundle.proposal_sha256!==digest(Buffer.from(JSON.stringify(request.proposal))))throw Error('record-review-target-closure');
 return targets.map(target=>{
  const review=bundle.reviews.find(r=>r.version_ref===target.version_ref);
  if(!review)throw Error('record-owner-review-required');
  const stored=native.projection.subjects[target.version_ref];
  if(stored&&(!isDeepStrictEqual(stored.record,target.record)||stored.carrier_ref!==target.carrier_ref))throw Error('record-review-native-original-mismatch');
  const body=read(review.body),decision=read(review.decision),auth=read(decision.authorization),role=read(decision.role_assignment);
  const contract=native.projection.contracts[target.carrier_ref],required=contract?.artifact?.instance_contract?.required_semantic_fields??[];
  const owners=['owner_ref','semantic_owner_ref','accountable_owner_ref'].filter(k=>required.includes(k)&&typeof body[k]==='string');
  if(owners.length!==1)throw Error('record-owner-member-ambiguous');
  const owner=body[owners[0]];
  if(!isDeepStrictEqual(body,target.record)||decision.decision_ref!==target.decision_ref||decision.target!==target.version_ref||!sameBinding(decision.original,review.body)||decision.outcome!=='Accepted'||decision.scope!==review.scope||(typeof body.scope_ref==='string'&&body.scope_ref!==review.scope)||decision.owner!==owner||decision.source_cut!==request.proposal.source_snapshot_digest||role.role_ref!==owner||role.principal_ref!==decision.principal_ref||!sameBinding(role.basis,decision.authorization)||auth.authorized!==true||!auth.accepted_records?.some(r=>r.version===target.version_ref&&r.scope===review.scope&&(!review.workspace||(r.workspace===review.workspace&&r.workspace_scope===review.workspace_scope))&&sameBinding(r.source,review.body)))throw Error('record-owner-authority-unverified');
  return {version:target.version_ref,owner,decision:review.decision};
 });
}
