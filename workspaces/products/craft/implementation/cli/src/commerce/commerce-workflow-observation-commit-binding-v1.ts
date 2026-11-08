/** Checked data shape passed from an original observation invocation to the
 * selected native transaction. It has no effect authority by itself; native
 * storage must recheck the invocation and the exact journal row at commit.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
export type CommerceWorkflowObservationCommitBindingV1=
 Readonly<{
  kind:'dispatched-step';workflow:string;source_capture_sha256:string;store_id:string;
  consumer_entry_id:string;occurrence_id:string;order_id:string;
  step_name:string;target_entry_id:string;observation_entry_id:string;
  journal_entity:string;
  command_id:string;request_fingerprint:string;worker_id:string;worker_epoch:bigint;
  journal_worker_id:string;journal_worker_epoch:bigint;
  expected_progress_version:bigint;observation:unknown;
  journal_key:Readonly<{consumerEntryId:string;occurrenceId:string;stepName:string;commandId:string}>;
  source:'remote-result'|'quiescent-recovery';authority_effect:'none';
 }>|
 Readonly<{
  kind:'local';workflow:string;source_capture_sha256:string;store_id:string;
  consumer_entry_id:string;occurrence_id:string;order_id:string;
  local_step:string;next_step:string;observation_entry_id:string;
  worker_id:string;worker_epoch:bigint;expected_progress_version:bigint;
  observation:unknown;authority_effect:'none';
 }>;
