import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {composedFixture} from './C13-composed-source-fixture.mjs';
import {dataDigest} from '../../src/profile-engine/contracts.ts';
import {GENERIC_WORKFLOW_CAPABILITIES} from '../../src/generic/workflow-source.ts';

const addition=`
entity WorkflowStart:
  id UInt64
  initiated Bool
  identity id

entity WorkflowReservation:
  id UInt64
  reserved Bool
  identity id

query ReadWorkflowReservation:
  input id UInt64
  source reservation WorkflowReservation
  output optional<WorkflowReservation>
  where reservation.id == id
  project reservation
  on-missing return none
  on-unavailable fail read-unavailable

operation BeginWorkflow:
  input id UInt64
  input slotRequest ApprovalSlotRequest
  output WorkflowStart
  transaction Begin:
    atomic-participants WorkflowStart
    create initiated WorkflowStart:
      id <- id
      initiated <- true
    on-unique-conflict reject already-started
    on-proven-rollback fail storage-rolled-back
    on-unknown-commit fail outcome-unknown
  return initiated

operation ReserveWorkflow:
  input id UInt64
  output WorkflowReservation
  transaction Reserve:
    atomic-participants WorkflowReservation
    create reservation WorkflowReservation:
      id <- id
      reserved <- true
    on-unique-conflict reject already-reserved
    on-proven-rollback fail storage-rolled-back
    on-unknown-commit fail outcome-unknown
  return reservation

operation UndoWorkflow:
  input id UInt64
  output WorkflowReservation
  read prior from ReviewDesk.ReadWorkflowReservationEntry(id=id)
    on-missing reject reservation-not-found
    on-unavailable fail storage-unavailable
  transaction Undo:
    atomic-participants WorkflowReservation
    update released WorkflowReservation from prior:
      reserved <- false
    on-version-conflict reject reservation-changed
    on-unique-conflict reject identity-conflict
    on-proven-rollback fail storage-rolled-back
    on-unknown-commit fail outcome-unknown
  return released

entry ReviewDesk.BeginWorkflowEntry:
  invokes ReviewDesk.BeginWorkflow
  interaction request-response
  access:
    authenticated customer
    permission workflow.begin
    auth-resource workflow
    auth-action begin
    auth-scope review-desk

entry ReviewDesk.ReserveWorkflowEntry:
  invokes ReviewDesk.ReserveWorkflow
  interaction request-response
  access:
    authenticated operator
    permission workflow.reserve
    auth-resource workflow
    auth-action reserve
    auth-scope review-desk

entry ReviewDesk.UndoWorkflowEntry:
  invokes ReviewDesk.UndoWorkflow
  interaction request-response
  access:
    authenticated operator
    permission workflow.undo
    auth-resource workflow
    auth-action undo
    auth-scope review-desk

entry ReviewDesk.ReadWorkflowReservationEntry:
  invokes ReviewDesk.ReadWorkflowReservation
  interaction request-response
  access:
    authenticated operator
    permission workflow.read-reservation
    auth-resource workflow
    auth-action read-reservation
    auth-scope review-desk

workflow ApprovalFlow:
  owner ReviewDeskService
  scope generated-recoverable
  profile contracts/workflow-profile.json
  input id UInt64
  input slotRequest ApprovalSlotRequest
  correlation id
  durable-state ReviewDesk.WorkflowStart
  start ReviewDesk.BeginWorkflowEntry
  step reserve invokes ReviewDesk.ReserveWorkflowEntry compensate-with ReviewDesk.UndoWorkflowEntry
  step commit invokes ReviewDesk.CommitRequestApprovalEntry on-unknown resume-original-command on-definite-failure compensate
  step delivery awaits ReviewDesk.ApprovalCommitted delivered-to AuditService.RecordApprovedEntry
  recovery needed-compensations-only reverse-completion
`;
export function workflowFixture(){
 const root=composedFixture(addition);
 const base=JSON.parse(readFileSync(path.join(root,'contracts/selected-profile.json'),'utf8'));
 const profile={schema_version:'craft.generic-workflow-profile/v1-candidate',workflow:'ReviewDesk.ApprovalFlow',base_event_profile_sha256:dataDigest(base),capabilities:[...GENERIC_WORKFLOW_CAPABILITIES],recovery:'needed-compensations-only/reverse-completion-v1',storage:'service-owned-fenced-workflow-journal/v1-candidate'};
 writeFileSync(path.join(root,'contracts/workflow-profile.json'),JSON.stringify(profile,null,2)+'\n');return root;
}
