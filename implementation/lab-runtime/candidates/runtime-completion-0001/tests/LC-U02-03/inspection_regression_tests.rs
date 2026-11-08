fn reviewer_inspection_case(case:u8){
 let mode=0u8;
 use lab_control_store::{custody,ledger};
 let mut f=HostFixture::new();let intent=Intent::new(&mut f);
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
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
  });
  let control_task=threads.spawn(||{cw.serve_one(&cserver).unwrap();sender.send(cw.confirmation().clone()).unwrap();});
  let receipt_ref=&receipt_reader;let control_ref=&control_reader;let response_ref=&response_signer;let caller_ref=&caller;
  let prefix_task=threads.spawn(move ||{let current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();for _ in 0..4{
   let raw=pserver.receive().unwrap();let q:PrefixRequest=decode(&raw,65536).unwrap();let response=pw.confirm_originals(&q,caller_ref,receipt_ref,control_ref,&current,&limits(),response_ref).unwrap();pserver.send(&response).unwrap();}
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
  if matches!(mode,5|6){
   let before=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();let before_control=session.fixture_observation().unwrap().0;
   let result=session.dispatch(&create_frame);assert!(result.is_err());
   assert!(!f.f.base.join("stage/owned-stage").exists());assert_eq!(before,state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap());assert_eq!(before_control,session.fixture_observation().unwrap().0);
   host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return
  }
  let second=match session.dispatch(&create_frame).unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("create pending")};let payload:Value=response_signer.verify(&second).unwrap();assert_eq!(payload["durable_phase"],"staging");assert!(f.f.base.join("stage/owned-stage").is_dir());
  if mode==7{assert!(f.f.base.join("stage/retained-original-0/original.bin").exists());host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return}
  let snapshot=session.fixture_stage().unwrap();let stage=serde_json::to_value(snapshot.stage_binding.clone().unwrap()).unwrap();
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
  let observation=session.fixture_observation().unwrap();
  let mut body=InspectionOriginal{schema_version:"lab-broker-inspection-original/v1".into(),operation:f.f.scope.operation.clone(),control_confirmation:observation.0.clone(),prefix:observation.1.clone(),unknown:false};
  if case==7{body.prefix.entry_sha256=roots::hash(b"different independently selected observation head");}
  let original=encode(&body).unwrap();let subject=HostFixture::save(&f.input,"reviewer-normal-inspection.json",&original);facts4.selected_inputs.push(subject.clone());
  facts4.disclosure_subjects=if case==3{vec![]}else{vec![subject.clone()]};
  advance_profile(&f,&manager_channel,&profile4,&binding4,facts4,observation,&sh);
  let verb=if case==1{"inspect_operation"}else{"inspect"};let mut request=intent.disclosure(verb,77,&subject);
  if case==2{let mut frame:Value=decode(&request,65536).unwrap();let mut p=frame["permit"]["payload"].clone();let now=now_seconds().unwrap();p["not_before"]=json!(now-2);p["expires_at"]=json!(now-1);frame["permit"]=authority::signed_record(&p,"fixture-issuer",&intent.key).unwrap();frame["request"]["authorization_binding"]=wire::content_digest(&encode(&frame["permit"]).unwrap());request=encode(&frame).unwrap();}
  if case==6{let mut frame:Value=decode(&request,65536).unwrap();frame["permit"]["signature"]=json!("0".repeat(128));frame["request"]["authorization_binding"]=wire::content_digest(&encode(&frame["permit"]).unwrap());request=encode(&frame).unwrap();}
  if case==4{let mut frame:Value=decode(&empty_frame,65536).unwrap();frame["request"]["request_id"]=json!("validly-resigned-changed-duplicate");let mut p=frame["permit"]["payload"].clone();p["grant"]["chunks"][0]["core_sha256"]=json!(wire::hash(&wire::signing_bytes(&wire::authorization_core(&frame["request"]).unwrap()).unwrap()));frame["permit"]=authority::signed_record(&p,"fixture-issuer",&intent.key).unwrap();frame["request"]["authorization_binding"]=wire::content_digest(&encode(&frame["permit"]).unwrap());request=encode(&frame).unwrap();assert_ne!(request,empty_frame);}
  if case==5{let snapshot=session.fixture_stage().unwrap();let raw=intent.member_frame(4,serde_json::to_value(snapshot.stage_binding.unwrap()).unwrap(),32768).0;let mut frame:Value=decode(&raw,65536).unwrap();let mut p=frame["permit"]["payload"].clone();p["allowed_phase"]=json!("sealed");frame["permit"]=authority::signed_record(&p,"fixture-issuer",&intent.key).unwrap();frame["request"]["authorization_binding"]=wire::content_digest(&encode(&frame["permit"]).unwrap());request=encode(&frame).unwrap();}
  let receipts=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();let stage=state::owned_inventory_digest(&sh,4096,16*1024*1024).unwrap();let control=state::owned_inventory_digest(&ch,4096,16*1024*1024).unwrap();let pre=session.fixture_observation().unwrap();
  let result=session.dispatch(&request);
  if case<=1{assert!(matches!(result,Ok(DispatchResult::Reply(ref bytes)) if bytes==&original));}else{let expected=match case{2=>"CURRENT_AUTHORITY_PERIOD",3=>"DISCLOSURE_SUBJECT",4=>"IDEMPOTENCY_CONFLICT",5=>"PERMIT_STATE",6=>"SIGNATURE",7=>"INSPECTION_CURRENT_JOIN",_=>unreachable!()};assert!(matches!(result,Err(roots::Error(code)) if code==expected),"expected {expected}");}
  assert_eq!(receipts,state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap());assert_eq!(stage,state::owned_inventory_digest(&sh,4096,16*1024*1024).unwrap());assert_eq!(control,state::owned_inventory_digest(&ch,4096,16*1024*1024).unwrap());assert_eq!(pre,session.fixture_observation().unwrap());assert!(!f.f.base.join("receipts/sequence-0000000000000005").exists());
  host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();
 });
}
#[test]fn reviewer_inspection_normal_inspect_exact_current_original(){reviewer_inspection_case(0)}
#[test]fn reviewer_inspection_normal_inspect_operation_exact_current_original(){reviewer_inspection_case(1)}
#[test]fn reviewer_inspection_expired_signed_disclosure_refuses(){reviewer_inspection_case(2)}
#[test]fn reviewer_inspection_unselected_subject_refuses(){reviewer_inspection_case(3)}
#[test]fn reviewer_inspection_resigned_changed_duplicate_refuses(){reviewer_inspection_case(4)}
#[test]fn reviewer_inspection_signed_write_to_sealed_stage_refuses(){reviewer_inspection_case(5)}
#[test]fn reviewer_inspection_invalid_disclosure_signature_refuses(){reviewer_inspection_case(6)}
#[test]fn reviewer_inspection_stale_selected_observation_refuses(){reviewer_inspection_case(7)}
