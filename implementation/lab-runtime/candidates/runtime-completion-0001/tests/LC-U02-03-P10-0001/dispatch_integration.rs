use super::*;
use crate::{state,roots::Exclusive};
#[path="generation_fixture.rs"] mod generation_fixture;
use crate::dispatcher::*;
use std::{os::fd::{OwnedFd,FromRawFd,AsRawFd},collections::BTreeMap};
use serde_json::Value;
fn pair(name:&str,peer:&Caller)->(OwnedFd,ChannelSelection,Channel){
 let mut fds=[-1;2];assert_eq!(unsafe{libc::socketpair(libc::AF_UNIX,libc::SOCK_SEQPACKET|libc::SOCK_CLOEXEC,0,fds.as_mut_ptr())},0);
 let a=unsafe{OwnedFd::from_raw_fd(fds[0])};let bfd=unsafe{OwnedFd::from_raw_fd(fds[1])};
 let selection=|fd:i32|{let mut st:libc::stat=unsafe{std::mem::zeroed()};assert_eq!(unsafe{libc::fstat(fd,&mut st)},0);ChannelSelection{schema_version:"lab-broker-fixed-channel/v1".into(),channel_binding:b(name,name.as_bytes()),device:st.st_dev,inode:st.st_ino,peer:peer.clone(),max_packet_bytes:65536,timeout_ms:10000}};
 let asel=selection(a.as_raw_fd());let bsel=selection(bfd.as_raw_fd());(a,asel,Channel::from_selected(bfd,bsel).unwrap())
}
struct Intent{key:SigningKey,basis:Value,core:Value,scope:Value,enrollment:Vec<u8>}
impl Intent{
 fn new(f:&mut HostFixture)->Self{
  let now=now_seconds().unwrap();let key=SigningKey::from_bytes(&[7;32]);
  let scope=json!({"principal_ref":f.f.scope.execution_scope.principal_ref,"scope_ref":"fixture-scope","operation":"produce","store_id":f.f.scope.execution_scope.store_id,"instance_id":f.f.scope.execution_scope.instance_id,"activation_binding":f.f.scope.execution_scope.activation_binding,"slot_epoch":1,"intent_binding":b("intent",b"authentic independently enrolled fixture intent")});
  let limits=json!({"max_total_bytes":64,"max_actions":32,"max_frame_bytes":65536,"max_chunk_bytes":32768});let slots=json!([{"root_id":"stage","member":"empty.bin","preimage_binding":null,"max_bytes":0}]);
  let basis=authority::signed_record(&json!({"schema_version":"lab-completion-effect-authority-basis/v1","basis_id":"fixture-basis","scope":scope,"limits":limits,"output_slots":slots,"not_before":now-1,"expires_at":now+240}),"fixture-issuer",&key).unwrap();
  let original=b("original-request",b"original fixture request");
  let core=json!({"schema_version":"lab-completion-operation-request-core/v1","operation_id":"operation-1","idempotency_key":"idempotency-1","original_request_binding":original,"semantic_target_binding":b("target",b"target"),"source_cut_binding":b("cut",b"cut"),"effect_selection_binding":b("effect",b"effect"),"authority_basis_binding":wire::content_digest(&encode(&basis).unwrap()),"scope":scope,"limits":limits,"output_slots":slots,"operation_expires_at":now+230});
  f.f.scope.operation.fingerprint=authority::operation_fingerprint(&core).unwrap();f.f.scope.operation.original_request_sha256=original.sha256;f.f.scope.operation.issuer="fixture-issuer".into();
  f.facts.operation=f.f.scope.operation.clone();f.facts.live_authority_scope=scope.clone();f.query.original_fingerprint=f.f.scope.operation.fingerprint.clone();
  let enrollment=encode(&json!({"schema_version":"lab-completion-issuer-enrollment/v1","issuer_ref":"fixture-issuer","adapter":"owner-hex-v1","purpose":"broker-intent","algorithm":"ed25519","public_key":wire::hex(&key.verifying_key().to_bytes()),"trust_domain":"fixture"})).unwrap();
  Self{key,basis,core,scope,enrollment}
 }
 fn frame(&self,verb:&str,seq:u64,phase:&str,stage:Value)->Vec<u8>{
  let now=now_seconds().unwrap();let payload=json!({"root_id":"stage","stage_name":"owned-stage","max_bytes":self.core["limits"]["max_total_bytes"]});
  let mut request=json!({"schema_version":"lab-completion-broker-request/v1","request_id":format!("request-{seq}"),"operation_id":"operation-1","sequence":seq,"activation_binding":self.scope["activation_binding"],"store_id":self.scope["store_id"],"instance_id":self.scope["instance_id"],"slot_epoch":1,"principal_ref":self.scope["principal_ref"],"verb":verb,"intent_binding":self.scope["intent_binding"],"authorization_binding":wire::content_digest(b""),"payload":payload});
  let grant=json!({"kind":"empty-stage","root_id":"stage","stage_binding":stage,"member":null,"preimage_binding":null,"full_sha256":null,"full_length":0,"chunk_size":0,"sequence_start":seq,"chunks":[{"sequence":seq,"offset":0,"length":0,"core_sha256":wire::hash(&wire::signing_bytes(&wire::authorization_core(&request).unwrap()).unwrap())}]});
  let permit=authority::signed_record(&json!({"schema_version":"lab-completion-broker-permit/v1","permit_id":format!("permit-{seq}"),"operation_fingerprint":authority::operation_fingerprint(&self.core).unwrap(),"basis_binding":self.core["authority_basis_binding"],"scope":self.scope,"limits":self.core["limits"],"allowed_verb":verb,"allowed_phase":phase,"not_before":now-1,"expires_at":now+120,"grant":grant}),"fixture-issuer",&self.key).unwrap();request["authorization_binding"]=wire::content_digest(&encode(&permit).unwrap());encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":request,"permit":permit})).unwrap()
 }
}
#[test]fn fixed_services_full_chronological_commit_and_pending_cold(){full_lifecycle(0)}
#[test]fn issuer_revoked_after_pending_cold_blocks_original_outcome(){full_lifecycle(1)}
#[test]fn altered_cold_request_cannot_complete_pending_sequence(){full_lifecycle(2)}
#[test]fn authenticated_profile_cannot_replace_first_acknowledged_capture(){full_lifecycle(3)}
#[test]fn published_receipt_live_and_readonly_restart_preserve_original_bytes(){full_lifecycle(4)}
#[test]fn session_retained_sibling_count_refuses_before_new_stage(){full_lifecycle(5)}
#[test]fn session_retained_sibling_bytes_refuse_before_new_stage(){full_lifecycle(6)}
#[test]fn session_retained_sibling_exact_boundary_allows_stage(){full_lifecycle(7)}
#[test]fn missing_original_frame_has_fixed_authorized_unknown_inspection(){full_lifecycle(8)}
#[test]fn corrupt_control_history_has_fixed_authorized_unknown_inspection(){full_lifecycle(9)}
#[test]fn corrupt_original_confirmation_has_fixed_authorized_unknown_inspection(){full_lifecycle(10)}
#[test]fn receipt_name_bound_overflow_has_fixed_authorized_unknown_inspection(){full_lifecycle(11)}
fn full_lifecycle(mode:u8){
 use lab_control_store::{custody,ledger};
 let mut f=HostFixture::new();let mut intent=Intent::new(&mut f);if matches!(mode,14|15){intent.select_nonempty(&mut f);}
 if matches!(mode,5|6|7){
  use std::io::Write;
  let retained=if mode==5{2}else{1};for n in 0..retained{
   let p=f.f.base.join(format!("stage/retained-original-{n}"));fs::create_dir(&p).unwrap();fs::set_permissions(&p,fs::Permissions::from_mode(0o700)).unwrap();
   let mut options=fs::OpenOptions::new();use std::os::unix::fs::OpenOptionsExt;let mut out=options.write(true).create_new(true).mode(0o600).open(p.join("original.bin")).unwrap();
   out.write_all(&vec![17;if mode==6{65537}else if mode==7{65536}else{1}]).unwrap();out.sync_all().unwrap();
  }
 }
 let jp=f.f.base.join("control/generation-journal");fs::create_dir(&jp).unwrap();fs::set_permissions(&jp,fs::Permissions::from_mode(0o700)).unwrap();
 let jr=Root::open(Root::capture_fixture(&jp,"generation-journal",[b("alias",b"a"),b("anc",b"b"),b("acl",b"c")],f.f.scope.execution_scope.clone()).unwrap(),Domain::Fixture).unwrap();
 f.facts.roots.push(jr.selection().clone());f.selection.roots.push(jr.selection().clone());let static_generation=generation_fixture::static_generation(&f,&jr);let caller=f.f.scope.recipient.clone();
 let(hfd,hsel,hserver)=pair("host-fixed",&caller);let(pfd,psel,pserver)=pair("prefix-fixed",&caller);let(cfd,csel,cserver)=pair("control-fixed",&caller);let(mfd,msel,mserver)=pair("profile-manager-fixed",&caller);let(_clientfd,client_sel,_clientserver)=pair("worker-fixed",&caller);
 f.f.scope.channel_binding=psel.channel_binding.clone();
 let scope_binding=HostFixture::save(&f.input,"session-scope.json",&encode(&f.f.scope).unwrap());let core_binding=HostFixture::save(&f.input,"session-core.json",&encode(&intent.core).unwrap());let basis_binding=HostFixture::save(&f.input,"session-basis.json",&encode(&intent.basis).unwrap());let issuer_binding=HostFixture::save(&f.input,"session-issuer.json",&intent.enrollment);let quota_binding=HostFixture::save(&f.input,"session-quota.json",&encode(&limits()).unwrap());
 let response_raw=encode(&SignerSelection{schema_version:"lab-broker-fixed-signer/v1".into(),issuer_ref:"fixture-broker-response".into(),purpose:"broker-response".into(),algorithm:"ed25519".into(),adapter:"owner-hex-v1".into(),public_key:wire::hex(&f.f.response_key.verifying_key().to_bytes()),domain:Domain::Fixture}).unwrap();let response_binding=HostFixture::save(&f.input,"session-response-signer.json",&response_raw);let response_signer=SelectedSigner::select(&response_raw,&response_binding,Domain::Fixture,"broker-response").unwrap();let key_binding=HostFixture::save(&f.input,"session-response.key",wire::hex(&f.f.response_key.to_bytes()).as_bytes());
 let launch=LaunchSelection{schema_version:"lab-broker-fixed-launch/v1".into(),domain:Domain::Fixture,authority_domain:f.f.scope.authority_domain.clone(),operation:f.f.scope.operation.clone(),original_scope_binding:scope_binding.clone(),host_signer_binding:f.selection.signer_binding.clone(),receipt_signer_binding:response_binding.clone(),prefix_signer_binding:f.f.proof_signer.binding().clone(),intent_signer_binding:issuer_binding.clone(),control_signer_binding:signer("control-confirmation",29).0.binding().clone(),control_service_binding:b("control-service",b"selected fixed control witness"),source_binding:b("source",b"fixture source"),profile_binding:b("profile",b"fixture profile"),namespace_qualification_binding:b("namespace",b"fixture namespace"),caller:caller.clone(),broker_identity:caller.clone(),host_channel:hsel.clone(),prefix_channel:psel.clone(),control_channel:csel.clone(),client_channel:client_sel,allowed_root_ids:f.facts.roots.iter().map(|r|r.root_id.clone()).collect(),core_binding:core_binding.clone(),basis_binding:basis_binding.clone(),quota_binding:quota_binding.clone(),execution_scope:f.f.scope.execution_scope.clone(),max_observation_age_seconds:10};
 let static_client=Channel::from_selected(_clientfd,launch.client_channel.clone()).unwrap();
 let launch_raw=encode(&launch).unwrap();let launch_binding=HostFixture::save(&f.input,"session-launch.json",&launch_raw);
 let runtime=RuntimeSelection{schema_version:"lab-broker-runtime-selection/v1".into(),receipt_root_id:"receipts".into(),stage_root_id:"stage".into(),generation_root_id:"stage".into(),generation_journal_root_id:"generation-journal".into(),control_root_id:"control".into(),original_scope_binding:scope_binding.clone(),limits_binding:quota_binding.clone(),receipt_signer_binding:response_binding,receipt_private_key_binding:key_binding,commit_selection_binding:None,restart_selection_binding:None,supervisor_proof_binding:None,derived_selection_binding:None,global_order_binding:b("global-lock-order",b"fixed fixture global order")};let runtime_raw=encode(&runtime).unwrap();let runtime_binding=HostFixture::save(&f.input,"session-runtime.json",&runtime_raw);
 let now=now_seconds().unwrap();f.facts.query.launch_selection_binding=launch_binding.clone();f.facts.query.channel_binding=hsel.channel_binding.clone();f.facts.query.original_fingerprint=f.f.scope.operation.fingerprint.clone();
 f.facts.issuer_enrollment_binding=issuer_binding.clone();f.facts.core_binding=core_binding;f.facts.basis_binding=basis_binding;f.facts.quota_binding=quota_binding;f.facts.selected_inputs=vec![scope_binding.clone(),runtime_binding.clone(),runtime.receipt_signer_binding.clone(),runtime.receipt_private_key_binding.clone()];
 let native=f.selection.source_originals[0].clone();let reserve=f.selection.source_originals[1].clone();f.facts.revocation_binding=HostFixture::save(&f.input,"session-revocation.json",&encode(&RevocationOriginal{schema_version:"lab-broker-host-revocation/v1".into(),issuer_enrollment_binding:issuer_binding,native_original_binding:native.clone(),revoked:false,not_before:now-1,expires_at:now+240}).unwrap());
 f.facts.remaining_capacity.inventory_sha256=roots::hash(&encode(&Vec::<(String,roots::Identity,u64,String)>::new()).unwrap());f.facts.remaining_capacity.prefix_sha256=PrefixHead::genesis(&f.f.scope).unwrap().entry_sha256;
 let cap=CapacityOriginal{schema_version:"lab-broker-held-capacity/v1".into(),physical_root:f.f.receipt.identity().clone(),control_confirmation:f.facts.ledger_confirmation.clone(),remaining:f.facts.remaining_capacity.clone(),held_reservation_binding:reserve.clone(),not_before:now-1,expires_at:now+240};f.facts.capacity_custody_binding=HostFixture::save(&f.input,"session-capacity.json",&encode(&cap).unwrap());
 f.selection.template_binding=HostFixture::save(&f.input,"session-template.json",&encode(&f.facts).unwrap());f.selection.channel_binding=hsel.channel_binding.clone();f.selection.profile_channel_binding=msel.channel_binding.clone();f.selection.source_originals=vec![native,reserve,f.facts.revocation_binding.clone(),f.facts.capacity_custody_binding.clone()];f.selected_binding=HostFixture::save(&f.input,"session-service.json",&encode(&f.selection).unwrap());
 let mut host_service=f.service();let host=FixedHost::load(&launch_raw,&launch_binding,&f.signer_raw,hfd,Domain::Fixture).unwrap();let manager_channel=Channel::from_selected(mfd,msel.clone()).unwrap();
 let(control_signer,control_key)=signer("control-confirmation",29);let control_service=b("control-service",b"selected fixed control witness");let control_client=FixedControlClient::new(Channel::from_selected(cfd,csel.clone()).unwrap(),signer("control-confirmation",29).0,control_service.clone(),caller.clone()).unwrap();
 let prefix_client=FixedPrefixClient::new(Channel::from_selected(pfd,psel.clone()).unwrap(),signer("receipt-prefix",3).0);
 let control_selection=f.facts.roots.iter().find(|r|r.root_id=="control").unwrap().clone();let control_root=Root::open(control_selection.clone(),Domain::Fixture).unwrap();let control_reader=OriginalDirectory::open(control_selection,Domain::Fixture).unwrap().with_children(&[jr.selection().clone()]).unwrap();let receipt_reader=OriginalDirectory::open(f.f.receipt.selection().clone(),Domain::Fixture).unwrap();
 let cwpath=f.f.base.join("control-witness");fs::create_dir(&cwpath).unwrap();fs::set_permissions(&cwpath,fs::Permissions::from_mode(0o700)).unwrap();let cwroot=Root::open(Root::capture_fixture(&cwpath,"control-witness",[b("a",b"a"),b("b",b"b"),b("c",b"c")],f.f.scope.execution_scope.clone()).unwrap(),Domain::Fixture).unwrap();
 let locks=f.control.acquire(custody::Rank::Journal,Duration::from_millis(100)).unwrap();let held=locks.borrow().unwrap();let ih=f.input.exclusive(Duration::from_millis(100)).unwrap();let rh=f.f.receipt.exclusive(Duration::from_millis(100)).unwrap();let sh=f.f.stage.exclusive(Duration::from_millis(100)).unwrap();let ch=control_root.exclusive(Duration::from_millis(100)).unwrap();let jh=jr.exclusive(Duration::from_millis(100)).unwrap();let ph=f.f.witness.exclusive(Duration::from_millis(100)).unwrap();let cwh=cwroot.exclusive(Duration::from_millis(100)).unwrap();
 let mut pw=PrefixWitness::open(&ph,f.f.scope.clone(),scope_binding.clone(),PrefixHead::genesis(&f.f.scope).unwrap(),&f.f.proof_signer,f.f.proof_key.clone()).unwrap();
 let mut cw=ControlWitness::open(&cwh,&control_reader,&control_signer,control_key,control_service,caller.clone(),csel.channel_binding.clone(),f.facts.ledger_confirmation.clone(),f.facts.ledger_confirmation.clone(),0,roots::hash(&encode(&f.facts.ledger_confirmation).unwrap()),&[f.f.receipt.identity().clone(),f.f.stage.identity().clone()]).unwrap();
 let query=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:f.f.scope.history_key().unwrap(),recipient:caller.clone(),channel_binding:psel.channel_binding.clone(),challenge:roots::hash(b"current genesis"),current_ledger_confirmation:f.facts.ledger_confirmation.clone(),current_execution_scope:f.f.scope.execution_scope.clone(),not_before:now-1,expires_at:now+120};
 let current=CurrentPrefix::verify(&pw.inspect(&query,&caller,&caller,&psel.channel_binding,&f.facts.ledger_confirmation,&f.f.scope.execution_scope).unwrap(),&f.f.proof_signer,&query,&f.f.scope,&scope_binding,now).unwrap();
 let reserve_frame=intent.frame("reserve_family",0,"absent",Value::Null);let create_frame=intent.frame("create_stage",1,"reserved",Value::Null);
 let (sender,receiver)=std::sync::mpsc::channel();
 std::thread::scope(|threads|{
  let host_task=threads.spawn(||{
   host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();
   host_service.serve_profile_one(&mserver).unwrap();if mode==16{assert_eq!(host_service.serve_one(&hserver).unwrap_err().0,"HOST_ADDITIONAL_CAPACITY_JOIN");return}host_service.serve_one(&hserver).unwrap();
   if (8..=11).contains(&mode){host_service.serve_one(&hserver).unwrap();return}
   if (5..=11).contains(&mode)||matches!(mode,16|17){return}
   if matches!(mode,14|15){host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();if mode==15{return}host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();return}
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();
   if mode==3{host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();return}
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
   if mode==1{host_service.serve_profile_one(&mserver).unwrap();}if mode!=13{host_service.serve_one(&hserver).unwrap();}
   if mode==4{host_service.serve_profile_one(&mserver).unwrap();for _ in 0..3{host_service.serve_one(&hserver).unwrap();}}
  });
  let control_task=threads.spawn(||{cw.serve_one(&cserver).unwrap();sender.send(cw.confirmation().clone()).unwrap();if matches!(mode,0|4|12){cw.serve_one(&cserver).unwrap();sender.send(cw.confirmation().clone()).unwrap();}});
  let receipt_ref=&receipt_reader;let control_ref=&control_reader;let response_ref=&response_signer;let caller_ref=&caller;
  let prefix_task=threads.spawn(move ||{let mut current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();for i in 0..if matches!(mode,0|4|12){5}else if mode==3{3}else if matches!(mode,7|15){2}else if (5..=11).contains(&mode)||matches!(mode,16|17){1}else{4}{
   let raw=pserver.receive().unwrap();let q:PrefixRequest=decode(&raw,65536).unwrap();if i==4{current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();}
   let response=pw.confirm_originals(&q,caller_ref,receipt_ref,control_ref,&current,&limits(),response_ref).unwrap();pserver.send(&response).unwrap();}
   if mode==4{let raw=pserver.receive().unwrap();let q:PrefixInspectionRequest=decode(&raw,65536).unwrap();let response=pw.inspect(&q,caller_ref,caller_ref,&q.channel_binding,&current,&q.current_execution_scope).unwrap();pserver.send(&response).unwrap();}
  });
  let facts=host.query(&wire::Frame::decode(&reserve_frame).unwrap()).unwrap();let roots=BTreeMap::from([("input".into(),&ih),("receipts".into(),&rh),("stage".into(),&sh),("control".into(),&ch),("generation-journal".into(),&jh)]);
  let mut session=Session::start(&host,&control_client,&prefix_client,&f.control,&held,roots.clone(),&runtime_raw,runtime_binding.clone(),facts,current,SelectedSigner::select(&response_raw,&runtime.receipt_signer_binding,Domain::Fixture,"broker-response").unwrap(),f.f.response_key.clone()).unwrap();
  let first=match session.dispatch(&reserve_frame).unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("reserve pending")};let payload:Value=response_signer.verify(&first).unwrap();assert_eq!(payload["durable_phase"],"reserved");
  let(conf,head,inventory)=session.fixture_observation().unwrap();let mut next_facts=f.facts.clone();next_facts.ledger_confirmation=conf.clone();next_facts.operation_state=OriginalOperationState::Present{effect_eligible:true,outcome:None};next_facts.remaining_capacity.inventory_sha256=inventory;next_facts.remaining_capacity.prefix_sha256=head.entry_sha256;
  if (8..=11).contains(&mode){
   if mode==8{fs::rename(f.f.base.join("receipts/sequence-0000000000000001/frame.json"),f.f.base.join("preserved-missing-original-frame.json")).unwrap();}
   else if mode==10{let path=f.f.base.join("receipts/sequence-0000000000000001/confirmation.json");fs::copy(&path,f.f.base.join("preserved-corrupt-confirmation.json")).unwrap();fs::write(path,b"{}").unwrap();}
   else if mode==11{for n in 0..36{let p=f.f.base.join(format!("receipts/unselected-{n:04}"));fs::create_dir(&p).unwrap();fs::set_permissions(&p,fs::Permissions::from_mode(0o700)).unwrap();}}
   else{let record=f.f.base.join(format!("control/records/{:020}.json",conf.head.sequence));
    let actual=if record.exists(){record}else{let mut names:Vec<_>=fs::read_dir(f.f.base.join("control/records")).unwrap().map(|e|e.unwrap().path()).collect();names.sort();names.pop().unwrap()};
    fs::copy(&actual,f.f.base.join("preserved-corrupt-control-original.json")).unwrap();fs::write(actual,b"{}").unwrap();}
   let observation=UnknownInspectionOriginal{schema_version:"lab-broker-unknown-inspection/v1".into(),operation:f.f.scope.operation.clone(),original_scope_binding:scope_binding.clone(),selected_control_high_water:conf.clone(),receipt_root:f.f.receipt.identity().clone(),receipt_inventory_sha256:Some(state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap()),reason:if mode==9{"control-unverified"}else{"receipt-unverified"}.into(),writable:false};
   let bytes=encode(&observation).unwrap();let selected=HostFixture::save(&f.input,"selected-unknown-inspection.json",&bytes);next_facts.disclosure_subjects=vec![selected];
  }
  let mut next_cap=cap.clone();next_cap.control_confirmation=conf;next_cap.remaining=next_facts.remaining_capacity.clone();next_facts.capacity_custody_binding=HostFixture::save(&f.input,"capacity-after-reserve.json",&encode(&next_cap).unwrap());
  let stage_capacity=CapacityOriginal{physical_root:f.f.stage.identity().clone(),remaining:quota::Remaining{inventory_sha256:state::owned_inventory_digest(&sh,4096,16*1024*1024).unwrap(),prefix_sha256:next_facts.remaining_capacity.prefix_sha256.clone(),bytes:16*1024*1024,inodes:4096},..next_cap.clone()};
  let mut stage_capacity=stage_capacity;if mode==16{stage_capacity.physical_root=f.f.receipt.identity().clone();}if mode==17{stage_capacity.remaining.bytes=1;}
  let stage_capacity_binding=HostFixture::save(&f.input,"stage-capacity-after-reserve.json",&encode(&stage_capacity).unwrap());next_facts.additional_capacity_bindings=vec![stage_capacity_binding.clone()];
  let mut originals:Vec<_>=f.selection.source_originals.iter().map(|b|if b==&f.facts.capacity_custody_binding{next_facts.capacity_custody_binding.clone()}else{b.clone()}).collect();originals.push(stage_capacity_binding);let(next,_,request)=f.successor(&next_facts,originals);
  let update=manager_channel.call(&request).unwrap();let receipt:HostProfileReceipt=f.signer.verify(&update).unwrap();assert_eq!(receipt.request.revision,2);
  if (8..=11).contains(&mode){
   let subject=next_facts.disclosure_subjects[0].clone();let read=intent.disclosure("inspect_operation",0,&subject);
   let before=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();
   let returned=inspect_uncertain(&host,&prefix_client,&read,&roots,&runtime_raw,&runtime_binding).unwrap();assert_eq!(returned,fs::read(f.input.selection().absolute_path.clone()+"/selected-unknown-inspection.json").unwrap());
   let mut bad:Value=decode(&read,65536).unwrap();bad["permit"]["signature"]=json!("0".repeat(128));bad["request"]["authorization_binding"]=wire::content_digest(&encode(&bad["permit"]).unwrap());
   assert!(inspect_uncertain(&host,&prefix_client,&encode(&bad).unwrap(),&roots,&runtime_raw,&runtime_binding).is_err());
   assert!(inspect_uncertain(&host,&prefix_client,&create_frame,&roots,&runtime_raw,&runtime_binding).is_err());
   assert_eq!(before,state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap());
   assert!(!f.f.base.join("stage/owned-stage").exists());
   host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return
  }
  if matches!(mode,5|6|16|17){
   let before=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();let before_control=session.fixture_observation().unwrap().0;
   let result=session.dispatch(&create_frame);if mode==16{assert!(result.is_err());}else if mode==17{assert!(matches!(result,Err(roots::Error("STAGE_PHYSICAL_REMAINING_RESERVE"))));}else{assert!(result.is_err());}
   assert!(!f.f.base.join("stage/owned-stage").exists());assert_eq!(before,state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap());assert_eq!(before_control,session.fixture_observation().unwrap().0);
   host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return
  }
  let second=match session.dispatch(&create_frame).unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("create pending")};let payload:Value=response_signer.verify(&second).unwrap();assert_eq!(payload["durable_phase"],"staging");assert!(f.f.base.join("stage/owned-stage").is_dir());
  if mode==7{assert!(f.f.base.join("stage/retained-original-0/original.bin").exists());host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return}
  let snapshot=session.fixture_stage().unwrap();let stage=serde_json::to_value(snapshot.stage_binding.clone().unwrap()).unwrap();
  if matches!(mode,14|15){
   let content=vec![19u8;65536];let(first,grant)=intent.chunk_frame(2,stage.clone(),&content,0,if mode==15{16384}else{32768},if mode==15{16384}else{32768});
   let captured=MemberIdentityOriginal{schema_version:"lab-broker-captured-member-identity/v1".into(),operation:f.f.scope.operation.clone(),root_id:"stage".into(),member:"empty.bin".into(),identity_binding:authority::member_identity_binding(&grant).unwrap()};
   next_facts.member_identity_originals=vec![HostFixture::save(&f.input,"captured-full-member.json",&encode(&captured).unwrap())];
   let(profile,binding,facts)=advance_profile(&f,&manager_channel,&next,&receipt.request.next,next_facts,session.fixture_observation().unwrap(),&sh);
   if mode==15{
    let before=session.fixture_observation().unwrap();let inventory=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();
    assert!(matches!(session.dispatch(&first),Err(roots::Error("COMPLETE_SEQUENCE_CAPACITY"))));
    assert_eq!(before,session.fixture_observation().unwrap());assert_eq!(inventory,state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap());assert!(!f.f.base.join("stage/owned-stage/empty.bin").exists());
    host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return
   }
   assert!(matches!(session.dispatch(&first).unwrap(),DispatchResult::Reply(_)));
   advance_profile(&f,&manager_channel,&profile,&binding,facts,session.fixture_observation().unwrap(),&sh);
   let before=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();let before_control=session.fixture_observation().unwrap().0;
   let before_member=fs::read(f.f.base.join("stage/owned-stage/empty.bin")).unwrap();
   assert!(matches!(session.dispatch(&intent.chunk_frame(3,stage.clone(),&content,32768,1,32768).0),Err(roots::Error("BATCH_OFFSETS"))));
   assert_eq!(before,state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap());assert_eq!(before_control,session.fixture_observation().unwrap().0);assert_eq!(before_member,fs::read(f.f.base.join("stage/owned-stage/empty.bin")).unwrap());
   assert!(matches!(session.dispatch(&intent.chunk_frame(3,stage,&content,32768,32768,32768).0).unwrap(),DispatchResult::Reply(_)));
   assert_eq!(fs::read(f.f.base.join("stage/owned-stage/empty.bin")).unwrap(),content);
   assert_eq!(session.fixture_stage().unwrap().members["empty.bin"].ranges.len(),2);
   host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return
  }
  let (empty_frame,grant)=intent.member_frame(2,stage.clone(),32768);
  let captured=MemberIdentityOriginal{schema_version:"lab-broker-captured-member-identity/v1".into(),operation:f.f.scope.operation.clone(),root_id:"stage".into(),member:"empty.bin".into(),identity_binding:authority::member_identity_binding(&grant).unwrap()};
  next_facts.member_identity_originals=vec![HostFixture::save(&f.input,"captured-empty-member.json",&encode(&captured).unwrap())];
  let(profile3,binding3,mut facts3)=advance_profile(&f,&manager_channel,&next,&receipt.request.next,next_facts,session.fixture_observation().unwrap(),&sh);
  let changed=intent.member_frame(2,stage.clone(),16384).0;assert!(matches!(session.dispatch(&changed),Err(roots::Error("IMMUTABLE_MEMBER_SELECTION"))));assert!(!f.f.base.join("stage/owned-stage/empty.bin").exists());
  let response=match session.dispatch(&empty_frame).unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("empty member pending")};let payload:Value=response_signer.verify(&response).unwrap();assert_eq!(payload["durable_phase"],"staging");assert_eq!(fs::metadata(f.f.base.join("stage/owned-stage/empty.bin")).unwrap().len(),0);
  if mode==3{
   let changed_grant=intent.member_frame(3,stage.clone(),16384).1;
   let changed=MemberIdentityOriginal{identity_binding:authority::member_identity_binding(&changed_grant).unwrap(),..captured};
   facts3.member_identity_originals=vec![HostFixture::save(&f.input,"changed-capture-after-ack.json",&encode(&changed).unwrap())];
   advance_profile(&f,&manager_channel,&profile3,&binding3,facts3,session.fixture_observation().unwrap(),&sh);
   let before=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();
   assert!(matches!(session.dispatch(&intent.member_frame(3,stage,16384).0),Err(roots::Error("CAPTURED_MEMBER_RENEWAL_CHANGED"))));
   assert_eq!(state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap(),before);
   host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return
  }
  let snap=session.fixture_stage().unwrap();let manifest=members::Manifest{schema_version:"lab-member-generation/v1".into(),root_id:snap.root_id.clone(),operation_id:snap.operation_id.clone(),fingerprint:snap.fingerprint.clone(),stage_identity:snap.stage_identity.clone(),generation_name:"generation-1".into(),members:snap.members.iter().map(|(p,m)|(p.clone(),members::MemberContent{sha256:m.full_sha256.clone(),size_bytes:m.full_length})).collect()};
  let manifest_binding=HostFixture::save(&f.input,"selected-member-manifest.json",&encode(&manifest).unwrap());facts3.selected_inputs.push(manifest_binding.clone());
  let(profile4,binding4,mut facts4)=advance_profile(&f,&manager_channel,&profile3,&binding3,facts3,session.fixture_observation().unwrap(),&sh);
  let seal=intent.subject_frame("seal_stage",3,"staging",stage,&manifest_binding);let response=match session.dispatch(&seal).unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("seal pending")};let payload:Value=response_signer.verify(&response).unwrap();assert_eq!(payload["durable_phase"],"sealed");
  let snap=session.fixture_stage().unwrap();let(conf,_,_)=session.fixture_observation().unwrap();
  let(selected_commit,commit_inputs)=generation_fixture::select_commit(&f,&static_generation,&snap,&manifest_binding,&jh,&conf);
  facts4.effect_inputs.commit=Some(selected_commit);facts4.selected_inputs.extend(commit_inputs);
  let(profile5,binding5,mut facts5)=advance_profile(&f,&manager_channel,&profile4,&binding4,facts4,session.fixture_observation().unwrap(),&sh);
  let commit=intent.subject_frame("commit_generation",4,"sealed",serde_json::to_value(snap.stage_binding.unwrap()).unwrap(),&manifest_binding);
  let request=if matches!(mode,12|13){_clientserver.send(&commit).unwrap();session.serve_one(&static_client).unwrap().expect("fixed static cold handoff")}
   else{match session.dispatch(&commit).unwrap(){DispatchResult::PendingCold(r)=>r,_=>panic!("commit acknowledged before cold")}};
  assert!(!f.f.base.join("receipts/sequence-0000000000000005/response.json").exists());
  if mode==13{
   session.fail_cold(ColdFailure::Timeout,100).unwrap();assert!(session.complete_cold(generation_fixture::observation(&request)).is_err());
   let current=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:session.fixture_observation().unwrap().0,posture:ledger::Posture::Fixture}).unwrap();assert!(current.outcome("operation-1").is_none());
   let failure:Value=decode(&fs::read(f.f.base.join("receipts/sequence-0000000000000005/cold-failure.json")).unwrap(),65536).unwrap();assert_eq!(failure["outcome"],"UNKNOWN");
   assert!(!f.f.base.join("receipts/sequence-0000000000000005/response.json").exists());host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return;
  }
  assert!(session.dispatch(&commit).is_err());assert!(!f.f.base.join("stage/owned-stage").exists());assert!(f.f.base.join("stage/generation-1/empty.bin").exists());
  if mode==1 {
   let now=now_seconds().unwrap();facts5.revocation_binding=HostFixture::save(&f.input,"revoked-after-cold.json",&encode(&RevocationOriginal{schema_version:"lab-broker-host-revocation/v1".into(),issuer_enrollment_binding:facts5.issuer_enrollment_binding.clone(),native_original_binding:profile5.source_originals[0].clone(),revoked:true,not_before:now-1,expires_at:now+60}).unwrap());
   advance_profile(&f,&manager_channel,&profile5,&binding5,facts5.clone(),session.fixture_observation().unwrap(),&sh);
  }
  let mut supplied=request.clone();if mode==2{supplied.pointer_binding.sha256=roots::hash(b"different exact request");}
  let result=if mode==12{session.send_completed_cold(&static_client,generation_fixture::observation(&supplied)).unwrap();Ok(DispatchResult::Reply(_clientserver.receive().unwrap()))}
   else{session.complete_cold(generation_fixture::observation(&supplied))};
  if matches!(mode,0|4|12) {
   let response=match result.unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("cold still pending")};
   assert_eq!(response_signer.verify::<Value>(&response).unwrap()["durable_phase"],"pointer-committed");
   if mode==4{
    let subject=bound("receipts","sequence-0000000000000003/response.json",&fs::read(f.f.base.join("receipts/sequence-0000000000000003/response.json")).unwrap()).unwrap();
    let original=fs::read(f.f.base.join("receipts/sequence-0000000000000003/response.json")).unwrap();
    facts5.disclosure_subjects=vec![subject.clone()];
    let current=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:session.fixture_observation().unwrap().0,posture:ledger::Posture::Fixture}).unwrap();
    facts5.operation_state=OriginalOperationState::Present{effect_eligible:false,outcome:current.outcome("operation-1").cloned()};
    let(_,_,facts6)=advance_profile(&f,&manager_channel,&profile5,&binding5,facts5,session.fixture_observation().unwrap(),&sh);
    let read=intent.disclosure("read_receipt",2,&subject);assert!(matches!(session.dispatch(&read).unwrap(),DispatchResult::Reply(r) if r==original));
    let facts=host.query(&wire::Frame::decode(&read).unwrap()).unwrap();
    let now=now_seconds().unwrap();let query=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:f.f.scope.history_key().unwrap(),recipient:caller.clone(),channel_binding:psel.channel_binding.clone(),challenge:challenge().unwrap(),current_ledger_confirmation:facts6.ledger_confirmation,current_execution_scope:f.f.scope.execution_scope.clone(),not_before:now-1,expires_at:now+60};
    let current=prefix_client.current(&query,&f.f.scope,&scope_binding).unwrap();drop(session);
    let mut restarted=Session::restart(&host,&control_client,&prefix_client,&f.control,&held,roots,&runtime_raw,runtime_binding,facts,current,SelectedSigner::select(&response_raw,&runtime.receipt_signer_binding,Domain::Fixture,"broker-response").unwrap(),f.f.response_key.clone()).unwrap();
    assert!(matches!(restarted.dispatch(&read).unwrap(),DispatchResult::Reply(r) if r==original));
    assert!(restarted.dispatch(&commit).is_err());
    host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return
   }
  }else{
   if mode==1{assert!(matches!(result,Err(roots::Error("ISSUER_NOT_CURRENT"))));}else{assert!(result.is_err());}
   let current=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:session.fixture_observation().unwrap().0,posture:ledger::Posture::Fixture}).unwrap();
   assert!(current.outcome("operation-1").is_none());assert!(!f.f.base.join("control/generation-journal/commit-operation-1/terminal.json").exists());
   assert!(!f.f.base.join("receipts/sequence-0000000000000005/response.json").exists());
  }
  assert!(session.complete_cold(generation_fixture::observation(&request)).is_err());
  host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();
 });
}

fn advance_profile(f:&HostFixture,manager:&Channel,previous:&HostServiceSelection,previous_binding:&Binding,
 mut facts:HostFacts,observation:(HostConfirmation,PrefixHead,String),stage:&Exclusive<'_>)->(HostServiceSelection,Binding,HostFacts){
 let revision=previous.revision+1;facts.ledger_confirmation=observation.0.clone();if facts.operation_state==OriginalOperationState::AbsentReservable{facts.operation_state=OriginalOperationState::Present{effect_eligible:true,outcome:None};}
 facts.remaining_capacity.inventory_sha256=observation.2;facts.remaining_capacity.prefix_sha256=observation.1.entry_sha256;
 let now=now_seconds().unwrap();let capacity=CapacityOriginal{schema_version:"lab-broker-held-capacity/v1".into(),physical_root:f.f.receipt.identity().clone(),control_confirmation:observation.0,remaining:facts.remaining_capacity.clone(),held_reservation_binding:previous.source_originals[1].clone(),not_before:now-1,expires_at:now+120};
 facts.capacity_custody_binding=HostFixture::save(&f.input,&format!("advance-capacity-{revision}.json"),&encode(&capacity).unwrap());
 let stage_reserve=CapacityOriginal{physical_root:f.f.stage.identity().clone(),remaining:quota::Remaining{inventory_sha256:state::owned_inventory_digest(stage,4096,16*1024*1024).unwrap(),prefix_sha256:facts.remaining_capacity.prefix_sha256.clone(),bytes:16*1024*1024,inodes:4096},..capacity.clone()};
 facts.additional_capacity_bindings=vec![HostFixture::save(&f.input,&format!("advance-stage-reserve-{revision}.json"),&encode(&stage_reserve).unwrap())];
 let mut next=previous.clone();next.revision=revision;next.predecessor_binding=Some(previous_binding.clone());next.source_originals=vec![previous.source_originals[0].clone(),previous.source_originals[1].clone(),facts.revocation_binding.clone(),facts.capacity_custody_binding.clone()];next.source_originals.extend(facts.additional_capacity_bindings.clone());next.template_binding=HostFixture::save(&f.input,&format!("advance-template-{revision}.json"),&encode(&facts).unwrap());
 let binding=HostFixture::save(&f.input,&format!("advance-service-{revision}.json"),&encode(&next).unwrap());
 let request=HostProfileRequest{schema_version:"lab-broker-host-profile-reselection/v1".into(),prior:previous_binding.clone(),next:binding.clone(),revision,recipient:next.profile_recipient.clone(),channel_binding:next.profile_channel_binding.clone(),challenge:challenge().unwrap(),not_before:now-1,expires_at:now+120};
 let original=f.manager.sign(&f.manager_key,&request).unwrap();let response=manager.call(&original).unwrap();let receipt:HostProfileReceipt=f.signer.verify(&response).unwrap();assert_eq!(receipt.request.next,binding);(next,binding,facts)
}
impl Intent{
 fn disclosure(&self,verb:&str,sequence:u64,subject:&Binding)->Vec<u8>{
  let now=now_seconds().unwrap();let mut r=json!({"schema_version":"lab-completion-broker-request/v1","request_id":format!("disclosure-{sequence}"),"operation_id":"operation-1","sequence":sequence,"activation_binding":self.scope["activation_binding"],"store_id":self.scope["store_id"],"instance_id":self.scope["instance_id"],"slot_epoch":1,"principal_ref":self.scope["principal_ref"],"verb":verb,"intent_binding":self.scope["intent_binding"],"authorization_binding":wire::content_digest(b""),"payload":{"root_id":"stage","subject_binding":subject}});
  let permit=authority::signed_record(&json!({"schema_version":"lab-completion-broker-disclosure-permit/v1","authorization_id":"fresh-read","operation_id":"operation-1","operation_fingerprint":authority::operation_fingerprint(&self.core).unwrap(),"scope":self.scope,"allowed_verb":verb,"message_core_sha256":wire::hash(&wire::signing_bytes(&wire::authorization_core(&r).unwrap()).unwrap()),"subject_binding":subject,"not_before":now-1,"expires_at":now+60,"max_output_bytes":65536}),"fixture-issuer",&self.key).unwrap();r["authorization_binding"]=wire::content_digest(&encode(&permit).unwrap());encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":r,"permit":permit})).unwrap()
 }
 fn member_frame(&self,sequence:u64,stage:Value,chunk_size:u64)->(Vec<u8>,Value){
  let now=now_seconds().unwrap();let mut r=json!({"schema_version":"lab-completion-broker-request/v1","request_id":format!("member-{sequence}-{chunk_size}"),"operation_id":"operation-1","sequence":sequence,"activation_binding":self.scope["activation_binding"],"store_id":self.scope["store_id"],"instance_id":self.scope["instance_id"],"slot_epoch":1,"principal_ref":self.scope["principal_ref"],"verb":"write_member","intent_binding":self.scope["intent_binding"],"authorization_binding":wire::content_digest(b""),"payload":{"root_id":"stage","member":"empty.bin","preimage_binding":null,"full_sha256":roots::hash(b""),"full_length":0,"offset":0,"length":0,"chunk_sha256":roots::hash(b""),"bytes_base64":""}});
  let grant=json!({"kind":"member","root_id":"stage","stage_binding":stage,"member":"empty.bin","preimage_binding":null,"full_sha256":roots::hash(b""),"full_length":0,"chunk_size":chunk_size,"sequence_start":sequence,"chunks":[{"sequence":sequence,"offset":0,"length":0,"core_sha256":wire::hash(&wire::signing_bytes(&wire::authorization_core(&r).unwrap()).unwrap())}]});
  let permit=authority::signed_record(&json!({"schema_version":"lab-completion-broker-permit/v1","permit_id":format!("member-permit-{sequence}-{chunk_size}"),"operation_fingerprint":authority::operation_fingerprint(&self.core).unwrap(),"basis_binding":self.core["authority_basis_binding"],"scope":self.scope,"limits":self.core["limits"],"allowed_verb":"write_member","allowed_phase":"staging","not_before":now-1,"expires_at":now+100,"grant":grant}),"fixture-issuer",&self.key).unwrap();r["authorization_binding"]=wire::content_digest(&encode(&permit).unwrap());(encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":r,"permit":permit})).unwrap(),grant)
 }
 fn subject_frame(&self,verb:&str,sequence:u64,phase:&str,stage:Value,subject:&Binding)->Vec<u8>{
  let now=now_seconds().unwrap();let mut r=json!({"schema_version":"lab-completion-broker-request/v1","request_id":format!("subject-{sequence}"),"operation_id":"operation-1","sequence":sequence,"activation_binding":self.scope["activation_binding"],"store_id":self.scope["store_id"],"instance_id":self.scope["instance_id"],"slot_epoch":1,"principal_ref":self.scope["principal_ref"],"verb":verb,"intent_binding":self.scope["intent_binding"],"authorization_binding":wire::content_digest(b""),"payload":{"root_id":"stage","subject_binding":subject}});
  let grant=json!({"kind":"control","root_id":"stage","stage_binding":stage,"member":null,"preimage_binding":null,"full_sha256":null,"full_length":0,"chunk_size":0,"sequence_start":sequence,"chunks":[{"sequence":sequence,"offset":0,"length":0,"core_sha256":wire::hash(&wire::signing_bytes(&wire::authorization_core(&r).unwrap()).unwrap())}]});
  let permit=authority::signed_record(&json!({"schema_version":"lab-completion-broker-permit/v1","permit_id":format!("subject-permit-{sequence}"),"operation_fingerprint":authority::operation_fingerprint(&self.core).unwrap(),"basis_binding":self.core["authority_basis_binding"],"scope":self.scope,"limits":self.core["limits"],"allowed_verb":verb,"allowed_phase":phase,"not_before":now-1,"expires_at":now+100,"grant":grant}),"fixture-issuer",&self.key).unwrap();r["authorization_binding"]=wire::content_digest(&encode(&permit).unwrap());encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":r,"permit":permit})).unwrap()
 }
}

#[path="reviewer_derived.rs"] mod reviewer_derived;

#[test]fn fixed_static_cold_continuation_retains_session_and_sends_only_confirmed_original(){full_lifecycle(12)}
#[test]fn fixed_static_cold_failure_retains_unknown_without_outcome_or_response(){full_lifecycle(13)}

include!("native_close_tests.rs");

mod close_regression_tests {use super::*;include!("close_regression_tests.rs");}
mod slot_continuation_tests {use super::*;include!("slot_continuation_tests.rs");}

#[path="reviewer_reconcile.rs"] mod reviewer_reconcile;

#[test]fn full_member_two_chunks_charge_once_and_short_range_preserves_terminal_positions(){full_lifecycle(14)}
impl Intent{
 fn select_nonempty(&mut self,f:&mut HostFixture){
  let mut basis=self.basis["payload"].clone();basis["limits"]["max_total_bytes"]=json!(65536);basis["limits"]["max_actions"]=json!(8);basis["output_slots"][0]["max_bytes"]=json!(65536);
  self.basis=authority::signed_record(&basis,"fixture-issuer",&self.key).unwrap();self.core["limits"]=basis["limits"].clone();self.core["output_slots"]=basis["output_slots"].clone();self.core["authority_basis_binding"]=wire::content_digest(&encode(&self.basis).unwrap());
  f.f.scope.operation.fingerprint=authority::operation_fingerprint(&self.core).unwrap();f.facts.operation=f.f.scope.operation.clone();f.query.original_fingerprint=f.f.scope.operation.fingerprint.clone();
 }
 fn chunk_frame(&self,sequence:u64,stage:Value,full:&[u8],offset:usize,length:usize,chunk_size:usize)->(Vec<u8>,Value){
  use base64::Engine;let now=now_seconds().unwrap();let chunk=&full[offset..offset+length];
  let mut r=json!({"schema_version":"lab-completion-broker-request/v1","request_id":format!("range-{sequence}-{length}"),"operation_id":"operation-1","sequence":sequence,"activation_binding":self.scope["activation_binding"],"store_id":self.scope["store_id"],"instance_id":self.scope["instance_id"],"slot_epoch":1,"principal_ref":self.scope["principal_ref"],"verb":"write_member","intent_binding":self.scope["intent_binding"],"authorization_binding":wire::content_digest(b""),"payload":{"root_id":"stage","member":"empty.bin","preimage_binding":null,"full_sha256":roots::hash(full),"full_length":full.len(),"offset":offset,"length":length,"chunk_sha256":roots::hash(chunk),"bytes_base64":base64::engine::general_purpose::STANDARD.encode(chunk)}});
  let grant=json!({"kind":"member","root_id":"stage","stage_binding":stage,"member":"empty.bin","preimage_binding":null,"full_sha256":roots::hash(full),"full_length":full.len(),"chunk_size":chunk_size,"sequence_start":sequence,"chunks":[{"sequence":sequence,"offset":offset,"length":length,"core_sha256":wire::hash(&wire::signing_bytes(&wire::authorization_core(&r).unwrap()).unwrap())}]});
  let permit=authority::signed_record(&json!({"schema_version":"lab-completion-broker-permit/v1","permit_id":format!("range-permit-{sequence}-{length}"),"operation_fingerprint":authority::operation_fingerprint(&self.core).unwrap(),"basis_binding":self.core["authority_basis_binding"],"scope":self.scope,"limits":self.core["limits"],"allowed_verb":"write_member","allowed_phase":"staging","not_before":now-1,"expires_at":now+100,"grant":grant}),"fixture-issuer",&self.key).unwrap();r["authorization_binding"]=wire::content_digest(&encode(&permit).unwrap());(encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":r,"permit":permit})).unwrap(),grant)
 }
}

#[test]fn exact_small_chunk_plan_refuses_before_first_write_when_terminal_positions_cannot_fit(){full_lifecycle(15)}

mod inspection_regression_tests{use super::*;include!("inspection_regression_tests.rs");}

#[test]fn selected_reserve_for_other_physical_root_cannot_authorize_stage(){full_lifecycle(16)}
#[test]fn insufficient_selected_stage_reserve_refuses_before_intent(){full_lifecycle(17)}

mod author_native_writer_tests{use super::*;include!("author_native_writer_tests.rs");}

#[path="reviewer_tail.rs"] mod reviewer_tail;

#[path="author_derived_envelope_tests.rs"] mod author_derived_envelope_tests;

#[path="reviewer_envelope.rs"] mod reviewer_envelope;
#[path="reviewer_envelope_positive.rs"] mod reviewer_envelope_positive;

include!("reviewer_history.rs");
