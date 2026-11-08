import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, rmSync, unlinkSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {build} from './C11-source-fixture.mjs';
import {GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES} from '../../src/generic/composition-capabilities.ts';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.ts';
import {createGenericEventTransactionSourceContract} from '../../src/generic/transaction-source.ts';
import {captureExternalProfile,generateExternalBusinessSources} from '../../src/generic/external-read-profile.ts';
import {createExternalApiComposition} from '../../src/generic/external-read-source.ts';
import {reconstructCoreCommerceSources} from '../../src/commerce/commerce-core-reconstruction.ts';

const receiver=`module AuditService version 1

value-object ApprovalNotice:
  approvalId UInt64
  approved Bool

mapping FromApprovalCommittedPayload:
  input payload ReviewDesk.ApprovalCommittedPayload
  target ApprovalNotice
  total true
  field approvalId <- payload.approvalId
  field approved <- payload.approved

entity AuditRecord:
  id UInt64
  approved Bool
  identity id

mapping ToAuditRecord:
  input notice ApprovalNotice
  target AuditRecord
  total true
  field id <- notice.approvalId
  field approved <- notice.approved

operation RecordApproval:
  input notice ApprovalNotice
  output AuditRecord
  transaction Record:
    atomic-participants AuditRecord
    create record AuditRecord from ToAuditRecord(notice)
    on-unique-conflict reject audit-conflict
    on-proven-rollback fail storage-rolled-back
    on-unknown-commit fail outcome-unknown
  return record

entry AuditService.RecordApprovedEntry:
  invokes AuditService.RecordApproval
  interaction event ReviewDesk.ApprovalCommitted
  bind notice <- FromApprovalCommittedPayload(payload)
  access:
    authenticated relay
    permission audit-request.record
    auth-resource audit-request
    auth-action record
    auth-scope audit-service
`;

function replaceFile(root,file,from,to){const p=path.join(root,file),text=readFileSync(p,'utf8');assert.ok(text.includes(from),`${file}: source marker`);writeFileSync(p,text.replace(from,to));}

test('C12 V4 composes C11 external read and durable write with a checked Event handoff',()=>{
 const {root}=build('ReviewDesk');
 try{
  writeFileSync(path.join(root,'audit-service.alch'),receiver);
  replaceFile(root,'business.alch','    atomic-participants StoredRequest\n','    atomic-participants StoredRequest, ApprovalCommitted\n');
  replaceFile(root,'business.alch','      value <- ApplyDecision(request=stored.value,decision=decision)\n','      value <- ApplyDecision(request=stored.value,decision=decision)\n    emit ApprovalCommitted payload ToApprovalCommittedPayload(decision)\n');
  writeFileSync(path.join(root,'business.alch'),readFileSync(path.join(root,'business.alch'),'utf8')+`
value-object ApprovalCommittedPayload:
  approvalId UInt64
  approved Bool

mapping ToApprovalCommittedPayload:
  input decision Decision
  target ApprovalCommittedPayload
  total true
  field approvalId <- decision.decisionId
  field approved <- decision.approved

event ApprovalCommitted version 1:
  payload ApprovalCommittedPayload
  from ReviewDesk.CommitRequestApproval
  delivered-to AuditService.RecordApprovedEntry
`);
  replaceFile(root,'application.alch','  source business.alch\n','  source business.alch\n  source audit-service.alch\n');
  replaceFile(root,'application.alch','  service ReviewDeskService module ReviewDesk\n','  service ReviewDeskService module ReviewDesk\n  service AuditService module AuditService\n');
  const profilePath=path.join(root,'contracts/selected-profile.json'),profile=JSON.parse(readFileSync(profilePath,'utf8'));
  profile.schema_version='craft.generic-event-profile/v1-candidate';profile.capabilities=[...GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES];profile.storage='sqlite-fenced-event-handoff/v1-candidate';profile.services.push({id:'AuditService',module:'AuditService'});profile.string_policy={max_utf8_bytes:256,max_scalars:256};profile.event_handoff={transport:'process-local-checked-envelope/v1-candidate',delivery:'durable-at-least-once/v1-candidate'};
  writeFileSync(profilePath,JSON.stringify(profile,null,2)+'\n');
  const generationPath=path.join(root,'contracts/external-generation.json'),generation=JSON.parse(readFileSync(generationPath,'utf8'));
  generation.authored_paths.push('audit-service.alch');
  const application=readFileSync(path.join(root,'application.alch'),'utf8'),oldGenerated=application.match(/generated\/external-[a-f0-9]{64}\.alch/)?.[0];assert.ok(oldGenerated);
  const baseApp=application.split('\n').filter(line=>!line.includes('source generated/external-')&&!line.includes('external-bindings contracts/external-profile.json')&&!line.includes('external-config contracts/external-config.json')).join('\n');
  const business=readFileSync(path.join(root,'business.alch'),'utf8'),sources=[{path:'business.alch',text:business},{path:'audit-service.alch',text:receiver},{path:'application.alch',text:baseApp},{path:'generated/auth-context.alch',text:readFileSync(path.join(root,'generated/auth-context.alch'),'utf8')}];
  const external=captureExternalProfile(path.join(root,'contracts/external-profile.json'),root),regenerated=generateExternalBusinessSources(external,reconstructCoreCommerceSources(sources,'event-handoff-entry'),sources.filter(s=>s.path==='business.alch'||s.path==='audit-service.alch'),sources,'event-handoff-entry');
  unlinkSync(path.join(root,oldGenerated));for(const f of regenerated.files)writeFileSync(path.join(root,f.path),f.text);
  writeFileSync(path.join(root,'application.alch'),application.replace(oldGenerated,regenerated.files[0].path));
  const compositionText=JSON.stringify(createExternalApiComposition(regenerated.bindings),null,2)+'\n';writeFileSync(path.join(root,'contracts/external-composition.json'),compositionText);
  const sha=text=>createHash('sha256').update(text).digest('hex');generation.bindings=regenerated.bindings;generation.calls=regenerated.calls;generation.files=generation.files.filter(f=>f.path!==oldGenerated&&f.path!=='contracts/external-composition.json');for(const f of [...regenerated.files,{path:'contracts/external-composition.json',text:compositionText}])generation.files.push({path:f.path,sha256:sha(f.text),bytes:Buffer.byteLength(f.text)});
  writeFileSync(generationPath,JSON.stringify(generation,null,2)+'\n');
  const owner=createCoreCommerceSourceOwner('event-handoff-entry'),app=createGenericEventTransactionSourceContract(owner.inspect(owner.prepare(root))).contract;
  assert.equal(app.admission_mode,'event-handoff-entry');assert.ok(app.external_bindings.length>0);assert.ok(app.write_bindings.length>0);assert.equal(app.event_bindings.length,1);assert.ok(app.identity_limits);
  assert.ok(app.stateful_operations.some(o=>o.preflight.some(s=>s.kind==='read-external')&&o.preflight.some(s=>s.kind==='write-external')&&o.transaction.body.some(s=>s.kind==='emit-event')));
 }finally{rmSync(path.dirname(root),{recursive:true,force:true});}
});
