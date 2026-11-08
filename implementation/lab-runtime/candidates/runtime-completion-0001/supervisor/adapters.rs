//! Fixed start, terminal and restart adapters. Only host authentication/custody
//! remain external; ordinary record persistence and exact comparisons live here.
use super::{need,Result,attempt_journal::{AttemptJournal,PendingAppend,SelectedCheckpoint,DurableOriginal},records::{AttemptEvent,StartOriginal,RecoveryOriginal},containment::{Root,now},spawn::{PendingStart,Prepared},state::{Domain,Observation,PendingFinish}};
use lab_control_store::{codec,custody::Held,ledger::{ByteBinding,Operation,Outcome,Ledger,Change,HostConfirmation,PendingCheckpoint}};
use serde::{Serialize,Deserialize};
use std::time::{Instant,Duration};

/// Consumes the freshly prepared, never-restarted group. No Deserialize/Clone.
pub(crate) struct PendingAdmission<'a>{start:PendingStart<'a>,pending:PendingAppend}
pub(crate) struct StartAcknowledgment{proof:DurableOriginal}
impl StartAcknowledgment{
 pub(crate) fn proof(&self)->&DurableOriginal{&self.proof}
 pub(crate) fn verify_original(&self,expected:&[u8])->Result<()>{self.proof.validate()?;need(self.proof.event()==AttemptEvent::Start&&self.proof.bytes()==expected,"START_ACK_ORIGINAL_MISMATCH")}
}
impl<'a> PendingAdmission<'a>{
 pub(crate) fn retain(journal:&mut AttemptJournal<'_>,start:PendingStart<'a>)->Result<Self>{
  start.root().admission_currentness()?;journal.current()?;need(start.root().domain()==journal.header().domain,"ADMISSION_DOMAIN")?;let original:StartOriginal=codec::decode(start.original_bytes())?;original.validate()?;
  need(start.root().root_binding()==&journal.header().supervisor_root_binding&&start.root().physical_identity()?==journal.header().supervisor_root_identity,"ADMISSION_ROOT_HEADER")?;
  journal.match_groups(&start.root().groups()?,Some(&original))?;
  let pending=journal.append(AttemptEvent::Start,&original.operation,&original.attempt_id,None,start.original_bytes())?;Ok(Self{start,pending})
 }
 pub(crate) fn requested(&self)->&super::records::HostAttemptCheckpoint{self.pending.requested()}
 pub(crate) fn acknowledge(self,journal:&mut AttemptJournal<'_>,checkpoint:SelectedCheckpoint,plan:&Prepared)->Result<(PendingStart<'a>,StartAcknowledgment)>{
  // Check inventory again immediately before acknowledgment. Even empty unknown
  // groups fence admission, and are neither adopted nor deleted.
  journal.match_groups(&self.start.root().groups()?,None)?;plan.revalidate()?;
  let proof=journal.acknowledge(self.pending,checkpoint)?;journal.validate_launch(&proof,self.start.root())?;
  need(proof.bytes()==self.start.original_bytes(),"ADMISSION_ORIGINAL_CHANGED")?;
  Ok((self.start,StartAcknowledgment{proof}))
 }
}
pub(crate) struct PendingTerminal{observation:Observation,pending:PendingAppend}
impl PendingTerminal{
 pub(crate) fn retain(journal:&mut AttemptJournal<'_>,observation:Observation)->Result<Self>{
  let terminal=observation.terminal();let pending=journal.append(AttemptEvent::Terminal,&terminal.operation,&terminal.attempt_id,Some(&terminal.original_start_binding),&observation.bytes()?)?;Ok(Self{observation,pending})
 }
 pub(crate) fn requested(&self)->&super::records::HostAttemptCheckpoint{self.pending.requested()}
 pub(crate) fn acknowledge_and_outcome(self,journal:&mut AttemptJournal<'_>,checkpoint:SelectedCheckpoint,ledger:&mut Ledger<'_>,held:&Held<'_>,selected:Outcome)->Result<PendingFinish>{
  need(ledger.inspect().writable&&ledger.inspect().verified_head==journal.control().ledger()?.inspect().verified_head,"TERMINAL_CURRENT_LEDGER_JOIN")?;let proof=journal.acknowledge(self.pending,checkpoint)?;self.observation.persist_retained(ledger,held,proof,selected)
 }
}

#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct CleanupSelection{
 pub schema_version:String,pub domain:Domain,pub operation:Operation,pub original_start_binding:ByteBinding,
 pub original_checkpoint_binding:ByteBinding,pub containment_binding:ByteBinding,pub group_identity:super::containment::Identity,
 pub current_control:HostConfirmation,pub history_binding:ByteBinding,pub expires_utc_ns:u64,pub max_cleanup_ms:u64,
}
/// This exact cleanup-only grant is independently authenticated, never derived
/// from a prior effect permit or the existence/emptiness of a group.
pub(crate) struct CleanupAuthority{selection:CleanupSelection,binding:ByteBinding}
impl CleanupAuthority{
 fn checked(raw:&[u8],binding:ByteBinding,domain:Domain)->Result<Self>{need(raw.len()<=65536&&binding.valid()&&binding.kind=="evidence"&&binding.sha256==codec::digest(raw)&&binding.size_bytes==raw.len() as u64,"CLEANUP_AUTHORITY_BYTES")?;let selection:CleanupSelection=codec::decode(raw)?;
  need(codec::encode(&selection)?==raw&&selection.schema_version=="lab-supervisor-cleanup-selection/v1"&&selection.domain==domain&&selection.original_start_binding.valid()&&selection.original_checkpoint_binding.valid()&&selection.containment_binding.valid()&&selection.history_binding.valid()&&selection.expires_utc_ns>now()?&&selection.expires_utc_ns<=i64::MAX as u64&&(1..=30000).contains(&selection.max_cleanup_ms),"CLEANUP_AUTHORITY_SCOPE")?;Ok(Self{selection,binding})}
 #[cfg(test)]pub(crate) fn fixture(raw:&[u8],binding:ByteBinding)->Result<Self>{Self::checked(raw,binding,Domain::Fixture)}
 /// Fixed enrolled host transport: authenticate original cleanup authority,
 /// current control selection and group/history custody before passing bytes.
 /// This authorizes no workload launch, normal outcome, reconciliation or release.
 pub(crate) unsafe fn from_enrolled_host(raw:&[u8],binding:ByteBinding)->Result<Self>{Self::checked(raw,binding,Domain::Actual)}
}
/// A restarted handle has no conversion to PendingStart or StartAcknowledgment.
pub(crate) struct RestartRecovery<'a>{root:&'a Root,original:StartOriginal,start_binding:ByteBinding,checkpoint_binding:ByteBinding,authority:CleanupAuthority}
impl<'a> RestartRecovery<'a>{
 pub(crate) fn load(root:&'a Root,journal:&AttemptJournal<'_>,original_start:&ByteBinding,original_checkpoint:&SelectedCheckpoint,authority:CleanupAuthority)->Result<Self>{
  need(root.domain()==Domain::Actual&&root.cleanup_only(),"ACTUAL_CLEANUP_ONLY_ROOT_REQUIRED")?;let original=journal.selected_start_checkpoint(original_start,original_checkpoint)?;
  check_cleanup_selection(journal,&original,original_start,original_checkpoint.binding(),&authority)?;
  need(authority.selection.domain==Domain::Actual&&root.root_binding()==&original.containment_binding&&root.physical_identity()?==journal.header().supervisor_root_identity&&root.history_binding()==&authority.selection.history_binding,"RECOVERY_SELECTED_ROOT")?;
  // Reopen exact original only. This verifies identity, never adopts by name.
  root.reopen_cleanup(&original)?;
  Ok(Self{root,original,start_binding:original_start.clone(),checkpoint_binding:original_checkpoint.binding().clone(),authority})
 }
 pub(crate) fn cleanup(self,journal:&AttemptJournal<'_>)->Result<RecoveryObservation>{
  journal.recovery_current()?;journal.control().operation(&self.original.operation,false)?;need(journal.control().current==self.authority.selection.current_control&&now()?<self.authority.selection.expires_utc_ns,"RECOVERY_CURRENT_PERMISSION")?;
  let group=self.root.reopen_cleanup(&self.original)?;
  let mut error=None;let mut empty=false;if let Err(e)=group.kill_owned(){error=Some(e.0.to_string())}
  let begin=Instant::now();while error.is_none()&&begin.elapsed()<Duration::from_millis(self.authority.selection.max_cleanup_ms){
   if !now().is_ok_and(|n|n<self.authority.selection.expires_utc_ns){error=Some("RECOVERY_CLEANUP_PERMISSION_EXPIRED".into());break}
   match group.populated(){Ok(false)=>{empty=true;break},Ok(true)=>{},Err(e)=>{error=Some(e.0.into());break}}
   std::thread::sleep(Duration::from_millis(5));
  }
  if !empty&&error.is_none(){error=Some("RECOVERY_SUBTREE_NOT_PROVEN_EMPTY".into())}
  let observed=now().ok();if observed.is_none()&&error.is_none(){error=Some("RECOVERY_CLOCK_UNAVAILABLE".into())}
  let complete_group_inventory=self.root.groups().ok().map(|groups|journal.match_groups(&groups,None).is_ok());
  Ok(RecoveryObservation{record:recovery_record(journal,&self.original,self.start_binding,self.checkpoint_binding,&self.authority,empty,observed,error,complete_group_inventory,self.root.historical_complete())})
 }
}
pub(crate) fn check_cleanup_selection(journal:&AttemptJournal<'_>,original:&StartOriginal,start:&ByteBinding,checkpoint:&ByteBinding,authority:&CleanupAuthority)->Result<()>{
 let s=&authority.selection;journal.recovery_current()?;journal.control().operation(&original.operation,false)?;
 need(s.domain==journal.header().domain&&s.operation==original.operation&&s.original_start_binding==*start&&s.original_checkpoint_binding==*checkpoint&&s.containment_binding==original.containment_binding&&s.group_identity==original.group_identity&&s.current_control==journal.control().current&&now()?<s.expires_utc_ns,"RECOVERY_AUTHORITY_JOIN")
}
pub(crate) fn recovery_record(journal:&AttemptJournal<'_>,original:&StartOriginal,start:ByteBinding,checkpoint:ByteBinding,authority:&CleanupAuthority,empty:bool,observed:Option<u64>,error:Option<String>,complete_group_inventory:Option<bool>,historical_complete:bool)->RecoveryOriginal{
 RecoveryOriginal{schema_version:"lab-contained-recovery-observation/v1".into(),domain:journal.header().domain,operation:original.operation.clone(),attempt_id:original.attempt_id.clone(),original_start_binding:start,original_checkpoint_binding:checkpoint,cleanup_authority_binding:authority.binding.clone(),control_preimage:journal.control().current.clone(),group_identity:original.group_identity.clone(),observed_utc_ns:observed,subtree_empty:empty,direct_child_reaped:None,pid_identity_known:false,historical_complete,observation_error:error,journal_append_eligible:journal.inspect().writable,complete_group_inventory,outcome:"quarantined".into()}
}
pub(crate) struct RecoveryObservation{record:RecoveryOriginal}
impl RecoveryObservation {
 // Exact read-only original for a separately selected evidence sink. This is
 // not public disclosure permission, durable acknowledgement, or a capability.
 // Capture before consuming retain: a quarantined journal must still refuse it.
 pub(crate) fn original_bytes(&self)->Result<Vec<u8>>{let raw=codec::encode(&self.record)?;need(raw.len()<=65536,"RECOVERY_OBSERVATION_BOUND")?;Ok(raw)}
 #[cfg(test)]pub(crate) fn fixture(record:RecoveryOriginal)->Result<Self>{need(record.domain==Domain::Fixture,"FIXTURE_RECOVERY_ONLY")?;Ok(Self{record})}
}
pub(crate) struct PendingRecovery{pending:PendingAppend,operation:Operation}
pub(crate) enum RecoveryDisposition {Existing{outcome:Outcome,original:ByteBinding,recovery:ByteBinding},Pending(PendingRecoveryOutcome)}
pub(crate) struct PendingRecoveryOutcome{pending:PendingCheckpoint,expected:HostConfirmation,proof:DurableOriginal}
impl PendingRecovery{
 pub(crate) fn retain(journal:&mut AttemptJournal<'_>,observation:RecoveryObservation)->Result<Self>{let observation=observation.record;need(observation.outcome=="quarantined"&&observation.direct_child_reaped.is_none()&&!observation.pid_identity_known,"RECOVERY_NOT_REAP_PROOF")?;
  let pending=journal.append(AttemptEvent::Recovery,&observation.operation,&observation.attempt_id,Some(&observation.original_start_binding),&codec::encode(&observation)?)?;Ok(Self{pending,operation:observation.operation})}
 pub(crate) fn requested(&self)->&super::records::HostAttemptCheckpoint{self.pending.requested()}
 pub(crate) fn acknowledge_and_quarantine(self,journal:&mut AttemptJournal<'_>,checkpoint:SelectedCheckpoint,ledger:&mut Ledger<'_>,held:&Held<'_>)->Result<RecoveryDisposition>{
  let proof=journal.acknowledge(self.pending,checkpoint)?;proof.validate()?;journal.control().operation(&self.operation,false)?;
  need(ledger.inspect().writable&&ledger.inspect().verified_head==journal.control().ledger()?.inspect().verified_head&&ledger.operation(&self.operation.operation_id)==Some(&self.operation),"RECOVERY_CURRENT_LEDGER_JOIN")?;
  if let Some((outcome,original))=ledger.outcome(&self.operation.operation_id){return Ok(RecoveryDisposition::Existing{outcome:*outcome,original:original.clone(),recovery:proof.binding().clone()})}
  let pending=ledger.append(held,Change::Outcome{operation_id:self.operation.operation_id.clone(),fingerprint:self.operation.fingerprint.clone(),result_binding:proof.binding().clone(),outcome:Outcome::Quarantined})?;let expected=pending.requested_confirmation().clone();
  Ok(RecoveryDisposition::Pending(PendingRecoveryOutcome{pending,expected,proof}))
 }
}
impl PendingRecoveryOutcome{
 pub(crate) fn requested(&self)->&HostConfirmation{&self.expected}
 pub(crate) fn acknowledge(self,ledger:&mut Ledger<'_>,held:&Held<'_>,confirmation:HostConfirmation)->Result<ByteBinding>{self.proof.validate()?;need(confirmation==self.expected,"RECOVERY_OUTCOME_ACK")?;ledger.acknowledge(held,self.pending,confirmation)?;Ok(self.proof.binding().clone())}
}
