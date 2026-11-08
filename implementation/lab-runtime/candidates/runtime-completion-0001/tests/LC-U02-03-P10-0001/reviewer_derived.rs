//! Independent held-filesystem probes; no Actual selection or forged history.
use super::*;

#[test]
fn reviewer_chronological_baseline(){ full_lifecycle(0); }

#[test]
fn reviewer_nested_generation_endpoint_is_refused(){
 let f=Fixture::new();let generation=f.base.join("stage/generation-owned");
 fs::create_dir(&generation).unwrap();fs::set_permissions(&generation,fs::Permissions::from_mode(0o700)).unwrap();
 let member=generation.join("immutable.bin");fs::write(&member,b"original canonical member").unwrap();
 let selected=Root::capture_fixture(&generation,"derived",[b("a",b"fixture"),b("b",b"fixture"),b("c",b"fixture")],f.scope.execution_scope.clone()).unwrap();
 let managed=Root::open(selected,Domain::Fixture).unwrap();
 let mh=managed.exclusive(Duration::from_millis(100)).unwrap();let gh=f.stage.exclusive(Duration::from_millis(100)).unwrap();
 assert_ne!((managed.identity().device,managed.identity().inode),(f.stage.identity().device,f.stage.identity().inode));
 assert!(state::disjoint_endpoints(&mh,&gh).is_err());
 assert_eq!(fs::read(&member).unwrap(),b"original canonical member");
 assert_eq!(fs::read_dir(f.base.join("receipts")).unwrap().count(),0);
}

#[test]
fn reviewer_managed_ancestor_is_refused(){
 let f=Fixture::new();let member=f.base.join("stage/canonical.bin");fs::write(&member,b"unaltered canonical").unwrap();
 let selected=Root::capture_fixture(&f.base,"derived-parent",[b("a",b"fixture"),b("b",b"fixture"),b("c",b"fixture")],f.scope.execution_scope.clone()).unwrap();
 let managed=Root::open(selected,Domain::Fixture).unwrap();
 let mh=managed.exclusive(Duration::from_millis(100)).unwrap();let gh=f.stage.exclusive(Duration::from_millis(100)).unwrap();
 assert!(state::disjoint_endpoints(&mh,&gh).is_err());
 assert_eq!(fs::read(&member).unwrap(),b"unaltered canonical");
}

#[test]
fn reviewer_sibling_roots_with_shared_ancestors_are_allowed(){
 let f=Fixture::new();let mh=f.witness.exclusive(Duration::from_millis(100)).unwrap();let gh=f.stage.exclusive(Duration::from_millis(100)).unwrap();
 assert_eq!(f.witness.selection().ancestors[0],f.stage.selection().ancestors[0]);
 state::disjoint_endpoints(&mh,&gh).unwrap();
 assert!(state::disjoint_endpoints(&gh,&gh).is_err());
}

// Continues a real fixed-service committed operation with a new derived-only
// original operation. All signatures/roots are explicitly Fixture domain.
fn reviewer_continue<'a>(f:&HostFixture,held:&'a lab_control_store::custody::Held<'a>,
 original_roots:BTreeMap<String,&'a Exclusive<'a>>,confirmation:HostConfirmation,original_facts:HostFacts,
 original_intent:&Intent,mode:u8)->HostConfirmation{
 use lab_control_store::{ledger,custody};
 let now=now_seconds().unwrap();let save=|n:&str,b:&[u8]|HostFixture::save(&f.input,&format!("reviewer-{n}"),b);
 let root_at=|path:&std::path::Path,id:&str|Root::open(Root::capture_fixture(path,id,[b("alias",b"fixture alias"),b("ancestor",b"fixture ancestry"),b("acl",b"fixture acl")],f.f.scope.execution_scope.clone()).unwrap(),Domain::Fixture).unwrap();
 let newdir=|name:&str|{let p=f.f.base.join(name);fs::create_dir(&p).unwrap();fs::set_permissions(&p,fs::Permissions::from_mode(0o700)).unwrap();p};
 let receipt=root_at(&newdir("derived-receipts"),"receipts");
 let witness=root_at(&newdir("derived-prefix-witness"),"derived-witness");
 let cwroot=root_at(&newdir("derived-control-witness"),"derived-control-witness");
 let managed_path=match mode{1=>f.f.base.join("stage/generation-1"),2=>f.f.base.clone(),_=>newdir("managed")};
 let managed=root_at(&managed_path,"managed");
 let managed_member=match mode{1=>"empty.bin",2=>"stage/generation-1/empty.bin",_=>"cache.bin"};
 let canonical=f.f.base.join("stage/generation-1/empty.bin");let canonical_before=fs::read(&canonical).unwrap();
 let mut intent=Intent{key:original_intent.key.clone(),scope:original_intent.scope.clone(),core:original_intent.core.clone(),basis:Value::Null,enrollment:original_intent.enrollment.clone()};
 intent.scope["intent_binding"]=serde_json::to_value(save("derived-intent-contract.json",b"separate fixture derived-only operation")).unwrap();
 let limits_value=json!({"max_total_bytes":64,"max_actions":32,"max_frame_bytes":65536,"max_chunk_bytes":32768});
 let mut slots=json!([{"root_id":"managed","member":managed_member,"preimage_binding":null,"max_bytes":64}]);
 if mode==7{slots.as_array_mut().unwrap().push(json!({"root_id":"managed","member":"cache-extra.bin","preimage_binding":null,"max_bytes":64}));}
 intent.basis=authority::signed_record(&json!({"schema_version":"lab-completion-effect-authority-basis/v1","basis_id":"derived-basis","scope":intent.scope,"limits":limits_value,"output_slots":slots,"not_before":now-1,"expires_at":now+180}),"fixture-issuer",&intent.key).unwrap();
 intent.core["operation_id"]=json!("operation-derived");intent.core["idempotency_key"]=json!("derived-idempotency");
 intent.core["original_request_binding"]=serde_json::to_value(save("derived-original-request.json",b"new derived request")).unwrap();
 intent.core["scope"]=intent.scope.clone();intent.core["output_slots"]=slots;intent.core["limits"]=limits_value;
 intent.core["authority_basis_binding"]=wire::content_digest(&encode(&intent.basis).unwrap());intent.core["operation_expires_at"]=json!(now+170);
 let mut operation=f.f.scope.operation.clone();operation.operation_id="operation-derived".into();operation.host_event="derived-event".into();operation.fingerprint=authority::operation_fingerprint(&intent.core).unwrap();operation.original_request_sha256=intent.core["original_request_binding"]["sha256"].as_str().unwrap().into();
 let caller=f.f.scope.recipient.clone();let(hfd,hsel,hserver)=pair("derived-host-channel",&caller);let(pfd,psel,pserver)=pair("derived-prefix-channel",&caller);
 let(cfd,csel,cserver)=pair("derived-control-channel",&caller);let(mfd,msel,mserver)=pair("derived-manager-channel",&caller);let(_client,client_sel,_clientserver)=pair("derived-client-channel",&caller);
 let mut scope=f.f.scope.clone();scope.operation=operation.clone();scope.receipt_root=receipt.identity().clone();scope.channel_binding=psel.channel_binding.clone();
 let scope_binding=save("scope.json",&encode(&scope).unwrap());let core_binding=save("core.json",&encode(&intent.core).unwrap());let basis_binding=save("basis.json",&encode(&intent.basis).unwrap());let quota_binding=save("quota.json",&encode(&limits()).unwrap());
 let response_raw=fs::read(f.f.base.join("input/session-response-signer.json")).unwrap();let response_binding=bound("input","session-response-signer.json",&response_raw).unwrap();let response_signer=SelectedSigner::select(&response_raw,&response_binding,Domain::Fixture,"broker-response").unwrap();
 let key_bytes=fs::read(f.f.base.join("input/session-response.key")).unwrap();let key_binding=bound("input","session-response.key",&key_bytes).unwrap();
 let issuer_binding=save("issuer.json",&intent.enrollment);
 let launch=LaunchSelection{schema_version:"lab-broker-fixed-launch/v1".into(),domain:Domain::Fixture,authority_domain:scope.authority_domain.clone(),operation:operation.clone(),original_scope_binding:scope_binding.clone(),host_signer_binding:f.selection.signer_binding.clone(),receipt_signer_binding:response_binding.clone(),prefix_signer_binding:f.f.proof_signer.binding().clone(),intent_signer_binding:issuer_binding.clone(),control_signer_binding:signer("control-confirmation",29).0.binding().clone(),control_service_binding:b("derived-control-service",b"fixed reviewer fixture witness"),source_binding:b("source",b"fixture source"),profile_binding:b("profile",b"fixture profile"),namespace_qualification_binding:b("namespace",b"fixture namespace"),caller:caller.clone(),broker_identity:caller.clone(),host_channel:hsel.clone(),prefix_channel:psel.clone(),control_channel:csel.clone(),client_channel:client_sel,allowed_root_ids:vec!["input".into(),"control".into(),"stage".into(),"generation-journal".into(),"receipts".into(),"managed".into()],core_binding:core_binding.clone(),basis_binding:basis_binding.clone(),quota_binding:quota_binding.clone(),execution_scope:scope.execution_scope.clone(),max_observation_age_seconds:10};
 let launch_raw=encode(&launch).unwrap();let launch_binding=save("launch.json",&launch_raw);
 let runtime=RuntimeSelection{schema_version:"lab-broker-runtime-selection/v1".into(),receipt_root_id:"receipts".into(),stage_root_id:"stage".into(),generation_root_id:"stage".into(),generation_journal_root_id:"generation-journal".into(),control_root_id:"control".into(),original_scope_binding:scope_binding.clone(),limits_binding:quota_binding.clone(),receipt_signer_binding:response_binding.clone(),receipt_private_key_binding:key_binding.clone(),commit_selection_binding:None,restart_selection_binding:None,supervisor_proof_binding:None,derived_selection_binding:None,global_order_binding:b("global-order",b"fixed fixture order")};
 let runtime_raw=encode(&runtime).unwrap();let runtime_binding=save("runtime.json",&runtime_raw);
 let mut facts=original_facts.clone();facts.operation=operation;facts.operation_state=OriginalOperationState::AbsentReservable;facts.ledger_confirmation=confirmation.clone();facts.core_binding=core_binding;facts.basis_binding=basis_binding;facts.quota_binding=quota_binding;facts.issuer_enrollment_binding=issuer_binding.clone();facts.live_authority_scope=intent.scope.clone();facts.query.launch_selection_binding=launch_binding.clone();facts.query.channel_binding=hsel.channel_binding.clone();facts.query.original_fingerprint=scope.operation.fingerprint.clone();facts.query.operation_id=scope.operation.operation_id.clone();facts.effect_inputs=EffectInputs{commit:None,restart:None,supervisor:None,derived:None};facts.member_identity_originals.clear();facts.additional_capacity_bindings.clear();facts.selected_inputs=vec![scope_binding.clone(),runtime_binding.clone(),response_binding.clone(),key_binding.clone()];
 facts.roots.retain(|r|r.root_id!="receipts");facts.roots.extend([receipt.selection().clone(),managed.selection().clone()]);facts.not_before=now-1;facts.expires_at=now+180;facts.activation_expires_at=now+180;
 let native=f.selection.source_originals[0].clone();let reservation=f.selection.source_originals[1].clone();
 facts.revocation_binding=save("revocation.json",&encode(&RevocationOriginal{schema_version:"lab-broker-host-revocation/v1".into(),issuer_enrollment_binding:issuer_binding,native_original_binding:native.clone(),revoked:false,not_before:now-1,expires_at:now+180}).unwrap());
 facts.remaining_capacity=quota::Remaining{inventory_sha256:roots::hash(&encode(&Vec::<(String,roots::Identity,u64,String)>::new()).unwrap()),prefix_sha256:PrefixHead::genesis(&scope).unwrap().entry_sha256,bytes:16*1024*1024,inodes:4096};
 let capacity=CapacityOriginal{schema_version:"lab-broker-held-capacity/v1".into(),physical_root:receipt.identity().clone(),control_confirmation:confirmation.clone(),remaining:facts.remaining_capacity.clone(),held_reservation_binding:reservation.clone(),not_before:now-1,expires_at:now+180};facts.capacity_custody_binding=save("capacity.json",&encode(&capacity).unwrap());
 let mut service=f.selection.clone();service.revision=1;service.predecessor_binding=None;service.template_binding=save("template.json",&encode(&facts).unwrap());service.roots=facts.roots.clone();service.channel_binding=hsel.channel_binding.clone();service.profile_channel_binding=msel.channel_binding.clone();service.source_originals=vec![native.clone(),reservation.clone(),facts.revocation_binding.clone(),facts.capacity_custody_binding.clone()];service.not_before=now-1;service.expires_at=now+180;
 let service_binding=save("service.json",&encode(&service).unwrap());let mut host_service=HostService::load(&encode(&service).unwrap(),&service_binding,&f.signer_raw,&f.manager_raw,Domain::Fixture).unwrap();
 let host=FixedHost::load(&launch_raw,&launch_binding,&f.signer_raw,hfd,Domain::Fixture).unwrap();let manager=Channel::from_selected(mfd,msel).unwrap();
 let prefix=FixedPrefixClient::new(Channel::from_selected(pfd,psel.clone()).unwrap(),signer("receipt-prefix",3).0);
 let(cs,ck)=signer("control-confirmation",29);let control_client=FixedControlClient::new(Channel::from_selected(cfd,csel.clone()).unwrap(),signer("control-confirmation",29).0,launch.control_service_binding.clone(),caller.clone()).unwrap();
 let rr=OriginalDirectory::open(receipt.selection().clone(),Domain::Fixture).unwrap();let cr=OriginalDirectory::open(original_roots["control"].root().selection().clone(),Domain::Fixture).unwrap().with_children(&[original_roots["generation-journal"].root().selection().clone()]).unwrap();
 let rh=receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=witness.exclusive(Duration::from_millis(100)).unwrap();let cwh=cwroot.exclusive(Duration::from_millis(100)).unwrap();let mh=managed.exclusive(Duration::from_millis(100)).unwrap();
 let mut pw=PrefixWitness::open(&wh,scope.clone(),scope_binding.clone(),PrefixHead::genesis(&scope).unwrap(),&f.f.proof_signer,f.f.proof_key.clone()).unwrap();
 let mut cw=ControlWitness::open(&cwh,&cr,&cs,ck,launch.control_service_binding.clone(),caller.clone(),csel.channel_binding.clone(),confirmation.clone(),confirmation.clone(),0,roots::hash(&encode(&confirmation).unwrap()),&[receipt.identity().clone(),managed.identity().clone()]).unwrap();
 let query=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:scope.history_key().unwrap(),recipient:caller.clone(),channel_binding:psel.channel_binding.clone(),challenge:challenge().unwrap(),current_ledger_confirmation:confirmation.clone(),current_execution_scope:scope.execution_scope.clone(),not_before:now-1,expires_at:now+120};
 let current=CurrentPrefix::verify(&pw.inspect(&query,&caller,&caller,&psel.channel_binding,&confirmation,&scope.execution_scope).unwrap(),&f.f.proof_signer,&query,&scope,&scope_binding,now).unwrap();
 let reserve_frame=reviewer_frame(&intent,"reserve_family",0,"absent",None);
 // Two individually valid signed slots exceed the signed total. The broker's
 // pre-intent declared-budget check must reject the whole operation, before a
 // derived selection or local receipt can exist.
 if mode==7{
  let before=state::owned_inventory_digest(&rh,4096,16777216).unwrap();
  std::thread::scope(|threads|{
   let h=threads.spawn(||{host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();});
   let first=host.query(&wire::Frame::decode(&reserve_frame).unwrap()).unwrap();
   let mut roots=original_roots.clone();roots.insert("receipts".into(),&rh);roots.insert("managed".into(),&mh);
   let mut session=Session::start(&host,&control_client,&prefix,&f.control,held,roots,&runtime_raw,runtime_binding,first,current,SelectedSigner::select(&response_raw,&response_binding,Domain::Fixture,"broker-response").unwrap(),f.f.response_key.clone()).unwrap();
   let code=match session.dispatch(&reserve_frame){Err(e)=>e.0,Ok(_)=>panic!("overlarge signed slots reserved")};
   assert_eq!(code,"DECLARED_COMPLETION_CAPACITY");
   assert_eq!(state::owned_inventory_digest(&rh,4096,16777216).unwrap(),before);
   assert!(fs::read_dir(&managed_path).unwrap().next().is_none());
   h.join().unwrap();
  });
  return confirmation;
 }
 let (send,receive)=std::sync::mpsc::channel();
 std::thread::scope(|threads|{
  let h=threads.spawn(||{host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();});
  let c=threads.spawn(||{cw.serve_one(&cserver).unwrap();send.send(cw.confirmation().clone()).unwrap();if mode==0{cw.serve_one(&cserver).unwrap();send.send(cw.confirmation().clone()).unwrap();}});
  let pr=&response_signer;let pc=&caller;let prr=&rr;let pcr=&cr;
  let p=threads.spawn(move ||{for _ in 0..if mode==0{2}else{1}{let current=receive.recv_timeout(Duration::from_secs(10)).unwrap();let raw=pserver.receive().unwrap();let q:PrefixRequest=decode(&raw,65536).unwrap();let raw=pw.confirm_originals(&q,pc,prr,pcr,&current,&limits(),pr).unwrap();pserver.send(&raw).unwrap();}});
  let first=host.query(&wire::Frame::decode(&reserve_frame).unwrap()).unwrap();let mut roots=original_roots.clone();roots.insert("receipts".into(),&rh);roots.insert("managed".into(),&mh);
  let mut session=Session::start(&host,&control_client,&prefix,&f.control,held,roots,&runtime_raw,runtime_binding.clone(),first,current,SelectedSigner::select(&response_raw,&response_binding,Domain::Fixture,"broker-response").unwrap(),f.f.response_key.clone()).unwrap();
  assert!(matches!(session.dispatch(&reserve_frame).unwrap(),DispatchResult::Reply(_)));
  let(conf,head,inventory)=session.fixture_observation().unwrap();facts.ledger_confirmation=conf.clone();facts.operation_state=OriginalOperationState::Present{effect_eligible:true,outcome:None};facts.remaining_capacity.inventory_sha256=inventory;facts.remaining_capacity.prefix_sha256=head.entry_sha256;
  let cap=CapacityOriginal{control_confirmation:conf.clone(),remaining:facts.remaining_capacity.clone(),..capacity};facts.capacity_custody_binding=save("capacity-after-reserve.json",&encode(&cap).unwrap());
  let target_b=original_facts.effect_inputs.commit.as_ref().unwrap();let mut target:CommitSelection=decode(&fs::read(f.f.base.join("input").join(&target_b.relative_path)).unwrap(),65536).unwrap();
  let journal=original_roots["generation-journal"];
  let target_capacity=CapacityOriginal{physical_root:journal.root().identity().clone(),remaining:quota::Remaining{bytes:67108864,inodes:46,inventory_sha256:state::owned_inventory_digest(journal,4096,16777216).unwrap(),prefix_sha256:conf.head.sha256.clone()},..cap.clone()};
  target.reserve_binding=save("generation-capacity-current.json",&encode(&target_capacity).unwrap());target.runtime_selection.expires_utc_ns=(now+100)*1000000000;
  let selected_target=save("generation-target-current.json",&encode(&target).unwrap());
  facts.selected_inputs.extend(original_facts.selected_inputs.clone());facts.selected_inputs.extend([target.reserve_binding.clone(),selected_target.clone()]);
  let mut originals=BTreeMap::new();let journal_path=f.f.base.join("control/generation-journal/commit-operation-1");
  for entry in fs::read_dir(&journal_path).unwrap(){let p=entry.unwrap().path();let name=p.file_name().unwrap().to_str().unwrap();let bytes=fs::read(&p).unwrap();let b=bound("generation-journal",&format!("commit-operation-1/{name}"),&bytes).unwrap();facts.selected_inputs.push(b.clone());originals.insert(name.into(),b);}
  let pointer_raw=fs::read(f.f.base.join("stage/HEAD.json")).unwrap();let pointer=bound("stage","HEAD.json",&pointer_raw).unwrap();
  let restart=crate::commit::RestartSelection{schema_version:"lab-generation-restart-selection/v1".into(),journal_name:"commit-operation-1".into(),originals,observed_pointer:Some(pointer.clone()),predecessor_pointer_original:None};
  let content=save("derived-content.bin",if mode==6{&[b'x';65]}else{b"bounded derived output"});facts.selected_inputs.push(content.clone());
  let managed_cap=CapacityOriginal{physical_root:managed.identity().clone(),remaining:quota::Remaining{bytes:if mode==8{0}else{16777216},inodes:4096,inventory_sha256:state::owned_inventory_digest(&mh,4096,16777216).unwrap(),prefix_sha256:conf.head.sha256.clone()},..cap.clone()};
  let managed_capacity=save("managed-capacity.json",&encode(&managed_cap).unwrap());facts.selected_inputs.push(managed_capacity.clone());
  let existing=managed_path.join(managed_member);let(preimage_binding,preimage_identity)=if existing.exists(){let bytes=fs::read(&existing).unwrap();let file=fs::File::open(&existing).unwrap();(Some(bound("managed",managed_member,&bytes).unwrap()),Some(roots::Identity::observe(&file).unwrap()))}else{(None,None)};
  let mut derived=DerivedSelection{schema_version:"lab-broker-derived-selection/v1".into(),operation:scope.operation.clone(),managed_root_id:"managed".into(),target_commit_selection_binding:selected_target,target_restart_selection:restart,committed_pointer_binding:pointer,committed_operation:f.f.scope.operation.clone(),members:BTreeMap::from([(managed_member.into(),DerivedMember{preimage_binding,preimage_identity,content_binding:content})]),max_member_bytes:65536,capacity_binding:managed_capacity};
  match mode {
   3=>derived.operation.store_id="wrong-selected-store".into(),
   4=>derived.managed_root_id="input".into(),
   5=>{let member=derived.members.get_mut(managed_member).unwrap();member.preimage_binding=Some(bound("managed",managed_member,b"forged preimage").unwrap());member.preimage_identity=Some(managed.identity().clone());},
   _=>{}
  }
  let derived_binding=save("derived-selection.json",&encode(&derived).unwrap());facts.effect_inputs.derived=Some(derived_binding.clone());
  let mut next=service.clone();next.revision=2;next.predecessor_binding=Some(service_binding.clone());next.template_binding=save("template-next.json",&encode(&facts).unwrap());next.source_originals=vec![native,reservation,facts.revocation_binding.clone(),facts.capacity_custody_binding.clone()];
  let next_binding=save("service-next.json",&encode(&next).unwrap());let request=HostProfileRequest{schema_version:"lab-broker-host-profile-reselection/v1".into(),prior:service_binding,next:next_binding,revision:2,recipient:caller.clone(),channel_binding:next.profile_channel_binding.clone(),challenge:challenge().unwrap(),not_before:now-1,expires_at:now+120};manager.call(&f.manager.sign(&f.manager_key,&request).unwrap()).unwrap();
  let before=state::owned_inventory_digest(&rh,4096,16777216).unwrap();let raw=reviewer_frame(&intent,"repair_derived",1,"pointer-committed",Some(&derived_binding));let result=session.dispatch(&raw);
  if mode==0{let reply=match result.unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("derived pending cold")};assert_eq!(response_signer.verify::<Value>(&reply).unwrap()["status"],"PASS");assert_eq!(fs::read(&existing).unwrap(),b"bounded derived output");}
  else{
   let expected=match mode{1|2=>"DERIVED_CANNOT_WRITE_CANONICAL_CUSTODY",3=>"DERIVED_SEPARATE_OPERATION_SCOPE",4=>"DERIVED_SIGNED_ROOT",5=>"DERIVED_SIGNED_PREIMAGE",6=>"DERIVED_SIGNED_MEMBER_LIMIT",7=>"DERIVED_SIGNED_TOTAL_LIMIT",8=>"DERIVED_PROSPECTIVE_CAPACITY",_=>panic!("unsupported negative")};
   assert!(matches!(result,Err(roots::Error(code)) if code==expected),"mode {mode} did not refuse with {expected}");
   assert_eq!(before,state::owned_inventory_digest(&rh,4096,16777216).unwrap());
   if mode>=3{assert!(!existing.exists());}
  }
  assert_eq!(fs::read(canonical).unwrap(),canonical_before);assert_eq!(fs::read(f.f.base.join("stage/HEAD.json")).unwrap(),pointer_raw);if mode==0{let l=ledger::Ledger::open(&f.control,held,ledger::TrustedSelection{confirmation:session.fixture_observation().unwrap().0,posture:ledger::Posture::Fixture}).unwrap();assert!(l.outcome("operation-derived").is_some_and(|(o,_)|*o==ledger::Outcome::Committed));assert!(l.outcome("operation-1").is_some_and(|(o,_)|*o==ledger::Outcome::Committed));}h.join().unwrap();c.join().unwrap();p.join().unwrap();
  session.fixture_observation().unwrap().0
 })
}

fn reviewer_frame(i:&Intent,verb:&str,sequence:u64,phase:&str,subject:Option<&Binding>)->Vec<u8>{
 let now=now_seconds().unwrap();let payload=match subject{Some(b)=>json!({"root_id":"managed","subject_binding":b}),None=>json!({"root_id":"managed","stage_name":"unused-derived-stage","max_bytes":64})};
 let mut request=json!({"schema_version":"lab-completion-broker-request/v1","request_id":format!("derived-{sequence}"),"operation_id":"operation-derived","sequence":sequence,"activation_binding":i.scope["activation_binding"],"store_id":i.scope["store_id"],"instance_id":i.scope["instance_id"],"slot_epoch":1,"principal_ref":i.scope["principal_ref"],"verb":verb,"intent_binding":i.scope["intent_binding"],"authorization_binding":wire::content_digest(b""),"payload":payload});
 let grant=json!({"kind":if subject.is_some(){"control"}else{"empty-stage"},"root_id":"managed","stage_binding":null,"member":null,"preimage_binding":null,"full_sha256":null,"full_length":0,"chunk_size":0,"sequence_start":sequence,"chunks":[{"sequence":sequence,"offset":0,"length":0,"core_sha256":wire::hash(&wire::signing_bytes(&wire::authorization_core(&request).unwrap()).unwrap())}]});
 let permit=authority::signed_record(&json!({"schema_version":"lab-completion-broker-permit/v1","permit_id":format!("derived-permit-{sequence}"),"operation_fingerprint":authority::operation_fingerprint(&i.core).unwrap(),"basis_binding":i.core["authority_basis_binding"],"scope":i.scope,"limits":i.core["limits"],"allowed_verb":verb,"allowed_phase":phase,"not_before":now-1,"expires_at":now+100,"grant":grant}),"fixture-issuer",&i.key).unwrap();request["authorization_binding"]=wire::content_digest(&encode(&permit).unwrap());encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":request,"permit":permit})).unwrap()
}

fn reviewer_seed(probe_mode:u8){
 let mode=0;
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
   if mode>=8{host_service.serve_one(&hserver).unwrap();return}
   if mode>=5{return}
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();
   if mode==3{host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();return}
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
   if mode==1{host_service.serve_profile_one(&mserver).unwrap();}host_service.serve_one(&hserver).unwrap();
   if mode==4{host_service.serve_profile_one(&mserver).unwrap();for _ in 0..3{host_service.serve_one(&hserver).unwrap();}}
  });
  let control_task=threads.spawn(||{cw.serve_one(&cserver).unwrap();sender.send(cw.confirmation().clone()).unwrap();if matches!(mode,0|4){cw.serve_one(&cserver).unwrap();sender.send(cw.confirmation().clone()).unwrap();}});
  let receipt_ref=&receipt_reader;let control_ref=&control_reader;let response_ref=&response_signer;let caller_ref=&caller;
  let prefix_task=threads.spawn(move ||{let mut current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();for i in 0..if matches!(mode,0|4){5}else if mode==3{3}else if mode==7{2}else if mode>=5{1}else{4}{
   let raw=pserver.receive().unwrap();let q:PrefixRequest=decode(&raw,65536).unwrap();if i==4{current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();}
   let response=pw.confirm_originals(&q,caller_ref,receipt_ref,control_ref,&current,&limits(),response_ref).unwrap();pserver.send(&response).unwrap();}
   if mode==4{let raw=pserver.receive().unwrap();let q:PrefixInspectionRequest=decode(&raw,65536).unwrap();let response=pw.inspect(&q,caller_ref,caller_ref,&q.channel_binding,&current,&q.current_execution_scope).unwrap();pserver.send(&response).unwrap();}
  });
  let facts=host.query(&wire::Frame::decode(&reserve_frame).unwrap()).unwrap();let roots=BTreeMap::from([("input".into(),&ih),("receipts".into(),&rh),("stage".into(),&sh),("control".into(),&ch),("generation-journal".into(),&jh)]);
  let mut session=Session::start(&host,&control_client,&prefix_client,&f.control,&held,roots.clone(),&runtime_raw,runtime_binding.clone(),facts,current,SelectedSigner::select(&response_raw,&runtime.receipt_signer_binding,Domain::Fixture,"broker-response").unwrap(),f.f.response_key.clone()).unwrap();
  let first=match session.dispatch(&reserve_frame).unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("reserve pending")};let payload:Value=response_signer.verify(&first).unwrap();assert_eq!(payload["durable_phase"],"reserved");
  let(conf,head,inventory)=session.fixture_observation().unwrap();let mut next_facts=f.facts.clone();next_facts.ledger_confirmation=conf.clone();next_facts.operation_state=OriginalOperationState::Present{effect_eligible:true,outcome:None};next_facts.remaining_capacity.inventory_sha256=inventory;next_facts.remaining_capacity.prefix_sha256=head.entry_sha256;
  if mode>=8{
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
  if mode>=8{
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
  let snap=session.fixture_stage().unwrap();let(conf,_,_)=session.fixture_observation().unwrap();
  let(selected_commit,commit_inputs)=generation_fixture::select_commit(&f,&static_generation,&snap,&manifest_binding,&jh,&conf);
  facts4.effect_inputs.commit=Some(selected_commit);facts4.selected_inputs.extend(commit_inputs);
  let(profile5,binding5,mut facts5)=advance_profile(&f,&manager_channel,&profile4,&binding4,facts4,session.fixture_observation().unwrap(),&sh);
  let commit=intent.subject_frame("commit_generation",4,"sealed",serde_json::to_value(snap.stage_binding.unwrap()).unwrap(),&manifest_binding);
  let request=match session.dispatch(&commit).unwrap(){DispatchResult::PendingCold(r)=>r,_=>panic!("commit acknowledged before cold")};
  assert!(session.dispatch(&commit).is_err());assert!(!f.f.base.join("stage/owned-stage").exists());assert!(f.f.base.join("stage/generation-1/empty.bin").exists());
  if mode==1 {
   let now=now_seconds().unwrap();facts5.revocation_binding=HostFixture::save(&f.input,"revoked-after-cold.json",&encode(&RevocationOriginal{schema_version:"lab-broker-host-revocation/v1".into(),issuer_enrollment_binding:facts5.issuer_enrollment_binding.clone(),native_original_binding:profile5.source_originals[0].clone(),revoked:true,not_before:now-1,expires_at:now+60}).unwrap());
   advance_profile(&f,&manager_channel,&profile5,&binding5,facts5.clone(),session.fixture_observation().unwrap(),&sh);
  }
  let mut supplied=request.clone();if mode==2{supplied.pointer_binding.sha256=roots::hash(b"different exact request");}
  let result=session.complete_cold(generation_fixture::observation(&supplied));
  if matches!(mode,0|4) {
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
  if probe_mode==3{let after=reviewer_continue(&f,&held,roots.clone(),session.fixture_observation().unwrap().0,facts5.clone(),&intent,0);reviewer_continue_second(&f,&held,roots.clone(),after,facts5.clone(),&intent,3);}else{reviewer_continue(&f,&held,roots.clone(),session.fixture_observation().unwrap().0,facts5.clone(),&intent,probe_mode);}
 });
}

#[test] fn reviewer_full_derived_positive(){reviewer_seed(0)}
#[test] fn reviewer_full_derived_nested_refuses(){reviewer_seed(1)}
#[test] fn reviewer_full_derived_ancestor_refuses(){reviewer_seed(2)}
#[test] fn author_p10_wrong_selected_scope_refuses(){reviewer_seed(3)}
#[test] fn author_p10_wrong_selected_root_refuses(){reviewer_seed(4)}
#[test] fn author_p10_wrong_signed_preimage_refuses(){reviewer_seed(5)}
#[test] fn author_p10_signed_member_limit_refuses(){reviewer_seed(6)}
#[test] fn author_p10_signed_total_limit_refuses(){reviewer_seed(7)}
#[test] fn author_p10_held_managed_root_capacity_refuses(){reviewer_seed(8)}

fn reviewer_continue_second<'a>(f:&HostFixture,held:&'a lab_control_store::custody::Held<'a>,
 original_roots:BTreeMap<String,&'a Exclusive<'a>>,confirmation:HostConfirmation,original_facts:HostFacts,
 original_intent:&Intent,mode:u8)->HostConfirmation{
 use lab_control_store::{ledger,custody};
 let now=now_seconds().unwrap();let save=|n:&str,b:&[u8]|HostFixture::save(&f.input,&format!("reviewer-second-{n}"),b);
 let root_at=|path:&std::path::Path,id:&str|Root::open(Root::capture_fixture(path,id,[b("alias",b"fixture alias"),b("ancestor",b"fixture ancestry"),b("acl",b"fixture acl")],f.f.scope.execution_scope.clone()).unwrap(),Domain::Fixture).unwrap();
 let newdir=|name:&str|{let p=f.f.base.join(name);fs::create_dir(&p).unwrap();fs::set_permissions(&p,fs::Permissions::from_mode(0o700)).unwrap();p};
 let receipt=root_at(&newdir("second-derived-receipts"),"receipts");
 let witness=root_at(&newdir("second-derived-prefix-witness"),"derived-witness");
 let cwroot=root_at(&newdir("second-derived-control-witness"),"derived-control-witness");
 let managed_path=match mode{1=>f.f.base.join("stage/generation-1"),2=>f.f.base.clone(),_=>newdir("managed-second")};
 let managed=root_at(&managed_path,"managed");
 let managed_member=match mode{1=>"empty.bin",2=>"stage/generation-1/empty.bin",_=>"cache.bin"};
 let canonical=f.f.base.join("stage/generation-1/empty.bin");let canonical_before=fs::read(&canonical).unwrap();
 let mut intent=Intent{key:original_intent.key.clone(),scope:original_intent.scope.clone(),core:original_intent.core.clone(),basis:Value::Null,enrollment:original_intent.enrollment.clone()};
 intent.scope["intent_binding"]=serde_json::to_value(save("derived-intent-contract.json",b"separate fixture derived-only operation")).unwrap();
 let limits_value=json!({"max_total_bytes":64,"max_actions":32,"max_frame_bytes":65536,"max_chunk_bytes":32768});
 let slots=json!([{"root_id":"managed","member":managed_member,"preimage_binding":null,"max_bytes":64}]);
 intent.basis=authority::signed_record(&json!({"schema_version":"lab-completion-effect-authority-basis/v1","basis_id":"derived-basis","scope":intent.scope,"limits":limits_value,"output_slots":slots,"not_before":now-1,"expires_at":now+180}),"fixture-issuer",&intent.key).unwrap();
 intent.core["operation_id"]=json!("operation-derived-second");intent.core["idempotency_key"]=json!("derived-idempotency");
 intent.core["original_request_binding"]=serde_json::to_value(save("derived-original-request.json",b"new derived request")).unwrap();
 intent.core["scope"]=intent.scope.clone();intent.core["output_slots"]=slots;intent.core["limits"]=limits_value;
 intent.core["authority_basis_binding"]=wire::content_digest(&encode(&intent.basis).unwrap());intent.core["operation_expires_at"]=json!(now+170);
 let mut operation=f.f.scope.operation.clone();operation.operation_id="operation-derived-second".into();operation.host_event="derived-event-second".into();operation.fingerprint=authority::operation_fingerprint(&intent.core).unwrap();operation.original_request_sha256=intent.core["original_request_binding"]["sha256"].as_str().unwrap().into();
 let caller=f.f.scope.recipient.clone();let(hfd,hsel,hserver)=pair("derived-host-channel",&caller);let(pfd,psel,pserver)=pair("derived-prefix-channel",&caller);
 let(cfd,csel,cserver)=pair("derived-control-channel",&caller);let(mfd,msel,mserver)=pair("derived-manager-channel",&caller);let(_client,client_sel,_clientserver)=pair("derived-client-channel",&caller);
 let mut scope=f.f.scope.clone();scope.operation=operation.clone();scope.receipt_root=receipt.identity().clone();scope.channel_binding=psel.channel_binding.clone();
 let scope_binding=save("scope.json",&encode(&scope).unwrap());let core_binding=save("core.json",&encode(&intent.core).unwrap());let basis_binding=save("basis.json",&encode(&intent.basis).unwrap());let quota_binding=save("quota.json",&encode(&limits()).unwrap());
 let response_raw=fs::read(f.f.base.join("input/session-response-signer.json")).unwrap();let response_binding=bound("input","session-response-signer.json",&response_raw).unwrap();let response_signer=SelectedSigner::select(&response_raw,&response_binding,Domain::Fixture,"broker-response").unwrap();
 let key_bytes=fs::read(f.f.base.join("input/session-response.key")).unwrap();let key_binding=bound("input","session-response.key",&key_bytes).unwrap();
 let issuer_binding=save("issuer.json",&intent.enrollment);
 let launch=LaunchSelection{schema_version:"lab-broker-fixed-launch/v1".into(),domain:Domain::Fixture,authority_domain:scope.authority_domain.clone(),operation:operation.clone(),original_scope_binding:scope_binding.clone(),host_signer_binding:f.selection.signer_binding.clone(),receipt_signer_binding:response_binding.clone(),prefix_signer_binding:f.f.proof_signer.binding().clone(),intent_signer_binding:issuer_binding.clone(),control_signer_binding:signer("control-confirmation",29).0.binding().clone(),control_service_binding:b("derived-control-service",b"fixed reviewer fixture witness"),source_binding:b("source",b"fixture source"),profile_binding:b("profile",b"fixture profile"),namespace_qualification_binding:b("namespace",b"fixture namespace"),caller:caller.clone(),broker_identity:caller.clone(),host_channel:hsel.clone(),prefix_channel:psel.clone(),control_channel:csel.clone(),client_channel:client_sel,allowed_root_ids:vec!["input".into(),"control".into(),"stage".into(),"generation-journal".into(),"receipts".into(),"managed".into()],core_binding:core_binding.clone(),basis_binding:basis_binding.clone(),quota_binding:quota_binding.clone(),execution_scope:scope.execution_scope.clone(),max_observation_age_seconds:10};
 let launch_raw=encode(&launch).unwrap();let launch_binding=save("launch.json",&launch_raw);
 let runtime=RuntimeSelection{schema_version:"lab-broker-runtime-selection/v1".into(),receipt_root_id:"receipts".into(),stage_root_id:"stage".into(),generation_root_id:"stage".into(),generation_journal_root_id:"generation-journal".into(),control_root_id:"control".into(),original_scope_binding:scope_binding.clone(),limits_binding:quota_binding.clone(),receipt_signer_binding:response_binding.clone(),receipt_private_key_binding:key_binding.clone(),commit_selection_binding:None,restart_selection_binding:None,supervisor_proof_binding:None,derived_selection_binding:None,global_order_binding:b("global-order",b"fixed fixture order")};
 let runtime_raw=encode(&runtime).unwrap();let runtime_binding=save("runtime.json",&runtime_raw);
 let mut facts=original_facts.clone();facts.operation=operation;facts.operation_state=OriginalOperationState::AbsentReservable;facts.ledger_confirmation=confirmation.clone();facts.core_binding=core_binding;facts.basis_binding=basis_binding;facts.quota_binding=quota_binding;facts.issuer_enrollment_binding=issuer_binding.clone();facts.live_authority_scope=intent.scope.clone();facts.query.launch_selection_binding=launch_binding.clone();facts.query.channel_binding=hsel.channel_binding.clone();facts.query.original_fingerprint=scope.operation.fingerprint.clone();facts.query.operation_id=scope.operation.operation_id.clone();facts.effect_inputs=EffectInputs{commit:None,restart:None,supervisor:None,derived:None};facts.member_identity_originals.clear();facts.additional_capacity_bindings.clear();facts.selected_inputs=vec![scope_binding.clone(),runtime_binding.clone(),response_binding.clone(),key_binding.clone()];
 facts.roots.retain(|r|r.root_id!="receipts");facts.roots.extend([receipt.selection().clone(),managed.selection().clone()]);facts.not_before=now-1;facts.expires_at=now+180;facts.activation_expires_at=now+180;
 let native=f.selection.source_originals[0].clone();let reservation=f.selection.source_originals[1].clone();
 facts.revocation_binding=save("revocation.json",&encode(&RevocationOriginal{schema_version:"lab-broker-host-revocation/v1".into(),issuer_enrollment_binding:issuer_binding,native_original_binding:native.clone(),revoked:false,not_before:now-1,expires_at:now+180}).unwrap());
 facts.remaining_capacity=quota::Remaining{inventory_sha256:roots::hash(&encode(&Vec::<(String,roots::Identity,u64,String)>::new()).unwrap()),prefix_sha256:PrefixHead::genesis(&scope).unwrap().entry_sha256,bytes:16*1024*1024,inodes:4096};
 let capacity=CapacityOriginal{schema_version:"lab-broker-held-capacity/v1".into(),physical_root:receipt.identity().clone(),control_confirmation:confirmation.clone(),remaining:facts.remaining_capacity.clone(),held_reservation_binding:reservation.clone(),not_before:now-1,expires_at:now+180};facts.capacity_custody_binding=save("capacity.json",&encode(&capacity).unwrap());
 let mut service=f.selection.clone();service.revision=1;service.predecessor_binding=None;service.template_binding=save("template.json",&encode(&facts).unwrap());service.roots=facts.roots.clone();service.channel_binding=hsel.channel_binding.clone();service.profile_channel_binding=msel.channel_binding.clone();service.source_originals=vec![native.clone(),reservation.clone(),facts.revocation_binding.clone(),facts.capacity_custody_binding.clone()];service.not_before=now-1;service.expires_at=now+180;
 let service_binding=save("service.json",&encode(&service).unwrap());let mut host_service=HostService::load(&encode(&service).unwrap(),&service_binding,&f.signer_raw,&f.manager_raw,Domain::Fixture).unwrap();
 let host=FixedHost::load(&launch_raw,&launch_binding,&f.signer_raw,hfd,Domain::Fixture).unwrap();let manager=Channel::from_selected(mfd,msel).unwrap();
 let prefix=FixedPrefixClient::new(Channel::from_selected(pfd,psel.clone()).unwrap(),signer("receipt-prefix",3).0);
 let(cs,ck)=signer("control-confirmation",29);let control_client=FixedControlClient::new(Channel::from_selected(cfd,csel.clone()).unwrap(),signer("control-confirmation",29).0,launch.control_service_binding.clone(),caller.clone()).unwrap();
 let rr=OriginalDirectory::open(receipt.selection().clone(),Domain::Fixture).unwrap();let cr=OriginalDirectory::open(original_roots["control"].root().selection().clone(),Domain::Fixture).unwrap().with_children(&[original_roots["generation-journal"].root().selection().clone()]).unwrap();
 let rh=receipt.exclusive(Duration::from_millis(100)).unwrap();let wh=witness.exclusive(Duration::from_millis(100)).unwrap();let cwh=cwroot.exclusive(Duration::from_millis(100)).unwrap();let mh=managed.exclusive(Duration::from_millis(100)).unwrap();
 let mut pw=PrefixWitness::open(&wh,scope.clone(),scope_binding.clone(),PrefixHead::genesis(&scope).unwrap(),&f.f.proof_signer,f.f.proof_key.clone()).unwrap();
 let mut cw=ControlWitness::open(&cwh,&cr,&cs,ck,launch.control_service_binding.clone(),caller.clone(),csel.channel_binding.clone(),confirmation.clone(),confirmation.clone(),0,roots::hash(&encode(&confirmation).unwrap()),&[receipt.identity().clone(),managed.identity().clone()]).unwrap();
 let query=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:scope.history_key().unwrap(),recipient:caller.clone(),channel_binding:psel.channel_binding.clone(),challenge:challenge().unwrap(),current_ledger_confirmation:confirmation.clone(),current_execution_scope:scope.execution_scope.clone(),not_before:now-1,expires_at:now+120};
 let current=CurrentPrefix::verify(&pw.inspect(&query,&caller,&caller,&psel.channel_binding,&confirmation,&scope.execution_scope).unwrap(),&f.f.proof_signer,&query,&scope,&scope_binding,now).unwrap();
 let reserve_frame=reviewer_frame_second(&intent,"reserve_family",0,"absent",None);
 let (send,receive)=std::sync::mpsc::channel();
 std::thread::scope(|threads|{
  let h=threads.spawn(||{host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();});
  let c=threads.spawn(||{cw.serve_one(&cserver).unwrap();send.send(cw.confirmation().clone()).unwrap();if mode==0{cw.serve_one(&cserver).unwrap();send.send(cw.confirmation().clone()).unwrap();}});
  let pr=&response_signer;let pc=&caller;let prr=&rr;let pcr=&cr;
  let p=threads.spawn(move ||{for _ in 0..if mode==0{2}else{1}{let current=receive.recv_timeout(Duration::from_secs(10)).unwrap();let raw=pserver.receive().unwrap();let q:PrefixRequest=decode(&raw,65536).unwrap();let raw=pw.confirm_originals(&q,pc,prr,pcr,&current,&limits(),pr).unwrap();pserver.send(&raw).unwrap();}});
  let first=host.query(&wire::Frame::decode(&reserve_frame).unwrap()).unwrap();let mut roots=original_roots.clone();roots.insert("receipts".into(),&rh);roots.insert("managed".into(),&mh);
  let mut session=Session::start(&host,&control_client,&prefix,&f.control,held,roots,&runtime_raw,runtime_binding.clone(),first,current,SelectedSigner::select(&response_raw,&response_binding,Domain::Fixture,"broker-response").unwrap(),f.f.response_key.clone()).unwrap();
  assert!(matches!(session.dispatch(&reserve_frame).unwrap(),DispatchResult::Reply(_)));
  let(conf,head,inventory)=session.fixture_observation().unwrap();facts.ledger_confirmation=conf.clone();facts.operation_state=OriginalOperationState::Present{effect_eligible:true,outcome:None};facts.remaining_capacity.inventory_sha256=inventory;facts.remaining_capacity.prefix_sha256=head.entry_sha256;
  let cap=CapacityOriginal{control_confirmation:conf.clone(),remaining:facts.remaining_capacity.clone(),..capacity};facts.capacity_custody_binding=save("capacity-after-reserve.json",&encode(&cap).unwrap());
  let target_b=original_facts.effect_inputs.commit.as_ref().unwrap();let mut target:CommitSelection=decode(&fs::read(f.f.base.join("input").join(&target_b.relative_path)).unwrap(),65536).unwrap();
  let journal=original_roots["generation-journal"];
  let target_capacity=CapacityOriginal{physical_root:journal.root().identity().clone(),remaining:quota::Remaining{bytes:67108864,inodes:46,inventory_sha256:state::owned_inventory_digest(journal,4096,16777216).unwrap(),prefix_sha256:conf.head.sha256.clone()},..cap.clone()};
  target.reserve_binding=save("generation-capacity-current.json",&encode(&target_capacity).unwrap());target.runtime_selection.expires_utc_ns=(now+100)*1000000000;
  let selected_target=save("generation-target-current.json",&encode(&target).unwrap());
  facts.selected_inputs.extend(original_facts.selected_inputs.clone());facts.selected_inputs.extend([target.reserve_binding.clone(),selected_target.clone()]);
  let mut originals=BTreeMap::new();let journal_path=f.f.base.join("control/generation-journal/commit-operation-1");
  for entry in fs::read_dir(&journal_path).unwrap(){let p=entry.unwrap().path();let name=p.file_name().unwrap().to_str().unwrap();let bytes=fs::read(&p).unwrap();let b=bound("generation-journal",&format!("commit-operation-1/{name}"),&bytes).unwrap();facts.selected_inputs.push(b.clone());originals.insert(name.into(),b);}
  let pointer_raw=fs::read(f.f.base.join("stage/HEAD.json")).unwrap();let pointer=bound("stage","HEAD.json",&pointer_raw).unwrap();
  let restart=crate::commit::RestartSelection{schema_version:"lab-generation-restart-selection/v1".into(),journal_name:"commit-operation-1".into(),originals,observed_pointer:Some(pointer.clone()),predecessor_pointer_original:None};
  let content=save("derived-content.bin",b"bounded derived output");facts.selected_inputs.push(content.clone());
  let managed_cap=CapacityOriginal{physical_root:managed.identity().clone(),remaining:quota::Remaining{bytes:16777216,inodes:4096,inventory_sha256:state::owned_inventory_digest(&mh,4096,16777216).unwrap(),prefix_sha256:conf.head.sha256.clone()},..cap.clone()};
  let managed_capacity=save("managed-capacity.json",&encode(&managed_cap).unwrap());facts.selected_inputs.push(managed_capacity.clone());
  let existing=managed_path.join(managed_member);let(preimage_binding,preimage_identity)=if existing.exists(){let bytes=fs::read(&existing).unwrap();let file=fs::File::open(&existing).unwrap();(Some(bound("managed",managed_member,&bytes).unwrap()),Some(roots::Identity::observe(&file).unwrap()))}else{(None,None)};
  let derived=DerivedSelection{schema_version:"lab-broker-derived-selection/v1".into(),operation:scope.operation.clone(),managed_root_id:"managed".into(),target_commit_selection_binding:selected_target,target_restart_selection:restart,committed_pointer_binding:pointer,committed_operation:ledger::Ledger::open(&f.control,held,ledger::TrustedSelection{confirmation:conf.clone(),posture:ledger::Posture::Fixture}).unwrap().operation("operation-derived").unwrap().clone(),members:BTreeMap::from([(managed_member.into(),DerivedMember{preimage_binding,preimage_identity,content_binding:content})]),max_member_bytes:65536,capacity_binding:managed_capacity};
  let derived_binding=save("derived-selection.json",&encode(&derived).unwrap());facts.effect_inputs.derived=Some(derived_binding.clone());
  let mut next=service.clone();next.revision=2;next.predecessor_binding=Some(service_binding.clone());next.template_binding=save("template-next.json",&encode(&facts).unwrap());next.source_originals=vec![native,reservation,facts.revocation_binding.clone(),facts.capacity_custody_binding.clone()];
  let next_binding=save("service-next.json",&encode(&next).unwrap());let request=HostProfileRequest{schema_version:"lab-broker-host-profile-reselection/v1".into(),prior:service_binding,next:next_binding,revision:2,recipient:caller.clone(),channel_binding:next.profile_channel_binding.clone(),challenge:challenge().unwrap(),not_before:now-1,expires_at:now+120};manager.call(&f.manager.sign(&f.manager_key,&request).unwrap()).unwrap();
  let before=state::owned_inventory_digest(&rh,4096,16777216).unwrap();let raw=reviewer_frame_second(&intent,"repair_derived",1,"pointer-committed",Some(&derived_binding));let result=session.dispatch(&raw);
  if mode==0{let reply=match result.unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("derived pending cold")};assert_eq!(response_signer.verify::<Value>(&reply).unwrap()["status"],"PASS");assert_eq!(fs::read(&existing).unwrap(),b"bounded derived output");}
  else{assert!(matches!(result,Err(roots::Error("DERIVED_DECLARED_TARGET_OPERATION"))));assert_eq!(before,state::owned_inventory_digest(&rh,4096,16777216).unwrap());}
  assert_eq!(fs::read(canonical).unwrap(),canonical_before);assert_eq!(fs::read(f.f.base.join("stage/HEAD.json")).unwrap(),pointer_raw);if mode==0{let l=ledger::Ledger::open(&f.control,held,ledger::TrustedSelection{confirmation:session.fixture_observation().unwrap().0,posture:ledger::Posture::Fixture}).unwrap();assert!(l.outcome("operation-derived-second").is_some_and(|(o,_)|*o==ledger::Outcome::Committed));assert!(l.outcome("operation-1").is_some_and(|(o,_)|*o==ledger::Outcome::Committed));}h.join().unwrap();c.join().unwrap();p.join().unwrap();
  session.fixture_observation().unwrap().0
 })
}

fn reviewer_frame_second(i:&Intent,verb:&str,sequence:u64,phase:&str,subject:Option<&Binding>)->Vec<u8>{
 let now=now_seconds().unwrap();let payload=match subject{Some(b)=>json!({"root_id":"managed","subject_binding":b}),None=>json!({"root_id":"managed","stage_name":"unused-derived-stage","max_bytes":64})};
 let mut request=json!({"schema_version":"lab-completion-broker-request/v1","request_id":format!("derived-{sequence}"),"operation_id":"operation-derived-second","sequence":sequence,"activation_binding":i.scope["activation_binding"],"store_id":i.scope["store_id"],"instance_id":i.scope["instance_id"],"slot_epoch":1,"principal_ref":i.scope["principal_ref"],"verb":verb,"intent_binding":i.scope["intent_binding"],"authorization_binding":wire::content_digest(b""),"payload":payload});
 let grant=json!({"kind":if subject.is_some(){"control"}else{"empty-stage"},"root_id":"managed","stage_binding":null,"member":null,"preimage_binding":null,"full_sha256":null,"full_length":0,"chunk_size":0,"sequence_start":sequence,"chunks":[{"sequence":sequence,"offset":0,"length":0,"core_sha256":wire::hash(&wire::signing_bytes(&wire::authorization_core(&request).unwrap()).unwrap())}]});
 let permit=authority::signed_record(&json!({"schema_version":"lab-completion-broker-permit/v1","permit_id":format!("derived-permit-{sequence}"),"operation_fingerprint":authority::operation_fingerprint(&i.core).unwrap(),"basis_binding":i.core["authority_basis_binding"],"scope":i.scope,"limits":i.core["limits"],"allowed_verb":verb,"allowed_phase":phase,"not_before":now-1,"expires_at":now+100,"grant":grant}),"fixture-issuer",&i.key).unwrap();request["authorization_binding"]=wire::content_digest(&encode(&permit).unwrap());encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":request,"permit":permit})).unwrap()
}

#[test]fn reviewer_full_derived_wrong_committed_target_refuses(){reviewer_seed(3)}
