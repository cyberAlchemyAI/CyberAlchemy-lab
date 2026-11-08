// Reviewer fixture construction only: no supervisor import, cgroup launch,
// actual process containment claim, or production enrollment. Closed original
// records are independently selected in Fixture domain and fed to the fixed
// broker's real native-original adapter and Session close path.
fn reviewer_regression_save(root:&Root,path:&str,value:&Value)->Binding {
 let raw=encode(value).unwrap();let p=std::path::Path::new(&root.selection().absolute_path).join(path);
 let mut out=fs::OpenOptions::new().write(true).create_new(true).open(&p).unwrap();
 use std::io::Write;out.write_all(&raw).unwrap();out.sync_all().unwrap();
 fs::set_permissions(&p,fs::Permissions::from_mode(0o600)).unwrap();
 bound(&root.selection().root_id,path,&raw).unwrap()
}
fn reviewer_regression_selection(f:&HostFixture,native:&Root,current:&HostConfirmation,outcome:&str)->(Binding,Vec<Binding>){
 let now=now_seconds().unwrap();let ns=now*1_000_000_000;let operation=&f.f.scope.operation;
 let root_path=std::path::Path::new(&native.selection().absolute_path);
 for name in ["originals","records"]{fs::create_dir(root_path.join(name)).unwrap();fs::set_permissions(root_path.join(name),fs::Permissions::from_mode(0o700)).unwrap();}
 let gp=f.f.base.join("reviewer-inert-group");fs::create_dir(&gp).unwrap();fs::set_permissions(&gp,fs::Permissions::from_mode(0o700)).unwrap();
 let group=roots::Identity::observe(&fs::File::open(&gp).unwrap()).unwrap();
 let containment=HostFixture::save(&f.input,"reviewer-containment-selection.json",b"Fixture-only independently selected containment description; no actual cgroup qualification");
 let execution=HostFixture::save(&f.input,"reviewer-execution-selection.json",b"Fixture-only fixed worker execution selection");
 let history=HostFixture::save(&f.input,"reviewer-history-selection.json",b"Fixture-only complete original family selection");
 let custody=HostFixture::save(&f.input,"reviewer-native-custody.json",b"Fixture-only selected original journal custody");
 let header=reviewer_regression_save(native,"header.json",&json!({"schema_version":"lab-supervisor-attempt-journal/v1","domain":"fixture","root_id":native.selection().root_id,"root":native.identity(),"control_root":current.root,"authority_domain":current.authority_domain,"control_header_sha256":current.header_sha256,"supervisor_root_binding":containment,"supervisor_root_identity":group,"custody_binding":custody,"limits":{"max_records":16,"max_original_bytes":65536,"max_record_bytes":65536,"max_total_bytes":2097152,"max_attempts":2}}));
 let start=reviewer_regression_save(native,"originals/0000000000000001.json",&json!({"schema_version":"lab-contained-attempt-start/v1","operation":operation,"attempt_id":"reviewer-native-attempt","containment_binding":containment,"group_identity":group,"execution_binding":execution,"historical_selection":history,"created_utc_ns":ns-1_000_000_000,"dispatch_until_utc_ns":ns+60_000_000_000u64,"cleanup_until_utc_ns":ns+120_000_000_000u64,"limits":{"pids":4,"memory_bytes":1048576,"cpu_quota_us":1000,"output_bytes":4096,"runtime_ms":1000,"cleanup_ms":1000}}));
 let first=reviewer_regression_save(native,"records/0000000000000001.json",&json!({"schema_version":"lab-supervisor-attempt-record/v1","sequence":1,"previous_sha256":header.sha256,"operation":operation,"attempt_id":"reviewer-native-attempt","event":"start","control_preimage":current,"original_binding":start,"original_start_binding":start}));
 let start_checkpoint=json!({"schema_version":"lab-host-supervisor-checkpoint/v1","domain":"fixture","journal_root":native.identity(),"root_id":native.selection().root_id,"journal_header_sha256":header.sha256,"predecessor":{"sequence":0,"sha256":header.sha256},"head":{"sequence":1,"sha256":first.sha256},"control_preimage":current,"operation":operation,"attempt_id":"reviewer-native-attempt"});
 let start_checkpoint_binding=HostFixture::save(&f.input,"reviewer-start-checkpoint.json",&encode(&start_checkpoint).unwrap());
 let terminal=reviewer_regression_save(native,"originals/0000000000000002.json",&json!({"schema_version":"lab-contained-attempt-terminal/v1","domain":"fixture","operation":operation,"attempt_id":"reviewer-native-attempt","containment_binding":containment,"actual_group_identity":group,"execution_binding":execution,"original_start_binding":start,"historical_selection":history,"start_utc_ns":ns,"end_utc_ns":ns+1,"elapsed_ns":1,"child_pid":101,"pid_start_ticks":1,"reason":"normal","exit_code":0,"signal":null,"primary_error":null,"cleanup_errors":[],"direct_child_reaped":true,"subtree_empty":true,"inherited_descriptors_closed":true,"workload_started":true,"historical_complete":true}));
 let second=reviewer_regression_save(native,"records/0000000000000002.json",&json!({"schema_version":"lab-supervisor-attempt-record/v1","sequence":2,"previous_sha256":first.sha256,"operation":operation,"attempt_id":"reviewer-native-attempt","event":"terminal","control_preimage":current,"original_binding":terminal,"original_start_binding":start}));
 let checkpoint=json!({"schema_version":"lab-host-supervisor-checkpoint/v1","domain":"fixture","journal_root":native.identity(),"root_id":native.selection().root_id,"journal_header_sha256":header.sha256,"predecessor":{"sequence":1,"sha256":first.sha256},"head":{"sequence":2,"sha256":second.sha256},"control_preimage":current,"operation":operation,"attempt_id":"reviewer-native-attempt"});
 let checkpoint_binding=HostFixture::save(&f.input,"reviewer-terminal-checkpoint.json",&encode(&checkpoint).unwrap());
 let selection=SupervisorEvidenceSelection{schema_version:"lab-broker-supervisor-original-selection/v1".into(),journal_root_id:native.selection().root_id.clone(),journal_prefix:String::new(),header_binding:header,checkpoint_binding:checkpoint_binding.clone(),original_start_binding:start.clone(),records:vec![first,second],originals:vec![start.clone(),terminal.clone()],cleanup_checkpoint_binding:start_checkpoint_binding.clone(),execution_binding:execution.clone(),historical_binding:history.clone()};
 let selected=HostFixture::save(&f.input,"reviewer-native-selection.json",&encode(&selection).unwrap());
 let cleanup=json!({"schema_version":"lab-supervisor-cleanup-selection/v1","domain":"fixture","operation":operation,"original_start_binding":start,"original_checkpoint_binding":start_checkpoint_binding,"containment_binding":containment,"group_identity":group,"current_control":current,"history_binding":history,"expires_utc_ns":ns+120_000_000_000u64,"max_cleanup_ms":1000});
 let authority=HostFixture::save(&f.input,"reviewer-cleanup-authority.json",&encode(&cleanup).unwrap());
 let identity=HostFixture::save(&f.input,"reviewer-worker-native-identity.json",b"Fixture-only original worker identity: pid101 start1; no live child observation");
 let worker=WorkerIdentityOriginal{schema_version:"lab-broker-worker-identity/v1".into(),domain:Domain::Fixture,operation:operation.clone(),attempt_id:"reviewer-native-attempt".into(),original_start_binding:start,group_identity:group,child_pid:101,pid_start_ticks:1,native_identity_binding:identity.clone(),execution_binding:execution.clone()};
 let worker_binding=HostFixture::save(&f.input,"reviewer-worker-selection.json",&encode(&worker).unwrap());
 let proof=SupervisorClosure{schema_version:"lab-broker-supervisor-closure/v1".into(),operation:operation.clone(),execution_scope:f.f.scope.execution_scope.clone(),control_confirmation:current.clone(),authority_binding:authority.clone(),prior_close_terminal:None,original_terminal_binding:terminal.clone(),containment_selection_binding:containment.clone(),native_evidence_binding:selected.clone(),worker_identity_binding:worker_binding.clone(),cleanup_original_binding:terminal.clone(),populated:false,all_owned_children_reaped:true,cleanup:"clean".into(),outcome:outcome.into(),not_before:now-1,expires_at:now+120};
 let proof_binding=HostFixture::save(&f.input,"reviewer-supervisor-closure.json",&encode(&proof).unwrap());
 let all=vec![proof_binding.clone(),terminal,containment,selected,authority,worker_binding,identity,execution,history,custody,checkpoint_binding,start_checkpoint_binding];
 (proof_binding,all)
}
fn reviewer_close_frame(intent:&Intent,sequence:u64,phase:&str,subject:&Binding)->(Vec<u8>,RecoveryFact){
 let now=now_seconds().unwrap();let preimages=vec![subject.clone()];
 let mut request=json!({"schema_version":"lab-completion-broker-request/v1","request_id":format!("reviewer-close-{sequence}"),"operation_id":"operation-1","sequence":sequence,"activation_binding":intent.scope["activation_binding"],"store_id":intent.scope["store_id"],"instance_id":intent.scope["instance_id"],"slot_epoch":1,"principal_ref":intent.scope["principal_ref"],"verb":"close_family","intent_binding":intent.scope["intent_binding"],"authorization_binding":wire::content_digest(b""),"payload":{"root_id":"stage","subject_binding":subject}});
 let permit=authority::signed_record(&json!({"schema_version":"lab-completion-recovery-authorization/v1","authorization_id":format!("reviewer-recovery-{sequence}"),"operation_id":"operation-1","operation_fingerprint":authority::operation_fingerprint(&intent.core).unwrap(),"scope":intent.scope,"allowed_verb":"close_family","message_core_sha256":wire::hash(&wire::signing_bytes(&wire::authorization_core(&request).unwrap()).unwrap()),"subject_binding":subject,"not_before":now-1,"expires_at":now+60,"observed_phase":phase,"action":"close_family","preimages":preimages,"next_sequence":sequence,"next_offset":0,"cumulative_bytes":0,"cumulative_actions":sequence,"original_deadline":intent.core["operation_expires_at"]}),"fixture-issuer",&intent.key).unwrap();
 let binding=wire::content_digest(&encode(&permit).unwrap());request["authorization_binding"]=binding.clone();
 (encode(&json!({"schema_version":"lab-completion-broker-frame/v1","request":request,"permit":permit})).unwrap(),RecoveryFact{authorization_binding:binding,subject_binding:subject.clone(),preimages,action:"close_family".into(),consumed:false})
}

fn reviewer_assert_closed_records(f:&HostFixture,outcomes:usize){
 let mut names:Vec<_>=fs::read_dir(f.f.base.join("control/records")).unwrap().map(|e|e.unwrap().path()).collect();names.sort();
 let rows:Vec<Value>=names.iter().map(|p|decode(&fs::read(p).unwrap(),65536).unwrap()).collect();
 let changes:Vec<lab_control_store::ledger::Change>=rows.iter().map(|r|serde_json::from_value(r["change"].clone()).unwrap()).collect();
 assert_eq!(changes.iter().filter(|c|matches!(c,lab_control_store::ledger::Change::Outcome{..})).count(),outcomes);
 assert_eq!(changes.iter().filter(|c|matches!(c,lab_control_store::ledger::Change::SlotState{state:lab_control_store::ledger::SlotPhase::Closing,..})).count(),1);
 assert_eq!(changes.iter().filter(|c|matches!(c,lab_control_store::ledger::Change::SlotState{state:lab_control_store::ledger::SlotPhase::Closed,..})).count(),1);
 assert!(matches!(changes.last().unwrap(),lab_control_store::ledger::Change::SlotState{state:lab_control_store::ledger::SlotPhase::Closed,..}));
}
#[test]fn reviewer_regression_terminal_only_committed_close(){reviewer_regression_lifecycle(3)}
#[test]fn reviewer_regression_restarted_unknown_refuses_before_intent(){reviewer_regression_lifecycle(2)}
#[test]fn reviewer_regression_terminal_one_byte_short_refuses_before_intent(){reviewer_regression_lifecycle(4)}
fn reviewer_regression_lifecycle(native_mode:u8){
 let mode=0u8;
 use lab_control_store::{custody,ledger};
 let mut f=HostFixture::new();let intent=Intent::new(&mut f);
 let np=f.f.base.join("native-attempts");fs::create_dir(&np).unwrap();fs::set_permissions(&np,fs::Permissions::from_mode(0o700)).unwrap();
 let native_root=Root::open(Root::capture_fixture(&np,"native",[b("native-alias",b"a"),b("native-ancestor",b"b"),b("native-acl",b"c")],f.f.scope.execution_scope.clone()).unwrap(),Domain::Fixture).unwrap();
 f.facts.roots.push(native_root.selection().clone());f.selection.roots.push(native_root.selection().clone());
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
 let nh=native_root.exclusive(Duration::from_millis(100)).unwrap();
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
   if native_mode==2{host_service.serve_one(&hserver).unwrap();return}if native_mode==1{return}
   if mode>=8{host_service.serve_one(&hserver).unwrap();return}
   if mode>=5{return}
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();host_service.serve_one(&hserver).unwrap();
   if mode==3{host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();return}
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
   if mode==1{host_service.serve_profile_one(&mserver).unwrap();}host_service.serve_one(&hserver).unwrap();
   if mode==4{host_service.serve_profile_one(&mserver).unwrap();for _ in 0..3{host_service.serve_one(&hserver).unwrap();}}
   host_service.serve_profile_one(&mserver).unwrap();host_service.serve_one(&hserver).unwrap();
  });
  let control_task=threads.spawn(||{for _ in 0..if native_mode==2{1}else if native_mode==4{2}else{4}{cw.serve_one(&cserver).unwrap();sender.send(cw.confirmation().clone()).unwrap();}});
  let receipt_ref=&receipt_reader;let control_ref=&control_reader;let response_ref=&response_signer;let caller_ref=&caller;
  let prefix_task=threads.spawn(move ||{let mut current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();for i in 0..if native_mode==2{1}else if native_mode==4{5}else if native_mode==1{2}else{6}{
   let raw=pserver.receive().unwrap();let q:PrefixRequest=decode(&raw,65536).unwrap();if native_mode==1&&i==1{for _ in 0..3{current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();}}else if native_mode!=1&&native_mode!=2&&i==4{current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();}else if native_mode!=1&&native_mode!=2&&i==5{for _ in 0..2{current=receiver.recv_timeout(Duration::from_secs(10)).unwrap();}}
   let response=pw.confirm_originals(&q,caller_ref,receipt_ref,control_ref,&current,&limits(),response_ref).unwrap();pserver.send(&response).unwrap();}
   if native_mode==2{let raw=pserver.receive().unwrap();let q:PrefixInspectionRequest=decode(&raw,65536).unwrap();let response=pw.inspect(&q,caller_ref,caller_ref,&q.channel_binding,&current,&q.current_execution_scope).unwrap();pserver.send(&response).unwrap();}
   if mode==4{let raw=pserver.receive().unwrap();let q:PrefixInspectionRequest=decode(&raw,65536).unwrap();let response=pw.inspect(&q,caller_ref,caller_ref,&q.channel_binding,&current,&q.current_execution_scope).unwrap();pserver.send(&response).unwrap();}
  });
  let facts=host.query(&wire::Frame::decode(&reserve_frame).unwrap()).unwrap();let roots=BTreeMap::from([("native".into(),&nh),("input".into(),&ih),("receipts".into(),&rh),("stage".into(),&sh),("control".into(),&ch),("generation-journal".into(),&jh)]);
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
  let mut abort_frame=None;
  if native_mode==1||native_mode==2{let(subject,inputs)=reviewer_regression_selection(&f,&native_root,&conf,"aborted");let(raw,recovery)=reviewer_close_frame(&intent,1,if native_mode==2{"UNKNOWN"}else{"reserved"},&subject);next_facts.selected_inputs.extend(inputs);next_facts.effect_inputs.supervisor=Some(subject);next_facts.recovery=Some(recovery);abort_frame=Some(raw);}
  let mut next_cap=cap.clone();next_cap.control_confirmation=conf;next_cap.remaining=next_facts.remaining_capacity.clone();next_facts.capacity_custody_binding=HostFixture::save(&f.input,"capacity-after-reserve.json",&encode(&next_cap).unwrap());
  let stage_capacity=CapacityOriginal{physical_root:f.f.stage.identity().clone(),remaining:quota::Remaining{inventory_sha256:state::owned_inventory_digest(&sh,4096,16*1024*1024).unwrap(),prefix_sha256:next_facts.remaining_capacity.prefix_sha256.clone(),bytes:16*1024*1024,inodes:4096},..next_cap.clone()};
  let stage_capacity_binding=HostFixture::save(&f.input,"stage-capacity-after-reserve.json",&encode(&stage_capacity).unwrap());next_facts.additional_capacity_bindings=vec![stage_capacity_binding.clone()];
  let mut originals:Vec<_>=f.selection.source_originals.iter().map(|b|if b==&f.facts.capacity_custody_binding{next_facts.capacity_custody_binding.clone()}else{b.clone()}).collect();originals.push(stage_capacity_binding);let(next,_,request)=f.successor(&next_facts,originals);
  let update=manager_channel.call(&request).unwrap();let receipt:HostProfileReceipt=f.signer.verify(&update).unwrap();assert_eq!(receipt.request.revision,2);
  if native_mode==2{
   let frame=abort_frame.unwrap();let facts=host.query(&wire::Frame::decode(&frame).unwrap()).unwrap();
   let now=now_seconds().unwrap();let q=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:f.f.scope.history_key().unwrap(),recipient:caller.clone(),channel_binding:psel.channel_binding.clone(),challenge:challenge().unwrap(),current_ledger_confirmation:next_facts.ledger_confirmation.clone(),current_execution_scope:f.f.scope.execution_scope.clone(),not_before:now-1,expires_at:now+60};
   let selected=prefix_client.current(&q,&f.f.scope,&scope_binding).unwrap();drop(session);
   let mut restarted=Session::restart(&host,&control_client,&prefix_client,&f.control,&held,roots,&runtime_raw,runtime_binding,facts,selected,SelectedSigner::select(&response_raw,&runtime.receipt_signer_binding,Domain::Fixture,"broker-response").unwrap(),f.f.response_key.clone()).unwrap();
   let before=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();let before_control=restarted.fixture_observation().unwrap().0;
   assert!(matches!(restarted.dispatch(&frame),Err(roots::Error("RESTART_CLOSE_NEEDS_TRANSACTION_OUTCOME"))));
   assert_eq!(before,state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap());assert_eq!(before_control,restarted.fixture_observation().unwrap().0);
   assert!(!f.f.base.join("receipts/sequence-0000000000000002").exists());
   let ledger=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:before_control,posture:ledger::Posture::Fixture}).unwrap();assert!(ledger.outcome("operation-1").is_none());
   host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return;
  }
  if native_mode==1{let reply=match session.dispatch(&abort_frame.unwrap()).unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("close pending")};assert_eq!(response_signer.verify::<Value>(&reply).unwrap()["durable_phase"],"terminal");
   let current=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:session.fixture_observation().unwrap().0,posture:ledger::Posture::Fixture}).unwrap();assert_eq!(current.outcome("operation-1").unwrap().0,ledger::Outcome::Aborted);
   reviewer_assert_closed_records(&f,1);host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return;}
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
  let observation=session.fixture_observation().unwrap();let current=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:observation.0.clone(),posture:ledger::Posture::Fixture}).unwrap();let old_outcome=current.outcome("operation-1").cloned();assert_eq!(old_outcome.as_ref().unwrap().0,ledger::Outcome::Committed);
  let(subject,inputs)=reviewer_regression_selection(&f,&native_root,&observation.0,"committed");let(close,recovery)=reviewer_close_frame(&intent,5,"pointer-committed",&subject);
  facts5.operation_state=OriginalOperationState::Present{effect_eligible:false,outcome:old_outcome.clone()};facts5.effect_inputs.supervisor=Some(subject);facts5.selected_inputs.extend(inputs);facts5.recovery=Some(recovery);
  if native_mode==3||native_mode==4{facts5.remaining_capacity.bytes=limits().cleanup_bytes().unwrap()-if native_mode==4{1}else{0};facts5.remaining_capacity.inodes=quota::CLEANUP_FILES+1;assert!(facts5.remaining_capacity.bytes<limits().cleanup_bytes().unwrap()+limits().max_record_bytes*quota::SEQUENCE_FILES);}
  advance_profile(&f,&manager_channel,&profile5,&binding5,facts5,observation,&sh);
  if native_mode==4{let before=state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap();let before_control=session.fixture_observation().unwrap().0;assert!(matches!(session.dispatch(&close),Err(roots::Error("TERMINAL_PHYSICAL_RESERVE"))));assert_eq!(before,state::owned_inventory_digest(&rh,4096,16*1024*1024).unwrap());assert_eq!(before_control,session.fixture_observation().unwrap().0);host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();return;}

  let reply=match session.dispatch(&close).unwrap(){DispatchResult::Reply(r)=>r,_=>panic!("close pending")};assert_eq!(response_signer.verify::<Value>(&reply).unwrap()["durable_phase"],"terminal");
  let current=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:session.fixture_observation().unwrap().0,posture:ledger::Posture::Fixture}).unwrap();assert_eq!(current.outcome("operation-1").cloned(),old_outcome);reviewer_assert_closed_records(&f,1);
  host_task.join().unwrap();control_task.join().unwrap();prefix_task.join().unwrap();
 });
}

