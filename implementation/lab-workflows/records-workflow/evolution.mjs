import {isDeepStrictEqual} from 'node:util';
import {verifyPlanningEvidence} from '../../lab-runtime/alchlang/shared-records/evidence.mjs';
import {sameBinding} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
import {digest} from '../../lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {semanticDigest} from '../definition-catalog/kernel.mjs';
import {enforce} from './kernel.mjs';
export async function reviewEvolution(packet,trust,read){
 if(packet.operation!=='ReviewDefinitionEvolution')throw Error('evolution-review-operation-required');
 const {input}=verifyPlanningEvidence(packet,trust),v=input.value;
 const original=b=>{const raw=read(b);if(digest(raw)!==b.sha256||raw.length!==Number(b.bytes))throw Error('evolution-original-binding-mismatch');return JSON.parse(raw);};
 const previous=original(v.previous),target=original(v.target),receipt=original(v.owner_decision),authorization=original(receipt.authorization),role=original(receipt.role_assignment);
 const decision=authorization.accepted_definitions?.find(e=>e.version===target.definition_id+'@'+target.version&&sameBinding(e.source,v.target));
 const changes=[];
 if(semanticDigest(previous)!==semanticDigest(target))changes.push('Meaning');
 if(previous.term!==target.term)changes.push('Name');
 if(previous.semantic_owner_ref!==target.semantic_owner_ref)changes.push('Owner');
 if(v.previous_home!==v.target_home)changes.push('Custody');
 await enforce('EnforceEvolution',{identity_preserved:previous.definition_id===target.definition_id,version_fresh:previous.version!==target.version,previous_bound:sameBinding(receipt.previous,v.previous),target_bound:sameBinding(receipt.original,v.target),owner_decision_verified:receipt.outcome==='Accepted'&&receipt.owner===target.semantic_owner_ref&&receipt.target===target.definition_id+'@'+target.version&&role.role_ref===receipt.owner&&role.principal_ref===receipt.principal_ref&&sameBinding(role.basis,receipt.authorization)&&authorization.authorized===true,authority_scope_verified:receipt.scope===target.scope.authority_scope_ref&&receipt.source_cut===packet.cut&&!!decision&&decision.home===v.target_home,actual_changes:changes,authorized_changes:decision?.authorized_changes??[]});
 if(changes.includes('Owner')&&!v.previous_owner_consent)throw Error('previous-owner-transfer-consent-required');
 if(v.previous_owner_consent){
  const consent=original(v.previous_owner_consent);
  if(consent.owner!==previous.semantic_owner_ref||consent.outcome!=='Accepted'||consent.scope!==previous.scope.authority_scope_ref||consent.source_cut!==packet.cut||!sameBinding(consent.previous,v.previous)||!sameBinding(consent.original,v.target)||!consent.authorization||!consent.role_assignment)throw Error('previous-owner-consent-mismatch');
  const oldAuthority=original(consent.authorization),oldRole=original(consent.role_assignment);
  if(oldAuthority.authorized!==true||oldRole.role_ref!==previous.semantic_owner_ref||oldRole.principal_ref!==consent.principal_ref||!sameBinding(oldRole.basis,consent.authorization)||!oldAuthority.accepted_transfers?.some(t=>sameBinding(t.previous,v.previous)&&sameBinding(t.target,v.target)&&t.from_owner===previous.semantic_owner_ref&&t.to_owner===target.semantic_owner_ref&&t.home===v.target_home))throw Error('previous-owner-transfer-authority-unverified');
 }
 return {previous,target,home:v.target_home,previous_home:v.previous_home,changes,review:packet};
}
