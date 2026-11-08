use lab_control_store::{codec,custody::{Root,Rank},ledger::*,Result};
use std::{fs::{self,File,OpenOptions},io::Write,os::unix::fs::{PermissionsExt,OpenOptionsExt,symlink},path::{Path,PathBuf},sync::atomic::{AtomicU64,Ordering},time::{Duration,Instant}};
static NEXT:AtomicU64=AtomicU64::new(0);
const WAIT:Duration=Duration::from_millis(100);
fn h()->String { "a".repeat(64) }
fn b()->ByteBinding {ByteBinding{kind:"evidence".into(),root_id:"fixture".into(),relative_path:"selected/proof.json".into(),sha256:h(),size_bytes:10}}
struct Temp(PathBuf);
impl Temp {
 fn new()->Self { let parent=PathBuf::from(std::env::var_os("TMPDIR").expect("selected owned TMPDIR")); let path=parent.join(format!("control-fixture-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::Relaxed))); fs::create_dir(&path).unwrap();fs::set_permissions(&path,fs::Permissions::from_mode(0o700)).unwrap();Self(path) }
}
impl Drop for Temp { fn drop(&mut self){fs::remove_dir_all(&self.0).unwrap();} }
fn limits()->Limits { Limits{max_record_bytes:4096,max_records:128,max_total_bytes:1024*1024,reserved_records:6} }
fn writer()->WriterFence { WriterFence{instance:"host-fixture".into(),epoch:1} }
// A separately retained fixture-only host CAS: it does not read ledger data.
// Each witness file is outside the domain root and is durable before returning.
struct Witness { path:PathBuf,current:HostConfirmation }
impl Witness {
 fn new(parent:&Path,initial:HostConfirmation)->Self { let path=parent.join("independent-fixture-witness");fs::create_dir(&path).unwrap();let mut w=Self{path,current:initial};w.persist().unwrap();w }
 fn persist(&mut self)->Result<()> { let raw=codec::encode(&self.current)?;let mut f=OpenOptions::new().write(true).create_new(true).mode(0o600).open(self.path.join(format!("{}.json",self.current.head.sequence)))?;f.write_all(&raw)?;f.sync_all()?;File::open(&self.path)?.sync_all()?;Ok(()) }
 fn advance(&mut self,request:&HostConfirmation)->Result<HostConfirmation> {
  if request.predecessor!=self.current.head||request.head.sequence!=self.current.head.sequence+1||request.authority_domain!=self.current.authority_domain||request.root!=self.current.root||request.header_sha256!=self.current.header_sha256||request.writer!=self.current.writer {return Err(lab_control_store::Error("fixture host CAS refused".into()));}
  self.current=request.clone();self.persist()?;Ok(self.current.clone())
 }
 fn selection(&self)->TrustedSelection {TrustedSelection{confirmation:self.current.clone(),posture:Posture::Fixture}}
}
fn setup(t:&Temp)->(Root,Witness) { let root=Root::create_fixture(&t.0,"domain").unwrap();let initial={let locks=root.acquire(Rank::Journal,WAIT).unwrap();Ledger::initialize_fixture(&root,&locks.borrow().unwrap(),"authority-fixture",limits(),writer()).unwrap()}; let w=Witness::new(&t.0,initial);(root,w) }
fn append(l:&mut Ledger<'_>,held:&lab_control_store::custody::Held<'_>,w:&mut Witness,c:Change) {let p=l.append(held,c).unwrap();assert!(!l.inspect().writable);let confirmation=w.advance(p.requested_confirmation()).unwrap();l.acknowledge(held,p,confirmation).unwrap();assert!(l.inspect().writable);}
fn store(id:&str)->Change {Change::StoreEpoch{store_id:id.into(),prior_epoch:0,new_epoch:1,instance:format!("{}-instance",id),fence_binding:b()}}
fn slot()->Change {Change::SlotEpoch{slot_id:"source".into(),prior_epoch:0,new_epoch:1,holder:"family".into(),slot_receipt_binding:b(),prior_disposition_binding:b(),containment_binding:b()}}
fn phase(state:SlotPhase)->Change {Change::SlotState{slot_id:"source".into(),epoch:1,holder:"family".into(),state,terminal_binding:b()}}
fn op()->Operation {Operation{operation_id:"op1".into(),store_id:"store1".into(),store_instance:"store1-instance".into(),store_epoch:1,slot_id:"source".into(),slot_epoch:1,holder:"family".into(),fingerprint:h(),original_request_sha256:"b".repeat(64),issuer:"issuer".into(),host_event:"event".into()}}
fn ready(l:&mut Ledger<'_>,held:&lab_control_store::custody::Held<'_>,w:&mut Witness) {append(l,held,w,store("store1"));append(l,held,w,store("store2"));append(l,held,w,slot());append(l,held,w,phase(SlotPhase::Active));}
fn finish(outcome:Outcome)->Change {Change::Outcome{operation_id:"op1".into(),fingerprint:h(),result_binding:b(),outcome}}
fn recovery(root:&Root,l:&Ledger<'_>,action:ReconcileAction)->TrustedReconciliation {TrustedReconciliation{authority_domain:"authority-fixture".into(),root:root.identity(),writer:writer(),observed_head:l.inspect().verified_head,authority_binding:b(),action}}
fn confirm_recovery(root:&Root,l:&mut Ledger<'_>,held:&lab_control_store::custody::Held<'_>,w:&mut Witness,action:ReconcileAction){let selected=recovery(root,l,action);let pending=l.reconcile(held,selected).unwrap();let c=w.advance(pending.requested_confirmation()).unwrap();l.acknowledge(held,pending,c).unwrap();}

#[test] fn lost_result_restart_keeps_consumed_across_store_id(){
 let t=Temp::new();let(root,mut w)=setup(&t);
 {let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);append(&mut l,&held,&mut w,Change::Reserve{operation:op()});append(&mut l,&held,&mut w,finish(Outcome::Committed));}
 let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();assert_eq!(l.consumption("issuer","event"),Consumption::Consumed);assert_eq!(l.outcome("op1").unwrap().0,Outcome::Committed);
 let mut other=op();other.operation_id="new-op".into();other.store_id="store2".into();other.store_instance="store2-instance".into();assert!(l.append(&held,Change::Reserve{operation:other}).unwrap_err().0.contains("event consumed"));
}
#[test] fn durable_unconfirmed_tail_quarantines_without_forgetting_event(){
 let t=Temp::new();let(root,mut w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();
 let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);let p=l.append(&held,Change::Reserve{operation:op()}).unwrap();let exact=p.requested_confirmation().clone();drop(l);
 let mut reopened=Ledger::open(&root,&held,w.selection()).unwrap();assert!(!reopened.inspect().writable);assert_eq!(reopened.consumption("issuer","event"),Consumption::Consumed);assert_eq!(reopened.consumption("issuer","unseen"),Consumption::Unknown);assert!(reopened.append(&held,finish(Outcome::Committed)).is_err());
 // Only the independently serialized host CAS can confirm the durable tail.
 w.advance(&exact).unwrap();let recovered=Ledger::open(&root,&held,w.selection()).unwrap();assert!(recovered.inspect().writable);assert_eq!(recovered.consumption("issuer","event"),Consumption::Consumed);
}
#[test] fn confirmation_before_reply_recovers_without_second_reservation(){
 let t=Temp::new();let(root,mut w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);
 let p=l.append(&held,Change::Reserve{operation:op()}).unwrap();w.advance(p.requested_confirmation()).unwrap();drop(p);drop(l);
 let mut l=Ledger::open(&root,&held,w.selection()).unwrap();assert!(l.inspect().writable);assert!(l.append(&held,Change::Reserve{operation:op()}).is_err());assert_eq!(l.consumption("issuer","event"),Consumption::Consumed);
}
#[test] fn copied_stale_records_and_witness_ahead_are_inspection_only(){
 let t=Temp::new();let(root,mut w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);append(&mut l,&held,&mut w,Change::Reserve{operation:op()});drop(l);
 let record=t.0.join("domain/records/0000000000000005.json");let original=fs::read(&record).unwrap();fs::remove_file(&record).unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();assert!(!l.inspect().writable);assert_eq!(l.consumption("issuer","event"),Consumption::Unknown);assert!(l.append(&held,Change::Reserve{operation:op()}).is_err());assert!(!record.exists());assert!(!original.is_empty());
}
#[test] fn root_copy_and_branch_cas_cannot_reuse_common_checkpoint(){
 let t=Temp::new();let(root,mut w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();let p=l.append(&held,store("s")).unwrap();let mut altered=p.requested_confirmation().clone();altered.root.inode+=1;assert!(w.advance(&altered).is_err());let exact=p.requested_confirmation().clone();w.advance(&exact).unwrap();assert!(w.advance(&exact).is_err());
 let root2=Root::create_fixture(&t.0,"copy").unwrap();let locks2=root2.acquire(Rank::Journal,WAIT).unwrap();assert!(Ledger::open(&root2,&locks2.borrow().unwrap(),w.selection()).is_err());
}
#[test] fn missing_corrupt_unknown_and_fifo_tail_never_get_repaired(){
 for mode in ["partial","unknown","fifo","symlink"] {let t=Temp::new();let(root,w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let path=t.0.join("domain/records/0000000000000001.json");
 match mode {"partial"=>{fs::write(&path,b"{\"schema_version\":").unwrap();fs::set_permissions(&path,fs::Permissions::from_mode(0o600)).unwrap();},"unknown"=>{fs::write(t.0.join("domain/records/foreign"),b"x").unwrap();},"fifo"=>{use std::os::unix::ffi::OsStrExt;let c=std::ffi::CString::new(path.as_os_str().as_bytes()).unwrap();assert_eq!(unsafe{libc::mkfifo(c.as_ptr(),0o600)},0);},_=>symlink("/dev/null",&path).unwrap()};
 let start=Instant::now();let l=Ledger::open(&root,&held,w.selection()).unwrap();assert!(!l.inspect().writable);assert!(start.elapsed()<Duration::from_secs(1));assert_eq!(l.consumption("i","e"),Consumption::Unknown);assert_eq!(fs::read_dir(t.0.join("domain/records")).unwrap().count(),1);}
}
#[test] fn independent_witness_fields_and_actual_posture_are_closed(){
 let t=Temp::new();let(root,w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut selected=w.selection();selected.posture=Posture::Actual;assert!(Ledger::open(&root,&held,selected).is_err());
 for field in 0..5 {let mut s=w.selection();match field{0=>s.confirmation.authority_domain="other".into(),1=>s.confirmation.header_sha256="b".repeat(64),2=>s.confirmation.root.inode+=1,3=>s.confirmation.predecessor.sha256="b".repeat(64),_=>s.confirmation.head.sequence+=1};assert!(Ledger::open(&root,&held,s).map_or(true,|l|!l.inspect().writable));}
 assert!(Root::create_fixture(&t.0,"domain").is_err());
}
#[test] fn stale_epoch_holder_and_store_instance_refuse_before_append(){
 let t=Temp::new();let(root,mut w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);let head=l.inspect().verified_head;
 for field in 0..4 {let mut o=op();match field{0=>o.store_epoch+=1,1=>o.store_instance="other".into(),2=>o.slot_epoch+=1,_=>o.holder="other".into()};assert!(l.append(&held,Change::Reserve{operation:o}).is_err());assert_eq!(l.inspect().verified_head,head);}
 assert!(l.append(&held,slot()).is_err());
}
#[test] fn quarantine_outcome_fences_every_release_until_selected_recovery(){
 let t=Temp::new();let(root,mut w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);append(&mut l,&held,&mut w,Change::Reserve{operation:op()});append(&mut l,&held,&mut w,finish(Outcome::Quarantined));
 let mut other=op();other.operation_id="op2".into();other.host_event="event2".into();assert!(l.append(&held,Change::Reserve{operation:other}).is_err());assert!(l.append(&held,Change::StoreEpoch{store_id:"store1".into(),prior_epoch:1,new_epoch:2,instance:"replacement".into(),fence_binding:b()}).is_err());
 append(&mut l,&held,&mut w,phase(SlotPhase::Closing));assert!(l.append(&held,phase(SlotPhase::Closed)).is_err());append(&mut l,&held,&mut w,phase(SlotPhase::Quarantined));assert!(l.append(&held,slot()).is_err());
 let action=ReconcileAction::Outcome{operation_id:"op1".into(),fingerprint:h(),result_binding:b(),outcome:Outcome::Aborted};let mut stale=recovery(&root,&l,action.clone());stale.observed_head.sha256="e".repeat(64);assert!(l.reconcile(&held,stale).is_err());assert!(l.append(&held,Change::Reconcile{action:action.clone(),authority_binding:b(),observed_head:l.inspect().verified_head}).is_err());
 confirm_recovery(&root,&mut l,&held,&mut w,action);confirm_recovery(&root,&mut l,&held,&mut w,ReconcileAction::Slot{slot_id:"source".into(),epoch:1,holder:"family".into(),terminal_binding:b()});
 append(&mut l,&held,&mut w,Change::SlotEpoch{slot_id:"source".into(),prior_epoch:1,new_epoch:2,holder:"next-family".into(),slot_receipt_binding:b(),prior_disposition_binding:b(),containment_binding:b()});assert_eq!(l.consumption("issuer","event"),Consumption::Consumed);
}
#[test] fn ordered_locks_borrow_without_reacquisition_and_contend_bounded(){
 let t=Temp::new();let(root,_)=setup(&t);let mut locks=root.acquire(Rank::SourceSlot,WAIT).unwrap();assert!(locks.extend(Rank::SourceSlot,WAIT).is_err());assert!(locks.extend(Rank::Replay,WAIT).is_err());locks.extend(Rank::Publication,WAIT).unwrap();locks.extend(Rank::Replay,WAIT).unwrap();locks.extend(Rank::Native,WAIT).unwrap();locks.extend(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let nested=held.nested().unwrap();assert_eq!(nested.rank(),Rank::Journal);
 let start=Instant::now();assert!(root.acquire(Rank::Journal,Duration::from_millis(30)).is_err());assert!(start.elapsed()>=Duration::from_millis(25)&&start.elapsed()<Duration::from_secs(1));drop(nested);drop(held);drop(locks);assert!(root.acquire(Rank::Journal,WAIT).is_ok());
}
#[test] fn held_root_lock_and_records_attachment_swaps_refuse(){
 for target in ["locks/00-source-slot","records"] {let t=Temp::new();let(root,w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let path=t.0.join("domain").join(target);fs::rename(&path,path.with_extension("old")).unwrap();if target=="records"{fs::create_dir(&path).unwrap();fs::set_permissions(&path,fs::Permissions::from_mode(0o700)).unwrap();}else{let f=OpenOptions::new().write(true).create_new(true).mode(0o600).open(&path).unwrap();f.sync_all().unwrap();}assert!(held.nested().is_err());assert!(Ledger::open(&root,&held,w.selection()).is_err());}
}
#[test] fn terminal_budget_survives_capacity_exhaustion(){
 let t=Temp::new();let root=Root::create_fixture(&t.0,"domain").unwrap();let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut small=limits();small.max_records=11;let initial=Ledger::initialize_fixture(&root,&held,"authority-fixture",small,writer()).unwrap();let mut w=Witness::new(&t.0,initial);let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);append(&mut l,&held,&mut w,Change::Reserve{operation:op()});assert!(l.append(&held,store("exhausted")).is_err());append(&mut l,&held,&mut w,phase(SlotPhase::Closing));append(&mut l,&held,&mut w,finish(Outcome::Quarantined));append(&mut l,&held,&mut w,phase(SlotPhase::Quarantined));confirm_recovery(&root,&mut l,&held,&mut w,ReconcileAction::Outcome{operation_id:"op1".into(),fingerprint:h(),result_binding:b(),outcome:Outcome::Aborted});confirm_recovery(&root,&mut l,&held,&mut w,ReconcileAction::Slot{slot_id:"source".into(),epoch:1,holder:"family".into(),terminal_binding:b()});assert!(l.inspect().writable);assert_eq!(l.consumption("issuer","event"),Consumption::Consumed);assert!(l.append(&held,store("still-exhausted")).is_err());
}
#[test] fn canonical_duplicate_unknown_number_and_digest_tampering_refuse(){
 let good=codec::encode(&writer()).unwrap();assert_eq!(codec::decode::<WriterFence>(&good).unwrap(),writer());for bad in [b"{\"epoch\":1,\"epoch\":1,\"instance\":\"host-fixture\"}".as_slice(),b"{\"epoch\":1.0,\"instance\":\"host-fixture\"}",b"{\"epoch\":1,\"instance\":\"host-fixture\",\"unknown\":true}",b"{\"epoch\":9223372036854775808,\"instance\":\"host-fixture\"}"] {assert!(codec::decode::<WriterFence>(bad).is_err());}
}

#[test] fn crash_child_driver(){
 let Some(base)=std::env::var_os("CONTROL_CRASH_BASE") else{return;};let base=PathBuf::from(base);let mode=std::env::var("CONTROL_CRASH_MODE").unwrap();
 let raw=fs::read(base.join("selected-witness.json")).unwrap();let selected:HostConfirmation=codec::decode(&raw).unwrap();let root=Root::open(&base,"domain",&selected.root).unwrap();
 if mode=="lock" {assert!(root.acquire(Rank::Journal,Duration::from_millis(50)).is_err());fs::write(base.join("child-ready"),b"contended").unwrap();return;}
 let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut ledger=Ledger::open(&root,&held,TrustedSelection{confirmation:selected.clone(),posture:Posture::Fixture}).unwrap();let pending=ledger.append(&held,Change::Reserve{operation:op()}).unwrap();
 if mode=="confirmed" {let mut witness=Witness{path:base.join("independent-fixture-witness"),current:selected};witness.advance(pending.requested_confirmation()).unwrap();}
 let mut marker=OpenOptions::new().write(true).create_new(true).mode(0o600).open(base.join("child-ready")).unwrap();marker.write_all(b"durable-boundary").unwrap();marker.sync_all().unwrap();
 loop{std::thread::sleep(Duration::from_secs(1));}
}
fn launch_child(t:&Temp,selected:&HostConfirmation,mode:&str)->std::process::Child {
 fs::write(t.0.join("selected-witness.json"),codec::encode(selected).unwrap()).unwrap();
 std::process::Command::new(std::env::current_exe().unwrap()).args(["--exact","crash_child_driver","--nocapture"]).env("CONTROL_CRASH_BASE",&t.0).env("CONTROL_CRASH_MODE",mode).stdout(File::create(t.0.join("child.stdout")).unwrap()).stderr(File::create(t.0.join("child.stderr")).unwrap()).spawn().unwrap()
}
fn await_child(t:&Temp,child:&mut std::process::Child){let start=Instant::now();while !t.0.join("child-ready").exists(){if let Some(status)=child.try_wait().unwrap(){panic!("child exited before boundary: {:?}: {}",status,fs::read_to_string(t.0.join("child.stderr")).unwrap());}if start.elapsed()>Duration::from_secs(10){child.kill().unwrap();child.wait().unwrap();panic!("child boundary timeout");}std::thread::sleep(Duration::from_millis(5));}}
#[test] fn kill_and_restart_on_both_sides_of_independent_confirmation(){
 for mode in ["pending","confirmed"] {let t=Temp::new();let(root,mut w)=setup(&t);{let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);}
 let mut child=launch_child(&t,&w.current,mode);await_child(&t,&mut child);child.kill().unwrap();let status=child.wait().unwrap();assert!(!status.success());
 if mode=="confirmed"{w.current=codec::decode(&fs::read(w.path.join("5.json")).unwrap()).unwrap();}
 let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();assert_eq!(l.consumption("issuer","event"),Consumption::Consumed);assert_eq!(l.inspect().writable,mode=="confirmed");assert!(l.append(&held,Change::Reserve{operation:op()}).is_err());}
}
#[test] fn actual_process_contends_on_shared_domain_lock(){
 let t=Temp::new();let(root,w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let mut child=launch_child(&t,&w.current,"lock");await_child(&t,&mut child);let start=Instant::now();loop{if let Some(status)=child.try_wait().unwrap(){assert!(status.success());break;}if start.elapsed()>Duration::from_secs(2){child.kill().unwrap();child.wait().unwrap();panic!("lock child did not exit");}std::thread::sleep(Duration::from_millis(5));}drop(locks);assert!(root.acquire(Rank::Journal,WAIT).is_ok());
}
#[test] fn nested_effect_borrows_only_acknowledged_unresolved_operation(){
 let t=Temp::new();let(root,mut w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();ready(&mut l,&held,&mut w);let pending=l.append(&held,Change::Reserve{operation:op()}).unwrap();assert!(l.borrow_operation(&held,"op1",&h()).is_err());let c=w.advance(pending.requested_confirmation()).unwrap();l.acknowledge(&held,pending,c).unwrap();{let borrowed=l.borrow_operation(&held,"op1",&h()).unwrap();let nested=borrowed.nested().unwrap();assert_eq!(nested.rank(),Rank::Journal);assert_eq!(borrowed.operation().operation_id,"op1");}assert!(l.borrow_operation(&held,"op1",&"b".repeat(64)).is_err());append(&mut l,&held,&mut w,finish(Outcome::Quarantined));assert!(l.inspect().writable);assert_eq!(l.inspect().unresolved_operations,1);assert_eq!(l.inspect().quarantined_operations,1);assert!(l.borrow_operation(&held,"op1",&h()).is_err());
}
#[test] fn competing_writer_instance_and_epoch_fence_old_ledger(){
 let t=Temp::new();let(root,mut w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();append(&mut l,&held,&mut w,store("s"));let old=w.current.clone();
 let mut wrong=w.selection();wrong.confirmation.writer.instance="impostor-same-epoch".into();assert!(!Ledger::open(&root,&held,wrong).unwrap().inspect().writable);
 // This independent fixture host selection models a separately authorized
 // higher writer fence. An old writer cannot be made current from disk alone.
 let mut newer=w.selection();newer.confirmation.writer.epoch=2;newer.confirmation.writer.instance="replacement-host".into();let mut replacement=Ledger::open(&root,&held,newer).unwrap();let pending=replacement.append(&held,store("s2")).unwrap();let selected=pending.requested_confirmation().clone();replacement.acknowledge(&held,pending,selected.clone()).unwrap();assert!(!Ledger::open(&root,&held,TrustedSelection{confirmation:old,posture:Posture::Fixture}).unwrap().inspect().writable);assert!(l.append(&held,store("old-writer")).is_err());
}
#[test] fn full_evidence_locator_survives_codec_and_cannot_be_reduced_to_hash(){
 let binding=b();let original=codec::encode(&binding).unwrap();let mut other=binding.clone();other.root_id="different-root".into();assert_ne!(codec::digest(&original),codec::digest(&codec::encode(&other).unwrap()));assert_eq!(codec::decode::<ByteBinding>(&original).unwrap(),binding);assert!(codec::decode::<ByteBinding>(format!("{{\"sha256\":\"{}\",\"size_bytes\":10}}",h()).as_bytes()).is_err());
 let t=Temp::new();let(root,w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut l=Ledger::open(&root,&held,w.selection()).unwrap();let mut bad=b();bad.relative_path="../escape".into();assert!(l.append(&held,Change::StoreEpoch{store_id:"s".into(),prior_epoch:0,new_epoch:1,instance:"i".into(),fence_binding:bad}).is_err());assert_eq!(l.inspect().verified_records,0);
}

fn unhex(text:&str)->Vec<u8>{assert_eq!(text.len()%2,0);text.as_bytes().chunks_exact(2).map(|p|u8::from_str_radix(std::str::from_utf8(p).unwrap(),16).unwrap()).collect()}
#[test] fn independently_selected_foundation_c01_vectors_match_exact_rust_bytes(){
 let fixtures:serde_json::Value=serde_json::from_str(include_str!("c01-codec-vectors.json")).unwrap();let vectors=fixtures["vectors"].as_array().unwrap();assert_eq!(vectors.len(),33);
 for vector in vectors {let raw=unhex(vector["raw_hex"].as_str().unwrap());let expected=vector["admitted"].as_bool().unwrap();let name=vector["name"].as_str().unwrap();
  if vector["type"]=="binding" {let result=codec::decode::<ByteBinding>(&raw);assert_eq!(result.as_ref().is_ok_and(|b|b.valid()),expected,"C01 schema vector {}",name);if expected{assert_eq!(codec::encode(&result.unwrap()).unwrap(),raw,"canonical binding {}",name);}}
  else{let result=codec::decode::<serde_json::Value>(&raw);assert_eq!(result.is_ok(),expected,"canonical vector {}",name);if expected{assert_eq!(codec::encode(&result.unwrap()).unwrap(),raw);}}
 }
 let combining=unhex(vectors[0]["raw_hex"].as_str().unwrap());let composed=unhex(vectors[1]["raw_hex"].as_str().unwrap());assert_ne!(codec::digest(&combining),codec::digest(&composed));
 let mut extra=serde_json::to_value(b()).unwrap();extra["unknown"]=serde_json::Value::Bool(true);assert!(codec::decode::<ByteBinding>(&serde_json::to_vec(&extra).unwrap()).is_err());
 let mut overflow=serde_json::to_value(b()).unwrap();overflow["size_bytes"]=serde_json::Value::from(i64::MAX as u64+1);assert!(codec::decode::<ByteBinding>(&serde_json::to_vec(&overflow).unwrap()).is_err());
}
#[test] fn unicode_binding_at_4096_scalars_and_i64_edge_survives_durable_record(){
 let t=Temp::new();let root=Root::create_fixture(&t.0,"domain").unwrap();let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut selected_limits=limits();selected_limits.max_record_bytes=65536;let initial=Ledger::initialize_fixture(&root,&held,"authority-fixture",selected_limits,writer()).unwrap();let mut w=Witness::new(&t.0,initial);let mut ledger=Ledger::open(&root,&held,w.selection()).unwrap();let mut proof=b();proof.root_id="🧪".repeat(4096);proof.relative_path="é".repeat(4096);proof.size_bytes=i64::MAX as u64;assert!(proof.valid());let expected=proof.clone();append(&mut ledger,&held,&mut w,Change::StoreEpoch{store_id:"s".into(),prior_epoch:0,new_epoch:1,instance:"i".into(),fence_binding:proof});drop(ledger);let reopened=Ledger::open(&root,&held,w.selection()).unwrap();assert!(reopened.inspect().writable);let stored:serde_json::Value=serde_json::from_slice(&fs::read(t.0.join("domain/records/0000000000000001.json")).unwrap()).unwrap();let actual:ByteBinding=serde_json::from_value(stored["change"]["fence_binding"].clone()).unwrap();assert_eq!(actual,expected);
}
#[test] fn schema_admission_does_not_expand_record_bytes_depth_or_local_identifier_limits(){
 let t=Temp::new();let(root,w)=setup(&t);let locks=root.acquire(Rank::Journal,WAIT).unwrap();let held=locks.borrow().unwrap();let mut ledger=Ledger::open(&root,&held,w.selection()).unwrap();let mut proof=b();proof.relative_path="🧪".repeat(4096);assert!(proof.valid());let error=ledger.append(&held,Change::StoreEpoch{store_id:"s".into(),prior_epoch:0,new_epoch:1,instance:"i".into(),fence_binding:proof}).unwrap_err();assert_eq!(error.0,"record byte bound");assert_eq!(ledger.inspect().verified_records,0);
 assert!(!codec::identifier("not-a-local-identifier 🧪"));assert!(!codec::identifier(&"x".repeat(129)));assert!(codec::decode::<serde_json::Value>(&vec![b' ';65537]).is_err());assert!(codec::encode(&"x".repeat(65537)).is_err());let mut deep=serde_json::Value::Null;for _ in 0..65{deep=serde_json::Value::Array(vec![deep]);}assert!(codec::encode(&deep).is_err());
}
