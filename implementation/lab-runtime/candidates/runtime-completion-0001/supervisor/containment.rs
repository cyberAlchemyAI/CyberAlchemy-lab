//! Held cgroup2 topology. Actual selection is a fixed-loader capability, not parsed authority.
use super::{need,Error,Result,state::{history_complete,HistoricalDisposition,Scope,populated}};
use lab_control_store::ledger::{ByteBinding,BorrowedOperation};
use serde::{Serialize,Deserialize};
use std::{ffi::CString,fs::File,io::{Read,Write},os::{fd::{AsRawFd,FromRawFd},unix::fs::MetadataExt},path::Path,time::{SystemTime,UNIX_EPOCH}};
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Identity{pub device:u64,pub inode:u64,pub mount_id:u64,pub uid:u32,pub gid:u32,pub mode:u32}
pub fn identity(f:&File)->Result<Identity>{let m=f.metadata()?;let mut s:libc::statx=unsafe{std::mem::zeroed()};need(unsafe{libc::statx(f.as_raw_fd(),c"".as_ptr(),libc::AT_EMPTY_PATH|libc::AT_SYMLINK_NOFOLLOW,libc::STATX_MNT_ID,&mut s)}==0&&s.stx_mask&libc::STATX_MNT_ID!=0,"MOUNT_ID_REQUIRED")?;Ok(Identity{device:m.dev(),inode:m.ino(),mount_id:s.stx_mnt_id,uid:m.uid(),gid:m.gid(),mode:m.mode()&0o7777})}
pub(crate) fn now()->Result<u64>{let n=SystemTime::now().duration_since(UNIX_EPOCH).map_err(|_|Error("UTC_CLOCK"))?.as_nanos();need(n<=i64::MAX as u128,"UTC_BOUND")?;Ok(n as u64)}
pub(crate) fn name(s:&str)->Result<CString>{need(!s.is_empty()&&s.len()<=128&&s.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'-'||b==b'_'),"CGROUP_NAME")?;CString::new(s).map_err(|_|Error("CGROUP_NAME"))}
fn component(s:&str)->Result<CString>{need(!s.is_empty()&&s!="."&&s!=".."&&!s.contains(['/', '\\','\0']),"COMPONENT")?;CString::new(s).map_err(|_|Error("COMPONENT"))}
#[repr(C)]struct How{flags:u64,mode:u64,resolve:u64}
fn open(parent:&File,s:&str,flags:i32,no_xdev:bool)->Result<File>{let c=component(s)?;let h=How{flags:(flags|libc::O_NOFOLLOW|libc::O_CLOEXEC|if flags&libc::O_PATH==0{libc::O_NONBLOCK}else{0}) as u64,mode:0,resolve:0x08|0x04|0x02|if no_xdev{0x01}else{0}};let fd=unsafe{libc::syscall(libc::SYS_openat2,parent.as_raw_fd(),c.as_ptr(),&h,std::mem::size_of::<How>())};need(fd>=0,"OPENAT2_REQUIRED")?;Ok(unsafe{File::from_raw_fd(fd as i32)})}
fn read(parent:&File,s:&str)->Result<Vec<u8>>{let f=open(parent,s,libc::O_RDONLY,true)?;let mut b=Vec::new();f.take(4097).read_to_end(&mut b)?;need(b.len()<=4096,"CGROUP_READ_BOUND")?;Ok(b)}
fn write(parent:&File,s:&str,b:&[u8])->Result<()>{let mut f=open(parent,s,libc::O_WRONLY,true)?;f.write_all(b)?;Ok(())}
fn cgroup2(f:&File)->Result<()>{let mut s:libc::statfs=unsafe{std::mem::zeroed()};need(unsafe{libc::fstatfs(f.as_raw_fd(),&mut s)}==0&&s.f_type==0x63677270,"CGROUP2_REQUIRED")}
/// Only later statically selected host admission code can supply these original verified
/// values. No constructor parses an untrusted request, grants permission, or provisions a root.
pub(crate) struct TrustedHost{
 pub path:String,pub ancestors:Vec<Identity>,pub root_binding:ByteBinding,pub scope:Scope,
 pub expected_history:Vec<ByteBinding>,pub history:Vec<HistoricalDisposition>,pub history_binding:ByteBinding,
 pub custody_policy:ByteBinding,pub currentness:ByteBinding,pub worker_exclusion:ByteBinding,
 pub expires_utc_ns:u64,pub cleanup_until_utc_ns:u64,pub namespaces:Vec<(String,u64,u64)>,pub broker_uid:u32,pub worker_uid:u32,pub worker_gid:u32,
}
#[derive(Clone,Copy,PartialEq,Eq)]enum Purpose{Admission,CleanupOnly}
pub struct Root{selection:TrustedHost,handles:Vec<File>,components:Vec<String>,domain:super::state::Domain,purpose:Purpose}
impl Root{
 pub(crate) fn open(selection:TrustedHost)->Result<Self>{Self::open_selected(selection,super::state::Domain::Actual,Purpose::Admission)}
 #[cfg(test)]pub(crate) fn fixture(selection:TrustedHost)->Result<Self>{Self::open_selected(selection,super::state::Domain::Fixture,Purpose::Admission)}
 /// Fresh custody selection for exact cleanup only; RestartRecovery separately
 /// requires its independently authenticated cleanup grant and original prefix.
 pub(crate) fn open_cleanup(selection:TrustedHost)->Result<Self>{Self::open_selected(selection,super::state::Domain::Actual,Purpose::CleanupOnly)}
 #[cfg(test)]pub(crate) fn fixture_cleanup(selection:TrustedHost)->Result<Self>{Self::open_selected(selection,super::state::Domain::Fixture,Purpose::CleanupOnly)}
 fn open_selected(selection:TrustedHost,domain:super::state::Domain,purpose:Purpose)->Result<Self>{
  need(selection.root_binding.valid()&&selection.history_binding.valid()&&selection.custody_policy.valid()&&selection.currentness.valid()&&selection.worker_exclusion.valid(),"HOST_INPUT_BINDINGS")?;
  need(selection.worker_uid>0&&selection.worker_uid< u32::MAX&&selection.worker_gid>0&&selection.worker_gid<u32::MAX&&selection.worker_uid!=selection.broker_uid,"WORKER_IDENTITY")?;
  let path=Path::new(&selection.path);need(path.is_absolute()&&path.to_str()==Some(selection.path.as_str())&&!selection.path.ends_with('/')&&selection.path.len()<=4096,"CGROUP_ROOT_PATH")?;
  let parts:Vec<_>=selection.path.split('/').skip(1).map(str::to_owned).collect();need(!parts.is_empty()&&parts.len()<=64&&selection.ancestors.len()==parts.len()+1,"ANCESTOR_SELECTION")?;
  let fd=unsafe{libc::open(c"/".as_ptr(),libc::O_RDONLY|libc::O_DIRECTORY|libc::O_CLOEXEC)};need(fd>=0,"ROOT_OPEN")?;
  let mut handles=vec![unsafe{File::from_raw_fd(fd)}];
  for part in &parts {let f=open(handles.last().unwrap(),part,libc::O_RDONLY|libc::O_DIRECTORY,false)?;handles.push(f);}
  let root=Self{selection,handles,components:parts,domain,purpose};root.validate()?;if domain==super::state::Domain::Actual{cgroup2(root.fd())?;need(read(root.fd(),"cgroup.type")?==b"domain\n","CGROUP_DOMAIN_REQUIRED")?;}
  Ok(root)
 }
 fn fd(&self)->&File{self.handles.last().unwrap()}
 fn validate(&self)->Result<()>{
  need(unsafe{libc::geteuid()}==self.selection.broker_uid,"BROKER_IDENTITY_CHANGED")?;
  check_deadline(now()?,self.selection.expires_utc_ns,self.selection.cleanup_until_utc_ns,false)?;
  need(self.selection.namespaces.len()==4,"NAMESPACE_SELECTION")?;for (row,label)in self.selection.namespaces.iter().zip(["mnt","cgroup","user","pid"]){need(row.0==label,"NAMESPACE_ORDER")?;let m=std::fs::metadata(format!("/proc/self/ns/{label}"))?;need(m.dev()==row.1&&m.ino()==row.2,"NAMESPACE_CHANGED")?;}
  need(self.selection.expected_history.len()<=128&&self.selection.history.len()<=128,"HISTORY_BOUND")?;if self.purpose==Purpose::Admission{history_complete(&self.selection.expected_history,&self.selection.history)?;}
  for(i,f)in self.handles.iter().enumerate(){need(identity(f)?==self.selection.ancestors[i],"ANCESTOR_CHANGED")?;
   if i>0{let attached=open(&self.handles[i-1],&self.components[i-1],libc::O_RDONLY|libc::O_DIRECTORY,false)?;need(identity(&attached)?==identity(f)?,"ANCESTOR_DETACHED")?;}
   if self.domain==super::state::Domain::Actual{need(self.selection.ancestors[i].mode&0o022==0,"WRITABLE_ANCESTOR")?;}
  }
  need(identity(self.fd())?.uid==self.selection.broker_uid,"BROKER_ROOT_OWNER")?;
  Ok(())
 }
 pub(crate) fn create<'a>(&'a self,operation:&BorrowedOperation<'_>,attempt:&str,limits:Limits)->Result<Attempt<'a>>{
  self.admission_currentness()?;need(self.domain==super::state::Domain::Actual,"FIXTURE_CANNOT_DISPATCH")?;operation.nested()?;need(self.selection.scope.matches(operation.operation()),"CONTROL_SCOPE")?;limits.validate()?;let n=name(attempt)?;
  // mkdir is no-replace. An existing subtree (even empty) is foreign to this attempt.
  need(unsafe{libc::mkdirat(self.fd().as_raw_fd(),n.as_ptr(),0o700)}==0,"ATTEMPT_EXCLUSIVE_CREATE")?;
  let group=open(self.fd(),attempt,libc::O_RDONLY|libc::O_DIRECTORY,true)?;let id=identity(&group)?;
  need(id.mode&0o022==0&&id.uid==self.selection.broker_uid&&id.mount_id==identity(self.fd())?.mount_id,"ATTEMPT_CUSTODY")?;
  let a=Attempt{root:self,name:attempt.into(),group,id};a.validate()?;
  need(read(&a.group,"cgroup.type")?==b"domain\n"&&!populated(&read(&a.group,"cgroup.events")?)?,"ATTEMPT_NOT_EMPTY_DOMAIN")?;
  write(&a.group,"pids.max",format!("{}\n",limits.pids).as_bytes())?;
  write(&a.group,"memory.max",format!("{}\n",limits.memory_bytes).as_bytes())?;
  write(&a.group,"cpu.max",format!("{} 100000\n",limits.cpu_quota_us).as_bytes())?;
  // No worker ownership/delegation and no migration into an existing group.
  a.validate()?;Ok(a)
 }
 pub(crate) fn admission_currentness(&self)->Result<()>{need(self.purpose==Purpose::Admission,"CLEANUP_ONLY_CANNOT_DISPATCH")?;self.validate()?;history_complete(&self.selection.expected_history,&self.selection.history)?;check_deadline(now()?,self.selection.expires_utc_ns,self.selection.cleanup_until_utc_ns,true)}
 pub(crate) fn historical_complete(&self)->bool{history_complete(&self.selection.expected_history,&self.selection.history).is_ok()}
 pub(crate) fn cleanup_only(&self)->bool{self.purpose==Purpose::CleanupOnly}
 pub(crate) fn domain(&self)->super::state::Domain{self.domain}
 #[cfg(test)]pub(crate) fn fixture_attempt<'a>(&'a self,original:&super::records::StartOriginal)->Result<Attempt<'a>>{need(self.domain==super::state::Domain::Fixture,"FIXTURE_ONLY")?;self.validate()?;let group=open(self.fd(),&original.attempt_id,libc::O_RDONLY|libc::O_DIRECTORY,true)?;need(identity(&group)?==original.group_identity,"FIXTURE_GROUP_CHANGED")?;Ok(Attempt{root:self,name:original.attempt_id.clone(),group,id:original.group_identity.clone()})}
 pub(crate) fn deadlines(&self)->(u64,u64){(self.selection.expires_utc_ns,self.selection.cleanup_until_utc_ns)}
 pub(crate) fn worker(&self)->(u32,u32){(self.selection.worker_uid,self.selection.worker_gid)}
 pub(crate) fn root_binding(&self)->&ByteBinding{&self.selection.root_binding}
 pub(crate) fn history_binding(&self)->&ByteBinding{&self.selection.history_binding}
 pub(crate) fn physical_identity(&self)->Result<Identity>{self.validate()?;identity(self.fd())}
 /// Bounded exact child directory inventory. Kernel control files are not groups.
 pub(crate) fn groups(&self)->Result<std::collections::BTreeMap<String,Identity>>{
  self.validate()?;group_inventory(self.fd(),1024)
 }
 pub(crate) fn reopen_cleanup<'a>(&'a self,original:&super::records::StartOriginal)->Result<CleanupGroup<'a>>{
  need(self.cleanup_only(),"RESTART_REQUIRES_CLEANUP_ONLY_ROOT")?;self.validate()?;need(self.selection.scope.matches(&original.operation)&&self.root_binding()==&original.containment_binding,"RECOVERY_ROOT_SCOPE")?;
  let group=open(self.fd(),&original.attempt_id,libc::O_RDONLY|libc::O_DIRECTORY,true)?;
  need(identity(&group)?==original.group_identity,"RECOVERY_ORIGINAL_GROUP_CHANGED")?;cgroup2(&group)?;
  Ok(CleanupGroup{attempt:Attempt{root:self,name:original.attempt_id.clone(),group,id:original.group_identity.clone()}})
 }
}
pub(crate) fn group_inventory(parent:&File,maximum:usize)->Result<std::collections::BTreeMap<String,Identity>>{
 let mut result=std::collections::BTreeMap::new();let mut entries=0usize;
 for entry in std::fs::read_dir(format!("/proc/self/fd/{}",parent.as_raw_fd()))?{entries+=1;need(entries<=maximum+256,"CGROUP_INVENTORY_BOUND")?;let entry=entry?;let n=entry.file_name().into_string().map_err(|_|Error("CGROUP_NAME_ENCODING"))?;
  let file=open(parent,&n,libc::O_PATH,true)?;let metadata=file.metadata()?;need(metadata.is_file()||metadata.is_dir(),"CGROUP_UNKNOWN_ENTRY_TYPE")?;if metadata.is_dir(){name(&n)?;need(result.len()<maximum,"CGROUP_COUNT_BOUND")?;result.insert(n,identity(&file)?);}
 }Ok(result)
}
/// No dispatch, prepare or clone method exists on this restart handle.
pub(crate) struct CleanupGroup<'a>{attempt:Attempt<'a>}
impl CleanupGroup<'_>{pub(crate) fn kill_owned(&self)->Result<()>{self.attempt.kill_owned()}pub(crate) fn populated(&self)->Result<bool>{self.attempt.populated()}}
#[derive(Clone,Copy,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Limits{pub pids:u32,pub memory_bytes:u64,pub cpu_quota_us:u32,pub output_bytes:u64,pub runtime_ms:u64,pub cleanup_ms:u64}
impl Limits{pub fn validate(self)->Result<()>{need((1..=1024).contains(&self.pids)&&(1024*1024..=16*1024*1024*1024).contains(&self.memory_bytes)&&(1000..=100000).contains(&self.cpu_quota_us)&&(2..=64*1024*1024).contains(&self.output_bytes)&&(1..=86400000).contains(&self.runtime_ms)&&(1..=30000).contains(&self.cleanup_ms),"LIMITS")}}
pub(crate) struct Attempt<'a>{root:&'a Root,name:String,pub(crate) group:File,pub(crate) id:Identity}
impl Attempt<'_>{
 pub(crate) fn root(&self)->&Root{self.root}
 pub(crate) fn validate(&self)->Result<()>{self.root.validate()?;need(identity(&self.group)?==self.id,"ATTEMPT_CHANGED")?;let attached=open(self.root.fd(),&self.name,libc::O_RDONLY|libc::O_DIRECTORY,true)?;need(identity(&attached)?==self.id,"ATTEMPT_DETACHED")}
 pub(crate) fn dispatch_currentness(&self)->Result<()>{self.validate()?;self.root.admission_currentness()}
 pub(crate) fn populated(&self)->Result<bool>{self.validate()?;populated(&read(&self.group,"cgroup.events")?)}
 pub(crate) fn kill_owned(&self)->Result<()>{self.validate()?;write(&self.group,"cgroup.kill",b"1\n")}
}

pub(crate) fn check_deadline(now:u64,dispatch:u64,cleanup:u64,positive:bool)->Result<()>{need(dispatch>0&&dispatch<=cleanup&&cleanup<=i64::MAX as u64&&now<cleanup,"HOST_CLEANUP_SELECTION_EXPIRED")?;if positive{need(now<dispatch,"HOST_DISPATCH_EXPIRED")?;}Ok(())}
