//! Held stage/member mechanics. No disk mutation alone is an acknowledgment.
//! Actual receipt/state constructors are crate-private fixed-control boundaries;
//! fixture receipt APIs explicitly reject Actual. No authority provider is here.
use crate::roots::{self,Domain,Error,Exclusive,Identity,Result,require};
use std::{collections::BTreeMap,fs::File,io::{Read,Write},os::{fd::AsRawFd,unix::fs::FileExt}};
use serde::{Deserialize,Serialize};
use serde_json::Value;
use lab_completion_broker::{Frame,authority::{Decision,TrustDomain,VerifiedDispatch}};
use base64::Engine;

const MAX_MEMBERS:usize=1024;
const MAX_DIRS:usize=4096;
const MAX_STAGE_BYTES:u64=1<<30;
const MAX_RECEIPT_BYTES:usize=65536;

// No production fault configuration. These boundaries run only inside this
// unit's compiled test crate, after the indicated real filesystem syscall.
#[cfg(test)]
thread_local!{pub(crate) static FAIL_BOUNDARY:std::cell::Cell<u8>=const{std::cell::Cell::new(0)};}
fn boundary(_phase:u8)->Result<()>{
    #[cfg(test)]
    if FAIL_BOUNDARY.with(|v|v.get()==_phase){return Err(Error("INJECTED_SYSCALL_BOUNDARY"));}
    Ok(())
}

/// Frozen accepted protocol verifies authority first. This owned copy binds the
/// exact full frame, immutable operation fingerprint and trust domain to IO.
pub struct Action {pub(crate) request:Value,pub(crate) wire:String,pub(crate) fingerprint:String,pub(crate) domain:Domain,pub(crate) stage_binding:Option<roots::Binding>}
impl Action {
    pub fn from_verified(raw:&[u8],frame:&Frame,verified:&VerifiedDispatch)->Result<Self> {
        require(raw.len()<=65536&&roots::hash(raw)==frame.wire_digest(),"ORIGINAL_FRAME_BYTES")?;
        let decoded=Frame::decode(raw).map_err(|_|Error("ORIGINAL_FRAME_SCHEMA"))?;
        require(decoded.request()==frame.request(),"ORIGINAL_FRAME_REQUEST")?;
        let original:Value=serde_json::from_slice(raw).map_err(|_|Error("ORIGINAL_FRAME_SCHEMA"))?;
        let stage_binding:Option<roots::Binding>=serde_json::from_value(original["permit"]["payload"]["grant"]["stage_binding"].clone()).map_err(|_|Error("STAGE_BINDING"))?;
        require(stage_binding.as_ref().is_none_or(|b|b.valid()),"STAGE_BINDING")?;
        require(matches!(verified.decision(),Decision::Fresh{..})&&frame.wire_digest()==verified.wire_digest(),"FRESH_EXACT_DISPATCH_REQUIRED")?;
        Ok(Self{request:frame.request().clone(),wire:verified.wire_digest().into(),fingerprint:verified.operation_fingerprint().into(),
            stage_binding,domain:match verified.trust_domain(){TrustDomain::Fixture=>Domain::Fixture,TrustDomain::Actual=>Domain::Actual}})
    }
    fn text<'a>(&'a self,key:&str)->Result<&'a str>{self.request[key].as_str().ok_or(Error("ACTION_FIELD"))}
    fn seq(&self)->Result<u64>{self.request["sequence"].as_u64().ok_or(Error("ACTION_SEQUENCE"))}
    fn payload(&self)->&Value{&self.request["payload"]}
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Range {pub offset:u64,pub length:u64,pub sha256:String,pub sequence:u64,pub wire_digest:String,pub receipt_binding:Option<roots::Binding>}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Member {pub identity:Identity,pub preimage_binding:Value,pub full_sha256:String,pub full_length:u64,pub ranges:Vec<Range>}
impl Member {fn acknowledged_len(&self)->u64{self.ranges.iter().map(|r|r.length).sum()}}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub enum Phase {Staging,Sealed,Published}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Snapshot {
    pub domain:Domain,pub root_id:String,pub execution_scope:roots::ExecutionScope,pub root:Identity,pub namespace_epoch:u64,pub alias_binding:roots::Binding,pub ancestor_binding:roots::Binding,pub acl_binding:roots::Binding,
    pub stage_name:String,pub stage_identity:Identity,pub operation_id:String,pub fingerprint:String,pub next_sequence:u64,
    pub max_bytes:u64,pub phase:Phase,pub members:BTreeMap<String,Member>,pub directories:BTreeMap<String,Identity>,
    pub sealed_manifest_binding:Option<roots::Binding>,pub last_receipt_binding:Option<roots::Binding>,pub stage_binding:Option<roots::Binding>,
}
/// Exact pending result supplied to the fixed control store. It must durably
/// persist the original result under (operation_id,sequence), not latest member.
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Transition {
    pub schema_version:String,pub domain:Domain,pub root_id:String,pub namespace_epoch:u64,
    pub operation_id:String,pub fingerprint:String,pub sequence:u64,pub wire_digest:String,
    pub verb:String,pub stage_identity:Identity,pub state_sha256:String,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
struct Receipt {schema_version:String,transition:Transition,outcome:String}
/// Not deserializable or caller constructible outside the fixed compiled crate.
/// Host loader must independently select exact durable original control bytes.
pub struct DurableReceipt {transition:Transition,bytes:Vec<u8>,binding:roots::Binding,domain:Domain}
impl DurableReceipt {
    pub(crate) fn from_fixed_control(transition:Transition,bytes:Vec<u8>,binding:roots::Binding,domain:Domain)->Result<Self> {
        require(binding.valid()&&bytes.len()<=MAX_RECEIPT_BYTES&&roots::hash(&bytes)==binding.sha256&&bytes.len() as u64==binding.size_bytes,"CONTROL_RECEIPT_BYTES")?;
        let parsed:Receipt=serde_json::from_slice(&bytes).map_err(|_|Error("CONTROL_RECEIPT_SCHEMA"))?;
        require(canonical(&parsed)?==bytes&&parsed.schema_version=="lab-member-durable-receipt/v1"&&parsed.outcome=="durable"&&parsed.transition==transition&&transition.domain==domain,"CONTROL_RECEIPT_SCOPE")?;
        Ok(Self{transition,bytes,binding,domain})
    }
    /// Isolated test adapter only. The caller supplies an already exclusively
    /// opened fixture file; write+fsync is real, but never actual host continuity.
    pub fn persist_fixture(transition:&Transition,parent:&File,receipt_name:&str)->Result<Self> {
        require(transition.domain==Domain::Fixture,"FIXTURE_ONLY")?;
        let bytes=canonical(&Receipt{schema_version:"lab-member-durable-receipt/v1".into(),transition:transition.clone(),outcome:"durable".into()})?;
        require(bytes.len()<=MAX_RECEIPT_BYTES,"RECEIPT_BOUND")?;
        let mut file=roots::open_child(parent,receipt_name,libc::O_RDWR|libc::O_CREAT|libc::O_EXCL,0o600,true)?;
        let parent_id=Identity::observe(parent)?;roots::owned_file(&file,parent_id.uid,parent_id.mount_id)?;
        file.write_all(&bytes)?;file.sync_all()?;parent.sync_all()?;
        let binding=roots::Binding{kind:"evidence".into(),root_id:"fixture-control".into(),relative_path:receipt_name.into(),sha256:roots::hash(&bytes),size_bytes:bytes.len() as u64};
        Self::from_fixed_control(transition.clone(),bytes,binding,Domain::Fixture)
    }
    /// Historical fixture read selects exact operation/sequence/full transition
    /// and independent binding; no 'latest receipt' lookup exists.
    pub fn load_fixture(transition:&Transition,parent:&File,binding:roots::Binding)->Result<Self> {
        require(transition.domain==Domain::Fixture&&binding.root_id=="fixture-control","FIXTURE_ONLY")?;
        let file=roots::open_child(parent,&binding.relative_path,libc::O_RDONLY,0,true)?;
        let parent_id=Identity::observe(parent)?;roots::owned_file(&file,parent_id.uid,parent_id.mount_id)?;
        let len=file.metadata()?.len();require(len<=MAX_RECEIPT_BYTES as u64,"RECEIPT_BOUND")?;
        let mut raw=vec![0;len as usize];file.read_exact_at(&mut raw,0)?;
        Self::from_fixed_control(transition.clone(),raw,binding,Domain::Fixture)
    }
    pub fn binding(&self)->&roots::Binding{&self.binding}
    pub fn sha256(&self)->String{roots::hash(&self.bytes)}
}
fn canonical<T:Serialize>(value:&T)->Result<Vec<u8>> {
    serde_json::to_vec(&serde_json::to_value(value).map_err(|_|Error("ENCODE"))?).map_err(|_|Error("ENCODE"))
}
/// Fixed loader validates this against accepted immutable original control state
/// before restoration. JSON alone is not a TrustedState.
pub struct TrustedState {snapshot:Snapshot}
impl TrustedState {
    pub(crate) fn from_fixed_control(snapshot:Snapshot)->Self{Self{snapshot}}
    pub fn fixture(snapshot:Snapshot)->Result<Self>{require(snapshot.domain==Domain::Fixture,"FIXTURE_ONLY")?;Ok(Self{snapshot})}
}
struct Pending {transition:Transition,after:Snapshot,range:Option<(String,usize)>}
pub struct Stage<'a> {hold:&'a Exclusive<'a>,dir:File,state:Snapshot,pending:Option<Pending>,quarantined:bool}
impl<'a> Stage<'a> {
    pub fn create(hold:&'a Exclusive<'a>,action:&Action)->Result<Self> {
        hold.validate()?;let root=hold.root();let p=action.payload();
        require(root.selection().execution_scope.matches(&action.request)&&action.stage_binding.is_none()&&action.domain==root.selection().domain&&action.text("verb")==Ok("create_stage")&&p["root_id"]==root.selection().root_id,"CREATE_SCOPE")?;
        let stage=p["stage_name"].as_str().ok_or(Error("STAGE_NAME"))?;roots::name(stage)?;
        let max=p["max_bytes"].as_u64().ok_or(Error("STAGE_LIMIT"))?;require(max<=MAX_STAGE_BYTES,"STAGE_LIMIT")?;
        let sequence=action.seq()?;require(sequence<i64::MAX as u64&&roots::digest(&action.wire)&&roots::digest(&action.fingerprint),"ACTION_IDENTITY")?;
        let dir=roots::mkdir(hold.directory(),stage)?;
        let identity=roots::owned_dir(&dir,root.selection().broker_uid,root.identity().mount_id)?;
        let state=Snapshot{domain:action.domain,execution_scope:root.selection().execution_scope.clone(),root_id:root.selection().root_id.clone(),root:root.identity().clone(),namespace_epoch:root.selection().namespace_epoch,
            alias_binding:root.selection().alias_exclusion_binding.clone(),ancestor_binding:root.selection().ancestor_inventory_binding.clone(),acl_binding:root.selection().acl_policy_binding.clone(),stage_name:stage.into(),stage_identity:identity,operation_id:action.text("operation_id")?.into(),fingerprint:action.fingerprint.clone(),next_sequence:sequence,
            max_bytes:max,phase:Phase::Staging,members:BTreeMap::new(),directories:BTreeMap::new(),sealed_manifest_binding:None,last_receipt_binding:None,stage_binding:None};
        let mut out=Self{hold,dir,state,pending:None,quarantined:false};out.validate_attachment()?;out.set_pending(action,out.state.clone(),None)?;Ok(out)
    }
    pub fn restore(hold:&'a Exclusive<'a>,selected:TrustedState)->Result<Self> {
        hold.validate()?;let state=selected.snapshot;let root=hold.root();
        require(state.execution_scope==root.selection().execution_scope&&state.domain==root.selection().domain&&state.root_id==root.selection().root_id&&state.root==*root.identity()&&state.namespace_epoch==root.selection().namespace_epoch&&state.alias_binding==root.selection().alias_exclusion_binding&&state.ancestor_binding==root.selection().ancestor_inventory_binding&&state.acl_binding==root.selection().acl_policy_binding,"RESTORE_SCOPE")?;
        require(state.next_sequence<=i64::MAX as u64&&roots::digest(&state.fingerprint)&&state.last_receipt_binding.as_ref().is_some_and(|b|b.valid())&&state.stage_binding.as_ref().is_some_and(|b|b.valid())&&state.max_bytes<=MAX_STAGE_BYTES,"RESTORE_IDENTITY")?;
        let dir=roots::open_child(hold.directory(),&state.stage_name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        let out=Self{hold,dir,state,pending:None,quarantined:false};out.verify_contents(false)?;Ok(out)
    }
    pub fn execution_scope(&self)->&roots::ExecutionScope{&self.state.execution_scope}
    pub fn stage_binding(&self)->Option<&roots::Binding>{self.state.stage_binding.as_ref()}
    pub fn snapshot(&self)->Result<Snapshot>{require(!self.quarantined&&self.pending.is_none(),"PENDING_OR_QUARANTINED")?;self.verify_contents(false)?;Ok(self.state.clone())}
    /// Proposed metadata for the fixed control append. Receipt hashes remain empty
    /// until the original durable receipt is selected; this is not trusted state.
    pub fn proposed_state(&self)->Option<&Snapshot>{self.pending.as_ref().map(|p|&p.after)}
    pub fn pending(&self)->Option<&Transition>{self.pending.as_ref().map(|p|&p.transition)}
    pub fn acknowledge(&mut self,receipt:DurableReceipt)->Result<()> {
        let p=self.pending.as_ref().ok_or(Error("NO_PENDING_TRANSITION"))?;
        require(!self.quarantined&&receipt.domain==self.state.domain&&receipt.transition==p.transition,"ACK_SCOPE")?;
        // Recheck named custody, bytes and inventory after durable control append.
        // A replacement between write and acknowledgment cannot earn success.
        let mut after=p.after.clone();let binding=receipt.binding.clone();
        if let Some((member,index))=&p.range {after.members.get_mut(member).ok_or(Error("ACK_MEMBER"))?.ranges[*index].receipt_binding=Some(binding.clone());}
        after.last_receipt_binding=Some(binding.clone());if p.transition.verb=="create_stage"{after.stage_binding=Some(binding);}after.next_sequence=p.transition.sequence.checked_add(1).ok_or(Error("SEQUENCE_OVERFLOW"))?;
        let old=std::mem::replace(&mut self.state,after);
        if let Err(e)=self.verify_contents(false){self.state=old;self.quarantined=true;return Err(e);}
        self.pending=None;Ok(())
    }
    fn validate_attachment(&self)->Result<()> {
        self.hold.validate()?;
        let named=roots::open_child(self.hold.directory(),&self.state.stage_name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        require(roots::owned_dir(&named,self.state.root.uid,self.state.root.mount_id)?==self.state.stage_identity&&Identity::observe(&self.dir)?==self.state.stage_identity,"STAGE_ATTACHMENT")
    }
    fn check(&self,action:&Action,verb:&str)->Result<()> {
        require(!self.quarantined&&self.pending.is_none(),"PENDING_OR_QUARANTINED")?;self.validate_attachment()?;
        require(self.state.execution_scope.matches(&action.request)&&action.stage_binding==self.state.stage_binding&&action.domain==self.state.domain&&action.text("verb")==Ok(verb)&&action.text("operation_id")==Ok(self.state.operation_id.as_str())&&action.fingerprint==self.state.fingerprint&&action.seq()?==self.state.next_sequence&&action.payload()["root_id"]==self.state.root_id&&roots::digest(&action.wire),"OPERATION_SEQUENCE_SCOPE")?;
        require(self.state.next_sequence<i64::MAX as u64,"SEQUENCE_EXHAUSTED")
    }
    fn set_pending(&mut self,action:&Action,after:Snapshot,range:Option<(String,usize)>)->Result<()> {
        let transition=Transition{schema_version:"lab-member-pending-transition/v1".into(),domain:self.state.domain,root_id:self.state.root_id.clone(),namespace_epoch:self.state.namespace_epoch,
            operation_id:self.state.operation_id.clone(),fingerprint:self.state.fingerprint.clone(),sequence:action.seq()?,wire_digest:action.wire.clone(),verb:action.text("verb")?.into(),stage_identity:self.state.stage_identity.clone(),state_sha256:roots::hash(&canonical(&after)?)};
        self.pending=Some(Pending{transition,after,range});Ok(())
    }
    fn directory(&self,path:&str)->Result<File> {
        let mut dir=self.dir.try_clone()?;let mut joined=String::new();
        if path.is_empty(){return Ok(dir)}
        for part in roots::parts(path)? {
            if !joined.is_empty(){joined.push('/')}joined.push_str(part);
            dir=roots::open_child(&dir,part,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
            require(self.state.directories.get(&joined)==Some(&roots::owned_dir(&dir,self.state.root.uid,self.state.root.mount_id)?),"DIRECTORY_ATTACHMENT")?;
        }Ok(dir)
    }
    fn open_member(&self,path:&str)->Result<File> {
        let parts=roots::parts(path)?;let parent=self.directory(&parts[..parts.len()-1].join("/"))?;
        let file=roots::open_child(&parent,parts[parts.len()-1],libc::O_RDONLY,0,true)?;
        let member=self.state.members.get(path).ok_or(Error("UNSELECTED_MEMBER"))?;
        require(roots::owned_file(&file,self.state.root.uid,self.state.root.mount_id)?==member.identity,"MEMBER_ATTACHMENT")?;Ok(file)
    }
    fn verify_contents(&self,full:bool)->Result<()> {
        self.validate_attachment()?;
        require(self.state.members.len()<=MAX_MEMBERS&&self.state.directories.len()<=MAX_DIRS,"INVENTORY_BOUND")?;
        let mut dirs=vec![String::new()];dirs.extend(self.state.directories.keys().cloned());
        for dir in dirs {
            let prefix=if dir.is_empty(){String::new()}else{format!("{dir}/")};let f=self.directory(&dir)?;
            let mut expected=Vec::new();
            for key in self.state.members.keys().chain(self.state.directories.keys()) {
                if let Some(rest)=key.strip_prefix(&prefix){if !rest.contains('/'){expected.push(rest.to_string());}}
            }expected.sort();require(expected==roots::names(&f,MAX_MEMBERS+MAX_DIRS+1)?,"UNEXPLAINED_STAGE_ENTRY")?;
        }
        let mut total=0u64;let mut seen_sequences=std::collections::BTreeSet::new();
        for (path,member) in &self.state.members {
            require(roots::digest(&member.full_sha256)&&member.full_length<=self.state.max_bytes&&!member.ranges.is_empty()&&member.ranges.len()<=32769&&(member.full_length!=0||member.ranges.len()==1),"MEMBER_BOUND")?;
            let f=self.open_member(path)?;let mut offset=0u64;let mut last=None;
            for range in &member.ranges {
                require(seen_sequences.insert(range.sequence)&&range.sequence<self.state.next_sequence&&range.offset==offset&&range.length<=32768&&(range.length>0||member.full_length==0)&&roots::digest(&range.wire_digest)&&range.receipt_binding.as_ref().is_some_and(|b|b.valid())&&last.is_none_or(|n|range.sequence>n),"RANGE_HISTORY")?;
                let mut raw=vec![0;range.length as usize];f.read_exact_at(&mut raw,range.offset)?;require(roots::hash(&raw)==range.sha256,"ACKNOWLEDGED_RANGE_CHANGED")?;
                offset=offset.checked_add(range.length).ok_or(Error("RANGE_OVERFLOW"))?;last=Some(range.sequence);
            }
            require(offset<=member.full_length&&f.metadata()?.len()==offset,"UNEXPLAINED_MEMBER_TAIL")?;
            total=total.checked_add(offset).ok_or(Error("STAGE_OVERFLOW"))?;
            if full||self.state.phase!=Phase::Staging {
                require(offset==member.full_length,"INCOMPLETE_MEMBER")?;
                let mut h=sha2::Sha256::new();use sha2::Digest;let mut reader=f.take(member.full_length+1);let mut buffer=[0u8;32768];
                loop{let n=reader.read(&mut buffer)?;if n==0{break}h.update(&buffer[..n]);}require(format!("{:x}",h.finalize())==member.full_sha256,"FULL_MEMBER_DIGEST")?;
            }
        }
        require(total<=self.state.max_bytes,"STAGE_LIMIT")?;Ok(())
    }
    pub fn write_member(&mut self,action:&Action)->Result<()> {
        self.check(action,"write_member")?;require(self.state.phase==Phase::Staging,"STAGE_PHASE")?;self.verify_contents(false)?;
        let result=self.write_inner(action);if result.is_err(){self.quarantined=true;}result
    }
    fn write_inner(&mut self,action:&Action)->Result<()> {
        let p=action.payload();let path=p["member"].as_str().ok_or(Error("MEMBER_PATH"))?;let parts=roots::parts(path)?;
        let full=p["full_length"].as_u64().ok_or(Error("MEMBER_LENGTH"))?;let offset=p["offset"].as_u64().ok_or(Error("MEMBER_OFFSET"))?;
        let length=p["length"].as_u64().ok_or(Error("MEMBER_LENGTH"))?;let full_hash=p["full_sha256"].as_str().ok_or(Error("MEMBER_HASH"))?;
        require(full<=self.state.max_bytes&&length<=32768&&offset.checked_add(length).is_some_and(|n|n<=full)&&roots::digest(full_hash),"MEMBER_RANGE")?;
        let raw=base64::engine::general_purpose::STANDARD.decode(p["bytes_base64"].as_str().ok_or(Error("CHUNK_ENCODING"))?).map_err(|_|Error("CHUNK_ENCODING"))?;
        require(raw.len()==length as usize&&roots::hash(&raw)==p["chunk_sha256"].as_str().ok_or(Error("CHUNK_HASH"))?&&(length>0||(full==0&&offset==0)),"CHUNK_BYTES")?;
        let used:u64=self.state.members.values().map(Member::acknowledged_len).sum();require(used.checked_add(length).is_some_and(|n|n<=self.state.max_bytes),"STAGE_LIMIT")?;
        let mut after=self.state.clone();let mut parent=self.dir.try_clone()?;let mut joined=String::new();
        for part in &parts[..parts.len()-1] {
            if !joined.is_empty(){joined.push('/')}joined.push_str(part);
            if let Some(expected)=after.directories.get(&joined) {
                parent=roots::open_child(&parent,part,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
                require(roots::owned_dir(&parent,self.state.root.uid,self.state.root.mount_id)?==*expected,"DIRECTORY_ATTACHMENT")?;
            }else{
                require(after.directories.len()<MAX_DIRS,"DIRECTORY_LIMIT")?;parent=roots::mkdir(&parent,part)?;
                after.directories.insert(joined.clone(),roots::owned_dir(&parent,self.state.root.uid,self.state.root.mount_id)?);
            }
        }
        let child=parts[parts.len()-1];
        let file=if let Some(member)=after.members.get(path) {
            require(member.preimage_binding==p["preimage_binding"]&&member.full_length==full&&member.full_sha256==full_hash&&member.acknowledged_len()==offset&&!(full==0&&!member.ranges.is_empty()),"MEMBER_CONTINUITY")?;
            let f=roots::open_child(&parent,child,libc::O_RDWR,0,true)?;require(roots::owned_file(&f,self.state.root.uid,self.state.root.mount_id)?==member.identity,"MEMBER_ATTACHMENT")?;f
        }else{
            require(offset==0&&after.members.len()<MAX_MEMBERS,"MEMBER_START")?;
            let f=roots::open_child(&parent,child,libc::O_RDWR|libc::O_CREAT|libc::O_EXCL,0o600,true)?;
            let identity=roots::owned_file(&f,self.state.root.uid,self.state.root.mount_id)?;
            after.members.insert(path.into(),Member{identity,preimage_binding:p["preimage_binding"].clone(),full_sha256:full_hash.into(),full_length:full,ranges:Vec::new()});f
        };
        require(file.metadata()?.len()==offset,"MEMBER_TAIL")?;file.write_all_at(&raw,offset)?;boundary(1)?;file.sync_all()?;boundary(2)?;parent.sync_all()?;self.dir.sync_all()?;boundary(3)?;
        // Publish only pending metadata. Every range gets the selected original
        // control receipt hash during acknowledgment, never an invented one.
        let member=after.members.get_mut(path).unwrap();member.ranges.push(Range{offset,length,sha256:roots::hash(&raw),sequence:action.seq()?,wire_digest:action.wire.clone(),receipt_binding:None});
        let index=member.ranges.len()-1;self.validate_attachment()?;self.set_pending(action,after,Some((path.into(),index)))
    }
    /// Manifest is exact selected control subject; no adding members after seal.
    pub fn seal(&mut self,action:&Action,manifest:&[u8])->Result<()> {
        self.check(action,"seal_stage")?;require(self.state.phase==Phase::Staging,"STAGE_PHASE")?;
        self.check_manifest(action,manifest)?;self.verify_contents(true)?;
        for path in self.state.members.keys(){self.open_member(path)?.sync_all()?;}
        for path in self.state.directories.keys(){self.directory(path)?.sync_all()?;}
        self.dir.sync_all()?;let mut after=self.state.clone();after.phase=Phase::Sealed;after.sealed_manifest_binding=Some(serde_json::from_value(action.payload()["subject_binding"].clone()).map_err(|_|Error("MANIFEST_BINDING"))?);self.set_pending(action,after,None)
    }
    fn check_manifest(&self,action:&Action,bytes:&[u8])->Result<()> {
        require(bytes.len()<=65536&&action.payload()["subject_binding"]["sha256"]==roots::hash(bytes)&&action.payload()["subject_binding"]["size_bytes"]==bytes.len() as u64,"MANIFEST_BINDING")?;
        let selected:Manifest=serde_json::from_slice(bytes).map_err(|_|Error("MANIFEST_SCHEMA"))?;
        require(canonical(&selected)?==bytes&&selected.schema_version=="lab-member-generation/v1"&&selected.operation_id==self.state.operation_id&&selected.fingerprint==self.state.fingerprint&&selected.root_id==self.state.root_id&&selected.stage_identity==self.state.stage_identity,"MANIFEST_SCOPE")?;
        roots::name(&selected.generation_name)?;
        let members:BTreeMap<_,_>=self.state.members.iter().map(|(p,m)|(p.clone(),MemberContent{sha256:m.full_sha256.clone(),size_bytes:m.full_length})).collect();
        require(selected.members==members,"MANIFEST_MEMBERS")
    }
    pub fn publish(&mut self,action:&Action,manifest:&[u8])->Result<()> {
        self.check(action,"commit_generation")?;require(self.state.phase==Phase::Sealed,"STAGE_PHASE")?;self.check_manifest(action,manifest)?;self.verify_contents(true)?;
        require(self.state.sealed_manifest_binding.as_ref().is_some_and(|b|serde_json::to_value(b).ok().as_ref()==Some(&action.payload()["subject_binding"])),"SEALED_MANIFEST_CHANGED")?;
        let selected:Manifest=serde_json::from_slice(manifest).map_err(|_|Error("MANIFEST_SCHEMA"))?;
        require(selected.generation_name!=self.state.stage_name,"PUBLICATION_NAME")?;
        let old=roots::name(&self.state.stage_name)?;let new=roots::name(&selected.generation_name)?;
        let rc=unsafe{libc::renameat2(self.hold.directory().as_raw_fd(),old.as_ptr(),self.hold.directory().as_raw_fd(),new.as_ptr(),libc::RENAME_NOREPLACE)};
        require(rc==0,"PUBLICATION_COLLISION_OR_FAILURE")?;
        // Once rename succeeded, any sync/verification failure is uncertainty.
        self.quarantined=true;boundary(4)?;self.hold.directory().sync_all()?;
        self.state.stage_name=selected.generation_name;self.validate_attachment()?;
        let mut after=self.state.clone();after.phase=Phase::Published;self.set_pending(action,after,None)?;self.quarantined=false;Ok(())
    }
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MemberContent {pub sha256:String,pub size_bytes:u64}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Manifest {pub schema_version:String,pub root_id:String,pub operation_id:String,pub fingerprint:String,pub stage_identity:Identity,pub generation_name:String,pub members:BTreeMap<String,MemberContent>}
