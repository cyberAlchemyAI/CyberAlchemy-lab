//! Fixed original-byte persistence and independently confirmed attempt history.
//! No record or restarted journal can mint a fresh producer launch capability.
use super::{need,Error,Result,evidence::{self,EvidenceRoot},records::*,state::Domain,containment::identity};
use lab_control_store::{codec,custody::{Root as ControlRoot,Held,Rank},ledger::{Ledger,TrustedSelection,Posture,HostConfirmation,Operation,Head,ByteBinding,WriterFence}};
use serde::{Serialize,de::DeserializeOwned};
use std::{collections::{BTreeMap,BTreeSet},fs::File};

fn decoded<T:DeserializeOwned+Serialize>(raw:&[u8])->Result<T>{let value:T=codec::decode(raw)?;need(codec::encode(&value)?==raw,"ATTEMPT_ORIGINAL_CANONICAL")?;Ok(value)}
fn writer_precedes(a:&WriterFence,b:&WriterFence)->bool{
 codec::identifier(&a.instance)&&codec::identifier(&b.instance)&&a.epoch>0&&b.epoch>0&&a.epoch<=codec::MAX_INTEGER&&b.epoch<=codec::MAX_INTEGER&&
 a.epoch<=b.epoch&&(a.epoch!=b.epoch||a.instance==b.instance)
}
pub(crate) struct ControlView<'a>{root:&'a ControlRoot,directory:File,held:&'a Held<'a>,pub(crate) current:HostConfirmation,domain:Domain}
impl<'a> ControlView<'a>{
 pub(crate) fn new(root:&'a ControlRoot,directory:File,held:&'a Held<'a>,current:HostConfirmation,domain:Domain)->Result<Self>{let value=Self{root,directory,held,current,domain};value.ledger()?;Ok(value)}
 pub(crate) fn ledger(&self)->Result<Ledger<'a>>{
  self.root.validate()?;self.held.nested()?;need(self.held.rank()==Rank::Journal,"ATTEMPT_GLOBAL_LOCK_ORDER")?;
  let id=identity(&self.directory)?;let selected=self.root.identity();need(id.device==selected.device&&id.inode==selected.inode&&id.uid==selected.uid&&self.current.root==selected,"ATTEMPT_CONTROL_ROOT")?;
  let ledger=Ledger::open(self.root,self.held,TrustedSelection{confirmation:self.current.clone(),posture:if self.domain==Domain::Fixture{Posture::Fixture}else{Posture::Actual}})?;
  need(ledger.inspect().writable,"ATTEMPT_CONTROL_QUARANTINE")?;Ok(ledger)
 }
 pub(crate) fn operation(&self,op:&Operation,active:bool)->Result<()>{let ledger=self.ledger()?;need(ledger.operation(&op.operation_id)==Some(op),"ATTEMPT_ORIGINAL_OPERATION")?;if active{ledger.borrow_operation(self.held,&op.operation_id,&op.fingerprint)?;}Ok(())}
 pub(crate) fn historical(&self,c:&HostConfirmation)->Result<()>{
  // `c` is an original inside the attempt hash chain authenticated by the
  // independently selected HostAttemptCheckpoint. This comparison does not
  // authenticate an arbitrary caller-supplied historical writer fence.
  self.ledger()?;need(c.schema_version=="lab-host-control-confirmation/v1"&&c.authority_domain==self.current.authority_domain&&c.root==self.current.root&&c.header_sha256==self.current.header_sha256&&c.head.sequence<=self.current.head.sequence&&c.head.sequence>0&&c.predecessor.sequence.checked_add(1)==Some(c.head.sequence),"ATTEMPT_HISTORICAL_CONTROL_DOMAIN")?;
  need(writer_precedes(&c.writer,&self.current.writer),"ATTEMPT_HISTORICAL_CURRENT_WRITER")?;
  let root=identity(&self.directory)?;let records=evidence::directory(&self.directory,"records",&root)?;
  let raw=evidence::read(&records,&format!("{:016}.json",c.head.sequence),65536,&root)?;
  let row:serde_json::Value=codec::decode(&raw)?;
  need(codec::digest(&raw)==c.head.sha256&&row.get("previous_sha256").and_then(|v|v.as_str())==Some(c.predecessor.sha256.as_str()),"ATTEMPT_HISTORICAL_CONTROL_HEAD")?;
  let physical:WriterFence=serde_json::from_value(row.get("writer").cloned().ok_or(Error("CONTROL_WRITER_ENCODING"))?).map_err(|_|Error("CONTROL_WRITER_ENCODING"))?;
  // A new independently selected writer may hold the same older durable head.
  need(writer_precedes(&physical,&c.writer),"ATTEMPT_HISTORICAL_RECORD_WRITER")?;
  if c.head.sequence<self.current.head.sequence{
   let next_raw=evidence::read(&records,&format!("{:016}.json",c.head.sequence+1),65536,&root)?;
   let next:serde_json::Value=codec::decode(&next_raw)?;
   let writer:WriterFence=serde_json::from_value(next.get("writer").cloned().ok_or(Error("CONTROL_WRITER_ENCODING"))?).map_err(|_|Error("CONTROL_WRITER_ENCODING"))?;
   need(next.get("previous_sha256").and_then(|v|v.as_str())==Some(c.head.sha256.as_str())&&writer_precedes(&c.writer,&writer),"ATTEMPT_HISTORICAL_SUCCESSOR_WRITER")?;
  }
  Ok(())
 }
}

/// Private selection from the independently enrolled host confirmer. Actual host
/// authentication, nonrollbackable CAS and competing-writer fencing remain G01.
/// The journal implementation below verifies exact selected bytes and all joins.
pub(crate) struct SelectedCheckpoint{checkpoint:HostAttemptCheckpoint,original:Vec<u8>,binding:ByteBinding}
impl SelectedCheckpoint{
 #[cfg(test)]pub(crate) fn fixture(original:Vec<u8>,binding:ByteBinding)->Result<Self>{let result=Self::checked(original,binding)?;need(result.checkpoint.domain==Domain::Fixture,"ATTEMPT_FIXTURE_ONLY")?;Ok(result)}
 /// Fixed enrolled host transport only. Authentication must precede this call,
 /// and the independent expected binding must not be learned from this journal.
 /// This does not acknowledge a start or supply a launch capability.
 pub(crate) unsafe fn from_enrolled_host(original:Vec<u8>,binding:ByteBinding)->Result<Self>{let result=Self::checked(original,binding)?;need(result.checkpoint.domain==Domain::Actual,"ATTEMPT_ACTUAL_HOST_REQUIRED")?;Ok(result)}
 fn checked(original:Vec<u8>,binding:ByteBinding)->Result<Self>{need(original.len()<=65536&&binding.valid()&&binding.kind=="evidence"&&binding.size_bytes==original.len() as u64&&binding.sha256==codec::digest(&original),"ATTEMPT_HOST_ORIGINAL_BYTES")?;let checkpoint=decoded(&original)?;Ok(Self{checkpoint,original,binding})}
 pub(crate) fn checkpoint(&self)->&HostAttemptCheckpoint{&self.checkpoint}
 pub(crate) fn binding(&self)->&ByteBinding{&self.binding}
}
pub(crate) struct PendingAppend{requested:HostAttemptCheckpoint,original_binding:ByteBinding,record_binding:ByteBinding,event:AttemptEvent,attempt_id:String,operation:Operation}
impl PendingAppend {pub(crate) fn requested(&self)->&HostAttemptCheckpoint{&self.requested}}
pub(crate) struct DurableOriginal{root:EvidenceRoot,control_directory:File,header_sha:String,checkpoint:HostAttemptCheckpoint,checkpoint_binding:ByteBinding,original_binding:ByteBinding,record_binding:ByteBinding,original:Vec<u8>,event:AttemptEvent,operation:Operation,attempt_id:String}
impl DurableOriginal{
 pub(crate) fn bytes(&self)->&[u8]{&self.original}
 pub(crate) fn binding(&self)->&ByteBinding{&self.original_binding}
 pub(crate) fn checkpoint_binding(&self)->&ByteBinding{&self.checkpoint_binding}
 pub(crate) fn operation(&self)->&Operation{&self.operation}
 pub(crate) fn attempt_id(&self)->&str{&self.attempt_id}
 pub(crate) fn event(&self)->AttemptEvent{self.event}
 pub(crate) fn validate(&self)->Result<()>{
  self.root.validate()?;let header=evidence::read(self.root.fd(),"header.json",65536,self.root.id())?;need(codec::digest(&header)==self.header_sha,"DURABLE_HEADER_CHANGED")?;
  let h:JournalHeader=decoded(&header)?;self.checkpoint.valid_for(&h,&self.header_sha)?;
  need(evidence::names(self.root.fd(),4)?==["header.json","originals","records"],"DURABLE_ROOT_INVENTORY")?;
  let control_id=identity(&self.control_directory)?;let c=&self.checkpoint.control_preimage;need(control_id.device==c.root.device&&control_id.inode==c.root.inode&&control_id.uid==c.root.uid,"DURABLE_CONTROL_ROOT")?;
  let control_records=evidence::directory(&self.control_directory,"records",&control_id)?;let control_raw=evidence::read(&control_records,&format!("{:016}.json",c.head.sequence),65536,&control_id)?;need(codec::digest(&control_raw)==c.head.sha256,"DURABLE_CONTROL_PREIMAGE_CHANGED")?;
  let objects=evidence::directory(self.root.fd(),"originals",self.root.id())?;let records=evidence::directory(self.root.fd(),"records",self.root.id())?;let name=format!("{:016}.json",self.checkpoint.head.sequence);
  let expected:Vec<_>=(1..=self.checkpoint.head.sequence).map(|n|format!("{n:016}.json")).collect();need(evidence::names(&objects,h.limits.max_records as usize+1)?==expected&&evidence::names(&records,h.limits.max_records as usize+1)?==expected,"DURABLE_HISTORY_INVENTORY")?;
  let mut previous=self.header_sha.clone();for (index,name) in expected.iter().enumerate(){let rr=evidence::read(&records,name,h.limits.max_record_bytes,self.root.id())?;let row:AttemptRecord=decoded(&rr)?;let original=evidence::read(&objects,name,h.limits.max_original_bytes,self.root.id())?;
   need(row.sequence==index as u64+1&&row.previous_sha256==previous&&row.original_binding==self.root.binding(&format!("originals/{name}"),&original),"DURABLE_HISTORY_CHAIN")?;AttemptJournal::validate_original(&h,&row,&original)?;previous=codec::digest(&rr);
  }need(previous==self.checkpoint.head.sha256,"DURABLE_HISTORY_HEAD")?;
  let raw=evidence::read(&objects,&name,h.limits.max_original_bytes,self.root.id())?;let rec=evidence::read(&records,&name,h.limits.max_record_bytes,self.root.id())?;
  need(raw==self.original&&self.root.binding(&format!("originals/{name}"),&raw)==self.original_binding&&self.root.binding(&format!("records/{name}"),&rec)==self.record_binding&&codec::digest(&rec)==self.checkpoint.head.sha256,"DURABLE_ORIGINAL_CHANGED")
 }
}
pub(crate) struct JournalInspection{pub writable:bool,pub reason:Option<&'static str>,pub verified_records:u64,pub original_starts:Vec<ByteBinding>}
pub(crate) struct AttemptJournal<'a>{root:EvidenceRoot,control:ControlView<'a>,header:JournalHeader,header_sha:String,selected:SelectedCheckpoint,records:Vec<AttemptRecord>,originals:Vec<Vec<u8>>,total:u64,quarantine:Option<&'static str>,pending:bool}
impl<'a> AttemptJournal<'a>{
 /// Explicit initialization of an already selected empty root. No open failure
 /// falls back here. Actual provisioning/enrollment remains the host gate.
 pub(crate) fn initialize(root:&EvidenceRoot,control:&ControlView<'_>,header:&JournalHeader)->Result<HostAttemptCheckpoint>{
  root.validate()?;control.ledger()?;header.validate()?;
  need(header.root==*root.id()&&header.root_id==root.root_id()&&header.domain==root.domain()&&header.domain==control.domain&&header.custody_binding==*root.custody()&&header.control_root==control.current.root&&header.authority_domain==control.current.authority_domain&&header.control_header_sha256==control.current.header_sha256&&root.reserve()>=header.limits.max_total_bytes,"ATTEMPT_INITIAL_HEADER_SELECTION")?;
  need(evidence::names(root.fd(),4)?.is_empty(),"ATTEMPT_INITIAL_ROOT_NOT_EMPTY")?;
  let raw=codec::encode(header)?;need(raw.len()<=65536,"ATTEMPT_HEADER_BOUND")?;evidence::create(root.fd(),"header.json",&raw,root.id(),20)?;
  evidence::mkdir(root.fd(),"originals",root.id())?;evidence::mkdir(root.fd(),"records",root.id())?;
  let head=Head{sequence:0,sha256:codec::digest(&raw)};
  Ok(HostAttemptCheckpoint{schema_version:"lab-host-supervisor-checkpoint/v1".into(),domain:header.domain,journal_root:header.root.clone(),root_id:header.root_id.clone(),journal_header_sha256:head.sha256.clone(),predecessor:head.clone(),head,control_preimage:control.current.clone(),operation:None,attempt_id:None})
 }
 pub(crate) fn open(root:EvidenceRoot,control:ControlView<'a>,selected:SelectedCheckpoint)->Result<Self>{
  root.validate()?;control.ledger()?;let raw=evidence::read(root.fd(),"header.json",65536,root.id())?;let header:JournalHeader=decoded(&raw)?;header.validate()?;let header_sha=codec::digest(&raw);
  need(header.root==*root.id()&&header.root_id==root.root_id()&&header.domain==root.domain()&&header.domain==control.domain&&header.custody_binding==*root.custody()&&header.control_root==control.current.root&&header.authority_domain==control.current.authority_domain&&header.control_header_sha256==control.current.header_sha256&&root.reserve()>=header.limits.max_total_bytes,"ATTEMPT_HEADER_CURRENT_ROOT")?;
  selected.checkpoint.valid_for(&header,&header_sha)?;
  need(selected.binding.root_id!=header.root_id,"ATTEMPT_WITNESS_NOT_INDEPENDENT")?;
  let mut journal=Self{root,control,header,header_sha,selected,records:Vec::new(),originals:Vec::new(),total:raw.len() as u64,quarantine:None,pending:false};
  if let Err(error)=journal.scan(){journal.quarantine=Some(error.0);}Ok(journal)
 }
 fn scan(&mut self)->Result<()>{
  need(evidence::names(self.root.fd(),4)?==["header.json","originals","records"],"ATTEMPT_ROOT_INVENTORY")?;
  let records=evidence::directory(self.root.fd(),"records",self.root.id())?;let originals=evidence::directory(self.root.fd(),"originals",self.root.id())?;
  let names=evidence::names(&records,self.header.limits.max_records as usize+1)?;let original_names=evidence::names(&originals,self.header.limits.max_records as usize+1)?;
  need(names==original_names&&names.len() as u64<=self.header.limits.max_records,"ATTEMPT_ORPHAN_OR_TAIL")?;
  let mut previous=self.header_sha.clone();let mut starts=BTreeMap::new();let mut terminal=BTreeSet::new();let mut recovery=BTreeSet::new();
  for(index,name)in names.iter().enumerate(){need(*name==format!("{:016}.json",index+1),"ATTEMPT_SEQUENCE_GAP")?;
   let record_raw=evidence::read(&records,name,self.header.limits.max_record_bytes,self.root.id())?;let raw=evidence::read(&originals,name,self.header.limits.max_original_bytes,self.root.id())?;
   let record:AttemptRecord=decoded(&record_raw)?;
   need(record.schema_version=="lab-supervisor-attempt-record/v1"&&record.sequence==index as u64+1&&record.previous_sha256==previous&&record.original_binding==self.root.binding(&format!("originals/{name}"),&raw),"ATTEMPT_RECORD_CHAIN")?;
   self.control.operation(&record.operation,false)?;self.control.historical(&record.control_preimage)?;
   Self::validate_original(&self.header,&record,&raw)?;self.validate_lineage(&record,&raw)?;
   match record.event {
    AttemptEvent::Start=>{need(record.original_start_binding==record.original_binding&&!starts.contains_key(&record.operation.operation_id)&&!starts.values().any(|(_,id)|id==&record.attempt_id),"ATTEMPT_DUPLICATE_START")?;starts.insert(record.operation.operation_id.clone(),(record.original_binding.clone(),record.attempt_id.clone()));},
    event=>{need(starts.get(&record.operation.operation_id)==Some(&(record.original_start_binding.clone(),record.attempt_id.clone())),"ATTEMPT_START_LINEAGE")?;let set=if event==AttemptEvent::Terminal{&mut terminal}else{&mut recovery};need(set.insert(record.operation.operation_id.clone()),"ATTEMPT_DUPLICATE_OBSERVATION")?;}
   }
   self.total=self.total.checked_add((record_raw.len()+raw.len()) as u64).ok_or(Error("ATTEMPT_CAPACITY_OVERFLOW"))?;need(self.total<=self.header.limits.max_total_bytes,"ATTEMPT_BYTE_CAPACITY")?;
   previous=codec::digest(&record_raw);self.records.push(record);self.originals.push(raw);
  }
  let head=Head{sequence:self.records.len() as u64,sha256:previous};need(head==self.selected.checkpoint.head,"ATTEMPT_WITNESS_AHEAD_OR_BEHIND")?;
  if let Some(last)=self.records.last(){need(self.selected.checkpoint.predecessor.sha256==last.previous_sha256&&self.selected.checkpoint.operation.as_ref()==Some(&last.operation)&&self.selected.checkpoint.attempt_id.as_ref()==Some(&last.attempt_id)&&self.selected.checkpoint.control_preimage==last.control_preimage,"ATTEMPT_WITNESS_TRANSITION")?;}
  need(starts.len() as u64<=self.header.limits.max_attempts,"ATTEMPT_COUNT_CAPACITY")?;Ok(())
 }
 fn validate_original(header:&JournalHeader,r:&AttemptRecord,raw:&[u8])->Result<()>{
  match r.event{
   AttemptEvent::Start=>{let s:StartOriginal=decoded(raw)?;s.validate()?;need(s.operation==r.operation&&s.attempt_id==r.attempt_id&&s.containment_binding==header.supervisor_root_binding&&s.group_identity.mount_id==header.supervisor_root_identity.mount_id&&s.group_identity.uid==header.supervisor_root_identity.uid,"ATTEMPT_START_SCOPE")?;},
   AttemptEvent::Terminal=>{let s:TerminalOriginal=decoded(raw)?;need(s.schema_version=="lab-contained-attempt-terminal/v1"&&s.domain==header.domain&&s.operation==r.operation&&s.attempt_id==r.attempt_id&&s.original_start_binding==r.original_start_binding&&s.containment_binding==header.supervisor_root_binding,"ATTEMPT_TERMINAL_SCOPE")?;},
   AttemptEvent::Recovery=>{let s:RecoveryOriginal=decoded(raw)?;need(s.schema_version=="lab-contained-recovery-observation/v1"&&s.domain==header.domain&&s.operation==r.operation&&s.attempt_id==r.attempt_id&&s.original_start_binding==r.original_start_binding&&s.control_preimage==r.control_preimage&&s.original_checkpoint_binding.valid()&&s.cleanup_authority_binding.valid()&&s.direct_child_reaped.is_none()&&!s.pid_identity_known&&s.outcome=="quarantined","ATTEMPT_RECOVERY_SCOPE")?;}
  }Ok(())
 }

 fn validate_lineage(&self,r:&AttemptRecord,raw:&[u8])->Result<()>{
  if r.event==AttemptEvent::Start{return Ok(())}
  let i=self.records.iter().position(|s|s.event==AttemptEvent::Start&&s.original_binding==r.original_start_binding&&s.operation==r.operation&&s.attempt_id==r.attempt_id).ok_or(Error("ORIGINAL_START_LINEAGE_MISSING"))?;
  let original:StartOriginal=decoded(&self.originals[i])?;
  match r.event{AttemptEvent::Terminal=>{let t:TerminalOriginal=decoded(raw)?;need(t.actual_group_identity==original.group_identity&&t.execution_binding==original.execution_binding&&t.historical_selection==original.historical_selection&&t.start_utc_ns>=original.created_utc_ns,"TERMINAL_ORIGINAL_START_SCOPE")?;},AttemptEvent::Recovery=>{let t:RecoveryOriginal=decoded(raw)?;need(t.group_identity==original.group_identity,"RECOVERY_ORIGINAL_START_SCOPE")?;},_=>{}}
  Ok(())
 }
 pub(crate) fn inspect(&self)->JournalInspection{JournalInspection{writable:self.quarantine.is_none()&&!self.pending,reason:self.quarantine.or(self.pending.then_some("ATTEMPT_PENDING_HOST_CONFIRMATION")),verified_records:self.records.len() as u64,original_starts:self.records.iter().filter(|r|r.event==AttemptEvent::Start).map(|r|r.original_binding.clone()).collect()}}
 pub(crate) fn current(&self)->Result<()>{need(self.quarantine.is_none()&&!self.pending,"ATTEMPT_JOURNAL_QUARANTINED")?;self.root.validate()?;self.control.ledger()?;need(evidence::names(self.root.fd(),4)?==["header.json","originals","records"],"ATTEMPT_ROOT_INVENTORY_CHANGED")?;let raw=evidence::read(self.root.fd(),"header.json",65536,self.root.id())?;need(codec::digest(&raw)==self.header_sha,"ATTEMPT_HEADER_CHANGED")?;
  let original_dir=evidence::directory(self.root.fd(),"originals",self.root.id())?;let record_dir=evidence::directory(self.root.fd(),"records",self.root.id())?;
  let expected:Vec<_>=(1..=self.records.len()).map(|n|format!("{n:016}.json")).collect();need(evidence::names(&original_dir,self.header.limits.max_records as usize+1)?==expected&&evidence::names(&record_dir,self.header.limits.max_records as usize+1)?==expected,"ATTEMPT_HISTORY_INVENTORY_CHANGED")?;
  for(i,row)in self.records.iter().enumerate(){let n=&expected[i];let raw=evidence::read(&original_dir,n,self.header.limits.max_original_bytes,self.root.id())?;need(raw==self.originals[i]&&evidence::read(&record_dir,n,self.header.limits.max_record_bytes,self.root.id())?==codec::encode(row)?,"ATTEMPT_HISTORY_CHANGED")?;}Ok(())
 }
 /// Internal fixed adapters only. Public requests cannot choose event/originals.
 pub(crate) fn append(&mut self,event:AttemptEvent,operation:&Operation,attempt_id:&str,original_start:Option<&ByteBinding>,raw:&[u8])->Result<PendingAppend>{
  self.current()?;self.control.operation(operation,event==AttemptEvent::Start)?;
  let sequence=self.records.len() as u64+1;need(sequence<=self.header.limits.max_records&&raw.len() as u64<=self.header.limits.max_original_bytes,"ATTEMPT_APPEND_CAPACITY")?;
  let name=format!("{sequence:016}.json");let binding=self.root.binding(&format!("originals/{name}"),raw);
  let start=if event==AttemptEvent::Start{need(original_start.is_none()&&!self.records.iter().any(|r|r.event==AttemptEvent::Start&&(r.operation.operation_id==operation.operation_id||r.attempt_id==attempt_id)),"ATTEMPT_START_ALREADY_RECORDED")?;binding.clone()}else{
   let b=original_start.ok_or(Error("ATTEMPT_ORIGINAL_START_REQUIRED"))?;need(self.records.iter().any(|r|r.event==AttemptEvent::Start&&r.operation==*operation&&r.attempt_id==attempt_id&&r.original_binding==*b)&&!self.records.iter().any(|r|r.operation==*operation&&r.event==event),"ATTEMPT_OBSERVATION_LINEAGE")?;b.clone()
  };
  let record=AttemptRecord{schema_version:"lab-supervisor-attempt-record/v1".into(),sequence,previous_sha256:self.selected.checkpoint.head.sha256.clone(),operation:operation.clone(),attempt_id:attempt_id.into(),event,control_preimage:self.control.current.clone(),original_binding:binding.clone(),original_start_binding:start};
  Self::validate_original(&self.header,&record,raw)?;self.validate_lineage(&record,raw)?;let record_raw=codec::encode(&record)?;need(record_raw.len() as u64<=self.header.limits.max_record_bytes,"ATTEMPT_RECORD_BOUND")?;
  if event==AttemptEvent::Start{self.admission_capacity()?;}
  need(self.total.checked_add((raw.len()+record_raw.len()) as u64).is_some_and(|n|n<=self.header.limits.max_total_bytes),"ATTEMPT_BYTE_CAPACITY")?;
  // After the first write any uncertainty poisons this object. Reopen requires
  // the independent witness and exact full inventory; partial originals remain.
  self.pending=true;
  let originals=evidence::directory(self.root.fd(),"originals",self.root.id())?;let records=evidence::directory(self.root.fd(),"records",self.root.id())?;
  evidence::create(&originals,&name,raw,self.root.id(),1)?;evidence::create(&records,&name,&record_raw,self.root.id(),5)?;
  let head=Head{sequence,sha256:codec::digest(&record_raw)};
  let requested=HostAttemptCheckpoint{schema_version:"lab-host-supervisor-checkpoint/v1".into(),domain:self.header.domain,journal_root:self.header.root.clone(),root_id:self.header.root_id.clone(),journal_header_sha256:self.header_sha.clone(),predecessor:self.selected.checkpoint.head.clone(),head,control_preimage:self.control.current.clone(),operation:Some(operation.clone()),attempt_id:Some(attempt_id.into())};
  self.total+=(raw.len()+record_raw.len()) as u64;self.records.push(record);self.originals.push(raw.to_vec());
  Ok(PendingAppend{requested,original_binding:binding,record_binding:self.root.binding(&format!("records/{name}"),&record_raw),event,attempt_id:attempt_id.into(),operation:operation.clone()})
 }
 pub(crate) fn acknowledge(&mut self,pending:PendingAppend,confirmed:SelectedCheckpoint)->Result<DurableOriginal>{
  need(self.pending&&self.quarantine.is_none()&&confirmed.checkpoint==pending.requested&&confirmed.binding.root_id!=self.header.root_id,"ATTEMPT_HOST_ACK_MISMATCH")?;
  self.control.ledger()?;self.root.validate()?;
  let index=pending.requested.head.sequence as usize-1;need(index+1==self.records.len()&&self.records[index].operation==pending.operation&&self.records[index].attempt_id==pending.attempt_id&&self.records[index].event==pending.event,"ATTEMPT_ACK_PENDING_IDENTITY")?;
  let original=self.originals[index].clone();
  let proof=DurableOriginal{root:self.root.clone_held()?,control_directory:self.control.directory.try_clone()?,header_sha:self.header_sha.clone(),checkpoint:confirmed.checkpoint.clone(),checkpoint_binding:confirmed.binding.clone(),original_binding:pending.original_binding,record_binding:pending.record_binding,original,event:pending.event,operation:pending.operation,attempt_id:pending.attempt_id};proof.validate()?;
  self.selected=confirmed;self.pending=false;
  if let Err(error)=self.current(){self.quarantine=Some(error.0);return Err(error)}Ok(proof)
 }
 pub(crate) fn selected_start(&self,binding:&ByteBinding)->Result<(StartOriginal,Vec<u8>)>{self.current()?;let i=self.records.iter().position(|r|r.event==AttemptEvent::Start&&r.original_binding==*binding).ok_or(Error("SELECTED_ORIGINAL_START_MISSING"))?;Ok((decoded(&self.originals[i])?,self.originals[i].clone()))}


 pub(crate) fn admission_capacity(&self)->Result<()>{
  self.current()?;
  let starts=self.records.iter().filter(|r|r.event==AttemptEvent::Start).count() as u64;
  // Every retained start reserves both terminal and restart-observation slots
  // until each has actually been persisted; normal completion does not erase
  // a possible future cleanup observation. No reservation is recycled/reset.
  let obligations=self.records.iter().filter(|r|r.event==AttemptEvent::Start).map(|r|[AttemptEvent::Terminal,AttemptEvent::Recovery].into_iter().filter(|event|!self.records.iter().any(|o|o.operation==r.operation&&o.event==*event)).count() as u64).sum::<u64>();
  let worst=self.header.limits.max_original_bytes+self.header.limits.max_record_bytes;
  need(starts<self.header.limits.max_attempts&&self.records.len() as u64+3+obligations<=self.header.limits.max_records&&self.total.checked_add((3+obligations)*worst).is_some_and(|n|n<=self.header.limits.max_total_bytes),"ATTEMPT_RESERVED_TERMINAL_CAPACITY")
 }
 pub(crate) fn preflight_admission(&self,root:&super::containment::Root,operation:&Operation)->Result<()>{
  root.admission_currentness()?;self.admission_capacity()?;self.control.operation(operation,true)?;need(!self.records.iter().any(|r|r.event==AttemptEvent::Start&&r.operation.operation_id==operation.operation_id),"ATTEMPT_START_ALREADY_RECORDED")?;
  need(root.root_binding()==&self.header.supervisor_root_binding&&root.physical_identity()?==self.header.supervisor_root_identity,"ADMISSION_ROOT_HEADER")?;self.match_groups(&root.groups()?,None)
 }
 pub(crate) fn validate_launch(&self,proof:&DurableOriginal,root:&super::containment::Root)->Result<()>{
  root.admission_currentness()?;self.current()?;proof.validate()?;need(proof.event()==AttemptEvent::Start&&proof.checkpoint==self.selected.checkpoint&&proof.checkpoint_binding==self.selected.binding,"LAUNCH_CURRENT_START_CHECKPOINT")?;self.control.operation(proof.operation(),true)?;
  need(root.root_binding()==&self.header.supervisor_root_binding&&root.physical_identity()?==self.header.supervisor_root_identity,"LAUNCH_ROOT_HEADER")?;self.match_groups(&root.groups()?,None)
 }
 pub(crate) fn match_groups(&self,observed:&BTreeMap<String,super::containment::Identity>,pending:Option<&StartOriginal>)->Result<()>{
  let mut selected=BTreeMap::new();for(i,r)in self.records.iter().enumerate(){if r.event==AttemptEvent::Start{let s:StartOriginal=decoded(&self.originals[i])?;need(selected.insert(s.attempt_id,s.group_identity).is_none(),"GROUP_DUPLICATE_START")?;}}
  if let Some(s)=pending {need(selected.insert(s.attempt_id.clone(),s.group_identity.clone()).is_none(),"GROUP_PENDING_DUPLICATE")?;}
  need(observed==&selected,"UNEXPLAINED_OR_CHANGED_CHILD_GROUP")
 }
 pub(crate) fn recovery_current(&self)->Result<()>{self.root.validate()?;self.control.ledger()?;let raw=evidence::read(self.root.fd(),"header.json",65536,self.root.id())?;need(codec::digest(&raw)==self.header_sha,"RECOVERY_HEADER_CHANGED")}
 pub(crate) fn selected_start_checkpoint(&self,start:&ByteBinding,checkpoint:&SelectedCheckpoint)->Result<StartOriginal>{
  // A later incomplete tail cannot erase an independently acknowledged prefix.
  // Verify every original prefix byte; permit no launch or journal write here.
  self.recovery_current()?;checkpoint.checkpoint.valid_for(&self.header,&self.header_sha)?;need(checkpoint.binding.root_id!=self.header.root_id&&checkpoint.checkpoint.head.sequence>0,"RECOVERY_WITNESS_NOT_INDEPENDENT")?;
  let records=evidence::directory(self.root.fd(),"records",self.root.id())?;let originals=evidence::directory(self.root.fd(),"originals",self.root.id())?;
  evidence::names(&records,self.header.limits.max_records as usize+1)?;evidence::names(&originals,self.header.limits.max_records as usize+1)?;
  let mut previous=self.header_sha.clone();let mut result=None;
  for sequence in 1..=checkpoint.checkpoint.head.sequence {let name=format!("{sequence:016}.json");let rr=evidence::read(&records,&name,self.header.limits.max_record_bytes,self.root.id())?;let row:AttemptRecord=decoded(&rr)?;let raw=evidence::read(&originals,&name,self.header.limits.max_original_bytes,self.root.id())?;
   need(row.schema_version=="lab-supervisor-attempt-record/v1"&&row.sequence==sequence&&row.previous_sha256==previous&&row.original_binding==self.root.binding(&format!("originals/{name}"),&raw),"RECOVERY_PREFIX_CHAIN")?;Self::validate_original(&self.header,&row,&raw)?;self.control.operation(&row.operation,false)?;self.control.historical(&row.control_preimage)?;
   previous=codec::digest(&rr);
   if sequence==checkpoint.checkpoint.head.sequence {need(row.event==AttemptEvent::Start&&row.original_binding==*start&&row.original_start_binding==*start&&previous==checkpoint.checkpoint.head.sha256&&row.previous_sha256==checkpoint.checkpoint.predecessor.sha256&&checkpoint.checkpoint.operation.as_ref()==Some(&row.operation)&&checkpoint.checkpoint.attempt_id.as_ref()==Some(&row.attempt_id)&&checkpoint.checkpoint.control_preimage==row.control_preimage,"RECOVERY_ORIGINAL_CHECKPOINT")?;result=Some(decoded(&raw)?);}
  }result.ok_or(Error("RECOVERY_START_MISSING"))
 }
 pub(crate) fn outcome(&self,operation:&Operation)->Result<Option<(lab_control_store::ledger::Outcome,ByteBinding)>>{self.control.operation(operation,false)?;Ok(self.control.ledger()?.outcome(&operation.operation_id).cloned())}
 pub(crate) fn held(&self)->&Held<'a>{self.control.held}
 pub(crate) fn control(&self)->&ControlView<'a>{&self.control}
 pub(crate) fn header(&self)->&JournalHeader{&self.header}
}
