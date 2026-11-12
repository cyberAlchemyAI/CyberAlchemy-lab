import {readFileSync} from 'node:fs';
import {isDeepStrictEqual} from 'node:util';
import {verifyPlanningEvidence} from './evidence.mjs';
import {Snapshots,bind,sameBinding} from './snapshots.mjs';
import {nativePort} from './ports.mjs';
import {digest} from './verified-projection.mjs';
import {evaluate} from './kernel.mjs';
export async function deriveCarryForward(request,trust,database){
 const old=verifyPlanningEvidence(request.original_construction,trust,{historical:true});
 if(request.original_construction.operation!=='AssessConstructionEntry')throw Error('original-construction-entry-required');
 const original=old.input.value;
 const native=nativePort({action:'committed',store:request.original_native_store,operation:request.original_operation});
 const rawApproval=Buffer.from(request.original_approval_artifact,'base64');
 if(digest(rawApproval)!==original.permission.sha256||!isDeepStrictEqual(JSON.parse(rawApproval),native.approval)
   ||native.source_cut!==original.source_cut||!isDeepStrictEqual(native.targets,request.proposal.targets)
   ||!isDeepStrictEqual(native.proposal.schemas,request.proposal.schemas))throw Error('carry-forward-native-lineage-mismatch');
 const snapshots=new Snapshots(database,{readOnly:true});
 const asBinding=b=>({ref:b.ref??b.path,sha256:b.sha256,bytes:String(b.bytes)});
 try{
  const selected=snapshots.current(request.original_construction.scope);
  if(!selected)throw Error('carry-forward-authority-snapshot-required');
  const registry=JSON.parse(snapshots.material(selected.digest,'registry.json').bytes);
  const reviews=[];
  for(const review of original.definitions){
   const entry=registry.entries.find(e=>sameBinding(e.body,review.target));
   if(!entry)throw Error('carry-forward-definition-not-selected');
   const body=snapshots.material(selected.digest,entry.body.path);
   if(!sameBinding(body.binding,review.target))throw Error('carry-forward-body-mismatch');
   const receipt=snapshots.material(selected.digest,entry.owner_disposition.path);
   if(!sameBinding(receipt.binding,review.disposition.verification_receipt))throw Error('carry-forward-original-receipt-mismatch');
   const owner=JSON.parse(receipt.bytes);
   if(owner.source_cut!==review.source_cut||review.disposition.source_cut!==owner.source_cut
    ||owner.owner!==review.disposition.owner||owner.scope!==review.disposition.scope||owner.target!==entry.definition_id+'@'+entry.version)
     throw Error('original-review-receipt-context-mismatch');
   const fact={original_target:review.target,current_target:asBinding(entry.body),
    original_receipt:review.disposition.verification_receipt,current_receipt:asBinding(entry.owner_disposition),
    original_cut:owner.source_cut,current_cut:request.proposal.source_snapshot_digest,
    original_owner:review.disposition.owner,current_owner:owner.owner,original_scope:review.disposition.scope,current_scope:owner.scope,
    accepted:owner.outcome==='Accepted',authority_current:entry.standing==='admitted-current'&&registry.current_lookup[entry.definition_id]===owner.target};
   await evaluate('AssessReviewCarryForward',{value:fact});reviews.push(fact);
  }
  if(!trust.conformance?.specifications?.length)throw Error('current-conformance-specifications-unqualified');
  return {current_specifications:trust.conformance.specifications,current_obligations:trust.conformance.specifications.map(s=>s.obligation),original,current_cut:request.proposal.source_snapshot_digest,
   current_permission:bind('current-native-approval',Buffer.from(request.approval_artifact,'base64')),reviews};
 }finally{snapshots.close();}
}

export function verifyCurrentDefinitionReviews(value,request,trust,database){
 const snapshots=new Snapshots(database,{readOnly:true});
 try{
  const selected=snapshots.current(request.construction.scope);
  const registry=selected?JSON.parse(snapshots.material(selected.digest,'registry.json').bytes):null;
  const original=binding=>{
   const qualified=trust.materials?.[binding.ref??binding.path];
   let raw;
   if(qualified&&qualified.sha256===binding.sha256)raw=readFileSync(qualified.path);
   else if(selected)raw=snapshots.material(selected.digest,binding.ref??binding.path).bytes;
   else throw Error('original-review-material-unqualified');
   if(digest(raw)!==binding.sha256||raw.length!==Number(binding.bytes))throw Error('original-review-material-mismatch');
   return raw;
  };
  for(const target of request.proposal.targets.filter(t=>t.category==='definition')){
   const review=value.definitions.find(r=>r.disposition?.target&&r.target.sha256===r.disposition.target.sha256&&(()=>{
    try{const b=JSON.parse(original(r.target));return b.definition_id+'@'+b.version===target.version_ref;}catch{return false;}
   })());
   if(!review)throw Error('native-definition-original-review-required');
   const body=JSON.parse(original(review.target)),owner=JSON.parse(original(review.disposition.verification_receipt));
   const actual=target.record??body;
   if(!isDeepStrictEqual(body,actual)||owner.target!==target.version_ref||owner.outcome!=='Accepted'
    ||owner.source_cut!==review.source_cut||owner.source_cut!==review.disposition.source_cut
    ||owner.owner!==review.expected_owner||owner.owner!==review.disposition.owner
    ||owner.scope!==review.scope||owner.scope!==review.disposition.scope
    ||!sameBinding(owner.original,review.target))throw Error('original-review-receipt-context-mismatch');
   const authorization=JSON.parse(original(owner.authorization)),role=JSON.parse(original(owner.role_assignment));
   if(authorization.authorized!==true||!authorization.accepted_definitions?.some(i=>i.version===target.version_ref&&sameBinding(i.source,review.target))
    ||role.role_ref!==owner.owner||role.principal_ref!==owner.principal_ref||!sameBinding(role.basis,owner.authorization))
     throw Error('original-review-authority-unverified');
  }
 }finally{snapshots.close();}
}
