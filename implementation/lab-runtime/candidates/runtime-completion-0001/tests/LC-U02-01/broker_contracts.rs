use lab_completion_broker::{*,authority::*};
use ed25519_dalek::SigningKey;
use serde_json::{json,Value};
use base64::Engine;
use std::{os::fd::{OwnedFd,FromRawFd,AsRawFd},time::Duration,mem};

fn fixture_binding(raw:&[u8])->Value {
    json!({"kind":"evidence","root_id":"owned-root","relative_path":format!("records/{}",hash(raw)),
        "sha256":hash(raw),"size_bytes":raw.len()})
}

struct Fixture { key:SigningKey, enrollment:Enrollment, basis:Value, core:Value,
    request:Value, permit:Value, control:ControlSnapshot }
impl Fixture {
    fn new()->Self {
        let key=SigningKey::from_bytes(&[7;32]);
        let ev=json!({"schema_version":"lab-completion-issuer-enrollment/v1","issuer_ref":"fixture-issuer",
            "adapter":"owner-hex-v1","purpose":"broker-intent","algorithm":"ed25519",
            "public_key":hex(&key.verifying_key().to_bytes()),"trust_domain":"fixture"});
        let raw=canonical(&ev).unwrap();let enrollment=Enrollment::select(&raw,&hash(&raw),TrustDomain::Fixture).unwrap();
        let scope=json!({"principal_ref":"fixture-principal","scope_ref":"fixture-scope","operation":"produce",
            "store_id":"fixture-store","instance_id":"fixture-instance","activation_binding":fixture_binding(b"fixture-activation"),
            "slot_epoch":1,"intent_binding":fixture_binding(b"original-intent")});
        let limits=json!({"max_total_bytes":64,"max_actions":64,"max_frame_bytes":65536,"max_chunk_bytes":32768});
        let slots=json!([{"root_id":"owned-root","member":"payload.bin","preimage_binding":null,"max_bytes":64}]);
        let basis=signed_record(&json!({"schema_version":"lab-completion-effect-authority-basis/v1","basis_id":"fixture-basis",
            "scope":scope,"limits":limits,"output_slots":slots,"not_before":1,"expires_at":100}),"fixture-issuer",&key).unwrap();
        let core=json!({"schema_version":"lab-completion-operation-request-core/v1","operation_id":"operation-1",
            "idempotency_key":"idempotency-1","original_request_binding":fixture_binding(b"original-request"),
            "semantic_target_binding":fixture_binding(b"target"),"source_cut_binding":fixture_binding(b"source-cut"),
            "effect_selection_binding":fixture_binding(b"effect-selection"),"authority_basis_binding":content_digest(&canonical(&basis).unwrap()),
            "scope":scope,"limits":limits,"output_slots":slots,"operation_expires_at":90});
        let request=json!({"schema_version":"lab-completion-broker-request/v1","request_id":"request-1",
            "operation_id":"operation-1","sequence":0,"activation_binding":scope["activation_binding"],
            "store_id":"fixture-store","instance_id":"fixture-instance","slot_epoch":1,"principal_ref":"fixture-principal",
            "verb":"write_member","intent_binding":scope["intent_binding"],"authorization_binding":content_digest(b""),
            "payload":{"root_id":"owned-root","member":"payload.bin","preimage_binding":null,
                "full_sha256":hash(b"abc"),"full_length":3,"offset":0,"length":3,"chunk_sha256":hash(b"abc"),
                "bytes_base64":"YWJj"}});
        let grant=json!({"kind":"member","root_id":"owned-root","stage_binding":fixture_binding(b"owned-stage"),"member":"payload.bin","preimage_binding":null,
            "full_sha256":hash(b"abc"),"full_length":3,"chunk_size":3,"sequence_start":0,
            "chunks":[{"sequence":0,"offset":0,"length":3,"core_sha256":hash(&signing_bytes(&authorization_core(&request).unwrap()).unwrap())}]});
        let permit=signed_record(&json!({"schema_version":"lab-completion-broker-permit/v1","permit_id":"permit-1",
            "operation_fingerprint":operation_fingerprint(&core).unwrap(),"basis_binding":core["authority_basis_binding"],
            "scope":scope,"limits":limits,"allowed_verb":"write_member","allowed_phase":"staging",
            "not_before":1,"expires_at":80,"grant":grant}),"fixture-issuer",&key).unwrap();
        let peer=Peer{pid:unsafe{libc::getpid()},uid:unsafe{libc::getuid()},gid:unsafe{libc::getgid()}};
        let control=ControlSnapshot{domain:TrustDomain::Fixture,caller:peer,now:10,activation_expires_at:95,
            operation_id:"operation-1".into(),live_scope:scope.clone(),selected_roots:vec!["owned-root".into()],
            issuer_currentness:IssuerCurrentness{enrollment_digest:enrollment.binding.clone(),
                revocation_binding:fixture_binding(b"current-revocation"),revoked:false,checked_at:10},
            disclosure_subjects:vec![],recovery:None,recorded_request:None,
            operation_fingerprint:operation_fingerprint(&core).unwrap(),stage_binding:fixture_binding(b"owned-stage"),
            member_binding:Some(member_identity_binding(&grant).unwrap()),
            original_deadline:90,phase:"staging".into(),next_sequence:0,next_offset:0,cumulative_bytes:0,
            cumulative_actions:0,acknowledgment_uncertain:false,replay:None};
        Self{key,enrollment,basis,core,request,permit,control}
    }
    fn wire(&self)->Vec<u8> {
        let mut r=self.request.clone();r["authorization_binding"]=content_digest(&canonical(&self.permit).unwrap());
        canonical(&json!({"schema_version":"lab-completion-broker-frame/v1","request":r,"permit":self.permit})).unwrap()
    }
    fn frame(&self)->Frame {Frame::decode(&self.wire()).unwrap()}
    fn verify(&self)->Result<VerifiedDispatch> {verify(&self.frame(),self.control.caller,&self.enrollment,&self.basis,&self.core,&self.control)}
    fn resign(&mut self) {self.permit=signed_record(&self.permit["payload"],"fixture-issuer",&self.key).unwrap();}
    fn bind_message(&mut self) {
        self.permit["payload"]["grant"]["chunks"][0]["core_sha256"]=json!(hash(&signing_bytes(&authorization_core(&self.request).unwrap()).unwrap()));
        self.resign();
    }
}

#[test] fn valid_exact_member_decision_and_signed_receipt() {
    let f=Fixture::new();let decision=f.verify().unwrap();
    assert_eq!(decision.decision(),&Decision::Fresh{member_bytes:3});
    assert_eq!(decision.trust_domain(),TrustDomain::Fixture);
    let receipt=sign_receipt(&f.frame(),"staging","PASS",None,fixture_binding(b"fixture-result"),"fixture-issuer",&f.key).unwrap();
    let payload=f.enrollment.verify_record(&receipt,"lab-completion-broker-response/v1").unwrap();
    assert_eq!(payload["request_digest"],hash(&f.wire()));
    verify_receipt(&canonical(&receipt).unwrap(),&f.enrollment,&hash(&f.wire()),"operation-1",0).unwrap();
    assert!(verify_receipt(&canonical(&receipt).unwrap(),&f.enrollment,&hash(&f.wire()),"operation-1",1).is_err());
    let mut changed=payload.clone();changed["extra"]=json!(true);
    let signed=signed_record(&changed,"fixture-issuer",&f.key).unwrap();
    assert!(verify_receipt(&canonical(&signed).unwrap(),&f.enrollment,&hash(&f.wire()),"operation-1",0).is_err());
    assert!(sign_receipt(&f.frame(),"staging","FAIL",Some("private/path"),Value::Null,"fixture-issuer",&f.key).is_err());
}

#[test] fn canonical_numbers_duplicates_unicode_and_depth() {
    for raw in [b"{\"a\":1,\"a\":2}".as_slice(),b"-0",b"1.0",b"1e0",b"NaN",b"9223372036854775808",b"\"\\ud800\"",b"\xff"] {
        assert!(parse(raw,MAX_FRAME).is_err(),"{raw:?}");
    }
    assert_eq!(canonical(&parse("{\"é\":\"é\",\"z\":-9223372036854775808}".as_bytes(),MAX_FRAME).unwrap()).unwrap(),
               "{\"z\":-9223372036854775808,\"é\":\"é\"}".as_bytes());
    let deep=format!("{}0{}","[".repeat(65),"]".repeat(65));assert!(parse(deep.as_bytes(),MAX_FRAME).is_err());
    assert!(parse(&vec![b' ';MAX_FRAME+1],MAX_FRAME).is_err());
}

#[test] fn full_source_binding_never_collapses_to_content_digest() {
    let mut f=Fixture::new();f.request["activation_binding"]=content_digest(b"fixture-activation");
    assert!(Frame::decode(&f.wire()).is_err());
    let f=Fixture::new();let mut changed=f.core.clone();
    changed["original_request_binding"]["root_id"]=json!("other-root");
    assert_ne!(operation_fingerprint(&changed).unwrap(),operation_fingerprint(&f.core).unwrap());
    changed=f.core.clone();changed["original_request_binding"]["relative_path"]=json!("other/path");
    assert_ne!(operation_fingerprint(&changed).unwrap(),operation_fingerprint(&f.core).unwrap());
    assert!(validate_content_digest(&fixture_binding(b"same")).is_err());
}

#[test] fn valid_resigned_scope_cannot_replace_live_control_selection() {
    for (key,value) in [("principal_ref",json!("new-principal")),("slot_epoch",json!(2)),
        ("store_id",json!("other-store")),("instance_id",json!("other-instance")),
        ("activation_binding",fixture_binding(b"other-activation"))] {
        let mut f=Fixture::new();f.core["scope"][key]=value.clone();
        f.basis["payload"]["scope"]=f.core["scope"].clone();
        f.basis=signed_record(&f.basis["payload"],"fixture-issuer",&f.key).unwrap();
        f.core["authority_basis_binding"]=content_digest(&canonical(&f.basis).unwrap());
        f.permit["payload"]["scope"]=f.core["scope"].clone();
        f.permit["payload"]["basis_binding"]=f.core["authority_basis_binding"].clone();
        f.permit["payload"]["operation_fingerprint"]=json!(operation_fingerprint(&f.core).unwrap());
        f.request[key]=value;f.bind_message();
        assert_eq!(f.verify().unwrap_err(),Refusal("LIVE_REQUEST_SCOPE"));
    }
    let mut f=Fixture::new();f.control.operation_fingerprint="00".repeat(32);
    assert_eq!(f.verify().unwrap_err(),Refusal("IMMUTABLE_OPERATION_SELECTION"));
    let mut f=Fixture::new();f.control.selected_roots=vec!["foreign-root".into()];
    assert_eq!(f.verify().unwrap_err(),Refusal("LIVE_ROOT"));
}

#[test] fn renewed_member_cannot_replace_stored_bytes_at_next_offset() {
    let mut f=Fixture::new();
    f.permit["payload"]["grant"]["full_length"]=json!(6);
    f.permit["payload"]["grant"]["full_sha256"]=json!(hash(b"abcdef"));
    f.control.member_binding=Some(member_identity_binding(&f.permit["payload"]["grant"]).unwrap());
    f.control.next_sequence=1;f.control.next_offset=3;f.control.cumulative_bytes=3;f.control.cumulative_actions=1;
    f.request["sequence"]=json!(1);f.request["payload"]["offset"]=json!(3);
    f.request["payload"]["full_length"]=json!(6);f.request["payload"]["full_sha256"]=json!(hash(b"xyzabc"));
    f.permit["payload"]["grant"]["full_sha256"]=f.request["payload"]["full_sha256"].clone();
    f.permit["payload"]["grant"]["sequence_start"]=json!(1);
    f.permit["payload"]["grant"]["chunks"][0]["sequence"]=json!(1);
    f.permit["payload"]["grant"]["chunks"][0]["offset"]=json!(3);
    f.bind_message();
    assert_eq!(f.verify().unwrap_err(),Refusal("IMMUTABLE_MEMBER_SELECTION"));
    let mut f=Fixture::new();f.permit["payload"]["grant"]["stage_binding"]=fixture_binding(b"different-stage");f.resign();
    assert_eq!(f.verify().unwrap_err(),Refusal("STAGE_SELECTION"));
    let mut f=Fixture::new();f.request["payload"]["full_length"]=json!(4);
    f.permit["payload"]["grant"]["full_length"]=json!(4);f.bind_message();
    assert_eq!(f.verify().unwrap_err(),Refusal("IMMUTABLE_MEMBER_SELECTION"));
}

#[test] fn current_issuer_revocation_and_invalid_kernel_id_refuse() {
    let mut f=Fixture::new();f.control.issuer_currentness.revoked=true;
    assert_eq!(f.verify().unwrap_err(),Refusal("ISSUER_NOT_CURRENT"));
    let mut f=Fixture::new();f.control.issuer_currentness.checked_at=9;
    assert_eq!(f.verify().unwrap_err(),Refusal("ISSUER_NOT_CURRENT"));
    let mut f=Fixture::new();f.control.issuer_currentness.enrollment_digest=content_digest(b"other");
    assert_eq!(f.verify().unwrap_err(),Refusal("ISSUER_NOT_CURRENT"));
    let mut f=Fixture::new();f.control.caller.uid=u32::MAX;
    assert_eq!(f.verify().unwrap_err(),Refusal("CALLER_ID_RANGE"));
    f.control.caller.uid=1;f.control.caller.gid=u32::MAX;
    assert_eq!(f.verify().unwrap_err(),Refusal("CALLER_ID_RANGE"));
}

fn current_permit(f:&mut Fixture,verb:&str,recovery:bool) {
    let original=f.frame();let subject=fixture_binding(b"durable-original");
    f.control.replay=Some(ReplayRecord{sequence:0,wire_digest:original.wire_digest().into(),receipt_binding:subject.clone()});
    f.control.now=120;f.control.activation_expires_at=200;f.control.issuer_currentness.checked_at=120;
    f.control.phase="terminal".into();f.control.cumulative_actions=64;f.control.cumulative_bytes=64;
    f.control.next_sequence=1;f.control.next_offset=3;
    f.control.disclosure_subjects=vec![subject.clone()];
    f.request["request_id"]=json!("new-current-inspection");f.request["sequence"]=json!(if recovery {1} else {0});f.request["verb"]=json!(verb);
    f.request["payload"]=json!({"root_id":"owned-root","subject_binding":subject});
    let mut payload=json!({"schema_version":"lab-completion-broker-disclosure-permit/v1","authorization_id":"fresh-disclosure",
        "operation_id":"operation-1","operation_fingerprint":f.control.operation_fingerprint,
        "scope":f.control.live_scope,"allowed_verb":verb,
        "message_core_sha256":hash(&signing_bytes(&authorization_core(&f.request).unwrap()).unwrap()),
        "subject_binding":subject,"not_before":110,"expires_at":150,"max_output_bytes":4096});
    if recovery {
        f.control.phase="UNKNOWN".into();
        payload.as_object_mut().unwrap().remove("max_output_bytes");
        payload["schema_version"]=json!("lab-completion-recovery-authorization/v1");
        payload["observed_phase"]=json!("UNKNOWN");payload["action"]=json!(if verb=="close_family" {"close_family"} else {"seal_outcome"});
        payload["preimages"]=json!([subject]);payload["next_sequence"]=json!(1);payload["next_offset"]=json!(3);
        payload["cumulative_bytes"]=json!(64);payload["cumulative_actions"]=json!(64);payload["original_deadline"]=json!(90);
    }
    f.permit=signed_record(&payload,"fixture-issuer",&f.key).unwrap();
    if recovery {f.control.recovery=Some(RecoverySelection{authorization_digest:content_digest(&canonical(&f.permit).unwrap()),
        subject_binding:subject.clone(),preimages:vec![subject],action:payload["action"].as_str().unwrap().into(),consumed:false});}
}

#[test] fn expired_effect_and_advanced_phase_allow_only_fresh_disclosure() {
    for verb in ["inspect","inspect_operation","read_receipt"] {
        let mut f=Fixture::new();current_permit(&mut f,verb,false);
        assert!(matches!(f.verify().unwrap().decision(),Decision::Disclosure{..}));
        // The old basis is intentionally unavailable: current disclosure never
        // dereferences or revives old effect/source authority.
        f.basis=Value::Null;f.core=Value::Null;
        assert!(matches!(f.verify().unwrap().decision(),Decision::Disclosure{..}));
        let original_fingerprint=f.control.operation_fingerprint.clone();
        f.control.live_scope["activation_binding"]=fixture_binding(b"current-disclosure-activation");
        f.control.live_scope["intent_binding"]=fixture_binding(b"current-disclosure-intent");
        f.request["activation_binding"]=f.control.live_scope["activation_binding"].clone();
        f.request["intent_binding"]=f.control.live_scope["intent_binding"].clone();
        f.permit["payload"]["scope"]=f.control.live_scope.clone();
        f.permit["payload"]["message_core_sha256"]=json!(hash(&signing_bytes(&authorization_core(&f.request).unwrap()).unwrap()));
        f.resign();
        let checked=f.verify().unwrap();
        assert!(matches!(checked.decision(),Decision::Disclosure{..}));
        assert_eq!(checked.operation_fingerprint(),original_fingerprint);
        f.request["request_id"]=json!("changed-query");assert_eq!(f.verify().unwrap_err(),Refusal("CURRENT_MESSAGE_BINDING"));
    }
    let mut f=Fixture::new();f.control.now=120;f.control.activation_expires_at=200;
    f.control.issuer_currentness.checked_at=120;f.control.phase="terminal".into();
    assert!(f.verify().is_err()); // expired effect is not implicit disclosure
    let mut f=Fixture::new();current_permit(&mut f,"read_receipt",false);
    f.control.acknowledgment_uncertain=true;
    assert_eq!(f.verify().unwrap_err(),Refusal("RECONCILIATION_REQUIRED"));
    let mut f=Fixture::new();current_permit(&mut f,"read_receipt",false);
    f.request["sequence"]=json!(1);
    f.permit["payload"]["message_core_sha256"]=json!(hash(&signing_bytes(&authorization_core(&f.request).unwrap()).unwrap()));f.resign();
    assert_eq!(f.verify().unwrap_err(),Refusal("RECEIPT_SEQUENCE"));
    let mut f=Fixture::new();current_permit(&mut f,"inspect",false);
    f.control.phase="UNKNOWN".into();f.control.acknowledgment_uncertain=true;
    f.control.next_sequence=i64::MAX;f.control.cumulative_actions=i64::MAX;f.control.cumulative_bytes=i64::MAX;
    assert!(matches!(f.verify().unwrap().decision(),Decision::Disclosure{..}));
}

#[test] fn recovery_is_one_selected_action_and_cannot_reset_old_counters() {
    for verb in ["reconcile_operation","close_family"] {
        let mut f=Fixture::new();current_permit(&mut f,verb,true);
        assert!(matches!(f.verify().unwrap().decision(),Decision::Recovery{..}));
        f.control.phase="terminal".into();
        f.permit["payload"]["observed_phase"]=json!("terminal");f.resign();
        f.control.recovery.as_mut().unwrap().authorization_digest=content_digest(&canonical(&f.permit).unwrap());
        assert_eq!(f.verify().unwrap_err(),Refusal("RECOVERY_STATE"));
        f.control.phase="UNKNOWN".into();
        f.permit["payload"]["observed_phase"]=json!("UNKNOWN");f.resign();
        f.control.recovery.as_mut().unwrap().authorization_digest=content_digest(&canonical(&f.permit).unwrap());
        f.control.recovery.as_mut().unwrap().consumed=true;
        assert_eq!(f.verify().unwrap_err(),Refusal("RECOVERY_CONSUMED_OR_CHANGED"));
        f.control.recovery.as_mut().unwrap().consumed=false;
        f.control.next_offset=0;assert_eq!(f.verify().unwrap_err(),Refusal("RECOVERY_COUNTER_RESET"));
    }
    let mut f=Fixture::new();f.request["sequence"]=json!(1);
    f.permit["payload"]["grant"]["sequence_start"]=json!(1);
    f.permit["payload"]["grant"]["chunks"][0]["sequence"]=json!(1);f.bind_message();
    let old=f.frame();current_permit(&mut f,"reconcile_operation",true);
    f.control.recorded_request=Some(RecordedRequest{sequence:1,wire_digest:old.wire_digest().into()});
    assert_eq!(f.verify().unwrap_err(),Refusal("IDEMPOTENCY_CONFLICT"));
    f.control.recorded_request=Some(RecordedRequest{sequence:1,wire_digest:f.frame().wire_digest().into()});
    assert_eq!(f.verify().unwrap_err(),Refusal("RECOVERY_ALREADY_RECORDED"));
}

#[test] fn remaining_closed_verbs_require_legal_current_phase() {
    for (verb,phase) in [("create_stage","reserved"),("seal_stage","staging"),
        ("commit_generation","sealed"),("commit_generation","generation-published"),
        ("commit_generation","pointer-committed"),("repair_derived","pointer-committed")] {
        let mut f=Fixture::new();f.request["verb"]=json!(verb);f.control.phase=phase.into();
        let reservation=verb=="create_stage";
        f.request["payload"]=if reservation {json!({"root_id":"owned-root","stage_name":"new-stage","max_bytes":64})}
            else {json!({"root_id":"owned-root","subject_binding":fixture_binding(b"selected-control-subject")})};
        if reservation {f.control.stage_binding=Value::Null;}
        f.permit["payload"]["allowed_verb"]=json!(verb);f.permit["payload"]["allowed_phase"]=json!(phase);
        f.permit["payload"]["grant"]=json!({"kind":if reservation {"empty-stage"} else {"control"},
            "root_id":"owned-root","stage_binding":f.control.stage_binding,"member":null,"preimage_binding":null,
            "full_sha256":null,"full_length":0,"chunk_size":0,"sequence_start":0,
            "chunks":[{"sequence":0,"offset":0,"length":0,"core_sha256":"00".repeat(32)}]});
        f.bind_message();assert_eq!(f.verify().unwrap().decision(),&Decision::Fresh{member_bytes:0});
        f.control.phase="terminal".into();assert!(f.verify().is_err());
        f.request["payload"]["arbitrary_path"]=json!("foreign");assert!(Frame::decode(&f.wire()).is_err());
    }
}

#[test] fn unselected_fields_versions_algorithms_and_scope_refuse() {
    let f=Fixture::new();let mut v=parse(&f.wire(),MAX_FRAME).unwrap();
    v["request"]["python_import"]=json!("arbitrary.code");assert!(Frame::decode(&canonical(&v).unwrap()).is_err());
    for (key,value) in [("principal_ref",json!("wrong")),("slot_epoch",json!(2)),("store_id",json!("other")),("instance_id",json!("other"))] {
        let mut f=Fixture::new();f.request[key]=value;assert!(f.verify().is_err());
    }
    let mut f=Fixture::new();f.request["verb"]=json!("exec");assert!(Frame::decode(&f.wire()).is_err());
    let mut f=Fixture::new();f.permit["issuer_ref"]=json!("other");assert!(f.verify().is_err());
    let mut f=Fixture::new();f.permit["signature"]=json!("00".repeat(64));assert!(f.verify().is_err());
    let mut f=Fixture::new();f.permit["payload"]["schema_version"]=json!("unknown/v2");f.resign();assert!(f.verify().is_err());
}

#[test] fn caller_kernel_mapping_independent_of_intent() {
    let f=Fixture::new();let mut peer=f.control.caller;peer.uid=peer.uid.wrapping_add(1);
    assert!(verify(&f.frame(),peer,&f.enrollment,&f.basis,&f.core,&f.control).is_err());
    peer=f.control.caller;peer.pid+=1;
    assert!(verify(&f.frame(),peer,&f.enrollment,&f.basis,&f.core,&f.control).is_err());
}

#[test] fn phase_period_revocation_and_cumulative_bounds() {
    for now in [0,80,90,100] {let mut f=Fixture::new();f.control.now=now;assert!(f.verify().is_err());}
    let mut f=Fixture::new();f.control.phase="sealed".into();assert!(f.verify().is_err());
    let mut f=Fixture::new();f.control.activation_expires_at=9;assert!(f.verify().is_err());
    let mut f=Fixture::new();f.control.cumulative_bytes=62;assert!(f.verify().is_err());
    let mut f=Fixture::new();f.control.cumulative_actions=64;assert!(f.verify().is_err());
    let mut f=Fixture::new();f.control.original_deadline=101;assert!(f.verify().is_err());
}

#[test] fn changed_preimage_root_content_and_chunk_bytes_refuse() {
    for (key,v) in [("root_id",json!("foreign")),("member",json!("../escape")),("preimage_binding",fixture_binding(b"wrong")),
                    ("full_sha256",json!("00".repeat(32))),("full_length",json!(4)),("offset",json!(1)),("bytes_base64",json!("eHl6"))] {
        let mut f=Fixture::new();f.request["payload"][key]=v;
        match Frame::decode(&f.wire()) {Err(_)=>(),Ok(frame)=>assert!(verify(&frame,f.control.caller,&f.enrollment,&f.basis,&f.core,&f.control).is_err())}
    }
}

#[test] fn exact_duplicate_but_renewed_frame_conflicts() {
    let mut f=Fixture::new();let original=f.frame();
    f.control.replay=Some(ReplayRecord{sequence:0,wire_digest:original.wire_digest().into(),receipt_binding:fixture_binding(b"durable-original")});
    f.control.recorded_request=Some(RecordedRequest{sequence:0,wire_digest:original.wire_digest().into()});
    assert_eq!(f.verify().unwrap_err(),Refusal("RECEIPT_DISCLOSURE_REQUIRED"));
    let fingerprint=operation_fingerprint(&f.core).unwrap();
    f.permit["payload"]["permit_id"]=json!("renewal");f.permit["payload"]["expires_at"]=json!(85);f.resign();
    assert_eq!(f.verify().unwrap_err(),Refusal("IDEMPOTENCY_CONFLICT"));
    assert_eq!(operation_fingerprint(&f.core).unwrap(),fingerprint);
}

#[test] fn unknown_ack_and_offset_sequence_reset_refuse() {
    let mut f=Fixture::new();f.control.acknowledgment_uncertain=true;assert!(f.verify().is_err());
    let mut f=Fixture::new();f.control.next_sequence=1;assert!(f.verify().is_err());
    let mut f=Fixture::new();f.control.next_offset=3;assert!(f.verify().is_err());
    let mut f=Fixture::new();f.permit["payload"]["expires_at"]=json!(91);f.resign();assert!(f.verify().is_err());
}

#[test] fn fingerprint_excludes_new_permits_but_includes_material_intent() {
    let f=Fixture::new();let before=operation_fingerprint(&f.core).unwrap();
    let mut changed=f.core.clone();changed["original_request_binding"]=fixture_binding(b"new-request");
    assert_ne!(operation_fingerprint(&changed).unwrap(),before);
    changed=f.core.clone();changed["current_permit"]=f.permit.clone();assert!(operation_fingerprint(&changed).is_err());
    let mut other=f.request.clone();other["authorization_binding"]=content_digest(b"renewed");
    assert_eq!(authorization_core(&other).unwrap(),authorization_core(&f.request).unwrap());
    other["sequence"]=json!(1);assert_ne!(authorization_core(&other).unwrap(),authorization_core(&f.request).unwrap());
}

#[test] fn reservation_has_no_member_payload_and_exact_empty_grant() {
    let mut f=Fixture::new();f.control.phase="absent".into();f.request["verb"]=json!("reserve_family");
    f.request["payload"]=json!({"root_id":"owned-root","stage_name":"stage-1","max_bytes":64});
    let p=&mut f.permit["payload"];p["allowed_verb"]=json!("reserve_family");p["allowed_phase"]=json!("absent");
    p["grant"]=json!({"kind":"empty-stage","root_id":"owned-root","stage_binding":null,"member":null,"preimage_binding":null,
        "full_sha256":null,"full_length":0,"chunk_size":0,"sequence_start":0,
        "chunks":[{"sequence":0,"offset":0,"length":0,"core_sha256":"00".repeat(32)}]});
    f.control.stage_binding=Value::Null;f.control.member_binding=None;
    f.bind_message();assert_eq!(f.verify().unwrap().decision(),&Decision::Fresh{member_bytes:0});
    f.request["payload"]["bytes_base64"]=json!("YQ==");assert!(Frame::decode(&f.wire()).is_err());
}

#[test] fn bounded_batch_authorizes_exact_chunks_without_fingerprint_change() {
    let mut f=Fixture::new();let original=operation_fingerprint(&f.core).unwrap();let data:Vec<u8>=(0..32).collect();
    let mut requests=Vec::new();let mut rows=Vec::new();
    for i in 0..32 {
        let mut r=f.request.clone();r["sequence"]=json!(i);r["request_id"]=json!(format!("chunk-{i}"));
        r["payload"]["full_length"]=json!(32);r["payload"]["full_sha256"]=json!(hash(&data));
        r["payload"]["offset"]=json!(i);r["payload"]["length"]=json!(1);
        r["payload"]["chunk_sha256"]=json!(hash(&data[i..i+1]));
        r["payload"]["bytes_base64"]=json!(base64::engine::general_purpose::STANDARD.encode(&data[i..i+1]));
        rows.push(json!({"sequence":i,"offset":i,"length":1,"core_sha256":hash(&signing_bytes(&authorization_core(&r).unwrap()).unwrap())}));requests.push(r);
    }
    f.permit["payload"]["grant"]["full_length"]=json!(32);f.permit["payload"]["grant"]["full_sha256"]=json!(hash(&data));
    f.permit["payload"]["grant"]["chunk_size"]=json!(1);f.permit["payload"]["grant"]["chunks"]=json!(rows);f.resign();
    f.control.member_binding=Some(member_identity_binding(&f.permit["payload"]["grant"]).unwrap());
    for (i,r) in requests.into_iter().enumerate() {
        f.request=r;f.control.next_sequence=i as i64;f.control.next_offset=i as i64;f.control.cumulative_bytes=i as i64;f.control.cumulative_actions=i as i64;
        assert_eq!(f.verify().unwrap().decision(),&Decision::Fresh{member_bytes:1});
    }
    assert_eq!(operation_fingerprint(&f.core).unwrap(),original);
    f.permit["payload"]["grant"]["chunks"].as_array_mut().unwrap().push(json!({"sequence":32,"offset":32,"length":1,"core_sha256":"00".repeat(32)}));f.resign();
    assert_eq!(f.verify().unwrap_err(),Refusal("BATCH_LIMIT"));
}

#[test] fn fixture_cannot_select_actual_and_custody_cannot_mint_permit() {
    let f=Fixture::new();let mut actual=f.control.clone();actual.domain=TrustDomain::Actual;
    assert!(verify(&f.frame(),actual.caller,&f.enrollment,&f.basis,&f.core,&actual).is_err());
    let enrollment=json!({"schema_version":"lab-completion-issuer-enrollment/v1","issuer_ref":"fixture-custody",
        "adapter":"custody-challenge-base64-v1","purpose":"transport-authentication","algorithm":"ed25519",
        "public_key":base64::engine::general_purpose::STANDARD.encode(f.key.verifying_key().to_bytes()),"trust_domain":"fixture"});
    let bytes=canonical(&enrollment).unwrap();let selected=Enrollment::select(&bytes,&hash(&bytes),TrustDomain::Fixture).unwrap();
    assert!(selected.verify_record(&f.permit,"lab-completion-broker-permit/v1").is_err());
    assert!(Enrollment::select(&bytes,&hash(&bytes),TrustDomain::Actual).is_err());
    assert!(Enrollment::select(&bytes,&"00".repeat(32),TrustDomain::Fixture).is_err());
    use ed25519_dalek::Signer;
    let challenge=json!({"schema_version":"lab-context-host-challenge/v1-candidate","host_instance_ref":"fixture-host",
        "connection_ref":"fixture-connection","nonce":"01".repeat(32),"policy_sha256":"02".repeat(32),
        "expires_at":"2026-10-18T12:00:00Z","authority_effect":"none"});
    let proof=json!({"challenge":challenge,"signature":base64::engine::general_purpose::STANDARD.encode(f.key.sign(&canonical(&challenge).unwrap()).to_bytes())});
    selected.verify_custody_challenge(&proof,&challenge).unwrap();
    assert!(f.enrollment.verify_custody_challenge(&proof,&challenge).is_err());
    let mut wrong=challenge.clone();wrong["connection_ref"]=json!("other");
    assert!(selected.verify_custody_challenge(&proof,&wrong).is_err());
}

fn pair(kind:i32)->(OwnedFd,OwnedFd) {
    let mut fds=[-1;2];assert_eq!(unsafe{libc::socketpair(libc::AF_UNIX,kind|libc::SOCK_CLOEXEC,0,fds.as_mut_ptr())},0);
    unsafe{(OwnedFd::from_raw_fd(fds[0]),OwnedFd::from_raw_fd(fds[1]))}
}
fn send(fd:&OwnedFd,data:&[u8]) {assert_eq!(unsafe{libc::send(fd.as_raw_fd(),data.as_ptr().cast(),data.len(),libc::MSG_NOSIGNAL)},data.len() as isize);}
fn fd_count()->usize {std::fs::read_dir("/proc/self/fd").unwrap().count()}
fn send_rights(fd:&OwnedFd,rights:&[i32]) {
    let data=b"{}";let mut io=libc::iovec{iov_base:data.as_ptr() as *mut _,iov_len:data.len()};
    let mut buf=[0usize;64];let mut msg:libc::msghdr=unsafe{mem::zeroed()};
    msg.msg_iov=&mut io;msg.msg_iovlen=1;msg.msg_control=buf.as_mut_ptr().cast();
    msg.msg_controllen=unsafe{libc::CMSG_SPACE(mem::size_of_val(rights) as u32)} as usize;
    unsafe {let h=libc::CMSG_FIRSTHDR(&msg);(*h).cmsg_level=libc::SOL_SOCKET;(*h).cmsg_type=libc::SCM_RIGHTS;
        (*h).cmsg_len=libc::CMSG_LEN(mem::size_of_val(rights) as u32) as usize;
        std::ptr::copy_nonoverlapping(rights.as_ptr().cast::<u8>(),libc::CMSG_DATA(h),mem::size_of_val(rights));
        assert_eq!(libc::sendmsg(fd.as_raw_fd(),&msg,libc::MSG_NOSIGNAL),2);}
}

#[test] fn real_seqpacket_credentials_are_per_message() {
    let (a,b)=pair(libc::SOCK_SEQPACKET);let receiver=Receiver::new(b,MAX_FRAME,MAX_CONTROL).unwrap();
    send(&a,b"first");let first=receiver.receive(Duration::from_secs(1)).unwrap();
    assert_eq!(first.peer.pid,unsafe{libc::getpid()});
    let child=unsafe{libc::fork()};assert!(child>=0);
    if child==0 {unsafe{libc::send(a.as_raw_fd(),b"child".as_ptr().cast(),5,libc::MSG_NOSIGNAL);libc::_exit(0);}}
    let second=receiver.receive(Duration::from_secs(1)).unwrap();let mut status=0;assert_eq!(unsafe{libc::waitpid(child,&mut status,0)},child);
    assert_eq!(second.peer.pid,child);assert_ne!(first.peer.pid,second.peer.pid);
    assert_eq!(second.peer.uid,unsafe{libc::getuid()});assert_eq!(second.bytes,b"child");
}

#[test] fn rights_and_truncated_rights_close_every_delivered_descriptor() {
    for limit in [MAX_CONTROL,64] {
        let (a,b)=pair(libc::SOCK_SEQPACKET);let receiver=Receiver::new(b,MAX_FRAME,limit).unwrap();
        let (r,w)=pair(libc::SOCK_SEQPACKET);let before=fd_count();
        send_rights(&a,&vec![r.as_raw_fd();16]);
        assert!(receiver.receive(Duration::from_secs(1)).is_err());
        assert_eq!(fd_count(),before,"received rights leaked at control limit {limit}");
        send(&r,b"still-owned");let mut data=[0u8;16];assert_eq!(unsafe{libc::recv(w.as_raw_fd(),data.as_mut_ptr().cast(),16,0)},11);
    }
}

#[test] fn packet_and_control_truncation_and_stream_refuse() {
    let (a,b)=pair(libc::SOCK_SEQPACKET);let receiver=Receiver::new(b,32,MAX_CONTROL).unwrap();
    send(&a,&[b'a';33]);assert_eq!(receiver.receive(Duration::from_secs(1)).unwrap_err(),Refusal("PACKET_TRUNCATED"));
    let (a,b)=pair(libc::SOCK_SEQPACKET);let receiver=Receiver::new(b,MAX_FRAME,1).unwrap();
    send(&a,b"data");assert_eq!(receiver.receive(Duration::from_secs(1)).unwrap_err(),Refusal("PACKET_TRUNCATED"));
    let (_a,b)=pair(libc::SOCK_STREAM);assert!(Receiver::new(b,MAX_FRAME,MAX_CONTROL).is_err());
    let (_a,b)=pair(libc::SOCK_DGRAM);assert!(Receiver::new(b,MAX_FRAME,MAX_CONTROL).is_err());
}

#[test] fn actual_socket_message_without_credentials_refuses() {
    let (a,b)=pair(libc::SOCK_SEQPACKET);
    let fd=unsafe{libc::fcntl(b.as_raw_fd(),libc::F_DUPFD_CLOEXEC,0)};assert!(fd>=0);
    let duplicate=unsafe{OwnedFd::from_raw_fd(fd)};
    let receiver=Receiver::new(b,MAX_FRAME,MAX_CONTROL).unwrap();
    let disabled:libc::c_int=0;
    assert_eq!(unsafe{libc::setsockopt(duplicate.as_raw_fd(),libc::SOL_SOCKET,libc::SO_PASSCRED,
        (&disabled as *const libc::c_int).cast(),mem::size_of_val(&disabled) as libc::socklen_t)},0);
    send(&a,b"missing-credential");
    assert_eq!(receiver.receive(Duration::from_secs(1)).unwrap_err(),Refusal("CREDENTIALS_REQUIRED"));
}

#[test] fn receive_timeout_and_empty_packet_refuse() {
    let (a,b)=pair(libc::SOCK_SEQPACKET);let receiver=Receiver::new(b,MAX_FRAME,MAX_CONTROL).unwrap();
    let start=std::time::Instant::now();assert_eq!(receiver.receive(Duration::from_millis(25)).unwrap_err(),Refusal("RECEIVE_TIMEOUT"));
    assert!(start.elapsed()<Duration::from_secs(1));
    send(&a,b"");assert!(receiver.receive(Duration::from_secs(1)).is_err());
}
