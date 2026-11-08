use crate::{state::*,quota,roots::{self,Root,Domain,Binding,ExecutionScope},members};
use std::{fs,path::PathBuf,os::unix::fs::PermissionsExt,time::Duration,sync::atomic::{AtomicU64,Ordering}};
use lab_control_store::ledger::{Operation,HostConfirmation,WriterFence,Head};
use lab_completion_broker::{self as wire,authority};
use serde_json::json;
use ed25519_dalek::SigningKey;
static NEXT:AtomicU64=AtomicU64::new(0);
fn b(name:&str,raw:&[u8])->Binding{bound("fixture-input",name,raw).unwrap()}
fn limits()->quota::Limits{quota::Limits{schema_version:"lab-broker-quota/v1".into(),max_record_bytes:65536,max_response_bytes:65536,max_sequences:32,max_stage_bytes:65536,max_member_bytes:65536,max_members:16,max_retained_bytes:16*1024*1024,max_retained_files:4096,max_stage_count:2,max_orphan_count:2,max_orphan_bytes:131072,max_inflight:1}}
struct Fixture{base:PathBuf,receipt:Root,witness:Root,stage:Root,scope:PrefixScope,ledger:HostConfirmation,proof_signer:SelectedSigner,proof_key:SigningKey,response_signer:SelectedSigner,response_key:SigningKey}
fn signer(purpose:&str,n:u8)->(SelectedSigner,SigningKey){let key=SigningKey::from_bytes(&[n;32]);let raw=encode(&SignerSelection{schema_version:"lab-broker-fixed-signer/v1".into(),issuer_ref:format!("fixture-{purpose}"),purpose:purpose.into(),algorithm:"ed25519".into(),adapter:"owner-hex-v1".into(),public_key:wire::hex(&key.verifying_key().to_bytes()),domain:Domain::Fixture}).unwrap();(SelectedSigner::select(&raw,&b(&format!("{purpose}.json"),&raw),Domain::Fixture,purpose).unwrap(),key)}
impl Fixture{
 fn new()->Self{
 let base=PathBuf::from(std::env::var("TMPDIR").unwrap()).join(format!("dispatch-state-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::SeqCst)));fs::create_dir(&base).unwrap();fs::set_permissions(&base,fs::Permissions::from_mode(0o700)).unwrap();
 let execution_scope=ExecutionScope{activation_binding:b("activation.json",b"isolated fixture activation"),store_id:"fixture-store".into(),instance_id:"fixture-instance".into(),slot_epoch:1,principal_ref:"fixture-principal".into()};
 let root=|name:&str|{let path=base.join(name);fs::create_dir(&path).unwrap();fs::set_permissions(&path,fs::Permissions::from_mode(0o700)).unwrap();Root::open(Root::capture_fixture(&path,name,[b("alias.json",b"fixture aliases"),b("ancestors.json",b"fixture ancestors"),b("acl.json",b"fixture acl")],execution_scope.clone()).unwrap(),Domain::Fixture).unwrap()};
 let receipt=root("receipts");let witness=root("witness");let stage=root("stage");
 let operation=Operation{operation_id:"operation-1".into(),store_id:"fixture-store".into(),store_instance:"fixture-instance".into(),store_epoch:1,slot_id:"slot".into(),slot_epoch:1,holder:"fixture-principal".into(),fingerprint:roots::hash(b"original operation"),original_request_sha256:roots::hash(b"original request"),issuer:"intent-issuer".into(),host_event:"event-1".into()};
 let scope=PrefixScope{schema_version:"lab-broker-receipt-scope/v1".into(),domain:Domain::Fixture,authority_domain:"fixture-authority".into(),control_root:lab_control_store::custody::Identity{device:1,inode:2,uid:unsafe{libc::geteuid()}},receipt_root:receipt.identity().clone(),receipt_root_id:"receipts".into(),writer:WriterFence{instance:"writer".into(),epoch:1},execution_scope,operation,recipient:Caller{pid:std::process::id() as i32,uid:unsafe{libc::geteuid()},gid:unsafe{libc::getegid()}},channel_binding:b("channel.json",b"original channel")};
 let ledger=HostConfirmation{schema_version:"lab-host-control-confirmation/v1".into(),authority_domain:scope.authority_domain.clone(),root:scope.control_root.clone(),header_sha256:roots::hash(b"header"),writer:scope.writer.clone(),predecessor:Head{sequence:3,sha256:roots::hash(b"before reserve")},head:Head{sequence:4,sha256:roots::hash(b"reserved")}};
 let(proof_signer,proof_key)=signer("receipt-prefix",3);let(response_signer,response_key)=signer("broker-response",4);
 Self{base,receipt,witness,stage,scope,ledger,proof_signer,proof_key,response_signer,response_key}
 }
 fn frame(&self,seq:u64)->Vec<u8>{let permit=json!({"fixture":"journal-only structural input; no authority claim"});encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":{"schema_version":"lab-completion-broker-request/v1","request_id":format!("req-{seq}"),"operation_id":self.scope.operation.operation_id,"sequence":seq,"activation_binding":self.scope.execution_scope.activation_binding,"store_id":"fixture-store","instance_id":"fixture-instance","slot_epoch":1,"principal_ref":"fixture-principal","verb":"create_stage","intent_binding":b("intent.json",b"intent"),"authorization_binding":wire::content_digest(&encode(&permit).unwrap()),"payload":{"root_id":"stage","stage_name":"owned-stage","max_bytes":65536}},"permit":permit})).unwrap()}
 fn current(&self,w:&PrefixWitness<'_>,new_channel:bool)->CurrentPrefix{let now=now_seconds().unwrap();let mut current_ledger=self.ledger.clone();let channel=if new_channel{current_ledger.writer=WriterFence{instance:"later-writer".into(),epoch:2};b("later-channel.json",b"different current channel")}else{self.scope.channel_binding.clone()};let query=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:self.scope.history_key().unwrap(),recipient:self.scope.recipient.clone(),channel_binding:channel.clone(),challenge:roots::hash(b"fresh inspection challenge"),current_ledger_confirmation:current_ledger.clone(),current_execution_scope:self.scope.execution_scope.clone(),not_before:now,expires_at:now+120};let raw=w.inspect(&query,&self.scope.recipient,&self.scope.recipient,&channel,&current_ledger,&self.scope.execution_scope).unwrap();CurrentPrefix::verify(&raw,&self.proof_signer,&query,&self.scope,&b("original-scope.json",&encode(&self.scope).unwrap()),now).unwrap()}
}
impl Drop for Fixture{fn drop(&mut self){if !std::thread::panicking(){fs::remove_dir_all(&self.base).unwrap();}}}
fn reserve(j:&ReceiptJournal<'_>)->quota::Remaining{let(inv,_)=j.inventory().unwrap();quota::Remaining{inventory_sha256:inv,prefix_sha256:j.head().entry_sha256.clone(),bytes:8*1024*1024,inodes:4096}}
fn complete<'a>(f:&Fixture,j:&mut ReceiptJournal<'a>,w:&mut PrefixWitness<'_>,stage_hold:&'a roots::Exclusive<'a>)->Vec<u8>{
 complete_with_ttl(f,j,w,stage_hold,120)
}
fn complete_with_ttl<'a>(f:&Fixture,j:&mut ReceiptJournal<'a>,w:&mut PrefixWitness<'_>,stage_hold:&'a roots::Exclusive<'a>,ttl:u64)->Vec<u8>{
 let raw=f.frame(0);let frame=wire::Frame::decode(&raw).unwrap();let mut p=j.begin(&frame,&raw,&f.scope.operation.fingerprint,&f.ledger,&reserve(j)).unwrap();
 let action=members::Action{request:frame.request().clone(),wire:frame.wire_digest().into(),fingerprint:f.scope.operation.fingerprint.clone(),domain:Domain::Fixture,stage_binding:None};
 let mut stage=members::Stage::create(stage_hold,&action).unwrap();let receipt=j.member_receipt(&mut p,stage.pending().unwrap(),stage.proposed_state().unwrap()).unwrap();let rb=receipt.binding().clone();stage.acknowledge(receipt).unwrap();let snap=stage.snapshot().unwrap();
 let response=encode(&authority::sign_receipt(&frame,"staging","PASS",None,serde_json::to_value(&rb).unwrap(),f.response_signer.issuer(),&f.response_key).unwrap()).unwrap();j.finish(&mut p,Some(&snap),&response,"staging","PASS").unwrap();assert!(j.entries().is_err());
 let now=now_seconds().unwrap();let q=j.confirmation_request(&p,roots::hash(b"CAS challenge"),now,now+ttl).unwrap();let proof=w.compare_and_swap(&q,&f.scope.recipient).unwrap();let verified=VerifiedPrefix::verify(&proof,&f.proof_signer,&q,now_seconds().unwrap()).unwrap();let returned=j.confirm(p,verified,&f.response_signer).unwrap();assert_eq!(returned,response);returned
}
#[test]fn strict_codec_domains(){assert!(encode(&json!({"number":u64::MAX})).is_err());assert!(decode::<serde_json::Value>(b"{\"a\":1,\"a\":2}",4096).is_err());assert!(decode::<serde_json::Value>(b"{\"a\":-0}",4096).is_err());assert!(decode::<serde_json::Value>(b"{\"a\":1.0}",4096).is_err());let raw=encode(&json!({"s":"e\u{301}\u{0}𐐀","n":i64::MAX})).unwrap();assert_eq!(decode::<serde_json::Value>(&raw,4096).unwrap()["s"],"e\u{301}\u{0}𐐀");}
#[test]fn signer_domain_purpose_and_key_alias_refuse(){let(s,k)=signer("receipt-prefix",3);let raw=s.sign(&k,&json!({"schema_version":"fixture-proof/v1"})).unwrap();assert!(s.verify::<serde_json::Value>(&raw).is_ok());let(other,_)=signer("broker-response",4);assert!(other.verify::<serde_json::Value>(&raw).is_err());assert!(s.distinct(&s).is_err());assert!(s.distinct(&other).is_ok());assert!(s.signing_key(&wire::hex(&[4;32]).into_bytes()).is_err());}
#[test]fn exact_prefix_and_acknowledged_ranges_restart_remain_recovery_fenced(){let f=Fixture::new();let rh=f.receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=f.witness.exclusive(Duration::from_millis(100)).unwrap();let sh=f.stage.exclusive(Duration::from_millis(100)).unwrap();let mut w=PrefixWitness::open(&wh,f.scope.clone(),b("original-scope.json",&encode(&f.scope).unwrap()),PrefixHead::genesis(&f.scope).unwrap(),&f.proof_signer,f.proof_key.clone()).unwrap();let mut j=ReceiptJournal::open_empty(&rh,f.scope.clone(),limits()).unwrap();let original=complete(&f,&mut j,&mut w,&sh);drop(j);let restored=RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).unwrap();assert!(restored.requires_reconciliation());restored.validate_ranges(&sh).unwrap();assert_eq!(fs::read(f.base.join("receipts/sequence-0000000000000001/response.json")).unwrap(),original);}
#[test]fn current_channel_writer_change_does_not_rewrite_original_genesis(){let f=Fixture::new();let rh=f.receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=f.witness.exclusive(Duration::from_millis(100)).unwrap();let sh=f.stage.exclusive(Duration::from_millis(100)).unwrap();let original_scope=encode(&f.scope).unwrap();let mut w=PrefixWitness::open(&wh,f.scope.clone(),b("original-scope.json",&original_scope),PrefixHead::genesis(&f.scope).unwrap(),&f.proof_signer,f.proof_key.clone()).unwrap();let mut j=ReceiptJournal::open_empty(&rh,f.scope.clone(),limits()).unwrap();let response=complete(&f,&mut j,&mut w,&sh);drop(j);let current=f.current(&w,true);let restored=RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),current,&f.proof_signer,&f.response_signer).unwrap();assert!(restored.requires_reconciliation());assert_eq!(original_scope,encode(&f.scope).unwrap());assert_eq!(fs::read(f.base.join("receipts/sequence-0000000000000001/response.json")).unwrap(),response);let mut changed=f.scope.clone();changed.channel_binding=b("new.json",b"new");assert_eq!(changed.history_key().unwrap(),f.scope.history_key().unwrap());assert_ne!(changed.digest().unwrap(),f.scope.digest().unwrap());assert!(RestartedPrefix::inspect(&rh,changed,limits(),f.current(&w,true),&f.proof_signer,&f.response_signer).is_err());}
#[test]fn retained_unconfirmed_intent_and_erased_tail_never_resume_producer(){let f=Fixture::new();let rh=f.receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=f.witness.exclusive(Duration::from_millis(100)).unwrap();let w=PrefixWitness::open(&wh,f.scope.clone(),b("original-scope.json",&encode(&f.scope).unwrap()),PrefixHead::genesis(&f.scope).unwrap(),&f.proof_signer,f.proof_key.clone()).unwrap();let mut j=ReceiptJournal::open_empty(&rh,f.scope.clone(),limits()).unwrap();let raw=f.frame(0);let frame=wire::Frame::decode(&raw).unwrap();let p=j.begin(&frame,&raw,&f.scope.operation.fingerprint,&f.ledger,&reserve(&j)).unwrap();assert!(j.entries().is_err());drop(p);drop(j);assert!(RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).is_err());fs::remove_dir_all(f.base.join("receipts/sequence-0000000000000001")).unwrap();let clean_old=RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).unwrap();assert!(clean_old.requires_reconciliation());}
#[test]fn missing_confirmed_entry_and_changed_original_refuse(){for changed in [false,true]{let f=Fixture::new();let rh=f.receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=f.witness.exclusive(Duration::from_millis(100)).unwrap();let sh=f.stage.exclusive(Duration::from_millis(100)).unwrap();let mut w=PrefixWitness::open(&wh,f.scope.clone(),b("original-scope.json",&encode(&f.scope).unwrap()),PrefixHead::genesis(&f.scope).unwrap(),&f.proof_signer,f.proof_key.clone()).unwrap();let mut j=ReceiptJournal::open_empty(&rh,f.scope.clone(),limits()).unwrap();complete(&f,&mut j,&mut w,&sh);drop(j);let path=f.base.join("receipts/sequence-0000000000000001");if changed{fs::write(path.join("acknowledged.json"),b"{}").unwrap();}else{fs::remove_dir_all(path).unwrap();}assert!(RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).is_err());}}
#[test]fn quota_prospective_counts_capacity_and_completion_positions(){let l=limits();let mut u=quota::Usage::default();let r=quota::Remaining{inventory_sha256:roots::hash(b"inventory"),prefix_sha256:roots::hash(b"prefix"),bytes:2*1024*1024,inodes:4096};assert!(quota::admit(&l,&u,&r,&r.inventory_sha256,&r.prefix_sha256).is_ok());u.inflight=1;assert!(quota::admit(&l,&u,&r,&r.inventory_sha256,&r.prefix_sha256).is_err());u.inflight=0;assert!(quota::completion_positions(&l,0,31,false,&u).is_err());u.stage_count=l.max_stage_count;assert!(quota::completion_positions(&l,0,1,true,&u).is_err());assert!(quota::admit(&l,&u,&r,&roots::hash(b"changed"),&r.prefix_sha256).is_err());let mut exhausted=r.clone();exhausted.inodes=25;assert!(quota::admit(&l,&u,&exhausted,&r.inventory_sha256,&r.prefix_sha256).is_err());}

fn cb(name:&str)->lab_control_store::ledger::ByteBinding{let x=b(name,b"fixture original control proof");lab_control_store::ledger::ByteBinding{kind:x.kind,root_id:x.root_id,relative_path:x.relative_path,sha256:x.sha256,size_bytes:x.size_bytes}}
fn control_limits()->lab_control_store::ledger::Limits{lab_control_store::ledger::Limits{max_record_bytes:65536,max_records:128,max_total_bytes:8*1024*1024,reserved_records:8}}
fn control_reader(f:&Fixture,path:&std::path::Path)->OriginalDirectory{let selection=Root::capture_fixture(path,"control",[b("alias",b"original"),b("ancestors",b"original"),b("acl",b"original")],f.scope.execution_scope.clone()).unwrap();OriginalDirectory::open(selection,Domain::Fixture).unwrap()}
#[test]fn host_readonly_control_matches_every_original_change_variant(){
 use lab_control_store::{custody,ledger::{self,Change,SlotPhase,Outcome,ReconcileAction,TrustedReconciliation}};
 let f=Fixture::new();let root=custody::Root::create_fixture(&f.base,"control").unwrap();let locks=root.acquire(custody::Rank::Journal,Duration::from_millis(100)).unwrap();let held=locks.borrow().unwrap();
 let mut confirmation=ledger::Ledger::initialize_fixture(&root,&held,"fixture-authority",control_limits(),f.scope.writer.clone()).unwrap();
 let reader=control_reader(&f,&f.base.join("control"));let mut ledger=ledger::Ledger::open(&root,&held,ledger::TrustedSelection{confirmation:confirmation.clone(),posture:ledger::Posture::Fixture}).unwrap();
 reader.control_originals(&confirmation).unwrap();
 let mut operation=f.scope.operation.clone();
 let changes=[Change::StoreEpoch{store_id:operation.store_id.clone(),prior_epoch:0,new_epoch:1,instance:operation.store_instance.clone(),fence_binding:cb("store")},
 Change::SlotEpoch{slot_id:operation.slot_id.clone(),prior_epoch:0,new_epoch:1,holder:operation.holder.clone(),slot_receipt_binding:cb("slot"),prior_disposition_binding:cb("prior"),containment_binding:cb("containment")},
 Change::SlotState{slot_id:operation.slot_id.clone(),epoch:1,holder:operation.holder.clone(),state:SlotPhase::Active,terminal_binding:cb("activation")},
 Change::Reserve{operation:operation.clone()},
 Change::Outcome{operation_id:operation.operation_id.clone(),fingerprint:operation.fingerprint.clone(),result_binding:cb("unknown"),outcome:Outcome::Quarantined}];
 for change in changes {let pending=ledger.append(&held,change).unwrap();let next=pending.requested_confirmation().clone();assert!(reader.control_originals(&confirmation).is_err());let originals=reader.control_originals(&next).unwrap();ledger.acknowledge(&held,pending,next.clone()).unwrap();confirmation=next;assert!(ledger.inspect().writable);reader.recheck_control(&originals,&confirmation).unwrap();}
 let selected=TrustedReconciliation{authority_domain:"fixture-authority".into(),root:root.identity(),writer:f.scope.writer.clone(),observed_head:confirmation.head.clone(),authority_binding:cb("repair"),action:ReconcileAction::Outcome{operation_id:operation.operation_id.clone(),fingerprint:operation.fingerprint.clone(),result_binding:cb("aborted"),outcome:Outcome::Aborted}};
 let pending=ledger.reconcile(&held,selected).unwrap();confirmation=pending.requested_confirmation().clone();reader.control_originals(&confirmation).unwrap();ledger.acknowledge(&held,pending,confirmation.clone()).unwrap();
 for state in [SlotPhase::Quarantined] {let pending=ledger.append(&held,Change::SlotState{slot_id:operation.slot_id.clone(),epoch:1,holder:operation.holder.clone(),state,terminal_binding:cb("slot-terminal")}).unwrap();confirmation=pending.requested_confirmation().clone();reader.control_originals(&confirmation).unwrap();ledger.acknowledge(&held,pending,confirmation.clone()).unwrap();}
 let pending=ledger.reconcile(&held,TrustedReconciliation{authority_domain:"fixture-authority".into(),root:root.identity(),writer:f.scope.writer.clone(),observed_head:confirmation.head.clone(),authority_binding:cb("close-repair"),action:ReconcileAction::Slot{slot_id:operation.slot_id.clone(),epoch:1,holder:operation.holder.clone(),terminal_binding:cb("closed")}}).unwrap();confirmation=pending.requested_confirmation().clone();reader.control_originals(&confirmation).unwrap();ledger.acknowledge(&held,pending,confirmation.clone()).unwrap();
 // A later epoch/event remains distinct; old event/operation identities do not reset.
 operation.operation_id="operation-2".into();operation.host_event="event-2".into();operation.store_epoch=2;operation.slot_epoch=2;
 for change in [Change::StoreEpoch{store_id:operation.store_id.clone(),prior_epoch:1,new_epoch:2,instance:operation.store_instance.clone(),fence_binding:cb("store2")},Change::SlotEpoch{slot_id:operation.slot_id.clone(),prior_epoch:1,new_epoch:2,holder:operation.holder.clone(),slot_receipt_binding:cb("slot2"),prior_disposition_binding:cb("closed"),containment_binding:cb("containment2")},Change::SlotState{slot_id:operation.slot_id.clone(),epoch:2,holder:operation.holder.clone(),state:SlotPhase::Active,terminal_binding:cb("activation2")},Change::Reserve{operation:operation.clone()},Change::Outcome{operation_id:operation.operation_id.clone(),fingerprint:operation.fingerprint.clone(),result_binding:cb("committed"),outcome:Outcome::Committed}] {let pending=ledger.append(&held,change).unwrap();confirmation=pending.requested_confirmation().clone();reader.control_originals(&confirmation).unwrap();ledger.acknowledge(&held,pending,confirmation.clone()).unwrap();}
 assert!(!reader.control_originals(&confirmation).unwrap().check_operation(&confirmation,Domain::Fixture,&operation).unwrap());
 assert_eq!(ledger.inspect().known_events,2);
}
#[test]fn host_verifier_and_accepted_ledger_reject_same_original_semantic_corruptions(){
 use lab_control_store::{custody,ledger::{self,Change,SlotPhase,Outcome}};
 let cases=["duplicate-event","duplicate-operation","wrong-slot","wrong-store","unresolved","outcome-twice","change-committed","wrong-header","wrong-writer","wrong-root","wrong-layout","missing-record","extra-record","bad-chain","wrong-epoch","unpermitted-reconcile"];
 for case in cases {
 let f=Fixture::new();let root=custody::Root::create_fixture(&f.base,"control").unwrap();let locks=root.acquire(custody::Rank::Journal,Duration::from_millis(100)).unwrap();let held=locks.borrow().unwrap();
 let mut selected=ledger::Ledger::initialize_fixture(&root,&held,"fixture-authority",control_limits(),f.scope.writer.clone()).unwrap();let mut ledger=ledger::Ledger::open(&root,&held,ledger::TrustedSelection{confirmation:selected.clone(),posture:ledger::Posture::Fixture}).unwrap();
 let o=f.scope.operation.clone();for change in [Change::StoreEpoch{store_id:o.store_id.clone(),prior_epoch:0,new_epoch:1,instance:o.store_instance.clone(),fence_binding:cb("store")},Change::SlotEpoch{slot_id:o.slot_id.clone(),prior_epoch:0,new_epoch:1,holder:o.holder.clone(),slot_receipt_binding:cb("slot"),prior_disposition_binding:cb("prior"),containment_binding:cb("containment")},Change::SlotState{slot_id:o.slot_id.clone(),epoch:1,holder:o.holder.clone(),state:SlotPhase::Active,terminal_binding:cb("activation")},Change::Reserve{operation:o.clone()}] {let p=ledger.append(&held,change).unwrap();selected=p.requested_confirmation().clone();ledger.acknowledge(&held,p,selected.clone()).unwrap();}
 if ["outcome-twice","change-committed"].contains(&case){let p=ledger.append(&held,Change::Outcome{operation_id:o.operation_id.clone(),fingerprint:o.fingerprint.clone(),result_binding:cb("done"),outcome:Outcome::Committed}).unwrap();selected=p.requested_confirmation().clone();ledger.acknowledge(&held,p,selected.clone()).unwrap();}
 drop(ledger);let reader=control_reader(&f,&f.base.join("control"));reader.control_originals(&selected).unwrap();
 let mut extra=None;
 match case {
 "wrong-header"=>selected.header_sha256=roots::hash(b"wrong"),
 "wrong-writer"=>selected.writer.instance="not-original-writer".into(),
 "wrong-root"=>selected.root.inode+=1,
 "wrong-layout"=>{let p=f.base.join("control/header.json");let mut header:serde_json::Value=serde_json::from_slice(&fs::read(&p).unwrap()).unwrap();header["layout"][1]["inode"]=json!(123);let raw=encode(&header).unwrap();fs::write(p,&raw).unwrap();selected.header_sha256=roots::hash(&raw);},
 "missing-record"=>{fs::remove_file(f.base.join("control/records/0000000000000002.json")).unwrap();},
 "bad-chain"=>{let p=f.base.join("control/records/0000000000000002.json");let mut record:serde_json::Value=serde_json::from_slice(&fs::read(&p).unwrap()).unwrap();record["previous_sha256"]=json!(roots::hash(b"wrong"));fs::write(p,encode(&record).unwrap()).unwrap();},
 "extra-record"=>extra=Some(serde_json::to_value(Change::Outcome{operation_id:o.operation_id.clone(),fingerprint:o.fingerprint.clone(),result_binding:cb("extra"),outcome:Outcome::Aborted}).unwrap()),
 "wrong-epoch"=>extra=Some(json!({"kind":"StoreEpoch","store_id":o.store_id,"prior_epoch":1,"new_epoch":3,"instance":o.store_instance,"fence_binding":cb("epoch")})),
 "outcome-twice"|"change-committed"=>extra=Some(serde_json::to_value(Change::Outcome{operation_id:o.operation_id.clone(),fingerprint:o.fingerprint.clone(),result_binding:cb("changed"),outcome:Outcome::Aborted}).unwrap()),
 "unpermitted-reconcile"=>extra=Some(json!({"kind":"Reconcile","action":{"action":"Outcome","operation_id":o.operation_id,"fingerprint":o.fingerprint,"result_binding":cb("bad-reconcile"),"outcome":"committed"},"authority_binding":cb("authority"),"observed_head":selected.head})),
 _=>{let mut next=o.clone();next.operation_id="next-operation".into();next.host_event="next-event".into();match case{"duplicate-event"=>next.host_event=o.host_event.clone(),"duplicate-operation"=>next.operation_id=o.operation_id.clone(),"wrong-slot"=>next.slot_epoch=2,"wrong-store"=>next.store_epoch=2,_=>{}}extra=Some(serde_json::to_value(Change::Reserve{operation:next}).unwrap());}
 }
 if let Some(change)=extra {let raw=encode(&json!({"schema_version":"lab-control-record/v1","authority_domain":"fixture-authority","sequence":selected.head.sequence+1,"previous_sha256":selected.head.sha256,"writer":selected.writer,"change":change})).unwrap();let path=f.base.join(format!("control/records/{:016}.json",selected.head.sequence+1));fs::write(&path,&raw).unwrap();fs::set_permissions(path,fs::Permissions::from_mode(0o600)).unwrap();if case!="extra-record"{selected.predecessor=selected.head.clone();selected.head.sequence+=1;selected.head.sha256=roots::hash(&raw);}}
 assert!(reader.control_originals(&selected).is_err(),"host accepted {case}");
 let reopened=ledger::Ledger::open(&root,&held,ledger::TrustedSelection{confirmation:selected,posture:ledger::Posture::Fixture});assert!(reopened.is_err()||!reopened.unwrap().inspect().writable,"Ledger accepted {case}");
 }
}
#[test]fn fixed_control_witness_verifies_prior_chain_and_lost_reply_original(){
 use lab_control_store::{custody,ledger::{self,Change}};
 let f=Fixture::new();let root=custody::Root::create_fixture(&f.base,"control").unwrap();let locks=root.acquire(custody::Rank::Journal,Duration::from_millis(100)).unwrap();let held=locks.borrow().unwrap();
 let genesis=ledger::Ledger::initialize_fixture(&root,&held,"fixture-authority",control_limits(),f.scope.writer.clone()).unwrap();let mut ledger=ledger::Ledger::open(&root,&held,ledger::TrustedSelection{confirmation:genesis.clone(),posture:ledger::Posture::Fixture}).unwrap();
 let reader=control_reader(&f,&f.base.join("control"));let wh=f.witness.exclusive(Duration::from_millis(100)).unwrap();let(signer,key)=signer("control-confirmation",11);let service=b("service.json",b"independently selected fixed host service");
 let mut witness=ControlWitness::open(&wh,&reader,&signer,key.clone(),service.clone(),f.scope.recipient.clone(),f.scope.channel_binding.clone(),genesis.clone(),genesis.clone(),0,roots::hash(&encode(&genesis).unwrap()),&[f.receipt.identity().clone(),f.stage.identity().clone()]).unwrap();
 let p=ledger.append(&held,Change::StoreEpoch{store_id:"fixture-store".into(),prior_epoch:0,new_epoch:1,instance:"fixture-instance".into(),fence_binding:cb("fence")}).unwrap();let desired=p.requested_confirmation().clone();
 let now=now_seconds().unwrap();let q=ControlCasRequest{schema_version:"lab-broker-control-cas-request/v1".into(),service_selection_binding:service.clone(),prior:genesis.clone(),desired:desired.clone(),recipient:f.scope.recipient.clone(),channel_binding:f.scope.channel_binding.clone(),challenge:roots::hash(b"fresh control cas"),not_before:now,expires_at:now+120};
 let mut forged=q.clone();forged.desired.head.sha256=roots::hash(b"not actual record");assert!(witness.compare_and_swap(&forged,&f.scope.recipient).is_err());assert!(fs::read_dir(f.base.join("witness")).unwrap().next().is_none());
 let response=witness.compare_and_swap(&q,&f.scope.recipient).unwrap();assert_eq!(witness.compare_and_swap(&q,&f.scope.recipient).unwrap(),response);
 let proof:ControlCasProof=signer.verify(&response).unwrap();assert_eq!(proof.request.desired,desired);ledger.acknowledge(&held,p,desired.clone()).unwrap();
 let inspection=ControlInspectionRequest{schema_version:"lab-broker-control-inspection-request/v1".into(),service_selection_binding:service.clone(),recipient:f.scope.recipient.clone(),channel_binding:f.scope.channel_binding.clone(),challenge:roots::hash(b"fresh after reply loss"),not_before:now,expires_at:now+120};
 let inspected:ControlInspectionProof=signer.verify(&witness.inspect(&inspection,&f.scope.recipient).unwrap()).unwrap();assert_eq!(witness.read_original(&ControlOriginalRequest{schema_version:"lab-broker-control-original-request/v1".into(),query:inspection.clone(),original_binding:inspected.original_proof_binding.unwrap()},&f.scope.recipient).unwrap(),response);assert_eq!(inspected.confirmation,desired);
 let mut stale=q.clone();stale.challenge=roots::hash(b"different request same slot");assert!(witness.compare_and_swap(&stale,&f.scope.recipient).is_err());
 drop(witness);assert!(ControlWitness::open(&wh,&reader,&signer,key.clone(),service.clone(),f.scope.recipient.clone(),f.scope.channel_binding.clone(),genesis.clone(),genesis.clone(),0,roots::hash(&encode(&genesis).unwrap()),&[]).is_err());
 let reopened=ControlWitness::open(&wh,&reader,&signer,key,service,f.scope.recipient.clone(),f.scope.channel_binding.clone(),genesis,desired.clone(),1,roots::hash(&response),&[f.receipt.identity().clone()]).unwrap();assert_eq!(reopened.confirmation(),&desired);
}

// Fixed host-serving/profile mechanics use separate enrolled fixture keys and
// original owned files. No boolean callback or real host authority is involved.
struct HostFixture {
    f:Fixture, input:Root, control:lab_control_store::custody::Root,
    selection:HostServiceSelection, selected_binding:Binding, signer_raw:Vec<u8>, manager_raw:Vec<u8>,
    signer:SelectedSigner, manager:SelectedSigner, manager_key:SigningKey, facts:HostFacts, query:HostQuery,
}
impl HostFixture {
 fn save(root:&Root,name:&str,raw:&[u8])->Binding {
  let path=std::path::Path::new(&root.selection().absolute_path).join(name);
  use std::io::Write;use std::os::unix::fs::OpenOptionsExt;
  let mut out=fs::OpenOptions::new().write(true).create_new(true).mode(0o600).open(path).unwrap();out.write_all(raw).unwrap();out.sync_all().unwrap();
  bound(&root.selection().root_id,name,raw).unwrap()
 }
 fn new()->Self {
  use lab_control_store::{custody,ledger};
  let mut f=Fixture::new();let control=custody::Root::create_fixture(&f.base,"control").unwrap();
  let locks=control.acquire(custody::Rank::Journal,Duration::from_millis(100)).unwrap();let held=locks.borrow().unwrap();
  let mut conf=ledger::Ledger::initialize_fixture(&control,&held,"fixture-authority",control_limits(),f.scope.writer.clone()).unwrap();
  let mut ledger=ledger::Ledger::open(&control,&held,ledger::TrustedSelection{confirmation:conf.clone(),posture:ledger::Posture::Fixture}).unwrap();
  for change in [ledger::Change::StoreEpoch{store_id:f.scope.operation.store_id.clone(),prior_epoch:0,new_epoch:1,instance:f.scope.operation.store_instance.clone(),fence_binding:cb("fence")},
    ledger::Change::SlotEpoch{slot_id:f.scope.operation.slot_id.clone(),prior_epoch:0,new_epoch:1,holder:f.scope.operation.holder.clone(),slot_receipt_binding:cb("slot"),prior_disposition_binding:cb("prior"),containment_binding:cb("containment")},
    ledger::Change::SlotState{slot_id:f.scope.operation.slot_id.clone(),epoch:1,holder:f.scope.operation.holder.clone(),state:ledger::SlotPhase::Active,terminal_binding:cb("active")}]{
    let p=ledger.append(&held,change).unwrap();conf=p.requested_confirmation().clone();ledger.acknowledge(&held,p,conf.clone()).unwrap();
  }drop(ledger);drop(held);drop(locks);f.scope.control_root=control.identity();f.ledger=conf.clone();
  let path=f.base.join("input");fs::create_dir(&path).unwrap();fs::set_permissions(&path,fs::Permissions::from_mode(0o700)).unwrap();
  let input=Root::open(Root::capture_fixture(&path,"input",[b("alias",b"alias"),b("anc",b"anc"),b("acl",b"acl")],f.scope.execution_scope.clone()).unwrap(),Domain::Fixture).unwrap();
  let enrollment=|purpose:&str,n:u8|{let key=SigningKey::from_bytes(&[n;32]);let raw=encode(&SignerSelection{schema_version:"lab-broker-fixed-signer/v1".into(),issuer_ref:format!("fixture-{purpose}"),purpose:purpose.into(),algorithm:"ed25519".into(),adapter:"owner-hex-v1".into(),public_key:wire::hex(&key.verifying_key().to_bytes()),domain:Domain::Fixture}).unwrap();
    let binding=Self::save(&input,&format!("{purpose}.json"),&raw);(SelectedSigner::select(&raw,&binding,Domain::Fixture,purpose).unwrap(),key,raw,binding)};
  let(signer,key,signer_raw,signer_binding)=enrollment("host-selection",21);
  let(manager,manager_key,manager_raw,manager_binding)=enrollment("host-profile-selection",22);
  let key_binding=Self::save(&input,"host.key",wire::hex(&key.to_bytes()).as_bytes());
  let native=Self::save(&input,"native-revocation.json",&encode(&json!({"schema_version":"fixture-native-revocation/v1","revoked":false})).unwrap());
  let heldreserve=Self::save(&input,"native-reserve.json",&encode(&json!({"schema_version":"fixture-held-capacity/v1","fixture_only":true})).unwrap());
  let now=now_seconds().unwrap();let issuer=Self::save(&input,"intent-enrollment.json",b"original independent fixture intent enrollment");
  let revocation=Self::save(&input,"revocation-1.json",&encode(&RevocationOriginal{schema_version:"lab-broker-host-revocation/v1".into(),issuer_enrollment_binding:issuer.clone(),native_original_binding:native.clone(),revoked:false,not_before:now-1,expires_at:now+240}).unwrap());
  let remaining=quota::Remaining{inventory_sha256:roots::hash(b"empty receipt inventory selected by fixture manager"),prefix_sha256:PrefixHead::genesis(&f.scope).unwrap().entry_sha256,bytes:8*1024*1024,inodes:4096};
  let capacity=Self::save(&input,"capacity-1.json",&encode(&CapacityOriginal{schema_version:"lab-broker-held-capacity/v1".into(),physical_root:f.receipt.identity().clone(),control_confirmation:conf.clone(),remaining:remaining.clone(),held_reservation_binding:heldreserve.clone(),not_before:now-1,expires_at:now+240}).unwrap());
  let control_sel=Root::capture_fixture(&f.base.join("control"),"control",[b("alias",b"alias"),b("anc",b"anc"),b("acl",b"acl")],f.scope.execution_scope.clone()).unwrap();
  let roots=vec![input.selection().clone(),control_sel,f.receipt.selection().clone(),f.stage.selection().clone()];
  let query=HostQuery{schema_version:"lab-broker-current-host-query/v1".into(),read_only:false,launch_selection_binding:b("launch",b"externally selected fixture launch"),operation_id:f.scope.operation.operation_id.clone(),original_fingerprint:f.scope.operation.fingerprint.clone(),frame_sha256:roots::hash(b"original fixture frame"),challenge:roots::hash(b"unpredictability supplied in actual FixedHost::query"),channel_binding:b("host-channel",b"host channel"),recipient:f.scope.recipient.clone()};
  let facts=HostFacts{schema_version:"lab-broker-current-host-facts/v1".into(),query:query.clone(),domain:Domain::Fixture,authority_domain:f.scope.authority_domain.clone(),operation:f.scope.operation.clone(),scope:f.scope.execution_scope.clone(),live_authority_scope:json!({}),ledger_confirmation:conf,control_root_id:"control".into(),operation_state:OriginalOperationState::AbsentReservable,roots:roots.clone(),quota_binding:b("quota",b"quota"),issuer_enrollment_binding:issuer,revocation_binding:revocation.clone(),issuer_revoked:false,observation_utc_seconds:now,not_before:now-1,expires_at:now+240,activation_expires_at:now+240,core_binding:b("core",b"core"),basis_binding:b("basis",b"basis"),selected_inputs:vec![],member_identity_originals:vec![],disclosure_subjects:vec![],recovery:None,remaining_capacity:remaining,capacity_custody_binding:capacity.clone(),capacity_root_id:"receipts".into(),additional_capacity_bindings:vec![],effect_inputs:EffectInputs{commit:None,restart:None,supervisor:None,derived:None},current_prefix_binding:b("prefix",b"prefix")};
  let template=Self::save(&input,"template-1.json",&encode(&facts).unwrap());
  let selection=HostServiceSelection{schema_version:"lab-broker-host-service/v1".into(),domain:Domain::Fixture,signer_binding,key_binding,template_binding:template,profile_issuer_binding:manager_binding,profile_recipient:f.scope.recipient.clone(),profile_channel_binding:b("manager-channel",b"separate manager channel"),revision:1,predecessor_binding:None,source_originals:vec![native,heldreserve,revocation,capacity],roots,recipient:f.scope.recipient.clone(),channel_binding:query.channel_binding.clone(),not_before:now-1,expires_at:now+240};
  let selected_binding=Self::save(&input,"service-1.json",&encode(&selection).unwrap());
  Self{f,input,control,selection,selected_binding,signer_raw,manager_raw,signer,manager,manager_key,facts,query}
 }
 fn service(&self)->HostService{HostService::load(&encode(&self.selection).unwrap(),&self.selected_binding,&self.signer_raw,&self.manager_raw,Domain::Fixture).unwrap()}
 fn successor(&self,facts:&HostFacts,originals:Vec<Binding>)->(HostServiceSelection,Binding,Vec<u8>){
  let mut next=self.selection.clone();next.revision=2;next.predecessor_binding=Some(self.selected_binding.clone());
  next.template_binding=Self::save(&self.input,"template-2.json",&encode(facts).unwrap());next.source_originals=originals;
  let binding=Self::save(&self.input,"service-2.json",&encode(&next).unwrap());let now=now_seconds().unwrap();
  let request=HostProfileRequest{schema_version:"lab-broker-host-profile-reselection/v1".into(),prior:self.selected_binding.clone(),next:binding.clone(),revision:2,recipient:next.profile_recipient.clone(),channel_binding:next.profile_channel_binding.clone(),challenge:roots::hash(b"independent fixture manager challenge"),not_before:now-1,expires_at:now+120};
  let raw=self.manager.sign(&self.manager_key,&request).unwrap();(next,binding,raw)
 }
}
#[test]fn fixed_host_absent_reservation_and_exact_signed_profile_advancement(){
 use lab_control_store::{custody,ledger};
 let f=HostFixture::new();let mut service=f.service();
 let raw=service.respond(&encode(&f.query).unwrap(),&f.query.recipient).unwrap();let facts:HostFacts=f.signer.verify(&raw).unwrap();assert_eq!(facts.operation_state,OriginalOperationState::AbsentReservable);
 let locks=f.control.acquire(custody::Rank::Journal,Duration::from_millis(100)).unwrap();let held=locks.borrow().unwrap();
 let mut ledger=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:f.facts.ledger_confirmation.clone(),posture:ledger::Posture::Fixture}).unwrap();
 let p=ledger.append(&held,ledger::Change::Reserve{operation:f.facts.operation.clone()}).unwrap();let confirmed=p.requested_confirmation().clone();
 // Physically valid tail alone is not current: old source profile refuses.
 assert!(service.respond(&encode(&f.query).unwrap(),&f.query.recipient).is_err());
 ledger.acknowledge(&held,p,confirmed.clone()).unwrap();
 let mut current=f.facts.clone();current.ledger_confirmation=confirmed.clone();current.operation_state=OriginalOperationState::Present{effect_eligible:true,outcome:None};
 let oldcap:CapacityOriginal=decode(&fs::read(f.input.selection().absolute_path.clone()+"/capacity-1.json").unwrap(),65536).unwrap();let mut cap=oldcap;cap.control_confirmation=confirmed;
 current.capacity_custody_binding=HostFixture::save(&f.input,"capacity-2.json",&encode(&cap).unwrap());
 let originals=f.selection.source_originals.iter().map(|b|if b==&f.facts.capacity_custody_binding{current.capacity_custody_binding.clone()}else{b.clone()}).collect();
 let(next,_,request)=f.successor(&current,originals);
 let mut forged:serde_json::Value=decode(&request,65536).unwrap();forged["payload"]["revision"]=json!(3);
 assert!(service.reselect(&encode(&forged).unwrap(),&next.profile_recipient,&next.profile_channel_binding).is_err());
 let receipt=service.reselect(&request,&next.profile_recipient,&next.profile_channel_binding).unwrap();let receipt:HostProfileReceipt=f.signer.verify(&receipt).unwrap();assert_eq!(receipt.result,"selected");
 let after:HostFacts=f.signer.verify(&service.respond(&encode(&f.query).unwrap(),&f.query.recipient).unwrap()).unwrap();assert_eq!(after.operation_state,current.operation_state);assert_eq!(after.ledger_confirmation,current.ledger_confirmation);
 assert!(service.reselect(&request,&next.profile_recipient,&next.profile_channel_binding).is_err());
}
#[test]fn host_effective_validity_is_intersection_and_expired_native_original_refuses(){
 let f=HostFixture::new();let mut facts=f.facts.clone();let now=now_seconds().unwrap();
 let mut cap:CapacityOriginal=decode(&fs::read(f.input.selection().absolute_path.clone()+"/capacity-1.json").unwrap(),65536).unwrap();cap.expires_at=now+3;
 facts.capacity_custody_binding=HostFixture::save(&f.input,"capacity-2.json",&encode(&cap).unwrap());
 let originals=f.selection.source_originals.iter().map(|b|if b==&f.facts.capacity_custody_binding{facts.capacity_custody_binding.clone()}else{b.clone()}).collect();
 let(next,_,request)=f.successor(&facts,originals);let mut service=f.service();service.reselect(&request,&next.profile_recipient,&next.profile_channel_binding).unwrap();
 let original=service.respond(&encode(&f.query).unwrap(),&f.query.recipient).unwrap();let value:HostFacts=f.signer.verify(&original).unwrap();assert_eq!(value.expires_at,cap.expires_at);
 while now_seconds().unwrap()<cap.expires_at{std::thread::sleep(Duration::from_millis(2));}
 assert!(service.respond(&encode(&f.query).unwrap(),&f.query.recipient).is_err());
}

#[test]fn member_declared_capacity_charged_once_across_full_boundary_chunks(){
 let mut l=limits();l.max_stage_bytes=65536;l.max_member_bytes=65536;
 let mut u=quota::Usage::default();assert!(quota::member(&l,&u,65536,true,32768).is_ok());
 u.stage_bytes=65536;u.member_count=1;assert!(quota::member(&l,&u,65536,false,32768).is_ok());
 assert!(quota::member(&l,&u,1,true,1).is_err());assert!(quota::member(&l,&u,0,true,0).is_ok());
 assert!(quota::member(&l,&u,65536,false,0).is_err());
}

#[path="dispatch_integration.rs"] mod dispatch_integration;

#[test]fn lost_local_prefix_confirmation_settles_original_after_request_expiry_without_new_cas(){
 let f=Fixture::new();let rh=f.receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=f.witness.exclusive(Duration::from_millis(100)).unwrap();let sh=f.stage.exclusive(Duration::from_millis(100)).unwrap();
 let scope_binding=b("original-scope.json",&encode(&f.scope).unwrap());
 let mut witness=PrefixWitness::open(&wh,f.scope.clone(),scope_binding.clone(),PrefixHead::genesis(&f.scope).unwrap(),&f.proof_signer,f.proof_key.clone()).unwrap();
 let mut journal=ReceiptJournal::open_empty(&rh,f.scope.clone(),limits()).unwrap();let response=complete_with_ttl(&f,&mut journal,&mut witness,&sh,3);drop(journal);
 let path=f.base.join("receipts/sequence-0000000000000001/confirmation.json");let original=fs::read(&path).unwrap();
 fs::rename(&path,f.base.join("preserved-lost-confirmation.json")).unwrap();
 assert!(RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&witness,false),&f.proof_signer,&f.response_signer).is_err());
 std::thread::sleep(Duration::from_secs(4));
 let current=f.current(&witness,true);let request=current.original_request().unwrap();
 let bytes=witness.read_original(&request,&f.scope.recipient,&f.scope.recipient,&request.query.channel_binding,&request.query.current_ledger_confirmation,&request.query.current_execution_scope).unwrap();assert_eq!(bytes,original);
 let mut altered=bytes.clone();altered[0]=b'[';assert!(current.verify_original(&altered,&f.proof_signer,&f.scope).is_err());assert!(!path.exists());
 let verified=current.verify_original(&bytes,&f.proof_signer,&f.scope).unwrap();
 let count=fs::read_dir(f.base.join("witness")).unwrap().count();
 RestartedPrefix::retain_missing_confirmation(&rh,&f.scope,&limits(),&current,&verified,&f.proof_signer,&f.response_signer).unwrap();
 assert_eq!(fs::read(&path).unwrap(),original);assert_eq!(fs::read_dir(f.base.join("witness")).unwrap().count(),count);
 let restored=RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),current,&f.proof_signer,&f.response_signer).unwrap();restored.validate_ranges(&sh).unwrap();assert!(restored.requires_reconciliation());
 assert_eq!(fs::read(f.base.join("receipts/sequence-0000000000000001/response.json")).unwrap(),response);
}

#[test]fn retained_payloads_remain_charged_across_operations_and_restart(){
 let f=Fixture::new();let sh=f.stage.exclusive(Duration::from_millis(100)).unwrap();let l=limits();
 let raw=f.frame(0);let frame=wire::Frame::decode(&raw).unwrap();let action=members::Action{request:frame.request().clone(),wire:frame.wire_digest().into(),fingerprint:f.scope.operation.fingerprint.clone(),domain:Domain::Fixture,stage_binding:None};
 let stage=members::Stage::create(&sh,&action).unwrap();let snapshot=stage.proposed_state().unwrap().clone();
 let active=payload_usage(&sh,&l,Some(&snapshot)).unwrap();assert_eq!(active.stage_count,1);assert_eq!(active.orphan_count,0);
 drop(stage); // An ended/unknown original operation has no live exemption.
 let old=payload_usage(&sh,&l,None).unwrap();assert_eq!(old.stage_count,1);assert_eq!(old.orphan_count,1);
 let other=roots::mkdir(sh.directory(),"other-original-generation").unwrap();use std::io::Write;
 let mut file=roots::open_child(&other,"member",libc::O_CREAT|libc::O_EXCL|libc::O_WRONLY,0o600,true).unwrap();file.write_all(&[7;31]).unwrap();file.sync_all().unwrap();other.sync_all().unwrap();
 let total=payload_usage(&sh,&l,None).unwrap();assert_eq!(total.stage_count,2);assert_eq!(total.orphan_count,2);assert_eq!(total.orphan_bytes,31);
 let before=owned_inventory_digest(&sh,l.max_retained_files,l.max_retained_bytes).unwrap();
 assert!(quota::completion_positions(&l,0,1,true,&total).is_err());
 assert_eq!(before,owned_inventory_digest(&sh,l.max_retained_files,l.max_retained_bytes).unwrap());
 assert_eq!(total,payload_usage(&sh,&l,None).unwrap()); // New operation/reopen cannot zero retained counts.
 let mut changed=snapshot.clone();changed.stage_identity.inode+=1;assert!(payload_usage(&sh,&l,Some(&changed)).is_err());
 std::os::unix::fs::symlink("other-original-generation",f.base.join("stage/alias")).unwrap();assert!(payload_usage(&sh,&l,None).is_err());
}

fn unfinished_entry(f:&Fixture,j:&mut ReceiptJournal<'_>)->(PendingSequence,PrefixRequest){
 let raw=f.frame(0);let frame=wire::Frame::decode(&raw).unwrap();let mut p=j.begin(&frame,&raw,&f.scope.operation.fingerprint,&f.ledger,&reserve(j)).unwrap();
 let response=encode(&authority::sign_receipt(&frame,"staging","PASS",None,serde_json::Value::Null,f.response_signer.issuer(),&f.response_key).unwrap()).unwrap();
 j.finish(&mut p,None,&response,"staging","PASS").unwrap();let now=now_seconds().unwrap();let q=j.confirmation_request(&p,roots::hash(b"original pending CAS"),now,now+120).unwrap();(p,q)
}
fn recovery_entry(f:&Fixture,j:&mut ReceiptJournal<'_>)->(PendingSequence,PrefixRequest){
 let subject=j.recovery_subject().unwrap();let raw_subject=encode(&subject).unwrap();let subject_binding=b("independently-selected-orphan-subject.json",&raw_subject);
 let sequence=j.consumed_requests().unwrap().keys().next_back().copied().unwrap()+1;
 let mut value:serde_json::Value=decode(&f.frame(sequence),65536).unwrap();value["request"]["verb"]=json!("reconcile_operation");value["request"]["payload"]=json!({"root_id":"receipts","subject_binding":subject_binding});
 let raw=encode(&value).unwrap();let frame=wire::Frame::decode(&raw).unwrap();let mut p=j.begin(&frame,&raw,&f.scope.operation.fingerprint,&f.ledger,&reserve(j)).unwrap();
 j.put(&mut p,"orphan-inventory.json",&raw_subject).unwrap();
 let response=encode(&authority::sign_receipt(&frame,"quarantined","UNKNOWN",Some("ORIGINAL_EFFECT_UNKNOWN"),serde_json::Value::Null,f.response_signer.issuer(),&f.response_key).unwrap()).unwrap();
 j.finish(&mut p,None,&response,"quarantined","UNKNOWN").unwrap();let now=now_seconds().unwrap();let q=j.confirmation_request(&p,roots::hash(b"fresh recovery CAS"),now,now+120).unwrap();(p,q)
}
#[test]fn no_relocation_recovery_and_delayed_original_cas_have_one_winner(){
 for winner in ["old-before-recovery","old-after-recovery","recovery"]{
 let f=Fixture::new();let rh=f.receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=f.witness.exclusive(Duration::from_millis(100)).unwrap();
 let mut w=PrefixWitness::open(&wh,f.scope.clone(),b("original-scope.json",&encode(&f.scope).unwrap()),PrefixHead::genesis(&f.scope).unwrap(),&f.proof_signer,f.proof_key.clone()).unwrap();
 let mut j=ReceiptJournal::open_empty(&rh,f.scope.clone(),limits()).unwrap();let(old_pending,old)=unfinished_entry(&f,&mut j);
 let original_bytes=fs::read(f.base.join("receipts/sequence-0000000000000001/frame.json")).unwrap();drop(old_pending);drop(j);
 if winner=="old-before-recovery"{
   w.compare_and_swap(&old,&f.scope.recipient).unwrap();
   // A fresh independent selected head prevents creating a competing recovery
   // against the stale genesis; first settle the exact original proof.
   assert!(RestartedPrefix::inspect_recovery(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).is_err());
   let current=f.current(&w,false);let query=current.original_request().unwrap();let raw=w.read_original(&query,&f.scope.recipient,&f.scope.recipient,&query.query.channel_binding,&f.ledger,&f.scope.execution_scope).unwrap();let proof=current.verify_original(&raw,&f.proof_signer,&f.scope).unwrap();
   RestartedPrefix::retain_missing_confirmation(&rh,&f.scope,&limits(),&current,&proof,&f.proof_signer,&f.response_signer).unwrap();
   let restored=RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).unwrap().into_recovery_journal();assert!(restored.recovery_subject().is_err());continue;
 }
 let mut restored=RestartedPrefix::inspect_recovery(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).unwrap().into_recovery_journal();
 assert_eq!(restored.consumed_requests().unwrap().get(&0),Some(&old.wire_sha256));
 let(p,q)=recovery_entry(&f,&mut restored);assert_eq!(q.next.ordinal,1);assert_eq!(q.sequence,1);assert!(q.entry_binding.relative_path.starts_with("recovery-"));
 if winner=="old-after-recovery"{
    w.compare_and_swap(&old,&f.scope.recipient).unwrap();assert!(w.compare_and_swap(&q,&f.scope.recipient).is_err());drop(p);drop(restored);
    let current=f.current(&w,false);let query=current.original_request().unwrap();let raw=w.read_original(&query,&f.scope.recipient,&f.scope.recipient,&query.query.channel_binding,&f.ledger,&f.scope.execution_scope).unwrap();let proof=current.verify_original(&raw,&f.proof_signer,&f.scope).unwrap();
    RestartedPrefix::retain_missing_confirmation(&rh,&f.scope,&limits(),&current,&proof,&f.proof_signer,&f.response_signer).unwrap();
    assert!(RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).is_err());
    let again=RestartedPrefix::inspect_recovery(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).unwrap().into_recovery_journal();
    assert_eq!(again.recovery_subject().unwrap().tails.len(),1);assert_eq!(again.consumed_requests().unwrap().len(),2);
 }else{
    let raw=w.compare_and_swap(&q,&f.scope.recipient).unwrap();assert!(w.compare_and_swap(&old,&f.scope.recipient).is_err());
    let proof=VerifiedPrefix::verify(&raw,&f.proof_signer,&q,now_seconds().unwrap()).unwrap();restored.confirm(p,proof,&f.response_signer).unwrap();drop(restored);
    let mut again=RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&w,false),&f.proof_signer,&f.response_signer).unwrap().into_recovery_journal();
    let all=again.consumed_requests().unwrap();assert_eq!(all.len(),2);assert_eq!(all[&0],old.wire_sha256);
    let frame=wire::Frame::decode(&original_bytes).unwrap();assert!(again.begin(&frame,&original_bytes,&f.scope.operation.fingerprint,&f.ledger,&reserve(&again)).is_err());
    let mut changed:serde_json::Value=decode(&original_bytes,65536).unwrap();changed["request"]["request_id"]=json!("changed-same-sequence");let bytes=encode(&changed).unwrap();let frame=wire::Frame::decode(&bytes).unwrap();assert!(again.begin(&frame,&bytes,&f.scope.operation.fingerprint,&f.ledger,&reserve(&again)).is_err());
 }
 assert_eq!(fs::read(f.base.join("receipts/sequence-0000000000000001/frame.json")).unwrap(),original_bytes);
 }
}

#[test]fn terminal_reserve_survives_payload_exhaustion_without_extra_effect_budget(){
 let l=limits();let mut u=quota::Usage::default();u.stage_count=l.max_stage_count+1;u.orphan_count=l.max_orphan_count+1;u.orphan_bytes=l.max_orphan_bytes+1;
 let r=quota::Remaining{inventory_sha256:roots::hash(b"exact current inventory"),prefix_sha256:roots::hash(b"exact prefix"),bytes:l.cleanup_bytes().unwrap(),inodes:quota::CLEANUP_FILES+1};
 assert!(quota::admit(&l,&u,&r,&r.inventory_sha256,&r.prefix_sha256).is_err());assert!(quota::admit_cleanup(&l,&u,&r,&r.inventory_sha256,&r.prefix_sha256).is_ok());
 let mut short=r.clone();short.bytes-=1;assert!(quota::admit_cleanup(&l,&u,&short,&r.inventory_sha256,&r.prefix_sha256).is_err());
 u.sequences=l.max_sequences;assert!(quota::admit_cleanup(&l,&u,&r,&r.inventory_sha256,&r.prefix_sha256).is_err());
}

#[test]fn derived_namespace_requires_physical_endpoint_disjointness(){
 let f=Fixture::new();let child=f.base.join("stage/managed-child");fs::create_dir(&child).unwrap();fs::set_permissions(&child,fs::Permissions::from_mode(0o700)).unwrap();
 let child=Root::open(Root::capture_fixture(&child,"managed-child",[b("alias",b"a"),b("ancestor",b"b"),b("acl",b"c")],f.scope.execution_scope.clone()).unwrap(),Domain::Fixture).unwrap();
 let sh=f.stage.exclusive(Duration::from_millis(100)).unwrap();let ch=child.exclusive(Duration::from_millis(100)).unwrap();let rh=f.receipt.exclusive(Duration::from_millis(100)).unwrap();
 assert!(disjoint_endpoints(&ch,&sh).is_err());assert!(disjoint_endpoints(&sh,&ch).is_err());assert!(disjoint_endpoints(&sh,&sh).is_err());
 disjoint_endpoints(&rh,&sh).unwrap();disjoint_endpoints(&sh,&rh).unwrap();
 assert!(f.base.join("stage/managed-child").is_dir());assert_eq!(fs::read_dir(f.base.join("receipts")).unwrap().count(),0);
}

#[test]fn advanced_writer_recovery_uses_signed_current_admission_and_immutable_history(){
 let f=Fixture::new();let rh=f.receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=f.witness.exclusive(Duration::from_millis(100)).unwrap();let sh=f.stage.exclusive(Duration::from_millis(100)).unwrap();
 let scope_original=encode(&f.scope).unwrap();let mut w=PrefixWitness::open(&wh,f.scope.clone(),b("original-scope.json",&scope_original),PrefixHead::genesis(&f.scope).unwrap(),&f.proof_signer,f.proof_key.clone()).unwrap();
 let mut original=ReceiptJournal::open_empty(&rh,f.scope.clone(),limits()).unwrap();let response=complete(&f,&mut original,&mut w,&sh);drop(original);
 let checkpoint=f.current(&w,true);let mut current=f.ledger.clone();current.writer=WriterFence{instance:"later-writer".into(),epoch:2};
 let restart=RestartedPrefix::inspect_recovery(&rh,f.scope.clone(),limits(),checkpoint,&f.proof_signer,&f.response_signer).unwrap();let mut journal=restart.into_recovery_journal();
 let producer=f.frame(1);let producer_frame=wire::Frame::decode(&producer).unwrap();assert_eq!(journal.begin(&producer_frame,&producer,&f.scope.operation.fingerprint,&current,&reserve(&journal)).err().unwrap().0,"RESTART_NO_PRODUCER");
 let mut v:serde_json::Value=decode(&producer,65536).unwrap();v["request"]["verb"]=json!("close_family");v["request"]["payload"]=json!({"root_id":"receipts","subject_binding":b("closure",b"fixture original closure")});let raw=encode(&v).unwrap();let frame=wire::Frame::decode(&raw).unwrap();
 assert!(journal.begin_terminal(&frame,&raw,&f.scope.operation.fingerprint,&f.ledger,&reserve(&journal)).is_err());
 let mut pending=journal.begin_terminal(&frame,&raw,&f.scope.operation.fingerprint,&current,&reserve(&journal)).unwrap();
 let signed=encode(&authority::sign_receipt(&frame,"terminal","UNKNOWN",Some("FIXTURE_ACCOUNTING"),serde_json::Value::Null,f.response_signer.issuer(),&f.response_key).unwrap()).unwrap();journal.finish(&mut pending,None,&signed,"terminal","UNKNOWN").unwrap();
 let now=now_seconds().unwrap();let q=journal.confirmation_request(&pending,roots::hash(b"later writer CAS"),now,now+60).unwrap();
 assert_eq!(q.scope,f.scope);assert_eq!(q.ledger_confirmation.writer,current.writer);assert!(q.current_admission.is_some());
 let mut altered=q.clone();altered.current_admission.as_mut().unwrap().original[0]^=1;assert!(w.compare_and_swap(&altered,&f.scope.recipient).is_err());
 let proof=w.compare_and_swap(&q,&f.scope.recipient).unwrap();let verified=VerifiedPrefix::verify(&proof,&f.proof_signer,&q,now).unwrap();journal.confirm(pending,verified,&f.response_signer).unwrap();drop(journal);
 let replay=RestartedPrefix::inspect(&rh,f.scope.clone(),limits(),f.current(&w,true),&f.proof_signer,&f.response_signer).unwrap();assert!(replay.requires_reconciliation());
 assert_eq!(scope_original,encode(&f.scope).unwrap());assert_eq!(response,fs::read(f.base.join("receipts/sequence-0000000000000001/response.json")).unwrap());
}

#[path="prefix_service_tests.rs"] mod prefix_service_tests;
