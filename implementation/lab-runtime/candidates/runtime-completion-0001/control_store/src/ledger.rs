//! Immutable control records. A pending durable append is NOT an effect grant.
//! The separately retained host confirmer must CAS predecessor→head and fence
//! writer/branch identities. Supplying a checkpoint read from this ledger alone
//! is circular and is never a production continuity source.
use super::{codec, custody::{self, Held, Identity, Root}, fail, Error, Result};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

/// Full C01 locator identity is retained. This control ledger never opens the
/// referenced body; the independently selected authority verifier does that.
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ByteBinding { pub kind:String,pub root_id:String,pub relative_path:String,pub sha256:String,pub size_bytes:u64 }
impl ByteBinding {
    pub fn valid(&self)->bool { matches!(self.kind.as_str(),"execution"|"semantic"|"evidence"|"public-package"|"protected-input")&&(1..=4096).contains(&self.root_id.chars().count())&&(1..=4096).contains(&self.relative_path.chars().count())&&!self.relative_path.contains(['\\','\0'])&&self.relative_path.split('/').all(|p|!p.is_empty()&&p!="."&&p!="..")&&codec::hash(&self.sha256)&&self.size_bytes<=codec::MAX_INTEGER }
}

#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Limits { pub max_record_bytes:u64,pub max_records:u64,pub max_total_bytes:u64,pub reserved_records:u64 }
impl Limits {
    fn validate(&self)->Result<()> {
        if !(2048..=65536).contains(&self.max_record_bytes) || !(8..=100000).contains(&self.max_records) || !(6..=16).contains(&self.reserved_records) || self.reserved_records>=self.max_records || self.max_total_bytes<self.max_record_bytes*8 || self.max_total_bytes>1024*1024*1024 { return fail("finite control limits"); } Ok(())
    }
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WriterFence { pub instance:String,pub epoch:u64 }
impl WriterFence { fn valid(&self)->bool { codec::identifier(&self.instance)&&self.epoch>0&&self.epoch<=codec::MAX_INTEGER } }
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Head { pub sequence:u64,pub sha256:String }
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HostConfirmation {
    pub schema_version:String,pub authority_domain:String,pub root:Identity,pub header_sha256:String,
    pub writer:WriterFence,pub predecessor:Head,pub head:Head,
}
/// Passed only by the fixed host authority loader, never deserialized from a
/// broker request. Production must independently verify custody, freshness,
/// serialization and writer fencing before constructing this selection.
#[derive(Clone,Debug)]
pub struct TrustedSelection { pub confirmation:HostConfirmation,pub posture:Posture }
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Posture { Fixture,Actual }
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
struct Header { schema_version:String,authority_domain:String,layout:Vec<Identity>,limits:Limits,fixture_only:bool }
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Operation {
    pub operation_id:String,pub store_id:String,pub store_instance:String,pub store_epoch:u64,
    pub slot_id:String,pub slot_epoch:u64,pub holder:String,pub fingerprint:String,
    pub original_request_sha256:String,pub issuer:String,pub host_event:String,
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(tag="kind",deny_unknown_fields)]
pub enum Change {
    StoreEpoch { store_id:String,prior_epoch:u64,new_epoch:u64,instance:String,fence_binding:ByteBinding },
    SlotEpoch { slot_id:String,prior_epoch:u64,new_epoch:u64,holder:String,slot_receipt_binding:ByteBinding,prior_disposition_binding:ByteBinding,containment_binding:ByteBinding },
    SlotState { slot_id:String,epoch:u64,holder:String,state:SlotPhase,terminal_binding:ByteBinding },
    Reserve { operation:Operation },
    Outcome { operation_id:String,fingerprint:String,result_binding:ByteBinding,outcome:Outcome },
    Reconcile { action:ReconcileAction,authority_binding:ByteBinding,observed_head:Head },
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(tag="action",deny_unknown_fields)]
pub enum ReconcileAction {
    Outcome { operation_id:String,fingerprint:String,result_binding:ByteBinding,outcome:Outcome },
    Slot { slot_id:String,epoch:u64,holder:String,terminal_binding:ByteBinding },
}
/// Exact evidence/authority selection from the fixed recovery verifier. The
/// Rust API does not authenticate this struct and must never parse it directly
/// from caller input. It cannot select a new root, writer or observed head.
pub struct TrustedReconciliation { pub authority_domain:String,pub root:Identity,pub writer:WriterFence,pub observed_head:Head,pub authority_binding:ByteBinding,pub action:ReconcileAction }
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]
pub enum SlotPhase { Reserved,Active,Closing,Closed,Quarantined }
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]
pub enum Outcome { Committed,Aborted,Quarantined }
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
struct Record { schema_version:String,authority_domain:String,sequence:u64,previous_sha256:String,writer:WriterFence,change:Change }
#[derive(Clone,Debug)]
struct Store { epoch:u64,instance:String }
#[derive(Clone,Debug)]
struct Slot { epoch:u64,holder:String,phase:SlotPhase }
#[derive(Clone,Debug,Default)]
struct State { stores:BTreeMap<String,Store>,slots:BTreeMap<String,Slot>,operations:BTreeMap<String,Operation>,outcomes:BTreeMap<String,(Outcome,ByteBinding)>,events:BTreeSet<(String,String)> }
impl State {
    fn terminal(&self,id:&str)->bool { self.outcomes.get(id).is_some_and(|(o,_)|matches!(o,Outcome::Committed|Outcome::Aborted)) }
    fn apply(&mut self,c:&Change)->Result<()> {
        match c {
            Change::StoreEpoch{store_id,prior_epoch,new_epoch,instance,fence_binding}=>{
                if !codec::identifier(store_id)||!codec::identifier(instance)||!fence_binding.valid()||*new_epoch!=prior_epoch.checked_add(1).ok_or_else(||Error("epoch overflow".into()))? || *new_epoch>codec::MAX_INTEGER || self.stores.get(store_id).map_or(0,|s|s.epoch)!=*prior_epoch { return fail("store epoch/fence"); }
                if self.operations.iter().any(|(id,o)|&o.store_id==store_id&&!self.terminal(id)) { return fail("unresolved prior store operation"); }
                self.stores.insert(store_id.clone(),Store{epoch:*new_epoch,instance:instance.clone()});
            }
            Change::SlotEpoch{slot_id,prior_epoch,new_epoch,holder,slot_receipt_binding,prior_disposition_binding,containment_binding}=>{
                if !codec::identifier(slot_id)||!codec::identifier(holder)||!slot_receipt_binding.valid()||!prior_disposition_binding.valid()||!containment_binding.valid()||*new_epoch!=prior_epoch.checked_add(1).ok_or_else(||Error("epoch overflow".into()))?||*new_epoch>codec::MAX_INTEGER || self.slots.get(slot_id).map_or(0,|s|s.epoch)!=*prior_epoch { return fail("slot epoch/disposition"); }
                if self.slots.get(slot_id).is_some_and(|s|s.phase!=SlotPhase::Closed) || self.operations.iter().any(|(id,o)|&o.slot_id==slot_id&&!self.terminal(id)) { return fail("unreleased prior slot"); }
                if self.slots.values().any(|s|s.phase!=SlotPhase::Closed) { return fail("authority domain live family already held"); }
                self.slots.insert(slot_id.clone(),Slot{epoch:*new_epoch,holder:holder.clone(),phase:SlotPhase::Reserved});
            }
            Change::SlotState{slot_id,epoch,holder,state,terminal_binding}=>{
                if !terminal_binding.valid() { return fail("slot transition binding"); }
                let unresolved=self.operations.iter().any(|(id,o)|&o.slot_id==slot_id&&!self.terminal(id));
                let slot=self.slots.get_mut(slot_id).ok_or_else(||Error("unknown slot".into()))?;
                if slot.epoch!=*epoch || slot.holder!=*holder { return fail("stale slot transition"); }
                let legal=matches!((slot.phase,state),(SlotPhase::Reserved,SlotPhase::Active)|(SlotPhase::Reserved,SlotPhase::Closing)|(SlotPhase::Active,SlotPhase::Closing)|(SlotPhase::Closing,SlotPhase::Closed)|(SlotPhase::Reserved,SlotPhase::Quarantined)|(SlotPhase::Active,SlotPhase::Quarantined)|(SlotPhase::Closing,SlotPhase::Quarantined));
                if !legal || (*state==SlotPhase::Closed&&unresolved) { return fail("illegal slot transition"); }
                slot.phase=*state;
            }
            Change::Reserve{operation:o}=>{
                if [&o.operation_id,&o.store_id,&o.store_instance,&o.slot_id,&o.holder,&o.issuer,&o.host_event].iter().any(|s|!codec::identifier(s))||!codec::hash(&o.fingerprint)||!codec::hash(&o.original_request_sha256) { return fail("operation domain"); }
                if self.events.contains(&(o.issuer.clone(),o.host_event.clone())) { return fail("authority-domain event consumed"); }
                if self.operations.contains_key(&o.operation_id) { return fail("operation identity consumed; inspect only"); }
                let store=self.stores.get(&o.store_id).ok_or_else(||Error("unknown store".into()))?;
                let slot=self.slots.get(&o.slot_id).ok_or_else(||Error("unknown slot".into()))?;
                if store.epoch!=o.store_epoch||store.instance!=o.store_instance||slot.epoch!=o.slot_epoch||slot.holder!=o.holder||slot.phase!=SlotPhase::Active { return fail("stale store/slot/holder"); }
                // Stronger bounded baseline: one unresolved mutation per domain.
                // This also reserves a finite terminal budget independently of
                // how many logical stores share the replay registry.
                if self.operations.keys().any(|id|!self.terminal(id)) { return fail("domain unresolved operation"); }
                self.events.insert((o.issuer.clone(),o.host_event.clone())); self.operations.insert(o.operation_id.clone(),o.clone());
            }
            Change::Outcome{operation_id,fingerprint,result_binding,outcome}=>{
                let op=self.operations.get(operation_id).ok_or_else(||Error("unknown operation".into()))?;
                if op.fingerprint!=*fingerprint||!result_binding.valid()||self.outcomes.contains_key(operation_id) { return fail("outcome identity/duplicate"); }
                self.outcomes.insert(operation_id.clone(),(*outcome,result_binding.clone()));
            }
            Change::Reconcile{action,authority_binding,observed_head}=>{
                if !authority_binding.valid()||!codec::hash(&observed_head.sha256) { return fail("reconciliation evidence binding"); }
                match action {
                    ReconcileAction::Outcome{operation_id,fingerprint,result_binding,outcome}=>{
                        let op=self.operations.get(operation_id).ok_or_else(||Error("unknown recovery operation".into()))?;
                        if op.fingerprint!=*fingerprint||!result_binding.valid()||*outcome==Outcome::Quarantined||self.outcomes.get(operation_id).map(|v|v.0)!=Some(Outcome::Quarantined) { return fail("reconciliation outcome scope"); }
                        self.outcomes.insert(operation_id.clone(),(*outcome,result_binding.clone()));
                    }
                    ReconcileAction::Slot{slot_id,epoch,holder,terminal_binding}=>{
                        if !terminal_binding.valid()||self.operations.iter().any(|(id,o)|&o.slot_id==slot_id&&!self.terminal(id)) { return fail("reconciliation slot unresolved/evidence"); }
                        let slot=self.slots.get_mut(slot_id).ok_or_else(||Error("unknown recovery slot".into()))?;
                        if slot.epoch!=*epoch||slot.holder!=*holder||slot.phase!=SlotPhase::Quarantined { return fail("reconciliation slot scope"); }
                        slot.phase=SlotPhase::Closed;
                    }
                }
            }
        } Ok(())
    }
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub enum Consumption { Consumed,Available,Unknown }
#[derive(Clone,Debug)]
pub struct Inspection {
    /// Continuity permits bounded control appends, not effect authorization.
    /// Quarantined operations can leave this true for selected reconciliation.
    pub writable:bool,pub quarantine_reason:Option<String>,pub verified_head:Head,pub verified_records:u64,pub bytes:u64,pub known_events:usize,pub unknown_tail:bool,
    pub unresolved_operations:usize,pub quarantined_operations:usize,pub quarantined_slots:usize,
}
/// This is a proposal for host CAS, never an acknowledgment or effect permit.
#[derive(Debug)]
pub struct PendingCheckpoint { requested:HostConfirmation }
impl PendingCheckpoint { pub fn requested_confirmation(&self)->&HostConfirmation { &self.requested } }
#[derive(Debug)]
pub struct Acknowledged { confirmation:HostConfirmation }
impl Acknowledged { pub fn confirmation(&self)->&HostConfirmation { &self.confirmation } }
pub struct BorrowedOperation<'a> { operation:&'a Operation,capability:Held<'a> }
impl BorrowedOperation<'_> {
    pub fn operation(&self)->&Operation { self.operation }
    pub fn nested(&self)->Result<Held<'_>> { self.capability.nested() }
}
pub struct Ledger<'a> { root:&'a Root,header:Header,header_sha:String,selected:HostConfirmation,posture:Posture,head:Head,previous:Head,state:State,bytes:u64,quarantine:Option<String>,pending:bool }
impl<'a> Ledger<'a> {
    /// Fixture initialization is not host provisioning. A separately retained
    /// fixture witness may confirm this genesis only for conditional tests.
    pub fn initialize_fixture(root:&Root,held:&Held<'_>,domain:&str,limits:Limits,writer:WriterFence)->Result<HostConfirmation> {
        held.require(root)?; limits.validate()?;
        if !codec::identifier(domain)||!writer.valid() { return fail("domain/writer"); }
        if !root.names(1)?.is_empty() { return fail("bootstrap requires empty owned ledger"); }
        let header=Header{schema_version:"lab-control-header/v1".into(),authority_domain:domain.into(),layout:root.layout()?,limits,fixture_only:true};
        let raw=codec::encode(&header)?;
        custody::create(&root.directory,"header.json",&raw)?;
        let hash=codec::digest(&raw); let head=Head{sequence:0,sha256:hash.clone()};
        Ok(HostConfirmation{schema_version:"lab-host-control-confirmation/v1".into(),authority_domain:domain.into(),root:root.identity(),header_sha256:hash,writer,predecessor:head.clone(),head})
    }
    pub fn open(root:&'a Root,held:&Held<'_>,selection:TrustedSelection)->Result<Self> {
        held.require(root)?;
        let selected=selection.confirmation;
        if selected.schema_version!="lab-host-control-confirmation/v1"||selected.root!=root.identity()||!codec::identifier(&selected.authority_domain)||!selected.writer.valid()||!codec::hash(&selected.header_sha256)||!codec::hash(&selected.head.sha256)||!codec::hash(&selected.predecessor.sha256) { return fail("invalid independently selected continuity witness"); }
        let raw=custody::read(&mut custody::open_at(&root.directory,"header.json",libc::O_RDONLY)?,65536)?;
        let header:Header=codec::decode(&raw)?; header.limits.validate()?; let header_sha=codec::digest(&raw);
        if header.schema_version!="lab-control-header/v1"||header.authority_domain!=selected.authority_domain||header_sha!=selected.header_sha256||header.layout!=root.layout()? { return fail("selected header/root/layout binding"); }
        if header.fixture_only!=(selection.posture==Posture::Fixture) { return fail("fixture/actual posture mismatch"); }
        let head=Head{sequence:0,sha256:header_sha.clone()};
        let mut ledger=Self{root,header,header_sha,selected,posture:selection.posture,head:head.clone(),previous:head,state:State::default(),bytes:raw.len() as u64,quarantine:None,pending:false};
        if let Err(e)=ledger.load() { ledger.quarantine=Some(e.0); }
        if ledger.quarantine.is_none() && (ledger.head!=ledger.selected.head || ledger.previous!=ledger.selected.predecessor) { ledger.quarantine=Some("independent witness/head/predecessor mismatch".into()); }
        Ok(ledger)
    }
    fn load(&mut self)->Result<()> {
        let names=self.root.names(self.header.limits.max_records as usize+1)?;
        if names.len()>self.header.limits.max_records as usize { return fail("record count exhausted/corrupt"); }
        let mut prior_writer:Option<WriterFence>=None;
        for (index,name) in names.iter().enumerate() {
            let sequence=index as u64+1;
            if *name!=format!("{:016}.json",sequence) { return fail("missing/unexpected control record"); }
            let raw=custody::read(&mut custody::open_at(&self.root.records,name,libc::O_RDONLY)?,self.header.limits.max_record_bytes as usize)?;
            if self.bytes+raw.len() as u64>self.header.limits.max_total_bytes { return fail("control byte limit"); }
            let r:Record=codec::decode(&raw)?;
            if r.schema_version!="lab-control-record/v1"||r.authority_domain!=self.header.authority_domain||r.sequence!=sequence||r.previous_sha256!=self.head.sha256||!r.writer.valid()||r.writer.epoch>self.selected.writer.epoch { return fail("record chain/domain/writer"); }
            if (r.writer.epoch==self.selected.writer.epoch&&r.writer.instance!=self.selected.writer.instance)||prior_writer.as_ref().is_some_and(|w|r.writer.epoch<w.epoch||(r.writer.epoch==w.epoch&&r.writer.instance!=w.instance)) { return fail("writer epoch/instance continuity"); }
            prior_writer=Some(r.writer.clone());
            if let Change::Reconcile{observed_head,..}=&r.change { if observed_head!=&self.head { return fail("reconciliation stale preimage"); } }
            let mut next=self.state.clone(); next.apply(&r.change)?; self.state=next;
            self.bytes+=raw.len() as u64; self.previous=self.head.clone(); self.head=Head{sequence,sha256:codec::digest(&raw)};
        } Ok(())
    }
    pub fn inspect(&self)->Inspection { Inspection{writable:self.quarantine.is_none()&&!self.pending,quarantine_reason:self.quarantine.clone().or_else(||self.pending.then(||"pending independent confirmation".into())),verified_head:self.head.clone(),verified_records:self.head.sequence,bytes:self.bytes,known_events:self.state.events.len(),unknown_tail:self.quarantine.is_some(),unresolved_operations:self.state.operations.keys().filter(|id|!self.state.terminal(id)).count(),quarantined_operations:self.state.outcomes.values().filter(|v|v.0==Outcome::Quarantined).count(),quarantined_slots:self.state.slots.values().filter(|s|s.phase==SlotPhase::Quarantined).count()} }
    pub fn consumption(&self,issuer:&str,event:&str)->Consumption {
        if self.state.events.contains(&(issuer.into(),event.into())) { Consumption::Consumed }
        else if self.quarantine.is_some()||self.pending { Consumption::Unknown } else { Consumption::Available }
    }
    pub fn operation(&self,id:&str)->Option<&Operation> { self.state.operations.get(id) }
    pub fn outcome(&self,id:&str)->Option<&(Outcome,ByteBinding)> { self.state.outcomes.get(id) }
    /// Nested effects share this acknowledged operation and held slot. They do
    /// not reserve a second family/event or acquire another lock description.
    /// Outer fixed authority checks remain mandatory for each actual effect.
    pub fn borrow_operation<'b>(&'b self,held:&'b Held<'_>,id:&str,fingerprint:&str)->Result<BorrowedOperation<'b>> {
        held.require(self.root)?;
        if self.quarantine.is_some()||self.pending { return fail("unconfirmed operation cannot dispatch"); }
        let current=Self::open(self.root,held,TrustedSelection{confirmation:self.selected.clone(),posture:self.posture})?;
        if !current.inspect().writable||current.head!=self.head { return fail("nested control state changed"); }
        let operation=self.state.operations.get(id).ok_or_else(||Error("unknown nested operation".into()))?;
        if operation.fingerprint!=fingerprint||self.state.outcomes.contains_key(id)||self.state.slots.get(&operation.slot_id).is_none_or(|s|s.epoch!=operation.slot_epoch||s.holder!=operation.holder||s.phase!=SlotPhase::Active)||self.state.stores.get(&operation.store_id).is_none_or(|s|s.epoch!=operation.store_epoch||s.instance!=operation.store_instance) { return fail("nested operation no longer effect eligible"); }
        Ok(BorrowedOperation{operation,capability:held.nested()?})
    }
    pub fn append(&mut self,held:&Held<'_>,change:Change)->Result<PendingCheckpoint> {
        if matches!(change,Change::Reconcile{..}) { return fail("separately selected reconciliation required"); }
        self.append_selected(held,change)
    }
    pub fn reconcile(&mut self,held:&Held<'_>,selection:TrustedReconciliation)->Result<PendingCheckpoint> {
        if selection.authority_domain!=self.header.authority_domain||selection.root!=self.root.identity()||selection.writer!=self.selected.writer||selection.observed_head!=self.head { return fail("reconciliation selected scope/preimage"); }
        self.append_selected(held,Change::Reconcile{action:selection.action,authority_binding:selection.authority_binding,observed_head:selection.observed_head})
    }
    fn append_selected(&mut self,held:&Held<'_>,change:Change)->Result<PendingCheckpoint> {
        held.require(self.root)?;
        if self.quarantine.is_some()||self.pending { return fail("control continuity quarantined/pending"); }
        // Re-read the exact inventory under the same held domain locks. An old
        // in-memory instance cannot append after another owner advanced disk.
        let current=Self::open(self.root,held,TrustedSelection{confirmation:self.selected.clone(),posture:self.posture})?;
        if !current.inspect().writable || current.head!=self.head { self.quarantine=Some("control changed under selected state".into()); return fail("control changed"); }
        let terminal=matches!(&change,Change::Outcome{..}|Change::Reconcile{..}|Change::SlotState{state:SlotPhase::Closing|SlotPhase::Closed|SlotPhase::Quarantined,..});
        let reserved=if terminal {0}else{self.header.limits.reserved_records};
        if self.head.sequence+1+reserved>self.header.limits.max_records || self.bytes+(reserved+1)*self.header.limits.max_record_bytes>self.header.limits.max_total_bytes { return fail("control capacity reserved/exhausted"); }
        let mut next=self.state.clone(); next.apply(&change)?;
        let record=Record{schema_version:"lab-control-record/v1".into(),authority_domain:self.header.authority_domain.clone(),sequence:self.head.sequence+1,previous_sha256:self.head.sha256.clone(),writer:self.selected.writer.clone(),change};
        let raw=codec::encode(&record)?;
        if raw.len() as u64>self.header.limits.max_record_bytes { return fail("record byte bound"); }
        if let Err(e)=custody::create(&self.root.records,&format!("{:016}.json",record.sequence),&raw) { self.quarantine=Some("append/fsync outcome uncertain; inspect only".into()); return Err(e); }
        self.previous=self.head.clone(); self.head=Head{sequence:record.sequence,sha256:codec::digest(&raw)}; self.bytes+=raw.len() as u64; self.state=next; self.pending=true;
        Ok(PendingCheckpoint{requested:HostConfirmation{schema_version:"lab-host-control-confirmation/v1".into(),authority_domain:self.header.authority_domain.clone(),root:self.root.identity(),header_sha256:self.header_sha.clone(),writer:self.selected.writer.clone(),predecessor:self.previous.clone(),head:self.head.clone()}})
    }
    pub fn acknowledge(&mut self,held:&Held<'_>,pending:PendingCheckpoint,confirmed:HostConfirmation)->Result<Acknowledged> {
        held.require(self.root)?;
        if !self.pending||self.quarantine.is_some()||confirmed!=pending.requested||confirmed.predecessor!=self.selected.head||confirmed.head!=self.head { return fail("independent host confirmation mismatch"); }
        // No acknowledgment if the named attachment/bytes changed after fsync
        // or during external confirmation.
        let checked=Self::open(self.root,held,TrustedSelection{confirmation:confirmed.clone(),posture:self.posture})?;
        if !checked.inspect().writable { self.quarantine=Some("post-confirmation control drift".into()); return fail("post-confirmation control drift"); }
        self.selected=confirmed.clone(); self.pending=false; Ok(Acknowledged{confirmation:confirmed})
    }
}

#[cfg(test)]
mod durability_tests {
 use super::*;
 use super::super::custody::{Rank,FAIL_BOUNDARY};
 use std::{fs,path::PathBuf,time::Duration};
 #[test]
 fn each_create_write_file_sync_directory_sync_boundary_preserves_uncertainty(){
  for phase in 1..=4 {
   let base=PathBuf::from(std::env::var_os("TMPDIR").unwrap()).join(format!("control-sync-boundary-{}-{}",std::process::id(),phase));fs::create_dir(&base).unwrap();let root=Root::create_fixture(&base,"domain").unwrap();
   let locks=root.acquire(Rank::Journal,Duration::from_secs(1)).unwrap();let held=locks.borrow().unwrap();let limit=Limits{max_record_bytes:4096,max_records:64,max_total_bytes:1024*1024,reserved_records:6};let writer=WriterFence{instance:"fixture".into(),epoch:1};let initial=Ledger::initialize_fixture(&root,&held,"fixture",limit,writer).unwrap();let mut selected=initial.clone();let mut l=Ledger::open(&root,&held,TrustedSelection{confirmation:initial,posture:Posture::Fixture}).unwrap();let hash="a".repeat(64);
   let binding=ByteBinding{kind:"evidence".into(),root_id:"fixture".into(),relative_path:"proof.json".into(),sha256:hash.clone(),size_bytes:10};
   // These selections are fixture inputs for syscall tests only. They do not
   // model independent host CAS (covered by external integration fixtures).
   for change in [Change::StoreEpoch{store_id:"s".into(),prior_epoch:0,new_epoch:1,instance:"i".into(),fence_binding:binding.clone()},Change::SlotEpoch{slot_id:"slot".into(),prior_epoch:0,new_epoch:1,holder:"f".into(),slot_receipt_binding:binding.clone(),prior_disposition_binding:binding.clone(),containment_binding:binding.clone()},Change::SlotState{slot_id:"slot".into(),epoch:1,holder:"f".into(),state:SlotPhase::Active,terminal_binding:binding.clone()}] {
    let p=l.append(&held,change).unwrap();selected=p.requested_confirmation().clone();l.acknowledge(&held,p,selected.clone()).unwrap();
   }
   let operation=Operation{operation_id:"op".into(),store_id:"s".into(),store_instance:"i".into(),store_epoch:1,slot_id:"slot".into(),slot_epoch:1,holder:"f".into(),fingerprint:hash.clone(),original_request_sha256:hash,issuer:"issuer".into(),host_event:"event".into()};
   FAIL_BOUNDARY.with(|v|v.set(phase));let failed=l.append(&held,Change::Reserve{operation});FAIL_BOUNDARY.with(|v|v.set(0));assert!(failed.is_err());assert!(!l.inspect().writable);assert!(l.borrow_operation(&held,"op",&"a".repeat(64)).is_err());drop(l);
   let file=base.join("domain/records/0000000000000004.json");let before=fs::read(&file).unwrap();let reopened=Ledger::open(&root,&held,TrustedSelection{confirmation:selected,posture:Posture::Fixture}).unwrap();assert!(!reopened.inspect().writable);assert_eq!(reopened.consumption("issuer","event"),if phase==1{Consumption::Unknown}else{Consumption::Consumed});assert_eq!(fs::read(&file).unwrap(),before);drop(reopened);drop(held);drop(locks);drop(root);fs::remove_dir_all(base).unwrap();
  }
 }
}
