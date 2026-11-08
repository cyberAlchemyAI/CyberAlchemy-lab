// Exact fixture basis adapted from accepted LC-U02-01; no actual issuer.
use lab_completion_broker::{*,authority::*};
use ed25519_dalek::SigningKey;
use serde_json::{json,Value};
use std::time::Duration;

fn fixture_binding(raw:&[u8])->Value {
    json!({"kind":"evidence","root_id":"owned-root","relative_path":format!("records/{}",hash(raw)),
        "sha256":hash(raw),"size_bytes":raw.len()})
}

struct SignedFixture { key:SigningKey, enrollment:Enrollment, basis:Value, core:Value,
    request:Value, permit:Value, control:ControlSnapshot }
impl SignedFixture {
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

#[test] fn verified_original_frame_stage_subject_is_enforced_by_actual_io(){
 let mut signed=SignedFixture::new();let scope=scope_of(&signed);let f=crate::custody_tests::Fixture::with_scope(Some(scope));let hold=f.root.exclusive(Duration::from_millis(50)).unwrap();
 let mut create=crate::custody_tests::create_for(&f);create.fingerprint=signed.control.operation_fingerprint.clone();
 let mut stage=crate::members::Stage::create(&hold,&create).unwrap();f.receipt(&mut stage);
 signed.request["sequence"]=json!(1);signed.permit["payload"]["grant"]["sequence_start"]=json!(1);signed.permit["payload"]["grant"]["chunks"][0]["sequence"]=json!(1);
 signed.control.next_sequence=1;signed.control.cumulative_actions=1;
 let binding=serde_json::to_value(stage.stage_binding().unwrap()).unwrap();
 signed.permit["payload"]["grant"]["stage_binding"]=binding.clone();signed.control.stage_binding=binding;
 signed.control.member_binding=Some(member_identity_binding(&signed.permit["payload"]["grant"]).unwrap());signed.bind_message();
 let wire=signed.wire();let frame=signed.frame();let verified=signed.verify().unwrap();
 let action=crate::members::Action::from_verified(&wire,&frame,&verified).unwrap();
 let mut wrong=signed.wire();wrong.push(b' ');assert!(crate::members::Action::from_verified(&wrong,&frame,&verified).is_err());
 let mut original=signed.control.stage_binding.clone();original["relative_path"]=json!("different-stage-original.json");signed.control.stage_binding=original.clone();signed.permit["payload"]["grant"]["stage_binding"]=original;signed.control.member_binding=Some(member_identity_binding(&signed.permit["payload"]["grant"]).unwrap());signed.resign();
 let wrong_decision=signed.verify().unwrap();let wrong_action=crate::members::Action::from_verified(&signed.wire(),&signed.frame(),&wrong_decision).unwrap();
 assert!(stage.write_member(&wrong_action).is_err());assert!(!f.base.join("root/stage-1/payload.bin").exists());
 stage.write_member(&action).unwrap();f.receipt(&mut stage);assert_eq!(std::fs::read(f.base.join("root/stage-1/payload.bin")).unwrap(),b"abc");
}

fn scope_of(f:&SignedFixture)->crate::roots::ExecutionScope{crate::roots::ExecutionScope{activation_binding:serde_json::from_value(f.request["activation_binding"].clone()).unwrap(),store_id:f.request["store_id"].as_str().unwrap().into(),instance_id:f.request["instance_id"].as_str().unwrap().into(),slot_epoch:f.request["slot_epoch"].as_u64().unwrap(),principal_ref:f.request["principal_ref"].as_str().unwrap().into()}}
fn signed_creation()->SignedFixture{
 let mut f=SignedFixture::new();f.request["verb"]=json!("create_stage");f.request["payload"]=json!({"root_id":"owned-root","stage_name":"stage-1","max_bytes":64});
 f.permit["payload"]["allowed_verb"]=json!("create_stage");f.permit["payload"]["allowed_phase"]=json!("reserved");
 f.permit["payload"]["grant"]=json!({"kind":"empty-stage","root_id":"owned-root","stage_binding":null,"member":null,"preimage_binding":null,"full_sha256":null,"full_length":0,"chunk_size":0,"sequence_start":0,"chunks":[{"sequence":0,"offset":0,"length":0,"core_sha256":"0".repeat(64)}]});
 f.control.phase="reserved".into();f.control.stage_binding=Value::Null;f.control.member_binding=None;f.bind_message();f
}
#[test]fn self_consistent_signed_old_scope_cannot_allocate_new_same_named_root(){
 for mode in 0..5{let signed=signed_creation();let frame=signed.frame();let verified=signed.verify().unwrap();let action=crate::members::Action::from_verified(&signed.wire(),&frame,&verified).unwrap();let mut scope=scope_of(&signed);match mode{0=>scope.activation_binding.sha256="f".repeat(64),1=>scope.store_id="new-store".into(),2=>scope.instance_id="new-instance".into(),3=>scope.slot_epoch=2,_=>scope.principal_ref="new-principal".into()};let f=crate::custody_tests::Fixture::with_scope(Some(scope));let hold=f.root.exclusive(Duration::from_millis(50)).unwrap();assert!(crate::members::Stage::create(&hold,&action).is_err());assert!(!f.base.join("root/stage-1").exists());}
}
#[test]fn signed_creation_accepts_distinct_selected_namespace_and_slot_epochs(){let signed=signed_creation();let scope=scope_of(&signed);let f=crate::custody_tests::Fixture::with_scope(Some(scope));assert_eq!(f.root.selection().namespace_epoch,9);assert_eq!(f.root.selection().execution_scope.slot_epoch,1);let hold=f.root.exclusive(Duration::from_millis(50)).unwrap();let action=crate::members::Action::from_verified(&signed.wire(),&signed.frame(),&signed.verify().unwrap()).unwrap();let mut stage=crate::members::Stage::create(&hold,&action).unwrap();f.receipt(&mut stage);assert_eq!(stage.snapshot().unwrap().execution_scope,f.root.selection().execution_scope);}
