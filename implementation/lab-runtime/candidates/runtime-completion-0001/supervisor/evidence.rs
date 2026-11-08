//! Supervisor-owned held evidence root. Selection does not authenticate host custody.
use super::{need,Error,Result,containment::{Identity,identity},state::Domain};
use lab_control_store::ledger::ByteBinding;
use std::{ffi::CString,fs::File,io::{Read,Write},os::{fd::{AsRawFd,FromRawFd},unix::fs::MetadataExt}};

#[derive(Clone)]
pub(crate) struct EvidenceSelection {
 pub path:String,pub ancestors:Vec<Identity>,pub domain:Domain,pub root_id:String,
 pub custody_binding:ByteBinding,pub alias_exclusion:ByteBinding,
 pub capacity_reserve_binding:ByteBinding,pub reserved_bytes:u64,
}
pub(crate) struct EvidenceRoot { selection:EvidenceSelection,handles:Vec<File>,parts:Vec<String> }
#[repr(C)]struct How {flags:u64,mode:u64,resolve:u64}
fn component(name:&str)->Result<CString>{need(!name.is_empty()&&name!="."&&name!=".."&&!name.contains(['/', '\\','\0'])&&name.len()<=255,"EVIDENCE_COMPONENT")?;CString::new(name).map_err(|_|Error("EVIDENCE_COMPONENT"))}
pub(crate) fn open(parent:&File,name:&str,flags:i32,create:bool)->Result<File>{
 let name=component(name)?;
 let how=How{flags:(flags|libc::O_CLOEXEC|libc::O_NOFOLLOW|libc::O_NONBLOCK) as u64,mode:if create{0o600}else{0},resolve:0x08|0x04|0x02|0x01};
 let fd=unsafe{libc::syscall(libc::SYS_openat2,parent.as_raw_fd(),name.as_ptr(),&how,std::mem::size_of::<How>())};
 need(fd>=0,"EVIDENCE_OPENAT2")?;Ok(unsafe{File::from_raw_fd(fd as i32)})
}
fn ancestor(parent:&File,name:&str)->Result<File>{
 let name=component(name)?;let how=How{flags:(libc::O_RDONLY|libc::O_DIRECTORY|libc::O_CLOEXEC|libc::O_NOFOLLOW|libc::O_NONBLOCK) as u64,mode:0,resolve:0x08|0x04|0x02};
 let fd=unsafe{libc::syscall(libc::SYS_openat2,parent.as_raw_fd(),name.as_ptr(),&how,std::mem::size_of::<How>())};need(fd>=0,"EVIDENCE_ANCESTOR")?;Ok(unsafe{File::from_raw_fd(fd as i32)})
}
pub(crate) fn names(parent:&File,maximum:usize)->Result<Vec<String>>{
 let mut result=Vec::new();for item in std::fs::read_dir(format!("/proc/self/fd/{}",parent.as_raw_fd()))?{
  need(result.len()<maximum,"EVIDENCE_INVENTORY_BOUND")?;let name=item?.file_name().into_string().map_err(|_|Error("EVIDENCE_NAME_ENCODING"))?;component(&name)?;result.push(name);
 }result.sort();Ok(result)
}
pub(crate) fn directory(parent:&File,name:&str,root:&Identity)->Result<File>{let file=open(parent,name,libc::O_RDONLY|libc::O_DIRECTORY,false)?;owned_directory(&file,root)?;Ok(file)}
pub(crate) fn owned_directory(file:&File,root:&Identity)->Result<Identity>{
 let id=identity(file)?;let m=file.metadata()?;need(m.is_dir()&&id.uid==root.uid&&id.gid==root.gid&&id.mode==0o700&&id.mount_id==root.mount_id&&id.device==root.device,"EVIDENCE_DIRECTORY_CUSTODY")?;Ok(id)
}
fn regular(file:&File,root:&Identity)->Result<()>{let m=file.metadata()?;let id=identity(file)?;need(m.is_file()&&m.nlink()==1&&id.uid==root.uid&&id.gid==root.gid&&id.mode==0o600&&id.mount_id==root.mount_id&&id.device==root.device,"EVIDENCE_MEMBER_CUSTODY")}
pub(crate) fn read(parent:&File,name:&str,maximum:u64,root:&Identity)->Result<Vec<u8>>{
 need(maximum<=1_048_576,"EVIDENCE_READ_LIMIT")?;let mut f=open(parent,name,libc::O_RDONLY,false)?;regular(&f,root)?;let before=f.metadata()?;need(before.len()<=maximum,"EVIDENCE_MEMBER_BOUND")?;
 let mut raw=Vec::new();(&mut f).take(maximum+1).read_to_end(&mut raw)?;let after=f.metadata()?;
 let stamp=|m:&std::fs::Metadata|(m.dev(),m.ino(),m.len(),m.mode(),m.uid(),m.gid(),m.nlink(),m.mtime(),m.mtime_nsec(),m.ctime(),m.ctime_nsec());
 need(stamp(&before)==stamp(&after)&&raw.len() as u64==before.len(),"EVIDENCE_MEMBER_CHANGED")?;regular(&f,root)?;Ok(raw)
}
#[cfg(test)]thread_local!{pub(crate) static SYNC_FAIL:std::cell::Cell<u8>=const{std::cell::Cell::new(0)};}
#[cfg(test)]thread_local!{pub(crate) static FAIL_AT:std::cell::Cell<u8>=const{std::cell::Cell::new(0)};}
pub(crate) fn boundary(_point:u8)->Result<()>{#[cfg(test)]if FAIL_AT.with(|p|p.get()==_point){return Err(Error("INJECTED_ATTEMPT_JOURNAL_BOUNDARY"))}Ok(())}
fn sync(file:&File,_point:u8)->Result<()>{
 #[cfg(test)]if SYNC_FAIL.with(|p|p.get()==_point){let path=CString::new(format!("/proc/self/fd/{}",file.as_raw_fd())).map_err(|_|Error("SYNC_FIXTURE_PATH"))?;let fd=unsafe{libc::open(path.as_ptr(),libc::O_PATH|libc::O_CLOEXEC)};need(fd>=0,"SYNC_FIXTURE_OPEN")?;let selected=unsafe{File::from_raw_fd(fd)};return selected.sync_all().map_err(Into::into)}
 file.sync_all()?;Ok(())
}
pub(crate) fn create(parent:&File,name:&str,raw:&[u8],root:&Identity,base:u8)->Result<()>{
 let mut f=open(parent,name,libc::O_WRONLY|libc::O_CREAT|libc::O_EXCL,true)?;regular(&f,root)?;boundary(base)?;
 f.write_all(raw)?;boundary(base+1)?;sync(&f,base+2)?;boundary(base+2)?;sync(parent,base+3)?;boundary(base+3)?;Ok(())
}
pub(crate) fn mkdir(parent:&File,name:&str,root:&Identity)->Result<File>{let n=component(name)?;need(unsafe{libc::mkdirat(parent.as_raw_fd(),n.as_ptr(),0o700)}==0,"EVIDENCE_EXCLUSIVE_DIRECTORY")?;let f=directory(parent,name,root)?;f.sync_all()?;parent.sync_all()?;Ok(f)}
impl EvidenceRoot {
 /// The actual fixed host loader must independently authenticate selection and
 /// exclusive reserve/alias custody. This performs the complete held-file checks;
 /// it never creates, provisions, repairs or adopts an unselected root.
 pub(crate) fn open(selection:EvidenceSelection)->Result<Self>{
  need(selection.path.starts_with('/')&&!selection.path.ends_with('/')&&selection.path.len()<=4096&&selection.root_id.chars().count()>0&&selection.root_id.chars().count()<=4096,"EVIDENCE_ROOT_SELECTION")?;
  need(selection.custody_binding.valid()&&selection.alias_exclusion.valid()&&selection.capacity_reserve_binding.valid()&&selection.reserved_bytes>0,"EVIDENCE_CUSTODY_SELECTION")?;
  let parts:Vec<_>=selection.path.split('/').skip(1).map(str::to_string).collect();need(!parts.is_empty()&&parts.len()<=64&&selection.ancestors.len()==parts.len()+1,"EVIDENCE_ANCESTOR_INVENTORY")?;
  let fd=unsafe{libc::open(c"/".as_ptr(),libc::O_RDONLY|libc::O_DIRECTORY|libc::O_CLOEXEC)};need(fd>=0,"EVIDENCE_ROOT_OPEN")?;let mut handles=vec![unsafe{File::from_raw_fd(fd)}];
  for name in &parts{handles.push(ancestor(handles.last().unwrap(),name)?);}
  let result=Self{selection,handles,parts};result.validate()?;Ok(result)
 }
 pub(crate) fn validate(&self)->Result<()>{
  for(i,f)in self.handles.iter().enumerate(){let id=identity(f)?;need(id==self.selection.ancestors[i],"EVIDENCE_ANCESTOR_CHANGED")?;
   if self.selection.domain==Domain::Actual{need(id.mode&0o022==0,"EVIDENCE_WRITABLE_ANCESTOR")?;}
   if i>0{need(identity(&ancestor(&self.handles[i-1],&self.parts[i-1])?)?==id,"EVIDENCE_ANCESTOR_DETACHED")?;}
  }
  let id=self.id();need(id.uid==unsafe{libc::geteuid()}&&id.gid==unsafe{libc::getegid()}&&id.mode==0o700,"EVIDENCE_ROOT_OWNER")?;owned_directory(self.fd(),id)?;Ok(())
 }
 pub(crate) fn fd(&self)->&File{self.handles.last().unwrap()}
 pub(crate) fn id(&self)->&Identity{self.selection.ancestors.last().unwrap()}
 pub(crate) fn root_id(&self)->&str{&self.selection.root_id}
 pub(crate) fn domain(&self)->Domain{self.selection.domain}
 pub(crate) fn reserve(&self)->u64{self.selection.reserved_bytes}
 pub(crate) fn custody(&self)->&ByteBinding{&self.selection.custody_binding}
 pub(crate) fn clone_held(&self)->Result<Self>{self.validate()?;Ok(Self{selection:self.selection.clone(),handles:self.handles.iter().map(File::try_clone).collect::<std::io::Result<_>>()?,parts:self.parts.clone()})}
 pub(crate) fn binding(&self,path:&str,raw:&[u8])->ByteBinding{ByteBinding{kind:"evidence".into(),root_id:self.root_id().into(),relative_path:path.into(),sha256:lab_control_store::codec::digest(raw),size_bytes:raw.len() as u64}}
}
