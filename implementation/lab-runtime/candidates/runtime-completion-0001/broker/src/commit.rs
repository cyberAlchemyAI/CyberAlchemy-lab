//! Fixed generation/pointer protocol. No RPC parser or caller-provided executable
//! callback can enter this module. Actual host admission/transport is a later
//! statically linked integration; fixture observations never become authority.
use crate::{roots::{self,Binding,Domain,Error,Exclusive,Identity,Result,require},members::{Action,Stage,Phase as MemberPhase,DurableReceipt,Manifest as MemberManifest},generation::*};
use lab_control_store::{custody::{Held,Rank},ledger::{Ledger,Operation,Change,Outcome,HostConfirmation,PendingCheckpoint,ByteBinding}};
use serde::{Deserialize,Serialize};
use std::{collections::{BTreeMap,BTreeSet},fs::File,io::{Read,Write},os::{fd::AsRawFd,unix::fs::FileExt}};

/// Runtime attachment, separate from the preactivation store and control policy.
/// Fields are private: deserializing a policy/request cannot create admission.
pub struct ControlAdmission<'a> {
    control_root:&'a lab_control_store::custody::Root,control_directory:File,policy:ControlPolicy,policy_binding:Binding,
    confirmation:HostConfirmation,scope:roots::ExecutionScope,domain:Domain,
    reserve_binding:Option<Binding>,reserved_bytes:u64,reserved_inodes:u64,reserve_inventory_sha256:Option<String>,reserve_head:Option<lab_control_store::ledger::Head>,runtime_selection:RuntimeCommitSelection,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RuntimeCommitSelection {pub store_binding:Binding,pub c01_store_binding:Binding,pub generation_manifest_binding:Binding,pub execution_scope:roots::ExecutionScope,pub commit_authority_binding:Binding,pub expires_utc_ns:u64,pub operation_id:String,pub original_fingerprint:String}
impl<'a> ControlAdmission<'a> {
    #[cfg(test)] pub(crate) fn fixture_capacity(mut self,bytes:u64,inodes:u64,inventory:String)->Result<Self>{require(self.domain==Domain::Fixture,"FIXTURE_ONLY")?;self.reserve_binding=Some(self.policy_binding.clone());self.reserved_bytes=bytes;self.reserved_inodes=inodes;self.reserve_inventory_sha256=Some(inventory);self.reserve_head=Some(self.confirmation.head.clone());Ok(self)}

    pub fn fixture(control_root:&'a lab_control_store::custody::Root,control_directory:File,held:&Held<'_>,root:&Exclusive<'_>,journal:&Exclusive<'_>,confirmation:HostConfirmation,policy_raw:&[u8],expected:&Binding,runtime_selection:RuntimeCommitSelection)->Result<Self>{
        require(root.root().selection().domain==Domain::Fixture&&journal.root().selection().domain==Domain::Fixture,"ACTUAL_HOST_PROVIDER_REQUIRED")?;
        Self::admit(control_root,control_directory,held,root,journal,confirmation,policy_raw,expected,None,0,0,None,Domain::Fixture,runtime_selection)
    }
    /// Fixed U02-03 host loader only. Caller must independently authenticate the
    /// original policy/confirmation and exact nonrollbackable root enrollment;
    /// attest no alternate writer/rollback path, current activation and held
    /// global lock; and verify a still-held exclusive filesystem capacity reserve
    /// (not fstatvfs free space) covering journal/terminal/cleanup obligations.
    /// The reserve original must bind these remaining bytes/inodes, the exact
    /// current journal inventory digest, and this confirmation head/domain/root.
    /// The loader verifies it is still held and excludes already retained residue;
    /// a reused receipt cannot cover a changed inventory or a new repair branch.
    /// Accepted Ledger capacity is separately reserved by the control store;
    /// generation-root pointer/member capacity is separately selected there.
    /// `expected` and reserve receipt come from host custody, never broker JSON.
    /// No actual host loader is implemented by this seam.
    pub(crate) unsafe fn from_fixed_host(control_root:&'a lab_control_store::custody::Root,control_directory:File,held:&Held<'_>,root:&Exclusive<'_>,journal:&Exclusive<'_>,confirmation:HostConfirmation,policy_raw:&[u8],expected:&Binding,reserve_binding:Binding,reserved_bytes:u64,reserved_inodes:u64,reserve_inventory_sha256:String,runtime_selection:RuntimeCommitSelection)->Result<Self>{
        require(root.root().selection().domain==Domain::Actual&&journal.root().selection().domain==Domain::Actual&&reserve_binding.valid()&&reserved_bytes>0,"ACTUAL_CONTROL_ADMISSION")?;
        Self::admit(control_root,control_directory,held,root,journal,confirmation,policy_raw,expected,Some(reserve_binding),reserved_bytes,reserved_inodes,Some(reserve_inventory_sha256),Domain::Actual,runtime_selection)
    }
    fn admit(control_root:&'a lab_control_store::custody::Root,control_directory:File,held:&Held<'_>,root:&Exclusive<'_>,journal:&Exclusive<'_>,confirmation:HostConfirmation,raw:&[u8],expected:&Binding,reserve_binding:Option<Binding>,reserved_bytes:u64,reserved_inodes:u64,reserve_inventory_sha256:Option<String>,domain:Domain,runtime_selection:RuntimeCommitSelection)->Result<Self>{
        require(raw.len()<=1_048_576&&expected.valid()&&expected.sha256==roots::hash(raw)&&expected.size_bytes==raw.len() as u64,"CONTROL_POLICY_BYTES")?;
        let policy:ControlPolicy=serde_json::from_slice(raw).map_err(|_|Error("CONTROL_POLICY_SCHEMA"))?;
        require(canonical(&policy)?==raw&&policy.schema_version=="lab-generation-control-policy/v1"&&!policy.control_root_id.is_empty()&&policy.control_root_id.chars().count()<=4096&&!policy.writer_domain.is_empty()&&policy.writer_domain.len()<=128&&
            policy.control_root==control_root.identity()&&policy.control_root==confirmation.root&&policy.authority_domain==confirmation.authority_domain&&policy.header_sha256==confirmation.header_sha256&&
            policy.journal==JournalRootPolicy::from_runtime(journal.root().selection())&&policy.journal.domain==domain&&
            root.root().selection().execution_scope==journal.root().selection().execution_scope,"CONTROL_POLICY_JOIN")?;
        // Journal must be the directly selected child of this exact held control
        // root. Equal root names or byte bindings in another root cannot join it.
        let ancestors=&journal.root().selection().ancestors;
        require(ancestors.len()>=2,"CONTROL_PARENT_MISSING")?;let parent=&ancestors[ancestors.len()-2];
        require(parent.device==policy.control_root.device&&parent.inode==policy.control_root.inode&&parent.uid==policy.control_root.uid,"CONTROL_PARENT_IDENTITY")?;
        let physical=Identity::observe(&control_directory)?;require(physical.device==policy.control_root.device&&physical.inode==policy.control_root.inode&&physical.uid==policy.control_root.uid,"CONTROL_HANDLE_IDENTITY")?;
        require(runtime_selection.execution_scope==root.root().selection().execution_scope&&runtime_selection.store_binding.valid()&&runtime_selection.c01_store_binding.valid()&&runtime_selection.generation_manifest_binding.valid()&&runtime_selection.commit_authority_binding.valid()&&runtime_selection.expires_utc_ns>0&&runtime_selection.expires_utc_ns<=i64::MAX as u64&&roots::digest(&runtime_selection.original_fingerprint)&&!runtime_selection.operation_id.is_empty(),"RUNTIME_COMMIT_SELECTION")?;
        let reserve_head=if domain==Domain::Actual{Some(confirmation.head.clone())}else{None};
        let this=Self{control_root,control_directory,policy,policy_binding:expected.clone(),confirmation,scope:root.root().selection().execution_scope.clone(),domain,reserve_binding,reserved_bytes,reserved_inodes,reserve_inventory_sha256,reserve_head,runtime_selection};
        this.open(held)?;Ok(this)
    }
    fn open(&self,held:&Held<'_>)->Result<Ledger<'a>>{
        control(self.control_root.validate())?;let physical=Identity::observe(&self.control_directory)?;require(physical.device==self.policy.control_root.device&&physical.inode==self.policy.control_root.inode&&physical.uid==self.policy.control_root.uid,"CONTROL_HANDLE_IDENTITY")?;
        control(Ledger::open(self.control_root,held,lab_control_store::ledger::TrustedSelection{confirmation:self.confirmation.clone(),posture:if self.domain==Domain::Fixture{lab_control_store::ledger::Posture::Fixture}else{lab_control_store::ledger::Posture::Actual}}))
    }
    fn check(&self,held:&Held<'_>,ledger:&Ledger<'_>)->Result<()>{let observed=self.open(held)?;require(observed.inspect().writable&&ledger.inspect().writable&&observed.inspect().verified_head==ledger.inspect().verified_head,"CONTROL_CHECKPOINT_JOIN")}
}

#[cfg(test)]
thread_local!{pub(crate) static FAULT:std::cell::Cell<u8>=const{std::cell::Cell::new(0)};}
#[cfg(test)]
thread_local!{pub(crate) static SYNC_FAULT:std::cell::Cell<u8>=const{std::cell::Cell::new(0)};}
fn sync_at(file:&File,_point:u8)->Result<()>{
    #[cfg(test)] if SYNC_FAULT.with(|v|v.get()==_point){
        // Real EBADF from fsync on an O_PATH handle to the same owned object.
        // This exercises the error branch, not power-loss durability.
        use std::os::fd::FromRawFd;
        let path=std::ffi::CString::new(format!("/proc/self/fd/{}",file.as_raw_fd())).unwrap();
        let fd=unsafe{libc::open(path.as_ptr(),libc::O_PATH|libc::O_CLOEXEC)};require(fd>=0,"SYNC_ERROR_FIXTURE_OPEN")?;
        let handle=unsafe{File::from_raw_fd(fd)};return handle.sync_all().map_err(Into::into);
    }
    file.sync_all()?;Ok(())
}
fn boundary(_n:u8)->Result<()> {#[cfg(test)] if FAULT.with(|v|v.get()==_n){return Err(Error("INJECTED_BOUNDARY"))} Ok(())}
fn control<T>(r:lab_control_store::Result<T>)->Result<T>{r.map_err(|_|Error("CONTROL_REFUSED"))}
fn byte_binding(b:&Binding)->ByteBinding{ByteBinding{kind:b.kind.clone(),root_id:b.root_id.clone(),relative_path:b.relative_path.clone(),sha256:b.sha256.clone(),size_bytes:b.size_bytes}}
fn bytes(parent:&File,name:&str,maximum:u64,owner:u32,mount:u64)->Result<Vec<u8>> {
    let f=roots::open_child(parent,name,libc::O_RDONLY,0,true)?;roots::owned_file(&f,owner,mount)?;
    require(f.metadata()?.len()<=maximum,"FILE_BOUND")?;let mut out=Vec::new();f.take(maximum+1).read_to_end(&mut out)?;require(out.len() as u64<=maximum,"FILE_BOUND")?;Ok(out)
}
fn create(parent:&File,name:&str,raw:&[u8],owner:u32,mount:u64)->Result<()> {
    let mut f=roots::open_child(parent,name,libc::O_RDWR|libc::O_CREAT|libc::O_EXCL,0o600,true)?;roots::owned_file(&f,owner,mount)?;
    f.write_all(raw)?;f.sync_all()?;parent.sync_all()?;Ok(())
}
fn bind(root:&str,path:&str,raw:&[u8])->Binding{Binding{kind:"evidence".into(),root_id:root.into(),relative_path:path.into(),sha256:roots::hash(raw),size_bytes:raw.len() as u64}}
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]
pub enum Phase{Intent,GenerationPublished,PointerPrepared,PointerRenamed,PointerSynced,ColdVerified,OutcomePending,Confirmed}
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]
pub enum Visibility{OldCanonical,CommitUncertain,NewUnconfirmed,Confirmed}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PhaseRecord {
    pub schema_version:String,pub operation:Operation,pub store_selection_binding:Binding,
    pub runtime_selection_binding:Binding,
    pub sequence:u64,pub predecessor_sha256:Option<String>,pub phase:Phase,pub visibility:Visibility,
    pub generation_manifest_binding:Binding,pub writer_profile_binding:Binding,pub pointer_binding:Binding,pub subject_binding:Option<Binding>,
}
/// Selected exact prior directory inventory. New facts cannot be inferred from
/// mtime, a convenient pointer, or the presence of equal generation bytes.
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PriorInventory {
    pub generations:BTreeMap<String,u64>,pub orphans:BTreeMap<String,u64>,
    pub journal_directories:BTreeMap<String,Binding>,
    pub repaired_journals:BTreeMap<String,Binding>,pub retained_repair_journals:BTreeMap<String,String>,pub orphan_files:BTreeMap<String,Binding>,
}
/// Original input selections are supplied by the fixed trusted loader. This
/// interface does not authenticate a deserialized policy or issue a permit.
pub struct Inputs {
    pub store:StoreSelection,pub store_binding:Binding,pub manifest:GenerationManifest,
    pub replay_expectation_original:Vec<u8>,pub c01_store_original:Vec<u8>,
    pub old_pointer:Option<Vec<u8>>,pub prior:PriorInventory,
    pub verifier_executable:Binding,pub verifier_inputs:Vec<Binding>,pub verifier_uid:u32,
    pub commit_authority_binding:Binding,pub authority_expires_utc_ns:u64,
}
/// A fixture-only observation constructor. Actual transport must supervise the
/// separately selected process and independently attest its original bytes,
/// identity, deadline/cleanup. A raw result string cannot construct that fact.
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ColdProcessProof {
    pub schema_version:String,pub request_sha256:String,pub result_sha256:String,pub native_report_sha256:String,
    pub process_identity_binding:Binding,pub confinement_binding:Binding,pub retained_originals_binding:Binding,
    pub observed_uid:u32,pub executable_binding:Binding,pub elapsed_ms:u64,pub exit_code:i32,pub cleanup:String,
}
pub struct ColdObservation { request:ColdRequest,raw:Vec<u8>,native_report:Vec<u8>,process_original:Vec<u8>,domain:Domain }
impl ColdObservation {
    pub fn fixture(request:&ColdRequest,raw:Vec<u8>,native_report:Vec<u8>)->Result<Self>{
        let r=validate_cold(request,&raw)?;
        let fixture=bind("fixture-only","process-observation",b"fixture-only, no process custody");
        let p=ColdProcessProof{schema_version:"lab-generation-cold-process/v1".into(),request_sha256:roots::hash(&canonical(request)?),result_sha256:roots::hash(&raw),native_report_sha256:roots::hash(&native_report),process_identity_binding:fixture.clone(),confinement_binding:fixture.clone(),retained_originals_binding:fixture,observed_uid:r.workload_uid,executable_binding:r.executable_binding,elapsed_ms:r.elapsed_ms,exit_code:0,cleanup:"clean".into()};
        Self::checked(request,raw,native_report,canonical(&p)?,Domain::Fixture)
    }
    #[cfg(test)] pub(crate) fn fixture_with_process(request:&ColdRequest,raw:Vec<u8>,native_report:Vec<u8>,process_original:Vec<u8>)->Result<Self>{Self::checked(request,raw,native_report,process_original,Domain::Fixture)}
    /// U08-02 fixed cold transport only. Caller independently verifies selected
    /// executable/dependencies before launch, uses a separate enrolled UID and
    /// bounded confinement, borrows existing global locks without reentry,
    /// observes actual PID/start/credentials/exit/deadline/cleanup, and retains
    /// native original observations in approved custody. No selected callback
    /// or Python module may execute under broker identity. The passed process
    /// proof must be the exact original of that fixed supervised transport,
    /// not a caller-authored assertion. This seam implements no host transport.
    pub(crate) unsafe fn from_fixed_transport(request:&ColdRequest,raw:Vec<u8>,native_report:Vec<u8>,process_original:Vec<u8>)->Result<Self>{Self::checked(request,raw,native_report,process_original,Domain::Actual)}
    fn checked(request:&ColdRequest,raw:Vec<u8>,native_report:Vec<u8>,process_original:Vec<u8>,domain:Domain)->Result<Self>{
        let r=validate_cold(request,&raw)?;
        require(native_report.len() as u64==r.native_report_binding.size_bytes&&native_report.len()<=65536&&roots::hash(&native_report)==r.native_report_binding.sha256&&process_original.len()<=65536,"COLD_ORIGINAL_BYTES")?;
        let p:ColdProcessProof=serde_json::from_slice(&process_original).map_err(|_|Error("COLD_PROCESS_SCHEMA"))?;
        require(canonical(&p)?==process_original&&p.schema_version=="lab-generation-cold-process/v1"&&p.request_sha256==r.request_sha256&&p.result_sha256==roots::hash(&raw)&&p.native_report_sha256==roots::hash(&native_report)&&
            [&p.process_identity_binding,&p.confinement_binding,&p.retained_originals_binding].iter().all(|b|b.valid())&&p.observed_uid==request.worker_uid&&p.observed_uid!=request.broker_uid&&p.executable_binding==request.verifier_executable_binding&&p.elapsed_ms==r.elapsed_ms&&p.elapsed_ms<=request.timeout_ms&&p.exit_code==0&&p.cleanup=="clean","COLD_PROCESS_SCOPE")?;
        Ok(Self{request:request.clone(),raw,native_report,process_original,domain})
    }
}
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
struct FinalReceipt {schema_version:String,operation:Operation,pointer_binding:Binding,generation_manifest_binding:Binding,writer_profile_binding:Binding,cold_result_binding:Binding,cold_process_binding:Binding,native_original_binding:Binding,phase_head:Binding}
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
struct ConfirmedReceipt {schema_version:String,operation:Operation,terminal_binding:Binding,confirmation:HostConfirmation}
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
struct ControlRecordWitness {schema_version:String,authority_domain:String,sequence:u64,previous_sha256:String,writer:lab_control_store::ledger::WriterFence,change:Change}
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
struct MemberReceiptOriginal {schema_version:String,transition:crate::members::Transition,outcome:String}

/// One serializer for admission envelopes and actual phase/terminal records.
/// Future local hashes have fixed width; their sizes are bounded by the selected
/// ordinary limit. External receipt locators are not guessed: their exact bytes
/// are checked when returned, before acknowledgment/retention. Publication may
/// already have occurred and remains an inspectable orphan on that refusal.
struct OrdinaryRecords<'a> {
    inputs:&'a Inputs,operation:&'a Operation,runtime:&'a Binding,
    manifest:&'a Binding,profile:&'a Binding,pointer:&'a Binding,
    journal_root:&'a str,journal_name:&'a str,
}
impl OrdinaryRecords<'_> {
    fn bound(&self,raw:&[u8])->Result<()> {require(raw.len() as u64<=self.inputs.store.limits.max_record_bytes,"ORDINARY_RECORD_ENVELOPE")}
    fn local(&self,name:&str,raw:&[u8])->Binding{bind(self.journal_root,&format!("{}/{name}",self.journal_name),raw)}
    fn future(&self,name:&str)->Binding{let mut b=self.local(name,b"");b.size_bytes=self.inputs.store.limits.max_record_bytes;b}
    fn phase(&self,sequence:u64,predecessor_sha256:Option<String>,phase:Phase,visibility:Visibility,subject_binding:Option<Binding>)->PhaseRecord {
        PhaseRecord{schema_version:"lab-generation-phase/v1".into(),operation:self.operation.clone(),store_selection_binding:self.inputs.store_binding.clone(),runtime_selection_binding:self.runtime.clone(),sequence,predecessor_sha256,phase,visibility,generation_manifest_binding:self.manifest.clone(),writer_profile_binding:self.profile.clone(),pointer_binding:self.pointer.clone(),subject_binding}
    }
    fn cold(&self,broker_uid:u32)->Result<ColdRequest>{Ok(ColdRequest{repair_intent_binding:None,schema_version:"lab-generation-cold-request/v1".into(),store_selection_binding:self.inputs.store_binding.clone(),pointer_binding:self.pointer.clone(),generation_manifest_binding:self.manifest.clone(),writer_profile_binding:self.profile.clone(),member_manifest_binding:self.inputs.manifest.member_manifest_binding.clone(),original_cut_binding:self.inputs.manifest.original_cut_binding.clone(),expected_replay_result_binding:self.inputs.manifest.expected_replay_result_binding.clone(),replay_expectation:serde_json::from_slice(&self.inputs.replay_expectation_original).map_err(|_|Error("REPLAY_EXPECTATION_SCHEMA"))?,verifier_executable_binding:self.inputs.verifier_executable.clone(),verifier_input_bindings:self.inputs.verifier_inputs.clone(),broker_uid,worker_uid:self.inputs.verifier_uid,timeout_ms:self.inputs.store.limits.verifier_timeout_ms,max_result_bytes:self.inputs.store.limits.max_verifier_result_bytes})}
    fn terminal(&self,cold:Binding,process:Binding,native:Binding,phase:Binding)->FinalReceipt{FinalReceipt{schema_version:"lab-generation-terminal/v1".into(),operation:self.operation.clone(),pointer_binding:self.pointer.clone(),generation_manifest_binding:self.manifest.clone(),writer_profile_binding:self.profile.clone(),cold_result_binding:cold,cold_process_binding:process,native_original_binding:native,phase_head:phase}}
    fn confirmed(&self,terminal:Binding,confirmation:HostConfirmation)->ConfirmedReceipt{ConfirmedReceipt{schema_version:"lab-generation-confirmed/v1".into(),operation:self.operation.clone(),terminal_binding:terminal,confirmation}}
    fn preflight(&self,broker_uid:u32,confirmation:&HostConfirmation)->Result<()> {
        let phases=[(Phase::Intent,Visibility::OldCanonical,Some(self.inputs.commit_authority_binding.clone())),(Phase::GenerationPublished,Visibility::OldCanonical,None),(Phase::PointerPrepared,Visibility::OldCanonical,None),(Phase::PointerRenamed,Visibility::CommitUncertain,None),(Phase::PointerSynced,Visibility::NewUnconfirmed,None),(Phase::ColdVerified,Visibility::NewUnconfirmed,Some(self.future("cold-result.json"))),(Phase::OutcomePending,Visibility::NewUnconfirmed,Some(self.future("terminal.json"))),(Phase::Confirmed,Visibility::Confirmed,Some(self.future("confirmed.json")))];
        for (n,(phase,visibility,subject)) in phases.into_iter().enumerate(){self.bound(&canonical(&self.phase(n as u64+1,if n==0{None}else{Some("0".repeat(64))},phase,visibility,subject))?)?;}
        let request=self.cold(broker_uid)?;self.bound(&canonical(&request)?)?;
        // Lower envelope of every successful cold result: all already selected
        // repeated adapter/cut/cardinality fields and fixed protocol fields.
        // The transport's future native locator is deliberately not fabricated;
        // its exact returned form is checked with the complete observation batch.
        let minimum_native=Binding{kind:"evidence".into(),root_id:"a".into(),relative_path:"a".into(),sha256:request.replay_expectation.native_report_sha256.clone(),size_bytes:request.replay_expectation.native_report_size_bytes};
        let minimum_result=canonical(&ColdResult{schema_version:"lab-generation-cold-result/v1".into(),request_sha256:roots::hash(&canonical(&request)?),executable_binding:request.verifier_executable_binding.clone(),input_bindings:request.verifier_input_bindings.clone(),manifest_binding:request.generation_manifest_binding.clone(),original_cut_binding:request.original_cut_binding.clone(),expected_contract_binding:request.expected_replay_result_binding.clone(),native_report_binding:minimum_native,observed_cardinalities:request.replay_expectation.cardinalities.clone(),observed_adapter_bindings:request.replay_expectation.adapter_bindings.clone(),actual_exit:Some(0),outcome:"PASS".into(),cleanup:"clean".into(),workload_uid:request.worker_uid,elapsed_ms:request.timeout_ms})?;
        self.bound(&minimum_result)?;require(minimum_result.len() as u64<=request.max_result_bytes,"KNOWN_COLD_RESULT_BOUND")?;
        // Exact known original bytes and native observation count are selected
        // before publication. Future transport locators are checked on return.
        require(self.inputs.manifest.member_manifest_binding.size_bytes<=self.inputs.store.limits.max_record_bytes&&request.replay_expectation.native_report_size_bytes<=self.inputs.store.limits.max_record_bytes,"KNOWN_ORIGINAL_RECORD_BOUND")?;
        self.bound(&canonical(&self.terminal(self.future("cold-result.json"),self.future("cold-process.json"),self.future("native-replay-original.bin"),self.future("phase-06.json")))?)?;
        let mut maximum=confirmation.clone();maximum.predecessor.sequence=i64::MAX as u64;maximum.head.sequence=i64::MAX as u64;maximum.predecessor.sha256="0".repeat(64);maximum.head.sha256="0".repeat(64);
        self.bound(&canonical(&self.confirmed(self.future("terminal.json"),maximum))?)?;Ok(())
    }
}

pub struct Commit<'a> {
    root:&'a Exclusive<'a>,journal_root:&'a Exclusive<'a>,held:&'a Held<'a>,stage:Stage<'a>,
    admission:ControlAdmission<'a>,
    inputs:Inputs,operation:Operation,journal:File,journal_id:Identity,journal_name:String,
    journal_files:BTreeMap<String,Binding>,journal_identities:BTreeMap<String,Identity>,records:Vec<PhaseRecord>,manifest_binding:Binding,writer_profile_binding:Binding,
    pointer:PointerRecord,pointer_raw:Vec<u8>,pointer_binding:Binding,pointer_temp:String,pointer_identity:Option<Identity>,old_pointer_identity:Option<Identity>,
    phase:Phase,visibility:Visibility,poisoned:bool,cold_result:Option<Binding>,pending:Option<PendingCheckpoint>,
}
fn now()->Result<u64>{let n=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map_err(|_|Error("CLOCK"))?.as_nanos();require(n<=i64::MAX as u128,"CLOCK_BOUND")?;Ok(n as u64)}
impl<'a> Commit<'a> {
    /// The public constructor supports isolated fixtures only. Actual callers
    /// need the separately enrolled fixed host/cold-verifier adapter; no fallback.
    pub fn begin_fixture(root:&'a Exclusive<'a>,journal_root:&'a Exclusive<'a>,held:&'a Held<'a>,ledger:&Ledger<'_>,admission:ControlAdmission<'a>,stage:Stage<'a>,inputs:Inputs)->Result<Self>{
        require(root.root().selection().domain==Domain::Fixture&&journal_root.root().selection().domain==Domain::Fixture,"ACTUAL_HOST_PROVIDER_REQUIRED")?;
        require(admission.domain==Domain::Fixture,"ADMISSION_DOMAIN")?;Self::begin(root,journal_root,held,ledger,admission,stage,inputs)
    }
    /// Reachable only to the statically linked fixed host coordinator after it
    /// constructs actual ControlAdmission. No request parser or fixture adapter
    /// may call this. The unsafe loader boundary is in admission construction.
    pub(crate) fn begin_admitted(root:&'a Exclusive<'a>,journal_root:&'a Exclusive<'a>,held:&'a Held<'a>,ledger:&Ledger<'_>,admission:ControlAdmission<'a>,stage:Stage<'a>,inputs:Inputs)->Result<Self>{
        require(admission.domain==Domain::Actual&&root.root().selection().domain==Domain::Actual&&journal_root.root().selection().domain==Domain::Actual,"ACTUAL_CONTROL_ADMISSION")?;
        Self::begin(root,journal_root,held,ledger,admission,stage,inputs)
    }
    fn begin(root:&'a Exclusive<'a>,journal_root:&'a Exclusive<'a>,held:&'a Held<'a>,ledger:&Ledger<'_>,admission:ControlAdmission<'a>,stage:Stage<'a>,inputs:Inputs)->Result<Self>{
        root.validate()?;journal_root.validate()?;control(held.nested())?;require(held.rank()==Rank::Journal,"GLOBAL_LOCK_ORDER")?;
        admission.check(held,ledger)?;
        require(inputs.store_binding==admission.runtime_selection.store_binding&&inputs.commit_authority_binding==admission.runtime_selection.commit_authority_binding&&inputs.authority_expires_utc_ns==admission.runtime_selection.expires_utc_ns,"INDEPENDENT_COMMIT_SELECTION")?;
        inputs.store.validate()?;
        require(inputs.store.c01_selection_binding==admission.runtime_selection.c01_store_binding&&inputs.c01_store_original==c01_store(&inputs.store)?&&inputs.store.c01_selection_binding.sha256==roots::hash(&inputs.c01_store_original)&&inputs.store.c01_selection_binding.size_bytes==inputs.c01_store_original.len() as u64,"C01_STORE_ORIGINAL_JOIN")?;
        let store_raw=canonical(&inputs.store)?;
        require(inputs.store_binding.valid()&&inputs.store_binding.sha256==roots::hash(&store_raw)&&inputs.store_binding.size_bytes==store_raw.len() as u64,"STORE_SELECTION_BYTES")?;
        let snap=stage.snapshot()?;
        require(snap.operation_id==admission.runtime_selection.operation_id&&snap.fingerprint==admission.runtime_selection.original_fingerprint,"INDEPENDENT_OPERATION_SELECTION")?;
        require(snap.phase==MemberPhase::Sealed && snap.execution_scope==admission.scope &&
            snap.root==*root.root().identity() && snap.root_id==inputs.store.generations_root_id &&
            inputs.store.pointer_root_id==root.root().selection().root_id && inputs.store.control_root_binding==admission.policy_binding && inputs.store.writer_domain==admission.policy.writer_domain && inputs.store.control_root_id==admission.policy.control_root_id&&
            admission.policy.journal==JournalRootPolicy::from_runtime(journal_root.root().selection()) &&
            root.root().selection().execution_scope==journal_root.root().selection().execution_scope &&
            root.root().identity()!=journal_root.root().identity(),"STORE_ROOT_SCOPE")?;
        require(admission.domain==Domain::Fixture||(admission.reserve_binding.is_some()&&admission.reserved_bytes>=inputs.store.limits.journal_reserve_bytes),"CONTROL_RESERVE_CAPABILITY")?;
        let op=control(ledger.borrow_operation(held,&snap.operation_id,&snap.fingerprint))?.operation().clone();
        require(ledger.inspect().unresolved_operations==1 && op.store_id==inputs.store.store_id && op.store_instance==inputs.store.instance_id &&
            op.slot_epoch==snap.execution_scope.slot_epoch && op.holder==snap.execution_scope.principal_ref,"ONE_RESERVED_OPERATION")?;
        let m=&inputs.manifest;let selected_manifest=canonical(m)?;require(admission.runtime_selection.generation_manifest_binding.sha256==roots::hash(&selected_manifest)&&admission.runtime_selection.generation_manifest_binding.size_bytes==selected_manifest.len() as u64,"INDEPENDENT_MANIFEST_SELECTION")?;let native_binding=snap.sealed_manifest_binding.as_ref().ok_or(Error("SEALED_MANIFEST_REQUIRED"))?;
        require(m.schema_version=="lab-generation-manifest/v1"&&m.store_id==op.store_id&&m.creation_instance==op.store_instance&&m.writer_epoch==op.store_epoch&&
            m.operation_id==op.operation_id&&m.original_fingerprint==op.fingerprint&&m.stage_identity==snap.stage_identity&&
            Some(&m.stage_creation_binding)==snap.stage_binding.as_ref()&&m.member_manifest_binding==*native_binding&&
            m.reader_inventory_binding.valid()&&m.reader_inventory_binding.sha256==roots::hash(&canonical(&inputs.store.consumer_inventory)?)&&
            m.reader_inventory_binding.size_bytes==canonical(&inputs.store.consumer_inventory)?.len() as u64&&m.original_cut_binding.valid()&&m.expected_replay_result_binding.valid(),"GENERATION_SCOPE")?;
        roots::name(&m.generation_id)?;require(m.generation_id!=snap.stage_name&&m.generation_id!=inputs.store.pointer_member,"GENERATION_NAME")?;
        let declared:BTreeSet<_>=inputs.store.member_inventory.iter().map(|r|r.relative_path.clone()).collect();
        require(declared==m.members.keys().cloned().collect()&&declared==snap.members.keys().cloned().collect(),"COMPLETE_MEMBER_INVENTORY")?;
        let mut total=0u64;
        for(path,b)in &m.members {let member=&snap.members[path];require(b.valid()&&b.root_id==snap.root_id&&b.relative_path==format!("{}/{path}",m.generation_id)&&b.sha256==member.full_sha256&&b.size_bytes==member.full_length&&b.size_bytes<=inputs.store.limits.max_member_bytes,"GENERATION_MEMBER")?;total=total.checked_add(b.size_bytes).ok_or(Error("SIZE_OVERFLOW"))?;}
        require(total<=inputs.store.limits.max_stage_bytes,"STAGE_CAPACITY")?;
        let old_binding=if let Some(raw)=&inputs.old_pointer {let p:PointerRecord=serde_json::from_slice(raw).map_err(|_|Error("OLD_POINTER_SCHEMA"))?;p.validate()?;require(canonical(&p)?==*raw&&p.logical_store_id==m.store_id&&p.sequence.checked_add(1)==Some(m.sequence)&&p.writer_epoch<=m.writer_epoch,"POINTER_PREDECESSOR")?;Some(bind(&inputs.store.pointer_root_id,&inputs.store.pointer_member,raw))}else{require(m.sequence==1,"GENESIS_SEQUENCE")?;None};
        require(m.predecessor_pointer_binding==old_binding,"PREDECESSOR_BINDING")?;
        require(inputs.commit_authority_binding.valid()&&now()?<inputs.authority_expires_utc_ns&&inputs.authority_expires_utc_ns<=i64::MAX as u64,"CURRENT_COMMIT_AUTHORITY")?;
        require(inputs.verifier_executable.valid()&&inputs.verifier_executable.kind=="execution"&&inputs.verifier_uid>0&&inputs.verifier_uid<u32::MAX&&inputs.verifier_uid!=snap.root.uid&&inputs.verifier_inputs.len()<=128&&inputs.verifier_inputs.iter().all(Binding::valid),"VERIFIER_SELECTION")?;
        let expectation:ReplayExpectation=serde_json::from_slice(&inputs.replay_expectation_original).map_err(|_|Error("REPLAY_EXPECTATION_SCHEMA"))?;expectation.validate()?;
        require(inputs.replay_expectation_original.len()<=65536&&canonical(&expectation)?==inputs.replay_expectation_original&&m.expected_replay_result_binding.sha256==roots::hash(&inputs.replay_expectation_original)&&m.expected_replay_result_binding.size_bytes==inputs.replay_expectation_original.len() as u64&&
            expectation.original_cut_binding==m.original_cut_binding&&expectation.source_cut==m.source_cut&&expectation.reader_inventory_binding==m.reader_inventory_binding&&expectation.member_inventory_binding.sha256==roots::hash(&canonical(&inputs.store.member_inventory)?)&&expectation.member_inventory_binding.size_bytes==canonical(&inputs.store.member_inventory)?.len() as u64&&expectation.adapter_bindings==inputs.verifier_inputs,"REPLAY_EXPECTATION_SELECTION")?;
        Self::check_prior(root,journal_root,held,ledger,&admission,&inputs,&snap.stage_name,total)?;
        restart::remaining_capacity(&admission,journal_root,&inputs.store.limits)?;
        Self::compare_pointer(root,&inputs.store.pointer_member,&inputs.old_pointer)?;
        let old_pointer_identity=if inputs.old_pointer.is_some(){Some(Identity::observe(&roots::open_child(root.directory(),&inputs.store.pointer_member,libc::O_RDONLY,0,true)?)?)}else{None};
        let journal_name=format!("commit-{}",op.operation_id);roots::name(&journal_name)?;
        restart::repair_capacity_before_commit(journal_root,&admission,&inputs,&op,&journal_name)?;
        let manifest_raw=canonical(m)?;require(manifest_raw.len() as u64<=inputs.store.limits.max_record_bytes,"MANIFEST_BOUND")?;
        let writer_profile_binding=bind(&journal_root.root().selection().root_id,&format!("{journal_name}/manifest.json"),&manifest_raw);
        let manifest_binding=bind(&journal_root.root().selection().root_id,&format!("{journal_name}/c01-manifest.json"),&c01_manifest(m)?);
        let pointer=PointerRecord{schema_version:"lab-completion-pointer-record/v1".into(),logical_store_id:m.store_id.clone(),writer_epoch:m.writer_epoch,sequence:m.sequence,predecessor_pointer_binding:old_binding,generation_manifest_binding:manifest_binding.clone(),operation_id:op.operation_id.clone()};pointer.validate()?;
        let pointer_raw=canonical(&pointer)?;let pointer_binding=bind(&inputs.store.pointer_root_id,&inputs.store.pointer_member,&pointer_raw);
        let pointer_temp=format!("pointer-{}",op.operation_id);roots::name(&pointer_temp)?;
        let limit=inputs.store.limits.max_record_bytes;
        for raw in [&manifest_raw,&c01_manifest(m)?,&inputs.c01_store_original,&store_raw,&canonical(&admission.policy)?,&inputs.replay_expectation_original,&canonical(&admission.runtime_selection)?,&pointer_raw]{require(raw.len() as u64<=limit,"INITIAL_RECORD_BOUND")?;}
        let runtime_binding=bind(&journal_root.root().selection().root_id,&format!("{journal_name}/runtime-selection.json"),&canonical(&admission.runtime_selection)?);
        OrdinaryRecords{inputs:&inputs,operation:&op,runtime:&runtime_binding,manifest:&manifest_binding,profile:&writer_profile_binding,pointer:&pointer_binding,journal_root:&journal_root.root().selection().root_id,journal_name:&journal_name}.preflight(root.root().identity().uid,&admission.confirmation)?;
        let journal=roots::mkdir(journal_root.directory(),&journal_name)?;
        let journal_id=roots::owned_dir(&journal,journal_root.root().identity().uid,journal_root.root().identity().mount_id)?;
        let mut this=Self{root,journal_root,held,stage,admission,inputs,operation:op,journal,journal_id,journal_name,journal_files:BTreeMap::new(),journal_identities:BTreeMap::new(),records:vec![],manifest_binding,writer_profile_binding,pointer,pointer_raw,pointer_binding,pointer_temp,pointer_identity:None,old_pointer_identity,phase:Phase::Intent,visibility:Visibility::OldCanonical,poisoned:false,cold_result:None,pending:None};
        this.put("manifest.json",&manifest_raw)?;this.put("c01-manifest.json",&c01_manifest(&this.inputs.manifest)?)?;this.put("c01-store.json",&this.inputs.c01_store_original.clone())?;this.put("store.json",&store_raw)?;this.put("control-policy.json",&canonical(&this.admission.policy)?)?;this.put("replay-expectation.json",&this.inputs.replay_expectation_original.clone())?;
        this.put("runtime-selection.json",&canonical(&this.admission.runtime_selection)?)?;this.append(Phase::Intent,Some(this.inputs.commit_authority_binding.clone()))?;Ok(this)
    }
    fn check_prior(root:&'a Exclusive<'a>,journal:&'a Exclusive<'a>,held:&'a Held<'a>,ledger:&Ledger<'_>,admission:&ControlAdmission<'a>,i:&Inputs,stage:&str,new_bytes:u64)->Result<()> {
        let l=&i.store.limits;require(i.prior.generations.len() as u64+1<=l.retained_generation_count&&i.prior.orphans.len() as u64+1<=l.retained_orphan_count,"RETAINED_COUNT_CAPACITY")?;
        let mut expected=vec![stage.to_string()];let mut generation_bytes=0u64;let mut orphan_bytes=0u64;
        for (map,total) in [(&i.prior.generations,&mut generation_bytes),(&i.prior.orphans,&mut orphan_bytes)] {
            for(name,selected_bytes)in map {roots::name(name)?;require(!expected.contains(name),"INVENTORY_ALIAS")?;expected.push(name.clone());let f=roots::open_child(root.directory(),name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;let actual=tree_bytes(&f,root.root().identity(),0,&mut 0)?;require(actual==*selected_bytes,"RETAINED_BYTES_CHANGED")?;*total=total.checked_add(actual).ok_or(Error("CAPACITY_OVERFLOW"))?;}
        }
        for(name,b)in &i.prior.orphan_files{roots::name(name)?;require(!expected.contains(name)&&b.valid()&&b.root_id==i.store.generations_root_id&&b.relative_path==*name,"ORPHAN_FILE_SELECTION")?;let raw=bytes(root.directory(),name,l.max_record_bytes,root.root().identity().uid,root.root().identity().mount_id)?;require(bind(&b.root_id,&b.relative_path,&raw)==*b,"ORPHAN_FILE_BYTES")?;orphan_bytes=orphan_bytes.checked_add(raw.len() as u64).ok_or(Error("CAPACITY_OVERFLOW"))?;expected.push(name.clone());}
        require(i.prior.orphans.len()+i.prior.orphan_files.len()+1<=l.retained_orphan_count as usize,"ORPHAN_COUNT_CAPACITY")?;
        require(generation_bytes.checked_add(new_bytes).is_some_and(|n|n<=l.retained_generation_bytes)&&orphan_bytes.checked_add(new_bytes).is_some_and(|n|n<=l.retained_orphan_bytes),"RETAINED_BYTE_CAPACITY")?;
        if i.old_pointer.is_some(){require(!expected.contains(&i.store.pointer_member),"POINTER_ALIAS")?;expected.push(i.store.pointer_member.clone())}expected.sort();require(roots::names(root.directory(),8193)?==expected,"UNKNOWN_ROOT_ENTRY")?;
        let mut expected_journals:BTreeSet<String>=i.prior.journal_directories.keys().cloned().collect();
        for(name,b)in &i.prior.repaired_journals{require(expected_journals.insert(name.clone()),"REPAIRED_JOURNAL_DUPLICATE")?;let branch=b.relative_path.split('/').next().ok_or(Error("REPAIRED_PATH"))?;require(expected_journals.insert(branch.into()),"REPAIRED_BRANCH_DUPLICATE")?;}
        for(name,digest)in &i.prior.retained_repair_journals{require(name.starts_with("recovery-")&&roots::digest(digest)&&expected_journals.insert(name.clone()),"REPAIR_RESIDUE_SELECTION")?;}
        restart::journal_capacity(expected_journals.len(),2)?;require(roots::names(journal.directory(),restart::JOURNAL_CEILING+1)?==expected_journals.into_iter().collect::<Vec<_>>(),"JOURNAL_INVENTORY")?;
        require(i.prior.journal_directories.len()+i.prior.repaired_journals.len()<=4096,"PRIOR_JOURNAL_BOUND")?;
        let mut pointers=BTreeMap::new();let mut generations=BTreeSet::new();let mut selected_residue=BTreeMap::new();
        for(name,binding)in &i.prior.journal_directories {
            let (pointer,generation)=prior_journal(root,journal,ledger,admission,name,binding,l.max_record_bytes)?;
            require(pointer.logical_store_id==i.store.store_id&&pointers.insert(pointer.sequence,pointer).is_none()&&generations.insert(generation),"PRIOR_STORE_OR_DUPLICATE")?;
        }
        for(name,binding)in &i.prior.repaired_journals{let proof=restart::repaired_journal(root,journal,held,ledger,admission,name,binding)?;for(n,d)in proof.retained_journals(){if let Some(old)=selected_residue.insert(n.clone(),d.clone()){require(old==*d,"REPAIR_RESIDUE_CONFLICT")?;}}if let Some(pointer)=proof.pointer(){require(pointer.logical_store_id==i.store.store_id&&pointers.insert(pointer.sequence,pointer.clone()).is_none()&&generations.insert(proof.generation().into()),"REPAIRED_STORE_OR_DUPLICATE")?;}else{require(!i.prior.generations.contains_key(proof.generation()),"ABORTED_GENERATION_NOT_CANONICAL")?;}}
        let observed_journals=restart::journal_inventory(journal,None)?;for(n,d)in &i.prior.retained_repair_journals{require(selected_residue.get(n)==Some(d)&&observed_journals.get(n)==Some(d),"UNSETTLED_REPAIR_RESIDUE")?;}
        require(generations==i.prior.generations.keys().cloned().collect(),"GENERATION_JOURNAL_COVERAGE")?;
        let mut predecessor=None;
        for(index,(sequence,pointer))in pointers.iter().enumerate(){require(*sequence==index as u64+1&&pointer.predecessor_pointer_binding==predecessor,"PRIOR_POINTER_CHAIN")?;predecessor=Some(bind(&i.store.pointer_root_id,&i.store.pointer_member,&canonical(pointer)?));}
        require(predecessor==i.old_pointer.as_ref().map(|raw|bind(&i.store.pointer_root_id,&i.store.pointer_member,raw)),"CURRENT_POINTER_CONFIRMED_HEAD")?;
        let mut v:libc::statvfs=unsafe{std::mem::zeroed()};require(unsafe{libc::fstatvfs(journal.directory().as_raw_fd(),&mut v)}==0,"CAPACITY_OBSERVATION")?;
        require((v.f_bavail as u128)*(v.f_frsize as u128)>=l.journal_reserve_bytes as u128&&v.f_favail>=l.journal_reserve_inodes,"CONTROL_RESERVE")?;Ok(())
    }
    fn compare_pointer(root:&Exclusive<'_>,name:&str,expected:&Option<Vec<u8>>)->Result<()> {
        root.validate()?;let present=roots::names(root.directory(),8193)?.iter().any(|n|n==name);
        match expected {None=>require(!present,"POINTER_PREIMAGE"),Some(raw)=>require(present&&bytes(root.directory(),name,1_048_576,root.root().identity().uid,root.root().identity().mount_id)?==*raw,"POINTER_PREIMAGE")}
    }
    fn guard(&self)->Result<()> {
        require(!self.poisoned,"COMMIT_QUARANTINED")?;control(self.held.nested())?;self.root.validate()?;self.journal_root.validate()?;control(self.admission.control_root.validate())?;
        let named=roots::open_child(self.journal_root.directory(),&self.journal_name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        require(Identity::observe(&named)?==self.journal_id&&Identity::observe(&self.journal)?==self.journal_id,"JOURNAL_ATTACHMENT")?;
        require(roots::names(&self.journal,32)?==self.journal_files.keys().cloned().collect::<Vec<_>>(),"JOURNAL_HISTORY_INVENTORY")?;
        for(name,b)in &self.journal_files{let f=roots::open_child(&self.journal,name,libc::O_RDONLY,0,true)?;require(self.journal_identities.get(name)==Some(&Identity::observe(&f)?),"JOURNAL_FILE_ATTACHMENT")?;let raw=bytes(&self.journal,name,self.inputs.store.limits.max_record_bytes,self.journal_id.uid,self.journal_id.mount_id)?;require(bind(&b.root_id,&b.relative_path,&raw)==*b,"JOURNAL_HISTORY_CHANGED")?;}Ok(())
    }
    fn put(&mut self,name:&str,raw:&[u8])->Result<Binding>{
        require(raw.len() as u64<=self.inputs.store.limits.max_record_bytes&&self.journal_files.len()<31,"JOURNAL_BOUND")?;
        create(&self.journal,name,raw,self.journal_id.uid,self.journal_id.mount_id)?;
        let b=bind(&self.journal_root.root().selection().root_id,&format!("{}/{name}",self.journal_name),raw);self.journal_files.insert(name.into(),b.clone());self.journal_identities.insert(name.into(),Identity::observe(&roots::open_child(&self.journal,name,libc::O_RDONLY,0,true)?)?);Ok(b)
    }
    fn envelope(&self)->OrdinaryRecords<'_>{OrdinaryRecords{inputs:&self.inputs,operation:&self.operation,runtime:&self.journal_files["runtime-selection.json"],manifest:&self.manifest_binding,profile:&self.writer_profile_binding,pointer:&self.pointer_binding,journal_root:&self.journal_root.root().selection().root_id,journal_name:&self.journal_name}}
    fn next_phase(&self,phase:Phase,visibility:Visibility,subject:Option<Binding>)->Result<PhaseRecord>{let predecessor=self.records.last().map(canonical).transpose()?.map(|b|roots::hash(&b));let r=self.envelope().phase(self.records.len() as u64+1,predecessor,phase,visibility,subject);self.envelope().bound(&canonical(&r)?)?;Ok(r)}
    fn append(&mut self,phase:Phase,subject:Option<Binding>)->Result<()> {
        let r=self.next_phase(phase,self.visibility,subject)?;
        self.put(&format!("phase-{:02}.json",r.sequence),&canonical(&r)?)?;self.records.push(r);self.phase=phase;Ok(())
    }
    fn step<T>(&mut self,f:impl FnOnce(&mut Self)->Result<T>)->Result<T>{if let Err(e)=self.guard(){self.poisoned=true;return Err(e)}let r=f(self);if r.is_err(){self.poisoned=true}r}
    pub fn phase(&self)->Phase{self.phase}
    pub fn visibility(&self)->Visibility{self.visibility}
    pub fn quarantined(&self)->bool{self.poisoned}
    pub fn journal_name(&self)->&str{&self.journal_name}
    pub fn publish(&mut self,action:&Action,member_manifest:&[u8])->Result<()> {self.step(|s|{
        require(s.phase==Phase::Intent,"COMMIT_PHASE")?;s.current()?;
        let native:MemberManifest=serde_json::from_slice(member_manifest).map_err(|_|Error("NATIVE_MANIFEST_SCHEMA"))?;
        require(native.generation_name==s.inputs.manifest.generation_id&&native.fingerprint==s.operation.fingerprint&&native.operation_id==s.operation.operation_id,"NATIVE_MANIFEST_SCOPE")?;
        s.envelope().bound(member_manifest)?;
        s.stage.publish(action,member_manifest)?;boundary(1)?;s.put("member-manifest.json",member_manifest)?;Ok(())
    })}
    pub fn publication_pending(&self)->Option<&crate::members::Transition>{self.stage.pending()}
    pub fn acknowledge_publication(&mut self,receipt:DurableReceipt,original:&[u8])->Result<()> {self.step(|s|{
        require(s.phase==Phase::Intent&&receipt.binding().size_bytes==original.len() as u64&&receipt.binding().sha256==roots::hash(original),"PUBLICATION_ORIGINAL")?;s.envelope().bound(original)?;s.next_phase(Phase::GenerationPublished,Visibility::OldCanonical,Some(receipt.binding().clone()))?;s.stage.acknowledge(receipt)?;let snap=s.stage.snapshot()?;require(snap.phase==MemberPhase::Published&&snap.stage_name==s.inputs.manifest.generation_id,"PUBLICATION_STATE")?;
        s.put("publication-original.json",original)?;
        s.append(Phase::GenerationPublished,snap.last_receipt_binding)?;Ok(())
    })}
    fn current_pointer(&self)->Result<()>{
        Self::compare_pointer(self.root,&self.inputs.store.pointer_member,&Some(self.pointer_raw.clone()))?;
        require(self.pointer_identity.as_ref()==Some(&Identity::observe(&roots::open_child(self.root.directory(),&self.inputs.store.pointer_member,libc::O_RDONLY,0,true)?)?),"CURRENT_POINTER_ATTACHMENT")
    }
    fn current(&self)->Result<()> {
        require(now()?<self.inputs.authority_expires_utc_ns,"COMMIT_AUTHORITY_EXPIRED")?;
        // An exclusive Held prevents a second lock owner, not a mutation by the
        // same fixed caller. Reopen the exact selected host-confirmed head and
        // reborrow the original active slot/store/operation on every positive
        // boundary. This borrows existing locks; it never adopts a newer head.
        let current=self.admission.open(self.held)?;
        let borrowed=control(current.borrow_operation(self.held,&self.operation.operation_id,&self.operation.fingerprint))?;
        require(borrowed.operation()==&self.operation&&current.inspect().unresolved_operations==1,"CURRENT_CONTROL_OPERATION")?;
        require(now()?<self.inputs.authority_expires_utc_ns,"COMMIT_AUTHORITY_EXPIRED")
    }
    pub fn prepare_pointer(&mut self)->Result<()> {self.step(|s|{
        require(s.phase==Phase::GenerationPublished,"COMMIT_PHASE")?;s.current()?;s.stage.snapshot()?;
        let mut f=roots::open_child(s.root.directory(),&s.pointer_temp,libc::O_RDWR|libc::O_CREAT|libc::O_EXCL,0o600,true)?;roots::owned_file(&f,s.root.root().identity().uid,s.root.root().identity().mount_id)?;
        s.pointer_identity=Some(Identity::observe(&f)?);f.write_all(&s.pointer_raw)?;boundary(2)?;let mut held=vec![0;s.pointer_raw.len()];f.read_exact_at(&mut held,0)?;require(held==s.pointer_raw,"POINTER_WRITE_VERIFY")?;sync_at(&f,1)?;boundary(3)?;sync_at(s.root.directory(),2)?;
        s.append(Phase::PointerPrepared,None)
    })}
    pub fn activate_pointer(&mut self)->Result<()> {self.step(|s|{
        require(s.phase==Phase::PointerPrepared,"COMMIT_PHASE")?;s.current()?;s.stage.snapshot()?;
        Self::compare_pointer(s.root,&s.inputs.store.pointer_member,&s.inputs.old_pointer)?;
        if let Some(expected)=&s.old_pointer_identity{require(Identity::observe(&roots::open_child(s.root.directory(),&s.inputs.store.pointer_member,libc::O_RDONLY,0,true)?)?==*expected,"OLD_POINTER_ATTACHMENT")?;}
        require(s.pointer_identity.as_ref()==Some(&Identity::observe(&roots::open_child(s.root.directory(),&s.pointer_temp,libc::O_RDONLY,0,true)?)?),"POINTER_TEMP_ATTACHMENT")?;
        require(bytes(s.root.directory(),&s.pointer_temp,1_048_576,s.root.root().identity().uid,s.root.root().identity().mount_id)?==s.pointer_raw,"POINTER_TEMP_CHANGED")?;
        let old=roots::name(&s.pointer_temp)?;let new=roots::name(&s.inputs.store.pointer_member)?;
        require(unsafe{libc::renameat2(s.root.directory().as_raw_fd(),old.as_ptr(),s.root.directory().as_raw_fd(),new.as_ptr(),0)}==0,"POINTER_RENAME")?;
        s.visibility=Visibility::CommitUncertain;boundary(4)?;s.append(Phase::PointerRenamed,None)?;
        sync_at(s.root.directory(),3)?;boundary(5)?;s.visibility=Visibility::NewUnconfirmed;s.append(Phase::PointerSynced,None)
    })}
    pub fn cold_request(&self)->Result<ColdRequest>{self.guard()?;self.current()?;require(self.phase==Phase::PointerSynced,"COLD_PHASE")?;self.envelope().cold(self.root.root().identity().uid)}
    pub fn accept_cold(&mut self,observation:ColdObservation)->Result<()> {self.step(|s|{
        let expected=s.cold_request()?;require(observation.domain==s.root.root().selection().domain&&observation.request==expected,"COLD_OBSERVATION_SCOPE")?;validate_cold(&expected,&observation.raw)?;boundary(6)?;
        s.stage.snapshot()?;s.current_pointer()?;
        let request_raw=canonical(&expected)?;
        for raw in [&request_raw,&observation.native_report,&observation.process_original,&observation.raw]{s.envelope().bound(raw)?;}
        let result_binding=s.envelope().local("cold-result.json",&observation.raw);s.next_phase(Phase::ColdVerified,Visibility::NewUnconfirmed,Some(result_binding))?;
        s.put("cold-request.json",&request_raw)?;s.put("native-replay-original.bin",&observation.native_report)?;s.put("cold-process.json",&observation.process_original)?;
        let b=s.put("cold-result.json",&observation.raw)?;s.cold_result=Some(b.clone());s.append(Phase::ColdVerified,Some(b))
    })}
    pub fn persist_outcome(&mut self,ledger:&mut Ledger<'_>)->Result<()> {self.step(|s|{
        require(s.phase==Phase::ColdVerified,"OUTCOME_PHASE")?;s.current()?;
        s.admission.check(s.held,ledger)?;
        let borrowed=control(ledger.borrow_operation(s.held,&s.operation.operation_id,&s.operation.fingerprint))?;require(borrowed.operation()==&s.operation,"CONTROL_OPERATION_CHANGED")?;drop(borrowed);
        s.stage.snapshot()?;s.current_pointer()?;
        let head=s.journal_files[&format!("phase-{:02}.json",s.records.len())].clone();
        let r=s.envelope().terminal(s.cold_result.clone().ok_or(Error("COLD_MISSING"))?,s.journal_files["cold-process.json"].clone(),s.journal_files["native-replay-original.bin"].clone(),head);
        let raw=canonical(&r)?;s.envelope().bound(&raw)?;let expected=s.envelope().local("terminal.json",&raw);s.next_phase(Phase::OutcomePending,Visibility::NewUnconfirmed,Some(expected))?;
        let b=s.put("terminal.json",&raw)?;boundary(7)?;s.current()?;
        let pending=control(ledger.append(s.held,Change::Outcome{operation_id:s.operation.operation_id.clone(),fingerprint:s.operation.fingerprint.clone(),result_binding:byte_binding(&b),outcome:Outcome::Committed}))?;s.pending=Some(pending);boundary(8)?;s.append(Phase::OutcomePending,Some(b))
    })}
    pub fn requested_confirmation(&self)->Result<&HostConfirmation>{self.guard()?;require(self.phase==Phase::OutcomePending,"OUTCOME_PENDING_REQUIRED")?;Ok(self.pending.as_ref().ok_or(Error("PENDING_MISSING"))?.requested_confirmation())}
    pub fn acknowledge_outcome(&mut self,ledger:&mut Ledger<'_>,confirmation:HostConfirmation)->Result<()> {self.step(|s|{
        require(s.phase==Phase::OutcomePending,"OUTCOME_PENDING_REQUIRED")?;require(s.pending.as_ref().is_some_and(|p|p.requested_confirmation()==&confirmation),"HOST_CONFIRMATION_SCOPE")?;
        s.stage.snapshot()?;s.current_pointer()?;
        let r=s.envelope().confirmed(s.journal_files["terminal.json"].clone(),confirmation.clone());let raw=canonical(&r)?;s.envelope().bound(&raw)?;let expected=s.envelope().local("confirmed.json",&raw);s.next_phase(Phase::Confirmed,Visibility::Confirmed,Some(expected))?;
        let p=s.pending.take().ok_or(Error("PENDING_MISSING"))?;let acknowledged=control(ledger.acknowledge(s.held,p,confirmation))?;s.admission.confirmation=acknowledged.confirmation().clone();boundary(9)?;
        let b=s.put("confirmed.json",&raw)?;s.visibility=Visibility::Confirmed;s.append(Phase::Confirmed,Some(b))
    })}
    /// Identity-only pinned result. Original per-consumer disclosure permission
    /// is intentionally absent; U08-02 must independently admit each read.
    pub fn confirmed_selection(&self)->Result<PointerRecord>{self.guard()?;require(self.phase==Phase::Confirmed&&self.visibility==Visibility::Confirmed,"READ_WRITE_FENCE")?;self.stage.snapshot()?;self.current_pointer()?;Ok(self.pointer.clone())}
    #[cfg(test)] pub(crate) fn fixture_prior_recheck_at_successor_limit(&self,ledger:&Ledger<'_>,successor_limit:u64)->Result<PointerRecord>{require(self.admission.domain==Domain::Fixture,"FIXTURE_ONLY")?;self.admission.check(self.held,ledger)?;Ok(prior_journal(self.root,self.journal_root,ledger,&self.admission,&self.journal_name,&self.journal_files["confirmed.json"],successor_limit)?.0)}
    #[cfg(test)] pub(crate) fn fixture_prior_recheck(&self,ledger:&Ledger<'_>)->Result<PointerRecord>{require(self.admission.domain==Domain::Fixture,"FIXTURE_ONLY")?;self.admission.check(self.held,ledger)?;Ok(prior_journal(self.root,self.journal_root,ledger,&self.admission,&self.journal_name,&self.journal_files["confirmed.json"],self.inputs.store.limits.max_record_bytes)?.0)}
}
fn tree_bytes(dir:&File,id:&Identity,depth:usize,count:&mut usize)->Result<u64>{
    require(depth<=32&&*count<=65536,"RETAINED_INVENTORY_BOUND")?;roots::owned_dir(dir,id.uid,id.mount_id)?;let mut total=0u64;
    for name in roots::names(dir,65537)?{*count+=1;require(*count<=65536,"RETAINED_INVENTORY_BOUND")?;let f=roots::open_child(dir,&name,libc::O_RDONLY,0,true)?;let m=f.metadata()?;
        let n=if m.is_dir(){tree_bytes(&f,id,depth+1,count)?}else{roots::owned_file(&f,id.uid,id.mount_id)?;m.len()};total=total.checked_add(n).ok_or(Error("CAPACITY_OVERFLOW"))?;
    }Ok(total)
}

fn decode<T:serde::de::DeserializeOwned+Serialize>(raw:&[u8])->Result<T>{let v:T=serde_json::from_slice(raw).map_err(|_|Error("JOURNAL_CLOSED_SCHEMA"))?;require(canonical(&v)?==raw,"JOURNAL_CANONICAL_BYTES")?;Ok(v)}
fn prior_journal(root:&Exclusive<'_>,journal:&Exclusive<'_>,ledger:&Ledger<'_>,admission:&ControlAdmission<'_>,name:&str,selected:&Binding,_successor_maximum:u64)->Result<(PointerRecord,String)>{
    roots::name(name)?;require(selected.valid()&&selected.root_id==journal.root().selection().root_id&&[format!("{name}/confirmed.json"),format!("{name}/terminal.json")].contains(&selected.relative_path),"JOURNAL_SELECTION")?;
    let dir=roots::open_child(journal.directory(),name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
    let id=roots::owned_dir(&dir,journal.root().identity().uid,journal.root().identity().mount_id)?;
    let mandatory=["manifest.json","c01-manifest.json","c01-store.json","runtime-selection.json","store.json","control-policy.json","replay-expectation.json","member-manifest.json","publication-original.json","cold-request.json","cold-result.json","native-replay-original.bin","cold-process.json","terminal.json"];
    let present=roots::names(&dir,32)?;
    let mut expected:Vec<String>=mandatory.iter().map(|s|s.to_string()).chain((1..=6).map(|n|format!("phase-{n:02}.json"))).collect();
    let mut phase_count=6;
    if present.contains(&"phase-07.json".into()){expected.push("phase-07.json".into());phase_count=7;}
    if present.contains(&"confirmed.json".into()){require(phase_count==7,"PRIOR_WRAPPER_ORDER")?;expected.push("confirmed.json".into());}
    if present.contains(&"phase-08.json".into()){require(present.contains(&"confirmed.json".into()),"PRIOR_WRAPPER_ORDER")?;expected.push("phase-08.json".into());phase_count=8;}
    expected.sort();require(present==expected,"PRIOR_JOURNAL_FULL_INVENTORY")?;
    let store_raw=bytes(&dir,"store.json",restart::RECORD_CEILING,id.uid,id.mount_id)?;let original_store:StoreSelection=decode(&store_raw)?;original_store.validate()?;let maximum=original_store.limits.max_record_bytes;require(store_raw.len() as u64<=maximum,"PRIOR_STORE_BOUND")?;let mut raw=BTreeMap::new();for n in &expected {raw.insert(n.clone(),bytes(&dir,n,maximum,id.uid,id.mount_id)?);}
    let local=|n:&str|bind(&selected.root_id,&format!("{name}/{n}"),&raw[n]);
    let selected_name=selected.relative_path.rsplit('/').next().ok_or(Error("JOURNAL_SELECTION"))?;
    require(raw.contains_key(selected_name)&&local(selected_name)==*selected,"JOURNAL_CONFIRMATION_BYTES")?;
    let confirmed:Option<ConfirmedReceipt>=raw.get("confirmed.json").map(|r|decode(r)).transpose()?;
    let terminal:FinalReceipt=decode(&raw["terminal.json"])?;
    let manifest:GenerationManifest=decode(&raw["manifest.json"])?;
    let store:StoreSelection=decode(&raw["store.json"])?;store.validate()?;require(c01_store(&store)?==raw["c01-store.json"]&&store.c01_selection_binding.sha256==roots::hash(&raw["c01-store.json"])&&store.c01_selection_binding.size_bytes==raw["c01-store.json"].len() as u64&&c01_manifest(&manifest)?==raw["c01-manifest.json"],"PRIOR_C01_PROJECTION")?;
    let runtime:RuntimeCommitSelection=decode(&raw["runtime-selection.json"])?;
    require(runtime.execution_scope.valid()&&runtime.store_binding.sha256==roots::hash(&raw["store.json"])&&runtime.store_binding.size_bytes==raw["store.json"].len() as u64&&runtime.c01_store_binding==store.c01_selection_binding&&runtime.generation_manifest_binding.sha256==roots::hash(&raw["manifest.json"])&&runtime.generation_manifest_binding.size_bytes==raw["manifest.json"].len() as u64&&runtime.operation_id==manifest.operation_id&&runtime.original_fingerprint==manifest.original_fingerprint&&runtime.execution_scope.store_id==manifest.store_id&&runtime.execution_scope.instance_id==manifest.creation_instance,"PRIOR_RUNTIME_SELECTION")?;
    let policy:ControlPolicy=decode(&raw["control-policy.json"])?;
    require(policy.schema_version=="lab-generation-control-policy/v1"&&policy.control_root==admission.policy.control_root&&policy.authority_domain==admission.policy.authority_domain&&policy.header_sha256==admission.policy.header_sha256&&policy.journal==admission.policy.journal&&policy.writer_domain==store.writer_domain&&policy.control_root_id==store.control_root_id&&policy.control_root_id==admission.policy.control_root_id,"PRIOR_CONTROL_DOMAIN")?;
    require(store.control_root_binding.sha256==roots::hash(&raw["control-policy.json"])&&store.control_root_binding.size_bytes==raw["control-policy.json"].len() as u64,"PRIOR_CONTROL_POLICY_BYTES")?;
    require(terminal.schema_version=="lab-generation-terminal/v1"&&ledger.operation(&terminal.operation.operation_id)==Some(&terminal.operation)&&ledger.outcome(&terminal.operation.operation_id)==Some(&(Outcome::Committed,byte_binding(&local("terminal.json")))),"UNRESOLVED_PRIOR_JOURNAL")?;
    // The selected current host-confirmed Ledger verifies the original outcome.
    // Missing post-outcome wrappers remain missing; they are never synthesized.
    if let Some(confirmed)=&confirmed {
        require(confirmed.schema_version=="lab-generation-confirmed/v1"&&confirmed.operation==terminal.operation&&confirmed.terminal_binding==local("terminal.json"),"PRIOR_WRAPPER_SCOPE")?;
    let conf=&confirmed.confirmation;
    require(conf.schema_version=="lab-host-control-confirmation/v1"&&conf.authority_domain==admission.confirmation.authority_domain&&conf.root==admission.confirmation.root&&conf.header_sha256==admission.confirmation.header_sha256&&conf.head.sequence>0&&conf.head.sequence<=admission.confirmation.head.sequence&&conf.predecessor.sequence.checked_add(1)==Some(conf.head.sequence),"PRIOR_HOST_CONFIRMATION_DOMAIN")?;
    // Independently opened, exact control root; accepted Ledger has already
    // validated its entire chain to the current selected host head. Select the
    // historical outcome record by exact sequence/hash, never by a wrapper alone.
    let records=roots::open_child(&admission.control_directory,"records",libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
    let rid=roots::owned_dir(&records,id.uid,id.mount_id)?;
    let record_raw=bytes(&records,&format!("{:016}.json",conf.head.sequence),65536,rid.uid,rid.mount_id)?;
    let record:ControlRecordWitness=control(lab_control_store::codec::decode(&record_raw))?;
    require(roots::hash(&record_raw)==conf.head.sha256&&record.schema_version=="lab-control-record/v1"&&record.sequence==conf.head.sequence&&record.previous_sha256==conf.predecessor.sha256&&record.authority_domain==conf.authority_domain&&record.writer==conf.writer&&
        record.change==Change::Outcome{operation_id:terminal.operation.operation_id.clone(),fingerprint:terminal.operation.fingerprint.clone(),result_binding:byte_binding(&local("terminal.json")),outcome:Outcome::Committed},"PRIOR_CONTROL_RECORD_JOIN")?;
    }
    let pointer=PointerRecord{schema_version:"lab-completion-pointer-record/v1".into(),logical_store_id:manifest.store_id.clone(),writer_epoch:manifest.writer_epoch,sequence:manifest.sequence,predecessor_pointer_binding:manifest.predecessor_pointer_binding.clone(),generation_manifest_binding:local("c01-manifest.json"),operation_id:manifest.operation_id.clone()};pointer.validate()?;
    let pointer_binding=bind(&store.pointer_root_id,&store.pointer_member,&canonical(&pointer)?);
    require(manifest.schema_version=="lab-generation-manifest/v1"&&manifest.store_id==terminal.operation.store_id&&manifest.creation_instance==terminal.operation.store_instance&&manifest.writer_epoch==terminal.operation.store_epoch&&manifest.operation_id==terminal.operation.operation_id&&manifest.original_fingerprint==terminal.operation.fingerprint&&terminal.pointer_binding==pointer_binding&&terminal.generation_manifest_binding==local("c01-manifest.json")&&terminal.writer_profile_binding==local("manifest.json")&&terminal.cold_result_binding==local("cold-result.json")&&terminal.cold_process_binding==local("cold-process.json")&&terminal.native_original_binding==local("native-replay-original.bin")&&terminal.phase_head==local("phase-06.json"),"PRIOR_TERMINAL_SCOPE")?;
    let phases=[Phase::Intent,Phase::GenerationPublished,Phase::PointerPrepared,Phase::PointerRenamed,Phase::PointerSynced,Phase::ColdVerified,Phase::OutcomePending,Phase::Confirmed];
    let visibility=[Visibility::OldCanonical,Visibility::OldCanonical,Visibility::OldCanonical,Visibility::CommitUncertain,Visibility::NewUnconfirmed,Visibility::NewUnconfirmed,Visibility::NewUnconfirmed,Visibility::Confirmed];
    let mut prior=None;let mut phase_rows=Vec::new();
    for (n,phase) in phases.iter().take(phase_count).enumerate(){let filename=format!("phase-{:02}.json",n+1);let p:PhaseRecord=decode(&raw[&filename])?;
        require(p.schema_version=="lab-generation-phase/v1"&&p.sequence==n as u64+1&&p.phase==*phase&&p.visibility==visibility[n]&&p.predecessor_sha256==prior&&p.runtime_selection_binding==local("runtime-selection.json")&&p.store_selection_binding==runtime.store_binding&&p.operation==terminal.operation&&p.pointer_binding==pointer_binding&&p.generation_manifest_binding==local("c01-manifest.json")&&p.writer_profile_binding==local("manifest.json")&&p.store_selection_binding.sha256==roots::hash(&raw["store.json"])&&p.store_selection_binding.size_bytes==raw["store.json"].len() as u64,"PRIOR_PHASE_CHAIN")?;
        if let Some(first)=phase_rows.first(){let first:&PhaseRecord=first;require(p.store_selection_binding==first.store_selection_binding,"PRIOR_PHASE_SELECTION")?;}
        prior=Some(roots::hash(&raw[&filename]));phase_rows.push(p);
    }
    require(phase_rows[0].subject_binding==Some(runtime.commit_authority_binding.clone())&&runtime.commit_authority_binding.valid()&&[2,3,4].iter().all(|n|phase_rows[*n].subject_binding.is_none())&&phase_rows[5].subject_binding==Some(local("cold-result.json"))&&(phase_count<7||phase_rows[6].subject_binding==Some(local("terminal.json")))&&(phase_count<8||phase_rows[7].subject_binding==Some(local("confirmed.json"))),"PRIOR_PHASE_SUBJECTS")?;
    let publication:MemberReceiptOriginal=decode(&raw["publication-original.json"])?;
    require(publication.schema_version=="lab-member-durable-receipt/v1"&&publication.outcome=="durable"&&publication.transition.verb=="commit_generation"&&publication.transition.operation_id==manifest.operation_id&&publication.transition.fingerprint==manifest.original_fingerprint&&publication.transition.stage_identity==manifest.stage_identity&&phase_rows[1].subject_binding.as_ref().is_some_and(|b|b.valid()&&b.sha256==roots::hash(&raw["publication-original.json"])&&b.size_bytes==raw["publication-original.json"].len() as u64),"PRIOR_PUBLICATION_ORIGINAL")?;
    let native:MemberManifest=decode(&raw["member-manifest.json"])?;
    require(manifest.member_manifest_binding.sha256==roots::hash(&raw["member-manifest.json"])&&manifest.member_manifest_binding.size_bytes==raw["member-manifest.json"].len() as u64&&native.schema_version=="lab-member-generation/v1"&&native.generation_name==manifest.generation_id&&native.stage_identity==manifest.stage_identity&&native.operation_id==manifest.operation_id&&native.fingerprint==manifest.original_fingerprint&&native.root_id==root.root().selection().root_id,"PRIOR_NATIVE_MANIFEST")?;
    let declared:BTreeSet<_>=store.member_inventory.iter().map(|m|m.relative_path.clone()).collect();require(declared==manifest.members.keys().cloned().collect()&&declared==native.members.keys().cloned().collect(),"PRIOR_MEMBER_COVERAGE")?;
    let gen=roots::open_child(root.directory(),&manifest.generation_id,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;require(Identity::observe(&gen)?==manifest.stage_identity,"PRIOR_GENERATION_IDENTITY")?;
    let mut actual=BTreeSet::new();verify_generation_members(&gen,root.root().identity(),"",&manifest.members,&mut actual,0)?;require(actual==declared,"PRIOR_EXTRA_OR_MISSING_MEMBER")?;
    for(p,b)in &manifest.members{let n=&native.members[p];require(b.valid()&&b.root_id==native.root_id&&b.relative_path==format!("{}/{p}",manifest.generation_id)&&b.sha256==n.sha256&&b.size_bytes==n.size_bytes,"PRIOR_MEMBER_BINDING")?;}
    let expectation:ReplayExpectation=decode(&raw["replay-expectation.json"])?;expectation.validate()?;
    require(manifest.expected_replay_result_binding.sha256==roots::hash(&raw["replay-expectation.json"])&&manifest.expected_replay_result_binding.size_bytes==raw["replay-expectation.json"].len() as u64&&expectation.original_cut_binding==manifest.original_cut_binding&&expectation.source_cut==manifest.source_cut&&expectation.reader_inventory_binding==manifest.reader_inventory_binding&&expectation.member_inventory_binding.sha256==roots::hash(&canonical(&store.member_inventory)?)&&expectation.reader_inventory_binding.sha256==roots::hash(&canonical(&store.consumer_inventory)?),"PRIOR_EXPECTATION")?;
    let request:ColdRequest=decode(&raw["cold-request.json"])?;
    require(request.schema_version=="lab-generation-cold-request/v1"&&request.repair_intent_binding.is_none()&&request.store_selection_binding==phase_rows[0].store_selection_binding&&request.pointer_binding==pointer_binding&&request.generation_manifest_binding==local("c01-manifest.json")&&request.writer_profile_binding==local("manifest.json")&&request.member_manifest_binding==manifest.member_manifest_binding&&request.original_cut_binding==manifest.original_cut_binding&&request.expected_replay_result_binding==manifest.expected_replay_result_binding&&request.replay_expectation==expectation&&request.verifier_input_bindings==expectation.adapter_bindings,"PRIOR_COLD_REQUEST")?;
    ColdObservation::checked(&request,raw["cold-result.json"].clone(),raw["native-replay-original.bin"].clone(),raw["cold-process.json"].clone(),publication.transition.domain)?;
    Ok((pointer,manifest.generation_id))
}
fn verify_generation_members(dir:&File,id:&Identity,prefix:&str,selected:&BTreeMap<String,Binding>,actual:&mut BTreeSet<String>,depth:usize)->Result<()> {
    require(depth<=32&&actual.len()<=1024,"PRIOR_MEMBER_BOUND")?;roots::owned_dir(dir,id.uid,id.mount_id)?;
    for name in roots::names(dir,2049)? {let path=if prefix.is_empty(){name.clone()}else{format!("{prefix}/{name}")};let f=roots::open_child(dir,&name,libc::O_RDONLY,0,true)?;
        if f.metadata()?.is_dir(){require(selected.keys().any(|p|p.starts_with(&format!("{path}/"))),"PRIOR_EXTRA_DIRECTORY")?;verify_generation_members(&f,id,&path,selected,actual,depth+1)?;}else{
            roots::owned_file(&f,id.uid,id.mount_id)?;let expected=selected.get(&path).ok_or(Error("PRIOR_EXTRA_MEMBER"))?;require(expected.size_bytes<=1_073_741_824&&f.metadata()?.len()==expected.size_bytes,"PRIOR_MEMBER_SIZE")?;
            use sha2::{Digest,Sha256};let mut h=Sha256::new();let mut f=f;let mut buffer=[0u8;65536];let mut count=0u64;loop{let n=f.read(&mut buffer)?;if n==0{break}count+=n as u64;require(count<=expected.size_bytes,"PRIOR_MEMBER_SIZE")?;h.update(&buffer[..n]);}
            require(count==expected.size_bytes&&format!("{:x}",h.finalize())==expected.sha256,"PRIOR_MEMBER_BYTES")?;actual.insert(path);
        }
    }Ok(())
}

#[path="../../generation/restart.rs"]
pub(crate) mod restart;
pub use restart::{RestartSelection,RestartInspection,ObservedState,RepairKind,RecoveryAuthority,RecoveryCommit,HistoryProof,RepairVerifier};
