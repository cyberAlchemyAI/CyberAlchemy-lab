use super::*;
use std::os::fd::{OwnedFd,FromRawFd,AsRawFd};
fn pair(name:&str,peer:&Caller)->(Channel,Channel){
 let mut fd=[-1;2];assert_eq!(unsafe{libc::socketpair(libc::AF_UNIX,libc::SOCK_SEQPACKET|libc::SOCK_CLOEXEC,0,fd.as_mut_ptr())},0);
 let make=|raw:i32|{let owned=unsafe{OwnedFd::from_raw_fd(raw)};let mut s:libc::stat=unsafe{std::mem::zeroed()};assert_eq!(unsafe{libc::fstat(owned.as_raw_fd(),&mut s)},0);
 Channel::from_selected(owned,ChannelSelection{schema_version:"lab-broker-fixed-channel/v1".into(),channel_binding:b(name,name.as_bytes()),device:s.st_dev,inode:s.st_ino,peer:peer.clone(),max_packet_bytes:65536,timeout_ms:2000}).unwrap()};(make(fd[0]),make(fd[1]))
}
fn service_case(mode:u8){
 use lab_control_store::{custody,ledger};
 let mut f=HostFixture::new();let(client,server)=pair("prefix-service-channel",&f.f.scope.recipient);
 f.f.scope.channel_binding=server.selection().channel_binding.clone();
 let scope=HostFixture::save(&f.input,"prefix-scope.json",&encode(&f.f.scope).unwrap());
 let locks=f.control.acquire(custody::Rank::Journal,Duration::from_millis(100)).unwrap();let held=locks.borrow().unwrap();
 let mut ledger=ledger::Ledger::open(&f.control,&held,ledger::TrustedSelection{confirmation:f.f.ledger.clone(),posture:ledger::Posture::Fixture}).unwrap();
 let current=if mode==4{f.f.ledger.clone()}else{let pending=ledger.append(&held,ledger::Change::Reserve{operation:f.f.scope.operation.clone()}).unwrap();let current=pending.requested_confirmation().clone();ledger.acknowledge(&held,pending,current.clone()).unwrap();current};f.f.ledger=current.clone();
 // The original host facts still select the pre-Reserve head. The prefix server
 // obtains current control exclusively from the concrete verified witness.
 let control_sel=f.selection.roots.iter().find(|r|r.root_id=="control").unwrap();let control_read=OriginalDirectory::open(control_sel.clone(),Domain::Fixture).unwrap();
 let path=f.f.base.join("prefix-control-witness");fs::create_dir(&path).unwrap();fs::set_permissions(&path,fs::Permissions::from_mode(0o700)).unwrap();
 let control_root=Root::open(Root::capture_fixture(&path,"prefix-control-witness",[b("a",b"a"),b("b",b"b"),b("c",b"c")],f.f.scope.execution_scope.clone()).unwrap(),Domain::Fixture).unwrap();
 let ch=control_root.exclusive(Duration::from_millis(100)).unwrap();let wh=f.f.witness.exclusive(Duration::from_millis(100)).unwrap();let rh=f.f.receipt.exclusive(Duration::from_millis(100)).unwrap();let sh=f.f.stage.exclusive(Duration::from_millis(100)).unwrap();
 let(cs,ck)=signer("control-confirmation",29);let control_service=b("prefix-control-service",b"fixed selected control service");
 let mut chosen=current.clone();if mode==2{chosen.writer=WriterFence{instance:"new-writer".into(),epoch:2};}
 let cw=ControlWitness::open(&ch,&control_read,&cs,ck,control_service.clone(),f.f.scope.recipient.clone(),b("control-channel",b"control channel"),current.clone(),chosen.clone(),0,roots::hash(&encode(&current).unwrap()),&[f.f.receipt.identity().clone(),f.f.stage.identity().clone(),f.f.witness.identity().clone()]).unwrap();
 let response_raw=encode(&SignerSelection{schema_version:"lab-broker-fixed-signer/v1".into(),issuer_ref:f.f.response_signer.issuer().into(),purpose:"broker-response".into(),algorithm:"ed25519".into(),adapter:"owner-hex-v1".into(),public_key:wire::hex(&f.f.response_key.verifying_key().to_bytes()),domain:Domain::Fixture}).unwrap();
 // Preserve the exact enrollment locator used by the retained response verifier.
 let rb=HostFixture::save(&f.input,"prefix-response-signer.json",&response_raw);let rs=SelectedSigner::select(&response_raw,&rb,Domain::Fixture,"broker-response").unwrap();
 let lb=HostFixture::save(&f.input,"prefix-limits.json",&encode(&limits()).unwrap());let now=now_seconds().unwrap();
 let capacity=PrefixCapacityOriginal{schema_version:"lab-broker-prefix-capacity/v1".into(),domain:Domain::Fixture,history_key:f.f.scope.history_key().unwrap(),physical_root:f.f.witness.identity().clone(),control_root:chosen.root.clone(),control_header_sha256:chosen.header_sha256.clone(),held_reservation_binding:f.selection.source_originals[1].clone(),max_confirmations:2,reserved_bytes:if mode==3{65535}else{131072},reserved_inodes:2,not_before:now-1,expires_at:now+120};
 let cap=HostFixture::save(&f.input,"prefix-capacity.json",&encode(&capacity).unwrap());
 let role=PrefixServiceSelection{schema_version:"lab-broker-prefix-service/v1".into(),domain:Domain::Fixture,original_scope_binding:scope.clone(),prefix_signer_binding:f.f.proof_signer.binding().clone(),response_signer_binding:rb.clone(),limits_binding:lb.clone(),control_service_binding:control_service,control_signer_binding:cs.binding().clone(),receipt_root_id:"receipts".into(),witness_root:f.f.witness.identity().clone(),recipient:f.f.scope.recipient.clone(),channel_binding:if mode==1{b("other-channel",b"other channel")}else{server.selection().channel_binding.clone()},current_writer:chosen.writer.clone(),current_execution_scope:f.f.scope.execution_scope.clone(),capacity_binding:cap.clone(),not_before:now-1,expires_at:now+120};
 if (6..=9).contains(&mode){
  f.facts.revocation_binding=HostFixture::save(&f.input,"prefix-revoked.json",&encode(&RevocationOriginal{schema_version:"lab-broker-host-revocation/v1".into(),issuer_enrollment_binding:f.facts.issuer_enrollment_binding.clone(),native_original_binding:f.selection.source_originals[0].clone(),revoked:mode==6,not_before:now-10,expires_at:if mode==7{now}else{now+120}}).unwrap());f.selection.source_originals.push(f.facts.revocation_binding.clone());
 }
 if mode==8{f.facts.activation_expires_at=now;}if mode==9{f.facts.expires_at=now;}
 let role_b=HostFixture::save(&f.input,"prefix-role.json",&encode(&role).unwrap());f.facts.current_prefix_binding=role_b.clone();f.facts.quota_binding=lb.clone();
 f.selection.source_originals.extend([role_b,rb,lb,cap]);f.selection.template_binding=HostFixture::save(&f.input,"prefix-template.json",&encode(&f.facts).unwrap());f.selected_binding=HostFixture::save(&f.input,"prefix-service.json",&encode(&f.selection).unwrap());let mut host=f.service();
 let mut w=PrefixWitness::open(&wh,f.f.scope.clone(),scope.clone(),PrefixHead::genesis(&f.f.scope).unwrap(),&f.f.proof_signer,f.f.proof_key.clone()).unwrap();
 if mode==4{
  let q=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:f.f.scope.history_key().unwrap(),recipient:f.f.scope.recipient.clone(),channel_binding:server.selection().channel_binding.clone(),challenge:roots::hash(b"genesis bootstrap"),current_ledger_confirmation:current,current_execution_scope:f.f.scope.execution_scope.clone(),not_before:now-1,expires_at:now+60};
  client.send(&encode(&q).unwrap()).unwrap();w.serve_one(&server,&host,&cw).unwrap();let proof:PrefixInspection=f.f.proof_signer.verify(&client.receive().unwrap()).unwrap();assert_eq!(proof.head,PrefixHead::genesis(&f.f.scope).unwrap());assert!(proof.original_confirmation_binding.is_none());assert!(ledger.operation(&f.f.scope.operation.operation_id).is_none());return;
 }
 let mut j=ReceiptJournal::open_empty(&rh,f.f.scope.clone(),limits()).unwrap();let raw=f.f.frame(0);let frame=wire::Frame::decode(&raw).unwrap();let mut p=j.begin(&frame,&raw,&f.f.scope.operation.fingerprint,&current,&reserve(&j)).unwrap();
 let action=members::Action{request:frame.request().clone(),wire:frame.wire_digest().into(),fingerprint:f.f.scope.operation.fingerprint.clone(),domain:Domain::Fixture,stage_binding:None};let mut stage=members::Stage::create(&sh,&action).unwrap();let r=j.member_receipt(&mut p,stage.pending().unwrap(),stage.proposed_state().unwrap()).unwrap();let member_binding=r.binding().clone();stage.acknowledge(r).unwrap();
 let response=encode(&authority::sign_receipt(&frame,"staging","PASS",None,serde_json::to_value(member_binding).unwrap(),rs.issuer(),&f.f.response_key).unwrap()).unwrap();j.finish(&mut p,Some(&stage.snapshot().unwrap()),&response,"staging","PASS").unwrap();
 let request_now=now_seconds().unwrap();let request=j.confirmation_request(&p,roots::hash(b"fresh fixture CAS"),request_now,request_now+if mode==10{2}else{60}).unwrap();
 if (12..=14).contains(&mode){
  let original_frame=fs::read(f.f.base.join("receipts/sequence-0000000000000001/frame.json")).unwrap();
  drop(p);drop(j);
  if mode==12{
   client.send(&encode(&request).unwrap()).unwrap();w.serve_one(&server,&host,&cw).unwrap();let proof_bytes=client.receive().unwrap();
   let selected=service_inspection(&f,&scope,&client,&server,&mut w,&host,&cw,&current);
   assert!(RestartedPrefix::inspect_recovery(&rh,f.f.scope.clone(),limits(),selected,&f.f.proof_signer,&rs).is_err());
   let selected=service_inspection(&f,&scope,&client,&server,&mut w,&host,&cw,&current);let verified=selected.verify_original(&proof_bytes,&f.f.proof_signer,&f.f.scope).unwrap();
   RestartedPrefix::retain_missing_confirmation(&rh,&f.f.scope,&limits(),&selected,&verified,&f.f.proof_signer,&rs).unwrap();
   assert!(!fs::read_dir(f.f.base.join("receipts")).unwrap().any(|e|e.unwrap().file_name().to_string_lossy().starts_with("recovery-")));return
  }
  let selected=service_inspection(&f,&scope,&client,&server,&mut w,&host,&cw,&current);
  let mut journal=RestartedPrefix::inspect_recovery(&rh,f.f.scope.clone(),limits(),selected,&f.f.proof_signer,&rs).unwrap().into_recovery_journal();
  let subject=encode(&journal.recovery_subject().unwrap()).unwrap();let subject_binding=HostFixture::save(&f.input,"selected-orphan-recovery.json",&subject);
  let mut v:serde_json::Value=decode(&f.f.frame(1),65536).unwrap();v["request"]["verb"]=json!("reconcile_operation");v["request"]["payload"]=json!({"root_id":"receipts","subject_binding":subject_binding});let raw=encode(&v).unwrap();let frame=wire::Frame::decode(&raw).unwrap();
  let mut pending=journal.begin_terminal(&frame,&raw,&f.f.scope.operation.fingerprint,&current,&reserve(&journal)).unwrap();journal.put(&mut pending,"orphan-inventory.json",&subject).unwrap();
  let response=encode(&authority::sign_receipt(&frame,"quarantined","UNKNOWN",Some("ORIGINAL_EFFECT_UNKNOWN"),serde_json::Value::Null,rs.issuer(),&f.f.response_key).unwrap()).unwrap();journal.finish(&mut pending,None,&response,"quarantined","UNKNOWN").unwrap();
  let time=now_seconds().unwrap();let recovery=journal.confirmation_request(&pending,challenge().unwrap(),time,time+60).unwrap();
  let(winning,losing)=if mode==13{(&request,&recovery)}else{(&recovery,&request)};
  client.send(&encode(winning).unwrap()).unwrap();w.serve_one(&server,&host,&cw).unwrap();let exact=client.receive().unwrap();
  client.send(&encode(losing).unwrap()).unwrap();assert!(w.serve_one(&server,&host,&cw).is_err());assert_eq!(w.head().ordinal,1);
  assert_eq!(fs::read(f.f.base.join("receipts/sequence-0000000000000001/frame.json")).unwrap(),original_frame);
  assert!(fs::read_dir(f.f.base.join("receipts")).unwrap().any(|e|e.unwrap().file_name().to_string_lossy().starts_with("recovery-")));
  if mode==14{
   let verified=VerifiedPrefix::verify(&exact,&f.f.proof_signer,&recovery,now_seconds().unwrap()).unwrap();journal.confirm(pending,verified,&rs).unwrap();drop(journal);
   let selected=service_inspection(&f,&scope,&client,&server,&mut w,&host,&cw,&current);let mut restored=RestartedPrefix::inspect(&rh,f.f.scope.clone(),limits(),selected,&f.f.proof_signer,&rs).unwrap().into_recovery_journal();
   assert_eq!(restored.consumed_requests().unwrap().len(),2);assert_eq!(restored.consumed_requests().unwrap()[&0],request.wire_sha256);
   let old=wire::Frame::decode(&original_frame).unwrap();assert!(restored.begin(&old,&original_frame,&f.f.scope.operation.fingerprint,&current,&reserve(&restored)).is_err());
   let mut changed:serde_json::Value=decode(&original_frame,65536).unwrap();changed["request"]["request_id"]=json!("different-consumed-wire");let bytes=encode(&changed).unwrap();let old=wire::Frame::decode(&bytes).unwrap();assert!(restored.begin(&old,&bytes,&f.f.scope.operation.fingerprint,&current,&reserve(&restored)).is_err());
  }else{
   drop(pending);drop(journal);let selected=service_inspection(&f,&scope,&client,&server,&mut w,&host,&cw,&current);let verified=selected.verify_original(&exact,&f.f.proof_signer,&f.f.scope).unwrap();RestartedPrefix::retain_missing_confirmation(&rh,&f.f.scope,&limits(),&selected,&verified,&f.f.proof_signer,&rs).unwrap();
   let selected=service_inspection(&f,&scope,&client,&server,&mut w,&host,&cw,&current);let restored=RestartedPrefix::inspect_recovery(&rh,f.f.scope.clone(),limits(),selected,&f.f.proof_signer,&rs).unwrap().into_recovery_journal();assert_eq!(restored.consumed_requests().unwrap().len(),2);assert_eq!(restored.recovery_subject().unwrap().tails.len(),1);
  }return
 }
 if mode==10{w.fixture_delay(1,2100).unwrap();}client.send(&encode(&request).unwrap()).unwrap();
 let result=w.serve_one(&server,&host,&cw);
 if mode==10{
  assert_eq!(result.unwrap_err().0,"CURRENT_INTERVAL");assert_eq!(w.head().ordinal,1);
  assert!(!f.f.base.join("receipts/sequence-0000000000000001/confirmation.json").exists());
  let original=fs::read(f.f.base.join("witness/prefix-0000000000000001.json")).unwrap();
  client.send(&encode(&request).unwrap()).unwrap();assert!(w.serve_one(&server,&host,&cw).is_err());
  let fresh=service_inspection(&f,&scope,&client,&server,&mut w,&host,&cw,&chosen);
  let fetch=fresh.original_request().unwrap();client.send(&encode(&fetch).unwrap()).unwrap();w.serve_one(&server,&host,&cw).unwrap();assert_eq!(client.receive().unwrap(),original);
  let proof=fresh.verify_original(&original,&f.f.proof_signer,&f.f.scope).unwrap();
  RestartedPrefix::retain_missing_confirmation(&rh,&f.f.scope,&limits(),&fresh,&proof,&f.f.proof_signer,&rs).unwrap();
  assert_eq!(fs::read_dir(f.f.base.join("witness")).unwrap().count(),1);return
 }

 if matches!(mode,1|2|3|6|7|8|9){let error=result.unwrap_err().0;assert_eq!(error,match mode{1=>"PREFIX_FIXED_SERVICE_SELECTION",2=>"PREFIX_CURRENT_WRITER",3=>"PREFIX_WITNESS_CAPACITY",6=>"PREFIX_ISSUER_NOT_CURRENT",7|8|9=>"CURRENT_INTERVAL",_=>unreachable!()});assert_eq!(w.head().ordinal,0);assert_eq!(fs::read_dir(f.f.base.join("witness")).unwrap().count(),0);return;}
 result.unwrap();let original=client.receive().unwrap();let proof=VerifiedPrefix::verify(&original,&f.f.proof_signer,&request,now_seconds().unwrap()).unwrap();j.confirm(p,proof,&rs).unwrap();assert_eq!(w.head().ordinal,1);
 // Exact original retry returns identical bytes; no new witness file/event.
 client.send(&encode(&request).unwrap()).unwrap();w.serve_one(&server,&host,&cw).unwrap();assert_eq!(client.receive().unwrap(),original);assert_eq!(fs::read_dir(f.f.base.join("witness")).unwrap().count(),1);
 if mode==11{
  let time=now_seconds().unwrap();let query=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:f.f.scope.history_key().unwrap(),recipient:f.f.scope.recipient.clone(),channel_binding:server.selection().channel_binding.clone(),challenge:roots::hash(b"short independent inspection"),current_ledger_confirmation:chosen.clone(),current_execution_scope:f.f.scope.execution_scope.clone(),not_before:time,expires_at:time+2};
  w.fixture_delay(2,2100).unwrap();client.send(&encode(&query).unwrap()).unwrap();assert_eq!(w.serve_one(&server,&host,&cw).unwrap_err().0,"CURRENT_INTERVAL");
  let fresh=service_inspection(&f,&scope,&client,&server,&mut w,&host,&cw,&chosen);let fetch=fresh.original_request().unwrap();client.send(&encode(&fetch).unwrap()).unwrap();w.serve_one(&server,&host,&cw).unwrap();assert_eq!(client.receive().unwrap(),original);assert_eq!(w.head().ordinal,1);return
 }
 if mode==5{
  drop(j);let original_scope=encode(&f.f.scope).unwrap();let(new_client,new_server)=pair("new-prefix-admission-channel",&f.f.scope.recipient);
  let mut advanced=current.clone();advanced.writer=WriterFence{instance:"new-writer".into(),epoch:2};
  drop(cw);let newer=ControlWitness::open(&ch,&control_read,&cs,signer("control-confirmation",29).1,role.control_service_binding.clone(),f.f.scope.recipient.clone(),b("control-channel-new",b"control channel new"),current.clone(),advanced.clone(),0,roots::hash(&encode(&current).unwrap()),&[f.f.receipt.identity().clone(),f.f.stage.identity().clone(),f.f.witness.identity().clone()]).unwrap();
  let mut new_role=role.clone();new_role.current_writer=advanced.writer.clone();new_role.channel_binding=new_server.selection().channel_binding.clone();
  let mut new_facts=f.facts.clone();new_facts.current_prefix_binding=HostFixture::save(&f.input,"new-current-prefix-role.json",&encode(&new_role).unwrap());
  let mut sources=f.selection.source_originals.clone();sources.push(new_facts.current_prefix_binding.clone());let(_,_,manager_request)=f.successor(&new_facts,sources);
  host.reselect(&manager_request,&f.selection.profile_recipient,&f.selection.profile_channel_binding).unwrap();
  // A stale actual receiving channel cannot be used with the new role.
  client.send(&encode(&request).unwrap()).unwrap();assert_eq!(w.serve_one(&server,&host,&newer).unwrap_err().0,"PREFIX_FIXED_SERVICE_SELECTION");
  let query=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:f.f.scope.history_key().unwrap(),recipient:f.f.scope.recipient.clone(),channel_binding:new_server.selection().channel_binding.clone(),challenge:roots::hash(b"new writer exact inspection"),current_ledger_confirmation:advanced.clone(),current_execution_scope:f.f.scope.execution_scope.clone(),not_before:now-1,expires_at:now+60};
  new_client.send(&encode(&query).unwrap()).unwrap();w.serve_one(&new_server,&host,&newer).unwrap();let inspection=new_client.receive().unwrap();
  let selected=CurrentPrefix::verify(&inspection,&f.f.proof_signer,&query,&f.f.scope,&scope,now_seconds().unwrap()).unwrap();
  let restored=RestartedPrefix::inspect_recovery(&rh,f.f.scope.clone(),limits(),selected,&f.f.proof_signer,&rs).unwrap();let mut journal=restored.into_recovery_journal();
  let mut v:serde_json::Value=decode(&f.f.frame(1),65536).unwrap();v["request"]["verb"]=json!("close_family");v["request"]["payload"]=json!({"root_id":"receipts","subject_binding":b("accounting",b"fixture exact unknown accounting")});let raw=encode(&v).unwrap();let frame=wire::Frame::decode(&raw).unwrap();
  let mut pending=journal.begin_terminal(&frame,&raw,&f.f.scope.operation.fingerprint,&advanced,&reserve(&journal)).unwrap();
  let response=encode(&authority::sign_receipt(&frame,"terminal","UNKNOWN",Some("FIXTURE_ACCOUNTING"),serde_json::Value::Null,rs.issuer(),&f.f.response_key).unwrap()).unwrap();journal.finish(&mut pending,None,&response,"terminal","UNKNOWN").unwrap();
  let q=journal.confirmation_request(&pending,roots::hash(b"new writer selected receipt"),now,now+60).unwrap();new_client.send(&encode(&q).unwrap()).unwrap();w.serve_one(&new_server,&host,&newer).unwrap();let original_new=new_client.receive().unwrap();let proof=VerifiedPrefix::verify(&original_new,&f.f.proof_signer,&q,now_seconds().unwrap()).unwrap();journal.confirm(pending,proof,&rs).unwrap();
  assert_eq!(w.head().ordinal,2);assert_eq!(original_scope,encode(&f.f.scope).unwrap());assert_eq!(original,fs::read(f.f.base.join("witness/prefix-0000000000000001.json")).unwrap());assert_eq!(current.head,newer.confirmation().head);return;
 }
 // Later effect revocation/expiry does not rewrite or conceal an already
 // durable original under a new independently selected current query.
 let mut expired=f.facts.clone();expired.expires_at=now;expired.activation_expires_at=now;
 expired.revocation_binding=HostFixture::save(&f.input,"prefix-effect-revoked-after-cas.json",&encode(&RevocationOriginal{schema_version:"lab-broker-host-revocation/v1".into(),issuer_enrollment_binding:expired.issuer_enrollment_binding.clone(),native_original_binding:f.selection.source_originals[0].clone(),revoked:true,not_before:now-1,expires_at:now+120}).unwrap());
 let mut sources=f.selection.source_originals.clone();sources.push(expired.revocation_binding.clone());let (_,_,signed)=f.successor(&expired,sources);
 host.reselect(&signed,&f.selection.profile_recipient,&f.selection.profile_channel_binding).unwrap();
 client.send(&encode(&request).unwrap()).unwrap();assert!(w.serve_one(&server,&host,&cw).is_err());assert_eq!(w.head().ordinal,1);
 let inspect=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:f.f.scope.history_key().unwrap(),recipient:f.f.scope.recipient.clone(),channel_binding:server.selection().channel_binding.clone(),challenge:roots::hash(b"fresh exact prefix inspection"),current_ledger_confirmation:chosen,current_execution_scope:f.f.scope.execution_scope.clone(),not_before:now-1,expires_at:now+60};
 client.send(&encode(&inspect).unwrap()).unwrap();w.serve_one(&server,&host,&cw).unwrap();let observed=client.receive().unwrap();let value:PrefixInspection=f.f.proof_signer.verify(&observed).unwrap();assert_eq!(value.head.ordinal,1);
 let fetch=PrefixOriginalRequest{schema_version:"lab-broker-prefix-original-request/v1".into(),query:inspect,original_binding:value.original_confirmation_binding.unwrap()};client.send(&encode(&fetch).unwrap()).unwrap();w.serve_one(&server,&host,&cw).unwrap();assert_eq!(client.receive().unwrap(),original);
}
#[test]fn fixed_prefix_service_cas_inspection_original_and_retry(){service_case(0)}
#[test]fn fixed_prefix_service_receiving_channel_mismatch_refuses(){service_case(1)}
#[test]fn fixed_prefix_service_old_writer_cannot_cas_after_unchanged_head_fence(){service_case(2)}
#[test]fn fixed_prefix_service_insufficient_independent_witness_pool_refuses(){service_case(3)}

#[test]fn fixed_prefix_genesis_inspection_precedes_reserve_without_fabricating_operation(){service_case(4)}

#[test]fn fixed_prefix_new_cas_after_effect_revocation_refuses_without_witness_write(){service_case(6)}

#[test]fn fixed_prefix_current_writer_channel_recovery_keeps_exact_original_scope_and_receipt(){service_case(5)}

#[test]fn fixed_prefix_new_cas_expired_native_revocation_refuses(){service_case(7)}
#[test]fn fixed_prefix_new_cas_expired_activation_refuses(){service_case(8)}
#[test]fn fixed_prefix_new_cas_expired_facts_refuses(){service_case(9)}

fn service_inspection(f:&HostFixture,scope:&Binding,client:&Channel,server:&Channel,w:&mut PrefixWitness<'_>,host:&HostService,control:&ControlWitness<'_>,current:&HostConfirmation)->CurrentPrefix{
 let now=now_seconds().unwrap();let query=PrefixInspectionRequest{schema_version:"lab-broker-prefix-inspection-request/v1".into(),history_key:f.f.scope.history_key().unwrap(),recipient:f.f.scope.recipient.clone(),channel_binding:server.selection().channel_binding.clone(),challenge:challenge().unwrap(),current_ledger_confirmation:current.clone(),current_execution_scope:f.f.scope.execution_scope.clone(),not_before:now,expires_at:now+60};
 client.send(&encode(&query).unwrap()).unwrap();w.serve_one(server,host,control).unwrap();CurrentPrefix::verify(&client.receive().unwrap(),&f.f.proof_signer,&query,&f.f.scope,scope,now_seconds().unwrap()).unwrap()
}
#[test]fn fixed_prefix_expiry_during_persist_retains_cas_and_fresh_original_settlement(){service_case(10)}
#[test]fn fixed_prefix_query_expiry_after_sign_does_not_send_expired_observation(){service_case(11)}

#[test]fn fixed_prefix_original_wins_before_recovery_creation(){service_case(12)}
#[test]fn fixed_prefix_delayed_original_wins_after_recovery_creation(){service_case(13)}
#[test]fn fixed_prefix_recovery_wins_fences_old_cas_and_preserves_consumed_orphan(){service_case(14)}
