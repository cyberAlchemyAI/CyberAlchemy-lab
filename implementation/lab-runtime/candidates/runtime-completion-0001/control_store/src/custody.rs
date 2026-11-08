//! Held descriptors and fixed global lock order. The selected ancestor/mount
//! custody is a host invariant; no pathname is promoted to authority here.
use super::{fail, Error, Result};
use serde::{Deserialize, Serialize};
use std::{ffi::CString, fs::{File, OpenOptions}, io::{Read, Write}, os::{fd::{AsRawFd, FromRawFd}, unix::fs::{MetadataExt, OpenOptionsExt}}, path::Path, time::{Duration, Instant}};

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Identity { pub device: u64, pub inode: u64, pub uid: u32 }
impl Identity { pub fn of(file: &File) -> Result<Self> { let m=file.metadata()?; Ok(Self { device:m.dev(), inode:m.ino(), uid:m.uid() }) } }
fn cname(name: &str) -> Result<CString> {
    if name.is_empty() || name.contains('/') || name == "." || name == ".." { return fail("invalid child name"); }
    CString::new(name).map_err(|_| Error("nul child name".into()))
}
pub(crate) fn open_at(parent: &File, name: &str, flags: i32) -> Result<File> {
    let name=cname(name)?;
    let fd=unsafe { libc::openat(parent.as_raw_fd(),name.as_ptr(),flags|libc::O_CLOEXEC|libc::O_NOFOLLOW|libc::O_NONBLOCK,0o600) };
    if fd<0 { return Err(std::io::Error::last_os_error().into()); }
    Ok(unsafe { File::from_raw_fd(fd) })
}
fn directory_at(parent: &File,name:&str)->Result<File> { open_at(parent,name,libc::O_RDONLY|libc::O_DIRECTORY) }
fn mkdir_at(parent:&File,name:&str)->Result<File> {
    let c=cname(name)?;
    if unsafe { libc::mkdirat(parent.as_raw_fd(),c.as_ptr(),0o700) } != 0 { return Err(std::io::Error::last_os_error().into()); }
    let f=directory_at(parent,name)?; f.sync_all()?; parent.sync_all()?; Ok(f)
}
pub(crate) fn regular(file:&File)->Result<()> {
    let m=file.metadata()?;
    if !m.is_file() || m.nlink()!=1 || m.mode()&0o077 !=0 || m.uid()!=unsafe{libc::geteuid()} { return fail("control member custody/type"); }
    Ok(())
}
pub(crate) fn read(file:&mut File,maximum:usize)->Result<Vec<u8>> {
    regular(file)?;
    let before=file.metadata()?;
    if before.len()>maximum as u64 { return fail("control member bound"); }
    let mut raw=Vec::new(); file.take(maximum as u64+1).read_to_end(&mut raw)?;
    let after=file.metadata()?;
    if raw.len()>maximum || before.len()!=after.len() || before.mtime_nsec()!=after.mtime_nsec() || before.ctime_nsec()!=after.ctime_nsec() || before.mtime()!=after.mtime() || before.ctime()!=after.ctime() { return fail("control member changed/bound"); }
    Ok(raw)
}
pub(crate) fn create(parent:&File,name:&str,raw:&[u8])->Result<()> {
    let mut file=open_at(parent,name,libc::O_WRONLY|libc::O_CREAT|libc::O_EXCL)?;
    regular(&file)?; boundary(1)?; file.write_all(raw)?; boundary(2)?;
    file.sync_all()?; boundary(3)?; parent.sync_all()?; boundary(4)?; Ok(())
}
// Test-only fault injection after actual syscalls. No runtime configuration,
// dynamic hook, environment selection or failure switch exists in production.
#[cfg(test)]
thread_local! { pub(crate) static FAIL_BOUNDARY:std::cell::Cell<u8>=const {std::cell::Cell::new(0)}; }
#[inline]
fn boundary(_phase:u8)->Result<()> {
    #[cfg(test)]
    if FAIL_BOUNDARY.with(|v|v.get()==_phase) { return fail("injected syscall-boundary failure"); }
    Ok(())
}

pub struct Root {
    parent:File, name:String, pub(crate) directory:File, pub(crate) records:File,
    locks:File, identity:Identity, records_identity:Identity, locks_identity:Identity,
}
impl Root {
    /// Only inert fixtures may create a domain. Actual host bootstrap is a
    /// separate gated protocol, never an automatic fallback from open failure.
    pub fn create_fixture(parent:&Path,name:&str)->Result<Self> {
        let parent=OpenOptions::new().read(true).custom_flags(libc::O_DIRECTORY|libc::O_NOFOLLOW|libc::O_CLOEXEC).open(parent)?;
        let directory=mkdir_at(&parent,name)?;
        let records=mkdir_at(&directory,"records")?;
        let locks=mkdir_at(&directory,"locks")?;
        for name in LOCK_NAMES { create(&locks,name,b"fixed domain lock v1\n")?; }
        directory.sync_all()?; parent.sync_all()?;
        Self::from_parts(parent,name.into(),directory,records,locks)
    }
    pub fn open(parent:&Path,name:&str,expected:&Identity)->Result<Self> {
        let parent=OpenOptions::new().read(true).custom_flags(libc::O_DIRECTORY|libc::O_NOFOLLOW|libc::O_CLOEXEC).open(parent)?;
        let directory=directory_at(&parent,name)?;
        let records=directory_at(&directory,"records")?; let locks=directory_at(&directory,"locks")?;
        let root=Self::from_parts(parent,name.into(),directory,records,locks)?;
        if &root.identity!=expected { return fail("selected control root identity"); }
        root.validate()?; Ok(root)
    }
    fn from_parts(parent:File,name:String,directory:File,records:File,locks:File)->Result<Self> {
        for f in [&directory,&records,&locks] { let m=f.metadata()?; if !m.is_dir() || m.mode()&0o077!=0 || m.uid()!=unsafe{libc::geteuid()} { return fail("control directory custody"); } }
        let identity=Identity::of(&directory)?; let records_identity=Identity::of(&records)?; let locks_identity=Identity::of(&locks)?;
        Ok(Self{parent,name,directory,records,locks,identity,records_identity,locks_identity})
    }
    pub fn identity(&self)->Identity { self.identity.clone() }
    pub(crate) fn layout(&self)->Result<Vec<Identity>> {
        let mut value=vec![self.identity.clone(),self.records_identity.clone(),self.locks_identity.clone()];
        for name in LOCK_NAMES { let f=open_at(&self.locks,name,libc::O_RDONLY)?; regular(&f)?; value.push(Identity::of(&f)?); }
        Ok(value)
    }
    pub fn validate(&self)->Result<()> {
        if Identity::of(&directory_at(&self.parent,&self.name)?)?!=self.identity || Identity::of(&directory_at(&self.directory,"records")?)?!=self.records_identity || Identity::of(&directory_at(&self.directory,"locks")?)?!=self.locks_identity { return fail("control directory attachment changed"); }
        for f in [&self.directory,&self.records,&self.locks] { let m=f.metadata()?; if m.mode()&0o077!=0 || m.uid()!=unsafe{libc::geteuid()} { return fail("control directory custody changed"); } }
        Ok(())
    }
    pub(crate) fn names(&self,max:usize)->Result<Vec<String>> {
        let mut names=Vec::new();
        for row in std::fs::read_dir(format!("/proc/self/fd/{}",self.records.as_raw_fd()))? {
            if names.len()>=max { return fail("record inventory limit"); }
            names.push(row?.file_name().into_string().map_err(|_|Error("record name encoding".into()))?);
        }
        names.sort(); Ok(names)
    }
    pub fn acquire(&self, through:Rank, timeout:Duration)->Result<Locks<'_>> {
        if timeout.is_zero() || timeout>Duration::from_secs(30) { return fail("lock wait bound"); }
        self.validate()?; let deadline=Instant::now()+timeout; let mut held=Locks{root:self,files:Vec::new()};
        for i in 0..=through as usize { held.acquire_next(i,deadline)?; }
        Ok(held)
    }
}
const LOCK_NAMES:[&str;5]=["00-source-slot","01-publication","02-replay","03-native","04-journal"];
#[derive(Clone,Copy,Debug,PartialEq,Eq,PartialOrd,Ord)]
#[repr(usize)]
pub enum Rank { SourceSlot=0, Publication=1, Replay=2, Native=3, Journal=4 }
pub struct Locks<'a> { root:&'a Root,files:Vec<File> }
impl<'a> Locks<'a> {
    fn acquire_next(&mut self,i:usize,deadline:Instant)->Result<()> {
        if i!=self.files.len() || i>=LOCK_NAMES.len() { return fail("lock inversion/reacquisition"); }
        let f=open_at(&self.root.locks,LOCK_NAMES[i],libc::O_RDWR)?; regular(&f)?;
        loop {
            if unsafe {libc::flock(f.as_raw_fd(),libc::LOCK_EX|libc::LOCK_NB)}==0 { break; }
            let e=std::io::Error::last_os_error();
            if !matches!(e.raw_os_error(),Some(libc::EWOULDBLOCK)|Some(libc::EINTR)) { return Err(e.into()); }
            if Instant::now()>=deadline { return fail("lock bounded contention"); }
            std::thread::sleep(Duration::from_millis(2));
        }
        self.files.push(f); self.validate()?; Ok(())
    }
    pub fn extend(&mut self,rank:Rank,timeout:Duration)->Result<()> {
        if rank as usize!=self.files.len() || timeout.is_zero() || timeout>Duration::from_secs(30) { return fail("lock inversion/reacquisition/wait"); }
        self.acquire_next(rank as usize,Instant::now()+timeout)
    }
    pub fn borrow(&self)->Result<Held<'_>> { self.validate()?; Ok(Held{locks:self}) }
    fn validate(&self)->Result<()> {
        self.root.validate()?;
        for (i,f) in self.files.iter().enumerate() { regular(f)?; if Identity::of(f)?!=Identity::of(&open_at(&self.root.locks,LOCK_NAMES[i],libc::O_RDONLY)?)? { return fail("lock attachment changed"); } }
        Ok(())
    }
}
impl Drop for Locks<'_> { fn drop(&mut self) { for file in self.files.iter().rev() { unsafe {libc::flock(file.as_raw_fd(),libc::LOCK_UN);} } } }
pub struct Held<'a> { locks:&'a Locks<'a> }
impl Held<'_> {
    pub fn nested(&self)->Result<Held<'_>> { self.locks.validate()?; Ok(Held{locks:self.locks}) }
    pub fn rank(&self)->Rank { [Rank::SourceSlot,Rank::Publication,Rank::Replay,Rank::Native,Rank::Journal][self.locks.files.len()-1] }
    pub(crate) fn require(&self,root:&Root)->Result<()> {
        self.locks.validate()?;
        if self.rank()!=Rank::Journal || self.locks.root.identity!=root.identity { return fail("wrong/insufficient held control capability"); }
        root.validate()
    }
}
