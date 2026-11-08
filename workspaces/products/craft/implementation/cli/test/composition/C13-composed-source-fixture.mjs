import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,unlinkSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {build} from './C11-source-fixture.mjs';
import {GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES} from '../../src/generic/composition-capabilities.ts';
import {captureExternalProfile,generateExternalBusinessSources} from '../../src/generic/external-read-profile.ts';
import {createExternalApiComposition} from '../../src/generic/external-read-source.ts';
import {reconstructCoreCommerceSources} from '../../src/commerce/commerce-core-reconstruction.ts';
const sha=value=>createHash('sha256').update(value).digest('hex');
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

function replace(root,file,from,to){const p=path.join(root,file),text=readFileSync(p,'utf8');assert.ok(text.includes(from),`${file}: expected fixture marker`);writeFileSync(p,text.replace(from,to));}

export function composedFixture(extendBusiness=''){
 const {root}=build('ReviewDesk');
 writeFileSync(path.join(root,'audit-service.alch'),receiver);
 replace(root,'business.alch','    atomic-participants StoredRequest\n','    atomic-participants StoredRequest, ApprovalCommitted\n');
 replace(root,'business.alch','      value <- ApplyDecision(request=stored.value,decision=decision)\n','      value <- ApplyDecision(request=stored.value,decision=decision)\n    emit ApprovalCommitted payload ToApprovalCommittedPayload(decision)\n');
 replace(root,'business.alch','entry ReviewDesk.ReadStoredRequestEntry:\n  invokes ReviewDesk.ReadStoredRequest\n  interaction request-response\n  access:\n    authenticated customer','entry ReviewDesk.ReadStoredRequestEntry:\n  invokes ReviewDesk.ReadStoredRequest\n  interaction request-response\n  access:\n    authenticated operator');
 replace(root,'business.alch','entry ReviewDesk.CommitRequestApprovalEntry:\n  invokes ReviewDesk.CommitRequestApproval\n  interaction request-response\n  access:\n    authenticated customer','entry ReviewDesk.CommitRequestApprovalEntry:\n  invokes ReviewDesk.CommitRequestApproval\n  interaction request-response\n  access:\n    authenticated operator');
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
 if(extendBusiness)writeFileSync(path.join(root,'business.alch'),readFileSync(path.join(root,'business.alch'),'utf8')+extendBusiness);
 replace(root,'application.alch','  source business.alch\n','  source business.alch\n  source audit-service.alch\n');
 replace(root,'application.alch','  service ReviewDeskService module ReviewDesk\n','  service ReviewDeskService module ReviewDesk\n  service AuditService module AuditService\n');
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
 generation.bindings=regenerated.bindings;generation.calls=regenerated.calls;generation.files=generation.files.filter(f=>f.path!==oldGenerated&&f.path!=='contracts/external-composition.json');for(const f of [...regenerated.files,{path:'contracts/external-composition.json',text:compositionText}])generation.files.push({path:f.path,sha256:sha(f.text),bytes:Buffer.byteLength(f.text)});
 writeFileSync(generationPath,JSON.stringify(generation,null,2)+'\n');
 return root;
}

