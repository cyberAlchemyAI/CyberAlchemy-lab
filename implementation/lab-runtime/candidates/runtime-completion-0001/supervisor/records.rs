//! Closed attempt-journal records. Record decoding never grants launch or cleanup.
use super::{need,Result,containment::{Identity,Limits},state::{Domain,Reason}};
use lab_control_store::{codec,custody,ledger::{ByteBinding,Head,HostConfirmation,Operation}};
use serde::{Serialize,Deserialize};

#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct JournalLimits {pub max_records:u64,pub max_original_bytes:u64,pub max_record_bytes:u64,pub max_total_bytes:u64,pub max_attempts:u64}
impl JournalLimits {pub(crate) fn validate(&self)->Result<()>{
 need((8..=4096).contains(&self.max_records)&&(2048..=65536).contains(&self.max_original_bytes)&&(2048..=65536).contains(&self.max_record_bytes)&&self.max_total_bytes<=536870912&&self.max_total_bytes>=4*(self.max_original_bytes+self.max_record_bytes)&&(1..=1024).contains(&self.max_attempts),"ATTEMPT_JOURNAL_LIMITS")
}}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct JournalHeader {
 pub schema_version:String,pub domain:Domain,pub root_id:String,pub root:Identity,
 pub control_root:custody::Identity,pub authority_domain:String,pub control_header_sha256:String,
 pub supervisor_root_binding:ByteBinding,pub supervisor_root_identity:Identity,
 pub custody_binding:ByteBinding,pub limits:JournalLimits,
}
impl JournalHeader {pub(crate) fn validate(&self)->Result<()>{
 self.limits.validate()?;need(self.schema_version=="lab-supervisor-attempt-journal/v1"&&(1..=4096).contains(&self.root_id.chars().count())&&codec::identifier(&self.authority_domain)&&codec::hash(&self.control_header_sha256)&&self.supervisor_root_binding.valid()&&self.custody_binding.valid(),"ATTEMPT_JOURNAL_HEADER")
}}
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]
pub(crate) enum AttemptEvent {Start,Terminal,Recovery}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct AttemptRecord {
 pub schema_version:String,pub sequence:u64,pub previous_sha256:String,
 pub operation:Operation,pub attempt_id:String,pub event:AttemptEvent,
 pub control_preimage:HostConfirmation,pub original_binding:ByteBinding,
 pub original_start_binding:ByteBinding,
}
/// Distinct from Ledger's HostConfirmation: its head is the supervisor journal.
/// External host custody must authenticate and CAS this exact transition.
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct HostAttemptCheckpoint {
 pub schema_version:String,pub domain:Domain,pub journal_root:Identity,pub root_id:String,
 pub journal_header_sha256:String,pub predecessor:Head,pub head:Head,
 pub control_preimage:HostConfirmation,pub operation:Option<Operation>,pub attempt_id:Option<String>,
}
impl HostAttemptCheckpoint {pub(crate) fn valid_for(&self,h:&JournalHeader,header_sha:&str)->Result<()>{
 need(self.schema_version=="lab-host-supervisor-checkpoint/v1"&&self.domain==h.domain&&self.journal_root==h.root&&self.root_id==h.root_id&&self.journal_header_sha256==header_sha&&
  self.head.sequence<=h.limits.max_records&&codec::hash(&self.head.sha256)&&codec::hash(&self.predecessor.sha256)&&self.predecessor.sequence<=self.head.sequence&&
  self.control_preimage.authority_domain==h.authority_domain&&self.control_preimage.root==h.control_root&&self.control_preimage.header_sha256==h.control_header_sha256&&
  ((self.head.sequence==0&&self.predecessor==self.head&&self.head.sha256==header_sha&&self.operation.is_none()&&self.attempt_id.is_none())||
   (self.head.sequence>0&&self.predecessor.sequence.checked_add(1)==Some(self.head.sequence)&&self.operation.is_some()&&self.attempt_id.as_ref().is_some_and(|s|super::containment::name(s).is_ok()))),"HOST_ATTEMPT_CHECKPOINT")
}}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct StartOriginal {
 pub schema_version:String,pub operation:Operation,pub attempt_id:String,
 pub containment_binding:ByteBinding,pub group_identity:Identity,pub execution_binding:ByteBinding,
 pub historical_selection:ByteBinding,pub created_utc_ns:u64,pub dispatch_until_utc_ns:u64,
 pub cleanup_until_utc_ns:u64,pub limits:Limits,
}
impl StartOriginal {pub(crate) fn validate(&self)->Result<()>{
 self.limits.validate()?;super::containment::name(&self.attempt_id)?;
 need(self.schema_version=="lab-contained-attempt-start/v1"&&self.containment_binding.valid()&&self.execution_binding.valid()&&self.historical_selection.valid()&&
  self.created_utc_ns>0&&self.created_utc_ns<self.dispatch_until_utc_ns&&self.dispatch_until_utc_ns<=self.cleanup_until_utc_ns&&self.cleanup_until_utc_ns<=codec::MAX_INTEGER,"START_ORIGINAL")
}}
/// Owned decoding counterpart to the live, non-deserializable Observation.
/// This may validate historical bytes but can never construct Observation.
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct TerminalOriginal {
 pub schema_version:String,pub domain:Domain,pub operation:Operation,pub attempt_id:String,
 pub containment_binding:ByteBinding,pub actual_group_identity:Identity,pub execution_binding:ByteBinding,pub original_start_binding:ByteBinding,pub historical_selection:ByteBinding,
 pub start_utc_ns:u64,pub end_utc_ns:Option<u64>,pub elapsed_ns:u64,pub child_pid:u32,pub pid_start_ticks:Option<u64>,
 pub reason:Reason,pub exit_code:Option<i32>,pub signal:Option<i32>,pub primary_error:Option<String>,pub cleanup_errors:Vec<String>,
 pub direct_child_reaped:bool,pub subtree_empty:bool,pub inherited_descriptors_closed:bool,pub workload_started:Option<bool>,pub historical_complete:bool,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct RecoveryOriginal {
 pub schema_version:String,pub domain:Domain,pub operation:Operation,pub attempt_id:String,
 pub original_start_binding:ByteBinding,pub original_checkpoint_binding:ByteBinding,
 pub cleanup_authority_binding:ByteBinding,pub control_preimage:HostConfirmation,
 pub group_identity:Identity,pub observed_utc_ns:Option<u64>,pub subtree_empty:bool,
 pub direct_child_reaped:Option<bool>,pub pid_identity_known:bool,pub historical_complete:bool,
 pub observation_error:Option<String>,pub journal_append_eligible:bool,pub complete_group_inventory:Option<bool>,pub outcome:String,
}
