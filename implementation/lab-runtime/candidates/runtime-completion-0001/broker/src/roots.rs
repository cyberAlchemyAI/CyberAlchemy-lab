//! Linux held-root mechanics. Actual ancestor/namespace/alias exclusion is an
//! independently selected host invariant, not inferred from a pathname or UID.
use serde::{Deserialize, Serialize};
use std::{ffi::CString, fs::{File,OpenOptions}, 
    os::{fd::{AsRawFd,FromRawFd},unix::fs::{MetadataExt,OpenOptionsExt}},
    path::{Component,Path},time::{Duration,Instant}};

#[derive(Debug,Clone,PartialEq,Eq)]
pub struct Error(pub &'static str);
pub type Result<T> = std::result::Result<T,Error>;
impl From<std::io::Error> for Error { fn from(_:std::io::Error)->Self {Self("IO_FAILURE")} }
pub(crate) fn require(ok:bool,why:&'static str)->Result<()> {if ok {Ok(())}else{Err(Error(why))}}
pub(crate) fn hash(raw:&[u8])->String {use sha2::{Digest,Sha256};format!("{:x}",Sha256::digest(raw))}
pub(crate) fn digest(s:&str)->bool {s.len()==64&&s.bytes().all(|b|b.is_ascii_digit()||(b'a'..=b'f').contains(&b))}
pub(crate) fn name(s:&str)->Result<CString> {
    require(!s.is_empty()&&s.len()<=255&&!s.contains('/')&&!s.contains('\\')&&s!="."&&s!="..","CHILD_NAME")?;
    CString::new(s).map_err(|_|Error("CHILD_NAME"))
}
pub(crate) fn parts(s:&str)->Result<Vec<&str>> {
    require(!s.is_empty()&&s.len()<=1024&&!s.starts_with('/')&&!s.ends_with('/'),"RELATIVE_PATH")?;
    let parts:Vec<_>=s.split('/').collect();require(parts.len()<=32,"PATH_DEPTH")?;
    for p in &parts {name(p)?;} Ok(parts)
}
#[derive(Debug,Clone,Copy,PartialEq,Eq,Serialize,Deserialize)]
#[serde(rename_all="lowercase")]
pub enum Domain {Fixture,Actual}
#[derive(Debug,Clone,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Identity {pub device:u64,pub inode:u64,pub mount_id:u64,pub uid:u32,pub gid:u32,pub mode:u32}
impl Identity {
    pub fn observe(file:&File)->Result<Self> {
        let m=file.metadata()?;let mut sx:libc::statx=unsafe{std::mem::zeroed()};
        let empty=CString::new("").unwrap();
        let rc=unsafe{libc::statx(file.as_raw_fd(),empty.as_ptr(),libc::AT_EMPTY_PATH|libc::AT_SYMLINK_NOFOLLOW,
            libc::STATX_BASIC_STATS|libc::STATX_MNT_ID,&mut sx)};
        require(rc==0&&sx.stx_mask&libc::STATX_MNT_ID!=0,"MOUNT_ID_UNAVAILABLE")?;
        Ok(Self{device:m.dev(),inode:m.ino(),mount_id:sx.stx_mnt_id,uid:m.uid(),gid:m.gid(),mode:m.mode()&0o7777})
    }
}
/// Complete independently selected C01 metadata identity, never a digest-only
/// substitute for authority/custody policy provenance. Bodies are not read here.
#[derive(Debug,Clone,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Binding {pub kind:String,pub root_id:String,pub relative_path:String,pub sha256:String,pub size_bytes:u64}
impl Binding {
    pub fn valid(&self)->bool {
        matches!(self.kind.as_str(),"execution"|"semantic"|"evidence"|"public-package"|"protected-input")&&
        (1..=4096).contains(&self.root_id.chars().count())&&(1..=4096).contains(&self.relative_path.chars().count())&&
        !self.relative_path.contains(['\\','\0'])&&self.relative_path.split('/').all(|p|!p.is_empty()&&p!="."&&p!="..")&&
        digest(&self.sha256)&&self.size_bytes<=i64::MAX as u64
    }

}
/// Selected from the same activation/root inventory used by the fixed verifier.
/// Slot epoch is an authority/family value, distinct from namespace custody epoch.
#[derive(Debug,Clone,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExecutionScope {pub activation_binding:Binding,pub store_id:String,pub instance_id:String,pub slot_epoch:u64,pub principal_ref:String}
impl ExecutionScope {
    pub fn valid(&self)->bool {self.activation_binding.valid()&&self.slot_epoch>0&&self.slot_epoch<=i64::MAX as u64&&[&self.store_id,&self.instance_id,&self.principal_ref].iter().all(|s|!s.is_empty()&&s.len()<=128)}
    pub fn matches(&self,request:&serde_json::Value)->bool {
        self.valid()&&request["activation_binding"]==serde_json::to_value(&self.activation_binding).unwrap()&&
        request["store_id"]==self.store_id&&request["instance_id"]==self.instance_id&&request["slot_epoch"]==self.slot_epoch&&request["principal_ref"]==self.principal_ref
    }
}
#[derive(Debug,Clone,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Selection {
    pub root_id:String,pub execution_scope:ExecutionScope,pub absolute_path:String,pub ancestors:Vec<Identity>,pub domain:Domain,
    pub administrator_uid:u32,pub broker_uid:u32,pub namespace_epoch:u64,
    /// Independently selected current host observation of no writable aliases,
    /// prior writable descriptors, mount/user namespace substitution or ACLs.
    /// Fixture digest proves only fixture selection, never actual host custody.
    pub alias_exclusion_binding:Binding,
    pub ancestor_inventory_binding:Binding,pub acl_policy_binding:Binding,
}
#[repr(C)] struct OpenHow {flags:u64,mode:u64,resolve:u64}
pub(crate) fn open_child(parent:&File,child:&str,flags:i32,mode:u32,no_xdev:bool)->Result<File> {
    let c=name(child)?;
    let how=OpenHow{flags:(flags|libc::O_NOFOLLOW|libc::O_CLOEXEC|libc::O_NONBLOCK) as u64,
        mode:if flags&libc::O_CREAT!=0 {mode as u64}else{0},
        resolve:0x08|0x04|0x02|if no_xdev {0x01}else{0}};
    let fd=unsafe{libc::syscall(libc::SYS_openat2,parent.as_raw_fd(),c.as_ptr(),&how,std::mem::size_of::<OpenHow>())} as i32;
    require(fd>=0,"OPEN_BENEATH_FAILED")?;Ok(unsafe{File::from_raw_fd(fd)})
}
pub(crate) fn no_acl(file:&File)->Result<()> {
    for x in ["system.posix_acl_access","system.posix_acl_default"] {
        let c=CString::new(x).unwrap();let rc=unsafe{libc::fgetxattr(file.as_raw_fd(),c.as_ptr(),std::ptr::null_mut(),0)};
        if rc>=0 {return Err(Error("EXTENDED_ACL_REFUSED"));}
        let e=std::io::Error::last_os_error().raw_os_error();
        require(e==Some(libc::ENODATA)||e==Some(libc::ENOTSUP),"ACL_OBSERVATION_FAILED")?;
    }Ok(())
}
pub(crate) fn owned_dir(file:&File,uid:u32,mount:u64)->Result<Identity> {
    let id=Identity::observe(file)?;
    require(file.metadata()?.is_dir()&&id.uid==uid&&id.mode==0o700&&id.mount_id==mount,"DIRECTORY_CUSTODY")?;
    no_acl(file)?;Ok(id)
}
pub(crate) fn owned_file(file:&File,uid:u32,mount:u64)->Result<Identity> {
    let id=Identity::observe(file)?;let m=file.metadata()?;
    require(m.is_file()&&m.nlink()==1&&id.uid==uid&&id.mode==0o600&&id.mount_id==mount,"MEMBER_CUSTODY")?;
    no_acl(file)?;Ok(id)
}
pub(crate) fn mkdir(parent:&File,child:&str)->Result<File> {
    let c=name(child)?;require(unsafe{libc::mkdirat(parent.as_raw_fd(),c.as_ptr(),0o700)}==0,"DIRECTORY_COLLISION_OR_FAILURE")?;
    let f=open_child(parent,child,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
    f.sync_all()?;parent.sync_all()?;Ok(f)
}
pub(crate) fn names(dir:&File,maximum:usize)->Result<Vec<String>> {
    let mut out=Vec::new();
    for row in std::fs::read_dir(format!("/proc/self/fd/{}",dir.as_raw_fd()))? {
        require(out.len()<maximum,"INVENTORY_LIMIT")?;
        out.push(row?.file_name().into_string().map_err(|_|Error("NAME_ENCODING"))?);
    }out.sort();Ok(out)
}
fn absolute_parts(path:&str)->Result<Vec<String>> {
    require(path.starts_with('/')&&path.len()<=4096,"ROOT_PATH")?;
    let mut out=Vec::new();
    for part in Path::new(path).components() {match part {Component::RootDir=>(),Component::Normal(n)=>{
        let n=n.to_str().ok_or(Error("ROOT_ENCODING"))?;name(n)?;out.push(n.into());},_=>return Err(Error("ROOT_PATH"))}}
    require(!out.is_empty()&&out.len()<=64&&format!("/{}",out.join("/"))==path,"ROOT_PATH")?;Ok(out)
}
fn slash()->Result<File> {Ok(OpenOptions::new().read(true).custom_flags(libc::O_DIRECTORY|libc::O_NOFOLLOW|libc::O_CLOEXEC).open("/")?)}
struct HeldAncestor {file:File,identity:Identity}
pub struct Root {selection:Selection,components:Vec<String>,chain:Vec<HeldAncestor>}
impl Root {
    /// Fixture observer is never an Actual enrollment or writable-alias proof.
    pub fn capture_fixture(path:&Path,root_id:&str,policies:[Binding;3],execution_scope:ExecutionScope)->Result<Selection> {
        let path=path.to_str().ok_or(Error("ROOT_ENCODING"))?;let components=absolute_parts(path)?;
        let mut f=slash()?;let mut ancestors=vec![Identity::observe(&f)?];
        for p in components {f=open_child(&f,&p,libc::O_RDONLY|libc::O_DIRECTORY,0,false)?;ancestors.push(Identity::observe(&f)?);}
        Ok(Selection{root_id:root_id.into(),execution_scope,absolute_path:path.into(),ancestors,domain:Domain::Fixture,
            administrator_uid:unsafe{libc::geteuid()},broker_uid:unsafe{libc::geteuid()},namespace_epoch:1,
            alias_exclusion_binding:policies[0].clone(),ancestor_inventory_binding:policies[1].clone(),acl_policy_binding:policies[2].clone()})
    }
    /// Caller is fixed trusted host selection code. It must independently verify
    /// the external alias/namespace observation before selecting Actual.
    pub fn open(selection:Selection,required_domain:Domain)->Result<Self> {
        require(selection.execution_scope.valid()&&selection.domain==required_domain&&selection.namespace_epoch>0&&selection.namespace_epoch<=i64::MAX as u64&&selection.alias_exclusion_binding.valid()&&selection.ancestor_inventory_binding.valid()&&selection.acl_policy_binding.valid(),"HOST_SELECTION")?;
        require(!selection.root_id.is_empty()&&selection.root_id.len()<=128,"ROOT_ID")?;
        require(selection.broker_uid==unsafe{libc::geteuid()},"BROKER_OWNER")?;
        let components=absolute_parts(&selection.absolute_path)?;
        require(selection.ancestors.len()==components.len()+1,"ANCESTOR_COVERAGE")?;
        let mut chain=Vec::new();let f=slash()?;
        require(Identity::observe(&f)?==selection.ancestors[0],"ANCESTOR_IDENTITY")?;
        chain.push(HeldAncestor{identity:selection.ancestors[0].clone(),file:f});
        for (i,c) in components.iter().enumerate() {
            let prev=&chain[i];let expected=&selection.ancestors[i+1];
            let f=open_child(&prev.file,c,libc::O_RDONLY|libc::O_DIRECTORY,0,prev.identity.mount_id==expected.mount_id)?;
            require(Identity::observe(&f)?==*expected,"ANCESTOR_IDENTITY")?;
            chain.push(HeldAncestor{file:f,identity:expected.clone()});
        }
        let root=Self{selection,components,chain};root.validate()?;Ok(root)
    }
    pub fn selection(&self)->&Selection {&self.selection}
    pub fn identity(&self)->&Identity {&self.chain.last().unwrap().identity}
    pub(crate) fn directory(&self)->&File {&self.chain.last().unwrap().file}
    pub fn validate(&self)->Result<()> {
        let mut f=slash()?;
        for (i,held) in self.chain.iter().enumerate() {
            if i>0 {f=open_child(&f,&self.components[i-1],libc::O_RDONLY|libc::O_DIRECTORY,0,
                self.chain[i-1].identity.mount_id==held.identity.mount_id)?;}
            require(Identity::observe(&f)?==held.identity&&Identity::observe(&held.file)?==held.identity,"ANCESTOR_ATTACHMENT_CHANGED")?;
            let id=&held.identity;require(id.mode&0o022==0,"WRITABLE_ANCESTOR")?;no_acl(&f)?;
            if self.selection.domain==Domain::Actual {require(id.uid==self.selection.administrator_uid||id.uid==self.selection.broker_uid,"NONADMIN_ANCESTOR")?;}
        }
        owned_dir(self.directory(),self.selection.broker_uid,self.identity().mount_id)?;Ok(())
    }
    pub fn exclusive(&self,timeout:Duration)->Result<Exclusive<'_>> {
        require(self.selection.domain==Domain::Fixture,"ACTUAL_REQUIRES_PARENT_CUSTODY")?;
        require(!timeout.is_zero()&&timeout<=Duration::from_secs(30),"LOCK_DEADLINE")?;self.validate()?;
        // New open file description, not dup: a second lock cannot silently
        // succeed as a reentrant flock on the same open description.
        let dot=CString::new(".").unwrap();let fd=unsafe{libc::openat(self.directory().as_raw_fd(),dot.as_ptr(),libc::O_RDONLY|libc::O_DIRECTORY|libc::O_CLOEXEC|libc::O_NOFOLLOW)};
        require(fd>=0,"LOCK_OPEN")?;let file=unsafe{File::from_raw_fd(fd)};let end=Instant::now()+timeout;
        loop {
            if unsafe{libc::flock(fd,libc::LOCK_EX|libc::LOCK_NB)}==0 {break;}
            let e=std::io::Error::last_os_error().raw_os_error();require(e==Some(libc::EWOULDBLOCK)||e==Some(libc::EINTR),"LOCK_FAILED")?;
            require(Instant::now()<end,"LOCK_TIMEOUT")?;std::thread::sleep(Duration::from_millis(2));
        }
        let held=Exclusive{root:self,file:Some(file),parent:None};held.validate()?;Ok(held)
    }
}
/// Constructed only by later fixed host/control code after acquiring the
/// global source-slot -> publication -> replay -> native -> journal capability.
/// It represents continuous exclusive parent custody, not a caller assertion.
pub(crate) struct ParentHold {
    pub root:Identity,pub execution_scope:ExecutionScope,pub namespace_epoch:u64,pub alias_exclusion_binding:Binding,
    pub ancestor_inventory_binding:Binding,pub acl_policy_binding:Binding,pub global_order_binding:Binding,
}
impl Root {
    pub(crate) fn under_parent<'a>(&'a self,parent:&'a ParentHold)->Result<Exclusive<'a>> {
        self.validate()?;
        require(self.selection.domain==Domain::Actual&&parent.execution_scope==self.selection.execution_scope&&parent.root==*self.identity()&&
            parent.namespace_epoch==self.selection.namespace_epoch&&
            parent.alias_exclusion_binding==self.selection.alias_exclusion_binding&&parent.ancestor_inventory_binding==self.selection.ancestor_inventory_binding&&parent.acl_policy_binding==self.selection.acl_policy_binding&&parent.global_order_binding.valid(),"PARENT_CUSTODY")?;
        Ok(Exclusive{root:self,file:None,parent:Some(parent)})
    }
}
pub struct Exclusive<'a> {root:&'a Root,file:Option<File>,parent:Option<&'a ParentHold>}
impl Exclusive<'_> {
    pub fn root(&self)->&Root {self.root}
    pub fn validate(&self)->Result<()> {
        self.root.validate()?;
        if let Some(file)=&self.file {require(Identity::observe(file)?==*self.root.identity(),"LOCK_ATTACHMENT")?;}
        else {let p=self.parent.ok_or(Error("PARENT_CUSTODY"))?;require(p.execution_scope==self.root.selection.execution_scope&&p.root==*self.root.identity()&&p.namespace_epoch==self.root.selection.namespace_epoch,"PARENT_CUSTODY")?;}
        Ok(())
    }
    pub(crate) fn directory(&self)->&File {self.root.directory()}
}
impl Drop for Exclusive<'_> {fn drop(&mut self){if let Some(file)=&self.file {unsafe{libc::flock(file.as_raw_fd(),libc::LOCK_UN);}}}}
