//! clone3-only actual dispatch. All memory/strings/FD duplication is prepared in the parent.
use super::{need,Error,Result,containment::{Root,Attempt,Identity,identity,Limits,now},state::{Domain,Observation,Reason,Terminal}};
use lab_control_store::{codec,ledger::{BorrowedOperation,ByteBinding}};
use std::{ffi::CString,fs::File,io::Read,os::{fd::{AsRawFd,FromRawFd,RawFd},unix::fs::MetadataExt},time::{Duration,Instant}};

pub(crate) fn lifted(file:&File)->Result<File>{let fd=unsafe{libc::fcntl(file.as_raw_fd(),libc::F_DUPFD_CLOEXEC,10)};need(fd>=10,"DUP_DESCRIPTOR")?;Ok(unsafe{File::from_raw_fd(fd)})}
/// Fixed loader opens selected original ELF and dedicated regular stdio files; no shell,
/// PATH lookup, script interpreter fallback, or inherited ambient environment.
type Stamp=(u64,u64,u64,u32,u32,u32,u64,i64,i64,i64,i64);
fn stamp(m:&std::fs::Metadata)->Stamp{(m.dev(),m.ino(),m.len(),m.uid(),m.gid(),m.mode(),m.nlink(),m.mtime(),m.mtime_nsec(),m.ctime(),m.ctime_nsec())}
#[derive(Clone,Debug,PartialEq,Eq,serde::Serialize)]
pub(crate) struct StdioSelection{identity:Identity,stamp:Stamp,flags:i32,offset:u64,input_sha256:Option<String>}
/// Exact initial owned stream contract, shared by fixed loader selection and preclone verification.
pub(crate) fn stdio_selection(io:[&File;3])->Result<Vec<StdioSelection>>{
 use std::os::unix::fs::FileExt;
 let mut rows=Vec::new();let mut ids=std::collections::BTreeSet::new();
 for(i,f)in io.iter().enumerate(){let m=f.metadata()?;let id=identity(f)?;let flags=unsafe{libc::fcntl(f.as_raw_fd(),libc::F_GETFL)};let offset=unsafe{libc::lseek(f.as_raw_fd(),0,libc::SEEK_CUR)};
  need(m.is_file()&&m.nlink()==1&&m.uid()==unsafe{libc::geteuid()}&&m.mode()&0o077==0&&flags>=0&&(flags&libc::O_ACCMODE)==if i==0{libc::O_RDONLY}else{libc::O_WRONLY},"STDIO_SELECTION")?;
  need(ids.insert((m.dev(),m.ino())),"STDIO_ALIAS")?;need(offset==0&&flags&libc::O_APPEND==0,"STDIO_INITIAL_POSITION")?;
  need(if i==0{m.len()<=64*1024*1024}else{m.len()==0},"STDIO_INITIAL_LENGTH")?;
  let input_sha256=if i==0{let mut raw=vec![0;m.len() as usize];f.read_exact_at(&mut raw,0)?;Some(codec::digest(&raw))}else{None};
  need(stamp(&f.metadata()?)==stamp(&m)&&identity(f)?==id,"STDIO_SELECTION_DRIFT")?;
  rows.push(StdioSelection{identity:id,stamp:stamp(&m),flags,offset:0,input_sha256});
 }Ok(rows)
}
/// Equal per-stream slices enforce one aggregate output ceiling, including odd totals.
pub(crate) fn output_slice(total:u64)->Result<u64>{need((2..=64*1024*1024).contains(&total),"OUTPUT_AGGREGATE_BOUND")?;Ok(total/2)}
pub(crate) struct Prepared{program:File,program_binding:ByteBinding,program_stamp:Stamp,cwd:File,cwd_identity:Identity,stdio:[File;3],stdio_selection:Vec<StdioSelection>,argv:Vec<CString>,env:Vec<CString>,argv_ptr:Vec<*const libc::c_char>,env_ptr:Vec<*const libc::c_char>,pub execution:ByteBinding}
impl Prepared{
 pub(crate) fn new(program:&File,binding:&ByteBinding,cwd:&File,cwd_binding:&ByteBinding,stdio:[&File;3],argv:&[String],env:&[String],expected_plan:&ByteBinding)->Result<Self>{
  need(binding.valid()&&binding.kind=="execution"&&binding.size_bytes<=64*1024*1024,"EXECUTION_BINDING")?;
  let mut p=program.try_clone()?;let before=p.metadata()?;need(before.is_file()&&before.len()==binding.size_bytes&&before.mode()&0o022==0,"EXECUTABLE_TYPE")?;
  use std::io::{Seek,SeekFrom};p.seek(SeekFrom::Start(0))?;let mut raw=Vec::new();(&mut p).take(64*1024*1024+1).read_to_end(&mut raw)?;let after=p.metadata()?;
  need(raw.starts_with(b"\x7fELF")&&codec::digest(&raw)==binding.sha256&&stamp(&before)==stamp(&after),"EXECUTABLE_BYTES")?;
  need(!argv.is_empty()&&!argv[0].is_empty()&&argv.len()<=64&&env.len()<=64,"EXEC_VECTOR_COUNT")?;let bytes:usize=argv.iter().chain(env).map(|x|x.len()+1).sum();need(bytes<=32768,"EXEC_VECTOR_BYTES")?;
  let cwd_identity=identity(cwd)?;need(cwd.metadata()?.is_dir()&&cwd_identity.mode&0o022==0&&cwd_binding.valid(),"WORKING_DIRECTORY_SELECTION")?;
  let stdio_snapshot=stdio_selection(stdio)?;
  let plan_bytes=codec::encode(&serde_json::json!({"schema_version":"lab-supervisor-exec-selection/v1","program":binding,"working_directory_binding":cwd_binding,"working_directory_identity":cwd_identity,"argv":argv,"environment":env,"stdio_selection":stdio_snapshot}))?;
  need(expected_plan.valid()&&expected_plan.kind=="execution"&&expected_plan.size_bytes==plan_bytes.len() as u64&&expected_plan.sha256==codec::digest(&plan_bytes),"INDEPENDENT_EXEC_SELECTION")?;
  let argv:Vec<_>=argv.iter().map(|x|CString::new(x.as_str()).map_err(|_|Error("EXEC_VECTOR_NUL"))).collect::<Result<_>>()?;
  let mut keys=std::collections::BTreeSet::new();for s in env{let (key,_)=s.split_once('=').ok_or(Error("EXEC_ENV"))?;need(!key.is_empty()&&key.bytes().all(|c|c.is_ascii_alphanumeric()||c==b'_')&&keys.insert(key),"EXEC_ENV")?;}
  let env:Vec<_>=env.iter().map(|x|CString::new(x.as_str()).map_err(|_|Error("EXEC_VECTOR_NUL"))).collect::<Result<_>>()?;
  let mut argv_ptr:Vec<_>=argv.iter().map(|x|x.as_ptr()).collect();argv_ptr.push(std::ptr::null());let mut env_ptr:Vec<_>=env.iter().map(|x|x.as_ptr()).collect();env_ptr.push(std::ptr::null());
  Ok(Self{program:lifted(program)?,program_binding:binding.clone(),program_stamp:stamp(&after),cwd:lifted(cwd)?,cwd_identity,stdio:[lifted(stdio[0])?,lifted(stdio[1])?,lifted(stdio[2])?],stdio_selection:stdio_snapshot,argv,env,argv_ptr,env_ptr,execution:expected_plan.clone()})
 }
 pub(crate) fn revalidate(&self)->Result<()>{
  need(stdio_selection([&self.stdio[0],&self.stdio[1],&self.stdio[2]])?==self.stdio_selection,"PREPARED_STDIO_CHANGED")?;
  need(identity(&self.cwd)?==self.cwd_identity,"WORKING_DIRECTORY_CHANGED")?;
  use std::io::{Seek,SeekFrom};let mut f=self.program.try_clone()?;let before=f.metadata()?;need(stamp(&before)==self.program_stamp,"PREPARED_EXECUTABLE_CHANGED")?;f.seek(SeekFrom::Start(0))?;let mut raw=Vec::new();(&mut f).take(64*1024*1024+1).read_to_end(&mut raw)?;need(raw.len()==self.program_binding.size_bytes as usize&&codec::digest(&raw)==self.program_binding.sha256&&stamp(&f.metadata()?)==self.program_stamp,"PREPARED_EXECUTABLE_BYTES")?;Ok(())
 }
}
#[repr(C)]#[derive(Default)]pub(crate) struct CloneArgs{pub flags:u64,pub pidfd:u64,pub child_tid:u64,pub parent_tid:u64,pub exit_signal:u64,pub stack:u64,pub stack_size:u64,pub tls:u64,pub set_tid:u64,pub set_tid_size:u64,pub cgroup:u64}
pub(crate) fn clone_args(group:RawFd,pidfd:&mut i32)->Result<CloneArgs>{need(group>=0,"CGROUP_FD")?;Ok(CloneArgs{flags:0x200000000|0x100000000|0x00001000,pidfd:pidfd as *mut i32 as u64,exit_signal:libc::SIGCHLD as u64,cgroup:group as u64,..CloneArgs::default()})}
/// Async-signal-safe syscalls only. Inputs are duplicated >=10 before clone, so the
/// fixed 0..4 remapping cannot clobber any source. fd3 ELF and fd4 setup-error pipe
/// are CLOEXEC; all descriptors >=5 close before credentials or worker code.
pub(crate) unsafe fn install_descriptors(exec:i32,io:[i32;3],error:i32)->bool{
 for(i,fd)in io.iter().enumerate(){if libc::dup3(*fd,i as i32,0)<0{return false}}
 if libc::dup3(exec,3,libc::O_CLOEXEC)<0||libc::dup3(error,4,libc::O_CLOEXEC)<0{return false}
 libc::syscall(libc::SYS_close_range,5u32,u32::MAX,0u32)==0
}
unsafe fn child_fail(code:u32)->!{let _=libc::write(4,&code as *const u32 as *const libc::c_void,4);libc::_exit(126)}
#[repr(C)]struct CapHeader{version:u32,pid:i32}
#[repr(C)]#[derive(Default)]struct CapData{effective:u32,permitted:u32,inheritable:u32}
unsafe fn child(plan:&Prepared,error:i32,uid:u32,gid:u32,output:u64)->!{
 // No allocation, formatting, Drop, panic, user callbacks or mutexes in this branch.
 if libc::fchdir(plan.cwd.as_raw_fd())!=0{libc::_exit(126)}
 if !install_descriptors(plan.program.as_raw_fd(),[plan.stdio[0].as_raw_fd(),plan.stdio[1].as_raw_fd(),plan.stdio[2].as_raw_fd()],error){libc::_exit(126)}
 let limit=libc::rlimit{rlim_cur:output,rlim_max:output};if libc::setrlimit(libc::RLIMIT_FSIZE,&limit)!=0{child_fail(2)}
 if libc::prctl(libc::PR_SET_NO_NEW_PRIVS,1,0,0,0)!=0||libc::prctl(libc::PR_SET_KEEPCAPS,0,0,0,0)!=0||libc::prctl(libc::PR_CAP_AMBIENT,libc::PR_CAP_AMBIENT_CLEAR_ALL,0,0,0)!=0{child_fail(3)}
 if libc::syscall(libc::SYS_setgroups,0,std::ptr::null::<libc::gid_t>())!=0||libc::syscall(libc::SYS_setresgid,gid,gid,gid)!=0||libc::syscall(libc::SYS_setresuid,uid,uid,uid)!=0{child_fail(4)}
 let header=CapHeader{version:0x20080522,pid:0};let data=[CapData::default(),CapData::default()];
 if libc::syscall(libc::SYS_capset,&header,data.as_ptr())!=0{child_fail(5)}
 let mut got=[CapData::default(),CapData::default()];
 if libc::syscall(libc::SYS_capget,&header,got.as_mut_ptr())!=0||got.iter().any(|c|c.effective!=0||c.permitted!=0||c.inheritable!=0)||libc::getuid()!=uid||libc::geteuid()!=uid||libc::getgid()!=gid||libc::getegid()!=gid||libc::getgroups(0,std::ptr::null_mut())!=0||libc::prctl(libc::PR_GET_NO_NEW_PRIVS,0,0,0,0)!=1{child_fail(6)}
 for sig in 1..=64{if sig==libc::SIGKILL||sig==libc::SIGSTOP{continue}let mut a:libc::sigaction=std::mem::zeroed();a.sa_sigaction=libc::SIG_DFL;libc::sigemptyset(&mut a.sa_mask);let _=libc::sigaction(sig,&a,std::ptr::null_mut());}
 let mut mask:libc::sigset_t=std::mem::zeroed();libc::sigemptyset(&mut mask);if libc::sigprocmask(libc::SIG_SETMASK,&mask,std::ptr::null_mut())!=0{child_fail(7)}
 let ready:u32=0x52454144;if libc::write(4,&ready as *const u32 as *const libc::c_void,4)!=4{child_fail(9)}
 libc::syscall(libc::SYS_execveat,3,c"".as_ptr(),plan.argv_ptr.as_ptr(),plan.env_ptr.as_ptr(),libc::AT_EMPTY_PATH);child_fail(8)
}
fn reap(pidfd:&File)->Result<Option<(Option<i32>,Option<i32>)>>{let mut s:libc::siginfo_t=unsafe{std::mem::zeroed()};let rc=unsafe{libc::waitid(libc::P_PIDFD,pidfd.as_raw_fd() as u32,&mut s,libc::WEXITED|libc::WNOHANG)};need(rc==0,"PIDFD_REAP")?;if unsafe{s.si_pid()}==0{return Ok(None)};let code=unsafe{s.si_status()};Ok(Some(if s.si_code==libc::CLD_EXITED{(Some(code),None)}else{(None,Some(code))}))}
use super::records::StartOriginal as StartRecord;
pub(crate) struct PendingStart<'a>{attempt:Attempt<'a>,record:StartRecord,raw:Vec<u8>}
impl<'a> PendingStart<'a>{
 #[cfg(test)]pub(crate) fn fixture(root:&'a Root,record:StartRecord)->Result<Self>{let attempt=root.fixture_attempt(&record)?;let raw=codec::encode(&record)?;Ok(Self{attempt,record,raw})}
 pub(crate) fn original_bytes(&self)->&[u8]{&self.raw}pub(crate) fn root(&self)->&Root{self.attempt.root()}}
use super::adapters::StartAcknowledgment;
pub(crate) fn prepare<'a>(root:&'a Root,journal:&super::attempt_journal::AttemptJournal<'_>,op:&BorrowedOperation<'_>,attempt_id:&str,plan:&Prepared,limits:Limits)->Result<PendingStart<'a>>{
 journal.preflight_admission(root,op.operation())?;plan.revalidate()?;let attempt=root.create(op,attempt_id,limits)?;let(dispatch,cleanup)=root.deadlines();
 let record=StartRecord{schema_version:"lab-contained-attempt-start/v1".into(),operation:op.operation().clone(),attempt_id:attempt_id.into(),containment_binding:root.root_binding().clone(),group_identity:attempt.id.clone(),execution_binding:plan.execution.clone(),historical_selection:root.history_binding().clone(),created_utc_ns:now()?,dispatch_until_utc_ns:dispatch,cleanup_until_utc_ns:cleanup,limits};
 let raw=codec::encode(&record)?;need(raw.len()<=65536,"START_RECORD_BOUND")?;Ok(PendingStart{attempt,record,raw})
}
/// Consumes one prepared group and exact durable-start capability before clone. Death
/// before acknowledgement leaves a retained quarantined group, never guessed ownership.
/// Restart cleanup must load and verify the original acknowledged start independently.
/// Inaccessible delegation, clone3, pidfd or custody refuses, with no launch/migrate fallback.
pub(crate) fn run(pending:PendingStart<'_>,ack:StartAcknowledgment,journal:&super::attempt_journal::AttemptJournal<'_>,op:&BorrowedOperation<'_>,plan:&Prepared)->Result<Observation>{
 need(pending.root().domain()==Domain::Actual,"FIXTURE_CANNOT_DISPATCH")?;ack.verify_original(&pending.raw)?;journal.validate_launch(ack.proof(),pending.root())?;need(pending.record.operation==*op.operation()&&pending.record.execution_binding==plan.execution,"START_DISPATCH_SCOPE")?;
 let PendingStart{attempt:a,record,..}=pending;let root=a.root();let attempt_id=record.attempt_id.as_str();let limits=record.limits;
 limits.validate()?;op.nested()?;
 // The selected fixed supervisor must own its wait policy. Do not change global
 // subreaper state or reap unrelated children in this library.
 let mut sig:libc::sigaction=unsafe{std::mem::zeroed()};need(unsafe{libc::sigaction(libc::SIGCHLD,std::ptr::null(),&mut sig)}==0&&sig.sa_sigaction!=libc::SIG_IGN&&sig.sa_flags&libc::SA_NOCLDWAIT==0,"CHILD_WAIT_POLICY")?;
 let mut pipe=[-1;2];need(unsafe{libc::pipe2(pipe.as_mut_ptr(),libc::O_CLOEXEC|libc::O_NONBLOCK)}==0,"SETUP_PIPE")?;
 let reader=unsafe{File::from_raw_fd(pipe[0])};let writer_source=unsafe{File::from_raw_fd(pipe[1])};let writer=lifted(&writer_source)?;drop(writer_source);
 let mut pidfd=-1;let args=clone_args(a.group.as_raw_fd(),&mut pidfd)?;let start=now()?;let instant=Instant::now();let(worker_uid,worker_gid)=root.worker();
 plan.revalidate()?;a.dispatch_currentness()?;op.nested()?;journal.validate_launch(ack.proof(),root)?;
 let mut all:libc::sigset_t=unsafe{std::mem::zeroed()};let mut previous:libc::sigset_t=unsafe{std::mem::zeroed()};unsafe{libc::sigfillset(&mut all)};need(unsafe{libc::pthread_sigmask(libc::SIG_SETMASK,&all,&mut previous)}==0,"PARENT_SIGNAL_MASK")?;
 let pid=unsafe{libc::syscall(libc::SYS_clone3,&args,std::mem::size_of::<CloneArgs>())};if pid==0{unsafe{child(plan,writer.as_raw_fd(),worker_uid,worker_gid,limits.output_bytes/2)}}
 let parent_mask_restored=unsafe{libc::pthread_sigmask(libc::SIG_SETMASK,&previous,std::ptr::null_mut())}==0;drop(writer);
 need(pid>0&&pidfd>=0,"CLONE3_INTO_CGROUP_PIDFD_REQUIRED")?;let pidfd=unsafe{File::from_raw_fd(pidfd)};
 let mut t=Terminal{schema_version:"lab-contained-attempt-terminal/v1",domain:Domain::Actual,operation:op.operation().clone(),attempt_id:attempt_id.into(),containment_binding:root.root_binding().clone(),actual_group_identity:a.id.clone(),execution_binding:plan.execution.clone(),original_start_binding:ack.proof().binding().clone(),historical_selection:root.history_binding().clone(),start_utc_ns:start,end_utc_ns:None,elapsed_ns:0,child_pid:pid as u32,pid_start_ticks:std::fs::read(format!("/proc/{pid}/stat")).ok().and_then(|v|start_ticks(&v).ok()),reason:Reason::Exited,exit_code:None,signal:None,primary_error:None,cleanup_errors:vec![],direct_child_reaped:false,subtree_empty:false,inherited_descriptors_closed:false,workload_started:None,historical_complete:true};
 if !parent_mask_restored{t.primary_error=Some("PARENT_SIGNAL_RESTORE");t.cleanup_errors.push("PARENT_SIGNAL_RESTORE");}
 loop{
  if t.primary_error.is_some(){break}
  if op.nested().is_err(){t.reason=Reason::ContainmentChanged;t.primary_error=Some("CONTROL_CUSTODY_CHANGED");break}
  if let Err(e)=a.dispatch_currentness(){t.reason=Reason::ContainmentChanged;t.primary_error=Some(e.0);break}
  match reap(&pidfd){Ok(Some((code,sig)))=>{t.exit_code=code;t.signal=sig;t.direct_child_reaped=true;break},Ok(None)=>{},Err(e)=>{t.reason=Reason::ObservationFailed;t.primary_error=Some(e.0);break}}
  if instant.elapsed()>=Duration::from_millis(limits.runtime_ms){t.reason=Reason::Timeout;t.primary_error=Some("RUNTIME_TIMEOUT");break}
  std::thread::sleep(Duration::from_millis(5));
 }
 // Always clean the entire exact subtree, including setsid/reparented descendants.
 if let Err(e)=a.kill_owned(){t.cleanup_errors.push(e.0)}
 let end=Instant::now();while end.elapsed()<Duration::from_millis(limits.cleanup_ms){
  if !t.direct_child_reaped{match reap(&pidfd){Ok(Some((code,sig)))=>{t.exit_code=code;t.signal=sig;t.direct_child_reaped=true},Ok(None)=>{},Err(e)=>{t.cleanup_errors.push(e.0);break}}}
  match a.populated(){Ok(false)=>t.subtree_empty=true,Ok(true)=>t.subtree_empty=false,Err(e)=>{t.cleanup_errors.push(e.0);break}}
  if t.direct_child_reaped&&t.subtree_empty{break}std::thread::sleep(Duration::from_millis(5));
 }
 if !t.direct_child_reaped||!t.subtree_empty{t.cleanup_errors.push("CONTAINMENT_NOT_PROVEN_EMPTY_REAPED")}
 let mut message=[0u8;9];let n=unsafe{libc::read(reader.as_raw_fd(),message.as_mut_ptr() as *mut libc::c_void,9)};
 // Exact setup marker proves trusted closure completed. Missing/partial marker,
 // a setup error or appended exec error stays uncertain, including a pre-exec kill.
 if setup_complete(&message,n){t.inherited_descriptors_closed=true}else{t.reason=Reason::ChildSetupFailed;if t.primary_error.is_none(){t.primary_error=Some("CHILD_SETUP_OR_EXEC_FAILED")}else{t.cleanup_errors.push("CHILD_SETUP_OR_EXEC_FAILED")}}
 let mut output_total=0u64;for i in 1..=2{match plan.stdio[i].metadata(){Ok(m)=>{let selected=&plan.stdio_selection[i];if identity(&plan.stdio[i]).ok().as_ref()!=Some(&selected.identity)||m.nlink()!=1||m.len()>limits.output_bytes/2{t.cleanup_errors.push("OUTPUT_CUSTODY_OR_BOUND")};output_total=output_total.saturating_add(m.len());},Err(_)=>t.cleanup_errors.push("OUTPUT_OBSERVATION_FAILED")}}
 if output_total>limits.output_bytes{t.cleanup_errors.push("OUTPUT_AGGREGATE_BOUND")}
 t.workload_started=if t.inherited_descriptors_closed&&t.exit_code.is_some()&&t.exit_code!=Some(126){Some(true)}else if n>=8{Some(false)}else{None};
 match now(){Ok(end) if end>=start=>t.end_utc_ns=Some(end),_=>{if t.primary_error.is_none(){t.primary_error=Some("END_CLOCK_UNAVAILABLE")}else{t.cleanup_errors.push("END_CLOCK_UNAVAILABLE")}}}
 t.elapsed_ns=instant.elapsed().as_nanos().min(i64::MAX as u128) as u64;
 let unreaped_pidfd=if t.direct_child_reaped{None}else{Some(pidfd)};Ok(Observation{terminal:t,unreaped_pidfd})
}

pub(crate) fn setup_complete(message:&[u8],n:isize)->bool{n==4&&message.len()>=4&&message[..4]==0x52454144u32.to_ne_bytes()}

pub(crate) fn start_ticks(raw:&[u8])->Result<u64>{need(raw.len()<=8192,"PROC_STAT_BOUND")?;let s=std::str::from_utf8(raw).map_err(|_|Error("PROC_STAT"))?;let end=s.rfind(')').ok_or(Error("PROC_STAT"))?;let fields:Vec<_>=s[end+1..].split_whitespace().collect();need(fields.len()>=20,"PROC_STAT")?;let n=fields[19].parse().map_err(|_|Error("PROC_STAT"))?;need(n>0,"PROC_STAT_START")?;Ok(n)}
