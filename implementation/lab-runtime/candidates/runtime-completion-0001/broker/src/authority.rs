//! Pure authority decisions. Trusted host snapshots are inputs from fixed Rust
//! custody modules, never caller assertions. This unit performs no durable writes.
use crate::*;
use base64::Engine;
use ed25519_dalek::{Signature, Signer, SigningKey, VerifyingKey};
use serde_json::{json, Value};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TrustDomain { Fixture, Actual }
fn domain_name(domain:TrustDomain) -> &'static str {
    match domain {TrustDomain::Fixture=>"fixture",TrustDomain::Actual=>"actual"}
}
pub struct Enrollment { issuer:String, adapter:String, purpose:String, key:VerifyingKey,
    domain:TrustDomain, pub binding:Value }
impl Enrollment {
    /// expected_hash and required_domain come from independently selected host
    /// custody, not a packet field or candidate self-pin. Actual enrollment and
    /// its protected-root loader are deployment obligations, not shipped here.
    pub fn select(raw:&[u8],expected_hash:&str,required_domain:TrustDomain)->Result<Self> {
        need(hash(raw)==expected_hash,"ENROLLMENT_PIN")?;
        let v=parse(raw,8192)?;
        closed(&v,&["schema_version","issuer_ref","adapter","purpose","algorithm","public_key","trust_domain"])?;
        need(v["schema_version"]=="lab-completion-issuer-enrollment/v1" && v["algorithm"]=="ed25519","ENROLLMENT_ALGORITHM")?;
        need(v["trust_domain"]==domain_name(required_domain),"TRUST_DOMAIN")?;
        let adapter=text(&v,"adapter",64)?;
        let purpose=text(&v,"purpose",64)?;
        let key_bytes=match adapter {
            "owner-hex-v1"=>{need(purpose=="broker-intent","ISSUER_PURPOSE")?;unhex::<32>(text(&v,"public_key",64)?)?},
            "custody-challenge-base64-v1"=>{
                need(purpose=="transport-authentication","ISSUER_PURPOSE")?;
                let encoded=text(&v,"public_key",64)?;
                let raw=base64::engine::general_purpose::STANDARD.decode(encoded).map_err(|_|Refusal("BASE64"))?;
                need(base64::engine::general_purpose::STANDARD.encode(&raw)==encoded,"BASE64")?;
                raw.try_into().map_err(|_|Refusal("PUBLIC_KEY_LENGTH"))?
            },
            _=>return Err(Refusal("ISSUER_ADAPTER")),
        };
        let key=VerifyingKey::from_bytes(&key_bytes).map_err(|_|Refusal("PUBLIC_KEY"))?;
        need(!key.is_weak(),"WEAK_KEY")?;
        Ok(Self{issuer:text(&v,"issuer_ref",128)?.into(),adapter:adapter.into(),purpose:purpose.into(),
            key,domain:required_domain,binding:content_digest(raw)})
    }
    pub fn verify_record(&self,envelope:&Value,domain:&str)->Result<Value> {
        need(self.adapter=="owner-hex-v1" && self.purpose=="broker-intent","INTENT_ADAPTER_REQUIRED")?;
        closed(envelope,&["issuer_ref","payload","signature"])?;
        need(envelope["issuer_ref"]==self.issuer,"ISSUER_MISMATCH")?;
        need(envelope["payload"]["schema_version"]==domain,"SIGNING_DOMAIN")?;
        let sig=Signature::from_bytes(&unhex::<64>(text(envelope,"signature",128)?)?);
        let bytes=canonical(&json!({"issuer_ref":self.issuer,"payload":envelope["payload"]}))?;
        self.key.verify_strict(&bytes,&sig).map_err(|_|Refusal("SIGNATURE"))?;
        Ok(envelope["payload"].clone())
    }
    pub fn verify_custody_challenge(&self,proof:&Value,expected_challenge:&Value)->Result<AuthenticatedTransport> {
        need(self.adapter=="custody-challenge-base64-v1" && self.purpose=="transport-authentication","TRANSPORT_ADAPTER_REQUIRED")?;
        closed(proof,&["challenge","signature"])?;
        closed(expected_challenge,&["schema_version","host_instance_ref","connection_ref","nonce","policy_sha256","expires_at","authority_effect"])?;
        text(expected_challenge,"host_instance_ref",128)?;text(expected_challenge,"connection_ref",128)?;
        digest(expected_challenge,"nonce")?;digest(expected_challenge,"policy_sha256")?;
        text(expected_challenge,"expires_at",64)?;
        need(expected_challenge["authority_effect"]=="none","TRANSPORT_AUTHORITY_EFFECT")?;
        need(&proof["challenge"]==expected_challenge && expected_challenge["schema_version"]=="lab-context-host-challenge/v1-candidate","CHALLENGE_MISMATCH")?;
        let encoded=text(proof,"signature",88)?;
        let raw=base64::engine::general_purpose::STANDARD.decode(encoded).map_err(|_|Refusal("BASE64"))?;
        need(base64::engine::general_purpose::STANDARD.encode(&raw)==encoded,"BASE64")?;
        let bytes:[u8;64]=raw.try_into().map_err(|_|Refusal("SIGNATURE_LENGTH"))?;
        self.key.verify_strict(&canonical(expected_challenge)?,&Signature::from_bytes(&bytes)).map_err(|_|Refusal("SIGNATURE"))?;
        Ok(AuthenticatedTransport{_enrollment:self.binding.clone()})
    }
}
/// Deliberately cannot be substituted for a verified intent permit.
pub struct AuthenticatedTransport { _enrollment:Value }

pub fn signed_record(payload:&Value,issuer:&str,key:&SigningKey)->Result<Value> {
    signing_bytes(payload)?;
    need(!issuer.is_empty() && issuer.len()<=128,"ISSUER_LENGTH")?;
    let bytes=canonical(&json!({"issuer_ref":issuer,"payload":payload}))?;
    Ok(json!({"issuer_ref":issuer,"payload":payload,"signature":hex(&key.sign(&bytes).to_bytes())}))
}

const SCOPE:&[&str]=&["principal_ref","scope_ref","operation","store_id","instance_id",
    "activation_binding","slot_epoch","intent_binding"];
fn scope(v:&Value)->Result<()> {
    closed(v,SCOPE)?;
    for k in ["principal_ref","scope_ref","operation","store_id","instance_id"] {text(v,k,128)?;}
    binding(&v["activation_binding"])?;binding(&v["intent_binding"])?;
    integer(v,"slot_epoch",1,i64::MAX)?;Ok(())
}
fn limits(v:&Value)->Result<()> {
    closed(v,&["max_total_bytes","max_actions","max_frame_bytes","max_chunk_bytes"])?;
    integer(v,"max_total_bytes",0,i64::MAX)?;integer(v,"max_actions",1,i64::MAX)?;
    integer(v,"max_frame_bytes",1,MAX_FRAME as i64)?;integer(v,"max_chunk_bytes",1,MAX_CHUNK as i64)?;Ok(())
}
fn slots(v:&Value)->Result<()> {
    let a=v.as_array().ok_or(Refusal("OUTPUT_SLOTS"))?;
    need(!a.is_empty() && a.len()<=32,"OUTPUT_SLOTS")?;
    let mut seen=std::collections::BTreeSet::new();
    for row in a {
        closed(row,&["root_id","member","preimage_binding","max_bytes"])?;
        text(row,"root_id",128)?;relative(text(row,"member",1024)?)?;
        nullable_binding(&row["preimage_binding"])?;integer(row,"max_bytes",0,i64::MAX)?;
        need(seen.insert((row["root_id"].to_string(),row["member"].to_string())),"OUTPUT_SLOT_DUPLICATE")?;
    }Ok(())
}
pub fn operation_fingerprint(core:&Value)->Result<String> {
    closed(core,&["schema_version","operation_id","idempotency_key","original_request_binding",
        "semantic_target_binding","source_cut_binding","effect_selection_binding","authority_basis_binding",
        "scope","limits","output_slots","operation_expires_at"])?;
    need(core["schema_version"]=="lab-completion-operation-request-core/v1","OPERATION_DOMAIN")?;
    text(core,"operation_id",128)?;text(core,"idempotency_key",128)?;
    for k in ["original_request_binding","semantic_target_binding","source_cut_binding","effect_selection_binding"] {binding(&core[k])?;}
    validate_content_digest(&core["authority_basis_binding"])?;
    scope(&core["scope"])?;limits(&core["limits"])?;slots(&core["output_slots"])?;
    integer(core,"operation_expires_at",1,i64::MAX)?;
    Ok(hash(&signing_bytes(core)?))
}

#[derive(Debug,Clone)]
pub struct ReplayRecord { pub sequence:i64, pub wire_digest:String, pub receipt_binding:Value }
#[derive(Debug,Clone)]
pub struct RecordedRequest { pub sequence:i64, pub wire_digest:String }
#[derive(Debug,Clone)]
pub struct IssuerCurrentness {
    pub enrollment_digest:Value, pub revocation_binding:Value, pub revoked:bool,
    /// The fixed control loader must sample revocation for this message under
    /// custody. A caller-supplied signed assertion is not this observation.
    pub checked_at:i64,
}
#[derive(Debug,Clone)]
pub struct RecoverySelection {
    pub authorization_digest:Value, pub subject_binding:Value, pub preimages:Vec<Value>,
    pub action:String, pub consumed:bool,
}
/// Fixed broker control loader supplies this fresh snapshot while holding the
/// store's lock. None of these fields can be accepted from request JSON. A raw
/// Rust struct is an internal code boundary, not proof of deployed host custody.
#[derive(Debug,Clone)]
pub struct ControlSnapshot {
    pub domain:TrustDomain, pub caller:Peer, pub now:i64, pub activation_expires_at:i64,
    pub operation_id:String, pub live_scope:Value, pub selected_roots:Vec<String>,
    pub issuer_currentness:IssuerCurrentness, pub disclosure_subjects:Vec<Value>,
    pub recovery:Option<RecoverySelection>,
    /// Lookup for this incoming operation+sequence, independently of the
    /// historical receipt selected as a disclosure subject. None proves absence
    /// under the held control lock; it never means 'not looked up'.
    pub recorded_request:Option<RecordedRequest>,
    pub operation_fingerprint:String, pub stage_binding:Value, pub member_binding:Option<Value>,
    pub original_deadline:i64, pub phase:String, pub next_sequence:i64,
    pub next_offset:i64, pub cumulative_bytes:i64, pub cumulative_actions:i64,
    pub acknowledgment_uncertain:bool, pub replay:Option<ReplayRecord>,
}
#[derive(Debug,Clone,PartialEq)]
pub enum Decision {
    Fresh{member_bytes:usize},
    Disclosure{subject_binding:Value,max_output_bytes:usize},
    Recovery{authorization_digest:Value,action:String,subject_binding:Value},
}
#[derive(Debug)]
pub struct VerifiedDispatch {
    decision:Decision, fingerprint:String, full_frame_digest:String, domain:TrustDomain,
}
impl VerifiedDispatch {
    pub fn decision(&self)->&Decision {&self.decision}
    pub fn operation_fingerprint(&self)->&str {&self.fingerprint}
    pub fn wire_digest(&self)->&str {&self.full_frame_digest}
    pub fn trust_domain(&self)->TrustDomain {self.domain}
}
const PHASES:&[&str]=&["absent","reserved","staging","sealed","generation-published",
    "pointer-committed","terminal","quarantined","UNKNOWN"];
fn phase_verb(phase:&str,verb:&str)->bool {
    match verb {
        "reserve_family"=>phase=="absent",
        "create_stage"=>["absent","reserved"].contains(&phase),
        "write_member"=>["reserved","staging"].contains(&phase),
        "seal_stage"=>phase=="staging",
        "commit_generation"=>["sealed","generation-published","pointer-committed"].contains(&phase),
        "repair_derived"=>phase=="pointer-committed",
        "reconcile_operation"=>["quarantined","UNKNOWN"].contains(&phase),
        "read_receipt"|"inspect"|"inspect_operation"=>PHASES.contains(&phase),
        "close_family"=>PHASES.contains(&phase) && phase!="terminal",
        _=>false,
    }
}

// Fresh disclosure and recovery authorize a current action on a recorded
// operation. They deliberately do not consume the expired original effect
// grant, reset its counters, or admit a producer dispatch.
fn current_authorization(frame:&Frame,enrollment:&Enrollment,control:&ControlSnapshot,
                         domain:&str,extra:&[&str])->Result<Value> {
    let p=enrollment.verify_record(&frame.permit,domain)?;
    let mut fields=vec!["schema_version","authorization_id","operation_id","operation_fingerprint",
        "scope","allowed_verb","message_core_sha256","subject_binding","not_before","expires_at"];
    fields.extend_from_slice(extra);closed(&p,&fields)?;
    text(&p,"authorization_id",128)?;digest(&p,"operation_fingerprint")?;digest(&p,"message_core_sha256")?;
    binding(&p["subject_binding"])?;
    need(p["operation_id"]==control.operation_id && p["operation_fingerprint"]==control.operation_fingerprint &&
         p["scope"]==control.live_scope && p["allowed_verb"]==frame.request["verb"],"CURRENT_AUTHORITY_SCOPE")?;
    need(p["subject_binding"]==frame.request["payload"]["subject_binding"] &&
         p["message_core_sha256"]==hash(&signing_bytes(&frame.authorization_core()?)?),"CURRENT_MESSAGE_BINDING")?;
    let begin=integer(&p,"not_before",0,i64::MAX)?;
    let end=integer(&p,"expires_at",1,control.activation_expires_at)?;
    need(begin<end && control.now>=begin && control.now<end,"CURRENT_AUTHORITY_PERIOD")?;
    Ok(p)
}

fn verify_disclosure(frame:&Frame,enrollment:&Enrollment,control:&ControlSnapshot)->Result<VerifiedDispatch> {
    let p=current_authorization(frame,enrollment,control,"lab-completion-broker-disclosure-permit/v1",&["max_output_bytes"])?;
    let cap=integer(&p,"max_output_bytes",1,MAX_FRAME as i64)? as usize;
    need(control.disclosure_subjects.len()<=64,"DISCLOSURE_SELECTION_LIMIT")?;
    for subject in &control.disclosure_subjects {binding(subject)?;}
    need(control.disclosure_subjects.contains(&p["subject_binding"]),"DISCLOSURE_SUBJECT")?;
    if frame.request["verb"]=="read_receipt" {
        let previous=control.replay.as_ref().ok_or(Refusal("RECEIPT_UNAVAILABLE"))?;
        need(frame.request["sequence"]==previous.sequence,"RECEIPT_SEQUENCE")?;
        need(!control.acknowledgment_uncertain && previous.receipt_binding==p["subject_binding"],"RECONCILIATION_REQUIRED")?;
    }
    Ok(VerifiedDispatch{decision:Decision::Disclosure{subject_binding:p["subject_binding"].clone(),max_output_bytes:cap},
        fingerprint:control.operation_fingerprint.clone(),full_frame_digest:frame.digest.clone(),domain:control.domain})
}

fn verify_recovery(frame:&Frame,enrollment:&Enrollment,control:&ControlSnapshot)->Result<VerifiedDispatch> {
    need(phase_verb(&control.phase,text(&frame.request,"verb",64)?),"RECOVERY_STATE")?;
    need(control.recorded_request.is_none(),"RECOVERY_ALREADY_RECORDED")?;
    let p=current_authorization(frame,enrollment,control,"lab-completion-recovery-authorization/v1",
        &["observed_phase","action","preimages","next_sequence","next_offset","cumulative_bytes","cumulative_actions","original_deadline"])?;
    let selected=control.recovery.as_ref().ok_or(Refusal("RECOVERY_SELECTION_REQUIRED"))?;
    validate_content_digest(&selected.authorization_digest)?;binding(&selected.subject_binding)?;
    need(!selected.consumed && selected.authorization_digest==content_digest(&canonical(&frame.permit)?),"RECOVERY_CONSUMED_OR_CHANGED")?;
    need(p["observed_phase"]==control.phase && p["subject_binding"]==selected.subject_binding &&
         p["action"]==selected.action,"RECOVERY_SELECTION")?;
    let action=text(&p,"action",64)?;
    let allowed=if frame.request["verb"]=="close_family" {action=="close_family"}
        else {["reconcile_chunk","complete_commit","quarantine","seal_outcome","restore_continuity"].contains(&action)};
    need(allowed,"RECOVERY_ACTION")?;
    let preimages=p["preimages"].as_array().ok_or(Refusal("RECOVERY_PREIMAGES"))?;
    need(!preimages.is_empty() && preimages.len()<=32 && *preimages==selected.preimages,"RECOVERY_PREIMAGES")?;
    for b in preimages {binding(b)?;}
    for (name,value) in [("next_sequence",control.next_sequence),("next_offset",control.next_offset),
        ("cumulative_bytes",control.cumulative_bytes),("cumulative_actions",control.cumulative_actions),
        ("original_deadline",control.original_deadline)] {
        need(integer(&p,name,0,i64::MAX)?==value,"RECOVERY_COUNTER_RESET")?;
    }
    Ok(VerifiedDispatch{decision:Decision::Recovery{authorization_digest:selected.authorization_digest.clone(),
        action:action.into(),subject_binding:selected.subject_binding.clone()},fingerprint:control.operation_fingerprint.clone(),
        full_frame_digest:frame.digest.clone(),domain:control.domain})
}

pub fn verify(frame:&Frame,peer:Peer,enrollment:&Enrollment,basis_envelope:&Value,
              core:&Value,control:&ControlSnapshot)->Result<VerifiedDispatch> {
    need(control.domain==enrollment.domain,"TRUST_DOMAIN")?;
    need(peer.pid>0 && peer.uid!=u32::MAX && peer.gid!=u32::MAX,"CALLER_ID_RANGE")?;
    need(peer==control.caller,"CALLER_MAPPING")?;
    need(control.now>=0 && control.next_sequence>=0 && control.next_offset>=0 &&
        control.cumulative_bytes>=0 && control.cumulative_actions>=0,"CONTROL_COUNTERS")?;
    scope(&control.live_scope)?;
    need(!control.selected_roots.is_empty() && control.selected_roots.len()<=32 &&
         control.selected_roots.iter().all(|r|!r.is_empty() && r.len()<=128),"CONTROL_ROOTS")?;
    let mut unique=std::collections::BTreeSet::new();
    need(control.selected_roots.iter().all(|r|unique.insert(r)),"CONTROL_ROOTS")?;
    let current=&control.issuer_currentness;
    validate_content_digest(&current.enrollment_digest)?;binding(&current.revocation_binding)?;
    need(current.enrollment_digest==enrollment.binding && !current.revoked &&
         current.checked_at==control.now,"ISSUER_NOT_CURRENT")?;
    need(control.now<control.activation_expires_at,"LIVE_ACTIVATION_EXPIRED")?;
    need(PHASES.contains(&control.phase.as_str()),"CONTROL_PHASE")?;
    need(frame.request["operation_id"]==control.operation_id,"LIVE_OPERATION_ID")?;
    for key in ["principal_ref","store_id","instance_id","activation_binding","slot_epoch","intent_binding"] {
        need(frame.request[key]==control.live_scope[key],"LIVE_REQUEST_SCOPE")?;
    }
    need(control.selected_roots.iter().any(|r|frame.request["payload"]["root_id"]==*r),"LIVE_ROOT")?;
    unhex::<32>(&control.operation_fingerprint)?;
    let verb=text(&frame.request,"verb",64)?;
    // Explicit read-query namespace: disclosure signing domain + closed read
    // verb + request_id identify the query. operation_id/sequence identify its
    // historical target, not a new mutation slot. No ledger write, reservation,
    // sequence increment or effect quota is needed to inspect in any state.
    if ["inspect","inspect_operation","read_receipt"].contains(&verb) {
        return verify_disclosure(frame,enrollment,control);
    }
    let seq=integer(&frame.request,"sequence",0,i64::MAX)?;
    if let Some(record)=&control.recorded_request {
        need(record.sequence==seq,"REPLAY_SELECTION")?;
        unhex::<32>(&record.wire_digest)?;
        need(record.wire_digest==frame.digest,"IDEMPOTENCY_CONFLICT")?;
    } else {
        need(seq==control.next_sequence,"NEXT_SEQUENCE")?;
    }
    if ["reconcile_operation","close_family"].contains(&verb) {
        return verify_recovery(frame,enrollment,control);
    }
    let fingerprint=operation_fingerprint(core)?;
    need(fingerprint==control.operation_fingerprint,"IMMUTABLE_OPERATION_SELECTION")?;
    need(core["scope"]==control.live_scope && core["operation_id"]==control.operation_id,"LIVE_OPERATION_SCOPE")?;
    nullable_binding(&control.stage_binding)?;
    let basis=enrollment.verify_record(basis_envelope,"lab-completion-effect-authority-basis/v1")?;
    closed(&basis,&["schema_version","basis_id","scope","limits","output_slots","not_before","expires_at"])?;
    text(&basis,"basis_id",128)?;scope(&basis["scope"])?;limits(&basis["limits"])?;slots(&basis["output_slots"])?;
    need(core["authority_basis_binding"]==content_digest(&canonical(basis_envelope)?),"AUTHORITY_BASIS_BINDING")?;
    need(core["scope"]==basis["scope"] && core["limits"]==basis["limits"] && core["output_slots"]==basis["output_slots"],"AUTHORITY_BASIS_SCOPE")?;
    let begin=integer(&basis,"not_before",0,i64::MAX)?;
    let end=integer(&basis,"expires_at",1,i64::MAX)?;
    let operation_end=integer(core,"operation_expires_at",1,end)?;
    need(begin<end && operation_end==control.original_deadline && control.now>=begin &&
         control.now<operation_end && control.now<control.activation_expires_at,"BASIS_PERIOD")?;
    let permit=enrollment.verify_record(&frame.permit,"lab-completion-broker-permit/v1")?;
    closed(&permit,&["schema_version","permit_id","operation_fingerprint","basis_binding","scope","limits",
        "allowed_verb","allowed_phase","not_before","expires_at","grant"])?;
    text(&permit,"permit_id",128)?;digest(&permit,"operation_fingerprint")?;
    need(permit["operation_fingerprint"]==fingerprint && permit["basis_binding"]==core["authority_basis_binding"],"PERMIT_OPERATION")?;
    need(permit["scope"]==core["scope"] && permit["limits"]==core["limits"],"PERMIT_SCOPE")?;
    let pbegin=integer(&permit,"not_before",begin,end)?;
    let pend=integer(&permit,"expires_at",1,operation_end.min(control.activation_expires_at))?;
    need(pbegin<pend && control.now>=pbegin && control.now<pend,"PERMIT_PERIOD")?;
    let r=&frame.request; let verb=text(r,"verb",64)?; let phase=text(&permit,"allowed_phase",32)?;
    need(PHASES.contains(&phase) && PHASES.contains(&control.phase.as_str()) && phase_verb(phase,verb) && permit["allowed_verb"]==verb,"PERMIT_STATE")?;
    need(r["operation_id"]==core["operation_id"],"OPERATION_ID")?;
    for key in ["principal_ref","store_id","instance_id","activation_binding","slot_epoch","intent_binding"] {
        need(r[key]==core["scope"][key],"REQUEST_SCOPE")?;
    }
    // Canonical outer wire length is already capped by decode; selected policy
    // may narrow it further. It never widens the public Lab envelope.
    let full=canonical(&json!({"schema_version":"lab-completion-broker-frame/v1","request":r,"permit":frame.permit}))?;
    need(full.len()<=integer(&permit["limits"],"max_frame_bytes",1,MAX_FRAME as i64)? as usize,"SELECTED_FRAME_LIMIT")?;
    let g=&permit["grant"];
    closed(g,&["kind","root_id","stage_binding","member","preimage_binding","full_sha256","full_length","chunk_size","sequence_start","chunks"])?;
    nullable_binding(&g["stage_binding"])?;
    need(g["stage_binding"]==control.stage_binding,"STAGE_SELECTION")?;
    let kind=text(g,"kind",32)?;text(g,"root_id",128)?;
    let sequence_start=integer(g,"sequence_start",0,i64::MAX)?;
    let chunks=g["chunks"].as_array().ok_or(Refusal("BATCH"))?;
    need(!chunks.is_empty() && chunks.len()<=MAX_BATCH,"BATCH_LIMIT")?;
    let mut last_offset=None;
    let full_length=integer(g,"full_length",0,i64::MAX)?;
    let chunk_size=integer(g,"chunk_size",0,MAX_CHUNK as i64)?;
    let slots=core["output_slots"].as_array().ok_or(Refusal("OUTPUT_SLOTS"))?;
    need(slots.iter().any(|s|s["root_id"]==g["root_id"]),"UNDECLARED_ROOT")?;
    match kind {
        "member"=>{
            need(verb=="write_member" && chunk_size>0,"MEMBER_GRANT_VERB")?;
            need(!g["stage_binding"].is_null(),"MEMBER_STAGE_REQUIRED")?;
            let slot=slots.iter().find(|s|s["root_id"]==g["root_id"] && s["member"]==g["member"]).ok_or(Refusal("UNDECLARED_MEMBER"))?;
            relative(text(g,"member",1024)?)?;nullable_binding(&g["preimage_binding"])?;digest(g,"full_sha256")?;
            need(g["preimage_binding"]==slot["preimage_binding"] && full_length<=integer(slot,"max_bytes",0,i64::MAX)?,"MEMBER_PREIMAGE_LIMIT")?;
            need(chunk_size<=integer(&permit["limits"],"max_chunk_bytes",1,MAX_CHUNK as i64)?,"SELECTED_CHUNK_LIMIT")?;
            let selected=control.member_binding.as_ref().ok_or(Refusal("MEMBER_SELECTION_REQUIRED"))?;
            validate_content_digest(selected)?;
            need(*selected==member_identity_binding(g)?,"IMMUTABLE_MEMBER_SELECTION")?;
        },
        "empty-stage"|"control"=>{
            need(g["member"].is_null() && g["preimage_binding"].is_null() && g["full_sha256"].is_null() && full_length==0 && chunk_size==0 && chunks.len()==1,"CONTROL_GRANT_SHAPE")?;
            let reservation=["reserve_family","create_stage"].contains(&verb);
            need((kind=="empty-stage" && reservation) || (kind=="control" && !reservation && verb!="write_member"),"GRANT_VERB")?;
        },
        _=>return Err(Refusal("GRANT_KIND")),
    }
    for (index,row) in chunks.iter().enumerate() {
        closed(row,&["sequence","offset","length","core_sha256"])?;digest(row,"core_sha256")?;
        let seq=integer(row,"sequence",0,i64::MAX)?;
        need(sequence_start.checked_add(index as i64)==Some(seq),"BATCH_SEQUENCE")?;
        let offset=integer(row,"offset",0,full_length)?;
        let length=integer(row,"length",0,MAX_CHUNK as i64)?;
        if kind=="member" {
            need(offset%chunk_size==0 && length==(full_length-offset).min(chunk_size) &&
                 (full_length==0 || length>0) && last_offset.is_none_or(|last|last==offset),"BATCH_OFFSETS")?;
        } else {need(offset==0 && length==0,"CONTROL_GRANT_SHAPE")?;}
        last_offset=offset.checked_add(length);
    }
    let seq=integer(r,"sequence",0,i64::MAX)?;
    let selected=chunks.iter().find(|c|c["sequence"]==seq).ok_or(Refusal("SEQUENCE_NOT_PERMITTED"))?;
    need(selected["core_sha256"]==hash(&signing_bytes(&frame.authorization_core()?)?),"MESSAGE_CORE_BINDING")?;
    let p=&r["payload"];need(p["root_id"]==g["root_id"],"REQUEST_ROOT")?;
    let bytes=if verb=="write_member" {
        for key in ["member","preimage_binding","full_sha256","full_length"] {need(p[key]==g[key],"REQUEST_MEMBER_CONTENT")?;}
        need(p["offset"]==selected["offset"] && p["length"]==selected["length"],"REQUEST_CHUNK_RANGE")?;
        integer(p,"length",0,MAX_CHUNK as i64)?
    } else {
        if kind=="empty-stage" {need(integer(p,"max_bytes",0,i64::MAX)?<=integer(&permit["limits"],"max_total_bytes",0,i64::MAX)?,"RESERVATION_LIMIT")?;}
        0
    };
    // Full-frame identity includes the derived permit. Renewing the permit at
    // an acknowledged sequence never silently becomes an original replay.
    if control.recorded_request.is_some() {
        need(!control.acknowledgment_uncertain,"RECONCILIATION_REQUIRED")?;
        // An effect grant never implicitly authorizes disclosure. The client
        // issues a distinct current read_receipt request for the stored record.
        return Err(Refusal("RECEIPT_DISCLOSURE_REQUIRED"));
    }
    let inspection=["inspect_operation","read_receipt","reconcile_operation"].contains(&verb);
    need(phase==control.phase,"PERMIT_STATE")?;
    need(!control.acknowledgment_uncertain || inspection,"RECONCILIATION_REQUIRED")?;
    need(seq==control.next_sequence,"NEXT_SEQUENCE")?;
    if verb=="write_member" {need(p["offset"]==control.next_offset,"NEXT_OFFSET")?;}
    if !["inspect_operation","read_receipt"].contains(&verb) {
        need(control.cumulative_bytes.checked_add(bytes).is_some_and(|n|n<=core["limits"]["max_total_bytes"].as_i64().unwrap_or(-1)),"CUMULATIVE_BYTE_LIMIT")?;
        need(control.cumulative_actions.checked_add(1).is_some_and(|n|n<=core["limits"]["max_actions"].as_i64().unwrap_or(-1)),"CUMULATIVE_ACTION_LIMIT")?;
    }
    Ok(VerifiedDispatch{decision:Decision::Fresh{member_bytes:bytes as usize},fingerprint,
        full_frame_digest:frame.digest.clone(),domain:control.domain})
}

/// Identity of captured producer bytes admitted once by the fixed control store.
/// Not a digest of the renewed permit, interval or batch cursor.
pub fn member_identity_binding(grant:&Value)->Result<Value> {
    let identity=json!({"schema_version":"lab-completion-member-selection/v1",
        "root_id":grant["root_id"],"stage_binding":grant["stage_binding"],"member":grant["member"],
        "preimage_binding":grant["preimage_binding"],"full_sha256":grant["full_sha256"],
        "full_length":grant["full_length"],"chunk_size":grant["chunk_size"]});
    Ok(content_digest(&signing_bytes(&identity)?))
}

/// Call only after the later fixed Rust control store has made the represented
/// receipt durable. This codec signs a record; it does not assert fsync occurred.
pub fn sign_receipt(frame:&Frame,durable_phase:&str,status:&str,error:Option<&str>,
                    result_binding:Value,issuer:&str,key:&SigningKey)->Result<Value> {
    need(PHASES.contains(&durable_phase),"RECEIPT_PHASE")?;
    need(["PASS","FAIL","UNKNOWN","REFUSED"].contains(&status),"RECEIPT_STATUS")?;
    need(error.is_none_or(|e|!e.is_empty() && e.len()<=64 && e.bytes().all(|b|b.is_ascii_uppercase()||b==b'_'||b.is_ascii_digit())),"RECEIPT_ERROR")?;
    nullable_binding(&result_binding)?;
    let payload=json!({"schema_version":"lab-completion-broker-response/v1","request_digest":frame.digest,
        "operation_id":frame.request["operation_id"],"sequence":frame.request["sequence"],
        "durable_phase":durable_phase,"status":status,"error":error,"result_binding":result_binding});
    signed_record(&payload,issuer,key)
}

/// Closed receipt codec. A valid signature authenticates bytes, not the claimed
/// durable store state. Callers still require their independent store witness.
pub fn verify_receipt(raw:&[u8],enrollment:&Enrollment,request_digest:&str,
                      operation_id:&str,sequence:i64)->Result<Value> {
    let envelope=parse(raw,MAX_FRAME)?;
    need(canonical(&envelope)?==raw,"NONCANONICAL_WIRE")?;
    let p=enrollment.verify_record(&envelope,"lab-completion-broker-response/v1")?;
    closed(&p,&["schema_version","request_digest","operation_id","sequence","durable_phase","status","error","result_binding"])?;
    digest(&p,"request_digest")?;text(&p,"operation_id",128)?;integer(&p,"sequence",0,i64::MAX)?;
    need(p["request_digest"]==request_digest && p["operation_id"]==operation_id && p["sequence"]==sequence,"RECEIPT_REQUEST_BINDING")?;
    need(PHASES.contains(&text(&p,"durable_phase",32)?),"RECEIPT_PHASE")?;
    need(["PASS","FAIL","UNKNOWN","REFUSED"].contains(&text(&p,"status",16)?),"RECEIPT_STATUS")?;
    if !p["error"].is_null() {
        need(text(&p,"error",64)?.bytes().all(|b|b.is_ascii_uppercase()||b==b'_'||b.is_ascii_digit()),"RECEIPT_ERROR")?;
    }
    nullable_binding(&p["result_binding"])?;Ok(p)
}
