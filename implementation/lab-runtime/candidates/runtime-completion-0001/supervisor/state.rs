use super::{need,Error,Result};
use lab_control_store::{codec,custody::Held,ledger::{Acknowledged,ByteBinding,Change,HostConfirmation,Ledger,Operation,Outcome,PendingCheckpoint}};
use serde::{Serialize,Deserialize};

#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]
pub enum Domain{Fixture,Actual}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Scope{pub store_id:String,pub store_instance:String,pub store_epoch:u64,pub slot_id:String,pub slot_epoch:u64,pub holder:String}
impl Scope{pub fn matches(&self,o:&Operation)->bool{self.store_id==o.store_id&&self.store_instance==o.store_instance&&self.store_epoch==o.store_epoch&&self.slot_id==o.slot_id&&self.slot_epoch==o.slot_epoch&&self.holder==o.holder}}
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]
pub enum HistoricalState{Released,ReviewedNonoverlap,Unknown}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HistoricalDisposition{pub family:ByteBinding,pub state:HistoricalState,pub original_disposition:ByteBinding,pub independent_review:ByteBinding,pub currentness:ByteBinding}
/// These independently selected original records are not authenticated by JSON parsing.
/// Only a fixed trusted loader may construct Actual host input; no public receipt grants authority.
pub fn history_complete(expected:&[ByteBinding],records:&[HistoricalDisposition])->Result<()>{
 need(expected.len()<=128&&expected.len()==records.len(),"HISTORY_COVERAGE")?;
 for (i,(family,r)) in expected.iter().zip(records).enumerate(){
  need(family.valid()&&r.family==*family&&r.original_disposition.valid()&&r.independent_review.valid()&&r.currentness.valid(),"HISTORY_SELECTION")?;
  need(!expected[..i].contains(family),"HISTORY_DUPLICATE")?;
  need(r.state!=HistoricalState::Unknown,"HISTORY_UNKNOWN")?;
 }
 Ok(())
}
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]
pub enum Reason{Exited,Timeout,ChildSetupFailed,ContainmentChanged,ObservationFailed}
#[derive(Clone,Debug,PartialEq,Eq,Serialize)]
pub struct Terminal {
 pub schema_version:&'static str,pub domain:Domain,pub operation:Operation,pub attempt_id:String,
 pub containment_binding:ByteBinding,pub actual_group_identity:super::containment::Identity,pub execution_binding:ByteBinding,pub original_start_binding:ByteBinding,pub historical_selection:ByteBinding,
 pub start_utc_ns:u64,pub end_utc_ns:Option<u64>,pub elapsed_ns:u64,pub child_pid:u32,pub pid_start_ticks:Option<u64>,
 pub reason:Reason,pub exit_code:Option<i32>,pub signal:Option<i32>,pub primary_error:Option<&'static str>,
 pub cleanup_errors:Vec<&'static str>,pub direct_child_reaped:bool,pub subtree_empty:bool,
 pub inherited_descriptors_closed:bool,pub workload_started:Option<bool>,pub historical_complete:bool,
}
/// Created by the fixed supervisor, never deserialized from an untrusted report.
pub struct Observation{pub(crate) terminal:Terminal,pub(crate) unreaped_pidfd:Option<std::fs::File>}
impl Observation{
 pub fn terminal(&self)->&Terminal{&self.terminal}
 pub(crate) fn unreaped_pidfd(&self)->Option<&std::fs::File>{self.unreaped_pidfd.as_ref()}
 pub fn bytes(&self)->Result<Vec<u8>>{Ok(codec::encode(&self.terminal)?)}
 pub fn outcome_eligible(&self)->bool{self.clean()&&self.terminal.primary_error.is_none()&&matches!(self.terminal.reason,Reason::Exited)&&self.terminal.end_utc_ns.is_some()&&self.terminal.workload_started==Some(true)}
 pub fn clean(&self)->bool{let t=&self.terminal;t.pid_start_ticks.is_some()&&t.direct_child_reaped&&t.subtree_empty&&t.inherited_descriptors_closed&&t.historical_complete&&t.cleanup_errors.is_empty()}
 /// Actual terminal evidence must already have been durably retained by the fixed evidence writer.
 /// The byte binding proves identity, not external persistence or permission. This crate-private
 /// boundary is unavailable to JSON requests; fixture tests exercise the same codec separately.
 pub(crate) fn persist_retained(self,ledger:&mut Ledger<'_>,held:&Held<'_>,proof:super::attempt_journal::DurableOriginal,selected_outcome:Outcome)->Result<PendingFinish>{
  proof.validate()?;need(proof.event()==super::records::AttemptEvent::Terminal&&proof.operation()==&self.terminal.operation&&proof.attempt_id()==self.terminal.attempt_id&&proof.bytes()==self.bytes()?,"TERMINAL_DURABLE_SCOPE")?;
  let raw=proof.bytes().to_vec();let binding=proof.binding().clone();let mut result=self.persist_bytes(ledger,held,&raw,binding,selected_outcome)?;result.retained=Some(proof);Ok(result)
 }
 #[cfg(test)]pub(crate) fn persist(self,ledger:&mut Ledger<'_>,held:&Held<'_>,terminal_bytes:&[u8],binding:ByteBinding,selected_outcome:Outcome)->Result<PendingFinish>{need(self.terminal.domain==Domain::Fixture,"FIXTURE_TERMINAL_ONLY")?;self.persist_bytes(ledger,held,terminal_bytes,binding,selected_outcome)}
 fn persist_bytes(self,ledger:&mut Ledger<'_>,held:&Held<'_>,terminal_bytes:&[u8],binding:ByteBinding,selected_outcome:Outcome)->Result<PendingFinish>{
  need(binding.valid()&&binding.kind=="evidence"&&binding.size_bytes==terminal_bytes.len() as u64&&binding.sha256==codec::digest(terminal_bytes)&&self.bytes()?==terminal_bytes,"TERMINAL_ORIGINAL_BYTES")?;
  if !self.outcome_eligible(){need(selected_outcome==Outcome::Quarantined,"UNKNOWN_REQUIRES_QUARANTINE")?;}
  // A normal process exit never selects Committed or Aborted by itself. The fixed parent
  // must independently select that domain outcome from original operation evidence.
  let op=&self.terminal.operation;
  {let borrowed=ledger.borrow_operation(held,&op.operation_id,&op.fingerprint)?;need(borrowed.operation()==op,"TERMINAL_OPERATION_CHANGED")?;}
  let pending=ledger.append(held,Change::Outcome{operation_id:op.operation_id.clone(),fingerprint:op.fingerprint.clone(),result_binding:binding.clone(),outcome:selected_outcome})?;
  let expected=pending.requested_confirmation().clone();
  Ok(PendingFinish{observation:self,original_terminal:binding,outcome:selected_outcome,pending,expected,retained:None})
 }
}
pub struct PendingFinish{observation:Observation,original_terminal:ByteBinding,outcome:Outcome,pending:PendingCheckpoint,expected:HostConfirmation,retained:Option<super::attempt_journal::DurableOriginal>}
pub struct AcknowledgedCleanup{original_terminal:ByteBinding,control:Acknowledged,clean:bool}
impl PendingFinish{
 pub fn requested_confirmation(&self)->&HostConfirmation{&self.expected}
 pub fn acknowledge(self,ledger:&mut Ledger<'_>,held:&Held<'_>,confirmed:HostConfirmation)->Result<AcknowledgedCleanup>{
  need(confirmed==self.expected,"TERMINAL_CONFIRMATION")?;if let Some(proof)=&self.retained{proof.validate()?;}
  let control=ledger.acknowledge(held,self.pending,confirmed)?;
  Ok(AcknowledgedCleanup{clean:self.observation.outcome_eligible()&&self.outcome!=Outcome::Quarantined,original_terminal:self.original_terminal,control})
 }
}
impl AcknowledgedCleanup{
 pub fn terminal_binding(&self)->&ByteBinding{&self.original_terminal}
 pub fn confirmation(&self)->&HostConfirmation{self.control.confirmation()}
 /// Cleanup of this one attempt only. Family closure still requires the fixed parent to
 /// reconcile every operation/history and perform the accepted slot transition.
 pub fn this_attempt_clean(&self)->bool{self.clean}
}
/// Strict, finite parsing of cgroup.events. Unknown future numeric keys are retained by the
/// kernel but cannot override required populated/frozen keys. No PID guessing occurs.
pub fn populated(raw:&[u8])->Result<bool>{
 need(raw.len()<=4096&&!raw.is_empty(),"EVENTS_BOUND")?;
 let text=std::str::from_utf8(raw).map_err(|_|Error("EVENTS_ENCODING"))?;
 let mut seen=std::collections::BTreeSet::new();let mut result=None;
 for line in text.lines(){let v:Vec<_>=line.split_whitespace().collect();need(v.len()==2&&v[0].bytes().all(|b|b.is_ascii_lowercase()||b==b'_')&&seen.insert(v[0]),"EVENTS_FORMAT")?;let n=v[1].parse::<u64>().map_err(|_|Error("EVENTS_NUMBER"))?;need(v[1]==n.to_string(),"EVENTS_NUMBER")?;
  if v[0]=="populated"{need(n<=1,"EVENTS_BOOLEAN")?;result=Some(n==1)}else if v[0]=="frozen"{need(n<=1,"EVENTS_BOOLEAN")?;}
 }
 result.ok_or(Error("EVENTS_POPULATED_MISSING"))
}
